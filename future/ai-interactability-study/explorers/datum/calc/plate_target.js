// The plate and the rim as a calibration target: a camera over the bore fits its own pose (and the seat depth) from the rim circle
// and the two ports, then predicts where the corner is. Used by scene datum-19; run in node for the numbers in the exchange.
'use strict';
const TAU = Math.PI * 2, DEG = Math.PI / 180;
function rng(seed) { let a = seed >>> 0; return function () { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0, v = 0; while (u === 0) u = r(); v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v); }
const F = 1500, U0 = 640, V0 = 480, RI = 61.85, RO = 63.5, PORT = 19.05, PZ = 6.35;
// pose p = [cx, cy, H, tx, ty, ds]; world z up, rim plane z = 0, plate outer face at z = -(6.35 + ds)
function project(X, p) {
  let x = X[0] - p[0], y = X[1] - p[1], z = X[2] - p[2];
  // base: camera x = world x, camera y = -world y, camera z = -world z
  let cxv = x, cyv = -y, czv = -z;
  // tilts about camera y then camera x (small)
  const cty = Math.cos(p[4]), sty = Math.sin(p[4]), ctx = Math.cos(p[3]), stx = Math.sin(p[3]);
  let x1 = cty * cxv + sty * czv, z1 = -sty * cxv + cty * czv, y1 = cyv;
  let y2 = ctx * y1 - stx * z1, z2 = stx * y1 + ctx * z1;
  return [U0 + F * x1 / z2, V0 + F * y2 / z2];
}
function backproject(uv, p, zPlane) {                 // pixel -> point on the plane z = zPlane, for a camera with pose p
  const xn = (uv[0] - U0) / F, yn = (uv[1] - V0) / F;
  // ray in camera coordinates (xn, yn, 1); undo tilts, then base
  const cty = Math.cos(p[4]), sty = Math.sin(p[4]), ctx = Math.cos(p[3]), stx = Math.sin(p[3]);
  let x2 = xn, y2 = yn, z2 = 1;
  let y1 = ctx * y2 + stx * z2, z1 = -stx * y2 + ctx * z2, x1 = x2;
  let cx_ = cty * x1 - sty * z1, cz_ = sty * x1 + cty * z1, cy_ = y1;
  // world direction: x = cx_, y = -cy_, z = -cz_
  const d = [cx_, -cy_, -cz_], t = (zPlane - p[2]) / d[2];
  return [p[0] + t * d[0], p[1] + t * d[1], zPlane];
}
function features(ds, NP) {                            // known world points (correspondences known: roll from the ports)
  const pts = [];
  for (let k = 0; k < NP; k++) { const a = TAU * k / NP; pts.push([RI * Math.cos(a), RI * Math.sin(a), 0]); pts.push([RO * Math.cos(a), RO * Math.sin(a), 0]); }
  pts.push([PORT, 0, -(PZ + ds)]); pts.push([-PORT, 0, -(PZ + ds)]);
  return pts;
}
function solve(obs, pts0, p0, sigmaPx, free) {         // p0 nominal; free[j] false pins parameter j (used for the seat depth)
  free = free || [true, true, true, true, true, true];
  let p = p0.slice(); const n = 6, NP = (pts0.length - 2);
  const model = pp => { const pts = pts0.slice(0, NP).concat([[PORT, 0, -(PZ + pp[5])], [-PORT, 0, -(PZ + pp[5])]]); return pts.map(X => project(X, pp)); };
  let lam = 1e-3;
  for (let it = 0; it < 30; it++) {
    const m = model(p), r = []; m.forEach((q, i) => { r.push(q[0] - obs[i][0], q[1] - obs[i][1]); });
    const J = Array.from({ length: r.length }, () => new Array(n).fill(0));
    for (let j = 0; j < n; j++) { const h = j < 3 ? 1e-3 * (j === 2 ? 100 : 1) : (j < 5 ? 1e-6 : 1e-4), pp = p.slice(), pm = p.slice(); pp[j] += h; pm[j] -= h; const a = model(pp), b = model(pm); for (let i = 0; i < a.length; i++) { J[2 * i][j] = (a[i][0] - b[i][0]) / (2 * h); J[2 * i + 1][j] = (a[i][1] - b[i][1]) / (2 * h); } }
    const A = Array.from({ length: n }, () => new Array(n).fill(0)), g = new Array(n).fill(0);
    for (let i = 0; i < r.length; i++) for (let a = 0; a < n; a++) { g[a] += J[i][a] * r[i]; for (let b = 0; b < n; b++) A[a][b] += J[i][a] * J[i][b]; }
    for (let a = 0; a < n; a++) { if (!free[a]) { for (let b = 0; b < n; b++) { A[a][b] = 0; A[b][a] = 0; } A[a][a] = 1; g[a] = 0; } else A[a][a] *= 1 + lam; }
    const dx = lsolve(A, g.map(v => -v)); if (!dx) break;
    const pn = p.map((v, i) => v + dx[i]);
    const mn = model(pn); let e0 = 0, e1 = 0; m.forEach((q, i) => { e0 += (q[0] - obs[i][0]) ** 2 + (q[1] - obs[i][1]) ** 2; }); mn.forEach((q, i) => { e1 += (q[0] - obs[i][0]) ** 2 + (q[1] - obs[i][1]) ** 2; });
    if (e1 < e0) { p = pn; lam = Math.max(1e-9, lam / 3); if (Math.sqrt(dx.reduce((s, v, i) => s + (v * (i < 3 ? 1 : 1000)) ** 2, 0)) < 1e-7) break; } else lam *= 5;
  }
  // covariance of ds from the Jacobian at the solution (sigma^2 (J^T J)^-1)
  const m = model(p), n2 = 2 * m.length, J = Array.from({ length: n2 }, () => new Array(n).fill(0));
  for (let j = 0; j < n; j++) { const h = j < 3 ? 1e-3 * (j === 2 ? 100 : 1) : (j < 5 ? 1e-6 : 1e-4), pp = p.slice(), pm = p.slice(); pp[j] += h; pm[j] -= h; const a = model(pp), b = model(pm); for (let i = 0; i < a.length; i++) { J[2 * i][j] = (a[i][0] - b[i][0]) / (2 * h); J[2 * i + 1][j] = (a[i][1] - b[i][1]) / (2 * h); } }
  const A = Array.from({ length: n }, () => new Array(n).fill(0)); for (let i = 0; i < n2; i++) for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) A[a][b] += J[i][a] * J[i][b];
  for (let a = 0; a < n; a++) if (!free[a]) { for (let b = 0; b < n; b++) { A[a][b] = 0; A[b][a] = 0; } A[a][a] = 1; }
  const inv = linv(A); const sd = inv ? p.map((_, i) => sigmaPx * Math.sqrt(Math.max(0, inv[i][i]))) : null;
  return { p: p, sd: sd };
}
function lsolve(A, b) { const n = b.length, M = A.map((r, i) => r.concat([b[i]])); for (let i = 0; i < n; i++) { let m = i; for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[m][i])) m = r; if (Math.abs(M[m][i]) < 1e-14) return null;[M[i], M[m]] = [M[m], M[i]]; for (let r = 0; r < n; r++) if (r !== i) { const f = M[r][i] / M[i][i]; for (let c = i; c <= n; c++) M[r][c] -= f * M[i][c]; } } return M.map((r, i) => r[n] / r[i]); }
function linv(A) { const n = A.length, M = A.map((r, i) => r.concat(Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)))); for (let i = 0; i < n; i++) { let m = i; for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[m][i])) m = r; if (Math.abs(M[m][i]) < 1e-14) return null;[M[i], M[m]] = [M[m], M[i]]; const d = M[i][i]; for (let c = 0; c < 2 * n; c++) M[i][c] /= d; for (let r = 0; r < n; r++) if (r !== i) { const f = M[r][i]; for (let c = 0; c < 2 * n; c++) M[r][c] -= f * M[i][c]; } } return M.map(r => r.slice(n)); }

