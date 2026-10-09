// line-laser-pose.mjs (eyes, wave 3) - what the two lines of eyes-01's line laser, and the dot's spot, say about the gun's pose.
//
// freedom's question (exchange/freedom--on--eyes-w2.md section 1): "do the two slopes give you the barrel's pitch and roll?".
// Model (all ILLUSTRATIVE except the tube geometry [repo] and the kit's gun frame):
//   corner frame: the joint at the origin; x radial (+ into the wall), y tangent, z up. Straight corner: plate z = 0 for x < 0, wall x = 0 for 0 < z < 6.35
//   (the curvature of r = 61.85 is ignored: over the 5 mm the wall trace spans it is 0.2 mm of sagitta).
//   Gun frame = the kit's (origin nozzle tip, +Z back, -Y grip side, dot at (0,0,-16)); reference pose A = dialsToPose(45,30,-15) unless --pose says otherwise.
//   Camera at (rr sin th, rr cos th, z) on the barrel looking at the dot, roll follows the gun (up = gun +Y); pinhole, 1280 px across, FOV 32.
//   Line laser emitter 90 deg further round and 6 mm further back. ITS FAN PLANE IS FIXED IN THE GUN FRAME. It contains the emitter and the dot;
//   --fanroll rolls it about the emitter-dot axis: 0 = the plane also contains the nominal radial direction (how eyes-01 first drew it).
//   --planes=2 adds a second fan at 90 deg to the first (a cross-hair module).
//   Unknowns (5): dot displacement dx (radial), dz (vertical) and a small rotation w = (wx, wy, wz) about the dot, in the corner frame.
//   A slide dy along the seam leaves every image unchanged (a straight corner): no sensor that sees only the corner can observe it.
//   Observables per fan: normal-form line parameters (angle phi, offset rho) of the plate trace and the wall trace in the image (4 numbers);
//   plus, once, the position of the red spot along the beam's image line (1 number). Line parameters carry noise sigma_px*sqrt(12/N)/L (angle) and sigma_px/sqrt(N) (offset).
// Prints the linearised 1-sigma error of each unknown (mm, deg) with the lines alone, with the spot, and with an IMU on top (gravity sees wx, wy), and names
// the direction (a mix of the unknowns) that a configuration cannot see at all.
// usage: node line-laser-pose.mjs [--sweep=1] [--fanroll=0] [--planes=1] [--camz=85] [--camth=0] [--fov=32] [--sig=0.3] [--imu=0.3] [--pose=45,30,-15]
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const FS = require('../../freedom/calc/statics.js');
const DEG = Math.PI / 180, RAD = 180 / Math.PI;
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const nrm = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const mv = (M, v) => [M[0] * v[0] + M[1] * v[1] + M[2] * v[2], M[3] * v[0] + M[4] * v[1] + M[5] * v[2], M[6] * v[0] + M[7] * v[1] + M[8] * v[2]];
const mmul = (A, B) => { const C = new Array(9); for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[i * 3 + j] = A[i * 3] * B[j] + A[i * 3 + 1] * B[3 + j] + A[i * 3 + 2] * B[6 + j]; return C; };
const tr = M => [M[0], M[3], M[6], M[1], M[4], M[7], M[2], M[5], M[8]];
function rotvec(w) {
  const t = Math.hypot(...w); let a, b;
  if (t < 1e-9) { a = 1; b = 0.5; } else { a = Math.sin(t) / t; b = (1 - Math.cos(t)) / (t * t); }
  const [x, y, z] = w;
  return [1 - b * (y * y + z * z), -a * z + b * x * y, a * y + b * x * z, a * z + b * x * y, 1 - b * (x * x + z * z), -a * x + b * y * z, -a * y + b * x * z, a * x + b * y * z, 1 - b * (x * x + y * y)];
}
const wrap = a => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };

