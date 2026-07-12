/**
 * pour-clearance.ts — net-class clearance applied over the exported circuit-json. A pour
 * declares it on the board, beside its outline:
 *
 *   <copperpour connectsTo="net.V12" netClearance="0.5mm from V3V3, V5, SDA, SCL" ... />
 *
 * findPourClearanceRules reads that off the source (tscircuit doesn't know netClearance and drops
 * it, so the rule is carried in the attribute and parsed here, like pretty=). widenPourVoids
 * applies it: each <copperpour> arrives already solved into a brep — an outer_ring plus inner_rings,
 * one per antipad void the solver cut around a foreign pad at its single clearance — and for a
 * declared net pair this appends a larger keepout ring around the foreign pad. The gerber converter
 * draws every inner_ring as a clear region, so the larger overlapping clear is the one that takes.
 * Per layer: the V12 pour clears around the low-voltage pads under it; the planes it pairs with
 * clear around the 12V barrels punching through them.
 *
 * Read live every build — a part moving re-cuts the voids. No-op on a board with no netClearance.
 */

export type ClearanceRule = { a: string; b: string; clearanceMm: number }

// Read each pour's `netClearance="<mm>mm from NetA, NetB, …"` into unordered net pairs, paired with
// the pour's own net (connectsTo). The aggressor is the declaring pour's net; the rest are victims.
export function findPourClearanceRules(src: string): ClearanceRule[] {
  const rules: ClearanceRule[] = []
  for (const el of src.match(/<copperpour\b[\s\S]*?\/>/g) || []) {
    const decl = (el.match(/\bnetClearance="([^"]*)"/) || [])[1]
    const net = (el.match(/\bconnectsTo="net\.([^"]*)"/) || [])[1]
    if (!decl || !net) continue
    const m = decl.match(/^\s*([\d.]+)\s*mm\s+from\s+(.+)$/i)
    if (!m) continue
    const clearanceMm = parseFloat(m[1]!)
    for (const v of m[2]!.split(",").map((s) => s.trim()).filter(Boolean)) rules.push({ a: net, b: v, clearanceMm })
  }
  return rules
}

type Vert = { x: number; y: number }

// point in polygon, ray cast
function pointInPolygon(x: number, y: number, verts: Vert[]): boolean {
  let inside = false
  for (let i = 0, j = verts.length - 1; i < verts.length; j = i++) {
    const xi = verts[i]!.x, yi = verts[i]!.y, xj = verts[j]!.x, yj = verts[j]!.y
    if (((yi > y) !== (yj > y)) && (x < ((xj - xi) * (y - yi)) / (yj - yi) + xi)) inside = !inside
  }
  return inside
}

// axis-aligned half-extent {hx,hy} of a pad's copper
function padHalfExtent(pad: any): { hx: number; hy: number } {
  if (pad.type === "pcb_smtpad") {
    if (pad.shape === "circle") return { hx: pad.radius, hy: pad.radius }
    return { hx: (pad.width ?? 0) / 2, hy: (pad.height ?? 0) / 2 }
  }
  if (pad.shape === "circular_hole_with_rect_pad") {
    const w = pad.rect_pad_width ?? pad.outer_diameter ?? pad.hole_diameter ?? 0
    const h = pad.rect_pad_height ?? pad.outer_diameter ?? pad.hole_diameter ?? 0
    const rot = ((pad.rect_ccw_rotation ?? 0) * Math.PI) / 180
    if (rot) {
      const c = Math.abs(Math.cos(rot)), s = Math.abs(Math.sin(rot))
      return { hx: (w / 2) * c + (h / 2) * s, hy: (w / 2) * s + (h / 2) * c }
    }
    return { hx: w / 2, hy: h / 2 }
  }
  const d = pad.outer_diameter ?? pad.hole_diameter ?? 0
  return { hx: d / 2, hy: d / 2 }
}

