const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function mk(s, dx, over) { return Object.assign({ arm: {mode:'none'}, rings: [], nose: { s, phi: 40, rc: 12, k: 100, preload: 0, cmd:[0,0,0] }, tail: { dx, wireL: 350, kb: 0.15, pre: 3, wireCmd: [0,0], yawCmd: 0 }, kWire: 200, umbilical:{F:2,droop:0.5} }, over||{}); }
function solve(o, x0) { const m = FR.build(o); const r = m.solve(x0||new Float64Array(m.n), {maxIter: 200}); return {m,r}; }
for (const s of [16, 40, 70, 110]) {
  const dx = 160, base = solve(mk(s,dx)); if (!base.r.converged) { console.log('s', s, 'no eq'); continue; }
  const u0 = Array.from(base.r.x.slice(0,3)); const dc = base.m.dotCompliance(base.r.x);
  const acts = { cupX:o=>o.nose.cmd[0]=1, cupY:o=>o.nose.cmd[1]=1, cupZ:o=>o.nose.cmd[2]=1, wireA:o=>o.tail.wireCmd[0]=1, wireB:o=>o.tail.wireCmd[1]=1, bothWires:o=>{o.tail.wireCmd=[1,1];}, yaw:o=>o.tail.yawCmd=1 };
  const out = [];
  for (const k of Object.keys(acts)) { const o = mk(s,dx); acts[k](o); const r = solve(o, base.r.x); out.push(k + ' ' + (r.r.converged ? Array.from(r.r.x.slice(0,3)).map((v,i)=>(v-u0[i]).toFixed(2)).join(',') : 'NC')); }
  console.log('collar station', s, '| mm/N r,t,z', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','), '| dot mm per actuator mm:', out.join(' | '));
}
