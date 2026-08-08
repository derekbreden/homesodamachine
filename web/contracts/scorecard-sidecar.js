// The scorecard sidecar — <model>.scorecard.json beside a 3D STEP model, carrying the
// enclosure's requirements verdict (the same one the build prints to the terminal). Produced
// by hardware/manifold-layout/_scorecard.py::write, called at the tail of front_half.py's
// run, served path-confined by web/lib/viewer-routes.js (/api/step-scorecard/*), and read by
// web/public/js/viewer/scorecard-3d.js to draw the bottom bar + drill-down modal.
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
 * @property {ScorecardNeed} [need]  what the run CONNECTS, beside how well it turns. Optional:
 *                                   an edition whose scorecard predates the figure omits it.
 */

/**
 * @typedef {Object} ScorecardNeed  what a run connects, before what it rides
 * @property {number[][]} ends  the two endpoint waypoints, world mm
 * @property {{x: number, y: number, z: number}} axis  the ENDPOINT separation split by world
 *                             axis. It reads off the two endpoints alone, so a route that
 *                             climbs 280 mm in y and comes back reports Δy 0 — that gap between
 *                             the split and `path` is the reading, not a defect in it
 * @property {number} span     endpoint-to-endpoint distance
 * @property {number} path     developed centreline length, arcs included — the stock it cuts
 * @property {number|null} detour  path ÷ span, null where the ends coincide. A run near 1 spends
 *                             its length on its own need; far above it the run is riding
 *                             infrastructure its ends never asked for, and there the move is the
 *                             ROUTE rather than the corner — which no corner grade will say.
 *                             Near 1 is not health: a short run can be pinned at both ends and
 *                             still red, and the figure says where to look, not what to do
 */

/**
 * @typedef {Object} ScorecardMount  one component's fastening — the record behind `mounted`
 * @property {string} component
 * @property {string|null} by  the part whose printed feature fastens it; null = the joint is
 *                             still to design, and this row is one unit of the focus axis's gap
 * @property {string} held     what merely holds it today ("none" | "wall-capture" | "tray" | …).
 *                             The distance from this to `by` is the joint to print.
 * @property {string} kind     "real" | "placeholder" — the component's geometry authorship
 */

/**
 * @typedef {Object} ScorecardFocus  the two axes the work is ON, as counted things
 * @property {string} id        the check id — "bend-radius" | "mounted"
 * @property {string} label     the bar's short noun: "tube radii" | "mounted"
 * @property {number} done      how many are at spec
 * @property {number} total     how many there are
 * @property {"fail"|"warn"|"pass"} status
 */

/**
 * @typedef {Object} Scorecard
 * @property {boolean} gatesPass  every gate passes
 * @property {number} placed   0..100 — placement criteria defined and held
 * @property {number} located  0..100 — every connector positioned AND sized on the component
 * @property {number} shaped   0..100 — real geometry, not a placeholder box
 * @property {number} routed   0..100 — connections modeled as real 3D paths
 * @property {number} held     0..100 — a printed holder fastens each component
 * @property {number} [mounted]  0..100 — the feature that fastens each component is printed
 *                               INTO another placed part. Stricter than `held`, which also
 *                               counts capture and adhesive. Optional: an edition whose
 *                               scorecard predates the axis omits it, so the guard below does
 *                               not require it and a bar still draws without it.
 * @property {ScorecardCheck[]} checks
 * @property {ScorecardPort[]} ports  the full connector inventory: every port's coordinate + bore
 * @property {ScorecardShape[]} shapes  per component, the boxes it really occupies
 * @property {ScorecardBend[]} bends  per routed run, the radius it turns at and its grade
 * @property {ScorecardMount[]} mounts  per component, the part that fastens it. Optional: an
 *                                      edition whose scorecard predates the axis omits it.
 * @property {ScorecardSource} [source]  what the build read to produce this card. Optional: an
 *                                       edition whose scorecard predates the block omits it.
 */

