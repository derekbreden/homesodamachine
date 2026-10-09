// cords-spot-cov.mjs (eyes, wave 2) - deterministic version of cords-spot-observer.mjs: linearised expected error.
// Same setup as room-06's self-calibration (24 anchor offsets, 8 cord-zero offsets, ridge prior = the assumed sigmas).
// For each observation type it builds the data Jacobian J at the true parameters over the calibration poses, forms
// Sigma = (J^T J / s^2 + P^2)^-1, then the expected error of the dot (radial x, tangent y, vertical z at the station) and of
// the beam direction over fresh target poses:  cov = G Sigma G^T, G = d(dot)/d(theta).  No optimiser, no local minima.
// Observation types: dot3d (room-06's assumption: a 3-D dot position), plane (spot on one board at plate height),
//   steps (board at 0, 6, 12 mm above plate height), corner (spot on plate or wall, whichever the beam meets first, camera knows which),
//   stereo-dot (dot3d but with depth axis 5x noisier: two cameras at a narrow angle).
// Run: node explorers/eyes/calc/cords-spot-cov.mjs [N] [sigma] [seedCount]
import { world } from '../../room/calc/pose.mjs';
import { V, M3, cordGeometry, forwardKin, solveLinear, rng } from '../../room/calc/cdpr-core.mjs';
import { lugs, anchors as cage } from '../../room/calc/corner-cords-pairing-search.mjs';

const N = +(process.argv[2] || 40), SIGMA = +(process.argv[3] || 0.10), SEEDS = +(process.argv[4] || 8);
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
const nomAnchors = pairing.map(k => cage[k]);
const dotLocal = [0, 0, -16], dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);
const RW = 61.85, ZP = p0[2], ZRIM = ZP + 6.35;
const S = { anchor: 2.0, cord: 1.0 };
const NP = 32;
const prior = new Array(NP).fill(0).map((_, i) => 1 / (i < 24 ? S.anchor : S.cord));

function beamRay(pose) { return { n: V.add(pose.p, M3.mulV(pose.R, [0, 0, 16])), d: M3.mulV(pose.R, [0, 0, -1]) }; }
function hitPlate(r, z, bounded) { if (r.d[2] >= -1e-6) return null; const t = (z - r.n[2]) / r.d[2]; if (t <= 0) return null; const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || Math.hypot(h[0], h[1]) <= RW + 1e-9) ? { t, h, s: 'plate' } : null; }
function hitWall(r, bounded) {
  const a = r.d[0] ** 2 + r.d[1] ** 2, b = 2 * (r.n[0] * r.d[0] + r.n[1] * r.d[1]), c = r.n[0] ** 2 + r.n[1] ** 2 - RW * RW;
  const disc = b * b - 4 * a * c; if (disc < 0 || a < 1e-12) return null;
  const t = (-b + Math.sqrt(disc)) / (2 * a); if (t <= 0) return null;
  const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || (h[2] >= ZP - 1e-9 && h[2] <= ZRIM + 6)) ? { t, h, s: 'wall' } : null;
}
// observation vector for a pose on a named surface: 'x' dot, 'plate', number (board height above plate), 'wall'
function obs(pose, surf) {
  if (surf === 'x') return pose.p.slice();
  if (surf === 'plate+nz') { const r = beamRay(pose), h = hitPlate(r, ZP, false); return h ? [h.h[0], h.h[1], r.n[2]] : null; }   // spot on the board + height of the nozzle tip (side camera)
  if (surf === 'plate+n3') { const r = beamRay(pose), h = hitPlate(r, ZP, false); return h ? [h.h[0], h.h[1], r.n[0], r.n[1], r.n[2]] : null; }   // spot + 3-D nozzle tip (two cameras)
  const r = beamRay(pose);
  if (surf === 'wall') { const h = hitWall(r, false); return h ? [Math.atan2(h.h[1], h.h[0]) * RW, h.h[2]] : null; }
  const z = surf === 'plate' ? ZP : ZP + surf; const h = hitPlate(r, z, false); return h ? [h.h[0], h.h[1]] : null;
}
function firstSurface(pose) { const r = beamRay(pose), a = hitPlate(r, ZP, true), b = hitWall(r, true); const pk = a && b ? (a.t < b.t ? a : b) : (a || b); return pk ? pk.s : null; }
function noiseVec(kind, dim) { return new Array(dim).fill(SIGMA).map((s, i) => kind === 'stereo-dot' && i === 0 ? SIGMA * 5 : (kind === 'plane+nz' && i === 2 ? 0.2 : (kind === 'plane+n3' && i >= 2 ? 0.2 : s))); }

