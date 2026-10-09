const SM = require('./sled.js');
function row(label, o) { const r = SM.simulate(o, 12, 0.002); const p = r.p; const last = r.trace[r.trace.length - 1];
  console.log(label.padEnd(50), 'K', r.K.toFixed(2), 'N*m/rad | I', r.I.toFixed(4), '| T', r.T.toFixed(2), 's | zeta', r.zeta.toFixed(2), '| tau', r.tau.toFixed(3), 'N*m | static dot', r.dotss.toFixed(2), 'mm | peak', r.peak.toFixed(2), 'mm at', (r.peakT - p.t0).toFixed(2), 's | end', last.dot.toFixed(3), 'mm | bead outside tol', r.beadOut.toFixed(1), 'mm | payload', r.mtot.toFixed(2), 'kg | mm/N', r.mmPerN.toFixed(1), '| drop', r.drop.toFixed(2), 's'); return r; }
console.log('freedom-08 as drawn (pivot at housing top, no keel), 1 N step at 145 mm lever');
row('plumb bob, no keel, bearing only', { mk: 0, c: 0, dF: 1 });
row('plumb bob, no keel, 0.1 N step', { mk: 0, c: 0, dF: 0.1 });
row('plumb bob, no keel, 0.2 N step (trim authority)', { mk: 0, c: 0, dF: 0.2 });
console.log('keel');
row('keel 0.6 kg at 200 mm, undamped', { c: 0 });
row('keel 0.6 kg at 200 mm, critical damper', { c: 0.47 });
row('keel 1.0 kg at 250 mm, undamped', { mk: 1.0, dk: 0.25, c: 0 });
row('keel 1.0 kg at 250 mm, critical damper', { mk: 1.0, dk: 0.25, c: 1.0 });
console.log('cable anchored on the pivot line');
row('keel 0.6/0.2, critical damper, e = 0', { c: 0.47, e: 0 });
row('keel 0.6/0.2, critical damper, e = 5 mm', { c: 0.47, e: 0.005 });
row('keel 0.6/0.2, critical, e = 0, couple 0.05 N*m', { c: 0.47, e: 0, dC: 0.05 });
row('keel 0.6/0.2, critical, e = 0, couple 0.2 N*m', { c: 0.47, e: 0, dC: 0.2 });
console.log('the couple alone and the moment of the force');
row('no keel, e=0, couple 0.14 N*m (EI 0.05, R 0.35)', { mk: 0, c: 0, e: 0, dC: 0.14 });
console.log('what e and K make 0.15 mm at the dot for a 1 N step:');
for (const mk of [0, 0.6, 1.5]) { const d = SM.derived({ mk: mk, dk: 0.2 }); console.log('  mk', mk, 'K', d.K.toFixed(2), 'e allowed for 0.15 mm/N =', (0.15 / d.mmPerN * 0.145 * 1000).toFixed(2), 'mm'); }
console.log('trim resolution: 1 mm of a trim mass of 100 g -> deg of tilt, without keel and with 0.6 kg keel at 200 mm:');
for (const mk of [0, 0.6, 1.0]) { const d = SM.derived({ mk: mk, dk: 0.2 }); const dth = (0.1 * 0.001) / (d.S); console.log('  mk', mk, '=> ', (dth * 180 / Math.PI).toFixed(3), 'deg per mm of 100 g trim; range +-30 mm =', (dth * 30 * 180 / Math.PI).toFixed(2), 'deg; dot per mm', (dth * 0.202 * 1000).toFixed(3), 'mm'); }
const t = row('trim loop on, keel, critical damper, dF 0.2', { trim: true, c: 0.47, dF: 0.2 });
const t2 = row('trim loop on, keel, critical damper, dF 1', { trim: true, c: 0.47, dF: 1 });
