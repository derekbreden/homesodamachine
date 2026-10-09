// dot-probe.mjs (eyes) - numbers behind eyes-06 (the dot as the probe: sweep-kink and bounce spot).
// Section geometry: plate top z = 0 (r <= 0), wall face r = 0 (z >= 0). Beam tilted beta from vertical toward the wall.
// s = radial position where the beam line meets the plate plane, extended through the wall if s > 0.
//   s <= 0: the spot is on the plate at r = s;      s > 0: the spot is on the wall at height z = s * cot(beta)
// Specular bounce (mirror surfaces): the pair of spots is {plate at |s|, wall at |s| cot(beta)} in both cases.
// Camera basis for view direction v: right = normalize(v x z), up = right x v.  All numbers pure geometry [derived].
const D = Math.PI / 180;
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const norm = a => { const l = Math.hypot(...a); return a.map(x => x / l); };
function basis(psiDeg, elDeg) { const c = [-Math.cos(elDeg * D) * Math.cos(psiDeg * D), -Math.cos(elDeg * D) * Math.sin(psiDeg * D), Math.sin(elDeg * D)], v = c.map(x => -x); const right = norm(cross(v, [0, 0, 1])); const up = cross(right, v); return { right, up, v }; }
const P = (b, p) => [dot(p, b.right), dot(p, b.up)];
function kinkStrength(psi, el, betaDeg) {
  const b = basis(psi, el), cot = 1 / Math.tan(betaDeg * D);
  const up_ = P(b, [1, 0, 0]), uw_ = P(b, [0, 0, cot]);      // image motion per mm of sweep: on the plate, on the wall
  const d = Math.hypot(uw_[0] - up_[0], uw_[1] - up_[1]), m = Math.hypot(...up_) + Math.hypot(...uw_);
  return { K: d / m, dv: d, plate: Math.hypot(...up_), wall: Math.hypot(...uw_) };
}
console.log('SWEEP KINK: image-motion difference per mm of sweep, beta = 32 deg. K = |u_wall - u_plate| / (|u_wall| + |u_plate|)');
console.log('psi = azimuth of the camera off the section plane (0: looking within the radial-vertical plane from the bore side; 90: along the tangent)');
console.log('el\\psi   ' + [0, 30, 60, 75, 90].map(x => String(x).padStart(7)).join(''));
for (const el of [5, 15, 30, 45, 58, 70]) console.log(String(el).padStart(4) + '     ' + [0, 30, 60, 75, 90].map(psi => kinkStrength(psi, el, 32).K.toFixed(2).padStart(7)).join(''));
const px = 0.05, sig = 0.3;   // 0.05 mm per pixel, 0.3 px localisation noise (illustrative)
for (const [psi, el] of [[90, 5], [60, 15], [30, 30], [0, 58], [0, 10]]) { const k = kinkStrength(psi, el, 32); console.log('camera psi ' + psi + ', el ' + el + ': |du| = ' + k.dv.toFixed(2) + ' image-mm per mm -> corner located to about ' + (k.dv > 0.02 ? (sig * px / k.dv / 3).toFixed(3) + ' mm (1 sigma, ~9 samples on each side)' : 'not at all (degenerate)')); }
console.log('\nBOUNCE: gain in radial sensitivity when the pair separation is read instead of the single dot against the corner (beta = 32 deg)');
for (const [psi, el] of [[0, 5], [0, 15], [0, 45], [60, 15], [90, 5]]) {
  const b = basis(psi, el), cot = 1 / Math.tan(32 * D), single = Math.hypot(...P(b, [1, 0, 0])), pair = Math.hypot(...[0, 1].map(i => P(b, [0, 0, cot])[i] + P(b, [1, 0, 0])[i]));
  console.log('camera psi ' + psi + ', el ' + el + ': single dot ' + single.toFixed(3) + ' , pair ' + pair.toFixed(3) + ' image-mm per mm of offset; gain x' + (pair / Math.max(single, 1e-6)).toFixed(1));
}
console.log('\nBrightness ratio bounce / direct = R * spec (R = plate reflectance at 650 nm, ILLUSTRATIVE 0.6; spec = specular fraction of the reflection).');
for (const spec of [0.2, 0.5, 0.8, 0.95]) console.log('spec ' + spec + ': ratio ' + (0.6 * spec).toFixed(2));
