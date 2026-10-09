// freedom W3: the arm's window in kilograms and what heavier payload does (answers borrowed on freedom-02). ILLUSTRATIVE numbers of calc/20.
const A = require('./20-balanced-arm.js'), G = 9.80665;
const win = o => { const a = A.analyse(o); return a.win.map(w => w[0].toFixed(0) + ' to ' + w[1].toFixed(0)).join(', ') || 'none'; };
console.log('mismatch forgiven = friction / (g L cos th)');
for (const [taf, L, th] of [[0.4, 0.45, 5], [0.4, 0.8, 5], [2.0, 0.45, 5], [8.0, 0.45, 5], [0.4, 0.45, 30]]) console.log(' friction', taf, 'N*m, L', L, 'm, th', th, 'deg:', (taf / (G * L * Math.cos(th * Math.PI / 180))).toFixed(3), 'kg');
console.log('window with spring matched to the payload, error slope 0.15/rad, friction 0.4, brake off:');
for (const m of [1.5, 1.95, 2.3]) console.log(' payload', m, 'kg:', win({ m, md: m, eps: 0.15, taf: 0.4, thMin: -20, thMax: 50 }));
console.log('payload 0.1 kg too heavy for the spring (gas): 1.5 kg:', win({ m: 1.6, md: 1.5, eps: 0.15, taf: 0.4, thMin: -20, thMax: 50 }));
console.log('vernier moves the 1.2 kg gun 10 mm along the arm: torque', (1.2 * G * 0.010).toFixed(3), 'N*m =', (100 * 1.2 * G * 0.010 / 0.4).toFixed(0), '% of the 0.4 N*m band');
console.log('fibre share 0.35 kg: a quarter is', (0.35 / 4 * 1000).toFixed(0), 'g');
// after the brake: what a force step at the tip does. Brake 8 N*m holds; pre-sliding 40 N*m/rad per joint
for (const dF of [0.5, 1, 2]) { const tq = dF * 0.45; console.log('force step', dF, 'N at the tip:', tq.toFixed(2), 'N*m, held by the 8 N*m brake (', (100 * tq / 8).toFixed(0), '% of it), tip deflection by pre-sliding', (tq / 40 * 450).toFixed(1), 'mm'); }
