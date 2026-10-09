// feedback-budget.mjs (eyes, wave 3) - arithmetic behind the lens eyes-18 and the notes of eyes-17: what each way of telling or holding a hand
// needs from the estimate, and what a wrong estimate costs. No hand model: only statics and delays. Every number is ILLUSTRATIVE unless a
// source is named; the point is the form of each relation and the order of magnitude, not the values.
//
// Channels (radial axis; the vertical axis is the same):
//   hand    the hand alone, steering by its own eye, resolution `delta` (mm)
//   bar     an LED bar: the lit LED is the estimate, `ledStep` mm per LED; the hand follows it with trust `tau` (0..1)
//   tone    a pitch or pulse rate, `toneStep` mm per step (coarser than the bar)
//   buzz    a buzz at the grip that says which side, once the estimate passes `buzzThr`
//   spring  freedom-14: a bungee between the gun and an anchor a motor moves; pulls toward the estimated seam outside a band, cap `Fcap`
//   brake   eyes-17: a clamp that refuses moves away from the estimated seam outside the band; capacity `Fb`; power off = free
//   stylus  a touch trigger on the shell (freedom-12, eyes-05): no estimate at all
// Faults: biased (b), late (total latency L), frozen (age T), blind, noisy (sigma).
export const P0 = {
  b: 0.30, w: 0.10, tau: 0.7, v: 3, fps: 30, Lproc: 15, Lbrake: 30, Lspring: 60, Lled: 1, Lvis: 200, Ltac: 150, Laud: 150,
  kw: 0.15, Kh: 0.5, Fcap: 2, Fb: 2, Fdet: 0.3, delta: 0.1, sigma: 0.03, ledStep: 0.05, toneStep: 0.10, buzzThr: 0.15, seamRate: 0.02, N: 10,
};
export function budget(p) {
  p = Object.assign({}, P0, p);
  const frame = 1000 / p.fps;                              // ms between eye readings
  const sense = frame + p.Lproc;                           // eye to a fresh estimate (ms), a mean age of half a frame is ignored
  const lat = { bar: sense + p.Lled + p.Lvis, tone: sense + 5 + p.Laud, buzz: sense + 20 + p.Ltac, spring: sense + p.Lspring, brake: sense + p.Lbrake, stylus: 1 + p.Lbrake };   // ms, the human's own delay is in the cues
  const mm = (msLat) => p.v * msLat / 1000;                // mm crossed at hand speed v during a latency
  const out = { frame, sense, lat };
  // where the gun settles (mm from the TRUE seam, 0 = on it) when the estimate reads high by b (so the estimated seam is at -b) and the hand aims at the true seam
  const settle = {
    hand: { at: 0, spread: p.delta },
    bar: { at: -p.tau * p.b, spread: Math.max(p.ledStep, p.delta) / 2 },
    tone: { at: -p.tau * p.b, spread: Math.max(p.toneStep, p.delta) / 2 },
    buzz: { at: -Math.max(0, p.b - p.buzzThr), spread: p.buzzThr / 2 },   // the hand backs off until the buzz stops: it stops at the threshold, inside the estimated band's wider edge
    spring: { at: -Math.min(p.kw * Math.max(0, p.b - p.w), p.Fcap) / (p.Kh + p.kw), spread: p.delta },
    brake: { at: 0, spread: p.delta, refused: -p.b + p.w, effort: p.Fb },                   // 'refused' = where a compliant hand stops if it starts inside the band
    stylus: { at: 0, spread: 0.02 },
  };
  out.settle = settle;
  // does the hand notice? (the disagreement is bigger than its own resolution, or the push is bigger than what it can feel while holding the gun)
  out.noticed = {
    hand: 'not applicable',
    bar: p.tau * p.b > p.delta ? 'if it looks at the dot' : 'no: below the hand’s own resolution',
    tone: p.tau * p.b > p.delta ? 'if it looks at the dot' : 'no',
    buzz: 'a buzz on the wrong side is felt, but not why',
    spring: p.kw * Math.max(0, p.b - p.w) > p.Fdet ? 'yes: a push' : 'no: ' + (p.kw * Math.max(0, p.b - p.w) * 1000).toFixed(0) + ' mN is under what a hand notices on a held gun',
    brake: 'yes: a stop, and it takes ' + p.Fb.toFixed(1) + ' N to get through',
    stylus: 'not applicable',
  };
  out.notes = {
    lateOvershoot: { brake: mm(lat.brake), spring: mm(lat.spring), bar: mm(lat.bar), tone: mm(lat.tone), buzz: mm(lat.buzz), stylus: mm(lat.stylus) },
    frozen: (T) => ({ barShown: 'last value', drift: p.seamRate * T, brake: 'one-way valve at the frozen value', spring: 'constant ' + (p.kw * Math.max(0, p.b - p.w)).toFixed(3) + ' N until it decays' }),
    noisy: {
      barFlicker: p.sigma / p.ledStep,                       // LEDs of flicker (1 sigma)
      springForce: p.kw * p.sigma * 1000,                    // mN
      brakeToggles: (h) => p.fps * 0.5 * (1 - erf(h / (p.sigma * Math.SQRT2))),   // state changes per second for an estimate sitting on a band edge, with hysteresis h: fps x P(noise beyond h); fps/2 at h = 0
    },
    pushes: (n) => Math.sqrt(p.delta * p.delta + 0) / Math.sqrt(Math.max(1, n)),   // 1-sigma of the mean disagreement after n pushes through the wall (hand perception noise only)
  };
  out.pushesToDetect = (bTarget) => Math.ceil(Math.pow(1.96 * p.delta / bTarget, 2));   // pushes to see a bias of bTarget mm at 95 % (hand unbiased)
  return out;
}
function erf(x) { const s = Math.sign(x), t = 1 / (1 + 0.3275911 * Math.abs(x)); const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return s * y; }

