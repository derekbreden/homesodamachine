const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function run(label, opts) {
  const m = FR.build(opts); const r = m.solve(new Float64Array(m.n)); const x = r.x;
  const arm = m.armEl ? m.springForce(x, m.armEl) : null;
  console.log(label, 'conv', r.converged, 'u', Array.from(x.slice(0,3)).map(v=>v.toFixed(2)).join(','), 'rot deg', [x[3],x[4],x[5]].map(v=>(v/FS.S*180/Math.PI).toFixed(2)).join(','), 'armF', arm && arm.F ? arm.F.map(v=>v.toFixed(2)).join(',') : '-', 'W', m.g.W.toFixed(2));
}
run('arm only rigid, no umbilical', { rings: [], umbilical: { F: 0 }, arm: { mode: 'rigid', at: 'housingCtr' } });
run('arm only rigid, kRot huge', { rings: [], umbilical: { F: 0 }, arm: { mode: 'rigid', at: 'housingCtr', kRot: 1e8, k: 1e4 } });
run('arm point at COM-ish (0,-18,178)', { rings: [], umbilical: { F: 0 }, arm: { mode: 'point', at: [0,-18,178] } });
