const { chromium } = require(process.env.PROVOWARE_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('fs');
const path = require('path');
const output=process.env.PROVOWARE_QA_OUTPUT || fs.mkdtempSync('/tmp/naqya-ui-evidence-');
fs.mkdirSync(output,{recursive:true});
const {spawn}=require('child_process');
const origin='http://127.0.0.1:18765';
(async()=>{
 const project=fs.mkdtempSync('/tmp/naqya-ui-case-');
 const server=spawn(process.env.PROVOWARE_PYTHON || 'python3',['-S','app/server.py','--no-browser'],{cwd:path.resolve(__dirname,'../..'),env:{...process.env,PROVOWARE_PORT:'18765',PROVOWARE_PROJECT_PATH:project},stdio:'ignore'});
 await new Promise(r=>setTimeout(r,800));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const results=[];
 try {
 for(const scale of [100,150,200]) {
  const context=await browser.newContext({viewport:{width:800,height:600}});
  await context.request.post(origin+'/api/settings',{data:{font_scale:1}});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const result={scale,viewport:[800,600],checks:[],errors};
  try {
   await page.goto(origin+'/index.html');await page.waitForFunction(()=>document.querySelector('#startStatus').textContent==='Bereit');
   for(let i=0;i<(scale-100)/10;i++)await page.locator('#fontUp').click();
   for(let i=0;i<(scale-100)/10;i++)await page.locator('#zoomIn').click();
   await page.waitForTimeout(100);
   result.font=await page.locator('#fontValue').textContent();result.areaZoom=await page.locator('#zoomValue').textContent();
   await page.screenshot({path:`${output}/naqya-${scale}-overview.png`});
   result.layout=await page.evaluate(()=>({width:innerWidth,height:innerHeight,horizontal:document.documentElement.scrollWidth>innerWidth+2,navHorizontal:document.querySelector('#mainNav').scrollWidth>document.querySelector('#mainNav').clientWidth+2}));
   await page.locator('[data-view="memo"]').click();
   const title=`QA ${scale} Prozent`;
   await page.locator('#memoForm [name="title"]').fill(title);
   await page.locator('#memoForm [name="body"]').fill('Isolierter Bedienungstest');
   await page.locator('#memoForm button.primary').click();
   await page.locator('.item h4').filter({hasText:title}).waitFor();result.checks.push('Memo speichern');
   const card=page.locator('.item').filter({has:page.locator('h4',{hasText:title})});
   await card.locator('[data-edit-memo]').click();
   await page.locator('#memoForm [name="body"]').fill('Bearbeitet');await page.locator('#memoForm button.primary').click();
   await card.locator('p').filter({hasText:'Bearbeitet'}).waitFor();result.checks.push('Memo bearbeiten');
   await card.locator('[data-trash-memo]').click();
   await page.waitForFunction(t=>![...document.querySelectorAll('.item h4')].some(e=>e.textContent===t),title);
   await page.locator('[data-view="trash"]').click();
   await page.locator('.item').filter({has:page.locator('h4',{hasText:title})}).locator('[data-restore]').click();
   await page.locator('[data-view="memo"]').click();await page.locator('.item h4').filter({hasText:title}).waitFor();result.checks.push('Papierkorb und Wiederherstellen');
   await page.screenshot({path:`${output}/naqya-${scale}-memo.png`});
   result.pass=!result.layout.horizontal&&!result.layout.navHorizontal&&!errors.length&&result.font.includes(String(scale))&&result.areaZoom.includes(String(scale));
  }catch(e){result.pass=false;result.failure=e.message;await page.screenshot({path:`${output}/naqya-${scale}-failure.png`}).catch(()=>{});}
  results.push(result);await context.close();
 }
 }finally{await browser.close();server.kill();await new Promise(r=>server.once('exit',r));fs.rmSync(project,{recursive:true,force:true});}
 fs.writeFileSync(path.join(output,'naqya-results.json'),JSON.stringify(results,null,2));
 console.log(JSON.stringify(results,null,2));process.exitCode=results.every(x=>x.pass)?0:1;
})().catch(e=>{console.error(e);process.exitCode=1});
