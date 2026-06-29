/**
 * pretty-router.ts — the in-process 2nd-pass clean-fan router. Pure functions: given an
 * obstacle circuit-json (the board with the target nets NOT yet routed) and the net pairs
 * to route, cleanFanRoute returns a clean fan — straight → 45° → straight — as a route of
 * pcb_trace/pcb_via points that render-board splices straight into circuit-json.
 *
 * NO file or child-process I/O — the caller supplies the circuit-json (render-board routes
 * against it mid-build). Routes are computed from live pad geometry every build, never
 * snapshotted into frozen coordinates in the board .tsx.
 */

export type RoutePoint =
  | { route_type: "wire"; x: number; y: number; width: number; layer: string }
  | { route_type: "via"; x: number; y: number; from_layer: string; to_layer: string }

export type RoutedNet = { from: string; to: string; route: RoutePoint[]; vias: number }

export type FanType = "fanRowToColumn" | "fanColumnToRow" | "fanColumnToColumn" | "fanRowToRow"

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

// A clean fan: a FIXED geometric path (NOT a search) — straight → 45° → straight. The XY
// shape never bends around copper; the only obstacle-aware decision is which LAYER each
// piece runs on. Pass `field` (the copper routed so far) to make it Z-aware.
export type CleanSpec = { fanType: FanType; layer?: string; width?: number; stub?: number; field?: any[]; clr?: number }

const wirePt = (x: number, y: number, width: number, layer: string): RoutePoint =>
  ({ route_type: "wire", x: +x.toFixed(3), y: +y.toFixed(3), width, layer })
const viaPt = (x: number, y: number, from_layer: string, to_layer: string): RoutePoint =>
  ({ route_type: "via", x: +x.toFixed(3), y: +y.toFixed(3), from_layer, to_layer })

// distance from point (px,py) to segment (ax,ay)-(bx,by)
const ptSegDist = (px: number, py: number, ax: number, ay: number, bx: number, by: number): number => {
  const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy
  const tt = L2 ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L2)) : 0
  return Math.hypot(px - (ax + tt * dx), py - (ay + tt * dy))
}
// min distance between segment AB and segment CD (0 if they cross)
const segSegDist = (ax: number, ay: number, bx: number, by: number, cx: number, cy: number, dx: number, dy: number): number => {
  const d1x = bx - ax, d1y = by - ay, d2x = dx - cx, d2y = dy - cy, den = d1x * d2y - d1y * d2x
  if (Math.abs(den) > 1e-12) {
    const ux = cx - ax, uy = cy - ay, ta = (ux * d2y - uy * d2x) / den, tb = (ux * d1y - uy * d1x) / den
    if (ta >= 0 && ta <= 1 && tb >= 0 && tb <= 1) return 0
  }
  return Math.min(
    ptSegDist(ax, ay, cx, cy, dx, dy), ptSegDist(bx, by, cx, cy, dx, dy),
    ptSegDist(cx, cy, ax, ay, bx, by), ptSegDist(dx, dy, ax, ay, bx, by),
  )
}
// Does segment a→b on `layer` come within edge-to-edge `clr` of any copper there the fan
// doesn't own — a trace wire, or an SMD pad (e.g. C4's 0805 pads sitting in the U6→U2 I2C
// corridor)? The fan's own from/to endpoint pads are exempt (its escape and landing
// legitimately touch them — passed as `own`); copper pours are ignored — a pour auto-clears
// around any trace, never a short. An SMD pad blocks only its own copper layer, so a diagonal
// that hits one on top can dive under it on the bottom. Returns the offending id, or null.
const diagHitsCopper = (a: { x: number; y: number }, b: { x: number; y: number }, layer: string, field: any[], clr: number, width: number, own: { x: number; y: number }[]): string | null => {
  const owned = (x: number, y: number) => own.some((o) => Math.hypot(x - o.x, y - o.y) < 0.05)
  for (const e of field) {
    if (e.type === "pcb_trace") {
      const r = e.route || []
      for (let i = 0; i + 1 < r.length; i++) {
        const p = r[i], q = r[i + 1]
        if (p.route_type !== "wire" || q.route_type !== "wire" || p.layer !== layer || q.layer !== layer) continue
        if (segSegDist(a.x, a.y, b.x, b.y, p.x, p.y, q.x, q.y) < clr + width / 2 + (p.width ?? 0.2) / 2) return e.pcb_trace_id || "?"
      }
    } else if (e.type === "pcb_smtpad" && e.layer === layer && !owned(e.x, e.y)) {
      // a disc covering the whole pad: the rect's half-diagonal (rotation-invariant — covers
      // the corner a 45° run would otherwise clip), or the circle radius. The pads we care
      // about sit squarely in a corridor, so the conservative disc is exact enough.
      const reach = e.shape === "circle" ? (e.radius || 0) : Math.hypot(e.width || 0, e.height || 0) / 2
      if (reach && ptSegDist(e.x, e.y, a.x, a.y, b.x, b.y) < clr + width / 2 + reach) return e.pcb_smtpad_id || "?"
    }
  }
  return null
}

