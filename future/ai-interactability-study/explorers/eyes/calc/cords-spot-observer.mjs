// cords-spot-observer.mjs (eyes, wave 2) - stress on room-06's self-calibration: what does the observer actually see?
// room-06's fit (explorers/room/calc/corner-cords-calibration.mjs) takes as its measurement the DOT's 3-D position in the cage
// frame with 0.10 mm noise per axis. A red 0.3 mW dot is not a point in air: it is a SPOT where the beam meets a surface. A
// camera reports where that spot lies ON the surface (two numbers), so the measurement is a beam-surface intersection, and the
// surface has to be somewhere known. This script repeats room-06's fit with the observation replaced by spots on
//   plane    : one horizontal board (the plate level)
//   corner   : the tube's own corner (plate and wall, whichever the beam meets first)
//   steps    : the board at three known heights (a shelf under it, room-01 style)
//   dot3d    : room-06's assumption (control)
// and scores each by the same metric (3-D dot error over 200 fresh targets, calibrated model), plus the number of the 32
// parameters left poorly determined. Illustrative errors as in room-06. Imports room's helpers read-only.
// Run: node explorers/eyes/calc/cords-spot-observer.mjs [seed] [N] [sigma]
import { world } from '../../room/calc/pose.mjs';
import { V, M3, cordGeometry, forwardKin, solveLinear, rng } from '../../room/calc/cdpr-core.mjs';
import { lugs, anchors as cage } from '../../room/calc/corner-cords-pairing-search.mjs';

const seed = +(process.argv[2] || 1), N = +(process.argv[3] || 40), SIGMA = +(process.argv[4] || 0.10);
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
const nomAnchors = pairing.map(k => cage[k]);
const dotLocal = [0, 0, -16], dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);
const RW = 61.85, ZP = p0[2], ZRIM = ZP + 6.35;
const S = { anchor: 2.0, lug: 0.2, cord: 1.0, meas: SIGMA };

// ---- surfaces: first hit of the beam (nozzle -> dot -> beyond)
function beamRay(pose) { const n = V.add(pose.p, M3.mulV(pose.R, [0, 0, 16])), d = M3.mulV(pose.R, [0, 0, -1]); return { n, d }; }
function hitPlate(r, z, bounded) { if (r.d[2] >= -1e-6) return null; const t = (z - r.n[2]) / r.d[2]; if (t <= 0) return null; const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || Math.hypot(h[0], h[1]) <= RW + 1e-9) ? { t, h, s: 'plate' } : null; }
function hitWall(r, bounded) {
  const a = r.d[0] ** 2 + r.d[1] ** 2, b = 2 * (r.n[0] * r.d[0] + r.n[1] * r.d[1]), c = r.n[0] ** 2 + r.n[1] ** 2 - RW * RW;
  const disc = b * b - 4 * a * c; if (disc < 0 || a < 1e-12) return null;
  const t = (-b + Math.sqrt(disc)) / (2 * a); if (t <= 0) return null;
  const h = V.add(r.n, V.scl(r.d, t)); return (!bounded || (h[2] >= ZP - 1e-9 && h[2] <= ZRIM + 6)) ? { t, h, s: 'wall' } : null;
}
// observation of a pose on target `kind`; `surf` (from the TRUE rig) says which surface the camera saw, the model must use the same
function observe(kind, pose, surf) {
  if (kind === 'dot3d') return { v: pose.p.slice(), surf: 'x' };
  const r = beamRay(pose);
  if (kind === 'plane') { const h = hitPlate(r, ZP, false); return h ? { v: [h.h[0], h.h[1]], surf: 'plate' } : null; }
  if (kind === 'steps') { const z = ZP + (surf || 0); const h = hitPlate(r, z, false); return h ? { v: [h.h[0], h.h[1]], surf: z - ZP } : null; }
  if (kind === 'corner') {
    if (surf === 'plate') { const h = hitPlate(r, ZP, false); return h ? { v: [h.h[0], h.h[1]], surf } : null; }
    if (surf === 'wall') { const h = hitWall(r); return h ? { v: [h.h[0], h.h[1], h.h[2]].slice(0, 3).map((x, i) => x), surf } : null; }
    const a = hitPlate(r, ZP, true), b = hitWall(r, true), pick = a && b ? (a.t < b.t ? a : b) : (a || b);
    if (!pick) return null;
    return pick.s === 'plate' ? { v: [pick.h[0], pick.h[1]], surf: 'plate' } : { v: [Math.atan2(pick.h[1], pick.h[0]) * RW, pick.h[2]], surf: 'wall' };   // on the wall: arc length and height
  }
  return null;
}
function obsDim(kind, surf) { return kind === 'dot3d' ? 3 : 2; }
function wallObs(pose) { const r = beamRay(pose), h = hitWall(r, false); return h ? { v: [Math.atan2(h.h[1], h.h[0]) * RW, h.h[2]], surf: 'wall' } : null; }
function observeAs(kind, pose, surf) {
  if (kind === 'corner' && surf === 'wall') return wallObs(pose);
  return observe(kind, pose, surf);
}

