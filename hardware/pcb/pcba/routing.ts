/**
 * routing — the hand-routing geometry kit pcba.tsx builds pcbPaths with.
 *
 * A hand trace is a `route(...)`: pad anchors at the ends, one-dimensional constraints between.
 * `F.col(pin, dx)` is the vertical line dx east of a pad's CENTRE; `F.row(pin, dy)` the horizontal
 * line dy north of it. To hug a pad EDGE instead, `F.east/west(pin, gap)` and `F.above/below(pin,
 * gap)` place the line `gap` clear of that face of the real pad rectangle (from the footprint, so
 * the pad's true size is used — no guessed half-width). A corridor lane is a bare `{ col: x }`.
 * Consecutive constraints intersect into the
 * waypoints, and the closing turn into each pad falls out of the pad itself — so every corner is
 * 90° by construction, every coordinate derives from the pad (or corridor) that shapes it, and the
 * path rides any move of its parts, alone or as a group. Points are board coordinates: each trace
 * declares pcbPathRelativeTo="board". Manual vias are full-stack top<->bottom ONLY, so hand paths
 * live on the top or bottom layer.
 */

export type Pt = { x: number; y: number }
type Constraint = { col: number } | { row: number }
// A pad in the part's board-axes frame: centre offset from the part centre, plus the half-width /
// half-height of its board-axis bounding box (so an edge is `pin ± half ± gap`, exact from the
// footprint — never a guessed extent).
type PadGeom = { off: [number, number]; hw: number; hh: number }
export type Frame = {
  name: string
  pin: (p: string) => Pt
  col: (p: string, dx?: number) => { col: number }   // vertical line dx east of the pad CENTRE
  row: (p: string, dy?: number) => { row: number }    // horizontal line dy north of the pad CENTRE
  east: (p: string, gap?: number) => { col: number }  // vertical line gap east of the pad's east EDGE
  west: (p: string, gap?: number) => { col: number }  // …west of the west edge
  above: (p: string, gap?: number) => { row: number } // horizontal line gap north of the north edge
  below: (p: string, gap?: number) => { row: number } // …south of the south edge
}

// Derive a part's pad offsets (board-axes mm from the part's centre) by walking its placed element
// down to the <smtpad>s — INVOKING each component wrapper on the way (Usblc6 → centred →
// USBLC6_2SC6 → <footprint>), so the footprint tscircuit actually places is the one source of truth
// and no hand-copied table can drift. Every `pcbRotation` on an intrinsic element composes on the
// way down (a wrapper's rotation prop is forwarded to an intrinsic, so it counts exactly once) —
// the returned offsets are fully rotated, including a wrapper's own intrinsic rotation (Buzzer
// seats its MLT-5020 at 90). Every pad is keyed by its portHints id (`pin1`…) AND by each of the
// chip's pinLabels aliases (`EN`, `VBUS`, `IO36`…), so routing taps a pad by whichever name reads
// clearest.
const framePins = (node: any): Record<string, PadGeom> => {
  const out: Record<string, PadGeom> = {}
  const mm = (v: number | string) => typeof v === "number" ? v : parseFloat(v)
  let labels: Record<string, string[]> = {}
  const walk = (n: any, rot: number) => {
    if (!n || typeof n !== "object") return
    if (Array.isArray(n)) return n.forEach((c) => walk(c, rot))
    const { type, props = {} } = n
    if (typeof type === "function") { try { walk(type(props), rot) } catch {} return }  // open the wrapper
    const r = rot + (props.pcbRotation != null ? mm(props.pcbRotation) : 0)
    if (props.pinLabels) labels = props.pinLabels
    if (type === "smtpad" && props.portHints?.length) {
      const t = (r * Math.PI) / 180, cos = Math.cos(t), sin = Math.sin(t)
      const [px, py] = [mm(props.pcbX), mm(props.pcbY)]
      const off: [number, number] = [cos * px - sin * py, sin * px + cos * py]
      // The pad rectangle rotated by r: its board-axis bounding half-extents. (Axis-aligned at 0/90/
      // 180/270 — which every part here is — so this is the pad's own half-width / half-height.)
      const [w, h] = [props.width != null ? mm(props.width) : 0, props.height != null ? mm(props.height) : 0]
      const geom: PadGeom = { off, hw: Math.abs(cos) * w / 2 + Math.abs(sin) * h / 2, hh: Math.abs(sin) * w / 2 + Math.abs(cos) * h / 2 }
      out[props.portHints[0]] = geom
      for (const alias of labels[props.portHints[0]] ?? []) out[alias] = geom
    }
    if (props.footprint) walk(props.footprint, r)
    if (props.children) walk(props.children, r)
  }
  walk(node, 0)
  return out
}