// An SMD pad is on its one layer; a plated through-hole (top..bottom) is on every copper layer.
function padOnLayer(pad: any, layer: string): boolean {
  if (pad.type === "pcb_smtpad") return pad.layer === layer
  const ls: string[] = pad.layers || []
  return ls.includes(layer) || (ls.includes("top") && ls.includes("bottom"))
}

// pad bbox grown by clr, wound CCW like the solver's inner_rings
function keepoutRing(cx: number, cy: number, hx: number, hy: number): { vertices: Vert[] } {
  return { vertices: [
    { x: cx - hx, y: cy - hy }, { x: cx + hx, y: cy - hy },
    { x: cx + hx, y: cy + hy }, { x: cx - hx, y: cy + hy },
  ] }
}

export type WidenStats = { added: number; perPour: Record<string, number>; pads: string[] }

export type FastenerAnnulus = { name: string; rMm: number; net: string | null }

// Read each plated hole's `fastenerAnnulus="<mm>mm"` — the radius its fastener stack (screw
// head / standoff / washer) sweeps on the two outer faces — plus the hole's name and declared
// net (connectsTo). Carried in the source attribute and parsed here, exactly like netClearance
// above (tscircuit's platedhole schema strips the unknown prop).
export function findFastenerAnnuli(src: string): FastenerAnnulus[] {
  const out: FastenerAnnulus[] = []
  for (const el of src.match(/<platedhole\b[\s\S]*?\/>/g) || []) {
    const r = (el.match(/\bfastenerAnnulus="([\d.]+)\s*mm"/) || [])[1]
    const name = (el.match(/\bname="([^"]*)"/) || [])[1]
    if (!r || !name) continue
    const net = (el.match(/\bconnectsTo="net\.([^"]*)"/) || [])[1] ?? null
    out.push({ name, rMm: parseFloat(r), net })
  }
  return out
}

/** Clear every outer-layer pour out from under mounting hardware. The solver's antipad around a
 *  plated hole is pad + one trace clearance — hardware sweeps wider, and solder mask is not a
 *  fastener-rated insulator, so foreign copper must not sit inside the stack's footprint. For each
 *  declared hole (matched by port_hints name), every brep pour on `top`/`bottom` whose net differs
 *  from the hole's own gets a square keepout ring (same geometry as widenPourVoids') of half-extent
 *  rMm — so the guaranteed clearance is rMm on the axes and more on the diagonals, and a pour edge
 *  nearer than rMm is crossed outright, leaving no crescent scrap between ring and edge. Inner
 *  planes keep the solver's antipad: no fastener reaches them, and their copper is plane budget.
 *  A pour on the hole's OWN net stays — that copper is what the hardware is meant to touch.
 *  Mutates `circuit` in place; same stats shape as widenPourVoids. */
export function widenFastenerAnnuli(circuit: any[], annuli: FastenerAnnulus[]): WidenStats {
  const stats: WidenStats = { added: 0, perPour: {}, pads: [] }
  if (!annuli.length) return stats
  const by = (t: string) => circuit.filter((e) => e.type === t)
  const netById: Record<string, string> = Object.fromEntries(by("source_net").map((n) => [n.source_net_id, n.name]))
  const holes = by("pcb_plated_hole")
  for (const a of annuli) {
    const hole = holes.find((h) => (h.port_hints || []).includes(a.name))
    if (!hole) continue
    for (const pour of by("pcb_copper_pour")) {
      if (pour.shape !== "brep" || !pour.brep_shape) continue
      if (pour.layer !== "top" && pour.layer !== "bottom") continue // fasteners only touch the outer faces
      if (netById[pour.source_net_id] === a.net) continue
      const outer: Vert[] = pour.brep_shape.outer_ring?.vertices
      if (!outer?.length || !pointInPolygon(hole.x, hole.y, outer)) continue
      pour.brep_shape.inner_rings = pour.brep_shape.inner_rings || []
      pour.brep_shape.inner_rings.push(keepoutRing(hole.x, hole.y, a.rMm, a.rMm))
      stats.added++
      stats.perPour[pour.pcb_copper_pour_id] = (stats.perPour[pour.pcb_copper_pour_id] || 0) + 1
      stats.pads.push(`${a.name}→${netById[pour.source_net_id]}@${pour.layer}`)
    }
  }
  return stats
}