// Route one net as a clean fan. The pad escape and the pad landing are PERPENDICULAR to
// their pin lines; the 45° diagonal happens in open space between them. The path is FIXED —
// it never bends to dodge copper. It IS obstacle-aware in Z: if the diagonal would cross
// top copper, that diagonal drops to the bottom layer (a via at each end) so it passes
// under instead of shorting — when the bottom is clear there too; if BOTH layers are
// blocked it throws (it can't route this fixed path without a short). Escape/landing stay
// on the pads' (top) layer. With no `field`, it stays all-top, 0 vias.
//
// fanType is fan<source line>To<target line>: the source pads lie on a ROW (escape ⟂ in Y)
// or a COLUMN (escape ⟂ in X); the target pads lie on a ROW (land ⟂ in Y) or a COLUMN
// (land ⟂ in X). All four are escape → 45° → land, the diagonal covering the offset the
// two straights don't:
//   fanRowToColumn     escape Y, land X     fanColumnToRow     escape X, land Y
//   fanColumnToColumn  escape X, land X     fanRowToRow        escape Y, land Y
export function cleanFanRoute(pads: Record<string, { x: number; y: number }>, from: string, to: string, spec: CleanSpec): RoutedNet {
  const s = pads[from], t = pads[to]
  if (!s || !t) throw new Error(`clean fan: no pad ${!s ? from : to}`)
  const top = spec.layer ?? "top", bottom = top === "top" ? "bottom" : "top"
  const width = spec.width ?? 0.2, stub = spec.stub ?? 1, clr = spec.clr ?? 0.25
  const sgx = Math.sign(t.x - s.x), sgy = Math.sign(t.y - s.y)
  // the four FIXED corners: source pad → perpendicular escape → diagonal end → target pad.
  // The diagonal (p1→p2) is 45° by construction (|Δx| = |Δy|); the escape (p0→p1) and the
  // landing (p2→p3) are each a single axis, ⟂ to the source / target pin line.
  let p0: { x: number; y: number }, p1: { x: number; y: number }, p2: { x: number; y: number }, p3: { x: number; y: number }
  if (spec.fanType === "fanRowToColumn") {        // escape Y, land X
    const y1 = s.y + sgy * stub
    p0 = { x: s.x, y: s.y }; p1 = { x: s.x, y: y1 }
    p2 = { x: s.x + sgx * Math.abs(t.y - y1), y: t.y }; p3 = { x: t.x, y: t.y }
  } else if (spec.fanType === "fanColumnToRow") {  // escape X, land Y
    const x1 = s.x + sgx * stub
    p0 = { x: s.x, y: s.y }; p1 = { x: x1, y: s.y }
    p2 = { x: t.x, y: s.y + sgy * Math.abs(t.x - x1) }; p3 = { x: t.x, y: t.y }
  } else if (spec.fanType === "fanColumnToColumn") { // escape X, land X (diagonal spans Y)
    const x1 = s.x + sgx * stub
    p0 = { x: s.x, y: s.y }; p1 = { x: x1, y: s.y }
    p2 = { x: x1 + sgx * Math.abs(t.y - s.y), y: t.y }; p3 = { x: t.x, y: t.y }
  } else if (spec.fanType === "fanRowToRow") {      // escape Y, land Y (diagonal spans X)
    const y1 = s.y + sgy * stub
    p0 = { x: s.x, y: s.y }; p1 = { x: s.x, y: y1 }
    p2 = { x: t.x, y: y1 + sgy * Math.abs(t.x - s.x) }; p3 = { x: t.x, y: t.y }
  } else {
    throw new Error(`clean fan ${from} -> ${to}: unknown fanType ${JSON.stringify(spec.fanType)} (expected fanRowToColumn | fanColumnToRow | fanColumnToColumn | fanRowToRow)`)
  }
  // Z-only obstacle awareness: keep the whole net on top unless the diagonal p1→p2 would
  // cross top copper — then drop JUST the diagonal to the bottom layer. The XY path is
  // identical either way; only the layer of the diagonal (and its two vias) changes.
  let diagLayer = top
  const own = [s, t] // the fan's own endpoint pads — its escape/landing touch them, so they're exempt
  if (spec.field && diagHitsCopper(p1, p2, top, spec.field, clr, width, own)) {
    if (!diagHitsCopper(p1, p2, bottom, spec.field, clr, width, own)) diagLayer = bottom
    else throw new Error(`[pretty] fan ${from} -> ${to}: diagonal crosses copper on BOTH layers — cannot route this fixed path without a short`)
  }
  const w = (pp: { x: number; y: number }, l: string) => wirePt(pp.x, pp.y, width, l)
  let route: RoutePoint[], vias = 0
  if (diagLayer === top) {
    route = [w(p0, top), w(p1, top), w(p2, top), w(p3, top)]
  } else {
    route = [
      w(p0, top), w(p1, top),                          // escape on top
      viaPt(p1.x, p1.y, top, bottom), w(p1, bottom),   // dive
      w(p2, bottom),                                   // diagonal on bottom
      viaPt(p2.x, p2.y, bottom, top), w(p2, top),      // surface
      w(p3, top),                                      // landing on top
    ]
    vias = 2
  }
  return { from, to, route, vias }
}

// warn (don't fail) if a fan's pin mapping isn't monotone — that's when risers cross.
// axis = source coordinate that's swept; tax = target coordinate that must track it.
export function monoWarn(pairs: { from: string; to: string }[], pads: Record<string, { x: number; y: number }>, axis: "x" | "y", tax: "x" | "y", label: string) {
  const pts = pairs.map((p) => ({ s: pads[p.from], t: pads[p.to] })).filter((p) => p.s && p.t)
  const by = [...pts].sort((a, b) => a.s![axis] - b.s![axis]).map((p) => p.t![tax])
  const up = by.every((v, i) => i === 0 || v >= by[i - 1]!), dn = by.every((v, i) => i === 0 || v <= by[i - 1]!)
  if (!up && !dn) console.error(`[pretty] WARN: ${label} pin mapping non-monotone — fan may cross`)
}