export function makeRig(opt) {
  const o = Object.assign({ pose: [45, 30, -15], camz: 85, camth: 0, fov: 32, fanroll: 0, planes: 1, sig: 0.3, spotSig: 0.5, N: 30, plate: 18, wall: 6 }, opt);
  const P0 = FS.dialsToPose(o.pose[0], o.pose[1], o.pose[2]), R0 = P0.R, D = [0, 0, -16];
  const th = o.camth * DEG, rr = o.camz < 118 ? 27 : 30;
  const C = [rr * Math.sin(th), rr * Math.cos(th), o.camz], E = [rr * Math.sin(th + Math.PI / 2), rr * Math.cos(th + Math.PI / 2), o.camz + 6];
  const fwd = nrm(sub(D, C)), upG = [0, 1, 0], right = nrm(cross(fwd, upG)), upC = cross(right, fwd);
  const f = 640 / Math.tan(o.fov * DEG / 2);
  const proj = P => { const d = sub(P, C), z = dot(d, fwd); return [f * dot(d, right) / z, f * dot(d, upC) / z]; };
  const rNomG = mv(tr(R0), [1, 0, 0]), axE = nrm(sub(E, D)), n0 = nrm(cross(sub(E, D), rNomG));
  const rollAbout = (n, ang) => { const c = Math.cos(ang), s = Math.sin(ang), k = cross(axE, n); return nrm(add(add(mul(n, c), mul(k, s)), mul(axE, dot(axE, n) * (1 - c)))); };
  const normals = [rollAbout(n0, o.fanroll * DEG)]; if (o.planes === 2) normals.push(rollAbout(normals[0], Math.PI / 2));
  const beamG = [0, 0, -1];
  function observe(p) {   // p = [dx, dz, wx, wy, wz] (mm, mm, rad) -> flat observable vector and per-fan details
    const R = mmul(rotvec([p[2], p[3], p[4]]), R0), dotW = [p[0], 0, p[1]];
    const toW = g => add(dotW, mv(R, sub(g, D))), fromW = w => add(D, mv(tr(R), sub(w, dotW)));
    const A0 = fromW([0, 0, 0]), dirC = mv(tr(R), [0, 1, 0]), zG = mv(tr(R), [0, 0, 1]), xG = mv(tr(R), [1, 0, 0]);
    const out = [], det = [];
    normals.forEach(nL => {
      const s = dot(nL, sub(E, A0)) / dot(nL, dirC), Pc = add(A0, mul(dirC, s));
      let dp = nrm(cross(nL, zG)), dw = nrm(cross(nL, xG));
      if (dot(dp, xG) > 0) dp = mul(dp, -1); if (dot(dw, zG) < 0) dw = mul(dw, -1);
      const line = (P, d, L) => { const a = proj(P), b = proj(add(P, mul(d, L))), t = [b[0] - a[0], b[1] - a[1]], len = Math.hypot(...t); return { phi: Math.atan2(t[1], t[0]), rho: (-t[1] * a[0] + t[0] * a[1]) / len, len }; };
      const lp = line(Pc, dp, o.plate), lw = line(Pc, dw, o.wall);
      out.push(lp.phi, lp.rho, lw.phi, lw.rho); det.push({ lp, lw });
    });
    const O_W = toW([0, 0, 0]), dW = mv(R, beamG), hits = [];
    if (dW[2] < -1e-9) { const lam = -O_W[2] / dW[2], X = add(O_W, mul(dW, lam)); if (lam > 0 && X[0] <= 1e-4) hits.push(lam); }
    if (dW[0] > 1e-9) { const lam = -O_W[0] / dW[0], X = add(O_W, mul(dW, lam)); if (lam > 0 && X[2] >= -1e-4 && X[2] <= 6.35) hits.push(lam); }
    const lam = hits.length ? Math.min(...hits) : 16, spot = proj(mul(beamG, lam));
    const a0 = proj(D), a1 = proj(add(D, beamG)), bd = nrm([a1[0] - a0[0], a1[1] - a0[1], 0]);
    out.push((spot[0] - a0[0]) * bd[0] + (spot[1] - a0[1]) * bd[1]);
    return { v: out, det };
  }
  const nObs = 4 * normals.length + 1;
  const isAngle = i => i < 4 * normals.length && i % 2 === 0;
  const steps = [0.02, 0.02, 0.05 * DEG, 0.05 * DEG, 0.05 * DEG];
  const cols = steps.map((h, j) => { const p1 = [0, 0, 0, 0, 0], p2 = [0, 0, 0, 0, 0]; p1[j] = h; p2[j] = -h; const a = observe(p1).v, b = observe(p2).v; return a.map((x, i) => (isAngle(i) ? wrap(x - b[i]) : x - b[i]) / (2 * h)); });
  const A = Array.from({ length: nObs }, (_, i) => cols.map(c => c[i]));   // A[i][j] = d obs_i / d unknown_j, unknowns in (mm, mm, rad, rad, rad)
  const base = observe([0, 0, 0, 0, 0]);
  const sd = []; base.det.forEach(d => { sd.push(o.sig * Math.sqrt(12 / o.N) / d.lp.len, o.sig / Math.sqrt(o.N), o.sig * Math.sqrt(12 / o.N) / d.lw.len, o.sig / Math.sqrt(o.N)); }); sd.push(o.spotSig);
  const mmPx = 2 * Math.hypot(...sub(D, C)) * Math.tan(o.fov * DEG / 2) / 1280;
  return { o, A, sd, nObs, mmPx, base, observe };
}

