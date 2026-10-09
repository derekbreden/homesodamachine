// view-sensitivity.mjs  (eyes)
// A camera at elevation eps above the plate plane, on the bore side, looking radially at the dot.
// A small displacement d of the dot's target on the surface shows up in the image with size |d x v| where v is the
// unit viewing direction (component along the ray is invisible). For plate-radial (x) and wall-vertical (z) offsets:
//   radial sensitivity  = sin(eps)      vertical sensitivity = cos(eps)        [derived: pure geometry]
// Also: how low can a camera across the bore be and still clear the far rim?
const RI = 61.85, RO = 63.5, dz = 6.35;
console.log('eps deg | radial sens | vertical sens | mm of radial error per image mm');
for (const e of [3, 5, 10, 20, 30, 45, 60, 75, 90]) {
  const r = Math.sin(e * Math.PI / 180), z = Math.cos(e * Math.PI / 180);
  console.log([e, r.toFixed(3), z.toFixed(3), (1 / r).toFixed(1)].join(' | '));
}
const minEl = Math.atan(dz / (RI + RO)) * 180 / Math.PI;
console.log('\nLowest elevation at which a camera outside the far rim still sees the dot over that rim: atan(6.35 / (61.85 + 63.5)) = ' + minEl.toFixed(2) + ' deg');
console.log('At 300 mm from the dot that is a camera only ' + (300 * Math.tan(minEl * Math.PI / 180)).toFixed(0) + ' mm above the dot height.');