function analyse(seed, kind, nPoses, opts = {}) {
  const rnd = rng(seed);
  const tp = () => ({ R: M3.mul(M3.rodrigues([0, 1, 2].map(() => (rnd.u() * 2 - 1) * 4 * Math.PI / 180)), R0), p: V.add(p0, [(rnd.u() * 2 - 1) * 25, (rnd.u() * 2 - 1) * 25, (rnd.u() * 2 - 1) * 15]) });
  const thetaT = new Array(NP).fill(0).map((_, i) => rnd.n() * (i < 24 ? S.anchor : S.cord));
  const model = (theta, cmd) => {
    const anch = nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]);
    return forwardKin(anch, lugs, dotLocal, cmd.map((c, i) => c + theta[24 + i]), { p: p0, R: R0 });
  };
  const zero = new Array(NP).fill(0);
  const cmdOf = pose => cordGeometry(nomAnchors, lugs, dotLocal, pose).map(g => g.L);
  // calibration poses
  const rows = [];   // each: {cmd, surf}
  let guard = 0;
  while (rows.length < nPoses && guard++ < 5000) {
    const t = tp(), cmd = cmdOf(t);
    let surf = 'x';
    if (kind === 'plane') surf = 'plate';
    else if (kind === 'plane+nz') surf = 'plate+nz';
    else if (kind === 'plane+n3') surf = 'plate+n3';
    else if (kind === 'steps') surf = [0, 6, 12][rows.length % 3];
    else if (kind === 'corner') { const f = firstSurface(model(thetaT, cmd)); if (!f) continue; surf = f; }
    const a = obs(model(thetaT, cmd), surf), b = obs(model(zero, cmd), surf);
    if (!a || !b) continue;
    rows.push({ cmd, surf });
  }
  // data Jacobian at the truth
  const Jrows = [], sig = [];
  for (const rw of rows) {
    const base = obs(model(thetaT, rw.cmd), rw.surf); const dim = base.length;
    const cols = [];
    for (let j = 0; j < NP; j++) { const th = thetaT.slice(); th[j] += 1e-3; const ob = obs(model(th, rw.cmd), rw.surf); cols.push(base.map((v, a) => (ob[a] - v) / 1e-3)); }
    const nz = noiseVec(kind, dim);
    for (let a = 0; a < dim; a++) { Jrows.push(cols.map(c => c[a] / nz[a])); }
  }
  const JTJ = Array.from({ length: NP }, (_, i) => Array.from({ length: NP }, (_, j) => { let s = 0; for (const r of Jrows) s += r[i] * r[j]; return s + (i === j ? prior[i] ** 2 : 0) + (i === j ? 1e-12 : 0); }));
  // invert JTJ (Sigma)
  const Sigma = Array.from({ length: NP }, () => new Array(NP).fill(0));
  for (let k = 0; k < NP; k++) { const e = new Array(NP).fill(0); e[k] = 1; const col = solveLinear(JTJ, e); for (let i = 0; i < NP; i++) Sigma[i][k] = col[i]; }
  // fresh targets: G = d(dot)/d(theta) and d(beam dir)/d(theta)
  let sx = 0, sy = 0, sz = 0, sa = 0, cnt = 0;
  for (let f = 0; f < 120; f++) {
    const t = tp(), cmd = cmdOf(t), base = model(thetaT, cmd), dirB = M3.mulV(base.R, [0, 0, -1]);
    const G = [[], [], []], H = [[], [], []];
    for (let j = 0; j < NP; j++) { const th = thetaT.slice(); th[j] += 1e-3; const m = model(th, cmd), d2 = M3.mulV(m.R, [0, 0, -1]); for (let a = 0; a < 3; a++) { G[a].push((m.p[a] - base.p[a]) / 1e-3); H[a].push((d2[a] - dirB[a]) / 1e-3); } }
    const quad = (A) => A.map(row => { let s = 0; for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) s += row[i] * Sigma[i][j] * row[j]; return s; });
    const q = quad(G), h = quad(H);
    sx += q[0]; sy += q[1]; sz += q[2]; sa += h[0] + h[1] + h[2]; cnt++;
  }
  return { rx: Math.sqrt(sx / cnt), ry: Math.sqrt(sy / cnt), rz: Math.sqrt(sz / cnt), aimDeg: Math.sqrt(sa / cnt) * 180 / Math.PI, used: rows.length, nWall: rows.filter(r => r.surf === 'wall').length };
}

console.log(`expected 1-sigma error of the dot after calibration (linearised), N=${N} poses, spot noise ${SIGMA} mm, mean over ${SEEDS} seeds; x radial, y tangent, z vertical at the station`);
for (const kind of ['dot3d', 'stereo-dot', 'plane', 'steps', 'corner', 'plane+nz', 'plane+n3']) {
  const acc = { rx: 0, ry: 0, rz: 0, aim: 0, wall: 0 };
  for (let s = 1; s <= SEEDS; s++) { const r = analyse(s, kind, N); acc.rx += r.rx ** 2; acc.ry += r.ry ** 2; acc.rz += r.rz ** 2; acc.aim += r.aimDeg ** 2; acc.wall += r.nWall; }
  const f = v => Math.sqrt(v / SEEDS);
  console.log(`${kind.padEnd(11)} radial ${f(acc.rx).toFixed(3)}  tangent ${f(acc.ry).toFixed(3)}  vertical ${f(acc.rz).toFixed(3)} mm   aim ${f(acc.aim).toFixed(3)} deg${kind === 'corner' ? '   (avg wall spots ' + (acc.wall / SEEDS).toFixed(1) + ')' : ''}`);
}
