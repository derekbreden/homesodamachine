// cords-spot-grid.mjs (eyes, wave 2) - builds the table behind scenes/eyes-13-cords-see-a-spot (branch of room-06).
// Linearised expected error of the dot after self-calibration, by what the observer sees. Same model as room-06's
// calc/corner-cords-calibration.mjs (24 anchor offsets + 8 cord zeros, ridge prior = the assumed sigmas 2 / 1 mm);
// the observation type is what changes. Mean square over SEEDS random draws of the true errors and 120 fresh targets.
// Output: explorers/eyes/calc/cords-spot-grid.json  { kinds:[..], N:[..], sigma:[..], data[kind][N][sigma] = {x,y,z,aim} }
// Run: node explorers/eyes/calc/cords-spot-grid.mjs [seeds]
import fs from 'node:fs';
import { world } from '../../room/calc/pose.mjs';
import { V, M3, cordGeometry, forwardKin, solveLinear, rng } from '../../room/calc/cdpr-core.mjs';
import { lugs, anchors as cage } from '../../room/calc/corner-cords-pairing-search.mjs';

const SEEDS = +(process.argv[2] || 4);
const KINDS = ['dot3d', 'stereo-dot', 'plane', 'steps', 'corner', 'plane+nz', 'plane+n3'];
const NS = [10, 20, 40, 80], SIGS = [0.05, 0.10, 0.20, 0.30], NZ_SIGMA = 0.2;
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
const nomAnchors = pairing.map(k => cage[k]);
const dotLocal = [0, 0, -16], dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);
const RW = 61.85, ZP = p0[2], ZRIM = ZP + 6.35;
const S = { anchor: 2.0, cord: 1.0 }, NP = 32;
const prior = new Array(NP).fill(0).map((_, i) => 1 / (i < 24 ? S.anchor : S.cord));
function beamRay(pose) { return { n: V.add(pose.p, M3.mulV(pose.R, [0, 0, 16])), d: M3.mulV(pose.R, [0, 0, -1]) }; }
function hitPlate(r, z, bounded) { if (r.d[2] >= -1e-6) return null; const t = (z - r.n[2]) / r.d[2]; if (t <= 0) return null; const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || Math.hypot(h[0], h[1]) <= RW + 1e-9) ? { t, h, s: 'plate' } : null; }
function hitWall(r, bounded) {
  const a = r.d[0] ** 2 + r.d[1] ** 2, b = 2 * (r.n[0] * r.d[0] + r.n[1] * r.d[1]), c = r.n[0] ** 2 + r.n[1] ** 2 - RW * RW;
  const disc = b * b - 4 * a * c; if (disc < 0 || a < 1e-12) return null;
  const t = (-b + Math.sqrt(disc)) / (2 * a); if (t <= 0) return null;
  const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || (h[2] >= ZP - 1e-9 && h[2] <= ZRIM + 6)) ? { t, h, s: 'wall' } : null;
}
// returns {spot:[...], aux:[...]}; spot noise = sigma (per axis, x5 on the first axis for 'stereo-dot'), aux noise = NZ_SIGMA
function obs(pose, surf, kind) {
  if (surf === 'x') return { spot: pose.p.slice(), aux: [] };
  const r = beamRay(pose);
  if (surf === 'wall') { const h = hitWall(r, false); return h ? { spot: [Math.atan2(h.h[1], h.h[0]) * RW, h.h[2]], aux: [] } : null; }
  const z = surf === 'plate' ? ZP : ZP + surf; const h = hitPlate(r, z, false); if (!h) return null;
  const aux = kind === 'plane+nz' ? [r.n[2]] : kind === 'plane+n3' ? [r.n[0], r.n[1], r.n[2]] : [];
  return { spot: [h.h[0], h.h[1]], aux };
}
function firstSurface(pose) { const r = beamRay(pose), a = hitPlate(r, ZP, true), b = hitWall(r, true); const pk = a && b ? (a.t < b.t ? a : b) : (a || b); return pk ? pk.s : null; }

