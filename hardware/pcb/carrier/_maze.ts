/**
 * _maze.ts — the obstacle-aware second-pass router. Where clean-pass.ts's fan rule
 * needs an empty corridor, this threads a clean octilinear (H/V/45°) route through a
 * field of pads, traces, and vias — the "more intelligence" for congested cases.
 *
 *   bun _maze.ts
 *
 * It builds the obstacle field by exporting mini.tsx with the target nets' <trace>s
 * removed (so the autorouter places everything else as it will once these are
 * carved), rasterizes every other net's copper + every pad/via into a per-layer
 * occupancy grid with a clearance halo, then routes each target net with an
 * 8-direction A* (diagonals cost √2, corner-cutting forbidden, vias costed high so
 * they appear only when a layer change is genuinely needed). Each routed net joins
 * the obstacle field for the next. Output is <pcbtrace> JSX for mini.tsx; the core
 * carve patch drops these connections from the autorouter (the <trace> stays the
 * netlist). Edit SPEC for a different case.
 */
import { execFileSync } from "node:child_process"
import { readFileSync, writeFileSync, rmSync } from "node:fs"

// ── SPEC: which connections to maze-route, in routing order (hardest first helps) ──
const SPEC = {
  board: "mini",
  // each: from/to pin selectors (for the temp <trace> removal + start/goal pads)
  pairs: [
    { from: "J6.RA1", to: "U2B.GPB0" },
    { from: "J6.RA2", to: "U2B.GPB1" },
    { from: "J6.RA3", to: "U2B.GPB2" },
    { from: "J6.RA4", to: "U2B.GPB3" },
  ],
  region: { x0: 2, x1: 21, y0: 20, y1: 44 }, // routing window (mm), padded internally
  cell: 0.1,        // grid pitch (mm)
  clr: 0.25,        // min copper-edge clearance to other nets (mm)
  width: 0.2,       // drawn trace width (mm)
  viaCost: 60,      // in cells — high so a via only appears when unavoidable
  startLayer: "top",
  turn: 12,        // turn penalty (cells) — higher = straighter, fewer segments
}

// ── export the obstacle board: mini.tsx with the SPEC nets' <trace>s removed ──
const src = readFileSync(`${SPEC.board}.tsx`, "utf8")
let stripped = src
for (const { from, to } of SPEC.pairs) {
  const fa = from.replace(".", " > ."), ta = to.replace(".", " > .")
  const re = new RegExp(`\\s*<trace from="\\.${fa.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}" to="\\.${ta.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}" />`, "g")
  stripped = stripped.replace(re, "")
}
const tmpTsx = `._maze_obstacles.tsx`, tmpJson = `._maze_obstacles.json`
writeFileSync(tmpTsx, stripped)
execFileSync("node_modules/.bin/tsci", ["export", "-f", "circuit-json", "-o", tmpJson, tmpTsx], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmpJson, "utf8")) as any[]
rmSync(tmpTsx, { force: true }); rmSync(tmpJson, { force: true })
rmSync(`.${tmpTsx.slice(1).replace(/\.tsx$/, "")}.circuit.json`, { force: true })

const sp: any = {}, pp: any = {}, sc: any = {}
for (const e of c) {
  if (e.type === "source_port") sp[e.source_port_id] = e
  if (e.type === "pcb_port") pp[e.pcb_port_id] = e
  if (e.type === "source_component") sc[e.source_component_id] = e
}
const label = (pid: string) => { const p = pp[pid]; const o = p && sp[p.source_port_id]; return o ? `${sc[o.source_component_id].name}.${o.name}` : "" }
const pads: Record<string, { x: number; y: number; r: number; port: string }> = {}
for (const h of c.filter((e) => e.type === "pcb_plated_hole")) {
  const l = label(h.pcb_port_id); if (!l) continue
  pads[l] = { x: h.x, y: h.y, r: Math.max(h.outer_diameter || 0, h.rect_pad_width || 0, h.rect_pad_height || 0, h.hole_diameter || 0) / 2, port: h.pcb_port_id }
}

// ── occupancy grid (per layer) ──
const { x0, x1, y0, y1 } = SPEC.region, CELL = SPEC.cell
const NX = Math.ceil((x1 - x0) / CELL) + 1, NY = Math.ceil((y1 - y0) / CELL) + 1
const LAYERS = ["top", "bottom"]
const occ = LAYERS.map(() => new Uint8Array(NX * NY))
const gx = (x: number) => Math.round((x - x0) / CELL), gy = (y: number) => Math.round((y - y0) / CELL)
const ax = (i: number) => x0 + i * CELL, ay = (j: number) => y0 + j * CELL
const idx = (i: number, j: number) => j * NX + i
const inb = (i: number, j: number) => i >= 0 && i < NX && j >= 0 && j < NY
const HALF = SPEC.width / 2

