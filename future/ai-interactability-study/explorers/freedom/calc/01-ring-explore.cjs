const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function report(label, opts) {
  const t0 = Date.now();
  const m = FR.build(opts);
  const r = m.solve(new Float64Array(m.n));
  const x = r.x;
  const th = [x[3]/FS.S, x[4]/FS.S, x[5]/FS.S].map(v => v*180/Math.PI);
  const dc = m.dotCompliance(x);
  const T = m.spec.elements.filter(e => e.group==='wires').map(e => (m.springForce(x,e).T).toFixed(2));
  const arm = m.armEl ? m.springForce(x, m.armEl) : null;
  const eig = dc.eig.values.slice(0, 6).map(v => v.toExponential(1)).join(' ');
  console.log('\n== ' + label + '  (' + (Date.now()-t0) + ' ms, ' + r.iters + ' it, conv=' + r.converged + ', gnorm ' + r.gnorm.toExponential(1) + ')');
  console.log(' dot u (mm):', x.slice(0,3).map(v=>v.toFixed(2)).join(', '), ' rot (deg):', th.map(v=>v.toFixed(2)).join(', '));
  console.log(' wire T (N):', T.join(', '), ' armF (N):', arm ? (arm.F ? arm.F.map(v=>v.toFixed(2)).join(',') : arm.T.toFixed(2)) : '-');
  console.log(' dot compliance mm/N diag [r,t,z]:', [0,1,2].map(i => dc.C[i][i].toFixed(2)).join(', '), ' smallest Hessian eig:', eig);
  return {m, r, dc};
}
const base = {};
report('rings loop/loop + arm point at housingTop', {});
report('rings only (no arm)', { arm: { mode: 'none' } });
report('rings seat at tip, no arm', { arm: { mode: 'none' }, rings: [ {id:'tip', at:'tip', s:40, contact:'seat', axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ] });
report('seat tip + arm rigid at housingTop', { arm: { mode: 'rigid', at:'housingTop' }, rings: [ {id:'tip', at:'tip', s:40, contact:'seat', axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ] });
report('seat tip + arm point at gripMid', { arm: { mode: 'point', at:'gripMid' }, rings: [ {id:'tip', at:'tip', s:40, contact:'seat', axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ] });
