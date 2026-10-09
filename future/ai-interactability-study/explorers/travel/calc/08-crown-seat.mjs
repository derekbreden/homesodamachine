// 08 - the crown's seat on the tube (exchange on datum-03-rim-crown, wave 2).
// Questions: (A) what does a ring centred by k pads do with a lobed outside diameter; (B) how far does a steady sideways force move a
// ring carried on spring pads; (C) how far does the ring turn under umbilical drag on cords, on a rod, on a wrapped wire pair; (D) what
// does a full ring do on an uneven rim compared with three pads.
// Everything about the tube's shape, the pads and the forces is ILLUSTRATIVE unless tagged: the tube's real roundness, the umbilical's
// force and the gun's mass are [unknown] (context/shared-context.md). Geometry from the repo: OD 127 mm, bore 123.70 mm, wall 1.65 mm.
// Run: node explorers/travel/calc/08-crown-seat.mjs
import { fmt } from './lib.mjs';

const TAU = 2 * Math.PI, DEG = Math.PI / 180;

// ---- A. ring centre from k equal-force spring pads on an OD with one lobe harmonic n of amplitude e (linearised, exact for small e)
// pad i at azimuth th_i = th0 + i*TAU/k; compression_i = r_i - rho - c.u_i; equal compression -> c = (2/k) sum r_i u_i  (k >= 3, equal spacing)
function centreLobe(k, n, e, alpha, th0) {
  let cx = 0, cy = 0;
  for (let i = 0; i < k; i++) {
    const th = th0 + i * TAU / k, r = e * Math.cos(n * (th - alpha));
    cx += r * Math.cos(th); cy += r * Math.sin(th);
  }
  return [2 / k * cx, 2 / k * cy];
}
function gainWorst(k, n) {                       // worst |c|/e over lobe phase and pad clock
  let w = 0;
  for (let a = 0; a < 180; a += 5) for (let t = 0; t < 360 / k; t += 5) { const c = centreLobe(k, n, 1, a * DEG, t * DEG); w = Math.max(w, Math.hypot(c[0], c[1])); }
  return w;
}
console.log('A. Ring centre error / lobe amplitude, k equal-force pads, worst case over lobe phase and pad clock');
console.log('   (a lobe of harmonic n is the OD out-of-round: n = 2 is ovality, n = 3 three-lobing from roll forming or a chuck)');
console.log('   pads k \\ lobe n :   n=1      n=2      n=3      n=4      n=5      n=6      n=7');
for (const k of [3, 4, 5, 6, 8]) {
  const row = [1, 2, 3, 4, 5, 6, 7].map(n => fmt(gainWorst(k, n), 2).padStart(6));
  console.log('   k = ' + k + '           : ' + row.join('   '));
}
console.log('   Rule (checked above): k equal pads pass harmonics n = k-1 and k+1 (and their multiples of k) at gain 1 and reject the rest.');
console.log('   Three pads pass ovality (n=2) at unity; four pads reject ovality and pass three-lobing (n=3); six reject n=2..4.');
console.log('   n = 1 (an OD centre offset) passes at gain 1 for every k: that is the OD-to-bore concentricity term itself.\n');

// V block: two rigid stops at +-gamma about the bisector, third pad a spring pushing the ring into the V. c along the bisector = (r1+r2)/(2 cos g);
// perpendicular part = (r2 - r1)/(2 sin g). Worst-case gain for an n=2 lobe over phase.
function vGain(g, n) {
  let w = 0;
  for (let a = 0; a < 180; a += 2) for (let t = 0; t < 360; t += 5) {
    const th1 = t * DEG - g, th2 = t * DEG + g, r1 = Math.cos(n * (th1 - a * DEG)), r2 = Math.cos(n * (th2 - a * DEG));
    const cb = (r1 + r2) / (2 * Math.cos(g)), cp = (r2 - r1) / (2 * Math.sin(g));
    w = Math.max(w, Math.hypot(cb, cp));
  }
  return w;
}
console.log('   Two rigid stops (a V, half-angle g) plus one spring pad: worst-case centre error / ovality amplitude');
for (const g of [30, 45, 60, 80]) console.log('   V half-angle ' + g + ' deg : n=2 gain ' + fmt(vGain(g * DEG, 2), 2) + ', n=3 gain ' + fmt(vGain(g * DEG, 3), 2));
console.log('   (a V-block on an oval part magnifies the ovality: the classic reason a two-point V is a poor centring device for out-of-round work)\n');

