// Numbers behind room-03 (wall port: the gun on a rod through a pivot in the enclosure wall).
// Geometry: the dot, the barrel axis, the pivot P and the tail T are collinear (the dot lies on the barrel axis, 16 mm
// ahead of the nozzle: kit proxy). The tail T is pushed by two actuators; the rod passes through P; the dot is D = P + (d+s) u
// with u = (P - T)/|P - T|.  Gun mass, centre of mass, umbilical pull are [unknown]; values marked [illustrative].
// Run: node explorers/room/calc/wall-port-lever.mjs
import { world, worldDir, ANCHORS, JOINT, add, sub, scl, dot3, len, unit, cross, fmt } from './pose.mjs';

const roll = 45, hole = 30, vert = -15;                   // reference opening pose [illustrative]
const b = unit(worldDir([0, 0, -1], roll, hole, vert));   // beam / barrel direction, nozzle -> dot
const D = JOINT.slice();
console.log('beam direction b =', fmt(b, 3), '   dot D =', fmt(D, 2));

// two unit vectors perpendicular to b (actuator directions)
let e1 = unit(cross([0, 0, 1], b)), e2 = unit(cross(b, e1));
console.log('tail actuator directions  e1 (roughly horizontal) =', fmt(e1, 3), '  e2 =', fmt(e2, 3));

function dotAfter(d, Lt, a1, a2, s = 0) {
  const P = sub(D, scl(b, d));
  const T0 = sub(P, scl(b, Lt));
  const T = add(add(T0, scl(e1, a1)), scl(e2, a2));
  const u = unit(sub(P, T));
  return { dot: add(P, scl(u, d + s)), u };
}

console.log('\n== 1. Dot motion per millimetre of tail actuator, and the angle it swings (exact vectors) [derived]');
console.log(' d = pivot to dot, Lt = pivot to tail actuator.  rho = d/Lt is the reduction (dot mm per actuator mm).');
console.log('   d     Lt    rho    dot move for 1 mm a1    for 10 mm a1     swing at 10 mm    a1 step for 0.01 mm dot');
for (const d of [300, 400, 500, 700]) for (const Lt of [400, 800, 1500]) {
  const base = dotAfter(d, Lt, 0, 0).dot;
  const m1 = dotAfter(d, Lt, 1, 0).dot, m10 = dotAfter(d, Lt, 10, 0);
  const swing = Math.acos(Math.min(1, dot3(m10.u, b))) * 180 / Math.PI;
  console.log(String(d).padStart(5), String(Lt).padStart(6), (d / Lt).toFixed(2).padStart(7), (len(sub(m1, base))).toFixed(3).padStart(14) + ' mm', (len(sub(m10.dot, base))).toFixed(2).padStart(14) + ' mm', swing.toFixed(2).padStart(12) + ' deg', ((0.01 / (d / Lt)) * 1000).toFixed(1).padStart(14) + ' um');
}

console.log('\n== 2. Pivot error is amplified, actuator compliance is reduced [derived]');
console.log('  If the ball moves by delta while the tail is held, the dot moves by delta*(1 + d/Lt).  If the actuators ride on the same plate as the ball, a plate slide moves the dot by exactly delta and the orientation stays put.');
for (const [d, Lt] of [[400, 800], [400, 1500], [600, 800]]) console.log(`  d ${d}, Lt ${Lt}: pivot clearance 0.05 mm -> dot ${(0.05 * (1 + d / Lt)).toFixed(3)} mm`);

console.log('\n== 3. Orientation drift when the dot is moved sideways by tilting only [derived]');
for (const d of [300, 400, 600]) console.log(`  d ${d}: +/-5 mm of dot travel = +/-${(Math.atan(5 / d) * 180 / Math.PI).toFixed(2)} deg; +/-10 mm = +/-${(Math.atan(10 / d) * 180 / Math.PI).toFixed(2)} deg; +/-20 mm = +/-${(Math.atan(20 / d) * 180 / Math.PI).toFixed(2)} deg`);
console.log('  (a slide of the pivot plate moves the dot with zero orientation change.)');