function jacobiEig(M) {
  const n = M.length, a = M.map(r => r.slice()), v = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));
  for (let sweep = 0; sweep < 80; sweep++) {
    let off = 0; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += a[i][j] * a[i][j];
    if (off < 1e-26) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(a[p][q]) < 1e-32) continue;
      const t = 0.5 * Math.atan2(2 * a[p][q], a[q][q] - a[p][p]), c = Math.cos(t), s = Math.sin(t);
      for (let k = 0; k < n; k++) { const x = a[k][p], y = a[k][q]; a[k][p] = c * x - s * y; a[k][q] = s * x + c * y; }
      for (let k = 0; k < n; k++) { const x = a[p][k], y = a[q][k]; a[p][k] = c * x - s * y; a[q][k] = s * x + c * y; }
      for (let k = 0; k < n; k++) { const x = v[k][p], y = v[k][q]; v[k][p] = c * x - s * y; v[k][q] = s * x + c * y; }
    }
  }
  return { values: a.map((r, i) => r[i]), vectors: v };
}
// Information in (mm, deg): rows = indices of observables used; priors = [[unknown index, sigma in deg]]
export function analyse(rig, rows, priors) {
  const U = [1, 1, DEG, DEG, DEG];   // unknown in (mm|rad) = U * unknown in (mm|deg)
  const F = Array.from({ length: 5 }, () => new Array(5).fill(0));
  for (const i of rows) for (let a = 0; a < 5; a++) for (let b = 0; b < 5; b++) F[a][b] += rig.A[i][a] * U[a] * rig.A[i][b] * U[b] / (rig.sd[i] * rig.sd[i]);
  for (const [j, sdeg] of priors || []) F[j][j] += 1 / (sdeg * sdeg);
  const e = jacobiEig(F), idx = e.values.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]);
  const sig = [0, 1, 2, 3, 4].map(j => { let s = 0, blind = 0; for (let k = 0; k < 5; k++) { if (e.values[k] > 1e-7) s += e.vectors[j][k] * e.vectors[j][k] / e.values[k]; else blind += e.vectors[j][k] * e.vectors[j][k]; } return blind > 1e-3 ? Infinity : Math.sqrt(s); });
  const blind = idx.filter(([l]) => l <= 1e-7).map(([, k]) => e.vectors.map(r => r[k]));
  return { sigma: sig, weakest: idx[0][0] > 1e-7 ? 1 / Math.sqrt(idx[0][0]) : Infinity, blind, weakestVec: e.vectors.map(r => r[idx[0][1]]) };
}
export const NAMES = ['dot radial (mm)', 'dot vertical (mm)', 'turn about radial x (deg)', 'turn about tangent y (deg)', 'turn about vertical z (deg)'];
const fmt = x => (!isFinite(x) || x > 1e3 ? 'blind' : x.toFixed(3));

