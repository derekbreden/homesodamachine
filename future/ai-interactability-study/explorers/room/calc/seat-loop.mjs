// seat-loop.mjs - how much does the dot move per newton of pull once the gun is seated, when the seat fork
// hangs from a post and a seat arm (use-02-swing-head as drawn) or from a shorter, stiffer carrier?
//
// Model (all ILLUSTRATIVE, statics only): the gun and shell are rigid; the balls and grooves are rigid; the fork is a rigid
// node at the seat centre; the only compliant things are the post and the seat arm, Euler-Bernoulli beams in a 3D frame
// (post fixed at the bench, seat arm horizontal from the post to the fork). A load F acts at the cable exit (grip base);
// it is moved to the seat centre as a force and a moment; the dot then moves by the fork translation plus the fork
// rotation times the lever from the seat centre to the dot.
// Not modelled: joint stiffness (printed adapters, bolted T-slot corners are worse), bench flexure, contact compliance,
// the swing bearing, and the gun's own shell.
// Section values: 2020 T-slot I about 0.70 cm4 (recovered from room's table-opening-numbers.mjs: 13.6 um/N at 270 mm); torsion J is a
// guess (open profile). 40x40x3 Al tube, 25x25x2.5 steel tube: closed-section formulas. Catalog values NOT checked against a listing.
//
// Run: node explorers/room/calc/seat-loop.mjs
import { world, ANCHORS, RIM_Z } from './pose.mjs';

const roll = 45, hole = 30, vert = -15;
const BENCH_Z = RIM_Z - 238.4;                       // rim stands 238.4 mm above the bench [repo]
const seatLocalZ = 108;                              // flange 116 minus the 8 mm fork sits under it (use-02 default ZF = 116)
const fork = world([0, 0, seatLocalZ], roll, hole, vert);
const dotW = world(ANCHORS.dot, roll, hole, vert);
const exitW = world(ANCHORS.gripBase, roll, hole, vert);   // where the umbilical pulls
const post = [150, -330];                                  // use-02 default: R 362 at bearing atan2(-330, 150)

