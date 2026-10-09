// 07 - with the gun in the kit's ILLUSTRATIVE opening pose, how far can the tube be lifted, and can it then slide out (+x) or be pulled straight up?
// The barrel is approximated by spheres along its axis (radius profile from the kit proxy; housing as radius 24 = half diagonal of its 34 x 34 mm section).
// The tube rim is a ring (radius 62.675 mm, half-wall 0.825 mm) at z = 152.4 + lift, centred at (slide, 0). Recess and wall are [repo]; pose and gun are illustrative.
// Run: node explorers/travel/calc/07-lift-and-slide.mjs
import { world, OPENING, RIM_Z, INNER_RADIUS, fmt } from './lib.mjs';

const { roll, holeDial, vertical } = OPENING;
const RC = INNER_RADIUS + 0.825, HW = 0.825;
const prof = z => (z < 23 ? 2.2 + 2.8 * z / 23 : z < 54 ? 8.5 : z < 100 ? 5.5 : z < 118 ? 12 : 24);
function pts(dz = 0) {
  const out = [];
  for (let z = 0; z <= 253; z += 3) { const p = world([0, 0, z], roll, holeDial, vertical); out.push({ p: [p[0], p[1], p[2] + dz], r: prof(z), z }); }
  return out;
}
function clearance(P, lift, sx, sy) {
  let min = Infinity, at = null;
  for (const s of P) {
    const dx = s.p[0] - sx, dy = s.p[1] - sy;
    const d = Math.hypot(Math.hypot(dx, dy) - RC, s.p[2] - (RIM_Z + lift)) - HW - s.r;
    if (d < min) { min = d; at = s; }
  }
  return { min, at };
}
console.log('Opening pose (illustrative). Gun raised by dz (mm) as a rigid translation.\n');
console.log('A. Lift the tube straight up by h, no slide. Smallest gap between the rim ring and the gun (negative = collision):');
console.log('dz(gun)   ' + [5, 10, 20, 40, 60, 80, 120, 152].map(h => ('h=' + h).padStart(8)).join(''));
for (const dz of [0, 20, 40, 100, 200]) {
  const P = pts(dz);
  console.log(String(dz).padStart(6), '   ' + [5, 10, 20, 40, 60, 80, 120, 152].map(h => fmt(clearance(P, h, 0, 0).min, 1).padStart(8)).join(''));
}
console.log('\nB. Lift by 12 mm then slide the tube toward +x by s. Smallest gap:');
console.log('dz(gun)   ' + [0, 20, 40, 80, 120, 160].map(s => ('s=' + s).padStart(8)).join(''));
for (const dz of [0, 5, 10, 20, 40, 100]) {
  const P = pts(dz);
  console.log(String(dz).padStart(6), '   ' + [0, 20, 40, 80, 120, 160].map(s => fmt(Math.min(...Array.from({ length: s + 1 }, (_, i) => clearance(P, 12, i, 0).min)), 1).padStart(8)).join(''));
}
// smallest gun raise dz that clears a 12 mm lift plus a full slide out (0..160 mm) with 3 mm margin
let dzNeeded = null;
for (let dz = 0; dz <= 300; dz++) { const P = pts(dz); let ok = true; for (let s = 0; s <= 200 && ok; s++) if (clearance(P, 12, s, 0).min < 3) ok = false; if (ok) { dzNeeded = dz; break; } }
console.log('\nSmallest rigid raise of the gun that clears a 12 mm lift and a slide out toward +x, with a 3 mm margin:', dzNeeded, 'mm (illustrative)');
// smallest raise for lifting straight up out of the machine (152 mm + 4.5 nest pilot)
let dzUp = null;
for (let dz = 0; dz <= 600; dz += 2) { const P = pts(dz); let ok = true; for (let h = 0; h <= 200 && ok; h += 2) if (clearance(P, h, 0, 0).min < 3) ok = false; if (ok) { dzUp = dz; break; } }
console.log('Smallest rigid raise that lets the tube be lifted straight up and out (lift 0..200 mm):', dzUp, 'mm');
