/**
 * Discrete-copper clearance + genuine-error analysis of a routed circuit-json, for the
 * web viewer's board readout (folded into picks.json by pick-data.ts).
 *
 * FLOOR — the smallest edge-to-edge gap between two pieces of copper that must not run that
 * close: any two DIFFERENT-net shapes on a shared layer. Copper is pads, plated-hole barrels,
 * vias, and trace segments; every
 * shape reduces to a rounded polyline (a rect is 4 zero-radius edges, a pill/circle/via/
 * trace a segment with a radius), so a gap is `min segment-segment distance − r1 − r2`.
 * A plated hole and a through-via are conductive on EVERY copper layer (the barrel), not just
 * the two outer layers where they flash a pad — so a barrel is modelled on all `num_layers`
 * copper layers and is checked against the inner-layer signals that cross it. (This is why the
 * router's post-hoc through-holing needs an honest referee: a barrel re-spanned top<->bottom
 * now shares every inner layer with any trace routed there.) Poured planes stay out of the
 * FLOOR — plane connection is antipad geometry, a separate axis handled by the POUR check.
 * Net identity groups by net NAME first (a plane spans several connectivity keys the pour
 * joins), then connectivity key (one signal net), then unique (unconnected copper). Stitch
 * and mst pcb_traces carry no ports, so their net comes from their source_trace.
 *
 * SHADOW — a pad's footprint is reserved through the ENTIRE stack, not just its own copper layer.
 * On this board the column under a pad is barrel territory: the plane stitcher drops a via-in-pad
 * on every poured-net SMD pad, and pad-via-to-pad-via (routeBottom) is the sanctioned move onto
 * the bottom for signals — so any pad, stitched or not, is one net-assignment or one routeBottom
 * away from being a through-hole. Foreign-net trace copper crossing a pad's projected outline on a
 * layer the pad is NOT on shares no layer with it, so the FLOOR never pairs them — yet it spends
 * the pad's via column and threads the stitch field at fab-floor gaps. Flagged when the trace
 * copper is inside the projection or within the 0.1 mm fab floor of it.
 *
 * POUR — a solid copperpour must not cover foreign-net copper: for every pcb_copper_pour
 * (an outer ring minus its antipad void rings) any discrete copper of a DIFFERENT net whose
 * body lands in the SOLID region is a short (the pour floods it with no antipad). This is the
 * class the outer-layer-only checks were blind to: the copper-pour-solver antipads rects and
 * circles but silently drops pill shapes, so USB-C shield slots and DRV8870 pill pads sit in
 * solid plane copper. Same-net overlap is the intended connection and is skipped.
 *
 * VIA SPAN — JLCPCB standard assembly drills through-holes only. Any pcb_via whose two
 * endpoints are not exactly {top, bottom} is a blind/buried via and is flagged: the router
 * routes multi-layer and every via must end up a full-column through-hole.
 *
 * SLIVER — a poured fragment thinner than the fab's minimum feature width (2·area/perimeter)
 * is a floating acid-trap the pour solver left behind; flagged as a fab risk, not a short.
 *
 * ERRORS — the above, plus the genuine DRC findings filtered out of the pour-blind noise the
 * board carries every render: the "missing a connection to smtpad" trace errors read only direct
 * trace copper, blind to the plane and via paths most nets take, so they drop here — net continuity
 * is judged in full by connectivity.ts. The "via outside the board boundary" placement errors are
 * false (the stitch vias land post-DRC, inside). A third: tscircuit's clearance DRC is rotation-blind
 * — it reads a rotated pill pad as axis-aligned, so a column of imported SOIC/SOP pads reads "0 mm
 * apart" (pad_pad) and a trace cleanly threading past them reads as a contact (pad_trace). Each such
 * error is refereed against this file's own rotation-aware geometry (padGap / padMinClearance) and
 * dropped only when the pad really clears its minimum. What survives is genuine copper overlaps /
 * too-close, courtyard overlaps, and any other placement error.
 */

type Pt = [number, number]
type Kind = "pad" | "via" | "trace"
type Feat = { edges: Pt[][]; r: number; layers: Set<string>; net: string; label: string; kind: Kind; minx: number; maxx: number; miny: number; maxy: number }
// One end of a tight pair, resolvable back to a pickable entity in the viewer: its
// kind + label say what it is, (x, y) is the witness point where it pinches (board
// mm) — a via/pad centre or the point on a trace nearest its neighbour. The viewer
// pans there and selects the entity when the check row is clicked.
export type ClearanceEnd = { kind: Kind; label: string; x: number; y: number }
export type ClearancePair = { gap: number; a: string; b: string; ends: [ClearanceEnd, ClearanceEnd] }
export type BoardError = { kind: string; text: string }
export type ClearanceReport = { floor: number | null; tight: ClearancePair[]; errors: BoardError[] }