function run(P, seed) {
  const r = rng(seed), NP = 48;
  const pTrue = [P.cx, P.cy, P.H, P.tx * DEG, P.ty * DEG, P.ds];
  const pts = features(P.ds, NP), obs = pts.map(X => { const q = project(X, pTrue); return [q[0] + P.sigma * gauss(r), q[1] + P.sigma * gauss(r)]; });
  const pNom = [0, 0, P.Hnom, 0, 0, 0];
  const dsSrc = P.dsSrc || 'fit';
  const p0 = pNom.slice(); if (dsSrc === 'touch') p0[5] = P.ds + 0.03 * gauss(r);
  const fit = solve(obs, features(0, NP), p0, P.sigma, [true, true, true, true, true, dsSrc === 'fit']);
  // the reading: how far inside the rim's inner edge the dot appears (image distance along the radial direction, plate-plane scale)
  const dotW = [RI - P.a, 0, -(PZ + P.ds)];
  const noisy = q => [q[0] + P.sigma * gauss(r), q[1] + P.sigma * gauss(r)];
  const dotObs = noisy(project(dotW, pTrue)), edgeObs = noisy(project([RI, 0, 0], pTrue)), axisObs = project([0, 0, 0], pTrue);
  const ux = edgeObs[0] - axisObs[0], uy = edgeObs[1] - axisObs[1], un = Math.hypot(ux, uy), ex = ux / un, ey = uy / un;
  const Xpx = (edgeObs[0] - dotObs[0]) * ex + (edgeObs[1] - dotObs[1]) * ey;          // px, dot inside the edge
  const par = (p, ds) => { const c = project([RI, 0, -(PZ + ds)], p), e = project([RI, 0, 0], p), a0 = project([0, 0, 0], p); const vx = e[0] - a0[0], vy = e[1] - a0[1], vn = Math.hypot(vx, vy); return ((e[0] - c[0]) * vx / vn + (e[1] - c[1]) * vy / vn); };   // px
  const sc = (H, ds) => F / (H + PZ + ds);
  const naive = Xpx / sc(P.Hnom, 0);                                                    // corner taken to be the rim edge
  const nominal = (Xpx - par(pNom, 0)) / sc(P.Hnom, 0);                                 // parallax predicted for a level camera on the axis
  const fitted = (Xpx - par(fit.p, fit.p[5])) / sc(fit.p[2], fit.p[5]);
  const parTrue = par(pTrue, P.ds) / sc(P.H, P.ds);
  return { fit: fit, a: P.a, naive: naive, nominal: nominal, fitted: fitted, parTrue: parTrue, dsFit: fit.p[5], dsSd: fit.sd ? fit.sd[5] : NaN, pose: fit.p, sd: fit.sd };
}
module.exports = { run, project, backproject, features, solve, F, U0, V0, RI, RO, PORT, PZ, rng, gauss };
if (require.main === module) {
  const base = { cx: 0, cy: 0, H: 300, Hnom: 300, tx: 0, ty: 0, ds: 0, a: 0.20, sigma: 0.15 };
  const show = (label, P) => { let e = [0, 0, 0], par = 0, ds = 0, dsd = 0, N = 60; for (let i = 0; i < N; i++) { const q = run(P, 100 + i); e[0] += (q.naive - q.a) ** 2; e[1] += (q.nominal - q.a) ** 2; e[2] += (q.fitted - q.a) ** 2; par = q.parTrue; ds += (q.dsFit - P.ds) ** 2; dsd = q.dsSd; } console.log(label.padEnd(46), 'parallax', par.toFixed(2).padStart(5), '| rim-edge=corner err', Math.sqrt(e[0] / N).toFixed(2).padStart(5), '| nominal-camera err', Math.sqrt(e[1] / N).toFixed(3).padStart(6), '| fitted err', Math.sqrt(e[2] / N).toFixed(3).padStart(6), '| depth err rms', Math.sqrt(ds / N).toFixed(2), '(sd', dsd.toFixed(2) + ')'); };
  console.log('dot reading error at the station, mm; pixel noise 0.15 px; f = 1500 px; H = camera height over the rim');
  show('centred, level, H 300, seat depth 0', base);
  show('camera 10 mm toward the station', Object.assign({}, base, { cx: 10 }));
  show('camera 25 mm toward the station', Object.assign({}, base, { cx: 25 }));
  show('tilt 2 deg (about y)', Object.assign({}, base, { ty: 2 }));
  show('tilt 2 deg, offset 10 mm, H 320 (nominal 300)', Object.assign({}, base, { cx: 10, ty: 2, H: 320 }));
  show('seat depth +0.5 mm, centred', Object.assign({}, base, { ds: 0.5 }));
  show('seat depth +0.5, tilt 2, offset 10', Object.assign({}, base, { ds: 0.5, ty: 2, cx: 10 }));
  show('H 200 (closer), seat +0.5', Object.assign({}, base, { H: 200, Hnom: 200, ds: 0.5 }));
  show('H 450 (farther), seat +0.5', Object.assign({}, base, { H: 450, Hnom: 450, ds: 0.5 }));
  show('H 150, seat +0.5', Object.assign({}, base, { H: 150, Hnom: 150, ds: 0.5 }));
  show('pixel noise 0.5, seat +0.5', Object.assign({}, base, { ds: 0.5, sigma: 0.5 }));
  show('camera on the station side, x=+40, tilt -8 deg', Object.assign({}, base, { cx: 40, ty: -8 }));
}
