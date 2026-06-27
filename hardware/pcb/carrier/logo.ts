/**
 * logo — the Home Soda Machine mark as monocolor silkscreen polylines.
 *
 * The shared brand logo (ios/AppIcon.svg, the firmware splash, the site) is a
 * tapered soda glass with a liquid surface and rising bubbles. Silk is single
 * colour and stroke-only, so this renders the recognizable subset — the glass
 * outline, the liquid wave, and the bubbles — as flattened polylines (curves
 * subdivided, circles polygonized), mapped from the SVG viewBox (0..1024,
 * Y-down) into PCB millimetres (Y-up), centered at (cx, cy) with the glass body
 * `h` mm tall. Stroke them with <silkscreenpath> (see mini.tsx).
 *
 * The SVG clips the liquid + bubbles to the glass interior (a clipPath); we do
 * the same here so nothing spills past the glass: the wave is trimmed to meet
 * both walls exactly, and each bubble is clipped to the glass body so the low
 * one is cut off at the base instead of poking through it. Geometry taken
 * verbatim from ios/AppIcon.svg.
 */
type Pt = { x: number; y: number }

const GLASS_SVG_H = 530 // glass spans y247..y777 in the source viewBox
const SVG_C = 512 // icon centre (the glass is centred on it)
const r3 = (v: number) => +v.toFixed(3)

// quadratic bézier P0->(control C)->P1, subdivided into `n` segments (excludes P0)
const qflat = (p0: Pt, c: Pt, p1: Pt, n = 10): Pt[] => {
  const o: Pt[] = []
  for (let i = 1; i <= n; i++) {
    const t = i / n, u = 1 - t
    o.push({ x: u * u * p0.x + 2 * u * t * c.x + t * t * p1.x, y: u * u * p0.y + 2 * u * t * c.y + t * t * p1.y })
  }
  return o
}
const circle = (cx: number, cy: number, r: number, n = 20): Pt[] => {
  const o: Pt[] = []
  for (let i = 0; i < n; i++) { const a = (i / n) * 2 * Math.PI; o.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) }) }
  return o
}

// glass outline (SVG coords): M310 247 L340 747 Q345 777 380 777 L644 777 Q679 777 684 747 L714 247 Z
function glassSvg(): Pt[] {
  const g: Pt[] = [{ x: 310, y: 247 }, { x: 340, y: 747 }]
  g.push(...qflat({ x: 340, y: 747 }, { x: 345, y: 777 }, { x: 380, y: 777 }))
  g.push({ x: 644, y: 777 })
  g.push(...qflat({ x: 644, y: 777 }, { x: 679, y: 777 }, { x: 684, y: 747 }))
  g.push({ x: 714, y: 247 }, { x: 310, y: 247 })
  return g
}

// the glass tapered walls, as lines x = m·y + c (used to trim the wave to the walls)
const wall = (left: boolean) => {
  const x0 = left ? 310 : 714, x1 = left ? 340 : 684
  const m = (x1 - x0) / (747 - 247)
  return { x: (y: number) => x0 + (y - 247) * m, m, c: x0 - 247 * m }
}
const LEFT = wall(true), RIGHT = wall(false)

// Sutherland–Hodgman: clip closed polygon `subj` to a convex polygon `clip`.
function clipPolygon(subj: Pt[], clip: Pt[]): Pt[] {
  let area = 0
  for (let i = 0; i < clip.length; i++) { const p = clip[i], q = clip[(i + 1) % clip.length]; area += p.x * q.y - q.x * p.y }
  const sign = Math.sign(area) || 1
  const inside = (p: Pt, a: Pt, b: Pt) => sign * ((b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)) >= 0
  const isect = (s: Pt, e: Pt, a: Pt, b: Pt): Pt => {
    const d1x = e.x - s.x, d1y = e.y - s.y, d2x = b.x - a.x, d2y = b.y - a.y
    const den = d1x * d2y - d1y * d2x
    if (Math.abs(den) < 1e-9) return e
    const t = ((a.x - s.x) * d2y - (a.y - s.y) * d2x) / den
    return { x: s.x + t * d1x, y: s.y + t * d1y }
  }
  let out = subj
  for (let i = 0; i < clip.length && out.length; i++) {
    const a = clip[i], b = clip[(i + 1) % clip.length], input = out
    out = []
    for (let j = 0; j < input.length; j++) {
      const cur = input[j], prev = input[(j - 1 + input.length) % input.length]
      const ci = inside(cur, a, b), pi = inside(prev, a, b)
      if (ci) { if (!pi) out.push(isect(prev, cur, a, b)); out.push(cur) }
      else if (pi) out.push(isect(prev, cur, a, b))
    }
  }
  return out
}

// Trim the (open) wave polyline to the glass interior, landing its ends exactly
// on the walls so the liquid surface touches both sides with no gap.
function clipWaveToWalls(pts: Pt[]): Pt[] {
  const inside = (p: Pt) => p.x >= LEFT.x(p.y) && p.x <= RIGHT.x(p.y)
  const cross = (q: Pt, p: Pt): Pt => {
    const o = inside(q) ? p : q // the outside endpoint picks the wall
    const w = o.x < LEFT.x(o.y) ? LEFT : RIGHT
    const dx = p.x - q.x, dy = p.y - q.y
    const t = (w.m * q.y + w.c - q.x) / (dx - w.m * dy)
    return { x: q.x + t * dx, y: q.y + t * dy }
  }
  const out: Pt[] = []
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i], pin = inside(p)
    if (i > 0 && pin !== inside(pts[i - 1])) out.push(cross(pts[i - 1], p))
    if (pin) out.push(p)
  }
  return out
}

/** The logo as a list of polyline routes (glass, liquid wave, four bubbles),
 *  in PCB mm, centered at (cx, cy), glass body `h` mm tall. */
export function logoRoutes(cx: number, cy: number, h: number): Pt[][] {
  const s = h / GLASS_SVG_H
  const P = (p: Pt): Pt => ({ x: r3(cx + (p.x - SVG_C) * s), y: r3(cy - (p.y - SVG_C) * s) })
  const map = (pts: Pt[]) => pts.map(P)

  const glass = glassSvg()
  const clip = glass.slice(0, -1) // drop the closing duplicate -> convex clip polygon

  // liquid surface wave: M300 347 Q400 327 512 352 Q624 377 724 342 (the source
  // runs wall-to-wall and is clipped); trim it to touch both walls.
  const wave = clipWaveToWalls([
    { x: 300, y: 347 },
    ...qflat({ x: 300, y: 347 }, { x: 400, y: 327 }, { x: 512, y: 352 }),
    ...qflat({ x: 512, y: 352 }, { x: 624, y: 377 }, { x: 724, y: 342 }),
  ])

  // bubbles, each clipped to the glass body (the low one is cut at the base)
  const bubbles = [[440, 740, 42], [572, 610, 36], [500, 489, 33], [628, 408, 29]] as const
  const bubbleRoutes = bubbles.map(([bx, by, r]) => clipPolygon(circle(bx, by, r), clip))

  return [map(glass), map(wave), ...bubbleRoutes.map(map)]
}
