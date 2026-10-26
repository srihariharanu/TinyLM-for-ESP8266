#pragma once
#include <ESP8266WebServer.h>
#include <DNSServer.h>
extern "C" {
#include <user_interface.h>
}
#include "web_ui.h"

constexpr char AP_SSID[]="TinyLM-Offline";
constexpr char AP_PASSWORD[]="TinyLM8266";
constexpr uint8_t SESSION_LIMIT=4;
constexpr uint32_t SESSION_TTL=30UL*60UL*1000UL;
ESP8266WebServer webServer(80);
DNSServer dnsServer;
IPAddress portalIP(192,168,4,1);
struct PortalSession {
  bool used=false;
  char token[33]={0};
  char name[33]={0};
  char reply[MAX_REPLY+1]={0};
  uint32_t touched=0,jobId=0;
  uint16_t count=0;
  bool done=false;
};
PortalSession sessions[SESSION_LIMIT];
int activeSession=-1;
uint32_t nextJobId=0,jobStarted=0;

String jsonString(const char* text) {
  String out; out.reserve(strlen(text)+8); out+='"';
  for(const char* p=text;*p;p++) {
    unsigned char c=*p;
    if(c=='"' || c=='\\') {out+='\\';out+=(char)c;}
    else if(c=='\n') out+="\\n";
    else if(c=='\r') out+="\\r";
    else if(c=='\t') out+="\\t";
    else if(c>=32) out+=(char)c;
  }
  out+='"'; return out;
}
void sendJSON(int status,const String& body) {
  webServer.sendHeader("Cache-Control","no-store");
  webServer.sendHeader("X-Content-Type-Options","nosniff");
  webServer.keepAlive(false);
  webServer.send(status,"application/json; charset=utf-8",body);
}
void apiError(int status,const char* message) {sendJSON(status,"{\"error\":"+jsonString(message)+"}");}
void expireSessions() {
  uint32_t now=millis();
  for(int i=0;i<SESSION_LIMIT;i++) if(sessions[i].used && i!=activeSession && (uint32_t)(now-sessions[i].touched)>SESSION_TTL) sessions[i].used=false;
}
int currentSession() {
  expireSessions();
  String cookies=webServer.header("Cookie");
  int start=cookies.indexOf("TinyLM=");
  if(start<0) return -1;
  start+=7; int end=cookies.indexOf(';',start);
  String token=end<0?cookies.substring(start):cookies.substring(start,end);
  if(token.length()!=32) return -1;
  for(int i=0;i<SESSION_LIMIT;i++) if(sessions[i].used && token==sessions[i].token) {sessions[i].touched=millis();return i;}
  return -1;
}
void redirectPortal() {
  webServer.sendHeader("Cache-Control","no-store");
  webServer.sendHeader("Location","http://192.168.4.1/",true);
  webServer.keepAlive(false); webServer.send(302,"text/plain","Open TinyLM at http://192.168.4.1/");
}
void servePage() {
  String host=webServer.hostHeader();
  if(host!="192.168.4.1" && host!="192.168.4.1:80") {redirectPortal();return;}
  webServer.sendHeader("Cache-Control","no-store");
  webServer.sendHeader("Content-Encoding","gzip");
  webServer.sendHeader("X-Content-Type-Options","nosniff");
  webServer.sendHeader("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
  webServer.keepAlive(false);
  webServer.send_P(200,PSTR("text/html; charset=utf-8"),(PGM_P)WEB_UI,WEB_UI_SIZE);
}
void sessionInfo() {
  int id=currentSession();
  String out="{\"signedIn\":"; out+=id>=0?"true":"false";
  out+=",\"ready\":";out+=ready?"true":"false";
  if(id>=0) {out+=",\"name\":";out+=jsonString(sessions[id].name);}
  out+='}';sendJSON(200,out);
}
void signIn() {
  if(!ready) {apiError(503,"The model is starting. Try again shortly.");return;}
  String name=webServer.arg("name");name.trim();
  if(name.length()<1 || name.length()>32) {apiError(400,"Enter a name between 1 and 32 characters.");return;}
  for(size_t i=0;i<name.length();i++) if(name[i]<32 || name[i]>126) {apiError(400,"Use English letters for your local display name.");return;}
  int id=currentSession();
  if(id<0) for(int i=0;i<SESSION_LIMIT;i++) if(!sessions[i].used) {id=i;break;}
  if(id<0) {apiError(503,"All four local sessions are in use. Try again later.");return;}
  if(activeSession==id) {apiError(409,"Wait for the current reply to finish.");return;}
  PortalSession& session=sessions[id];session=PortalSession();session.used=true;session.touched=millis();
  name.toCharArray(session.name,sizeof(session.name));
  snprintf(session.token,sizeof(session.token),"%08lx%08lx%08lx%08lx",(unsigned long)os_random(),(unsigned long)os_random(),(unsigned long)os_random(),(unsigned long)os_random());
  webServer.sendHeader("Set-Cookie",String("TinyLM=")+session.token+"; Path=/; HttpOnly; SameSite=Strict; Max-Age=1800");
  sendJSON(200,"{\"name\":"+jsonString(session.name)+"}");
}
void signOut() {
  int id=currentSession();
  if(id>=0) {if(activeSession==id) activeSession=-1;sessions[id]=PortalSession();}
  webServer.sendHeader("Set-Cookie","TinyLM=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0");
  sendJSON(200,"{\"ok\":true}");
}
void beginWebReply() {
  int id=currentSession();
  if(id<0) {apiError(401,"Sign in to start chatting.");return;}
  if(!ready) {apiError(503,"The model is not ready.");return;}
  if(activeSession>=0) {apiError(409,"The board is finishing another reply. Try again in a moment.");return;}
  String message=webServer.arg("message");message.trim();
  if(!message.length() || message.length()>MAX_INPUT) {apiError(400,"Enter a message between 1 and 120 characters.");return;}
  for(size_t i=0;i<message.length();i++) if(message[i]<32 || message[i]>126) {apiError(400,"Please use English letters, numbers and punctuation.");return;}
  PortalSession& session=sessions[id];session.reply[0]=0;session.count=0;session.done=false;
  if(++nextJobId==0) ++nextJobId;
  session.jobId=nextJobId;session.touched=millis();
  prime(message.c_str());activeSession=id;jobStarted=millis();
  sendJSON(202,String("{\"id\":")+session.jobId+",\"state\":\"generating\"}");
}
void webReplyResult() {
  int id=currentSession();
  if(id<0) {apiError(401,"Sign in to continue chatting.");return;}
  String requested=webServer.arg("id");
  if(!requested.length()) {apiError(400,"A reply id is required.");return;}
  for(size_t i=0;i<requested.length();i++) if(requested[i]<'0' || requested[i]>'9') {apiError(400,"Invalid reply id.");return;}
  PortalSession& session=sessions[id];
  if(!session.jobId || (uint32_t)strtoul(requested.c_str(),nullptr,10)!=session.jobId) {apiError(404,"That reply is no longer available. Send your message again.");return;}
  String out;out.reserve(260);out="{\"state\":\"";out+=session.done?"done":"generating";
  out+="\",\"reply\":";out+=jsonString(session.reply);out+='}';sendJSON(200,out);
}
void stepWebReply() {
  if(activeSession<0) return;
  PortalSession& session=sessions[activeSession];
  int next=nextToken();
  if(next==3 || session.count>=MAX_REPLY) {
    session.done=true;session.touched=millis();
    Serial.printf("[WEB_REPLY_DONE chars=%u ms=%lu free_heap=%u]\n",session.count,millis()-jobStarted,ESP.getFreeHeap());
    activeSession=-1;return;
  }
  session.reply[session.count++]=letter(next);session.reply[session.count]=0;
  feed(next);
}
bool startPortal() {
  WiFi.mode(WIFI_AP);WiFi.setSleepMode(WIFI_NONE_SLEEP);
  if(!WiFi.softAPConfig(portalIP,portalIP,IPAddress(255,255,255,0))) return false;
  if(!WiFi.softAP(AP_SSID,AP_PASSWORD,6,false,4)) return false;
  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  if(!dnsServer.start(53,"*",portalIP)) return false;
  webServer.collectHeaders("Cookie");
  webServer.on("/",HTTP_GET,servePage);
  webServer.on("/api/session",HTTP_GET,sessionInfo);
  webServer.on("/api/signin",HTTP_POST,signIn);
  webServer.on("/api/signout",HTTP_POST,signOut);
  webServer.on("/api/chat",HTTP_POST,beginWebReply);
  webServer.on("/api/result",HTTP_GET,webReplyResult);
  webServer.on("/api/status",HTTP_GET,[](){sendJSON(200,String("{\"ready\":")+(ready?"true":"false")+",\"freeHeap\":"+ESP.getFreeHeap()+",\"stations\":"+WiFi.softAPgetStationNum()+",\"busy\":"+(activeSession>=0?"true":"false")+"}");});
  webServer.onNotFound([](){if(webServer.uri().startsWith("/api/")) apiError(404,"Endpoint not found.");else redirectPortal();});
  webServer.begin();
  Serial.printf("[PORTAL ssid=%s url=http://192.168.4.1/ free_heap=%u]\n",AP_SSID,ESP.getFreeHeap());
  return true;
}
void portalLoop() {dnsServer.processNextRequest();webServer.handleClient();stepWebReply();}
