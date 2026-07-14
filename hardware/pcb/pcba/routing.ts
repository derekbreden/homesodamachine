/**
 * routing — the hand-routing geometry kit pcba.tsx builds pcbPaths with.
 *
 * A hand trace is a `route(...)`: pad anchors at the ends, one-dimensional constraints between.
 * Every `F.*` constraint reads in the PART's OWN frame: `F.col(pin, d)` steps d along the part's
 * local-x from a pad, `F.row(pin, d)` along local-y; `F.east/west/above/below(pin, gap)` sit `gap`
 * clear of the pad's own +x/−x/+y/−y face (real footprint size, no guessed half-width). The part's
 * placement rotation drops each onto a board col or row — so at rot 0 they ARE the plain board
 * lines, but when the part turns the whole trace turns with it (positions already rode a rotation;
 * now the directions do too, so a cluster can be rotated and nothing inside it changes). A corridor
 * lane is a bare `{ col: x }` — board-absolute, anchored to no part, so it deliberately does NOT ride.
 * Consecutive constraints intersect into the
 * waypoints, and the closing turn into each pad falls out of the pad itself — so every corner is
 * 90° by construction, every coordinate derives from the pad (or corridor) that shapes it, and the
 * path rides any move of its parts, alone or as a group. Points are board coordinates: each trace
 * declares pcbPathRelativeTo="board". Every manual via is one full-stack through-hole DRILL; the
 * copper may enter and leave it on any layer (routeBottom pairs top pads through the bottom,
 * routeInner drops onto a trace-free inner plane layer), so a hand path lives on whichever
 * layers its via points name.
 */

