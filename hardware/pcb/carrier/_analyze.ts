/**
 * _analyze.ts — read a built <board>.circuit.json and report the metrics that
 * matter for layout optimisation: total vias, DRC errors, real content bounds,
 * per-module bounding boxes + gaps, and (the useful part) every via attributed
 * to the named-pin pair of the trace it sits on, grouped by connector/module.
 *
 *   bun _analyze.ts [board]        # default: mini
 */
const board = process.argv[2] || "mini"
const c = JSON.parse(require("fs").readFileSync(`${board}.circuit.json`, "utf8")) as any[]

const byType: Record<string, any[]> = {}
for (const e of c) (byType[e.type] ||= []).push(e)

// ---- maps ------------------------------------------------------------------
const srcComp: Record<string, any> = {}
for (const e of byType.source_component || []) srcComp[e.source_component_id] = e
const srcPort: Record<string, any> = {}
for (const e of byType.source_port || []) srcPort[e.source_port_id] = e
const pcbPort: Record<string, any> = {}
for (const e of byType.pcb_port || []) pcbPort[e.pcb_port_id] = e

// pcb_port_id -> "U1A.IO21"
const portLabel = (pid: string): string => {
  const pp = pcbPort[pid]
  if (!pp) return pid
  const sp = srcPort[pp.source_port_id]
  if (!sp) return pid
  const comp = srcComp[sp.source_component_id]
  return `${comp ? comp.name : "?"}.${sp.name}`
}

// ---- traces: endpoints + net ----------------------------------------------
const traceEndpoints: Record<string, { net: string; ports: string[] }> = {}
for (const t of byType.pcb_trace || []) {
  const ports = new Set<string>()
  for (const seg of t.route || []) {
    if (seg.start_pcb_port_id) ports.add(seg.start_pcb_port_id)
    if (seg.end_pcb_port_id) ports.add(seg.end_pcb_port_id)
  }
  traceEndpoints[t.pcb_trace_id] = { net: t.connection_name, ports: [...ports] }
}

// ---- vias attributed to their trace's named-pin pair -----------------------
const vias = byType.pcb_via || []
const viaGroups: Record<string, number> = {}
const viaDetail: Record<string, string[]> = {}
for (const v of vias) {
  const te = traceEndpoints[v.pcb_trace_id]
  let key = "(no-trace)"
  if (te) {
    const labels = te.ports.map(portLabel).sort()
    key = labels.join("  <->  ") || te.net
  }
  viaGroups[key] = (viaGroups[key] || 0) + 1
  ;(viaDetail[key] ||= []).push(`(${v.x.toFixed(1)}, ${v.y.toFixed(1)})`)
}

// ---- module bounding boxes (from pcb_component + its pads) ------------------
// gather all copper/hole features per pcb_component
const compFeatures: Record<string, { xs: number[]; ys: number[] }> = {}
const addF = (cid: string, x: number, y: number, hw = 0, hh = 0) => {
  if (!cid) return
  const f = (compFeatures[cid] ||= { xs: [], ys: [] })
  f.xs.push(x - hw, x + hw); f.ys.push(y - hh, y + hh)
}
for (const h of byType.pcb_plated_hole || []) addF(h.pcb_component_id, h.x, h.y, (h.rect_pad_width || h.hole_diameter) / 2, (h.rect_pad_height || h.hole_diameter) / 2)
for (const h of byType.pcb_hole || []) addF(h.pcb_component_id, h.x, h.y, h.hole_diameter / 2, h.hole_diameter / 2)
for (const p of byType.pcb_smtpad || []) addF(p.pcb_component_id, p.x, p.y, (p.width || 0) / 2, (p.height || 0) / 2)

const pcbComp: Record<string, any> = {}
for (const e of byType.pcb_component || []) pcbComp[e.pcb_component_id] = e

type Box = { name: string; x0: number; y0: number; x1: number; y1: number; cx: number; cy: number; rot: number }
const boxes: Box[] = []
for (const cid in compFeatures) {
  const f = compFeatures[cid]
  const comp = pcbComp[cid]
  const sc = comp ? srcComp[comp.source_component_id] : null
  boxes.push({
    name: sc ? sc.name : cid,
    x0: Math.min(...f.xs), y0: Math.min(...f.ys),
    x1: Math.max(...f.xs), y1: Math.max(...f.ys),
    cx: comp ? comp.center.x : 0, cy: comp ? comp.center.y : 0,
    rot: comp ? comp.rotation : 0,
  })
}

// overall content bounds (copper + holes only — what must fit on the board)
const allX = boxes.flatMap((b) => [b.x0, b.x1])
const allY = boxes.flatMap((b) => [b.y0, b.y1])
const cx0 = Math.min(...allX), cx1 = Math.max(...allX)
const cy0 = Math.min(...allY), cy1 = Math.max(...allY)

// ---- DRC errors ------------------------------------------------------------
const errs = (byType as any)
const errTypes = Object.keys(byType).filter((k) => /error/.test(k))
const warnUnrouted = (byType.source_pin_missing_trace_warning || []).length

// ---- report ----------------------------------------------------------------
const board0 = (byType.pcb_board || [])[0]
console.log(`# ${board}  —  vias: ${vias.length}   unrouted-pins: ${warnUnrouted}`)
console.log(`board declared: ${board0?.width} x ${board0?.height} mm`)
console.log(`content bbox:   ${(cx1 - cx0).toFixed(1)} x ${(cy1 - cy0).toFixed(1)} mm   [x ${cx0.toFixed(1)}..${cx1.toFixed(1)}  y ${cy0.toFixed(1)}..${cy1.toFixed(1)}]`)
const slackX = (board0?.width ?? 0) - (cx1 - cx0), slackY = (board0?.height ?? 0) - (cy1 - cy0)
console.log(`board slack:    ${slackX.toFixed(1)} x ${slackY.toFixed(1)} mm (declared - content)`)
if (errTypes.length) for (const et of errTypes) console.log(`DRC ${et}: ${byType[et].length}`)
else console.log(`DRC errors: 0`)

console.log(`\n## vias by net (named-pin pair), total ${vias.length}`)
for (const [k, n] of Object.entries(viaGroups).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(3)}  ${k}`)
}

console.log(`\n## modules (name: center rot | bbox WxH | edges)`)
for (const b of boxes.sort((a, b) => a.name.localeCompare(b.name))) {
  console.log(`  ${b.name.padEnd(5)} c=(${b.cx.toFixed(1)},${b.cy.toFixed(1)}) r${b.rot}  ${(b.x1 - b.x0).toFixed(1)}x${(b.y1 - b.y0).toFixed(1)}  x[${b.x0.toFixed(1)},${b.x1.toFixed(1)}] y[${b.y0.toFixed(1)},${b.y1.toFixed(1)}]`)
}
