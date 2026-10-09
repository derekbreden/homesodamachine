// Wave 2: travel-16's yoke pivot as the end-of-bead escape. Kit proxy gun in pose B (roll 0, hole dial 35, vertical -90):
// barrel in the radial plane over the bore. Trunnions on the housing sides (gun-local x axis through the housing centre, z 185.5).
// Rotate the gun about the trunnion axis and see what the nozzle does and how far the tip leaves the puddle point.
// Everything is the kit's ILLUSTRATIVE proxy; nothing is measured. Usage: node calc/w2_yoke.mjs
import { world, ANCHORS, sub, add, mul, unit, norm, cross, dot, fmt, DEG, RI, RO, RIM_Z, rotAbout } from './pose.mjs';

const POSES = { B: [0, 35, -90], B2: [0, 95, 90], A: [45, 30, -15] };
for (const [name, d] of Object.entries(POSES)) {
  const W = l => world(l, ...d);
  const nz = W(ANCHORS.nozzleTip), dt = W(ANCHORS.dot);
  const tr = W([0, 0, 185.5]), trx = W([17, 0, 185.5]), trn = W([-17, 0, 185.5]);
  const axis = unit(sub(trx, trn));
  const beam = unit(sub(dt, nz));
  console.log(`\npose ${name}: nozzle ${fmt(nz)} dot ${fmt(dt)} beam ${fmt(beam, 3)} angle from vertical ${(Math.acos(-beam[2]) / DEG).toFixed(1)} deg`);
  console.log(`  trunnion centre ${fmt(tr)} axis ${fmt(axis, 3)} lever nozzle-trunnion ${norm(sub(nz, tr)).toFixed(0)} mm, dot-trunnion ${norm(sub(dt, tr)).toFixed(0)} mm`);
  console.log(`  tip above rim ${(nz[2] - RIM_Z).toFixed(1)} mm, tip radius from axis ${Math.hypot(nz[0], nz[1]).toFixed(1)} mm`);
  if (name === 'A') continue;
  for (const sgn of [+1, -1]) {
    console.log(`  rotate ${sgn > 0 ? '+' : '-'} about the trunnion axis:`);
    for (const th of [5, 10, 15, 20, 30]) {
      const p = rotAbout(nz, tr, axis, sgn * th * DEG), bd = rotAbout(add(nz, beam), tr, axis, sgn * th * DEG), b2 = unit(sub(bd, p));
      const stand = norm(sub(p, dt));                 // distance from the nozzle to the original puddle point
      const rad = Math.hypot(p[0], p[1]);
      console.log(`    ${String(th).padStart(2)} deg: nozzle ${fmt(p)}  tip above rim ${(p[2] - RIM_Z).toFixed(1)}  radius ${rad.toFixed(1)}  distance to the puddle point ${stand.toFixed(1)} (was 16.0)  beam ${(Math.acos(-b2[2]) / DEG).toFixed(1)} deg from vertical`);
    }
  }
  // return-seat amplification: angular repeatability at the stop -> dot
  for (const dth of [0.02, 0.05, 0.1]) console.log(`  a stop repeatable to ${dth} deg moves the dot ${(norm(sub(dt, tr)) * dth * DEG).toFixed(3)} mm`);
}
// plunge alternative in pose B: along the beam
console.log('\nCompare: 20 mm along the beam is 20 mm of standoff by definition; the yoke pivot gives the same standoff growth for the angle above.');
