// Manual tip-joint fin placement through the pinned, unmodified upstream engine.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [engineDir,input,scopeFile,outputDir] = process.argv.slice(2);
const load = f => import(pathToFileURL(path.resolve(engineDir,f)).href);
const {readSTL,writeBinarySTL} = await load('web/stl.js');
const {buildTopology,analyze} = await load('web/overhangs.js');
const {buildFins} = await load('web/fins.js');
const scope = JSON.parse(fs.readFileSync(scopeFile));
const pos = readSTL(fs.readFileSync(input));
const topo = buildTopology({getAttribute:k=>k==='position'?{array:pos}:null});
const a=-105*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
const rot=[1,0,0,0,c,s,0,-s,c];
const selected=new Set();
for(let f=0;f<topo.nFaces;f++) {
  const dot=scope.normal.reduce((v,n,i)=>v+n*topo.nrm[f*3+i],0);
  let distance=0;
  for(let v=0;v<3;v++) {
    const d=scope.normal.reduce((total,n,i)=>total+n*(pos[f*9+v*3+i]-scope.point[i]),0);
    distance=Math.max(distance,Math.abs(d));
  }
  if(dot<-.999 && distance<.02)selected.add(f);
}
fs.mkdirSync(outputDir,{recursive:true});
for(const [name,mode,coverage] of [['auto','auto',.5],['full','full',.5],['full100','full',1]]) {
  const result=analyze(topo,45,rot);
  for(let f=0;f<topo.nFaces;f++)if(!selected.has(f)){result.over[f]=0;result.kept[f]=0;}
  result.regions=result.regions.map(g=>{
    const faces=g.faces.filter(f=>selected.has(f));
    return {faces,area:faces.reduce((sum,f)=>sum+topo.area[f],0)};
  }).filter(g=>g.faces.length);
  result.overArea=result.regions.reduce((v,g)=>v+g.area,0);
  result.overFaceCount=result.regions.reduce((v,g)=>v+g.faces.length,0);
  const options={mode,coverage,downhill:true,bedPad:false,layerHeight:.24,tines:false,
    plateOnly:true,tineDensity:0,tunables:{propGap:.24,cutout:'none',iface:false,
      nozzle:.4,wallLines:2,tinesPerWall:0}};
  const built=buildFins(topo,result,rot,options);
  const flat=typeof built.triangles[0]==='number';
  const points=flat?Array.from({length:built.triangles.length/3},(_,i)=>built.triangles.slice(i*3,i*3+3)):built.triangles;
  if(points.length){
    const blob=writeBinarySTL(points,`tip-joint-${name}`);
    fs.writeFileSync(path.join(outputDir,`${name}-seated.stl`),Buffer.from(await blob.arrayBuffer()));
  }
  const record={name,options,selected_faces:Array.from(selected),contact_scope:scope,
    retained_contact_faces:result.overFaceCount,contact_area_mm2:result.overArea,
    offset:result.offset,fin_count:built.fins.length,tines:built.tines,
    fins:built.fins,props:built.props,seating:built.seating,skipped:built.skipped,
    floating:built.floating};
  fs.writeFileSync(path.join(outputDir,`${name}.json`),JSON.stringify(record,null,2)+'\n');
  console.log(JSON.stringify({name,fins:built.fins.length,tines:built.tines,
    contact_area:result.overArea,offset:result.offset,seating:built.seating}));
}
