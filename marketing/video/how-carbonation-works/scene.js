/* A deterministic, shot-driven film. Geometry is in mm; the picture clock is seconds. */
(async()=>{
const T=THREE,W=1920,H=1080,FPS=30;
const V=(x,y,z=0)=>new T.Vector3(x,y,z),clamp=T.MathUtils.clamp,lerp=T.MathUtils.lerp;
const smooth=(a,b,t)=>{const p=clamp((t-a)/(b-a),0,1);return p*p*(3-2*p);};
const smoother=(a,b,t)=>{const p=clamp((t-a)/(b-a),0,1);return p*p*p*(10+p*(-15+6*p));};
const ease=t=>.5-.5*Math.cos(Math.PI*clamp(t,0,1));
const mod=(x,m)=>((x%m)+m)%m;
const load=async p=>{const r=await fetch(p);if(!r.ok)throw Error(p+': '+r.status);return r.json();};
const [clock,captions,outerData,coreData,coilData,faucetData,hardwareData,sectionData,floatData,datums]=await Promise.all([
 load('audio/timing.json'),load('audio/captions-edited.json'),load('assets/enclosure-cad.json'),load('assets/cold-core-cad.json'),load('assets/coil-path.json'),load('assets/faucet-cad.json'),
 load('assets/carbonator-hardware-full.json'),load('assets/carbonator-hardware-section.json'),load('assets/magnetic-float-cad.json'),load('assets/carbonator-datums.json')]);
await document.fonts.ready;
const canvas=document.getElementById('picture');
const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:true});
renderer.setSize(W,H,false);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=.94;renderer.localClippingEnabled=true;
const scene=new T.Scene(),camera=new T.PerspectiveCamera(33,W/H,.5,6000);
// The backdrop is inside WebGL, so transmission and reflections see the studio.
const backdrop=document.createElement('canvas');backdrop.width=1024;backdrop.height=8;
const bg=backdrop.getContext('2d'),gradient=bg.createLinearGradient(0,0,1024,0);
gradient.addColorStop(0,'#eaf6ff');gradient.addColorStop(.46,'#eaf6ff');gradient.addColorStop(.68,'#c8e5fa');gradient.addColorStop(.86,'#87b6ec');gradient.addColorStop(1,'#2d63d5');
bg.fillStyle=gradient;bg.fillRect(0,0,1024,8);
const backdropTexture=new T.CanvasTexture(backdrop);backdropTexture.colorSpace=T.SRGBColorSpace;scene.background=backdropTexture;
const carbon=createCarbonator(T,renderer,scene,datums);
carbon.world.visible=false;
const palette={ice:0xdce6ff,water:0x72c7ff,orange:0xff9152,copper:0xb96e42};
function mesh(geometry,material,parent){const m=new T.Mesh(geometry,material);parent.add(m);return m;}
function cad(data,anchor=V(0,64.7,-323.8),local=false){
 const group=new T.Group();scene.add(group);const parts=[];
 for(const d of data.meshes){
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(d.positions,3));g.setAttribute('normal',new T.Float32BufferAttribute(d.normals,3));g.setIndex(d.indices);
  const col=new T.Color().fromArray(d.color||[.3,.3,.3]);
  const metal=d.group==='evaporator'||d.group==='carbonator'||['pressure-shell','endcap','port','float-guide','jet-cap'].includes(d.role)||d.name==='prv-sv125';
  const mat=new T.MeshPhysicalMaterial({color:col,roughness:metal?.36:.60,metalness:metal?.82:.02,clearcoat:metal?.08:.02,envMapIntensity:.8});
  let material=mat;
  if(d.sectionFaceIndices?.length){
   const cut=new Set(Array.from({length:d.sectionFaceIndices.length/3},(_,i)=>d.sectionFaceIndices.slice(i*3,i*3+3).join(','))),solid=[],section=[];
   for(let i=0;i<d.indices.length;i+=3)(cut.has(d.indices.slice(i,i+3).join(','))?section:solid).push(...d.indices.slice(i,i+3));
   g.setIndex(solid.concat(section));g.clearGroups();g.addGroup(0,solid.length,0);g.addGroup(solid.length,section.length,1);
   material=[mat,new T.MeshStandardMaterial({color:0x9caab7,roughness:.82,metalness:.18})];
  }
  if(d.role==='float-body'){mat.color.setHex(0xd8d6cf);mat.roughness=.78;mat.metalness=0;}
  if(d.role==='float-magnet'){mat.color.setHex(0x737d88);mat.roughness=.35;mat.metalness=.65;}
  const m=mesh(g,material,group);if(!local){m.rotation.x=-Math.PI/2;m.position.copy(anchor).multiplyScalar(-1);}m.userData={...d,material:mat};parts.push(m);
 }
 return {group,parts};
}
const outer=cad(outerData),core=cad(coreData);
outer.group.visible=false;core.group.visible=false;
// Compile the reveal parts with opacity support before their first appearance.
// Changing only transparent after compilation can leave Three's OPAQUE shader cached.
for(const m of [...outer.parts,...core.parts])m.material.transparent=true;
const fullHardware=cad(hardwareData,V(),true),sectionHardware=cad(sectionData,V(),true),floatCAD=cad(floatData,V(),true);
fullHardware.group.visible=sectionHardware.group.visible=floatCAD.group.visible=false;
const cutPlane=new T.Plane(V(0,0,-1),100);
for(const m of fullHardware.parts)m.material.clippingPlanes=[cutPlane];
// The identical assembly is clipped open; the closed solid section supplies cut faces.
function poseHardware(t){
 const cut=smoother(16.8,20.0,t);cutPlane.constant=lerp(110,0,cut);
 fullHardware.group.visible=t<20.0;sectionHardware.group.visible=t>=20.0;
 floatCAD.group.visible=true;floatCAD.group.position.set(0,filmLevel(t)-8.766,-41.849);
}
function alpha(m,a){m.visible=a>.002;m.material.opacity=a;m.material.depthWrite=a>.995;}
const anchor=V(0,64.7,-323.8);
function poseCAD(t){
 const u=t-9.833333,open=smooth(10.6,12.9,t),strip=smooth(12.3,14.6,t);
 outer.group.visible=true;core.group.visible=true;
 for(const m of outer.parts){m.position.copy(anchor).multiplyScalar(-1);const n=m.userData.name,g=m.userData.group;
  if(n==='enclosure-front-top'){m.position.z+=open*210;m.position.y+=open*150;m.position.x-=open*82;}
  else if(n==='enclosure-front-bottom'){m.position.z+=open*150;m.position.y-=open*60;m.position.x-=open*90;}
  else if(n==='enclosure-back-top'){m.position.z-=open*175;m.position.y+=open*160;m.position.x+=open*100;}
  else if(n==='enclosure-back-bottom'){m.position.z-=open*175;m.position.y-=open*70;m.position.x+=open*100;}
  alpha(m,1-smooth(12.3,14.4,t));
 }
 for(const m of core.parts){m.position.copy(anchor).multiplyScalar(-1);const g=m.userData.group;
  if(g==='insulation'){
   m.position.y+=strip*(m.userData.name.includes('cap')||m.userData.name.includes('lid')?150:10);
   m.position.x+=strip*(m.userData.name.includes('left')?-130:130);
   alpha(m,1-smooth(12.6,14.6,t));
  }else if(g==='flavor-reservoirs'){m.position.x+=strip*(m.userData.name.includes('left')?-160:160);alpha(m,1-smooth(12.8,14.7,t));}
  else if(g==='carbonator')m.visible=false;
  else if(g==='evaporator')alpha(m,1-smooth(17.1,19.2,t));
  else alpha(m,1-smooth(12.8,14.7,t));
 }
 poseHardware(t);
}
// The exact evaporator centerline is sampled from the current coil model.
const coilGroup=new T.Group();scene.add(coilGroup);coilGroup.visible=false;
const flowPoints=coilData.flowPoints||coilData.wrapPoints;
const coilCurve=new T.CatmullRomCurve3(flowPoints.map(p=>V(...p)),false,'centripetal');
const clipBack=new T.Plane(V(0,0,-1),0),clipFront=new T.Plane(V(0,0,1),0);
const copper=new T.MeshPhysicalMaterial({color:0xe69a64,metalness:.78,roughness:.25,clearcoat:.15,envMapIntensity:1.3,clippingPlanes:[clipBack]});
const copperGhost=new T.MeshPhysicalMaterial({color:0xcb814b,metalness:.70,roughness:.26,transparent:true,opacity:.57,depthWrite:false,clippingPlanes:[clipFront]});
const coilGeo=new T.TubeGeometry(coilCurve,1800,coilData.tubeRadius,10,false);
mesh(coilGeo,copper,coilGroup);mesh(coilGeo,copperGhost,coilGroup);
const coolant=new T.MeshBasicMaterial({color:0xb1e6ff,transparent:true,opacity:.78,depthWrite:false});
const flowPulse=new T.InstancedMesh(new T.SphereGeometry(1,8,6),coolant,82);coilGroup.add(flowPulse);flowPulse.frustumCulled=false;flowPulse.renderOrder=9;
const heatMat=new T.MeshBasicMaterial({color:palette.orange,transparent:true,opacity:.8,depthWrite:false});
const heat=new T.InstancedMesh(new T.SphereGeometry(.75,7,5),heatMat,84);coilGroup.add(heat);heat.frustumCulled=false;heat.renderOrder=9;
const heatTargets=coilData.wrapPoints.filter(p=>p[1]>12&&p[1]<76&&p[0]>40&&p[2]<0).map(p=>V(...p));
const dummy=new T.Object3D();
function inst(object,i,p,scale=1){dummy.position.copy(p);dummy.scale.setScalar(scale);dummy.updateMatrix();object.setMatrixAt(i,dummy.matrix);}
function poseCooling(t){
 const reveal=smooth(70.3,73.1,t);coilGroup.visible=reveal>.001;
 copper.transparent=reveal<.999;copper.opacity=reveal;copperGhost.opacity=.57*reveal;
 const cold=smooth(75.0,83.0,t);
 carbon.waterSide.color.setHex(0x7bbce3).lerp(new T.Color(0x599ed5),cold*.25);carbon.waterTop.color.setHex(0xb8e0f2);
 const thermal=smooth(74.7,76.0,t)*(1-smooth(81.5,83.0,t));
 for(let i=0;i<84;i++){
  const u=mod(t*.63+i*.61803,1),target=heatTargets[(i*19)%heatTargets.length];
  // Warm tracers cross the water and bonded wall into the copper contact.
  const r=lerp(.34,1,u),p=V(target.x*r,target.y,target.z*r);
  inst(heat,i,p,thermal*(.7+Math.sin(Math.PI*u)*.6));
 }
 heat.instanceMatrix.needsUpdate=true;heatMat.opacity=.8*thermal;
 for(let i=0;i<82;i++){
  const u=mod(t*.043+i/82,1),p=coilCurve.getPoint(u);
  inst(flowPulse,i,p,reveal*(.5+u*.6));
 }
 flowPulse.instanceMatrix.needsUpdate=true;
}
// The faucet and its display are current CAD, with the outlet datums supplied by it.
const faucet=cad(faucetData,V(0,0,0));faucet.group.visible=false;
const serveWorld=new T.Group();scene.add(serveWorld);serveWorld.visible=false;
const glassCenter=V(0,.4,196),GLASS_H=86.45,GLASS_R=38.15;
// Each profile edge owns its normals. A horizontal lip cannot shade the tall wall.
function profiledGlass(profile,segments=144){
 const pos=[],norm=[],index=[];
 for(let e=0;e<profile.length-1;e++){
  const [r0,y0]=profile[e],[r1,y1]=profile[e+1],dr=r1-r0,dy=y1-y0,len=Math.hypot(dr,dy),base=pos.length/3;
  for(const [r,y]of [[r0,y0],[r1,y1]])for(let i=0;i<=segments;i++){
   const a=i/segments*Math.PI*2,c=Math.cos(a),s=Math.sin(a);pos.push(r*c,y,r*s);norm.push(dy/len*c,-dr/len,dy/len*s);
  }
  for(let i=0;i<segments;i++){const a=base+i,b=a+segments+1;index.push(a,b,b+1,a,b+1,a+1);}
 }
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setAttribute('normal',new T.Float32BufferAttribute(norm,3));g.setIndex(index);return g;
}
const glassMat=new T.MeshPhysicalMaterial({color:0xa9c4d8,metalness:.04,roughness:.055,transparent:true,opacity:1,ior:1.47,clearcoat:.8,depthWrite:false,side:T.DoubleSide});
glassMat.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>','diffuseColor.a *= .018 + .62 * pow(1.0-abs(dot(normal,normalize(vViewPosition))),2.8);\n#include <opaque_fragment>');};
const profile=[[0,0],[27.8,0],[30.8,1.6],[31.2,4.5],[38.15,85.7],[38.12,86.2],[37.9,86.45],[37.5,86.5],[37.2,86.3],[36.95,85.8],[30.15,6],[28.8,5.2],[0,5.2]];
const glass=mesh(profiledGlass(profile),glassMat,serveWorld);glass.position.copy(glassCenter);glass.renderOrder=10;
const glassEdge=new T.MeshBasicMaterial({color:0x66839f,transparent:true,opacity:.42,depthWrite:false});
for(const [r,y,tube]of [[37.65,86.3,.21],[30.55,1.7,.25]]){const edge=mesh(new T.TorusGeometry(r,tube,8,144),glassEdge,serveWorld);edge.rotation.x=Math.PI/2;edge.position.copy(glassCenter).add(V(0,y,0));edge.renderOrder=11;}
const coldBeads=new T.InstancedMesh(new T.SphereGeometry(1,9,7),new T.MeshPhysicalMaterial({color:0xe9f8ff,roughness:.06,metalness:.1,transparent:true,opacity:.56,clearcoat:1,depthWrite:false}),130);serveWorld.add(coldBeads);coldBeads.frustumCulled=false;coldBeads.renderOrder=11;
for(let i=0;i<130;i++){const a=i*2.399963,y=8+((i*.754877666)%1)*65,r=31.2+(38.15-31.2)*(y-4.5)/(85.7-4.5);inst(coldBeads,i,glassCenter.clone().add(V(Math.cos(a)*r,y,Math.sin(a)*r)),.20+Math.pow((i*.61803)%1,2)*.47);}coldBeads.instanceMatrix.needsUpdate=true;
const innerGlassRadius=y=>30.15+(36.95-30.15)*clamp((y-6)/(85.8-6),0,1);
const drinkSide=new T.MeshPhysicalMaterial({color:0xafcb5b,roughness:.12,transparent:true,opacity:.43,depthWrite:false,clearcoat:.3,side:T.DoubleSide});
const drink=mesh(new T.CylinderGeometry(1,1,1,96,1,true),drinkSide,serveWorld);drink.position.copy(glassCenter);drink.renderOrder=4;
const drinkTop=mesh(new T.CircleGeometry(1,96),new T.MeshPhysicalMaterial({color:0xdaeab0,roughness:.10,transparent:true,opacity:.36,ior:1.333,clearcoat:.4,depthWrite:false,side:T.DoubleSide}),serveWorld);drinkTop.rotation.x=-Math.PI/2;drinkTop.renderOrder=7;
const bubblesInGlass=new T.InstancedMesh(new T.SphereGeometry(1,10,7),carbon.bubbles.material.clone(),240);serveWorld.add(bubblesInGlass);bubblesInGlass.frustumCulled=false;bubblesInGlass.renderOrder=8;
const waterExit=V(0,180.3887434,133.996722),flavorExit=V(-3.175,184.2857434,138.637722),tangent=V(0,-.76604444,.64278761);
const waterMat=new T.MeshPhysicalMaterial({color:0xbce6ff,roughness:.045,transmission:.52,thickness:2,ior:1.333,clearcoat:1,depthWrite:false});
const flavorMat=new T.MeshPhysicalMaterial({color:0xc1db7b,roughness:.06,transmission:.4,thickness:1,ior:1.333,clearcoat:1,depthWrite:false});
const jets=[{exit:waterExit,speed:900,r:1.45,material:waterMat},{exit:flavorExit,speed:750,r:.42,material:flavorMat}].map(d=>{
 const points=Array.from({length:72},(_,i)=>V(0,-i,0)),curve=new T.CatmullRomCurve3(points);
 return {...d,mesh:mesh(new T.TubeGeometry(curve,71,d.r,10,false),d.material,serveWorld)};
});
const dropSplash=new T.InstancedMesh(new T.SphereGeometry(.5,7,5),waterMat,40);serveWorld.add(dropSplash);dropSplash.frustumCulled=false;dropSplash.renderOrder=8;
const counterMaterial=new T.ShaderMaterial({uniforms:{studio:{value:backdropTexture}},vertexShader:'void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform sampler2D studio;void main(){gl_FragColor=texture2D(studio,vec2(gl_FragCoord.x/1920.0,.5));\n#include <colorspace_fragment>\n}'});
const counter=mesh(new T.PlaneGeometry(3000,3000),counterMaterial,serveWorld);counter.rotation.x=-Math.PI/2;counter.position.y=0;
const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=128;
const shadowContext=shadowCanvas.getContext('2d'),shadowGradient=shadowContext.createRadialGradient(64,64,2,64,64,63);
shadowGradient.addColorStop(0,'rgba(39,63,86,.50)');shadowGradient.addColorStop(.45,'rgba(39,63,86,.30)');shadowGradient.addColorStop(.7,'rgba(39,63,86,.14)');shadowGradient.addColorStop(1,'rgba(39,63,86,0)');shadowContext.fillStyle=shadowGradient;shadowContext.fillRect(0,0,128,128);
const shadowTexture=new T.CanvasTexture(shadowCanvas);
for(const [z,size]of [[0,138],[196,126]]){const shadow=mesh(new T.PlaneGeometry(size,size*.83),new T.MeshBasicMaterial({map:shadowTexture,transparent:true,depthWrite:false,toneMapped:false}),serveWorld);shadow.rotation.x=-Math.PI/2;shadow.position.set(3,.12,z-3);}
const glassContact=mesh(new T.RingGeometry(27.1,30.4,96),new T.MeshBasicMaterial({color:0x59768e,transparent:true,opacity:.20,depthWrite:false,toneMapped:false}),serveWorld);glassContact.rotation.x=-Math.PI/2;glassContact.position.set(0,.15,196);
const displayTexture=await new T.TextureLoader().loadAsync('assets/faucet-display-flavor1.png');displayTexture.colorSpace=T.SRGBColorSpace;
for(const m of faucet.parts){
 const n=m.userData.name.toLowerCase();
 if(n==='faucet_display_screen'){
  const p=m.geometry.attributes.position,uv=[];
  for(let i=0;i<p.count;i++)uv.push((p.getX(i)+8.875)/17.75,(p.getZ(i)-200.580)/25.483);
  m.geometry.setAttribute('uv',new T.Float32BufferAttribute(uv,2));
  m.material=new T.MeshBasicMaterial({map:displayTexture,color:0xffffff});continue;
 }
 if(n.includes('display')||n.includes('lcd')){m.material.color.setHex(0x253b32);}
 if(n.includes('shell')||n.includes('body')||n.includes('cover')){m.material.color.setHex(0x17212d);m.material.roughness=.62;m.material.metalness=.01;m.material.clearcoat=0;}
}
function poseFaucet(t,opening=false){
 faucet.group.visible=true;serveWorld.visible=true;
 const pouring=!opening&&t>=87.5&&t<=95.3;
 for(const m of faucet.parts)if(m.userData.name==='lever'){
  const turn=.23*smooth(87.3,87.5,t)*(1-smooth(95.3,95.55,t));
  m.rotation.x=-Math.PI/2-turn;
  m.position.set(0,46-46*Math.cos(turn),46*Math.sin(turn));
 }
 const fill=opening?68:lerp(40,68,smooth(87.5,95.3,t));
 drink.geometry.dispose();drink.geometry=new T.CylinderGeometry(innerGlassRadius(fill)-.15,29.9,fill-5.5,96,1,true);drink.position.set(glassCenter.x,glassCenter.y+(fill+5.5)/2,glassCenter.z);
 drinkTop.position.set(glassCenter.x,glassCenter.y+fill,glassCenter.z);drinkTop.scale.setScalar(innerGlassRadius(fill)-.17);
 const wobble=pouring?.4:.08;drinkTop.rotation.x=-Math.PI/2+Math.sin(t*9)*wobble*.025;
 for(let i=0;i<240;i++){
  const a=i*2.39996,r=Math.sqrt((i*.754877)%1)*30,u=mod(t*(.20+(i%5)*.025)+i*.61803,1);
  inst(bubblesInGlass,i,V(Math.cos(a)*r,glassCenter.y+6+u*(fill-7),glassCenter.z+Math.sin(a)*r),.14+(i%7)*.045);
 }
 bubblesInGlass.instanceMatrix.needsUpdate=true;
 for(const j of jets){
  j.mesh.visible=false;
  if(!opening&&t>=87.5&&t<=95.55){
   const flight=(-j.speed*tangent.y-Math.sqrt(Math.pow(j.speed*tangent.y,2)+2*9810*(j.exit.y-glassCenter.y-fill)))/9810;
   const dur=Math.abs(flight),tail=Math.max(0,t-95.3),front=Math.min(dur,t-87.5);
   if(front>tail+.0001){
    const pts=Array.from({length:72},(_,i)=>{const q=lerp(tail,front,i/71);return j.exit.clone().addScaledVector(tangent,j.speed*q).add(V(.10*Math.sin(i*.7-t*23),-4905*q*q,0));});
    j.mesh.visible=true;j.mesh.geometry.dispose();j.mesh.geometry=new T.TubeGeometry(new T.CatmullRomCurve3(pts),71,j.r,10,false);
   }
  }
 }
 for(let i=0;i<40;i++){
  const age=mod(t*1.8+i*.061,.7),born=t-age/1.8,a=i*2.39996,rad=age*18,active=!opening&&born>=87.62&&born<=95.42;
  inst(dropSplash,i,V(Math.cos(a)*rad,glassCenter.y+fill+25*age-50*age*age,glassCenter.z-8+Math.sin(a)*rad),active?.45:0.0001);
 }
 dropSplash.instanceMatrix.needsUpdate=true;
 const u=opening?t/9.833333:(t-87.5)/14.533333;
 const az=opening?lerp(.48,.42,ease(u)):.42;
 setCamera(V(0,96,110),opening?585:lerp(585,570,ease(u)),az,.15,245);
}
function setCamera(target,dist,az,elevation,offset=260){
 camera.position.set(target.x+Math.sin(az)*dist,target.y+Math.sin(elevation)*dist,target.z+Math.cos(az)*Math.cos(elevation)*dist);
 camera.lookAt(target);camera.setViewOffset(W,H,-offset,0,W,H);camera.updateProjectionMatrix();camera.updateMatrixWorld();
}
// Camera time is independent of the editorial cards. Every mechanism shot is
// one track, including the nozzle-to-impact move and the refill-to-coil reveal.
const cameraTrack=[
 {t:14.3,p:[0,101,78],d:1100,a:.62,e:.33},
 {t:21.3,p:[0,64,0],d:350,a:.28,e:.21},
 {t:32.2,p:[0,64,0],d:350,a:.28,e:.21},
 {t:35.7,p:[19.05,124.5,0],d:92,a:.10,e:-.055},
 {t:39.3,p:[19.05,124.5,0],d:92,a:.10,e:-.055},
 {t:45.3,p:[15,51,0],d:218,a:.14,e:.20},
 {t:58.7,p:[15,61,0],d:218,a:.14,e:.20},
 {t:64.0,p:[0,71,-8],d:335,a:.25,e:.20},
 {t:68.7,p:[0,71,-8],d:335,a:.25,e:.20},
 {t:73.6,p:[0,65,0],d:365,a:.35,e:.23},
 {t:85.8,p:[0,65,0],d:350,a:.48,e:.23}
];
function carbonCamera(t){
 let a=cameraTrack[0],b=a;
 for(let i=1;i<cameraTrack.length;i++){b=cameraTrack[i];if(t<=b.t)break;a=b;}
 const u=a===b?0:smoother(a.t,b.t,t);
 setCamera(V(...a.p).lerp(V(...b.p),u),lerp(a.d,b.d,u),lerp(a.a,b.a,u),lerp(a.e,b.e,u),260);
}
function simTime(t){
 if(t<31.433333)return lerp(0,8,clamp((t-20.166667)/11.266666,0,1));
 if(t<41.5)return lerp(8,11,clamp((t-31.433333)/10.066667,0,1));
 if(t<55.333333)return lerp(11,23,clamp((t-41.5)/13.833333,0,1));
 if(t<62.5)return lerp(23,26,clamp((t-55.333333)/7.166667,0,1));
 if(t<67.8)return lerp(26,28,clamp((t-62.5)/5.3,0,1));
 return Math.min(36,28+(t-67.8)*1.5);
}
function filmLevel(t){
 if(t<31.433333)return carbon.LOW;
 if(t<41.5)return lerp(carbon.LOW,56,clamp((t-31.433333)/10.066667,0,1));
 if(t<55.333333)return lerp(56,68,clamp((t-41.5)/13.833333,0,1));
 if(t<62.5)return lerp(68,72.5,clamp((t-55.333333)/7.166667,0,1));
 return lerp(72.5,carbon.HIGH,smooth(62.5,67.8,t));
}
const type=document.getElementById('type'),eyebrow=document.getElementById('eyebrow'),headline=document.getElementById('headline'),detail=document.getElementById('detail'),url=document.getElementById('url'),captionEl=document.getElementById('captions'),callouts=document.getElementById('callouts');
const cards={
 hook:['A look inside','How\ncarbonation\nworks.','Pressure. Mixing. Cold.'],
 reveal:['Under the counter','The cold\ncore.','Water, gas and refrigeration.'],
 gas:['01 / Pressure','CO₂ enters\nfrom below.','Bubbles rise.\nGas collects above the water.'],
 jet:['02 / The inlet','A tiny jet.','1/16 in\n1.59 mm bore'],
 mixing:['03 / Mixing','Water plunges.\nGas follows.','A jet drives contact\nand circulation.'],
 dissolution:['The result','Dissolved\ncarbon dioxide.','This is carbonation.'],
 level:['Automatic refill','Refill.\nThen stop.','Magnetic float.\nExternal level sensing.'],
 cooling:['04 / Cold','Heat into the\nrefrigerant.','Copper evaporator\nwrapped around stainless steel.'],
 serve:['Together','Pressure.\nMixing.\nCooling.','Chilled carbonated water,\nready for the faucet.'],
 close:['Home Soda Machine','Cold soda,\non tap.','Follow the build.']
};
function annotation(text,point,x,y,accent=false,opacity=1){
 const p=point.clone().project(camera),px=(p.x*.5+.5)*W,py=(-p.y*.5+.5)*H;
 const side=x>px?-1:1,edge=x+side*12;
 const width=text.length*14.9+20,labelX=side<0?x-10:x-width+10;
 return `<g opacity="${opacity}"><path d="M${edge},${y-8} L${lerp(edge,px,.55)},${y-8} L${px},${py}" ${accent?'style="stroke:#dc753d"':''}/><circle cx="${px}" cy="${py}" r="3.5"/><rect x="${labelX}" y="${y-27}" width="${width}" height="36" rx="4" fill="#eaf6ff" fill-opacity=".94"/><text x="${x}" y="${y}" text-anchor="${side<0?'start':'end'}">${text}</text></g>`;
}
const transitionCanvas=document.getElementById('transition'),transitionContext=transitionCanvas.getContext('2d');
const pictureBuffer=document.createElement('canvas');pictureBuffer.width=W;pictureBuffer.height=H;const bufferContext=pictureBuffer.getContext('2d');
function poseWorld(t,mode,id){
 outer.group.visible=core.group.visible=carbon.world.visible=faucet.group.visible=serveWorld.visible=coilGroup.visible=fullHardware.group.visible=sectionHardware.group.visible=floatCAD.group.visible=false;
 if(mode==='faucet'){poseFaucet(t,t<20);return null;}
 carbonCamera(t);
 if(mode==='reveal')poseCAD(t);else poseHardware(t);
 carbon.world.visible=true;
 const st=simTime(t),s=carbon.tick(st,0,true,{waterOn:smooth(31.7,32.2,t)*(1-smooth(67.5,67.8,t)),gasOn:1-smooth(27.9,30.2,t),level:filmLevel(t)});
 carbon.entrained.visible=carbon.foam.visible=true;carbon.bubbles.visible=true;
 carbon.waterSide.color.setHex(0x7bbce3);carbon.waterTop.color.setHex(0xb8def0);
 if(t>=69.766667)poseCooling(t);
 for(const m of floatCAD.parts)if(m.userData.role==='float-body'){const accent=smooth(62.6,64,t)*(1-smooth(68.5,69.7,t));m.material.emissive.setRGB(.09*accent,.025*accent,0);}
 return mode==='reveal'?null:s;
}
function drawView(t,mode,id){const s=poseWorld(t,mode,id);renderer.render(scene,camera);return s;}
window.renderFrame=async function(frame,{captionsVisible=true}={}){
 const t=frame/FPS;
 const beat=clock.scenes.find(s=>t>=s.start&&t<s.end)||clock.scenes.at(-1),id=beat.id;
 const mode=t<9.833333?'faucet':t<20.166667?'reveal':t<87.5?'carbon':'faucet';
 const transition=[{start:9.433333,end:10.233333,from:'faucet',to:'reveal'},{start:86.9,end:88.1,from:'carbon',to:'faucet'}].find(q=>t>=q.start&&t<=q.end);
 let s;
 if(transition){
  drawView(t,transition.from,id);bufferContext.clearRect(0,0,W,H);bufferContext.drawImage(canvas,0,0);
  s=drawView(t,transition.to,id);
  transitionCanvas.style.display='block';transitionContext.clearRect(0,0,W,H);transitionContext.globalAlpha=1-smoother(transition.start,transition.end,t);transitionContext.drawImage(pictureBuffer,0,0);transitionContext.globalAlpha=1;
 }else{transitionCanvas.style.display='none';s=drawView(t,mode,id);}
 let card=cards[id];
 if(id==='serve'&&t>=87.5)card=['At the faucet','Two streams.\nOne glass.','Carbonated water + flavor.'];
 eyebrow.textContent=card[0];headline.textContent=card[1];detail.textContent=card[2];
 const fadeIn=smooth(beat.start,beat.start+.45,t),fadeOut=1-smooth(beat.end-.35,beat.end,t);
 type.style.opacity=String(Math.min(fadeIn,fadeOut));
 if(id==='serve'&&Math.abs(t-87.5)<.35)type.style.opacity=String(smooth(87.5,87.9,t));
 url.style.opacity=id==='close'?String(smooth(96.7,97.3,t)):0;
 let labels='';
 if(s){
  if(id==='gas')labels=annotation('CO₂ headspace',V(-24,105,-8),1550,265,false,smooth(21.4,22.0,t))+annotation('CO₂ inlet',V(...datums.gasLumen[0]),1535,835,true,smooth(21.4,22.0,t));
  if(id==='jet'&&t>35&&t<40.3)labels=annotation('Drilled jet cap',V(carbon.JX+3,carbon.JY+1,0),1520,410,true,smooth(35,35.5,t)*(1-smooth(39.3,40.3,t)));
  if((id==='mixing'||id==='dissolution')&&t>45.4)labels=annotation('Entrained gas',V(carbon.JX,s.level-22,7),1610,655,false,smooth(45.4,46,t)*(1-smooth(58.7,60.2,t)));
  if(id==='level')labels=annotation('Magnetic float',V(4.5,s.level+3,-24.4),1575,365,true,smooth(63.0,63.5,t)*(1-smooth(69.0,69.7,t)));
  if(id==='cooling')labels=annotation('Refrigerant flow',coilCurve.getPoint(.54),1540,345,false,smooth(73.4,74.2,t))+annotation('Heat transfer',V(63,52,-12),1530,707,true,smooth(73.4,74.2,t));
 }
 callouts.innerHTML=labels;
 const cap=captionsVisible?captions.find(c=>t>=c.start&&t<c.end):null;
 captionEl.innerHTML=cap?'<span>'+cap.text+'</span>':'';
 const topFade=1-smooth(0,.85,t),endFade=smooth(101.0,102.033333,t);
 document.getElementById('fade').style.opacity=String(Math.max(topFade,endFade));
 document.body.dataset.ready='true';document.body.dataset.scene=id;
 return {time:t,scene:id,camera:{position:camera.position.toArray(),quaternion:camera.quaternion.toArray()},cutYUpZ:cutPlane.constant,transition:transition?{from:transition.from,to:transition.to,mix:smoother(transition.start,transition.end,t)}:null,simulation:s?{level:s.level,waterOn:s.waterOn,gasOn:s.gasOn,bubbles:s.activeFeed+s.activeEntrained}:null};
};
window.filmReady=true;
await window.renderFrame(0);
const q=new URLSearchParams(location.search);
if(q.has('t'))await window.renderFrame(Math.round(Number(q.get('t'))*FPS));
if(q.has('play')){const start=performance.now();async function run(){await window.renderFrame(Math.floor((performance.now()-start)/1000*FPS));requestAnimationFrame(run);}run();}
})();