const stampDisc = (x: number, y: number, r: number, layers: number[]) => {
  const rc = Math.ceil(r / CELL), ci = gx(x), cj = gy(y)
  for (let dj = -rc; dj <= rc; dj++) for (let di = -rc; di <= rc; di++) {
    if (Math.hypot(di, dj) * CELL > r) continue
    const i = ci + di, j = cj + dj; if (inb(i, j)) for (const L of layers) occ[L][idx(i, j)] = 1
  }
}
const stampCapsule = (xa: number, ya: number, xb: number, yb: number, r: number, L: number) => {
  const n = Math.max(1, Math.ceil(Math.hypot(xb - xa, yb - ya) / (CELL / 2)))
  for (let s = 0; s <= n; s++) stampDisc(xa + (xb - xa) * s / n, ya + (yb - ya) * s / n, r, [L])
}

// own pads of the nets we route — never treat these as obstacles
const ownPorts = new Set<string>()
for (const { from, to } of SPEC.pairs) { for (const sel of [from, to]) { const p = pads[sel]; if (p) ownPorts.add(p.port) } }

const layerOf = (l: string) => Math.max(0, LAYERS.indexOf(l))
// pads / plated holes (block both layers — through-hole)
for (const h of c.filter((e) => e.type === "pcb_plated_hole")) {
  if (ownPorts.has(h.pcb_port_id)) continue
  stampDisc(h.x, h.y, Math.max(h.outer_diameter || 0, h.rect_pad_width || 0, h.rect_pad_height || 0, h.hole_diameter || 0) / 2 + SPEC.clr + HALF, [0, 1])
}
// non-plated holes (mounting holes) — copper must clear them on both layers
for (const h of c.filter((e) => e.type === "pcb_hole")) stampDisc(h.x, h.y, (h.hole_diameter || 0) / 2 + SPEC.clr + HALF, [0, 1])
// vias (both layers)
for (const v of c.filter((e) => e.type === "pcb_via")) stampDisc(v.x, v.y, (v.outer_diameter || 0.3) / 2 + SPEC.clr + HALF, [0, 1])
// other-net trace segments (per layer)
for (const t of c.filter((e) => e.type === "pcb_trace")) {
  const r = t.route || []
  for (let i = 0; i + 1 < r.length; i++) {
    const a = r[i], b = r[i + 1]; if (a.route_type !== "wire" || b.route_type !== "wire" || a.layer !== b.layer) continue
    stampCapsule(a.x, a.y, b.x, b.y, (a.width || 0.2) / 2 + SPEC.clr + HALF, layerOf(a.layer))
  }
}

// ── octile A* over (i, j, layer, dir) with a turn penalty ──
// dir is the move index taken to ENTER the cell (8 = none/start/post-via). Charging
// a turn when the next move's direction differs makes A* prefer long straight runs,
// so the path comes out as a few clean H/V/45° segments instead of grid stairs.
const SQ2 = Math.SQRT2
const TURN = SPEC.turn ?? 12
const moves = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, SQ2], [1, -1, SQ2], [-1, 1, SQ2], [-1, -1, SQ2]]
const NXY = NX * NY
function route(sx: number, sy: number, gxm: number, gym: number, sLayer: number) {
  const S = { i: gx(sx), j: gy(sy), l: sLayer }, G = { i: gx(gxm), j: gy(gym) }
  for (const [px, py] of [[sx, sy], [gxm, gym]]) {
    const ci = gx(px), cj = gy(py)
    for (let dj = -2; dj <= 2; dj++) for (let di = -2; di <= 2; di++) { const i = ci + di, j = cj + dj; if (inb(i, j)) { occ[0][idx(i, j)] = 0; occ[1][idx(i, j)] = 0 } }
  }
  const key = (i: number, j: number, l: number, d: number) => ((l * 9 + d) * NY + j) * NX + i
  const h = (i: number, j: number) => { const di = Math.abs(i - G.i), dj = Math.abs(j - G.j); return (di + dj) + (SQ2 - 2) * Math.min(di, dj) }
  const dist = new Map<number, number>(), prev = new Map<number, number>()
  const free = (i: number, j: number, l: number) => inb(i, j) && !occ[l][idx(i, j)]
  const startK = key(S.i, S.j, S.l, 8); dist.set(startK, 0)
  // binary heap of [f, g, key]
  const heap: [number, number, number][] = [[h(S.i, S.j), 0, startK]]
  const push = (f: number, g: number, k: number) => { heap.push([f, g, k]); let c = heap.length - 1; while (c > 0) { const p = (c - 1) >> 1; if (heap[p][0] <= heap[c][0]) break;[heap[p], heap[c]] = [heap[c], heap[p]]; c = p } }
  const pop = () => { const top = heap[0], last = heap.pop()!; if (heap.length) { heap[0] = last; let p = 0; for (; ;) { let s = p, l = 2 * p + 1, r = l + 1; if (l < heap.length && heap[l][0] < heap[s][0]) s = l; if (r < heap.length && heap[r][0] < heap[s][0]) s = r; if (s === p) break;[heap[p], heap[s]] = [heap[s], heap[p]]; p = s } } return top }
  const unpack = (k: number) => { const i = k % NX, j = Math.floor(k / NX) % NY, ld = Math.floor(k / NXY); return [i, j, ld % 9, Math.floor(ld / 9)] as const }
  let found: number | null = null
  while (heap.length) {
    const [, g, k] = pop()
    const [i, j, d, l] = unpack(k)
    if (g > (dist.get(k) ?? Infinity) + 1e-9) continue
    if (i === G.i && j === G.j) { found = k; break }
    for (let m = 0; m < 8; m++) {
      const [di, dj, cost] = moves[m]
      const ni = i + di, nj = j + dj
      if (!free(ni, nj, l)) continue
      if (di !== 0 && dj !== 0 && (!free(i + di, j, l) || !free(i, j + dj, l))) continue
      const nd = g + cost + (d !== 8 && d !== m ? TURN : 0)
      const nk = key(ni, nj, l, m)
      if (nd < (dist.get(nk) ?? Infinity)) { dist.set(nk, nd); prev.set(nk, k); push(nd + h(ni, nj), nd, nk) }
    }
    const ol = 1 - l
    if (free(i, j, ol)) { const nk = key(i, j, ol, d), nd = g + SPEC.viaCost; if (nd < (dist.get(nk) ?? Infinity)) { dist.set(nk, nd); prev.set(nk, k); push(nd + h(i, j), nd, nk) } }
  }
  if (found == null) return null
  const path: [number, number, number][] = []
  let k: number | undefined = found
  while (k !== undefined) { const [i, j, , l] = unpack(k); path.push([i, j, l]); k = prev.get(k) }
  path.reverse()
  return path
}

