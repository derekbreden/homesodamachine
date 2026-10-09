// marker-error.mjs (eyes) - error at the dot when the gun's pose comes from fiducial tags on the shell.
// First-order pinhole propagation. Every constant below is ILLUSTRATIVE (labelled), none measured.
//   image width W = 1920 px, horizontal field of view 60 deg           (illustrative camera)
//   corner localisation noise sigma_c = 0.15 px (good light; 0.1-0.3 px is the usual quoted range: unchecked)
//   tag side a, camera distance Z, lever arm L from the cube centre to the dot
//   fixed cube-to-dot calibration error 0.10 mm (illustrative; a scan of the shell is 0.02 mm per the Revopoint spec, [repo] tools.md)
// Model:
//   lateral position of a tag centre      s_xy = (sc/2) * Z/f                       (mean of 4 corners)
//   depth of a tag                        s_z  = sc * Z^2 / (sqrt2 * a * f)         (from apparent size)
//   orientation (2 axes), one tag         s_th = sc * Z / (a * f) / max(sin(tilt), 0.35)     rad, tilt = 35 deg here
//   cube with faces at 90 deg             rotation error x0.7;  n cameras: everything / sqrt(n)  (depth of one is lateral of another)
const W = 1920, hfov = 60 * Math.PI / 180, f = W / (2 * Math.tan(hfov / 2)), sc = 0.15, sCal = 0.10;
// position covariance from n cameras with viewing-ray unit vectors: information along a ray 1/sz^2, across it 1/sxy^2
function inv3(m) { const [a, b, c, d, e, g, h, i, j] = [m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2]]; const A = e * j - g * i, B = -(d * j - g * h), C = d * i - e * h, det = a * A + b * B + c * C; return [[A / det, -(b * j - c * i) / det, (b * g - c * e) / det], [B / det, (a * j - c * h) / det, -(a * g - c * d) / det], [C / det, -(a * i - b * h) / det, (a * e - b * d) / det]]; }
function posSigma(rays, sxy, sz) {
  const I = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (const u of rays) for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) I[r][c] += u[r] * u[c] / (sz * sz) + ((r === c ? 1 : 0) - u[r] * u[c]) / (sxy * sxy);
  const C = inv3(I); return Math.sqrt(C[0][0] + C[1][1] + C[2][2]);
}
export function sigmaDot({ a, Z, L, nCam, cube, sepDeg = 90 }) {
  const sxy = sc / 2 * Z / f, sz = sc * Z * Z / (Math.SQRT2 * a * f);
  let sth = sc * Z / (a * f) / Math.max(Math.sin(35 * Math.PI / 180), 0.35) * (cube ? 0.7 : 1);
  const th = sepDeg * Math.PI / 180, rays = nCam >= 2 ? [[1, 0, 0], [Math.cos(th), Math.sin(th), 0]] : [[1, 0, 0]];
  const pos = posSigma(rays, sxy, sz);
  const rot = sth * Math.sqrt(2) / Math.sqrt(nCam);
  return { total: Math.hypot(pos, L * rot, sCal), pos: pos, lever: L * rot };
}
console.log('f = ' + f.toFixed(0) + ' px.  sigma at the dot (mm, 1 sigma), by lever arm L from the cube to the dot');
for (const [label, cfg] of [['1 camera, one 25 mm tag, Z 500', { a: 25, Z: 500, nCam: 1, cube: false }], ['2 cameras, 25 mm cube faces, Z 500', { a: 25, Z: 500, nCam: 2, cube: true }], ['2 cameras, 45 mm faces, Z 500', { a: 45, Z: 500, nCam: 2, cube: true }], ['2 cameras, 25 mm faces, Z 250', { a: 25, Z: 250, nCam: 2, cube: true }]]) {
  console.log('\n' + label);
  console.log('L mm : ' + [40, 80, 120, 180, 230, 280].map(L => String(L).padStart(6)).join(''));
  console.log('sigma: ' + [40, 80, 120, 180, 230, 280].map(L => sigmaDot({ ...cfg, L }).total.toFixed(2).padStart(6)).join(''));
}
console.log('\nTwo cameras, 25 mm faces, Z 500, L 80: uncertainty at the dot against the angle between the two viewing rays');
for (const sep of [5, 10, 20, 40, 60, 90, 120]) { const r_ = sigmaDot({ a: 25, Z: 500, L: 80, nCam: 2, cube: true, sepDeg: sep }); console.log('  ' + String(sep).padStart(3) + ' deg: position part ' + r_.pos.toFixed(2) + ' mm, total ' + r_.total.toFixed(2) + ' mm'); }
const r = (cfg, L) => sigmaDot({ ...cfg, L }).total.toFixed(2);
const c25 = { a: 25, Z: 500, nCam: 2, cube: true }, c45 = { a: 45, Z: 500, nCam: 2, cube: true };
console.log('\nReading: with two cameras at 500 mm and 25 mm faces the dot is known to about ' + r(c25, 230) + ' mm (1 sigma) from a cube on the housing 230 mm back, ' + r(c25, 80) + ' mm from a cube 80 mm back, ' + r(c25, 40) + ' mm at 40 mm; 45 mm faces: ' + r(c45, 230) + ' / ' + r(c45, 80) + ' / ' + r(c45, 40) + '.');
console.log('A cube 40-80 mm behind the tip is above the rim and in plain view from the bore side (scene eyes-03), so the trade is heat and fit, not line of sight.');
