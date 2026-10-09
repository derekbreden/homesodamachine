// How stiff is a room-hung gun, laterally, under the simplest arrangements?  Masses, pulls and bungee rates are [illustrative];
// the formulas are textbook statics.  Run: node explorers/room/calc/suspension-stiffness.mjs
const g = 9.81;
console.log('== 1. A gun of mass m hung from one line of length L (a pendulum): lateral stiffness k = m g / L [derived]');
for (const m of [1.5, 2.5]) for (const L of [0.3, 1.0, 2.4]) {
  const k = m * g / L;   // N/m
  console.log(`  m ${m} kg, L ${L} m: k = ${k.toFixed(1)} N/m = ${(k / 1000).toFixed(4)} N/mm -> a 1 N tug moves it ${(1000 / k).toFixed(0)} mm; sway period ${(2 * Math.PI * Math.sqrt(L / g)).toFixed(2)} s`);
}
console.log('  (a longer line is a softer pendulum, not a stiffer one; the room\'s height helps the cable, not the stiffness.)');

console.log('\n== 2. Add a pair of opposing bungees (Derek\'s example), each pretension T, length Lb, restraining ONE horizontal axis [derived, small displacement]');
console.log('  Displacement along the bungee axis: k_axial = 2 k_b (rate of each bungee, N/m) - soft by design.');
console.log('  Displacement PERPENDICULAR to the bungee axis: k_perp = 2 T / Lb.');
for (const T of [5, 20, 50]) for (const Lb of [0.5, 1.5]) console.log(`  T ${T} N, Lb ${Lb} m: k_perp = ${(2 * T / Lb).toFixed(0)} N/m = ${(2 * T / Lb / 1000).toFixed(3)} N/mm`);
for (const kb of [50, 200, 800]) console.log(`  bungee rate ${kb} N/m each: k_axial = ${2 * kb} N/m; 1 N moves it ${(1000 / (2 * kb)).toFixed(1)} mm`);

console.log('\n== 3. What tension would a perpendicular bungee pair need to reach 1 N/mm (1 N moves it 1 mm)? [derived]');
for (const Lb of [0.5, 1.5]) console.log(`  Lb ${Lb} m: T = k Lb / 2 = ${(1000 * 1000 * Lb / 2 / 1000).toFixed(0)} N  (${(1000 * Lb / 2 / g).toFixed(0)} kg-force of pretension on a bungee)`);

console.log('\n== 4. Taut lines that do not stretch (fixed length, e.g. winch-held Dyneema/steel): axial stiffness k = E A / L [derived, EA illustrative]');
for (const [nm, EA] of [['1 mm Dyneema-type braid EA 60 kN', 6e4], ['0.5 mm stainless EA 12 kN', 1.2e4], ['1 mm nylon monofilament EA 0.3 kN', 3e2]]) for (const L of [0.5, 1.0]) {
  console.log(`  ${nm}, L ${L} m: k = ${(EA / L / 1000).toFixed(1)} N/mm along the line (so a taut line is hundreds of times stiffer than gravity or pretension can be)`);
}
console.log('  The difference is what the constraint is made of: gravity and pretension give restoring force proportional to displacement over LENGTH; a fixed-length taut line gives it from the material\'s stretch.');

console.log('\n== 5. Hang + dock (state-based stiffness): free-hang k vs a docked contact [illustrative]');
const kFree = 2.0 * g / 1.0;     // 2 kg, 1 m
for (const kd of [5, 20, 100]) console.log(`  docked contact ${kd} N/mm vs free hang ${(kFree / 1000).toFixed(3)} N/mm: ${(kd * 1000 / kFree).toFixed(0)}x stiffer once the shell seats`);