/**
 * The ESP32-WROOM antenna fires off the west board edge, and its keepout box (the
 * footprint's silk antenna outline, part-frame x −16.764…−10.48 at rot 0) must carry no
 * copper. The module's two GND corner pads sit only ~1.2 mm east of the box, so the
 * planes can't be pulled far back — this punches the box (carried a touch east of it,
 * stopping ~0.2 mm short of those pads) out of every pour, so no plane floods under the
 * antenna. Derived from the WROOM's placed centre (its supplier part is C701341); it
 * assumes the design's rot-0 placement (antenna due west). Returns how many pours it cut.
 */
export function antennaKeepout(circuit: any[]): number {
  const by = (t: string) => circuit.filter((e) => e.type === t)
  const sc = by("source_component").find(
    (c) => c.manufacturer_part_number === "ESP32_WROOM_32E_N4" || c.supplier_part_numbers?.jlcpcb?.includes("C701341"),
  )
  if (!sc) return 0
  const pc = by("pcb_component").find((p) => p.source_component_id === sc.source_component_id)
  if (!pc?.center) return 0
  const cx = pc.center.x, cy = pc.center.y
  // antenna box east edge is cx−10.48, the GND pad west edge ~cx−9.77; carve to cx−10.0
  // (past the box, ~0.2 mm shy of the pads) and from cx−11.5 (just off the west edge).
  const x0 = cx - 11.5, x1 = cx - 10.0, y0 = cy - 10, y1 = cy + 10
  let n = 0
  for (const pour of by("pcb_copper_pour")) {
    if (pour.shape !== "brep" || !pour.brep_shape) continue
    const outer: Vert[] = pour.brep_shape.outer_ring?.vertices
    if (!outer?.length) continue
    if (Math.min(...outer.map((v) => v.x)) > x1) continue // pour doesn't reach the antenna
    pour.brep_shape.inner_rings = pour.brep_shape.inner_rings || []
    pour.brep_shape.inner_rings.push({ vertices: [
      { x: x0, y: y0 }, { x: x1, y: y0 }, { x: x1, y: y1 }, { x: x0, y: y1 },
    ] })
    n++
  }
  return n
}

/** Drop poured fragments the solver pinched off below the fab minimum feature width — tiny
 *  floating acid-traps (a near-zero-area triangle, a sub-0.1 mm strip) left by its polygon
 *  boolean ops. Gated on BOTH thinness (2·area/perimeter) AND small area so a legitimately
 *  thin-waisted but large connected plane region is never removed; nothing this small can carry
 *  a connection (the smallest via pad is 0.5 mm). Mutates `circuit` in place, returns the count.
 *  Kept in lockstep with clearance.ts's SLIVER check — same thresholds, so the DRC reports zero
 *  once this has run. */
export function dropPourSlivers(circuit: any[], minWidthMm = 0.1, maxAreaMm2 = 0.15): number {
  const isSliver = (pour: any): boolean => {
    const verts: Vert[] = pour.brep_shape?.outer_ring?.vertices
    if (!verts) return false
    if (verts.length < 3) return true
    let area2 = 0, per = 0
    for (let i = 0, j = verts.length - 1; i < verts.length; j = i++) {
      area2 += verts[j]!.x * verts[i]!.y - verts[i]!.x * verts[j]!.y
      per += Math.hypot(verts[i]!.x - verts[j]!.x, verts[i]!.y - verts[j]!.y)
    }
    const area = Math.abs(area2) / 2
    const width = per > 0 ? Math.abs(area2) / per : 0
    return width < minWidthMm && area < maxAreaMm2
  }
  let dropped = 0
  // Splice out the sliver pours (back-to-front so indices stay valid). Removing the element is
  // safe — nothing that small connects anything — and leaves the gerber converter nothing to draw.
  for (let i = circuit.length - 1; i >= 0; i--) {
    if (circuit[i].type === "pcb_copper_pour" && isSliver(circuit[i])) { circuit.splice(i, 1); dropped++ }
  }
  return dropped
}

