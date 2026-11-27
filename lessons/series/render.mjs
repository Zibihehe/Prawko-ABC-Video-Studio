import {chromium} from 'playwright';
import {mkdir} from 'node:fs/promises';
await mkdir('frames',{recursive:true});await mkdir('rendered',{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:960,height:540},deviceScaleFactor:1});
 let rejectError;const error=new Promise((_,reject)=>{rejectError=reject});error.catch(()=>{});
 page.on('pageerror',e=>{console.error(e);rejectError(e)});
 page.on('console',m=>console.log(m.type(),m.text()));
 const response=await page.goto('http://127.0.0.1:8000/lessons/series/?lesson='+process.env.LESSON+'');
 if(!response?.ok())throw Error('Scene HTTP error');
 await Promise.race([error,page.waitForFunction(()=>window.ready===true,{},{timeout:60000})]);
 for(const t of [0,8,12,17,24]){await page.evaluate(t=>window.frame(t),t);await page.screenshot({path:'rendered/check-'+t+'.png'});}
 for(let i=0;i<720;i++){
  await Promise.race([error,page.evaluate(t=>window.frame(t),i/24)]);
  await page.screenshot({path:'frames/'+String(i).padStart(4,'0')+'.png'});
  if(i%120===0)console.log('Frame',i);
 }
} finally {await browser.close()}
