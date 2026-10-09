// rod-under-tilt.mjs - room-03's rod, with eyes's beam model (exchange/eyes--on--room-w2.md, calc/wall-window.mjs in explorers/eyes),
// re-derived here and then asked a new question: what does the direction of gravity in the rod's frame do to the bend?
//
// Model (same as eyes): the rod is one beam through the ball. Inside segment d (ball to the dot end), tail Lt (ball to the actuators).
// Load F acts sideways at the dot end (upper-bound style: the gun's weight component across the rod + the cable's pull). The moment
// F d passes through the ball and bends BOTH segments. The tail actuators hold the tail POINT (pinned), so the tangent at the ball tilts by
// tau = F d Lt / (3 E I d)... (below), and the dot ends off the commanded line by  tip flex + tau d.
// [illustrative] aluminium tube, wall 2 mm unless given, E 69 GPa, gun 1.47 kg, cable pull 2 N, d 400, Lt 800.
// Run: node explorers/room/calc/rod-under-tilt.mjs
const G = 9.81, E = 69000;                                    // N/mm^2
function dotError({ OD = 20, wall = 2, d = 400, Lt = 800, F, M0 = 0 }) {
  const I = Math.PI / 64 * (OD ** 4 - (OD - 2 * wall) ** 4), EI = E * I;
  // sideways force F at the dot end + a pure couple M0 at the dot end (a CoM that sits off the rod axis under an axial weight)
  const Mball = F * d + M0;                                   // moment through the ball
  const tipFlex = F * d ** 3 / (3 * EI) + M0 * d ** 2 / (2 * EI);          // dot end vs the tangent at the ball, inside segment
  const tau = Mball * Lt / (3 * EI);                          // tangent tilt at the ball when the tail POINT is held (tail = beam pinned at the actuators)
  return { EI: EI / 1e6, tipFlex, tau: tau * 1000, dot: tipFlex + tau * d };
}
const line = (tag, r) => console.log(tag.padEnd(58), 'EI', r.EI.toFixed(0).padStart(5), 'N m^2 | tip flex', r.tipFlex.toFixed(2).padStart(5), 'mm | tilt at the ball', r.tau.toFixed(2).padStart(5), 'mrad | dot off the commanded line', r.dot.toFixed(2).padStart(5), 'mm');
const m = 1.47, Fc = 2;
console.log('room-03 as drawn: rod 45 deg below horizontal (barrel elevation 45 deg, the reference pose): gravity across the rod = m g sin(45 deg)');
line('  reference pose, OD 20 x 2 (eyes: 2.4 mm)', dotError({ F: m * G * Math.sin(45 * Math.PI / 180) + Fc }));
line('  OD 25 x 2', dotError({ OD: 25, F: m * G * Math.sin(45 * Math.PI / 180) + Fc }));
line('  OD 38 x 3 (the 1-1/2 in tube found on Prime)', dotError({ OD: 38, wall: 3, F: m * G * Math.sin(45 * Math.PI / 180) + Fc }));
console.log('the same rod when the tube is tipped so that the barrel leans less (tilt about the tangent, reference gun A: best 32.4 deg from vertical):');
line('  A at 32.5 deg tilt, OD 20 x 2', dotError({ F: m * G * Math.sin(32.4 * Math.PI / 180) + Fc }));
line('  A at 32.5 deg tilt, OD 38 x 3', dotError({ OD: 38, wall: 3, F: m * G * Math.sin(32.4 * Math.PI / 180) + Fc }));
console.log('the barrel exactly plumb (gun in the radial plane, wire off the gun, tube tipped 30 deg: attitude B): gravity is along the rod, its lever is the CoM offset 23 mm');
const M0 = m * G * 23;                                        // N mm : weight (axial) times the centre of mass's 23 mm offset from the barrel axis
line('  B at 30 deg, OD 20 x 2 (cable 2 N still acts)', dotError({ F: Fc, M0 }));
line('  B at 30 deg, OD 38 x 3', dotError({ OD: 38, wall: 3, F: Fc, M0 }));
line('  B at 30 deg, OD 20 x 2, cable pull 0 (weight only)', dotError({ F: 0, M0 }));
console.log('A change of 1 N in the cable pull (the part a calibration cannot absorb): dot moves', (dotError({ F: 1 }).dot).toFixed(2), 'mm at OD 20 x 2,', (dotError({ OD: 38, wall: 3, F: 1 }).dot).toFixed(3), 'mm at OD 38 x 3.');
console.log('note: the model puts the load at the dot end (upper bound); the real grip is 240 mm along the barrel, so the cable pull acts at a larger d.');
