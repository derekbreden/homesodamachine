// room-06 corner cords: can eight taut lines from the corners of the room carry the gun and hold the dot, and how stiff is it?
// Gun mass 1.47 kg, CoM and lug positions on the proxy shell, umbilical pull, cord modulus: all [illustrative] (the real values are [unknown]).
// Run: node explorers/room/calc/corner-cords.mjs
import { world, worldDir, ANCHORS, JOINT, RO, RIM_Z } from './pose.mjs';
import { V, M3, cordGeometry, solveTensions, stiffness3, eig3, rng } from './cdpr-core.mjs';

const dotLocal = [0, 0, -16];
const dials = { roll: 45, hole: 30, vert: -15 };
function poseFromDials(dl, shift = [0, 0, 0], dw = [0, 0, 0]) {
  const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
  const ex = V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), ey = V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), ez = V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o);
  let R = M3.fromColumns(ex, ey, ez);
  const dotW = world(dotLocal, dl.roll, dl.hole, dl.vert);
  if (dw[0] || dw[1] || dw[2]) R = M3.mul(M3.rodrigues(dw), R);   // small extra rotation about the dot
  return { R, p: V.add(dotW, shift) };
}
// lugs on the shell (local, mm), each 3 mm outside the sleeve: [illustrative]
const lugs = [[-16, 0, 109], [16, 0, 109], [-20, 20, 150], [20, 20, 150], [-20, 20, 235], [20, 20, 235], [-18, -118, 237], [18, -118, 237]];
// anchors: four corner poles, two anchors each (top, low): [illustrative cage 700 x 700, top 650, low 170 above the tube bottom]
const anchors = [[350, 350, 650], [-350, 350, 650], [-350, -350, 650], [350, -350, 650], [350, -350, 170], [-350, -350, 170], [-350, 350, 170], [350, 350, 170]];
// which lug goes to which anchor (chosen by hand so cords do not cross the gun's own body or the tube): [illustrative]
// (the first hand pairing 0..7 in order has NO positive internal tension: every cord turned the gun the same way about x;
// corner-cords-pairing-search.mjs found 43 of 40320 pairings that also keep the cords out of the shell)
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
const anchorFor = i => anchors[pairing[i]];
const anchorsOrdered = lugs.map((_, i) => anchorFor(i));

const mass = 1.47, comLocal = [0, -23, 181];    // proxy (opening-pose numbers from wall-port-lever.mjs)
const g = 9.81;

function analyse(pose, opts = {}) {
  const geo = cordGeometry(anchorsOrdered, lugs, dotLocal, pose);
  const com = V.add(pose.p, M3.mulV(pose.R, V.sub(comLocal, dotLocal)));
  const Fg = [0, 0, -mass * g];
  const grip = V.add(pose.p, M3.mulV(pose.R, V.sub(ANCHORS.gripBase, dotLocal)));
  const Fu = opts.umbilical || [0, 0, 0];
  const F = V.add(Fg, Fu);
  const Mo = V.add(V.cross(V.sub(com, com), Fg), V.cross(V.sub(grip, com), Fu));
  const sol = solveTensions(geo, com, F, Mo, opts.tMin ?? 5);
  return { geo, com, sol };
}

const base = poseFromDials(dials);
console.log('anchors (cage corner poles, top and low):'); anchors.forEach((a, i) => console.log('  A' + i, JSON.stringify(a)));
const r0 = analyse(base);
console.log('\n== 1. Opening pose, gun weight only, minimum pretension 5 N per cord');
console.log('  feasible:', r0.sol.feasible, ' tensions (N):', r0.sol.t.map(v => v.toFixed(1)).join(' '), ' cord lengths (mm):', r0.geo.map(x => x.L.toFixed(0)).join(' '));

console.log('\n== 2. Stiffness of the taut set at the gun (translational, N/mm) for several line types [EA values illustrative, unchecked]');
const lines = { 'Dyneema-type 1 mm braid (EA ~ 60 kN)': 6.0e4, '1 mm 7x7 stainless wire (EA ~ 45 kN)': 4.5e4, '0.5 mm stainless wire (EA ~ 12 kN)': 1.2e4, 'nylon 1 mm monofilament (EA ~ 0.3 kN)': 3.0e2 };
for (const [name, EA] of Object.entries(lines)) {
  const K = stiffness3(r0.geo, r0.sol.t, EA), e = eig3(K);
  const kmin = e.values[0], kmax = e.values[2];
  console.log(`  ${name.padEnd(44)} eigen (N/mm) min ${kmin.toFixed(1)} mid ${e.values[1].toFixed(1)} max ${kmax.toFixed(1)}   weakest direction ${e.weakest.map(v => v.toFixed(2)).join(',')}   2 N tug in that direction -> ${(2 / kmin).toFixed(3)} mm`);
}
console.log('  compare the naive pendulum and bungee pair: see suspension-stiffness.mjs (tens of N/m, i.e. 0.01-0.1 N/mm).');

