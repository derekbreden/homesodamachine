/**
 * The shape of out/<board>.picks.json — the board sidecar the web viewer reads.
 * Produced by hardware/pcb/pcba/pick-data.ts; consumed by web/public/js/viewer/{pcb,pcb-pick,pcb-edit}.js,
 * served path-confined by web/lib/viewer-routes.js. Positions are board millimetres; the
 * viewer maps mm onto the Gerber SVG at unitsPerMm (1 mm = 1000 units).
 *
 * Identity (pads/vias/traces) is what the pad picker hit-tests. Readout (size, fab) and checks
 * (clearance, errors, capAudit, connectors, footprints, ampacity) are what the board chip and
 * Board-checks panel show. The check shapes are defined with their analyses in hardware/pcb/pcba/ —
 * ClearancePair/BoardError in clearance.ts, CapAudit in cap-audit.ts, ConnectorAudit in
 * connector-audit.ts, FootprintAudit in footprint-audit.ts, AmpacityAudit in ampacity-audit.ts —
 * and gathered here so the whole file has one definition. (Fab is a plain readout with no analysis
 * of its own, so it's defined inline.)
 */
import type { ClearancePair, BoardError } from "../../hardware/pcb/pcba/clearance"
import type { CapAudit } from "../../hardware/pcb/pcba/cap-audit"
import type { ConnectorAudit } from "../../hardware/pcb/pcba/connector-audit"
import type { FootprintAudit } from "../../hardware/pcb/pcba/footprint-audit"
import type { AmpacityAudit } from "../../hardware/pcb/pcba/ampacity-audit"
import type { Scorecard } from "../../hardware/pcb/pcba/scorecard"

export type { ClearancePair, BoardError } from "../../hardware/pcb/pcba/clearance"
export type { CapAudit, CapAuditRow, CoverageGap } from "../../hardware/pcb/pcba/cap-audit"
export type { ConnectorAudit, ConnectorRow } from "../../hardware/pcb/pcba/connector-audit"
export type { FootprintAudit, FootprintPair } from "../../hardware/pcb/pcba/footprint-audit"
export type { AmpacityAudit, AmpacityRow } from "../../hardware/pcb/pcba/ampacity-audit"
export type { Scorecard, Check } from "../../hardware/pcb/pcba/scorecard"

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

/** Manufacturability readout: BOM sourcing + the tightest drill/annular the fab must hit. */
export type FabStats = {
  layers: number | null
  partsSourced: { sourced: number; total: number }
  unsourced: string[]              // ref-des of placed parts carrying no JLCPCB #
  minDrillMm: number | null
  minAnnularMm: number | null      // overall min ring (min of the two below) — the readout number
  minViaAnnularMm: number | null   // tightest via ring (JLCPCB via floor 0.1 mm)
  minPadAnnularMm: number | null   // tightest THT-pad ring (JLCPCB pad floor 0.13 mm)
}

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
  connectors: ConnectorAudit
  footprints: FootprintAudit
  ampacity: AmpacityAudit | null
  fab: FabStats
  scorecard: Scorecard   // the requirements verdict — gate checks + manual-routing progress
}
