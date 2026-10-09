const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
for (const F of [0.5, 1, 2]) for (const pre of [0, 5, 10]) for (const droop of [0.5, 1]) {
  const o = { arm: {mode:'none'}, rings: [], nose: { s: 40, phi: 40, rc: 12, k: 100, preload: pre, cmd:[0,0,0] }, tail: { dx: 160, wireL: 350, kb: 0.15, pre: 3, wireCmd:[0,0], yawCmd: 0 }, kWire: 200, umbilical:{F, droop} };
  const m = FR.build(o); const r = m.solve(new Float64Array(m.n), {maxIter: 200});
  const cone = m.noseEl, c = m.bodyPoint(r.x, cone.local), rel = M.sub(c, cone.a), rho = Math.hypot(rel[0], rel[1]);
  console.log('F', F, 'preload', pre, 'droop', droop, 'conv', r.converged, 'gnorm', r.gnorm.toFixed(2), 'lateral climb', rho.toFixed(1), 'mm', 'u', Array.from(r.x.slice(0,3)).map(v=>v.toFixed(1)).join(','));
}
