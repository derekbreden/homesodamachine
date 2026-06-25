/**
 * _route.ts — a tiny 2-layer maze router for hand-routing ONE net the autorouter
 * packs too tight. Exports a fresh circuit-json (the target net's <trace> must be
 * absent so the autorouter has placed everything else), rasterizes every other
 * net's copper + pads into a 2-layer occupancy grid with a clearance halo, then
 * BFS-finds a top/bottom path (vias to switch layer) from the start pad to the
 * goal pad. Prints a <pcbtrace> route array.
 *
 *   bun _route.ts <startX> <startY> <goalX> <goalY> <keepNetSubstr>
 * keepNetSubstr: a string both pads' labels share (e.g. "IO18") so the router
 * knows which copper is the net's own (not an obstacle).
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"

const [sx, sy, gx, gy] = process.argv.slice(2, 6).map(Number)
const keep = process.argv[6] || ""
const tmp = ".route.json"
execFileSync("node_modules/.bin/tsci", ["export", "-f", "circuit-json", "-o", tmp, "mini.tsx"], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmp, "utf8")) as any[]
rmSync(tmp, { force: true })

const sp: any = {}, pp: any = {}, sc: any = {}
for (const e of c) { if (e.type === "source_port") sp[e.source_port_id] = e; if (e.type === "pcb_port") pp[e.pcb_port_id] = e; if (e.type === "source_component") sc[e.source_component_id] = e }
const label = (pid: string) => { const p = pp[pid]; const o = p && sp[p.source_port_id]; return o ? `${sc[o.source_component_id].name}.${o.name}` : "" }

const CELL = 0.2, CLR = +process.argv[11] || 0.18 // grid + min copper-edge clearance target
// bounds default to the driver corridor; override via argv 7-10 for other regions
const X0 = +process.argv[7] || -36, X1 = +process.argv[8] || -11, Y0 = +process.argv[9] || -48, Y1 = +process.argv[10] || -12
const NX = Math.ceil((X1 - X0) / CELL), NY = Math.ceil((Y1 - Y0) / CELL)
const gxi = (x: number) => Math.round((x - X0) / CELL), gyi = (y: number) => Math.round((y - Y0) / CELL)
const occ = [new Uint8Array(NX * NY), new Uint8Array(NX * NY)] // 0=top,1=bottom
const idx = (gx: number, gy: number) => gy * NX + gx
const inb = (gx: number, gy: number) => gx >= 0 && gx < NX && gy >= 0 && gy < NY

// stamp a disc of occupied cells of radius r (mm) around (x,y) on the given layers
const stamp = (x: number, y: number, r: number, layers: number[]) => {
  const rc = Math.ceil(r / CELL), cx = gxi(x), cy = gyi(y)
  for (let dy = -rc; dy <= rc; dy++) for (let dx = -rc; dx <= rc; dx++) {
    if (Math.hypot(dx, dy) * CELL > r) continue
    const X = cx + dx, Y = cy + dy; if (!inb(X, Y)) continue
    for (const L of layers) occ[L][idx(X, Y)] = 1
  }
}
const layerOf = (l: string) => (l === "bottom" ? 1 : 0)

// obstacles: every OTHER net's trace segments (sampled) + pads + vias
let segObs = 0
for (const t of c.filter((e) => e.type === "pcb_trace")) {
  const ports = new Set<string>(); for (const s of t.route || []) for (const k of ["start_pcb_port_id", "end_pcb_port_id"] as const) if (s[k]) ports.add(label(s[k]))
  if ([...ports].some((p) => p.includes(keep))) continue // the net's own copper
  const r = t.route || []
  for (let i = 0; i + 1 < r.length; i++) {
    const a = r[i], b = r[i + 1]; if (a.layer !== b.layer) continue
    const L = layerOf(a.layer), w = (a.width || 0.2) / 2, halo = w + 0.15 + CLR
    const n = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / (CELL / 2)))
    for (let s = 0; s <= n; s++) { stamp(a.x + (b.x - a.x) * s / n, a.y + (b.y - a.y) * s / n, halo, [L]); segObs++ }
  }
}
for (const h of c.filter((e) => e.type === "pcb_plated_hole")) {
  if (label(h.pcb_port_id).includes(keep)) continue
  stamp(h.x, h.y, Math.max(h.rect_pad_width || 0, h.hole_diameter || 0) / 2 + 0.15 + CLR, [0, 1])
}
for (const v of c.filter((e) => e.type === "pcb_via")) stamp(v.x, v.y, (v.outer_diameter || 0.3) / 2 + 0.15 + CLR, [0, 1])

// BFS from start to goal over (cell, layer); via toggles layer (small cost via Dijkstra-ish on uniform+via)
const S = { x: gxi(sx), y: gyi(sy), l: layerOf("top") }, G = { x: gxi(gx), y: gyi(gy) }
// clear start/goal discs (their own pads may have stamped neighbours)
for (const P of [[sx, sy], [gx, gy]]) { const rc = 2; for (let dy = -rc; dy <= rc; dy++) for (let dx = -rc; dx <= rc; dx++) { const X = gxi(P[0]) + dx, Y = gyi(P[1]) + dy; if (inb(X, Y)) { occ[0][idx(X, Y)] = 0; occ[1][idx(X, Y)] = 0 } } }
const key = (x: number, y: number, l: number) => (l * NY + y) * NX + x
const prev = new Map<number, number>(), dist = new Map<number, number>()
const startK = key(S.x, S.y, S.l); dist.set(startK, 0)
const pq: [number, number, number, number][] = [[0, S.x, S.y, S.l]]
const VIA = 8 // via cost (in cells) to discourage excess vias
let found: [number, number, number] | null = null
while (pq.length) {
  pq.sort((a, b) => a[0] - b[0]); const [d, x, y, l] = pq.shift()!
  if (d > (dist.get(key(x, y, l)) ?? 1e9)) continue
  if (x === G.x && y === G.y) { found = [x, y, l]; break }
  const moves: [number, number, number, number][] = [[x + 1, y, l, 1], [x - 1, y, l, 1], [x, y + 1, l, 1], [x, y - 1, l, 1], [x, y, 1 - l, VIA]]
  for (const [nx, ny, nl, cost] of moves) {
    if (!inb(nx, ny) || occ[nl][idx(nx, ny)]) continue
    const nk = key(nx, ny, nl), nd = d + cost
    if (nd < (dist.get(nk) ?? 1e9)) { dist.set(nk, nd); prev.set(nk, key(x, y, l)); pq.push([nd, nx, ny, nl]) }
  }
}
if (!found) { console.error("NO PATH FOUND — loosen CLR or widen bounds"); process.exit(1) }

// reconstruct + simplify (keep vertices where direction or layer changes)
const path: [number, number, number][] = []
let k: number | undefined = key(found[0], found[1], found[2])
while (k !== undefined) { const l = Math.floor(k / (NX * NY)), rem = k % (NX * NY); path.push([rem % NX, Math.floor(rem / NX), l]); k = prev.get(k) }
path.reverse()
const out: any[] = []
const ax = (gx: number) => +(X0 + gx * CELL).toFixed(2), ay = (gy: number) => +(Y0 + gy * CELL).toFixed(2)
for (let i = 0; i < path.length; i++) {
  const [px, py, pl] = path[i], lname = pl === 1 ? "bottom" : "top"
  const prevP = path[i - 1], nextP = path[i + 1]
  const layerChange = prevP && prevP[2] !== pl
  const dirChange = prevP && nextP && (Math.sign(px - prevP[0]) !== Math.sign(nextP[0] - px) || Math.sign(py - prevP[1]) !== Math.sign(nextP[1] - py))
  if (layerChange) { out.push({ route_type: "via", x: ax(px), y: ay(py), from_layer: prevP[2] === 1 ? "bottom" : "top", to_layer: lname }); out.push({ route_type: "wire", x: ax(px), y: ay(py), width: 0.3, layer: lname }) }
  else if (i === 0 || i === path.length - 1 || dirChange) out.push({ route_type: "wire", x: ax(px), y: ay(py), width: 0.3, layer: lname })
}
// snap exact endpoints
out[0].x = sx; out[0].y = sy; out[out.length - 1].x = gx; out[out.length - 1].y = gy
console.log(`// ${out.filter((o) => o.route_type === "via").length} vias, ${out.length} pts`)
console.log(out.map((o) => "      " + JSON.stringify(o).replace(/"(\w+)":/g, "$1: ")).join(",\n"))
