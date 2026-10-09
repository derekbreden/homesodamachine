// freedom W2: how much of eyes-01's trim range does each support spend per newton of umbilical pull, and what does a change of pull do?
// One rigid body (kit gun proxy, ILLUSTRATIVE mass 1.2 kg, COM 178 back, umbilical pull direction from exit blended with straight down).
// Supports compared, all at the reference pose:
//   A  eyes-01 as drawn but with real rotation: one elastic line to a stage carrying a RIGID rod to the housing lug (translation k, rotation = the stage's own, taken rigid)
//   B  same lug but ball-ended (translation k, no rotational restraint)  -> a pendulum on a spring
//   C  nose seat + tail bridle (freedom-01b) with the nose stage as the trim
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
function run(label, o, F) {
  o.umbilical = { F: F, droop: 0.5 };
  const m = FR.build(o); const r = m.solve(new Float64Array(m.n), { maxIter: 300 });
  if (!r.converged) return { label, F, ok: false };
  const x = r.x, dc = m.dotCompliance(x);
  const tilt = M.len([x[3], x[4], x[5]]) / FS.S * 180 / Math.PI;
  return { label, F, ok: true, u: [x[0], x[1], x[2]], tilt, C: [0, 1, 2].map(i => dc.C[i][i]) };
}
const fmt = v => v.toFixed(2);
console.log('--- pull change from the setup pull (2 N) to 4 N, 6 N: dot displacement (r,t,z) mm and tilt deg, relative to the 2 N pose');
const supports = {
  'A rigid rod on elastic k=0.5': k => ({ rings: [], nose: null, tail: null, arm: { mode: 'rigid', at: 'housingTop', k: k, kRot: 1e5, cmd: [0, 0, 0] } }),
  'B ball-end lug on elastic': k => ({ rings: [], nose: null, tail: null, arm: { mode: 'point', at: 'housingTop', k: k, cmd: [0, 0, 0] } }),
};
for (const name of Object.keys(supports)) {
  for (const k of [0.1, 0.5, 2, 10]) {
    const base = run(name, supports[name](k), 2);
    if (!base.ok) { console.log(name, 'k', k, 'no equilibrium at 2 N'); continue; }
    const rows = [4, 6].map(F => { const r = run(name, supports[name](k), F); return r.ok ? '+' + (F - 2) + ' N: dot ' + [0, 1, 2].map(i => fmt(r.u[i] - base.u[i])).join(',') + ' tilt ' + fmt(r.tilt - base.tilt) + ' deg' : '+' + (F - 2) + ' N: no eq'; });
    console.log(name.padEnd(30), 'k', String(k).padEnd(5), 'compliance r,t,z', base.C.map(fmt).join(','), 'mm/N | tilt at 2 N', fmt(base.tilt), 'deg |', rows.join(' | '));
  }
}
