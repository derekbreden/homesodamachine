const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function solve(opts, x0) { const m = FR.build(opts); const r = m.solve(x0 || new Float64Array(m.n)); return { m, r }; }
const rings = (tipContact) => [ {id:'tip', at:'tip', s:40, contact:tipContact, axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', contact:'loop', axis:'x', kb:0.15, pre:3} ];
const spots = ['collar','housingTop','housingBack','gripMid','gripBase'];
for (const mode of ['rigid','point']) for (const spot of spots) {
  const base = solve({ arm: { mode, at: spot }, rings: rings('seat') });
  if (!base.r.converged) { console.log(mode.padEnd(6), spot.padEnd(11), 'no equilibrium'); continue; }
  const u0 = Array.from(base.r.x.slice(0,3));
  const gains = [0,1,2].map(ax => { const cmd=[0,0,0]; cmd[ax]=1; const s = solve({ arm: { mode, at: spot, cmd }, rings: rings('seat') }, base.r.x); return Array.from(s.r.x.slice(0,3)).map((v,i)=> v-u0[i]); });
  const dc = base.m.dotCompliance(base.r.x);
  console.log(mode.padEnd(6), spot.padEnd(11), 'u0', u0.map(v=>v.toFixed(2)).join(','), '| dot mm per arm mm  X:', gains[0].map(v=>v.toFixed(2)).join(','), ' Y:', gains[1].map(v=>v.toFixed(2)).join(','), ' Z:', gains[2].map(v=>v.toFixed(2)).join(','), '| compl r,t,z', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','));
}