const AABB_CAP = 1.5 // skip a pair whose bounding boxes are farther apart than this (mm)
const TIGHT_MAX = 8  // how many of the tightest pairs to keep for the readout
const MIN_FEATURE_WIDTH = 0.1 // fab minimum copper feature width (mm) — thinner pours are slivers
const SLIVER_MAX_AREA = 0.15 // mm² — a thin fragment this small is a floating sliver, not a thin-waisted plane
const ERR_CAP = 24 // cap on how many pour/via findings to keep (dedup + summary handle the rest)
const SHADOW_CLEARANCE = 0.1 // fab min clearance, applied to a pad's through-stack projection (SHADOW)

// A net name is a real signal name unless it's a synthetic id (__u/__t/__v) or a raw
// connectivity key — those read as "signal" in the human-facing readout.
const netLabel = (net: string) => (net.startsWith("__") || /connectivity_net/.test(net) ? "signal" : net)

// The copper layer stack a barrel spans, top→inner→bottom, for a board of `n` layers.
const copperLayers = (n: number): string[] =>
  n <= 2 ? ["top", "bottom"] : ["top", ...Array.from({ length: n - 2 }, (_, i) => `inner${i + 1}`), "bottom"]

// A route's copper as [a, b, layer] segments. A via point carries from_layer/to_layer but no
// `layer`; the copper LEAVING a via runs on its to_layer and the copper ENTERING one on its
// from_layer. Attribute a via-adjacent segment to that layer instead of skipping it — dropping it
// (as an `a.layer !== b.layer` guard did) makes the copper immediately after every via invisible
// to the floor, which is exactly where a manual drop-and-run crosses another net.
const traceSegs = (rt: any[]): [any, any, string][] => {
  const out: [any, any, string][] = []
  for (let i = 0; i + 1 < rt.length; i++) {
    const a = rt[i], b = rt[i + 1]
    if (a.x == null || b.x == null || (a.x === b.x && a.y === b.y)) continue
    const layer = a.route_type === "via" ? a.to_layer : b.route_type === "via" ? a.layer : a.layer === b.layer ? a.layer : null
    if (layer != null) out.push([a, b, layer])
  }
  return out
}

