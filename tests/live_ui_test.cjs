const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
for(const name of ['tmp','logs'])fs.mkdirSync(path.join(root,name),{recursive:true});
(async()=>{
 const context=await chromium.launchPersistentContext(path.join(root,'tmp','live-browser-profile'),{...(process.env.BROWSER_EXECUTABLE_PATH ? {executablePath:process.env.BROWSER_EXECUTABLE_PATH} : {}),headless:true,viewport:{width:390,height:844},isMobile:true,hasTouch:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--disable-crash-reporter'],env:{...process.env,TEMP:path.join(root,'tmp'),TMP:path.join(root,'tmp')}});
 const page=await context.newPage();let errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>new URL(r.request().url()).hostname==='192.168.4.1'?r.continue():r.abort());
 try{
  await page.goto('http://192.168.4.1/',{timeout:10000});
  await page.locator('#signin').waitFor({state:'visible',timeout:5000});
  await page.locator('#name').fill('Sri Hariharan U');await page.locator('#signin-button').click();
  await page.locator('#chat').waitFor({state:'visible',timeout:5000});
  await page.locator('#message').fill('what is ram');await page.locator('#send').click();
  await page.waitForFunction(()=>document.querySelector('.assistant .bubble')?.textContent==='ram holds temporary data while a program is running.',null,{timeout:15000});
  await page.waitForFunction(()=>document.getElementById('send').disabled===false);
  await page.screenshot({path:path.join(root,'logs','live-mobile-chat.png'),fullPage:true});
  await page.locator('#signout').click();await page.locator('#signin').waitFor({state:'visible',timeout:5000});
  const result={actual_esp8266_page:true,signin:true,real_neural_reply:true,signout:true,browser_errors:errors};
  fs.writeFileSync(path.join(root,'logs','live-ui-test.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
  if(errors.length)process.exitCode=1;
 }finally{await context.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
