const cj = JSON.parse(require("fs").readFileSync("zprobe.cj.json","utf8"))
const comps = cj.filter((e:any)=>e.type==="source_component")
const pcbComps = cj.filter((e:any)=>e.type==="pcb_component")
// map source name -> pcb_component_id + center
const srcById:any = {}; for (const c of comps) srcById[c.source_component_id]=c.name
const centerByPcb:any = {}, nameByPcb:any = {}
for (const p of pcbComps){ centerByPcb[p.pcb_component_id]={x:p.center.x,y:p.center.y}; nameByPcb[p.pcb_component_id]=srcById[p.source_component_id] }
const paths = cj.filter((e:any)=>e.type==="pcb_silkscreen_path")
const texts = cj.filter((e:any)=>e.type==="pcb_silkscreen_text")
const f=(n:number)=>n.toFixed(3)
for (const pc of pcbComps){
  const name = nameByPcb[pc.pcb_component_id]; const c=centerByPcb[pc.pcb_component_id]
  console.log(`\n=== ${name} @ (${f(c.x)},${f(c.y)}) ===`)
  const myPaths = paths.filter((p:any)=>p.pcb_component_id===pc.pcb_component_id)
  for (const p of myPaths){
    const xs=p.route.map((r:any)=>r.x-c.x), ys=p.route.map((r:any)=>r.y-c.y)
    console.log(`  silk-path strokeW=${p.stroke_width} local-x[${f(Math.min(...xs))},${f(Math.max(...xs))}] local-y[${f(Math.min(...ys))},${f(Math.max(...ys))}] pts=${p.route.length}`)
  }
  const myTexts = texts.filter((t:any)=>t.pcb_component_id===pc.pcb_component_id)
  for (const t of myTexts){
    console.log(`  silk-text "${t.text}" local=(${f(t.anchor_position.x-c.x)},${f(t.anchor_position.y-c.y)}) font=${t.font_size} rot=${t.ccw_rotation||0} align=${t.anchor_alignment}`)
  }
}
