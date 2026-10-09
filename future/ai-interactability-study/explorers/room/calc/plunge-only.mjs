// plunge-only.mjs - can one long plunge along the barrel axis do the job of use-02's swing plus its 46 mm plunge?
// The gun is the kit proxy at the reference opening pose (ILLUSTRATIVE, not measured). The swap volume (radius 95, from z -20 to
// 65 mm above the rim) is use-02's own illustrative volume: the space the tube must lift through. Sample points of the gun
// proxy are use-02's (scene use-02-swing-head, SAMP), so the two analyses use the same drawn gun.
// Run: node explorers/room/calc/plunge-only.mjs
import { world, worldDir, ANCHORS, RIM_Z, JOINT_Z, RI, RO, unit, fmt } from './pose.mjs';

const roll = 45, hole = 30, vert = -15, CAP = 152.4;
const axisUp = unit(worldDir([0, 0, 1], roll, hole, vert));      // toward the back of the gun (retract direction)
const SWAP = { r: 95, z0: -20, z1: RIM_Z + 25 + 40 };            // use-02 default
const gunSamples = (() => {
  const s = [];
  const cyl = (z0, z1, r0, r1, n) => { for (let i = 0; i <= n; i++) { const t = i / n; s.push({ p: [0, 0, z0 + (z1 - z0) * t], r: r0 + (r1 - r0) * t }); } };
  cyl(0, 23, 2.2, 5, 4); cyl(23, 54, 8.5, 8.5, 4); cyl(54, 100, 5.5, 5.5, 6); cyl(100, 118, 12, 12, 3);
  [-17, 17].forEach(x => [-17, 17].forEach(y => [118, 185.5, 253].forEach(z => s.push({ p: [x, y, z], r: 0 }))));
  for (let i = 0; i <= 8; i++) { const t = i / 8; s.push({ p: [0, -25 - 86 * t, 172 + 60 * t], r: 15 }); }
  s.push({ p: [0, -118, 237], r: 6 });
  return s;
})();
const wpt = (lp, p) => { const w = world(lp, roll, hole, vert); return [w[0] + axisUp[0] * p, w[1] + axisUp[1] * p, w[2] + axisUp[2] * p]; };
const distTube = q => {   // signed distance to wall (annulus RI..RO up to the rim) and plate (disc inside RI, top at CAP, 6.35 thick)
  const rho = Math.hypot(q[0], q[1]);
  const inWall = rho > RI && rho < RO && q[2] > 0 && q[2] < RIM_Z, inPlate = rho < RI && q[2] > CAP - 6.35 - 12 && q[2] < CAP - 6.35;
  const dWall = Math.hypot(Math.max(0, RI - rho, rho - RO), Math.max(0, -q[2], q[2] - RIM_Z));
  const dPlate = Math.hypot(Math.max(0, rho - RI), Math.max(0, JOINT_Z - 6.35 - 12 - q[2], q[2] - (JOINT_Z)));
  return Math.min(inWall ? -1 : dWall, inPlate ? -1 : dPlate);
};
const distSwap = q => {
  const rho = Math.hypot(q[0], q[1]), dr = rho - SWAP.r, dz = Math.max(SWAP.z0 - q[2], q[2] - SWAP.z1);
  return dr < 0 && dz < 0 ? Math.max(dr, dz) : Math.hypot(Math.max(0, dr), Math.max(0, dz));
};
function clearances(p) {
  let mt = Infinity, ms = Infinity, whichS = '';
  gunSamples.forEach((o, i) => { const q = wpt(o.p, p); const dt = distTube(q) - o.r, ds = distSwap(q) - o.r; mt = Math.min(mt, dt); if (ds < ms) { ms = ds; whichS = i; } });
  return { tube: mt, swap: ms, idx: whichS };
}
// a fork plate: disc of radius rr centred on the barrel axis at gun-local z = zf, normal to the axis; sample its rim
function forkClear(zf, rr) {
  const c = world([0, 0, zf], roll, hole, vert);
  // two in-plane axes: gun local x and y directions
  const ex = worldDir([1, 0, 0], roll, hole, vert), ey = worldDir([0, 1, 0], roll, hole, vert);
  let m = Infinity;
  for (let i = 0; i < 48; i++) { const a = i / 48 * 2 * Math.PI; const q = [0, 1, 2].map(k => c[k] + rr * (Math.cos(a) * ex[k] + Math.sin(a) * ey[k])); m = Math.min(m, distSwap(q)); }
  return m;
}

console.log('retract direction (toward the back of the gun)', fmt(axisUp, 3), ' elevation', (Math.asin(axisUp[2]) * 180 / Math.PI).toFixed(1), 'deg');
const nz0 = world(ANCHORS.nozzleTip, roll, hole, vert);
console.log('nozzle tip at seat: world', fmt(nz0), ' above rim', (nz0[2] - RIM_Z).toFixed(1), '\n');
console.log('  p mm | nozzle above rim | nozzle plan (x, y) | gun to tube wall/plate | gun to swap volume | grip base above rim');
for (const p of [0, 20, 40, 60, 80, 100, 120, 130, 150, 175, 200]) {
  const c = clearances(p), nz = wpt(ANCHORS.nozzleTip, p), gb = wpt(ANCHORS.gripBase, p);
  console.log(String(p).padStart(5), '|', (nz[2] - RIM_Z).toFixed(1).padStart(10), '      |', (nz[0].toFixed(0) + ', ' + nz[1].toFixed(0)).padStart(15), '   |', c.tube.toFixed(1).padStart(10), '            |', c.swap.toFixed(1).padStart(8), '           |', (gb[2] - RIM_Z).toFixed(0).padStart(6));
}
let firstClear = null;
for (let p = 0; p <= 300; p += 1) { if (clearances(p).swap >= 0 && clearances(p + 10).swap >= 0) { firstClear = p; break; } }
console.log('\nsmallest plunge that leaves the gun proxy outside use-02\'s illustrative swap volume:', firstClear, 'mm  (nozzle then', (wpt(ANCHORS.nozzleTip, firstClear)[2] - RIM_Z).toFixed(0), 'mm above the rim)');
console.log('for comparison, use-02 retracts 40 mm, then swings 65-150 mm at the nozzle.\n');

console.log('the seat plate stays where it is. Its clearance to the swap volume (negative = intrudes) by seat position and circle:');
console.log('  seat plane at gun-local z | fork radius 44 (Rc 30) | fork radius 59 (Rc 45)');
for (const zf of [92, 100, 108, 122, 138, 152]) console.log('  ', String(zf).padStart(8), '            |', forkClear(zf, 44).toFixed(1).padStart(10), '            |', forkClear(zf, 59).toFixed(1).padStart(10));
console.log('\nA plunge-only head needs the seat to be a ring (the gun retracts through it), so the plate is a disc with a hole, not use-02\'s open fork.');
