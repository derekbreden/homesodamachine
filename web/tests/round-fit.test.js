import { test } from "node:test";
import assert from "node:assert/strict";

import {
  ARC_FIT_LENGTH_REL,
  ROUND_FIT_MIN_SWEEP_DEG,
  ROUND_FIT_RESIDUAL_MAX_MM,
  arcFitMeasured,
  roundFitMeasured,
} from "../public/js/viewer/round-fit.js";

const chord = (radius, degrees) => 2 * radius * Math.sin(degrees * Math.PI / 360);

test("accepts measured arcs within the absolute residual cap", () => {
  assert.equal(roundFitMeasured(3, chord(3, 90), 0.05), true);
  assert.equal(roundFitMeasured(87, chord(87, 2.58), 0.372), true);
  assert.equal(ROUND_FIT_RESIDUAL_MAX_MM, 0.5);
});

test("rejects the 6.25-metre cylinder fit as unmeasured curvature", () => {
  // The old 2%-of-radius rule allowed 124.98 mm of residual here.
  assert.equal(roundFitMeasured(6249.043, 28.092, 0.4), false);
});

test("rejects a nearly perfect giant-radius fit too", () => {
  // An absolute residual cap is necessary but cannot reject this by itself.
  assert.equal(roundFitMeasured(246302, 100, 0.016), false);
});

test("caps residual independently of radius", () => {
  assert.equal(roundFitMeasured(100, chord(100, 20), 0.5), true);
  assert.equal(roundFitMeasured(100, chord(100, 20), 0.500001), false);
});

test("holds the sweep boundary and refuses non-finite inputs", () => {
  assert.equal(roundFitMeasured(10, chord(10, ROUND_FIT_MIN_SWEEP_DEG), 0), true);
  assert.equal(roundFitMeasured(10, chord(10, ROUND_FIT_MIN_SWEEP_DEG - 0.01), 0), false);
  assert.equal(roundFitMeasured(Infinity, 10, 0), false);
  assert.equal(roundFitMeasured(10, NaN, 0), false);
  assert.equal(roundFitMeasured(10, 10, NaN), false);
});

// Vectors measured off hardware/manifold-layout/enclosure-assembly.step.mesh at
// station 69 — the fits the policy actually has to sort, rather than synthetic
// boundary cases. Radii in mm, chord in the axis-normal plane, residual
// vertex-to-circle.
test("sorts the real fits in the assembly payload", () => {
  // Giant radii off patches that never swept. The worst sit at a residual near
  // zero, so the cap cannot reach them and only the sweep test rejects them.
  assert.equal(roundFitMeasured(246301.7, 190.96, 0.0160), false); // foam-shell, 0.044°
  assert.equal(roundFitMeasured(200849.6, 134.89, 0.0063), false); // front-top, 0.038°
  assert.equal(roundFitMeasured(100948.8, 160.51, 0.0284), false); // front-bottom
  assert.equal(roundFitMeasured(14011.6, 105.15, 0.0121), false);  // foam-cap-bottom

  // These two sweep plenty — 27.7° and 180° — but their vertices do not lie on
  // a circle. A cone fit explains none of it (R² 0.0007 and 0.0000, and the
  // residual survives detrending), so they are not tapers either: they are
  // non-circular faces, and `curved` is the true report for both.
  assert.equal(roundFitMeasured(92.291, 44.14, 0.8899), false);
  assert.equal(roundFitMeasured(86.007, 174.50, 0.9459), false);

  // Genuine arcs, down to the C14 tunnel block's own r=3 corner.
  assert.equal(roundFitMeasured(43.181, 4.74, 0.0), true);
  assert.equal(roundFitMeasured(41.160, 22.56, 0.1635), true);
  assert.equal(roundFitMeasured(18.900, 53.46, 0.0), true);
  assert.equal(roundFitMeasured(3.0, 4.24, 0.0), true);
});

// --- arcFitMeasured: an arc has to account for the path actually walked ---
//
// THE FIXTURE IS A REAL PICK. Derek clicked what looked like two thin protrusions on
// back-top's +X flank and the viewer handed him
//
//   x=98.300 y=244.495 z=257.099 → x=98.500 y=244.461 z=257.422 · len 142.065
//                                · arc r=35.657 · center x=100.116 y=279.995 z=259.902
//
// — two endpoints 0.381 mm apart on an arc of 142 mm. No single arc is both. The chain was
// two straight segments bridging a collapsed 0.25 mm feature in the decimated payload, and
// `fitCircle` drew a circumcircle through three points that were very nearly two. Every
// reader downstream then reasoned from a radius and a centre that were never measured.

test("rejects the back-top payload chain that was reported as an arc", () => {
  assert.equal(arcFitMeasured(35.657, 0.381, 142.065), false);
});

test("accepts a real minor arc, on the length its chord and radius predict", () => {
  // A quarter round of R3: chord 4.243, path 4.712.
  assert.equal(arcFitMeasured(3, chord(3, 90), 3 * Math.PI / 2), true);
  assert.equal(arcFitMeasured(35.657, chord(35.657, 30), 35.657 * Math.PI / 6), true);
});

test("accepts the major arc, which shares its chord with the minor one", () => {
  // A rim that nearly closes: ends 0.381 mm apart and the whole circle walked between them.
  const r = 35.657;
  assert.equal(arcFitMeasured(r, 0.381, 2 * Math.PI * r - 0.381), true);
});

test("holds the length tolerance where it is stated", () => {
  const r = 20, deg = 60;
  const exact = r * deg * Math.PI / 180;
  const c = chord(r, deg);
  assert.equal(arcFitMeasured(r, c, exact * (1 + ARC_FIT_LENGTH_REL * 0.9)), true);
  assert.equal(arcFitMeasured(r, c, exact * (1 + ARC_FIT_LENGTH_REL * 4)), false);
});

test("refuses a chord that cannot lie on the circle, and non-finite input", () => {
  assert.equal(arcFitMeasured(2, 9, 5), false);
  assert.equal(arcFitMeasured(NaN, 1, 1), false);
  assert.equal(arcFitMeasured(3, 1, 0), false);
});
