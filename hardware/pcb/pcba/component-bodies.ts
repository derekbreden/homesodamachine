/**
 * Shared component-body geometry — the one physical-extent model both the connector audit and the
 * footprint-clearance readout measure against, so they never disagree about how big a part is.
 *
 * A "body" is the rectangle a placed part actually occupies, by the most accurate source available:
 *
 *   WAFER  — a JST-XH pinheader (>=3 pads at ~2.5 mm pitch). Its imported footprint DOES carry a
 *            courtyard, but that courtyard is pad-margin-inflated wider than the real plastic, so we
 *            reconstruct the true housing from the pin row instead. ALONG the row the shroud runs
 *            (n−1)·2.5 + 5.0 mm (2.5 mm of plastic past each outer pin) — exact, and it governs
 *            same-edge neighbour spacing. ACROSS the row the housing is ASYMMETRIC: the pin row sits
 *            3.5 mm from the tall mating-opening face and 2.4 mm from the base face. Every connector
 *            is placed with its opening toward the board edge it serves, so we put the 3.5 mm side
 *            toward the nearest edge and the 2.4 mm side toward the interior — matching the real
 *            plastic a neighbour (or a cross-row part like the buck) actually has to clear.
 *   COURTYARD — any other part that has a real courtyard outline (the ICs, the USB-C, the screw
 *            terminal, the battery holder): the IPC courtyard IS the body-plus-assembly extent.
 *   PADS   — a part with neither (the 0402/0603 passives carry no courtyard in circuit-json): the
 *            copper envelope, a close and slightly conservative proxy for the tiny chip body.
 *
 * `collectBodies` returns every part's body under this model, plus the board edge rect and the
 * mounting-hole pads, so a caller can measure body-to-edge / body-to-body / body-to-hole uniformly.
 */

export type Rect = { minx: number; maxx: number; miny: number; maxy: number }
export type Body = { ref: string; rect: Rect; kind: "wafer" | "courtyard" | "pads" }
export type Hole = { name: string; x: number; y: number; r: number }

// Provenance: the XUNPU WAFER-XH2.54-nPZZ parts the board sources (LCSC C5359632 4P etc.).
// PITCH and END are on the vendor spec: C5359632 lists "Pitch 2.5 mm" and "X-Length of Bottom
// Edge on Board 12.5 mm" for the 4P → 12.5 = (4−1)·2.5 + 2·2.5, i.e. 2.5 mm of plastic past each
// outer pin. OPEN/BASE (the across-row depths) are read off the imported EasyEDA footprint
// courtyard (imports/WAFER_XH2_54_4PZZ.tsx: +3.72 toward the opening, −2.70 toward the base from
// the pin row) less the ~0.25 mm pad-clearance the courtyard inflates by, giving the plastic-only
// housing depth the connector audit measures.
export const XH_PITCH = 2.5      // JST-XH pin pitch (mm)
export const XH_END = 2.5        // plastic past each outer pin, along the row (housing = pitch·(n−1)+5.0)
export const XH_OPEN_DEPTH = 3.5 // pin row -> mating-opening face, across the row (faces the board edge)
export const XH_BASE_DEPTH = 2.4 // pin row -> base face, across the row (faces the interior)

// Edge-to-edge gap between two axis-aligned rects; negative = penetration depth of an overlap.
export const gapRect = (a: Rect, b: Rect): number => {
  const dx = Math.max(a.minx - b.maxx, b.minx - a.maxx, 0)
  const dy = Math.max(a.miny - b.maxy, b.miny - a.maxy, 0)
  if (dx === 0 && dy === 0)
    return -Math.min(Math.min(a.maxx, b.maxx) - Math.max(a.minx, b.minx), Math.min(a.maxy, b.maxy) - Math.max(a.miny, b.miny))
  return Math.hypot(dx, dy)
}

