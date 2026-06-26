import { readFileSync } from "node:fs"
const c = JSON.parse(readFileSync(".next.json","utf8")) as any[]
const by:Record<string,any[]>={}; for(const e of c)(by[e.type]||=[]).push(e)

console.log("## COPPER POUR element structure")
for(const p of by.pcb_copper_pour||[]){
  console.log(`- layer=${p.layer} net=${p.connects_to||p.connectsTo||p.source_net_id||"?"} keys=[${Object.keys(p).join(",")}]`)
}
// dump one full
if(by.pcb_copper_pour?.length) console.log("\nsample:",JSON.stringify(by.pcb_copper_pour[0]).slice(0,600))

console.log("\n## SMALL SILK TEXTS (font_size <= 0.7)")
const small=(by.pcb_silkscreen_text||[]).filter(t=>(t.font_size||9)<=0.7)
const byText:Record<string,number>={}
for(const t of small){ const k=`${t.font_size}mm "${(t.text||'').slice(0,16)}"`; byText[k]=(byText[k]||0)+1 }
const ks=Object.keys(byText); console.log("count:",small.length,"unique:",ks.length)
for(const k of ks.slice(0,20)) console.log("  ",byText[k],"x",k)

console.log("\n## BOARD OUTLINE")
const b=by.pcb_board?.[0]
console.log("outline pts:",JSON.stringify(b?.outline))
console.log("width/height/center:",b?.width,b?.height,JSON.stringify(b?.center))
