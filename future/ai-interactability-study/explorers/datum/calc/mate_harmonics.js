// mate_harmonics.js - what a part mated to the tube passes to the gun: motion versus shape.
// A rigid ring on the whole circle follows the tube's MOTION (the rigid offset of the tube from the rotation axis, harmonic 1) and none of its SHAPE
// (ovality, three-lobing: harmonics 2, 3, 4 of the wall); the pads or fingers only decide how much shape leaks into the ring's own centre.
// A mate at the station (a roller on the bore wall a lead s ahead of the dot) follows both, up to the phase its lead costs.
// Amplitudes are ILLUSTRATIVE (the real out-of-round and wall eccentricity of the tubes are [unknown]: `explorers/datum/ideas/datum-21-mates-on-the-tube.md`).
// Run: node explorers/datum/calc/mate_harmonics.js > explorers/datum/calc/mate_harmonics.out
const DEG = Math.PI / 180, TAU = 2 * Math.PI, R = 61.85, N = 720;
const f = (x, n = 3) => x.toFixed(n);
function lcg(seed) { let s = seed; return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296; }

// wall (bore) radial profile in the tube frame: b1 = eccentricity of the bore against the OD centre, b2.. = shape (OD lobes taken equal: uniform wall)
function profile(b, ph) { return th => b.reduce((s, a, i) => s + a * Math.cos((i + 1) * (th - ph[i])), 0); }
function padCentre(fn, k, clock) {           // k equal-force pads/fingers: centre = (2/k) sum r_i u_i  (checked in travel/calc/08)
  let cx = 0, cy = 0; for (let i = 0; i < k; i++) { const t = clock + i * TAU / k, r = fn(t); cx += r * Math.cos(t); cy += r * Math.sin(t); }
  return [2 / k * cx, 2 / k * cy];
}
function series(kind, P, ph, phW) {
  const B = profile(P.b, ph), Bod = profile([0, ...P.b.slice(1)], ph);   // OD lobes: same shape, no centre offset by definition
  let e = new Float64Array(N);
  for (let j = 0; j < N; j++) {
    const th = j / N * TAU;
    if (kind === 'room') e[j] = -(P.w * Math.cos(th - phW) + B(th));                                   // gun fixed in the room, tube indicated to w
    else if (kind === 'od') { const c = padCentre(Bod, P.k, P.clock * DEG); e[j] = c[0] * Math.cos(th) + c[1] * Math.sin(th) - B(th); }   // ring on the OD
    else if (kind === 'bore') { const c = padCentre(B, P.k, P.clock * DEG); e[j] = c[0] * Math.cos(th) + c[1] * Math.sin(th) - B(th); } // ring on the bore (fingers, then lock)
    else if (kind === 'clip') e[j] = B(th + P.s / R) - B(th);                                            // roller on the bore a lead s ahead, gun follows it
  }
  return e;
}
function stats(e) {
  const m = e.reduce((s, v) => s + v, 0) / N; let ss = 0, lo = 1e9, hi = -1e9; const h = [];
  for (let j = 0; j < N; j++) { const v = e[j] - m; ss += v * v; lo = Math.min(lo, v); hi = Math.max(hi, v); }
  for (let n = 1; n <= 5; n++) { let a = 0, b = 0; for (let j = 0; j < N; j++) { const th = j / N * TAU; a += (e[j] - m) * Math.cos(n * th); b += (e[j] - m) * Math.sin(n * th); } h.push(2 / N * Math.hypot(a, b)); }
  return { rms: Math.sqrt(ss / N), pp: hi - lo, h: h };
}
function run(P, seeds = 300) {                 // Monte Carlo over the phases of every term and the pad clock
  const out = {}; const kinds = ['room', 'od', 'bore', 'clip'];
  kinds.forEach(k => { out[k] = { rms: [], pp: [], h: [0, 0, 0, 0, 0] }; });
  const rnd = lcg(11);
  for (let sd = 0; sd < seeds; sd++) {
    const ph = P.b.map(() => rnd() * TAU), phW = rnd() * TAU; const Q = Object.assign({}, P, { clock: rnd() * 360 });
    kinds.forEach(k => { const st = stats(series(k, Q, ph, phW)); out[k].rms.push(st.rms); out[k].pp.push(st.pp); st.h.forEach((v, i) => { out[k].h[i] += v / seeds; }); });
  }
  const q = (a, p) => a.slice().sort((x, y) => x - y)[Math.floor(p * (a.length - 1))];
  kinds.forEach(k => { out[k].med = q(out[k].rms, 0.5); out[k].p90 = q(out[k].rms, 0.9); out[k].ppMed = q(out[k].pp, 0.5); });
  return out;
}
const label = { room: 'room-fixed gun, tube indicated to w', od: 'ring on the OD (k pads, then locked)', bore: 'ring on the bore (k fingers, then locked)', clip: 'roller on the bore, lead s' };

