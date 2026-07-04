/**
 * Connector fence / edge audit — for the web viewer's Board-checks panel (folded into picks.json
 * by pick-data.ts, rendered by web/public/js/viewer/pcb.js).
 *
 * The board's layout premise is that every off-board connector sits on a labelled edge with its
 * wafer body a uniform, comfortable distance (~1 mm) from the board edge and from its neighbours —
 * so the field looms plug in without the housings fouling each other or overhanging the cut. That
 * invariant has been broken before (connector fences spaced ~0.15 mm body-to-body), and nothing
 * standing checks it: the copper DRC sees pads, not plastic. This measures the plastic.
 *
 * BODY. Each connector's keepout rect: a real courtyard OUTLINE where the footprint carries one
 * (the USB-C, the screw terminal), else — for the XH pinheaders, whose footprint courtyard is
 * pad-derived and narrower than the wafer — the true XH wafer body reconstructed from the pin
 * geometry: along the pin row the housing runs (n−1)·2.5 + 4.9 mm (2.45 mm of plastic past each
 * outer pin), and ~6.2 mm across. The along-row span — the one that governs same-edge neighbour
 * spacing, i.e. the dimension the past bug got wrong — is reconstructed exactly; the cross span is
 * a symmetric approximation of the label-tiered silk fence, plenty for a clearance proxy.
 *
 * AGNOSTIC to specifics beyond the universal ref-des conventions: a connector is a part named
 * `J*`, a mounting hole `MH*`. It measures each connector body's smallest gap to the board edge,
 * to every other connector body, and to the mounting-hole pads, and flags any under the target.
 */

export type ConnectorRow = {
  ref: string
  clearance: number   // smallest gap (mm) to edge / neighbour / mounting hole; negative = collision
  to: string          // what that nearest thing is ("board edge", another ref, ...)
  over: boolean       // clearance under target
}
export type ConnectorAudit = { rows: ConnectorRow[]; flagged: number; target: number }

// Minimum acceptable body-to-body / body-to-hole clearance (mm) before housings risk fouling.
// The design intent is >=1 mm between connector plastic and any neighbour connector or mounting
// hole (a seated wafer's shroud plus the screw head/standoff at a corner both need the room), so
// the audit flags anything under it. Edge proximity is judged separately (overhang only): a
// connector is allowed to sit AT the board edge (the USB-C opening and the screw-terminal throats
// are meant to), so only a body that actually crosses the outline is flagged.
export const CONNECTOR_TARGET = 1.0
const XH_PITCH = 2.5
const XH_END = 2.45      // plastic past each outer pin, along the row (JST-XH housing A = pitch·(n−1)+4.9)
const XH_HALF_DEPTH = 3.1 // ~half the silk fence depth, across the row (symmetric approximation)

type Rect = { minx: number; maxx: number; miny: number; maxy: number }
const gapRect = (a: Rect, b: Rect) => {
  const dx = Math.max(a.minx - b.maxx, b.minx - a.maxx, 0)
  const dy = Math.max(a.miny - b.maxy, b.miny - a.maxy, 0)
  if (dx === 0 && dy === 0) // overlap → negative penetration depth
    return -Math.min(Math.min(a.maxx, b.maxx) - Math.max(a.minx, b.minx), Math.min(a.maxy, b.maxy) - Math.max(a.miny, b.miny))
  return Math.hypot(dx, dy)
}

