import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {launchBrowser,closeBrowser,finish} from '../../tools/render/browser.js';

const here=path.dirname(fileURLToPath(import.meta.url));
const url='http://127.0.0.1:8862/future/pump-first-layout-study/index.html';
const out=path.join(here,'renders','gallery');
await fs.mkdir(out,{recursive:true});
const views=[
  ['overview','three','all',true,false],['top','top','all',false,false],
  ['pump-water','three','pump',false,false],['gas-water','three','gas',false,false],
  ['electronics','three','electronics',false,false],['mounts','three','structure',false,true],
  ['rear','rear','all',false,false],['funnel','three','funnel',true,false],
  ['enclosure','three','all',true,true],['front-closure','three','all',false,true],
  ['funnel-tooling','three','funnel',true,false]];
let browser;const errors=[];
const viewer=path.join(here,'index.html');
const viewerSHA=createHash('sha256').update(await fs.readFile(viewer)).digest('hex');
try{
  browser=await launchBrowser();const page=await browser.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url,{waitUntil:'networkidle0',timeout:60000});
  await page.waitForSelector('#pump-bay-study[data-ready="true"]',{timeout:60000});
  for(const theme of ['light','dark']){
    await page.evaluate(theme=>{document.documentElement.style.colorScheme=theme;document.body.style.background='transparent';document.documentElement.style.background='transparent'},theme);
    for(const [size,width,height] of [['large',784,470],['small',352,370]]){
      await page.setViewport({width,height:1200,deviceScaleFactor:1});
      await page.addStyleTag({content:`#pump-bay-study .pb-label{font-size:${size==='large'?16:14}px}`});
      for(const [id,view,show,funnel,walls] of views){
        const layout=await page.evaluate(({id,view,show,funnel,walls,height})=>{
          const s=window.pumpBayStudy;Object.assign(s.state,{arrangement:id==='front-closure'?'factory':id==='funnel-tooling'?'tooling':'candidate',view,show,funnel,walls,inspect:'',roof:'ghost',labels:true});
          s.build();
          const stage=document.querySelector('.pb-stage');stage.style.height=height+'px';stage.style.background='transparent';
          s.orient();s.setSelection();s.resize();
          const box=stage.getBoundingClientRect();
          const labels=[...stage.querySelectorAll('.pb-label')].map(e=>{
            const b=e.getBoundingClientRect();return {text:e.textContent,left:b.left,right:b.right,top:b.top,bottom:b.bottom};
          });
          const problems=[];
          for(const a of labels)if(a.left<box.left-1||a.right>box.right+1||a.top<box.top-1||a.bottom>box.bottom+1)problems.push('Clipped label: '+a.text);
          for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
            const a=labels[i],b=labels[j];
            if(Math.min(a.right,b.right)>Math.max(a.left,b.left)&&Math.min(a.bottom,b.bottom)>Math.max(a.top,b.top))problems.push('Overlapping labels: '+a.text+' / '+b.text);
          }
          return problems;
        },{id,view,show,funnel,walls,height});
        errors.push(...layout.map(e=>`${id}/${theme}/${size}: ${e}`));
        await (await page.$('.pb-stage')).screenshot({path:path.join(out,`${id}-${theme}-${size}.png`),omitBackground:true});
      }
    }
  }
  if(createHash('sha256').update(await fs.readFile(viewer)).digest('hex')!==viewerSHA)
    errors.push('Native viewer changed during gallery rendering.');
  await fs.writeFile(path.join(out,'check.json'),JSON.stringify({pass:!errors.length,errors,
    viewer_sha256:viewerSHA,source_sha256:createHash('sha256').update(await fs.readFile(fileURLToPath(import.meta.url))).digest('hex'),
    views:views.length,themes:2,sizes:2},null,2)+'\n');
  console.log(JSON.stringify({errors,images:views.length*4}));
}finally{await closeBrowser(browser)}
finish(errors.length?1:0);
