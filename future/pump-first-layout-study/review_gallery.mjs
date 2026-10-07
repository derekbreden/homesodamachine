import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {launchBrowser,closeBrowser,finish} from '../../tools/render/browser.js';

const here=path.dirname(fileURLToPath(import.meta.url));
const [fragment,preview]=process.argv.slice(2);
if(!fragment||!preview)throw new Error('Provide the fragment and its sandboxed preview.');
const out=path.join(here,'renders','gallery');
await fs.mkdir(out,{recursive:true});
const errors=[],checks=[];let browser;
try{
  browser=await launchBrowser();
  const page=await browser.newPage();
  page.on('pageerror',error=>errors.push(String(error)));
  await page.goto(pathToFileURL(preview).href,{waitUntil:'networkidle0'});
  const frame=page.frames().find(f=>f.parentFrame());
  await frame.waitForSelector('#pump-bay-native-gallery [data-view]');
  const views=await frame.$$eval('[data-view] option',options=>options.map(o=>o.value));
  for(const width of [320,736]){
    await page.setViewport({width,height:900,deviceScaleFactor:1});
    for(const theme of ['light','dark']){
      await frame.evaluate(theme=>document.documentElement.style.colorScheme=theme,theme);
      for(const view of views){
        await frame.select('[data-view]',view);
        await frame.waitForFunction(()=>{
          const image=document.querySelector('[data-scene]');
          return image.complete&&image.naturalWidth>0;
        });
        const result=await frame.evaluate(()=>{
          const root=document.getElementById('pump-bay-native-gallery');
          const image=root.querySelector('[data-scene]'),picker=root.querySelector('[data-view]');
          return {view:picker.value,width:root.clientWidth,scrollWidth:document.documentElement.scrollWidth,
                  viewport:innerWidth,imageWidth:image.naturalWidth,imageHeight:image.naturalHeight,
                  alt:image.alt,readings:root.querySelector('[data-readings]').textContent,
                  selectedSavedView:window.openai?.widgetState?.modelContent?.view};
        });
        result.pass=result.view===view&&result.scrollWidth<=result.viewport&&Boolean(result.alt);
        checks.push({width,theme,...result});
        if(!result.pass)errors.push(JSON.stringify(result));
      }
      await frame.select('[data-view]','overview');
      await page.screenshot({path:path.join(out,`qa-${theme}-${width}.png`),fullPage:true});
    }
  }
  await frame.evaluate(()=>window.dispatchEvent(new CustomEvent('openai:set_globals',{
    detail:{globals:{widgetState:{modelContent:{view:'top'}}}}
  })));
  const restored=await frame.$eval('[data-view]',e=>e.value);
  checks.push({action:'restore-selection',view:restored,pass:restored==='top'});
  if(restored!=='top')errors.push('Selection state did not restore.');
  const raw=await fs.readFile(fragment);
  const report={pass:!errors.length,errors,checks,fragment_sha256:createHash('sha256').update(raw).digest('hex'),
                fragment_bytes:raw.length,source_sha256:createHash('sha256').update(await fs.readFile(fileURLToPath(import.meta.url))).digest('hex')};
  await fs.writeFile(path.join(out,'inline-check.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({pass:report.pass,checks:checks.length,bytes:raw.length,errors}));
}finally{await closeBrowser(browser)}
finish(errors.length?1:0);
