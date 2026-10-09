// Who owns the wobble: the model used by scene datum-14 (same code, run here in node to print the numbers quoted in the exchange).
// Radial seam offset at the station as harmonics k = 1..3 of the table angle: signal(theta) = sum_k Re(c_k e^{i k theta}).
// Pieces (ILLUSTRATIVE amplitudes): R rig (k 1,2), S seat (k 1), W work (k 1,2,3, rotates with the tube), B judge bias (k 1,3, rotates with the tube).
'use strict';
const TAU = Math.PI * 2;
function rng(seed) { let a = seed >>> 0; return function () { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0, v = 0; while (u === 0) u = r(); v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v); }
const cx = (a, ph) => [a * Math.cos(-ph), a * Math.sin(-ph)];                       // A cos(k th - ph) = Re(A e^{-i ph} e^{i k th})
const cadd = (x, y) => [x[0] + y[0], x[1] + y[1]], csub = (x, y) => [x[0] - y[0], x[1] - y[1]];
const cmul = (x, y) => [x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]], cabs = x => Math.hypot(x[0], x[1]);
const crot = (x, k, psi) => cmul(x, [Math.cos(-k * psi), Math.sin(-k * psi)]);        // signal(theta - psi): c_k e^{-i k psi}
const H = 3;
const zero = () => [[0, 0], [0, 0], [0, 0]];
function draw(r, amps) { return amps.map(a => cx(a, r() * TAU)); }                   // random phases
function sum(...ps) { return zero().map((_, k) => ps.reduce((s, p) => cadd(s, p[k]), [0, 0])); }
function rotate(p, psi) { return p.map((c, k) => crot(c, k + 1, psi)); }
function sig(p, th) { let s = 0; for (let k = 0; k < H; k++) s += p[k][0] * Math.cos((k + 1) * th) - p[k][1] * Math.sin((k + 1) * th); return s; }
function rmsOfDiff(a, b) { let s = 0; for (let k = 0; k < H; k++) { const d = csub(a[k], b[k]); s += (d[0] * d[0] + d[1] * d[1]) / 2; } return Math.sqrt(s); }
// least squares harmonics 1..hh (+DC) from samples (angles, values)
function fitHarm(angles, vals, hh) {
  const n = 2 * hh + 1, M = Array.from({ length: n }, () => new Array(n + 1).fill(0));
  const row = a => { const r = [1]; for (let k = 1; k <= hh; k++) r.push(Math.cos(k * a), Math.sin(k * a)); return r; };
  angles.forEach((a, i) => { const r = row(a); for (let p = 0; p < n; p++) { for (let q = 0; q < n; q++) M[p][q] += r[p] * r[q]; M[p][n] += r[p] * vals[i]; } });
  for (let p = 0; p < n; p++) M[p][p] += 1e-9;
  for (let i = 0; i < n; i++) { let m = i; for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[m][i])) m = r;[M[i], M[m]] = [M[m], M[i]]; for (let r = 0; r < n; r++) if (r !== i) { const f = M[r][i] / M[i][i]; for (let c = i; c <= n; c++) M[r][c] -= f * M[i][c]; } }
  const x = M.map((row2, i) => row2[n] / row2[i]), out = zero();
  for (let k = 1; k <= hh; k++) out[k - 1] = [x[2 * k - 1], -x[2 * k]];          // a cos + b sin = Re((a - i b) e^{i k th})
  return out;
}
function first4(s, r, tnoise) { const a = touchAngles(4), T = s.T; return fitHarm(a, a.map(t => sig(T, t) + tnoise * gauss(r)), 1)[0]; }
function touchAngles(K) { const a = []; for (let j = 0; j < K; j++) a.push(TAU * j / K + 0.3); return a; }

const NB = 60;
function judgeMap(state, N, noise, r) {       // per-bin mean of N laps of (truth + bias + noise); returns harmonics (k<=3) of the bins + raw bins
  const ang = [], y = [];
  for (let j = 0; j < NB; j++) { const th = TAU * j / NB; let s = 0; for (let n = 0; n < N; n++) s += sig(state.T, th) + sig(state.B, th) + noise * gauss(r); ang.push(th); y.push(s / N); }
  return { bins: y, harm: fitHarm(ang, y, H) };
}
function touches(state, K, tnoise, r) { const a = touchAngles(K); return fitHarm(a, a.map(t => sig(state.T, t) + tnoise * gauss(r)), Math.min(H, Math.floor((K - 1) / 2))); }

