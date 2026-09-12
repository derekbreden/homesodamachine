// Static, inextensible centreline scenarios in millimetres. Straight-rest energy
// is sum |t[i] - t[i-1]|² / mean(edge lengths); a uniform bending modulus cancels
// from this unloaded equilibrium. Coil scenarios rotate the preferred tangent
// by ds / assumed radius about a supplied world axis. They express an assumed
// winding direction, not a measured tube memory or a material-frame rod model.
//
// Length constraints use simultaneous manifold projection (a tridiagonal
// Jacobian product), following the centreline/inextensibility separation in
// Bergou et al., Discrete Elastic Rods, §§4/8:
// https://www.cs.columbia.edu/cg/pdfs/143-rods.pdf
// This model omits gravity, pressure, friction, torsion and contact response.
// Convergence measures constrained stationarity from a CAD-seeded search; it
// does not establish the global energy minimum or the tube's installed shape.

const EPS = 1e-10;
const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const dot = (a, b) => {
  let sum = 0;
  for (let i = 0; i < a.length; i++) sum += a[i] * b[i];
  return sum;
};
const maxAbs = values => {
  let maximum = 0;
  for (let i = 0; i < values.length; i++) maximum = Math.max(maximum, Math.abs(values[i]));
  return maximum;
};
const vector = (value, name) => {
  if (!Array.isArray(value) || value.length !== 3 || !value.every(Number.isFinite)) {
    throw new TypeError(`${name} must be three finite coordinates`);
  }
  return value.slice();
};
const unit = (value, name) => {
  const v = vector(value, name), length = Math.hypot(...v);
  if (length < EPS) throw new RangeError(`${name} must have a direction`);
  return v.map(x => x / length);
};
const positive = (value, fallback, name) => {
  value ??= fallback;
  if (!Number.isFinite(value) || value <= 0) throw new RangeError(`${name} must be positive`);
  return value;
};

function sample(points, arc, s) {
  let lo = 0, hi = arc.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (arc[mid] < s) lo = mid;
    else hi = mid;
  }
  const t = Math.max(0, Math.min(1, (s - arc[lo]) / (arc[hi] - arc[lo])));
  return points[lo].map((x, k) => x + t * (points[hi][k] - x));
}

