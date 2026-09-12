// Capsule-to-surface screening in the assembly's millimetre, Z-up frame.
// A screened curve is still an unconstrained shape: contact is reported, not solved.
// Hidden parts remain physical obstacles. Mesh names identify each contact.

const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const pointAt = (p, d, t) => [p[0] + t * d[0], p[1] + t * d[1], p[2] + t * d[2]];
const length = (a) => Math.hypot(...a);
const now = () => globalThis.performance?.now?.() ?? Date.now();
const baseName = (name) => String(name || '').replace(/\/\d+$/, '');
const overlaps = (a, b) => a[0] <= b[3] && a[3] >= b[0] && a[1] <= b[4] && a[4] >= b[1] && a[2] <= b[5] && a[5] >= b[2];

function boundsOf(points) {
  const b = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
  for (let i = 0; i < points.length; i += 3) {
    for (let k = 0; k < 3; k++) {
      b[k] = Math.min(b[k], points[i + k]);
      b[k + 3] = Math.max(b[k + 3], points[i + k]);
    }
  }
  return b;
}

function expandedSegmentBounds(a, b, r) {
  return [Math.min(a[0], b[0]) - r, Math.min(a[1], b[1]) - r, Math.min(a[2], b[2]) - r,
    Math.max(a[0], b[0]) + r, Math.max(a[1], b[1]) + r, Math.max(a[2], b[2]) + r];
}

function triangle(mesh, i) {
  const at = (j) => {
    const k = mesh.indices[i * 3 + j] * 3;
    return [mesh.positions[k], mesh.positions[k + 1], mesh.positions[k + 2]];
  };
  return [at(0), at(1), at(2)];
}

function pointTriangleSquared(p, a, b, c) {
  const ab = sub(b, a), ac = sub(c, a), ap = sub(p, a);
  const normal = cross(ab, ac);
  if (dot(normal, normal) < 1e-24) {
    return Math.min(...[[a, b], [b, c], [c, a]].map(([x, y]) =>
      segmentSegmentSquared(p, p, x, y).distance2));
  }
  const d1 = dot(ab, ap), d2 = dot(ac, ap);
  if (d1 <= 0 && d2 <= 0) return dot(ap, ap);
  const bp = sub(p, b), d3 = dot(ab, bp), d4 = dot(ac, bp);
  if (d3 >= 0 && d4 <= d3) return dot(bp, bp);
  const vc = d1 * d4 - d3 * d2;
  if (vc <= 0 && d1 >= 0 && d3 <= 0) {
    const q = sub(p, pointAt(a, ab, d1 / (d1 - d3)));
    return dot(q, q);
  }
  const cp = sub(p, c), d5 = dot(ab, cp), d6 = dot(ac, cp);
  if (d6 >= 0 && d5 <= d6) return dot(cp, cp);
  const vb = d5 * d2 - d1 * d6;
  if (vb <= 0 && d2 >= 0 && d6 <= 0) {
    const q = sub(p, pointAt(a, ac, d2 / (d2 - d6)));
    return dot(q, q);
  }
  const va = d3 * d6 - d5 * d4;
  if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) {
    const q = sub(p, pointAt(b, sub(c, b), (d4 - d3) / ((d4 - d3) + (d5 - d6))));
    return dot(q, q);
  }
  const sum = va + vb + vc;
  if (Math.abs(sum) < 1e-20) return Math.min(dot(ap, ap), dot(bp, bp), dot(cp, cp));
  const v = vb / sum, w = vc / sum;
  const q = [p[0] - a[0] - ab[0] * v - ac[0] * w,
    p[1] - a[1] - ab[1] * v - ac[1] * w,
    p[2] - a[2] - ab[2] * v - ac[2] * w];
  return dot(q, q);
}

function segmentSegmentSquared(p, q, a, b) {
  const d = sub(q, p), e = sub(b, a), r = sub(p, a);
  const dd = dot(d, d), ee = dot(e, e), de = dot(d, e);
  const dr = dot(d, r), er = dot(e, r);
  let s, t;
  if (dd < 1e-20 && ee < 1e-20) return {distance2: dot(r, r), s: 0};
  if (dd < 1e-20) { s = 0; t = clamp(er / ee); }
  else if (ee < 1e-20) { t = 0; s = clamp(-dr / dd); }
  else {
    const denominator = dd * ee - de * de;
    s = Math.abs(denominator) > 1e-20 ? clamp((de * er - dr * ee) / denominator) : 0;
    t = (de * s + er) / ee;
    if (t < 0) { t = 0; s = clamp(-dr / dd); }
    else if (t > 1) { t = 1; s = clamp((de - dr) / dd); }
  }
  const v = sub(pointAt(p, d, s), pointAt(a, e, t));
  return {distance2: dot(v, v), s};
}