if (process.argv[1] && process.argv[1].endsWith('line-laser-pose.mjs')) {
  const args = Object.fromEntries(process.argv.slice(2).map(a => a.replace(/^--/, '').split('=')));
  const imu = +(args.imu || 0.3);
  const pr = (rig, title, rows, priors) => { const r = analyse(rig, rows, priors); console.log('  ' + title.padEnd(24) + r.sigma.map(fmt).map(s => s.padStart(9)).join('') + '   ' + (r.blind.length ? 'blind: (dx,dz,wx,wy,wz) = ' + r.blind[0].map(x => x.toFixed(2)).join(',') : 'weakest direction ' + r.weakest.toFixed(2))); return r; };
  const cfgs = args.sweep ? [0, 15, 30, 45, 60, 90].flatMap(fr => [1, 2].map(pl => ({ fanroll: fr, planes: pl }))) : [{ fanroll: +(args.fanroll || 0), planes: +(args.planes || 1) }];
  console.log('columns: dot radial, dot vertical (mm); turns about radial x, tangent y, vertical z (deg). sigma_px ' + (args.sig || 0.3) + ', N 30 points per trace, IMU ' + imu + ' deg on x and y');
  for (const c of cfgs) {
    const rig = makeRig(Object.assign({ camz: +(args.camz || 85), camth: +(args.camth || 0), fov: +(args.fov || 32), sig: +(args.sig || 0.3) }, c, args.pose ? { pose: args.pose.split(',').map(Number) } : {}));
    const nL = 4 * rig.o.planes, lines = [...Array(nL).keys()], all = [...lines, nL];
    console.log('\nfan roll ' + c.fanroll + ' deg, ' + c.planes + ' fan(s); camera z ' + rig.o.camz + ' mm, clock ' + rig.o.camth + ' deg; ' + rig.mmPx.toFixed(3) + ' mm/px; plate trace ' + rig.base.det[0].lp.len.toFixed(0) + ' px, wall trace ' + rig.base.det[0].lw.len.toFixed(0) + ' px');
    console.log('  ' + ''.padEnd(24) + ['radial', 'vertical', 'about x', 'about y', 'about z'].map(s => s.padStart(9)).join(''));
    pr(rig, 'lines only', lines); pr(rig, 'lines + red spot', all); pr(rig, 'lines + spot + IMU', all, [[2, imu], [3, imu]]);
  }
  const rig = makeRig({ camz: +(args.camz || 85), camth: +(args.camth || 0), fov: +(args.fov || 32), fanroll: +(args.fanroll || 0) });
  console.log('\nwhat 1 deg of turn does to the picture (one fan, roll ' + rig.o.fanroll + ' deg): change of the plate-line angle, of the wall-line angle (deg), and the far-end shift of the plate line over its ' + rig.base.det[0].lp.len.toFixed(0) + ' px (' + rig.o.plate + ' mm):');
  [[2, 'about radial x'], [3, 'about tangent y'], [4, 'about vertical z']].forEach(([j, n]) => {
    const p = [0, 0, 0, 0, 0]; p[j] = DEG; const o = rig.observe(p).v, b = rig.base.v;
    const dphiP = wrap(o[0] - b[0]) * RAD, dphiW = wrap(o[2] - b[2]) * RAD, far = Math.abs(wrap(o[0] - b[0])) * rig.base.det[0].lp.len;
    console.log('  ' + n.padEnd(16) + 'plate ' + dphiP.toFixed(3) + '  wall ' + dphiW.toFixed(3) + '   far end of the plate line moves ' + far.toFixed(2) + ' px = ' + (far * rig.mmPx).toFixed(3) + ' mm');
  });
}
