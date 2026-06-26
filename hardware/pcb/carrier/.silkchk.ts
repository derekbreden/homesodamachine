import { readFileSync } from "node:fs"
const c = JSON.parse(readFileSync(".next.json","utf8")) as any[]
const by:Record<string,any[]>={}; for(const e of c)(by[e.type]||=[]).push(e)
const pads=(by.pcb_plated_hole||[]).map(h=>({x:h.x,y:h.y,r:(h.outer_diameter||h.rect_pad_width||1)/2}))
// approximate each silk text as a box: width ~ chars*fs*0.62, height ~ fs, centered at (x,y), rotated 0/90/270
let hits=0, worst=0, examples:string[]=[]
for(const t of by.pcb_silkscreen_text||[]){
  const fs=t.font_size||0.8, txt=(t.text||""), wlen=txt.length*fs*0.62, hh=fs
  const rot=((t.pcb_rotation||t.ccw_rotation||0)%360+360)%360
  // half-extents in x,y after rotation (axis-aligned approx)
  const hx=(rot===90||rot===270)?hh/2:wlen/2
  const hy=(rot===90||rot===270)?wlen/2:hh/2
  for(const p of pads){
    const dx=Math.abs(p.x-t.x)-hx, dy=Math.abs(p.y-t.y)-hy
    // overlap if pad center within box expanded by pad r
    if(dx< p.r && dy< p.r){ const pen=Math.min(p.r-dx,p.r-dy); if(pen>0){hits++; if(pen>worst){worst=pen}; if(examples.length<8)examples.push(`"${txt}"@(${t.x.toFixed(1)},${t.y.toFixed(1)}) pad(${p.x.toFixed(1)},${p.y.toFixed(1)}) ov~${pen.toFixed(2)}mm`); break} }
  }
}
console.log("silk texts:",(by.pcb_silkscreen_text||[]).length,"| texts overlapping a pad:",hits,"| worst overlap ~",worst.toFixed(2),"mm")
for(const e of examples) console.log("  ",e)
