// This page presents reviewed native features and opens their editable documents only on demand.
import {createPreview} from '/solidcraft-lab/carbonator/assembly-preview.js';
const $=id=>document.getElementById(id),base='/solidcraft-lab/features/';
const identity=()=>[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],resources=[],drafts=new Map();
const query=new URL(location.href).searchParams;
let data,preview,currentStudy=query.get('study')||'handhold',currentModel=query.get('model'),busy=false,frame,api,native=false,firstDisplay,lastEdit;
const study=()=>data.studies.find(s=>s.id===currentStudy),model=()=>study().models.find(m=>m.id===currentModel),key=()=>currentStudy+'/'+currentModel;
async function load(url,type,label){const response=await fetch(url);if(!response.ok)throw new Error(`${label} could not be loaded.`);const bytes=await response.arrayBuffer();resources.push({url,type,bytes:bytes.byteLength});return bytes;}
function lock(value){busy=value;document.querySelectorAll('button,select,input').forEach(c=>c.disabled=value);for(const id of ['study','model','section','edit'])$(id).disabled=value||native;}
async function action(run){if(busy)return;lock(true);try{await run();}catch(error){if(frame&&!native){frame.remove();frame=null;api=null;}$('cover').hidden=true;$('status').textContent=error.message;console.error(error);}finally{lock(false);if(document.hidden&&api){await closeNative();await show();}}}
function controls(){
  const s=study();if(!s.models.some(m=>m.id===currentModel))currentModel=s.models[0].id;const m=model();
  $('study').replaceChildren(...data.studies.map(s=>new Option(s.label,s.id)));$('study').value=currentStudy;
  $('model').replaceChildren(...s.models.map(m=>new Option(m.label,m.id)));$('model').value=currentModel;
  $('description').textContent=m.description||s.description;$('finding').textContent=s.finding;$('scope').textContent=s.scope;$('view-title').textContent=s.label;
  $('facts').replaceChildren(...(m.facts||s.facts||[]).map(([name,value])=>{const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;row.append(dt,dd);return row;}));
  $('downloads').replaceChildren();for(const file of m.downloads||[]){const a=document.createElement('a');a.href=file.url;a.textContent=file.label;a.download='';$('downloads').append(a);}
  $('machine-link').replaceChildren();if(s.machine){const a=document.createElement('a');a.href=s.machine;a.textContent='Locate the handhold in the machine ↗';$('machine-link').append(a);}
  $('edit').hidden=!m.design;
  const url=new URL(location.href);url.searchParams.set('study',currentStudy);url.searchParams.set('model',currentModel);history.replaceState(null,'',url);
}
async function show(fit=false){
  if(api)await closeNative();controls();native=false;const m=model();preview.visible(true);$('preview').hidden=false;$('native-stage').hidden=true;$('native-controls').hidden=true;$('reference').hidden=true;
  await preview.show({path:['features',currentStudy,currentModel],count:1},{world:identity(),items:[{id:m.id,node:key(),transform:identity(),explode:[0,0,0]}],assembly:true},{fit});
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));firstDisplay={at:new Date().toISOString(),study:currentStudy,model:currentModel,stats:preview.stats()};
  $('cover').hidden=true;$('state-label').textContent=m.state||'Exported geometry · CAD engine closed';$('status').textContent=m.note||study().note;
}
async function closeNative(){try{if(api){const result=await api.request('document.export');drafts.set(key(),result.text);}}finally{frame?.remove();frame=null;api=null;native=false;}}
async function edit(){
  $('cover-title').textContent='Opening the native design';$('cover-detail').textContent='Starting the complete editable SolidCraft model.';$('cover').hidden=false;
  frame=document.createElement('iframe');frame.title='Native feature design';
  const ready=new Promise((resolve,reject)=>{const timer=setTimeout(()=>done(new Error('SolidCraft did not start.')),180000);function done(error){clearTimeout(timer);removeEventListener('message',listener);error?reject(error):resolve();}function listener(e){if(e.source!==frame?.contentWindow||e.origin!==location.origin)return;if(e.data?.type==='solidcraft-lab-ready')done();if(e.data?.type==='solidcraft-lab-error')done(new Error(e.data.error));}addEventListener('message',listener);});
  frame.src='/labs/solidcraft/beduan/editor?embed=editor'+(navigator.gpu?'':'&webgl');$('native-stage').append(frame);await ready;api=frame.contentWindow.solidcraft;
  const text=drafts.get(key())||await (await fetch(model().design)).text();const result=await api.request('document.import',{text,name:study().label});if(result.errors)throw new Error('The native design reports feature errors.');
  await api.execute(model().nativeView||study().nativeView||'view.isometric');await api.execute('view.fit');await api.execute('view.ribbon_tabs_only',{on:true});
  native=true;preview.visible(false);$('preview').hidden=true;$('native-stage').hidden=false;$('cover').hidden=true;$('reference').hidden=false;$('native-controls').hidden=false;$('state-label').textContent='Native SolidCraft · local draft';
  const inspection=await api.inspect();$('parameters').replaceChildren(...(model().parameters||study().parameters||[]).map(p=>{const label=document.createElement('label'),input=document.createElement('input');label.textContent=p.label;input.name=p.name;input.type='number';input.step='any';input.required=true;input.value=inspection.params.find(x=>x.name===p.name)?.value??p.value;label.append(input);return label;}));
  $('dimensions').hidden=!$('parameters').children.length;$('status').textContent='Edit the native feature history or its dimensions. Download the draft to keep your changes.';
}
$('study').onchange=()=>action(async()=>{currentStudy=$('study').value;currentModel=null;await show(true);});$('model').onchange=()=>action(async()=>{currentModel=$('model').value;await show();});$('fit').onclick=()=>api?api.execute('view.fit'):preview.fit();$('section').onchange=()=>preview.section($('section').checked);$('edit').onclick=()=>action(edit);$('reference').onclick=()=>action(()=>show());
$('dimensions').onsubmit=e=>{e.preventDefault();action(async()=>{const start=performance.now(),changes=Object.fromEntries([...$('parameters').querySelectorAll('input')].map(input=>[input.name,input.value+' mm']));const result=await api.execute('parameters.change',{changes});if(result.errors?.length)throw new Error('A native feature could not be rebuilt. Inspect its history before retaining the draft.');const doc=await api.request('document.export');drafts.set(key(),doc.text);lastEdit={at:new Date().toISOString(),wall_ms:performance.now()-start,recomputed:result.recomputed||0};$('status').textContent=`Native dimensions updated in ${(lastEdit.wall_ms/1000).toFixed(2)} s. The feature history remains editable.`;});};
$('download-draft').onclick=()=>action(async()=>{const doc=await api.request('document.export'),url=URL.createObjectURL(new Blob([doc.text],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=currentStudy+'-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&api&&!busy)action(async()=>{await closeNative();await show();});else if(!document.hidden)preview?.invalidate();});
export function inspectFeatures(){return {study:currentStudy,model:currentModel,busy,native,firstDisplay,lastEdit,resources:resources.map(r=>({...r})),preview:preview?.stats()};}
async function start(){data=await (await fetch(base+'studies.json',{cache:'no-cache'})).json();if(!data.studies.some(s=>s.id===currentStudy))currentStudy=data.studies[0].id;const nodes={};for(const s of data.studies)for(const m of s.models)nodes[s.id+'/'+m.id]={label:m.label,display:m.display};preview=await createPreview($('preview'),{nodes},load,{fitDirection:()=>study().fitDirection||[1.1,-1.6,.85]});await action(()=>show(true));}
start().catch(error=>{$('cover-title').textContent='Could not open the study';$('cover-detail').textContent=error.message;console.error(error);});
