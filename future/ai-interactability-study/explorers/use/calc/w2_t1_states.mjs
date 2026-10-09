// Wave 2: travel-01 (tube travels) read as a sequence of states.
// What does the fixed gun's 5 mm tip-above-rim margin ask of the Z axis, and what does an end-of-bead escape by the work cost?
// Uses the kit's ILLUSTRATIVE proxy gun at the reference opening pose (pose.mjs). Nothing here is measured.
// Usage: node calc/w2_t1_states.mjs
import { world, ANCHORS, sub, mul, unit, norm, fmt, DEG, RI, RO, RIM_Z } from './pose.mjs';

const DIALS = [45, 30, -15];
const W = l => world(l, ...DIALS);
const nozzle = W(ANCHORS.nozzleTip), dotW = W(ANCHORS.dot);
const beam = unit(sub(dotW, nozzle));            // nozzle -> dot
const vert = -beam[2];                            // 0.712: vertical component of the beam axis
console.log('nozzle', fmt(nozzle), ' rim z', RIM_Z.toFixed(1), ' tip above rim', (nozzle[2] - RIM_Z).toFixed(1), 'mm');
console.log('beam vertical component', vert.toFixed(3), ' angle from vertical', (Math.acos(vert) / DEG).toFixed(1), 'deg');

// 1. Z axis range against the swap margin.
const margin = nozzle[2] - RIM_Z;                 // 5.0 mm nominal
console.log('\n1. Shuttle margin: tip is', margin.toFixed(1), 'mm above the rim plane at nominal Z.');
for (const zTrim of [-6, -3, 0, 3, 6]) {
  for (const spread of [0, 1, 2, 4]) {
    const h = margin - spread - zTrim;
    if (spread === 2) console.log(`   fine Z left at ${zTrim >= 0 ? '+' : ''}${zTrim} mm, tube ${spread} mm taller than nominal -> tip above rim ${h.toFixed(1)} mm ${h < 0 ? '  COLLIDES on a horizontal shuttle' : (h < 2 ? '  (under 2 mm: marginal)' : '')}`);
  }
}
console.log('   Z fine range +/-6 mm exceeds the 5.0 mm margin: the last weld can leave Z where the next shuttle hits the nozzle.');
console.log('   Measured in travel-01\'s own scene (scenes/travel-01-tube-travels, z and shut controls, shuttle 20 mm): its rim badge is off at z = +1 and on from z = +2, because the barrel behind the tip is nearer the rim ring than the tip is;');
console.log('   so 8 mm of the 12 mm fine range (-6 to +1) is shuttle-safe, and the tip-only figure below (4 mm) is optimistic.');
console.log('   Z must be at or below', (margin - 1).toFixed(1), 'mm (1 mm clear) minus the tube spread before any shuttle: a state interlock, or a drop tier.');

// 2. Escape by the work: dropping the work by h gives a standoff growth of h * vert along the beam.
console.log('\n2. Escape along the beam by dropping the work vertically:');
for (const E of [5, 10, 20, 30, 40]) {
  const h = E / vert;
  const vs = [60, 100];
  console.log(`   ${E} mm of standoff growth along the beam needs ${h.toFixed(1)} mm of Z drop;`, vs.map(v => `${(h / v).toFixed(2)} s at ${v} mm/s (${(8 * h / v).toFixed(1)} mm of seam at 8 mm/s)`).join('; '));
}
console.log('   the Z fine range (+/-6 mm) gives at most', (12 * vert).toFixed(1), 'mm of standoff growth if the whole range is used (trim at +6, drop to -6)');
console.log('   the gun moving instead: each mm along the beam is 1 mm; nozzle rises', vert.toFixed(3), 'mm per mm');

// 3. Two-tier Z: the drop tier carries the trim tier. Which error is which.
const seamH = 232;        // seam height above the rotator feet, travel notebook [derived from repo numbers]
for (const tilt of [0.05, 0.1, 0.3]) console.log(`\n3. layer tilt ${tilt} deg at ${seamH} mm -> ${(seamH * Math.tan(tilt * DEG)).toFixed(2)} mm at the dot`);
console.log('   the drop tier lands on a hard stop, so what matters is its repeatability at the stop, not its straightness over the travel;');
console.log('   the fine tier keeps its own short travel and sits on top of it (travel-01\'s own stack rule: long axes at the bottom).');