function prepare(run, options) {
  if (!Array.isArray(run.points) || run.points.length < 2) {
    throw new TypeError('A tube needs at least two centreline points');
  }
  const source = run.points.map((p, i) => vector(p, `points[${i}]`));
  const requestedSpacing = positive(options.sampleSpacingMm, 6, 'sampleSpacingMm');
  const tangentStep = Math.min(0.1, requestedSpacing / 50);
  const sourceArc = [0];
  for (let i = 1; i < source.length; i++) {
    const length = distance(source[i], source[i - 1]);
    if (length < EPS) throw new RangeError('Consecutive centreline points must differ');
    sourceArc.push(sourceArc.at(-1) + length);
  }
  if (run.arcLengths != null) {
    if (!Array.isArray(run.arcLengths) || run.arcLengths.length !== source.length ||
        run.arcLengths[0] !== 0 || !run.arcLengths.every(Number.isFinite)) {
      throw new RangeError('arcLengths must start at zero and match the centreline points');
    }
    for (let i = 1; i < source.length; i++) {
      const segment = run.arcLengths[i] - run.arcLengths[i - 1];
      if (segment <= 0 || segment < distance(source[i], source[i - 1]) - 1e-4) {
        throw new RangeError('Arc intervals must be positive and at least their chord length');
      }
    }
    sourceArc.splice(0, sourceArc.length, ...run.arcLengths);
  }
  const length = sourceArc.at(-1);
  const tangents = run.endTangents ?? [
    source[1].map((v, k) => v - source[0][k]),
    source.at(-1).map((v, k) => v - source.at(-2)[k]),
  ];
  const supplied = (run.holds ?? []).filter(hold => options.omitHoldId == null || hold.id !== options.omitHoldId);
  const holds = [
    { s: 0, id: 'start', label: 'Start fitting', point: source[0], tangent: tangents[0], endpoint: true },
    ...supplied,
    { s: length, id: 'end', label: 'End fitting', point: source.at(-1), tangent: tangents[1], endpoint: true },
  ].map((hold, i) => {
    if (!Number.isFinite(hold.s) || hold.s < -EPS || hold.s > length + EPS) {
      throw new RangeError(`holds[${i}].s lies outside the exposed centreline`);
    }
    const s = Math.max(0, Math.min(length, hold.s));
    const tangent = hold.tangent ? unit(hold.tangent, 'hold tangent') : null;
    const clampLengthMm = hold.clampLengthMm ?? 0;
    if (!Number.isFinite(clampLengthMm) || clampLengthMm < 0 || (clampLengthMm && !tangent)) {
      throw new RangeError('A finite grip needs a nonnegative clampLengthMm and a tangent');
    }
    return { ...hold, s, point: vector(hold.point ?? sample(source, sourceArc, s), 'hold point'),
      tangent, clampLengthMm };
  }).sort((a, b) => a.s - b.s);

  const constraints = [];
  for (const hold of holds) {
    constraints.push({ ...hold });
    for (const direction of [-1, 1]) {
      if (!hold.tangent) continue;
      for (const offset of [hold.clampLengthMm / 2, hold.clampLengthMm / 2 + tangentStep]) {
        if (!offset) continue;
        const s = Math.max(0, Math.min(length, hold.s + direction * offset));
        constraints.push({ s, point: hold.point.map((v, k) => v + (s - hold.s) * hold.tangent[k]),
          tangent: null });
      }
    }
  }
  constraints.sort((a, b) => a.s - b.s);
  const pins = [];
  for (const hold of constraints) {
    if (pins.length && hold.s - pins.at(-1).s < 1e-6) {
      if (distance(hold.point, pins.at(-1).point) > 1e-4) {
        throw new RangeError('Coincident holds specify different positions');
      }
      if (hold.tangent && pins.at(-1).tangent && dot(hold.tangent, pins.at(-1).tangent) < 1 - 1e-6) {
        throw new RangeError('Coincident holds specify different directions');
      }
      pins.at(-1).tangent ||= hold.tangent;
    } else pins.push(hold);
  }
  const maxPoints = Math.round(positive(options.maxPoints, 160, 'maxPoints'));
  if (maxPoints < 8 || maxPoints > 512) throw new RangeError('maxPoints must be between 8 and 512');
  if (pins.length * 2 - 1 > maxPoints) throw new RangeError('Too many holds for maxPoints');
  const spacing = Math.max(requestedSpacing,
    length / Math.max(1, maxPoints - pins.length * 2));
  const arc = [0];
  for (let i = 1; i < pins.length; i++) {
    const count = Math.max(2, Math.ceil((pins[i].s - pins[i - 1].s) / spacing));
    pins[i - 1].index = arc.length - 1;
    for (let j = 1; j <= count; j++) {
      arc.push(pins[i - 1].s + (pins[i].s - pins[i - 1].s) * j / count);
    }
  }
  pins.at(-1).index = arc.length - 1;
  const nominal = arc.map(s => sample(source, sourceArc, s));
  const x = new Float64Array(nominal.flat());
  const fixed = new Uint8Array(arc.length);
  const edgeLength = new Float64Array(arc.length - 1);
  const warnings = [];
  for (let i = 0; i < edgeLength.length; i++) edgeLength[i] = arc[i + 1] - arc[i];
  const pin = (index, point) => {
    if (fixed[index] && distance(Array.from(x.subarray(index * 3, index * 3 + 3)), point) > 1e-4) {
      throw new RangeError('Grip directions conflict with adjacent holds');
    }
    x.set(point, index * 3);
    fixed[index] = 1;
  };
  for (const hold of pins) pin(hold.index, hold.point);
  let previous = -1, feasible = true;
  for (let i = 0; i < fixed.length; i++) {
    if (!fixed[i]) continue;
    if (previous >= 0) {
      const chord = Math.hypot(...[0, 1, 2].map(k => x[i * 3 + k] - x[previous * 3 + k]));
      if (chord > arc[i] - arc[previous] + 1e-4) {
        warnings.push('A span is shorter than the distance between its retained points.');
        feasible = false;
      } else if (Math.abs(chord - (arc[i] - arc[previous])) < 1e-7) {
        // An inextensible span whose chord consumes its entire length has no
        // bending freedom. Keeping it exactly straight removes its singular
        // constraint Jacobian without adding a restraint to the tube model.
        for (let j = previous + 1; j < i; j++) {
          const fraction = (arc[j] - arc[previous]) / (arc[i] - arc[previous]);
          for (let k = 0; k < 3; k++) x[j * 3 + k] = x[previous * 3 + k] + fraction * (x[i * 3 + k] - x[previous * 3 + k]);
          fixed[j] = 1;
        }
      }
    }
    previous = i;
  }
  for (const hold of holds) hold.index = arc.findIndex(s => Math.abs(s - hold.s) < 1e-6);
  return { x, fixed, edgeLength, arc, nominal, holds, warnings, length, feasible, tangentStep };
}

