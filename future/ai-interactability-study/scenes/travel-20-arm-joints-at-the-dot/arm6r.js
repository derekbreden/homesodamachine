// arm6r.js: a UR3e-class 6R arm (the maker's published DH numbers): forward kinematics, a damped-least-squares inverse and the
// Jacobian at a point on the flange. Classic script (file:// safe); the same code as explorers/travel/calc/arm6r.mjs, which
// calc/15-arm-radial-line.mjs uses. Units mm and radians, +Z up. A GENERIC UR-type layout (shoulder yaw, three parallel pitch
// joints, two wrist joints) with the UR3e's link lengths; nothing else about the arm is modelled.
(function (global) {
const DH = [
  { d: 151.85, a: 0, al: Math.PI / 2 },
  { d: 0, a: -243.55, al: 0 },
  { d: 0, a: -213.2, al: 0 },
  { d: 131.05, a: 0, al: Math.PI / 2 },
  { d: 85.35, a: 0, al: -Math.PI / 2 },
  { d: 92.1, a: 0, al: 0 },
];

const I4 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function mul(A, B) { const C = new Array(16).fill(0); for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) { let s = 0; for (let k = 0; k < 4; k++) s += A[r * 4 + k] * B[k * 4 + c]; C[r * 4 + c] = s; } return C; }
function dhMat(th, d, a, al) { const ct = Math.cos(th), st = Math.sin(th), ca = Math.cos(al), sa = Math.sin(al); return [ct, -st * ca, st * sa, a * ct, st, ct * ca, -ct * sa, a * st, 0, sa, ca, d, 0, 0, 0, 1]; }
function baseMat(x, y, z, yaw) { const c = Math.cos(yaw), s = Math.sin(yaw); return [c, -s, 0, x, s, c, 0, y, 0, 0, 1, z, 0, 0, 0, 1]; }

// frames[i] = pose of link i (i = 0 base ... 6 flange) in the world
function fk(q, base) {
  const F = [base.slice()]; let T = base.slice();
  for (let i = 0; i < 6; i++) { T = mul(T, dhMat(q[i], DH[i].d, DH[i].a, DH[i].al)); F.push(T); }
  return F;
}
const pos = T => [T[3], T[7], T[11]], zax = T => [T[2], T[6], T[10]], xax = T => [T[0], T[4], T[8]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

// Jacobian at a world point p rigidly attached to the flange: columns = joint i (rows: vx vy vz wx wy wz)
function jac(F, p) {
  const J = []; for (let r = 0; r < 6; r++) J.push(new Array(6).fill(0));
  for (let i = 0; i < 6; i++) { const z = zax(F[i]), o = pos(F[i]), v = cross(z, sub(p, o)); for (let r = 0; r < 3; r++) { J[r][i] = v[r]; J[r + 3][i] = z[r]; } }
  return J;
}
function solve(A, b) { const n = b.length, M = A.map((r, i) => r.concat([b[i]])); for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; [M[c], M[p]] = [M[p], M[c]]; const d = M[c][c] || 1e-12; for (let r = c + 1; r < n; r++) { const f = M[r][c] / d; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; } } const x = new Array(n).fill(0); for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / (M[r][r] || 1e-12); } return x; }

// target: { p:[x,y,z] of the flange origin, z:[..] flange axis, x:[..] flange x-axis }. Returns { q, ok, errPos, errRot }.
function ik(target, base, q0, opts = {}) {
  let q = q0.slice(); const lam = opts.lam || 0.02; const zt = target.z, xt = target.x;
  for (let it = 0; it < (opts.iters || 200); it++) {
    const F = fk(q, base), T = F[6], p = pos(T);
    const ep = sub(target.p, p);
    // rotation error: sum of cross products of current and target axes (small-angle vector)
    const er1 = cross(xax(T), xt), er2 = cross(zax(T), zt);
    const er = [0.5 * (er1[0] + er2[0]), 0.5 * (er1[1] + er2[1]), 0.5 * (er1[2] + er2[2])];
    const w = 120;   // mm per rad: weight the rotation error like a lever
    const e = [ep[0], ep[1], ep[2], er[0] * w, er[1] * w, er[2] * w];
    const nrm = Math.hypot(...e); if (nrm < 1e-6) break;
    const J = jac(F, p); for (let r = 3; r < 6; r++) for (let c = 0; c < 6; c++) J[r][c] *= w;
    const JJt = []; for (let r = 0; r < 6; r++) { JJt.push([]); for (let c = 0; c < 6; c++) { let s = 0; for (let k = 0; k < 6; k++) s += J[r][k] * J[c][k]; JJt[r].push(s + (r === c ? lam * lam * 1e4 : 0)); } }
    const y = solve(JJt, e); const dq = new Array(6).fill(0); for (let i = 0; i < 6; i++) { let s = 0; for (let r = 0; r < 6; r++) s += J[r][i] * y[r]; dq[i] = s; }
    const step = Math.min(1, 0.6 / Math.max(1e-9, Math.max(...dq.map(Math.abs)))); for (let i = 0; i < 6; i++) q[i] += dq[i] * step;
  }
  const F = fk(q, base), T = F[6], ep = sub(target.p, pos(T)), a1 = cross(xax(T), xt), a2 = cross(zax(T), zt);
  return { q, F, errPos: Math.hypot(...ep), errRot: Math.hypot(...a1, ...a2) / Math.SQRT2 };
}

function ikBest(target, base, opts = {}) {
  // multi-start; choose the converged solution nearest a preferred posture (shoulder up, elbow bent, wrist pointing down-ish)
  const ref = opts.ref || [0, -1.2, 1.9, -2.3, -1.57, 0];
  const az = Math.atan2(target.p[1] - base[7], target.p[0] - base[3]) - Math.atan2(base[4], base[0]);
  const seeds = []; for (const q1 of [az, az + Math.PI]) for (const q2 of [-1.9, -1.2, -0.5]) for (const q3 of [-1.9, 1.9, 1.0]) for (const q4 of [-1.6, 1.6, 0]) for (const q5 of [-1.57, 1.57]) seeds.push([q1, q2, q3, q4, q5, 0]);
  let best = null;
  for (const s of seeds) {
    const r = ik(target, base, s, { iters: 90 }); if (r.errPos > 0.05 || r.errRot > 1e-3) continue;
    const wrap = a => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };
    r.q = r.q.map(wrap);
    const cost = r.q.reduce((t, v, i) => t + Math.abs(wrap(v - ref[i])) * (i === 5 ? 0.2 : 1), 0);
    if (!best || cost < best.cost) best = Object.assign(r, { cost });
  }
  return best;
}

global.ARM6R = { DH: DH, fk: fk, jac: jac, ik: ik, ikBest: ikBest, baseMat: baseMat };
})(window);
