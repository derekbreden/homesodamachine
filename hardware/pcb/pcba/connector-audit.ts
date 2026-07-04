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
 * BODY is the shared component-body model (component-bodies.ts): a real courtyard where the
 * footprint carries one (the USB-C, the screw terminal), else the XH wafer plastic reconstructed
 * from the pin row. So this audit and the footprint-clearance readout size a connector identically.
 *
 * AGNOSTIC to specifics beyond the universal ref-des conventions: a connector is a part named
 * `J*`, a mounting hole `MH*`. It measures each connector body's smallest gap to the board edge,
 * to every other connector body, and to the mounting-hole pads, and flags any under the target.
 */
import { collectBodies, gapRect } from "./component-bodies"

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

export function auditConnectors(circuit: any[]): ConnectorAudit {
  const { bodies: allBodies, edge, holes } = collectBodies(circuit)
  if (!edge) return { rows: [], flagged: 0, target: CONNECTOR_TARGET }
  const bodies = allBodies.filter((b) => /^J\d/.test(b.ref))

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
