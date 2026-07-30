// The scorecard sidecar — <model>.scorecard.json beside a 3D STEP model, carrying the
// enclosure's requirements verdict (the same one the build prints to the terminal). Produced
// by hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py::scorecard_dict (written
// in enclosure_assembly.py), served path-confined by web/lib/viewer-routes.js
// (/api/step-scorecard/*), and read by web/public/js/viewer/scorecard-3d.js to draw the
// bottom bar + drill-down modal.
//
// One verdict, two surfaces: this file is the contract between the Python emitter and the JS
// viewer. web/tests/scorecard-sidecar.test.js asserts the committed sidecar conforms.

export const SCORECARD_SUFFIX = ".scorecard.json";

// A STEP path -> its scorecard sidecar path (both root-relative). The viewer derives the
// sidecar to fetch from the model it is opening.
export function scorecardPathFor(stepPath) {
  return stepPath.replace(/\.step$/, SCORECARD_SUFFIX);
}

// Request-confinement for the served route: the param must name a *.scorecard.json.
export const SCORECARD_REQUEST_RE = /\.scorecard\.json$/;

/**
 * @typedef {Object} ScorecardCheck
 * @property {string} id
 * @property {string} label
 * @property {"gate"|"goal"} kind
 * @property {"pass"|"fail"|"warn"} status
 * @property {string} value    what the design is (the measurement)
 * @property {string} target   what it must be (the requirement)
 * @property {string[]} detail  offending / itemized rows
 * @property {boolean} active   goal axes only: false = deferred (rendered gray)
 */

/**
 * @typedef {Object} ScorecardShape  one component's real boxes — the shape record behind `shaped`
 * @property {string} component
 * @property {number[][]} boxes  one [xmin, ymin, zmin, xmax, ymax, zmax] per solid the component
 *                               is built from. The single box drawn around all of them is a
 *                               different object, and for a hollow or L-shaped body mostly air.
 * @property {number} fill       material volume over the boxes' volume; 1.0 = the boxes are the part
 * @property {boolean} primitive  the geometry is still a bare box or cylinder
 * @property {string} declared   what the component registry claims: "real" | "placeholder"
 */

/**
 * @typedef {Object} ScorecardPort  one connector in the audit-readable inventory
 * @property {string} component  the component name it sits on
 * @property {string} name       connector id, unique within its component
 * @property {"fluid"|"refrigerant"|"electrical"} kind
 * @property {number[]|null} pos [x, y, z] world mm, or null = not yet located
 * @property {string} face       body face it exits: x-/x+/y-/y+/z-/z+ ("" when unlocated)
 * @property {number|null} diam  nominal bore Ø mm (the mating dimension), or null = not yet sized
 * @property {string} mates      the other end, human-readable
 * @property {"ok"|"off-surface"|"no-pos"|"no-diam"} status
 * @property {string} note
 */

/**
 * @typedef {Object} ScorecardCorner  one interior corner, graded on the radius IT turns at
 * @property {number} at      the corner's waypoint index along the run
 * @property {number} turn    how far it deflects, degrees
 * @property {number} radius  the radius this corner seats — the largest its own two legs hold,
 *                            up to the cap its author set
 * @property {number} ratio   radius / minBend
 * @property {string} grade   A..F on `ratio`
 * @property {number[]} legs  the two leg lengths it sits between, mm
 */

/**
 * @typedef {Object} ScorecardBend  one routed run, and every corner in it graded separately
 * @property {string} id        the run's connection id
 * @property {string} kind      fluid | water | co2 | refrigerant
 * @property {string} frm       source port anchor, "component.port"
 * @property {string} to        destination port anchor — the two bodies a fix would move
 * @property {string} stock     the tube it is drawn in, which is what sets `minBend`
 * @property {number} od        the run's bore Ø mm
 * @property {number} radius    the TIGHTEST corner in the run. A run holds one radius per corner,
 *                              so this is its worst and says nothing about the rest — read
 *                              `corners` for that.
 * @property {number} cap       the ceiling its author set; corners rise to what their legs seat
 *                              and stop here
 * @property {number} minBend   the tightest radius that stock takes without kinking
 * @property {number} ratio     radius / minBend
 * @property {string|null} grade  A..F on `ratio`, or null for a run with no corner to grade
 * @property {ScorecardCorner[]} corners  every interior corner with its own radius and grade
 * @property {number} atSpec    how many of those corners are at or above `minBend`
 * @property {number} bends     interior corners
 * @property {number|null} worstTurn  the sharpest turn in degrees, null when straight
 * @property {number|null} seat  largest radius the centreline as drawn seats, every leg counted
 * @property {number|null} reach largest radius its INTERIOR legs seat — the ceiling the pack
 *                               imposes, leads excluded. null = no interior leg bounds it.
 * @property {number|null} reachRatio  reach / minBend
 * @property {string|null} reachGrade  A..F on `reachRatio`. Failing BOTH grades is a placement
 *                                     to move; failing only `grade` is a radius to raise.
 * @property {{leg: number, length: number, demand: number, from: number[], to: number[]}|null}
 *           binding  the interior leg that sets `reach`: its index, its length, the tangent it
 *                    owes as a multiple of R, and its two endpoints in world mm
 */

