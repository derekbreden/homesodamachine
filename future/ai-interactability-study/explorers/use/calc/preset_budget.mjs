// A5 preset cartridge: what a height ring, a register and a tilted ring do to the numbers the rig doc already accepts.
// Accepted at the working end [repo weld-rotation-rig.md]: radial <= 0.25 mm TIR, plate-face <= 0.30 mm TIR at the weld circle.
// Everything else is ILLUSTRATIVE or derived; the spread of tube lengths and seat depths is [unknown].
// Usage: node calc/preset_budget.mjs
const H_WEAVE = 146.05, D_WELD = 123.70, D_RING = 127;   // weld-circle height above tube bottom [derived], weld circle diameter [repo], ring bearing diameter [illustrative]
console.log('1) Ring parallelism error d (mm across the ring) -> what it adds');
console.log('   tilt alpha = d / D_RING; face TIR at the weld circle = alpha * D_WELD; radial eccentricity at the weld end = alpha * H (before the screws correct it)');
for (const d of [0.02, 0.05, 0.10, 0.15, 0.25]) {
  const a = d / D_RING;
  console.log(`   d=${d.toFixed(2)}: face TIR +${(a * D_WELD).toFixed(3)} mm (limit 0.30), radial ecc ${(a * H_WEAVE).toFixed(3)} mm -> radial TIR ${(2 * a * H_WEAVE).toFixed(3)} mm if left uncorrected (limit 0.25)`);
}
console.log('\n2) Cartridge register clearance c (mm): the cartridge may sit anywhere within +-c/2 of the axis on the rotator');
for (const c of [0.02, 0.05, 0.10, 0.20]) console.log(`   c=${c.toFixed(2)}: adds up to ${c.toFixed(2)} mm to the radial TIR (worst case), about ${(c * 0.7).toFixed(2)} mm RMS-ish [illustrative]`);
console.log('\n3) Height ring quantum q (mm): worst-case seam z error after setting the ring to the gauge reading is q/2 + gauge reading error (0.0127 mm = 0.0005 in indicator [repo tool])');
for (const q of [0.05, 0.1, 0.25, 0.5, 1.0]) console.log(`   q=${q.toFixed(2)}: seam z error up to +-${(q / 2 + 0.0127).toFixed(3)} mm`);
console.log('\n4) Tube-length spread L (mm, +-): seam z at the gun with no compensation is +-L (recess is set from the rim by a depth-stop [repo])');
console.log('   +-1.6 mm (1/16 in) [assumed common cut tolerance, unchecked] => the dot is 1.6 mm above or below the seam before any setting.');
console.log('   Slew of a 0.3 mm face runout over one lap: see lap_rates.mjs.');
