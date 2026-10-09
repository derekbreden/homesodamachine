// Branch 01b: a spherical collar resting in a cone seat near the nozzle; the tail is a bridle (two wires + a bungee pair).
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function solve(o, x0) { const m = FR.build(o); const r = m.solve(x0 || new Float64Array(m.n), {maxIter: 80}); return { m, r }; }
const mk = (s, extra) => Object.assign({ arm: {mode:'none'}, rings: [], nose: { s, phi: 40, rc: 12, k: 100, preload: 0, cmd:[0,0,0] }, tail: { dx: 60, wireL: 350, kb: 0.15, pre: 3, wireCmd: 0, yawCmd: 0 }, kWire: 200 }, extra || {});
function report(label, o) {
  const b = solve(o); const x = b.r.x;
  if (!b.r.converged) { console.log(label.padEnd(40), 'NO EQUILIBRIUM', b.r.gnorm.toFixed(2)); return null; }
  const dc = b.m.dotCompliance(x);
  const cone = b.m.noseEl; const c = b.m.bodyPoint(x, cone.local); const rel = M.sub(c, cone.a); const h = rel[2], rho = Math.hypot(rel[0], rel[1]);
  const d = h*cone.sinPhi - rho*cone.cosPhi;
  const T = b.m.tailEls.wires.map(w => b.m.springForce(x, w).T.toFixed(1));
  console.log(label.padEnd(36), 'u', Array.from(x.slice(0,3)).map(v=>v.toFixed(2)).join(','), 'rot', [x[3],x[4],x[5]].map(v=>(v/FS.S*180/Math.PI).toFixed(2)).join(','), '| mm/N', [0,1,2].map(i=>dc.C[i][i].toFixed(2)).join(','), '| seat pen', (cone.rc - d).toFixed(2), 'lat', rho.toFixed(2), '| tail wires', T.join(','), 'free', dc.free);
  return b;
}
for (const s of [16, 40, 70, 110]) report('nose station ' + s, mk(s));
for (const P of [0, 3, 6]) report('nose 40 preload ' + P + ' N', mk(40, { nose: {s:40, phi:40, rc:12, k:100, preload:P, cmd:[0,0,0]} }));
for (const F of [0, 2, 5]) report('nose 40 umbilical ' + F + ' N', mk(40, { umbilical: {F, droop:0.5} }));