if (process.argv[1] && process.argv[1].endsWith('feedback-budget.mjs')) {
  const r = budget({}), f = x => x.toFixed(2);
  console.log('defaults (illustrative):', JSON.stringify(P0));
  console.log('\nsensing: a frame every ' + f(r.frame) + ' ms, +' + P0.Lproc + ' ms processing = a fresh estimate ' + f(r.sense) + ' ms after the event');
  console.log('\nlatency from event to effect (ms), and mm crossed at ' + P0.v + ' mm/s:');
  for (const k of Object.keys(r.lat)) console.log('  ' + k.padEnd(7) + f(r.lat[k]).padStart(8) + ' ms   ' + f(r.notes.lateOvershoot[k]).padStart(6) + ' mm');
  console.log('\nbias b = ' + P0.b + ' mm, band ' + P0.w + ', trust ' + P0.tau + ': where the gun settles (mm from the true seam), and whether the hand notices');
  for (const k of Object.keys(r.settle)) console.log('  ' + k.padEnd(7) + ('at ' + f(r.settle[k].at)).padEnd(10) + ('+/- ' + f(r.settle[k].spread)).padEnd(10) + (r.settle[k].refused !== undefined ? ' (starts inside the band: refused at ' + f(r.settle[k].refused) + ', effort ' + r.settle[k].effort + ' N) ' : '') + r.noticed[k]);
  console.log('\nnoisy estimate, sigma ' + P0.sigma + ' mm: bar flicker +/-' + f(r.notes.noisy.barFlicker) + ' LED, spring force noise ' + f(r.notes.noisy.springForce) + ' mN; brake edge toggles per second at hysteresis 0 / sigma / 2 sigma / 3 sigma: ' + [0, 1, 2, 3].map(m => f(r.notes.noisy.brakeToggles(m * P0.sigma))).join(' / '));
  console.log('frozen for 10 s: seam has moved ' + f(r.notes.frozen(10).drift) + ' mm (runout rate ' + P0.seamRate + ' mm/s); ' + JSON.stringify(r.notes.frozen(10)));
  console.log('\nthe override is data: pushes to see a bias of 0.05 / 0.1 / 0.2 mm at 95 % with the hand seeing to ' + P0.delta + ' mm: ' + [0.05, 0.1, 0.2].map(x => r.pushesToDetect(x)).join(' / '));
  console.log('1-sigma of the mean disagreement after 1 / 4 / 16 pushes: ' + [1, 4, 16].map(n => f(r.notes.pushes(n))).join(' / ') + ' mm');
}
