// Extra checks on the best pairings from corner-cords-pairing-search.mjs: do cords leave the shell outward, do cords keep
// apart from each other, and do they clear the tube?  Illustrative geometry.  Run: node explorers/room/calc/corner-cords-pairing-checks.mjs
import { world, ANCHORS, RO, RIM_Z } from './pose.mjs';
import { V, M3, cordGeometry } from './cdpr-core.mjs';
import { lugs, anchors } from './corner-cords-pairing-search.mjs';
const dotLocal = [0, 0, -16];
const dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const pose = { R, p: world(dotLocal, dl.roll, dl.hole, dl.vert) };
// outward normals of the lugs in local frame (sleeve faces)
const normals = [[-1, 0, 0], [1, 0, 0], [-1, 0.3, 0], [1, 0.3, 0], [-1, 0.3, 0], [1, 0.3, 0], [-1, 0, 0], [1, 0, 0]].map(n => V.unit(n));
function segDist(p1, q1, p2, q2) {   // min distance between segments (sampled; fine for a check)
  let best = 1e9;
  for (let i = 0; i <= 60; i++) { const a = V.add(p1, V.scl(V.sub(q1, p1), i / 60)); for (let j = 0; j <= 60; j++) { const b = V.add(p2, V.scl(V.sub(q2, p2), j / 60)); best = Math.min(best, V.len(V.sub(a, b))); } }
  return best;
}
const list = [[0, 1, 2, 4, 5, 7, 3, 6], [0, 1, 2, 4, 5, 7, 6, 3], [0, 1, 2, 7, 4, 6, 3, 5], [0, 1, 3, 5, 4, 7, 6, 2], [0, 1, 4, 5, 3, 7, 2, 6]];
for (const perm of list) {
  const anc = perm.map(k => anchors[k]);
  const geo = cordGeometry(anc, lugs, dotLocal, pose);
  const outward = geo.map((g, i) => V.dot(g.u, M3.mulV(R, normals[i])));
  let minSep = 1e9;
  for (let i = 0; i < 8; i++) for (let j = i + 1; j < 8; j++) minSep = Math.min(minSep, segDist(geo[i].lugW, geo[i].anchor, geo[j].lugW, geo[j].anchor));
  let minTube = 1e9;
  geo.forEach(g => { for (let k = 0; k <= 300; k++) { const p = V.add(g.lugW, V.scl(V.sub(g.anchor, g.lugW), k / 300)); if (p[2] < RIM_Z + 20) minTube = Math.min(minTube, Math.hypot(p[0], p[1]) - RO); } });
  console.log(perm.join(' '), ' outward-normal dot per cord', outward.map(v => v.toFixed(2)).join(' '), ' min cord-cord distance', minSep.toFixed(1), 'mm; min plan gap to tube below rim+20', minTube > 1e8 ? 'n/a' : minTube.toFixed(0) + ' mm');
}
