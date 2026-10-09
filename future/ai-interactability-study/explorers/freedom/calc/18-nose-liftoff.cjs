const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const mk = (o) => Object.assign({ arm:{mode:'none'}, rings:[], kWire:200, umbilical:{F:2,droop:0.5}, nose:{s:70,phi:40,rc:12,k:100,preload:3,cmd:[0,0,0]}, tail:{dx:160,wireL:300,kb:0.15,pre:3,wireCmd:[0,0],yawCmd:0} }, o);
for (const droop of [0, 1]) for (const pre of [0, 6]) for (const F of [8, 12, 16, 24]) {
  const m=FR.build(mk({umbilical:{F,droop},nose:{s:70,phi:40,rc:12,k:100,preload:pre,cmd:[0,0,0]}})); const r=m.solve(new Float64Array(m.n),{maxIter:250});
  const el=m.noseEl,c=m.bodyPoint(r.x,el.local),rel=M.sub(c,el.a),rho=Math.hypot(rel[0],rel[1]); const pen=el.rc-(rel[2]*el.sinPhi-Math.hypot(rho,0.05)*el.cosPhi);
  const T=m.tailEls.wires.map(w=>m.springForce(r.x,w).T.toFixed(1));
  console.log('droop',droop,'preload',pre,'F',F,'conv',r.converged,'pen',pen.toFixed(3),'off-axis',rho.toFixed(2),'u',Array.from(r.x.slice(0,3)).map(v=>v.toFixed(2)).join(','),'T',T.join(','));
}
