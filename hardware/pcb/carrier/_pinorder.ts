/**
 * _pinorder.ts — for each JST trunk connector, compare its declared pin sequence
 * against the position order of the pads it routes to. A connector whose pins run
 * opposite to their target pads forces every wire to cross — and the autorouter
 * pays for each crossing in vias. Prints the current label order, the target pad
 * each pin routes to (with the target's x/y), and the order the pins WOULD take if
 * sorted by target position along the connector's own axis.
 *
 *   bun _pinorder.ts [board]
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"
import path from "node:path"

const board = process.argv[2] || "mini"
const tmp = `.${board}.pinorder.json`
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
const compName = (sid: string) => srcComp[sid]?.name || "?"
const label = (pid: string) => { const pp = pcbPort[pid]; const sp = pp && srcPort[pp.source_port_id]; return sp ? `${compName(sp.source_component_id)}.${sp.name}` : pid }

// net union-find (pins + nets)
const P: Record<string, string> = {}, find = (x: string): string => { P[x] ??= x; return P[x] === x ? x : (P[x] = find(P[x])) }, uni = (a: string, b: string) => { P[find(a)] = find(b) }
for (const t of byType.source_trace || []) { const ids = [...(t.connected_source_port_ids || []), ...(t.connected_source_net_ids || [])]; for (let i = 1; i < ids.length; i++) uni(ids[0], ids[i]) }
const repOfPort = (pid: string) => { const pp = pcbPort[pid]; return pp ? find(pp.source_port_id) : null }

// poured nets (GND/V12) — pins on these have no single routing target
const sn: Record<string, any> = {}; for (const e of byType.source_net || []) sn[e.source_net_id] = e
const pouredReps = new Set<string>()
for (const e of byType.source_net || []) if (/^(GND|V12)$/i.test(e.name)) pouredReps.add(find(e.source_net_id))

// pcb_port position by id
const ppos: Record<string, { x: number; y: number }> = {}
for (const pp of byType.pcb_port || []) ppos[pp.pcb_port_id] = { x: pp.x, y: pp.y }

// connectors = source_components named J*
const conns = (byType.source_component || []).filter((sc) => /^J\d+$/.test(sc.name)).map((sc) => sc.name).sort((a, b) => +a.slice(1) - +b.slice(1))
const pcbComp: Record<string, any> = {}; for (const e of byType.pcb_component || []) pcbComp[e.pcb_component_id] = e

for (const cn of conns) {
  const sc = (byType.source_component || []).find((s) => s.name === cn)!
  // this connector's pcb_ports
  const myPorts = (byType.pcb_port || []).filter((pp) => { const sp = srcPort[pp.source_port_id]; return sp && sp.source_component_id === sc.source_component_id })
  if (!myPorts.length) continue
  // axis: connector runs along x or y? whichever spans more
  const xs = myPorts.map((p) => p.x), ys = myPorts.map((p) => p.y)
  const spanX = Math.max(...xs) - Math.min(...xs), spanY = Math.max(...ys) - Math.min(...ys)
  const axis = spanX >= spanY ? "x" : "y"
  // order pins along the connector axis
  const rowSorted = [...myPorts].sort((a, b) => (axis === "x" ? a.x - b.x : a.y - b.y))
  const rows: string[] = []
  for (const pp of rowSorted) {
    const rep = repOfPort(pp.pcb_port_id)
    const lbl = label(pp.pcb_port_id).split(".")[1]
    if (rep && pouredReps.has(rep)) { rows.push(`${lbl.padEnd(7)} -> (plane)`); continue }
    // target pad = other module pad on this net
    const targets = (byType.pcb_port || []).filter((q) => q.pcb_port_id !== pp.pcb_port_id && repOfPort(q.pcb_port_id) === rep && /^U\d/.test(label(q.pcb_port_id)))
    if (!targets.length) { rows.push(`${lbl.padEnd(7)} -> (none)`); continue }
    const t = targets[0]
    rows.push(`${lbl.padEnd(7)} -> ${label(t.pcb_port_id).padEnd(10)} @(${t.x.toFixed(1)},${t.y.toFixed(1)})  [${axis === "x" ? t.x.toFixed(1) : t.y.toFixed(1)}]`)
  }
  // ideal order: sort connector signal pins by target coord along the SAME axis
  const withT = rowSorted.map((pp) => {
    const rep = repOfPort(pp.pcb_port_id)
    const lbl = label(pp.pcb_port_id).split(".")[1]
    if (rep && pouredReps.has(rep)) return { lbl, key: null as number | null }
    const targets = (byType.pcb_port || []).filter((q) => q.pcb_port_id !== pp.pcb_port_id && repOfPort(q.pcb_port_id) === rep && /^U\d/.test(label(q.pcb_port_id)))
    return { lbl, key: targets.length ? (axis === "x" ? targets[0].x : targets[0].y) : null }
  })
  const signalPins = withT.filter((p) => p.key != null).sort((a, b) => (a.key! - b.key!))
  const pc = pcbComp[(byType.pcb_component || []).find((p) => p.source_component_id === sc.source_component_id)?.pcb_component_id]
  console.log(`\n=== ${cn}  axis=${axis}  rot=${(byType.pcb_component || []).find((p) => p.source_component_id === sc.source_component_id)?.rotation}  center≈(${(xs.reduce((a, b) => a + b) / xs.length).toFixed(1)},${(ys.reduce((a, b) => a + b) / ys.length).toFixed(1)}) ===`)
  console.log("  current order (pin1->N along axis):")
  for (const r of rows) console.log("    " + r)
  console.log("  signal pins sorted by target " + axis + ": " + signalPins.map((p) => p.lbl).join(", "))
}