// ---------------------------------------------------------------- tiny linear algebra
function solve(A, b) {
  const n = b.length, M = A.map((r, i) => r.concat([b[i]]));
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
  }
  const x = Array(n).fill(0);
  for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / M[r][r]; }
  return x;
}
// 3D Euler-Bernoulli beam, local 12x12 (u1 v1 w1 rx1 ry1 rz1 u2 ...), x along the beam
function beamK(E, G, A, Iy, Iz, J, L) {
  const K = Array.from({ length: 12 }, () => Array(12).fill(0));
  const set = (i, j, v) => { K[i][j] = v; K[j][i] = v; };
  const a = E * A / L, t = G * J / L;
  const b1 = 12 * E * Iz / L ** 3, b2 = 6 * E * Iz / L ** 2, b3 = 4 * E * Iz / L, b4 = 2 * E * Iz / L;
  const c1 = 12 * E * Iy / L ** 3, c2 = 6 * E * Iy / L ** 2, c3 = 4 * E * Iy / L, c4 = 2 * E * Iy / L;
  set(0, 0, a); set(6, 6, a); set(0, 6, -a);
  set(3, 3, t); set(9, 9, t); set(3, 9, -t);
  set(1, 1, b1); set(7, 7, b1); set(1, 7, -b1); set(1, 5, b2); set(1, 11, b2); set(5, 7, -b2); set(7, 11, -b2); set(5, 5, b3); set(11, 11, b3); set(5, 11, b4);
  set(2, 2, c1); set(8, 8, c1); set(2, 8, -c1); set(2, 4, -c2); set(2, 10, -c2); set(4, 8, c2); set(8, 10, c2); set(4, 4, c3); set(10, 10, c3); set(4, 10, c4);
  return K;
}
function rot3(ex) { // rotation matrix rows = local axes in global; local y chosen to avoid a vertical-parallel degeneracy
  const x = ex, up = Math.abs(x[2]) > 0.99 ? [1, 0, 0] : [0, 0, 1];
  const yv = [up[1] * x[2] - up[2] * x[1], up[2] * x[0] - up[0] * x[2], up[0] * x[1] - up[1] * x[0]]; const yl = Math.hypot(...yv);
  const y = yv.map(v => v / yl);
  const z = [x[1] * y[2] - x[2] * y[1], x[2] * y[0] - x[0] * y[2], x[0] * y[1] - x[1] * y[0]];
  return [x, y, z];
}
function globalK(sec, p, q) {
  const d = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], L = Math.hypot(...d), R = rot3(d.map(v => v / L));
  const Kl = beamK(sec.E, sec.G, sec.A, sec.I, sec.I, sec.J, L);
  const T = Array.from({ length: 12 }, () => Array(12).fill(0));
  for (let b = 0; b < 4; b++) for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) T[3 * b + i][3 * b + j] = R[i][j];
  // Kg = T^T Kl T
  const KT = Kl.map(r => T[0].map((_, j) => r.reduce((s, v, k) => s + v * T[k][j], 0)));
  return T[0].map((_, i) => KT[0].map((_, j) => T.reduce((s, row, k) => s + row[i] * KT[k][j], 0)));
}
// nodes: 0 base (fixed), 1 post top / arm root, 2 fork. elements 0-1 (post) and 1-2 (arm). returns 3x3 map F -> dot displacement (mm/N)
function loopCompliance(secPost, secArm, nodes, dotPt, exitPt) {
  const n = 3, N = 6 * n, K = Array.from({ length: N }, () => Array(N).fill(0));
  const add = (Ke, a, b) => { const ix = [...Array(6).keys()].map(i => 6 * a + i).concat([...Array(6).keys()].map(i => 6 * b + i)); for (let i = 0; i < 12; i++) for (let j = 0; j < 12; j++) K[ix[i]][ix[j]] += Ke[i][j]; };
  add(globalK(secPost, nodes[0], nodes[1]), 0, 1); add(globalK(secArm, nodes[1], nodes[2]), 1, 2);
  const free = [...Array(12).keys()].map(i => i + 6);       // nodes 1 and 2 free
  const Kf = free.map(i => free.map(j => K[i][j]));
  const C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  const forkP = nodes[2], lever = [exitPt[0] - forkP[0], exitPt[1] - forkP[1], exitPt[2] - forkP[2]];
  const rDot = [dotPt[0] - forkP[0], dotPt[1] - forkP[1], dotPt[2] - forkP[2]];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  for (let k = 0; k < 3; k++) {
    const F = [0, 0, 0]; F[k] = 1;
    const M = cross(lever, F);
    const f = Array(12).fill(0); f[6] = F[0]; f[7] = F[1]; f[8] = F[2]; f[9] = M[0]; f[10] = M[1]; f[11] = M[2];
    const u = solve(Kf, f), t = u.slice(6, 9), th = u.slice(9, 12);
    const dotDisp = cross(th, rDot).map((v, i) => v + t[i]);
    for (let i = 0; i < 3; i++) C[i][k] = dotDisp[i];
  }
  return C;
}
function maxGain(C) { // largest singular value of C (mm per N)
  const CtC = [0, 1, 2].map(i => [0, 1, 2].map(j => C[0][i] * C[0][j] + C[1][i] * C[1][j] + C[2][i] * C[2][j]));
  let v = [1, 1, 1]; for (let it = 0; it < 200; it++) { const w = CtC.map(r => r.reduce((s, x, k) => s + x * v[k], 0)); const l = Math.hypot(...w); v = w.map(x => x / l); }
  const w = CtC.map(r => r.reduce((s, x, k) => s + x * v[k], 0)); return Math.sqrt(v.reduce((s, x, k) => s + x * w[k], 0));
}