export function analyzeClearance(circuit: any[]): ClearanceReport {
  const boardEl = circuit.find((e) => e.type === "pcb_board")
  const LAYERS = copperLayers(boardEl?.num_layers ?? 2)
  const srcPort: Record<string, any> = {}, pcbPort: Record<string, any> = {}
  const compName: Record<string, string> = {}
  const netByKey: Record<string, string> = {}, netById: Record<string, string> = {}
  const stNet: Record<string, string> = {}
  for (const e of circuit) {
    if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
    else if (e.type === "source_component") compName[e.source_component_id] = e.name
    else if (e.type === "source_net") { netByKey[e.subcircuit_connectivity_map_key] = e.name; netById[e.source_net_id] = e.name }
  }
  for (const e of circuit) if (e.type === "source_trace")
    stNet[e.source_trace_id] = (e.subcircuit_connectivity_map_key && netByKey[e.subcircuit_connectivity_map_key]) || netById[e.connected_source_net_ids?.[0]] || e.subcircuit_connectivity_map_key || ""

  let uniq = 0
  const netName = (pcbPortId?: string): string | null => {
    const sp = pcbPortId && pcbPort[pcbPortId] ? srcPort[pcbPort[pcbPortId].source_port_id] : null
    const k = sp?.subcircuit_connectivity_map_key
    return (k && netByKey[k]) || k || null
  }
  const netOfPort = (pcbPortId?: string) => netName(pcbPortId) || `__u${uniq++}`
  const refPin = (pcbPortId?: string) => {
    const sp = pcbPortId && pcbPort[pcbPortId] ? srcPort[pcbPort[pcbPortId].source_port_id] : null
    return sp ? `${compName[sp.source_component_id] ?? "?"}.${sp.name ?? "?"}` : "?"
  }
  const netOfTrace = (t: any) => {
    const s = t.route.find((r: any) => r.start_pcb_port_id)?.start_pcb_port_id
    const e = t.route.find((r: any) => r.end_pcb_port_id)?.end_pcb_port_id
    if (s) return netOfPort(s)
    if (e) return netOfPort(e)
    return stNet[t.source_trace_id] || stNet[t.connection_name] || `__t${uniq++}`
  }

  const feats: Feat[] = []
  const push = (edges: Pt[][], r: number, layers: string[], net: string, label: string, kind: Kind) => {
    let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity
    for (const e of edges) for (const p of e) { minx = Math.min(minx, p[0]); maxx = Math.max(maxx, p[0]); miny = Math.min(miny, p[1]); maxy = Math.max(maxy, p[1]) }
    feats.push({ edges, r, layers: new Set(layers), net, label, kind, minx: minx - r, maxx: maxx + r, miny: miny - r, maxy: maxy + r })
  }
  const rectEdges = (x: number, y: number, w: number, h: number, deg: number): Pt[][] => {
    const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a)
    const k = [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]].map(([dx, dy]) => [x + dx * c - dy * s, y + dx * s + dy * c] as Pt)
    return [[k[0], k[1]], [k[1], k[2]], [k[2], k[3]], [k[3], k[0]]]
  }
  const seg = (x1: number, y1: number, x2: number, y2: number): Pt[][] => [[[x1, y1], [x2, y2]]]

  for (const e of circuit) {
    if (e.type === "pcb_smtpad") {
      const net = netOfPort(e.pcb_port_id), label = refPin(e.pcb_port_id)
      if (e.shape === "rect") push(rectEdges(e.x, e.y, e.width, e.height, e.ccw_rotation || 0), 0, [e.layer], net, label, "pad")
      else { // pill / rotated_pill — a capsule along its long axis
        const w = e.width, h = e.height, r = e.radius ?? Math.min(w, h) / 2
        const half = Math.max(0, (Math.max(w, h) - 2 * r) / 2)
        const ang = ((h >= w ? 90 : 0) + (e.ccw_rotation || 0)) * Math.PI / 180
        push(seg(e.x - Math.cos(ang) * half, e.y - Math.sin(ang) * half, e.x + Math.cos(ang) * half, e.y + Math.sin(ang) * half), r, [e.layer], net, label, "pad")
      }
    } else if (e.type === "pcb_plated_hole") {
      push(seg(e.x, e.y, e.x, e.y), (e.outer_diameter ?? e.hole_diameter) / 2, LAYERS, netOfPort(e.pcb_port_id), refPin(e.pcb_port_id), "pad")
    }
  }
  const traceNet: Record<string, string> = {}
  for (const e of circuit) if (e.type === "pcb_trace") traceNet[e.pcb_trace_id] = netOfTrace(e)
  for (const e of circuit) if (e.type === "pcb_via") {
    const net = traceNet[e.pcb_trace_id] || `__v${uniq++}`
    push(seg(e.x, e.y, e.x, e.y), e.outer_diameter / 2, LAYERS, net, `via on ${netLabel(net)}`, "via")
  }
  for (const e of circuit) if (e.type === "pcb_trace") {
    const net = traceNet[e.pcb_trace_id] || `__t${uniq++}`
    for (const [a, b, layer] of traceSegs(e.route))
      push(seg(a.x, a.y, b.x, b.y), (a.width ?? b.width ?? 0.2) / 2, [layer], net, `trace on ${netLabel(net)}`, "trace")
  }

  // Min distance between segments p1p2 and p3p4 (handles zero-length = point).
  const segSeg = (p1: Pt, p2: Pt, p3: Pt, p4: Pt) => {
    const d1x = p2[0] - p1[0], d1y = p2[1] - p1[1], d2x = p4[0] - p3[0], d2y = p4[1] - p3[1]
    const rx = p1[0] - p3[0], ry = p1[1] - p3[1]
    const a = d1x * d1x + d1y * d1y, e = d2x * d2x + d2y * d2y, f = d2x * rx + d2y * ry
    const cl = (v: number) => Math.max(0, Math.min(1, v)), E = 1e-12
    let s: number, t: number
    if (a <= E && e <= E) return Math.hypot(rx, ry)
    if (a <= E) { s = 0; t = cl(f / e) }
    else { const c = d1x * rx + d1y * ry; if (e <= E) { t = 0; s = cl(-c / a) } else { const b = d1x * d2x + d1y * d2y, den = a * e - b * b; s = den > E ? cl((b * f - c * e) / den) : 0; t = (b * s + f) / e; if (t < 0) { t = 0; s = cl(-c / a) } else if (t > 1) { t = 1; s = cl((b - c) / a) } } }
    return Math.hypot(p1[0] + d1x * s - (p3[0] + d2x * t), p1[1] + d1y * s - (p3[1] + d2y * t))
  }
  const dist = (A: Feat, B: Feat) => {
    let m = Infinity
    for (const ea of A.edges) for (const eb of B.edges) { const d = segSeg(ea[0], ea[1], eb[0], eb[1]); if (d < m) m = d }
    return m - A.r - B.r
  }
  const shareLayer = (A: Feat, B: Feat) => { for (const l of A.layers) if (B.layers.has(l)) return true; return false }

  // The witness points of the closest edge pair — same s,t solve as segSeg, but
  // keeping the two points so a tight pair can say WHERE it pinches (on the centre-
  // lines; a via/point feature witnesses at its centre). Only run for the handful of
  // pairs kept for the readout, so the extra work is negligible.
  const segSegPts = (p1: Pt, p2: Pt, p3: Pt, p4: Pt) => {
    const d1x = p2[0] - p1[0], d1y = p2[1] - p1[1], d2x = p4[0] - p3[0], d2y = p4[1] - p3[1]
    const rx = p1[0] - p3[0], ry = p1[1] - p3[1]
    const a = d1x * d1x + d1y * d1y, e = d2x * d2x + d2y * d2y, f = d2x * rx + d2y * ry
    const cl = (v: number) => Math.max(0, Math.min(1, v)), E = 1e-12
    let s = 0, t = 0
    if (a <= E && e <= E) { s = 0; t = 0 }
    else if (a <= E) { s = 0; t = cl(f / e) }
    else { const c = d1x * rx + d1y * ry; if (e <= E) { t = 0; s = cl(-c / a) } else { const b = d1x * d2x + d1y * d2y, den = a * e - b * b; s = den > E ? cl((b * f - c * e) / den) : 0; t = (b * s + f) / e; if (t < 0) { t = 0; s = cl(-c / a) } else if (t > 1) { t = 1; s = cl((b - c) / a) } } }
    const ax = p1[0] + d1x * s, ay = p1[1] + d1y * s, bx = p3[0] + d2x * t, by = p3[1] + d2y * t
    return { d: Math.hypot(ax - bx, ay - by), ax, ay, bx, by }
  }
  const nearest = (A: Feat, B: Feat) => {
    let best = { d: Infinity, ax: 0, ay: 0, bx: 0, by: 0 }
    for (const ea of A.edges) for (const eb of B.edges) { const c = segSegPts(ea[0], ea[1], eb[0], eb[1]); if (c.d < best.d) best = c }
    return best
  }
  const endOf = (F: Feat, x: number, y: number): ClearanceEnd => ({ kind: F.kind, label: F.label, x: round(x), y: round(y) })

  // Pad/hole feature keyed by its "Comp.Pin" label (traces/vias carry an "... on <net>" label, so
  // they're excluded). Used to referee the native pad_pad DRC below against this file's rotation-
  // aware geometry: tscircuit's own DRC treats every pill pad as axis-aligned, so a column of
  // rotated pills reads "0 mm apart" when they're really at full pitch. `padGap` returns the true
  // edge-to-edge gap so those false positives can be dropped without hiding a genuinely tight pair.
  const padFeatByLabel: Record<string, Feat> = {}
  for (const f of feats) { if (f.label.includes(" on ")) continue; if (!(f.label in padFeatByLabel)) padFeatByLabel[f.label] = f }
  const padGap = (a: string, b: string): number | null => {
    const A = padFeatByLabel[a], B = padFeatByLabel[b]
    return A && B ? dist(A, B) : null
  }
  // A pad's true worst-case clearance to any foreign-net copper (pad, trace, or via), rotation-
  // aware. If this is >= the DRC minimum, the pad genuinely clears everything, so any native pad-
  // trace "too close" naming it is the same rotated-pill blindness as the pad_pad case — the native
  // check reads a rotated pill as axis-aligned and a cleanly-passing trace as a contact.
  const padMinClearance = (label: string): number | null => {
    const A = padFeatByLabel[label]
    if (!A) return null
    let m = Infinity
    for (const B of feats) { if (B === A || B.net === A.net || !shareLayer(A, B)) continue; const d = dist(A, B); if (d < m) m = d }
    return isFinite(m) ? m : null
  }

  let floor = Infinity
  const pairs: ClearancePair[] = []
  for (let i = 0; i < feats.length; i++) for (let j = i + 1; j < feats.length; j++) {
    const A = feats[i], B = feats[j]
    if (A.net === B.net || !shareLayer(A, B)) continue
    if (A.minx > B.maxx + AABB_CAP || B.minx > A.maxx + AABB_CAP || A.miny > B.maxy + AABB_CAP || B.miny > A.maxy + AABB_CAP) continue
    const d = dist(A, B)
    if (d < floor) floor = d
    if (d < 0.35) {
      const n = nearest(A, B)
      pairs.push({ gap: round(d), a: A.label, b: B.label, ends: [endOf(A, n.ax, n.ay), endOf(B, n.bx, n.by)] })
    }
  }
  pairs.sort((x, y) => x.gap - y.gap)

  // SHADOW (see file header) — foreign-net trace copper crossing a pad's through-stack projection
  // on a layer the pad is not on. Single-layer pad feats only: a plated-hole barrel is real copper
  // on every layer and already lives in the FLOOR. Same-layer approaches are likewise the FLOOR's
  // axis; this pairs exactly what the FLOOR structurally cannot.
  const shadows: { gap: number; text: string }[] = []
  const shadowSeen = new Set<string>()
  for (const P of feats) {
    if (P.kind !== "pad" || P.layers.size !== 1) continue
    for (const T of feats) {
      if (T.kind !== "trace" || T.net === P.net || shareLayer(P, T)) continue
      if (P.minx > T.maxx + SHADOW_CLEARANCE || T.minx > P.maxx + SHADOW_CLEARANCE || P.miny > T.maxy + SHADOW_CLEARANCE || T.miny > P.maxy + SHADOW_CLEARANCE) continue
      const d = dist(P, T)
      if (d >= SHADOW_CLEARANCE) continue
      const key = `${P.label}|${T.net}|${[...T.layers].join()}`
      if (shadowSeen.has(key)) continue
      shadowSeen.add(key)
      shadows.push({ gap: d, text: `Pad shadow — ${T.label} (${[...T.layers].join("/")}) in ${P.label}'s through-stack shadow (${[...P.layers].join("/")} pad, gap ${round(d)} mm)` })
    }
  }
  shadows.sort((a, b) => a.gap - b.gap)
  const shadowErrors: BoardError[] = shadows.slice(0, ERR_CAP).map((s) => ({ kind: "pad-shadow", text: s.text }))
  if (shadows.length > ERR_CAP) shadowErrors.push({ kind: "pad-shadow", text: `…and ${shadows.length - ERR_CAP} more pad-shadow crossings` })

  const errors = [
    ...floatingPadErrors(circuit, netById, netOfPort, refPin, traceNet),
    ...shadowErrors,
    ...pourShortErrors(circuit, LAYERS, netByKey, netById, netOfPort, refPin, netOfTrace, traceNet),
    ...viaSpanErrors(circuit),
    ...sliverErrors(circuit, netById),
    ...genuineErrors(circuit, pcbPort, padGap, padMinClearance),
  ]
  return { floor: isFinite(floor) ? round(floor) : null, tight: pairs.slice(0, TIGHT_MAX), errors }
}

