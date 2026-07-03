/**
 * The shape of out/<board>.picks.json — the board sidecar the web viewer reads.
 * Produced by hardware/pcb/pcba/pick-data.ts; consumed by web/public/js/viewer/{pcb,pcb-pick,pcb-edit}.js,
 * served path-confined by web/lib/viewer-routes.js. Positions are board millimetres; the
 * viewer maps mm onto the Gerber SVG at unitsPerMm (1 mm = 1000 units).
 *
 * Identity (pads/vias/traces) is what the pad picker hit-tests. Readout (size) and checks
 * (clearance, errors, capAudit) are what the board chip and Board-checks panel show. The check
 * shapes are defined with their analyses in hardware/pcb/pcba/ — ClearancePair/BoardError in clearance.ts, CapAudit in
 * cap-audit.ts — and gathered here so the whole file has one definition.
 */
import type { ClearancePair, BoardError } from "../../hardware/pcb/pcba/clearance"
import type { CapAudit } from "../../hardware/pcb/pcba/cap-audit"

export type { ClearancePair, BoardError } from "../../hardware/pcb/pcba/clearance"
export type { CapAudit, CapAuditRow } from "../../hardware/pcb/pcba/cap-audit"

/** A pad's identity, resolved pcb_port → source_port → component; null where a pad has no port. */
export type PadIdentity = {
  ref: string | null     // component ref-des (U1, C7)
  pin: string | null     // port / pin name
  pinNum: number | null  // numeric pin, when the part numbers its pins
  net: string | null     // net name via the port's connectivity key
}

/** One pickable copper pad — a plated through-hole or an SMT pad — at a board-mm position. */
export type Pad = PadIdentity & {
  x: number
  y: number
  kind: "through-hole" | "smt-pad"
  hole?: number | null   // through-hole drill diameter (mm); absent on SMT pads
  pad: number | null     // pad outer size (mm): diameter, or width for a rect/pill
  shape: string | null
}

/** A via as a point carrying the net of its trace and the layers it hops. */
export type Via = {
  x: number
  y: number
  net: string | null
  fromLayer: string | null
  toLayer: string | null
  outer: number | null   // via pad outer diameter (mm)
}

/** A routed net as a 2D polyline between two endpoint pads; layer hops flattened away. */
export type Trace = {
  net: string | null
  from: string | null    // "REF.pin" of the start pad, when known
  to: string | null      // "REF.pin" of the end pad, when known
  width: number | null   // trace width (mm)
  points: [number, number][]  // route points, board mm
}

/** Board outer dimensions (mm), straight off the board element. */
export type BoardSize = { width: number; height: number }

/** The clearance readout on the wire — the floor and its tightest cross-net pairs.
 *  analyzeClearance also returns errors; those ride at the top level of the file. */
export type ClearanceReadout = { floor: number | null; tight: ClearancePair[] }

/** out/<board>.picks.json in full. */
export type PicksFile = {
  board: string
  unitsPerMm: number
  size: BoardSize | null
  pads: Pad[]
  vias: Via[]
  traces: Trace[]
  clearance: ClearanceReadout
  errors: BoardError[]
  capAudit: CapAudit | null
}
