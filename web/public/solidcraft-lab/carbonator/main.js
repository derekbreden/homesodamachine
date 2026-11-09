// The carbonator lab opens cached assembly representations and loads native workspaces only by request.
import {createPreview} from './preview.js';
const base='/labs/solidcraft/carbonator';
const assets='/solidcraft-lab/carbonator/';
const $=id=>document.getElementById(id);
const requests=new Map(), resources=[], timings=[];
let config, children, preview, expanded=false, exploded=false, busy=false;
let frame, api, current, pollTimer, pollWork, pauseWanted=false, nativeVisible=false, nativeLoaded=false;
let models={}, revision, sourceKey, sourceVersion;
let exterior;
let canUndo=false;
let count=Number($('copies').value);
export function inspectLab(){
  return {resources:resources.map(item=>({...item})),preview:preview?.stats(),native:{loaded:Boolean(api),current,loadedModelTexts:Object.keys(models)},busy,count};
}
const names={parent:'Parent assembly',core:'Carbonator core',tube:'Tube',endcap:'Endcap',representation:'Assembly envelope'};
const dimensions={tube:{length:'Tube length'},endcap:{thickness:'Plate thickness'},core:{cap_recess:'Cap recess'},parent:{},representation:{}};

function status(text,error=false){$('status').textContent=text;$('status').toggleAttribute('data-error',error);}
function note(label,ms,detail=''){
  timings.unshift({label,ms,detail});timings.splice(7);
  $('timing-list').replaceChildren(...timings.map(item=>{
    const row=document.createElement('li'),label=document.createElement('span'),value=document.createElement('strong');
    label.textContent=item.label;value.textContent=item.ms<1000?`${Math.round(item.ms)} ms`:`${(item.ms/1000).toFixed(2)} s`;
    row.append(label,value);
    if(item.detail){const small=document.createElement('small');small.textContent=item.detail;row.append(small);}
    return row;
  }));
}
function audit(){
  const leaf=resources.filter(item=>item.type==='authoring').map(item=>item.label);
  $('part-files').textContent=leaf.length?[...new Set(leaf)].join(', '):'None';
  $('engine-state').textContent=api?'Loaded':frame?'Loading':'Not loaded';
  if(!api)$('native-bodies').textContent='Not loaded';
  $('resource-list').replaceChildren(...resources.map(item=>{
    const row=document.createElement('li');row.textContent=`${item.label} · ${(item.bytes/1024).toFixed(1)} kB · ${item.type}`;return row;
  }));
}
async function load(url,type,label){
  if(!requests.has(url))requests.set(url,(async()=>{
    const response=await fetch(url);if(!response.ok)throw new Error(`${label} could not be loaded.`);
    const data=await response.arrayBuffer();resources.push({url,type,label,bytes:data.byteLength});audit();return data;
  })().catch(error=>{requests.delete(url);throw error;}));
  return requests.get(url);
}
const json=async(url,type,label)=>JSON.parse(new TextDecoder().decode(await load(url,type,label)));
function cover(title,detail,resume=false){
  $('cover').hidden=false;$('cover-title').textContent=title;$('cover-detail').textContent=detail;$('resume').hidden=!resume;
}
function lock(value,label){
  busy=value;
  for(const button of document.querySelectorAll('button,select,.parameter input'))button.disabled=value;
  $('undo').disabled=value||!api||!canUndo;
  $('publish').disabled=value||!api||current==='parent';
  $('copies').disabled=value||nativeVisible;
  $('expand').disabled=value;
  $('section').disabled=value||nativeVisible||!expanded;
  for(const control of $('native-controls').querySelectorAll('button,input'))control.disabled=value||!api||!nativeLoaded;
  $('publish').disabled=value||!api||!nativeLoaded||current==='parent';
  $('undo').disabled=value||!api||!nativeLoaded||!canUndo;
  $('state-label').textContent=label|| (nativeVisible?names[current]+' · native':expanded?'Core · exact display':'Parent · assembly envelope');
  $('state-dot').toggleAttribute('data-ready',!value);
}
function store(){
  if(!sourceKey)return;
  try{
    localStorage.setItem(sourceKey,JSON.stringify({version:sourceVersion,current,exterior}));
    if(current&&models[current])localStorage.setItem(sourceKey+':'+current,models[current]);
  }
  catch{status('Local storage is unavailable. Download edited native designs to keep them.',true);}
}
async function modelText(kind){
  if(!models[kind]){
    const type=kind==='tube'||kind==='endcap'?'authoring':'assembly snapshot';
    let kept;try{kept=localStorage.getItem(sourceKey+':'+kind);}catch{}
    if(kept){
      models[kind]=kept;
      if(!resources.some(item=>item.url===sourceKey+':'+kind))resources.push({url:sourceKey+':'+kind,type,label:names[kind]+' (local)',bytes:new TextEncoder().encode(kept).length});
      audit();
    }else{
      const url=`${base}/native/${kind}`;
      models[kind]=new TextDecoder().decode(await load(url,type,names[kind]));
      if(type==='authoring')requests.delete(url);
    }
  }
  return models[kind];
}
async function capture(){
  if(!api||!nativeLoaded||!current)return;
  const kept=await api.request('document.export');
  models[current]=kept.text;revision=kept.revision;store();
  await api.request('document.saved',{revision:kept.revision});
}
async function sync(){
  const model=await api.inspect();
  $('native-scope').textContent=`${names[current]} · ${model.timeline.length} own features`;
  $('native-bodies').textContent=String(model.bodies.length);
  $('native-title').textContent=names[current];
  $('dimension-inputs').replaceChildren();
  for(const [name,labelText] of Object.entries(dimensions[current])){
    const param=model.params.find(param=>param.name===name);if(!param)continue;
    const label=document.createElement('label');label.className='parameter';
    const text=document.createElement('span');text.textContent=labelText;
    const input=document.createElement('input');input.name=name;input.value=param.expression;input.spellcheck=false;input.disabled=busy;
    label.append(text,input);$('dimension-inputs').append(label);
  }
  $('dimensions').hidden=current==='parent';
  $('publish').textContent=current==='core'?'Update parent':'Update core and parent';
  canUndo=Boolean(model.undo);$('undo').disabled=busy||!canUndo;
  return model;
}
function schedule(){
  clearTimeout(pollTimer);if(!api||busy||document.hidden||!nativeVisible)return;
  pollTimer=setTimeout(()=>{
    pollWork=(async()=>{
      const next=await api.request('document.revision');
      if(next.revision!==revision){
        await capture();
        if(!document.activeElement?.closest('#dimensions'))await sync();
      }
    })().catch(error=>status(error.message,true)).finally(()=>{pollWork=null;schedule();});
  },2500);
}
function showNative(){
  nativeVisible=true;$('preview').hidden=true;$('native-stage').hidden=false;preview.visible(false);
  $('reference').hidden=false;$('pause').hidden=false;$('native-controls').hidden=false;
  $('section').disabled=true;$('explode').disabled=true;$('copies').disabled=true;
}
async function showReference(){
  nativeVisible=false;$('preview').hidden=false;$('native-stage').hidden=true;preview.visible(true);
  $('reference').hidden=true;$('pause').hidden=true;$('native-controls').hidden=true;$('cover').hidden=true;
  $('section').disabled=!expanded;$('explode').disabled=false;$('copies').disabled=false;$('expand').disabled=false;
  $('native-scope').textContent='Closed';$('state-label').textContent='Saved reference view';
  if(expanded&&children)await preview.expand(children);else preview.count(count);
  status('Reference display. Editable designs remain closed until requested.');
}
async function ensureEngine(){
  if(api)return;
  const started=performance.now();
  cover('Starting native SolidCraft','The runtime loads for this workspace. Other parts remain closed.');
  frame=document.createElement('iframe');frame.title='SolidCraft assembly workspace';
  const mode=navigator.gpu?'':'&webgl';
  frame.src=`/labs/solidcraft/beduan/editor?embed=editor${mode}`;
  const ready=new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>finish(new Error('The native engine did not start.')),240000);
    const handler=event=>{
      if(event.origin!==location.origin||event.source!==frame?.contentWindow)return;
      if(event.data?.type==='solidcraft-lab-ready')finish();
      if(event.data?.type==='solidcraft-lab-error')finish(new Error(event.data.error));
    };
    function finish(error){clearTimeout(timeout);removeEventListener('message',handler);error?reject(error):resolve();}
    addEventListener('message',handler);
  });
  $('native-stage').append(frame);audit();await ready;
  api=frame.contentWindow.solidcraft;
  nativeLoaded=false;
  note('Native engine startup',performance.now()-started);audit();
}
async function importModel(kind,{keep=true}={}){
  if(keep)await capture();
  const previous=current;
  const text=await modelText(kind);
  const started=performance.now();
  const opened=await api.request('document.import',{text,name:names[kind]});
  current=kind;
  nativeLoaded=true;
  if(previous!==kind)delete models[previous];
  if(opened.errors)throw new Error(`${names[kind]} has feature errors.`);
  if(kind==='parent'){
    const doc=JSON.parse(text);
    if(doc.occurrences.length===1&&count>1){
      const columns=Math.ceil(Math.sqrt(count));
      const commands=Array.from({length:count-1},(_,index)=>{
        const i=index+1;return {command:'occurrence.copy',params:{component:'Carbonator core',translate:[i%columns*config.pitch,Math.floor(i/columns)*config.pitch,0]}};
      });
      await api.request('engine.batch',{commands});
    }
  }
  const panels=!matchMedia('(max-width:700px)').matches;
  await api.request('ui.set',{showBrowser:panels,showTimeline:panels});
  await api.execute('view.ribbon_tabs_only',{on:!panels});
  await api.request('ui.view',{view:'iso'});await api.request('ui.view',{view:'fit'});
  note(`Open ${names[kind]}`,performance.now()-started,kind==='parent'?'Envelope only; no tube or endcap geometry requested.':kind==='core'?'Exact saved part bodies; leaf histories remain closed.':kind==='representation'?'Exterior bounds published by the exact core.':'Only this part’s editable history is evaluated.');
  await capture();await sync();$('cover').hidden=true;
}
async function action(label,work){
  if(busy)return;
  clearTimeout(pollTimer);lock(true,label);status(label+'…');
  try{
    if(pollWork)await pollWork;
    await work();
    if(api){await capture();await sync();}
  }catch(error){
    status(error.message,true);
    if(frame&&!api){frame.remove();frame=null;cover('Native workspace could not open',error.message,true);}
  }finally{
    lock(false);
    if(nativeVisible){$('section').disabled=true;$('explode').disabled=true;}
    audit();
    if(pauseWanted||document.hidden){pauseWanted=false;await pause();}else schedule();
  }
}
async function openNative(kind){
  await action('Opening '+names[kind],async()=>{
    showNative();await ensureEngine();await importModel(kind);status(`${names[kind]} is open. Only requested workspaces are loaded.`);
  });
}
async function pause(){
  clearTimeout(pollTimer);
  if(busy){pauseWanted=true;return;}
  if(!api)return;
  lock(true,'Saving local workspace');
  try{
    if(pollWork)await pollWork;
    await capture();frame.remove();frame=null;api=null;nativeLoaded=false;audit();
    if(nativeVisible)cover('Native workspace paused','Its current design is retained locally. Resuming opens that saved workspace, without following its child sources.',true);
    status('Native runtime unloaded. Local workspaces are retained in this browser.');
  }catch(error){status(error.message,true);}
  finally{lock(false,nativeVisible?'Native workspace paused':'Saved reference view');}
}
async function expand(){
  if(!children)children=await json(config.children,'assembly interfaces','Core part list and placements');
  if(!nativeVisible)await preview.expand(children);
  expanded=true;$('children').hidden=false;$('expand').setAttribute('aria-expanded','true');
  if(!nativeVisible){$('section').checked=true;preview.section(true);}
  $('expand').firstChild.textContent='▾ Carbonator core ';
  $('fit-note').textContent=`Nominal radial clearance: ${children.radialClearanceMm.toFixed(3)} mm. Cap placement follows the tube’s end faces.`;
}
function resetContext(){
  sourceKey=`hsm-carbonator-lab:${sourceVersion}:${count}`;
  let kept;try{kept=JSON.parse(localStorage.getItem(sourceKey));}catch{}
  models={};current=kept?.current||'parent';revision=null;exterior=kept?.exterior||{...config.exterior};
}

