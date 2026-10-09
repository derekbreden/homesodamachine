// umbilical-gauge.mjs (eyes, wave 3) - freedom's question on eyes-11b: "with beads every 200 mm and a camera at 1 to 2 m, what force change would your curve fit resolve?
// my number: 1 mm of shape is 0.3 to 56 mN for EI 0.05 to 0.5 N m^2 and 0.3 to 0.8 m of free length; is your 1 mm real?"
// Model (ILLUSTRATIVE): a free length L of fibre held as a cantilever at the hook end and loaded at the gun end; small-deflection tip stiffness 3 EI / L^3.
// Force per mm of shape = 3 EI / L^3 (N per m = mN per mm). The camera: HFOV, pixels across, distance; bead centroid noise in pixels.
const args = Object.fromEntries(process.argv.slice(2).map(a => a.replace(/^--/, '').split('=')));
const hfov = +(args.hfov || 60), W = +(args.w || 3840), sig = +(args.sig || 0.3);
console.log('force per mm of shape change at the free end, 3 EI / L^3 (mN per mm):');
console.log('            L = 0.3 m   0.5 m    0.8 m');
for (const EI of [0.05, 0.15, 0.5]) console.log('  EI ' + EI.toFixed(2) + '   ' + [0.3, 0.5, 0.8].map(L => (3 * EI / Math.pow(L, 3)).toFixed(1).padStart(8)).join(''));
console.log('\ncamera: HFOV ' + hfov + ' deg, ' + W + ' px across, bead centroid ' + sig + ' px');
for (const d of [1.0, 1.5, 2.0]) { const mmpx = 2 * d * 1000 * Math.tan(hfov * Math.PI / 360) / W; console.log('  distance ' + d.toFixed(1) + ' m: ' + mmpx.toFixed(2) + ' mm per pixel, bead in the image plane to ' + (mmpx * sig).toFixed(2) + ' mm; a 4-bead fit with a fixed hook and the gun exit known: about ' + (mmpx * sig / 2).toFixed(2) + ' mm of shape'); }
console.log('\nwhat that resolves: 0.15 to 0.45 mm of in-plane shape = ' + (0.15 * 0.3).toFixed(2) + ' to ' + (0.45 * 56).toFixed(0) + ' mN across the whole EI and L range: one to two orders below the 0.5 to 2 N pull change that matters (freedom-15).');
console.log('what it does NOT resolve: (1) the direction along the camera axis: a single camera sees one plane, so a fibre that bends toward or away from it is invisible; two cameras or a mirror are needed for depth; (2) hysteresis: the shape at a pose depends on how the fibre got there, so shape-to-force needs a table made by pulling a spring scale at the exit at several poses, and a flag when the shape is off that table; (3) the gun exit pose itself: 1 mm of exit error is 1 mm of shape.');
console.log('so the gauge is not camera-limited; it is depth- and hysteresis-limited.');
