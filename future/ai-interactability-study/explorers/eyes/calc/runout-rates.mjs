// runout-rates.mjs  (eyes)
// How fast does the seam move relative to a fixed gun because of runout?
// Inputs, with sources:
//   weld circle radius RI = 61.85 mm                          [repo] weld-rotation-rig.md (Ø123.70)
//   bead travel window 5..15 mm/s, nominal 8                   [repo] weld-rotation-rig.md
//   radial runout <= 0.25 mm TIR, face runout <= 0.30 mm TIR   [repo] weld-rotation-rig.md (acceptance limits)
// Model (illustrative simplification): pure eccentricity e = TIR/2 for radial; a tilted plate face whose
// height at the weld circle varies as a = TIR/2 * cos(phi). Real tubes have ovality and plate seat error too.
const RI = 61.85, TIR_R = 0.25, TIR_F = 0.30;
console.log('v mm/s | rev s | rpm | radial e mm | peak radial rate mm/s | peak face rate mm/s | 1 mm drift takes (min at peak rate)');
for (const v of [5, 8, 10, 15]) {
  const w = v / RI;                       // rad/s
  const rev = 2 * Math.PI / w;
  const eR = TIR_R / 2, eF = TIR_F / 2;
  const rateR = eR * w, rateF = eF * w;
  console.log([v, rev.toFixed(1), (60 / rev).toFixed(3), eR.toFixed(3), rateR.toFixed(4), rateF.toFixed(4), (1 / rateR / 60).toFixed(1)].join(' | '));
}
console.log('\nTake-away: the seam moves at most ~0.02-0.04 mm/s under a fixed gun. A 10 Hz camera sees 0.002-0.004 mm of that per frame.');
console.log('Hand tremor is much faster and larger than this; it is not measured for this gun [unknown].');
