import {chromium} from 'playwright';
import {mkdir} from 'node:fs/promises';
await mkdir('frames',{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:960,height:540},deviceScaleFactor:1});
 page.on('pageerror',e=>console.error(e));
 await page.goto('http://127.0.0.1:8000/three/');
 await page.waitForFunction(()=>window.ready===true,{},{timeout:90000});
 for(let i=0;i<720;i++){
  await page.evaluate(t=>window.frame(t),i/24);
  await page.screenshot({path:'frames/'+String(i).padStart(4,'0')+'.png'});
  if(i%120===0)console.log('Frame',i);
 }
} finally {await browser.close()}
