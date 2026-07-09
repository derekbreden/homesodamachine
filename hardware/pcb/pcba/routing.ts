/**
 * routing — the hand-routing geometry kit pcba.tsx builds pcbPaths with.
 *
 * A pcbPath's numeric {x,y} points are in the FROM component's OWN frame: board = center +
 * R(rotation)·local, where `center` is the component's resolved pcb center and `rotation` is its
 * `rot`. Get the center or rotation wrong and every point lands off — that is the single thing that
 * makes hand routing go sideways. (See routing-procedure.md.) Manual vias are full-stack top<->bottom
 * ONLY, so hand paths live on the top or bottom layer.
 *
 * `frame(el)` captures a placed component and turns its pin geometry into path points. Every method
 * returns a point in THAT (the trace's `from`) frame:
 *   .ref(pin)             the pad string anchor, e.g. "U14.pin1" — use for a pcbPath's endpoints
 *   .pin(pin)             the pad's BOARD position {x,y}
 *   .at(bx, by)           a fixed BOARD point — stays put when THIS component moves
 *   .off(dx, dy)          a raw LOCAL offset — rides THIS component
 *   .fromPin(pin, bx, by) a point (bx,by) mm (board axes) from THIS frame's own pad — RIDES this
 *                         component, so an exit stub follows its pad when the part moves
 *   .toPin(f, pin, bx,by) a point (bx,by) mm from ANOTHER frame f's pad — board-fixed, and FOLLOWS
 *                         that pad if f moves, so an approach tracks its target
 */

export type Pt = { x: number; y: number }
export type Frame = {
  at: (bx: number, by: number) => Pt
  pin: (p: string) => Pt
  ref: (p: string) => string
  off: (dx: number, dy: number) => Pt
  fromPin: (p: string, bx?: number, by?: number) => Pt
  toPin: (f: { pin: (p: string) => Pt }, p: string, bx?: number, by?: number) => Pt
}

// Derive a part's pad offsets (footprint-local mm, pre-rotation) by walking its placed element down
// to the <smtpad>s — INVOKING each component wrapper on the way (Usblc6 → centred → USBLC6_2SC6 →
// <footprint>), so the footprint tscircuit actually places is the one source of truth and no hand-
// copied table can drift. Every pad is keyed by its portHints id (`pin1`…) AND by each of the chip's
// pinLabels aliases (`EN`, `VBUS`, `IO36`…), so routing taps a pad by whichever name reads clearest.
export const framePins = (node: any): Record<string, [number, number]> => {
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

// A "frame": a component's placed pose (centre + rotation) plus its pad geometry, exposing board-
// coord helpers to hand-route against. Call it with the placed ELEMENT — `frame(<Usblc6 name x y
// rot/>)` — and centre / rotation / pins all derive from it (props + footprint), so the placement is
// the single source of truth. The explicit form `frame(name, cx, cy, rot, pins)` is for a part whose
// pad names aren't footprint pins (a Jst's AOUT/DOUT are board-assigned labels, not <smtpad> ids).
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
  const at = (bx: number, by: number): Pt => {     // board -> this frame's local: R(-rot)·(board - center)
    const dx = bx - cx, dy = by - cy
    return { x: cos * dx + sin * dy, y: -sin * dx + cos * dy }
  }
  const pin = (p: string): Pt => {                 // this frame's pad, in board coords
    const [ox, oy] = pins[p] ?? (() => { throw new Error(`${name}: no pad ${p}`) })()
    return { x: cx + cos * ox - sin * oy, y: cy + sin * ox + cos * oy }
  }
  return {
    at, pin,
    ref: (p: string) => `${name}.${p}`,
    off: (dx: number, dy: number): Pt => ({ x: dx, y: dy }),
    fromPin: (p: string, bx = 0, by = 0): Pt => { const b = pin(p); return at(b.x + bx, b.y + by) },
    toPin: (f: { pin: (p: string) => Pt }, p: string, bx = 0, by = 0): Pt => { const b = f.pin(p); return at(b.x + bx, b.y + by) },
  }
}

// A no-via "U" that ties two pads of the same connector `f`: out from `a` by the board stub, across
// to `b`, back in — one jumper, not a second full path. Returns a whole pcbPath.
export const pcbU = (f: Frame, a: string, b: string, stub: [number, number]) =>
  [f.ref(a), f.fromPin(a, ...stub), f.fromPin(b, ...stub), f.ref(b)]

// A fan from one source pad to several dest pads that share an approach lane: each branch exits the
// source the same way, runs to board x=`laneX`, then to its dest pad's row and in. Returns one
// { to, pcbPath } per dest — map them onto <trace from={...}>. No vias.
export const pcbFan = (srcF: Frame, srcPin: string, exit: [number, number], destF: Frame, destPins: string[], laneX: number) =>
  destPins.map((d) => ({
    to: destF.ref(d),
    pcbPath: [srcF.ref(srcPin), srcF.fromPin(srcPin, ...exit), srcF.at(laneX, destF.pin(d).y), destF.ref(d)],
  }))

// Place a run in a corridor between two column centres `a` and `b`: centre it (bias 0) to maximise
// clearance to both walls, or bias to one (−1 hug a / +1 hug b) to deliberately leave the other side
// open for a future trace. A corridor run is NEVER at an arbitrary offset — clearance is a resource,
// allocated on purpose (centre or reserve), never spent by accident. (See hand-routing.md.)
export const channel = (a: number, b: number, bias = 0): number => (a + b) / 2 + bias * (Math.abs(b - a) / 2 - 0.6)

// Orthogonal (90°-only) tap from a midpoint pad up to a U1 pin. Every pad exits along its own face:
// the source pad escapes sideways past its own top resistor, and — because the H-across (`apY`) sits
// well below U1 — the U1 pad exits *south* on a clean stub before any jog, never from its E/W side.
// orthoTap jogs H to `laneX` (its escape / corridor lane), V up to `apY`, H across to the pin's
// column, V into the pad. The H-across collapses when `laneX` already sits under the pin (straight up).
export const orthoTap = (fromF: Frame, pin: string, laneX: number, toF: Frame, toPin: string, apY = -10.8): (Pt | string)[] => {
  const p = fromF.pin(pin), q = toF.pin(toPin), path: Pt[] = [{ x: laneX, y: p.y }]
  if (Math.abs(laneX - q.x) > 1e-6) path.push({ x: laneX, y: apY }, { x: q.x, y: apY })
  return [fromF.ref(pin), ...path.map((v) => fromF.at(v.x, v.y)), toF.ref(toPin)]
}

// `orthoDrop` drops a pad straight down (at its own column, or `dropX` to clear an obstacle) to the
// target's row, then H straight into it — for the J11 connector inputs. Two segments, one 90° corner.
export const orthoDrop = (fromF: Frame, pin: string, toF: Frame, toPin: string, dropX?: number): (Pt | string)[] => {
  const p = fromF.pin(pin), q = toF.pin(toPin)
  return [fromF.ref(pin), fromF.at(dropX ?? p.x, q.y), toF.ref(toPin)]
}
