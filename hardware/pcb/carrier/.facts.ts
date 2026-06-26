import { readFileSync } from "node:fs"
const c = JSON.parse(readFileSync(".next.json","utf8")) as any[]
const by:Record<string,any[]>={}; for(const e of c)(by[e.type]||=[]).push(e)
const round=(x:number,n=3)=>Math.round(x*10**n)/10**n
const distinct=(a:number[])=>[...new Set(a.map(v=>round(v)))].sort((x,y)=>x-y)

console.log("## BOARD")
const b=by.pcb_board?.[0]
console.log("declared WxH:",b?.width,"x",b?.height,"center",JSON.stringify(b?.center))
const ec=by.pcb_board_outline?.[0]||b
// outline points
const ol = (by.pcb_cutout||[]).length
console.log("cutouts:",ol)

console.log("\n## COPPER TRACES")
let tw:number[]=[]
for(const t of by.pcb_trace||[]) for(const p of t.route||[]) if(p.route_type==="wire"&&p.width) tw.push(p.width)
console.log("distinct trace widths (mm):",distinct(tw))
console.log("min trace width:",Math.min(...tw),"count segments:",tw.length)
// layer usage
const layerWire:Record<string,number>={}
for(const t of by.pcb_trace||[]) for(const p of t.route||[]) if(p.route_type==="wire"&&p.layer) layerWire[p.layer]=(layerWire[p.layer]||0)+1
console.log("wire segments per layer:",JSON.stringify(layerWire))

console.log("\n## PLATED HOLES (component through-holes)")
const ph=by.pcb_plated_hole||[]
const phHole=distinct(ph.map(h=>h.hole_diameter||h.hole_width||0).filter(Boolean))
const phOuter=distinct(ph.map(h=>h.outer_diameter||0).filter(Boolean))
console.log("count:",ph.length)
console.log("distinct drill (mm):",phHole)
console.log("distinct pad OD (mm):",phOuter)
// annular ring per hole (min)
let minAnnular=1e9, minAnnShape=""
for(const h of ph){ const hd=h.hole_diameter||h.hole_width; const od=h.outer_diameter||h.rect_pad_width
  if(hd&&od){ const a=(od-hd)/2; if(a<minAnnular){minAnnular=a;minAnnShape=h.shape||"?"} } }
console.log("min annular ring (mm):",round(minAnnular,3),"shape:",minAnnShape)
// shapes
const shapes:Record<string,number>={}; for(const h of ph) shapes[h.shape||"?"]=(shapes[h.shape||"?"]||0)+1
console.log("pad shapes:",JSON.stringify(shapes))

console.log("\n## VIAS")
const v=by.pcb_via||[]
console.log("count:",v.length)
console.log("distinct via drill (mm):",distinct(v.map(x=>x.hole_diameter||0).filter(Boolean)))
console.log("distinct via OD (mm):",distinct(v.map(x=>x.outer_diameter||0).filter(Boolean)))
if(v.length){let ma=1e9;for(const x of v){const a=((x.outer_diameter||0)-(x.hole_diameter||0))/2;if(a<ma)ma=a}console.log("min via annular (mm):",round(ma,3))}

console.log("\n## NON-PLATED HOLES (mounting)")
const nph=by.pcb_hole||[]
console.log("count:",nph.length)
console.log("distinct dia (mm):",distinct(nph.map(h=>h.hole_diameter||h.hole_width||0).filter(Boolean)))

console.log("\n## SMD PADS")
const smt=by.pcb_smtpad||[]
console.log("count:",smt.length,"(0 => no paste/stencil needed)")

console.log("\n## SILKSCREEN TEXT")
const st=by.pcb_silkscreen_text||[]
const fs=distinct(st.map(t=>t.font_size||0).filter(Boolean))
console.log("count:",st.length,"distinct font_size (mm):",fs,"min:",Math.min(...st.map(t=>t.font_size||99)))

console.log("\n## EDGE / CONTENT EXTENT (copper incl. pours)")
let lo={x:1e9,y:1e9},hi={x:-1e9,y:-1e9}
const grow=(x:number,y:number)=>{lo.x=Math.min(lo.x,x);lo.y=Math.min(lo.y,y);hi.x=Math.max(hi.x,x);hi.y=Math.max(hi.y,y)}
for(const t of by.pcb_trace||[]) for(const p of t.route||[]) if(typeof p.x==="number")grow(p.x,p.y)
for(const h of [...ph,...v,...nph]) grow(h.x,h.y)
for(const p of by.pcb_copper_pour||[]) { // pours may carry route/points
  const pts=p.route||p.points||p.outline||[]
  for(const q of pts) if(typeof q.x==="number")grow(q.x,q.y) }
console.log("copper+pour bbox: x[",round(lo.x,2),",",round(hi.x,2),"] y[",round(lo.y,2),",",round(hi.y,2),"]")
console.log("pour element count:",(by.pcb_copper_pour||[]).length)
