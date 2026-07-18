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
 * @typedef {Object} Scorecard
 * @property {boolean} gatesPass  every gate passes
 * @property {number} placed   0..100 — placement criteria defined and held
 * @property {number} located  0..100 — every connector positioned AND sized on the component
 * @property {number} shaped   0..100 — real geometry, not a placeholder box
 * @property {number} routed   0..100 — connections modeled as real 3D paths
 * @property {number} held     0..100 — a printed holder fastens each component
 * @property {ScorecardCheck[]} checks
 * @property {ScorecardPort[]} ports  the full connector inventory: every port's coordinate + bore
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
  return true;
}