/**
 * @typedef {Object} ScorecardSource  when the card was built, and off what HEAD
 * @property {string} generated  ISO-8601 UTC, when the build wrote this card
 * @property {string|null} commit  HEAD at build time. ORIENTATION ONLY — what the tree was at,
 *                                 not what the card was built from: nothing here fingerprints a
 *                                 file, so a dirty tree stamps exactly as a clean one. Whether
 *                                 the card still describes the tree is answered by running the
 *                                 build, and by nothing this block carries
 */

// ── Focus ────────────────────────────────────────────────────────────────────────────────────
// The two axes the work is on: `bend-radius` (a gate) and `mounted` (a goal — the live one,
// every other goal on the card being deferred). Both surfaces that render this scorecard lead
// with them, in this order.
//
// _scorecard.py's own FOCUS_IDS is the same pair, and web/tests/scorecard-focus.test.js holds
// the two to each other. A constant spelt in two files is a constant that drifts between them,
// and the drift shows up as the terminal and the viewer leading a reader with different work.
export const FOCUS_IDS = ["bend-radius", "mounted"];

// The focus axes as counted things — `done/total` read off `bends` and `mounts`. What the bar
// says, and what the modal's focus panels head with. An edition whose sidecar carries neither
// axis gets [].
export function focusAxes(sc) {
  const out = [];
  const bendCk = (sc.checks || []).find((c) => c.id === "bend-radius");
  if (bendCk && Array.isArray(sc.bends)) {
    out.push({
      id: "bend-radius", label: "tube radii", status: bendCk.status,
      done: sc.bends.reduce((n, b) => n + (b.atSpec || 0), 0),
      total: sc.bends.reduce((n, b) => n + (b.corners ? b.corners.length : 0), 0),
    });
  }
  const mountCk = (sc.checks || []).find((c) => c.id === "mounted");
  if (mountCk && Array.isArray(sc.mounts)) {
    out.push({
      id: "mounted", label: "mounted", status: mountCk.status,
      done: sc.mounts.filter((m) => m.by).length, total: sc.mounts.length,
    });
  }
  return out;
}

// The bend grades, best to worst, and the worst a run may carry and still clear the gate. Mirrors
// _scorecard.py's GRADE_BANDS / BEND_GRADE_PASS — the emitter grades, this side only reads a grade
// back to pass/short.
export const BEND_GRADES = ["A", "B", "C", "D", "F"];
export const BEND_GRADE_PASS = "B";
const short = (g) => !!g && BEND_GRADES.indexOf(g) > BEND_GRADES.indexOf(BEND_GRADE_PASS);

// A run short on `grade` and on `reachGrade` both — see the ScorecardBend typedef above for what
// the pair says. The two bodies on its ends are what a fix moves.
export function bendPinned(b) {
  return short(b.grade) && short(b.reachGrade);
}

// The runs a bend-radius fix acts on, worst first: every run with a corner under its stock's
// minimum, pinned ones ahead of the ones that are only a number to raise.
export function failingBends(sc) {
  return (sc.bends || []).filter((b) => short(b.grade))
    .sort((a, b) => Number(bendPinned(b)) - Number(bendPinned(a))
                    || a.ratio - b.ratio || a.id.localeCompare(b.id));
}

// The components with no printed feature fastening them, one row per open joint. A body already
// held by something looser sorts last — that joint is a conversion, and one nothing holds at all
// is a joint to invent.
export function unmountedComponents(sc) {
  return (sc.mounts || []).filter((m) => !m.by)
    .sort((a, b) => Number(a.held !== "none") - Number(b.held !== "none")
                    || a.component.localeCompare(b.component));
}

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
  // mounts is the per-component fastening record — the `mounted` focus axis's structured table.
  // Present on current sidecars; validated when present so an older sidecar without it still reads.
  if (o.mounts !== undefined) {
    if (!Array.isArray(o.mounts)) return false;
    const mountsOk = o.mounts.every(
      (m) =>
        m &&
        typeof m.component === "string" &&
        (m.by === null || typeof m.by === "string") &&
        typeof m.held === "string",
    );
    if (!mountsOk) return false;
  }
  return true;
}
