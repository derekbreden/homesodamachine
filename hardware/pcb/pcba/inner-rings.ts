/**
 * Inner-layer annular rings, injected into the plane-layer copper.
 *
 * A plated hole's pad is drawn on the layers it declares, and a THT barrel declares top and
 * bottom. Three barrels take an inner-layer trace as the only path to their pin — J8.SDA and
 * J8.SCL, where the I2C star meets the connector, and J4.IO23 — so each wants copper on the
 * layer its trace runs on. Without it the trace reaches the barrel as a cut edge in the hole
 * wall: a connection the plating still makes, over the trace's width rather than the pad's
 * circumference.
 *
 * The generator draws a plated hole only on the layers the element lists, and reaches for the
 * layer's soldermask name while doing it — which inner layers do not have — so the ring is
 * emitted here as RS-274X instead, the same splice `led-knockout.ts` makes into the front silk.
 * Each plane voids around a barrel by its pad radius plus the pour's own `netClearance`, whatever
 * layer the pad is drawn on, so a ring lands in clearance already cut for it and the solved pours
 * are left alone.
 *
 * Geometry is board-mm, 1:1 with the inner copper gerbers (no y-flip), same as every other
 * feature render-board.ts writes.
 */

/** Barrels this layer's traces terminate on: pad centre + the diameter its ring wants. */
function ringsOn(circuit: any[], layerRef: string) {
  const holes = circuit.filter((e) => e.type === "pcb_plated_hole")
  const out = new Map<string, { x: number; y: number; d: number }>()
  for (const t of circuit) {
    if (t.type !== "pcb_trace") continue
    for (const p of t.route ?? []) {
      if (p.layer !== layerRef) continue
      for (const h of holes) {
        if (Math.abs(p.x - h.x) > 0.05 || Math.abs(p.y - h.y) > 0.05) continue
        const d = h.outer_diameter ?? Math.min(h.outer_width ?? Infinity, h.outer_height ?? Infinity)
        if (Number.isFinite(d)) out.set(h.pcb_plated_hole_id, { x: h.x, y: h.y, d })
      }
    }
  }
  return [...out.values()]
}

/**
 * RS-274X fragment for `layerRef`'s rings, to splice into that layer before `M02*`.
 * `base` is the layer string being spliced into: its highest `%ADD<n>` sets the ring's own
 * D-code, so it can never collide with an aperture the generator already defined.
 */
export function innerRingGerber(circuit: any[], base: string, layerRef: "inner1" | "inner2"): string {
  const rings = ringsOn(circuit, layerRef)
  if (!rings.length) return ""
  let ap = 0
  for (const m of base.matchAll(/%ADD(\d+)/g)) ap = Math.max(ap, Number(m[1]))
  const um = (v: number) => Math.round(v * 1e6)
  const L: string[] = ["%LPD*%"]
  const byDia = new Map<number, { x: number; y: number }[]>()
  for (const r of rings) {
    if (!byDia.has(r.d)) byDia.set(r.d, [])
    byDia.get(r.d)!.push({ x: r.x, y: r.y })
  }
  for (const [d, pts] of byDia) {
    ap += 1
    L.push(`%ADD${ap}C,${d.toFixed(6)}*%`, `D${ap}*`)
    for (const p of pts) L.push(`X${um(p.x)}Y${um(p.y)}D03*`)
  }
  return L.join("\n")
}

/** Every inner-layer trace endpoint that lands on a plated hole has a pad flashed under it. */
export function assertInnerRinged(circuit: any[], glayers: Record<string, string>) {
  const gbr: Record<string, string> = { inner1: "In1_Cu", inner2: "In2_Cu" }
  const flashed = (text: string, x: number, y: number) => {
    let cx = 0, cy = 0
    for (const raw of (text ?? "").split("\n")) {
      const m = /^(?:X(-?\d+))?(?:Y(-?\d+))?D0?([123])\*$/.exec(raw.trim())
      if (!m) continue
      if (m[1]) cx = Number(m[1]) * 1e-6
      if (m[2]) cy = Number(m[2]) * 1e-6
      if (m[3] === "3" && Math.abs(cx - x) < 0.02 && Math.abs(cy - y) < 0.02) return true
    }
    return false
  }
  const bare: string[] = []
  for (const layerRef of ["inner1", "inner2"] as const)
    for (const r of ringsOn(circuit, layerRef))
      if (!flashed(glayers[gbr[layerRef]!]!, r.x, r.y))
        bare.push(`  ${layerRef}: barrel at (${r.x.toFixed(3)}, ${r.y.toFixed(3)}) carries a trace on that layer with no pad under it`)
  if (bare.length)
    throw new Error(`zero-ring inner-layer connection:\n${[...new Set(bare)].join("\n")}`)
}
