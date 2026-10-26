from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs,urlparse
import json,time
ROOT=Path(__file__).resolve().parents[1]
class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    name=''; job_time=0; message=''
    def respond(self,status,data,headers=None):
        payload=json.dumps(data).encode() if isinstance(data,dict) else data
        self.send_response(status)
        self.send_header('Content-Type','application/json' if isinstance(data,dict) else 'text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        for k,v in (headers or {}).items():self.send_header(k,v)
        self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/': return self.respond(200,(ROOT/'web'/'index.html').read_bytes())
        signed='TinyLM=preview' in self.headers.get('Cookie','')
        if path=='/api/session':return self.respond(200,{'signedIn':signed,'ready':True,'name':Handler.name})
        if path=='/api/result':
            reply='ram holds temporary data while a program is running.'
            elapsed=time.monotonic()-Handler.job_time
            return self.respond(200,{'state':'done' if elapsed>.8 else 'generating','reply':reply if elapsed>.8 else reply[:15]})
        return self.respond(404,{'error':'Not found'})
    def do_POST(self):
        form=parse_qs(self.rfile.read(int(self.headers.get('Content-Length',0))).decode())
        if self.path=='/api/signin':
            Handler.name=form.get('name',[''])[0]
            return self.respond(200,{'name':Handler.name},{'Set-Cookie':'TinyLM=preview; Path=/; HttpOnly; SameSite=Strict'})
        if self.path=='/api/signout':return self.respond(200,{'ok':True},{'Set-Cookie':'TinyLM=; Path=/; Max-Age=0'})
        if self.path=='/api/chat':
            if 'TinyLM=preview' not in self.headers.get('Cookie',''):return self.respond(401,{'error':'Sign in first'})
            Handler.job_time=time.monotonic();Handler.message=form.get('message',[''])[0]
            return self.respond(202,{'id':1,'state':'generating'})
        return self.respond(404,{'error':'Not found'})
print('UI QA preview: http://127.0.0.1:8765',flush=True)
ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
