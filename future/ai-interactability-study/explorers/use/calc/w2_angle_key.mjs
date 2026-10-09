// Wave 2: how well must the angle be known for a follow table keyed by rotator angle (travel-02 and the five other map-and-replay ideas)?
// Residual radial error when a periodic runout is replayed with a phase error phi: 2 a_n |sin(n phi / 2)| for harmonic n of amplitude a_n.
// Amplitudes: 1x 0.125 mm (0.25 mm TIR acceptance [repo], as a sinusoid), 2x 0.03 mm (travel-02's illustrative ovality), 3x 0.01 mm (illustrative).
// Usage: node calc/w2_angle_key.mjs
const A = [[1, 0.125], [2, 0.03], [3, 0.01]];
const DEG = Math.PI / 180;
console.log('phase error (deg) -> residual by harmonic (mm) and their sum (worst case, phases aligned)');
for (const phi of [1, 2, 5, 10, 20, 30, 60]) {
  const r = A.map(([n, a]) => 2 * a * Math.abs(Math.sin(n * phi * DEG / 2)));
  console.log(String(phi).padStart(3), 'deg :', r.map(v => v.toFixed(4)).join('  '), ' sum', r.reduce((t, v) => t + v, 0).toFixed(4));
}
for (const tol of [0.02, 0.05]) {
  let phi = 0; while (A.map(([n, a]) => 2 * a * Math.abs(Math.sin(n * phi * DEG / 2))).reduce((t, v) => t + v, 0) < tol && phi < 90) phi += 0.05;
  console.log(`the table stays inside ${tol} mm up to about ${phi.toFixed(1)} deg of phase error (first three harmonics, worst case)`);
}
console.log('\nsteps: 0.025 deg per pulse [repo] -> 10 deg is', (10 / 0.025).toFixed(0), 'steps; arc length at r = 61.85 mm:', (61.85 * 10 * DEG).toFixed(1), 'mm');
console.log('an index mark read by eye to +-1 mm of arc is', (1 / 61.85 / DEG).toFixed(1), 'deg');
console.log('The driver lets the motor go 10 s after the pedal is released, and the console degrees are "a readout for the operator, never a limit" [repo firmware README; whether the count restarts at each press is not stated]:');
console.log('after the release the table can be turned by hand, so a count is only as good as the last time the motor held it; the index mark (or a pulse) is a zero that survives.');
