// Numbers behind the "tried" entries of freedom-01: who is the master of each axis?
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const R = (tip, kb, axT, axB, base) => [ {id:'tip', at:'tip', s:40, contact:tip, axis:axT, kb, pre:3}, {id:'base', at:'base', contact:base||'loop', axis:axB, kb, pre:3} ];
function solve(o, x0) { const m = FR.build(o); const r = m.solve(x0 || new Float64Array(m.n)); return { m, r }; }
function row(label, o) {
  const b = solve(o); if (!b.r.converged) { console.log(label.padEnd(58), 'NO EQUILIBRIUM (gnorm ' + b.r.gnorm.toFixed(1) + ')'); return; }
  const u0 = Array.from(b.r.x.slice(0,3));
  const gains = [0,1,2].map(ax => { const cmd=[0,0,0]; cmd[ax]=1; const O = JSON.parse(JSON.stringify(o)); O.arm = Object.assign({}, O.arm||{}, {cmd}); const s = solve(O, b.r.x); return s.r.x[ax]-u0[ax]; });
  const dc = b.m.dotCompliance(b.r.x);
  const armF = b.m.armEl ? b.m.springForce(b.r.x, b.m.armEl).F : [0,0,0];
  console.log(label.padEnd(58), 'gain r,t,z', gains.map(v=>v.toFixed(2)).join(','), '| mm/N r,t,z', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','), '| arm Fz', armF[2].toFixed(1), 'N | free modes', dc.free);
}
console.log('--- vertical support type (rigid grip at housingTop, tip seat, base loop, bungees soft):');
for (const [name,k] of [['stiff wire k=200',200],['long bungee k=0.2',0.2],['constant-force balancer k=0.02',0.02]])
  row(name, { kWire:k, arm:{mode:'rigid',at:'housingTop'}, rings:R('seat',0.15,'y','x') });
console.log('--- no vertical support at all (carry 0): arm only');
row('carry 0', { carry:0, arm:{mode:'rigid',at:'housingTop'}, rings:R('seat',0.15,'y','x') });
console.log('--- bungee stiffness (rigid grip):');
for (const kb of [0.05,0.15,0.6,3]) row('kb '+kb, { arm:{mode:'rigid',at:'housingTop'}, rings:R('seat',kb,'y','x') });
console.log('--- tip ring contact with rigid grip at housing:');
row('tip loop (free slide)', { arm:{mode:'rigid',at:'housingTop'}, rings:R('loop',0.15,'y','x') });
row('tip seat', { arm:{mode:'rigid',at:'housingTop'}, rings:R('seat',0.15,'y','x') });
console.log('--- no arm:');
row('loop tip, loop base, no arm', { arm:{mode:'none'}, rings:R('loop',0.15,'y','x') });
row('seat tip, loop base, no arm', { arm:{mode:'none'}, rings:R('seat',0.15,'y','x') });
row('seat tip, cable-pickup base, no arm', { arm:{mode:'none'}, rings:R('seat',0.15,'y','x','cable') });
console.log('--- wire length effect on sway (seat tip, loop base, rigid grip):');
for (const L of [200,450,1000]) row('wire L '+L, { wireL:L, arm:{mode:'rigid',at:'housingTop'}, rings:R('seat',0.15,'y','x') });
console.log('--- point (ball-end) grip vs bungee axis choice:');
for (const [a,b] of [['x','x'],['y','y'],['y','x'],['x','y']]) row('point@housingBack bungees tip:'+a+' base:'+b, { arm:{mode:'point',at:'housingBack'}, rings:R('seat',0.15,a,b) });