// rocker pairs: 3 rockers at 120 deg, each carrying two spring pads at +-delta and equalising their force through its pivot.
// Solving the equilibrium (see scenes/travel-14-exact-crown): c = (2 / (3 cos d)) * sum_j rbar_j u_j, rbar_j = cos(n d) * r(theta_j)
// so the lobe harmonic n is passed by the 3-point rule (n = 2, 4, 5, 7, ...) times cos(n d)/cos(d); stiffness K = 3 ks cos^2(d).
function rockerGain(n, dl) {
  let w = 0;
  for (let a = 0; a < 180; a += 5) for (let t = 0; t < 120; t += 5) {
    let cx = 0, cy = 0;
    for (let j = 0; j < 3; j++) { const th = t * DEG + j * TAU / 3, rb = Math.cos(n * dl) * Math.cos(n * (th - a * DEG)); cx += rb * Math.cos(th); cy += rb * Math.sin(th); }
    cx *= 2 / (3 * Math.cos(dl)); cy *= 2 / (3 * Math.cos(dl)); w = Math.max(w, Math.hypot(cx, cy));
  }
  return w;
}
console.log('   Three rockers, each averaging two pads at +-delta (six pads): worst-case centre error / lobe amplitude');
console.log('   delta      n=1    n=2    n=3    n=4    n=5    n=6    K (x ks)');
for (const dl of [0, 20, 30, 45, 60]) console.log('   ' + String(dl).padStart(4) + ' deg ' + [1, 2, 3, 4, 5, 6].map(n => fmt(rockerGain(n, dl * DEG), 2).padStart(6)).join(' ') + '   ' + fmt(3 * Math.pow(Math.cos(dl * DEG), 2), 2).padStart(6));
console.log('   delta 45 deg rejects n = 2 and n = 3, passes n = 4 magnified 1.41 and n = 5 at 1.0; n = 1 (a centre offset) always passes at 1.\n');

// ---- B. sideways force on a ring on k spring pads: K = (k/2) ks  (linear, equal pads, in any direction)
console.log('B. Radial stiffness of a ring centred on k spring pads of stiffness ks (K = k/2 * ks) and the shift under a steady sideways force');
console.log('   pad ks (N/mm)    k   K (N/mm)    shift per N (um)   at 1 N     at 3 N     at 9 N (mm)');
for (const ks of [1, 5, 20, 40, 100, 300]) for (const k of [3, 6]) {
  const K = k / 2 * ks;
  console.log('   ' + String(ks).padStart(8) + '        ' + k + '   ' + fmt(K, 1).padStart(7) + '   ' + fmt(1000 / K, 1).padStart(12) + '       ' + [1, 3, 9].map(F => fmt(F / K, 3).padStart(8)).join('   '));
}
// what spring rate does a pad need so that it (a) takes up the OD spread and (b) keeps the ring within 0.02 mm under 3 N
{
  const spread = 0.13 * 2 + 0.10;    // +-0.127 mm OD tolerance (5.000 in +-0.005 in: ILLUSTRATIVE tolerance) plus 0.10 mm ovality/eccentricity
  const Fmin = 2, Fmax = 20;         // N per pad: enough to seat, low enough not to dent a 1.65 mm wall (ILLUSTRATIVE)
  const ks = (Fmax - Fmin) / spread;
  console.log('\n   A pad must keep its force between ' + Fmin + ' and ' + Fmax + ' N over an OD spread of ' + fmt(spread, 2) + ' mm (illustrative): ks <= ' + fmt(ks, 0) + ' N/mm.');
  console.log('   Three such pads: K = ' + fmt(1.5 * ks, 0) + ' N/mm; 3 N sideways then moves the ring ' + fmt(3 / (1.5 * ks), 3) + ' mm. The ring is exactly as stiff as the pad that had to be soft enough to seat.');
  console.log('   Locked (set screws or a cam after settling): K is the contact stiffness, taken here as 500 N/mm per pad (ILLUSTRATIVE): 3 N -> ' + fmt(3 / (1.5 * 500), 4) + ' mm.\n');
}

