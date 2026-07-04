/**
 * Footprint (component-body) clearance readout — the body-to-body sibling of the copper clearance
 * floor, for the web viewer's Board-checks panel (folded into picks.json by pick-data.ts).
 *
 * clearance.ts measures COPPER — the smallest gap between pads/traces/vias on different nets. That
 * is what shorts a board, but it is blind to the other way two parts collide: their PHYSICAL BODIES
 * (courtyard / plastic / package) fouling each other even when their copper clears. A cap tucked
 * under a JST wafer, two SOICs whose packages kiss, a regression that nudges one part into its
 * neighbour — copper DRC passes, and nothing standing catches it. This measures the bodies.
 *
 * Each part's body is the shared component-body model (component-bodies.ts) — courtyard where the
 * footprint has one, reconstructed plastic for the XH wafers, copper envelope for the bare passives
 * — so a connector reads the same size here as in the connector audit. It reports the FLOOR (the
 * single tightest body-to-body gap on the board) and the tightest few pairs, exactly as the copper
 * readout does. It is informational, not a flag: a true body OVERLAP already surfaces as a red
 * pcb_courtyard_overlap_error, and dense-but-fine SMD (courtyards carry IPC assembly margin, so a
 * 0.4 mm courtyard gap is ~0.9 mm of real package air, well within the fab's ~0.2 mm placement) is
 * expected on a packed board — the point is visibility into how close the closest bodies sit.
 */
import { collectBodies, gapRect } from "./component-bodies"

export type FootprintPair = { gap: number; a: string; b: string }
export type FootprintAudit = { floor: number | null; tight: FootprintPair[] }

const AABB_CAP = 2.0 // ignore a pair whose bodies are farther apart than this (mm) — cheap prefilter
const TIGHT_MAX = 8  // how many of the tightest body pairs to keep for the readout

export function auditFootprints(circuit: any[]): FootprintAudit {
  const { bodies } = collectBodies(circuit)
  let floor = Infinity
  const pairs: FootprintPair[] = []
  for (let i = 0; i < bodies.length; i++) {
    for (let j = i + 1; j < bodies.length; j++) {
      const a = bodies[i].rect, b = bodies[j].rect
      if (a.minx > b.maxx + AABB_CAP || b.minx > a.maxx + AABB_CAP || a.miny > b.maxy + AABB_CAP || b.miny > a.maxy + AABB_CAP) continue
      const g = gapRect(a, b)
      if (g < floor) floor = g
      pairs.push({ gap: Math.round(g * 1000) / 1000, a: bodies[i].ref, b: bodies[j].ref })
    }
  }
  pairs.sort((x, y) => x.gap - y.gap)
  return { floor: isFinite(floor) ? Math.round(floor * 1000) / 1000 : null, tight: pairs.slice(0, TIGHT_MAX) }
}
