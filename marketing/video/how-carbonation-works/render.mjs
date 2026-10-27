#!/usr/bin/env node
/** Render explicit frames in Chromium, encode resumable scene clips, then mux the sound master. */
import fs from 'node:fs/promises';
import fss from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {gunzipSync} from 'node:zlib';
import {spawn,execFileSync} from 'node:child_process';
import {once} from 'node:events';
import {createHash} from 'node:crypto';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(HERE,'../../..');
const require=createRequire(path.join(repo,'tools/render/package.json'));
const {default:puppeteer}=await import(require.resolve('puppeteer'));
const args=process.argv.slice(2),has=s=>args.includes(s),arg=(s,d)=>{const i=args.indexOf(s);return i>=0?args[i+1]:d;};
const out=path.join(HERE,'out');await fs.mkdir(path.join(out,'vendor'),{recursive:true});
for(const n of ['enclosure','cold-core','faucet']){
 const target=path.join(HERE,`assets/${n}-cad.json`);
 if(!fss.existsSync(target))await fs.writeFile(target,gunzipSync(await fs.readFile(target+'.gz')));
}
const vendor=path.join(out,'vendor/three.min.js');
if(!fss.existsSync(vendor)){
 const response=await fetch('https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.min.js');
 if(!response.ok)throw Error('Three.js download failed: '+response.status);await fs.writeFile(vendor,new Uint8Array(await response.arrayBuffer()));
}
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.jpg':'image/jpeg','.mp4':'video/mp4','.vtt':'text/vtt','.wav':'audio/wav'};
const server=http.createServer(async(req,res)=>{
 if(req.url==='/favicon.ico'){res.writeHead(204);res.end();return;}
 try{const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname),p=path.resolve(HERE,'.'+pathname);
  if(!p.startsWith(HERE+path.sep)){res.writeHead(403);res.end();return;}
  if(path.extname(p)==='.mp4'&&req.headers.range){
   const stat=await fs.stat(p),match=/bytes=(\d+)-(\d*)/.exec(req.headers.range);
   if(match){const start=Number(match[1]),end=match[2]?Math.min(Number(match[2]),stat.size-1):stat.size-1;
    res.writeHead(206,{'Content-Type':'video/mp4','Content-Length':end-start+1,'Content-Range':`bytes ${start}-${end}/${stat.size}`,'Accept-Ranges':'bytes'});fss.createReadStream(p,{start,end}).pipe(res);return;}
  }
  const data=await fs.readFile(p);res.writeHead(200,{'Content-Type':mime[path.extname(p)]||'application/octet-stream','Cache-Control':'no-store'});res.end(data);
 }catch{res.writeHead(404);res.end('Not found');}
});
await new Promise(r=>server.listen(Number(arg('--port','8794')),'127.0.0.1',r));
const port=server.address().port;
if(has('--serve')){console.log(`Player: http://127.0.0.1:${port}/watch.html\nSource picture: http://127.0.0.1:${port}/studio.html?play`);await new Promise(()=>{});}
const clock=JSON.parse(await fs.readFile(path.join(HERE,'audio/timing.json'),'utf8'));
const browser=await puppeteer.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist','--force-color-profile=srgb','--disable-background-timer-throttling']});
const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
async function screenshot(frame,destination,options={}){
 const state=await page.evaluate(async({frame,options})=>window.renderFrame(frame,options),{frame,options});
 if(errors.length)throw Error(errors.join('\n'));
 const data=await page.screenshot({type:'jpeg',quality:96,captureBeyondViewport:false});
 if(destination)await fs.writeFile(destination,data);return {data,state};
}
try{
 await page.goto(`http://127.0.0.1:${port}/studio.html`,{waitUntil:'networkidle0',timeout:90000});
 await page.waitForFunction('window.filmReady===true',{timeout:90000});
 if(errors.length)throw Error(errors.join('\n'));
 if(has('--stills')){
  const times=[4.2,11.3,14.7,18.4,24.0,29.7,36.7,47.2,56.8,65.1,68.2,73.9,77.8,85.0,90.0,98.5];
  await fs.mkdir(path.join(out,'review'),{recursive:true});
  for(const t of times){const p=path.join(out,'review',String(t.toFixed(1)).padStart(5,'0')+'.jpg');const {state}=await screenshot(Math.round(t*30),p);console.log(JSON.stringify({...state,file:p}));}
  const thumbFrame=Math.round(49.0*30);await screenshot(thumbFrame,null,{captionsVisible:false});
  await page.evaluate(()=>{document.getElementById('eyebrow').textContent='A look inside';document.getElementById('headline').textContent='How\ncarbonation\nworks.';document.getElementById('detail').textContent='Inside a home soda machine';document.getElementById('type').style.opacity=1;document.getElementById('callouts').innerHTML='';});
  const thumb=await page.screenshot({type:'jpeg',quality:96});await fs.writeFile(path.join(out,'thumbnail-1920.jpg'),thumb);
 }
 if(has('--render')){
  const segmentDir=path.join(out,'segments');await fs.mkdir(segmentDir,{recursive:true});
  const hash=createHash('sha256');for(const n of ['scene.js','carbonator.js','studio.html','audio/timing.json','audio/captions-edited.json','assets/cad-manifest.json','assets/coil-path.json','assets/Archivo-latin-variable.woff2','assets/IBMPlexMono-latin-regular.woff2','assets/faucet-display-flavor1.png','out/vendor/three.min.js'])hash.update(await fs.readFile(path.join(HERE,n)));
  const signature=hash.digest('hex');
  const selected=arg('--shots','').split(',').filter(Boolean),files=[];
  for(let i=0;i<clock.scenes.length;i++){
   const s=clock.scenes[i],start=Math.round(s.start*30),end=i+1<clock.scenes.length?Math.round(clock.scenes[i+1].start*30):clock.frames;
   const movie=path.join(segmentDir,s.id+'.mp4'),manifest=movie+'.json';files.push(movie);
   if(selected.length&&!selected.includes(s.id))continue;
   let prior=null;try{prior=JSON.parse(await fs.readFile(manifest,'utf8'));}catch{}
   if(!has('--fresh')&&fss.existsSync(movie)&&prior?.signature===signature&&prior?.frames===end-start){console.log(`Reuse ${s.id}: ${end-start} frames`);continue;}
   console.log(`Render ${s.id}: frames ${start}..${end-1}`);
   const encoder=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-framerate','30','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',movie],{stdio:['pipe','ignore','pipe']});
   let log='';encoder.stderr.on('data',d=>{log+=d.toString();});
   const finished=new Promise((resolve,reject)=>encoder.on('exit',code=>code===0?resolve():reject(Error(`ffmpeg ${s.id}: ${code}\n${log}`))));
   const begun=Date.now();
   for(let n=start;n<end;n++){
    const {data}=await screenshot(n);
    if(!encoder.stdin.write(data))await once(encoder.stdin,'drain');
    if((n-start)%120===0)console.log(`${s.id} ${n-start}/${end-start} (${((Date.now()-begun)/1000).toFixed(1)}s)`);
   }
   encoder.stdin.end();await finished;
   await fs.writeFile(manifest,JSON.stringify({signature,startFrame:start,frames:end-start},null,2)+'\n');
  }
  if(files.every(p=>fss.existsSync(p))){
   const list=path.join(out,'concat.txt');await fs.writeFile(list,files.map(p=>"file '"+p.replaceAll("'","'\\''")+"'").join('\n')+'\n');
   const picture=path.join(out,'picture.mp4'),master=path.join(out,'how-carbonation-works.mp4');
   execFileSync('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','concat','-safe','0','-i',list,'-c','copy',picture]);
   execFileSync('ffmpeg',['-hide_banner','-loglevel','warning','-y','-i',picture,'-i',path.join(HERE,'audio/mix-master.wav'),'-map','0:v:0','-map','1:a:0','-vf','scale=in_range=full:out_range=limited:in_color_matrix=bt601:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-preset','medium','-crf','16','-profile:v','high','-level:v','4.1','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','320k','-ar','48000','-metadata:s:a:0','language=eng','-movflags','+faststart','-shortest',master]);
   for(const ext of ['srt','vtt'])await fs.copyFile(path.join(HERE,`audio/film.${ext}`),path.join(out,`how-carbonation-works.${ext}`));
   await fs.writeFile(path.join(out,'render-manifest.json'),JSON.stringify({signature,width:1920,height:1080,fps:30,frames:clock.frames,duration:clock.frames/30,videoSha256:createHash('sha256').update(await fs.readFile(master)).digest('hex')},null,2)+'\n');
   console.log(`Master: ${master}`);
  }
 }
}finally{await browser.close();server.close();}