console.log('\n== 4. Loads at the tail actuator from forces on the gun side (moment balance about P) [illustrative forces, proxy geometry]');
// bending torque = component of (arm x F) perpendicular to the rod; the part along the rod is a roll torque, held by a roll lock.
const bend = (arm, F) => { const t = cross(arm, F); const a = dot3(t, b); return len(sub(t, scl(b, a))); };
const gripBaseW = world(ANCHORS.gripBase, roll, hole, vert);
for (const d of [300, 400, 500]) {
  const P = sub(D, scl(b, d));
  const arm = sub(gripBaseW, P);
  const axial = dot3(arm, b), off = len(sub(arm, scl(b, axial)));
  // worst direction of a 1 N force at the grip base: the one giving the largest bending torque = |arm_perp-to-force...| ; scan directions
  let worst = 0;
  for (let i = 0; i < 4000; i++) { const th = Math.acos(1 - 2 * Math.random()), ph = 2 * Math.PI * Math.random(); const F = [Math.sin(th) * Math.cos(ph), Math.sin(th) * Math.sin(ph), Math.cos(th)]; worst = Math.max(worst, bend(arm, F)); }
  const Lt = 800;
  console.log(`  d ${d}: grip base (umbilical exit) is ${axial.toFixed(0)} mm in front of P along the rod and ${off.toFixed(0)} mm off it; 1 N of pull in the worst direction gives ${(worst / 1000).toFixed(3)} N m of bending torque -> ${(worst / Lt).toFixed(2)} N at a tail ${Lt} mm out`);
}
console.log('  So a cable pull on the gun side reaches the actuators as roughly a fifth to a third of its size, and reaches the dot only through the actuators\' compliance times the reduction rho.');

console.log('\n== 5. Gravity: where the tail counterweight has to sit (moment balance about P) [illustrative masses, proxy centre of mass]');
// proxy masses along local z (kg) [illustrative]: barrel/nozzle 0.12 @ z60, housing 0.85 @ z185, grip 0.50 @ gripMid
const parts = [[0.12, [0, 0, 60]], [0.85, [0, 0, 185]], [0.50, ANCHORS.gripMid]];
const M = parts.reduce((s, p) => s + p[0], 0);
const comLocal = parts.reduce((s, p) => add(s, scl(p[1], p[0] / M)), [0, 0, 0]);
const comW = world(comLocal, roll, hole, vert);
console.log(`  proxy gun mass ${M.toFixed(2)} kg [illustrative: the real mass is unknown], centre of mass local ${fmt(comLocal, 0)} -> world ${fmt(comW, 0)}`);
for (const d of [300, 400, 500]) {
  const P = sub(D, scl(b, d));
  const arm = sub(comW, P);
  const axial = dot3(arm, b), off = len(sub(arm, scl(b, axial)));
  const tau = bend(arm, [0, 0, -M * 9.81]);           // N mm, pitch/yaw part
  for (const Lt of [800]) {
    const mcw = (M * 9.81 * 0 + tau) / (9.81 * Lt * Math.sqrt(1 - b[2] * b[2]));   // counterweight at the tail, same lever geometry
    console.log(`  d ${d}: CoM ${axial.toFixed(0)} mm in front of P and ${off.toFixed(0)} mm off the rod; gravity bending torque ${(tau / 1000).toFixed(2)} N m = ${(tau / Lt).toFixed(1)} N at a tail ${Lt} mm out if left uncounterweighted; a counterweight of about ${mcw.toFixed(2)} kg at ${Lt} mm (plus rod and cradle) zeroes it`);
  }
  console.log(`       load on the pivot: about ${((M + 0.4) * 9.81).toFixed(0)} N (gun + counterweight + rod, illustrative)`);
}

console.log('\n== 6. Insertion stroke needed to lift the tube out through the top (barrel must leave the column above the tube) [derived, opening pose]');
{
  const N0 = world(ANCHORS.nozzleTip, roll, hole, vert);
  const back = scl(b, -1);
  const colR = 63.5 + 8.5 + 5;     // tube OD + barrel radius + 5 mm, illustrative
  let first = null;
  for (let s = 0; s <= 400; s += 1) {
    const p = add(N0, scl(back, s));
    const rp = Math.hypot(p[0], p[1]);
    if (rp > colR && p[2] < 310 && first == null) first = s;
  }
  console.log(`  retracting along the barrel axis, the nozzle leaves the plan-radius-${colR.toFixed(0)} column after about ${first} mm of stroke (nozzle then ${(N0[2] + back[2] * first).toFixed(0)} mm high). Add margin: 150 to 200 mm of insertion stroke, or a hinged/lifting lid, for tube swaps.`);
}
