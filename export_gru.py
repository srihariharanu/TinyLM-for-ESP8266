from pathlib import Path
import json, time, hashlib, re
import numpy as np
import torch

ROOT=Path(__file__).resolve().parent
MODEL=ROOT/'model'; FW=ROOT/'firmware'/'RecurrentLM'; FW.mkdir(parents=True,exist_ok=True)
checkpoint=torch.load(MODEL/'gru-best.pt',map_location='cpu',weights_only=False)
state={k:v.detach().numpy().astype(np.float32) for k,v in checkpoint['state'].items()}
CHARS=checkpoint['chars']; H=checkpoint['H']; D=checkpoint['D']; V=checkpoint['V']
WORDS=checkpoint['words']; WD=checkpoint['word_dim']; word_index={w:i for i,w in enumerate(WORDS)}

def quantize_rows(a):
    scales=np.maximum(np.max(np.abs(a),axis=1)/127.0,1e-9).astype(np.float32)
    q=np.clip(np.rint(a/scales[:,None]),-127,127).astype(np.int8)
    return q,scales

arrays={}
for source,name in [('emb.weight','E'),('gru.weight_ih_l0','WI'),('gru.weight_hh_l0','WH'),('out.weight','WO'),('word_emb.weight','WE'),('enc.weight','WC')]:
    arrays[name+'_Q'],arrays[name+'_S']=quantize_rows(state[source])
for source,name in [('gru.bias_ih_l0','BI'),('gru.bias_hh_l0','BH'),('out.bias','BO'),('enc.bias','BC')]: arrays[name]=state[source]
arrays['WG']=state['word_gate.weight'].reshape(-1)
# numpy int32 copies are used only by the computer-side verifier.
qi={k:a.astype(np.int32) for k,a in arrays.items() if k.endswith('_Q')}

def token(c): return 4+CHARS.index(c) if c in CHARS else 4

def step(idx,h):
    gi=(qi['WI_Q']@qi['E_Q'][idx]).astype(np.float32)*arrays['WI_S']*arrays['E_S'][idx]+arrays['BI']
    hq=np.clip(np.rint(h*32767),-32767,32767).astype(np.int32)
    gh=(qi['WH_Q']@hq).astype(np.float32)*(arrays['WH_S']/32767.0)+arrays['BH']
    r=1/(1+np.exp(-np.clip(gi[:H]+gh[:H],-30,30)))
    z=1/(1+np.exp(-np.clip(gi[H:2*H]+gh[H:2*H],-30,30)))
    n=np.tanh(gi[2*H:]+r*gh[2*H:])
    h=(1-z)*n+z*h
    hq=np.clip(np.rint(h*32767),-32767,32767).astype(np.int32)
    scores=(qi['WO_Q']@hq).astype(np.float32)*(arrays['WO_S']/32767.0)+arrays['BO']
    scores[:3]=-1e9
    return h,int(scores.argmax())

def generate(prompt):
    wordids=[word_index.get(w,1) for w in re.findall(r'[a-z0-9]+',prompt.lower()[:120])] or [1]
    gates=arrays['WG'][wordids]
    attention=np.exp(gates-gates.max()).astype(np.float32)
    attention/=attention.sum()
    pooled=(qi['WE_Q'][wordids].astype(np.float32)*arrays['WE_S'][wordids,None]*attention[:,None]).sum(axis=0)
    pool_scale=np.float32(max(float(np.max(np.abs(pooled)))/32767.0,1e-9))
    pool_q=np.clip(np.rint(pooled/pool_scale),-32767,32767).astype(np.int32)
    h=np.tanh((qi['WC_Q']@pool_q).astype(np.float32)*arrays['WC_S']*pool_scale+arrays['BC'])
    h,nxt=step(2,h)
    text=''; ids=[]
    for _ in range(160):
        ids.append(nxt)
        if nxt==3: break
        text+=CHARS[nxt-4]
        h,nxt=step(nxt,h)
    return text,ids

checks=[]
for item in json.loads((ROOT/'data'/'heldout-prompts.json').read_text()):
    reply,ids=generate(item['prompt'])
    checks.append({**item,'reply':reply,'hint_present':item['expected_hint'] in reply})
(MODEL/'evaluation-int8.json').write_text(json.dumps(checks,indent=2))
final_checks=[]
for item in json.loads((ROOT/'data'/'final-test-prompts.json').read_text()):
    reply,ids=generate(item['prompt'])
    final_checks.append({**item,'reply':reply,'hint_present':item['expected_hint'] in reply})
(MODEL/'evaluation-final.json').write_text(json.dumps(final_checks,indent=2))
reference=[]
for prompt in ['hello','what is ram','what is your name']:
    text,ids=generate(prompt)
    reference.append({'prompt':prompt,'tokens':ids[:8],'reply':text})
(MODEL/'reference-int8.json').write_text(json.dumps(reference,indent=2))
np.savez(MODEL/'gru-int8.npz',**arrays)
with (FW/'weights.h').open('w',encoding='ascii') as f:
    f.write('#pragma once\n#include <pgmspace.h>\n#include <stdint.h>\n')
    f.write(f'constexpr int HIDDEN={H}, EMBED={D}, VOCAB={V};\n')
    f.write('const char alphabet[] PROGMEM = '+json.dumps(CHARS)+';\n')
    f.write(f'constexpr int WORD_COUNT={len(WORDS)}, WORD_DIM={WD};\n')
    offsets=[]; pos=0
    for word in WORDS: offsets.append(pos); pos+=len(word)+1
    assert pos<65536
    f.write('const uint16_t WORD_OFFSETS[] PROGMEM = {'+','.join(map(str,offsets))+'};\n')
    f.write('const char WORD_TEXT[] PROGMEM = '+' '.join('"'+word+'\\0"' for word in WORDS)+';\n')
    f.write('const uint8_t REFERENCE_IDS[3][8] PROGMEM = {'+','.join('{'+','.join(map(str,r['tokens']+[3]*(8-len(r['tokens']))))+'}' for r in reference)+'};\n')
    for name,a in arrays.items():
        typ='int8_t' if a.dtype==np.int8 else 'float'
        vals=','.join(str(int(x)) if typ=='int8_t' else f'{x:.8e}f' for x in a.ravel())
        f.write(f'alignas(4) const {typ} {name}[{a.size}] PROGMEM = {{'+vals+'};\n')
info=json.loads((MODEL/'gru-info.json').read_text())
info.update(weight_format='per-row symmetric int8 weights; float32 row scales and biases; int16 recurrent dot-product activations',
            deployed_weight_bytes=sum(a.nbytes for a in arrays.values()),
            quantized_heldout_hint_matches=sum(x['hint_present'] for x in checks),
            final_test_hint_matches=sum(x['hint_present'] for x in final_checks),final_test_count=len(final_checks),
            header_sha256=hashlib.sha256((FW/'weights.h').read_bytes()).hexdigest())
(MODEL/'gru-info.json').write_text(json.dumps(info,indent=2))
print(json.dumps(info,indent=2),flush=True)
print(json.dumps(checks,indent=2),flush=True)
print('FINAL UNSEEN TESTS:',json.dumps(final_checks,indent=2),flush=True)
print('Quantized references:',json.dumps(reference),flush=True)
