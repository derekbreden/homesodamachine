const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const rings = (tip) => [ {id:'tip', at:'tip', s:40, contact:tip, axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ];
for (const kWire of [200, 2, 0.15, 0.02]) for (const [mode, at] of [['rigid','housingTop'],['point','housingTop']]) {
  const opts = { kWire, arm: { mode, at }, rings: rings('seat'), umbilical: { F: 2, droop: 0.5 } };
  const m0 = FR.build(opts); const r0 = m0.solve(new Float64Array(m0.n)); const f0 = m0.springForce(r0.x, m0.armEl).F;
  const t0 = Date.now(); const res = FR.nullWires(opts, 5);
  const m1 = FR.build(Object.assign({}, opts, { wireT: res.T })); const r1 = m1.solve(new Float64Array(m1.n));
  const dc = m1.dotCompliance(r1.x);
  console.log('kWire', String(kWire).padEnd(5), mode, at.padEnd(10), 'before |F|', M.len(f0).toFixed(2), 'after |F|', M.len(res.f).toFixed(2), 'wireT', res.T.map(v=>v.toFixed(1)).join(','), 'dot u', Array.from(r1.x.slice(0,3)).map(v=>v.toFixed(2)).join(','), 'compl', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','), (Date.now()-t0)+'ms', r1.converged?'':'NOCONV');
}