// Returns a location on the capsule centre segment and its distance to the triangle.
export function segmentTriangleDistance(p, q, a, b, c) {
  const d = sub(q, p), ab = sub(b, a), ac = sub(c, a);
  const h = cross(d, ac), det = dot(ab, h);
  if (Math.abs(det) > 1e-12) {
    const v = sub(p, a), u = dot(v, h) / det;
    const k = cross(v, ab), w = dot(d, k) / det, t = dot(ac, k) / det;
    if (u >= -1e-10 && w >= -1e-10 && u + w <= 1 + 1e-10 && t >= 0 && t <= 1) {
      return {distance: 0, fraction: t, point: pointAt(p, d, t)};
    }
  }
  let distance2 = pointTriangleSquared(p, a, b, c), fraction = 0;
  const end2 = pointTriangleSquared(q, a, b, c);
  if (end2 < distance2) { distance2 = end2; fraction = 1; }
  for (const [x, y] of [[a, b], [b, c], [c, a]]) {
    const found = segmentSegmentSquared(p, q, x, y);
    if (found.distance2 < distance2) { distance2 = found.distance2; fraction = found.s; }
  }
  return {distance: Math.sqrt(Math.max(0, distance2)), fraction, point: pointAt(p, d, fraction)};
}

function makeTree(mesh) {
  const count = mesh.indices.length / 3;
  const bounds = new Float64Array(count * 6), centers = new Float64Array(count * 3);
  for (let i = 0; i < count; i++) {
    const tri = triangle(mesh, i);
    for (let k = 0; k < 3; k++) {
      bounds[i * 6 + k] = Math.min(tri[0][k], tri[1][k], tri[2][k]);
      bounds[i * 6 + k + 3] = Math.max(tri[0][k], tri[1][k], tri[2][k]);
      centers[i * 3 + k] = (bounds[i * 6 + k] + bounds[i * 6 + k + 3]) / 2;
    }
  }
  function node(ids) {
    const b = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
    for (const i of ids) for (let k = 0; k < 3; k++) {
      b[k] = Math.min(b[k], bounds[i * 6 + k]);
      b[k + 3] = Math.max(b[k + 3], bounds[i * 6 + k + 3]);
    }
    if (ids.length <= 12) return {bounds: b, ids};
    let axis = 0;
    for (let k = 1; k < 3; k++) if (b[k + 3] - b[k] > b[axis + 3] - b[axis]) axis = k;
    ids.sort((a, c) => centers[a * 3 + axis] - centers[c * 3 + axis]);
    const middle = ids.length >> 1;
    return {bounds: b, left: node(ids.slice(0, middle)), right: node(ids.slice(middle))};
  }
  return node(Array.from({length: count}, (_, i) => i));
}

export function createTubeContactIndex(entries) {
  const meshes = entries.map((entry) => {
    const positions = entry.positions;
    const indices = entry.indices || Uint32Array.from({length: positions.length / 3}, (_, i) => i);
    if (positions.length % 3 || indices.length % 3) throw new Error('Malformed contact mesh');
    return {name: baseName(entry.name), positions, indices, bounds: boundsOf(positions), tree: null};
  });
  return {meshes};
}

// Remove only the measured interface intervals, not a fitting's whole body.
function freeIntervals(allowed, name, s0, s1) {
  let intervals = [[0, 1]];
  if (s1 - s0 < 1e-12) return allowed.some((x) => baseName(x.name) === name && s0 >= x.s0 && s0 <= x.s1) ? [] : intervals;
  for (const item of allowed) {
    if (baseName(item.name) !== name) continue;
    const lo = clamp((item.s0 - s0) / (s1 - s0)), hi = clamp((item.s1 - s0) / (s1 - s0));
    if (hi <= lo) continue;
    intervals = intervals.flatMap(([a, b]) => {
      if (hi <= a || lo >= b) return [[a, b]];
      const out = [];
      if (lo > a) out.push([a, lo]);
      if (hi < b) out.push([hi, b]);
      return out;
    });
  }
  return intervals;
}

// Sleeve diameters apply only over their measured arc-length intervals.
function radiusIntervals(ranges, radius, s0, s1) {
  const relevant = ranges.filter((r) => r.s0 <= s1 && r.s1 >= s0);
  const cuts = [0, 1];
  if (s1 > s0) for (const range of relevant) {
    for (const s of [range.s0, range.s1]) if (s > s0 && s < s1) cuts.push((s - s0) / (s1 - s0));
  }
  const sorted = [...new Set(cuts)].sort((a, b) => a - b);
  return sorted.slice(1).map((hi, i) => {
    const lo = sorted[i], middle = s0 + (lo + hi) * 0.5 * (s1 - s0);
    return {lo, hi, radius: Math.max(radius, ...relevant.filter((r) =>
      middle >= r.s0 && middle <= r.s1).map((r) => r.radiusMm))};
  });
}