/**
 * @typedef {Object} Scorecard
 * @property {boolean} gatesPass  every gate passes
 * @property {number} placed   0..100 — placement criteria defined and held
 * @property {number} located  0..100 — every connector positioned AND sized on the component
 * @property {number} shaped   0..100 — real geometry, not a placeholder box
 * @property {number} routed   0..100 — connections modeled as real 3D paths
 * @property {number} held     0..100 — a printed holder fastens each component
 * @property {ScorecardCheck[]} checks
 * @property {ScorecardPort[]} ports  the full connector inventory: every port's coordinate + bore
 * @property {ScorecardShape[]} shapes  per component, the boxes it really occupies
 * @property {ScorecardBend[]} bends  per routed run, the radius it turns at and its grade
 */

// True when `o` has the shape the viewer reads. Used by the conformance test and as a client
// guard — a malformed sidecar draws no bar rather than throwing.
export function isScorecard(o) {
  if (!o || typeof o !== "object") return false;
  if (typeof o.gatesPass !== "boolean") return false;
  for (const k of ["placed", "located", "shaped", "routed", "held"]) {
    if (typeof o[k] !== "number") return false;
  }
  if (!Array.isArray(o.checks)) return false;
  const checksOk = o.checks.every(
    (c) =>
      c &&
      typeof c.label === "string" &&
      (c.kind === "gate" || c.kind === "goal") &&
      (c.status === "pass" || c.status === "fail" || c.status === "warn") &&
      typeof c.value === "string" &&
      Array.isArray(c.detail),
  );
  if (!checksOk) return false;
  // ports is the connector inventory. Present on current sidecars; validated when present so an
  // older sidecar without it still reads (draws the bar, just no port table).
  if (o.ports !== undefined) {
    if (!Array.isArray(o.ports)) return false;
    const portsOk = o.ports.every(
      (p) =>
        p &&
        typeof p.component === "string" &&
        typeof p.name === "string" &&
        (p.pos === null || (Array.isArray(p.pos) && p.pos.length === 3 && p.pos.every((n) => typeof n === "number"))) &&
        (p.diam === null || typeof p.diam === "number") &&
        typeof p.mates === "string" &&
        typeof p.status === "string",
    );
    if (!portsOk) return false;
  }
  // shapes is the per-component box record. Present on current sidecars; validated when present
  // so an older sidecar without it still reads.
  if (o.shapes !== undefined) {
    if (!Array.isArray(o.shapes)) return false;
    const shapesOk = o.shapes.every(
      (s) =>
        s &&
        typeof s.component === "string" &&
        Array.isArray(s.boxes) &&
        s.boxes.every((b) => Array.isArray(b) && b.length === 6 && b.every((n) => typeof n === "number")) &&
        typeof s.fill === "number" &&
        typeof s.primitive === "boolean",
    );
    if (!shapesOk) return false;
  }
  // bends is the per-run bend-radius grading. Present on current sidecars; validated when
  // present so an older sidecar without it still reads.
  if (o.bends !== undefined) {
    if (!Array.isArray(o.bends)) return false;
    const bendsOk = o.bends.every(
      (b) =>
        b &&
        typeof b.id === "string" &&
        typeof b.stock === "string" &&
        typeof b.radius === "number" &&
        typeof b.minBend === "number" &&
        typeof b.ratio === "number" &&
        (b.grade === null || typeof b.grade === "string") &&
        (b.reach === null || typeof b.reach === "number") &&
        (b.reachGrade === null || typeof b.reachGrade === "string") &&
        (b.binding === null ||
          (b.binding && typeof b.binding.leg === "number" && typeof b.binding.length === "number")),
    );
    if (!bendsOk) return false;
  }
  return true;
}
