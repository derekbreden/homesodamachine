// Numbers behind room-01 (table opening). Run: node explorers/room/calc/table-opening-numbers.mjs
// Everything about the gun (mass, umbilical pull) is [unknown]; the ranges below are [illustrative].
import { RI, RO, RIM_Z, JOINT_Z } from './pose.mjs';

console.log('== 1. What one millimetre of gun motion does at the station (seam circle r = ' + RI.toFixed(2) + ' mm) [derived]');
for (const s of [0.5, 1, 2, 5, 10]) {
  const ang = (s / RI) * 180 / Math.PI, rad = s * s / (2 * RI);
  console.log(`  tangent slide ${String(s).padStart(4)} mm -> approach turns ${ang.toFixed(2)} deg in plan, radial miss of the seam ${rad.toFixed(3)} mm`);
}
console.log('  radial (X) and vertical (Z) moves are 1:1 with the dot; only the tangent slide (Y) is an angle in disguise.');

console.log('\n== 2. What the hole in the table does and does not shrink');
const tube = 2 * RO;
for (const holeD of [140, 150, 160, 175, 200]) {
  const clr = (holeD - tube) / 2;
  console.log(`  hole D ${holeD} mm around tube D ${tube.toFixed(1)}: the tube axis can sit anywhere within +/-${clr.toFixed(1)} mm of the hole centre (loose fit)`);
}
console.log('  a loose hole is about as good as a hand-placed rotator; a fitted collar (see room-01 notes) makes it +/-0.2 mm. The reliable shrink is Z: the rim is a table-plane datum, and everything the gun structure needs stands 40 mm, not 270 mm, above its rails.');

console.log('\n== 3. Cantilever post height vs deflection per newton (illustrative section values, catalog range, unchecked)');
const E = 69e3;   // N/mm^2, 6063 aluminium (typical)
const sections = { '2020 slot profile (I ~ 0.7 cm^4)': 7.0e3, '3030 slot profile (I ~ 3 cm^4)': 3.0e4, '40x40x3 square tube (I ~ 9.5 cm^4)': 9.5e4 };
const hs = [{ h: 270, note: 'bench, joint 232 mm up: rail-to-shell-lug about 270' }, { h: 120, note: 'half-height stub' }, { h: 40, note: 'table opening: rail to shell riser about 40' }];
for (const [name, I] of Object.entries(sections)) {
  const row = hs.map(o => `${o.h} mm: ${(o.h ** 3 / (3 * E * I) * 1000).toFixed(3)} um/N`).join('   ');
  console.log('  ' + name.padEnd(38) + row);
}
console.log('  so a 2 N umbilical tug (illustrative) moves a bare 2020 post 270 mm tall by about 0.03 mm and a 40 mm one by nothing measurable;');
console.log('  a 20 N stuck-wire yank moves the tall post about 0.27 mm. The pit is a simplifier and a stiffness margin, not a fix for something broken.');

console.log('\n== 4. Gun shell attachment heights above the rim plane at the opening pose (from opening-pose-geometry.mjs) [derived, proxy]');
console.log('  nozzle tip +5 mm; barrel mid +60; collar +83; housing top +143; housing back +185; grip base +133 (plan radius 234).');
console.log('  A low carriage (top of riser +40 to +90 above the table) can hold the shell only at the barrel or collar; everything above hangs off it as a cantilever.');

console.log('\n== 5. Tube seat variation the shelf must absorb [unknown magnitude; illustrative +/-3 mm]');
for (const v of [0.5, 1, 2, 3]) console.log(`  plate ${v} mm deeper than nominal -> the dot ends up ${v} mm above the plate face unless the shelf raises the tube ${v} mm (or the gun drops ${v} mm). If the only free axis were a slide along the beam (about 45 deg from vertical in the opening pose) it would take ${(v / Math.cos(45 * Math.PI / 180)).toFixed(2)} mm of slide, and the slide also moves the dot radially.`);
console.log('  rim flush with the table is a datum for the rim, not for the corner: rim-to-plate depth varies with each plate seat, so the shelf is still needed per tube.');
