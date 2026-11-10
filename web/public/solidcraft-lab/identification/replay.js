// This replay compares native and production payloads with the same camera, renderer and historical input dimensions.
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {decodeMeshPayload} from '/js/viewer/mesh-payload.js';
import {createPreview} from '/solidcraft-lab/carbonator/assembly-preview.js';
import {readNativeDisplay} from '/solidcraft-lab/carbonator/native-display.js';
const $=id=>document.getElementById(id),base='/solidcraft-lab/identification/';
const identity=()=>[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],resources=[];
let catalog,preview,implementation='native',variant='before',selected=null,busy=false,api,frame,localText,native=false,firstDisplay;
const urls=new URL(location.href);implementation=urls.searchParams.get('implementation')==='rust'?'rust':'native';variant=urls.searchParams.get('variant')==='after'?'after':'before';
async function load(url,type,label){const response=await fetch(url);if(!response.ok)throw new Error(`${label} could not be loaded.`);const bytes=await response.arrayBuffer();resources.push({url,type,label,bytes:bytes.byteLength});return bytes;}
async function readDisplay(bytes,kind,options){
  if(kind!=='rust-payload')return readNativeDisplay(bytes,kind,options);
  const payload=decodeMeshPayload(new Uint8Array(bytes));if(!payload?.meshes.length)throw new Error('The Rust payload has no surfaces.');
  const parts=payload.meshes.map(mesh=>{
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(mesh.attributes.position.array,3));geometry.setAttribute('normal',new THREE.BufferAttribute(mesh.attributes.normal.array,3));geometry.setIndex(new THREE.BufferAttribute(mesh.index.array,1));
    const values=new Float32Array(mesh.attributes.position.array.length),color=mesh.color||[.7,.73,.77];
    for(let i=0;i<values.length;i+=3)values.set(color,i);geometry.setAttribute('color',new THREE.BufferAttribute(values,3));return geometry;
  });
  const geometry=mergeGeometries(parts,false);parts.forEach(p=>p.dispose());geometry.computeBoundingBox();return geometry;
}
function setBusy(value){busy=value;for(const control of document.querySelectorAll('button,select,input'))control.disabled=value;}
function note(label,ms){const row=document.createElement('li'),text=document.createElement('span'),time=document.createElement('strong');text.textContent=label;time.textContent=ms<1000?`${Math.round(ms)} ms`:`${(ms/1000).toFixed(2)} s`;row.append(text,time);$('timing-list').prepend(row);while($('timing-list').children.length>6)$('timing-list').lastChild.remove();}
async function action(run){if(busy)return;setBusy(true);try{await run();}catch(error){$('cover').hidden=true;$('status').textContent=error.message;console.error(error);}finally{setBusy(false);if(document.hidden&&api){await closeNative();await show();}}}
function controls(){
  $('implementation').value=implementation;$('variant').value=variant;$('source-label').textContent=implementation==='native'?'SolidCraft native meshes':'Production Rust payloads';$('width-label').textContent=catalog.variants[variant].width.toFixed(1)+' mm';
  $('view-title').textContent=selected?catalog.parts.find(p=>p.key===selected).label:'All identification chips';
  $('parts').replaceChildren(...catalog.parts.map(part=>{const button=document.createElement('button');button.type='button';button.textContent=part.label;button.setAttribute('aria-pressed',String(part.key===selected));button.onclick=()=>action(async()=>{selected=part.key;await show(true);});return button;}));
  const url=new URL(location.href);url.searchParams.set('implementation',implementation);url.searchParams.set('variant',variant);history.replaceState(null,'',url);
}
async function show(fit=false){
  if(api)await closeNative();native=false;controls();
  const mode=catalog.models[implementation]?.[variant];if(!mode){$('cover-title').textContent='Waiting for this replay';$('cover-detail').textContent='The baseline is published. Its edited output will appear when the replay is ready.';$('cover').hidden=false;return;}
  $('preview').hidden=false;$('native-stage').hidden=true;$('native-controls').hidden=true;$('reference').hidden=true;preview.visible(true);
  const parts=catalog.parts.filter(p=>!selected||p.key===selected),start=performance.now();
  const items=parts.map(part=>({id:part.key,node:`${implementation}-${variant}-${part.key}`,transform:implementation==='rust'?part.transform:identity(),explode:[0,0,0]}));
  await preview.show({path:['chips',implementation,variant],count:1},{world:identity(),items,assembly:true},{fit});
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  firstDisplay={at:new Date().toISOString(),implementation,variant,parts:parts.map(p=>p.key),resources:resources.map(r=>({...r})),stats:preview.stats()};
  note(`${implementation==='native'?'SolidCraft':'Rust'} · ${catalog.variants[variant].width.toFixed(1)} mm`,performance.now()-start);
  $('state-label').textContent=implementation==='native'?'Native exported geometry':'Production geometry';$('cover').hidden=true;$('engine-label').textContent='Not loaded';$('load-note').textContent='The same viewer and camera draw both implementations.';
  $('status').textContent=variant==='before'?'Complete original chips. Select Approved width to review the side-edge change.':'The approved width removes 0.20 mm from each side. Bores and lettering remain in place.';
  $('downloads').replaceChildren();
  for(const file of mode.downloads||[]){const a=document.createElement('a');a.href=file.url;a.textContent=file.label;a.download='';$('downloads').append(a);}
}
async function closeNative(){if(api){const doc=await api.request('document.export');localText=doc.text;}frame?.remove();frame=null;api=null;native=false;$('engine-label').textContent='Not loaded';}
async function edit(){
  $('cover-title').textContent='Starting SolidCraft';$('cover-detail').textContent='Opening the complete editable set.';$('cover').hidden=false;
  frame=document.createElement('iframe');frame.title='Native identification-chip design';
  const ready=new Promise((resolve,reject)=>{const timer=setTimeout(()=>done(new Error('SolidCraft did not start.')),180000);function done(error){clearTimeout(timer);removeEventListener('message',listener);error?reject(error):resolve();}function listener(e){if(e.source!==frame?.contentWindow||e.origin!==location.origin)return;if(e.data?.type==='solidcraft-lab-ready')done();if(e.data?.type==='solidcraft-lab-error')done(new Error(e.data.error));}addEventListener('message',listener);});
  frame.src='/labs/solidcraft/beduan/editor?embed=editor'+(navigator.gpu?'':'&webgl');$('native-stage').append(frame);await ready;api=frame.contentWindow.solidcraft;
  const text=localText||await (await fetch(catalog.models.native[variant]?.design||catalog.models.native.before.design)).text();
  const result=await api.request('document.import',{text,name:'Identification chips'});if(result.errors)throw new Error('The native design has feature errors.');
  await api.execute('view.top');await api.execute('view.fit');await api.execute('view.ribbon_tabs_only',{on:true});
  native=true;preview.visible(false);$('preview').hidden=true;$('native-stage').hidden=false;$('cover').hidden=true;$('reference').hidden=false;$('native-controls').hidden=false;$('engine-label').textContent='Native editor';$('state-label').textContent='Native authoring · complete set';
  const inspection=await api.inspect();const parameter=inspection.params.find(p=>p.name==='side_clearance');$('clearance').value=parameter?.value??(variant==='before'?0:.2);$('status').textContent='The native parameter changes the six chip edges. Geometry and lettering remain editable in SolidCraft.';
}
$('implementation').onchange=()=>action(async()=>{implementation=$('implementation').value;await show();});$('variant').onchange=()=>action(async()=>{variant=$('variant').value;localText=null;await show();});
$('all-parts').onclick=()=>action(async()=>{selected=null;await show(true);});$('fit').onclick=()=>api?api.execute('view.fit'):preview.fit();$('section').onchange=()=>preview.section($('section').checked);
$('edit').onclick=()=>action(edit);$('reference').onclick=()=>action(()=>show());
$('dimensions').onsubmit=e=>{e.preventDefault();action(async()=>{const start=performance.now();const result=await api.execute('parameters.change',{name:'side_clearance',expression:$('clearance').value+' mm'});const doc=await api.request('document.export');localText=doc.text;note('Native parameter edit',performance.now()-start);$('status').textContent=`Native clearance changed. ${result.recomputed} features recomputed.`;});};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&api&&!busy)action(async()=>{await closeNative();await show();});else if(!document.hidden)preview?.invalidate();});
export function inspectReplay(){return {implementation,variant,selected,busy,native,resources:resources.map(r=>({...r})),firstDisplay,preview:preview?.stats()};}
async function start(){catalog=await (await fetch(base+'catalog.json',{cache:'no-cache'})).json();const nodes={};for(const [impl,variants] of Object.entries(catalog.models))for(const [v,model] of Object.entries(variants))for(const part of catalog.parts)if(model.parts[part.key])nodes[`${impl}-${v}-${part.key}`]={label:part.label,display:model.parts[part.key]};
  preview=await createPreview($('preview'),{nodes},load,{onSelect:key=>{if(key)action(async()=>{selected=key;await show(true);});},readDisplay});await action(()=>show(true));}
start().catch(error=>{$('cover-title').textContent='Could not open the comparison';$('cover-detail').textContent=error.message;console.error(error);});