// FLOATING PAD — an SMD pad whose net is poured on a DIFFERENT layer connects to that plane
// only through a stitch via (plane-stitching.md): the pad is copper on one layer, the plane on
// another, and nothing joins them but the via. If that via is missing or bare-netted, the pad
// silently floats — a dead VCC/GND/rail pin — and NO other check sees it (the pour is blind, the
// gerbers look right, DRC passes). So verify the stitch: every poured-net SMD pad not already on
// its plane's layer must have a same-net via landing within it. (A through via spans the whole
// stack, so a via on the pad = a reach to the plane.) This is the referee for the core patch that
// drops those vias — it catches a regression where a pad's stitch goes missing or loses its net.
function floatingPadErrors(
  circuit: any[], netById: Record<string, string>,
  netOfPort: (id?: string) => string, refPin: (id?: string) => string,
  traceNet: Record<string, string>,
): BoardError[] {
  // net name -> the layer its plane/island is poured on
  const pourLayer: Record<string, string> = {}
  for (const e of circuit) if (e.type === "pcb_copper_pour") {
    const net = netById[e.source_net_id]
    if (net && !(net in pourLayer)) pourLayer[net] = e.layer
  }
  if (!Object.keys(pourLayer).length) return []
  // every netted via, as a point (through vias reach every layer, so a via in the pad stitches it)
  const vias: { net: string; x: number; y: number }[] = []
  for (const e of circuit) if (e.type === "pcb_via") {
    const net = traceNet[e.pcb_trace_id]
    if (net) vias.push({ net, x: e.x, y: e.y })
  }
  const bad: string[] = []
  for (const e of circuit) {
    if (e.type !== "pcb_smtpad") continue
    const net = netOfPort(e.pcb_port_id)
    const pl = pourLayer[net]
    if (!pl) continue            // net isn't a poured plane — it connects by trace, not by stitch
    if (e.layer === pl) continue // pad already sits on its plane's layer (e.g. a top V12 pad)
    const hw = (e.width || 0) / 2 + 0.05, hh = (e.height || 0) / 2 + 0.05
    const stitched = vias.some((v) => v.net === net && Math.abs(v.x - e.x) <= hw && Math.abs(v.y - e.y) <= hh)
    if (!stitched) bad.push(`${refPin(e.pcb_port_id)} (${netLabel(net)}) — no stitch via to the ${pl} plane`)
  }
  const out: BoardError[] = []
  for (const b of bad.slice(0, ERR_CAP)) out.push({ kind: "floating-pad", text: `Floating pad — ${b}` })
  if (bad.length > ERR_CAP) out.push({ kind: "floating-pad", text: `…and ${bad.length - ERR_CAP} more floating pads` })
  return out
}