export function collectBodies(circuit: any[]): { bodies: Body[]; edge: Rect | null; holes: Hole[] } {
  const sc: Record<string, string> = {}
  for (const e of circuit) if (e.type === "source_component") sc[e.source_component_id] = e.name
  const nameOf: Record<string, string> = {}
  for (const e of circuit) if (e.type === "pcb_component") nameOf[e.pcb_component_id] = sc[e.source_component_id] ?? "?"

  const board = circuit.find((e) => e.type === "pcb_board")
  const outline: { x: number; y: number }[] = board?.outline ?? []
  const edge: Rect | null = outline.length >= 3 ? {
    minx: Math.min(...outline.map((p) => p.x)), maxx: Math.max(...outline.map((p) => p.x)),
    miny: Math.min(...outline.map((p) => p.y)), maxy: Math.max(...outline.map((p) => p.y)),
  } : null

  // Copper (pads + plated holes) per component, and courtyards per component; large standalone
  // plated holes are mounting holes (a bare <platedhole> lands nameless, so size is the tell).
  const padsByComp: Record<string, { x: number; y: number }[]> = {}
  const outlineByComp: Record<string, Rect> = {}
  const holes: Hole[] = []
  for (const e of circuit) {
    if (e.type === "pcb_smtpad" || e.type === "pcb_plated_hole") {
      if (typeof e.x === "number" && e.pcb_component_id) (padsByComp[e.pcb_component_id] ??= []).push({ x: e.x, y: e.y })
    }
    if (e.type === "pcb_plated_hole") {
      const hn = nameOf[e.pcb_component_id] ?? ""
      const od = e.outer_diameter ?? e.hole_diameter ?? 0
      if (/^MH/.test(hn) || od >= 3) holes.push({ name: hn || `MH@${e.x.toFixed(0)},${e.y.toFixed(0)}`, x: e.x, y: e.y, r: od / 2 })
    }
    if (e.type === "pcb_courtyard_outline" && e.outline?.length) {
      const xs = e.outline.map((p: any) => p.x), ys = e.outline.map((p: any) => p.y)
      outlineByComp[e.pcb_component_id] = { minx: Math.min(...xs), maxx: Math.max(...xs), miny: Math.min(...ys), maxy: Math.max(...ys) }
    }
  }

  const bodies: Body[] = []
  for (const [compId, name] of Object.entries(nameOf)) {
    const cy = outlineByComp[compId]
    const pads = padsByComp[compId]
    if (pads?.length) {
      const minx = Math.min(...pads.map((p) => p.x)), maxx = Math.max(...pads.map((p) => p.x))
      const miny = Math.min(...pads.map((p) => p.y)), maxy = Math.max(...pads.map((p) => p.y))
      const along = maxx - minx >= maxy - miny ? "x" : "y"
      const span = along === "x" ? maxx - minx : maxy - miny
      const isXhRow = pads.length >= 3 && span > 0 && Math.abs(span / (pads.length - 1) - XH_PITCH) < 0.2
      if (isXhRow) {
        // Across-row depth is asymmetric: the 3.5 mm mating-opening face points at the nearest board
        // edge (every connector is seated that way), the 2.4 mm base face at the interior.
        let rect: Rect
        if (along === "x") {   // horizontal row -> N/S edge; opening is +y (north) or -y (south)
          const openNorth = !edge || (edge.maxy - maxy) <= (miny - edge.miny)
          rect = { minx: minx - XH_END, maxx: maxx + XH_END,
                   miny: miny - (openNorth ? XH_BASE_DEPTH : XH_OPEN_DEPTH),
                   maxy: maxy + (openNorth ? XH_OPEN_DEPTH : XH_BASE_DEPTH) }
        } else {               // vertical row -> E/W edge; opening is +x (east) or -x (west)
          const openEast = !edge || (edge.maxx - maxx) <= (minx - edge.minx)
          rect = { minx: minx - (openEast ? XH_BASE_DEPTH : XH_OPEN_DEPTH),
                   maxx: maxx + (openEast ? XH_OPEN_DEPTH : XH_BASE_DEPTH),
                   miny: miny - XH_END, maxy: maxy + XH_END }
        }
        bodies.push({ ref: name, kind: "wafer", rect })
        continue
      }
      if (cy) { bodies.push({ ref: name, kind: "courtyard", rect: cy }); continue }
      bodies.push({ ref: name, kind: "pads", rect: { minx, maxx, miny, maxy } })
      continue
    }
    if (cy) bodies.push({ ref: name, kind: "courtyard", rect: cy })
  }
  return { bodies, edge, holes }
}
