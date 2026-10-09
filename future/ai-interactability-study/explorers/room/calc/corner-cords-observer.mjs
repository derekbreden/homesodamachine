// corner-cords-observer.mjs - room-06's self-calibration again, with the observer made honest (answer to eyes, wave 3).
// The first version (corner-cords-calibration.mjs) fitted 32 numbers to a 3-D position of the dot. A camera does not report
// that: the red dot is a place where the beam meets a surface, so a camera reports where a LINE ends (two numbers per pose).
// Here the same nonlinear fit is run on what each observer could report, and each fit is judged on 100 fresh target poses.
// Observers:  dot3d (the old assumption) | plane (spot on a board at plate height) | corner (spot on plate or wall, whichever
// the beam meets first) | plane+nz (spot + nozzle-tip height, camera B) | plane+n3 (spot + nozzle tip in 3-D) | tags (a marker
// cube on the shell seen by two cameras: dot in 3-D at 0.2 mm plus the beam direction at 0.05 deg).
// All noise values and the pose ranges are [illustrative]; nothing here is measured.
// Run: node explorers/room/calc/corner-cords-observer.mjs [N=40] [sigma=0.1] [seeds=10]
import { world, JOINT_Z, RI, RIM_Z } from './pose.mjs';
import { V, M3, cordGeometry, forwardKin, solveLinear, rng } from './cdpr-core.mjs';
import { lugs, anchors as cage } from './corner-cords-pairing-search.mjs';

const N = +(process.argv[2] || 40), SIG = +(process.argv[3] || 0.1), SEEDS = +(process.argv[4] || 10);
const SIG_NOZZLE = 0.2, SIG_TAG = 0.2, SIG_AIM = 0.05 * Math.PI / 180;
const pairing = [6, 0, 1, 4, 5, 7, 2, 3], nomAnchors = pairing.map(k => cage[k]), dotLocal = [0, 0, -16];
const dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);

// what an observer reports for a gun pose {p (dot), R}: an array of numbers and a noise sigma per number
function observe(kind, pose) {
  const tip = V.add(pose.p, M3.mulV(pose.R, [0, 0, 16])), d = M3.mulV(pose.R, [0, 0, -1]);
  const plate = () => { const t = (JOINT_Z - tip[2]) / d[2]; const s = V.add(tip, V.scl(d, t)); return [s[0], s[1]]; };
  const corner = () => {           // first surface along the beam: plate face (r < RI) or the wall (RI, up to the rim)
    const tp = (JOINT_Z - tip[2]) / d[2], sp = V.add(tip, V.scl(d, tp));
    if (Math.hypot(sp[0], sp[1]) <= RI) return [sp[0], sp[1]];
    const a = d[0] ** 2 + d[1] ** 2, b = 2 * (tip[0] * d[0] + tip[1] * d[1]), c = tip[0] ** 2 + tip[1] ** 2 - RI * RI;
    const tw = (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a), sw = V.add(tip, V.scl(d, tw));
    return [Math.atan2(sw[1], sw[0]) * RI, sw[2]];
  };
  switch (kind) {
    case 'dot3d': return { y: pose.p.slice(), s: [SIG, SIG, SIG] };
    case 'plane': return { y: plate(), s: [SIG, SIG] };
    case 'corner': return { y: corner(), s: [SIG, SIG] };
    case 'plane+nz': return { y: plate().concat([tip[2]]), s: [SIG, SIG, SIG_NOZZLE] };
    case 'plane+n3': return { y: plate().concat(tip), s: [SIG, SIG, SIG_NOZZLE, SIG_NOZZLE, SIG_NOZZLE] };
    case 'tags': return { y: pose.p.concat(d), s: [SIG_TAG, SIG_TAG, SIG_TAG, SIG_AIM, SIG_AIM, SIG_AIM] };
  }
}
const KINDS = ['dot3d', 'plane', 'corner', 'plane+nz', 'plane+n3', 'tags'];

