// plate_seat.js - the end plate in its slip fit, what a three-foot setting ring makes of it, and what eight tacks do to it.
// Everything about tack lift, foot tolerance and holding is ILLUSTRATIVE; the geometry is from the repo (hardware/assembly/pressure-vessel.md,
// weld-rotation-rig.md): plate OD 4.860 in, bore 4.870 in (123.70 mm), plate 0.250 in thick, recessed 0.250 in, weld circle 123.70 mm.
// Run: node explorers/datum/calc/plate_seat.js > explorers/datum/calc/plate_seat.out
const IN = 25.4, DEG = Math.PI / 180, TAU = 2 * Math.PI;
const Dp = 4.860 * IN, Db = 4.870 * IN, t = 0.250 * IN, Dw = 123.70, R = Dw / 2;
const f = (x, n = 3) => (Math.abs(x) < 1e-12 ? 0 : x).toFixed(n);

console.log('A. Does the slip fit square the plate?');
const diag = Math.hypot(Dp, t);
console.log('   plate OD ' + f(Dp) + ' mm, bore ' + f(Db) + ' mm, radial slip ' + f((Db - Dp) / 2) + ' mm, thickness ' + f(t) + ' mm');
console.log('   plate diagonal sqrt(D^2 + t^2) = ' + f(diag) + ' mm, bore ' + f(Db) + ' mm: the diagonal is ' + f(Db - diag) + ' mm SHORTER than the bore.');
console.log('   A tilted plug of thickness t needs a bore of D cos(a) + t sin(a); its maximum over a is the diagonal, so this plate can lie at ANY tilt,');
console.log('   edge-on if it were let, without touching the wall on both sides. The slip fit does not square it; a burr or a spacer or a hand does.');
console.log('   (Repo: "a rolled-over saw burr is enough to catch a plate part-way down and hold it off its seated depth".)\n');

console.log('B. Face wobble at the weld circle from a plate tilt a (rig acceptance: face TIR <= 0.30 mm)');
for (const a of [0.05, 0.10, 0.139, 0.25, 0.5, 1.0]) console.log('   tilt ' + f(a, 3) + ' deg -> face TIR at the weld circle ' + f(Dw * Math.tan(a * DEG)) + ' mm (amplitude at the station ' + f(R * Math.tan(a * DEG)) + ' mm)');
console.log('   the 0.30 mm acceptance is a tilt of ' + f(Math.atan(0.30 / Dw) / DEG, 3) + ' deg between plate and rotation axis; the crown follows the RIM, so the plate tilt against the rim is what it cannot see.\n');

console.log('C. Three feet on the setting ring (radius rf, azimuths 22.5 + 120 k deg), foot-length error d_i, plate pressed flat against all three');
function feetPlane(d, rf, phi0) {   // plane through three foot points (rf cos p_i, rf sin p_i, d_i); returns amplitude at the weld circle and mean
  let sx = 0, sy = 0, m = 0;
  for (let i = 0; i < 3; i++) { const p = phi0 + i * TAU / 3; sx += d[i] * Math.cos(p); sy += d[i] * Math.sin(p); m += d[i]; }
  const gx = 2 / (3 * rf) * sx, gy = 2 / (3 * rf) * sy;           // gradient (mm per mm)
  return { mean: m / 3, amp: R * Math.hypot(gx, gy), tiltDeg: Math.atan(Math.hypot(gx, gy)) / DEG };
}
function lcg(seed) { let s = seed; return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296; }
for (const rf of [40, 52]) for (const tol of [0.02, 0.05, 0.10]) {
  const rnd = lcg(7); let worst = 0, ssq = 0, N = 4000;
  for (let k = 0; k < N; k++) { const d = [0, 1, 2].map(() => (rnd() * 2 - 1) * tol); const r = feetPlane(d, rf, 22.5 * DEG); worst = Math.max(worst, r.amp); ssq += r.amp * r.amp; }
  const w = feetPlane([tol, -tol, -tol], rf, 22.5 * DEG);
  console.log('   feet at r = ' + rf + ' mm, foot length tolerance +-' + f(tol, 2) + ' mm: face tilt amplitude at the weld circle rms ' + f(Math.sqrt(ssq / N)) + ' mm, worst of ' + N + ' draws ' + f(worst) + ' mm, one-long-two-short ' + f(w.amp) + ' mm');
}
console.log('   Set-screw feet (M3, 0.5 mm pitch, set with a depth gauge) are +-0.02; printed feet +-0.10. The plate face is then the RING\'s plane to that amplitude,');
console.log('   whatever the rim, the tilt in the slip fit or the burr under it did: the surface that set the plate is the surface the gun rides.\n');

console.log('D. Eight tacks, order 0,180,90,270,45,225,135,315 deg [repo: opposite-side-bisecting]; each tack locks the plate edge at its own height h0 + u_i');
const order = [0, 180, 90, 270, 45, 225, 135, 315];
function tacks(uMean, uSd, seed) {
  const rnd = lcg(seed); const gauss = () => { let s = 0; for (let i = 0; i < 12; i++) s += rnd(); return s - 6; };
  const u = order.map(() => uMean + uSd * gauss());
  let c = 0, sx = 0, sy = 0;
  order.forEach((a, i) => { c += u[i]; sx += u[i] * Math.cos(a * DEG); sy += u[i] * Math.sin(a * DEG); });
  return { mean: c / 8, amp: 2 / 8 * Math.hypot(sx, sy) };
}
console.log('   Plate face after the eighth tack = constant + first harmonic (plane fit of the eight locked heights):');
for (const [um, us] of [[0.02, 0.01], [0.05, 0.02], [0.10, 0.05], [0.20, 0.10]]) {
  let m = 0, a2 = 0, N = 2000; for (let k = 0; k < N; k++) { const r = tacks(um, us, 100 + k); m += r.mean; a2 += r.amp * r.amp; }
  console.log('   tack lift mean ' + f(um, 2) + ' mm, spread ' + f(us, 2) + ' mm: plate constant ' + f(m / N) + ' mm, first-harmonic amplitude rms ' + f(Math.sqrt(a2 / N)) + ' mm (about half the spread)');
}
console.log('   A steady lift (the same u at every tack) is a constant: a seat depth shift, one number per tube. Only the spread between tacks tilts the plate.');
console.log('   Feet that clamp during the tacks are a ceiling: the plate cannot rise, the tack pull is locked in as stress, and what comes back when the plug is lifted');
console.log('   is elastic recovery, a fraction r of what a free plate would have moved (r is unknown; the scene uses 0.3). Nothing here knows r; an indicator on the plate face before and after the tacks does.\n');

console.log('E. What the ring removes from the datum chain (illustrative spreads, mm, worst case in sum): seat depth spread and plate seat tilt');
const rows = [['plate pressed by hand to a spacer, as today', 0.50, 0.10], ['setting ring, set-screw feet, feet hold during tacks', 0.06, 0.03], ['setting ring, printed feet, no hold', 0.20, 0.10]];
rows.forEach(r => console.log('   ' + r[0].padEnd(52) + ' depth +-' + f(r[1], 2) + ', tilt +-' + f(r[2], 2)));
