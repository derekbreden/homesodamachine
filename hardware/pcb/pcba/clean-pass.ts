/**
 * clean-pass.ts — second-pass router for the runs the capacity autorouter leaves
 * ugly. A <pcbtrace> covering a connection's two pads makes the core patch carve
 * that connection out of the autorouter (patches/@tscircuit%2Fcore), so the clean
 * route this script computes is the net's only copper. Routes are derived from a
 * fresh circuit-json export, so geometry tracks placement — move a part, rerun.
 *
 *   bun clean-pass.ts          # prints <pcbtrace> JSX to paste into pcba.tsx
 *
 * RULES (each net = one perpendicular riser + one 45° landing: 0 vias, 1 layer,
 * provably crossing-free under a monotonic pin mapping):
 *   fanRowToColumn    — source on a horizontal row: vertical riser + 45°.
 *   fanColumnToColumn — source on a vertical column: horizontal riser + 45°.
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"

const tmp = ".pcba.cleanpass.json"
execFileSync("node_modules/.bin/tsci", ["export", "-f", "circuit-json", "-o", tmp, "pcba.tsx"], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmp, "utf8")) as any[]
rmSync(tmp, { force: true })

const sp: any = {}, pp: any = {}, sc: any = {}
for (const e of c) {
  if (e.type === "source_port") sp[e.source_port_id] = e
  if (e.type === "pcb_port") pp[e.pcb_port_id] = e
  if (e.type === "source_component") sc[e.source_component_id] = e
}
// pad center by "<Comp>.<pin>" — chips land on pcb_smtpad, JSTs on pcb_plated_hole
const pads: Record<string, { x: number; y: number }> = {}
for (const h of c.filter((e) => e.type === "pcb_smtpad" || e.type === "pcb_plated_hole")) {
  const p = pp[h.pcb_port_id]; if (!p) continue
  const o = sp[p.source_port_id]; if (!o) continue
  const nm = o.name || (o.port_hints || []).find((x: string) => !/^\d+$/.test(x))
  if (nm) pads[`${sc[o.source_component_id].name}.${nm}`] = { x: +h.x.toFixed(3), y: +h.y.toFixed(3) }
}
const pad = (s: string) => { const p = pads[s]; if (!p) throw new Error(`no pad ${s}`); return p }
const wire = (x: number, y: number, w: number, l: string) => `{route_type:"wire",x:${+x.toFixed(3)},y:${+y.toFixed(3)},width:${w},layer:"${l}"}`

type Pair = { from: string; to: string }
const block = (from: string, to: string, route: string[]) =>
  `    {/* ${from} -> ${to} */}\n    <pcbtrace route={[\n      ${route.join(",\n      ")},\n    ]} />`

const monoWarn = (pts: { s: any; t: any }[], axis: "x" | "y", tax: "x" | "y") => {
  const by = [...pts].sort((a, b) => a.s[axis] - b.s[axis]).map((p) => p.t[tax])
  const up = by.every((v, i) => i === 0 || v >= by[i - 1]), dn = by.every((v, i) => i === 0 || v <= by[i - 1])
  if (!up && !dn) console.error(`// WARN: non-monotone mapping — fan may cross`)
}

function fanRowToColumn(pairs: Pair[], o: { layer?: string; width?: number } = {}) {
  const layer = o.layer ?? "top", width = o.width ?? 0.2
  const pts = pairs.map((p) => ({ ...p, s: pad(p.from), t: pad(p.to) }))
  monoWarn(pts, "x", "y")
  return pts.map(({ from, to, s, t }) => {
    const cy = t.y - Math.sign(t.y - s.y) * Math.abs(s.x - t.x)
    if ((cy - s.y) * (t.y - s.y) < 0) console.error(`// WARN: ${from}->${to} riser reverses (|dx| ${Math.abs(s.x - t.x).toFixed(2)} > |dy| ${Math.abs(s.y - t.y).toFixed(2)})`)
    return block(from, to, [wire(s.x, s.y, width, layer), wire(s.x, cy, width, layer), wire(t.x, t.y, width, layer)])
  }).join("\n")
}

function fanColumnToColumn(pairs: Pair[], o: { layer?: string; width?: number } = {}) {
  const layer = o.layer ?? "top", width = o.width ?? 0.2
  const pts = pairs.map((p) => ({ ...p, s: pad(p.from), t: pad(p.to) }))
  monoWarn(pts, "y", "x")
  return pts.map(({ from, to, s, t }) => {
    const cx = t.x - Math.sign(t.x - s.x) * Math.abs(s.y - t.y)
    if ((cx - s.x) * (t.x - s.x) < 0) console.error(`// WARN: ${from}->${to} riser reverses (|dy| ${Math.abs(s.y - t.y).toFixed(2)} > |dx| ${Math.abs(s.x - t.x).toFixed(2)})`)
    return block(from, to, [wire(s.x, s.y, width, layer), wire(cx, s.y, width, layer), wire(t.x, t.y, width, layer)])
  }).join("\n")
}

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]

// ── TOP cluster ────────────────────────────────────────────────────────────
console.log("    {/* GPA -> ULN IN (U2 -> U4): same-pitch parallel diagonal bus */}")
console.log(fanRowToColumn(i8.map((k) => ({ from: `U2.GPA${k}`, to: `U4.IN${8 - k}` }))))
console.log("    {/* REEDS A (J6 -> U2 GPB): converging fan, reordered J6 */}")
console.log(fanRowToColumn([1, 2, 3, 4].map((n) => ({ from: `J6.RA${n}`, to: `U2.GPB${n - 1}` }))))
console.log("    {/* ULN OUT -> MANIFOLD A (U4 -> J1): widening fan */}")
console.log(fanColumnToColumn(i8.map((k) => ({ from: `U4.OUT${k + 1}`, to: `J1.OUT${k + 1}` }))))

// ── BOTTOM cluster (U3 is rot90 — GPA/GPB sit left, mirror-flipped from U2) ───
// GPA is on the side away from U5, so drive the bus from the IN column (source
// spread in y) down-left into the GPA row: knee lands on a clean vertical line.
console.log("    {/* ULN IN -> GPA (U5 -> U3): parallel diagonal bus, knee left of U5 */}")
console.log(fanColumnToColumn(i8.map((k) => ({ from: `U5.IN${8 - k}`, to: `U3.GPA${k}` }))))
console.log("    {/* REEDS B (J7 -> U3 GPB): converging fan, reordered+shifted J7 */}")
console.log(fanRowToColumn([["RB1", 0], ["RB2", 1], ["RB3", 2], ["RB4", 3], ["CLO", 4], ["CHI", 5]].map(([r, g]) => ({ from: `J7.${r}`, to: `U3.GPB${g}` }))))
console.log("    {/* ULN OUT -> MANIFOLD B (U5 -> J2): widening fan */}")
console.log(fanColumnToColumn([["OUT1", "OUT1"], ["OUT2", "OUT2"], ["OUT3", "OUT3"], ["OUT4", "OUT4"], ["OUT5", "FAN"]].map(([o, j]) => ({ from: `U5.${o}`, to: `J2.${j}` }))))
