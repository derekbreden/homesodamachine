// look-ahead-geometry.mjs (eyes) - what a camera above the rim, some degrees of arc away from the station, sees of the dot.
// Geometry [repo]: seam circle r = 61.85 mm at z = 146.05; rim at z = 152.4, OD radius 63.5. Dot at (61.85, 0, 146.05).
// The eye stands R = 71.5 mm from the axis (8 mm outside the rim circle), h mm above the rim. All positions illustrative.
const RI = 61.85, RO = 63.5, ZR = 152.4, ZD = 146.05, D = Math.PI / 180;
const dot = [RI, 0, ZD];
const sub = (a, b) => a.map((x, i) => x - b[i]), len = a => Math.hypot(...a), nrm = a => a.map(x => x / len(a));
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]], dt = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
function clearsRim(p, target) { // does the straight line from p to target stay above the rim annulus (RI..RO, z <= ZR) ?
  for (let t = 0; t <= 1; t += 0.001) { const q = [p[0] + (target[0] - p[0]) * t, p[1] + (target[1] - p[1]) * t, p[2] + (target[2] - p[2]) * t]; const r = Math.hypot(q[0], q[1]); if (r >= RI + 1e-6 && r <= RO && q[2] <= ZR) return false; if (r > RO && q[2] <= ZR) return false; } return true; }
console.log('arc deg | height above rim | clears rim to the dot? | sens radial | sens vertical | kink strength (32 deg beam) | plate Lambert | wall Lambert');
for (const arc of [15, 25, 35, 50]) for (const h of [10, 25, 46, 80]) {
  const a = arc * D, p = [71.5 * Math.cos(a), 71.5 * Math.sin(a), ZR + h];
  const v = nrm(sub(dot, p)), ok = clearsRim(p, [dot[0] - 0.4, 0, dot[2] + 0.4]);
  const sr = Math.sqrt(1 - v[0] * v[0]), sz = Math.sqrt(1 - v[2] * v[2]);
  const right = nrm(cross(v, [0, 0, 1])), up = cross(right, v), P = q => [dt(q, right), dt(q, up)], cot = 1 / Math.tan(32 * D);
  const up_ = P([1, 0, 0]), uw_ = P([0, 0, cot]), d = Math.hypot(uw_[0] - up_[0], uw_[1] - up_[1]), K = d / (Math.hypot(...up_) + Math.hypot(...uw_));
  console.log([arc, h, ok ? 'yes' : 'no', sr.toFixed(2), sz.toFixed(2), K.toFixed(2), Math.abs(v[2]).toFixed(2), Math.abs(v[0]).toFixed(2)].join(' | '));
}
console.log('\nThe arc chord at 35 deg is ' + (2 * RI * Math.sin(17.5 * D)).toFixed(1) + ' mm; arc length ' + (RI * 35 * D).toFixed(1) + ' mm = ' + (RI * 35 * D / 8).toFixed(1) + ' s at 8 mm/s.');
