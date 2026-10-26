const fs=require('fs');
const path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
for(const name of ['tmp','logs'])fs.mkdirSync(path.join(root,name),{recursive:true});
(async()=>{
 const context=await chromium.launchPersistentContext(path.join(root,'tmp','browser-profile'),{
 ...(process.env.BROWSER_EXECUTABLE_PATH ? {executablePath:process.env.BROWSER_EXECUTABLE_PATH} : {}),headless:true,
 viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true,
 args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check','--disable-crash-reporter','--crash-dumps-dir='+path.join(root,'tmp','crashes')],
 env:{...process.env,TEMP:path.join(root,'tmp'),TMP:path.join(root,'tmp')}
 });
 const page=await context.newPage();const errors=[];const external=[];
 page.on('pageerror',error=>errors.push(error.message));
 await page.route('**/*',route=>{const host=new URL(route.request().url()).hostname;if(host==='127.0.0.1')return route.continue();external.push(route.request().url());return route.abort();});
 const checks=[];
 try{
  await page.goto('http://127.0.0.1:8765/');
  await page.locator('#signin').waitFor({state:'visible'});
  await page.screenshot({path:path.join(root,'logs','mobile-signin.png'),fullPage:true});
  checks.push({check:'mobile_signin_no_horizontal_overflow',pass:await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)});
  await page.locator('#name').fill('Sri Hariharan U');await page.locator('#signin-button').click();
  await page.locator('#chat').waitFor({state:'visible'});
  checks.push({check:'local_signin',pass:await page.locator('#session-name').innerText()==='Sri Hariharan U'});
  checks.push({check:'author_credit',pass:await page.locator('#chat a[href="mailto:srihariharanu@gmail.com"]').count()===1});
  await page.locator('#message').fill('what is ram');await page.locator('#send').click();
  await page.locator('#state-label').filter({hasText:'On-device model'}).waitFor();
  await page.waitForFunction(()=>document.querySelector('.assistant .bubble')?.textContent==='ram holds temporary data while a program is running.');
  checks.push({check:'reply_polling_and_display',pass:true});
  await page.screenshot({path:path.join(root,'logs','mobile-chat.png'),fullPage:true});
  for(const size of [{width:320,height:568},{width:390,height:844},{width:768,height:1024}]){
   await page.setViewportSize(size);
   const details=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
   checks.push({check:'chat_layout_'+size.width,pass:details.scroll<=details.width,...details});
  }
  await page.reload();await page.locator('#chat').waitFor({state:'visible'});checks.push({check:'session_restored_on_reload',pass:true});
  await page.locator('#signout').click();await page.locator('#signin').waitFor({state:'visible'});checks.push({check:'signout',pass:true});
  checks.push({check:'no_remote_assets',pass:external.length===0});checks.push({check:'no_browser_errors',pass:errors.length===0,errors});
  fs.writeFileSync(path.join(root,'logs','web-ui-test.json'),JSON.stringify({checks,external},null,2));
  console.log(JSON.stringify(checks,null,2));
  if(checks.some(x=>!x.pass))process.exitCode=1;
 }finally{await context.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
