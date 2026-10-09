// freedom W3: the numbers the scene freedom-16-fibre-line quotes at its defaults (bundle EI 0.11 N*m^2, 2.5 N/m; clip turns down, R 500, psi 60).
const FL = require('./fibre-line.js');
const dials = { roll: 45, holeDial: 30, vertical: -15 }, alpha = 30.2, fr = FL.frame(dials, alpha), REF = dials;
const N = v => Math.hypot(...v), sub = (a, b) => a.map((x, i) => x - b[i]);
const base = { dials, alpha, EI: 0.11, w: 2.5, N: 80 };
const clip = (o) => FL.routeClip(Object.assign({}, base, { R: 500, psi: 60, turn: -1, slack: 0 }, o || {}));
console.log('== A clip (turn down, R 500, psi 60)');
for (const [lab, o] of [['exact', {}], ['clip 10 mm off', { errPos: 10 }], ['clip 5 deg off', { errAng: 5 }], ['clip -5 deg off', { errAng: -5 }], ['20 mm extra fibre', { slack: 20 }], ['R 400', { R: 400 }], ['R 700', { R: 700 }]]) {
  const r = clip(o); if (!r.ok) { console.log(lab.padEnd(20), 'FAILED', r.reason); continue; }
  const T = FL.torqueAbout(fr.D, r.wrench); console.log(lab.padEnd(20), '|F|', N(r.wrench.F).toFixed(2), 'N | couple', (N(r.wrench.M) / 1000).toFixed(3), 'N*m | torque about D', N(T).toFixed(0), 'N*mm | min radius', r.minR.toFixed(0), 'mm');
}
const ev = (mk) => { const a = mk(0), b = mk(5); const sa = FL.sumWrenches(fr.D, a.list || [a.wrench]), sb = FL.sumWrenches(fr.D, b.list || [b.wrench]); return { dF: N(sub(sb.F, sa.F)), dT: N(sub(sb.T, sa.T)) }; };
console.log('\n== anchor gives 5 mm: |dF|, |d torque about D|');
console.log('A exact', JSON.stringify(ev(d => clip({ dFar: d }))), ' A 10mm off', JSON.stringify(ev(d => clip({ errPos: 10, dFar: d }))));
for (const [k, kind] of [['B', 'none'], ['C', 'arc'], ['D', 'S']]) console.log(k, JSON.stringify(ev(d => FL.routeTether(Object.assign({}, base, { boot: kind, Rb: 350, Ls: 400, F: 0, Lp: 350, dialsRef: REF, dFar: d, N: 60 })))));
console.log('D with F = 3 N', JSON.stringify(ev(d => FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 3, Lp: 350, dialsRef: REF, dFar: d, N: 60 })))));
console.log('\n== aim error of the pulley end (S-boot, F 0): change from the perfect aim');
for (const [v, s] of [[10, 0], [20, 0], [0, 20], [40, 40]]) { const r0 = FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 0, Lp: 350, dialsRef: REF, N: 60 })), r1 = FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 0, Lp: 350, dialsRef: REF, aimV: v, aimS: s, N: 60 })); const s0 = FL.sumWrenches(fr.D, r0.list), s1 = FL.sumWrenches(fr.D, r1.list); console.log('aim', v + '/' + s, 'dF', N(sub(s1.F, s0.F)).toFixed(3), 'N, dTorque', N(sub(s1.T, s0.T)).toFixed(0), 'N*mm'); }
console.log('\n== static wrench, S-boot F0');
const d = FL.routeTether(Object.assign({}, base, { boot: 'S', Rb: 350, Ls: 400, F: 0, Lp: 350, dialsRef: REF, N: 60 }));
console.log('force on gun', d.wrench.F.map(v => v.toFixed(2)), '|F|', N(d.wrench.F).toFixed(2), 'torque about D', N(FL.sumWrenches(fr.D, d.list).T).toFixed(0), 'N*mm, release at', N(sub(d.exitAt, fr.D)).toFixed(0), 'mm, boot length', d.boot.length.toFixed(0), 'mm, sag', d.sag.toFixed(1), 'mm');
console.log('\n== span sag vs EI (S-boot, F 0, Ls 400, w 2 N/m fibre only)');
for (const EI of [0.02, 0.05, 0.1, 0.5]) { const r = FL.routeTether(Object.assign({}, base, { EI, w: 2, boot: 'S', Rb: 350, Ls: 400, F: 0, Lp: 350, dialsRef: REF, N: 60 })); console.log('EI', EI, 'sag', r.sag.toFixed(1), 'mm');}
