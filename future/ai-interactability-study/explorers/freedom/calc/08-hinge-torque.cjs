// The two rings define a hinge line A-B (tip-ring point, base-ring point). How much gravity torque does the gun put on that hinge at the
// reference pose, and where would it swing to if nothing held it? Illustrative mass and COM (statics.js / ringmodel.js DEFAULTS).
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const pose = FS.dialsToPose(45, 30, -15);
const W = (m) => M.add(pose.origin, M.mv(pose.R, m));
const D = FR.DEFAULTS, LOC = FR.LOCAL;
for (const tipS of [10, 40, 100]) {
  const A = [0,0,tipS], B = LOC.cablePair;
  const els = [ {type:'pin', a:{local:A}, b:{world:W(A)}, k:1e3}, {type:'pin', a:{local:B}, b:{world:W(B)}, k:1e3}, {type:'gravity'} ];
  const m = FS.makeModel({ body: { mass: D.mass, com: D.com, ref: pose, dotLocal: LOC.dot }, nodes: [], elements: els });
  const x0 = new Float64Array(6); const g = m.grad(x0);
  // torque about the hinge = gradient in rotation about the hinge axis; project the rotation-gradient (torque/S about the dot ... the pins carry it) -> use the free-hinge solve
  const r = m.solve(x0, { maxIter: 80 });
  const axis = M.norm(M.sub(W(B), W(A)));
  const th = [r.x[3]/FS.S, r.x[4]/FS.S, r.x[5]/FS.S];
  const ang = M.dot(th, axis) * 180/Math.PI;
  const comW = W(D.com), rel = M.sub(comW, W(A)), perp = M.sub(rel, M.mul(axis, M.dot(rel, axis)));
  const horiz = Math.hypot(perp[0], perp[1]);   // horizontal lever of COM from the line, at the reference pose, for a torque about a horizontal-ish line
  const torque = FR.hingeBalance({rings:[{id:'tip',at:'tip',s:tipS,contact:'loop',axis:'y',kb:.15,pre:3},{id:'base',at:'base',contact:'loop',axis:'x',kb:.15,pre:3}]},0).offset;
  console.log('tip ring at', String(tipS).padStart(3), 'mm | COM distance from hinge line', torque.toFixed(1), 'mm | swing from the reference roll to gravity-neutral:', ang.toFixed(0), 'deg (about the hinge axis) | conv', r.converged);
}
