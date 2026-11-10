// This view draws the blinded trial's reviewed exports with the existing lab renderer.
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {decodeMeshPayload} from '/js/viewer/mesh-payload.js';
import {createPreview} from '/solidcraft-lab/carbonator/assembly-preview.js';
import {readNativeDisplay} from '/solidcraft-lab/carbonator/native-display.js';
const $=id=>document.getElementById(id),base='/solidcraft-lab/identification/blind/';
const identity=()=>[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],resources=[];
const query=new URL(location.href).searchParams;
let implementation=query.get('implementation')==='rust'?'rust':'native',variant=query.get('variant')==='before'?'before':'after',selected=null,busy=false,catalog,preview,firstDisplay;
async function load(url,type,label){const response=await fetch(url);if(!response.ok)throw new Error(`${label} could not be loaded.`);const bytes=await response.arrayBuffer();resources.push({url,type,bytes:bytes.byteLength});return bytes;}
async function readDisplay(bytes,kind,options){
  if(kind!=='rust-payload')return readNativeDisplay(bytes,kind,options);
  const payload=decodeMeshPayload(new Uint8Array(bytes));if(!payload?.meshes.length)throw new Error('The Rust payload has no surfaces.');
  const parts=payload.meshes.map(mesh=>{const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(mesh.attributes.position.array,3));geometry.setAttribute('normal',new THREE.BufferAttribute(mesh.attributes.normal.array,3));geometry.setIndex(new THREE.BufferAttribute(mesh.index.array,1));const values=new Float32Array(mesh.attributes.position.array.length);for(let i=0;i<values.length;i+=3)values.set(mesh.color||[.7,.73,.77],i);geometry.setAttribute('color',new THREE.BufferAttribute(values,3));return geometry;});
  const geometry=mergeGeometries(parts,false);parts.forEach(p=>p.dispose());geometry.computeBoundingBox();return geometry;
}
async function action(run){if(busy)return;busy=true;document.querySelectorAll('button,select,input').forEach(c=>c.disabled=true);try{await run();}catch(error){$('status').textContent=error.message;$('cover').hidden=true;console.error(error);}finally{busy=false;document.querySelectorAll('button,select,input').forEach(c=>c.disabled=false);}}
function controls(){
  $('implementation').value=implementation;$('variant').value=variant;
  $('parts').replaceChildren(...catalog.parts.map(part=>{const button=document.createElement('button');button.type='button';button.textContent=catalog.models[implementation]?.[variant]?.parts[part.key]?.label||part.label;button.setAttribute('aria-pressed',String(part.key===selected));button.onclick=()=>action(async()=>{selected=part.key;await show(true);});return button;}));
  const url=new URL(location.href);url.searchParams.set('implementation',implementation);url.searchParams.set('variant',variant);history.replaceState(null,'',url);
}
async function show(fit=false){
  controls();const model=catalog.models[implementation]?.[variant];
  if(!model){$('cover-title').textContent='This version is being reviewed';$('cover-detail').textContent='Its exported geometry will appear when it is ready.';$('cover').hidden=false;return;}
  const parts=catalog.parts.filter(p=>!selected||p.key===selected);
  const items=parts.map(part=>({id:part.key,node:`${implementation}-${variant}-${part.key}`,transform:part.transform,explode:[0,0,0]}));
  await preview.show({path:['blind',implementation,variant],count:1},{world:identity(),items,assembly:true},{fit});
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  firstDisplay={at:new Date().toISOString(),implementation,variant,parts:parts.map(p=>p.key),stats:preview.stats()};
  $('cover').hidden=true;$('view-title').textContent=selected?(model.parts[selected].label||selected):'All parts';$('state-label').textContent=implementation==='native'?'Native SolidCraft export':'Ordinary hsm payload';$('status').textContent=variant==='before'?'These completed models were frozen before their authors received the later request.':'The same authors applied the revealed request to their frozen models.';
  $('downloads').replaceChildren();for(const file of model.downloads||[]){if(selected&&file.part&&file.part!==selected)continue;const a=document.createElement('a');a.href=file.url;a.textContent=file.label;a.download='';$('downloads').append(a);}
}
$('implementation').onchange=()=>action(async()=>{implementation=$('implementation').value;await show();});$('variant').onchange=()=>action(async()=>{variant=$('variant').value;await show();});$('all-parts').onclick=()=>action(async()=>{selected=null;await show(true);});$('fit').onclick=()=>preview.fit();$('section').onchange=()=>preview.section($('section').checked);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)preview?.invalidate();});
export function inspectBlind(){return {implementation,variant,selected,busy,firstDisplay,resources:resources.map(r=>({...r})),preview:preview?.stats()};}
async function start(){
  catalog=await (await fetch(base+'catalog.json',{cache:'no-cache'})).json();const nodes={};
  for(const [impl,variants] of Object.entries(catalog.models))for(const [v,model] of Object.entries(variants))for(const part of catalog.parts)if(model.parts[part.key])nodes[`${impl}-${v}-${part.key}`]={label:model.parts[part.key].label||part.label,display:model.parts[part.key]};
  preview=await createPreview($('preview'),{nodes},load,{onSelect:key=>{if(key)action(async()=>{selected=key;await show(true);});},readDisplay});await action(()=>show(true));
  const report=await (await fetch(base+'results.json',{cache:'no-cache'})).json();$('request').textContent=report.request?.text||'';$('conclusion').textContent=report.conclusion||'';
  for(const timing of report.summary||[]){const p=document.createElement('span');p.style.display='block';p.textContent=timing;$('times').append(p);}
}
start().catch(error=>{$('cover-title').textContent='Could not open the comparison';$('cover-detail').textContent=error.message;console.error(error);});