// J Jᵀ is tridiagonal because only neighbouring segment constraints share a
// movable vertex. Fixed vertices have zero inverse weight in that product.
function constraintSystem(x, fixed, lengths) {
  const count = lengths.length;
  const direction = new Float64Array(count * 3);
  const diagonal = new Float64Array(count);
  const offDiagonal = new Float64Array(count - 1);
  const errors = new Float64Array(count);
  let maxError = 0;
  for (let i = 0; i < count; i++) {
    const p = i * 3;
    const dx = x[p + 3] - x[p], dy = x[p + 4] - x[p + 1], dz = x[p + 5] - x[p + 2];
    const length = Math.hypot(dx, dy, dz);
    errors[i] = length - lengths[i];
    maxError = Math.max(maxError, Math.abs(errors[i]));
    const divisor = Math.max(EPS, length);
    direction[p] = dx / divisor; direction[p + 1] = dy / divisor; direction[p + 2] = dz / divisor;
    diagonal[i] = 2 - fixed[i] - fixed[i + 1];
    if (!diagonal[i]) { diagonal[i] = 1; errors[i] = 0; }
    diagonal[i] += 1e-9;
    if (i && !fixed[i]) {
      offDiagonal[i - 1] = -(direction[p - 3] * direction[p] + direction[p - 2] * direction[p + 1] + direction[p - 1] * direction[p + 2]);
    }
  }
  return { direction, diagonal, offDiagonal, errors, maxError };
}

function solveTridiagonal(system, rhs) {
  const d = system.diagonal.slice(), answer = Float64Array.from(rhs), off = system.offDiagonal;
  for (let i = 1; i < d.length; i++) {
    const factor = off[i - 1] / Math.max(1e-12, d[i - 1]);
    d[i] -= factor * off[i - 1];
    answer[i] -= factor * answer[i - 1];
  }
  for (let i = d.length - 1; i >= 0; i--) {
    answer[i] = (answer[i] - (i + 1 < d.length ? off[i] * answer[i + 1] : 0)) / Math.max(1e-12, d[i]);
  }
  return answer;
}

function subtractConstraintNormal(v, system, lambda, fixed) {
  for (let i = 0; i < lambda.length; i++) {
    for (let k = 0; k < 3; k++) {
      const correction = system.direction[i * 3 + k] * lambda[i];
      if (!fixed[i]) v[i * 3 + k] += correction;
      if (!fixed[i + 1]) v[(i + 1) * 3 + k] -= correction;
    }
  }
}

function projectVector(v, system, fixed) {
  const out = Float64Array.from(v);
  for (let i = 0; i < fixed.length; i++) if (fixed[i]) out.fill(0, i * 3, i * 3 + 3);
  const rhs = new Float64Array(fixed.length - 1);
  for (let i = 0; i < rhs.length; i++) {
    for (let k = 0; k < 3; k++) {
      rhs[i] += system.direction[i * 3 + k] * (out[(i + 1) * 3 + k] - out[i * 3 + k]);
    }
  }
  subtractConstraintNormal(out, system, solveTridiagonal(system, rhs), fixed);
  return out;
}

function restoreLengths(x, fixed, lengths, tolerance = 1e-8, maxIterations = 12) {
  let system = constraintSystem(x, fixed, lengths);
  for (let iteration = 0; iteration < maxIterations && system.maxError > tolerance; iteration++) {
    const correction = new Float64Array(x.length);
    subtractConstraintNormal(correction, system, solveTridiagonal(system, system.errors), fixed);
    const trial = x.slice();
    let accepted = false;
    for (let scale = 1; scale >= 1 / 128; scale /= 2) {
      for (let j = 0; j < x.length; j++) trial[j] = x[j] + correction[j] * scale;
      const next = constraintSystem(trial, fixed, lengths);
      if (next.maxError < system.maxError) {
        x.set(trial); system = next; accepted = true; break;
      }
    }
    if (!accepted) break;
  }
  return system;
}