function run(kind, seed) {
  const r = rng(seed);
  const S = { anchor: 2, lug: 0.2, cord: 1 };
  const trueAnch = nomAnchors.map(a => a.map(v => v + r.n() * S.anchor)), trueLugs = lugs.map(l => l.map(v => v + r.n() * S.lug)), trueOff = nomAnchors.map(() => r.n() * S.cord);
  // poses the software may choose: the range of room-06 (+-25 x +-25 x +-15 mm, +-4 deg), but the nozzle tip must stay inside the bore
  // (r < RI - 3) so that the beam lands on the plate or the wall face in front of it (a dot 14 mm into the metal is not a pose)
  const target = () => { for (;;) { const tp = { R: M3.mul(M3.rodrigues([0, 1, 2].map(() => (r.u() * 2 - 1) * 4 * Math.PI / 180)), R0), p: V.add(p0, [(r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 15]) }; const tip = V.add(tp.p, M3.mulV(tp.R, [0, 0, 16])); if (Math.hypot(tip[0], tip[1]) < RI - 3) return tp; } };
  const rig = (cmd, init) => forwardKin(trueAnch, trueLugs, dotLocal, cmd.map((c, i) => c + trueOff[i]), init);
  const train = [];
  for (let k = 0; k < N; k++) {
    const tp = target(), cmd = cordGeometry(nomAnchors, lugs, dotLocal, tp).map(g => g.L), fk = rig(cmd, tp), ob = observe(kind, fk);
    train.push({ cmd, tp, y: ob.y.map((v, i) => v + r.n() * ob.s[i]), s: ob.s });
  }
  const NP = 32, prior = new Array(NP).fill(0).map((_, i) => 1 / (i < 24 ? S.anchor : S.cord));
  const modelPose = (th, t) => forwardKin(nomAnchors.map((a, i) => [a[0] + th[3 * i], a[1] + th[3 * i + 1], a[2] + th[3 * i + 2]]), lugs, dotLocal, t.cmd.map((c, i) => c + th[24 + i]), t.tp, 20);
  let theta = new Array(NP).fill(0), lam = 1e-3, ok = true;
  const cost = th => { let c = 0; train.forEach(t => { const y = observe(kind, modelPose(th, t)).y; y.forEach((v, i) => { c += ((t.y[i] - v) / t.s[i]) ** 2; }); }); return c + th.reduce((s, v, i) => s + (v * prior[i]) ** 2, 0); };
  let c0 = cost(theta);
  for (let iter = 0; iter < 14; iter++) {
    const res = [], base = train.map(t => observe(kind, modelPose(theta, t)).y);
    train.forEach((t, k) => base[k].forEach((v, i) => res.push((t.y[i] - v) / t.s[i])));
    const cols = [];
    for (let j = 0; j < NP; j++) { const th2 = theta.slice(); th2[j] += 1e-3; const col = []; train.forEach((t, k) => { const y2 = observe(kind, modelPose(th2, t)).y; y2.forEach((v, i) => col.push((v - base[k][i]) / 1e-3 / t.s[i])); }); cols.push(col); }
    const JTJ = Array.from({ length: NP }, (_, i) => Array.from({ length: NP }, (_, j) => { let s = 0; for (let k = 0; k < res.length; k++) s += cols[i][k] * cols[j][k]; return s; }));
    const JTr = Array.from({ length: NP }, (_, i) => { let s = 0; for (let k = 0; k < res.length; k++) s += cols[i][k] * res[k]; return s - prior[i] ** 2 * theta[i]; });
    let improved = false;
    for (let tries = 0; tries < 8 && !improved; tries++) {
      const A = JTJ.map((row, i) => row.map((v, j) => v + (i === j ? prior[i] ** 2 + lam * (JTJ[i][i] + 1) : 0)));
      const dx = solveLinear(A, JTr); if (!dx) { lam *= 10; continue; }
      const th2 = theta.map((v, i) => v + dx[i]), c1 = cost(th2);
      if (c1 < c0) { theta = th2; c0 = c1; lam = Math.max(lam / 5, 1e-6); improved = true; } else lam *= 8;
    }
    if (!improved) break;
  }
  // judge on fresh targets: true dot vs commanded (3-D, and split into radial / tangent / vertical), beam direction error
  const est = { anch: nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]), off: theta.slice(24) };
  let s3 = 0, sr = 0, st = 0, sz = 0, sa = 0, T = 100;
  for (let k = 0; k < T; k++) {
    const tp = target(), cmd = cordGeometry(est.anch, lugs, dotLocal, tp).map((g, i) => g.L - est.off[i]), fk = rig(cmd, tp);
    const e = V.sub(fk.p, tp.p); s3 += V.dot(e, e); sr += e[0] ** 2; st += e[1] ** 2; sz += e[2] ** 2;
    const d1 = M3.mulV(fk.R, [0, 0, -1]), d0 = M3.mulV(tp.R, [0, 0, -1]); sa += Math.acos(Math.min(1, V.dot(d1, d0))) ** 2;
  }
  return { rms3: Math.sqrt(s3 / T), r: Math.sqrt(sr / T), t: Math.sqrt(st / T), z: Math.sqrt(sz / T), aim: Math.sqrt(sa / T) * 180 / Math.PI, cost: c0 };
}

console.log(`N = ${N} poses, in-surface / dot noise ${SIG} mm, nozzle ${SIG_NOZZLE} mm, tags ${SIG_TAG} mm + ${(SIG_AIM * 180 / Math.PI).toFixed(2)} deg; anchors 2 mm, cord zeros 1 mm, lugs 0.2 mm; ${SEEDS} seeds; rms over 100 fresh targets, mean over seeds (median in brackets)`);
console.log('observer     3-D rms   radial  tangent vertical   aim (deg)   runs with 3-D rms > 1 mm (not converged)');
for (const kind of (process.env.KINDS ? process.env.KINDS.split(',') : KINDS)) {
  const rs = []; for (let s = 1; s <= SEEDS; s++) rs.push(run(kind, s));
  if (process.env.DEBUG) console.log(JSON.stringify(rs));
  const good = rs.filter(x => x.rms3 < 1), mean = k => good.reduce((a, x) => a + x[k], 0) / Math.max(1, good.length), med = k => { const v = good.map(x => x[k]).sort((a, b) => a - b); return v[Math.floor(v.length / 2)]; };
  console.log(`${kind.padEnd(11)}  ${mean('rms3').toFixed(3)} (${med('rms3').toFixed(3)})  ${mean('r').toFixed(3)}  ${mean('t').toFixed(3)}  ${mean('z').toFixed(3)}   ${mean('aim').toFixed(3)}   ${rs.length - good.length} of ${rs.length}`);
}
