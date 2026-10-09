// travel-01 after use's exchange: a drop tier under the fine Z, seated on three balls at its top stop. What tilt does the seat leave,
// what does the tilt do to a seam circle of radius 61.85 mm, and what does the escape ask of the tier?
// ILLUSTRATIVE numbers (ball scatter, spans, speeds); the geometry is [repo] / [derived]. Run: node explorers/travel/calc/12-drop-tier-seat.mjs
const R = 61.85, DEG = 180 / Math.PI;
console.log('Tilt from three balls: worst case one ball high by c over a span s: tilt ~ c / s (rad). Seam-circle face runout from a tilt: peak r tan(tilt), peak-to-peak twice that.');
console.log('  c (um)  span (mm)   tilt (deg)   peak at r=61.85 (um)   seam sideways at 232 mm (um)   seam sideways at 330 mm (um)');
for (const c of [2, 5, 10, 20, 50]) for (const s of [100, 150, 250]) {
  const t = c / 1000 / s; console.log(String(c).padStart(7), String(s).padStart(9), (t * DEG).toFixed(4).padStart(12), (R * Math.tan(t) * 1000).toFixed(1).padStart(16), (232 * Math.tan(t) * 1000).toFixed(1).padStart(24), (330 * Math.tan(t) * 1000).toFixed(1).padStart(28));
}
console.log('\nWhat tilt is acceptable? A face-runout share of 0.02 mm peak (a tenth of the 0.30 mm TIR window [repo]) allows tilt =', (Math.atan(0.02 / R) * DEG).toFixed(4), 'degrees;');
console.log('use quotes 0.05 degree = 0.054 mm peak, 0.11 mm peak to peak:', (R * Math.tan(0.05 / DEG)).toFixed(3), 'mm peak.');
console.log('A 3-ball top seat with 10 um scatter at 150 mm span leaves', (Math.atan(0.010 / 150) * DEG).toFixed(4), 'degrees, i.e.', (R * Math.tan(0.010 / 150) * 1000).toFixed(1), 'um peak: about', ((0.02) / (R * Math.tan(0.010 / 150))).toFixed(0), 'times inside that share. A lab jack scissor (0.3 degrees, illustrative, sourcing 6) is', (R * Math.tan(0.3 / DEG)).toFixed(2), 'mm peak.');
console.log('\nThe fine axes trim a tilt\'s position but not the tilt: the once-per-turn vertical term stays. Peak to peak at the seam for 0.02 degree:', (2 * R * Math.tan(0.02 / DEG)).toFixed(3), 'mm.');
console.log('\nEscape as a tier drop (the work leaves the head), beam vertical component 0.712 in the kit\'s opening pose [derived]:');
const vb = 0.712;
for (const e of [10, 20, 30, 40]) console.log('  ' + e + ' mm along the beam = ' + (e / vb).toFixed(1) + ' mm of Z');
console.log('  at 60 mm/s the drop of 28.1 mm takes', (28.1 / 60).toFixed(2), 's, and the seam has turned', (8 * 28.1 / 60).toFixed(1), 'mm at 8 mm/s while it happens (0.47 s x 8 mm/s = 3.7 mm).');
console.log('  the fine Z alone (12 mm of range) gives at most', (12 * vb).toFixed(1), 'mm along the beam.');
console.log('\nSwap clearance with a drop of D: the rim clears the barrel by (5.0 mm tip margin + D - fine Z high stop) before the shuttle starts. With D = 40 and Z at +6: ', (5.0 + 40 - 6).toFixed(0), 'mm; without the tier and Z at +6 the barrel is 4 mm into the rim (use-13: red from Z = +2 in travel-01\'s own scene).');