console.log('\n== 3. Feasible region: sample dot offsets +/-25 x +/-25 x +/-15 mm and small extra rotations +/-4 deg about the dot; tensions must stay in [5, 150] N under gun weight + 2 N umbilical pull in six directions');
const R = rng(20260928);
let ok = 0, tot = 0, worstMin = 1e9, worstMax = 0;
const Fus = [[2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]];
for (let n = 0; n < 400; n++) {
  const sh = [(R.u() * 2 - 1) * 25, (R.u() * 2 - 1) * 25, (R.u() * 2 - 1) * 15];
  const dw = [0, 1, 2].map(() => (R.u() * 2 - 1) * 4 * Math.PI / 180);
  const pose = poseFromDials(dials, sh, dw);
  let good = true;
  for (const fu of Fus) {
    const r = analyse(pose, { umbilical: fu, tMin: 5 });
    if (!r.sol.feasible || Math.max(...r.sol.t) > 150) { good = false; break; }
    worstMin = Math.min(worstMin, Math.min(...r.sol.t)); worstMax = Math.max(worstMax, Math.max(...r.sol.t));
  }
  tot++; if (good) ok++;
}
console.log(`  ${ok} of ${tot} sampled poses hold all six disturbances with every cord in tension (worst min ${worstMin.toFixed(1)} N, worst max ${worstMax.toFixed(1)} N)`);

console.log('\n== 4. Sag of a cord under its own weight [derived]');
for (const [nm, mu] of [['1 mm Dyneema braid 0.7 g/m', 0.0007], ['1 mm 7x7 steel 4.4 g/m', 0.0044]]) for (const T of [10, 30]) {
  const L = 0.9, sag = mu * g * L * L / (8 * T) * 1000;
  console.log(`  ${nm}, ${T} N, ${L} m: sag ${sag.toFixed(3)} mm (in the middle of the span; the pull direction at the lug is ${(Math.atan(4 * sag / 1000 / L) * 180 / Math.PI).toFixed(3)} deg off the chord)`);
}

console.log('\n== 5. Cord clearance to the tube and rim for the opening pose (cord lug -> anchor segments vs the tube cylinder r=' + RO + ', z<' + RIM_Z.toFixed(1) + ')');
r0.geo.forEach((c, i) => {
  let minClear = 1e9;
  for (let k = 0; k <= 200; k++) {
    const p = V.add(c.lugW, V.scl(V.sub(c.anchor, c.lugW), k / 200));
    const rad = Math.hypot(p[0], p[1]);
    if (p[2] < RIM_Z) minClear = Math.min(minClear, rad - RO); else minClear = Math.min(minClear, Math.min(minClear, 1e6));
  }
  console.log(`  cord ${i}: min plan clearance to the tube below rim height ${minClear > 1e5 ? 'never below the rim' : minClear.toFixed(1) + ' mm'}`);
});

console.log('\n== 6. Dot deflection under a 2 N umbilical pull at the grip base including the gun turning (6x6 axial stiffness K = A diag(EA/L) A^T about the CoM; geometric term ignored for rotation) [illustrative]');
{
  const geo = r0.geo, com = r0.com;
  const grip = V.add(base.p, M3.mulV(base.R, V.sub(ANCHORS.gripBase, dotLocal)));
  const A = geo.map(g => { const m = V.cross(V.sub(g.lugW, com), g.u); return [g.u[0], g.u[1], g.u[2], m[0], m[1], m[2]]; });
  for (const [nm, EA] of [['Dyneema-type 1 mm', 6e4], ['0.5 mm stainless', 1.2e4]]) {
    const K = Array.from({ length: 6 }, (_, i) => Array.from({ length: 6 }, (_, j) => A.reduce((s, row, k) => s + row[i] * row[j] * EA / geo[k].L, 0)));
    let worst = 0, wd = null;
    const dirs = [[2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]];
    for (const F of dirs) {
      const Mo = V.cross(V.sub(grip, com), F);
      const dx = solveLinear6(K, [F[0], F[1], F[2], Mo[0], Mo[1], Mo[2]]);
      const dp = dx.slice(0, 3), th = dx.slice(3, 6);
      const dDot = V.add(dp, V.cross(th, V.sub(base.p, com)));
      const mag = V.len(dDot); if (mag > worst) { worst = mag; wd = F; }
    }
    console.log(`  ${nm}: worst dot deflection ${(worst * 1000).toFixed(1)} um for 2 N at the grip base (direction ${wd.join(',')})`);
  }
}
function solveLinear6(K, b) {
  const n = 6, M = K.map((r, i) => r.slice().concat([b[i]]));
  for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; [M[c], M[p]] = [M[p], M[c]]; for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; } }
  const x = new Array(n).fill(0); for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / M[r][r]; } return x;
}
