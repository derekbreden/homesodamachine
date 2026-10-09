// Derek's third ring: what does a third loop on the housing change? (freedom-01, round 8). ILLUSTRATIVE parameters (ringmodel.js defaults).
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const rings = (third, axis3) => { const r = [ {id:'tip', at:'tip', s:40, contact:'seat', axis:'y', kb:0.15, pre:3}, {id:'base', at:'base', d:20, contact:'loop', axis:'x', kb:0.15, pre:3} ]; if (third) r.push({id:'third', at:'housing', s:185, contact:'rubber', axis:axis3||'y', kb:0.15, pre:3}); return r; };
function solve(o, x0) { const m = FR.build(o); const r = m.solve(x0 || new Float64Array(m.n), {maxIter:80}); return {m, r}; }
function row(label, mode, at, third, axis3, kb) {
  const o = { arm:{mode, at}, rings: rings(third, axis3) }; if (kb) o.rings.forEach(r => r.kb = kb);
  const b = solve(o); if (!b.r.converged) { console.log(label.padEnd(58), 'NO EQUILIBRIUM'); return; }
  const u0 = Array.from(b.r.x.slice(0,3)), dc = b.m.dotCompliance(b.r.x);
  const gains = [0,1,2].map(ax => { const O = JSON.parse(JSON.stringify(o)); O.arm.cmd=[0,0,0]; O.arm.cmd[ax]=1; const s = solve(O, b.r.x); return s.r.x[ax]-u0[ax]; });
  const armF = b.m.springForce(b.r.x, b.m.armEl).F; const tilt = M.len([b.r.x[3],b.r.x[4],b.r.x[5]])/FS.S*180/Math.PI;
  console.log(label.padEnd(58), 'gain r,t,z', gains.map(v=>v.toFixed(2)).join(','), '| mm/N', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','), '| arm |F|', M.len(armF).toFixed(1), 'N | dot u', u0.map(v=>v.toFixed(1)).join(','), '| tilt', tilt.toFixed(1), 'deg');
}
console.log('--- ball-ended (point) grip at the housing back, seat tip, base loop:');
row('two loops', 'point', 'housingBack', false);
row('three loops (third: rubber loop on the housing, bungees Y)', 'point', 'housingBack', true, 'y');
row('three loops (third bungees X)', 'point', 'housingBack', true, 'x');
row('three loops, firm bungees (0.6 N/mm)', 'point', 'housingBack', true, 'y', 0.6);
console.log('--- rigid grip at the housing top:');
row('two loops', 'rigid', 'housingTop', false);
row('three loops', 'rigid', 'housingTop', true, 'y');
