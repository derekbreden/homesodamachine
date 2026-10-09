// orientation-family.mjs - the work tipped about the seam's tangent line through the dot by psi, the gun kept at the reference
// pose relative to the tube (roll 45, hole dial 30, vertical -15; kit proxy, ILLUSTRATIVE). psi = 0 is today's vertical tube;
// psi > 0 leans the tube toward the station (the station moves to the low side of the rim circle); psi = 90 is a horizontal
// tube with the station at the bottom (6 o'clock) and its mouth toward +X; psi < 0 leans the other way; psi = 180 is inverted.
// What changes with psi is the direction of gravity in the work's frame, so: what gravity does to the pool, the gun's weight
// lever about the dot, where the plume rises relative to the nozzle, how deep a pocket of argon stays, and how the cable leaves.
// [derived] from the kit's proxy geometry + 1.47 kg gun (illustrative), centre of mass local (0,-23,181) (illustrative).
// Run: node explorers/room/calc/orientation-family.mjs
import { world, JOINT, RI, RO, RIM_Z, JOINT_Z, GRIP_BASE, ROLL_AXIS } from './pose.mjs';
const DEG = Math.PI / 180;
export const ATTITUDES = { A: { roll: 45, hole: 30, vert: -15 }, B: { roll: 0, hole: 35, vert: -90 }, B2: { roll: 0, hole: 95, vert: 90 } };   // A = reference opening pose; B, B2 = travel's radial-plane attitudes (no wire on the gun)
let dl = ATTITUDES.A;
const rotY = (v, psiDeg) => { const c = Math.cos(psiDeg * DEG), s = Math.sin(psiDeg * DEG); return [v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c]; };   // about +Y, right-handed
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], len = a => Math.hypot(...a), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const unit = a => { const l = len(a); return a.map(v => v / l); };
const G = 9.81, MASS = 1.47, COM_LOCAL = [0, -23, 181], TUBE_MASS = 1.4;   // kg [illustrative; the rotating mass 1.40 kg first closure is [repo]]
const dotW = JOINT;

