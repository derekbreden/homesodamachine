import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {launchBrowser,closeBrowser,frameBuffer,finish} from '../../tools/render/browser.js';

const here=path.dirname(fileURLToPath(import.meta.url));
const url=process.env.PUMP_STUDY_URL || 'http://127.0.0.1:8862/future/pump-first-layout-study/index.html';
const out=path.join(here,'renders');
await fs.mkdir(out,{recursive:true});
let browser;
const errors=[];const checks=[];
const viewerSHA=createHash('sha256').update(await fs.readFile(path.join(here,'index.html'))).digest('hex');
try{
  browser=await launchBrowser();
  const page=await browser.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('requestfailed',req=>errors.push(req.url()+': '+req.failure()?.errorText));
  await page.setViewport({width:1250,height:1000,deviceScaleFactor:1});
  await page.goto(url,{waitUntil:'networkidle0',timeout:60000});
  await page.waitForSelector('#pump-bay-study[data-ready="true"]',{timeout:60000});
  for(const [name,view,show,funnel,walls] of [
    ['overview','three','all',true,false],['top','top','all',false,false],
    ['pump-water','three','pump',false,false],['gas-water','three','gas',false,false],
    ['electronics','three','electronics',false,false],['mounts','three','structure',false,true],
    ['rear','rear','all',false,false],['funnel','three','funnel',true,false],
    ['enclosure','three','all',true,true],['water-side','west','all',false,false],
    ['electrical-side','east','all',false,false]]){
    const result=await page.evaluate(({view,show,funnel,walls})=>{
      const a=window.pumpBayStudy;
      a.state.view=view;a.state.show=show;a.state.funnel=funnel;a.state.walls=walls;a.state.inspect='';
      document.querySelector('.pb-stage').style.height='700px';
      a.orient();a.setSelection();a.renderer.render(a.scene,a.camera);
      return {image:a.renderer.domElement.toDataURL('image/png'),visible:a.parts.filter(p=>p.object.visible).length,
              parts:a.parts.map(p=>({id:p.id,label:p.label,detail:p.detail,role:p.role}))};
    },{view,show,funnel,walls});
    await page.$eval('.pb-stage',e=>e.style.background='var(--background)');
    await (await page.$('.pb-stage')).screenshot({path:path.join(out,name+'.png')});
    if(name==='overview')await fs.writeFile(path.join(out,'components.json'),JSON.stringify(result.parts,null,2)+'\n');
    checks.push({name,visible:result.visible});
  }
  for(const width of [320,736]){
    await page.setViewport({width,height:1150,deviceScaleFactor:1});
    const result=await page.evaluate(()=>{
      const a=window.pumpBayStudy;
      document.querySelector('.pb-stage').style.height='';a.state.view='three';a.state.show='all';a.state.funnel=true;a.state.inspect='';a.orient();a.setSelection();
      return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,canvas:document.querySelector('canvas').clientWidth,
              controls:[...document.querySelectorAll('select,button,input')].map(e=>({type:e.type,x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right}))};
    });
    checks.push({width,...result});
    if(result.scrollWidth>result.viewport||result.controls.some(c=>c.x<0||c.right>result.viewport+1))errors.push('Controls overflow at '+width+'px');
    await page.screenshot({path:path.join(out,'qa-'+width+'.png'),fullPage:true});
  }
  await page.select('[data-control="arrangement"]','current');
  checks.push(await page.evaluate(()=>({action:'current',state:window.pumpBayStudy.state.arrangement,readout:document.querySelector('[data-readout]').textContent})));
  await page.select('[data-control="arrangement"]','candidate');
  await page.select('[data-control="inspect"]','g-ganen-pump');
  await page.click('[data-action="frame"]');
  checks.push(await page.evaluate(()=>({action:'inspect-pump',selection:window.pumpBayStudy.state.inspect,zoom:window.pumpBayStudy.camera.zoom,detail:document.querySelector('[data-detail]').textContent})));
  await page.select('[data-control="inspect"]','psu');
  const supply=await page.$eval('[data-detail]',e=>e.textContent);
  checks.push({action:'supply-limit',pass:supply.includes('Installation clearance unresolved'),detail:supply});
  if(!supply.includes('Installation clearance unresolved'))errors.push('Supply installation limitation missing');
  for(const arrangement of ['factory','tooling']){
    await page.select('[data-control="arrangement"]',arrangement);
    const result=await page.evaluate(()=>({arrangement:window.pumpBayStudy.state.arrangement,
      ids:window.pumpBayStudy.parts.map(p=>p.id),visible:window.pumpBayStudy.parts.filter(p=>p.object.visible).map(p=>p.id)}));
    result.pass=arrangement==='factory'?result.ids.includes('j13-front-stowed')&&!result.ids.includes('display')&&!result.ids.includes('control-loom-J13-retained-cartridge-loom'):result.visible.includes('mold-cavity')&&result.visible.includes('mold-core');
    checks.push({action:'arrangement',...result});
    if(!result.pass)errors.push('Incorrect '+arrangement+' occupancy');
  }
  await page.select('[data-control="arrangement"]','candidate');
  const wiring=JSON.parse(await fs.readFile(path.join(here,'wiring/candidate.json'),'utf8'));
  const ids=await page.evaluate(()=>window.pumpBayStudy.parts.map(p=>p.id));
  const missing=Object.keys(wiring.parts).filter(id=>!ids.includes(id));
  checks.push({action:'complete-wiring',count:Object.keys(wiring.parts).length,missing,pass:!missing.length});
  if(missing.length)errors.push('Missing native wiring articles: '+missing.join(', '));
  if(createHash('sha256').update(await fs.readFile(path.join(here,'index.html'))).digest('hex')!==viewerSHA)errors.push('Viewer changed during review');
  await fs.writeFile(path.join(here,'viewer-check.json'),JSON.stringify({pass:!errors.length,viewer_sha256:viewerSHA,errors,checks},null,2)+'\n');
  console.log(JSON.stringify({errors,checks:checks.length},null,2));
}finally{await closeBrowser(browser);}
finish(errors.length?1:0);
