/* statics.js - a small rigid-body-on-springs statics solver used by the freedom scenes and calc scripts.
 *
 * What it models: ONE rigid body (the gun in its printed shell) plus massless "ring nodes", tied to fixed
 * points and to each other by springs, wires (very stiff springs that only pull), lateral ring pins, seats and
 * point pins. Forces: gravity and constant forces (umbilical pull, trigger). It finds the pose that minimises the
 * potential energy (Newton with damping, numeric Hessian) and returns the Hessian, so callers can read stiffness
 * and compliance at the dot.
 *
 * What it does NOT model: friction and stick-slip, hysteresis and creep of bungees, cable dynamics, vibration,
 * shell flexibility, real ring clearance. Every stiffness, mass and force a scene feeds it is ILLUSTRATIVE
 * unless a comment says otherwise. The output says which way things move and by roughly how much per newton;
 * it is not a measurement.
 *
 * Units: millimetres, newtons, so stiffness is N/mm, energy is N*mm, torque N*mm. +Z up (as the kit).
 * Pose variables: x[0..2] = dot displacement u (mm); x[3..5] = rotation vector theta about the dot, world
 * frame, stored as S*theta (mm) with S = 100 mm so all variables share one unit; x[6+3i..] = displacement of ring node i.
 *
 * UMD: window.FreedomStatics in a page, module.exports in node.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FreedomStatics = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const S = 100;           // mm: rotation variable scale
  const smax = e => 0.5 * (e + Math.sqrt(e * e + 4e-4));   // smoothed max(e,0), delta = 0.02 mm
  const G = 9.80665;       // m/s^2

  // ------------------------------------------------------------------ tiny maths (arrays)
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const len = a => Math.sqrt(dot(a, a));
  const norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  // rotation matrix (row-major 3x3 as 9-array) from rotation vector
  function expm(w) {
    const t = Math.sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
    let a, b;
    if (t < 1e-8) { a = 1 - t * t / 6; b = 0.5 - t * t / 24; } else { a = Math.sin(t) / t; b = (1 - Math.cos(t)) / (t * t); }
    const x = w[0], y = w[1], z = w[2];
    return [
      1 - b * (y * y + z * z), -a * z + b * x * y, a * y + b * x * z,
      a * z + b * x * y, 1 - b * (x * x + z * z), -a * x + b * y * z,
      -a * y + b * x * z, a * x + b * y * z, 1 - b * (x * x + y * y)];
  }
  const mv = (M, v) => [M[0] * v[0] + M[1] * v[1] + M[2] * v[2], M[3] * v[0] + M[4] * v[1] + M[5] * v[2], M[6] * v[0] + M[7] * v[1] + M[8] * v[2]];
  const mm = (A, B) => {
    const C = new Array(9);
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[i * 3 + j] = A[i * 3] * B[j] + A[i * 3 + 1] * B[3 + j] + A[i * 3 + 2] * B[6 + j];
    return C;
  };

  // ------------------------------------------------------------------ reference pose: port of WK.dialsToPose (kit/weldkit.js)
  // The kit's local frame: origin nozzle tip, +Z toward the back of the gun, -Y grip side, dot at (0,0,-16).
  const IN = 25.4, DEG = Math.PI / 180;
  const INNER_RADIUS = 2.5 * IN - 0.065 * IN;
  const CAP_TOP = 6 * IN - 0.25 * IN;
  const JOINT = [INNER_RADIUS, 0, CAP_TOP];
  const PITCH = 60 * DEG, CLEARANCE = 16;
  const GRIP_BASE = [0, -118, 237];
  const ROLL_AXIS = (function () { const l = Math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE); return [0, GRIP_BASE[1] / l, (GRIP_BASE[2] + CLEARANCE) / l]; })();
  const HOLE_AXIS_OFFSET = 35;
  function posePointArr(p, rollDeg, holeRollDeg, vertDeg) {
    const x = p[0], y = p[1], z = p[2], s = Math.sin(PITCH), c = Math.cos(PITCH);
    const along = z + CLEARANCE, py = -c * along + s * y, pz = s * along + c * y, roll = rollDeg * DEG;
    const ay = -c * ROLL_AXIS[2] + s * ROLL_AXIS[1], az = s * ROLL_AXIS[2] + c * ROLL_AXIS[1];
    const d = ay * py + az * pz, cr = Math.cos(roll), sr = Math.sin(roll);
    const rx = x * cr + (ay * pz - az * py) * sr, ry = py * cr + az * x * sr + ay * d * (1 - cr), rz = pz * cr - ay * x * sr + az * d * (1 - cr);
    const hr = holeRollDeg * DEG, ch = Math.cos(hr), sh = Math.sin(hr), hy = ry * ch + rz * sh, hz = -ry * sh + rz * ch;
    const v = vertDeg * DEG, cv = Math.cos(v), sv = Math.sin(v);
    return [JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz];
  }
  // -> { origin (world position of the nozzle-tip origin), R (row-major 3x3: world = origin + R * local) }
  function dialsToPose(roll, holeDial, vertical) {
    const hr = holeDial - HOLE_AXIS_OFFSET, o = posePointArr([0, 0, 0], roll, hr, vertical);
    const cols = [0, 1, 2].map(k => { const p = [0, 0, 0]; p[k] = 1; const q = posePointArr(p, roll, hr, vertical); return sub(q, o); });
    return { origin: o, R: [cols[0][0], cols[1][0], cols[2][0], cols[0][1], cols[1][1], cols[2][1], cols[0][2], cols[1][2], cols[2][2]] };
  }

  // ------------------------------------------------------------------ dense linear algebra (small)
  function solveLinear(A, b, n) {           // Gaussian elimination with partial pivoting; A is n*n row-major (copied)
    const M = new Float64Array(n * (n + 1));
    for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) M[i * (n + 1) + j] = A[i * n + j]; M[i * (n + 1) + n] = b[i]; }
    for (let c = 0; c < n; c++) {
      let p = c, best = Math.abs(M[c * (n + 1) + c]);
      for (let r = c + 1; r < n; r++) { const v = Math.abs(M[r * (n + 1) + c]); if (v > best) { best = v; p = r; } }
      if (best < 1e-14) return null;
      if (p !== c) for (let j = c; j <= n; j++) { const t = M[c * (n + 1) + j]; M[c * (n + 1) + j] = M[p * (n + 1) + j]; M[p * (n + 1) + j] = t; }
      for (let r = c + 1; r < n; r++) {
        const f = M[r * (n + 1) + c] / M[c * (n + 1) + c];
        if (f !== 0) for (let j = c; j <= n; j++) M[r * (n + 1) + j] -= f * M[c * (n + 1) + j];
      }
    }
    const x = new Float64Array(n);
    for (let i = n - 1; i >= 0; i--) { let s = M[i * (n + 1) + n]; for (let j = i + 1; j < n; j++) s -= M[i * (n + 1) + j] * x[j]; x[i] = s / M[i * (n + 1) + i]; }
    return x;
  }
  // Jacobi eigen-decomposition of a symmetric matrix -> {values[], vectors[][]} (vectors[k] is the k-th eigenvector)
  function eigSym(A, n) {
    const a = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => A[i * n + j]));
    const v = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += a[i][j] * a[i][j];
      if (off < 1e-22) break;
      for (let p = 0; p < n - 1; p++) for (let q = p + 1; q < n; q++) {
        if (Math.abs(a[p][q]) < 1e-30) continue;
        const th = (a[q][q] - a[p][p]) / (2 * a[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) { const akp = a[k][p], akq = a[k][q]; a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq; }
        for (let k = 0; k < n; k++) { const apk = a[p][k], aqk = a[q][k]; a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk; }
        for (let k = 0; k < n; k++) { const vkp = v[k][p], vkq = v[k][q]; v[k][p] = c * vkp - s * vkq; v[k][q] = s * vkp + c * vkq; }
      }
    }
    const vals = a.map((r, i) => r[i]);
    const order = vals.map((x, i) => i).sort((i, j) => vals[i] - vals[j]);
    return { values: order.map(i => vals[i]), vectors: order.map(i => v.map(r => r[i])) };
  }

  // ------------------------------------------------------------------ the model
  /* spec = {
   *   body: { mass (kg), com: local point, ref: { origin, R } (from dialsToPose), dotLocal: [0,0,-16] },
   *   nodes: [ { name, p0: [x,y,z] } ... ]                 // massless ring nodes, initial (reference) positions
   *   elements: [ ... see below ... ]
   * }
   * A point reference `pt` is one of  { local: [x,y,z] } (fixed on the body),  { node: i },  { world: [x,y,z] }.
   * Elements (all have `name`, `group` for shares; `off:true` disables):
   *   { type:'gravity' }                                      body weight from spec.body.mass, at com
   *   { type:'force', pt, F:[fx,fy,fz] }                      constant force (N) at a point on the body or on a node
   *   { type:'spring', a:pt, b:pt, k, L0, slack:true|false }  N/mm; slack=true => pulls only (bungee, wire)
   *   { type:'ring', node:i, local:[..], axis:[..local], k }  node is held on the body's axis line (lateral penalty)
   *   { type:'stop', node:i, local:[..], axis:[..local], side:+1|-1, k }  unilateral axial seat: node cannot go beyond
   *                                                            the body point along side*axis (collar against ring)
   *   { type:'slip', node:i, local:[..], axis:[..local], k, Fmax }  friction hold along the axis: elastic to Fmax (N), then slides
   *   { type:'cone', local, a:[x,y,z], sinPhi, cosPhi, rc, k }      sphere-in-cone seat (unilateral): collar centre stays above the cone surface
   *   { type:'pin', a:pt, b:pt, k }                           3D point pin (zero rest length): arm grip point / ball seat
   *   { type:'rot', k, ref?: [wx,wy,wz] }                     rotational stiffness about the dot (N*mm/rad) to the reference
   *                                                            orientation (a rigid grip in an arm end)
   */
  function makeModel(spec) {
    const body = spec.body, nodes = spec.nodes || [], els = spec.elements;
    const n = 6 + 3 * nodes.length;
    const R0 = body.ref.R, o0 = body.ref.origin, dl = body.dotLocal || [0, 0, -CLEARANCE];
    const dot0 = add(o0, mv(R0, dl));
    const model = { n: n, spec: spec, S: S, dot0: dot0, R0: R0, o0: o0 };
    const RL = mv(R0, [0, 0, 0]);
    void RL;

    // world position of a body-local point at pose x
    function bodyPoint(x, Rw, local) {
      const rel = sub(local, dl), p = mv(Rw, rel);
      return [dot0[0] + x[0] + p[0], dot0[1] + x[1] + p[1], dot0[2] + x[2] + p[2]];
    }
    function rotOf(x) { return mm(expm([x[3] / S, x[4] / S, x[5] / S]), R0); }   // world-from-local
    function nodePos(x, i) { const b = 6 + 3 * i, p0 = nodes[i].p0; return [p0[0] + x[b], p0[1] + x[b + 1], p0[2] + x[b + 2]]; }
    function resolve(x, Rw, pt) {
      if (pt.local) return bodyPoint(x, Rw, pt.local);
      if (pt.node != null) return nodePos(x, pt.node);
      return pt.world;
    }
    model.bodyPoint = function (x, local) { return bodyPoint(x, rotOf(x), local); };
    model.nodePos = nodePos;
    model.rotOf = rotOf;
    model.worldOf = function (x, pt) { return resolve(x, rotOf(x), pt); };
    model.bodyDir = function (x, localDir) { return mv(rotOf(x), mv(mm([1, 0, 0, 0, 1, 0, 0, 0, 1], [1, 0, 0, 0, 1, 0, 0, 0, 1]), localDir)); };

    // energy of one element (returns N*mm). Also used for per-element shares.
    function elementEnergy(el, x, Rw) {
      if (el.off) return 0;
      switch (el.type) {
        case 'gravity': { const p = bodyPoint(x, Rw, body.com); return body.mass * G * p[2]; }
        case 'force': { const p = resolve(x, Rw, el.pt); return -(el.F[0] * p[0] + el.F[1] * p[1] + el.F[2] * p[2]); }
        case 'spring': {
          const a = resolve(x, Rw, el.a), b = resolve(x, Rw, el.b), dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
          const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
          let e = d - el.L0;
          if (el.slack) { const del = Math.min(0.5, Math.max(0.02, 0.3 / el.k)); e = 0.5 * (e + Math.sqrt(e * e + del * del)); }   // smoothed max(e,0): keeps the Hessian well behaved at the taut/slack kink
          return 0.5 * el.k * e * e;
        }
        case 'pin': {
          const a = resolve(x, Rw, el.a), b = resolve(x, Rw, el.b), dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
          return 0.5 * el.k * (dx * dx + dy * dy + dz * dz);
        }
        case 'ring': {
          const q = bodyPoint(x, Rw, el.local), ax = mv(Rw, el.axis), r = nodePos(x, el.node);
          const dx = r[0] - q[0], dy = r[1] - q[1], dz = r[2] - q[2], al = dx * ax[0] + dy * ax[1] + dz * ax[2];
          const px = dx - al * ax[0], py = dy - al * ax[1], pz = dz - al * ax[2];
          return 0.5 * el.k * (px * px + py * py + pz * pz);
        }
        case 'stop': {
          const q = bodyPoint(x, Rw, el.local), ax = mv(Rw, el.axis), r = nodePos(x, el.node);
          const al = (r[0] - q[0]) * ax[0] + (r[1] - q[1]) * ax[1] + (r[2] - q[2]) * ax[2];
          const pen = smax(el.side * al - (el.gap || 0));      // penetration if > 0 (smoothed)
          return 0.5 * el.k * pen * pen;
        }
        case 'slip': {   // friction-limited axial hold: elastic up to Fmax, then slides (static approximation, no history)
          const q = bodyPoint(x, Rw, el.local), ax = mv(Rw, el.axis), r = nodePos(x, el.node);
          const sl = (r[0] - q[0]) * ax[0] + (r[1] - q[1]) * ax[1] + (r[2] - q[2]) * ax[2], a = Math.abs(sl), sc = el.Fmax / el.k;
          return a <= sc ? 0.5 * el.k * sl * sl : el.Fmax * (a - 0.5 * sc);
        }
        case 'cone': {   // sphere (collar, radius rc, centre at body point `local`) resting in a circular cone whose vertical axis passes through world point `a`
          const c = bodyPoint(x, Rw, el.local), rx = c[0] - el.a[0], ry = c[1] - el.a[1], h = c[2] - el.a[2], rho = Math.sqrt(rx * rx + ry * ry + 0.0025);   // 0.05 mm regulariser: the apex line is otherwise a kink
          const d = h * el.sinPhi - rho * el.cosPhi, pen = el.rc - d;
          const pp = smax(pen);
          return 0.5 * el.k * pp * pp;
        }
        case 'rot': {
          const rx = x[3], ry = x[4], rz = x[5];
          const ref = el.ref || [0, 0, 0], dx = rx - ref[0], dy = ry - ref[1], dz = rz - ref[2];
          return 0.5 * (el.k / (S * S)) * (dx * dx + dy * dy + dz * dz);       // k in N*mm/rad; x holds S*theta
        }
        default: return 0;
      }
    }
    model.elementEnergy = function (el, x) { return elementEnergy(el, x, rotOf(x)); };
    function energy(x) {
      const Rw = rotOf(x); let E = 0;
      for (let i = 0; i < els.length; i++) E += elementEnergy(els[i], x, Rw);
      return E;
    }
    model.energy = energy;
    model.energyByGroup = function (x) { const Rw = rotOf(x), out = {}; els.forEach(el => { const e = elementEnergy(el, x, Rw); if (e) out[el.group || el.name || el.type] = (out[el.group || el.name || el.type] || 0) + e; }); return out; };

    // gradient (central difference) and Hessian (central differences of the gradient)
    const H_STEP = 2e-3;
    function grad(x) {
      const g = new Float64Array(n), xp = Float64Array.from(x);
      for (let i = 0; i < n; i++) { const xi = xp[i]; xp[i] = xi + H_STEP; const e1 = energy(xp); xp[i] = xi - H_STEP; const e2 = energy(xp); xp[i] = xi; g[i] = (e1 - e2) / (2 * H_STEP); }
      return g;
    }
    function hess(x) {
      const H = new Float64Array(n * n), xp = Float64Array.from(x), hs = 4e-3;
      for (let j = 0; j < n; j++) {
        const xj = xp[j]; xp[j] = xj + hs; const g1 = grad(xp); xp[j] = xj - hs; const g2 = grad(xp); xp[j] = xj;
        for (let i = 0; i < n; i++) H[i * n + j] = (g1[i] - g2[i]) / (2 * hs);
      }
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { const m = 0.5 * (H[i * n + j] + H[j * n + i]); H[i * n + j] = m; H[j * n + i] = m; }
      return H;
    }
    model.grad = grad; model.hess = hess;

    // Newton with damping and a trust region. Returns { x, E, iters, gnorm, converged }.
    model.solve = function (x0, o) {
      o = o || {};
      let x = Float64Array.from(x0 || new Float64Array(n)), E = energy(x), lam = 1e-3, iters = 0;
      const maxIt = o.maxIter || 40, trust = o.trust || 25, tol = o.tol || 1e-5;
      let g = grad(x), gn = 0;
      for (; iters < maxIt; iters++) {
        gn = 0; for (let i = 0; i < n; i++) gn = Math.max(gn, Math.abs(g[i]));
        if (gn < tol) break;
        const H = hess(x);
        let stepped = false;
        for (let tries = 0; tries < 12; tries++) {
          const A = Float64Array.from(H); for (let i = 0; i < n; i++) A[i * n + i] += lam + 1e-7;
          const rhs = new Float64Array(n); for (let i = 0; i < n; i++) rhs[i] = -g[i];
          const d = solveLinear(A, rhs, n);
          if (!d) { lam *= 10; continue; }
          let dm = 0; for (let i = 0; i < n; i++) dm = Math.max(dm, Math.abs(d[i]));
          if (dm > trust) for (let i = 0; i < n; i++) d[i] *= trust / dm;
          const xn = new Float64Array(n); for (let i = 0; i < n; i++) xn[i] = x[i] + d[i];
          const En = energy(xn);
          if (En <= E + 1e-12) { x = xn; E = En; lam = Math.max(lam / 4, 1e-9); stepped = true; break; }
          lam *= 6;
        }
        if (!stepped) break;
        g = grad(x);
      }
      gn = 0; for (let i = 0; i < n; i++) gn = Math.max(gn, Math.abs(g[i]));
      return { x: x, E: E, iters: iters, gnorm: gn, converged: gn < (o.accept || 0.05) };
    };

    // compliance of the dot to a pure force at the dot: 3x3 block of H^-1 (mm/N), with a small regulariser.
    // A direction with no restoring stiffness comes back large (capped at cap mm/N) and flagged free.
    model.dotCompliance = function (x, o) {
      o = o || {};
      const H = hess(x), reg = o.reg || 1e-4, cap = o.cap || 1000;
      const A = Float64Array.from(H); for (let i = 0; i < n; i++) A[i * n + i] += reg;
      const C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
      for (let k = 0; k < 3; k++) {
        const e = new Float64Array(n); e[k] = 1;
        const sol = solveLinear(A, e, n);
        for (let i = 0; i < 3; i++) C[i][k] = sol ? Math.min(cap, sol[i]) : cap;
      }
      const ev = eigSym(H, n);
      return { C: C, H: H, eig: ev, free: ev.values.filter(v => v < 1e-3).length };
    };
    // per-element share of the Hessian diagonal along a direction d (length n vector); returns {group: k_share}
    model.stiffnessShares = function (x, d) {
      const res = {}, xp = Float64Array.from(x), h = 4e-3, Rw0 = null; void Rw0;
      els.forEach(function (el) {
        if (el.off) return;
        const e0 = elementEnergy(el, x, rotOf(x));
        const xa = Float64Array.from(x), xb = Float64Array.from(x);
        for (let i = 0; i < n; i++) { xa[i] += h * d[i]; xb[i] -= h * d[i]; }
        const k = (elementEnergy(el, xa, rotOf(xa)) - 2 * e0 + elementEnergy(el, xb, rotOf(xb))) / (h * h);
        const key = el.group || el.name || el.type; res[key] = (res[key] || 0) + k;
      });
      void xp;
      return res;
    };
    // net force by element on the body at x (world forces at the attachment, for reading loads): spring/pin only
    model.springForce = function (x, el) {
      const Rw = rotOf(x);
      if (el.type === 'spring') {
        const a = resolve(x, Rw, el.a), b = resolve(x, Rw, el.b), d = sub(a, b), L = len(d), e = L - el.L0;
        if (el.slack && e <= 0) return { T: 0, len: L, dir: norm(d) };
        return { T: el.k * e, len: L, dir: norm(d) };
      }
      if (el.type === 'pin') { const a = resolve(x, Rw, el.a), b = resolve(x, Rw, el.b), d = sub(a, b); return { T: el.k * len(d), len: len(d), F: mul(d, -el.k) }; }
      return null;
    };
    return model;
  }

  // Given the elements of a suspension, choose rest lengths so the reference pose is an equilibrium with the
  // requested preload. helper for scenes: L0 = length_at_ref - T/k for each spring with a `preload` (N).
  function setRestLengths(model, elements) {
    const x0 = new Float64Array(model.n);
    const Rw = model.rotOf(x0);
    elements.forEach(function (el) {
      if (el.type !== 'spring' || el.preload == null) return;
      const r = (pt) => (pt.local ? model.bodyPoint(x0, pt.local) : pt.node != null ? model.nodePos(x0, pt.node) : pt.world);
      const L = len(sub(r(el.a), r(el.b)));
      el.L0 = L - el.preload / el.k;
    });
    void Rw;
    return elements;
  }

  return { makeModel: makeModel, dialsToPose: dialsToPose, posePointArr: posePointArr, setRestLengths: setRestLengths,
    S: S, G: G, JOINT: JOINT, INNER_RADIUS: INNER_RADIUS, CAP_TOP: CAP_TOP, GRIP_BASE: GRIP_BASE, ROLL_AXIS: ROLL_AXIS, CLEARANCE: CLEARANCE,
    math: { add: add, sub: sub, mul: mul, dot: dot, cross: cross, len: len, norm: norm, expm: expm, mv: mv, mm: mm, solveLinear: solveLinear, eigSym: eigSym } };
});