const frames: Record<string, Frame> = {}

// A "frame": a component's placed pose (centre + rotation) plus its pad geometry. Call it with the
// placed ELEMENT — `frame(<Usblc6 name x y rot/>)` — and centre / rotation / pins all derive from
// it (props + footprint), so the placement is the single source of truth. The explicit form
// `frame(name, cx, cy, rot, pins)` is for a part whose pad names aren't footprint pins (a Jst's
// labels are board-assigned, not <smtpad> ids). Every frame registers by name; `route` resolves
// its "U14.pin1" anchors through the registry.
export function frame(el: any): Frame
export function frame(name: string, cx: number, cy: number, rot: number, pins?: Record<string, [number, number]>): Frame
export function frame(a: any, cx = 0, cy = 0, rot = 0, pins: Record<string, [number, number]> = {}): Frame {
  let name: string
  let geoms: Record<string, PadGeom>
  if (a && typeof a === "object" && a.props) {     // placed element → derive centre and pad geometry
    name = a.props.name; cx = a.props.x; cy = a.props.y
    rot = 0                                        // framePins offsets arrive fully rotated
    geoms = framePins(a)
  } else {                                         // explicit form: board-assigned offsets, no pad size
    name = a
    geoms = Object.fromEntries(Object.entries(pins).map(([k, off]) => [k, { off, hw: 0, hh: 0 }]))
  }
  const t = (rot * Math.PI) / 180, cos = Math.cos(t), sin = Math.sin(t)
  const geom = (p: string): PadGeom => geoms[p] ?? (() => { throw new Error(`${name}: no pad ${p}`) })()
  const pin = (p: string): Pt => {                 // this frame's pad centre, in board coords
    const [ox, oy] = geom(p).off
    return { x: cx + cos * ox - sin * oy, y: cy + sin * ox + cos * oy }
  }
  const f: Frame = {
    name, pin,
    col: (p, dx = 0) => ({ col: pin(p).x + dx }),
    row: (p, dy = 0) => ({ row: pin(p).y + dy }),
    east: (p, gap = 0) => ({ col: pin(p).x + geom(p).hw + gap }),
    west: (p, gap = 0) => ({ col: pin(p).x - geom(p).hw - gap }),
    above: (p, gap = 0) => ({ row: pin(p).y + geom(p).hh + gap }),
    below: (p, gap = 0) => ({ row: pin(p).y - geom(p).hh - gap }),
  }
  frames[name] = f
  return f
}

// Place a run in a corridor between two column centres `a` and `b`: centre it (bias 0) to maximise
// clearance to both walls, or bias to one (−1 hug a / +1 hug b) to deliberately leave the other side
// open for a future trace. A corridor run is NEVER at an arbitrary offset — clearance is a resource,
// allocated on purpose (centre or reserve), never spent by accident. (See hand-routing.md.)
export const channel = (a: number, b: number, bias = 0): number => (a + b) / 2 + bias * (Math.abs(b - a) / 2 - 0.6)

// An orthogonal path from pad to pad through the given column/row constraints. Each constraint
// supplies the one coordinate it is responsible for; the other carries over from the point before,
// and the closing turn into the far pad comes from the pad itself. "U14.pin1" anchors resolve
// through the frame registry.
export const route = (from: string, ...rest: [...Constraint[], string]): (Pt | string)[] => {
  const to = rest[rest.length - 1] as string
  const constraints = rest.slice(0, -1) as Constraint[]
  const at = (anchor: string): Pt => {
    const [name, pad] = [anchor.slice(0, anchor.indexOf(".")), anchor.slice(anchor.indexOf(".") + 1)]
    const f = frames[name] ?? (() => { throw new Error(`route: no frame ${name}`) })()
    return f.pin(pad)
  }
  const pts: Pt[] = []
  let cur = at(from)
  for (const c of constraints) {
    cur = "col" in c ? { x: c.col, y: cur.y } : { x: cur.x, y: c.row }
    pts.push(cur)
  }
  const end = at(to)
  if (constraints.length) {
    const last = constraints[constraints.length - 1]!
    const close = "col" in last ? { x: cur.x, y: end.y } : { x: end.x, y: cur.y }
    if (Math.hypot(close.x - cur.x, close.y - cur.y) > 1e-9 && Math.hypot(close.x - end.x, close.y - end.y) > 1e-9)
      pts.push(close)
  }
  return [from, ...pts, to]
}
