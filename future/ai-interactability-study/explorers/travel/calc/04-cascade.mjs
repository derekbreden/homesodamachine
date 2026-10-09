// 04 - the cascade: hand (setup) -> motor (per tube) -> follow (per revolution), and what is left at the dot.
// All error magnitudes are ILLUSTRATIVE except: runout limits 0.25 mm radial / 0.30 mm face TIR (acceptance numbers in the rig doc [repo]),
// bead speed window 5-15 mm/s [repo], seam radius 61.85 mm [repo]. The tolerance band is a drawing aid, not a requirement.
// The scene travel-02-cascade uses the same equations (ported inline).
// Run: node explorers/travel/calc/04-cascade.mjs
import { INNER_RADIUS as R, fmt } from './lib.mjs';

function lcg(seed) { let s = seed >>> 0; return () => ((s = (1664525 * s + 1013904223) >>> 0) / 4294967296); }
function gauss(rnd) { let u = 0, v = 0; while (u === 0) u = rnd(); while (v === 0) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

export function simulate(p) {
  const rnd = lcg(p.seed || 7);
  const N = 361;
  const omega = p.speed / R;                        // rad/s
  const rows = [];
  // measurement: the AI observes the raw error at every angle with noise sigma (a camera/probe estimate), one dry revolution
  const rawR = [], rawZ = [];
  const b1 = 0.6, b2 = 2.1, bz = 1.05;
  for (let i = 0; i < N; i++) {
    const th = i * Math.PI / 180;
    rawR.push(p.e0r + p.tirR / 2 * Math.cos(th - b1) + p.ovality * Math.cos(2 * th - b2) + p.bearing * Math.sin(7 * th + 0.4));
    rawZ.push(p.e0z + p.tirF / 2 * Math.cos(th - bz) + p.bearing * Math.sin(5 * th + 1.3));
  }
  const noisy = a => a.map(v => v + (p.obsNoise || 0) * gauss(rnd));
  const obsR = p.observe ? noisy(rawR) : null, obsZ = p.observe ? noisy(rawZ) : null;
  const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
  const q = (v, step) => (step > 0 ? Math.round(v / step) * step : v);
  const clamp = (v, r) => Math.max(-r, Math.min(r, v));
  // L1: per-tube static offset
  let u1r = 0, u1z = 0;
  if (p.l1) {
    if (p.observe) { u1r = -q(mean(obsR), p.step1); u1z = -q(mean(obsZ), p.step1); }
    u1r = clamp(u1r, p.range1); u1z = clamp(u1z, p.range1);
  }
  // L2: follow. Fit harmonics 1..H of the OBSERVED error minus the mean (least squares by projection), quantise, lag.
  function fit(obs, H) {
    const m = mean(obs), coef = [];
    for (let h = 1; h <= H; h++) {
      let a = 0, b = 0;
      for (let i = 0; i < N - 1; i++) { const th = i * Math.PI / 180; a += (obs[i] - m) * Math.cos(h * th); b += (obs[i] - m) * Math.sin(h * th); }
      coef.push([2 * a / (N - 1), 2 * b / (N - 1)]);
    }
    return coef;
  }
  const cR = p.l2 && p.observe ? fit(obsR, p.harm) : null, cZ = p.l2 && p.observe ? fit(obsZ, p.harm) : null;
  const lagRad = omega * (p.latency || 0);
  const evalFit = (c, th) => c.reduce((s, ab, k) => s + ab[0] * Math.cos((k + 1) * th) + ab[1] * Math.sin((k + 1) * th), 0);
  let satR = false, satZ = false;
  for (let i = 0; i < N; i++) {
    const th = i * Math.PI / 180;
    let u2r = 0, u2z = 0;
    if (cR) { const raw = -evalFit(cR, th - lagRad); u2r = q(clamp(raw, p.range2), p.step2); if (Math.abs(raw) > p.range2) satR = true; }
    if (cZ) { const raw = -evalFit(cZ, th - lagRad); u2z = q(clamp(raw, p.range2), p.step2); if (Math.abs(raw) > p.range2) satZ = true; }
    rows.push({ deg: i, rawR: rawR[i], rawZ: rawZ[i], afterL1R: rawR[i] + u1r, afterL1Z: rawZ[i] + u1z, resR: rawR[i] + u1r + u2r, resZ: rawZ[i] + u1z + u2z, u2r, u2z });
  }
  const stat = (key) => { const v = rows.map(r => r[key]); return { min: Math.min(...v), max: Math.max(...v), pp: Math.max(...v) - Math.min(...v), rms: Math.sqrt(mean(v.map(x => x * x))) }; };
  return { rows, u1r, u1z, satR, satZ, raw: { r: stat('rawR'), z: stat('rawZ') }, afterL1: { r: stat('afterL1R'), z: stat('afterL1Z') }, res: { r: stat('resR'), z: stat('resZ') },
    maxRate2: p.tirR / 2 * omega, omega };
}

const base = { speed: 8, e0r: 1.7, e0z: -0.9, tirR: 0.25, tirF: 0.30, ovality: 0.03, bearing: 0.01, obsNoise: 0.01, observe: true, l1: true, l2: true,
  step1: 0.02, step2: 0.005, range1: 5, range2: 0.5, harm: 1, latency: 0, seed: 7 };
const cases = [
  ['hand only (no L1, no L2)', { l1: false, l2: false }],
  ['L1 open loop (no observation: nothing to command from)', { observe: false, l2: false }],
  ['L1 closed loop, 0.02 mm steps', { l2: false }],
  ['L1 + L2 follow, harmonic 1, step 0.005', {}],
  ['L1 + L2 follow, harmonics 1-2', { harm: 2 }],
  ['L1 + L2, 2 s latency', { latency: 2 }],
  ['L1 + L2, 0.02 mm steps on L2', { step2: 0.02 }],
  ['L1 + L2, L2 range only +-0.10 mm', { range2: 0.10 }],
  ['L1 + L2, obs noise 0.05 mm', { obsNoise: 0.05 }],
  ['no L2, runout accepted at limits (0.25/0.30) after L1', { l2: false }],
  ['L1 + L2, runout 0.50/0.60 (twice the acceptance limits)', { tirR: 0.5, tirF: 0.6 }],
];
console.log('speed ' + base.speed + ' mm/s -> ' + fmt(base.speed / R / Math.PI * 180, 2) + ' deg/s, ' + fmt(2 * Math.PI * R / base.speed, 1) + ' s per revolution');
console.log('case'.padEnd(62), 'radial p-p / rms (mm)   vertical p-p / rms (mm)   sat');
for (const [name, ov] of cases) {
  const r = simulate({ ...base, ...ov });
  console.log(name.padEnd(62), (fmt(r.res.r.pp, 3) + ' / ' + fmt(r.res.r.rms, 3)).padEnd(23), (fmt(r.res.z.pp, 3) + ' / ' + fmt(r.res.z.rms, 3)).padEnd(25), (r.satR ? 'R ' : '') + (r.satZ ? 'Z' : ''));
}
const r0 = simulate({ ...base });
console.log('\nmax follow rate for tirR=0.25 at 8 mm/s: ' + fmt(r0.maxRate2 * 1000, 1) + ' um/s;  at 15 mm/s: ' + fmt(0.125 * 15 / R * 1000, 1) + ' um/s');
console.log('steps/s for a 5 um step at 15 mm/s: ' + fmt(0.125 * 15 / R / 0.005, 1));
