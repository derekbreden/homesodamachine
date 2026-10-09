// freedom-01c: three jobs for the same rubber. One axis, one bungee, ILLUSTRATIVE numbers.
const kb = 0.15;            // N/mm bungee (scene 01 default)
const pre = 5;              // N preload against a stop
const kStop = 50;           // N/mm stiffness of a printed stop + screw contact
const step = 0.01;          // mm per motor step (a lead screw, e.g. T6x1 at 1/16 microstep: 1 mm / 3200 = 0.0003 mm; 0.01 is deliberately coarse)
console.log('bungee alone: a 1 N disturbance moves the ring', (1 / kb).toFixed(1), 'mm; a 0.1 N one', (0.1 / kb).toFixed(2), 'mm');
console.log('bungee + hard stop (preload', pre, 'N): holds position to within', (1 / kStop).toFixed(3), 'mm per N until a push of', pre, 'N unloads the stop; beyond that it behaves as the bungee,', (1 / kb).toFixed(1), 'mm per N');
console.log('series-elastic (motor moves the bungee anchor by steps of', step, 'mm): force resolution', (kb * step * 1000).toFixed(2), 'mN per step; a 5 N force range needs', (pre / kb).toFixed(0), 'mm of anchor travel; the ring floats where forces balance');
console.log('screw + stop with bungee return: no backlash while the preload holds; the screw sets position to', step, 'mm per step; the return force is', pre, 'N');
const w = 12, L = 350;
console.log('pendulum stiffness of a', w, 'N load on a', L, 'mm wire:', (w / L).toFixed(3), 'N/mm (soft in every direction the bungees do not hold)');
