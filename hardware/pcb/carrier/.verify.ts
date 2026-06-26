import { readFileSync } from "node:fs"
const c = JSON.parse(readFileSync(".next.json","utf8")) as any[]
const by:Record<string,any[]>={}; for(const e of c)(by[e.type]||=[]).push(e)
const round=(x:number,n=3)=>Math.round(x*10**n)/10**n
// silk font sizes
const fs=[...new Set((by.pcb_silkscreen_text||[]).map(t=>t.font_size).filter(Boolean))].sort((a,b)=>a-b)
console.log("silk font sizes (mm):",fs,"=> min",Math.min(...fs))
const n05=(by.pcb_silkscreen_text||[]).filter(t=>(t.font_size||9)<0.8).length
console.log("texts below 0.8mm:",n05)
// pour pullback per layer
const outline={x0:-66.9,x1:60.9,y0:-51,y1:47.7}
for(const p of by.pcb_copper_pour||[]){
  const r=p.brep_shape?.outer_ring?.vertices||[]
  if(!r.length){console.log(p.layer,"(no outer ring / explicit outline)");continue}
  const xs=r.map((v:any)=>v.x), ys=r.map((v:any)=>v.y)
  const lo={x:Math.min(...xs),y:Math.min(...ys)}, hi={x:Math.max(...xs),y:Math.max(...ys)}
  const pull={L:round(lo.x-outline.x0,2),R:round(outline.x1-hi.x,2),B:round(lo.y-outline.y0,2),T:round(outline.y1-hi.y,2)}
  console.log(`${p.layer.padEnd(7)} pullback L${pull.L} R${pull.R} B${pull.B} T${pull.T}`)
}