$('open-parent').addEventListener('click',()=>openNative('parent'));
$('open-core').addEventListener('click',()=>openNative('core'));
for(const button of document.querySelectorAll('[data-edit]'))button.addEventListener('click',()=>openNative(button.dataset.edit));
$('expand').addEventListener('click',()=>action('Opening core display',async()=>{
  if(expanded){expanded=false;exploded=false;if(!nativeVisible){preview.count(count);$('section').checked=false;preview.section(false);}$('children').hidden=true;$('expand').setAttribute('aria-expanded','false');$('expand').firstChild.textContent='▸ Carbonator core ';}
  else await expand();
  status('Display parts are available. Their editable designs remain closed.');
}));
$('copies').addEventListener('change',()=>{
  count=Number($('copies').value);resetContext();expanded=false;exploded=false;preview.count(count);
  $('section').checked=false;preview.section(false);
  $('section').disabled=true;
  $('children').hidden=true;$('expand').setAttribute('aria-expanded','false');$('expand').firstChild.textContent='▸ Carbonator core ';
  status(`${count} placements share the saved module shape. No child authoring files were requested.`);
});
$('section').addEventListener('change',()=>preview.section($('section').checked));
$('explode').addEventListener('click',()=>action('Exploding reference',async()=>{
  if(!expanded)await expand();
  exploded=!exploded;preview.explode(exploded);$('explode').textContent=exploded?'Assemble':'Explode';
  status(exploded?'Exploded reference display. Native joints retain the assembled fit-up.':'Assembled reference display.');
}));
$('fit').addEventListener('click',()=>{if(api&&nativeVisible)action('Fit',()=>api.request('ui.view',{view:'fit'}));else preview.fit();});
$('dimensions').addEventListener('submit',event=>{
  event.preventDefault();
  const changes=Object.fromEntries(new FormData($('dimensions')));
  action('Applying dimension',async()=>{
    const started=performance.now(),result=await api.execute('parameters.change',{changes});
    note('Edit '+names[current],performance.now()-started,`${result.recomputed} native features rebuilt`);
    status('This workspace is updated. Use Update parents to replace its saved assembly representation.');
  });
});
$('undo').addEventListener('click',()=>action('Undo',()=>api.execute('edit.undo')));
$('publish').addEventListener('click',()=>action('Updating linked assemblies',async()=>{
  const leaf=current;const started=performance.now();await capture();
  try{
    if(leaf==='tube'||leaf==='endcap'){
      await api.execute('component.extract',{component:leaf==='tube'?'Tube':'Endcap',path:`parts/${leaf}.sc`});
      await importModel('core',{keep:false});
      const result=await api.execute('component.update_links',{component:leaf==='tube'?'Tube':'Endcap'});
      if(result.failed.length)throw new Error(result.failed[0].error);
      const solved=await api.execute('joint.list',{});
      if(solved.errors.length||solved.conflicts.length)throw new Error('The updated core has unresolved joints.');
      await capture();
    }
    const measured=await api.execute('inspect.measure',{bodies:['Tube wall']});
    const bounds=measured.bodies[0].bbox;
    const outerDiameter=Number((bounds.max[0]-bounds.min[0]).toFixed(9));
    const length=Number((bounds.max[2]-bounds.min[2]).toFixed(9));
    const changed=outerDiameter!==exterior.outer_diameter||length!==exterior.length;
    if(changed){
      await importModel('representation',{keep:false});
      await api.execute('parameters.change',{changes:{outer_diameter:`${outerDiameter} mm`,length:`${length} mm`}});
      await api.execute('file.save_as',{path:'representation.sc',cache:true,overwrite:true});
      await capture();
    }
    await importModel('parent',{keep:false});
    if(changed){
      const result=await api.execute('component.update_links',{component:'Carbonator core'});
      if(result.failed.length)throw new Error(result.failed[0].error);
      exterior={outer_diameter:outerDiameter,length};
    }
    await api.request('ui.view',{view:'fit'});
    note('Update '+names[leaf]+' → parent',performance.now()-started,changed?'Parent envelope updated from the exterior bounds.':'Parent envelope unchanged; the edit stays inside the exact core.');
    status(changed?'Parent envelope updated. Exact tube and cap geometry stays in the core.':'Exact core updated. Its exterior bounds are unchanged, so the parent envelope is unchanged.');
  }catch(error){
    if(current===leaf)await importModel(leaf,{keep:false});
    throw error;
  }
}));
$('download').addEventListener('click',()=>action('Downloading native design',async()=>{
  const data=await api.request('document.export');
  const url=URL.createObjectURL(new Blob([data.text],{type:'application/json'}));
  const link=document.createElement('a');link.href=url;link.download=`carbonator-${current}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}));
$('pause').addEventListener('click',()=>pause());
$('resume').addEventListener('click',()=>openNative(current));
$('reference').addEventListener('click',async()=>{
  await pause();lock(true,'Opening reference display');
  try{await showReference();}catch(error){status(error.message,true);}finally{lock(false);}
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();else preview?.invalidate();});

try{
  lock(true,'Loading saved representation');
  config=await json(assets+'module.json','module interface','Carbonator module');
  sourceVersion=config.sourceVersion;resetContext();
  preview=await createPreview($('preview'),config,load);
  await preview.ready;
  note('Saved assembly view',performance.now(),'Navigation to first render; no native runtime or child histories loaded.');
  $('cover').hidden=true;lock(false,'Parent · assembly envelope');
  status('Assembly envelope loaded. Opening the core requests its exact parts; editing a part requests its history.');
}catch(error){cover('Could not open saved shape',error.message);status(error.message,true);lock(false,'Could not open');}
