import { chromium } from 'playwright';
import path from 'path'; import fs from 'fs'; import { pathToFileURL } from 'url';
const exe='/opt/pw-browsers/chromium';
const b=await chromium.launch({executablePath: fs.existsSync(exe)?exe:undefined,args:['--no-sandbox']});
const ctx=await b.newContext({viewport:{width:800,height:480},deviceScaleFactor:1});
const p=await ctx.newPage();
for (const f of process.argv.slice(2)){
  const abs=path.resolve(f);
  await p.goto(pathToFileURL(abs).href,{waitUntil:'networkidle'});
  try{await p.evaluate(()=>document.fonts.ready);}catch{}
  const rows=await p.evaluate(()=>{
    const out=[];
    document.querySelectorAll('*').forEach(el=>{
      if(['HTML','BODY','HEAD','META','TITLE','LINK','SCRIPT','PATH','RECT','CIRCLE','G','SPAN','B','U','I','S'].includes(el.tagName))return;
      const r=el.getBoundingClientRect();
      if(r.width<1||r.height<1)return;
      const cls=(el.className.baseVal!==undefined?el.className.baseVal:el.className)||el.tagName;
      out.push([String(cls).slice(0,34), Math.round(r.x*10)/10, Math.round(r.y*10)/10, Math.round(r.right*10)/10, Math.round(r.bottom*10)/10]);
    });
    return out;
  });
  console.log('=== '+path.basename(abs));
  for(const r of rows) console.log(`  ${r[0].padEnd(36)} x ${String(r[1]).padStart(6)} → ${String(r[3]).padStart(6)}   y ${String(r[2]).padStart(6)} → ${String(r[4]).padStart(6)}`);
}
await b.close();