// A nearest contact is one representative of a sampled segment, not an exact
// boundary of the contact patch. Compare both grids so a tiny tangent segment
// does not invent a new contact on an unchanged, more coarsely sampled CAD line.
export function newTubeContacts(nominalReport, scenarioReport, {nominalArcLengths = [], arcLengths = []} = {}) {
  const byBody = new Map();
  for (const contact of nominalReport?.contacts || []) {
    if (!byBody.has(contact.name)) byBody.set(contact.name, []);
    byBody.get(contact.name).push(contact);
  }
  const spacing = (arc, i) => Math.abs((arc[i + 1] ?? 0) - (arc[i] ?? 0));
  return (scenarioReport?.contacts || []).filter((contact) => !(byBody.get(contact.name) || []).some((nominal) =>
    Math.abs(contact.s - nominal.s) <= Math.max(2, spacing(arcLengths, contact.segment),
      spacing(nominalArcLengths, nominal.segment))));
}

export function screenTubeContacts(index, route, {clearanceMm = 0, maxContacts = 80} = {}) {
  const started = now();
  const {points, radiusMm, allowedContacts = [], radiusRanges = []} = route;
  if (!Array.isArray(points) || points.length < 2 || !Number.isFinite(radiusMm) || radiusMm < 0) {
    throw new Error('Contact screening needs a centreline and a finite nonnegative radius');
  }
  const parameters = route.arcLengths;
  if (parameters && (parameters.length !== points.length || parameters.some((s, i) =>
      !Number.isFinite(s) || (i && s < parameters[i - 1])))) throw new Error('Invalid contact arc lengths');
  if (!Array.isArray(radiusRanges) || radiusRanges.some((r) => !r ||
      ![r.s0, r.s1, r.radiusMm].every(Number.isFinite) || r.s0 < 0 || r.s1 <= r.s0 || r.radiusMm < 0)) {
    throw new Error('Invalid sleeve radius intervals');
  }
  const exclude = new Set((route.excludeNames || []).map(baseName));
  const clearance = Math.max(0, clearanceMm);
  const contacts = [];
  let testedTriangles = 0, builtMeshes = 0, arc = 0, totalContacts = 0;
  const candidates = index.meshes.filter((mesh) => !exclude.has(mesh.name));
  for (let segment = 0; segment + 1 < points.length; segment++) {
    const p = points[segment], q = points[segment + 1], d = sub(q, p), segmentLength = length(d);
    if (![...p, ...q].every(Number.isFinite)) throw new Error('Non-finite contact centreline');
    const s0 = parameters ? parameters[segment] : arc;
    const s1 = parameters ? parameters[segment + 1] : arc + segmentLength;
    const radii = radiusIntervals(radiusRanges, radiusMm, s0, s1);
    const wholeBounds = expandedSegmentBounds(p, q, Math.max(...radii.map((r) => r.radius)) + clearance);
    for (const mesh of candidates) {
      if (!overlaps(wholeBounds, mesh.bounds)) continue;
      const intervals = freeIntervals(allowedContacts, mesh.name, s0, s1);
      if (!intervals.length) continue;
      if (!mesh.tree) { mesh.tree = makeTree(mesh); builtMeshes++; }
      let nearest = null;
      for (const part of radii) for (const [start, end] of intervals) {
        const lo = Math.max(start, part.lo), hi = Math.min(end, part.hi);
        if (hi <= lo) continue;
        const limit = part.radius + clearance;
        const a = pointAt(p, d, lo), b = pointAt(p, d, hi);
        const segmentBounds = expandedSegmentBounds(a, b, limit);
        const stack = [mesh.tree];
        while (stack.length) {
          const node = stack.pop();
          if (!overlaps(segmentBounds, node.bounds)) continue;
          if (!node.ids) { stack.push(node.left, node.right); continue; }
          for (const i of node.ids) {
            testedTriangles++;
            const found = segmentTriangleDistance(a, b, ...triangle(mesh, i));
            if (found.distance > limit + 1e-8) continue;
            const fraction = lo + (hi - lo) * found.fraction;
            const gapMm = found.distance - part.radius;
            if (!nearest || gapMm < nearest.gapMm) nearest = {
              ...found, fraction, gapMm, radiusMm: part.radius, s: s0 + fraction * (s1 - s0)};
          }
        }
      }
      if (nearest) {
        totalContacts++;
        if (contacts.length < maxContacts) contacts.push({name: mesh.name, segment, s: nearest.s,
          point: nearest.point, gapMm: nearest.gapMm, radiusMm: nearest.radiusMm});
      }
    }
    arc += segmentLength;
  }
  return {status: totalContacts ? 'interference' : 'clear', contacts, totalContacts,
    truncated: totalContacts > contacts.length, testedTriangles, builtMeshes,
    elapsedMs: now() - started, method: 'capsule-surface',
    limitations: ['Screens triangle surfaces; does not solve friction or contact equilibrium.',
      'A span wholly enclosed inside a solid without crossing its surface is not detected.']};
}
