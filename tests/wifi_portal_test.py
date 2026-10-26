from pathlib import Path
import http.client, json, time, gzip, urllib.parse, socket, struct, subprocess, traceback
from wifi_link import TemporaryWifi
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'logs').mkdir(exist_ok=True)
checks=[]
def check(name,condition,detail=None):
    checks.append({'check':name,'pass':bool(condition),'detail':detail})
    print(name+': '+('PASS' if condition else 'FAIL'),flush=True)
    if not condition:raise AssertionError(name)
class Client:
    def __init__(self):self.cookie=''
    def request(self,path,data=None,host=None):
        connection=http.client.HTTPConnection('192.168.4.1',80,timeout=3)
        headers={'Connection':'close'}
        if self.cookie:headers['Cookie']=self.cookie
        if host:headers['Host']=host
        body=None
        if data is not None:body=urllib.parse.urlencode(data);headers['Content-Type']='application/x-www-form-urlencoded'
        try:
            connection.request('POST' if data is not None else 'GET',path,body,headers)
            response=connection.getresponse();payload=response.read();heads=dict(response.getheaders())
            cookie=response.getheader('Set-Cookie')
            if cookie:self.cookie=cookie.split(';',1)[0]
            if response.getheader('Content-Encoding')=='gzip':payload=gzip.decompress(payload)
            try:result=json.loads(payload)
            except (ValueError,UnicodeDecodeError):result=payload
            return response.status,result,heads
        finally:connection.close()
def dns_check():
    query=struct.pack('!HHHHHH',4321,0x100,1,0,0,0)+b'\x08anything\x07offline\x04test\x00'+struct.pack('!HH',1,1)
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
        s.settimeout(2);s.sendto(query,('192.168.4.1',53));answer,_=s.recvfrom(1024)
    return b'\xc0\xa8\x04\x01' in answer
results={'checks':checks}
try:
    with TemporaryWifi() as wifi:
        results['temporary_wifi_profile']=True
        c=Client();deadline=time.monotonic()+10
        while True:
            try:status,data,_=c.request('/api/status');break
            except OSError:
                if time.monotonic()>deadline:raise
                time.sleep(.3)
        check('board_ready',status==200 and data['ready'],data)
        status,page,headers=c.request('/')
        check('embedded_page_matches_source',status==200 and page==(ROOT/'web'/'index.html').read_bytes())
        check('author_credit_on_board',b'Sri Hariharan U' in page and b'srihariharanu@gmail.com' in page)
        status,_,headers=c.request('/generate_204',host='connectivitycheck.gstatic.com')
        check('captive_portal_redirect',status==302 and headers.get('Location')=='http://192.168.4.1/')
        check('wildcard_dns',dns_check())
        status,_,_=c.request('/api/chat',{'message':'hello'})
        check('chat_requires_local_signin',status==401)
        status,data,_=c.request('/api/signin',{'name':'Sri Hariharan U'})
        check('local_signin',status==200 and data['name']=='Sri Hariharan U')
        status,data,_=c.request('/api/session')
        check('session_cookie_recognized',status==200 and data['signedIn'])
        status,_,_=c.request('/api/chat',{'message':'x'*121})
        check('input_limit_enforced',status==400)
        reference=json.loads((ROOT/'model'/'reference-int8.json').read_text())
        expected=next(x['reply'] for x in reference if x['prompt']=='what is ram')
        status,job,_=c.request('/api/chat',{'message':'what is ram'})
        check('chat_accepted',status==202)
        status,state,_=c.request('/api/status')
        check('server_responsive_while_generating',status==200 and state['busy'],state)
        status,_,_=c.request('/api/chat',{'message':'hello'})
        check('simultaneous_model_job_rejected',status==409)
        other=Client();status,_,_=other.request('/api/signin',{'name':'Other local session'})
        check('second_session',status==200)
        status,_,_=other.request('/api/result?id='+str(job['id']))
        check('reply_isolation',status==404)
        deadline=time.monotonic()+15
        while True:
            status,result,_=c.request('/api/result?id='+str(job['id']))
            check_ok=status==200
            if not check_ok:raise RuntimeError('Result endpoint failed')
            if result['state']=='done':break
            if time.monotonic()>deadline:raise TimeoutError('Reply did not complete')
            time.sleep(.2)
        check('wifi_reply_matches_neural_reference',result['reply']==expected,result['reply'])
        check('dns_responsive_after_generation',dns_check())
        status,data,_=c.request('/api/status')
        check('healthy_heap_after_chat',status==200 and data['freeHeap']>18000,data)
        results['post_chat_status']=data
        other.request('/api/signout',{})
        status,_,_=c.request('/api/signout',{})
        status,info,_=c.request('/api/session')
        check('signout_invalidates_session',status==200 and not info['signedIn'])
        live=subprocess.run(['node',str(ROOT/'tests'/'live_ui_test.cjs')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=35)
        (ROOT/'logs'/'live-ui-test-run.txt').write_text(live.stdout+live.stderr,encoding='utf-8')
        check('real_board_mobile_browser_chat',live.returncode==0,live.stdout[-700:]+live.stderr[-700:])
    results['original_wifi_restored']=True
except BaseException as error:
    results['error']=repr(error);traceback.print_exc()
finally:
    (ROOT/'logs'/'wifi-portal-test.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
if results.get('error'):raise SystemExit(1)
print('OFFLINE WIFI PORTAL TEST PASSED; original Wi-Fi restored.',flush=True)
