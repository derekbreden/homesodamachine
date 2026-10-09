// room-02: the gun standing on three ball feet on the table plane (a "stool" printed as part of the shell).
// Which foot points on the shell underside reach the table plane at plan positions outside the hole, and does the
// centre of mass project inside the foot triangle?  Then: how much of the gun's weight may the ceiling balancer take before
// a sideways umbilical pull lifts a foot?   Gun mass 1.47 kg, CoM, forces: [illustrative] (real values [unknown]).
// Run: node explorers/room/calc/stool-feet.mjs
import { world, ANCHORS, RIM_Z, fmt } from './pose.mjs';
const dl = [45, 30, -15];
const feetLocal = { A: [-16, -20, 150], B: [16, -20, 150], C: [0, -125, 237] };
const foot = {};
for (const [k, p] of Object.entries(feetLocal)) { const w = world(p, ...dl); foot[k] = w; console.log(k, 'local', p, '-> world', fmt(w, 0), ' height above the table (rim plane)', (w[2] - RIM_Z).toFixed(0), 'mm, plan radius', Math.hypot(w[0], w[1]).toFixed(0), '(hole radius 80)'); }
const com = world([0, -23, 181], ...dl), m = 1.47, g = 9.81;
console.log('CoM world', fmt(com, 0), ' height above table', (com[2] - RIM_Z).toFixed(0), 'mm');
const F = [foot.A, foot.B, foot.C];
function loads(Fb, xb, yb, Wc, xg, yg, Hx, Hy, h) {
  const Ntot = m * g - Fb + Wc;
  const rx = m * g * com[0] - Fb * xb + Wc * xg + h * Hx, ry = m * g * com[1] - Fb * yb + Wc * yg + h * Hy;
  const M = [[1, 1, 1], F.map(f => f[0]), F.map(f => f[1])], b = [Ntot, rx, ry];
  const det = (a) => a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0]) + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
  const D = det(M), out = [];
  for (let c = 0; c < 3; c++) { const Mc = M.map((row, i) => row.map((v, j) => (j === c ? b[i] : v))); out.push(det(Mc) / D); }
  return out;
}
const hook = world([0, 17, 185.5], ...dl), grip = world(ANCHORS.gripBase, ...dl);
console.log('balancer attach (housing top lug)', fmt(hook, 0), ' grip base (umbilical)', fmt(grip, 0), ' height of grip base above table', (grip[2] - RIM_Z).toFixed(0), 'mm');
console.log('\nfoot loads (N) [A, B, C]');
for (const share of [0, 0.5, 0.7, 0.9]) {
  for (const [nm, Wc, H] of [['no cable', 0, [0, 0]], ['cable weight 1.8 N down, 0.1 N sideways (-Y)', 1.8, [0, -0.1]], ['cable drag 1 N toward -Y', 0, [0, -1]], ['cable drag 1 N toward +X', 0, [1, 0]], ['stuck-wire yank 10 N toward -Y', 0, [0, -10]]]) {
    const N = loads(share * m * g, hook[0], hook[1], Wc, grip[0], grip[1], H[0], H[1], grip[2] - RIM_Z);
    console.log(`  balancer takes ${(share * 100).toFixed(0).padStart(3)}%  ${nm.padEnd(48)} feet ${N.map(v => v.toFixed(1).padStart(6)).join(' ')}  ${Math.min(...N) < 0 ? '<-- a foot lifts' : ''}`);
  }
}

// ---- cross-check against scene room-02 at its defaults (share 0.35, stance 120, rear 260, umbilical hangs from a following trolley)
{
  const feetScene = [[-17 - 0.6 * 120, -100], [-17 + 0.4 * 120, -100], [-17, -260]];
  F.length = 0; feetScene.forEach(f => F.push([f[0], f[1], 0]));
  const N = loads(0.35 * m * g, hook[0], hook[1], 2.4, grip[0], grip[1], 0, -0.1, grip[2] - RIM_Z);
  console.log('\nscene room-02 default cross-check: feet', feetScene.map(f => f.join(',')).join(' | '), '-> loads', N.map(v => v.toFixed(1)).join(' '), '(scene showed A 1.7, B 5.5, C 4.6)');
}
