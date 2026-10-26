from pathlib import Path
import json, random, time, re, unicodedata, math
from collections import Counter
import numpy as np
import pyarrow.parquet as pq
import torch
from torch import nn

ROOT=Path(__file__).resolve().parent
(ROOT/'logs').mkdir(exist_ok=True)
DATA=ROOT/'data'; MODEL=ROOT/'model'; MODEL.mkdir(exist_ok=True)
CHARS=" abcdefghijklmnopqrstuvwxyz0123456789.,?!'\":;()-/+"
PAD,BOS,SEP,EOS=0,1,2,3
V=4+len(CHARS); D=48; H=192
QMAX,AMAX=120,160
random.seed(2026); np.random.seed(2026); torch.manual_seed(2026)
torch.set_num_threads(6)
device='cuda' if torch.cuda.is_available() else 'cpu'
if device=='cuda': torch.cuda.manual_seed_all(2026)

def clean(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(' +',' ',''.join(c if c in CHARS else ' ' for c in s)).strip()
def encode(s): return [4+CHARS.index(c) for c in clean(s)]
def short_reply(s):
    s=clean(s)
    # Prefer one complete sentence, keeping short replies within board limits.
    m=re.search(r'[.!?](?: |$)',s)
    if m and m.end()>=16: s=s[:m.end()].strip()
    if len(s)>AMAX-1: s=s[:AMAX-2].rsplit(' ',1)[0]+'.'
    return s

general=[]
for row in pq.read_table(DATA/'train-00000-of-00001.parquet').to_pylist():
    msgs=row['messages']
    for a,b in zip(msgs,msgs[1:]):
        if a['role']=='user' and b['role']=='assistant':
            q=clean(a['content']); ans=short_reply(b['content'])
            if 3<=len(q)<=QMAX and 10<=len(ans)<AMAX:
                general.append((q,ans))
general=list(dict.fromkeys(general))
random.shuffle(general)
focused=[(clean(x['user']),clean(x['assistant'])) for x in json.loads((DATA/'focused-dialogues.json').read_text())]
heldout=json.loads((DATA/'heldout-prompts.json').read_text())
excluded={clean(x['prompt']) for x in heldout}
excluded.update(clean(x['prompt']) for x in json.loads((DATA/'final-test-prompts.json').read_text()))
general=[x for x in general if x[0] not in excluded]
focused=[x for x in focused if x[0] not in excluded]
# Split by exact input so a validation question cannot occur in the training set.
questions=sorted({q for q,a in focused}); random.shuffle(questions)
valq=set(questions[:max(1,len(questions)//10)])
focus_val=[x for x in focused if x[0] in valq]
focus_train=[x for x in focused if x[0] not in valq]
(DATA/'prepared-training.json').write_text(json.dumps({'general':general,'focused_train':focus_train,'focused_validation':focus_val},indent=2))


counts=Counter(word for q,a in general+focused for word in re.findall(r'[a-z0-9]+',q))
required={word for q,a in focused for word in re.findall(r'[a-z0-9]+',q)}
chosen=required | {w for w,c in counts.most_common(2046-len(required))}
WORDS=['<pad>','<unk>']+sorted(chosen)
word_index={word:i for i,word in enumerate(WORDS)}
def encode_words(q):
    return [word_index.get(w,1) for w in re.findall(r'[a-z0-9]+',clean(q))] or [1]
(DATA/'word-vocabulary.json').write_text(json.dumps(WORDS,indent=2))

class TinyGRU(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb=nn.Embedding(V,D,padding_idx=PAD)
        self.gru=nn.GRU(D,H,batch_first=True)
        self.out=nn.Linear(H,V)
        self.word_emb=nn.Embedding(len(WORDS),64,padding_idx=0)
        self.word_gate=nn.Embedding(len(WORDS),1)
        nn.init.zeros_(self.word_gate.weight)
        self.enc=nn.Linear(64,H)
    def forward(self,x,h=None,words=None):
        if h is None:
            scores=self.word_gate(words).squeeze(-1).masked_fill(words==0,-1e9)
            attention=scores.softmax(dim=1)
            pooled=(self.word_emb(words)*attention.unsqueeze(-1)).sum(dim=1)
            h=torch.tanh(self.enc(pooled)).unsqueeze(0)
        y,h=self.gru(self.emb(x),h)
        return self.out(y),h

net=TinyGRU().to(device)
optimizer=torch.optim.AdamW(net.parameters(),lr=.0025,weight_decay=.0001)

def batch(pairs,size=48):
    selected=random.choices(pairs,k=size)
    if pairs is focus_train:
        augmented=[]
        for q,a in selected:
            original=q
            # Surface-form variation; only training questions are used.
            if random.random()<.4:
                for stem in ('what is a ','what is an ','what is ','explain '):
                    if q.startswith(stem):
                        subject=q[len(stem):].rstrip('?')
                        q=random.choice(['explain '+subject,'tell me about '+subject,'describe '+subject,'what does '+subject+' mean'])
                        break
            q=random.choice(['','','','please ','hey, ','tiny, ','can you tell me '])+q
            q+=random.choice(['','','','?',' please',' for me',' in simple words'])
            if clean(q) in excluded or len(q)>QMAX: q=original
            augmented.append((q,a))
        selected=augmented
    seqs=[]; masks=[]; word_seqs=[]
    for q,a in selected:
        qi=encode(q[:QMAX]); ai=encode(a[:AMAX-1])
        seq=[SEP]+ai+[EOS]
        word_seqs.append(encode_words(q))
        seqs.append(seq)
        masks.append(0)
    n=max(map(len,seqs))-1
    xx=torch.zeros((size,n),dtype=torch.long)
    yy=torch.full((size,n),-100,dtype=torch.long)
    ww=torch.zeros((size,n),dtype=torch.float32)
    for i,(seq,start) in enumerate(zip(seqs,masks)):
        xx[i,:len(seq)-1]=torch.tensor(seq[:-1])
        yy[i,start:len(seq)-1]=torch.tensor(seq[start+1:])
        ww[i,start:len(seq)-1]=1
        ww[i,start:min(start+12,len(seq)-1)]=12
    words=torch.zeros((size,max(map(len,word_seqs))),dtype=torch.long)
    for i,ws in enumerate(word_seqs): words[i,:len(ws)]=torch.tensor(ws)
    return xx.to(device),yy.to(device),ww.to(device),words.to(device)

@torch.no_grad()
def evaluate_loss(pairs):
    net.eval(); losses=[]
    for _ in range(5):
        x,y,w,words=batch(pairs,32); logits,_=net(x,words=words)
        losses.append(((nn.functional.cross_entropy(logits.reshape(-1,V),y.reshape(-1),reduction='none').reshape_as(w)*w).sum()/w.sum()).item())
    net.train(); return sum(losses)/len(losses)

@torch.no_grad()
def reply(q,maxchars=160):
    net.eval()
    x=torch.tensor([[SEP]],device=device)
    words=torch.tensor([encode_words(q[:QMAX])],device=device)
    logits,h=net(x,words=words); result=''
    for _ in range(maxchars):
        scores=logits[0,-1].clone(); scores[:3]=-1e9
        nxt=int(scores.argmax())
        if nxt==EOS: break
        result+=CHARS[nxt-4]
        logits,h=net(torch.tensor([[nxt]],device=device),h)
    net.train(); return result

start=time.time(); records=[]; best=1e9
print(json.dumps({'device':device,'gpu':torch.cuda.get_device_name(0) if device=='cuda' else None,
 'parameters':sum(x.numel() for x in net.parameters()),'general_pairs':len(general),
 'focused_train':len(focus_train),'focused_validation':len(focus_val),'hidden':H,'embedding':D,'vocab':V}),flush=True)
for phase,steps in [('general',1200),('focused',6000)]:
    for step in range(1,steps+1):
        # Most final-stage batches teach concise, input-conditioned responses.
        pairs=general if phase=='general' else (focus_train if random.random()<.97 else general)
        x,y,w,words=batch(pairs)
        optimizer.zero_grad(set_to_none=True)
        logits,_=net(x,words=words)
        loss=(nn.functional.cross_entropy(logits.reshape(-1,V),y.reshape(-1),reduction='none').reshape_as(w)*w).sum()/w.sum()
        loss.backward(); nn.utils.clip_grad_norm_(net.parameters(),1.0); optimizer.step()
        if step%400==0:
            val=evaluate_loss(focus_val)
            rec={'phase':phase,'step':step,'loss':round(loss.item(),4),'validation_loss':round(val,4),
                 'elapsed_seconds':round(time.time()-start,1)}
            records.append(rec)
            print(json.dumps(rec),flush=True)
            (ROOT/'logs'/'training-progress.json').write_text(json.dumps(records,indent=2))
            print('sample: '+reply('what is ram'),flush=True)
            if phase=='focused' and val<best:
                best=val
                torch.save({'state':net.state_dict(),'chars':CHARS,'D':D,'H':H,'V':V,'words':WORDS,'word_dim':64},MODEL/'gru-best.pt')
        if phase=='focused' and step==3600:
            for group in optimizer.param_groups: group['lr']=.001
ckpt=torch.load(MODEL/'gru-best.pt',map_location=device,weights_only=False)
net.load_state_dict(ckpt['state'])
results=[]
for item in heldout:
    answer=reply(item['prompt'])
    results.append({**item,'reply':answer,'hint_present':item['expected_hint'] in answer})
print(json.dumps(results,indent=2),flush=True)
(MODEL/'evaluation-float.json').write_text(json.dumps(results,indent=2))
metadata={'architecture':'learned word-attention encoder plus character GRU decoder','hidden_units':H,'embedding_dimensions':D,'word_vocabulary_size':len(WORDS),'word_embedding_dimensions':64,
 'vocabulary':CHARS,'special_tokens':{'pad':PAD,'user_start':BOS,'assistant_start':SEP,'end':EOS},
 'parameters':sum(x.numel() for x in net.parameters()),'training_method':'learned input word attention; first 12 reply characters weighted 12x; surface-form augmentation; 6000 focused steps','general_pairs':len(general),'focused_train_pairs':len(focus_train),
 'focused_validation_pairs':len(focus_val),'best_validation_loss':best,'training_device':device,
 'gpu':torch.cuda.get_device_name(0) if device=='cuda' else None,'training_seconds':time.time()-start,
 'max_user_characters':QMAX,'max_reply_characters':AMAX,'heldout_hint_matches':sum(x['hint_present'] for x in results),
 'heldout_count':len(results),'limitations':'Single-message, small-domain experimental LM; keyword matches are not a general intelligence benchmark.'}
(MODEL/'gru-info.json').write_text(json.dumps(metadata,indent=2))
print('TRAINING COMPLETE',flush=True)
