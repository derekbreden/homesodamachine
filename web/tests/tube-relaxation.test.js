import { test } from 'node:test';
import assert from 'node:assert/strict';
import { relaxTube } from '../public/js/viewer/tube-relaxation.js';

const distance = (a, b) => Math.hypot(...a.map((v, k) => v - b[k]));
const length = points => points.slice(1).reduce((sum, p, i) => sum + distance(p, points[i]), 0);
const sRoute = { points: [[0, 0, 0], [60, 0, 0], [60, 60, 0], [120, 60, 0]], minBendRadiusMm: 14 };
const arch = { points: Array.from({ length: 61 }, (_, i) => [150 * i / 60, 0, 40 * Math.sin(Math.PI * i / 60)]) };
const assertLengths = result => {
  assert.ok(Math.abs(result.diagnostics.lengthErrorMm) < 0.001);
  assert.ok(result.diagnostics.maxSegmentErrorMm < 0.0001);
  for (let i = 1; i < result.points.length; i++) {
    assert.ok(Math.abs(distance(result.points[i], result.points[i - 1]) -
      (result.arcLengths[i] - result.arcLengths[i - 1])) < 0.0001);
  }
};
const at = (result, s) => {
  let i = result.arcLengths.findIndex(value => value >= s);
  if (i <= 0) return result.points[Math.max(0, i)];
  const t = (s - result.arcLengths[i - 1]) / (result.arcLengths[i] - result.arcLengths[i - 1]);
  return result.points[i].map((v, k) => result.points[i - 1][k] + t * (v - result.points[i - 1][k]));
};
const roundedPolyline = (waypoints, radius) => {
  const points = [waypoints[0]], arcLengths = [0];
  const unit = v => { const length = Math.hypot(...v); return v.map(x => x / length); };
  const dot = (a, b) => a.reduce((sum, v, k) => sum + v * b[k], 0);
  const append = (end, length, curve) => {
    const start = points.at(-1), s = arcLengths.at(-1), count = Math.ceil(length / 4);
    for (let i = 1; i <= count; i++) {
      const t = i / count;
      points.push(curve ? curve(t) : start.map((v, k) => v + t * (end[k] - v)));
      arcLengths.push(s + t * length);
    }
  };
  for (let i = 1; i < waypoints.length - 1; i++) {
    const p = waypoints[i], a = unit(p.map((v, k) => v - waypoints[i - 1][k]));
    const b = unit(waypoints[i + 1].map((v, k) => v - p[k]));
    const theta = Math.acos(dot(a, b)), trim = radius * Math.tan(theta / 2);
    const start = p.map((v, k) => v - trim * a[k]), end = p.map((v, k) => v + trim * b[k]);
    const normal = unit(b.map((v, k) => v - dot(a, b) * a[k]));
    const center = start.map((v, k) => v + radius * normal[k]);
    append(start, distance(points.at(-1), start));
    append(end, radius * theta, t => center.map((v, k) => v + radius *
      (-normal[k] * Math.cos(theta * t) + a[k] * Math.sin(theta * t))));
  }
  append(waypoints.at(-1), distance(points.at(-1), waypoints.at(-1)));
  return { points, arcLengths };
};

test('a taut span stays straight even under an assumed coil memory', () => {
  for (const scenario of ['straight', 'coil-positive', 'coil-negative']) {
    const result = relaxTube({ points: [[0, 0, 0], [100, 0, 0]] }, { scenario });
    assert.equal(result.diagnostics.converged, true);
    assert.ok(result.diagnostics.maxDisplacementMm < 1e-10);
    assert.equal(result.diagnostics.minRadiusMm, null);
    assertLengths(result);
  }
});

test('CAD corners relax while fittings keep their positions and exit directions', () => {
  const result = relaxTube(sRoute);
  assert.equal(result.diagnostics.converged, true);
  assert.deepEqual(result.points[0], sRoute.points[0]);
  assert.deepEqual(result.points.at(-1), sRoute.points.at(-1));
  assert.equal(result.points[1][1], 0);
  assert.equal(result.points.at(-2)[1], 60);
  assert.ok(distance(at(result, 60), sRoute.points[1]) > 1);
  assert.ok(result.diagnostics.bendingEnergy < result.diagnostics.initialBendingEnergy / 2);
  assertLengths(result);
});