function build(seed, kind) {
  const rnd = rng(seed);
  const tp = () => ({ R: M3.mul(M3.rodrigues([0, 1, 2].map(() => (rnd.u() * 2 - 1) * 4 * Math.PI / 180)), R0), p: V.add(p0, [(rnd.u() * 2 - 1) * 25, (rnd.u() * 2 - 1) * 25, (rnd.u() * 2 - 1) * 15]) });
  const thetaT = new Array(NP).fill(0).map((_, i) => rnd.n() * (i < 24 ? S.anchor : S.cord));
  const model = (theta, cmd) => {
    const anch = nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]);
    return forwardKin(anch, lugs, dotLocal, cmd.map((c, i) => c + theta[24 + i]), { p: p0, R: R0 });
  };
  const zero = new Array(NP).fill(0), cmdOf = pose => cordGeometry(nomAnchors, lugs, dotLocal, pose).map(g => g.L);
  const rows = []; let guard = 0; const maxN = Math.max(...NS);
  while (rows.length < maxN && guard++ < 8000) {
    const t = tp(), cmd = cmdOf(t); let surf = 'x';
    if (kind === 'plane' || kind === 'plane+nz' || kind === 'plane+n3') surf = 'plate';
    else if (kind === 'steps') surf = [0, 6, 12][rows.length % 3];
    else if (kind === 'corner') { const f = firstSurface(model(thetaT, cmd)); if (!f) continue; surf = f; }
    const a = obs(model(thetaT, cmd), surf, kind), b = obs(model(zero, cmd), surf, kind);
    if (!a || !b) continue;
    rows.push({ cmd, surf });
  }
  // per-row Jacobians at the truth, split into spot and aux parts
  const spotRows = [], auxRows = [], rowIndex = [];   // rowIndex[k] = how many spot/aux rows exist after pose k
  for (const rw of rows) {
    const base = obs(model(thetaT, rw.cmd), rw.surf, kind);
    const cols = [];
    for (let j = 0; j < NP; j++) { const th = thetaT.slice(); th[j] += 1e-3; const ob = obs(model(th, rw.cmd), rw.surf, kind); cols.push({ s: base.spot.map((v, a) => (ob.spot[a] - v) / 1e-3), x: base.aux.map((v, a) => (ob.aux[a] - v) / 1e-3) }); }
    for (let a = 0; a < base.spot.length; a++) spotRows.push({ r: cols.map(c => c.s[a]), first: kind === 'stereo-dot' && a === 0 });
    for (let a = 0; a < base.aux.length; a++) auxRows.push(cols.map(c => c.x[a]));
    rowIndex.push([spotRows.length, auxRows.length]);
  }
  // fresh targets
  const Gs = [], Hs = [];
  for (let f = 0; f < 100; f++) {
    const t = tp(), cmd = cmdOf(t), base = model(thetaT, cmd), dirB = M3.mulV(base.R, [0, 0, -1]);
    const G = [[], [], []], H = [[], [], []];
    for (let j = 0; j < NP; j++) { const th = thetaT.slice(); th[j] += 1e-3; const m = model(th, cmd), d2 = M3.mulV(m.R, [0, 0, -1]); for (let a = 0; a < 3; a++) { G[a].push((m.p[a] - base.p[a]) / 1e-3); H[a].push((d2[a] - dirB[a]) / 1e-3); } }
    Gs.push(G); Hs.push(H);
  }
  return { spotRows, auxRows, rowIndex, Gs, Hs, used: rows.length };
}
function evalAt(b, nPoses, sigma, kind) {
  if (nPoses > b.rowIndex.length) return null;
  const [ns, na] = b.rowIndex[nPoses - 1];
  const A = Array.from({ length: NP }, (_, i) => Array.from({ length: NP }, (_, j) => (i === j ? prior[i] ** 2 + 1e-12 : 0)));
  for (let k = 0; k < ns; k++) { const sr = b.spotRows[k], w = 1 / ((sr.first ? 5 * sigma : sigma) ** 2); for (let i = 0; i < NP; i++) { const ri = sr.r[i] * w; if (ri === 0) continue; for (let j = 0; j < NP; j++) A[i][j] += ri * sr.r[j]; } }
  const wa = 1 / NZ_SIGMA ** 2;
  for (let k = 0; k < na; k++) { const r = b.auxRows[k]; for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) A[i][j] += r[i] * r[j] * wa; }
  const Sig = Array.from({ length: NP }, () => new Array(NP).fill(0));
  for (let k = 0; k < NP; k++) { const e = new Array(NP).fill(0); e[k] = 1; const col = solveLinear(A, e); for (let i = 0; i < NP; i++) Sig[i][k] = col[i]; }
  const quad = row => { let s = 0; for (let i = 0; i < NP; i++) for (let j = 0; j < NP; j++) s += row[i] * Sig[i][j] * row[j]; return s; };
  let sx = 0, sy = 0, sz = 0, sa = 0;
  for (let f = 0; f < b.Gs.length; f++) { sx += quad(b.Gs[f][0]); sy += quad(b.Gs[f][1]); sz += quad(b.Gs[f][2]); sa += quad(b.Hs[f][0]) + quad(b.Hs[f][1]) + quad(b.Hs[f][2]); }
  const n = b.Gs.length; return { x: sx / n, y: sy / n, z: sz / n, aim: sa / n };
}
const out = { note: 'linearised expected 1-sigma error of the dot after self-calibration; x radial, y tangent, z vertical (mm); aim in degrees; illustrative sigmas as room-06 (anchors 2 mm, cord zeros 1 mm); spot noise per surface axis; nozzle-height / nozzle-3D aux noise 0.2 mm', kinds: KINDS, N: NS, sigma: SIGS, seeds: SEEDS, data: {} };
for (const kind of KINDS) {
  out.data[kind] = {};
  const builds = []; for (let s = 1; s <= SEEDS; s++) builds.push(build(s, kind));
  for (const n of NS) {
    out.data[kind][n] = {};
    for (const sg of SIGS) {
      let ax = 0, ay = 0, az = 0, aa = 0, c = 0;
      for (const b of builds) { const r = evalAt(b, n, sg, kind); if (!r) continue; ax += r.x; ay += r.y; az += r.z; aa += r.aim; c++; }
      out.data[kind][n][sg] = { x: +Math.sqrt(ax / c).toFixed(4), y: +Math.sqrt(ay / c).toFixed(4), z: +Math.sqrt(az / c).toFixed(4), aim: +(Math.sqrt(aa / c) * 180 / Math.PI).toFixed(4) };
    }
  }
  console.log(kind, JSON.stringify(out.data[kind][40][0.1]));
}
fs.writeFileSync(new URL('./cords-spot-grid.json', import.meta.url), JSON.stringify(out));
console.log('wrote cords-spot-grid.json');
