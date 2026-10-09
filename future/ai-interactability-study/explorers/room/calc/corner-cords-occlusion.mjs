// corner-cords-occlusion.mjs - do the eight cords cross the cage-top camera's sight line to the dot (or to the spot on the plate)?
// room-06's scene draws the cords as non-occluding; eyes (wave 2) noted nothing says whether one crosses the view.
// Sight line: camera at (20, -40, 700) [as drawn in the scene] to the dot. A cord blocks it if the closest approach of the two
// segments is under (cord radius + half a spot) = 0.65 + 0.5 mm. Cords: nominal geometry, lug on the shell -> anchor in the cage.
// [illustrative] cord radius, camera place. Run: node explorers/room/calc/corner-cords-occlusion.mjs [poses=400]
import { world } from './pose.mjs';
import { V, M3, cordGeometry, rng } from './cdpr-core.mjs';
import { lugs, anchors as cage } from './corner-cords-pairing-search.mjs';

const pairing = [6, 0, 1, 4, 5, 7, 2, 3], anch = pairing.map(k => cage[k]), dotLocal = [0, 0, -16];
const dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R0 = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const p0 = world(dotLocal, dl.roll, dl.hole, dl.vert);
const cams = { 'cage top (20,-40,700)': [20, -40, 700], 'cage top, over the shell (-60,-20,700)': [-60, -20, 700], 'off to the +Y side (20,300,600)': [20, 300, 600] };

function segDist(p1, q1, p2, q2) {     // closest distance between segments p1q1 and p2q2
  const d1 = V.sub(q1, p1), d2 = V.sub(q2, p2), r = V.sub(p1, p2), a = V.dot(d1, d1), e = V.dot(d2, d2), f = V.dot(d2, r);
  const c = V.dot(d1, r), b = V.dot(d1, d2), den = a * e - b * b;
  let s = den > 1e-12 ? Math.min(1, Math.max(0, (b * f - c * e) / den)) : 0, t = (b * s + f) / e;
  if (t < 0) { t = 0; s = Math.min(1, Math.max(0, -c / a)); } else if (t > 1) { t = 1; s = Math.min(1, Math.max(0, (b - c) / a)); }
  return V.len(V.sub(V.add(p1, V.scl(d1, s)), V.add(p2, V.scl(d2, t))));
}
const NPOSE = +(process.argv[2] || 400), r = rng(7);
const results = {}; Object.keys(cams).forEach(k => { results[k] = { blocked: 0, byCord: new Array(8).fill(0), tot: 0, mins: [] }; });
let skipped = 0;
for (let k = 0; k < NPOSE; k++) {
  const shift = [(r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 25, (r.u() * 2 - 1) * 15];
  const R = M3.mul(M3.rodrigues([0, 1, 2].map(() => (r.u() * 2 - 1) * 4 * Math.PI / 180)), R0), p = V.add(p0, shift);
  const tip = V.add(p, M3.mulV(R, [0, 0, 16]));
  if (Math.hypot(tip[0], tip[1]) > 58.85) { skipped++; continue; }      // nozzle tip must stay inside the bore
  const geo = cordGeometry(anch, lugs, dotLocal, { p, R });
  for (const [name, cpos] of Object.entries(cams)) {
    const res = results[name]; res.tot++;
    let hit = false, best = 1e9;
    geo.forEach((g, i) => { const d = segDist(cpos, p, g.lugW, g.anchor); best = Math.min(best, d); if (d < 1.15) { hit = true; res.byCord[i]++; } });
    if (hit) res.blocked++; res.mins.push(best);
  }
}
console.log(`${NPOSE} random poses in room-06's range (${skipped} skipped: tip outside the bore); a cord blocks if it passes within 1.15 mm of the sight line`);
for (const [name, res] of Object.entries(results)) {
  const m = res.mins.sort((a, b) => a - b);
  console.log(`  ${name.padEnd(40)} blocked in ${res.blocked} of ${res.tot} poses (${(100 * res.blocked / res.tot).toFixed(1)} %); closest approach median ${m[Math.floor(m.length / 2)].toFixed(1)} mm, min ${m[0].toFixed(2)} mm; by cord ${res.byCord.join(' ')}`);
}