test('only actual holds constrain interior points, and omitting a hold changes the solution', () => {
  const run = { ...sRoute, holds: [{ s: 60, id: 'cap-tie', label: 'Cap tie' }] };
  const retained = relaxTube(run), released = relaxTube(run, { omitHoldId: 'cap-tie' });
  assert.equal(retained.diagnostics.converged, true);
  assert.deepEqual(at(retained, 60), [60, 0, 0]);
  assert.ok(distance(at(released, 60), [60, 0, 0]) > 1);
  assert.equal(retained.spans.length, 2);
  assert.equal(released.spans.length, 1);
  assert.equal(retained.spans[0].slackMm, 0);
  assertLengths(retained);
  // An optional id is not a requirement for a physical hold to take effect.
  assert.deepEqual(at(relaxTube({ ...sRoute, holds: [{ s: 60 }] }), 60), [60, 0, 0]);
});

test('a finite straight grip retains its whole length', () => {
  const result = relaxTube({ ...sRoute,
    holds: [{ s: 90, id: 'saddle', tangent: [0, 1, 0], clampLengthMm: 12 }] });
  for (const s of [84, 87, 90, 93, 96]) assert.ok(distance(at(result, s), [60, s - 60, 0]) < 1e-8);
  assertLengths(result);
});

test('exact CAD arc parameters preserve developed length beyond sampled chords', () => {
  const radius = 50;
  const points = Array.from({ length: 81 }, (_, i) =>
    [radius * Math.sin(Math.PI * i / 80), radius * (1 - Math.cos(Math.PI * i / 80)), 0]);
  const arcLengths = points.map((_, i) => radius * Math.PI * i / 80);
  const result = relaxTube({ points, arcLengths, endTangents: [[1, 0, 0], [-1, 0, 0]] },
    { sampleSpacingMm: 3, maxIterations: 1000 });
  assert.equal(result.diagnostics.converged, true);
  assert.ok(arcLengths.at(-1) - length(points) > 0.01);
  assert.ok(Math.abs(result.diagnostics.lengthMm - Math.PI * radius) < 0.0001);
  // A half circle minimizes squared curvature at total turning pi. The finite
  // endpoint segments approximate its clamps; geometry and energy approach it.
  const analyticEnergy = Math.PI / (2 * radius);
  assert.ok(Math.abs(result.diagnostics.bendingEnergy / analyticEnergy - 1) < 0.03);
  assert.ok(result.diagnostics.maxDisplacementMm < 0.5);
  assertLengths(result);
});

test('a tight feasible quarter circle does not acquire a mesh-sized fitting grip', () => {
  const radius = 14;
  const points = Array.from({ length: 81 }, (_, i) =>
    [radius * Math.sin(Math.PI * i / 160), radius * (1 - Math.cos(Math.PI * i / 160)), 0]);
  const arcLengths = points.map((_, i) => radius * Math.PI * i / 160);
  const run = { points, arcLengths, endTangents: [[1, 0, 0], [0, 1, 0]] };
  const coarse = relaxTube(run, { sampleSpacingMm: 6 });
  const fine = relaxTube(run, { sampleSpacingMm: 1.5 });
  for (const result of [coarse, fine]) {
    assert.equal(result.diagnostics.converged, true);
    assert.ok(result.diagnostics.numericalTangentStepMm <= 0.1);
    assert.ok(result.diagnostics.maxDisplacementMm < 0.2);
    assert.ok(Math.abs(result.diagnostics.bendingEnergy / (Math.PI / (4 * radius)) - 1) < 0.01);
    assertLengths(result);
  }
  assert.ok(Math.abs(fine.diagnostics.minRadiusMm - radius) < 0.05);
});

test('refining the discretization and adding iterations preserves the relaxed shape', () => {
  const coarse = relaxTube(arch, { sampleSpacingMm: 8, maxIterations: 1000 });
  const medium = relaxTube(arch, { sampleSpacingMm: 4, maxIterations: 1000 });
  const fine = relaxTube(arch, { sampleSpacingMm: 2, maxPoints: 256, maxIterations: 1500 });
  for (const result of [coarse, medium, fine]) {
    assert.equal(result.diagnostics.converged, true);
    assertLengths(result);
  }
  let coarseError = 0, mediumError = 0;
  for (let i = 0; i <= 100; i++) {
    const s = fine.diagnostics.nominalLengthMm * i / 100;
    coarseError = Math.max(coarseError, distance(at(coarse, s), at(fine, s)));
    mediumError = Math.max(mediumError, distance(at(medium, s), at(fine, s)));
  }
  assert.ok(coarseError < 0.7, `coarse displacement ${coarseError}`);
  assert.ok(mediumError < coarseError, `refinement ${coarseError} -> ${mediumError}`);
  const repeat = relaxTube(arch, { sampleSpacingMm: 4, maxIterations: 2000 });
  assert.deepEqual(repeat.points, medium.points);
});