// POUR — a solid copperpour covering foreign-net copper is a short (see file header). For each
// pcb_copper_pour (an outer ring minus its antipad void rings), any discrete copper of a
// different net whose body lands in the solid region gets flagged. Same-net = intended flood.
function pourShortErrors(
  circuit: any[], LAYERS: string[],
  netByKey: Record<string, string>, netById: Record<string, string>,
  netOfPort: (id?: string) => string, refPin: (id?: string) => string,
  netOfTrace: (t: any) => string, traceNet: Record<string, string>,
): BoardError[] {
  type Ring = { pts: Pt[]; minx: number; maxx: number; miny: number; maxy: number }
  type Pour = { layer: string; net: string; outer: Ring; voids: Ring[] }
  const ring = (verts: any[]): Ring => {
    const pts = verts.map((v) => [v.x, v.y] as Pt)
    let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity
    for (const [x, y] of pts) { minx = Math.min(minx, x); maxx = Math.max(maxx, x); miny = Math.min(miny, y); maxy = Math.max(maxy, y) }
    return { pts, minx, maxx, miny, maxy }
  }
  const inRing = (p: Pt, r: Ring) => {
    if (p[0] < r.minx || p[0] > r.maxx || p[1] < r.miny || p[1] > r.maxy) return false
    let inside = false
    for (let i = 0, j = r.pts.length - 1; i < r.pts.length; j = i++) {
      const xi = r.pts[i][0], yi = r.pts[i][1], xj = r.pts[j][0], yj = r.pts[j][1]
      if (((yi > p[1]) !== (yj > p[1])) && p[0] < ((xj - xi) * (p[1] - yi)) / (yj - yi) + xi) inside = !inside
    }
    return inside
  }
  // A point is in a pour's SOLID copper iff inside its outer ring and in none of its voids.
  const inSolid = (p: Pt, pour: Pour) => {
    if (!inRing(p, pour.outer)) return false
    for (const v of pour.voids) if (inRing(p, v)) return false
    return true
  }

  const pours: Pour[] = []
  for (const e of circuit) {
    if (e.type !== "pcb_copper_pour" || !e.brep_shape?.outer_ring?.vertices) continue
    pours.push({
      layer: e.layer,
      net: netById[e.source_net_id] ?? `__pour${e.pcb_copper_pour_id}`,
      outer: ring(e.brep_shape.outer_ring.vertices),
      voids: (e.brep_shape.inner_rings ?? []).map((h: any) => ring(h.vertices)),
    })
  }
  if (!pours.length) return []
  const poursByLayer = new Map<string, Pour[]>()
  for (const p of pours) (poursByLayer.get(p.layer) ?? poursByLayer.set(p.layer, []).get(p.layer)!).push(p)

  // Sample points for a discrete copper feature: enough to catch a body sitting in solid pour
  // (a properly antipadded feature has its whole body inside the pour's void). Center is the
  // strongest signal; add spread so a partial flood is still caught.
  const spread = (cx: number, cy: number, hw: number, hh: number): Pt[] => {
    const out: Pt[] = [[cx, cy]]
    for (const fx of [-0.6, 0.6]) for (const fy of [-0.6, 0.6]) out.push([cx + fx * hw, cy + fy * hh])
    out.push([cx + 0.6 * hw, cy], [cx - 0.6 * hw, cy], [cx, cy + 0.6 * hh], [cx, cy - 0.6 * hh])
    return out
  }

  // (layer, feature) → sample points + net + label, for everything the pours could flood.
  type Feature = { layers: string[]; net: string; label: string; samples: Pt[] }
  const features: Feature[] = []
  for (const e of circuit) {
    if (e.type === "pcb_smtpad") {
      const w = e.width ?? (e.radius ? e.radius * 2 : 0), h = e.height ?? (e.radius ? e.radius * 2 : 0)
      features.push({ layers: [e.layer], net: netOfPort(e.pcb_port_id), label: refPin(e.pcb_port_id), samples: spread(e.x, e.y, w / 2, h / 2) })
    } else if (e.type === "pcb_plated_hole") {
      const w = e.outer_diameter ?? e.rect_pad_width ?? e.hole_width ?? e.hole_diameter ?? 0
      const h = e.outer_height ?? e.rect_pad_height ?? e.hole_height ?? e.hole_diameter ?? w
      features.push({ layers: LAYERS, net: netOfPort(e.pcb_port_id), label: refPin(e.pcb_port_id), samples: spread(e.x, e.y, w / 2, h / 2) })
    } else if (e.type === "pcb_via") {
      const net = traceNet[e.pcb_trace_id] || "signal"
      features.push({ layers: LAYERS, net, label: `via on ${net}`, samples: spread(e.x, e.y, e.outer_diameter / 2, e.outer_diameter / 2) })
    } else if (e.type === "pcb_trace") {
      const net = netOfTrace(e)
      // Sample each segment along its length; a signal crossing a plane rides an antipad void.
      const byLayer = new Map<string, Pt[]>()
      for (const [a, b, layer] of traceSegs(e.route)) {
        const arr = byLayer.get(layer) ?? byLayer.set(layer, []).get(layer)!
        const steps = Math.max(2, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 0.3))
        for (let s = 0; s <= steps; s++) arr.push([a.x + ((b.x - a.x) * s) / steps, a.y + ((b.y - a.y) * s) / steps])
      }
      for (const [layer, samples] of byLayer) features.push({ layers: [layer], net, label: `trace on ${net}`, samples })
    }
  }

  const seen = new Set<string>()
  const found: { text: string; layer: string }[] = []
  for (const f of features) {
    for (const layer of f.layers) {
      for (const pour of poursByLayer.get(layer) ?? []) {
        if (f.net === pour.net) continue // intended connection
        if (!f.samples.some((p) => inSolid(p, pour))) continue
        const key = `${f.label}|${pour.net}|${layer}`
        if (seen.has(key)) continue
        seen.add(key)
        found.push({ text: `${f.label} (${netLabel(f.net)}) covered by the ${pour.net} pour on ${layer}`, layer })
        break // one finding per feature per layer
      }
    }
  }
  const out = found.slice(0, ERR_CAP).map((f) => ({ kind: "pour-short", text: f.text }))
  if (found.length > ERR_CAP) out.push({ kind: "pour-short", text: `…and ${found.length - ERR_CAP} more pour shorts` })
  return out
}

