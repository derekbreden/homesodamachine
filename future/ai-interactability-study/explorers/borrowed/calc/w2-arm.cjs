const A = require('./arm.js'), FA = require('/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/explorers/freedom/calc/20-balanced-arm.js');
const fmt = w => w.length ? w.map(x => x[0].toFixed(0) + '..' + x[1].toFixed(0)).join(' ') : 'none';
console.log('--- checks against freedom-02: gas model, default 1.5 kg on a 2.0 kg spring, friction 0.4, L 0.45');
let a = A.analyse({ type: 'gas', md: 2.0 }, 1.5); console.log('mine gas: window', fmt(a.win), ' | freedom:', fmt(FA.analyse({}).win));
a = A.analyse({ type: 'gas', md: 1.5 }, 1.5); console.log('matched gas: window', fmt(a.win), '| freedom matched:', fmt(FA.analyse({ md: 1.5 }).win));
console.log('--- mismatch tolerance in kg = taf/(g L cos th): L 0.45, th 5 deg');
for (const taf of [0.1, 0.2, 0.4, 1, 2]) for (const L of [0.3, 0.45, 0.8]) console.log('taf', taf, 'L', L, '-> +-', A.tolKg({ taf, L }, 5).toFixed(3), 'kg');
console.log('--- window for a mismatch of 0.1 kg and 0.3 kg, matched md = 1.5, taf 0.4');
for (const type of ['gas', 'coil', 'coil0']) for (const dm of [0, 0.05, 0.1, 0.2, 0.3]) { const r = A.analyse({ type, md: 1.5 }, 1.5 + dm); console.log(type.padEnd(6), 'payload 1.5 +', dm, 'kg: window', fmt(r.win)); }
console.log('--- balance error over angle for a matched plain coil spring, l0 = 0.10 and 0.2 m: net torque N*m at -20, 5, 30, 50 deg');
for (const l0 of [0.05, 0.1, 0.2]) console.log('l0', l0, [-20, 5, 30, 50].map(t => A.net({ type: 'coil', md: 1.5, l0 }, 1.5, t).toFixed(3)).join(' '));
console.log('gas eps .15:', [-20, 5, 30, 50].map(t => A.net({ type: 'gas', md: 1.5 }, 1.5, t).toFixed(3)).join(' '));
console.log('--- payload budget: gun 1.2 + vernier 0.6 + camera 0.15 + cable 0.35 =', 1.2 + 0.6 + 0.15 + 0.35, 'kg; without vernier', 1.2 + 0.15 + 0.35);
console.log('--- cable share drift: 25% of 0.35 kg = ', 0.25 * 0.35, 'kg vs tolerance at taf 0.4, L 0.45:', A.tolKg({ taf: 0.4, L: 0.45 }, 5).toFixed(3), 'kg');
