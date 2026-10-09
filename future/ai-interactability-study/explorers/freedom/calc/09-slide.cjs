const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function slide(m, x, i) { const r = m.rings[i], q = m.bodyPoint(x, r._geom.local), nd = m.nodePos(x, i), ax = M.mv(m.rotOf(x), r._geom.axis); return M.dot(M.sub(nd, q), ax); }
for (const [tip, kb] of [['loop',0.15],['seat',0.15],['loop',0.05]]) {
  const rings = [ {id:'tip', at:'tip', s:40, contact:tip, axis:'y', kb, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb, pre:3} ];
  const m = FR.build({ arm: {mode:'rigid', at:'housingTop'}, rings }); const r = m.solve(new Float64Array(m.n));
  const T = m.spec.elements.filter(e=>e.group==='wires').map(e=>m.springForce(r.x,e).T.toFixed(1));
  console.log('tip', tip, 'kb', kb, 'slide tip ring', slide(m,r.x,0).toFixed(1), 'mm, base ring', slide(m,r.x,1).toFixed(1), 'mm; wires T', T.join(','), 'arm Fz', m.springForce(r.x,m.armEl).F[2].toFixed(1));
}
