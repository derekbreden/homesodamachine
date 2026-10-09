// The lap: how fast does the seam move relative to a stationary dot, and what does that ask of anything that follows it?
// Accepted runout at the working end [repo weld-rotation-rig.md]: 0.25 mm TIR radial, 0.30 mm TIR face at the weld circle.
// Bead travel 5-15 mm/s [repo]; weld circle circumference 388.61 mm [repo]; overlap past the first tack about 20 degrees [repo].
// A pure first-harmonic (one cycle per revolution) runout is the ONLY shape modelled: real runout also has an out-of-round part.
// Usage: node calc/lap_rates.mjs
const C = 388.61, R = 61.85, TIR_R = 0.25, TIR_F = 0.30, OVER = 20;
console.log('speed  rpm    lap s   380deg s | radial slew mm/s (peak) | face slew mm/s | time to drift 0.02 mm at peak slew (s)');
for (const v of [5, 8, 10, 15]) {
  const T = C / v, w = 2 * Math.PI / T;
  const sr = (TIR_R / 2) * w, sf = (TIR_F / 2) * w;
  console.log(String(v).padStart(4), (60 / T).toFixed(3).padStart(7), T.toFixed(1).padStart(7), (T * (360 + OVER) / 360).toFixed(1).padStart(8), '|', sr.toFixed(4).padStart(14), '        |', sf.toFixed(4).padStart(10), '     |', (0.02 / Math.max(sr, sf)).toFixed(2).padStart(8));
}
console.log('\nreading: a follower that keeps the dot within 0.02 mm of a one-cycle-per-lap runout needs to update its position about every');
console.log('0.5 to 1.5 seconds (the last column) and never move faster than about 0.036 mm per second. That is slow enough for a hand-turned fine screw, a');
console.log('hobby servo behind a reduction, or a spring-loaded roller on the tube; the hard part is resolution and backlash, not speed.');
console.log('\nGun-side amplification for a pivot at the grip base (279 mm from the dot [derived]): 1 arcsecond -> ', (279 * Math.PI / 180 / 3600).toFixed(5), 'mm at the dot; 1 arcminute ->', (279 * Math.PI / 180 / 60).toFixed(3), 'mm; 1 degree ->', (279 * Math.PI / 180).toFixed(2), 'mm');
console.log('Tangent slide s at the dot: approach angle turns', (180 / Math.PI / R).toFixed(2), 'deg per mm; radial miss', (1 / (2 * R)).toFixed(4), 'mm per mm^2 [derived]');
