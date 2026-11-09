// The reference viewer picks components and opens their saved displays without starting native authoring.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createNavigation} from '/js/viewer/navigation.js';

export async function createPreview(host,config,load,{onSelect=()=>{}}={}){
  const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor('#292e37');
  renderer.localClippingEnabled=true;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;
  host.append(renderer.domElement);
  const scene=new THREE.Scene();
  scene.add(new THREE.HemisphereLight('#e6efff','#465469',3));
  for(const [position,intensity] of [[[250,-300,400],5],[[-220,-100,120],3],[[100,220,300],4]]){
    const light=new THREE.DirectionalLight('#ffffff',intensity);light.position.set(...position);scene.add(light);
  }
  const camera=new THREE.PerspectiveCamera(35,1,.1,10000);camera.up.set(0,0,1);
  const root=new THREE.Group(),selectionOverlay=new THREE.Group(),hoverOverlay=new THREE.Group();
  scene.add(root,selectionOverlay,hoverOverlay);
  const clipping=new THREE.Plane(new THREE.Vector3(1,0,0),0);
  const material=new THREE.MeshStandardMaterial({color:0xffffff,vertexColors:true,metalness:.35,roughness:.38,side:THREE.DoubleSide});
  const loader=new GLTFLoader(),geometries=new Map(),edges=new Map();
  let route={path:['parent'],count:1},manifest,exploded=false,section=false,selected=null,hovered=null;
  let hidden=new Set(),drawQueued=false,visible=true,draws=0,navigation;
  let firstDraw;const ready=new Promise(resolve=>firstDraw=resolve);
  function invalidate(){if(!drawQueued){drawQueued=true;requestAnimationFrame(render);}}
  function render(){
    drawQueued=false;
    if(!visible||document.hidden)return;
    const moving=navigation?.update();
    if(navigation&&!moving)navigation.dropStalledGesture();
    renderer.render(scene,camera);draws++;
    if(root.children.length){firstDraw?.();firstDraw=null;}
    if(moving)invalidate();
  }
  async function geometry(url,label){
    if(!geometries.has(url))geometries.set(url,(async()=>{
      const bytes=await load(url,'display',label),gltf=await loader.parseAsync(bytes,location.origin+'/');
      gltf.scene.updateMatrixWorld(true);let result;
      gltf.scene.traverse(node=>{if(node.isMesh){result=node.geometry.clone().applyMatrix4(node.matrixWorld);
        if(!result.getAttribute('color')){
          const color=node.material.color||new THREE.Color('#b4bbc5'),values=new Float32Array(result.getAttribute('position').count*3);
          for(let i=0;i<values.length;i+=3){values[i]=color.r;values[i+1]=color.g;values[i+2]=color.b;}
          result.setAttribute('color',new THREE.BufferAttribute(values,3));
        }
        node.geometry.dispose();node.material?.dispose?.();}});
      if(!result)throw new Error('The saved shape contains no display surface.');
      result.computeBoundingBox();return result;
    })().catch(error=>{geometries.delete(url);throw error;}));
    return geometries.get(url);
  }
  let moduleGeometry;
  function position(index){
    const columns=Math.ceil(Math.sqrt(route.count));
    return [index%columns*config.pitch,Math.floor(index/columns)*config.pitch,0];
  }
  function worldBounds(){
    const box=new THREE.Box3(),matrix=new THREE.Matrix4();
    root.updateMatrixWorld(true);
    for(const mesh of root.children){
      if(!mesh.visible)continue;
      if(mesh.isInstancedMesh){
        for(let i=0;i<mesh.count;i++){
          if(hidden.has('module-'+(i+1)))continue;
          mesh.getMatrixAt(i,matrix);
          box.union(mesh.geometry.boundingBox.clone().applyMatrix4(matrix));
        }
      }else box.expandByObject(mesh);
    }
    return box;
  }
  navigation=createNavigation({camera,renderer,getGroup:()=>root,getBounds:worldBounds,invalidate,gizmoClassName:'lab-viewcube',gizmoSize:()=>matchMedia('(max-width:700px)').matches?100:140});
  host.append(navigation.gizmoCanvas);
  const controls=navigation.controls;
  function clearOverlay(group){
    for(const child of [...group.children]){group.remove(child);child.material.dispose();}
  }
  function paint(group,id,color,opacity){
    clearOverlay(group);if(!id)return;
    root.updateMatrixWorld(true);
    for(const mesh of root.children){
      if(!mesh.visible)continue;
      const matrix=new THREE.Matrix4();
      if(mesh.isInstancedMesh){
        if(!id.startsWith('module-')||hidden.has(id))continue;
        const index=Number(id.slice(7))-1;if(index<0||index>=mesh.count)continue;mesh.getMatrixAt(index,matrix);
      }else{
        if(mesh.userData.component!==id&&id!=='assembly')continue;
        matrix.copy(mesh.matrixWorld);
      }
      if(!edges.has(mesh.geometry))edges.set(mesh.geometry,new THREE.EdgesGeometry(mesh.geometry,30));
      const planes=section?[clipping]:[];
      const shell=new THREE.Mesh(mesh.geometry,new THREE.MeshBasicMaterial({color,opacity,transparent:true,side:THREE.DoubleSide,depthWrite:false,depthTest:false,clippingPlanes:planes}));
      const wire=new THREE.LineSegments(edges.get(mesh.geometry),new THREE.LineBasicMaterial({color,transparent:true,opacity:.95,depthTest:false,clippingPlanes:planes}));
      shell.applyMatrix4(matrix);wire.applyMatrix4(matrix);shell.renderOrder=993;wire.renderOrder=994;group.add(shell,wire);
    }
  }
  function overlays(){paint(selectionOverlay,selected,0xffa733,.18);paint(hoverOverlay,hovered===selected?null:hovered,0x9fd8ff,.1);invalidate();}
  function clearMeshes(){for(const child of [...root.children]){root.remove(child);if(child.isInstancedMesh)child.dispose();}}
  async function show(next,children,{fit:shouldFit=false,hidden:nextHidden=[]}={}){
    route={path:[...next.path],count:next.count};manifest=children;hidden=new Set(nextHidden);exploded=false;selected=null;hovered=null;
    clearOverlay(selectionOverlay);clearOverlay(hoverOverlay);
    const parent=route.path.length===1;
    const base=new THREE.Matrix4().fromArray(children.world.flat());
    clipping.constant=-base.elements[12];
    if(parent&&!moduleGeometry)moduleGeometry=await geometry(config.nodes.instrumented.preview,'Instrumented carbonator saved exterior');
    const parts=parent?[]:children.items;
    const shapes=await Promise.all(parts.map(async item=>[item,await geometry(config.nodes[item.node].preview,config.nodes[item.node].label+' saved shape')]));
    clearMeshes();
    if(parent){
      const instances=new THREE.InstancedMesh(moduleGeometry,material,route.count);
      for(let i=0;i<route.count;i++){
        const matrix=new THREE.Matrix4().makeTranslation(...position(i));
        if(hidden.has('module-'+(i+1)))matrix.scale(new THREE.Vector3(0,0,0));
        instances.setMatrixAt(i,matrix);
      }
      instances.instanceMatrix.needsUpdate=true;root.add(instances);
    }else{
      for(const [item,shape] of shapes){
        const mesh=new THREE.Mesh(shape,material);
        mesh.userData.component=item.id;mesh.userData.occurrence=item;
        mesh.applyMatrix4(new THREE.Matrix4().fromArray(item.transform.flat()).premultiply(base));
        mesh.visible=!hidden.has(item.id);root.add(mesh);
      }
    }
    if(shouldFit)fit();else{navigation.fitDepth();invalidate();}
  }
  function fit(){
    const bounds=worldBounds();if(bounds.isEmpty())return;
    const center=bounds.getCenter(new THREE.Vector3()),radius=bounds.getSize(new THREE.Vector3()).length()/2;
    const distance=radius/Math.sin(THREE.MathUtils.degToRad(camera.fov/2))/Math.min(camera.aspect,1)*1.12;
    navigation.dropStalledGesture();camera.up.set(0,0,1);
    camera.position.copy(center).add(new THREE.Vector3(1.1,-1.6,.85).normalize().multiplyScalar(distance));
    controls.target.copy(center);controls.update();navigation.fitDepth();invalidate();
  }
  function setSection(value){
    section=value;material.clippingPlanes=section?[clipping]:[];material.needsUpdate=true;overlays();
  }
  function setHidden(id,value){
    if(id===null)hidden.clear();else if(value)hidden.add(id);else hidden.delete(id);
    for(const mesh of root.children){
      if(mesh.isInstancedMesh){
        for(let i=0;i<mesh.count;i++){
          const matrix=new THREE.Matrix4().makeTranslation(...position(i));
          if(hidden.has('module-'+(i+1)))matrix.scale(new THREE.Vector3(0,0,0));mesh.setMatrixAt(i,matrix);
        }
        mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();
      }else mesh.visible=!hidden.has(mesh.userData.component);
    }
    if(hidden.has(selected))selected=null;hovered=null;overlays();
  }
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
  function pick(event){
    const rect=renderer.domElement.getBoundingClientRect();
    pointer.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1);
    camera.updateMatrixWorld();root.updateMatrixWorld(true);raycaster.setFromCamera(pointer,camera);
    const hit=raycaster.intersectObjects(root.children.filter(mesh=>mesh.visible),false).find(hit=>!section||clipping.distanceToPoint(hit.point)>=0);
    if(!hit)return null;
    const id=hit.object.isInstancedMesh?'module-'+(hit.instanceId+1):hit.object.userData.component;
    return hidden.has(id)?null:id;
  }
  let down;
  renderer.domElement.addEventListener('pointerdown',event=>{down=event.isPrimary?{id:event.pointerId,x:event.clientX,y:event.clientY}:null;});
  renderer.domElement.addEventListener('pointermove',event=>{
    if(!event.buttons&&event.pointerType!=='touch'){
      const next=pick(event);if(next!==hovered){hovered=next;overlays();}
      renderer.domElement.style.cursor=next?'pointer':'';
    }
  });
  renderer.domElement.addEventListener('pointerleave',()=>{hovered=null;overlays();});
  renderer.domElement.addEventListener('pointercancel',()=>down=null);
  renderer.domElement.addEventListener('pointerup',event=>{
    if(!down||event.pointerId!==down.id)return;
    const start=down;down=null;
    if(event.button!==0||Math.hypot(event.clientX-start.x,event.clientY-start.y)>6||navigation.isTouchGesture()||host.classList.contains('cad-gesturing'))return;
    onSelect(pick(event));
  });
  const resize=new ResizeObserver(()=>{
    const {width,height}=host.getBoundingClientRect();if(!width||!height)return;
    renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();navigation.resize();invalidate();
  });resize.observe(host);
  const {width,height}=host.getBoundingClientRect();renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();navigation.resize();
  return {
    ready,show,fit,invalidate,
    select(id){selected=id;hovered=null;overlays();},
    hide(id){setHidden(id,true);},showHidden(id){setHidden(id,false);},
    section:setSection,
    explode(value){
      if(route.path.length===1||!manifest.assembly)return;exploded=value;
      for(const mesh of root.children){
        const item=mesh.userData.occurrence;
        mesh.matrix.identity();mesh.position.set(0,0,0);mesh.quaternion.identity();mesh.scale.set(1,1,1);
        const matrix=new THREE.Matrix4().fromArray(item.transform.flat());
        if(value)matrix.premultiply(new THREE.Matrix4().makeTranslation(...item.explode));
        matrix.premultiply(new THREE.Matrix4().fromArray(manifest.world.flat()));mesh.applyMatrix4(matrix);
      }
      overlays();fit();
    },
    visible(value){visible=value;navigation.controls.enabled=value;if(value){navigation.resetFrameClock();invalidate();}},
    stats(){return {calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,count:route.path.length===1?route.count:1,expanded:route.path.length>1,path:[...route.path],selected,hidden:[...hidden],geometries:renderer.info.memory.geometries,draws,camera:{position:camera.position.toArray(),up:camera.up.toArray(),target:controls.target.toArray()}};},
    dispose(){resize.disconnect();navigation.dispose();clearOverlay(selectionOverlay);clearOverlay(hoverOverlay);for(const value of geometries.values())value.then(shape=>shape.dispose());for(const shape of edges.values())shape.dispose();material.dispose();renderer.dispose();renderer.domElement.remove();},
  };
}
