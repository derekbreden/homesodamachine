/**
 * pour-clearance.ts — net-class clearance over the exported circuit-json, the seam pretty-router
 * works in. A pour declares it on the board, beside its outline:
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
