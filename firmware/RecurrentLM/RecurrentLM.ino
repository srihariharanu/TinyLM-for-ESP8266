#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <math.h>
#include <string.h>
#include "weights.h"
constexpr int MAX_INPUT=120, MAX_REPLY=160;
static_assert(HIDDEN%4==0 && EMBED%4==0,"Packed dot products require multiples of four");
float state[HIDDEN], inputGates[3*HIDDEN], recurrentGates[3*HIDDEN];
int16_t hq[HIDDEN], eq[EMBED];
float pooled[WORD_DIM];
int16_t pooledQ[WORD_DIM];
uint16_t wordIds[61];
float wordAttention[61];
char input[MAX_INPUT+1];
int inputLength=0;
bool ready=false;
float readf(const float* p,int i) { return pgm_read_float(p+i); }
int32_t dotFlash(const int8_t* row,const int16_t* x,int n) {
  int32_t sum=0;
  for(int j=0;j<n;j+=4) {
    uint32_t w=pgm_read_dword(row+j);
    sum+=(int8_t)(w&255)*x[j];
    sum+=(int8_t)((w>>8)&255)*x[j+1];
    sum+=(int8_t)((w>>16)&255)*x[j+2];
    sum+=(int8_t)((w>>24)&255)*x[j+3];
  }
  return sum;
}
void quantizeState() {
  for(int j=0;j<HIDDEN;j++) hq[j]=(int16_t)lroundf(fmaxf(-1.0f,fminf(1.0f,state[j]))*32767.0f);
}
float sigmoid(float x) { return 1.0f/(1.0f+expf(-fmaxf(-30.0f,fminf(30.0f,x)))); }
int token(char c) {
  if(c>='A' && c<='Z') c+='a'-'A';
  for(int i=4;i<VOCAB;i++) if(pgm_read_byte(alphabet+i-4)==c) return i;
  return 4;
}
char letter(int id) { return pgm_read_byte(alphabet+id-4); }
void feed(int id) {
  for(int d=0;d<EMBED;d++) eq[d]=(int8_t)pgm_read_byte(E_Q+id*EMBED+d);
  float es=readf(E_S,id);
  quantizeState();
  for(int j=0;j<3*HIDDEN;j++) {
    inputGates[j]=(float)dotFlash(WI_Q+j*EMBED,eq,EMBED)*readf(WI_S,j)*es+readf(BI,j);
    recurrentGates[j]=(float)dotFlash(WH_Q+j*HIDDEN,hq,HIDDEN)*(readf(WH_S,j)/32767.0f)+readf(BH,j);
    if((j&63)==0) yield();
  }
  for(int j=0;j<HIDDEN;j++) {
    float r=sigmoid(inputGates[j]+recurrentGates[j]);
    float z=sigmoid(inputGates[HIDDEN+j]+recurrentGates[HIDDEN+j]);
    float n=tanhf(inputGates[2*HIDDEN+j]+r*recurrentGates[2*HIDDEN+j]);
    state[j]=(1.0f-z)*n+z*state[j];
  }
}
int nextToken() {
  quantizeState();
  int best=3; float score=-1e30f;
  for(int k=3;k<VOCAB;k++) {
    float s=(float)dotFlash(WO_Q+k*HIDDEN,hq,HIDDEN)*(readf(WO_S,k)/32767.0f)+readf(BO,k);
    if(s>score) {score=s;best=k;}
  }
  return best;
}
int compareWord(const char* word,int id) {
  uint16_t offset=pgm_read_word(WORD_OFFSETS+id);
  for(int i=0;;i++) {
    char stored=pgm_read_byte(WORD_TEXT+offset+i);
    if(word[i]!=stored) return (int)(unsigned char)word[i]-(int)(unsigned char)stored;
    if(!stored) return 0;
  }
}
int wordId(const char* word) {
  int lo=2,hi=WORD_COUNT-1;
  while(lo<=hi) {
    int mid=(lo+hi)/2,cmp=compareWord(word,mid);
    if(cmp==0) return mid;
    if(cmp>0) lo=mid+1; else hi=mid-1;
  }
  return 1;
}
void prime(const char* prompt) {
  int count=0,length=0; char word[MAX_INPUT+1];
  for(int i=0;;i++) {
    char c=prompt[i]; if(c>='A' && c<='Z') c+='a'-'A';
    if((c>='a' && c<='z') || (c>='0' && c<='9')) {
      if(length<MAX_INPUT) word[length++]=c;
    } else if(length) {
      word[length]=0; if(count<61) wordIds[count++]=wordId(word); length=0;
    }
    if(!c) break;
  }
  if(!count) wordIds[count++]=1;
  float maximum=-1e30f,total=0;
  for(int i=0;i<count;i++) {wordAttention[i]=readf(WG,wordIds[i]);maximum=fmaxf(maximum,wordAttention[i]);}
  for(int i=0;i<count;i++) {wordAttention[i]=expf(wordAttention[i]-maximum);total+=wordAttention[i];}
  memset(pooled,0,sizeof(pooled));
  for(int i=0;i<count;i++) {
    int id=wordIds[i]; float scale=wordAttention[i]/total*readf(WE_S,id);
    for(int d=0;d<WORD_DIM;d++) pooled[d]+=(int8_t)pgm_read_byte(WE_Q+id*WORD_DIM+d)*scale;
  }
  float poolScale=1e-9f;
  for(int d=0;d<WORD_DIM;d++) poolScale=fmaxf(poolScale,fabsf(pooled[d])/32767.0f);
  for(int d=0;d<WORD_DIM;d++) pooledQ[d]=(int16_t)lroundf(pooled[d]/poolScale);
  for(int j=0;j<HIDDEN;j++) state[j]=tanhf((float)dotFlash(WC_Q+j*WORD_DIM,pooledQ,WORD_DIM)*readf(WC_S,j)*poolScale+readf(BC,j));
  feed(2);
}
bool verify() {
  const char* prompts[]={"hello","what is ram","what is your name"};
  bool all=true;
  for(int p=0;p<3;p++) {
    prime(prompts[p]); bool ok=true;
    for(int i=0;i<8;i++) {
      int actual=nextToken(); int expected=pgm_read_byte(&REFERENCE_IDS[p][i]);
      if(actual!=expected) {Serial.printf("[MISMATCH prompt=%d position=%d expected=%d actual=%d]\n",p,i,expected,actual);ok=false;break;}
      if(actual==3) break;
      feed(actual);
    }
    Serial.printf("[REFERENCE %d %s]\n",p,ok?"PASS":"FAIL");
    all=all && ok;
  }
  return all;
}
void respond(const char* prompt) {
  unsigned long begin=millis(); prime(prompt); unsigned long primed=millis();
  Serial.print("Tiny: "); int count=0;
  for(;count<MAX_REPLY;count++) {
    int id=nextToken(); if(id==3) break;
    Serial.print(letter(id)); feed(id); yield();
  }
  unsigned long end=millis();
  Serial.printf("\n[REPLY_DONE chars=%d input_ms=%lu generation_ms=%lu free_heap=%u]\n",count,primed-begin,end-primed,ESP.getFreeHeap());
  Serial.println("[READY]");
}
#include "portal.h"

