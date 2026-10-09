const ES = require('./eye-support.js');
const f = v => (v >= 0 ? '+' : '') + v.toFixed(2);
console.log('eyes-01 lug on one elastic (rod 70 mm above the lug), 2 N setup pull, +1 N change, open loop (no trim): dot mm per N (r,t,z), beam turn deg per N, tilt from the hand-set pose at setup');
for (const k of [0.2, 0.5, 2, 10]) for (const krot of [0, 0.3, 3, 100]) {
  const t0 = Date.now();
  const p = ES.perNewton({ sup: 'lug', k, krot }, 1);
  console.log('k', String(k).padEnd(4), 'krot', String(krot).padEnd(4), p ? 'dot ' + p.u.map(f).join(',') + ' mm/N | beam ' + p.tiltPerN.toFixed(2) + ' deg/N | setup tilt ' + p.tilt0.toFixed(2) + ' deg | range fills at ' + (6 / Math.max(Math.abs(p.u[0]), Math.abs(p.u[2]))).toFixed(1) + ' N' : 'no equilibrium', (Date.now() - t0) + ' ms');
}
console.log('nose seat + tail bridle');
for (const s of [40, 70, 110]) {
  const p = ES.perNewton({ sup: 'seat', s }, 1);
  console.log('s', s, p ? 'dot ' + p.u.map(f).join(',') + ' mm/N | beam ' + p.tiltPerN.toFixed(2) + ' deg/N | setup tilt ' + p.tilt0.toFixed(2) + ' deg | range fills at ' + (6 / Math.max(Math.abs(p.u[0]), Math.abs(p.u[2]))).toFixed(1) + ' N' : 'no equilibrium');
}