const rnd = rng(seed);
function targetPose(r) {
  const shift = [(r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 15];
  const dw = [0, 1, 2].map(() => (r.u() * 2 - 1) * 4 * Math.PI / 180);
  return { R: M3.mul(M3.rodrigues(dw), R0), p: V.add(p0, shift) };
}
const trueAnchors = nomAnchors.map(a => a.map(v => v + rnd.n() * S.anchor));
const trueLugs = lugs.map(l => l.map(v => v + rnd.n() * S.lug));
const trueOffsets = nomAnchors.map(() => rnd.n() * S.cord);
const cmdLengths = (anch, lg, pose) => cordGeometry(anch, lg, dotLocal, pose).map(g => g.L);
function rigPose(cmd) { const Ls = cmd.map((c, i) => c + trueOffsets[i]); return forwardKin(trueAnchors, trueLugs, dotLocal, Ls, { p: p0, R: R0 }); }
function modelPose(theta, cmd) {
  const anch = nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]);
  return forwardKin(anch, lugs, dotLocal, cmd.map((c, i) => c + theta[24 + i]), { p: p0, R: R0 });
}
const NP = 32;
const prior = new Array(NP).fill(0).map((_, i) => 1 / (i < 24 ? S.anchor : S.cord));

function runKind(kind, nPoses) {
  const rr = rng(seed + 100);
  const train = [];
  let tries = 0;
  while (train.length < nPoses && tries++ < 5000) {
    const tp = targetPose(rr), cmd = cmdLengths(nomAnchors, lugs, tp), rp = rigPose(cmd);
    let surf = null;
    if (kind === 'steps') surf = [0, 6, 12][train.length % 3];
    if (kind === 'corner') { const r = beamRay(rp), a = hitPlate(r, ZP, true), b = hitWall(r, true); const pk = a && b ? (a.t < b.t ? a : b) : (a || b); if (!pk) continue; surf = pk.s; }
    const ob = observeAs(kind, rp, surf); if (!ob) continue;
    const nom = observeAs(kind, modelPose(new Array(NP).fill(0), cmd), surf); if (!nom) continue;   // a pose the nominal model also sees landing on that surface
    train.push({ cmd, surf, meas: ob.v.map(x => x + rr.n() * S.meas) });
  }
  let theta = new Array(NP).fill(0), lastCond = null, lastRms = null;
  for (let iter = 0; iter < 30; iter++) {
    const rowsRes = [], cols = Array.from({ length: NP }, () => []);
    const base = train.map(t => { const ob = observeAs(kind, modelPose(theta, t.cmd), t.surf); return ob ? ob.v : null; });
    if (base.some(b => !b)) break;
    train.forEach((t, k) => t.meas.forEach((m, a) => rowsRes.push((m - base[k][a]) / S.meas)));
    for (let j = 0; j < NP; j++) {
      const th2 = theta.slice(); th2[j] += 1e-3;
      train.forEach((t, k) => { const ob = observeAs(kind, modelPose(th2, t.cmd), t.surf); for (let a = 0; a < base[k].length; a++) cols[j].push(((ob ? ob.v[a] : base[k][a]) - base[k][a]) / 1e-3 / S.meas); });
    }
    const JTJ0 = Array.from({ length: NP }, (_, i) => Array.from({ length: NP }, (_, j) => { let s = 0; for (let k = 0; k < rowsRes.length; k++) s += cols[i][k] * cols[j][k]; return s; }));
    const JTJ = JTJ0.map((r, i) => r.map((v, j) => v + (i === j ? prior[i] ** 2 + 1e-9 : 0)));
    const JTr = Array.from({ length: NP }, (_, i) => { let s = 0; for (let k = 0; k < rowsRes.length; k++) s += cols[i][k] * rowsRes[k]; return s - prior[i] ** 2 * theta[i]; });
    const dx = solveLinear(JTJ, JTr); if (!dx) break;
    theta = theta.map((v, i) => v + dx[i]); lastCond = JTJ0; lastRms = Math.sqrt(rowsRes.reduce((q, v) => q + v * v, 0) / rowsRes.length);
    if (Math.hypot(...dx) < 1e-7) break;
  }
  // how many parameter directions does the data pin down better than the prior alone? (eigenvalues of J^T J relative to prior^2)
  let pinned = 0, total = NP;
  if (lastCond) {
    // whiten by the prior: A = P^-1 JTJ P^-1 ; eigenvalues via power/Jacobi is heavy; count by diagonal dominance proxy instead
    const A = lastCond.map((r, i) => r.map((v, j) => v / (prior[i] * prior[j])));
    // Jacobi eigenvalue sweep (small n)
    const M = A.map(r => r.slice());
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0; for (let i = 0; i < NP; i++) for (let j = i + 1; j < NP; j++) off += M[i][j] ** 2;
      if (off < 1e-9) break;
      for (let p = 0; p < NP - 1; p++) for (let q = p + 1; q < NP; q++) {
        if (Math.abs(M[p][q]) < 1e-12) continue;
        const th = (M[q][q] - M[p][p]) / (2 * M[p][q]), t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < NP; k++) { const a = M[k][p], b = M[k][q]; M[k][p] = c * a - s * b; M[k][q] = s * a + c * b; }
        for (let k = 0; k < NP; k++) { const a = M[p][k], b = M[q][k]; M[p][k] = c * a - s * b; M[q][k] = s * a + c * b; }
      }
    }
    const ev = M.map((r, i) => r[i]).sort((a, b) => a - b);
    pinned = ev.filter(v => v > 1).length;   // directions where data information exceeds the prior information
  }
  // test: fresh targets, calibrated model, 3-D dot error
  const T = 200; const e = [];
  const ikCmd = pose => { const anch = nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]); return cordGeometry(anch, lugs, dotLocal, pose).map((g, i) => g.L - theta[24 + i]); };
  const rt = rng(seed + 999);
  for (let k = 0; k < T; k++) { const tp = targetPose(rt); const a = rigPose(ikCmd(tp)); e.push(V.len(V.sub(a.p, tp.p))); }
  const s = e.slice().sort((x, y) => x - y);
  return { rms: Math.sqrt(e.reduce((q, v) => q + v * v, 0) / e.length), p95: s[Math.floor(0.95 * s.length)], max: s[s.length - 1], pinned, wrms: lastRms, used: train.length, nWall: train.filter(t => t.surf === 'wall').length };
}

console.log(`seed ${seed}, ${N} calibration poses, spot noise ${SIGMA} mm per in-surface axis; anchors sigma ${S.anchor}, cord zero sigma ${S.cord}, lugs sigma ${S.lug} mm (illustrative)`);
for (const kind of ['dot3d', 'plane', 'steps', 'corner']) {
  for (const n of [N]) {
    const r = runKind(kind, n);
    console.log(`${kind.padEnd(7)} n=${String(r.used).padStart(3)}  fresh-target dot error rms ${r.rms.toFixed(3)} mm  95% ${r.p95.toFixed(3)}  max ${r.max.toFixed(3)}   directions pinned by data ${r.pinned}/32  residual rms ${r.wrms ? r.wrms.toFixed(2) : '-'} sigma${kind === 'corner' ? '   (wall spots ' + r.nWall + ')' : ''}`);
  }
}