const SECT = {
  '2020 T-slot (I 0.70 cm4)': { E: 69000, G: 26000, A: 360, I: 6992, J: 8000 },
  '2020, J x2': { E: 69000, G: 26000, A: 360, I: 6992, J: 16000 },
  '40x40x3 Al tube': { E: 69000, G: 26000, A: 444, I: 101972, J: 152000 },
  '25x25x2.5 steel tube': { E: 200000, G: 77000, A: 225, I: 19219, J: 28000 },
  '40x40x3 steel tube': { E: 200000, G: 77000, A: 444, I: 101972, J: 152000 },
};
const forkH = fork[2] - BENCH_Z;
console.log('fork at world', fork.map(v => v.toFixed(1)).join(', '), ' height above bench', forkH.toFixed(0), 'mm; post at (150, -330)');
const planD = Math.hypot(fork[0] - post[0], fork[1] - post[1]);
console.log('plan distance post -> fork (seat arm length)', planD.toFixed(0), 'mm');
console.log('dot is', Math.hypot(...dotW.map((v, i) => v - fork[i])).toFixed(0), 'mm from the seat centre; cable exit (grip base) is', Math.hypot(...exitW.map((v, i) => v - fork[i])).toFixed(0), 'mm from it\n');

function report(label, postH, armXY, secP, secA) {
  const nodes = [[post[0], post[1], BENCH_Z], [post[0], post[1], BENCH_Z + postH], [armXY[0], armXY[1], BENCH_Z + postH]];
  const C = loopCompliance(secP, secA, nodes, dotW, exitW);
  const g = maxGain(C);
  console.log(label.padEnd(58), '| post', String(Math.round(postH)).padStart(4), 'arm', String(Math.round(Math.hypot(armXY[0] - post[0], armXY[1] - post[1]))).padStart(4), '| dot moves', (g * 1000).toFixed(1).padStart(6), 'um/N worst direction (', (1 / g).toFixed(1), 'N/mm ) | 2 N ->', (2 * g).toFixed(3), 'mm');
  return g;
}
console.log('use-02 as drawn: post to the fork height, seat arm horizontal to the fork');
for (const [name, s] of Object.entries(SECT)) report(name, forkH, [fork[0], fork[1]], s, s);

// the scene draws the post as a 26 mm round bar and the seat arm as a 14 mm round bar (cylinder radii 13 and 7); the material is not stated
const round = (d, E, G) => { const I = Math.PI * d ** 4 / 64; return { E, G, A: Math.PI * d * d / 4, I, J: 2 * I }; };
console.log('as drawn in use-02 (post d26 round, seat arm d14 round; steel then aluminium; the scene states no material):');
report('post d26 / arm d14, steel', forkH, [fork[0], fork[1]], round(26, 200000, 77000), round(14, 200000, 77000));
report('post d26 / arm d14, aluminium', forkH, [fork[0], fork[1]], round(26, 69000, 26000), round(14, 69000, 26000));
report('post d26 steel / arm d14 steel, arm short 100', forkH, [post[0] + (fork[0] - post[0]) * 100 / planD, post[1] + (fork[1] - post[1]) * 100 / planD], round(26, 200000, 77000), round(14, 200000, 77000));
report('post d40 steel / arm d20 steel', forkH, [fork[0], fork[1]], round(40, 200000, 77000), round(20, 200000, 77000));
console.log('\nsame sections with the seat carried by a short post standing on the table (rim-flush pit, room-01): fork about', (fork[2] - RIM_Z).toFixed(0), 'mm above the rim plane, arm 120 mm');
const shortArm = [post[0] + (fork[0] - post[0]) * 120 / planD, post[1] + (fork[1] - post[1]) * 120 / planD];
for (const [name, s] of Object.entries(SECT)) report(name, fork[2] - RIM_Z, shortArm, s, s);

console.log('\nSensitivity: 2020 with the post 320 mm and the arm shortened to 150 / 100 / 60 mm (seat arm hangs off a post nearer the fork)');
for (const la of [330, 150, 100, 60]) { const a = [post[0] + (fork[0] - post[0]) * la / planD, post[1] + (fork[1] - post[1]) * la / planD]; report('2020, arm ' + la, forkH, a, SECT['2020 T-slot (I 0.70 cm4)'], SECT['2020 T-slot (I 0.70 cm4)']); }

