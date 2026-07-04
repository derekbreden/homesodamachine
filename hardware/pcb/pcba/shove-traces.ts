/**
 * shove-traces.ts — post-route pad-clearance repair over the exported circuit-json.
 *
 * The capacity autorouter's high-density stage draws copper with no foreign-pad
 * obstacle (it enforces trace↔trace clearance but is blind to component pads), so
 * a routed trace can be drawn grazing a pad it doesn't connect to — a real DRC
 * short the board's clearance.ts only catches after the fact. This pass closes
 * that gap deterministically, on the same footing as the pour-clearance passes:
 * for every trace segment that comes within the clearance floor of a DIFFERENT-net
 * pad, it splices a detour vertex that lifts the segment out to the floor.
 *
 * Net identity (copied from clearance.ts) means a trace's own destination pads are
 * same-net and never shoved — only foreign copper is. Every candidate nudge is
 * re-checked against ALL foreign copper on its layer and kept only if the result
 * is DRC-clean; otherwise the original geometry is left untouched. So the pass is
 * monotonic: it removes pad shorts where geometry allows and never makes the board
 * worse. Idempotent and order-independent (a second run finds nothing to do).
 */

type Pt = [number, number]
type Feat = {
  net: string
  layers: Set<string>
  edges: Pt[][]
  r: number
  minx: number
  maxx: number
  miny: number
  maxy: number
  isPad: boolean
}

const copperLayers = (n: number): string[] =>
  n <= 2
    ? ["top", "bottom"]
    : ["top", ...Array.from({ length: n - 2 }, (_, i) => `inner${i + 1}`), "bottom"]

// Closest points and distance between segments p1p2 and p3p4 (zero-length = point).
function segSegClosest(
  p1: Pt,
  p2: Pt,
  p3: Pt,
  p4: Pt,
): { d: number; on1: Pt; on2: Pt } {
  const d1x = p2[0] - p1[0],
    d1y = p2[1] - p1[1],
    d2x = p4[0] - p3[0],
    d2y = p4[1] - p3[1]
  const rx = p1[0] - p3[0],
    ry = p1[1] - p3[1]
  const a = d1x * d1x + d1y * d1y,
    e = d2x * d2x + d2y * d2y,
    f = d2x * rx + d2y * ry
  const cl = (v: number) => Math.max(0, Math.min(1, v)),
    E = 1e-12
  let s: number, t: number
  if (a <= E && e <= E) {
    s = 0
    t = 0
  } else if (a <= E) {
    s = 0
    t = cl(f / e)
  } else {
    const c = d1x * rx + d1y * ry
    if (e <= E) {
      t = 0
      s = cl(-c / a)
    } else {
      const b = d1x * d2x + d1y * d2y,
        den = a * e - b * b
      s = den > E ? cl((b * f - c * e) / den) : 0
      t = (b * s + f) / e
      if (t < 0) {
        t = 0
        s = cl(-c / a)
      } else if (t > 1) {
        t = 1
        s = cl((b - c) / a)
      }
    }
  }
  const on1: Pt = [p1[0] + d1x * s, p1[1] + d1y * s]
  const on2: Pt = [p3[0] + d2x * t, p3[1] + d2y * t]
  return { d: Math.hypot(on1[0] - on2[0], on1[1] - on2[1]), on1, on2 }
}

const rectEdges = (
  x: number,
  y: number,
  w: number,
  h: number,
  deg: number,
): Pt[][] => {
  const a = (deg * Math.PI) / 180,
    c = Math.cos(a),
    s = Math.sin(a)
  const k = [
    [-w / 2, -h / 2],
    [w / 2, -h / 2],
    [w / 2, h / 2],
    [-w / 2, h / 2],
  ].map(([dx, dy]) => [x + dx * c - dy * s, y + dx * s + dy * c] as Pt)
  return [
    [k[0], k[1]],
    [k[1], k[2]],
    [k[2], k[3]],
    [k[3], k[0]],
  ]
}
const seg = (x1: number, y1: number, x2: number, y2: number): Pt[][] => [
  [
    [x1, y1],
    [x2, y2],
  ],
]

const bbox = (edges: Pt[][], r: number) => {
  let minx = Infinity,
    maxx = -Infinity,
    miny = Infinity,
    maxy = -Infinity
  for (const e of edges)
    for (const p of e) {
      minx = Math.min(minx, p[0])
      maxx = Math.max(maxx, p[0])
      miny = Math.min(miny, p[1])
      maxy = Math.max(maxy, p[1])
    }
  return { minx: minx - r, maxx: maxx + r, miny: miny - r, maxy: maxy + r }
}

