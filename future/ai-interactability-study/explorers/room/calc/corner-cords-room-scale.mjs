// The corner-cords structure at three cage sizes: does the same lug-to-anchor pairing still hold the gun, and how does the
// weakest translational stiffness change with cord length?  Same illustrative gun and lines as corner-cords.mjs.
// Run: node explorers/room/calc/corner-cords-room-scale.mjs
import { world, ANCHORS } from './pose.mjs';
import { V, M3, cordGeometry, solveTensions, stiffness3, eig3 } from './cdpr-core.mjs';
import { lugs } from './corner-cords-pairing-search.mjs';
const dotLocal = [0, 0, -16], dl = { roll: 45, hole: 30, vert: -15 };
const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
const R = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
const pose = { R, p: world(dotLocal, dl.roll, dl.hole, dl.vert) };
const com = V.add(pose.p, M3.mulV(R, V.sub([0, -23, 181], dotLocal)));
const grip = V.add(pose.p, M3.mulV(R, V.sub(ANCHORS.gripBase, dotLocal)));
const pairing = [6, 0, 1, 4, 5, 7, 2, 3];
for (const [name, half, top, low] of [['0.7 m cage (scene)', 350, 650, 170], ['1.2 m cage', 600, 1100, 250], ['room: 2.4 x 2.4 m, ceiling 2.3 m', 1200, 2300, 300]]) {
  const cage = [[half, half, top], [-half, half, top], [-half, -half, top], [half, -half, top], [half, -half, low], [-half, -half, low], [-half, half, low], [half, half, low]];
  const anch = lugs.map((_, i) => cage[pairing[i]]);
  const geo = cordGeometry(anch, lugs, dotLocal, pose);
  const sol = solveTensions(geo, com, [0, -0, -14.4], [0, 0, 0], 5);
  const Fu = [0, -2, 0], sol2 = solveTensions(geo, com, [0, -2, -14.4], V.cross(V.sub(grip, com), Fu), 5);
  const K = stiffness3(geo, sol.t, 6e4), e = eig3(K);
  const Lmean = geo.reduce((s, g) => s + g.L, 0) / geo.length;
  const maxHoriz = Math.max(...sol.t.map((t, i) => t * Math.hypot(geo[i].u[0], geo[i].u[1])));
  console.log(name.padEnd(36), 'mean cord length', Lmean.toFixed(0), 'mm  feasible:', sol.feasible, '(with 2 N pull:', sol2.feasible + ')', ' tensions', Math.min(...sol.t).toFixed(1), 'to', Math.max(...sol.t).toFixed(1), 'N',
    ' weakest stiffness', e.values[0].toFixed(0), 'N/mm (EA 60 kN)', ' largest horizontal cord load at an anchor', maxHoriz.toFixed(1), 'N');
}
