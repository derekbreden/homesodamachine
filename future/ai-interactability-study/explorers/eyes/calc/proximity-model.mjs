// proximity-model.mjs (eyes) - how well could a pad or coil near the nozzle tell its distance to the plate or wall?
// Two crude first-principles models; results are ILLUSTRATIVE (real geometry, fringing, the copper nozzle and the
// printed shell are not modelled). Noise figures are chip specs or explicitly assumed:
//   FDC1004 capacitance resolution 0.5 fF, +-15 pF range, 4 channels      [TI product page, fetched 2026-09-28]
//   LDC1612 28-bit conversion, 2 channels, metal proximity              [TI product page, fetched 2026-09-28]
//   LDC1612 achievable inductance noise: ASSUMED 1 ppm of L (illustrative) - not checked against the datasheet plots.
const eps0 = 8.854e-12, mu0 = 4e-7 * Math.PI;

// --- capacitive: pad of area A facing a large grounded plane at distance d; fringing modelled as d0 added to the gap
function capFF(dmm, Amm2 = 60, d0mm = 1.0) { return eps0 * (Amm2 * 1e-6) / ((dmm + d0mm) * 1e-3) * 1e15; }   // fF

// --- eddy current: circular loop radius a over a perfect conductor; image loop at 2d with opposite current.
function ellipKE(k) { let a = 1, b = Math.sqrt(1 - k * k), c = k, sum = c * c / 2 * 1, pow = 1; let n = 0; let s = 0.5 * c * c; while (Math.abs(c) > 1e-14 && n < 30) { const an = (a + b) / 2, bn = Math.sqrt(a * b); c = (a - b) / 2; a = an; b = bn; pow *= 2; s += pow / 2 * c * c; n++; } const K = Math.PI / (2 * a); const E = K * (1 - s); return { K, E }; }
function mutual(aMm, sepMm) { const a = aMm * 1e-3, s = sepMm * 1e-3; const k2 = 4 * a * a / (4 * a * a + s * s), k = Math.sqrt(k2); const { K, E } = ellipKE(k); return mu0 * a * ((2 / k - k) * K - (2 / k) * E); }
function selfL(aMm, wireMm = 0.1) { const a = aMm * 1e-3; return mu0 * a * (Math.log(8 * a / (wireMm * 1e-3)) - 2); }
function dLppm(aMm, dmm) { return mutual(aMm, 2 * dmm) / selfL(aMm) * 1e6; }   // fractional inductance drop in ppm

console.log('CAPACITIVE, pad 60 mm^2 effective (8 x 8 mm plus fringe), gap offset d0 = 1 mm, noise 0.5 fF (FDC1004 spec)');
console.log('gap mm | C fF | slope fF/mm | distance resolution mm');
for (const d of [3, 5, 8, 12, 16, 20, 30]) { const c = capFF(d), s = Math.abs(capFF(d + 0.01) - capFF(d - 0.01)) / 0.02; console.log([d, c.toFixed(1), s.toFixed(2), (0.5 / s).toFixed(3)].join(' | ')); }
console.log('\nEDDY CURRENT, single loop radius a over a large plane, noise ASSUMED 1 ppm of L');
for (const a of [3, 5, 8]) {
  console.log('coil radius ' + a + ' mm:  gap mm | dL/L ppm | slope ppm/mm | resolution um');
  for (const d of [3, 5, 8, 12, 16, 20]) { const v = dLppm(a, d), s = Math.abs(dLppm(a, d + 0.01) - dLppm(a, d - 0.01)) / 0.02; console.log('   ' + [d, v.toFixed(0), s.toFixed(0), (1 / s * 1000).toFixed(2)].join(' | ')); }
}
console.log('\nTake-away (illustrative): at 8-12 mm a pad of 60 mm^2 resolves ~0.04-0.1 mm; a 5 mm-radius coil resolves micrometres if 1 ppm holds.');
console.log('Neither number includes the nozzle\'s own metal, temperature drift, the wire, spatter, or the wall-versus-plate mixing.');

// skin depth in 316L at coil frequency: delta = sqrt(rho / (pi f mu0)), rho ~ 7.4e-7 ohm m (typical austenitic stainless, textbook value)
for (const f of [1e6, 5e6, 10e6]) console.log('skin depth in 316L at ' + f / 1e6 + ' MHz: ' + (Math.sqrt(7.4e-7 / (Math.PI * f * mu0)) * 1e3).toFixed(2) + ' mm (wall is 1.65 mm, plate 6.35 mm: thick targets)');
// drift: a 50 ppm inductance error (illustrative: coil and shell warm by a few kelvin) equals how much distance?
const s5 = Math.abs(dLppm(5, 8.01) - dLppm(5, 7.99)) / 0.02;
console.log('50 ppm drift at 8 mm with the 5 mm coil = ' + (50 / s5).toFixed(3) + ' mm; at 12 mm = ' + (50 / (Math.abs(dLppm(5, 12.01) - dLppm(5, 11.99)) / 0.02)).toFixed(3) + ' mm');
