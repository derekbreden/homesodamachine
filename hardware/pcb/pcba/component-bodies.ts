/**
 * Shared component-body geometry — the one physical-extent model both the connector audit and the
 * footprint-clearance readout measure against, so they never disagree about how big a part is.
 *
 * A "body" is the rectangle a placed part actually occupies, by the most accurate source available:
 *
 *   WAFER  — a JST-XH pinheader (>=3 pads at ~2.5 mm pitch). Its imported footprint DOES carry a
 *            courtyard, but that courtyard is pad-margin-inflated wider than the real plastic, so we
 *            reconstruct the true housing from the pin row instead: along the row the shroud runs
 *            (n−1)·2.5 + 4.9 mm (2.45 mm of plastic past each outer pin), ~6.2 mm across. The
 *            along-row span — the one that governs same-edge neighbour spacing — is exact; the cross
 *            span is a symmetric approximation of the label-tiered silk fence, plenty as a proxy.
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

export const XH_PITCH = 2.5      // JST-XH pin pitch (mm)
export const XH_END = 2.45       // plastic past each outer pin, along the row (housing A = pitch·(n−1)+4.9)
export const XH_HALF_DEPTH = 3.1 // ~half the silk fence depth, across the row (symmetric approximation)

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
        bodies.push({ ref: name, kind: "wafer", rect: along === "x"
          ? { minx: minx - XH_END, maxx: maxx + XH_END, miny: miny - XH_HALF_DEPTH, maxy: maxy + XH_HALF_DEPTH }
          : { minx: minx - XH_HALF_DEPTH, maxx: maxx + XH_HALF_DEPTH, miny: miny - XH_END, maxy: maxy + XH_END } })
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
