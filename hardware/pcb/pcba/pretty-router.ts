/**
 * pretty-router.ts — the in-process 2nd-pass routers. Pure functions: given an
 * obstacle circuit-json (the board with the target nets NOT yet routed), the net
 * pairs to route, and params, they return clean octilinear routes plus helpers to
 * render those as <pcbtrace> JSX or as circuit-json pcb_trace entities.
 *
 * NO file or child-process I/O — the caller supplies the circuit-json (render-board
 * mid-build, or the thin _maze.ts / clean-pass.ts CLI shells). This is the routing
 * core extracted from _maze.ts so the 2nd pass can run as a real BUILD stage keyed
 * to live geometry, instead of being snapshotted into frozen coordinates pasted
 * into the board .tsx. See conversion-plan.md.
 */

export type RoutePoint =
  | { route_type: "wire"; x: number; y: number; width: number; layer: string }
  | { route_type: "via"; x: number; y: number; from_layer: string; to_layer: string }

export type RoutedNet = { from: string; to: string; route: RoutePoint[]; vias: number }

export type FanType = "fanRowToColumn" | "fanColumnToColumn"

export type MazeSpec = {
  cell: number; clr: number; width: number; viaCost: number
  startLayer: string; turn?: number
  // A* search window. Optional: when omitted (fan style) it is derived from the
  // nets' own pads + their ideal-fan extents, padded by `margin` (mm, default 3).
  region?: { x0: number; x1: number; y0: number; y1: number }
  margin?: number
  // Routing style. "maze" (default) = free obstacle-aware A*. "fan" = the SAME
  // obstacle-aware A*, but biased toward a clean perpendicular-riser + 45° landing
  // (`fanType` sets the riser axis): an empty corridor yields the tidy fan, while a
  // blocked one dips to the other layer (via) or detours instead of shorting.
  style?: "maze" | "fan"
  fanType?: FanType
}

// The ideal clean-fan polyline (riser + 45° landing) between two pads — geometry
// only, used to size the fan's search window and to bias the A* toward the tidy
// shape. fanRowToColumn risers run on Y (row source); fanColumnToColumn on X.
export function idealFanPts(s: { x: number; y: number }, t: { x: number; y: number }, fanType: FanType): { x: number; y: number }[] {
  if (fanType === "fanRowToColumn") {
    const cy = t.y - Math.sign(t.y - s.y) * Math.abs(s.x - t.x)
    return [s, { x: s.x, y: cy }, t]
  }
  const cx = t.x - Math.sign(t.x - s.x) * Math.abs(s.y - t.y)
  return [s, { x: cx, y: s.y }, t]
}

// pad keep-out radius: a disc that covers the whole pad. For a rectangular pad use
// the half-DIAGONAL (its corner reach), or a 45° trace clips the corner the disc misses.
const padR = (h: any) => {
  const w = h.rect_pad_width || 0, ht = h.rect_pad_height || 0
  const rectR = (w || ht) ? Math.hypot(w, ht) / 2 : 0
  return Math.max((h.outer_diameter || 0) / 2, rectR, (h.hole_diameter || 0) / 2)
}