test('the unloaded straight-rest solution is rigid-transform invariant', () => {
  const transform = p => [p[2] + 900, p[0] - 340, p[1] + 170];
  const original = relaxTube(arch), moved = relaxTube({ points: arch.points.map(transform) });
  assert.equal(moved.diagnostics.converged, true);
  for (let i = 0; i < original.points.length; i++) {
    assert.ok(distance(transform(original.points[i]), moved.points[i]) < 0.002);
  }
});

test('opposite assumed coil winding produces deterministic opposite bows', () => {
  const positive = relaxTube(arch, { scenario: 'coil-positive', maxIterations: 800 });
  const negative = relaxTube(arch, { scenario: 'coil-negative', maxIterations: 800 });
  assert.equal(positive.diagnostics.converged, true);
  assert.equal(negative.diagnostics.converged, true);
  assert.ok(Math.max(...positive.points.map(p => Math.abs(p[1]))) > 1);
  for (let i = 0; i < positive.points.length; i++) {
    assert.ok(distance(positive.points[i], negative.points[i].map((v, k) => k === 1 ? -v : v)) < 1e-8);
  }
  assertLengths(positive);
  assertLengths(negative);
});

test('the fluid-14 route remains solvable when its cap rib is omitted', () => {
  // Authored route fixture, reconstructed from exact 14 mm fillets. This keeps
  // the real short fitting leads and long free span without quantizing s.
  const run = roundedPolyline([
    [79.82, 102.86, 279.315], [79.82, 102.86, 294.315], [43.5, 185.63, 289],
    [43.5, 199.63, 289], [43.5, 209.63, 275.294], [43.5, 345.625, 275.294],
    [57.5, 422, 275.294], [57.5, 422, 253.4],
  ], 14);
  const result = relaxTube(run, { maxIterations: 800 });
  assert.equal(result.diagnostics.converged, true);
  assert.ok(result.diagnostics.maxDisplacementMm > 40);
  assert.ok(result.diagnostics.bendingEnergy < result.diagnostics.initialBendingEnergy / 3);
  assertLengths(result);
});

test('infeasible retain points are reported immediately, without claiming convergence', () => {
  const result = relaxTube({ points: [[0, 0, 0], [100, 0, 0]],
    holds: [{ id: 'misplaced-tie', s: 50, point: [90, 0, 0] }] });
  assert.equal(result.diagnostics.status, 'infeasible');
  assert.equal(result.diagnostics.converged, false);
  assert.equal(result.diagnostics.iterations, 0);
  assert.ok(result.warnings.some(message => message.includes('shorter')));
  assert.ok(result.warnings.some(message => message.includes('length residual')));
});

test('bounded iteration and bend-radius checks remain explicit', () => {
  const bounded = relaxTube(sRoute, { maxIterations: 1 });
  assert.equal(bounded.diagnostics.converged, false);
  assert.equal(bounded.diagnostics.iterations, 1);
  assert.ok(bounded.warnings.some(message => message.includes('Iteration limit')));
  assertLengths(bounded);
  const tight = relaxTube({ ...sRoute, minBendRadiusMm: 40 });
  assert.ok(tight.warnings.some(message => message.includes('minimum-radius')));
  assert.ok(tight.diagnostics.minRadiusMm < 40);
});

test('contact screening reports collisions and never masquerades as contact response', () => {
  const unscreened = relaxTube(sRoute);
  assert.equal(unscreened.diagnostics.contacts, 'not-screened');
  const screened = relaxTube(sRoute, { screenSegment(a, b, radiusMm) {
    assert.equal(radiusMm, 3.175);
    return Math.max(a[0], b[0]) > 50 && Math.min(a[0], b[0]) < 70 ? { body: 'obstacle' } : null;
  } });
  assert.equal(screened.diagnostics.contacts, 'screened');
  assert.ok(screened.contacts.length > 0);
  assert.deepEqual(screened.points, unscreened.points);
  assert.ok(screened.warnings.some(message => message.includes('contact response is not modeled')));
});

test('invalid coordinates, grip definitions and unbounded work requests are rejected', () => {
  assert.throws(() => relaxTube({ points: [[0, 0, 0], [NaN, 0, 0]] }), /finite/);
  assert.throws(() => relaxTube({ ...sRoute, holds: [{ s: 90, clampLengthMm: 8 }] }), /grip/);
  assert.throws(() => relaxTube(sRoute, { maxIterations: 50000 }), /4000/);
  assert.throws(() => relaxTube(sRoute, { maxPoints: 50000 }), /512/);
  assert.throws(() => relaxTube({ ...sRoute, arcLengths: [0, 20, 40, 60] }), /chord/);
});
