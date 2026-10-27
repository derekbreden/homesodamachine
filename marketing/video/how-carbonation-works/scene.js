/* A deterministic, shot-driven film. Geometry is in mm; the picture clock is seconds. */
(async()=>{
const T=THREE,W=1920,H=1080,FPS=30;
const V=(x,y,z=0)=>new T.Vector3(x,y,z),clamp=T.MathUtils.clamp,lerp=T.MathUtils.lerp;
const smooth=(a,b,t)=>{const p=clamp((t-a)/(b-a),0,1);return p*p*(3-2*p);};
const ease=t=>.5-.5*Math.cos(Math.PI*clamp(t,0,1));
const mod=(x,m)=>((x%m)+m)%m;
const load=async p=>{const r=await fetch(p);if(!r.ok)throw Error(p+': '+r.status);return r.json();};
const [clock,captions,outerData,coreData,coilData,faucetData]=await Promise.all([
 load('audio/timing.json'),load('audio/captions-edited.json'),load('assets/enclosure-cad.json'),load('assets/cold-core-cad.json'),load('assets/coil-path.json'),load('assets/faucet-cad.json')]);
await document.fonts.ready;
const canvas=document.getElementById('picture');
const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:true});
renderer.setSize(W,H,false);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.localClippingEnabled=true;
const scene=new T.Scene(),camera=new T.PerspectiveCamera(33,W/H,.5,6000);
const carbon=createCarbonator(T,renderer,scene);
carbon.world.visible=false;
const palette={ice:0xdce6ff,water:0x72c7ff,orange:0xff9152,copper:0xb96e42};
function mesh(geometry,material,parent){const m=new T.Mesh(geometry,material);parent.add(m);return m;}
function cad(data,anchor=V(0,64.7,-323.8)){
 const group=new T.Group();scene.add(group);const parts=[];
 for(const d of data.meshes){
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(d.positions,3));g.setAttribute('normal',new T.Float32BufferAttribute(d.normals,3));g.setIndex(d.indices);
  const col=new T.Color().fromArray(d.color||[.3,.3,.3]);
  const metal=d.group==='evaporator'||d.group==='carbonator';
  const mat=new T.MeshPhysicalMaterial({color:col,roughness:metal?.3:.47,metalness:metal?.86:.05,clearcoat:metal?.15:.25,transparent:true,opacity:1});
  const m=mesh(g,mat,group);m.rotation.x=-Math.PI/2;m.position.copy(anchor).multiplyScalar(-1);m.userData={...d,material:mat};parts.push(m);
 }
 return {group,parts};
}
const outer=cad(outerData),core=cad(coreData);
outer.group.visible=false;core.group.visible=false;
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
  else if(g==='carbonator')alpha(m,1);
  else if(g==='evaporator')alpha(m,1-smooth(17.1,19.2,t));
  else alpha(m,1-smooth(12.8,14.7,t));
 }
 const push=ease((t-14.3)/5.4),target=V(0,lerp(101,64,push),lerp(78,0,push));
 const dist=lerp(1100,342,push),az=lerp(.62,.31,push);
 setCamera(target,dist,az,lerp(.33,.26,push),260);
}
// The exact evaporator centerline is sampled from the current coil model.
const coilGroup=new T.Group();scene.add(coilGroup);coilGroup.visible=false;
const flowPoints=coilData.flowPoints||coilData.wrapPoints;
const coilCurve=new T.CatmullRomCurve3(flowPoints.map(p=>V(...p)),false,'centripetal');
const clipBack=new T.Plane(V(0,0,-1),0),clipFront=new T.Plane(V(0,0,1),0);
const copper=new T.MeshPhysicalMaterial({color:0xe69a64,metalness:.78,roughness:.25,clearcoat:.15,envMapIntensity:1.3,clippingPlanes:[clipBack]});
const copperGhost=new T.MeshPhysicalMaterial({color:0xdb8b54,metalness:.6,roughness:.23,transparent:true,opacity:.30,depthWrite:false,clippingPlanes:[clipFront]});
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
 copper.transparent=reveal<.999;copper.opacity=reveal;copperGhost.opacity=.30*reveal;
 const cold=smooth(75.0,83.0,t);carbon.wallSteel.emissive.setHex(0x2d70b5).multiplyScalar(cold*.11);
 carbon.waterSide.color.setHex(0x72c7ff);carbon.waterTop.color.setHex(0xb0e0ff);
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
const glassMat=new T.MeshPhysicalMaterial({color:0xe6f2ff,metalness:0,roughness:.06,transmission:.94,thickness:2,ior:1.49,depthWrite:false,side:T.DoubleSide});
const profile=[[0,1],[26,1],[30,2],[32,6],[GLASS_R,GLASS_H],[GLASS_R-1.3,GLASS_H],[30.4,7],[27,5],[0,5]].map(p=>new T.Vector2(...p));
const glass=mesh(new T.LatheGeometry(profile,96),glassMat,serveWorld);glass.position.copy(glassCenter);
const drinkSide=new T.MeshPhysicalMaterial({color:0xb3debd,roughness:.13,transparent:true,opacity:.40,depthWrite:false,clearcoat:1,side:T.DoubleSide});
const drink=mesh(new T.CylinderGeometry(35.4,29.5,1,80,1,true),drinkSide,serveWorld);drink.position.copy(glassCenter);
const drinkTop=mesh(new T.CircleGeometry(35.2,80),new T.MeshPhysicalMaterial({color:0xc5e9d0,roughness:.08,transmission:.52,thickness:14,ior:1.333,clearcoat:1,depthWrite:false,side:T.DoubleSide}),serveWorld);drinkTop.rotation.x=-Math.PI/2;
const bubblesInGlass=new T.InstancedMesh(new T.SphereGeometry(1,7,5),new T.MeshPhysicalMaterial({color:0xf0fbff,metalness:0,roughness:.05,transparent:true,opacity:.63,depthWrite:false}),140);serveWorld.add(bubblesInGlass);bubblesInGlass.frustumCulled=false;bubblesInGlass.renderOrder=8;
const waterExit=V(0,180.3887434,133.996722),flavorExit=V(-3.175,184.2857434,138.637722),tangent=V(0,-.76604444,.64278761);
const waterMat=new T.MeshPhysicalMaterial({color:0xbce6ff,roughness:.045,transmission:.52,thickness:2,ior:1.333,clearcoat:1,depthWrite:false});
const flavorMat=new T.MeshPhysicalMaterial({color:0xc1db7b,roughness:.06,transmission:.4,thickness:1,ior:1.333,clearcoat:1,depthWrite:false});
const jets=[{exit:waterExit,speed:900,r:1.45,material:waterMat},{exit:flavorExit,speed:750,r:.42,material:flavorMat}].map(d=>{
 const points=Array.from({length:72},(_,i)=>V(0,-i,0)),curve=new T.CatmullRomCurve3(points);
 return {...d,mesh:mesh(new T.TubeGeometry(curve,71,d.r,10,false),d.material,serveWorld)};
});
const dropSplash=new T.InstancedMesh(new T.SphereGeometry(.5,7,5),waterMat,40);serveWorld.add(dropSplash);dropSplash.frustumCulled=false;dropSplash.renderOrder=8;
const counter=mesh(new T.CylinderGeometry(330,330,6,96),new T.MeshStandardMaterial({color:0x10223d,roughness:.30,metalness:.2}),serveWorld);counter.position.set(0,-3,85);
const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=128;
const shadowContext=shadowCanvas.getContext('2d'),shadowGradient=shadowContext.createRadialGradient(64,64,2,64,64,63);
shadowGradient.addColorStop(0,'rgba(0,0,0,.72)');shadowGradient.addColorStop(.45,'rgba(0,0,0,.38)');shadowGradient.addColorStop(1,'rgba(0,0,0,0)');shadowContext.fillStyle=shadowGradient;shadowContext.fillRect(0,0,128,128);
const shadowTexture=new T.CanvasTexture(shadowCanvas);
for(const [z,size]of [[0,88],[196,92]]){const shadow=mesh(new T.PlaneGeometry(size,size),new T.MeshBasicMaterial({map:shadowTexture,transparent:true,depthWrite:false}),serveWorld);shadow.rotation.x=-Math.PI/2;shadow.position.set(0,.08,z);}
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
 if(n.includes('shell')||n.includes('body')||n.includes('cover')){m.material.color.setHex(0x18232c);m.material.roughness=.27;m.material.metalness=.18;}
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
 drink.scale.y=fill-5;drink.position.set(glassCenter.x,glassCenter.y+(fill+5)/2,glassCenter.z);
 drinkTop.position.set(glassCenter.x,glassCenter.y+fill,glassCenter.z);
 const wobble=pouring?.4:.08;drinkTop.rotation.x=-Math.PI/2+Math.sin(t*9)*wobble*.025;
 for(let i=0;i<140;i++){
  const a=i*2.39996,r=Math.sqrt((i*.754877)%1)*30,u=mod(t*(.20+(i%5)*.025)+i*.61803,1);
  inst(bubblesInGlass,i,V(Math.cos(a)*r,glassCenter.y+6+u*(fill-7),glassCenter.z+Math.sin(a)*r),.20+(i%7)*.07);
 }
 bubblesInGlass.instanceMatrix.needsUpdate=true;
 for(const j of jets){
  j.mesh.visible=pouring;
  if(pouring){
   const flight=(-j.speed*tangent.y-Math.sqrt(Math.pow(j.speed*tangent.y,2)+2*9810*(j.exit.y-glassCenter.y-fill)))/9810;
   const dur=Math.abs(flight),pts=Array.from({length:72},(_,i)=>{const q=dur*i/71;return j.exit.clone().addScaledVector(tangent,j.speed*q).add(V(.12*Math.sin(i*.7-t*23),-4905*q*q,0));});
   j.mesh.geometry.dispose();j.mesh.geometry=new T.TubeGeometry(new T.CatmullRomCurve3(pts),71,j.r,10,false);
  }
 }
 for(let i=0;i<40;i++){
  const age=mod(t*1.8+i*.061,.7),a=i*2.39996,rad=age*18;
  inst(dropSplash,i,V(Math.cos(a)*rad,glassCenter.y+fill+25*age-50*age*age,glassCenter.z-8+Math.sin(a)*rad),pouring?.45:0.0001);
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
function simTime(t){
 if(t<31.433333)return lerp(0,8,clamp((t-20.166667)/11.266666,0,1));
 if(t<41.5)return lerp(6,11,clamp((t-31.433333)/10.066667,0,1));
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
function annotation(text,point,x,y,accent=false){
 const p=point.clone().project(camera),px=(p.x*.5+.5)*W,py=(-p.y*.5+.5)*H;
 const side=x>px?-1:1,edge=x+side*12;
 return `<g><path d="M${edge},${y-8} L${lerp(edge,px,.55)},${y-8} L${px},${py}" ${accent?'style="stroke:#ff9152"':''}/><circle cx="${px}" cy="${py}" r="3.5"/><text x="${x}" y="${y}" text-anchor="${side<0?'start':'end'}">${text}</text></g>`;
}
let lastScene='';
window.renderFrame=async function(frame,{captionsVisible=true}={}){
 const t=frame/FPS;
 const beat=clock.scenes.find(s=>t>=s.start&&t<s.end)||clock.scenes.at(-1),id=beat.id;
 outer.group.visible=core.group.visible=carbon.world.visible=faucet.group.visible=serveWorld.visible=coilGroup.visible=false;
 let s;
 if(id==='hook')poseFaucet(t,true);
 else if(id==='reveal')poseCAD(t);
 else if(t>=87.5)poseFaucet(t,false);
 else{
  carbon.world.visible=true;const st=simTime(t),options=id==='gas'?{waterOn:0,level:carbon.LOW}:{gasOn:0,level:filmLevel(t)};
  s=carbon.tick(st,0,true,options);
  carbon.bubbles.visible=id==='gas';
  if(id==='gas'){carbon.entrained.visible=carbon.foam.visible=false;}else{carbon.entrained.visible=carbon.foam.visible=true;}
  carbon.setWallOpacity(1);carbon.setAccent(id==='level'?.8*(1-smooth(68.8,69.7,t)):0);
  carbon.wallSteel.emissive.setRGB(0,0,0);
  carbon.waterTop.color.setHex(0xb0d9f1);
  if(id==='jet'){
   const macro=smooth(33.2,35.6,t)*(1-smooth(39.6,41.5,t));
   setCamera(V(lerp(-1,-19.05,macro),lerp(64,121.2,macro),0),lerp(342,85,macro),lerp(.30,.15,macro),lerp(.25,-.08,macro),260);
  }else if(id==='mixing'||id==='dissolution'){
   const mix=smooth(42.2,45.3,t)*(1-smooth(60.5,62.5,t));
   setCamera(V(lerp(-1,-15,mix),lerp(64,s.level-12,mix),0),lerp(342,195,mix),lerp(.31,.16,mix),.21,260);
  }else if(id==='level')setCamera(V(0,76,-8),305,.34,.20,260);
  else if(id==='cooling'||id==='serve'){
   setCamera(V(0,65,0),lerp(350,333,smooth(70,83,t)),lerp(.30,.52,smooth(70,83,t)),.24,260);poseCooling(t);
  }else setCamera(V(0,64,0),342,.31,.25,260);
 }
 let card=cards[id];
 if(id==='serve'&&t>=87.5)card=['At the faucet','Two streams.\nOne glass.','Carbonated water + flavor.'];
 eyebrow.textContent=card[0];headline.textContent=card[1];detail.textContent=card[2];
 const fadeIn=smooth(beat.start,beat.start+.45,t),fadeOut=1-smooth(beat.end-.35,beat.end,t);
 type.style.opacity=String(Math.min(fadeIn,fadeOut));
 if(id==='serve'&&Math.abs(t-87.5)<.35)type.style.opacity=String(smooth(87.5,87.9,t));
 url.style.opacity=id==='close'?String(smooth(96.7,97.3,t)):0;
 let labels='';
 if(s){
  if(id==='gas')labels=annotation('CO₂ headspace',V(24,105,-8),1550,265)+annotation('CO₂ inlet',V(-45,-23,0),1535,835,true);
  if(id==='jet'&&t>35&&t<40.3)labels=annotation('Drilled jet cap',V(-15.85,122.4,0),1520,410,true);
  if(id==='mixing'&&t>45.4)labels=annotation('Entrained gas',V(-19,s.level-22,7),1610,655);
  if(id==='level')labels=annotation('Magnetic float',V(4,s.level+3,-32),1575,365,true);
  if(id==='cooling')labels=annotation('Refrigerant flow',coilCurve.getPoint(.54),1540,345)+annotation('Heat transfer',V(63,52,-12),1530,707,true);
 }
 callouts.innerHTML=labels;
 const cap=captionsVisible?captions.find(c=>t>=c.start&&t<c.end):null;
 captionEl.innerHTML=cap?'<span>'+cap.text+'</span>':'';
 const topFade=1-smooth(0,.85,t),endFade=smooth(101.0,102.033333,t);
 document.getElementById('fade').style.opacity=String(Math.max(topFade,endFade));
 renderer.render(scene,camera);
 document.body.dataset.ready='true';document.body.dataset.scene=id;
 lastScene=id;
 return {time:t,scene:id,simulation:s?{level:s.level,waterOn:s.waterOn,gasOn:s.gasOn,bubbles:s.activeFeed+s.activeEntrained}:null};
};
window.filmReady=true;
await window.renderFrame(0);
const q=new URLSearchParams(location.search);
if(q.has('t'))await window.renderFrame(Math.round(Number(q.get('t'))*FPS));
if(q.has('play')){const start=performance.now();async function run(){await window.renderFrame(Math.floor((performance.now()-start)/1000*FPS));requestAnimationFrame(run);}run();}
})();
