/**
 * Discrete-copper clearance + genuine-error analysis of a routed circuit-json, for the
 * web viewer's board readout (folded into picks.json by pick-data.ts).
 *
 * FLOOR — the smallest edge-to-edge gap between any two pieces of copper on different nets
 * that share a layer. Copper is pads, plated-hole barrels, vias, and trace segments; every
 * shape reduces to a rounded polyline (a rect is 4 zero-radius edges, a pill/circle/via/
 * trace a segment with a radius), so a gap is `min segment-segment distance − r1 − r2`.
 * Poured planes are out of scope — plane connection is antipad geometry, a separate axis.
 * Net identity groups by net NAME first (a plane spans several connectivity keys the pour
 * joins), then connectivity key (one signal net), then unique (unconnected copper). Stitch
 * and mst pcb_traces carry no ports, so their net comes from their source_trace.
 *
 * ERRORS — the genuine DRC findings, filtered out of the pour-blind noise the board carries
 * every render: the ~90 "missing a connection to smtpad" trace errors are a pad-alias/pour
 * artifact (the pad IS reached — tested against the routed copper) and the "via outside the
 * board boundary" placement errors are false (the stitch vias land post-DRC, inside). What
 * survives is copper overlaps / too-close, courtyard overlaps, real opens, and any other
 * placement error.
 */

type Pt = [number, number]
type Feat = { edges: Pt[][]; r: number; layers: Set<string>; net: string; label: string; minx: number; maxx: number; miny: number; maxy: number }
export type ClearancePair = { gap: number; a: string; b: string }
export type BoardError = { kind: string; text: string }
export type ClearanceReport = { floor: number | null; tight: ClearancePair[]; errors: BoardError[] }

const AABB_CAP = 1.5 // skip a pair whose bounding boxes are farther apart than this (mm)
const TIGHT_MAX = 8  // how many of the tightest pairs to keep for the readout

export function analyzeClearance(circuit: any[]): ClearanceReport {
  const srcPort: Record<string, any> = {}, pcbPort: Record<string, any> = {}
  const compName: Record<string, string> = {}
  const netByKey: Record<string, string> = {}, netById: Record<string, string> = {}
  const stNet: Record<string, string> = {}
  const smtpadByPort: Record<string, any> = {}
  for (const e of circuit) {
    if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
    else if (e.type === "source_component") compName[e.source_component_id] = e.name
    else if (e.type === "source_net") { netByKey[e.subcircuit_connectivity_map_key] = e.name; netById[e.source_net_id] = e.name }
    else if (e.type === "pcb_smtpad" && e.pcb_port_id) smtpadByPort[e.pcb_port_id] = e
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
  const netLabel = (net: string) => (net.startsWith("__") || /connectivity_net/.test(net) ? "signal" : net)

  const feats: Feat[] = []
  const push = (edges: Pt[][], r: number, layers: string[], net: string, label: string) => {
    let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity
    for (const e of edges) for (const p of e) { minx = Math.min(minx, p[0]); maxx = Math.max(maxx, p[0]); miny = Math.min(miny, p[1]); maxy = Math.max(maxy, p[1]) }
    feats.push({ edges, r, layers: new Set(layers), net, label, minx: minx - r, maxx: maxx + r, miny: miny - r, maxy: maxy + r })
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
      if (e.shape === "rect") push(rectEdges(e.x, e.y, e.width, e.height, e.ccw_rotation || 0), 0, [e.layer], net, label)
      else { // pill / rotated_pill — a capsule along its long axis
        const w = e.width, h = e.height, r = e.radius ?? Math.min(w, h) / 2
        const half = Math.max(0, (Math.max(w, h) - 2 * r) / 2)
        const ang = ((h >= w ? 90 : 0) + (e.ccw_rotation || 0)) * Math.PI / 180
        push(seg(e.x - Math.cos(ang) * half, e.y - Math.sin(ang) * half, e.x + Math.cos(ang) * half, e.y + Math.sin(ang) * half), r, [e.layer], net, label)
      }
    } else if (e.type === "pcb_plated_hole") {
      push(seg(e.x, e.y, e.x, e.y), (e.outer_diameter ?? e.hole_diameter) / 2, ["top", "bottom"], netOfPort(e.pcb_port_id), refPin(e.pcb_port_id))
    }
  }
  const traceNet: Record<string, string> = {}
  for (const e of circuit) if (e.type === "pcb_trace") traceNet[e.pcb_trace_id] = netOfTrace(e)
  for (const e of circuit) if (e.type === "pcb_via") {
    const net = traceNet[e.pcb_trace_id] || `__v${uniq++}`
    push(seg(e.x, e.y, e.x, e.y), e.outer_diameter / 2, ["top", "bottom"], net, `via on ${netLabel(net)}`)
  }
  for (const e of circuit) if (e.type === "pcb_trace") {
    const net = traceNet[e.pcb_trace_id] || `__t${uniq++}`, rt = e.route
    for (let i = 0; i + 1 < rt.length; i++) {
      const a = rt[i], b = rt[i + 1]
      if (a.x == null || b.x == null || a.layer !== b.layer || (a.x === b.x && a.y === b.y)) continue
      push(seg(a.x, a.y, b.x, b.y), (a.width ?? 0.2) / 2, [a.layer], net, `trace on ${netLabel(net)}`)
    }
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

  let floor = Infinity
  const pairs: ClearancePair[] = []
  for (let i = 0; i < feats.length; i++) for (let j = i + 1; j < feats.length; j++) {
    const A = feats[i], B = feats[j]
    if (A.net === B.net || !shareLayer(A, B)) continue
    if (A.minx > B.maxx + AABB_CAP || B.minx > A.maxx + AABB_CAP || A.miny > B.maxy + AABB_CAP || B.miny > A.maxy + AABB_CAP) continue
    const d = dist(A, B)
    if (d < floor) floor = d
    if (d < 0.35) pairs.push({ gap: round(d), a: A.label, b: B.label })
  }
  pairs.sort((x, y) => x.gap - y.gap)

  return { floor: isFinite(floor) ? round(floor) : null, tight: pairs.slice(0, TIGHT_MAX), errors: genuineErrors(circuit, pcbPort, smtpadByPort) }
}

// Filter the routed circuit's *_error rows down to the genuine ones (see file header).
function genuineErrors(circuit: any[], pcbPort: Record<string, any>, smtpadByPort: Record<string, any>): BoardError[] {
  const verts: Pt[] = []
  for (const e of circuit) if (e.type === "pcb_trace") for (const r of e.route) if (r.x != null) verts.push([r.x, r.y])
  const reached = (pad: any) => { const hw = (pad.width || 0) / 2 + 0.05, hh = (pad.height || 0) / 2 + 0.05; return verts.some((v) => Math.abs(v[0] - pad.x) <= hw && Math.abs(v[1] - pad.y) <= hh) }
  const out: BoardError[] = []
  for (const e of circuit) {
    if (typeof e.type !== "string" || !e.type.endsWith("_error")) continue
    const msg: string = e.message || ""
    if (e.type === "pcb_trace_error") {
      const m = /missing a connection to smtpad\[([^\]]+)\]/.exec(msg)
      if (m) { const pad = smtpadByPort[(e.pcb_port_ids || [])[0]]; if (pad && reached(pad)) continue; out.push({ kind: "open", text: `Unrouted: ${m[1]}` }); continue }
      out.push({ kind: "overlap", text: msg })
    } else if (e.type === "pcb_pad_pad_clearance_error" || e.type === "pcb_pad_trace_clearance_error") {
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
