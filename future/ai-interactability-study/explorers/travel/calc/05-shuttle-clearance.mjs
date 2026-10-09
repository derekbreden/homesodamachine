// 05 - can the whole rotator slide horizontally under a fixed gun (a "shuttle") without the rim hitting the nozzle?
// Rule: the nozzle tip must stay above the rim plane. Dot is 6.35 mm below the rim [repo]; nozzle clearance (tip to dot along the beam)
// is 16 mm in the kit's ILLUSTRATIVE proxy (the manual's graduated tube sets the real extension; real value [unknown]).
// The 0.48 mm wire and the beam are not solids; the wire must be retracted for a shuttle (it crosses the rim plane inside the bore).
// Run: node explorers/travel/calc/05-shuttle-clearance.mjs
import { DEG, fmt, RIM_Z, CAP_TOP } from './lib.mjs';

const recess = RIM_Z - CAP_TOP;   // 6.35
console.log('recess (rim above dot): ' + fmt(recess, 2) + ' mm [repo]');
console.log('\ntip height above rim plane = c*cos(beta) - recess   (c = nozzle clearance along the beam, beta = beam angle from vertical)');
const cs = [10, 13, 16, 20, 25];
console.log('beta(deg)  ' + cs.map(c => ('c=' + c).padStart(8)).join(''));
for (const b of [0, 15, 30, 40, 44.6, 50, 60, 66.6, 70, 80]) {
  console.log(fmt(b, 1).padStart(8), '  ' + cs.map(c => fmt(c * Math.cos(b * DEG) - recess, 1).padStart(8)).join(''));
}
for (const c of cs) console.log('c = ' + c + ' mm: tip stays above the rim plane while beta < ' + fmt(Math.acos(recess / c) / DEG, 1) + ' deg');
console.log('\nA tube lift of h (to leave the nest pilot, 4.5 mm [repo]) also raises the rim by h: needs tip height > h + margin, i.e. the reference pose (5.0 mm) does not allow a lift of 4.5 mm plus any margin.');
