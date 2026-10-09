const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const rings = (tip,base) => [ {id:'tip', at:'tip', s:40, contact:tip, axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:base, axis:'x', kb:0.15, pre:3} ];
for (const f of [0, 0.5, 1]) for (const F of [0, 2]) {
  const hb = FR.hingeBalance({}, f);
  const o = { mass: hb.mass, com: hb.com, arm: {mode:'none'}, rings: rings('seat','loop'), umbilical: {F, droop:0.5} };
  const m = FR.build(o); const r = m.solve(new Float64Array(m.n)); const x = r.x;
  console.log('balance', f, 'umbilical', F, 'COM offset from hinge line', hb.offset.toFixed(1), 'mm; cw', (hb.cwMass*1000).toFixed(0), 'g | conv', r.converged, 'u', Array.from(x.slice(0,3)).map(v=>v.toFixed(1)).join(','), 'rot deg', [x[3],x[4],x[5]].map(v=>(v/FS.S*180/Math.PI).toFixed(1)).join(','));
}