// add a routed path to the obstacle field so later nets avoid it
const addPathObstacle = (path: [number, number, number][]) => {
  for (let i = 0; i + 1 < path.length; i++) {
    const [pi, pj, pl] = path[i], [qi, qj, ql] = path[i + 1]
    if (pl === ql) stampCapsule(ax(pi), ay(pj), ax(qi), ay(qj), HALF + SPEC.clr + HALF, pl)
    else stampDisc(ax(pi), ay(pj), 0.3 + SPEC.clr + HALF, [0, 1]) // a via lands on both layers
  }
}

// emit a pcbtrace route (circuit-json wire/via points), simplified at turns/layer changes
function emit(from: string, to: string, path: [number, number, number][], sx: number, sy: number, gxm: number, gym: number) {
  const out: string[] = []
  const W = SPEC.width
  const pt = (x: number, y: number, l: number) => `{route_type:"wire",x:${+x.toFixed(3)},y:${+y.toFixed(3)},width:${W},layer:"${LAYERS[l]}"}`
  const via = (x: number, y: number, fl: number, tl: number) => `{route_type:"via",x:${+x.toFixed(3)},y:${+y.toFixed(3)},from_layer:"${LAYERS[fl]}",to_layer:"${LAYERS[tl]}"}`
  for (let n = 0; n < path.length; n++) {
    const [pi, pj, pl] = path[n], prevP = path[n - 1], nextP = path[n + 1]
    const layerChange = prevP && prevP[2] !== pl
    const dirChange = prevP && nextP && (Math.sign(pi - prevP[0]) !== Math.sign(nextP[0] - pi) || Math.sign(pj - prevP[1]) !== Math.sign(nextP[1] - pj))
    if (layerChange) { out.push(via(ax(pi), ay(pj), prevP[2], pl)); out.push(pt(ax(pi), ay(pj), pl)) }
    else if (n === 0 || n === path.length - 1 || dirChange) out.push(pt(ax(pi), ay(pj), pl))
  }
  // snap endpoints exactly onto the pads
  out[0] = pt(sx, sy, path[0][2]); out[out.length - 1] = pt(gxm, gym, path[path.length - 1][2])
  const vias = out.filter((o) => o.includes('"via"')).length
  console.log(`    {/* ${from} -> ${to} — ${vias} via${vias === 1 ? "" : "s"} */}`)
  console.log(`    <pcbtrace route={[\n      ${out.join(",\n      ")},\n    ]} />`)
}

for (const { from, to } of SPEC.pairs) {
  const s = pads[from], g = pads[to]
  if (!s || !g) { console.error(`// missing pad ${from} or ${to}`); continue }
  const path = route(s.x, s.y, g.x, g.y, layerOf(SPEC.startLayer))
  if (!path) { console.error(`// NO PATH ${from} -> ${to}`); continue }
  addPathObstacle(path)
  emit(from, to, path, s.x, s.y, g.x, g.y)
}
