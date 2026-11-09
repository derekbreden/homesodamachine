// The lab's component panel and history follow the selection and Open flow used by the parts viewer.
const $=id=>document.getElementById(id);
const counts=[1,8,64];
const leafIds=['tube','bottom-endcap','top-endcap'];

function routeFromURL(){
  const count=Number(new URLSearchParams(location.search).get('copies'))||1;
  const path=location.hash.slice(1).split('/');
  const result={path:['parent'],count:counts.includes(count)?count:1};
  if(path[0]==='parent'&&/^core-[1-9]\d*$/.test(path[1])&&Number(path[1].slice(5))<=result.count){
    result.path.push(path[1]);
    if(leafIds.includes(path[2]))result.path.push(path[2]);
  }
  return result;
}
const routeKey=route=>JSON.stringify(route);
const copy=route=>({path:[...route.path],count:route.count});

export function createComponentNavigation({onRoute,onSelect,onEdit,onHide,onShow}){
  let route=routeFromURL(),manifest,selection=null,native=false,disabled=false;
  const hiddenByView=new Map();
  let index=0;
  const entries=[copy(route)];
  const state=()=>({...history.state,solidcraftNavigation:{index}});
  function url(next){
    const query=new URLSearchParams(location.search);
    if(next.count===1)query.delete('copies');else query.set('copies',next.count);
    return location.pathname+(query.size?'?'+query:'')+'#'+next.path.join('/');
  }
  history.replaceState(state(),'',url(route));
  const instance=()=>Number(route.path[1]?.slice(5)||1);
  const coreLabel=()=>route.count===1?'Carbonator core':'Carbonator core '+instance();
  const title=path=>path.length===1?'Parent assembly':path.length===2?coreLabel():manifest?.occurrences.find(item=>item.id===path[2])?.label||path[2].replaceAll('-',' ');
  const kind=()=>route.path.length===1?'parent':route.path.length===2?'core':route.path[2]==='tube'?'tube':'endcap';
  const hidden=()=>{
    const key=routeKey(route);
    if(!hiddenByView.has(key))hiddenByView.set(key,new Set());
    return hiddenByView.get(key);
  };
  function items(){
    if(route.path.length===1)return Array.from({length:route.count},(_,i)=>({
      id:'core-'+(i+1),label:route.count===1?'Carbonator core':'Carbonator core '+(i+1),
      description:'Assembly envelope',kind:'core',path:['parent','core-'+(i+1)],
    }));
    return (manifest?.occurrences||[]).filter(item=>route.path.length===2||item.id===route.path[2]).map(item=>({
      id:item.id,label:item.label,description:item.part==='endcap'?'Shared endcap definition':'Tube wall',
      kind:item.part,path:[...route.path.slice(0,2),item.id],
    }));
  }
  function selected(){
    if(selection==='assembly')return {id:'assembly',label:coreLabel(),description:'Exact saved parts',kind:'core',path:route.path.slice(0,2)};
    return items().find(item=>item.id===selection);
  }
  function select(id){
    if(disabled)return;
    selection=id;onSelect(id);renderPanel();renderList();
  }
  function button(label,callback,className){
    const node=document.createElement('button');node.type='button';node.textContent=label;
    if(className)node.className=className;
    node.disabled=disabled;node.addEventListener('click',callback);return node;
  }
  function renderCrumbs(){
    $('breadcrumbs').replaceChildren();
    route.path.forEach((_,depth)=>{
      if(depth){const sep=document.createElement('span');sep.className='cad-crumb-sep';sep.textContent='/';$('breadcrumbs').append(sep);}
      const path=route.path.slice(0,depth+1);
      if(depth===route.path.length-1){
        const here=document.createElement('span');here.className='cad-crumb-here';here.textContent=title(path);here.setAttribute('aria-current','page');$('breadcrumbs').append(here);
      }else $('breadcrumbs').append(button(title(path),()=>go({path,count:route.count}),'cad-crumb-step'));
    });
    $('breadcrumbs').scrollLeft=$('breadcrumbs').scrollWidth;
  }
  function renderList(){
    $('component-list').replaceChildren();
    if(route.path.length===2){
      const group=button(coreLabel(),()=>select('assembly'),'component-group');
      group.setAttribute('aria-pressed',String(selection==='assembly'));$('component-list').append(group);
    }
    for(const item of items()){
      const row=button(item.label,()=>select(item.id),'component-row');
      row.dataset.component=item.id;row.setAttribute('aria-pressed',String(selection===item.id));
      const detail=document.createElement('small');detail.textContent=hidden().has(item.id)?'Hidden':item.description;row.append(detail);
      $('component-list').append(row);
    }
    $('component-list-title').textContent=route.path.length===1?'Components':route.path.length===2?'Core components':'Part';
    $('edit-current').textContent='Edit '+(kind()==='parent'?'parent':kind()==='core'?'core':kind()==='tube'?'tube':'endcap')+' in SolidCraft';
  }
  function renderPanel(){
    const item=selected();
    $('component-panel').hidden=native||(!item&&!hidden().size);
    $('selected-component').textContent=item?.label||'Hidden components';
    $('component-description').textContent=item?.description||'Hidden only in this view.';
    $('component-actions').hidden=!item;
    $('open-component').hidden=!item||routeKey({path:item.path,count:route.count})===routeKey(route);
    $('open-component').textContent=item?.kind==='core'?'Open carbonator core':'Open component';
    $('hide-component').hidden=!item||item.id==='assembly';
    $('edit-component').hidden=!item;
    $('component-holds').replaceChildren();
    if(item?.id==='assembly'){
      const head=document.createElement('p');head.textContent=coreLabel()+' holds '+items().length;head.className='component-holds-head';$('component-holds').append(head);
      for(const child of items())$('component-holds').append(button(child.label,()=>select(child.id),'component-holds-row'));
    }
    $('hidden-components').replaceChildren();
    if(hidden().size){
      const head=document.createElement('div');head.className='component-hidden-head';
      const label=document.createElement('span');label.textContent='Hidden ('+hidden().size+')';
      head.append(label,button('Show all',()=>{hidden().clear();onShow(null);renderPanel();renderList();},'component-show-all'));
      $('hidden-components').append(head);
      for(const id of hidden()){
        const item=items().find(item=>item.id===id),row=document.createElement('div');row.className='component-hidden-row';
        const label=document.createElement('span');label.textContent=item?.label||id;
        row.append(label,button('Show',()=>{hidden().delete(id);onShow(id);renderPanel();renderList();},'component-show'));
        $('hidden-components').append(row);
      }
    }
  }
  function render(){
    renderCrumbs();renderList();renderPanel();$('copies').value=String(route.count);
    $('component-browser').hidden=native;
    $('navigation-hint').hidden=native;
    $('navigation-hint').textContent='Click a component, then Open. Breadcrumbs and browser Back return to the assembly.';
  }
  function go(next,{replace=false,notify=true}={}){
    next=copy(next);
    if(routeKey(next)===routeKey(route)){if(notify)onRoute(next);return;}
    if(!replace&&notify&&next.count===route.count&&next.path.length<route.path.length){
      const prior=entries.findLastIndex((entry,i)=>i<index&&routeKey(entry)===routeKey(next));
      if(prior>=0){history.go(prior-index);return;}
    }
    if(replace){entries[index]=next;history.replaceState(state(),'',url(next));}
    else{entries.splice(index+1);entries.push(next);index++;history.pushState(state(),'',url(next));}
    route=next;selection=null;render();if(notify)onRoute(copy(route));
  }
  addEventListener('popstate',()=>{
    route=routeFromURL();
    const known=history.state?.solidcraftNavigation?.index;
    if(Number.isInteger(known)&&entries[known])index=known;
    else{index=0;entries.splice(0,entries.length,copy(route));history.replaceState(state(),'',url(route));}
    selection=null;render();onRoute(copy(route));
  });
  $('copies').addEventListener('change',()=>go({path:['parent'],count:Number($('copies').value)}));
  $('open-component').addEventListener('click',()=>{const item=selected();if(item)go({path:item.path,count:route.count});});
  $('hide-component').addEventListener('click',()=>{if(!selection)return;hidden().add(selection);onHide(selection);selection=null;onSelect(null);renderPanel();renderList();});
  $('clear-component').addEventListener('click',()=>select(null));
  $('edit-component').addEventListener('click',()=>{const item=selected();if(item)onEdit(item.kind,item.path);});
  $('edit-current').addEventListener('click',()=>onEdit(kind(),route.path));
  render();
  return {
    get route(){return copy(route);},get kind(){return kind();},get hidden(){return [...hidden()];},
    go,select,items,
    setManifest(value){manifest=value;render();},
    setNative(value){native=value;render();},
    setDisabled(value){disabled=value;},
    get selection(){return selection;},
  };
}