// edge-to-edge distance + closest points between two features
function featDist(A: Feat, B: Feat): { d: number; onA: Pt; onB: Pt } {
  let best = { d: Infinity, onA: [0, 0] as Pt, onB: [0, 0] as Pt }
  for (const ea of A.edges)
    for (const eb of B.edges) {
      const r = segSegClosest(ea[0], ea[1], eb[0], eb[1])
      if (r.d < best.d) best = { d: r.d, onA: r.on1, onB: r.on2 }
    }
  return { d: best.d - A.r - B.r, onA: best.onA, onB: best.onB }
}

const shareLayer = (A: Feat, B: Feat) => {
  for (const l of A.layers) if (B.layers.has(l)) return true
  return false
}

export function shoveTracesOffPads(
  circuit: any[],
  floorMm = 0.1,
  // Nudge just clear of the floor rather than as far as possible: overshooting
  // trades the pad graze for a tight approach to whatever sits on the trace's
  // other side. A small margin keeps both sides comfortable and, in a narrow
  // corridor, keeps the nudge inside what the clean-DRC validation will accept.
  extraMm = 0.02,
): number {
  const boardEl = circuit.find((e) => e.type === "pcb_board")
  const LAYERS = copperLayers(boardEl?.num_layers ?? 2)

  // --- net resolution (mirrors clearance.ts) ---
  const srcPort: Record<string, any> = {},
    pcbPort: Record<string, any> = {},
    netByKey: Record<string, string> = {},
    netById: Record<string, string> = {},
    stNet: Record<string, string> = {}
  for (const e of circuit) {
    if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
    else if (e.type === "source_net") {
      netByKey[e.subcircuit_connectivity_map_key] = e.name
      netById[e.source_net_id] = e.name
    }
  }
  for (const e of circuit)
    if (e.type === "source_trace")
      stNet[e.source_trace_id] =
        (e.subcircuit_connectivity_map_key &&
          netByKey[e.subcircuit_connectivity_map_key]) ||
        netById[e.connected_source_net_ids?.[0]] ||
        e.subcircuit_connectivity_map_key ||
        ""
  let uniq = 0
  const netName = (id?: string): string | null => {
    const sp = id && pcbPort[id] ? srcPort[pcbPort[id].source_port_id] : null
    const k = sp?.subcircuit_connectivity_map_key
    return (k && netByKey[k]) || k || null
  }
  const netOfPort = (id?: string) => netName(id) || `__u${uniq++}`
  const netOfTrace = (t: any) => {
    const s = t.route.find((r: any) => r.start_pcb_port_id)?.start_pcb_port_id
    const e = t.route.find((r: any) => r.end_pcb_port_id)?.end_pcb_port_id
    if (s) return netOfPort(s)
    if (e) return netOfPort(e)
    return stNet[t.source_trace_id] || `__t${uniq++}`
  }

  // --- foreign-copper feature index (pads, holes, vias, other trace segments) ---
  const padFeats: Feat[] = [] // what we shove OFF (pads + plated holes)
  const allFeats: Feat[] = [] // everything a shoved segment must clear
  const add = (
    edges: Pt[][],
    r: number,
    layers: string[],
    net: string,
    isPad: boolean,
  ) => {
    const f: Feat = { net, layers: new Set(layers), edges, r, isPad, ...bbox(edges, r) }
    allFeats.push(f)
    if (isPad) padFeats.push(f)
    return f
  }
  for (const e of circuit) {
    if (e.type === "pcb_smtpad") {
      const net = netOfPort(e.pcb_port_id)
      if (e.shape === "rect")
        add(rectEdges(e.x, e.y, e.width, e.height, e.ccw_rotation || 0), 0, [e.layer], net, true)
      else {
        const w = e.width,
          h = e.height,
          r = e.radius ?? Math.min(w, h) / 2
        const half = Math.max(0, (Math.max(w, h) - 2 * r) / 2)
        const ang = (((h >= w ? 90 : 0) + (e.ccw_rotation || 0)) * Math.PI) / 180
        add(
          seg(
            e.x - Math.cos(ang) * half,
            e.y - Math.sin(ang) * half,
            e.x + Math.cos(ang) * half,
            e.y + Math.sin(ang) * half,
          ),
          r,
          [e.layer],
          net,
          true,
        )
      }
    } else if (e.type === "pcb_plated_hole") {
      add(
        seg(e.x, e.y, e.x, e.y),
        (e.outer_diameter ?? e.hole_diameter) / 2,
        LAYERS,
        netOfPort(e.pcb_port_id),
        true,
      )
    }
  }
  const traceNet: Record<string, string> = {}
  for (const e of circuit)
    if (e.type === "pcb_trace") traceNet[e.pcb_trace_id] = netOfTrace(e)
  for (const e of circuit)
    if (e.type === "pcb_via")
      add(
        seg(e.x, e.y, e.x, e.y),
        e.outer_diameter / 2,
        LAYERS,
        traceNet[e.pcb_trace_id] || `__v${uniq++}`,
        false,
      )
  for (const e of circuit)
    if (e.type === "pcb_trace") {
      const net = traceNet[e.pcb_trace_id]
      const rt = e.route
      for (let i = 0; i + 1 < rt.length; i++) {
        const a = rt[i],
          b = rt[i + 1]
        if (a.x == null || b.x == null || a.layer !== b.layer || (a.x === b.x && a.y === b.y))
          continue
        add(seg(a.x, a.y, b.x, b.y), (a.width ?? 0.2) / 2, [a.layer], net, false)
      }
    }

  // Min clearance of a hypothetical segment (centerline, half-width hw, layer L,
  // net N) to all foreign copper — used to validate a candidate nudge.
  const segClearance = (A: Pt, B: Pt, hw: number, layer: string, net: string): number => {
    const s: Feat = { net, layers: new Set([layer]), edges: seg(A[0], A[1], B[0], B[1]), r: hw, isPad: false, ...bbox(seg(A[0], A[1], B[0], B[1]), hw) }
    let m = Infinity
    for (const f of allFeats) {
      if (f.net === net || !shareLayer(f, s)) continue
      if (s.minx > f.maxx || f.minx > s.maxx || s.miny > f.maxy || f.miny > s.maxy) continue
      const d = featDist(s, f).d
      if (d < m) m = d
    }
    return m
  }

  // --- the shove ---
  let nudges = 0
  for (const tr of circuit) {
    if (tr.type !== "pcb_trace") continue
    const net = traceNet[tr.pcb_trace_id]
    const rt = tr.route
    for (let i = 0; i + 1 < rt.length; i++) {
      const a = rt[i],
        b = rt[i + 1]
      if (a.x == null || b.x == null || a.layer !== b.layer || (a.x === b.x && a.y === b.y))
        continue
      const hw = (a.width ?? 0.2) / 2
      const A: Pt = [a.x, a.y],
        B: Pt = [b.x, b.y]
      // worst foreign pad for this segment on its layer
      let worst: { pad: Feat; gap: number; onSeg: Pt; onPad: Pt } | null = null
      for (const pad of padFeats) {
        if (pad.net === net || !pad.layers.has(a.layer)) continue
        if (A[0] < pad.minx && B[0] < pad.minx) continue
        if (A[0] > pad.maxx && B[0] > pad.maxx) continue
        if (A[1] < pad.miny && B[1] < pad.miny) continue
        if (A[1] > pad.maxy && B[1] > pad.maxy) continue
        const segFeat: Feat = { net, layers: new Set([a.layer]), edges: seg(A[0], A[1], B[0], B[1]), r: hw, isPad: false, ...bbox(seg(A[0], A[1], B[0], B[1]), hw) }
        const r = featDist(segFeat, pad)
        if (r.d < floorMm && (!worst || r.d < worst.gap))
          worst = { pad, gap: r.d, onSeg: r.onA, onPad: r.onB }
      }
      if (!worst) continue

      // Only nudge when the closest approach is genuinely mid-segment; a graze at
      // a vertex is a placement issue a waypoint can't cleanly fix.
      const segLen = Math.hypot(B[0] - A[0], B[1] - A[1])
      const t =
        ((worst.onSeg[0] - A[0]) * (B[0] - A[0]) +
          (worst.onSeg[1] - A[1]) * (B[1] - A[1])) /
        (segLen * segLen)
      if (t < 0.05 || t > 0.95) continue

      // push the closest point out along the pad→segment normal to the floor
      let nx = worst.onSeg[0] - worst.onPad[0],
        ny = worst.onSeg[1] - worst.onPad[1]
      const nl = Math.hypot(nx, ny)
      if (nl < 1e-9) continue
      nx /= nl
      ny /= nl
      const deficit = floorMm + extraMm - worst.gap
      const Cx = worst.onSeg[0] + nx * deficit,
        Cy = worst.onSeg[1] + ny * deficit
      const C: Pt = [Cx, Cy]

      // validate: both new sub-segments must clear ALL foreign copper by >= floor
      if (
        segClearance(A, C, hw, a.layer, net) < floorMm ||
        segClearance(C, B, hw, a.layer, net) < floorMm
      )
        continue

      // splice the detour vertex in and register its two segments as obstacles so
      // later shoves see them
      rt.splice(i + 1, 0, { route_type: "wire", x: Cx, y: Cy, width: a.width ?? 0.2, layer: a.layer })
      add(seg(A[0], A[1], Cx, Cy), hw, [a.layer], net, false)
      add(seg(Cx, Cy, B[0], B[1]), hw, [a.layer], net, false)
      nudges++
      i++ // re-examine from the new vertex onward
    }
  }
  return nudges
}
