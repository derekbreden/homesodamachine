const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function slide(m, x, i) { const r = m.rings[i], q = m.bodyPoint(x, r._geom.local), nd = m.nodePos(x, i), ax = M.mv(m.rotOf(x), r._geom.axis); return M.dot(M.sub(nd, q), ax); }
for (const fmax of [1, 4, 8]) for (const carry of [0.5, 0.9]) {
  const rings = [ {id:'tip', at:'tip', s:40, contact:'rubber', axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ];
  const m = FR.build({ fmax, carry, arm: {mode:'rigid', at:'housingTop'}, rings }); const r = m.solve(new Float64Array(m.n));
  const T = m.spec.elements.filter(e=>e.group==='wires').map(e=>m.springForce(r.x,e).T.toFixed(1));
  console.log('Fmax', fmax, 'carry', carry, 'slide tip', slide(m,r.x,0).toFixed(1), 'wires T', T.join(','), 'arm Fz', m.springForce(r.x,m.armEl).F[2].toFixed(1), 'conv', r.converged);
}
