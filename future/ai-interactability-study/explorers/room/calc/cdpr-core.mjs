// cdpr-core.mjs - small dependency-free kernel for the "corner cords" idea (room-06): eight taut lines from fixed anchors
// to lugs on the gun shell. Tension solve (non-negative, with a minimum pretension), translational stiffness, forward
// kinematics by Gauss-Newton, and a tiny dense linear solver. Classic maths, written out so it can be pasted into a scene.
// Units: mm, N. The gun's mass / centre of mass / umbilical pull are [unknown]; callers pass [illustrative] values.

export const V = {
  add: (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]],
  sub: (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]],
  scl: (a, k) => [a[0] * k, a[1] * k, a[2] * k],
  dot: (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2],
  cross: (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]],
  len: a => Math.hypot(a[0], a[1], a[2]),
  unit: a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; },
};
export const M3 = {
  mulV: (m, v) => [m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2], m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2], m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]],
  mul: (a, b) => [0, 1, 2].map(i => [0, 1, 2].map(j => a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j])),
  rodrigues: w => {
    const th = Math.hypot(w[0], w[1], w[2]);
    if (th < 1e-12) return [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const k = [w[0] / th, w[1] / th, w[2] / th], c = Math.cos(th), s = Math.sin(th), t = 1 - c;
    return [[t * k[0] * k[0] + c, t * k[0] * k[1] - s * k[2], t * k[0] * k[2] + s * k[1]],
            [t * k[0] * k[1] + s * k[2], t * k[1] * k[1] + c, t * k[1] * k[2] - s * k[0]],
            [t * k[0] * k[2] - s * k[1], t * k[1] * k[2] + s * k[0], t * k[2] * k[2] + c]];
  },
  fromColumns: (x, y, z) => [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]],
  inv3: m => {
    const [a, b, c] = m[0], [d, e, f] = m[1], [g, h, i] = m[2];
    const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g, det = a * A + b * B + c * C;
    return [[A / det, -(b * i - c * h) / det, (b * f - c * e) / det], [B / det, (a * i - c * g) / det, -(a * f - c * d) / det], [C / det, -(a * h - b * g) / det, (a * e - b * d) / det]];
  },
};

// Solve A x = b for a dense square system by Gaussian elimination with partial pivoting (small n).
export function solveLinear(A, b) {
  const n = b.length, M = A.map((r, i) => r.slice().concat([b[i]]));
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    if (Math.abs(M[p][c]) < 1e-14) return null;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
  }
  const x = new Array(n).fill(0);
  for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / M[r][r]; }
  return x;
}

// Lawson-Hanson NNLS: minimise |A s - b| subject to s >= 0. A is m x n (array of rows).
export function nnls(A, b, maxIter = 200) {
  const m = A.length, n = A[0].length;
  const x = new Array(n).fill(0), P = new Array(n).fill(false);
  const AT = (v) => { const w = new Array(n).fill(0); for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) w[j] += A[i][j] * v[i]; return w; };
  const resid = () => b.map((bi, i) => bi - A[i].reduce((s, a, j) => s + a * x[j], 0));
  const lsq = (idx) => {   // least squares on columns idx
    const k = idx.length, G = idx.map(i => idx.map(j => { let s = 0; for (let r = 0; r < m; r++) s += A[r][i] * A[r][j]; return s + (i === j ? 1e-12 : 0); }));
    const h = idx.map(i => { let s = 0; for (let r = 0; r < m; r++) s += A[r][i] * b[r]; return s; });
    return solveLinear(G, h);
  };
  for (let it = 0; it < maxIter; it++) {
    const w = AT(resid());
    let t = -1, best = 1e-10;
    for (let j = 0; j < n; j++) if (!P[j] && w[j] > best) { best = w[j]; t = j; }
    if (t < 0) break;
    P[t] = true;
    for (let inner = 0; inner < 100; inner++) {
      const idx = P.map((p, j) => p ? j : -1).filter(j => j >= 0);
      const z = lsq(idx);
      if (!z) { P[t] = false; break; }
      if (z.every(v => v > 1e-12)) { idx.forEach((j, k) => { x[j] = z[k]; }); for (let j = 0; j < n; j++) if (!P[j]) x[j] = 0; break; }
      let alpha = Infinity;
      idx.forEach((j, k) => { if (z[k] <= 1e-12) { const a = x[j] / (x[j] - z[k]); if (a < alpha) alpha = a; } });
      idx.forEach((j, k) => { x[j] += alpha * (z[k] - x[j]); });
      for (const j of idx) if (Math.abs(x[j]) < 1e-12) { x[j] = 0; P[j] = false; }
    }
  }
  const r = resid();
  return { x, resNorm: Math.hypot(...r) };
}

// Structure: anchors a[i] (world), lugs l[i] (LOCAL to the gun, same frame as `dotLocal`), pose {R, p} where p is the
// world position of dotLocal and R the world rotation of the gun. Returns geometry of cord i.
export function cordGeometry(anchors, lugsLocal, dotLocal, pose) {
  return anchors.map((a, i) => {
    const lw = V.add(pose.p, M3.mulV(pose.R, V.sub(lugsLocal[i], dotLocal)));
    const d = V.sub(a, lw), L = V.len(d);
    return { lugW: lw, anchor: a, L, u: V.scl(d, 1 / L) };   // u: unit vector from lug toward the anchor (the direction the cord pulls the gun)
  });
}