function rotations(lengths, scenario, options) {
  const normal = unit(options.coilNormal ?? [0, 0, 1], 'coilNormal');
  const radius = positive(options.coilRadiusMm, 250, 'coilRadiusMm');
  const sign = scenario === 'coil-positive' ? 1 : scenario === 'coil-negative' ? -1 : 0;
  return Array.from({ length: lengths.length - 1 }, (_, i) => {
    const angle = sign * (lengths[i] + lengths[i + 1]) / (2 * radius);
    const c = Math.cos(angle), s = Math.sin(angle), [x, y, z] = normal, v = 1 - c;
    return [c + x * x * v, x * y * v - z * s, x * z * v + y * s,
      y * x * v + z * s, c + y * y * v, y * z * v - x * s,
      z * x * v - y * s, z * y * v + x * s, c + z * z * v];
  });
}

function energyGradient(x, lengths, rotation) {
  const gradient = new Float64Array(x.length);
  let energy = 0;
  for (let i = 1; i < lengths.length; i++) {
    const p = i * 3, a = lengths[i - 1], b = lengths[i], weight = 2 / (a + b), r = rotation[i - 1];
    const bx = (x[p] - x[p - 3]) / a, by = (x[p + 1] - x[p - 2]) / a, bz = (x[p + 2] - x[p - 1]) / a;
    const rx = (x[p + 3] - x[p]) / b - r[0] * bx - r[1] * by - r[2] * bz;
    const ry = (x[p + 4] - x[p + 1]) / b - r[3] * bx - r[4] * by - r[5] * bz;
    const rz = (x[p + 5] - x[p + 2]) / b - r[6] * bx - r[7] * by - r[8] * bz;
    energy += weight * (rx * rx + ry * ry + rz * rz) / 2;
    for (let k = 0; k < 3; k++) {
      const back = weight * (r[k] * rx + r[k + 3] * ry + r[k + 6] * rz) / a;
      const front = weight * (k === 0 ? rx : k === 1 ? ry : rz) / b;
      gradient[p - 3 + k] += back;
      gradient[p + k] -= back + front;
      gradient[p + 3 + k] += front;
    }
  }
  return { energy, gradient };
}

// The bending Hessian is constant for these tangent-difference energies and
// has bandwidth eight in xyz storage. Its inverse gives smooth trial motions
// across a long span without a discretization-dependent smoothing timestep.
function bendingPreconditioner(lengths, rotation, fixed) {
  const size = fixed.length * 3, width = 9;
  const lower = new Float64Array(size * width);
  for (let i = 1; i < lengths.length; i++) {
    const a = lengths[i - 1], b = lengths[i], weight = 2 / (a + b), r = rotation[i - 1];
    for (let axis = 0; axis < 3; axis++) {
      const derivative = [0, 1, 2].map(k => r[axis * 3 + k] / a);
      derivative.push(...[0, 1, 2].map(k => -r[axis * 3 + k] / a - (axis === k ? 1 / b : 0)));
      derivative.push(...[0, 1, 2].map(k => axis === k ? 1 / b : 0));
      for (let j = 0; j < 9; j++) for (let k = 0; k <= j; k++) {
        const row = (i - 1) * 3 + j, column = (i - 1) * 3 + k;
        if (!fixed[Math.floor(row / 3)] && !fixed[Math.floor(column / 3)]) {
          lower[row * width + row - column] += weight * derivative[j] * derivative[k];
        }
      }
    }
  }
  for (let row = 0; row < size; row++) {
    if (fixed[Math.floor(row / 3)]) lower[row * width] = 1;
    for (let column = Math.max(0, row - width + 1); column <= row; column++) {
      let value = lower[row * width + row - column];
      for (let k = Math.max(0, row - width + 1); k < column; k++) {
        value -= lower[row * width + row - k] * lower[column * width + column - k];
      }
      lower[row * width + row - column] = row === column ?
        Math.sqrt(Math.max(1e-14, value)) : value / lower[column * width];
    }
  }
  return input => {
    const answer = input.slice();
    for (let row = 0; row < size; row++) {
      for (let k = Math.max(0, row - width + 1); k < row; k++) answer[row] -= lower[row * width + row - k] * answer[k];
      answer[row] /= lower[row * width];
    }
    for (let row = size - 1; row >= 0; row--) {
      for (let k = row + 1; k < Math.min(size, row + width); k++) answer[row] -= lower[k * width + k - row] * answer[k];
      answer[row] /= lower[row * width];
    }
    return answer;
  };
}

function searchDirection(gradient, history, precondition) {
  const q = gradient.slice(), alpha = [];
  for (let i = history.length - 1; i >= 0; i--) {
    const h = history[i]; alpha[i] = dot(h.s, q) / h.sy;
    for (let k = 0; k < q.length; k++) q[k] -= alpha[i] * h.y[k];
  }
  q.set(precondition(q));
  for (let i = 0; i < history.length; i++) {
    const h = history[i], beta = dot(h.y, q) / h.sy;
    for (let k = 0; k < q.length; k++) q[k] += h.s[k] * (alpha[i] - beta);
  }
  return q.map(v => -v);
}

