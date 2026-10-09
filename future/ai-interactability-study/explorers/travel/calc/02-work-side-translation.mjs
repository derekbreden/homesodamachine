// 02 - what a translation of the WORK (tube + rotator) does at the dot, gun held fixed.
// Seam = circle r = 61.85 mm [repo]. Along-seam translation is redundant (the rotator turns the seam through it).
// Run: node explorers/travel/calc/02-work-side-translation.mjs
import { INNER_RADIUS as r, DEG, fmt } from './lib.mjs';

console.log(`Seam radius r = ${fmt(r, 2)} mm [repo]`);
console.log('\nA: shift the tube along the gun tangent (y) by s, no other move. Dot leaves the seam circle radially; the seam normal turns by psi relative to the gun.');
console.log(' s(mm)   psi(deg)  radial error r*(1/cos psi -1)(mm)   resolution needed for 0.01 deg of psi (mm)');
for (const s of [0.1, 0.5, 1, 2, 3, 5, 10, 15]) {
  const psi = Math.atan2(s, r);
  const dr = Math.hypot(r, s) - r;         // dot is at distance hypot(r,s) from the (moved) axis: outside the seam circle
  console.log(fmt(s, 1).padStart(6), fmt(psi / DEG, 3).padStart(10), fmt(dr, 3).padStart(12), '                              ', fmt(0.01 * DEG * r, 4));
}
console.log('\nB: to turn the plan angle by psi with the dot kept ON the seam, move the axis on a circle of radius r about the dot:');
console.log(' psi(deg)  dx (radial, mm)  dy (tangent, mm)  travel ratio dy/psi (mm/deg)');
for (const psiDeg of [0.25, 0.5, 1, 2, 3, 5, 10, 20, 45]) {
  const p = psiDeg * DEG;
  console.log(fmt(psiDeg, 2).padStart(8), fmt(r * (1 - Math.cos(p)), 3).padStart(14), fmt(r * Math.sin(p), 3).padStart(16), fmt(r * Math.sin(p) / psiDeg, 3).padStart(16));
}
console.log(`\nSo a linear stage carries a 1/r reduction: about ${fmt(r * DEG, 3)} mm of tangent travel per degree of plan angle (derived from r).`);
console.log('1 um of tangent stage step = ' + fmt(0.001 / r / DEG, 5) + ' deg of plan angle.');

console.log('\nC: The gun-side alternative: a rotation psi about a pivot at distance L from the dot moves the dot by L*psi unless the pivot IS the dot.');
for (const L of [0, 50, 100, 200, 279]) console.log(' pivot ' + String(L).padStart(3) + ' mm from dot: ' + fmt(L * DEG, 3) + ' mm per degree');
