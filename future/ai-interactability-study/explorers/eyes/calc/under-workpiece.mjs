// under-workpiece.mjs (eyes) - can a camera below the rotator see the slip gap of the FIRST closure as a ring of light?
// Sources: plate thickness 6.35 mm, slip 0.005 in radial (0.127 mm) [repo pressure-vessel.md, endcap_circular_dxf.py];
//          service bore Ø90 mm in nest, turntable and base [repo weld-rotation-rig.md]; weld circle radius 61.85 mm [repo].
// Everything else is arithmetic.
const t = 6.35, gap = 0.127, RI = 61.85, boreR = 45;
const accept = Math.atan(gap / t) * 180 / Math.PI;
console.log('The gap is a slot ' + t + ' mm deep and ' + gap + ' mm wide: light passes only within +-' + accept.toFixed(2) + ' deg of the axis (straight-through limit).');
console.log('A camera on the axis sees the slot at radius ' + RI + ' mm at a ray angle atan(r / distance) from the axis:');
for (const d of [150, 300, 600, 1500, 3000]) console.log('  camera ' + d + ' mm below the plate underside: ray angle ' + (Math.atan(RI / d) * 180 / Math.PI).toFixed(2) + ' deg  -> ' + (Math.atan(RI / d) * 180 / Math.PI <= accept ? 'passes' : 'blocked by the slot walls'));
console.log('Distance at which the edge of the plate is seen within the acceptance angle: ' + (RI / Math.tan(accept * Math.PI / 180) / 1000).toFixed(1) + ' m. A telecentric lens (parallel rays) removes the distance but its front element must be as wide as the plate (about 125 mm).');
// through the service bore: the bore radius bounds the field from below unless the camera is close
const H = 140;   // mm from the bore plane to the plate underside, ILLUSTRATIVE (tube 152 mm, plate near the top, turntable and base thickness ignored)
console.log('\nField through a Ø90 mm bore (bore plane ' + H + ' mm below the plate, illustrative): radius seen at the plate = 45 (d + H) / d for a camera at d below the bore plane');
for (const d of [50, 100, 200, 350, 600]) console.log('  d = ' + d + ' mm: ' + (boreR * (d + H) / d).toFixed(0) + ' mm radius' + (boreR * (d + H) / d >= RI ? ' (reaches the plate edge)' : ' (does not reach the edge)'));
// thermal view: how long does the heat take to cross the 6.35 mm plate?
const alpha = 4.0e-6;   // m^2/s, austenitic stainless near room temperature (textbook order of magnitude; illustrative)
console.log('\nHeat crossing the plate: L^2 / alpha = ' + ((t * 1e-3) ** 2 / alpha).toFixed(1) + ' s (alpha ' + alpha + ' m^2/s, illustrative): an infrared view of the underside lags the bead by about that long, i.e. about ' + (8 * (t * 1e-3) ** 2 / alpha).toFixed(0) + ' mm of arc at 8 mm/s, and blurs it.');