function report(P, title) {
  console.log(title);
  console.log('   w (indicated residual amplitude) ' + f(P.w) + ', wall eccentricity b1 ' + f(P.b[0]) + ', ovality b2 ' + f(P.b[1]) + ', b3 ' + f(P.b[2]) + ', b4 ' + f(P.b[3]) + ' mm; k = ' + P.k + ', lead s = ' + P.s + ' mm');
  const o = run(P);
  console.log('   ' + 'reference'.padEnd(44) + 'rms med  rms p90   p-p med   harmonic amplitudes n=1..5 (mean over phases)');
  ['room', 'od', 'bore', 'clip'].forEach(k => console.log('   ' + label[k].padEnd(44) + f(o[k].med).padStart(7) + f(o[k].p90).padStart(9) + f(o[k].ppMed).padStart(10) + '   ' + o[k].h.map(v => f(v, 3)).join(' ')));
  console.log('');
  return o;
}
const base = { w: 0.125, b: [0.08, 0.10, 0.03, 0.02], k: 3, s: 10 };
report(base, 'A. Default illustrative tube (indicated to the rig limit 0.25 TIR: w = 0.125), three pads or fingers, roller 10 mm ahead');
report(Object.assign({}, base, { w: 0.03 }), 'B. The same tube indicated well (0.06 TIR, w = 0.03): a rigid crown has less to win');
report(Object.assign({}, base, { k: 4 }), 'C. Four pads or fingers: they reject n=2 and pass n=3 and n=5');
report(Object.assign({}, base, { b: [0.15, 0.05, 0.03, 0.02] }), 'D. Wall eccentricity larger than ovality (b1 = 0.15, b2 = 0.05): the bore reference gains what the OD ring cannot know');
report(Object.assign({}, base, { w: 0.015, b: [0.03, 0.11, 0.03, 0.02] }), 'E. A tube that is oval to the rig limit (b2 = 0.11: the OD indicator reads 0.22 TIR) and nearly concentric, well centred (w = 0.015): a 3-pad ring adds a first harmonic as big as the ovality');

console.log('F. Roller lead s, default tube: rms of the varying radial error (median over phases), and the fraction of the shape it leaves. The lead costs 2 sin(n s / 2R) of harmonic n.');
console.log('   s (mm)   lead angle   n=1     n=2     n=3     n=4    rms med   [gain 2 sin(n s / 2R)]');
for (const s of [0, 4, 6, 10, 14, 18, 25, 40]) {
  const o = run(Object.assign({}, base, { s }), 200);
  const g = n => 2 * Math.sin(n * s / (2 * R));
  console.log('   ' + String(s).padStart(4) + '     ' + f(s / R / DEG, 1).padStart(5) + ' deg   ' + [1, 2, 3, 4].map(n => f(g(n), 2)).join('    ') + '    ' + f(o.clip.med).padStart(6));
}
console.log('   A lead does not have to stay: software with an actuator can delay the reading by s / v (2.1 s at 17 mm and 8 mm/s); a passive clip cannot.\n');

console.log('G. The crown\'s radial win over a room-fixed gun on an indicated tube = w - (what the seat passes). Median rms difference room minus OD ring, mm (positive: the crown wins)');
console.log('   rows: w (residual after indicating); columns: b2 (ovality) with k = 3 pads / k = 4 pads; b1 = 0.08, b3 = 0.03.');
console.log('   The rig accepts a tube when the OD indicator reads <= 0.25 TIR, so accepted tubes have w + ovality + ... <= about 0.125 in amplitude: the corner cells');
console.log('   (w = 0.125 with b2 = 0.11) are outside what the rig would accept and are kept only to show the trend.');
for (const w of [0.0125, 0.03, 0.06, 0.125]) {
  const cells = [0.03, 0.06, 0.11].map(b2 => {
    const c = k => { const o = run({ w, b: [0.08, b2, 0.03, 0.02], k, s: 10 }, 200); return o.room.med - o.od.med; };
    return f(c(3), 3).padStart(7) + ' /' + f(c(4), 3).padStart(7);
  });
  console.log('   w = ' + f(w, 4) + '   b2 = 0.03: ' + cells[0] + '    b2 = 0.06: ' + cells[1] + '    b2 = 0.11: ' + cells[2]);
}
console.log('   b1 (wall eccentricity) is common to the room-fixed gun and to every OD ring, so it raises the floor of both and cannot cancel the crown\'s win;');
console.log('   what decides the radial win is w (how well the tube was indicated) against what the pads pass (ovality at k = 3, three-lobing at k = 4).');