function fresh(r, P) {
  const R = draw(r, [P.rig, P.rig * 0.5, 0]), S = draw(r, [P.seat, 0, 0]);
  const W = draw(r, [P.work * 1.2, P.work, P.work * 0.4]), B = draw(r, [P.bias, 0, P.bias * 0.65]);
  return { R, S, Wb: W, Bb: B, psi: 0, get T() { return sum(this.R, this.S, rotate(this.Wb, this.psi)); }, get B() { return rotate(this.Bb, this.psi); } };
}
function clone(s) { return { R: s.R, S: s.S, Wb: s.Wb, Bb: s.Bb, psi: s.psi, get T() { return sum(this.R, this.S, rotate(this.Wb, this.psi)); }, get B() { return rotate(this.Bb, this.psi); } }; }

function applyEvent(ev, s, r, P) {
  const n = clone(s);
  switch (ev) {
    case 'lift': n.S = [cadd(s.S[0], cx(0.015, r() * TAU)), [0, 0], [0, 0]]; break;
    case 'reseat': n.S = draw(r, [P.seat, 0, 0]); break;
    case 'rotate': n.S = draw(r, [P.seat, 0, 0]); n.psi = s.psi + 100 * Math.PI / 180; break;
    case 'reclamp': n.R = draw(r, [P.rig, P.rig * 0.5, 0]); break;
    case 'tack': n.Wb = draw(r, [P.work * 1.2, P.work, P.work * 1.2]); n.Bb = draw(r, [P.bias, 0, P.bias * 1.3]); break;
    case 'newtube': n.S = draw(r, [P.seat, 0, 0]); n.Wb = draw(r, [P.work * 1.2, P.work, P.work * 0.4]); n.Bb = draw(r, [P.bias, 0, P.bias * 0.65]); n.psi = r() * TAU; break;
  }
  return n;
}
// What the AI stores after "characterise": judge harmonics c (biased), touch harmonics t (unbiased), rig k>=2 from a master lap (R2, R3)
function characterise(s, P, r) {
  const j = judgeMap(s, P.N, P.noise, r), t = touches(s, P.K, P.tnoise, r);
  const Rm = [[0, 0], csub([s.R[1][0], s.R[1][1]], [0, 0]), [0, 0]].map((c, k) => k === 0 ? [0, 0] : [c[0] + (k === 1 ? P.tnoise * 0.5 * gauss(r) : 0), c[1] + (k === 1 ? P.tnoise * 0.5 * gauss(r) : 0)]);
  return { j: j, t: t, Rm: Rm, psi: s.psi };
}
// Policies after an event; returns replay residual rms (mm) and a cost in seconds
const REV = 388.61 / 8.0, TOUCH = 16;
function policies(ev, s0, P, r) {
  const ch = characterise(s0, P, r), s1 = applyEvent(ev, s0, r, P), T1 = s1.T;
  const stale = rmsOfDiff(T1, ch.j.harm);
  const jn = judgeMap(s1, P.N, P.noise, r), relearn = rmsOfDiff(T1, jn.harm);
  // owner-aware: keep the k>=2 pieces the event leaves alone; rebuild what it moved from touches (unbiased)
  let est, cost;
  const t1 = touches(s1, P.K, P.tnoise, r);
  if (ev === 'lift') { est = ch.t; cost = REV; }                                           // one diagnostic lap says nothing moved
  else if (ev === 'reseat') { est = [first4(s1, r, P.tnoise), ch.t[1], ch.t[2]]; cost = REV + 4 * TOUCH; }   // one diagnostic lap, then only the 1st harmonic is re-measured (4 touches)
  else if (ev === 'rotate') {
    // work piece (k>=2) turns with the tube: recover the turn from the judge's k=2,3 with the rig piece from a master, then re-key
    const Rk = ch.Rm; let best = 0, bestE = 1e9;
    for (let d = 0; d < 360; d += 0.5) { const dd = d * Math.PI / 180; let e = 0; for (const k of [2, 3]) { const pred = cadd(Rk[k - 1], crot(csub(ch.j.harm[k - 1], Rk[k - 1]), k, dd)); const q = csub(jn.harm[k - 1], pred); e += q[0] * q[0] + q[1] * q[1]; } if (e < bestE) { bestE = e; best = dd; } }
    est = [first4(s1, r, P.tnoise), cadd(Rk[1], crot(csub(ch.t[1], Rk[1]), 2, best)), cadd(Rk[2], crot(csub(ch.t[2], Rk[2]), 3, best))]; cost = REV + 4 * TOUCH;
  } else { est = t1; cost = REV + P.K * TOUCH; }                                            // reclamp, tack, newtube: one lap, then refit all from touches
  const owner = rmsOfDiff(T1, est);
  return { stale: stale, relearn: relearn, owner: owner, costRelearn: P.N * REV, costOwner: cost, bias: rmsOfDiff(sum(jn.harm.map(() => [0, 0]) && s1.B, zero()), zero()) };
}
// Judge-minus-touch check: can K touches at a given touch noise read a judge bias of a given size?
function biasCheck(P, T, seed0) {
  let g2 = 0, e2 = 0, b2 = 0;
  for (let i = 0; i < T; i++) {
    const r = rng(seed0 + i * 31), s = fresh(r, P), jn = judgeMap(s, P.N, P.noise, r), a = touchAngles(P.K), Tt = s.T;
    const vals = a.map(t => sig(Tt, t) + P.tnoise * gauss(r));
    const jt = a.map(t => { const b = t / TAU * NB, j0 = Math.floor(b) % NB, j1 = (j0 + 1) % NB, f = b - Math.floor(b); return jn.bins[j0] * (1 - f) + jn.bins[j1] * f; });
    const mj = jt.reduce((x, y) => x + y, 0) / jt.length, mt = vals.reduce((x, y) => x + y, 0) / vals.length;
    let g = 0; jt.forEach((v, k) => { const d = (v - mj) - (vals[k] - mt); g += d * d; }); g2 += g / jt.length;
    b2 += rmsOfDiff(s.B, zero()) ** 2; e2 += P.tnoise * P.tnoise + P.noise * P.noise / P.N;
  }
  const gap = Math.sqrt(g2 / T), exp = Math.sqrt(e2 / T), tb = Math.sqrt(b2 / T);
  return { gap, exp, excess: Math.sqrt(Math.max(0, gap * gap - exp * exp)), trueBias: tb };
}
if (typeof module !== 'undefined' && require.main === module) {
  const P = { rig: 0.06, seat: 0.20, work: 0.06 * 0.8, bias: 0.03, noise: 0.03, N: 3, K: 8, tnoise: 0.02 };
  const evs = ['lift', 'reseat', 'rotate', 'reclamp', 'tack', 'newtube'];
  console.log('radial rms residual after replay (mm), 400 draws; N=' + P.N + ' judge laps (noise ' + P.noise + '), K=' + P.K + ' touches (noise ' + P.tnoise + ')');
  console.log('event     stale   relearn   owner+touch   cost relearn s   cost owner s');
  for (const ev of evs) {
    let a = { stale: 0, relearn: 0, owner: 0 }, c = 0, co = 0; const T = 400;
    for (let i = 0; i < T; i++) { const r = rng(1000 + i * 17 + evs.indexOf(ev) * 7919); const s0 = fresh(r, P); const q = policies(ev, s0, P, r); a.stale += q.stale; a.relearn += q.relearn; a.owner += q.owner; c = q.costRelearn; co = q.costOwner; }
    console.log(ev.padEnd(9), (a.stale / T).toFixed(3).padStart(6), (a.relearn / T).toFixed(3).padStart(8), (a.owner / T).toFixed(3).padStart(12), String(Math.round(c)).padStart(14), String(Math.round(co)).padStart(14));
  }
  let bb = 0; for (let i = 0; i < 400; i++) { const r = rng(5 + i); const s = fresh(r, P); bb += rmsOfDiff(s.B, zero()); } console.log('bias alone (rms mean):', (bb / 400).toFixed(3));
  console.log('\njudge-minus-touch check at K=' + P.K + ', judge noise ' + P.noise + ', N=' + P.N + ', true bias about 25 um rms (mean of 300 draws):');
  for (const tn of [0.005, 0.01, 0.02, 0.04]) { const b = biasCheck(Object.assign({}, P, { tnoise: tn }), 300, 900); console.log('  touch noise ' + tn + ': gap ' + (b.gap * 1000).toFixed(0) + ' um, noise alone ' + (b.exp * 1000).toFixed(0) + ' um, excess ' + (b.excess * 1000).toFixed(0) + ' um (true ' + (b.trueBias * 1000).toFixed(0) + ')'); }
  // amplitude budget of the pieces at defaults
  const r = rng(3), s = fresh(r, P); const amp = p => p.map(c => cabs(c).toFixed(3)).join(', ');
  console.log('piece amplitudes k=1..3: R', amp(s.R), '| S', amp(s.S), '| W', amp(s.Wb), '| B', amp(s.Bb));
}
module.exports = { rng, gauss, fresh, applyEvent, characterise, policies, judgeMap, touches, sig, sum, rotate, rmsOfDiff, fitHarm, cabs, csub, cadd, crot, cx, draw, zero, H, NB, REV, TOUCH };
