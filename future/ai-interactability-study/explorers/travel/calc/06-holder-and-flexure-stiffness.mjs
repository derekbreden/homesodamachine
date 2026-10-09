// 06 - how much does a steady sideways force move the dot? Stiffness is a physical constraint that software coordinates do not remove.
// The FORCE is [unknown] (gun mass, umbilical weight/stiffness, trigger force are unmeasured), so the table is per newton.
// Materials: handbook Young's moduli (steel 200 GPa, aluminium 69 GPa); PET-GF15 taken as ~5 GPa: ILLUSTRATIVE, not the project's measured value.
// Run: node explorers/travel/calc/06-holder-and-flexure-stiffness.mjs
import { fmt } from './lib.mjs';

const mats = [['steel', 200e3], ['aluminium', 69e3], ['PET-GF (illustrative)', 5e3]];    // MPa = N/mm^2
console.log('A. A locked holder that is a plain cantilever (round rod, diameter d, length L). Deflection per newton at the tip: L^3 / (3 E I)  [handbook beam formula]');
console.log('   Dot shift per newton of umbilical pull, assuming the force acts at the tip and the gun is rigid.\n');
console.log('material'.padEnd(24), 'd(mm)  L(mm)   k (N/mm)   dot shift per N (um)   force for 50 um (N)');
for (const [name, E] of mats) {
  for (const [d, L] of [[12, 150], [12, 300], [20, 300], [30, 300]]) {
    const I = Math.PI * Math.pow(d, 4) / 64, k = 3 * E * I / Math.pow(L, 3);
    console.log(name.padEnd(24), String(d).padStart(5), String(L).padStart(6), fmt(k, 1).padStart(10), fmt(1000 / k, 1).padStart(16), fmt(0.05 * k, 2).padStart(20));
  }
}
console.log('\nB. A locked friction joint (ball head) is not a beam: its stiffness is set by clamp friction. If a joint slips or creeps by an angle theta under a load, the dot moves L*theta.');
for (const th of [0.005, 0.02, 0.05, 0.1]) console.log('   ' + th + ' deg of creep at L = 250 mm -> ' + fmt(250 * th * Math.PI / 180, 3) + ' mm at the dot');

console.log('\nC. A parallelogram flexure follow stage (two parallel leaf springs of thickness t, width b, length l, modulus E): k = 2 E b t^3 / l^3 along the working direction; bending strain at a guided end deflection x is 3 t x / l^2.');
console.log('   Printed leaves (PETG-like E = 1.5 GPa, strain limit 1 percent: ILLUSTRATIVE) versus spring-steel shim leaves (E = 200 GPa, strain limit 0.2 percent: ILLUSTRATIVE).');
const cases = [['PETG-like', 1500, 0.01, 0.8, 20, 40], ['PETG-like', 1500, 0.01, 1.6, 20, 40], ['spring steel', 200e3, 0.002, 0.5, 20, 30], ['spring steel', 200e3, 0.002, 1.0, 20, 30]];
for (const [name, E, eps, t, b, l] of cases) {
  const k = 2 * E * b * Math.pow(t, 3) / Math.pow(l, 3), xmax = eps * l * l / (3 * t);
  console.log('   ' + name.padEnd(13) + ' t ' + t + ' b ' + b + ' l ' + l + ' : k = ' + fmt(k, 1) + ' N/mm, travel to the strain limit = ' + fmt(xmax, 2) + ' mm, dot shift per N = ' + fmt(1000 / k, 1) + ' um');
}
console.log('   A printed flexure carrying the GUN (where cable pull acts) moves hundreds of microns per newton; a spring-steel-leaf flexure of the same footprint moves a few microns per newton. The same printed flexure under the WORK (dead weight, no cable) sees no such force. An allocation argument, not a design.');

console.log('\nD. Speed check: the rotator turns the seam past the station at v = 5-15 mm/s [repo]; a follow stage only needs the runout rate: TIR/2 * v / r');
for (const v of [5, 8, 15]) console.log('   v ' + v + ' mm/s: 0.25 mm TIR -> ' + fmt(0.125 * v / 61.85 * 1000, 1) + ' um/s ; 0.30 mm face TIR -> ' + fmt(0.15 * v / 61.85 * 1000, 1) + ' um/s');
