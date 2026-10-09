// Where do the gun's parts sit, at the reference scene's opening pose, relative to the tube rim plane?
// This decides what a table top flush with the rim can and cannot touch. All gun geometry is the kit's
// ILLUSTRATIVE proxy (manual envelope 253 x 143 x 34 mm; pitch, grip, clearance are proxy values).
// Run: node explorers/room/calc/opening-pose-geometry.mjs
import { world, worldDir, ANCHORS, RIM_Z, JOINT_Z, RI, RO, fmt, sub, len, unit, dot3 } from './pose.mjs';

const roll = 45, hole = 30, vert = -15;   // reference scene opening pose (illustrative)
console.log('opening pose dials: roll', roll, 'hole', hole, 'vertical', vert);
console.log('rim plane z =', RIM_Z.toFixed(2), ' joint z =', JOINT_Z.toFixed(2), ' RI', RI.toFixed(2), 'RO', RO.toFixed(2));
for (const k of Object.keys(ANCHORS)) {
  const w = world(ANCHORS[k], roll, hole, vert);
  console.log(k.padEnd(12), fmt(w), ' above rim plane', (w[2] - RIM_Z).toFixed(1), ' plan radius from tube axis', Math.hypot(w[0], w[1]).toFixed(1));
}
const beam = unit(worldDir([0, 0, -1], roll, hole, vert));
console.log('beam dir (nozzle -> dot)', fmt(beam, 3), ' angle from vertical', (Math.acos(-beam[2]) * 180 / Math.PI).toFixed(1), 'deg');
const axis = unit(worldDir([0, 0, 1], roll, hole, vert));
console.log('gun barrel axis (toward back)', fmt(axis, 3), ' elevation above horizontal', (Math.asin(axis[2]) * 180 / Math.PI).toFixed(1), 'deg');

// how far above the rim plane is the barrel axis when it is 50 / 100 / 150 mm horizontally away from the dot?
const nz = world(ANCHORS.nozzleTip, roll, hole, vert);
console.log('\nbarrel axis height above rim plane vs plan distance from the nozzle tip (barrel line only, illustrative)');
for (const s of [0, 25, 50, 75, 100, 125]) {
  const t = s / Math.hypot(axis[0], axis[1]);
  const p = [nz[0] + axis[0] * t, nz[1] + axis[1] * t, nz[2] + axis[2] * t];
  console.log('  plan', String(s).padStart(3), 'mm   z above rim', (p[2] - RIM_Z).toFixed(1), '  radius from tube axis', Math.hypot(p[0], p[1]).toFixed(1));
}

// Sweep the three dials over a plausible neighbourhood and report the extremes of nozzle-tip height above the rim
// and the lowest point of the housing box corners. Decides whether a table flush with the rim could ever be hit.
let minTip = 1e9, maxTip = -1e9, minHousing = 1e9;
for (let r = 0; r <= 80; r += 10) for (let h = -25; h <= 95; h += 10) for (let v = -90; v <= 90; v += 15) {
  const tip = world(ANCHORS.nozzleTip, r, h, v);
  minTip = Math.min(minTip, tip[2] - RIM_Z); maxTip = Math.max(maxTip, tip[2] - RIM_Z);
  for (const sx of [-17, 17]) for (const sy of [-17, 17]) for (const z of [118, 253]) {
    const c = world([sx, sy, z], r, h, v);
    minHousing = Math.min(minHousing, c[2] - RIM_Z);
  }
}
console.log('\nover dial sweep roll 0-80, hole -25..95, vertical -90..90:');
console.log('  nozzle tip height above rim plane: min', minTip.toFixed(1), 'max', maxTip.toFixed(1));
console.log('  lowest housing-box corner above rim plane:', minHousing.toFixed(1));
