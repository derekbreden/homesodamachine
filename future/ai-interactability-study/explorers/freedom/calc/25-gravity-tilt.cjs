// freedom-08: gravity as the tilt actuator. A gun hung from a pivot P above its centre of mass tilts until the COM is under P.
// Restoring stiffness = M g l (l = pivot-to-COM distance). A moving trim mass shifts the COM by m_s*d/M. ILLUSTRATIVE mass/COM (ringmodel.js).
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, L = FR.LOCAL, W = D.mass * FS.G;
const pivots = { 'housing top': L.housingTop, 'collar (barrel, 109)': L.collar, 'housing back': L.housingBack };
for (const k in pivots) {
  const P = pivots[k], l = M.len(M.sub(D.com, P)), kst = W * l / 1000;      // N*m/rad
  const lever = M.len(M.sub(P, L.dot));                                       // pivot to dot, mm
  const cable = M.len(M.sub(L.gripBase, P));                                  // pivot to cable exit, mm
  const tq = 2 * cable / 1000;                                                // N*m from 2 N of cable pull, all acting across the lever (worst case)
  console.log(k.padEnd(22), 'pivot-COM', l.toFixed(0), 'mm | gravity stiffness', kst.toFixed(2), 'N*m/rad =', (kst * Math.PI / 180).toFixed(4), 'N*m/deg | 2 N cable pull torque', tq.toFixed(2), 'N*m -> tilt up to', (tq / kst * 180 / Math.PI).toFixed(0), 'deg (small-angle) | pivot-to-dot', lever.toFixed(0), 'mm -> dot moves', (lever * Math.PI / 180).toFixed(1), 'mm per deg | trim mass 100 g moved 7.5 mm shifts COM', (0.1 * 7.5 / D.mass).toFixed(2), 'mm = tilt', (Math.atan(0.1 * 7.5 / D.mass / l) * 180 / Math.PI).toFixed(2), 'deg');
  console.log(' cable torque allowed for 0.1 deg of tilt error:', (kst * 0.1 * Math.PI / 180 * 1000).toFixed(2), 'N*mm =', ((kst * 0.1 * Math.PI / 180) / (2 * cable / 1000) * 100).toFixed(2), '% of a 2 N pull at the exit');
}
