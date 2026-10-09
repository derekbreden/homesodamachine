// freedom W3: what a route does to the gun where the cable leaves the shell (calc behind scene freedom-16-fibre-line).
// ILLUSTRATIVE: EI, weight per metre, the clip and rail geometry; the fibre's real EI and weight are [unknown].
const FL = require('./fibre-line.js');
const f = (v, d = 2) => v.map(x => x.toFixed(d)).join(', ');
const dials = { roll: 45, holeDial: 30, vertical: -15 }, alpha = 30.2, fr = FL.frame(dials, alpha);
const N = v => Math.hypot(...v), sub = (a, b) => a.map((x, i) => x - b[i]);
const EIf = 0.1, wf = 2, EIc = 0.01, wc = 0.5;              // fibre and conduit (bundled)
const EI = EIf + EIc, w = wf + wc, GJ = 0.8 * EIf;
const base = { dials, alpha, EI, w, N: 80 };
const T = wr => FL.torqueAbout(fr.D, wr);
console.log('reference pose: |DE| ' + fr.ell.toFixed(0) + ' mm; exit tangent ' + (90 - Math.acos(fr.t[2]) * 180 / Math.PI).toFixed(1) + ' deg above horizontal; roll axis ' + (90 - Math.acos(fr.u[2]) * 180 / Math.PI).toFixed(1) + ' deg above horizontal');
console.log('bundle EI', EI, 'N*m^2, w', w, 'N/m (fibre ' + EIf + ' / ' + wf + ', conduit ' + EIc + ' / ' + wc + ')');
const routes = {
  'A clip R500 psi60 slack40 (exact)': d => FL.routeClip(Object.assign({}, base, { R: 500, psi: 60, turn: 1, slack: 40, dFar: d })),
  'A clip R500 psi60 slack40, err 10 mm / 5 deg': d => FL.routeClip(Object.assign({}, base, { R: 500, psi: 60, turn: 1, slack: 40, errPos: 10, errAng: 5, dFar: d })),
  'B rail, no boot, F0': d => FL.routeTether(Object.assign({}, base, { boot: 'none', Rb: 350, Ls: 400, F: 0, Lp: 350, dFar: d, N: 60 })),
  'C rail, arc boot, F0': d => FL.routeTether(Object.assign({}, base, { boot: 'arc', Rb: 350, Ls: 400, F: 0, Lp: 350, dFar: d, N: 60 })),
  'D rail, S-boot, F0': d => FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 0, Lp: 350, dFar: d, N: 60 })),
  'D rail, S-boot, F3': d => FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 3, Lp: 350, dFar: d, N: 60 })),
};
console.log('\n== STATIC wrench at the release point (force on the gun, couple, torque about the dot, tension line / force line offsets)');
for (const [name, mk] of Object.entries(routes)) {
  const r = mk(0); if (!r.ok) { console.log(name, 'FAILED', r.reason); continue; }
  const F = r.wrench.F, Tq = T(r.wrench);
  console.log(name.padEnd(46), '|F|', N(F).toFixed(2), 'N | couple', (N(r.wrench.M) / 1000).toFixed(3), 'N*m | torque about D', N(Tq).toFixed(0), 'N*mm | release point', (N(sub(r.exitAt, fr.D))).toFixed(0), 'mm from the dot | min radius', r.minR > 9999 ? 'straight' : r.minR.toFixed(0), 'mm');
}
// events
function eventRows(name, mk) {
  const a = mk(0), b = mk(5); if (!a.ok || !b.ok) return [name, 'FAILED'];
  const wa = a.list || [a.wrench], wb = b.list || [b.wrench];
  const sa = FL.sumWrenches(fr.D, wa), sb = FL.sumWrenches(fr.D, wb);
  const dF = sub(sb.F, sa.F), dT = sub(sb.T, sa.T);
  return { dF, dT };
}
console.log('\n== EVENT 1: the far anchor gives 5 mm');
for (const [name, mk] of Object.entries(routes)) { const e = eventRows(name, mk); if (!e.dF) { console.log(name, 'FAILED'); continue; } const row = ['arm', 'seat', 'elastic'].map(k => FL.supportShift(FL.SUPPORTS[k], fr, e.dF, e.dT)); console.log(name.padEnd(46), 'dF', N(e.dF).toFixed(3).padEnd(6), 'N | d(torque about D)', N(e.dT).toFixed(1).padEnd(6), 'N*mm | dot shift arm/seat/elastic', row.map(x => x.total.toFixed(3)).join(' / '), 'mm'); }
console.log('\n== EVENT 2: the wire feed pushes 0.5 N along the conduit at its release point, 23 mm off the fibre');
for (const [name, mk] of Object.entries(routes)) {
  const r = mk(0); if (!r.ok) continue; const dir = r.exitDir, at = r.exitAt.map((v, i) => v + fr.X[i] * 23), dF = dir.map(v => v * 0.5), dT = FL.torqueAbout(fr.D, { at, F: dF, M: [0, 0, 0] });
  const row = ['arm', 'seat', 'elastic'].map(k => FL.supportShift(FL.SUPPORTS[k], fr, dF, dT)); console.log(name.padEnd(46), 'dF 0.500 N | d(torque about D)', N(dT).toFixed(1).padEnd(6), 'N*mm | dot shift arm/seat/elastic', row.map(x => x.total.toFixed(3)).join(' / '), 'mm');
}
console.log('\n== EVENT 3: roll +10 deg (the pulley end of the rail stays where it was aimed)');
const dialsR = { roll: 55, holeDial: 30, vertical: -15 };
for (const [name, mk] of Object.entries(routes)) {
  const r = mk(0); if (!r.ok) continue;
  let dF, dT, note = '';
  if (name[0] === 'A') {
    const L = r.length, rw = FL.rollWrenchClamped(alpha, 10, L, EIf, GJ);
    const lever = FL.lineOffset(fr.D, fr.E, [1, 0, 0]) * 0 + N(sub(fr.E, fr.D)) * 0.9;   // about 0.9 of |DE| perpendicular to the lateral force
    dF = [rw.forceLat, 0, 0]; const tt = Math.hypot(rw.torqueTwist, rw.momentBend, rw.forceLat * lever); dT = [tt, 0, 0]; note = 'twist ' + rw.twistDeg.toFixed(1) + ' deg, swing ' + rw.swingDeg.toFixed(1) + ' deg (twist torque ' + rw.torqueTwist.toFixed(0) + ', bend moment ' + rw.momentBend.toFixed(0) + ' N*mm)';
  } else {
    const mk2 = d => { const p = Object.assign({}, base, { dials: dialsR, dialsRef: dials, N: 60 }); const kind = name[0] === 'B' ? 'none' : (name[0] === 'C' ? 'arc' : 'S'); return FL.routeTether(Object.assign(p, { boot: kind, Rb: 350, Ls: 400, F: name.indexOf('F3') > 0 ? 3 : 0, Lp: 350, dFar: d })); };
    const a2 = mk2(0); const frR = FL.frame(dialsR, alpha); if (!a2.ok) { console.log(name, 'FAILED'); continue; }
    const s0 = FL.sumWrenches(fr.D, r.list), s1 = FL.sumWrenches(fr.D, a2.list); dF = sub(s1.F, s0.F); dT = sub(s1.T, s0.T);
    const ts = FL.twistSwing(alpha, 10); note = 'twist ' + ts.twistDeg.toFixed(1) + ' deg, swing of the exit tangent ' + ts.swingDeg.toFixed(1) + ' deg' + (name[0] === 'D' ? ' (span unchanged; the swivel spins; friction torque only)' : '');
  }
  const row = ['arm', 'seat', 'elastic'].map(k => FL.supportShift(FL.SUPPORTS[k], fr, dF, dT)); console.log(name.padEnd(46), 'dF', N(dF).toFixed(3).padEnd(6), 'N | d(torque about D)', N(dT).toFixed(1).padEnd(6), 'N*mm | dot shift arm/seat/elastic', row.map(x => x.total.toFixed(3)).join(' / '), 'mm |', note);
}
console.log('\n== twist rate per 10 deg of roll = twist / distance to the first rotational hold');
for (const [what, L] of [['rubber-coated hook at 0.12 m', 120], ['clip 0.4 m out', 400], ['clip 0.7 m out', 700], ['swivel collar: next hold is the laser end, about 4.6 m', 4600]]) { const ts = FL.twistSwing(0, 10); console.log(what.padEnd(60), (ts.twistDeg / (L / 1000)).toFixed(1), 'deg/m of twist for 10 deg of roll (alpha 0)'); }
