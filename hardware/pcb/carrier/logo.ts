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
 * Geometry taken verbatim from ios/AppIcon.svg: glass body, the liquid surface
 * wave, and the four bubble circles.
 */
type Pt = { x: number; y: number }

const GLASS_SVG_H = 530 // glass spans y247..y777 in the source viewBox
const SVG_C = 512 // icon centre (the glass is centred on it)
const r3 = (v: number) => +v.toFixed(3)

// quadratic bézier P0->(control C)->P1, subdivided into `n` segments
const qflat = (p0: Pt, c: Pt, p1: Pt, n = 10): Pt[] => {
  const o: Pt[] = []
  for (let i = 1; i <= n; i++) {
    const t = i / n, u = 1 - t
    o.push({ x: u * u * p0.x + 2 * u * t * c.x + t * t * p1.x, y: u * u * p0.y + 2 * u * t * c.y + t * t * p1.y })
  }
  return o
}
const circle = (cx: number, cy: number, r: number, n = 14): Pt[] => {
  const o: Pt[] = []
  for (let i = 0; i <= n; i++) { const a = (i / n) * 2 * Math.PI; o.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) }) }
  return o
}

/** The logo as a list of polyline routes (glass, liquid wave, four bubbles),
 *  in PCB mm, centered at (cx, cy), glass body `h` mm tall. */
export function logoRoutes(cx: number, cy: number, h: number): Pt[][] {
  const s = h / GLASS_SVG_H
  const P = (x: number, y: number): Pt => ({ x: r3(cx + (x - SVG_C) * s), y: r3(cy - (y - SVG_C) * s) })
  const map = (pts: Pt[]) => pts.map((p) => P(p.x, p.y))

  // glass: M310 247 L340 747 Q345 777 380 777 L644 777 Q679 777 684 747 L714 247 Z
  const glass: Pt[] = [{ x: 310, y: 247 }, { x: 340, y: 747 }]
  glass.push(...qflat({ x: 340, y: 747 }, { x: 345, y: 777 }, { x: 380, y: 777 }))
  glass.push({ x: 644, y: 777 })
  glass.push(...qflat({ x: 644, y: 777 }, { x: 679, y: 777 }, { x: 684, y: 747 }))
  glass.push({ x: 714, y: 247 }, { x: 310, y: 247 })

  // liquid surface wave: M300 347 Q400 327 512 352 Q624 377 724 342 — clipped to the glass interior
  let wave: Pt[] = []
  wave.push(...qflat({ x: 300, y: 347 }, { x: 400, y: 327 }, { x: 512, y: 352 }))
  wave.push(...qflat({ x: 512, y: 352 }, { x: 624, y: 377 }, { x: 724, y: 342 }))
  wave = wave.filter((p) => p.x >= 328 && p.x <= 696)

  const bubbles = [[440, 740, 42], [572, 610, 36], [500, 489, 33], [628, 408, 29]] as const

  return [map(glass), map(wave), ...bubbles.map(([bx, by, r]) => map(circle(bx, by, r)))]
}