/**
 * run.points: CAD centreline, mm, Z-up, in increasing tube arc length.
 * run.arcLengths optionally supplies exact developed s at every CAD sample;
 * without it, lengths are measured along the supplied polyline.
 * run.holds: {s, id?, label?, point?, tangent?, clampLengthMm?}; only physical
 * restraints belong here. A point hold fixes position. Tangents use numerical
 * segments at most 0.1 mm long, shortened under refinement, independent of the
 * main mesh spacing. clampLengthMm fixes a straight grip of that physical length.
 * End fittings always fix position/tangent.
 * options.omitHoldId removes one interior restraint for a sensitivity comparison.
 * Work is bounded by maxPoints (160) and maxIterations (400), including a
 * coarse initialization on longer runs; run in a Worker. The minimum-radius
 * check diagnoses the result and does not act as a curvature constraint.
 * options.screenSegment(a, b, radiusMm, index), when supplied, returns null or a
 * caller-defined contact finding. Screening never moves the centreline.
 */
export function relaxTube(run, options = {}) {
  const started = performance.now();
  const scenario = options.scenario ?? 'straight';
  if (!['straight', 'coil-positive', 'coil-negative'].includes(scenario)) throw new RangeError('Unknown tube scenario');
  const state = prepare(run, options);
  let { x } = state;
  const { fixed, edgeLength, arc, nominal, holds, length, warnings } = state;
  const maxIterations = Math.round(positive(options.maxIterations, 400, 'maxIterations'));
  if (maxIterations > 4000) throw new RangeError('maxIterations must not exceed 4000');
  const radiusMm = positive(run.radiusMm, 3.175, 'radiusMm');
  const minBendRadiusMm = run.minBendRadiusMm == null ? null : positive(run.minBendRadiusMm, null, 'minBendRadiusMm');
  const rotation = rotations(edgeLength, scenario, options);
  const precondition = bendingPreconditioner(edgeLength, rotation, fixed);
  const spacing = length / edgeLength.length;
  const initialBendingEnergy = energyGradient(x, edgeLength, rotation).energy;
  let coarseIterations = 0;
  if (state.feasible && !options.coarsePass && x.length > 64 * 3 && maxIterations >= 240) {
    const coarse = relaxTube(run, { ...options, coarsePass: true, maxIterations: 160,
      sampleSpacingMm: spacing * 3, screenSegment: undefined });
    coarseIterations = coarse.diagnostics.iterations;
    for (let i = 0; i < arc.length; i++) {
      if (!fixed[i]) x.set(sample(coarse.points, coarse.arcLengths, arc[i]), i * 3);
    }
  }
  let system = state.feasible ? restoreLengths(x, fixed, edgeLength, 1e-8, 40) : constraintSystem(x, fixed, edgeLength);
  let current = energyGradient(x, edgeLength, rotation);
  let gradient = projectVector(current.gradient, system, fixed);
  const history = [];
  let iterations = coarseIterations, converged = false, stalled = false, lastMovementMm = 0, gradientFallback = false;
  for (; state.feasible && iterations < maxIterations; iterations++) {
    const gradientMax = maxAbs(gradient);
    if (gradientMax * spacing ** 3 < 1e-5 && system.maxError < 1e-4) { converged = true; break; }
    let direction = gradientFallback ? gradient.map(v => -v * spacing ** 3 / 8) :
      projectVector(searchDirection(gradient, history, precondition), system, fixed);
    let slope = dot(gradient, direction);
    if (slope >= -1e-20) {
      history.length = 0;
      direction = gradient.map(v => -v * spacing ** 3 / 8);
      slope = dot(gradient, direction);
    }
    const longestMove = maxAbs(direction);
    if (longestMove < 1e-12) { stalled = true; break; }
    const firstStep = Math.min(1, spacing * 2 / Math.max(EPS, longestMove));
    let accepted = null;
    for (let attempt = 0; attempt < 14; attempt++) {
      const step = firstStep * 0.5 ** attempt;
      const candidate = x.map((v, i) => v + step * direction[i]);
      const candidateSystem = restoreLengths(candidate, fixed, edgeLength);
      if (candidateSystem.maxError > Math.max(1e-4, system.maxError * 1.05)) continue;
      const value = energyGradient(candidate, edgeLength, rotation);
      if (value.energy <= current.energy + 1e-4 * step * slope) {
        accepted = { x: candidate, system: candidateSystem, current: value }; break;
      }
    }
    if (!accepted) {
      if (!gradientFallback) { history.length = 0; gradientFallback = true; continue; }
      stalled = true; break;
    }
    gradientFallback = false;
    const nextGradient = projectVector(accepted.current.gradient, accepted.system, fixed);
    const s = x.map((v, i) => accepted.x[i] - v), y = gradient.map((v, i) => nextGradient[i] - v);
    const sy = dot(s, y);
    if (sy > 1e-12 * Math.hypot(...s) * Math.hypot(...y)) {
      history.push({ s, y, sy }); if (history.length > 10) history.shift();
    }
    lastMovementMm = maxAbs(s);
    x = accepted.x; system = accepted.system; current = accepted.current; gradient = nextGradient;
  }
  if (state.feasible) system = restoreLengths(x, fixed, edgeLength, 1e-6, 30);
  const points = Array.from({ length: fixed.length }, (_, i) => Array.from(x.subarray(i * 3, i * 3 + 3)));
  let solvedLength = 0, minRadiusMm = Infinity;
  for (let i = 1; i < points.length; i++) {
    const a = distance(points[i - 1], points[i]); solvedLength += a;
    if (i + 1 < points.length) {
      const b = distance(points[i], points[i + 1]);
      const t0 = points[i].map((v, k) => (v - points[i - 1][k]) / a);
      const t1 = points[i + 1].map((v, k) => (v - points[i][k]) / b);
      const halfSine = Math.sqrt(Math.max(0, (1 - Math.max(-1, Math.min(1, dot(t0, t1)))) / 2));
      if (halfSine > EPS) minRadiusMm = Math.min(minRadiusMm, (a + b) / (4 * halfSine));
    }
  }
  const displacement = points.map((point, i) => distance(point, nominal[i]));
  const spans = [];
  for (let i = 1; i < holds.length; i++) {
    const from = holds[i - 1], to = holds[i];
    if (to.s - from.s < EPS) continue;
    const chordMm = distance(from.point, to.point);
    spans.push({ from: from.id ?? from.label ?? `hold-${i - 1}`, to: to.id ?? to.label ?? `hold-${i}`,
      startS: from.s, endS: to.s, lengthMm: to.s - from.s, chordMm,
      slackMm: to.s - from.s - chordMm,
      maxDisplacementMm: Math.max(...displacement.slice(from.index, to.index + 1)) });
  }
  const contacts = [];
  if (options.screenSegment) {
    for (let i = 1; i < points.length; i++) {
      const contact = options.screenSegment(points[i - 1], points[i], radiusMm, i - 1);
      if (contact) contacts.push({ segment: i - 1, finding: contact });
    }
  }
  if (!converged && state.feasible) warnings.push(stalled ? 'Relaxation stalled before numerical convergence.' : 'Iteration limit reached before numerical convergence.');
  if (system.maxError > 1e-3) warnings.push('Segment length residual exceeds 0.001 mm; this scenario is not length-feasible.');
  if (minBendRadiusMm && minRadiusMm < minBendRadiusMm * 0.98) {
    warnings.push(`Scenario bends below the ${minBendRadiusMm} mm minimum-radius check.`);
  }
  if (contacts.length) warnings.push('The screened scenario intersects surrounding geometry; contact response is not modeled.');
  return { points, arcLengths: arc, holds, spans, contacts, warnings,
    diagnostics: { scenario, converged: converged && system.maxError <= 1e-3 && state.feasible,
      status: !state.feasible ? 'infeasible' : converged ? 'converged' : stalled ? 'stalled' : 'iteration-limit',
      iterations, coarseIterations, pointCount: points.length, lengthMm: solvedLength, nominalLengthMm: length,
      numericalTangentStepMm: state.tangentStep,
      lengthErrorMm: solvedLength - length, maxSegmentErrorMm: system.maxError,
      minRadiusMm: Number.isFinite(minRadiusMm) ? minRadiusMm : null,
      maxDisplacementMm: Math.max(...displacement), initialBendingEnergy,
      bendingEnergy: energyGradient(x, edgeLength, rotation).energy,
      projectedGradientMax: maxAbs(gradient), lastMovementMm,
      contacts: options.screenSegment ? 'screened' : 'not-screened',
      elapsedMs: performance.now() - started } };
}