export type Pt = { x: number; y: number }
// A via-point in a pcbPath: one full-stack through-hole DRILL at (x,y) that switches the copper onto
// `toLayer` for the segments that follow (tscircuit's manual-trace renderer honours this; the core
// fork records the barrel as spanning every layer, so pours antipad it on each plane it crosses even
// when the copper transition ends on an inner layer). A `{ via }` constraint drops one at the path's
// current point, so a route() can change layers inline instead of dropping into raw {x,y} points.
export type Layer = "top" | "inner1" | "inner2" | "bottom"
export type ViaPt = { x: number; y: number; via: true; toLayer: Layer }
export type PathPt = Pt | ViaPt
type Constraint = { col: number } | { row: number } | { via: Layer }
// A pad in the part's own frame: centre offset (already rotated into board coords), plus the pad's
// half-width / half-height in that frame (footprint dims, un-rotated — the frame rotates them).
type PadGeom = { off: [number, number]; hw: number; hh: number }
// Every method reads in the PART's frame and returns a board constraint: for a rotated part a `col`
// (a line along local-x) can land on a board row, which is exactly what lets a trace ride the part
// when it turns. At rot 0 they are the plain board col/row/edges.
export type Frame = {
  name: string
  pin: (p: string) => Pt
  col: (p: string, d?: number) => Constraint    // line d along the part's local-x from the pad CENTRE
  row: (p: string, d?: number) => Constraint    // line d along the part's local-y from the pad CENTRE
  east: (p: string, gap?: number) => Constraint // line gap beyond the pad's local +x EDGE
  west: (p: string, gap?: number) => Constraint // …its local −x edge
  above: (p: string, gap?: number) => Constraint // …its local +y edge
  below: (p: string, gap?: number) => Constraint // …its local −y edge
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
    if ((type === "smtpad" || type === "platedhole") && props.portHints?.length) {
      const t = (r * Math.PI) / 180, cos = Math.cos(t), sin = Math.sin(t)
      const [px, py] = [mm(props.pcbX), mm(props.pcbY)]
      const off: [number, number] = [cos * px - sin * py, sin * px + cos * py]
      // The pad's own half-width / half-height, in the PART's frame (the footprint dims). The part's
      // placement rotation is NOT baked in here — the frame's direction methods apply it — so an edge
      // stays the pad's own face and rides when the part turns. A plated hole's copper is its
      // outer ring, so its "pad size" is the outer diameter.
      const w = props.width != null ? mm(props.width) : props.outerDiameter != null ? mm(props.outerDiameter) : props.outerWidth != null ? mm(props.outerWidth) : 0
      const h = props.height != null ? mm(props.height) : props.outerDiameter != null ? mm(props.outerDiameter) : props.outerHeight != null ? mm(props.outerHeight) : 0
      const geom: PadGeom = { off, hw: w / 2, hh: h / 2 }
      out[props.portHints[0]] = geom
      // pinLabels values are a string OR an array of aliases — normalise, or a bare string
      // char-iterates ("RO" would register as "R" and "O", never "RO").
      const aliases = labels[props.portHints[0]]
      for (const alias of Array.isArray(aliases) ? aliases : aliases != null ? [aliases] : []) out[alias] = geom
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
  let placeRot: number                             // placement rotation — turns local offset directions into board col/row
  let geoms: Record<string, PadGeom>
  if (a && typeof a === "object" && a.props) {     // placed element → derive centre and pad geometry
    name = a.props.name; cx = a.props.x; cy = a.props.y
    placeRot = a.props.rot ?? a.props.pcbRotation ?? 0
    rot = 0                                        // framePins offsets arrive fully rotated
    geoms = framePins(a)
  } else {                                         // explicit form: board-assigned offsets, no pad size
    name = a; placeRot = rot
    geoms = Object.fromEntries(Object.entries(pins).map(([k, off]) => [k, { off, hw: 0, hh: 0 }]))
  }
  const t = (rot * Math.PI) / 180, cos = Math.cos(t), sin = Math.sin(t)
  const geom = (p: string): PadGeom => geoms[p] ?? (() => { throw new Error(`${name}: no pad ${p}`) })()
  const pin = (p: string): Pt => {                 // this frame's pad centre, in board coords
    const [ox, oy] = geom(p).off
    return { x: cx + cos * ox - sin * oy, y: cy + sin * ox + cos * oy }
  }
  // Part-LOCAL constraint lines. `lx`/`ly` step `d` along the part's own x / y axis, then the
  // placement rotation drops the result onto a board col or row — so the SAME call rides the part
  // when it turns (positions already ride; now the directions do too). Only 0/90/180/270 are used,
  // so `pc`/`ps` are ±1 or 0 and every local axis lands cleanly on a board axis.
  const pr = (placeRot * Math.PI) / 180, pc = Math.cos(pr), ps = Math.sin(pr)
  const lx = (p: string, d: number): Constraint => Math.abs(pc) > 0.5 ? { col: pin(p).x + d * pc } : { row: pin(p).y + d * ps }
  const ly = (p: string, d: number): Constraint => Math.abs(pc) > 0.5 ? { row: pin(p).y + d * pc } : { col: pin(p).x - d * ps }
  const f: Frame = {
    name, pin,
    col: (p, d = 0) => lx(p, d),
    row: (p, d = 0) => ly(p, d),
    east: (p, gap = 0) => lx(p, geom(p).hw + gap),
    west: (p, gap = 0) => lx(p, -(geom(p).hw + gap)),
    above: (p, gap = 0) => ly(p, geom(p).hh + gap),
    below: (p, gap = 0) => ly(p, -(geom(p).hh + gap)),
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
// Resolve an "Comp.pad" anchor to its board {x, y} through the frame registry.
const padAt = (anchor: string): Pt => {
  const [name, pad] = [anchor.slice(0, anchor.indexOf(".")), anchor.slice(anchor.indexOf(".") + 1)]
  const f = frames[name] ?? (() => { throw new Error(`no frame ${name}`) })()
  return f.pin(pad)
}

export const route = (from: string, ...rest: [...Constraint[], string]): (PathPt | string)[] => {
  const to = rest[rest.length - 1] as string
  const constraints = rest.slice(0, -1) as Constraint[]
  const pts: PathPt[] = []
  let cur = padAt(from)
  let lastAxis: "col" | "row" | null = null   // the closing turn ignores vias (they don't move the point)
  for (const c of constraints) {
    if ("via" in c) {
      // a zero-length layer transition at the current point, bracketed by a coincident wire on the
      // new layer (tscircuit's via-alignment check wants wire@p on both sides of via@p)
      pts.push({ x: cur.x, y: cur.y, via: true, toLayer: c.via }, { x: cur.x, y: cur.y })
    } else if ("col" in c) {
      cur = { x: c.col, y: cur.y }; pts.push(cur); lastAxis = "col"
    } else {
      cur = { x: cur.x, y: c.row }; pts.push(cur); lastAxis = "row"
    }
  }
  const end = padAt(to)
  if (lastAxis) {
    const close = lastAxis === "col" ? { x: cur.x, y: end.y } : { x: end.x, y: cur.y }
    if (Math.hypot(close.x - cur.x, close.y - cur.y) > 1e-9 && Math.hypot(close.x - end.x, close.y - end.y) > 1e-9)
      pts.push(close)
  }
  return [from, ...pts, to]
}


// A BOTTOM-layer path with a via on each end pad — Derek's "pad via to pad via". Same orthogonal
// geometry as route(), but the run lives on the bottom plane: a via drops on the FROM pad, the
// waypoints carry on the bottom, and a via climbs back to top on the TO pad (the trace's own from/to
// close it on top). The two pads are the ONLY vias. Reach for this only once the top face is proven
// blocked and the bottom corridor is clear — the GND pour antipads this copper like any crossing
// signal, and any autorouter trace it fouls is deferred, never negotiated. Corridor lanes here are
// board-absolute ({row}/{col}) because they thread board-fixed obstacles (vias, plated holes) —
// and they stay OUT of foreign pad shadows: a pad's footprint is via territory through the whole
// stack (stitch vias and pad-vias land there), so a lane under a pad row is a pad-shadow error
// (clearance.ts), not a shortcut.
export const routeBottom = (from: string, ...rest: [...Constraint[], string]): PathPt[] => {
  const to = rest[rest.length - 1] as string
  const mids = route(from, ...rest).slice(1, -1) as PathPt[]   // reuse route()'s orthogonal waypoints
  const a = padAt(from), b = padAt(to)
  // A via must be a zero-length transition: the wire on each side has to sit AT the via's point
  // (tscircuit's via-alignment check), so each via is bracketed by a coincident wire on the new layer
  // — exactly the `wire@p, via@p, wire@p, …` shape the autorouter emits.
  return [
    { x: a.x, y: a.y, via: true, toLayer: "bottom" },
    { x: a.x, y: a.y },
    ...mids,
    { x: b.x, y: b.y },
    { x: b.x, y: b.y, via: true, toLayer: "top" },
  ]
}

// A path from an SMD pad to a plated-hole BARREL — the I2C bus-edge shape. A via drops on the
// FROM pad (via-in-pad, one full-stack drill), the run rides `layer` — the plane layers are the
// widest corridors on the board, carrying no other traces — and the path simply ENDS at the
// barrel: a plated hole conducts on every layer, so the far end needs no via at all. That
// asymmetry is what lets a multi-drop net share one junction (each SMD pad carries exactly one
// via; every edge meets at the barrel) with no two drills ever landing on the same point —
// closing INTO a barrel with a via (routeBottom's shape) would put a via drill inside the
// connector's drill, a coincident-hit DFM fault. `layer` may also be "bottom": the same
// barrel-terminated shape one layer down (a connector-bound routeBottom). The same shadow
// discipline as routeBottom applies: a pad's footprint is via territory through the whole
// stack, so lanes stay out of foreign pad shadows and 0.14 clear of every barrel.
export const routeInner = (layer: "inner1" | "inner2" | "bottom", from: string, ...rest: [...Constraint[], string]): PathPt[] => {
  const a = padAt(from)
  const mids = route(from, ...rest).slice(1, -1) as PathPt[]   // reuse route()'s orthogonal waypoints
  return [
    { x: a.x, y: a.y, via: true, toLayer: layer },
    { x: a.x, y: a.y },
    ...mids,
  ]
}
