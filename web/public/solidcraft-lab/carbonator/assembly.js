// The nested SolidCraft example opens saved geometry at each assembly boundary and starts native editing on request.
import {createPreview} from './assembly-preview.js';
import {createAssemblyNavigation} from './assembly-navigation.js';
const $=id=>document.getElementById(id),base='/labs/solidcraft/carbonator',assets='/solidcraft-lab/carbonator/';
const resources=[],requests=new Map(),manifests=new Map(),models=new Map();
let catalog,preview,navigation,context,api,frame,current,revision,timer,busy=false,native=false,exploded=false,pending,paused;
let sourceKey,pollWork,database,pauseWanted=false;
async function workspaceStore(key,text){
  database ||= new Promise((resolve,reject)=>{
    const open=indexedDB.open('solidcraft-carbonator-lab',1);
    open.onupgradeneeded=()=>open.result.createObjectStore('designs');
    open.onsuccess=()=>resolve(open.result);open.onerror=()=>reject(open.error);
  });
  const db=await database;
  return new Promise((resolve,reject)=>{
    const transaction=db.transaction('designs',text===undefined?'readonly':'readwrite'),store=transaction.objectStore('designs');
    const request=text===undefined?store.get(storageKey(key)):store.put(text,storageKey(key));
    transaction.oncomplete=()=>resolve(request.result);transaction.onerror=()=>reject(transaction.error);
    transaction.onabort=()=>reject(transaction.error||new Error('The local workspace could not be saved.'));
  });
}
const storageKey=key=>sourceKey+key+(key==='instrumented-parent'?':'+navigation.route.count:'');
const identity=()=>[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];
function multiply(a,b){return b.map(col=>a.map((_,r)=>a.reduce((v,c,k)=>v+c[r]*col[k],0)));}
function status(text,error=false){$('status').textContent=text;$('status').toggleAttribute('data-error',error);}
function audit(){
  $('engine-state').textContent=api?'Loaded':frame?'Loading':'Not loaded';
  $('part-files').textContent=[...new Set(resources.filter(r=>r.type==='authoring').map(r=>r.label))].join(', ')||'None';
  const kinds=new Set(preview?.stats().displays.map(d=>d.kind));
  $('display-source').textContent=native?'Native editor':kinds.has('packed-preview')?'Packed comparison':kinds.has('native-export')?(kinds.has('saved-preview')?'Saved + exported':'SolidCraft export'):'SolidCraft saved cache';
  $('resource-list').replaceChildren(...resources.map(r=>{const li=document.createElement('li');li.textContent=`${r.label} · ${(r.bytes/1024).toFixed(1)} kB · ${r.type}`;return li;}));
}
async function load(url,type,label){
  if(!requests.has(url))requests.set(url,(async()=>{const r=await fetch(url);if(!r.ok)throw new Error(`${label} could not be loaded.`);const b=await r.arrayBuffer();resources.push({url,type,label,bytes:b.byteLength});audit();return b;})().catch(e=>{requests.delete(url);throw e;}));
  return requests.get(url);
}
async function json(url,type,label){return JSON.parse(new TextDecoder().decode(await load(url,type,label)));}
function setBusy(value,label){
  busy=value;navigation?.setDisabled(value);
  for(const el of document.querySelectorAll('button,select,#native-controls input'))el.disabled=value;
  $('copies').disabled=value||native;$('section').disabled=value||native;$('explode').disabled=value||native||!context?.assembly||context.node==='instrumented-parent';
  $('display-mode').disabled=value||native;
  $('publish').disabled=value||!api||current==='instrumented-parent';
  $('dimensions').hidden=!native||!catalog.nodes[current]?.parameters?.length;
  $('undo').disabled=value||!api;
  $('state-label').textContent=label||(native?'Native '+(catalog.nodes[current]?.label||'workspace'):context?.node==='instrumented-parent'?'Saved instrumented exterior':context?.assembly?'Direct components · saved geometry':'Saved part geometry');
  $('state-dot').toggleAttribute('data-ready',!value);
  audit();
}
function note(label,ms){const row=document.createElement('li'),text=document.createElement('span'),value=document.createElement('strong');text.textContent=label;value.textContent=ms<1000?`${Math.round(ms)} ms`:`${(ms/1000).toFixed(2)} s`;row.append(text,value);$('timing-list').prepend(row);while($('timing-list').children.length>7)$('timing-list').lastChild.remove();}
async function action(label,run){if(busy)return;setBusy(true,label);const start=performance.now();try{clearTimeout(timer);if(pollWork)await pollWork;await run();note(label,performance.now()-start);}catch(e){status(e.message,true);$('cover').hidden=true;console.error(e);}finally{setBusy(false);if(pending){const next=pending;pending=null;await openRoute(next);}else if(pauseWanted){pauseWanted=false;if(api&&native)$('pause').click();}}}
async function children(key){if(!manifests.has(key)){const node=catalog.nodes[key];manifests.set(key,await json(node.children,'assembly interfaces',node.label+' direct components'));}return manifests.get(key);}
async function resolve(route){
  let world=identity(),node='instrumented-parent';
  const trail=[{label:'Parent assembly',node,path:['parent']}];
  for(let depth=1;depth<route.path.length;depth++){
    let item;
    if(depth===1){const index=Number(route.path[depth].replace('module-',''))-1;if(index<0||index>=route.count||!Number.isInteger(index))throw new Error('This assembly occurrence is unavailable.');const cols=Math.ceil(Math.sqrt(route.count));item={node:'instrumented',label:catalog.nodes.instrumented.label,transform:identity()};item.transform[3]=[index%cols*catalog.pitch,Math.floor(index/cols)*catalog.pitch,0,1];}
    else{if(!catalog.nodes[node].children)throw new Error('This part has no child assembly.');item=(await children(node)).occurrences.find(o=>o.id===route.path[depth]);if(!item)throw new Error('This component path is unavailable.');}
    world=multiply(world,item.transform);node=item.node;trail.push({label:item.label||catalog.nodes[node].label,node,path:route.path.slice(0,depth+1)});
  }
  const assembly=Boolean(catalog.nodes[node].children)||node==='instrumented-parent';
  const items=node==='instrumented-parent'?Array.from({length:route.count},(_,i)=>({id:'module-'+(i+1),node:'instrumented',label:catalog.nodes.instrumented.label+(route.count>1?' '+(i+1):''),transform:identity(),explode:[0,0,0]})):assembly?(await children(node)).occurrences:[{id:'self',node,transform:identity(),explode:[0,0,0],path:route.path}];
  return {node,world,trail,items,assembly};
}
async function capture(){if(!api||!current)return;const doc=await api.request('document.export');revision=doc.revision;models.set(current,doc.text);await workspaceStore(current,doc.text);await api.request('document.saved',{revision});}
async function nativeText(key){
  if(models.has(key))return models.get(key);
  const kept=await workspaceStore(key);
  if(kept){models.set(key,kept);if(catalog.nodes[key]?.reference&&!await workspaceStore(key+':published')){const original=new TextDecoder().decode(await load(catalog.nodes[key].native,'assembly snapshot',catalog.nodes[key].label+' published state'));await seedReference(key,original);}resources.push({url:'local:'+key,type:'local native',label:catalog.nodes[key]?.label||key,bytes:new TextEncoder().encode(kept).length});audit();return kept;}
  const node=catalog.nodes[key],url=node?.native||`${base}/native/${key}`;
  const text=new TextDecoder().decode(await load(url,node?.children?'assembly snapshot':node?'authoring':'published reference',node?.label||key));requests.delete(url);models.set(key,text);await seedReference(key,text);return text;
}
async function engine(){
  if(api)return;
  $('cover-title').textContent='Starting SolidCraft';$('cover-detail').textContent='Opening this workspace from its saved native geometry.';$('cover').hidden=false;
  frame=document.createElement('iframe');frame.title='SolidCraft native assembly workspace';
  const ready=new Promise((resolve,reject)=>{const timeout=setTimeout(()=>done(new Error('The native runtime did not start.')),240000);const handler=e=>{if(e.origin!==location.origin||e.source!==frame?.contentWindow)return;if(e.data?.type==='solidcraft-lab-ready')done();if(e.data?.type==='solidcraft-lab-error')done(new Error(e.data.error));};function done(error){clearTimeout(timeout);removeEventListener('message',handler);error?reject(error):resolve();}addEventListener('message',handler);});
  frame.src='/labs/solidcraft/beduan/editor?embed=editor'+(navigator.gpu?'':'&webgl');$('native-stage').append(frame);audit();await ready;api=frame.contentWindow.solidcraft;audit();
}
async function importNative(key,{captureFirst=true}={}){if(captureFirst)await capture();const previous=current;const text=await nativeText(key);const result=await api.request('document.import',{text,name:catalog.nodes[key]?.label||key});if(result.errors)throw new Error('The native workspace has feature errors.');current=key;for(const loaded of models.keys())if(loaded!==key)models.delete(loaded);await capture();}
async function sync(){const model=await api.inspect();$('native-title').textContent=catalog.nodes[current]?.label||current;$('native-scope').textContent=`${$('native-title').textContent} · ${model.timeline.length} own features`;$('native-bodies').textContent=String(model.bodies.length);$('dimension-inputs').replaceChildren();for(const name of catalog.nodes[current]?.parameters||[]){const p=model.params.find(p=>p.name===name);if(!p)continue;const label=document.createElement('label');label.className='parameter';const span=document.createElement('span');span.textContent=name.replaceAll('_',' ');const input=document.createElement('input');input.name=name;input.value=p.expression;label.append(span,input);$('dimension-inputs').append(label);}return model;}
function poll(){clearTimeout(timer);if(!api||!native||document.hidden||busy)return;timer=setTimeout(()=>{if(busy)return;pollWork=(async()=>{try{const r=await api.request('document.revision');if(r.revision!==revision){await capture();if(!document.activeElement?.closest('#dimensions'))await sync();}}catch(e){status(e.message,true);}})().finally(()=>{pollWork=null;poll();});},2500);}
async function unload(){clearTimeout(timer);await capture();frame?.remove();frame=null;api=null;current=null;models.clear();audit();}
async function showRoute(route,{fit=false}={}){
  if(api)await unload();native=false;context=await resolve(route);navigation.setContext(context);navigation.setNative(false);
  $('preview').hidden=false;$('native-stage').hidden=true;$('native-controls').hidden=true;$('reference').hidden=true;$('pause').hidden=true;$('cover').hidden=true;preview.visible(true);$('native-scope').textContent='Closed';$('native-bodies').textContent='Not loaded';
  exploded=false;$('explode').textContent='Explode';await preview.show(route,context,{fit,hidden:navigation.hidden});
  audit();
  $('fit-note').hidden=!catalog.nodes[context.node].fit;$('fit-note').textContent=catalog.nodes[context.node].fit||'';
  status('Select a component, then Open. Each assembly loads its direct saved shapes. Native designs stay closed until Edit.');
}
async function openRoute(route){if(busy){pending=route;return;}await action('Opening assembly level',()=>showRoute(route));}
async function edit(key,path){if(!key)return;await action('Opening native design',async()=>{if(path.join('/')!==navigation.route.path.join('/')){navigation.go({path,count:navigation.route.count},{replace:false,force:true});pending=null;context=await resolve({path,count:navigation.route.count});navigation.setContext(context);}await engine();await importNative(key);await api.execute('view.ribbon_tabs_only',{on:true});if(key==='instrumented-parent'&&JSON.parse(models.get(key)).occurrences.length===1&&navigation.route.count>1){const columns=Math.ceil(Math.sqrt(navigation.route.count));for(let i=1;i<navigation.route.count;i++)await api.execute('occurrence.copy',{component:'Instrumented carbonator',translate:[i%columns*catalog.pitch,Math.floor(i/columns)*catalog.pitch,0]});}native=true;navigation.setNative(true);preview.visible(false);$('preview').hidden=true;$('native-stage').hidden=false;$('native-controls').hidden=false;$('reference').hidden=false;$('pause').hidden=false;$('cover').hidden=true;await sync();status('Native edits stay in this browser. Update parents republishes saved shapes along the affected assembly path.');});poll();}
const blank=()=>JSON.stringify({format:'solidcraft/51',name:'Published reference',units:'mm',params:[],features:[],next_id:1});
async function save(key){await api.execute('file.save_as',{path:key+'.sc',cache:true,overwrite:true});await capture();}
function referenceProjection(doc,node){
  const included=doc.features.filter(f=>!f.body_names?.length||f.body_names.some(name=>name==='Vessel tube'||!(node.omit||[]).some(token=>name.includes(token))));
  const components=new Set(included.map(f=>f.component)),bodies=new Set(included.flatMap(f=>f.body_names||[]));
  const filter=map=>Object.fromEntries(Object.entries(map||{}).filter(([name])=>bodies.has(name)));
  return JSON.stringify({features:included,metadata:doc.metadata,
    occurrences:doc.occurrences.filter(o=>components.has(o.component)).map(o=>({...o,transform:o.transform.map(col=>col.map(v=>Math.round(v*1e9)/1e9))})),
    components:doc.components.filter(c=>components.has(c.id)),materials:filter(doc.materials),
    appearances:{...doc.appearances,bodies:filter(doc.appearances?.bodies),components:Object.fromEntries(Object.entries(doc.appearances?.components||{}).filter(([id])=>components.has(Number(id))))}});
}
async function seedReference(key,text){
  const node=catalog.nodes[key];if(!node?.reference||await workspaceStore(key+':published'))return;
  await workspaceStore(key+':published',referenceProjection(JSON.parse(text),node));
}
async function flattened(key){
  const node=catalog.nodes[key],reference=key+'-reference';
  const source=JSON.parse(models.get(key)),projection=referenceProjection(source,node);
  if(await workspaceStore(key+':published')===projection)return false;
  status('Publishing '+node.label+' saved reference…');
  await api.request('document.import',{text:blank(),name:node.label+' publication'});current=null;
  await api.execute('component.insert_design',{path:key+'.sc',name:node.label});await api.execute('component.break_link',{component:node.label});
  let barrel;
  if(node.barrel){
    const measured=await api.execute('inspect.measure',{}),tube=measured.bodies.find(b=>b.name==='Vessel tube');
    const faces=await api.execute('model.faces',{body:'Vessel tube'}),cylinders=faces.faces.filter(f=>f.cylinder&&Math.abs(f.cylinder.axis[2])>.999999).map(f=>f.cylinder).sort((a,b)=>a.radius-b.radius),radii=cylinders.map(c=>c.radius);
    if(!tube||radii.length<2)throw new Error('The barrel requires cylindrical source interfaces.');
    const clean=x=>Math.round(x*1e9)/1e9;barrel={outside:clean(radii.at(-1)*2),bore:clean(radii[0]*2),length:clean(tube.bbox.max[2]-tube.bbox.min[2]),base:[clean(cylinders.at(-1).origin[0]),clean(cylinders.at(-1).origin[1]),clean(tube.bbox.min[2])]};
  }
  const remove=(await api.inspect()).bodies.map(b=>b.name).filter(name=>(node.omit||[]).some(token=>name.includes(token)));
  if(remove.length)await api.execute('solid.remove',{bodies:remove});
  if(barrel){
    await api.execute('component.activate',{component:0});
    await api.execute('solid.cylinder',{diameter:barrel.outside,height:barrel.length,base:barrel.base,axis:'Z',body_name:'Published barrel'});
    await api.execute('solid.cylinder',{diameter:barrel.bore,height:barrel.length,base:barrel.base,axis:'Z',operation:'cut',targets:['Published barrel']});
    await api.execute('material.assign',{bodies:['Published barrel'],material:source.materials?.['Vessel tube']||'Stainless Steel'});
    const look=source.appearances?.bodies?.['Vessel tube'];
    await api.execute('appearance.assign',{bodies:['Published barrel'],color:look?.color||'#b4bbc5',pbr:look?.pbr||{metallic:.8,roughness:.32,dielectric_ior:1.5}});
  }
  if(remove.length||barrel){
    await api.execute('file.save_as',{path:key+'-stage.sc',cache:true,overwrite:true});
    await api.request('document.import',{text:blank(),name:node.label+' saved exterior'});
    await api.execute('component.insert_design',{path:key+'-stage.sc',name:node.label});await api.execute('component.break_link',{component:node.label});
  }
  await api.execute('document.metadata.set',{values:source.metadata});await api.execute('file.save_as',{path:reference+'.sc',cache:true,overwrite:true});current=reference;await capture();
  await workspaceStore(key+':published',projection);return true;
}
async function propagate(child){
  const pending=new Set(),changed=new Set([child]);
  function parents(key){for(const [parent,node] of Object.entries(catalog.nodes))if(node.inputs?.some(i=>i.node===key)&&!pending.has(parent)){pending.add(parent);parents(parent);}}
  parents(child);
  while(pending.size){
    const ready=[...pending].filter(key=>!catalog.nodes[key].inputs.some(i=>pending.has(i.node)));
    if(!ready.length)throw new Error('The assembly interfaces contain a dependency cycle.');
    for(const key of ready){
      pending.delete(key);const node=catalog.nodes[key],uses=node.inputs.filter(i=>changed.has(i.node));if(!uses.length)continue;
      status('Updating '+node.label+'…');await new Promise(resolve=>requestAnimationFrame(resolve));
      const started=performance.now();await importNative(key,{captureFirst:false});
      const result=await api.execute('component.update_links',{components:uses.map(i=>i.component)});
      if(result.failed?.length)throw new Error('A selected native link could not be updated.');
      if(!result.updated?.length)continue;
      await save(key);
      if(node.reference&&!await flattened(key))continue;
      changed.add(key);note('Update '+node.label,performance.now()-started);
    }
  }
}
$('dimensions').addEventListener('submit',e=>{e.preventDefault();action('Applying native dimension',async()=>{const changes=Object.fromEntries([...$('dimension-inputs').querySelectorAll('input')].map(i=>[i.name,i.value]));await api.execute('parameters.change',{changes});await capture();await sync();status('Native design updated. Update parents publishes its changed interfaces.');}).then(poll);});
$('undo').addEventListener('click',()=>action('Undoing native edit',async()=>{await api.execute('edit.undo');await capture();await sync();}).then(poll));
$('publish').addEventListener('click',()=>action('Updating affected native parents',async()=>{const edited=current;await save(edited);const changed=!catalog.nodes[edited].reference||await flattened(edited);if(changed)await propagate(edited);const target=current&&catalog.nodes[current]?current:edited;if(current!==target)await importNative(target,{captureFirst:false});await sync();status('Affected native parents updated locally. Reference preview shows the published website snapshot.');}).then(poll));
$('download').addEventListener('click',()=>action('Preparing native download',async()=>{await capture();const url=URL.createObjectURL(new Blob([models.get(current)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=current+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}));
$('fit').addEventListener('click',()=>native?api?.execute('view.fit'):preview.fit());
$('section').addEventListener('change',()=>preview.section($('section').checked));
$('explode').addEventListener('click',()=>{exploded=!exploded;preview.explode(exploded);$('explode').textContent=exploded?'Assemble':'Explode';});
$('display-mode').addEventListener('change',()=>action('Opening '+($('display-mode').value==='native'?'SolidCraft meshes':'packed comparison'),async()=>{
  const mode=$('display-mode').value,url=new URL(location.href);if(mode==='packed')url.searchParams.set('display','packed');else url.searchParams.delete('display');
  history.replaceState(history.state,'',url);preview.mode(mode);await showRoute(navigation.route);
}));
$('reference').addEventListener('click',()=>action('Opening reference preview',()=>showRoute(navigation.route)));
$('pause').addEventListener('click',()=>action('Pausing native workspace',async()=>{paused=current;await unload();native=false;navigation.setNative(true);$('native-stage').hidden=true;$('cover-title').textContent='Native workspace paused';$('cover-detail').textContent='Your local design is saved. Resume to reopen it.';$('cover').hidden=false;$('resume').hidden=false;$('native-controls').hidden=true;$('pause').hidden=true;}));
$('resume').addEventListener('click',()=>edit(paused,navigation.route.path));
document.addEventListener('visibilitychange',()=>{if(document.hidden){if(busy)pauseWanted=true;else if(api)$('pause').click();}else{pauseWanted=false;poll();}});
export function inspectLab(){return {route:navigation?.route,node:context?.node,selection:navigation?.selection,resources:resources.map(r=>({...r})),preview:preview?.stats(),native:{loaded:Boolean(api),current,loadedModelTexts:[...models.keys()]},busy};}
async function start(){
  catalog=await json(assets+'levels.json','assembly catalog','Assembly interfaces');sourceKey='solidcraft-levels:'+catalog.sourceVersion+':';
  preview=await createPreview($('preview'),catalog,load,{onSelect:id=>navigation?.select(id)});
  const mode=new URL(location.href).searchParams.get('display')==='packed'?'packed':'native';$('display-mode').value=mode;preview.mode(mode);
  navigation=createAssemblyNavigation({catalog,onRoute:openRoute,onSelect:id=>preview.select(id),onEdit:edit,onHide:id=>preview.hide(id),onShow:id=>preview.showHidden(id)});
  await action('Opening saved instrumented assembly',()=>showRoute(navigation.route,{fit:true}));
}
start().catch(e=>{status(e.message,true);$('cover-title').textContent='The example could not open';$('cover-detail').textContent=e.message;console.error(e);});
