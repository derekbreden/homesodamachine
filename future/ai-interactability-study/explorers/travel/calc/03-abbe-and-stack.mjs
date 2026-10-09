// 03 - Abbe error of a work-side stage stack: the seam sits high above the stage, so a small tilt of a stage
// becomes a lateral error at the dot. Stack heights are from the rig doc [repo]; the stage tilt errors are ILLUSTRATIVE.
// Run: node explorers/travel/calc/03-abbe-and-stack.mjs
import { DEG, fmt } from './lib.mjs';

// [repo] weld-rotation-rig.md: tube rim stands 238.4 mm above the bench; bottom of tube 86 mm above bench; joint 146.05 above tube bottom.
const benchToFeet = 0;                  // rotator feet stand on the top plane of whatever stage carries them
const seamAboveFeet = 86 + 146.05;      // 232.05 mm  [derived from repo numbers: tube bottom 86 above bench, joint 146.05 above tube bottom]
console.log('Seam height above the rotator feet: ' + fmt(seamAboveFeet, 1) + ' mm  [derived]');

const stages = [
  { name: 'stage tilt 0.01 deg (good linear-rail axis, illustrative)', tiltDeg: 0.01 },
  { name: 'stage tilt 0.05 deg (hobby cross-slide, illustrative)',     tiltDeg: 0.05 },
  { name: 'stage tilt 0.10 deg (printed frame on rails, illustrative)', tiltDeg: 0.10 },
  { name: 'stage tilt 0.30 deg (scissor lab jack, illustrative)',       tiltDeg: 0.30 },
  { name: 'stage tilt 1.00 deg (loose drawer slide, illustrative)',    tiltDeg: 1.00 },
];
console.log('\nLateral error at the dot = tilt * (height of the seam above that stage\'s bearing plane)');
for (const s of stages) {
  console.log(s.name.padEnd(64), 'stage at rotator feet (H=' + fmt(seamAboveFeet, 0) + '):', fmt(s.tiltDeg * DEG * seamAboveFeet, 3).padStart(6), 'mm',
    '   stage 60 mm lower (H=' + fmt(seamAboveFeet + 60, 0) + '):', fmt(s.tiltDeg * DEG * (seamAboveFeet + 60), 3).padStart(6), 'mm');
}
// Compare: gun-side pivot errors, lever to the dot from the kit's proxy (illustrative geometry)
console.log('\nSame angles as gun-side joint slop with lever L to the dot (illustrative proxy: grip base 279 mm, barrel middle 93 mm)');
for (const s of stages) console.log(s.name.slice(0, 24).padEnd(26), 'L=279:', fmt(s.tiltDeg * DEG * 279, 3).padStart(6), 'mm   L=93:', fmt(s.tiltDeg * DEG * 93, 3).padStart(6), 'mm');

// what tilt keeps the seam within +-0.05 mm?
for (const tol of [0.05, 0.1, 0.25]) console.log('tilt allowed for +-' + tol + ' mm at H=' + fmt(seamAboveFeet, 0) + ':', fmt(tol / seamAboveFeet / DEG, 4), 'deg  (' + fmt(tol / seamAboveFeet * 1000, 3) + ' mrad)');
console.log('\nA tolerance is NOT a requirement here; +-0.05/0.10/0.25 mm are illustrative bands only.');
