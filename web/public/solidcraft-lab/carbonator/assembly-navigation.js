// The assembly lab uses selection, Open, breadcrumbs and browser history at every native component boundary.
const $=id=>document.getElementById(id),counts=[1,8,64];
const key=r=>JSON.stringify(r),copy=r=>({path:[...r.path],count:r.count});
function readRoute(){
  const count=Number(new URLSearchParams(location.search).get('copies'))||1;
  const path=location.hash.slice(1).split('/').filter(Boolean);
  return {path:path[0]==='parent'&&path.every(p=>/^[a-z\d-]+$/.test(p))?path:['parent'],count:counts.includes(count)?count:1};
}
export function createAssemblyNavigation({catalog,onRoute,onSelect,onEdit,onHide,onShow}){
  let route=readRoute(),context,selection=null,native=false,disabled=false;
  let index=0;const entries=[copy(route)],state=()=>({...history.state,solidcraftLevels:{index}});
  const hiddenViews=new Map(),hidden=()=>{const k=key(route);if(!hiddenViews.has(k))hiddenViews.set(k,new Set());return hiddenViews.get(k);};
  const items=()=>context?.items.map(i=>({...i,path:i.path||[...route.path,i.id],label:i.label||catalog.nodes[i.node].label,description:catalog.nodes[i.node].material||'Saved component'}))||[];
  const selected=()=>items().find(i=>i.id===selection);
  function button(label,run,cls){const b=document.createElement('button');b.type='button';b.textContent=label;if(cls)b.className=cls;b.disabled=disabled;b.addEventListener('click',run);return b;}
  function url(r){const q=new URLSearchParams(location.search);if(r.count===1)q.delete('copies');else q.set('copies',r.count);return location.pathname+(q.size?'?'+q:'')+'#'+r.path.join('/');}
  history.replaceState(state(),'',url(route));
  function render(){
    $('breadcrumbs').replaceChildren();
    for(const [i,item] of (context?.trail||[{label:'Parent assembly',path:['parent']}]).entries()){
      if(i){const s=document.createElement('span');s.className='cad-crumb-sep';s.textContent='/';$('breadcrumbs').append(s);}
      if(key(item.path)===key(route.path)){const s=document.createElement('span');s.className='cad-crumb-here';s.textContent=item.label;s.setAttribute('aria-current','page');$('breadcrumbs').append(s);}
      else $('breadcrumbs').append(button(item.label,()=>go({path:item.path,count:route.count}),'cad-crumb-step'));
    }
    $('breadcrumbs').scrollLeft=$('breadcrumbs').scrollWidth;
    $('component-list').replaceChildren();
    for(const item of items()){
      const b=button(item.label,()=>select(item.id),'component-row');b.dataset.component=item.id;b.setAttribute('aria-pressed',String(item.id===selection));
      const small=document.createElement('small');small.textContent=hidden().has(item.id)?'Hidden':item.description;b.append(small);$('component-list').append(b);
    }
    $('component-list-title').textContent=context?.assembly?'Components':'Part';
    $('edit-current').textContent='Edit this '+(context?.assembly?'assembly':'part')+' in SolidCraft';
    $('copies').value=String(route.count);$('component-browser').hidden=native;$('navigation-hint').hidden=native;
    const item=selected(),node=item&&catalog.nodes[item.node];
    $('component-panel').hidden=native||(!item&&!hidden().size);
    $('selected-component').textContent=item?.label||'Hidden components';
    $('component-description').textContent=node?[node.material,node.description].filter(Boolean).join(' · '):'Hidden only in this view.';
    $('component-actions').hidden=!item;$('open-component').hidden=!item||key(item.path)===key(route.path);
    $('open-component').textContent=node?.children?'Open assembly':'Open part';
    $('component-holds').replaceChildren();$('hidden-components').replaceChildren();
    if(hidden().size){
      const head=document.createElement('div');head.className='component-hidden-head';head.append(document.createTextNode('Hidden components'),button('Show all',()=>{hidden().clear();onShow(null);render();}));$('hidden-components').append(head);
      for(const id of hidden()){const row=document.createElement('div');row.className='component-hidden-row';row.append(document.createTextNode(items().find(i=>i.id===id)?.label||id),button('Show',()=>{hidden().delete(id);onShow(id);render();}));$('hidden-components').append(row);}
    }
  }
  function select(id){if(disabled)return;selection=id;onSelect(id);render();}
  function go(next,{replace=false,force=false}={}){
    if(disabled&&!force)return;
    if(!replace&&next.count===route.count&&next.path.length<route.path.length&&next.path.every((p,i)=>p===route.path[i])){
      const prior=entries.findLastIndex((entry,i)=>i<index&&key(entry)===key(next));
      if(prior>=0){history.go(prior-index);return;}
    }
    route=copy(next);selection=null;context=null;
    if(replace){entries[index]=copy(route);history.replaceState(state(),'',url(route));}
    else{entries.splice(index+1);entries.push(copy(route));index++;history.pushState(state(),'',url(route));}
    onSelect(null);onRoute(copy(route));
  }
  addEventListener('popstate',()=>{
    route=readRoute();selection=null;context=null;
    const known=history.state?.solidcraftLevels?.index;
    if(Number.isInteger(known)&&entries[known])index=known;
    else{index=0;entries.splice(0,entries.length,copy(route));history.replaceState(state(),'',url(route));}
    onSelect(null);onRoute(copy(route));
  });
  $('copies').addEventListener('change',()=>go({path:['parent'],count:Number($('copies').value)}));
  $('open-component').addEventListener('click',()=>{const item=selected();if(item)go({path:item.path,count:route.count});});
  $('hide-component').addEventListener('click',()=>{if(!selection)return;hidden().add(selection);onHide(selection);selection=null;onSelect(null);render();});
  $('clear-component').addEventListener('click',()=>select(null));
  $('edit-component').addEventListener('click',()=>{const item=selected();if(item)onEdit(item.node,item.path);});
  $('edit-current').addEventListener('click',()=>onEdit(context?.node,route.path));
  render();
  return {go,select,items,get route(){return copy(route);},get hidden(){return [...hidden()];},get selection(){return selection;},setContext(value){context=value;render();},setNative(value){native=value;render();},setDisabled(value){disabled=value;render();}};
}
