/**
 * _analyze.ts — board metrics. Exports a fresh circuit-json to a temp file, then
 * reports total vias, DRC errors, content/silk bounds + board slack, every via
 * attributed to its net/connector pin-pair, per-module bboxes, the realized
 * minimum copper clearance (trace-trace and trace-pad, different nets), and trace
 * loops once each module's internal same-name pin-bonding is accounted for —
 * split into removable signal loops and intentional power/ground parallel paths.
 *
 *   bun _analyze.ts [board]        # default: mini
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"
import path from "node:path"

const board = process.argv[2] || "mini"
const tmp = `.${board}.measure.json`
const tsci = path.join("node_modules", ".bin", "tsci")
execFileSync(tsci, ["export", "-f", "circuit-json", "-o", tmp, `${board}.tsx`], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmp, "utf8")) as any[]
rmSync(tmp, { force: true })

const byType: Record<string, any[]> = {}
for (const e of c) (byType[e.type] ||= []).push(e)

const srcComp: Record<string, any> = {}, srcPort: Record<string, any> = {}, pcbPort: Record<string, any> = {}
for (const e of byType.source_component || []) srcComp[e.source_component_id] = e
for (const e of byType.source_port || []) srcPort[e.source_port_id] = e
for (const e of byType.pcb_port || []) pcbPort[e.pcb_port_id] = e
const portLabel = (pid: string): string => {
  const pp = pcbPort[pid]; if (!pp) return pid
  const sp = srcPort[pp.source_port_id]; if (!sp) return pid
  const comp = srcComp[sp.source_component_id]
  return `${comp ? comp.name : "?"}.${sp.name}`
}

// vias attributed to their trace's named-pin pair
const traceEndpoints: Record<string, string[]> = {}
for (const t of byType.pcb_trace || []) {
  const ports = new Set<string>()
  for (const seg of t.route || []) { if (seg.start_pcb_port_id) ports.add(seg.start_pcb_port_id); if (seg.end_pcb_port_id) ports.add(seg.end_pcb_port_id) }
  traceEndpoints[t.pcb_trace_id] = [...ports]
}
const vias = byType.pcb_via || []
const viaGroups: Record<string, number> = {}
for (const v of vias) {
  const ep = traceEndpoints[v.pcb_trace_id]
  const key = ep ? ep.map(portLabel).sort().join("  <->  ") : "(no-trace)"
  viaGroups[key] = (viaGroups[key] || 0) + 1
}

// module bboxes (copper/holes)
const compF: Record<string, { xs: number[]; ys: number[] }> = {}
const addF = (cid: string, x: number, y: number, hw = 0, hh = 0) => { if (!cid) return; const f = (compF[cid] ||= { xs: [], ys: [] }); f.xs.push(x - hw, x + hw); f.ys.push(y - hh, y + hh) }
for (const h of byType.pcb_plated_hole || []) addF(h.pcb_component_id, h.x, h.y, (h.rect_pad_width || h.hole_diameter) / 2, (h.rect_pad_height || h.hole_diameter) / 2)
for (const h of byType.pcb_hole || []) addF(h.pcb_component_id, h.x, h.y, h.hole_diameter / 2, h.hole_diameter / 2)
for (const p of byType.pcb_smtpad || []) addF(p.pcb_component_id, p.x, p.y, (p.width || 0) / 2, (p.height || 0) / 2)
const pcbComp: Record<string, any> = {}
for (const e of byType.pcb_component || []) pcbComp[e.pcb_component_id] = e
const boxes = Object.entries(compF).map(([cid, f]) => {
  const comp = pcbComp[cid]; const sc = comp ? srcComp[comp.source_component_id] : null
  return { name: sc ? sc.name : cid, x0: Math.min(...f.xs), y0: Math.min(...f.ys), x1: Math.max(...f.xs), y1: Math.max(...f.ys), cx: comp?.center.x ?? 0, cy: comp?.center.y ?? 0, rot: comp?.rotation ?? 0 }
})
const cx0 = Math.min(...boxes.map((b) => b.x0)), cx1 = Math.max(...boxes.map((b) => b.x1))
const cy0 = Math.min(...boxes.map((b) => b.y0)), cy1 = Math.max(...boxes.map((b) => b.y1))

// silk extent (connector/module outlines — what the board edge must clear)
let sx0 = 1e9, sx1 = -1e9, sy0 = 1e9, sy1 = -1e9
for (const e of c) if (/silkscreen/.test(e.type)) for (const p of e.route || []) { sx0 = Math.min(sx0, p.x); sx1 = Math.max(sx1, p.x); sy0 = Math.min(sy0, p.y); sy1 = Math.max(sy1, p.y) }

// realized clearance: trace<->trace and trace<->pad/via, different nets, per layer
type Seg = { x1: number; y1: number; x2: number; y2: number; w: number; net: string; layer: string }
const segs: Seg[] = []
// A manual <pcbtrace> (clean-pass copper) carries no connection_name and no port-ids
// on its route, so its own landing pads would read as foreign-net overlaps. Tie each
// such trace and the two pads its endpoints sit on to one synthetic net (as the core
// carve patch ties them by the same endpoint match), so they're same-net here.
const padAt = (x: number, y: number) => (byType.pcb_plated_hole || []).find((p: any) => Math.abs(p.x - x) < 0.06 && Math.abs(p.y - y) < 0.06)
const cpNetByTrace: Record<string, string> = {}
const cpPortNet: Record<string, string> = {}
for (const t of byType.pcb_trace || []) {
  if (t.connection_name) continue
  const w = (t.route || []).filter((p: any) => p.route_type === "wire" && typeof p.x === "number")
  if (w.length < 2) continue
  const cp = `cp_${t.pcb_trace_id}`
  cpNetByTrace[t.pcb_trace_id] = cp
  for (const end of [w[0], w[w.length - 1]]) { const pad = padAt(end.x, end.y); if (pad) cpPortNet[pad.pcb_port_id] = cp }
}
for (const t of byType.pcb_trace || []) { const r = t.route || []; for (let i = 0; i + 1 < r.length; i++) { const a = r[i], b = r[i + 1]; if (a.layer !== b.layer) continue; segs.push({ x1: a.x, y1: a.y, x2: b.x, y2: b.y, w: a.width || 0.2, net: t.connection_name || cpNetByTrace[t.pcb_trace_id], layer: a.layer }) } }
const portNet: Record<string, string> = { ...cpPortNet }
for (const t of byType.pcb_trace || []) for (const s of t.route || []) { if (s.start_pcb_port_id && t.connection_name) portNet[s.start_pcb_port_id] = t.connection_name; if (s.end_pcb_port_id && t.connection_name) portNet[s.end_pcb_port_id] = t.connection_name }
const circs: { x: number; y: number; r: number; net: string; layers: string[] }[] = []
for (const p of byType.pcb_plated_hole || []) circs.push({ x: p.x, y: p.y, r: Math.max(p.rect_pad_width || 0, p.rect_pad_height || 0, p.hole_diameter || 0) / 2, net: portNet[p.pcb_port_id] || `pad_${p.pcb_plated_hole_id}`, layers: p.layers || ["top", "bottom"] })
// vias are copper too — a trace passing another net's via is a real clearance pinch
for (const v of vias) circs.push({ x: v.x, y: v.y, r: (v.outer_diameter || 0.3) / 2, net: (byType.pcb_trace || []).find((t: any) => t.pcb_trace_id === v.pcb_trace_id)?.connection_name || `via_${v.pcb_via_id}`, layers: v.layers || ["top", "bottom"] })
const ptSeg = (px: number, py: number, s: Seg) => { const dx = s.x2 - s.x1, dy = s.y2 - s.y1, L2 = dx * dx + dy * dy || 1e-9; let t = ((px - s.x1) * dx + (py - s.y1) * dy) / L2; t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (s.x1 + t * dx), py - (s.y1 + t * dy)) }
const segSeg = (a: Seg, b: Seg) => Math.min(ptSeg(a.x1, a.y1, b), ptSeg(a.x2, a.y2, b), ptSeg(b.x1, b.y1, a), ptSeg(b.x2, b.y2, a))
let minTT = Infinity, ttInfo = "", minTP = Infinity, tpInfo = ""
for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) { const a = segs[i], b = segs[j]; if (a.layer !== b.layer || a.net === b.net) continue; const g = segSeg(a, b) - a.w / 2 - b.w / 2; if (g < minTT) { minTT = g; ttInfo = `@${a.layer} ~(${a.x1.toFixed(1)},${a.y1.toFixed(1)})` } }
for (const s of segs) for (const p of circs) { if (!p.layers.includes(s.layer) || p.net === s.net) continue; const g = ptSeg(p.x, p.y, s) - p.r - s.w / 2; if (g < minTP) { minTP = g; tpInfo = `@${s.layer} (${p.x.toFixed(1)},${p.y.toFixed(1)})` } }

const errTypes = Object.keys(byType).filter((k) => /error/.test(k))
const board0 = (byType.pcb_board || [])[0]
const w0 = segs[0]?.w
console.log(`# ${board}  —  vias: ${vias.length}   unrouted-pins: ${(byType.source_pin_missing_trace_warning || []).length}`)
console.log(`board declared: ${board0?.width} x ${board0?.height} mm  (center ${JSON.stringify(board0?.center)})`)
console.log(`content bbox:   ${(cx1 - cx0).toFixed(1)} x ${(cy1 - cy0).toFixed(1)} mm   [x ${cx0.toFixed(1)}..${cx1.toFixed(1)}  y ${cy0.toFixed(1)}..${cy1.toFixed(1)}]`)
console.log(`silk extent:    x ${sx0.toFixed(1)}..${sx1.toFixed(1)}  y ${sy0.toFixed(1)}..${sy1.toFixed(1)}`)
console.log(errTypes.length ? errTypes.map((et) => `DRC ${et}: ${byType[et].length}`).join("\n") : `DRC errors: 0`)
console.log(`realized clearance: trace-trace ${minTT.toFixed(3)} mm ${ttInfo} | trace-pad ${minTP.toFixed(3)} mm ${tpInfo}  (trace w=${w0})`)

// ---- pour coverage: a copper pour carries every pad on its net, so the autorouter
// skips those nets (no traces, no vias). That makes the pour the ONLY connection for
// those pads — nothing in the routed-trace DRC checks it. So we check it here: every
// pad whose net is poured must sit in filled copper (inside the pour's outer ring and
// outside every carve-out ring). A pad in a gap is a floating island — a real break.
const ufN: Record<string, string> = {}
const findN = (x: string): string => { ufN[x] ??= x; let r = x; while (ufN[r] !== r) r = ufN[r]; while (ufN[x] !== r) { const n = ufN[x]; ufN[x] = r; x = n } return r }
for (const t of byType.source_trace || []) { const ids = [...(t.connected_source_port_ids || []), ...(t.connected_source_net_ids || [])]; for (let i = 1; i < ids.length; i++) ufN[findN(ids[0])] = findN(ids[i]) }
const padRep = (pid: string): string | null => { const o = pcbPort[pid]; return o ? findN(o.source_port_id) : null }
const inPoly = (x: number, y: number, vs: any[]): boolean => { let inside = false; for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) { const xi = vs[i].x, yi = vs[i].y, xj = vs[j].x, yj = vs[j].y; if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside } return inside }
const inPour = (x: number, y: number, pour: any): boolean => { if (!inPoly(x, y, pour.brep_shape.outer_ring.vertices)) return false; for (const r of pour.brep_shape.inner_rings || []) if (inPoly(x, y, r.vertices)) return false; return true }
const pads = [...(byType.pcb_plated_hole || []), ...(byType.pcb_smtpad || [])]
// A net can pour as several disconnected fragments; a pad is carried if ANY
// fragment of its net covers it. Group pours by net, then test each pad once.
const poursByRep: Record<string, any[]> = {}
for (const pour of byType.pcb_copper_pour || []) (poursByRep[findN(pour.source_net_id)] ||= []).push(pour)
let pourPads = 0; const uncovered: string[] = []
for (const h of pads) {
  if (!h.pcb_port_id) continue
  const rep = padRep(h.pcb_port_id); const ps = rep && poursByRep[rep]; if (!ps) continue
  pourPads++
  if (!ps.some((pour) => inPour(h.x, h.y, pour))) uncovered.push(`${portLabel(h.pcb_port_id)} @(${h.x.toFixed(1)},${h.y.toFixed(1)}) ${ps[0].layer}`)
}
console.log(`pour coverage: ${pourPads} poured-net pads, ${uncovered.length} uncovered${uncovered.length ? "  ⚠ FLOATING — pour does not reach these" : ""}`)
for (const u of uncovered) console.log(`  ✗ ${u}`)

// ---- trace loops: a declared trace whose two ends are ALREADY joined some other
// way closes a loop. Such loops are invisible at the raw-trace level because each
// socketed module bonds its own same-named pins internally (all VCC together, all
// GND — including the ESP's GNDb/GNDc — together, the DS3231's bridged bus). So we
// collapse those per U-module from a NAME rule, not a hand-kept wiring table:
// within a `U<n>` component, pins with the same name are one node and any /^gnd/
// name folds to GND. Then union-find the declared source_traces; whichever trace
// closes a loop is its loop members. On a SIGNAL net a loop is removable waste; on
// a power/ground net (isPwr) it's an intentional parallel path — a multi-tie or a
// plane stitch — so the two are reported apart. Connectors/nets stay per-pad. Zero
// upkeep: a new U-module or connector is classified by its name automatically.
const spLabel = (spid: string) => {
  const sp = srcPort[spid]; if (!sp) return spid
  const comp = srcComp[sp.source_component_id]
  return `${comp ? comp.name : "?"}.${sp.name}`
}
const bridgeNode = (label: string) => {
  const dot = label.indexOf("."); if (dot < 0) return label // a net node (net.X)
  const hdr = label.slice(0, dot), pin = label.slice(dot + 1)
  const m = hdr.match(/^(U\d+)/); if (!m) return label // connector pin — not bonded
  return `${m[1]}#${/^gnd/i.test(pin) ? "GND" : pin}`
}
// A loop on a power/ground net is a parallel path (extra tie or a plane stitch),
// not waste — it routes cleaner and shares current. Only signal-net loops are
// removable, so a loop is judged by the kind of net it closes.
const isPwr = (n: string) => /(?:[.#]|^net\.)(gnd|vcc|v5|v12|3v3)\b/i.test(n)
const uf: Record<string, string> = {}
const find = (x: string): string => { uf[x] ??= x; let r = x; while (uf[r] !== r) r = uf[r]; while (uf[x] !== r) { const n = uf[x]; uf[x] = r; x = n } return r }
const tadj: Record<string, { to: string; name: string }[]> = {}
const loops: { members: string[]; pwr: boolean }[] = []
for (const t of byType.source_trace || []) {
  const ns = [...(t.connected_source_port_ids || []).map(spLabel).map(bridgeNode), ...(t.connected_source_net_ids || [])]
  if (ns.length < 2) continue
  const name = t.display_name || t.source_trace_id
  const [a, b] = ns
  if (find(a) === find(b)) {
    const prev: Record<string, { from: string; name: string } | null> = { [a]: null }
    const q = [a]
    while (q.length) { const x = q.shift()!; if (x === b) break; for (const e of tadj[x] || []) if (!(e.to in prev)) { prev[e.to] = { from: x, name: e.name }; q.push(e.to) } }
    const members = [name]; let cur = b
    while (prev[cur]) { members.push(prev[cur]!.name); cur = prev[cur]!.from }
    loops.push({ members, pwr: isPwr(a) })
  } else { uf[find(a)] = find(b); (tadj[a] ??= []).push({ to: b, name }); (tadj[b] ??= []).push({ to: a, name }) }
}
const removable = loops.filter((l) => !l.pwr), pwrLoops = loops.filter((l) => l.pwr)
console.log(`removable redundant traces: ${removable.length}${removable.length ? "  (signal loop — one trace in each is removable)" : ""}`)
for (const l of removable) console.log(`  ! loop: ${l.members.join("  +  ")}`)
if (pwrLoops.length) console.log(`power/ground parallel paths: ${pwrLoops.length} (intentional — multi-tie / plane stitch, not removable)`)
for (const l of pwrLoops) console.log(`  ~ ${l.members.join("  +  ")}`)
console.log(`\n## vias by net (total ${vias.length})`)
for (const [k, n] of Object.entries(viaGroups).sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(3)}  ${k}`)
console.log(`\n## modules`)
for (const b of boxes.sort((a, b) => a.name.localeCompare(b.name))) console.log(`  ${b.name.padEnd(5)} c=(${b.cx.toFixed(1)},${b.cy.toFixed(1)}) r${b.rot}  bbox ${(b.x1 - b.x0).toFixed(1)}x${(b.y1 - b.y0).toFixed(1)}  x[${b.x0.toFixed(1)},${b.x1.toFixed(1)}] y[${b.y0.toFixed(1)},${b.y1.toFixed(1)}]`)