// float in a clearance fit
console.log('   A ring with a plain radial clearance c on the OD and no pads: it rests wherever the last sideways force left it, up to c/2 either way.');
for (const c of [0.10, 0.20, 0.40]) console.log('   clearance ' + fmt(c, 2) + ' mm -> +-' + fmt(c / 2, 3) + ' mm, and a reversal of the force direction moves it ' + fmt(c, 2) + ' mm');
console.log('');

// ---- C. ring azimuth under umbilical drag. Torque = F * arm (arm = cable exit to axis, 233 mm in datum-03's scene).
console.log('C. Ring turning under umbilical drag (arm 233 mm as in scenes/datum-03-rim-crown; the drag force is [unknown])');
const ARM = 233, RT = 76;      // tether attachment radius 76 mm as in the scene
function az(F, Ktheta) { return F * ARM / Ktheta / DEG; }      // Ktheta in N.mm/rad
const kcord = 1.0;             // N/mm per cord, scene default
const Kcords = 2 * kcord * RT * RT;
const Krod = 200 * RT * RT;    // one tangential tie rod, axial stiffness 200 N/mm (a 3 mm steel rod 100 mm long is ~ 14 kN/mm; ball-joint slop and the post dominate: ILLUSTRATIVE)
// a pre-tensioned steel wire pair wrapped on a groove at r = 76 mm: two wires of EA/L each; K_theta = 2 (EA/L) r^2
const EA = 100e3 * 1.1;        // 1.5 mm steel wire rope: E_eff ~ 100 GPa, metallic area ~ 1.1 mm^2 (ILLUSTRATIVE)
const Lw = 120;
const Kwire = 2 * (EA / Lw) * RT * RT;
console.log('   tether                              K_theta (N.m/rad)    ring turn at 1 N   3 N     10 N     dot slides along seam at 3 N');
for (const [name, K] of [['two cords, 0.2 N/mm each', 2 * 0.2 * RT * RT], ['two cords, 1 N/mm each (scene default)', Kcords], ['one tie rod, 200 N/mm', Krod], ['wrapped wire pair, pre-tensioned', Kwire]]) {
  console.log('   ' + name.padEnd(38) + fmt(K / 1000, 1).padStart(10) + '        ' + [1, 3, 10].map(F => (fmt(az(F, K), 2) + ' deg').padStart(10)).join(' ') + '        ' + fmt(3 * ARM / K * 61.85, 2) + ' mm');
}
console.log('   Any tether that pulls on one tab at radius r (two cords to one tab, or one rod) reacts the drag torque as a NET force on the ring: F_t = drag x arm / r = ' + fmt(ARM / RT, 2) + ' x drag (' + fmt(3 * ARM / RT, 1) + ' N at the default 3 N).');
console.log('   That force goes into the ring seat, so a tab tether multiplies the sideways load the seat sees. A pre-tensioned wire pair wrapped on the ring (two equal and opposite tangential pulls) reacts a pure couple: no net force.');
console.log('   Rotation about the tube axis is the one motion that does not move the dot, so a stiff constraint there costs nothing at the seam. Only its reaction force matters.\n');

// ---- D. full ring on an uneven rim, versus three fixed pads
console.log('D. Vertical: ring on the rim. A full annulus rests on the three highest spots it finds; three pads rest on their own three points.');
console.log('   Rim flatness f (peak to peak over 127 mm OD; the real value is [unknown]). The ring plane passes through three rim points; at the station');
console.log('   (r = 61.85 mm) its height differs from the rim there by up to about f (rough bound). As the tube turns the tilted ring plane sweeps once per revolution:');
for (const f of [0.05, 0.10, 0.20]) console.log('   f = ' + fmt(f, 2) + ' mm -> one-per-revolution vertical error up to ~' + fmt(f, 2) + ' mm at the dot; two stable seatings (a fourth high spot) differ by up to ' + fmt(f, 2) + ' mm');
console.log('   Three pads at fixed clock give one repeatable plane per tube; a full annulus gives whichever three spots the last placement found.');
