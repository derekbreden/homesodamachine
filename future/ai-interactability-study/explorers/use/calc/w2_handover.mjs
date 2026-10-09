// Wave 2: where the millimetres go in a support that hands the gun from one owner to the next.
// One axis at the dot (the radial one). Every number is ILLUSTRATIVE (the scene's defaults); nothing is measured.
// The same model is in scenes/use-14-handover-shift. Usage: node calc/w2_handover.mjs
export const DEF = {
  sh: 1.0,      // mm  1-sigma of where a hand leaves the gun
  sg: 0.15,     // mm  1-sigma shift of the shell as an arm grip closes
  sl: 0.05,     // mm  1-sigma shift as a clamp closes
  ss: 0.03,     // mm  1-sigma seat scatter (use-02 illustrative)
  ka: 5,        // N/mm arm at the dot (freedom-01 illustrative)
  kb: 0.15,     // N/mm bungees at the dot (freedom-01 illustrative)
  k1: 0.10, k2: 0.40, // N/mm soft drive springs (travel-05b defaults): ratio r = k1/(k1+k2)
  kL: 50,       // N/mm clamp closed (travel-05b default)
  kS: 40,       // N/mm seat (use-02/room-13 order of magnitude)
  fg: 0.15,     // N   guide friction (travel-05b default)
  fr: 0.05,     // N   ring friction in the suspension (illustrative)
  dF: 1.0,      // N   load change between the dry state and the weld
  sF: 0.05,     // N   force reading noise (for the null before release)
  sc: 0.05,     // mm  camera noise, 1-sigma, on dot-vs-seam
  q: 0.01,      // mm  finest command step at the dot (arm) or at the anchor (soft drive)
  w: 0.10,      // mm  window
  n: 6,         // max trim rounds
  brb: 1.0,     // mm  1-sigma of where the bungees would rest the gun if nothing else held it
  bm: 0,        // mm  mean shift at a grip or clamp closing (a bias)
  learn: false, // the AI has learned the bias and removes it
  after: true,  // observe after the last handover
  match: false, // the dry state carries the weld loads (gas on, wire jogged): only 20 percent of dF is left after the last look
  nullRel: false // null the arm force before releasing it (arrangement C)
};
export function mulberry(seed) { let a = seed >>> 0; return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
export function gauss(rng) { const u = Math.max(1e-12, rng()), v = rng(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
const settle = (x, xeq, band) => (Math.abs(x - xeq) <= band ? x : xeq + Math.sign(x - xeq) * band);  // Coulomb: stays inside the band, else lands on its edge
const quant = (v, q) => Math.round(v / q) * q;

// returns { steps:[{id, label, x, dx, note, rounds}], final }
export function closure(arr, P, rng) {
  const g = () => gauss(rng), steps = []; let x = 0; const bias = P.learn ? 0 : P.bm;
  const push = (id, label, nx, note, rounds, from) => { steps.push({ id, label, x: nx, dx: nx - (from == null ? x : from), note: note || '', rounds: rounds || 0 }); x = nx; };
  const loadLeft = P.match ? 0.2 * P.dF : P.dF;
  push('hand', 'hand sets', P.sh * g(), 'where a hand leaves the gun');
  if (arr === 'A' || arr === 'C') {
    push('grip', 'arm grips', x + P.sg * g() + bias, 'the shell shifts as the grip closes');
    const gain = P.ka / (P.ka + P.kb); let n = 0; const x0 = x;
    for (; n < P.n; n++) { const obs = x + P.sc * g(); if (Math.abs(obs) <= 0.5 * P.w) break; x += quant(-obs, P.q) * gain; }
    push('trim', 'trim (camera)', x, 'arm axis nulls what the camera reads', n, x0);
    if (arr === 'A') { push('weld', 'weld load', x + loadLeft / (P.ka + P.kb), 'load change / (arm + bungee) stiffness'); }
    else {
      let rest = P.brb * g(), nn = 0;                                   // where the bungees would put the gun
      if (P.nullRel) { for (; nn < P.n; nn++) { const fmeas = P.kb * (rest - x) + P.sF * g(); if (Math.abs(fmeas) <= P.sF) break; rest -= quant(fmeas / P.kb, P.q); } }
      const band = P.fr / P.kb;
      push('release', 'arm lets go', settle(x, rest, band), P.nullRel ? 'anchors were nulled to the arm force first' : 'the gun goes to where the bungees rest it', nn);
      push('weld', 'weld load', x + loadLeft / P.kb, 'load change / bungee stiffness');
    }
  } else if (arr === 'B') {
    const r = P.k1 / (P.k1 + P.k2), band = P.fg / (P.k1 + P.k2);
    let xs = x; let n = 0; const x0 = x;   // xs = where the springs alone would rest the gun
    const trim = () => { let m = 0; for (; m < P.n; m++) { const obs = x + P.sc * g(); if (Math.abs(obs) <= 0.5 * P.w) break; xs += r * quant(-obs / r, P.q); x = settle(x, xs, band); } return m; };
    n = trim();
    push('trim', 'trim (anchor)', x, 'anchor moves the gun through the springs, friction band +/-' + band.toFixed(2) + ' mm', n, x0);
    let cycles = 0;
    push('lock', 'clamp closes', x + P.sl * g() + bias, 'the clamp moves the gun as it closes');
    if (P.after) { for (; cycles < P.n; cycles++) { const obs = x + P.sc * g(); if (Math.abs(obs) <= 0.5 * P.w) break; const xb = x, m = trim(); x = x + P.sl * g() + bias; steps.push({ id: 'relock', label: 'unlock, trim, relock', x, dx: x - xb, note: 'one more clamp shift', rounds: m }); } }
    push('weld', 'weld load', x + loadLeft / P.kL, 'load change / clamp stiffness');
  } else if (arr === 'F') {
    push('seat', 'seat takes it', P.ss * g(), 'six contacts locate it: the arm only had to bring it within capture');
    push('weld', 'weld load', x + loadLeft / P.kS, 'load change / seat stiffness');
  }
  return { steps, final: x };
}
export function run(arr, P, N = 2000, seed = 7) {
  const rng = mulberry(seed), fin = [], per = {};
  for (let i = 0; i < N; i++) { const c = closure(arr, P, rng); fin.push(Math.abs(c.final)); c.steps.forEach(s => { (per[s.id] = per[s.id] || []).push(s.dx); }); }
  fin.sort((a, b) => a - b);
  const rms = a => Math.sqrt(a.reduce((t, v) => t + v * v, 0) / a.length);
  return { inside: fin.filter(v => v <= P.w).length / N, p50: fin[Math.floor(N * 0.5)], p95: fin[Math.floor(N * 0.95)], per: Object.fromEntries(Object.entries(per).map(([k, v]) => [k, rms(v)])) };
}
if (process.argv[1] && process.argv[1].endsWith('w2_handover.mjs')) {
  const f = v => v.toFixed(3);
  const show = (name, arr, P) => { const r = run(arr, P); console.log(name.padEnd(46), 'inside window', (100 * r.inside).toFixed(0).padStart(3) + '%', ' median', f(r.p50), ' p95', f(r.p95), ' rms per state', Object.entries(r.per).map(([k, v]) => k + ' ' + f(v)).join(', ')); };
  console.log('defaults: window +/-' + DEF.w + ' mm, load change ' + DEF.dF + ' N, camera ' + DEF.sc + ' mm');
  show('A arm grips and stays', 'A', DEF);
  show('A, dry state carries the weld loads', 'A', { ...DEF, match: true });
  show('A, arm 20 N/mm', 'A', { ...DEF, ka: 20 });
  show('B soft drive + clamp, observe after', 'B', DEF);
  show('B, no look after the clamp', 'B', { ...DEF, after: false });
  show('B, friction 0.02 N', 'B', { ...DEF, fg: 0.02 });
  show('B, friction 0.02 N, no look after', 'B', { ...DEF, fg: 0.02, after: false });
  show('C rings, arm lets go (no null)', 'C', DEF);
  show('C rings, arm lets go (null first)', 'C', { ...DEF, nullRel: true });
  show('C, bungees 3 N/mm', 'C', { ...DEF, kb: 3, nullRel: true });
  show('B, clamp bias 0.08 mm, look after', 'B', { ...DEF, bm: 0.08 });
  show('B, clamp bias 0.08 mm, no look after', 'B', { ...DEF, bm: 0.08, after: false });
  show('B, bias 0.08 learned, no look after', 'B', { ...DEF, bm: 0.08, learn: true, after: false });
  show('F seat (use-02), for comparison', 'F', DEF);
  console.log('\nnull precision of a soft spring: force noise / stiffness =', (DEF.sF / DEF.kb).toFixed(2), 'mm at k =', DEF.kb, 'N/mm;', (DEF.sF / 3).toFixed(3), 'mm at 3 N/mm');
}
