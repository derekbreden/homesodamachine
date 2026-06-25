/**
 * _spacing.ts — measure the REALIZED copper clearance of a built board, since
 * the autorouter stamps trace width without re-routing or DRC-checking it.
 * Reports the minimum edge-to-edge gap between copper of DIFFERENT nets, for:
 *   trace-segment <-> trace-segment, and trace-segment <-> pad/via.
 * Per layer (top/bottom). A gap < ~0 means an overlap the DRC missed.
 *
 *   bun _spacing.ts [board]
 */
const board = process.argv[2] || "mini"
const c = JSON.parse(require("fs").readFileSync(`${board}.circuit.json`, "utf8")) as any[]

type Seg = { x1: number; y1: number; x2: number; y2: number; w: number; net: string; layer: string }
const segs: Seg[] = []
for (const t of c.filter((e) => e.type === "pcb_trace")) {
  const r = t.route || []
  for (let i = 0; i + 1 < r.length; i++) {
    const a = r[i], b = r[i + 1]
    if (a.layer !== b.layer) continue // via transition, not a planar segment
    segs.push({ x1: a.x, y1: a.y, x2: b.x, y2: b.y, w: a.width || 0.2, net: t.connection_name, layer: a.layer })
  }
}

// pads + vias as net-bearing circles (radius). pad net via the port->trace map.
const pcbPortNet: Record<string, string> = {}
for (const t of c.filter((e) => e.type === "pcb_trace"))
  for (const s of t.route || []) {
    if (s.start_pcb_port_id) pcbPortNet[s.start_pcb_port_id] = t.connection_name
    if (s.end_pcb_port_id) pcbPortNet[s.end_pcb_port_id] = t.connection_name
  }
type Circ = { x: number; y: number; r: number; net: string; layers: string[]; what: string }
const circs: Circ[] = []
for (const p of c.filter((e) => e.type === "pcb_plated_hole"))
  circs.push({ x: p.x, y: p.y, r: Math.max(p.rect_pad_width || 0, p.rect_pad_height || 0, p.hole_diameter || 0) / 2, net: pcbPortNet[p.pcb_port_id] || `(pad ${p.pcb_plated_hole_id})`, layers: p.layers || ["top", "bottom"], what: "pad" })
for (const v of c.filter((e) => e.type === "pcb_via"))
  circs.push({ x: v.x, y: v.y, r: (v.outer_diameter || 0.3) / 2, net: c.find((t) => t.type === "pcb_trace" && t.pcb_trace_id === v.pcb_trace_id)?.connection_name || `(via)`, layers: v.layers || ["top", "bottom"], what: "via" })

// point-to-segment distance
const ptSeg = (px: number, py: number, s: Seg) => {
  const dx = s.x2 - s.x1, dy = s.y2 - s.y1
  const L2 = dx * dx + dy * dy || 1e-9
  let t = ((px - s.x1) * dx + (py - s.y1) * dy) / L2
  t = Math.max(0, Math.min(1, t))
  const cx = s.x1 + t * dx, cy = s.y1 + t * dy
  return Math.hypot(px - cx, py - cy)
}
// segment-to-segment distance (sample-free: min of endpoint-to-seg both ways; good enough at these scales)
const segSeg = (a: Seg, b: Seg) =>
  Math.min(ptSeg(a.x1, a.y1, b), ptSeg(a.x2, a.y2, b), ptSeg(b.x1, b.y1, a), ptSeg(b.x2, b.y2, a))

let minTT = { gap: Infinity, info: "" }
for (let i = 0; i < segs.length; i++)
  for (let j = i + 1; j < segs.length; j++) {
    const a = segs[i], b = segs[j]
    if (a.layer !== b.layer || a.net === b.net) continue
    const gap = segSeg(a, b) - a.w / 2 - b.w / 2
    if (gap < minTT.gap) minTT = { gap, info: `${a.net.slice(0, 24)} | ${b.net.slice(0, 24)} @${a.layer} ~(${a.x1.toFixed(1)},${a.y1.toFixed(1)})` }
  }

let minTP = { gap: Infinity, info: "" }
for (const s of segs)
  for (const p of circs) {
    if (!p.layers.includes(s.layer)) continue
    if (p.net === s.net) continue
    const gap = ptSeg(p.x, p.y, s) - p.r - s.w / 2
    if (gap < minTP.gap) minTP = { gap, info: `${s.net.slice(0, 20)} -> ${p.what} ${p.net.slice(0, 20)} @${s.layer} (${p.x.toFixed(1)},${p.y.toFixed(1)})` }
  }

console.log(`# ${board} realized clearance`)
console.log(`trace<->trace  min edge gap: ${minTT.gap.toFixed(3)} mm   [${minTT.info}]`)
console.log(`trace<->pad/via min edge gap: ${minTP.gap.toFixed(3)} mm   [${minTP.info}]`)
console.log(`(segments: ${segs.length}, pads+vias: ${circs.length})`)
