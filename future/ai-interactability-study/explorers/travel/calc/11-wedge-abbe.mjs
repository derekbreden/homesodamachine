// 11 - a wedge under the rotator (exchange on datum-12-work-side-tilt): where the seam goes, which rotation the tilt supplies at which station azimuth,
// and two stacked wedge rings (a Risley pair). Heights from the repo: the seam stands 232.05 mm above the rotator's feet (tube bottom 86 mm above the bench,
// seam 146.05 mm above the tube bottom) [derived]. Wedge angles and masses are illustrative.
// Run: node explorers/travel/calc/11-wedge-abbe.mjs
import { fmt, INNER_RADIUS } from './lib.mjs';
const DEG = Math.PI / 180, H = 86 + 146.05, R = INNER_RADIUS;

console.log('1. A wedge under the base tilts the rotator about a line at the bench (the ridge), not about the dot. Ridge = the radial line through the tube axis to the station.');
console.log('   Seam circle points (R cos p, R sin p, H) turn about the x axis by alpha. The seam point that was at the station moves sideways by H sin(alpha):');
console.log('   alpha   sideways shift of the seam point (mm)   drop (mm)   if the station is kept at y = 0: which tube azimuth arrives, and how far the seam moved radially (mm)');
for (const a of [1, 2, 5, 10]) {
  const al = a * DEG, side = H * Math.sin(al), drop = H * (1 - Math.cos(al));
  const s = H / R * Math.tan(al), ok = Math.abs(s) <= 1, phi = ok ? Math.asin(s) : NaN;
  console.log('   ' + String(a).padStart(4) + ' deg ' + fmt(side, 1).padStart(22) + fmt(drop, 2).padStart(16) + (ok ? '        azimuth ' + fmt(phi / DEG, 1) + ' deg, radial shift ' + fmt(R * Math.cos(phi) - R, 1) : '        (the station would leave the circle)'));
}
console.log('   A wedge set once and the gun placed afterwards does not care (the seam is where it is). A wedge that is changed between experiments moves the seam by 4 mm per degree,');
console.log('   so each change needs the gun (or an XYZ stage of tens of millimetres) to follow. datum-12 says the dot stays where it is: it does not, unless the pivot is at the dot (an arc, travel-03b).\n');

console.log('2. What the tilt supplies at the station. The tilt is a vector: magnitude alpha, direction fixed by the wedge (the lean). At a station whose radial direction is');
console.log('   psi from the lean, the plate normal tilts alpha cos(psi) in the radial section (the beam-versus-plate angle, the "grip-axis roll" of the reference scene) and');
console.log('   alpha sin(psi) along the tangent (the "hole-axis roll", pitch):');
for (const psi of [0, 30, 45, 60, 90]) console.log('   station ' + String(psi).padStart(2) + ' deg from the lean: in-section ' + fmt(10 * Math.cos(psi * DEG), 1) + ' deg, along the tangent ' + fmt(10 * Math.sin(psi * DEG), 1) + ' deg  (for a 10 deg wedge)');
console.log('   So one fixed wedge plus a choice of where the gun stands supplies any mix of those two rotations, not just the hole-axis roll.\n');

console.log('3. Two wedge rings stacked (a Risley pair): wedge angle a each; rotating one by delta relative to the other gives a tilt of magnitude 2a cos(delta/2) in the mean direction.');
for (const a of [3, 5]) {
  console.log('   a = ' + a + ' deg: reachable tilt 0 to ' + 2 * a + ' deg in any direction; one ring turned 1 deg changes the tilt by at most ' + fmt(a * DEG, 3) + ' deg (reduction ' + fmt(1 / (a * DEG), 1) + ' to 1); seam moves at most ' + fmt(H * Math.sin(2 * a * DEG), 1) + ' mm');
}
console.log('   Motorised, the pair is two rotary axes with a built-in reduction and no arcs; the seam displacement (4 mm per degree of tilt) has to be followed by the gun or a stack.\n');

console.log('4. Side load on the printed ball race: sin(alpha) of the weight (rotator plus tube plus vessel, 2 to 5 kg [unknown]):');
for (const a of [3, 5, 10]) console.log('   ' + a + ' deg -> ' + fmt(Math.sin(a * DEG) * 100, 0) + ' percent of the weight sideways: ' + fmt(2 * 9.81 * Math.sin(a * DEG), 1) + ' to ' + fmt(5 * 9.81 * Math.sin(a * DEG), 1) + ' N');
