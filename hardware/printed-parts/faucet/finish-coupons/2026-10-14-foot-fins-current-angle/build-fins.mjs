// Manual experiment: call the unmodified upstream engine on the posed foot.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [engineDir, input, outputDir] = process.argv.slice(2);
const load = file => import(pathToFileURL(path.resolve(engineDir, file)).href);
const {readSTL, writeBinarySTL} = await load('web/stl.js');
const {buildTopology, analyze} = await load('web/overhangs.js');
const {buildFins} = await load('web/fins.js');
const {PROP} = await load('web/prop.js');
const {kissEnds} = await load('web/kiss.js');
const pos = readSTL(fs.readFileSync(input));
const topo = buildTopology({getAttribute:k=>k==='position'?{array:pos}:null});
const a = -15 * Math.PI/180, c=Math.cos(a), s=Math.sin(a);
const rot = [1,0,0,0,c,s,0,-s,c];
const result = analyze(topo,45,rot);
const options = {mode:'auto',bedPad:false,layerHeight:0.24,coverage:0.5,
  tineDensity:0,plateOnly:true,tunables:{propGap:0.24,cutout:'none',iface:false,
    nozzle:0.4,wallLines:2,tinesPerWall:0}};
fs.mkdirSync(outputDir,{recursive:true});
const records=[];
for (const tines of [true,false]) {
  globalThis.__TINECAP=[];
  const built=buildFins(topo,result,rot,{...options,tines});
  const tris=built.triangles;
  const flat=typeof tris[0]==='number';
  const points=flat?Array.from({length:tris.length/3},(_,i)=>tris.slice(i*3,i*3+3)):tris;
  const name=tines?'A-tines':'B-plain';
  const blob=writeBinarySTL(points,name);
  fs.writeFileSync(path.join(outputDir,`${name}-seated.stl`),Buffer.from(await blob.arrayBuffer()));
  const rec={name,tines_enabled:tines,options:{...options,tines},offset:result.offset,
    overhang_area_mm2:result.overArea,bed_area_mm2:result.bedArea,
    tines:built.tines,fin_count:built.fins.length,skipped:built.skipped,
    floating:built.floating,seating:built.seating,
    support_parameters:{wall_mm:PROP.th,tip_mm:PROP.tip,tine_width_mm:PROP.tineW,
      tine_height_mm:0.24,effective_tine_search_reach_mm:PROP.tineReach*1.2,
      max_span_mm:PROP.maxUnsupportedSpan,edge_inset_mm:PROP.edgeInset},
    fins:built.fins,props:built.props,
    retained_tines:(built.props??[]).flatMap(p=>p.caps?
      globalThis.__TINECAP.slice(p.caps[0],p.caps[1]):[]).map(t=>{
        const top=Math.round((t.z+0.12)/0.24)*0.24,bottom=top-0.24;
        return {...t,top,bottom,ends:kissEnds(topo,rot,result.offset,t.x,t.y,
          t.biteX,t.biteY,bottom,top,{half:0.25,back:0.3,reach:0.6})};
      })};
  records.push(rec);
  console.log(JSON.stringify({name,tines:rec.tines,fins:rec.fin_count,seating:rec.seating,
    floating:rec.floating,offset:rec.offset}));
}
fs.writeFileSync(path.join(outputDir,'engine.json'),JSON.stringify(records,null,2)+'\n');