// Obstacle-aware A* router. Routes each pair through the field implied by `circuit`
// (every other net's copper + every pad/via, with a clearance halo), threading clean
// H/V/45° runs and costing vias high so they appear only when a layer change is needed.
// Each routed net joins the obstacle field for the next.
export function mazeRouteNets(circuit: any[], pairs: { from: string; to: string }[], spec: MazeSpec): RoutedNet[] {
  const c = circuit, SPEC = spec
  const sp: any = {}, pp: any = {}, sc: any = {}
  for (const e of c) {
    if (e.type === "source_port") sp[e.source_port_id] = e
    if (e.type === "pcb_port") pp[e.pcb_port_id] = e
    if (e.type === "source_component") sc[e.source_component_id] = e
  }
  const label = (pid: string) => { const p = pp[pid]; const o = p && sp[p.source_port_id]; return o ? `${sc[o.source_component_id].name}.${o.name}` : "" }
  const pads: Record<string, { x: number; y: number; r: number; port: string; layers: number[] }> = {}
  for (const h of c.filter((e) => e.type === "pcb_plated_hole")) {
    const l = label(h.pcb_port_id); if (!l) continue
    pads[l] = { x: h.x, y: h.y, r: padR(h), port: h.pcb_port_id, layers: [0, 1] }
  }
  // SMD pads can be maze endpoints too (the bare WROOM's IO pins). A plated hole connects
  // every layer; an SMD pad is single-layer, so the route must begin/end on that pad's
  // layer — a barrel-free via brings a bottom run up to a top pad just before it lands.
  // THT wins a name clash (it reaches all layers).
  for (const s of c.filter((e) => e.type === "pcb_smtpad")) {
    const l = label(s.pcb_port_id); if (!l || pads[l]) continue
    pads[l] = { x: s.x, y: s.y, r: padR(s), port: s.pcb_port_id, layers: [s.layer === "bottom" ? 1 : 0] }
  }

  // ── occupancy grid (per layer) ──
  // Region: explicit (maze groups carry a tuned window), else derived from this
  // call's own pads + their ideal-fan extents, padded by `margin` so the A* has
  // room to detour/via around an obstacle (fan style).
  let REGION = SPEC.region
  if (!REGION) {
    const pts: { x: number; y: number }[] = []
    for (const { from, to } of pairs) {
      const a = pads[from], b = pads[to]
      if (a) pts.push(a)
      if (b) pts.push(b)
      if (SPEC.style === "fan" && SPEC.fanType && a && b) pts.push(...idealFanPts(a, b, SPEC.fanType))
    }
    if (!pts.length) throw new Error("[route] no region and no resolvable pads to derive one from")
    const m = SPEC.margin ?? 3
    REGION = {
      x0: Math.min(...pts.map((p) => p.x)) - m, x1: Math.max(...pts.map((p) => p.x)) + m,
      y0: Math.min(...pts.map((p) => p.y)) - m, y1: Math.max(...pts.map((p) => p.y)) + m,
    }
  }
  const { x0, x1, y0, y1 } = REGION, CELL = SPEC.cell
  const NX = Math.ceil((x1 - x0) / CELL) + 1, NY = Math.ceil((y1 - y0) / CELL) + 1
  const LAYERS = ["top", "bottom"]
  const occ = LAYERS.map(() => new Uint8Array(NX * NY))
  const gx = (x: number) => Math.round((x - x0) / CELL), gy = (y: number) => Math.round((y - y0) / CELL)
  const ax = (i: number) => x0 + i * CELL, ay = (j: number) => y0 + j * CELL
  const idx = (i: number, j: number) => j * NX + i
  const inb = (i: number, j: number) => i >= 0 && i < NX && j >= 0 && j < NY
  const HALF = SPEC.width / 2

  // via drill keep-out grid: a via's DRILL can't sit within hole-to-hole spacing of any
  // other hole (pad, mounting hole, via) — overlapping drills are unfabbable. Unlike the
  // per-net pad exemption (which lets a TRACE reach its endpoint), this blocks a VIA even at
  // the route's own start/goal hole, so a via never lands on the through-hole it leaves from.
  const viaOcc = new Uint8Array(NX * NY)
  const VIAHOLER = 0.15, HOLEGAP = 0.45
  const stampViaKO = (x: number, y: number, holeR: number) => {
    const r = holeR + VIAHOLER + HOLEGAP, rc = Math.ceil(r / CELL), ci = gx(x), cj = gy(y)
    for (let dj = -rc; dj <= rc; dj++) for (let di = -rc; di <= rc; di++) {
      if (Math.hypot(di, dj) * CELL > r) continue
      const i = ci + di, j = cj + dj; if (inb(i, j)) viaOcc[idx(i, j)] = 1
    }
  }

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
  // stamp a (possibly rotated) rectangle + margin on ONE layer — used for SMD pads,
  // whose true rectangle must be marked (the half-diagonal disc the plated-hole path
  // uses swallows the narrow channels beside a big pad, e.g. the 10 mm coin contact).
  const stampRectLayer = (cx: number, cy: number, w: number, h: number, rot: number, m: number, L: number) => {
    const hw = w / 2 + m, hh = h / 2 + m
    const rad = (rot || 0) * Math.PI / 180, cos = Math.cos(rad), sin = Math.sin(rad)
    const R = Math.hypot(hw, hh), rc = Math.ceil(R / CELL), ci = gx(cx), cj = gy(cy)
    for (let dj = -rc; dj <= rc; dj++) for (let di = -rc; di <= rc; di++) {
      const i = ci + di, j = cj + dj; if (!inb(i, j)) continue
      const X = ax(i) - cx, Y = ay(j) - cy
      const lx = X * cos + Y * sin, ly = -X * sin + Y * cos
      if (Math.abs(lx) <= hw && Math.abs(ly) <= hh) occ[L][idx(i, j)] = 1
    }
  }

  const clearDisc = (x: number, y: number, r: number, layers: number[]) => {
    const rc = Math.ceil(r / CELL), ci = gx(x), cj = gy(y)
    for (let dj = -rc; dj <= rc; dj++) for (let di = -rc; di <= rc; di++) {
      if (Math.hypot(di, dj) * CELL > r) continue
      const i = ci + di, j = cj + dj; if (inb(i, j)) for (const L of layers) occ[L][idx(i, j)] = 0
    }
  }
  const layerOf = (l: string) => Math.max(0, LAYERS.indexOf(l))
  // EVERY pad/plated hole is an obstacle (block both layers — through-hole). A route
  // clears only ITS OWN two pads while routing, then re-stamps them — so a trace for
  // one net never runs through another net's pad even when both share an ESP column.
  for (const h of c.filter((e) => e.type === "pcb_plated_hole")) stampDisc(h.x, h.y, padR(h) + SPEC.clr + HALF, [0, 1])
  // non-plated holes (mounting holes) — copper must clear them on both layers
  for (const h of c.filter((e) => e.type === "pcb_hole")) stampDisc(h.x, h.y, (h.hole_diameter || 0) / 2 + SPEC.clr + HALF, [0, 1])
  // vias (both layers)
  for (const v of c.filter((e) => e.type === "pcb_via")) stampDisc(v.x, v.y, (v.outer_diameter || 0.3) / 2 + SPEC.clr + HALF, [0, 1])
  // via drill keep-out around every hole (incl. this route's own endpoints) and existing via
  for (const h of c.filter((e) => e.type === "pcb_plated_hole")) stampViaKO(h.x, h.y, (h.hole_diameter || h.hole_width || 0.6) / 2)
  for (const h of c.filter((e) => e.type === "pcb_hole")) stampViaKO(h.x, h.y, (h.hole_diameter || 0) / 2)
  for (const v of c.filter((e) => e.type === "pcb_via")) stampViaKO(v.x, v.y, (v.hole_diameter || 0.3) / 2)
  // other-net trace segments (per layer)
  for (const t of c.filter((e) => e.type === "pcb_trace")) {
    const r = t.route || []
    for (let i = 0; i + 1 < r.length; i++) {
      const a = r[i], b = r[i + 1]; if (a.route_type !== "wire" || b.route_type !== "wire" || a.layer !== b.layer) continue
      stampCapsule(a.x, a.y, b.x, b.y, (a.width || 0.2) / 2 + SPEC.clr + HALF, layerOf(a.layer))
    }
  }
  // SMD pads (single layer): a top pad blocks only top copper (a route can pass under
  // it on the bottom layer); the coin-cell VBAT contact (10 mm) + clip pads sit right
  // in the J5 corridor, so this keeps a signal from shorting across them.
  for (const s of c.filter((e) => e.type === "pcb_smtpad")) {
    const L = layerOf(s.layer)
    if (s.shape === "circle") { stampDisc(s.x, s.y, (s.radius || 0) + SPEC.clr + HALF, [L]); continue }
    const w = s.width || 0, h = s.height || 0; if (!w || !h) continue
    stampRectLayer(s.x, s.y, w, h, s.ccw_rotation || 0, SPEC.clr + HALF, L)
  }

  // ── octile A* over (i, j, layer, dir) with a turn penalty ──
  // dir is the move index taken to ENTER the cell (8 = none/start/post-via). Charging
  // a turn when the next move's direction differs makes A* prefer long straight runs,
  // so the path comes out as a few clean H/V/45° segments instead of grid stairs.
  const SQ2 = Math.SQRT2
  const TURN = SPEC.turn ?? 12
  const FAN_OFFPATH = 4 // per-cell penalty for straying off the ideal-fan corridor (fan style)
  const moves = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, SQ2], [1, -1, SQ2], [-1, 1, SQ2], [-1, -1, SQ2]]
  const NXY = NX * NY

  // Mark the ideal-fan corridor (riser + 45° polyline, ±halo cells) into a cell mask, so
  // the A* can be biased to hug it. Cells outside the mask cost FAN_OFFPATH extra.
  const markPreferred = (pts: { x: number; y: number }[], halo = 2): Uint8Array => {
    const mask = new Uint8Array(NX * NY)
    const mark = (x: number, y: number) => { const ci = gx(x), cj = gy(y); for (let dj = -halo; dj <= halo; dj++) for (let di = -halo; di <= halo; di++) { const i = ci + di, j = cj + dj; if (inb(i, j)) mask[idx(i, j)] = 1 } }
    for (let s = 0; s + 1 < pts.length; s++) {
      const a = pts[s], b = pts[s + 1], n = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / (CELL / 2)))
      for (let q = 0; q <= n; q++) mark(a.x + (b.x - a.x) * q / n, a.y + (b.y - a.y) * q / n)
    }
    return mask
  }

  function route(sx: number, sy: number, gxm: number, gym: number, startLayers: number[], goalLayers: number[], preferred?: Uint8Array | null) {
    const S = { i: gx(sx), j: gy(sy) }, G = { i: gx(gxm), j: gy(gym) }
    for (const [px, py] of [[sx, sy], [gxm, gym]]) {
      const ci = gx(px), cj = gy(py)
      for (let dj = -2; dj <= 2; dj++) for (let di = -2; di <= 2; di++) { const i = ci + di, j = cj + dj; if (inb(i, j)) { occ[0][idx(i, j)] = 0; occ[1][idx(i, j)] = 0 } }
    }
    const key = (i: number, j: number, l: number, d: number) => ((l * 9 + d) * NY + j) * NX + i
    const h = (i: number, j: number) => { const di = Math.abs(i - G.i), dj = Math.abs(j - G.j); return (di + dj) + (SQ2 - 2) * Math.min(di, dj) }
    const dist = new Map<number, number>(), prev = new Map<number, number>()
    const free = (i: number, j: number, l: number) => inb(i, j) && !occ[l][idx(i, j)]
    // a via drops a real pad (~0.25mm radius) on BOTH layers; obstacles are stamped only
    // to trace-half (HALF) clearance, so a minimally-free cell leaves the wider via pad too
    // close to neighbouring copper. Require the extra pad ring (beyond HALF) clear, both layers.
    const VIAR = Math.max(0, 0.25 - HALF), vrc = Math.ceil(VIAR / CELL)
    const viaClear = (i: number, j: number) => { for (let dj = -vrc; dj <= vrc; dj++) for (let di = -vrc; di <= vrc; di++) { if (Math.hypot(di, dj) * CELL > VIAR) continue; if (!free(i + di, j + dj, 0) || !free(i + di, j + dj, 1)) return false } return true }
    // A through-hole endpoint connects EVERY layer (startLayers/goalLayers = [top,bottom]),
    // so a route may BEGIN on either copper layer with no via — the barrel is the layer
    // change. An SMD endpoint is one layer, so its set is just that layer. A tiny epsilon
    // biases to the preferred startLayer so a clean route stays there on a tie.
    // binary heap of [f, g, key]
    const pref = layerOf(SPEC.startLayer)
    const heap: [number, number, number][] = []
    for (const sl of startLayers) { const sk = key(S.i, S.j, sl, 8), c0 = sl === pref ? 0 : 1e-3; dist.set(sk, c0); heap.push([h(S.i, S.j) + c0, c0, sk]) }
    const push = (f: number, g: number, k: number) => { heap.push([f, g, k]); let c = heap.length - 1; while (c > 0) { const p = (c - 1) >> 1; if (heap[p][0] <= heap[c][0]) break;[heap[p], heap[c]] = [heap[c], heap[p]]; c = p } }
    const pop = () => { const top = heap[0], last = heap.pop()!; if (heap.length) { heap[0] = last; let p = 0; for (; ;) { let s = p, l = 2 * p + 1, r = l + 1; if (l < heap.length && heap[l][0] < heap[s][0]) s = l; if (r < heap.length && heap[r][0] < heap[s][0]) s = r; if (s === p) break;[heap[p], heap[s]] = [heap[s], heap[p]]; p = s } } return top }
    const unpack = (k: number) => { const i = k % NX, j = Math.floor(k / NX) % NY, ld = Math.floor(k / NXY); return [i, j, ld % 9, Math.floor(ld / 9)] as const }
    let found: number | null = null
    while (heap.length) {
      const [, g, k] = pop()
      const [i, j, d, l] = unpack(k)
      if (g > (dist.get(k) ?? Infinity) + 1e-9) continue
      if (i === G.i && j === G.j && goalLayers.includes(l)) { found = k; break }
      for (let m = 0; m < 8; m++) {
        const [di, dj, cost] = moves[m]
        const ni = i + di, nj = j + dj
        if (!free(ni, nj, l)) continue
        if (di !== 0 && dj !== 0 && (!free(i + di, j, l) || !free(i, j + dj, l))) continue
        const nd = g + cost + (d !== 8 && d !== m ? TURN : 0) + (preferred && !preferred[idx(ni, nj)] ? FAN_OFFPATH : 0)
        const nk = key(ni, nj, l, m)
        if (nd < (dist.get(nk) ?? Infinity)) { dist.set(nk, nd); prev.set(nk, k); push(nd + h(ni, nj), nd, nk) }
      }
      const ol = 1 - l
      if (free(i, j, ol) && !viaOcc[idx(i, j)] && viaClear(i, j)) { const nk = key(i, j, ol, d), nd = g + SPEC.viaCost; if (nd < (dist.get(nk) ?? Infinity)) { dist.set(nk, nd); prev.set(nk, k); push(nd + h(i, j), nd, nk) } }
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

  // turn a grid path into a pcbtrace route (wire/via points), simplified at turns/layer
  // changes, with endpoints snapped exactly onto the pads.
  const W = SPEC.width
  const buildRoute = (path: [number, number, number][], sx: number, sy: number, gxm: number, gym: number): { route: RoutePoint[]; vias: number } => {
    const out: RoutePoint[] = []
    const pt = (x: number, y: number, l: number): RoutePoint => ({ route_type: "wire", x: +x.toFixed(3), y: +y.toFixed(3), width: W, layer: LAYERS[l] })
    const via = (x: number, y: number, fl: number, tl: number): RoutePoint => ({ route_type: "via", x: +x.toFixed(3), y: +y.toFixed(3), from_layer: LAYERS[fl], to_layer: LAYERS[tl] })
    for (let n = 0; n < path.length; n++) {
      const [pi, pj, pl] = path[n], prevP = path[n - 1], nextP = path[n + 1]
      const layerChange = prevP && prevP[2] !== pl
      const dirChange = prevP && nextP && (Math.sign(pi - prevP[0]) !== Math.sign(nextP[0] - pi) || Math.sign(pj - prevP[1]) !== Math.sign(nextP[1] - pj))
      if (layerChange) { out.push(via(ax(pi), ay(pj), prevP[2], pl)); out.push(pt(ax(pi), ay(pj), pl)) }
      else if (n === 0 || n === path.length - 1 || dirChange) out.push(pt(ax(pi), ay(pj), pl))
    }
    // snap endpoints exactly onto the pads
    out[0] = pt(sx, sy, path[0][2]); out[out.length - 1] = pt(gxm, gym, path[path.length - 1][2])
    const vias = out.filter((o) => o.route_type === "via").length
    return { route: out, vias }
  }

  const routed: RoutedNet[] = []
  for (const { from, to } of pairs) {
    const s = pads[from], g = pads[to]
    if (!s || !g) { console.error(`// missing pad ${from} or ${to}`); continue }
    // fan style: bias the A* toward this net's ideal riser+45° corridor (it still
    // detours / vias to dodge copper — that's the whole point of unifying the two).
    const preferred = SPEC.style === "fan" && SPEC.fanType ? markPreferred(idealFanPts(s, g, SPEC.fanType)) : null
    // open this net's own two pads, route, then re-stamp them as obstacles for the rest
    const sr = s.r + SPEC.clr + HALF, gr = g.r + SPEC.clr + HALF
    clearDisc(s.x, s.y, sr, [0, 1]); clearDisc(g.x, g.y, gr, [0, 1])
    const path = route(s.x, s.y, g.x, g.y, s.layers, g.layers, preferred)
    stampDisc(s.x, s.y, sr, [0, 1]); stampDisc(g.x, g.y, gr, [0, 1])
    if (!path) { console.error(`// NO PATH ${from} -> ${to}`); continue }
    addPathObstacle(path)
    routed.push({ from, to, ...buildRoute(path, s.x, s.y, g.x, g.y) })
  }
  return routed
}

// render a routed net as the <pcbtrace> JSX the board files use (CLI output + migration).
export function routedNetToJSX(rn: RoutedNet): string {
  const body = rn.route.map((p) =>
    p.route_type === "wire"
      ? `{route_type:"wire",x:${p.x},y:${p.y},width:${p.width},layer:"${p.layer}"}`
      : `{route_type:"via",x:${p.x},y:${p.y},from_layer:"${p.from_layer}",to_layer:"${p.to_layer}"}`
  ).join(",\n      ")
  return `    {/* ${rn.from} -> ${rn.to} — ${rn.vias} via${rn.vias === 1 ? "" : "s"} */}\n    <pcbtrace route={[\n      ${body},\n    ]} />`
}

// build a circuit-json pcb_trace entity for build-time injection. Passing source_trace_id
// ties the copper to its net (identity preserved) — no coordinate carve needed downstream.
export function routedNetToPcbTrace(rn: RoutedNet, ids: { pcb_trace_id: string; source_trace_id?: string; subcircuit_id?: string }): any {
  return {
    type: "pcb_trace",
    pcb_trace_id: ids.pcb_trace_id,
    route: rn.route,
    ...(ids.source_trace_id ? { source_trace_id: ids.source_trace_id } : {}),
    ...(ids.subcircuit_id ? { subcircuit_id: ids.subcircuit_id } : {}),
  }
}

// "Comp.pin" -> {x,y} from smtpads + plated holes (chips are SMD, JSTs through-hole).
export function cleanPads(circuit: any[]): Record<string, { x: number; y: number }> {
  const sp: any = {}, pp: any = {}, sc: any = {}
  for (const e of circuit) {
    if (e.type === "source_port") sp[e.source_port_id] = e
    if (e.type === "pcb_port") pp[e.pcb_port_id] = e
    if (e.type === "source_component") sc[e.source_component_id] = e
  }
  const pads: Record<string, { x: number; y: number }> = {}
  for (const h of circuit.filter((e) => e.type === "pcb_smtpad" || e.type === "pcb_plated_hole")) {
    const p = pp[h.pcb_port_id]; if (!p) continue
    const o = sp[p.source_port_id]; if (!o) continue
    const nm = o.name || (o.port_hints || []).find((x: string) => !/^\d+$/.test(x))
    if (nm) pads[`${sc[o.source_component_id].name}.${nm}`] = { x: +h.x.toFixed(3), y: +h.y.toFixed(3) }
  }
  return pads
}

// warn (don't fail) if a fan's pin mapping isn't monotone — that's when risers cross.
// axis = source coordinate that's swept; tax = target coordinate that must track it.
export function monoWarn(pairs: { from: string; to: string }[], pads: Record<string, { x: number; y: number }>, axis: "x" | "y", tax: "x" | "y", label: string) {
  const pts = pairs.map((p) => ({ s: pads[p.from], t: pads[p.to] })).filter((p) => p.s && p.t)
  const by = [...pts].sort((a, b) => a.s![axis] - b.s![axis]).map((p) => p.t![tax])
  const up = by.every((v, i) => i === 0 || v >= by[i - 1]!), dn = by.every((v, i) => i === 0 || v <= by[i - 1]!)
  if (!up && !dn) console.error(`[pretty] WARN: ${label} pin mapping non-monotone — fan may cross`)
}
