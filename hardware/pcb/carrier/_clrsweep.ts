/**
 * _clrsweep.ts — sweep the board's autorouter spacing knobs and measure the
 * REALIZED min trace<->trace copper gap for each. Settles which global lever (if
 * any) actually moves the autorouter's packing floor. Rewrites only the <board>
 * opening tag of mini.tsx into a temp file, exports circuit-json, measures.
 *
 *   bun _clrsweep.ts
 */
import { execFileSync } from "node:child_process"
import { readFileSync, writeFileSync, rmSync } from "node:fs"

const base = readFileSync("mini.tsx", "utf8")
const tsci = "node_modules/.bin/tsci"

// realized trace<->trace min edge gap (different nets, same layer)
const minTT = (c: any[]) => {
  type Seg = { x1: number; y1: number; x2: number; y2: number; w: number; net: string; layer: string }
  const segs: Seg[] = []
  for (const t of c.filter((e) => e.type === "pcb_trace")) {
    const r = t.route || []
    for (let i = 0; i + 1 < r.length; i++) {
      const a = r[i], b = r[i + 1]
      if (a.layer !== b.layer) continue
      segs.push({ x1: a.x, y1: a.y, x2: b.x, y2: b.y, w: a.width || 0.2, net: t.connection_name, layer: a.layer })
    }
  }
  const ptSeg = (px: number, py: number, s: Seg) => {
    const dx = s.x2 - s.x1, dy = s.y2 - s.y1, L2 = dx * dx + dy * dy || 1e-9
    let tt = ((px - s.x1) * dx + (py - s.y1) * dy) / L2; tt = Math.max(0, Math.min(1, tt))
    return Math.hypot(px - (s.x1 + tt * dx), py - (s.y1 + tt * dy))
  }
  const segSeg = (a: Seg, b: Seg) => Math.min(ptSeg(a.x1, a.y1, b), ptSeg(a.x2, a.y2, b), ptSeg(b.x1, b.y1, a), ptSeg(b.x2, b.y2, a))
  let tt = { gap: Infinity, info: "" }
  for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) {
    const a = segs[i], b = segs[j]
    if (a.layer !== b.layer || a.net === b.net) continue
    const gap = segSeg(a, b) - a.w / 2 - b.w / 2
    if (gap < tt.gap) tt = { gap, info: `@${a.layer}~(${a.x1.toFixed(1)},${a.y1.toFixed(1)})` }
  }
  // trace<->pad/via (different nets)
  const portNet: Record<string, string> = {}
  for (const t of c.filter((e) => e.type === "pcb_trace")) for (const s of t.route || []) {
    if (s.start_pcb_port_id) portNet[s.start_pcb_port_id] = t.connection_name
    if (s.end_pcb_port_id) portNet[s.end_pcb_port_id] = t.connection_name
  }
  const circs: { x: number; y: number; r: number; net: string; layers: string[] }[] = []
  for (const p of c.filter((e) => e.type === "pcb_plated_hole")) circs.push({ x: p.x, y: p.y, r: Math.max(p.rect_pad_width || 0, p.rect_pad_height || 0, p.hole_diameter || 0) / 2, net: portNet[p.pcb_port_id] || `pad`, layers: p.layers || ["top", "bottom"] })
  for (const v of c.filter((e) => e.type === "pcb_via")) circs.push({ x: v.x, y: v.y, r: (v.outer_diameter || 0.3) / 2, net: c.find((t: any) => t.type === "pcb_trace" && t.pcb_trace_id === v.pcb_trace_id)?.connection_name || `via`, layers: v.layers || ["top", "bottom"] })
  let tp = { gap: Infinity, info: "" }
  for (const s of segs) for (const p of circs) {
    if (!p.layers.includes(s.layer) || p.net === s.net) continue
    const gap = ptSeg(p.x, p.y, s) - p.r - s.w / 2
    if (gap < tp.gap) tp = { gap, info: `@${s.layer}(${p.x.toFixed(1)},${p.y.toFixed(1)})` }
  }
  return { tt, tp, floor: Math.min(tt.gap, tp.gap) }
}

const run = (label: string, boardTag: string) => {
  const variant = base.replace(/<board[^>]*>/, boardTag)
  if (variant === base && !base.includes(boardTag)) { console.log(`${label}: REPLACE FAILED`); return }
  const f = "._clrsw.tsx", j = "._clrsw.json"
  writeFileSync(f, variant)
  let viaN = 0, drc = 0, m: any = null, traceW = 0
  try {
    execFileSync(tsci, ["export", "-f", "circuit-json", "-o", j, f], { stdio: ["ignore", "ignore", "pipe"] })
    const c = JSON.parse(readFileSync(j, "utf8")) as any[]
    viaN = c.filter((e) => e.type === "pcb_via").length
    drc = c.filter((e) => e.type === "pcb_trace_error" || e.type === "pcb_port_not_connected_error").length
    let thin = Infinity
    for (const e of c) if (e.type === "pcb_trace") for (const r of (e.route || [])) if (r.width && r.width < thin) thin = r.width
    traceW = thin
    m = minTT(c)
  } catch (e: any) {
    console.log(`${label}: EXPORT FAILED ${String(e.stderr || e.status || e).slice(0, 120)}`)
    rmSync(f, { force: true }); rmSync(j, { force: true }); rmSync("._clrsw.circuit.json", { force: true }); return
  }
  rmSync(f, { force: true }); rmSync(j, { force: true }); rmSync("._clrsw.circuit.json", { force: true })
  console.log(`${label.padEnd(20)} vias:${String(viaN).padStart(3)} drc:${drc} minW:${traceW.toFixed(3)}  T-T:${m.tt.gap.toFixed(3)} ${m.tt.info}  T-pad:${m.tp.gap.toFixed(3)} ${m.tp.info}  FLOOR:${m.floor.toFixed(3)}mm`)
}

console.log("# minTraceWidth sweep — FLOOR = min(trace-trace, trace-pad), the weakest link\n")
for (const w of ["0.13mm", "0.14mm", "0.15mm", "0.16mm", "0.17mm", "0.18mm", "0.2mm", "0.22mm", "0.25mm"])
  run(`minTraceWidth=${w}`, `<board width="134mm" height="100mm" minTraceWidth="${w}">`)