export function auditConnectors(circuit: any[]): ConnectorAudit {
  const sc: Record<string, string> = {}
  for (const e of circuit) if (e.type === "source_component") sc[e.source_component_id] = e.name
  const nameOf: Record<string, string> = {}
  for (const e of circuit) if (e.type === "pcb_component") nameOf[e.pcb_component_id] = sc[e.source_component_id] ?? "?"

  // board outline → its bounding rectangle (the board is a rectangle)
  const board = circuit.find((e) => e.type === "pcb_board")
  const outline: { x: number; y: number }[] = board?.outline ?? []
  if (outline.length < 3) return { rows: [], flagged: 0, target: CONNECTOR_TARGET }
  const edge: Rect = {
    minx: Math.min(...outline.map((p) => p.x)), maxx: Math.max(...outline.map((p) => p.x)),
    miny: Math.min(...outline.map((p) => p.y)), maxy: Math.max(...outline.map((p) => p.y)),
  }

  // pads + courtyards per pcb_component
  const padsByComp: Record<string, { x: number; y: number }[]> = {}
  const outlineByComp: Record<string, Rect> = {}
  const holes: { name: string; x: number; y: number; r: number }[] = []
  for (const e of circuit) {
    if (e.type === "pcb_smtpad" || e.type === "pcb_plated_hole") {
      if (typeof e.x === "number" && e.pcb_component_id) (padsByComp[e.pcb_component_id] ??= []).push({ x: e.x, y: e.y })
    }
    if (e.type === "pcb_plated_hole") {
      const hn = nameOf[e.pcb_component_id] ?? ""
      const od = e.outer_diameter ?? e.hole_diameter ?? 0
      // Mounting hole: named MH*, OR any large (>=3 mm) standalone plated hole. A bare <platedhole>
      // lands in circuit-json with no component/name, so size is the reliable tell (signal + XH pin
      // holes are <2 mm); a screw head / standoff needs clearance to a connector body like a pin does.
      if (/^MH/.test(hn) || od >= 3) holes.push({ name: hn || `MH@${e.x.toFixed(0)},${e.y.toFixed(0)}`, x: e.x, y: e.y, r: od / 2 })
    }
    if (e.type === "pcb_courtyard_outline" && e.outline?.length) {
      const xs = e.outline.map((p: any) => p.x), ys = e.outline.map((p: any) => p.y)
      outlineByComp[e.pcb_component_id] = { minx: Math.min(...xs), maxx: Math.max(...xs), miny: Math.min(...ys), maxy: Math.max(...ys) }
    }
  }

  // connector bodies (parts named J*)
  const bodies: { ref: string; rect: Rect }[] = []
  for (const [compId, name] of Object.entries(nameOf)) {
    if (!/^J\d/.test(name)) continue
    const cy = outlineByComp[compId]
    const pads = padsByComp[compId]
    let rect: Rect | null = null
    if (pads && pads.length) {
      const minx = Math.min(...pads.map((p) => p.x)), maxx = Math.max(...pads.map((p) => p.x))
      const miny = Math.min(...pads.map((p) => p.y)), maxy = Math.max(...pads.map((p) => p.y))
      // pin row = the longer pad span. An XH wafer is >=3 pads at ~2.5 mm pitch: reconstruct its
      // true housing from the pins (the imported wafer footprint carries a courtyard, but it's
      // pad-margin-inflated wider than the real plastic — this audit measures plastic-to-plastic).
      // Non-row connectors (the USB-C, the screw terminal) keep their accurate courtyard.
      const along = (maxx - minx) >= (maxy - miny) ? "x" : "y"
      const span = along === "x" ? maxx - minx : maxy - miny
      const isXhRow = pads.length >= 3 && span > 0 && Math.abs(span / (pads.length - 1) - XH_PITCH) < 0.2
      if (isXhRow || !cy) {
        rect = along === "x"
          ? { minx: minx - XH_END, maxx: maxx + XH_END, miny: miny - XH_HALF_DEPTH, maxy: maxy + XH_HALF_DEPTH }
          : { minx: minx - XH_HALF_DEPTH, maxx: maxx + XH_HALF_DEPTH, miny: miny - XH_END, maxy: maxy + XH_END }
      }
    }
    if (!rect && cy) rect = cy   // real body courtyard (USB-C, screw terminal)
    if (rect) bodies.push({ ref: name, rect })
  }

  const rows: ConnectorRow[] = []
  for (const b of bodies) {
    let best = Infinity, to = "?"
    for (const o of bodies) {
      if (o === b) continue
      const g = gapRect(b.rect, o.rect)
      if (g < best) { best = g; to = o.ref }
    }
    for (const h of holes) {
      const cx = Math.max(b.rect.minx, Math.min(h.x, b.rect.maxx)), cy = Math.max(b.rect.miny, Math.min(h.y, b.rect.maxy))
      const g = Math.hypot(h.x - cx, h.y - cy) - h.r
      if (g < best) { best = g; to = h.name }
    }
    // Edge only matters as an overhang — sitting at the edge is allowed (USB-C / screw-terminal).
    const sideMin = Math.min(b.rect.minx - edge.minx, edge.maxx - b.rect.maxx, b.rect.miny - edge.miny, edge.maxy - b.rect.maxy)
    if (sideMin < 0 && sideMin < best) { best = sideMin; to = "board edge (overhang)" }
    rows.push({ ref: b.ref, clearance: Math.round(best * 100) / 100, to, over: best < CONNECTOR_TARGET })
  }
  rows.sort((a, b) => Number(b.over) - Number(a.over) || a.clearance - b.clearance)
  return { rows, flagged: rows.reduce((n, r) => n + (r.over ? 1 : 0), 0), target: CONNECTOR_TARGET }
}
