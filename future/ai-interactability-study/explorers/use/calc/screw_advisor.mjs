// A3 / A5: "tell the hand which screw to turn". Three M3x0.5 adjusters at 120 degrees push the tube OD toward the axis.
// Given the first harmonic of an indicator trace (eccentricity vector e of the tube centre relative to the rotation axis),
// screw i must advance by  e . r_i  (r_i = unit vector from the axis to screw i): they sum to zero, so one retracts when two advance.
// Simulation: how many indicate-and-turn rounds until TIR <= 0.20 mm (leaving margin under the accepted 0.25 [repo])?
// Hand error per screw ~ N(0, sigma_deg of a turn) plus 5 % of the move; indicator reading noise 0.01 mm; the tube has an
// out-of-round (2nd harmonic) part o that no screw can correct. ALL noise numbers are ILLUSTRATIVE.
// Usage: node calc/screw_advisor.mjs
const PITCH = 0.5;                                 // M3 x 0.5 mm per turn [assumed standard coarse pitch]
const g = () => { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
const beta = [90, 210, 330].map(d => d * Math.PI / 180);
function tir(e, o, psi) { let mn = 1e9, mx = -1e9; for (let k = 0; k < 360; k += 2) { const t = k * Math.PI / 180, v = e[0] * Math.cos(t) + e[1] * Math.sin(t) + o * Math.cos(2 * t + psi); mn = Math.min(mn, v); mx = Math.max(mx, v); } return mx - mn; }
function run(sigmaDeg, o, target = 0.20) {
  const mag = 0.1 + Math.random() * 0.5, ph = Math.random() * 2 * Math.PI, psi = Math.random() * 2 * Math.PI;
  let e = [mag * Math.cos(ph), mag * Math.sin(ph)], n = 0;
  while (tir(e, o, psi) > target && n < 12) {
    // indicator: first harmonic estimate with noise
    const m = [e[0] + 0.01 * g(), e[1] + 0.01 * g()];
    // advised advance of each screw (mm): push the tube away from the screws it leans toward
    for (let i = 0; i < 3; i++) {
      const adv = m[0] * Math.cos(beta[i]) + m[1] * Math.sin(beta[i]);
      const done = adv + adv * 0.05 * g() + (sigmaDeg / 360) * PITCH * g();
      e[0] -= done * Math.cos(beta[i]) * (2 / 3); e[1] -= done * Math.sin(beta[i]) * (2 / 3);   // 2/3: three-screw geometry, sum of projections
    }
    n++;
  }
  return n;
}
const N = 4000;
console.log('rounds of (indicate, advise, turn) until TIR <= 0.20 mm; initial eccentricity 0.1..0.6 mm; N =', N);
console.log('hand error (deg of a turn)  out-of-round o (mm)  | mean rounds | 95th pct | share that never converge (12 rounds)');
for (const s of [5, 15, 30, 60]) for (const o of [0.03, 0.08, 0.10]) {
  const r = Array.from({ length: N }, () => run(s, o)).sort((a, b) => a - b);
  const mean = r.reduce((a, b) => a + b, 0) / N;
  console.log(String(s).padStart(14), '                ', o.toFixed(2).padStart(6), '           |', mean.toFixed(2).padStart(8), '|', String(r[Math.floor(N * 0.95)]).padStart(6), '  |', (r.filter(x => x >= 12).length / N * 100).toFixed(1) + ' %');
}
console.log('\none degree of a turn of M3x0.5 =', (PITCH / 360).toFixed(4), 'mm at the tip; 15 degrees =', (15 * PITCH / 360).toFixed(3), 'mm');
console.log('an out-of-round tube of amplitude o has TIR about 2 o that no screw removes: TIR floor = 2 o (o=0.08 -> 0.16 mm)');