// VIA SPAN — flag any via that is not a full-column through-hole (endpoints {top, bottom}).
function viaSpanErrors(circuit: any[]): BoardError[] {
  const out: BoardError[] = []
  const bad: string[] = []
  for (const e of circuit) {
    if (e.type !== "pcb_via") continue
    const ends = new Set([e.from_layer, e.to_layer].filter(Boolean))
    const through = ends.has("top") && ends.has("bottom") && ends.size === 2
    if (!through) bad.push(`${e.from_layer}↔${e.to_layer} @(${round(e.x)},${round(e.y)})`)
  }
  if (bad.length) {
    for (const b of bad.slice(0, ERR_CAP)) out.push({ kind: "blind-via", text: `Blind/buried via ${b} — JLCPCB drills through-holes only` })
    if (bad.length > ERR_CAP) out.push({ kind: "blind-via", text: `…and ${bad.length - ERR_CAP} more blind/buried vias` })
  }
  return out
}

// SLIVER — a SMALL poured fragment thinner than the fab minimum feature width: a floating
// acid-trap the pour solver pinched off. Thinness proxy is 2·area/perimeter (≈ the half-width
// of a long thin piece). The area gate is what keeps this honest: a plane can legitimately
// have a thin WAIST while being a large connected region (e.g. a 2.4mm SDA fill), so thinness
// alone over-flags — only a piece that is both thin AND small is a genuine sliver.
function sliverErrors(circuit: any[], _netById: Record<string, string>): BoardError[] {
  const out: BoardError[] = []
  let n = 0
  for (const e of circuit) {
    if (e.type !== "pcb_copper_pour" || !e.brep_shape?.outer_ring?.vertices) continue
    const pts: Pt[] = e.brep_shape.outer_ring.vertices.map((v: any) => [v.x, v.y])
    if (pts.length < 3) { n++; continue }
    let area2 = 0, per = 0
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      area2 += pts[j][0] * pts[i][1] - pts[i][0] * pts[j][1]
      per += Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
    }
    const area = Math.abs(area2) / 2
    const width = per > 0 ? Math.abs(area2) / per : 0 // = 2·area/perimeter
    if (width < MIN_FEATURE_WIDTH && area < SLIVER_MAX_AREA) n++
  }
  if (n) out.push({ kind: "sliver", text: `${n} floating pour fragment${n === 1 ? "" : "s"} thinner than ${MIN_FEATURE_WIDTH} mm (acid trap / DFM)` })
  return out
}

