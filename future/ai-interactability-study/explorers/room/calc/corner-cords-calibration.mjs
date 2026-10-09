// Does self-calibration rescue sloppy anchors?  The classic objection to cord-suspended positioning is that anchor and cord-length
// errors of a millimetre or two wreck accuracy.  Here software commands a set of poses, an observer reports where the DOT actually
// is (sigma_m per axis), and least squares fits anchor offsets and cord-length offsets.  Then we command fresh target poses with
// the calibrated model and see where the true dot lands.   All error magnitudes are [illustrative]; nothing here is measured.
// Run: node explorers/room/calc/corner-cords-calibration.mjs [seed]
import { world } from './pose.mjs';
import { V, M3, cordGeometry, forwardKin, solveLinear, rng } from './cdpr-core.mjs';
import { lugs, anchors as cage } from './corner-cords-pairing-search.mjs';

const seed = +(process.argv[2] || 1);
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
const nomAnchors = pairing.map(k => cage[k]);
const dotLocal = [0, 0, -16];
const dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);

const env = (k, d) => (process.env[k] ? +process.env[k] : d);
const S = { anchor: env('SIG_ANCHOR', 2.0), lug: env('SIG_LUG', 0.2), cord: env('SIG_CORD', 1.0), meas: env('SIG_MEAS', 0.10) };   // sigma: anchor mm, lug mm, length zero mm, observer mm per axis [illustrative]
const rnd = rng(seed);

function targetPose(r) {
  const shift = [(r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 15];
  const dw = [0, 1, 2].map(() => (r.u() * 2 - 1) * 4 * Math.PI / 180);
  return { R: M3.mul(M3.rodrigues(dw), R0), p: V.add(p0, shift) };
}
// truth
const trueAnchors = nomAnchors.map(a => a.map(v => v + rnd.n() * S.anchor));
const trueLugs = lugs.map(l => l.map(v => v + rnd.n() * S.lug));
const trueOffsets = nomAnchors.map(() => rnd.n() * S.cord);

const cmdLengths = (anch, lg, pose) => cordGeometry(anch, lg, dotLocal, pose).map(g => g.L);
// the true rig: commanded length + zeroing error -> pose by FK on the true geometry
function rigDot(cmd) {
  const Ls = cmd.map((c, i) => c + trueOffsets[i]);
  return forwardKin(trueAnchors, trueLugs, dotLocal, Ls, { p: p0, R: R0 });
}

// --- calibration data
const N = +(process.argv[3] || 40);
const train = []; for (let k = 0; k < N; k++) {
  const tp = targetPose(rnd);
  const cmd = cmdLengths(nomAnchors, lugs, tp);
  const fk = rigDot(cmd);
  const meas = fk.p.map(v => v + rnd.n() * S.meas);
  train.push({ cmd, meas });
}
// parameters: 24 anchor offsets + 8 cord offsets
const NP = 32;
function model(theta, cmd) {
  const anch = nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]);
  const Ls = cmd.map((c, i) => c + theta[24 + i]);
  return forwardKin(anch, lugs, dotLocal, Ls, { p: p0, R: R0 }).p;
}
const prior = new Array(NP).fill(0).map((_, i) => 1 / (i < 24 ? S.anchor : S.cord));   // ridge weights = 1/sigma
let theta = new Array(NP).fill(0);
for (let iter = 0; iter < 12; iter++) {
  const res = [], J = [];
  for (const t of train) {
    const pr = model(theta, t.cmd);
    for (let a = 0; a < 3; a++) res.push((t.meas[a] - pr[a]) / S.meas);
  }
  // numeric Jacobian
  const cols = [];
  for (let j = 0; j < NP; j++) {
    const th2 = theta.slice(); const h = 1e-3; th2[j] += h;
    const col = [];
    for (const t of train) { const pr = model(theta, t.cmd), pr2 = model(th2, t.cmd); for (let a = 0; a < 3; a++) col.push((pr2[a] - pr[a]) / h / S.meas); }
    cols.push(col);
  }
  const JTJ = Array.from({ length: NP }, (_, i) => Array.from({ length: NP }, (_, j) => { let s = 0; for (let k = 0; k < res.length; k++) s += cols[i][k] * cols[j][k]; return s + (i === j ? prior[i] ** 2 : 0) + (i === j ? 1e-9 : 0); }));
  const JTr = Array.from({ length: NP }, (_, i) => { let s = 0; for (let k = 0; k < res.length; k++) s += cols[i][k] * res[k]; return s - prior[i] ** 2 * theta[i]; });
  const dx = solveLinear(JTJ, JTr);
  if (!dx) { console.log('singular'); break; }
  theta = theta.map((v, i) => v + dx[i]);
  const rms = Math.sqrt(res.reduce((s, v) => s + v * v, 0) / res.length);
  if (iter === 0 || iter === 11) console.log(`  iter ${iter}: weighted residual rms ${rms.toFixed(2)} (1 = at the observer noise)`);
  if (Math.hypot(...dx) < 1e-7) break;
}

// --- test: command NEW target poses with (a) the nominal model, (b) the calibrated model; see where the true dot lands
function ikCmd(useTheta, pose) {
  const anch = useTheta ? nomAnchors.map((a, i) => [a[0] + theta[3 * i], a[1] + theta[3 * i + 1], a[2] + theta[3 * i + 2]]) : nomAnchors;
  const off = useTheta ? theta.slice(24) : new Array(8).fill(0);
  return cordGeometry(anch, lugs, dotLocal, pose).map((g, i) => g.L - off[i]);
}
const T = 200; let e0 = [], e1 = [];
for (let k = 0; k < T; k++) {
  const tp = targetPose(rnd);
  const a = rigDot(ikCmd(false, tp)).p, b = rigDot(ikCmd(true, tp)).p;
  e0.push(V.len(V.sub(a, tp.p))); e1.push(V.len(V.sub(b, tp.p)));
}
const st = a => { const s = a.slice().sort((x, y) => x - y); return { rms: Math.sqrt(a.reduce((q, v) => q + v * v, 0) / a.length), p95: s[Math.floor(0.95 * s.length)], max: s[s.length - 1] }; };
const A0 = st(e0), A1 = st(e1);
console.log(`seed ${seed}, ${N} calibration poses; true anchor errors sigma ${S.anchor} mm, cord zeroing sigma ${S.cord} mm, observer sigma ${S.meas} mm per axis`);
console.log(`  dot error over ${T} fresh targets, nominal model   : rms ${A0.rms.toFixed(2)} mm, 95% ${A0.p95.toFixed(2)} mm, max ${A0.max.toFixed(2)} mm`);
console.log(`  dot error over ${T} fresh targets, calibrated model: rms ${A1.rms.toFixed(3)} mm, 95% ${A1.p95.toFixed(3)} mm, max ${A1.max.toFixed(3)} mm`);
