// freedom W2: the umbilical as a spring and as a force gauge (for eyes-11b). ILLUSTRATIVE: EI, weight per metre and lengths are [unknown].
// A cable of bending stiffness EI, free length l hanging from the gun's exit: lateral stiffness at the exit k = 3 EI / l^3 (cantilever), i.e. the pull change per mm the gun moves.
// A 2-D estimate of how far the tip of a cantilever bends under a lateral load F: d = F l^3 / (3 EI).
// The force to hold a cable bent to radius R over a quarter turn is of order EI / R^2 (bending moment EI/R applied over a lever about R).
const rows = [];
for (const EI of [0.05, 0.2, 0.5]) for (const l of [0.3, 0.5, 0.8]) {
  const k = 3 * EI / Math.pow(l, 3);                  // N/m
  rows.push({ EI, l, k_Nmm: k / 1000, mNperMm: k, mmPerN: 1000 / k * 1 / 1000 * 1000 });
}
console.log('EI (N m^2)  l (m)  lateral stiffness at the exit (N/mm)  | pull change per mm of gun motion (mN) | shape change per newton (mm)');
rows.forEach(r => console.log(String(r.EI).padEnd(10), String(r.l).padEnd(6), r.k_Nmm.toFixed(4).padEnd(36), '|', r.mNperMm.toFixed(1).padEnd(38), '|', (1 / r.k_Nmm).toFixed(0)));
console.log('bend force EI/R^2 at the manual radii: R 0.35 m (emitting) and 0.24 m (stored):');
for (const EI of [0.05, 0.2, 0.5]) console.log(' EI', EI, ' F at 0.35 m', (EI / 0.35 / 0.35).toFixed(2), 'N | at 0.24 m', (EI / 0.24 / 0.24).toFixed(2), 'N');
console.log('trim of +-6 mm against the cable alone:', [0.001, 0.01, 0.06].map(k => (6 * k * 1000).toFixed(0) + ' mN at k ' + k + ' N/mm').join(' | '));