// Filter the routed circuit's *_error rows down to the genuine ones (see file header).
function genuineErrors(circuit: any[], pcbPort: Record<string, any>, padGap: (a: string, b: string) => number | null, padMinClearance: (label: string) => number | null): BoardError[] {
  const out: BoardError[] = []
  for (const e of circuit) {
    if (typeof e.type !== "string" || !e.type.endsWith("_error")) continue
    const msg: string = e.message || ""
    if (e.type === "pcb_trace_error") {
      // "missing a connection to smtpad": tscircuit's trace-only reachability, blind to plane/via
      // paths — net continuity is judged in full by connectivity.ts.
      if (/missing a connection to smtpad/.test(msg)) continue
      // "trace ... too close to / overlaps pcb_smtpad [.C > .P]": referee the pad against real geometry.
      const pm = /pcb_smtpad "?pcb_port\[\.(\w+) > \.(\w+)\]"?/.exec(msg)
      if (pm) { const c = padMinClearance(`${pm[1]}.${pm[2]}`); if (c != null && c >= 0.1 - 1e-6) continue }
      out.push({ kind: "overlap", text: msg })
    } else if (e.type === "pcb_pad_pad_clearance_error") {
      // Referee against this file's rotation-aware geometry: tscircuit's DRC treats pill pads as
      // axis-aligned, flagging a column of rotated pills (an imported SOIC/SOP) as "0 mm apart".
      // If padGap says the pair really clears its own minimum, it's that false positive — drop it.
      const ports = [...msg.matchAll(/pcb_port\[\.(\w+) > \.(\w+)\]/g)].map((m) => `${m[1]}.${m[2]}`)
      const min = parseFloat(/minimum:\s*([\d.]+)\s*mm/.exec(msg)?.[1] ?? "0")
      if (ports.length === 2) { const g = padGap(ports[0], ports[1]); if (g != null && g >= min - 1e-6) continue }
      out.push({ kind: "clearance", text: msg })
    } else if (e.type === "pcb_pad_trace_clearance_error") {
      // Same rotated-pill blindness, pad-vs-trace: if the named pad clears all foreign copper by
      // its minimum (rotation-aware), the native "too close to trace" is a phantom — drop it.
      const pm = /pcb_port\[\.(\w+) > \.(\w+)\]/.exec(msg)
      const min = parseFloat(/minimum:\s*([\d.]+)\s*mm/.exec(msg)?.[1] ?? "0.1")
      if (pm) { const c = padMinClearance(`${pm[1]}.${pm[2]}`); if (c != null && c >= min - 1e-6) continue }
      out.push({ kind: "clearance", text: msg })
    } else if (e.type === "pcb_courtyard_overlap_error") {
      out.push({ kind: "courtyard", text: msg })
    } else if (e.type === "pcb_placement_error") {
      if (/outside or crossing the board boundary/.test(msg) && /\bVia\b/.test(msg)) continue // stitch-via false positive
      out.push({ kind: "placement", text: msg })
    } else {
      out.push({ kind: "other", text: msg })
    }
  }
  return out
}

const round = (n: number) => Math.round(n * 1000) / 1000
