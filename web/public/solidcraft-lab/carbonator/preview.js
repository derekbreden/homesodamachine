// The reference viewer loads opaque module shapes and requests child displays only on expansion.
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';

export async function createPreview(host, config, load) {
  const renderer = new THREE.WebGLRenderer({antialias:true, powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.setClearColor('#292e37');
  renderer.localClippingEnabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  host.append(renderer.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight('#e6efff','#465469',3));
  for(const [position,intensity] of [[[250,-300,400],5],[[-220,-100,120],3],[[100,220,300],4]]){
    const light=new THREE.DirectionalLight('#ffffff',intensity); light.position.set(...position); scene.add(light);
  }
  const camera = new THREE.PerspectiveCamera(35,1,.1,10000);
  camera.up.set(0,0,1);
  const controls = new OrbitControls(camera,renderer.domElement);
  controls.enableDamping = false;
  const clipping = new THREE.Plane(new THREE.Vector3(0,1,0),0);
  const material = new THREE.MeshStandardMaterial({color:config.color,metalness:.35,roughness:.38,side:THREE.DoubleSide,clippingPlanes:[]});
  const root=new THREE.Group(); scene.add(root);
  let count=1, expanded=false, exploded=false, childManifest, childGeometries;
  let drawQueued=false, visible=true;
  let firstDraw;
  const ready=new Promise(resolve=>firstDraw=resolve);
  const render=()=>{drawQueued=false;if(visible && !document.hidden){renderer.render(scene,camera);firstDraw?.();firstDraw=null;}};
  const invalidate=()=>{if(!drawQueued){drawQueued=true;requestAnimationFrame(render);}};
  controls.addEventListener('change',invalidate);
  const loader=new GLTFLoader();
  const geometry=async(url,label)=>{
    const bytes=await load(url,'display',label);
    const gltf=await loader.parseAsync(bytes,location.origin+'/');
    gltf.scene.updateMatrixWorld(true);
    let geometry;
    gltf.scene.traverse(node=>{if(node.isMesh){geometry=node.geometry.clone().applyMatrix4(node.matrixWorld);node.material?.dispose?.();}});
    if(!geometry)throw new Error('The saved shape contains no display surface.');
    return geometry;
  };
  const moduleGeometry=await geometry(config.preview,'Carbonator saved shape');
  function positions(){
    const columns=Math.ceil(Math.sqrt(count));
    return Array.from({length:count},(_,i)=>[i%columns*config.pitch,Math.floor(i/columns)*config.pitch,0]);
  }
  function rebuild(){
    material.color.set(expanded?'#b4bbc5':config.color);
    for(const child of [...root.children]){root.remove(child);if(child.isInstancedMesh)child.dispose();}
    if(!expanded){
      const instances=new THREE.InstancedMesh(moduleGeometry,material,count);
      positions().forEach((position,i)=>instances.setMatrixAt(i,new THREE.Matrix4().makeTranslation(...position)));
      instances.instanceMatrix.needsUpdate=true;root.add(instances);
    }else{
      for(const occurrence of childManifest.occurrences){
        const mesh=new THREE.Mesh(childGeometries[occurrence.part],material);
        const matrix=new THREE.Matrix4().fromArray(occurrence.transform.flat());
        if(exploded)matrix.premultiply(new THREE.Matrix4().makeTranslation(...occurrence.explode));
        mesh.applyMatrix4(matrix);root.add(mesh);
      }
    }
    invalidate();
  }
  function fit(){
    const bounds=new THREE.Box3().setFromObject(root);
    const center=bounds.getCenter(new THREE.Vector3());
    const size=bounds.getSize(new THREE.Vector3());
    const radius=size.length()/2;
    const distance=radius/Math.sin(THREE.MathUtils.degToRad(camera.fov/2))/Math.min(camera.aspect,1)*1.12;
    camera.position.copy(center).add(new THREE.Vector3(1.1,-1.6,.85).normalize().multiplyScalar(distance));
    camera.near=Math.max(.01,distance-radius*1.5);camera.far=distance+radius*5;camera.updateProjectionMatrix();
    controls.target.copy(center);controls.update();invalidate();
  }
  const resize=new ResizeObserver(()=>{
    const {width,height}=host.getBoundingClientRect();
    if(!width||!height)return;
    renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();invalidate();
  });resize.observe(host);
  const {width,height}=host.getBoundingClientRect();renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();
  rebuild();fit();
  return {
    ready,
    async expand(children){
      if(!childGeometries){
        childManifest=children;
        const values=await Promise.all(Object.entries(children.parts).map(async([key,part])=>[key,await geometry(part.preview,part.name+' saved shape')]));
        childGeometries=Object.fromEntries(values);
      }
      expanded=true;count=1;rebuild();fit();
    },
    collapse(){expanded=false;exploded=false;rebuild();fit();},
    count(value){count=value;expanded=false;exploded=false;rebuild();fit();},
    explode(value){exploded=value;rebuild();fit();},
    section(value){material.clippingPlanes=value?[clipping]:[];material.needsUpdate=true;invalidate();},
    visible(value){visible=value;if(value)invalidate();},
    fit, invalidate,
    stats(){return {calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,count,expanded,geometries:renderer.info.memory.geometries};},
    dispose(){resize.disconnect();controls.dispose();moduleGeometry.dispose();Object.values(childGeometries||{}).forEach(g=>g.dispose());material.dispose();renderer.dispose();renderer.domElement.remove();},
  };
}
