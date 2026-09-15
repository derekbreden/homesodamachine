/** The faucet brand mark as single-color silkscreen routes, centered in PCB mm.
 *  Source: brand/mark.svg. Geometry: tools/build_brand_assets.py.
 */
import { logoGeometry } from "./logo-geometry"

type Pt = { x: number; y: number }
const r3 = (v: number) => +v.toFixed(3)

/** `h` is the complete mark's height; `strokeWidth` matches its silk stroke. */
export function logoRoutes(cx: number, cy: number, h: number, strokeWidth = 0.15): Pt[][] {
  const { faucet, drop, bounds } = logoGeometry
  const scale = h / (bounds.bottom - bounds.top)
  const centerX = (bounds.left + bounds.right) / 2
  const centerY = (bounds.top + bounds.bottom) / 2
  const map = (x: number, y: number): Pt => ({
    x: r3(cx + (x - centerX) * scale), y: r3(cy - (y - centerY) * scale),
  })
  // Horizontal routes fill the silhouette. Their spacing keeps adjacent
  // strokes overlapping; a half-stroke inset leaves the source contour clear.
  const routes: Pt[][] = []
  const inset = strokeWidth / scale / 2
  const pitch = strokeWidth / scale * 0.25
  for (let y = bounds.top + inset; y < bounds.bottom - inset; y += pitch) {
    const intersections: number[] = []
    for (let i = 1; i < faucet.length; i++) {
      const [ax, ay] = faucet[i - 1], [bx, by] = faucet[i]
      if ((ay > y) !== (by > y)) intersections.push(ax + (y - ay) * (bx - ax) / (by - ay))
    }
    intersections.sort((a, b) => a - b)
    for (let i = 0; i + 1 < intersections.length; i += 2) {
      const left = intersections[i] + inset, right = intersections[i + 1] - inset
      if (right > left) routes.push([map(left, y), map(right, y)])
    }
    const dy = y - drop.cy
    const radius = drop.r - inset
    if (Math.abs(dy) < radius) {
      const dx = Math.sqrt(radius * radius - dy * dy)
      routes.push([map(drop.cx - dx, y), map(drop.cx + dx, y)])
    }
  }
  return routes
}
