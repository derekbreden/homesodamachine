// Adapted from the approved carbonator-turbulence study. Units are millimetres.
// Picture time is explicit, so source frames can be rendered in any order.
window.createCarbonator = function(THREE, renderer, scene) {
  const T=THREE;
  const world=new T.Group();scene.add(world);
  const vessel=new T.Group();world.add(vessel);
  const theme={rgba(name){
    const tokens={background:'#08152f',foreground:'#dce6ff','viz-series-1':'#72c7ff','viz-series-2':'#ff9152'};
    const n=parseInt((tokens[name]||'#dce6ff').slice(1),16);
    return [(n>>16)&255,(n>>8)&255,n&255,255];
  }};
  const R = 61.849, RO = 63.5, H = 127, LOW = 54.398, HIGH = 82.55;
  const JX = -19.05, JY = 121.4, BORE = 1.5875, DURATION = 36;
  const V = (x,y,z=0) => new T.Vector3(x,y,z);
  const clamp = T.MathUtils.clamp;
  const smooth = (a,b,x) => {const v=clamp((x-a)/(b-a),0,1);return v*v*(3-2*v);};
  const lerp = T.MathUtils.lerp;
  const mod = (x,m) => ((x%m)+m)%m;
  const neutral = new T.Color();
  const palette = {};
  function resolved(name) { const p=theme.rgba(name); return new T.Color(p[0]/255,p[1]/255,p[2]/255).convertSRGBToLinear(); }
  function mix(a,b,t) {return a.clone().lerp(b,t);}
  const halfPlane = new T.Plane(V(0,0,-1),0);
  const steel = new T.MeshPhysicalMaterial({metalness:.94,roughness:.28,clearcoat:.12,side:T.DoubleSide});
  const edgeSteel = new T.MeshStandardMaterial({metalness:.80,roughness:.38,side:T.DoubleSide});
  const darkSteel = new T.MeshStandardMaterial({metalness:.85,roughness:.32,side:T.DoubleSide});
  const wallSteel = steel.clone();
  const plateSteel = steel.clone();plateSteel.clippingPlanes=[halfPlane];
  const pipeSteel = steel.clone();
  const waterSide = new T.MeshPhysicalMaterial({metalness:0,roughness:.12,transparent:true,opacity:.20,depthWrite:false,side:T.DoubleSide,clearcoat:.9,ior:1.333});
  const waterTop = new T.MeshPhysicalMaterial({metalness:0,roughness:.10,transmission:.62,thickness:12,ior:1.333,clearcoat:1,clearcoatRoughness:.075,depthWrite:false,side:T.DoubleSide});
  const jetMat = new T.MeshPhysicalMaterial({metalness:0,roughness:.075,transmission:.28,thickness:1.6,ior:1.333,clearcoat:1,depthWrite:false,side:T.DoubleSide});
  const waterLineMat = new T.MeshBasicMaterial({transparent:true,opacity:.44,depthWrite:false});
  const gasLineMat = new T.MeshBasicMaterial({transparent:true,opacity:.35,depthWrite:false});
  const floatMat = new T.MeshStandardMaterial({roughness:.72,metalness:0});
  const magnetMat = new T.MeshStandardMaterial({roughness:.3,metalness:.85});
  const materials = [steel,edgeSteel,darkSteel,wallSteel,plateSteel,pipeSteel];
  const hemi = new T.HemisphereLight(0xffffff,0xffffff,.55);scene.add(hemi);
  const key = new T.DirectionalLight(0xffffff,2.3);key.position.set(-120,220,180);scene.add(key);
  const rim = new T.DirectionalLight(0xffffff,2.2);rim.position.set(180,170,-50);scene.add(rim);
  const fill = new T.DirectionalLight(0xffffff,.6);fill.position.set(20,-40,220);scene.add(fill);
  let envTexture;
  function environment() {
    const e = new T.Scene();
    const lightHost=palette.bg.r+palette.bg.g+palette.bg.b>1.5;
    e.background = mix(palette.bg,palette.fg,lightHost?.94:.12);
    const lightColor = new T.Color(1,1,1);
    const panel = (x,y,z,w,h,intensity) => {
      const m = new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({color:lightColor.clone().multiplyScalar(intensity),side:T.DoubleSide}));
      m.position.set(x,y,z);m.lookAt(0,0,0);e.add(m);
    };
    panel(-3,2,4,1.6,8,1.8);panel(4,1,2,.8,9,1.3);panel(0,5,-2,6,2,1.6);panel(-2,-2,-4,3,7,.7);
    const gen = new T.PMREMGenerator(renderer);
    const target=gen.fromScene(e,.025,.1,100);
    if(envTexture)envTexture.dispose();
    envTexture=target.texture;scene.environment=envTexture;
    gen.dispose();e.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material)o.material.dispose();});
  }
  // The material palette follows the host theme; illumination remains neutral.
  function setPalette() {
    palette.bg=resolved('background');palette.fg=resolved('foreground');palette.water=resolved('viz-series-1');palette.gas=resolved('viz-series-2');
    const lightHost=palette.bg.r+palette.bg.g+palette.bg.b>1.5;
    neutral.copy(mix(palette.bg,palette.fg,lightHost?.76:.32));
    materials.forEach((m,i)=>{m.color.copy(mix(neutral,new T.Color(1,1,1),i===2?.06:.22));m.envMapIntensity=1.0;});
    waterSide.color.copy(mix(palette.water,new T.Color(1,1,1),.18));
    waterTop.color.copy(mix(palette.water,new T.Color(1,1,1),.40));
    jetMat.color.copy(mix(palette.water,new T.Color(1,1,1),.42));
    waterLineMat.color.copy(palette.water);gasLineMat.color.copy(palette.gas);
    floatMat.color.copy(mix(palette.bg,palette.fg,.20));magnetMat.color.copy(neutral);
    environment();
    if(typeof gasPoints!=='undefined')gasPoints.material.color.copy(palette.gas);
  }
  function mesh(geo,mat,parent=vessel) {const m=new T.Mesh(geo,mat);parent.add(m);return m;}
  function cylinder(radius,length,x,y,z,material=steel,radial=64) {const m=mesh(new T.CylinderGeometry(radius,radius,length,radial),material);m.position.set(x,y,z);return m;}
  // A solid wall section, including the thin exposed cut faces.
  function annularSection(r0,r1,y0,y1,start=Math.PI/2,arc=Math.PI,material=steel) {
    const n=96,positions=[],normals=[],indices=[];
    for(let j=0;j<4;j++)for(let i=0;i<=n;i++) {
      const a=start+arc*i/n,r=j%2===0?r1:r0,y=j<2?y0:y1;
      positions.push(r*Math.sin(a),y,r*Math.cos(a));normals.push(Math.sin(a),0,Math.cos(a));
    }
    const face=(a,b,c,d)=>indices.push(a,b,c,a,c,d);
    for(let i=0;i<n;i++) {
      face(i,i+1,2*(n+1)+i+1,2*(n+1)+i);
      face(n+1+i,3*(n+1)+i,3*(n+1)+i+1,n+1+i+1);
      face(i,n+1+i,n+1+i+1,i+1);
      face(2*(n+1)+i,2*(n+1)+i+1,3*(n+1)+i+1,3*(n+1)+i);
    }
    face(0,2*(n+1),3*(n+1),n+1);face(n,2*(n+1)+n,3*(n+1)+n,n+1+n);
    const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setIndex(indices);g.computeVertexNormals();
    return mesh(g,material);
  }
  annularSection(R,RO,-12.7,139.7,Math.PI/2,Math.PI,wallSteel);
  // Recessed flat end plates: the cut passes through both pairs of ports.
  function plate(y0) {
    const shape=new T.Shape();shape.absarc(0,0,R-.13,0,Math.PI*2,false);
    for(const x of [JX,-JX]) {const h=new T.Path();h.absarc(x,0,5.6,0,Math.PI*2,true);shape.holes.push(h);}
    const g=new T.ExtrudeGeometry(shape,{depth:6.35,bevelEnabled:false,curveSegments:72});
    g.rotateX(-Math.PI/2);g.translate(0,y0,0);mesh(g,plateSteel);
    const ranges=[[-R,JX-5.6],[JX+5.6,-JX-5.6],[-JX+5.6,R]];
    for(const [a,b]of ranges) {const m=mesh(new T.PlaneGeometry(b-a,6.35),edgeSteel);m.position.set((a+b)/2,y0+3.175,.04);}
  }
  plate(-6.35);plate(H);
  // Weld beads are small, rounded fillets in the recessed rims.
  for(const y of [-6.65,133.65]) {
    const g=new T.TorusGeometry(R-1.2,1.35,8,96,Math.PI);g.rotateX(Math.PI/2);g.rotateY(Math.PI);
    const m=mesh(g,steel);m.position.y=y;
  }
  // A half-section of a pipe preserves both the exterior and the internal bore.
  function sectionPipe(points,outer,inner,mat=pipeSteel) {
    const path=new T.CatmullRomCurve3(points,false,'centripetal');
    const n=64,k=20,pos=[],idx=[];
    for(let j=0;j<2;j++)for(let i=0;i<=n;i++){
      const t=i/n,p=path.getPoint(t),d=path.getTangent(t),nrm=V(-d.y,d.x,0).normalize(),r=j?inner:outer;
      for(let q=0;q<=k;q++){const a=Math.PI+q/k*Math.PI;pos.push(p.x+nrm.x*Math.cos(a)*r,p.y+nrm.y*Math.cos(a)*r,p.z+Math.sin(a)*r);}
    }
    const layer=(n+1)*(k+1),face=(a,b,c,d)=>idx.push(a,b,c,a,c,d);
    for(let i=0;i<n;i++)for(let q=0;q<k;q++){
      const a=i*(k+1)+q;face(a,a+k+1,a+k+2,a+1);face(layer+a,layer+a+1,layer+a+k+2,layer+a+k+1);
    }
    for(let i=0;i<n;i++)for(const q of [0,k]){const a=i*(k+1)+q;face(a,a+k+1,layer+a+k+1,layer+a);}
    for(const i of [0,n])for(let q=0;q<k;q++){const a=i*(k+1)+q;face(a,a+1,layer+a+1,layer+a);}
    const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setIndex(idx);geo.computeVertexNormals();
    return {body:mesh(geo,mat),path};
  }
  const inlet=sectionPipe([V(-75,153),V(-35,153),V(-24,150),V(JX,141),V(JX,123.4)],6.6,3.25);
  const gasPipe=sectionPipe([V(-75,-23),V(-34,-23),V(-23,-19),V(JX,-9),V(JX,3)],6.6,3.25);
  const outletPipe=sectionPipe([V(19.05,3),V(19.05,-10),V(24,-19),V(36,-23),V(75,-23)],6.6,3.25);
  const relief=sectionPipe([V(19.05,124),V(19.05,143),V(24,151),V(38,153)],6.6,3.25);
  for(const [x,y]of [[JX,137],[19.05,137],[JX,-10],[19.05,-10]]) {
    const m=cylinder(8.2,7,x,y,0,darkSteel,6);m.material=darkSteel.clone();m.material.clippingPlanes=[halfPlane];
    // Thread crests at the plate entry.
    for(let i=0;i<5;i++){const g=new T.TorusGeometry(6.6,.24,5,32,Math.PI);g.rotateX(Math.PI/2);const t=mesh(g,edgeSteel);t.position.set(x,y-3+i*1.4,0);}
  }
  const valve=mesh(new T.CylinderGeometry(9,9,26,6),edgeSteel);valve.rotation.z=Math.PI/2;valve.position.set(50,153,0);
  const pull=mesh(new T.TorusGeometry(5.1,.7,7,32),steel);pull.position.set(68,153,0);pull.rotation.y=Math.PI/2;
  // The welded cap has a true 1/16-inch axial passage, shown in section.
  annularSection(BORE/2,4.75,JY,JY+2,Math.PI/2,Math.PI,steel).position.x=JX;
  const capBead=mesh(new T.TorusGeometry(4.72,.32,6,48,Math.PI),steel);capBead.rotation.x=Math.PI/2;capBead.position.set(JX,JY+2,0);
  const guide=cylinder(1.5875,H,0,H/2,-41.849,steel,16);
  const floatGroup=new T.Group();vessel.add(floatGroup);floatGroup.position.set(0,LOW-8.766,-41.849);
  const floatShape=new T.Shape();
  floatShape.moveTo(-11,-18);floatShape.quadraticCurveTo(-14,-18,-14,-14);floatShape.lineTo(-14,14);floatShape.quadraticCurveTo(-14,18,-10,18);floatShape.lineTo(10,18);floatShape.quadraticCurveTo(14,18,14,14);floatShape.lineTo(14,-14);floatShape.quadraticCurveTo(14,-18,11,-18);floatShape.closePath();
  const floatHole=new T.Path();floatHole.absarc(0,0,2,0,Math.PI*2,true);floatShape.holes.push(floatHole);
  const floatGeo=new T.ExtrudeGeometry(floatShape,{depth:28,bevelEnabled:true,bevelSize:.6,bevelThickness:.6,bevelSegments:2,curveSegments:12});
  floatGeo.rotateX(-Math.PI/2);floatGeo.translate(0,-14,0);
  const fmesh=mesh(floatGeo,floatMat,floatGroup);fmesh.scale.set(.92,1,.88);
  const magnet=mesh(new T.CylinderGeometry(4.75,4.75,3.18,24),magnetMat,floatGroup);magnet.rotation.x=Math.PI/2;magnet.position.set(0,0,-15.4);
  // Pool boundary, with a separately deformed reflecting surface.
  const pool=mesh(new T.CylinderGeometry(R-.38,R-.38,1,112,1,true),waterSide);pool.renderOrder=3;
  const bottomWater=mesh(new T.CircleGeometry(R-.38,96),waterSide);bottomWater.rotation.x=-Math.PI/2;bottomWater.position.y=.2;bottomWater.renderOrder=3;
  const surfaceGeo=new T.CircleGeometry(R-.38,112,1); // replaced by a concentric, well-resolved grid below
  const surfacePositions=[],surfaceIndices=[],rings=34,segments=112;
  surfacePositions.push(0,0,0);
  for(let r=1;r<=rings;r++)for(let a=0;a<segments;a++) {const theta=a/segments*Math.PI*2,rad=(R-.4)*r/rings;surfacePositions.push(Math.cos(theta)*rad,0,Math.sin(theta)*rad);}
  for(let a=0;a<segments;a++)surfaceIndices.push(0,1+(a+1)%segments,1+a);
  for(let r=1;r<rings;r++)for(let a=0;a<segments;a++){const a0=1+(r-1)*segments+a,a1=1+(r-1)*segments+(a+1)%segments,b0=a0+segments,b1=a1+segments;surfaceIndices.push(a0,a1,b1,a0,b1,b0);}
  const waterGeo=new T.BufferGeometry();waterGeo.setAttribute('position',new T.Float32BufferAttribute(surfacePositions,3));waterGeo.setIndex(surfaceIndices);waterGeo.computeVertexNormals();
  const surface=mesh(waterGeo,waterTop);surface.renderOrder=4;surfaceGeo.dispose();
  const surfaceAttr=waterGeo.attributes.position;
  const meniscus=mesh(new T.TorusGeometry(R-.8,.32,6,112),waterLineMat);meniscus.rotation.x=Math.PI/2;meniscus.renderOrder=5;
  const inletWater=mesh(new T.TubeGeometry(inlet.path,64,2.7,12,false),waterLineMat);inletWater.renderOrder=6;
  const boreWater=cylinder(BORE/2,2,JX,JY+1,0,waterLineMat,20);boreWater.renderOrder=6;
  const gasIn=mesh(new T.TubeGeometry(gasPipe.path,64,2.8,12,false),gasLineMat);gasIn.renderOrder=6;
  // Free jet: a contracted coherent core, with small advecting disturbances.
  const JN=90,JR=16,jetPositions=new Float32Array((JN+1)*JR*3),jetIndices=[];
  for(let i=0;i<JN;i++)for(let j=0;j<JR;j++){const a=i*JR+j,b=i*JR+(j+1)%JR;jetIndices.push(a,b,b+JR,a,b+JR,a+JR);}
  const jetGeo=new T.BufferGeometry();jetGeo.setAttribute('position',new T.BufferAttribute(jetPositions,3));jetGeo.setIndex(jetIndices);jetGeo.computeVertexNormals();
  const jet=mesh(jetGeo,jetMat);jet.renderOrder=6;jet.frustumCulled=false;
  // The irregular lip follows the cavity around the plunging jet.
  const crownSegments=64,crownPos=new Float32Array((crownSegments+1)*2*3),crownIdx=[];
  for(let j=0;j<crownSegments;j++){const a=j*2;crownIdx.push(a,a+1,a+3,a,a+3,a+2);}
  const crownGeo=new T.BufferGeometry();crownGeo.setAttribute('position',new T.BufferAttribute(crownPos,3));crownGeo.setIndex(crownIdx);crownGeo.computeVertexNormals();
  const crown=mesh(crownGeo,jetMat);crown.renderOrder=6;crown.frustumCulled=false;
  // Dark refracting rims and reflected highlights keep bubbles legible through water.
  const bubbleMaterial=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{rimTint:{value:new T.Color()},fillTint:{value:new T.Color()},lightTint:{value:new T.Color()}},
    vertexShader:`varying vec3 vN; varying vec3 vV;
      void main(){vec4 mv=modelViewMatrix*instanceMatrix*vec4(position,1.0);
        vN=normalize(normalMatrix*mat3(instanceMatrix)*normal);vV=normalize(-mv.xyz);
        gl_Position=projectionMatrix*mv;}`,
    fragmentShader:`uniform vec3 rimTint;uniform vec3 fillTint;uniform vec3 lightTint;
      varying vec3 vN;varying vec3 vV;
      void main(){vec3 n=normalize(vN),v=normalize(vV);
        float f=1.0-abs(dot(n,v));
        float edge=pow(f,1.5);
        float spec=pow(max(dot(reflect(-normalize(vec3(-.50,.80,.90)),n),v),0.0),48.0);
        float lower=pow(max(dot(reflect(-normalize(vec3(.40,-.65,.60)),n),v),0.0),75.0);
        vec3 col=mix(fillTint,rimTint,smoothstep(.18,.85,f));
        col=mix(col,lightTint,clamp(spec*1.9+lower*.65,0.0,1.0));
        gl_FragColor=vec4(col,clamp(.045+edge*.90+spec*.85+lower*.35,0.0,.98));
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`});
  const bubbleGeo=new T.SphereGeometry(1,16,11);
  const FEED_BUBBLES=100,ENTRAINED_BUBBLES=420,FOAM_BUBBLES=110,DROPLETS=84;
  const bubbles=new T.InstancedMesh(bubbleGeo,bubbleMaterial,FEED_BUBBLES);world.add(bubbles);bubbles.renderOrder=7;bubbles.frustumCulled=false;
  const entrained=new T.InstancedMesh(bubbleGeo,bubbleMaterial,ENTRAINED_BUBBLES);world.add(entrained);entrained.renderOrder=7;entrained.frustumCulled=false;
  const foam=new T.InstancedMesh(bubbleGeo,bubbleMaterial,FOAM_BUBBLES);world.add(foam);foam.renderOrder=8;foam.frustumCulled=false;
  const droplets=new T.InstancedMesh(new T.SphereGeometry(1,8,6),jetMat,DROPLETS);world.add(droplets);droplets.renderOrder=7;droplets.frustumCulled=false;
  const dummy=new T.Object3D();
  function instance(object,i,x,y,z,size,elongation=1) {dummy.position.set(x,y,z);dummy.scale.set(size,size*elongation,size);dummy.rotation.set(0,0,0);dummy.updateMatrix();object.setMatrixAt(i,dummy.matrix);}
  // Tracers are an explanatory overlay: CO₂ itself is invisible.
  const gasCount=165,gasPos=new Float32Array(gasCount*3);
  const gasGeometry=new T.BufferGeometry();gasGeometry.setAttribute('position',new T.BufferAttribute(gasPos,3));
  const tracerCanvas=document.createElement('canvas');tracerCanvas.width=tracerCanvas.height=32;
  const tracerContext=tracerCanvas.getContext('2d');
  const tracerGradient=tracerContext.createRadialGradient(16,16,1,16,16,15);
  tracerGradient.addColorStop(0,'rgba(255,255,255,1)');tracerGradient.addColorStop(.45,'rgba(255,255,255,.7)');tracerGradient.addColorStop(1,'rgba(255,255,255,0)');
  tracerContext.fillStyle=tracerGradient;tracerContext.fillRect(0,0,32,32);
  const tracerTexture=new T.CanvasTexture(tracerCanvas);
  const gasPoints=new T.Points(gasGeometry,new T.PointsMaterial({map:tracerTexture,size:1.4,transparent:true,opacity:.30,depthWrite:false,sizeAttenuation:true}));world.add(gasPoints);gasPoints.renderOrder=5;gasPoints.frustumCulled=false;
  const circulationCount=110,circulationPos=new Float32Array(circulationCount*3);
  const circulationGeo=new T.BufferGeometry();circulationGeo.setAttribute('position',new T.BufferAttribute(circulationPos,3));
  const circulation=new T.Points(circulationGeo,new T.PointsMaterial({size:.65,transparent:true,opacity:.28,depthWrite:false}));world.add(circulation);circulation.renderOrder=7;circulation.frustumCulled=false;
  // Surface rings travel outward from the plunging stream.
  const ringMaterial=new T.MeshBasicMaterial({transparent:true,opacity:.20,depthWrite:false,side:T.DoubleSide});
  const ringsMeshes=[];
  for(let i=0;i<5;i++){const m=mesh(new T.TorusGeometry(1,.035,4,80),ringMaterial.clone());m.rotation.x=Math.PI/2;m.renderOrder=6;ringsMeshes.push(m);}
  let frameCounter=0;
  function update(t,dt=0,immediate=true,options={}) {
    const waterOn=options.waterOn??smooth(6,6.65,t)*(1-smooth(27.7,28.0,t));
    const gasOn=options.gasOn??smooth(-.6,.3,t)*(1-smooth(4.4,6.8,t));
    const refill=smooth(6.4,28,t),level=options.level??lerp(LOW,HIGH,refill);
    const decay=t<28?1:Math.exp(-(t-28)*.65),agitation=waterOn*1.15+gasOn*.30+(t>28?.85*decay:0);
    pool.scale.y=level;pool.position.y=level/2;surface.position.y=level;meniscus.position.y=level+.04;
    floatGroup.position.y=level-8.766;
    inletWater.visible=waterOn>.01;boreWater.visible=waterOn>.01;gasIn.visible=gasOn>.01;gasLineMat.opacity=.18+.26*gasOn;
    jet.visible=waterOn>.005;
    const gap=JY-level,front=waterOn>.98?1:smooth(6.1,6.65,t),jetLength=gap*front;
    for(let i=0;i<=JN;i++) {
      const s=i/JN,d=jetLength*s;
      const contraction=1-.23*(1-Math.exp(-d/1.2));
      const corrugation=1+.085*s*Math.sin(d*1.2-t*50)+.025*Math.sin(d*2.1-t*78);
      const radius=BORE/2*contraction*corrugation*Math.sqrt(Math.max(.05,waterOn));
      const sway=.58*s*s*Math.sin(d*.32-t*17)+.12*s*Math.sin(d*.68-t*29),swayz=.40*s*s*Math.cos(d*.23-t*19);
      for(let j=0;j<JR;j++){const a=j/JR*Math.PI*2,idx=(i*JR+j)*3;jetPositions[idx]=JX+sway+Math.cos(a)*radius;jetPositions[idx+1]=JY-d;jetPositions[idx+2]=swayz+Math.sin(a)*radius;}
    }
    jetGeo.attributes.position.needsUpdate=true;jetGeo.computeVertexNormals();
    function surfaceHeight(x,z) {
      const dx=x-JX,r=Math.hypot(dx,z),a=Math.atan2(z,dx),edgeFade=1-smooth(R-7,R,Math.hypot(x,z));
      const wave=Math.sin(r*.51-t*15.5+Math.sin(a*3-t*4)*.8)*Math.exp(-r/34)*1.25;
      const cavity=-5.1*Math.exp(-r*r/16)*(1+.16*Math.sin(t*13));
      const lip=2.1*Math.exp(-Math.pow((r-5.0)/2.1,2))*(1+.35*Math.sin(a*5+t*12));
      const chop=.55*Math.sin(x*.21+t*6.2)*Math.cos(z*.19-t*5.1)+.22*Math.sin(x*.47-z*.31+t*11);
      return edgeFade*(agitation*(wave+waterOn*(cavity+lip)) + chop*Math.max(agitation,decay*.12));
    }
    for(let i=0;i<surfaceAttr.count;i++)surfaceAttr.setY(i,surfaceHeight(surfaceAttr.getX(i),surfaceAttr.getZ(i)));
    surfaceAttr.needsUpdate=true;if(frameCounter%2===0||immediate)waterGeo.computeVertexNormals();
    crown.visible=waterOn>.7;
    for(let i=0;i<=crownSegments;i++) {
      const a=i/crownSegments*Math.PI*2,r=4.7+.9*Math.sin(a*7+t*17)+.35*Math.sin(a*13-t*8);
      const peak=(1.8+2.7*Math.pow(.5+.5*Math.sin(a*9+t*13),3))*waterOn;
      const p=i*6;crownPos[p]=JX+Math.cos(a)*1.6;crownPos[p+1]=level-3.2;crownPos[p+2]=Math.sin(a)*1.6;
      crownPos[p+3]=JX+Math.cos(a)*r;crownPos[p+4]=level+peak;crownPos[p+5]=Math.sin(a)*r;
    }
    crownGeo.attributes.position.needsUpdate=true;crownGeo.computeVertexNormals();
    let activeFeed=0,activeEntrained=0;
    for(let i=0;i<FEED_BUBBLES;i++) {
      // Larger, wobbling bubbles leave the plain port in finite bursts.
      const seed=(i*.61803398875)%1,cycle=1.25+(i%7)*.09;
      const age=mod(t+i*.131,cycle),born=t-age,u=age/cycle;
      let size=0,x=JX,y=0,z=0;
      if(born<5.45&&born>-.9) {
        const spread=1+11*Math.pow(u,1.35);
        x=JX+Math.sin(u*12+i*2.2)*spread;
        z=Math.cos(u*9+i)*spread*.75+3*u;
        y=2+u*(level-1.5);
        size=(1.3+seed*seed*3.4)*(1-.12*u)*Math.min(1,u*18+.35);
        if(y>level+.3)size=0;
      }
      if(size>.05)activeFeed++;
      instance(bubbles,i,x,y,z,Math.max(.0001,size),.72+.14*Math.sin(i+t*17));
    }
    bubbles.instanceMatrix.needsUpdate=true;
    for(let i=0;i<ENTRAINED_BUBBLES;i++) {
      const seed=(i*.754877666)%1,life=1.35+(i%11)*.085;
      const age=mod(t+i*.077,life),born=t-age,u=age/life,a=i*2.39996;
      const active=born>6.5&&born<27.95;
      const maxDepth=Math.min(level-6,38+seed*20);
      let radius,depth,theta;
      if(u<.61){const d=u/.61;radius=(1.2+11*d)*Math.sqrt(seed+.03);depth=2+maxDepth*d;theta=a+d*2.7+Math.sin(t*11+i)*d*.15;}
      else {const up=(u-.61)/.39;radius=(11+up*16)*Math.sqrt(seed+.1);depth=(maxDepth+2)*(1-up);theta=a+2.7+up*1.2;}
      const x=JX+Math.cos(theta)*radius,z=Math.sin(theta)*radius;
      const size=active?(.42+seed*seed*1.60)*(1-.38*u)*Math.min(1,u*16+.6):0;
      if(size>.05)activeEntrained++;
      instance(entrained,i,x,Math.max(2,level-depth),z,Math.max(.0001,size),.82+.13*Math.sin(t*22+i));
    }
    entrained.instanceMatrix.needsUpdate=true;
    for(let i=0;i<FOAM_BUBBLES;i++) {
      const u=mod(t*1.9+i*.61803,1),a=i*2.39996+t*.6,rad=3.5+u*10.5;
      const x=JX+Math.cos(a)*rad,z=Math.sin(a)*rad;
      const born=t-u/1.9,active=born>6.6&&born<28;
      const size=active?(.4+(i%7)*.12)*Math.pow(1-u,.38):0;
      instance(foam,i,x,level+surfaceHeight(x,z)+size*.25,z,Math.max(.0001,size),.52);
    }
    foam.instanceMatrix.needsUpdate=true;
    for(let i=0;i<DROPLETS;i++) {
      const age=mod(t*1.8+i*.037,.9),a=i*2.39996,active=waterOn>.85;
      const rad=2.5+age*(9+i%8),y=level+(25+i%14)*age-52*age*age;
      const s=active&&y>level+.35?.25+(i%5)*.075:0;
      instance(droplets,i,JX+Math.cos(a)*rad,y,Math.sin(a)*rad,Math.max(.0001,s),1.3);
    }
    droplets.instanceMatrix.needsUpdate=true;
    const gasOpacity=.045+.045*smooth(0,5,t);gasPoints.material.opacity=gasOpacity;
    for(let i=0;i<gasCount;i++) {
      const a=i*2.399963+.023*t,rr=Math.sqrt(((i*.754877666)%1))*(R-5),f=mod(i*.5698403+t*.013,1);
      gasPos[3*i]=Math.cos(a)*rr;gasPos[3*i+1]=level+3+f*(H-level-6);gasPos[3*i+2]=Math.sin(a)*rr;
    }
    gasGeometry.attributes.position.needsUpdate=true;
    circulation.material.opacity=.24*agitation;
    for(let i=0;i<circulationCount;i++) {
      const u=mod(t*.55+i*.61803,1),a=(i%6)/6*Math.PI*2,ring=1+(i%7)*.055;
      // A downward central flow turns outward, then rises around its edges.
      const x=JX+(14-13*Math.cos(u*2*Math.PI))*Math.cos(a)*ring,z=(14-13*Math.cos(u*2*Math.PI))*Math.sin(a)*ring;
      circulationPos[3*i]=x;circulationPos[3*i+1]=level-16-15*Math.sin(u*2*Math.PI);circulationPos[3*i+2]=z;
    }
    circulationGeo.attributes.position.needsUpdate=true;
    ringsMeshes.forEach((m,i)=>{const u=mod(t*.47+i/5,1),r=3+u*34;m.scale.set(r,r,r);m.position.set(JX,level+.1,0);m.material.opacity=.065*(1-u)*agitation;m.visible=agitation>.01&&r<R-Math.abs(JX);});
    frameCounter++;
    return {level,waterOn,gasOn,activeFeed,activeEntrained,agitation};
  }
  const oldPalette=setPalette;
  function refreshPalette(){oldPalette();const lightHost=palette.bg.r+palette.bg.g+palette.bg.b>1.5;
    const dark=mix(palette.bg,palette.fg,lightHost?.94:.08),bright=mix(palette.bg,palette.fg,lightHost?.05:.94);
    bubbleMaterial.uniforms.rimTint.value.copy(mix(dark,palette.gas,.25));
    bubbleMaterial.uniforms.fillTint.value.copy(mix(palette.water,bright,.56));
    bubbleMaterial.uniforms.lightTint.value.copy(bright);
    circulation.material.color.copy(palette.water);gasPoints.material.color.copy(palette.gas);ringsMeshes.forEach(m=>m.material.color.copy(mix(palette.water,palette.fg,.25)));}
  refreshPalette();
  return {world,vessel,tick:update,waterSide,waterTop,wallSteel,steel,jetMat,floatGroup,guide,magnet,
    bubbles,entrained,foam,gasPoints,circulation,LOW,HIGH,H,R,RO,JX,JY,
    setWallOpacity(a){wallSteel.transparent=a<.999;wallSteel.opacity=a;wallSteel.depthWrite=a>.99;},
    setAccent(a){floatMat.emissive.setRGB(.35*a,.12*a,.015*a);}
  };
};
