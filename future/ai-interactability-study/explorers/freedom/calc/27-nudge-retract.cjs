// freedom-10: numbers for a blind nudge box and a spring-driven retract. ILLUSTRATIVE (mass from ringmodel.js; screw pitches are common stock values).
const m = 1.2;                       // kg gun + shell (illustrative)
const pitch = 1.0, fullSteps = 200, micro = 16;      // T6x1 lead screw (1 mm/turn), 1.8 deg stepper, 1/16 microstepping
console.log('nudge: one full step', (pitch / fullSteps * 1000).toFixed(1), 'um; one microstep', (pitch / fullSteps / micro * 1000).toFixed(2), 'um; 0.1 mm = ', (0.1 / (pitch / fullSteps)).toFixed(0), 'full steps');
console.log('nudge: a 0.2 mm nudge repeated 25 times = 5.0 mm; a hand watching the dot can tell a 0.2 mm move at the seam only with magnification (not computed).');
for (const [d, t] of [[20, 0.2], [20, 0.5], [50, 0.5]]) { const a = 2 * d / 1000 / (t * t); console.log('retract', d, 'mm in', t, 's: mean acceleration', a.toFixed(2), 'm/s^2, net force on', m, 'kg =', (m * a).toFixed(2), 'N above what carries the weight'); }
console.log('retract by spring: energy for a 20 mm lift against a 1.2 N net force =', (1.2 * 0.02 * 1000).toFixed(0), 'mJ; a latch (solenoid or servo hook) holds the preload, a slow motor re-arms');