/** Append a widened keepout ring to every pour wherever a rule-paired foreign pad sits inside it.
 *  Mutates `circuit` in place and returns what changed. */
export function widenPourVoids(circuit: any[], rules: ClearanceRule[] = []): WidenStats {
  const by = (t: string) => circuit.filter((e) => e.type === t)
  const SP: Record<string, any> = Object.fromEntries(by("source_port").map((e) => [e.source_port_id, e]))
  const SC: Record<string, any> = Object.fromEntries(by("source_component").map((e) => [e.source_component_id, e]))
  const PP: Record<string, any> = Object.fromEntries(by("pcb_port").map((e) => [e.pcb_port_id, e]))
  const netByKey: Record<string, string> = {}
  for (const n of by("source_net")) if (n.subcircuit_connectivity_map_key) netByKey[n.subcircuit_connectivity_map_key] = n.name
  const netById: Record<string, string> = Object.fromEntries(by("source_net").map((n) => [n.source_net_id, n.name]))

  const padNet = (pad: any): string | null => {
    const pp = PP[pad.pcb_port_id]; const sp = pp && SP[pp.source_port_id]
    return sp ? (netByKey[sp.subcircuit_connectivity_map_key] ?? null) : null
  }
  const padRef = (pad: any): string => {
    const pp = PP[pad.pcb_port_id]; const sp = pp && SP[pp.source_port_id]; const sc = sp && SC[sp.source_component_id]
    return sc ? `${sc.name}.${sp.name}` : (pad.pcb_smtpad_id || pad.pcb_plated_hole_id || "?")
  }
  // victim net -> clearance for a given pour net (rules are unordered pairs)
  const victims = (net: string): Record<string, number> => {
    const r: Record<string, number> = {}
    for (const ru of rules) {
      if (ru.a === net) r[ru.b] = Math.max(r[ru.b] ?? 0, ru.clearanceMm)
      if (ru.b === net) r[ru.a] = Math.max(r[ru.a] ?? 0, ru.clearanceMm)
    }
    return r
  }

  const pads = [...by("pcb_smtpad"), ...by("pcb_plated_hole")]
  const stats: WidenStats = { added: 0, perPour: {}, pads: [] }

  for (const pour of by("pcb_copper_pour")) {
    if (pour.shape !== "brep" || !pour.brep_shape) continue
    const pourNet = netById[pour.source_net_id]; if (!pourNet) continue
    const vic = victims(pourNet); if (!Object.keys(vic).length) continue
    const outer: Vert[] = pour.brep_shape.outer_ring?.vertices; if (!outer?.length) continue
    pour.brep_shape.inner_rings = pour.brep_shape.inner_rings || []
    for (const pad of pads) {
      const net = padNet(pad); if (net == null) continue
      const clr = vic[net]; if (clr == null) continue
      if (!padOnLayer(pad, pour.layer)) continue
      if (!pointInPolygon(pad.x, pad.y, outer)) continue
      const { hx, hy } = padHalfExtent(pad)
      pour.brep_shape.inner_rings.push(keepoutRing(pad.x, pad.y, hx + clr, hy + clr))
      stats.added++
      stats.perPour[pour.pcb_copper_pour_id] = (stats.perPour[pour.pcb_copper_pour_id] || 0) + 1
      stats.pads.push(`${padRef(pad)}[${net}]→${pourNet}@${pour.layer}`)
    }
  }
  return stats
}
