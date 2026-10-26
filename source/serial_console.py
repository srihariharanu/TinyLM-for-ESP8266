from pathlib import Path
import argparse, json, re, sys, time
import serial
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
ROOT=Path(__file__).resolve().parent
(ROOT/'logs').mkdir(exist_ok=True)
p=argparse.ArgumentParser(description='Offline ESP8266 recurrent neural language model console')
p.add_argument('--port',required=True); p.add_argument('--test',action='store_true')
a=p.parse_args()
s=serial.Serial(); s.port=a.port; s.baudrate=115200; s.timeout=.2; s.dtr=False; s.rts=False; s.open()
transcript=[]

def receive(boot=False,timeout=90):
    raw=bytearray(); displayed=False if boot else True
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        chunk=s.read(max(1,s.in_waiting))
        if chunk:
            raw.extend(chunk)
            if not displayed:
                pos=raw.find(b'RecurrentLM:')
                if pos>=0:
                    raw=raw[pos:]; displayed=True
                    print(raw.decode('ascii',errors='replace'),end='',flush=True)
            else: print(chunk.decode('ascii',errors='replace'),end='',flush=True)
        if b'[ERROR' in raw: raise RuntimeError(raw.decode('ascii',errors='replace'))
        if b'[READY]' in raw:
            text=raw.decode('ascii',errors='replace')
            transcript.append(text)
            return text
    raise TimeoutError('Board did not finish its reply. Check COM port and power.')

try:
    s.rts=True; time.sleep(.15); s.rts=False
    boot=receive(boot=True)
    if a.test:
        refs=json.loads((ROOT/'model'/'evaluation-final.json').read_text())
        prompts=[refs[i] for i in [1,2,3,4,7,8,11]]
        results={'reference_checks_passed':all(f'[REFERENCE {i} PASS]' in boot for i in range(3)),'responses':[]}
        for item in prompts:
            q=item['prompt']; print('\nYou: '+q,flush=True); transcript.append('\nYou: '+q+'\n')
            s.write((q+'\n').encode('ascii')); response=receive()
            match=re.search(r'Tiny: (.*?)\r?\n\[REPLY_DONE',response,re.S)
            reply=match.group(1).replace('\r','') if match else ''
            timing=re.search(r'chars=(\d+) input_ms=(\d+) generation_ms=(\d+) free_heap=(\d+)',response)
            row={'prompt':q,'reply':reply,'computer_reply':item['reply'],
                 'matches_computer':reply==item['reply'],'expected_hint':item['expected_hint'],
                 'hint_present':item['expected_hint'] in reply}
            if timing:
                n,im,gm,heap=map(int,timing.groups())
                row.update(characters=n,input_ms=im,generation_ms=gm,free_heap=heap,
                           characters_per_second=round(n*1000/max(1,gm),2))
            results['responses'].append(row)
            (ROOT/'logs'/'device-test.json').write_text(json.dumps(results,indent=2),encoding='ascii')
        (ROOT/'logs'/'device-test.txt').write_text(''.join(transcript),encoding='utf-8')
        if not results['reference_checks_passed'] or not all(x['matches_computer'] for x in results['responses']):
            raise RuntimeError('Device and computer inference disagree. See logs/device-test.json.')
        print('\nDEVICE INFERENCE TEST PASSED. Relevance is reported separately in device-test.json.')
    else:
        print('\nSmall experimental neural model. Ask a short question; /exit closes the console.')
        while True:
            q=input('\nYou: ')
            if q.strip().lower() in ('/exit','/quit'): break
            if not q.strip(): continue
            if len(q)>120: print('(Input limited to the first 120 characters.)')
            s.write((q[:120]+'\n').encode('ascii',errors='replace')); receive()
except KeyboardInterrupt:
    print('\nConsole closed.')
finally:
    s.close()
    if transcript: (ROOT/'logs'/'latest-console.txt').write_text(''.join(transcript),encoding='utf-8')
