/**
 * clean-pass.ts — a second-pass router for the runs the capacity autorouter
 * leaves ugly. The autorouter routes everything; the nets named in a SPEC are
 * carved out of it (a <pcbtrace> covering a connection's two pads makes the core
 * patch skip that connection — see patches/@tscircuit%2Fcore) and replaced with a
 * clean route this script computes from a geometric RULE.
 *
 * Each rule reads real pad coordinates from a fresh circuit-json export, so the
 * geometry tracks placement — move J7 or U3 and the routes follow. The output is
 * a block of <pcbtrace> JSX to paste into the board between the carved <trace>s.
 *
 *   bun clean-pass.ts [board=mini]
 *
 * RULES
 *   fanRowToColumn — a colinear row of source pads to a colinear column of target
 *   pads under a monotonic pin mapping (rightmost source -> topmost target, …).
 *   Each net is a vertical riser + one 45° segment landing on its pin: zero vias,
 *   one layer, and — because the riser and the diagonal nest by the monotonic
 *   order — provably crossing-free. Corner height per net is ty-(sx-tx), which
 *   puts the final segment at exactly 45° onto the pad.
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"

const board = process.argv[2] || "mini"
const tmp = `.${board}.cleanpass.json`
execFileSync("node_modules/.bin/tsci", ["export", "-f", "circuit-json", "-o", tmp, `${board}.tsx`], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmp, "utf8")) as any[]
rmSync(tmp, { force: true })

const sp: any = {}, pp: any = {}, sc: any = {}
for (const e of c) {
  if (e.type === "source_port") sp[e.source_port_id] = e
  if (e.type === "pcb_port") pp[e.pcb_port_id] = e
  if (e.type === "source_component") sc[e.source_component_id] = e
}
// pad center by "<Comp>.<pin>" selector, read from the plated holes (through-hole)
const pads: Record<string, { x: number; y: number }> = {}
for (const h of c.filter((e) => e.type === "pcb_plated_hole")) {
  const p = pp[h.pcb_port_id]; if (!p) continue
  const o = sp[p.source_port_id]; if (!o) continue
  pads[`${sc[o.source_component_id].name}.${o.name}`] = { x: +h.x.toFixed(3), y: +h.y.toFixed(3) }
}
const pad = (sel: string) => {
  const p = pads[sel]; if (!p) throw new Error(`no pad for ${sel}`); return p
}

type Pair = { from: string; to: string }
const wire = (x: number, y: number, w: number, layer: string) =>
  `{route_type:"wire",x:${+x.toFixed(3)},y:${+y.toFixed(3)},width:${w},layer:"${layer}"}`

/**
 * Row(source) -> Column(target) clean fan. `pairs` are {from,to} pin selectors
 * already in the intended mapping order. width/layer tune the copper.
 */
function fanRowToColumn(pairs: Pair[], opts: { layer?: string; width?: number } = {}) {
  const layer = opts.layer ?? "top", width = opts.width ?? 0.2
  const pts = pairs.map((p) => ({ ...p, s: pad(p.from), t: pad(p.to) }))
  // monotonic-nesting sanity: sources and targets must be co-monotone (a fan that
  // doesn't self-cross). Sort by source-x and confirm target ordering agrees.
  const byX = [...pts].sort((a, b) => a.s.x - b.s.x)
  const tY = byX.map((p) => p.t.y)
  const mono = tY.every((y, i) => i === 0 || y >= tY[i - 1]) || tY.every((y, i) => i === 0 || y <= tY[i - 1])
  if (!mono) console.error("// WARN: target order is not monotone in source-x — fan may cross")
  const blocks: string[] = []
  for (const { from, to, s, t } of pts) {
    const cornerY = t.y - Math.sign(t.y - s.y) * Math.abs(s.x - t.x) // 45° final segment lands on pad
    const route = [wire(s.x, s.y, width, layer), wire(s.x, cornerY, width, layer), wire(t.x, t.y, width, layer)]
    blocks.push(`    {/* ${from} -> ${to} */}\n    <pcbtrace route={[\n      ${route.join(",\n      ")},\n    ]} />`)
  }
  return blocks.join("\n")
}

// ── SPEC: J7 reeds -> U3B GPB inputs (rightmost J7 pin -> topmost GPB) ──────────
const J7_REEDS: Pair[] = [
  { from: "J7.RB1", to: "U3B.GPB0" },
  { from: "J7.RB2", to: "U3B.GPB1" },
  { from: "J7.RB3", to: "U3B.GPB2" },
  { from: "J7.RB4", to: "U3B.GPB3" },
  { from: "J7.CARBLO", to: "U3B.GPB4" },
  { from: "J7.CARBHI", to: "U3B.GPB5" },
]

console.log(fanRowToColumn(J7_REEDS, { layer: "top", width: 0.2 }))
