// Directions at the weld station, kit proxy at the opening pose (ILLUSTRATIVE): beam, barrel axis, wire axis, and their angles.
import { world, sub, add, mul, unit, dot, cross, fmt, DEG } from './pose.mjs';
const W = l => world(l, 45, 30, -15);
const N0 = W([0, 0, 0]), D0 = W([0, 0, -16]);
const beam = unit(sub(D0, N0)), aBack = mul(beam, -1);
const wl = unit([0, -24.7, 103.1]);
const wOut = unit(sub(W([wl[0] * 10, wl[1] * 10, -16 + wl[2] * 10]), D0));    // from the dot toward the guide (the wire's own axis)
console.log('nozzle', fmt(N0), 'dot', fmt(D0));
console.log('beam  (nozzle->dot)', fmt(beam, 3), ' barrel axis back', fmt(aBack, 3));
console.log('wire axis (dot->guide)', fmt(wOut, 3));
const ang = (a, b) => Math.acos(Math.max(-1, Math.min(1, dot(a, b)))) / DEG;
console.log('angle barrel-back vs wire axis', ang(aBack, wOut).toFixed(1), ' vertical comps: barrel', aBack[2].toFixed(3), 'wire', wOut[2].toFixed(3));
const cand = { 'barrel axis (plunge)': aBack, 'wire axis': wOut, 'vertical': [0, 0, 1], 'radial out': [1, 0, 0], 'tangent -y': [0, -1, 0], 'tangent +y': [0, 1, 0] };
for (const [k, d] of Object.entries(cand)) {
  const along = dot(d, wOut), lat = Math.sqrt(Math.max(0, 1 - along * along));
  console.log(k.padEnd(22), 'dir', fmt(d, 3), '| angle to wire', ang(d, wOut).toFixed(1), '| recession along wire', along.toFixed(3), '| lateral', lat.toFixed(3), '| beam-standoff per mm', dot(d, aBack).toFixed(3), '| vertical', d[2].toFixed(3));
}
// distance of the nozzle tip to the rim circle for a straight-line escape along d
const RIM_Z = 152.4, RI = 61.85, RO = 63.5;
for (const [k, d] of Object.entries(cand)) {
  let minD = 1e9, at = 0;
  for (let s = 0; s <= 120; s += 2) {
    const p = add(N0, mul(d, s)); const rho = Math.hypot(p[0], p[1]);
    const dist = Math.hypot(Math.max(0, RI - rho, rho - RO), Math.max(0, p[2] - RIM_Z < 0 ? RIM_Z - p[2] : 0));
    // clearance to the wall body (annulus RI..RO, z 0..RIM): distance when inside the height range
    const dwall = p[2] <= RIM_Z ? Math.max(0, RI - rho, rho - RO) : Math.hypot(Math.max(0, RI - rho, rho - RO), p[2] - RIM_Z);
    if (dwall < minD) { minD = dwall; at = s; }
  }
  console.log(k.padEnd(22), 'nozzle min distance to the wall/rim along 0-120 mm of travel', minD.toFixed(1), 'at', at, 'mm');
}
