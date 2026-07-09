/**
 * routing — the hand-routing geometry kit pcba.tsx builds pcbPaths with.
 *
 * A hand trace is a `route(...)`: pad anchors at the ends, one-dimensional constraints between.
 * `F.col(pin, dx)` is the vertical line dx east of a pad; `F.row(pin, dy)` the horizontal line dy
 * north of it; a corridor lane is a bare `{ col: x }`. Consecutive constraints intersect into the
 * waypoints, and the closing turn into each pad falls out of the pad itself — so every corner is
 * 90° by construction, every coordinate derives from the pad (or corridor) that shapes it, and the
 * path rides any move of its parts, alone or as a group. Points are board coordinates: each trace
 * declares pcbPathRelativeTo="board". Manual vias are full-stack top<->bottom ONLY, so hand paths
 * live on the top or bottom layer.
 */

export type Pt = { x: number; y: number }
type Constraint = { col: number } | { row: number }
export type Frame = {
  name: string
  pin: (p: string) => Pt
  col: (p: string, dx?: number) => { col: number }
  row: (p: string, dy?: number) => { row: number }
}

// Derive a part's pad offsets (footprint-local mm, pre-rotation) by walking its placed element down
// to the <smtpad>s — INVOKING each component wrapper on the way (Usblc6 → centred → USBLC6_2SC6 →
// <footprint>), so the footprint tscircuit actually places is the one source of truth and no hand-
// copied table can drift. Every pad is keyed by its portHints id (`pin1`…) AND by each of the chip's
// pinLabels aliases (`EN`, `VBUS`, `IO36`…), so routing taps a pad by whichever name reads clearest.
const framePins = (node: any): Record<string, [number, number]> => {
  const out: Record<string, [number, number]> = {}
  const mm = (v: number | string) => typeof v === "number" ? v : parseFloat(v)
  let labels: Record<string, string[]> = {}
  const walk = (n: any) => {
    if (!n || typeof n !== "object") return
    if (Array.isArray(n)) return n.forEach(walk)
    const { type, props = {} } = n
    if (typeof type === "function") { try { walk(type(props)) } catch {} return }  // open the wrapper
    if (props.pinLabels) labels = props.pinLabels
    if (type === "smtpad" && props.portHints?.length) {
      const off: [number, number] = [mm(props.pcbX), mm(props.pcbY)]
      out[props.portHints[0]] = off
      for (const alias of labels[props.portHints[0]] ?? []) out[alias] = off
    }
    if (props.footprint) walk(props.footprint)
    if (props.children) walk(props.children)
  }
  walk(node)
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
  if (a && typeof a === "object" && a.props) {     // placed element → derive centre, rotation, pins
    name = a.props.name; cx = a.props.x; cy = a.props.y
    rot = a.props.rot ?? a.props.pcbRotation ?? 0
    pins = framePins(a)
  } else name = a
  const t = (rot * Math.PI) / 180, cos = Math.cos(t), sin = Math.sin(t)
  const pin = (p: string): Pt => {                 // this frame's pad, in board coords
    const [ox, oy] = pins[p] ?? (() => { throw new Error(`${name}: no pad ${p}`) })()
    return { x: cx + cos * ox - sin * oy, y: cy + sin * ox + cos * oy }
  }
  const f: Frame = {
    name, pin,
    col: (p: string, dx = 0) => ({ col: pin(p).x + dx }),
    row: (p: string, dy = 0) => ({ row: pin(p).y + dy }),
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