void setup() {
  WiFi.persistent(false); WiFi.mode(WIFI_OFF);
  Serial.begin(115200); delay(500);
  Serial.println("\nRecurrentLM: learned word encoder and int8 GRU neural language model. Local ESP8266 inference with offline Wi-Fi portal.");
  Serial.printf("[MODEL hidden=%d embedding=%d vocabulary=%d cpu_mhz=%u free_heap=%u wifi=local-ap]\n",HIDDEN,EMBED,VOCAB,ESP.getCpuFreqMHz(),ESP.getFreeHeap());
  ready=verify();
  if(!ready) {Serial.println("[ERROR Neural inference check failed; chat disabled]");return;}
  if(!startPortal()) {Serial.println("[ERROR Offline Wi-Fi portal could not start]");return;}
  Serial.println("Type a message and press Enter. /reset clears the current input.");
  Serial.println("[READY]");
}
void loop() {
  if(ready) portalLoop();
  if(!ready) {delay(20);return;}
  while(Serial.available()) {
    char c=Serial.read(); if(c=='\r') continue;
    if(c=='\n') {
      input[inputLength]=0;
      if(strcmp(input,"/reset")==0) {Serial.println("[Input cleared. Each message starts a new recurrent state.]");Serial.println("[READY]");}
      else if(inputLength>0) {if(activeSession>=0) {Serial.println("[BUSY Mobile reply in progress]");Serial.println("[READY]");} else respond(input);}
      else Serial.println("[READY]");
      inputLength=0;
    } else if(c>=32 && c<=126 && inputLength<MAX_INPUT) input[inputLength++]=c;
  }
  delay(1);
}
