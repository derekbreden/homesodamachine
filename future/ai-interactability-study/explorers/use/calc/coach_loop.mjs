// A3 coach loop (scene use-06-coach-loop): aim, lock, verify. How many rounds until the camera says "inside the window"?
// Start: a hand aims the arm by eye, coarse error N(0, arm) per axis, then locks the ARM: one shift N(0, lock) per axis.
// Model per round (two axes r, z): estimate = truth + N(0, cam); advice = -estimate rounded to the knob step; hand executes advice plus
// N(0, hand notches); the fine stage may shift by N(0, stagelock) if it has a lock of its own; verify estimate = truth + N(0, cam);
// stop when |verify| <= window. The fine knobs sit DOWNSTREAM of the arm lock, so the arm lock shift happens once, not every round. By-eye branch: estimate error eye, no scale, hand misses by 4 x 0.05 mm SD.
// ALL noise numbers are ILLUSTRATIVE; the point is which parameter dominates. Usage: node calc/coach_loop.mjs
const g = () => { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
function run(P, maxR = 9) {
  let e = [g() * P.arm + g() * P.lock, g() * P.arm + g() * P.lock], n = 0, ok = false;
  const cam = P.eye ? P.eye : P.cam, res = P.eye ? 0.05 : P.res, hand = P.eye ? 4 : P.hand;
  while (n < maxR) {
    n++;
    const est = e.map(v => v + g() * cam);
    const notches = est.map(v => (P.eye ? -v / 0.05 : -Math.round(v / res)));
    e = e.map((v, i) => v + (notches[i] + g() * hand) * res);
    e = e.map(v => v + g() * (P.stagelock || 0));
    const ver = e.map(v => v + g() * cam);
    if (Math.hypot(ver[0], ver[1]) <= P.win) { ok = true; break; }
  }
  return { n: ok ? n : maxR + 1, ok, end: Math.hypot(e[0], e[1]) };
}
function stats(P, N = 6000) {
  const r = Array.from({ length: N }, () => run(P)), ok = r.filter(x => x.ok);
  const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
  const p95 = a => a.slice().sort((x, y) => x - y)[Math.floor(a.length * 0.95)];
  return { meanRounds: mean(ok.map(x => x.n)), fail: 1 - ok.length / N, meanEnd: mean(r.map(x => x.end)), p95end: p95(r.map(x => x.end)) };
}
const base = { cam: 0.05, res: 0.05, hand: 1.0, lock: 0.10, stagelock: 0.0, win: 0.10, arm: 1.5 };
const cases = [
  ['default (arm lock once 0.10)', base], ['arm lock shift 0.40 (once)', { ...base, lock: 0.40 }], ['fine stage lock 0.03 each round', { ...base, stagelock: 0.03 }], ['fine stage lock 0.08 each round', { ...base, stagelock: 0.08 }], ['fine stage lock 0.20 each round', { ...base, stagelock: 0.20 }],
  ['camera noise 0.02', { ...base, cam: 0.02 }], ['camera noise 0.10', { ...base, cam: 0.10 }], ['camera noise 0.20', { ...base, cam: 0.20 }],
  ['knob step 0.02', { ...base, res: 0.02 }], ['knob step 0.10', { ...base, res: 0.10 }], ['hand 3 notches', { ...base, hand: 3 }],
  ['window 0.05', { ...base, win: 0.05 }], ['window 0.20', { ...base, win: 0.20 }],
  ['by eye (eye error 0.35)', { ...base, eye: 0.35 }], ['by eye (eye error 0.15)', { ...base, eye: 0.15 }],
];
console.log('case                        mean rounds (converged) | never in 9 rounds | mean true error at the end (mm) | 95th pct');
for (const [name, P] of cases) { const s = stats(P); console.log(name.padEnd(28), s.meanRounds.toFixed(2).padStart(8), '            |', (s.fail * 100).toFixed(1).padStart(6) + ' %', '        |', s.meanEnd.toFixed(3).padStart(8), '                 |', s.p95end.toFixed(3)); }
console.log('\nreading: with the fine knobs downstream of the arm lock the loop converges in about two rounds; what limits it is the camera noise');
console.log('and any shift the fine stage suffers every round (a stage lock or backlash), not the arm lock, which happens once. A stage that shifts by');
console.log('as much as the window each time it is locked never converges.');