// contact compliance (Hertz), sphere on a flat, F per contact: what a printed groove does versus a hardened seat
const Rb = 3;   // 6 mm ball, radius 3 mm
function hertz(F, Est) { // steel ball on a plane of modulus Est (MPa, ball 200 GPa, both nu 0.3): delta in mm
  const Estar = 1 / ((1 - 0.09) / 200000 + (1 - 0.09) / Est);
  return Math.cbrt(9 * F * F / (16 * Estar * Estar * Rb));
}
console.log('\nHertz depth of a 6 mm steel ball on a flat at 20 N per contact (illustrative moduli):');
for (const [nm, E] of [['PETG / ASA-class print, E about 2 GPa', 2000], ['PET-GF, E about 5 GPa', 5000], ['aluminium, E 69 GPa', 69000], ['hardened steel, E 200 GPa', 200000]]) {
  const d = hertz(20, E);
  console.log('  ', nm.padEnd(40), 'indents', (d * 1000).toFixed(1), 'um; tangent stiffness dF/d(delta) =', (1.5 * 20 / (d * 1000)).toFixed(2), 'N/um');
}
console.log('(A 6 mm ball on a printed groove sinks tens of microns at 20 N: the preload sets where the dot sits, and a load change moves it; creep is on top.)');

// ---------------------------------------------------------------- the ring-seat layout of room-12 (plate at gun-local z 138, its own column)
console.log('\nroom-12 layout: seat plate at gun-local z 138 on its own column 100 mm behind it in plan (not shared with the rail mast)');
const forkR = world([0, 0, 138], roll, hole, vert);
const backPlan = [-0.646, -0.764];
const colXY = [forkR[0] + backPlan[0] * 100, forkR[1] + backPlan[1] * 100];
const forkH2 = forkR[2] - BENCH_Z;
const dir0 = (() => { const a = world([0, 0, 0], roll, hole, vert), b = world([0, -0.423, 0.906], roll, hole, vert); const d = b.map((v, i) => v - a[i]); const l = Math.hypot(...d); return d.map(v => v / l); })();
console.log('seat plate at world', forkR.map(v => v.toFixed(1)).join(', '), ' height above bench', forkH2.toFixed(0), ' column at plan', colXY.map(v => v.toFixed(0)).join(', '), ' cable exit dir', dir0.map(v => v.toFixed(3)).join(', '));
const secNames = ['2020 T-slot (I 0.70 cm4)', '40x40x3 Al tube', '25x25x2.5 steel tube'];
const out = {};
for (const nm of secNames) {
  const s2 = SECT[nm];
  const nodes = [[colXY[0], colXY[1], BENCH_Z], [colXY[0], colXY[1], BENCH_Z + forkH2], [forkR[0], forkR[1], BENCH_Z + forkH2]];
  const dotR = world(ANCHORS.dot, roll, hole, vert), exitR = world(ANCHORS.gripBase, roll, hole, vert);
  const C = loopCompliance(s2, s2, nodes, dotR, exitR);
  const g = maxGain(C);
  // pull along the cable exit direction (the cable pulls the gun toward its hook)
  const v = [0, 1, 2].map(i => C[i][0] * dir0[0] + C[i][1] * dir0[1] + C[i][2] * dir0[2]);
  console.log(nm.padEnd(28), 'worst-direction gain', (g * 1000).toFixed(1), 'um/N; pull along the exit line moves the dot (um/N) x,y,z =', v.map(x => (x * 1000).toFixed(1)).join(', '), ' |', (Math.hypot(...v) * 1000).toFixed(1), 'um/N');
  out[nm] = v;
}
console.log('JSON for the scene:', JSON.stringify(Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v.map(x => +(x * 1000).toFixed(2))]))));
