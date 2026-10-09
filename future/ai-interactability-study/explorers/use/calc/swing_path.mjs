// A4 swing head: which post position and swing direction let the gun leave the tube-swap volume,
// and what does a swing do if the plunge has NOT been retracted first?
// Everything here is the kit's ILLUSTRATIVE gun proxy and ILLUSTRATIVE keep-out numbers.
// Usage: node calc/swing_path.mjs
import { world, ANCHORS, sub, add, mul, unit, norm, fmt, DEG, RI, RO, RIM_Z, CAP_TOP, IN } from './pose.mjs';

const DIALS = [45, 30, -15];                       // reference scene's opening pose [illustrative]
const W = l => world(l, ...DIALS);
const nozzle = W(ANCHORS.nozzleTip), dotW = W(ANCHORS.dot);
const beam = unit(sub(dotW, nozzle));              // nozzle -> dot
const back = mul(beam, -1);                        // "straight away" = along the beam axis, backwards

// gun proxy sample points (local coords) with a sample radius: barrel cylinders, housing box corners, grip
function samples() {
  const s = [];
  const cyl = (z0, z1, r0, r1, n) => { for (let i = 0; i <= n; i++) { const t = i / n; s.push({ p: [0, 0, z0 + (z1 - z0) * t], r: r0 + (r1 - r0) * t }); } };
  cyl(0, 23, 2.2, 5, 4); cyl(23, 54, 8.5, 8.5, 4); cyl(54, 100, 5.5, 5.5, 6); cyl(100, 118, 12, 12, 3);
  for (const x of [-17, 17]) for (const y of [-17, 17]) for (const z of [118, 185.5, 253]) s.push({ p: [x, y, z], r: 0 });
  for (let i = 0; i <= 8; i++) { const t = i / 8; s.push({ p: [0, -25 + (-111 + 25) * t, 172 + (232 - 172) * t], r: 15 }); }
  s.push({ p: [0, -118, 237], r: 6 });
  return s;
}
const S = samples().map(o => ({ w: W(o.p), r: o.r }));

// tube solids (fixed): wall annulus and plate disc. Distance from point to solid (<0 = inside).
const distTube = p => {
  const rho = Math.hypot(p[0], p[1]);
  const dWall = Math.hypot(Math.max(0, RI - rho, rho - RO), Math.max(0, -p[2], p[2] - RIM_Z));
  const insideWall = rho > RI && rho < RO && p[2] > 0 && p[2] < RIM_Z;
  const dPlate = Math.hypot(Math.max(0, rho - RI), Math.max(0, CAP_TOP - 6.35 - p[2], p[2] - CAP_TOP));
  const insidePlate = rho < RI && p[2] > CAP_TOP - 6.35 && p[2] < CAP_TOP;
  return Math.min(insideWall ? -1 : dWall, insidePlate ? -1 : dPlate);
};
// keep-out swap volume: cylinder r = 95 mm from z = -20 up to rim + 25 lift + 40 hand clearance [illustrative]
const SWAP = { r: 95, z0: -20, z1: RIM_Z + 25 + 40 };
const distSwap = p => {
  const rho = Math.hypot(p[0], p[1]);
  const dr = rho - SWAP.r, dz = Math.max(SWAP.z0 - p[2], p[2] - SWAP.z1);
  if (dr < 0 && dz < 0) return Math.max(dr, dz);           // inside: negative depth
  return Math.hypot(Math.max(0, dr), Math.max(0, dz));
};

function pose(plunge, theta, post) {   // plunge along `back`, then rotate about vertical axis through post by theta (rad, ccw from above)
  const c = Math.cos(theta), s = Math.sin(theta);
  return p => {
    const q = add(p, mul(back, plunge));
    const dx = q[0] - post[0], dy = q[1] - post[1];
    return [post[0] + dx * c - dy * s, post[1] + dx * s + dy * c, q[2]];
  };
}
function evalPose(plunge, theta, post) {
  const f = pose(plunge, theta, post);
  let minTube = Infinity, minSwap = Infinity, worstT = null;
  for (const o of S) {
    const p = f(o.w); const dt = distTube(p) - o.r, ds = distSwap(p) - o.r;
    if (dt < minTube) { minTube = dt; worstT = p; }
    minSwap = Math.min(minSwap, ds);
  }
  return { minTube, minSwap, worstT };
}

console.log('beam dir (nozzle->dot)', fmt(beam, 3), ' plunge axis (straight away)', fmt(back, 3));
console.log('nozzle', fmt(nozzle), 'dot', fmt(dotW));
console.log('\nSeated pose clearance to tube solids (mm, sample radius subtracted):', evalPose(0, 0, [0, -330]).minTube.toFixed(1));
for (const p of [10, 20, 30, 40]) console.log(' plunge', p, 'mm ->', evalPose(p, 0, [0, -330]).minTube.toFixed(1), 'mm clear of tube; nozzle z', (nozzle[2] + back[2] * p).toFixed(1));

const posts = [[0, -330], [150, -330], [250, -250], [300, -100], [-150, -330], [-300, -150], [200, 0], [150, 200]];
for (const post of posts) {
  console.log('\nPost at', post.join(', '), ' R(nozzle) =', Math.hypot(nozzle[0] - post[0], nozzle[1] - post[1]).toFixed(0));
  for (const sign of [+1, -1]) {
    const row = [];
    for (const plunge of [0, 25, 40]) {
      let minTube = Infinity, firstOut = null, ok = true;
      for (let a = 0; a <= 120; a += 1) {
        const r = evalPose(plunge, sign * a * DEG, post);
        minTube = Math.min(minTube, r.minTube);
        if (firstOut == null && r.minSwap > 0) firstOut = a;
      }
      row.push(`plunge ${plunge}: min tube clearance over 0..120 deg = ${minTube.toFixed(1)}, clears swap volume from ${firstOut == null ? 'never' : firstOut + ' deg'}`);
    }
    console.log(sign > 0 ? ' swing +ccw' : ' swing -cw ', '\n   ' + row.join('\n   '));
  }
}