// Tension solve. wrench = external force F (N, world) and moment M about `com` (N mm) acting on the gun (gravity, umbilical pull...).
// Cords must satisfy sum(t_i u_i) + F = 0 and sum((l_i - com) x t_i u_i) + M = 0 with t_i >= tMin.
export function solveTensions(geo, com, F, Mo, tMin) {
  const n = geo.length;
  const A = [[], [], [], [], [], []];
  geo.forEach(g => {
    const r = V.sub(g.lugW, com), m = V.cross(r, g.u);
    [g.u[0], g.u[1], g.u[2], m[0], m[1], m[2]].forEach((v, k) => A[k].push(v));
  });
  const rhs0 = [-F[0], -F[1], -F[2], -Mo[0], -Mo[1], -Mo[2]];
  const shift = A.map(row => row.reduce((s, a) => s + a, 0) * tMin);
  const b = rhs0.map((v, k) => v - shift[k]);
  const { x, resNorm } = nnls(A, b);
  const t = x.map(v => v + tMin);
  return { t, resNorm, A, feasible: resNorm < 1e-6 * (1 + Math.hypot(...rhs0)) };
}

// Translational stiffness matrix at the gun (3x3, N/mm) for cord axial stiffness EA (N): k_i = EA / L_i plus geometric T_i/L_i.
export function stiffness3(geo, t, EA) {
  const K = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  geo.forEach((g, i) => {
    const ki = EA / g.L, gi = t[i] / g.L;
    for (let a = 0; a < 3; a++) for (let c = 0; c < 3; c++) {
      const uu = g.u[a] * g.u[c];
      K[a][c] += ki * uu + gi * ((a === c ? 1 : 0) - uu);
    }
  });
  return K;
}

// Symmetric 3x3 eigenvalues (Jacobi) - returns sorted ascending eigenvalues and the eigenvector of the smallest.
export function eig3(K) {
  const A = K.map(r => r.slice()), Vv = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  for (let sweep = 0; sweep < 50; sweep++) {
    let off = 0; for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) off += A[i][j] * A[i][j];
    if (off < 1e-18) break;
    for (let p = 0; p < 2; p++) for (let q = p + 1; q < 3; q++) {
      if (Math.abs(A[p][q]) < 1e-18) continue;
      const th = (A[q][q] - A[p][p]) / (2 * A[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < 3; k++) { const akp = A[k][p], akq = A[k][q]; A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq; }
      for (let k = 0; k < 3; k++) { const apk = A[p][k], aqk = A[q][k]; A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk; }
      for (let k = 0; k < 3; k++) { const vkp = Vv[k][p], vkq = Vv[k][q]; Vv[k][p] = c * vkp - s * vkq; Vv[k][q] = s * vkp + c * vkq; }
    }
  }
  const ev = [A[0][0], A[1][1], A[2][2]], order = [0, 1, 2].sort((i, j) => ev[i] - ev[j]);
  return { values: order.map(i => ev[i]), weakest: [Vv[0][order[0]], Vv[1][order[0]], Vv[2][order[0]]] };
}

// Forward kinematics: given cord lengths Ls (mm) and the geometry (anchors, lugsLocal, dotLocal), find the pose (p, R) by
// Gauss-Newton starting from `init` {p, R}. Returns {p, R, rms}.
export function forwardKin(anchors, lugsLocal, dotLocal, Ls, init, iters = 30) {
  let p = init.p.slice(), R = init.R.map(r => r.slice());
  for (let it = 0; it < iters; it++) {
    const geo = cordGeometry(anchors, lugsLocal, dotLocal, { p, R });
    const r = geo.map((g, i) => g.L - Ls[i]);
    const J = geo.map(g => { const rl = V.sub(g.lugW, p); const m = V.cross(rl, g.u); return [-g.u[0], -g.u[1], -g.u[2], -m[0], -m[1], -m[2]]; });   // d L / d [dp, dw] (world-frame small rotation about p)
    const JTJ = Array.from({ length: 6 }, (_, i) => Array.from({ length: 6 }, (_, j) => J.reduce((s, row) => s + row[i] * row[j], 0) + (i === j ? 1e-9 : 0)));
    const JTr = Array.from({ length: 6 }, (_, i) => J.reduce((s, row, k) => s + row[i] * r[k], 0));
    const dx = solveLinear(JTJ, JTr.map(v => -v));
    if (!dx) break;
    p = V.add(p, dx.slice(0, 3));
    R = M3.mul(M3.rodrigues(dx.slice(3, 6)), R);
    if (Math.hypot(...dx) < 1e-10) break;
  }
  const geo = cordGeometry(anchors, lugsLocal, dotLocal, { p, R });
  return { p, R, rms: Math.sqrt(geo.reduce((s, g, i) => s + (g.L - Ls[i]) ** 2, 0) / geo.length) };
}

// tiny seeded RNG for reproducible Monte Carlo
export function rng(seed) {
  let a = seed >>> 0;
  const u = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const n = () => { let x = 0, y = 0; while (x === 0) x = u(); y = u(); return Math.sqrt(-2 * Math.log(x)) * Math.cos(2 * Math.PI * y); };
  return { u, n };
}
