// 01 - where the gun's parts are in the reference opening pose, and how far each candidate pivot is from the dot.
// Gun geometry = the kit's ILLUSTRATIVE proxy. Dot = seam joint by construction of the dials.
// Run: node explorers/travel/calc/01-pose-and-levers.mjs
import { ANCHORS, OPENING, world, sub, norm, fmt, JOINT, RIM_Z, unit, cross, dot3, DEG } from './lib.mjs';

const { roll, holeDial, vertical } = OPENING;
console.log(`Opening pose (illustrative): roll ${roll}, hole dial ${holeDial}, vertical ${vertical}`);
console.log(`Joint J = (${JOINT.map(v => fmt(v)).join(', ')})  rim z = ${fmt(RIM_Z)}  (rim is ${fmt(RIM_Z - JOINT[2])} above the joint)`);
console.log('\nanchor            world x,y,z                      distance to dot   height over rim');
const dotW = world(ANCHORS.dot, roll, holeDial, vertical);
for (const [name, loc] of Object.entries(ANCHORS)) {
  const w = world(loc, roll, holeDial, vertical);
  console.log(name.padEnd(16), w.map(v => fmt(v, 1).padStart(8)).join(' '), '   ', fmt(norm(sub(w, dotW)), 1).padStart(7), '       ', fmt(w[2] - RIM_Z, 1).padStart(7));
}
// beam direction and angle from vertical
const tip = world(ANCHORS.nozzleTip, roll, holeDial, vertical);
const beam = unit(sub(dotW, tip));
console.log('\nbeam dir (nozzle -> dot):', beam.map(v => fmt(v, 3)).join(', '), ' angle from vertical:', fmt(Math.acos(-beam[2]) / DEG, 1), 'deg');
console.log('nozzle tip inside the bore? radial distance of tip from tube axis:', fmt(Math.hypot(tip[0], tip[1]), 1), ' (bore radius 61.85)');
// barrel axis in plan
const back = world(ANCHORS.housingBack, roll, holeDial, vertical);
const ax = unit(sub(back, tip));
console.log('barrel axis (tip -> back):', ax.map(v => fmt(v, 3)).join(', '), ' plan azimuth of the barrel (deg from +Y):', fmt(Math.atan2(ax[0], ax[1]) / DEG, 1));

// lever from candidate pivots to dot: 1 deg of rotation about a pivot P (axis perpendicular to the lever) moves the dot L*1deg
console.log('\nLever arm from each candidate pivot to the dot (opening pose) and dot travel per degree, per 0.01 deg');
for (const name of ['nozzleTip', 'barrelMid', 'collar', 'housingTop', 'housingBack', 'gripTop', 'gripMid', 'gripBase']) {
  const P = world(ANCHORS[name], roll, holeDial, vertical);
  const L = norm(sub(dotW, P));
  console.log(name.padEnd(12), 'lever', fmt(L, 0).padStart(5), 'mm   per deg', fmt(L * DEG, 2).padStart(6), 'mm   per 0.01 deg', fmt(L * DEG * 0.01, 3).padStart(6), 'mm');
}
