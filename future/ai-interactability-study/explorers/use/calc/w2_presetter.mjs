// Wave 2: four ways to centre the tube; per-tube minutes for the person, a presetter and the station; steady-cycle binding resource.
// The same model is in scenes/use-17-driven-presetter. Durations are ILLUSTRATIVE (use-01's, travel-06's). Usage: node calc/w2_presetter.mjs
const P = { tl: 1.0, tc: 1.5, ti: 6.0, ra: 2, tr: 1.0, tp: 44, np: 3, tv: 1.0, plate: 3.0, rest: 9.0, resth: 5.0, rh: 0.06, ra_: 0.05, rd: 0.024, reg: 0.03, shoe: 0.05 };
const rms = (...v) => Math.sqrt(v.reduce((t, x) => t + x * x, 0));
function rows(P, o) {
  const drv = P.np * P.tp / 60, ph = o.plateAtPre ? P.plate : 0, rest = P.rest - ph, restH = P.resth - (o.plateAtPre ? Math.min(P.plate, P.resth) : 0);
  const vf = o.station ? P.tv : 0, vfh = o.station ? 0.5 : 0;
  const R = [
    { n: 'today (hand, station)', hand: P.tl + P.ti + P.resth + (o.shoeOn ? P.tr : 0), pre: 0, sta: P.tl + P.ti + P.rest + (o.shoeOn ? P.tr : 0), e: [P.rh, 0, o.shoeOn ? 0 : P.shoe] },
    { n: 'use-03 (presetter, advisor)', hand: P.tl + P.tc + P.ra * P.tr + ph + vfh + restH, pre: P.tl + P.tc + P.ra * P.tr + ph, sta: 0.3 + vf + rest, e: [P.ra_, o.station ? 0 : P.reg, o.station && o.shoeOn ? 0 : P.shoe] },
    { n: 'travel-06 (driver, station)', hand: P.tl + P.tc + restH, pre: 0, sta: P.tl + P.tc + drv + rest, e: [P.rd, 0, o.shoeOn ? 0 : P.shoe] },
    { n: 'combination (driver, presetter)', hand: P.tl + P.tc + ph + vfh + restH, pre: P.tl + P.tc + drv + ph, sta: 0.3 + vf + rest, e: [P.rd, o.station ? 0 : P.reg, o.station && o.shoeOn ? 0 : P.shoe] },
  ];
  return R.map(r => ({ ...r, bind: Math.max(r.hand, r.pre, r.sta), who: Math.max(r.hand, r.pre, r.sta) === r.sta ? 'station' : Math.max(r.hand, r.pre, r.sta) === r.hand ? 'person' : 'presetter', err: rms(...r.e) }));
}
for (const o of [{ plateAtPre: false, station: true, shoeOn: false }, { plateAtPre: true, station: true, shoeOn: false }, { plateAtPre: true, station: true, shoeOn: true }]) {
  console.log('\noptions', JSON.stringify(o));
  for (const r of rows(P, o)) console.log(r.n.padEnd(34), 'person', r.hand.toFixed(1).padStart(5), ' presetter', r.pre.toFixed(1).padStart(5), ' station', r.sta.toFixed(1).padStart(5), ' binds', r.who.padEnd(9), ' error', r.err.toFixed(3));
}
console.log('\nmeasuring lap at 15 mm/s:', (388.61 / 15).toFixed(1), 's; at 8 mm/s', (388.61 / 8).toFixed(1), 's; at 30 mm/s', (388.61 / 30).toFixed(1), 's');
console.log('shoe engaged after indicating: a shift of F/k on the tube; 1 N on 5 N/mm contacts is', (1 / 5).toFixed(2), 'mm; on 50 N/mm', (1 / 50).toFixed(3), 'mm (illustrative)');