export function state(psi, att = 'A') {
  dl = ATTITUDES[att];
  const P = local => rotY(sub(world(local, dl.roll, dl.hole, dl.vert), dotW), psi);        // gun-local -> world offset from the dot at tilt psi
  const tip = P([0, 0, 0]), back = unit(sub(P([0, 0, 253]), tip)), com = P(COM_LOCAL), grip = P(GRIP_BASE);
  const exitDir = unit(sub(grip, P([0, 0, -16])));                                            // the cable leaves along the roll line, away from the dot
  const a = rotY([0, 0, 1], psi), s = rotY([1, 0, 0], psi);                                    // tube axis (out of the mouth), station outward normal
  const angVert = Math.acos(Math.min(1, Math.max(-1, back[2]))) / DEG;                        // barrel angle from vertical
  const comHoriz = Math.hypot(com[0], com[1]);                                                 // horizontal lever of the gun's weight about the dot
  // pool: gravity resolved on the plate (pressing toward the plate = -a.g) and on the wall (pressing toward the wall = s.g)
  const g = [0, 0, -1], toPlate = -dot(a, g), toWall = dot(s, g);
  // argon: lowest point of the rim circle relative to the station corner (world z), at the station side the pond depth is limited by it
  let lowRim = 1e9; for (let k = 0; k < 720; k++) { const t = k * Math.PI / 360, p = rotY([RI * Math.cos(t) - RI, RI * Math.sin(t), RIM_Z - JOINT_Z], psi); lowRim = Math.min(lowRim, p[2]); }
  const pond = Math.max(0, lowRim - 0);                                                        // depth of pond at the station (the station is the corner, z = 0)
  // where does the plume line (vertical through the dot) pass relative to the nozzle tip?
  const plumeOffset = Math.hypot(tip[0], tip[1]);                                              // nozzle tip's horizontal offset from the plume line, mm
  const cableUp = Math.asin(exitDir[2]) / DEG;                                                 // cable exit elevation above horizontal, degrees
  const tubeMoment = TUBE_MASS * G * Math.abs(Math.sin(psi * DEG)) * 0.1;                      // rough: tube weight component across the axis, N (x 0.1 shown as N below)
  return { psi, angVert, elev: 90 - angVert, comHoriz, momentNm: MASS * G * comHoriz / 1000, toPlate, toWall, pond, plumeOffset, cableUp, tubeSide: TUBE_MASS * G * Math.abs(Math.sin(psi * DEG)), a, s, back, tip, com, grip, exitDir };
}
if (process.argv[1] && process.argv[1].endsWith('orientation-family.mjs')) {
  console.log('psi  barrel from vertical | gun weight lever (mm), moment (N m) | gravity: toward plate / toward wall | argon pond at the station (mm) | nozzle tip off the plume line (mm) | cable exit elevation | tube weight across the axis (N)');
  for (const psi of [-90, -45, -30, 0, 15, 30, 32.5, 45, 60, 75, 90, 120, 135, 180]) {
    const r = state(psi);
    console.log(String(psi).padStart(5), '  ', r.angVert.toFixed(1).padStart(6), '°  |', r.comHoriz.toFixed(0).padStart(4), 'mm', r.momentNm.toFixed(2).padStart(5), 'N m |', r.toPlate.toFixed(2).padStart(5), '/', r.toWall.toFixed(2).padStart(5), '|', r.pond.toFixed(1).padStart(5), '|', r.plumeOffset.toFixed(1).padStart(5), '|', r.cableUp.toFixed(0).padStart(4), '° |', r.tubeSide.toFixed(1));
  }
  // where is the barrel closest to plumb (tilt about the tangent only)?
  let best = { angVert: 999 }; for (let psi = -90; psi <= 180; psi += 0.1) { const r = state(psi); if (r.angVert < best.angVert) best = r; }
  console.log('closest to plumb about the tangent axis: psi =', best.psi.toFixed(1), '° -> barrel', best.angVert.toFixed(1), '° from vertical, lever', best.comHoriz.toFixed(0), 'mm, moment', best.momentNm.toFixed(2), 'N m');
  // the tilt about ANY horizontal axis that makes the barrel exactly plumb
  const b0 = unit(sub(world([0, 0, 253], dl.roll, dl.hole, dl.vert), world([0, 0, 0], dl.roll, dl.hole, dl.vert)));
  console.log('reference barrel back-direction in the seam frame:', b0.map(v => v.toFixed(3)).join(', '), ' -> elevation', (Math.asin(b0[2]) / DEG).toFixed(1), '° ; out of the section plane (tangent component):', (Math.asin(-b0[1]) / DEG).toFixed(1), '°');
  console.log('for scale: reference (psi 0) lever', state(0).comHoriz.toFixed(0), 'mm, moment', state(0).momentNm.toFixed(2), 'N m');
}
if (process.argv[1] && process.argv[1].endsWith('orientation-family.mjs')) {
  console.log('\nThe same table for the two radial-plane attitudes of travel-16 (no wire on the gun): B grip out, B2 grip up.');
  for (const att of ['B', 'B2']) {
    console.log('attitude', att, 'psi | barrel from vertical | gun weight lever mm, moment N m | cable exit elevation | nozzle tip off the plume line mm');
    for (const psi of [0, 15, 30, 45, 60]) { const r = state(psi, att); console.log('   ', String(psi).padStart(3), r.angVert.toFixed(1).padStart(6), '°  ', r.comHoriz.toFixed(0).padStart(4), 'mm', r.momentNm.toFixed(2).padStart(5), 'N m ', r.cableUp.toFixed(0).padStart(4), '° ', r.plumeOffset.toFixed(1).padStart(5)); }
    let best = { angVert: 999 }; for (let psi = -90; psi <= 180; psi += 0.1) { const r = state(psi, att); if (r.angVert < best.angVert) best = r; }
    console.log('    closest to plumb: psi', best.psi.toFixed(1), '° ->', best.angVert.toFixed(1), '° from vertical, lever', best.comHoriz.toFixed(0), 'mm, moment', best.momentNm.toFixed(2), 'N m, cable exit elevation', best.cableUp.toFixed(0), '°, plume offset', best.plumeOffset.toFixed(1), 'mm, argon pond', best.pond.toFixed(1), 'mm');
  }
}
