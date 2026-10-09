// A4 swing head: does the umbilical's drawn bend stay above the manual's minimum radii while the head plunges and swings?
// Manual [p.20]: minimum bend radius 240 mm stored (laser off), 350 mm while emitting. Twisting forbidden.
// The cable here is the kit's cubic-Bezier stand-in (WK.bezierCable), NOT a cable model: no stiffness, weight or twist.
// The hook is ILLUSTRATIVE. Which states emit: plunge retract with the trigger held is emitting (repo weld sequence step 6-7); swing is stored.
import { world, ANCHORS, ROLL_AXIS, sub, add, mul, unit, norm, fmt, DEG } from './pose.mjs';
const DIALS = [45, 30, -15];
const W = l => world(l, ...DIALS);
const nozzle = W(ANCHORS.nozzleTip), beam = unit(sub(W(ANCHORS.dot), nozzle)), back = mul(beam, -1);
const exit0 = W(ANCHORS.gripBase);
const axisW = unit(sub(W([ROLL_AXIS[0] * 100, ROLL_AXIS[1] * 100, ROLL_AXIS[2] * 100 - 16]), W([0, 0, -16]))); // roll axis direction in world (dot -> grip base)
function bezier(a, da, b, db, stiff) {
  const k = Math.max(15, stiff * norm(sub(b, a)));
  const c1 = add(a, mul(unit(da), k)), c2 = add(b, mul(unit(db), -k));
  const pts = [];
  for (let i = 0; i <= 240; i++) { const t = i / 240, u = 1 - t; pts.push([0, 1, 2].map(j => u * u * u * a[j] + 3 * u * u * t * c1[j] + 3 * u * t * t * c2[j] + t * t * t * b[j])); }
  return pts;
}
function minR(pts) {
  let m = Infinity;
  for (let i = 1; i < pts.length - 1; i++) {
    const ab = sub(pts[i], pts[i - 1]), bc = sub(pts[i + 1], pts[i]), ca = sub(pts[i + 1], pts[i - 1]);
    const cr = [ab[1] * bc[2] - ab[2] * bc[1], ab[2] * bc[0] - ab[0] * bc[2], ab[0] * bc[1] - ab[1] * bc[0]];
    const a2 = norm(cr); if (a2 < 1e-9) continue;
    m = Math.min(m, (norm(ab) * norm(bc) * norm(ca)) / (2 * a2));
  }
  return m;
}
function rotZ(p, post, th) { const c = Math.cos(th), s = Math.sin(th), dx = p[0] - post[0], dy = p[1] - post[1]; return [post[0] + dx * c - dy * s, post[1] + dx * s + dy * c, p[2]]; }
const rotDir = (d, th) => rotZ(d, [0, 0, 0], th);
const post = [150, -330];
console.log('cable exit (seat pose)', fmt(exit0), ' exit direction', fmt(axisW, 3));
// hooks defined relative to the post: overhead point at height dz above the exit, offset (dx,dy) from the post axis
const hooks = [];
for (const dz of [150, 250, 400]) for (const off of [0, 150, 300]) hooks.push({ dz, off });
for (const stiff of [0.4, 0.6]) {
  console.log('\nstiffness', stiff, '(kit: ~0.2 limp .. 0.8 stiff)');
  console.log('hook dz  hook off  |  min R: seat | plunge 40 | swing 25deg (plunge 40) | swing 25 stored');
  for (const h of hooks) {
    const hook = [post[0], post[1] - h.off, exit0[2] + h.dz];       // straight above the swing axis, off along -Y
    const hd = [0, -1, 0];                                            // arrives heading -Y (toward the cart)
    const row = [];
    for (const [pl, th] of [[0, 0], [40, 0], [40, 25 * DEG], [40, 50 * DEG]]) {
      const e = add(exit0, mul(back, pl)); const d = axisW;
      const er = rotZ(e, post, th), dr = rotDir(d, th);
      row.push(minR(bezier(er, dr, hook, hd, stiff)).toFixed(0));
    }
    console.log(String(h.dz).padStart(5), String(h.off).padStart(9), '  |', row.map(v => v.padStart(6)).join(' '));
  }
}
console.log('\nreading: a cell >= 350 passes the emitting check, >= 240 passes stored. The plunge (emitting) column is the one that must be >= 350.');

// ---- second table: hook placed ALONG the cable's own exit direction (D mm out), with a lateral miss `m`.
// Hook on the swing arm (rotates with the gun): only the plunge changes the miss (<= 40 mm).
// Hook on the fixed post: the swing moves the exit sideways by about R*theta.
console.log('\nHook on the exit axis, distance D out, lateral miss m (mm) -> min bend radius (mm), stiffness 0.4');
const sideDir = unit([-axisW[1], axisW[0], 0]);
console.log('  D     m=0    m=40   m=100  m=150');
for (const D of [300, 450, 600, 800, 1000, 1300]) {
  const row = [];
  for (const m of [0, 40, 100, 150]) {
    const hook = add(add(exit0, mul(axisW, D)), mul(sideDir, m));
    row.push(minR(bezier(exit0, axisW, hook, axisW, 0.4)));
  }
  console.log(String(D).padStart(5), row.map(v => (isFinite(v) ? v.toFixed(0) : 'inf').padStart(7)).join(' '));
}
console.log('(a straight run has infinite radius; a miss of m over D bends the run into an S of radius about D^2/(4 m) [derived, small-angle]).');
