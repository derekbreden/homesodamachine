// The scorecard sidecar — <model>.scorecard.json beside a 3D STEP model, carrying the
// enclosure's requirements verdict (the same one the build prints to the terminal). Produced
// by hardware/manifold-layout/_scorecard.py::write, called at the tail of enclosure_assembly.py's
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
 * @typedef {Object} ScorecardSize  one population's outside dimensions, measured off its solids
 * @property {string} id      "enclosure" (the printed box) | "assembly" (everything placed)
 * @property {string} label   what the row measures, in words
 * @property {number[]} min   [x, y, z] world mm, the low corner of the box it stands in
 * @property {number[]} max   [x, y, z] world mm, the high corner
 * @property {number[]} mm    [width, depth, height] — max − min, on the axes the pack uses.
 *                            The measurement; inches come out of `inches()` below
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
 * @typedef {Object} ScorecardBend  one drawn line, and every corner in it graded separately
 * @property {string} id        the line's connection id. `_scenes.core_names` reads this off
 *                              every row for the cold core's own line names.
 * @property {string} kind      fluid | water | co2 | refrigerant
 * @property {string} frm       source port anchor, "component.port"
 * @property {string} to        destination port anchor — the two bodies a fix would move
 * @property {string} stock     the tube it is drawn in, which is what sets `minBend`
 * @property {number} od        the line's bore Ø mm
 * @property {number} length    developed centreline length, arcs included
 * @property {number} bend      the ceiling its author set; corners rise to what their legs seat
 *                              and stop here
 * @property {number} radius    the TIGHTEST corner in the line. A line holds one radius per
 *                              corner, so this is its worst and says nothing about the rest —
 *                              read `corners` for that.
 * @property {number} minBend   the tightest radius that stock takes without kinking
 * @property {number} ratio     radius / minBend
 * @property {string|null} grade  A..F on `ratio`, or null for a line with no corner to grade
 * @property {ScorecardCorner[]} corners  every interior corner with its own radius and grade
 * @property {number|null} reach largest radius its INTERIOR legs seat — the ceiling the pack
 *                               imposes, leads excluded. null = no interior leg bounds it.
 * @property {string|null} reachGrade  A..F on reach / minBend. Failing BOTH grades is a
 *                                     placement to move; failing only `grade` is a radius to
 *                                     raise.
 * @property {{leg: number, length: number, demand: number, from: number[], to: number[]}|null}
 *           binding  the interior leg that sets `reach`: its index, its length, the tangent it
 *                    owes as a multiple of R, and its two endpoints in world mm
 * @property {ScorecardNeed} [need]  what the line CONNECTS, beside how well it turns. Optional:
 *                                   a scorecard predating the figure omits it.
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
 * @typedef {Object} Scorecard
 * @property {boolean} gatesPass  every gate passes
 * @property {ScorecardSize[]} [size]  how big the thing is: the printed box, and everything
 *                               placed. Optional: a scorecard predating the table omits it,
 *                               and the card draws without a size block
 * @property {ScorecardCheck[]} checks
 * @property {string[]} [bodies]  every body the assembly places, by name. Optional: the cold
 *                               core's card carries it for `_scenes.core_names`
 * @property {ScorecardBend[]} [bends]  per routed run, the radius it turns at and its grade.
 *                               Optional: the cold core's card carries it for
 *                               `_scenes.core_names`, and a card whose bend grades ride their
 *                               own check's detail omits it.
 *
 * A run's corner grades reach a reader through the `bend-radius` check's own detail, and every
 * body's fastening through `mounted`'s.
 *
 * EVERY FIELD IS A READING, and there is no build stamp — one tree writes one file however
 * often it is built, so a card that comes back changed is a card whose numbers moved. What the
 * build could reach is what `BUILD.bazel` declares as the action's inputs instead.
 */

// ── Size ─────────────────────────────────────────────────────────────────────────────────────
// The sidecar carries millimetres, one triple per population. Inches are divided out here, for
// the reader who holds the machine rather than the model — _scorecard.py's `report` divides the
// same way for the terminal.
export const MM_PER_INCH = 25.4;

// One size row in both units: "223.0 × 474.0 × 358.0 mm · 8.78 × 18.66 × 14.09 in".
export function sizeText(row) {
  const mm = (row && row.mm) || [];
  return `${mm.map((v) => v.toFixed(1)).join(" × ")} mm · `
       + `${mm.map((v) => (v / MM_PER_INCH).toFixed(2)).join(" × ")} in`;
}

// True when `o` has the shape the viewer reads. Used by the conformance test and as a client
// guard — a malformed sidecar draws no bar rather than throwing.
export function isScorecard(o) {
  if (!o || typeof o !== "object") return false;
  if (typeof o.gatesPass !== "boolean") return false;
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
  // size is the measured outside of the printed box and of the whole assembly. Present on
  // current sidecars; validated when present so an older sidecar without it still reads.
  if (o.size !== undefined) {
    if (!Array.isArray(o.size)) return false;
    const triple = (v) => Array.isArray(v) && v.length === 3 && v.every((n) => typeof n === "number");
    const sizeOk = o.size.every(
      (s) =>
        s &&
        typeof s.id === "string" &&
        typeof s.label === "string" &&
        triple(s.min) && triple(s.max) && triple(s.mm),
    );
    if (!sizeOk) return false;
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
