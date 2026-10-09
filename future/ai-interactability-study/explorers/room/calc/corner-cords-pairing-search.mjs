// Which lug goes to which corner anchor? A hand pairing failed (every cord turned the gun the same way about x), so this
// searches all 8! pairings at the nominal pose for wrench feasibility (gun weight + 2 N umbilical pulls, tension >= tMin),
// then ranks survivors by their worst minimum-tension margin over sampled poses.  Illustrative geometry (see corner-cords.mjs).
// Run: node explorers/room/calc/corner-cords-pairing-search.mjs
import { world, ANCHORS } from './pose.mjs';
import { V, M3, cordGeometry, solveTensions, rng } from './cdpr-core.mjs';
const dotLocal = [0, 0, -16];
function poseFromDials(dl, shift = [0, 0, 0], dw = [0, 0, 0]) {
  const o = world([0, 0, 0], dl.roll, dl.hole, dl.vert);
  let R = M3.fromColumns(V.sub(world([1, 0, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 1, 0], dl.roll, dl.hole, dl.vert), o), V.sub(world([0, 0, 1], dl.roll, dl.hole, dl.vert), o));
  if (dw[0] || dw[1] || dw[2]) R = M3.mul(M3.rodrigues(dw), R);
  return { R, p: V.add(world(dotLocal, dl.roll, dl.hole, dl.vert), shift) };
}
const dials = { roll: 45, hole: 30, vert: -15 };
const LUGSCALE = +(process.env.LUGSCALE || 1), COMC = [0, -23, 181];   // >1: lugs on outrigger arms, scaled about the centre of mass
export const lugs = [[-16, 0, 109], [16, 0, 109], [-20, 20, 150], [20, 20, 150], [-20, 20, 235], [20, 20, 235], [-18, -118, 237], [18, -118, 237]].map(l => l.map((v, i) => COMC[i] + LUGSCALE * (v - COMC[i])));
const CAGE = (process.env.CAGE || '350,650,170').split(',').map(Number);   // half-width, top, low (mm); default is the 0.7 m cage of the scene
export const anchors = [[CAGE[0], CAGE[0], CAGE[1]], [-CAGE[0], CAGE[0], CAGE[1]], [-CAGE[0], -CAGE[0], CAGE[1]], [CAGE[0], -CAGE[0], CAGE[1]], [CAGE[0], -CAGE[0], CAGE[2]], [-CAGE[0], -CAGE[0], CAGE[2]], [-CAGE[0], CAGE[0], CAGE[2]], [CAGE[0], CAGE[0], CAGE[2]]];
const mass = 1.47, comLocal = [0, -23, 181], g = 9.81;
function feasible(perm, pose, tMin, Fu) {
  const anc = perm.map(k => anchors[k]);
  const geo = cordGeometry(anc, lugs, dotLocal, pose);
  const com = V.add(pose.p, M3.mulV(pose.R, V.sub(comLocal, dotLocal)));
  const grip = V.add(pose.p, M3.mulV(pose.R, V.sub(ANCHORS.gripBase, dotLocal)));
  const Fg = [0, 0, -mass * g];
  const F = V.add(Fg, Fu), Mo = V.cross(V.sub(grip, com), Fu);
  return solveTensions(geo, com, F, Mo, tMin);
}
function perms(a) { if (a.length <= 1) return [a]; const out = []; a.forEach((x, i) => perms(a.slice(0, i).concat(a.slice(i + 1))).forEach(p => out.push([x].concat(p)))); return out; }
// a cord must not run through the gun's own shell: sample its first 160 mm and test against the proxy solids (kit numbers, +3 mm sleeve)
const gripStart = [0, -25, 172], gripEnd = [0, -111, 232];
const gripLen = V.len(V.sub(gripEnd, gripStart)), gripDir = V.unit(V.sub(gripEnd, gripStart));
function insideGun(q) {   // q in gun-local coordinates
  const rad = Math.hypot(q[0], q[1]);
  if (q[2] >= -2 && q[2] <= 118 && rad < (q[2] < 23 ? 5.2 + 3 : q[2] < 54 ? 11.5 : q[2] < 100 ? 8.5 : 15)) return true;
  if (Math.abs(q[0]) < 20 && Math.abs(q[1]) < 20 && Math.abs(q[2] - 185.5) < 70.5) return true;
  const c = V.scl(V.add(gripStart, gripEnd), 0.5), d = V.sub(q, c), along = V.dot(d, gripDir);
  const perp = V.sub(d, V.scl(gripDir, along)); const across = Math.abs(perp[0]);
  const third = Math.abs(V.dot(perp, V.unit(V.cross(gripDir, [1, 0, 0]))));
  if (Math.abs(along) < gripLen / 2 + 8 + 3 && across < 18 && third < 17) return true;
  return false;
}
export function cordsClearGun(perm, pose) {
  const anc = perm.map(k => anchors[k]);
  const Rinv = [0, 1, 2].map(i => [0, 1, 2].map(j => pose.R[j][i]));
  for (let i = 0; i < lugs.length; i++) {
    const lugW = V.add(pose.p, M3.mulV(pose.R, V.sub(lugs[i], dotLocal)));
    const u = V.unit(V.sub(anc[i], lugW));
    for (let s = 6; s <= 160; s += 6) { const q = V.add(dotLocal, M3.mulV(Rinv, V.sub(V.add(lugW, V.scl(u, s)), pose.p))); if (insideGun(q)) return false; }
  }
  return true;
}
const nominal = poseFromDials(dials);
const RUN = process.argv[1] && process.argv[1].endsWith('corner-cords-pairing-search.mjs');
const all = RUN ? perms([0, 1, 2, 3, 4, 5, 6, 7]) : [];
const survivors = [];
for (const p of all) { if (!cordsClearGun(p, nominal)) continue; const r = feasible(p, nominal, 5, [0, 0, 0]); if (r.feasible) survivors.push(p); }
if (RUN) console.log('pairings whose cords leave the shell clear AND are feasible at the nominal pose with 5 N minimum pretension and gun weight only:', survivors.length, 'of', all.length);
const R = rng(7);
const samples = []; for (let i = 0; i < 12; i++) samples.push(poseFromDials(dials, [(R.u() * 2 - 1) * 25, (R.u() * 2 - 1) * 25, (R.u() * 2 - 1) * 15], [0, 1, 2].map(() => (R.u() * 2 - 1) * 4 * Math.PI / 180)));
const dirs = [[2, 0, 0], [-2, 0, 0], [0, 2, 0], [0, -2, 0], [0, 0, 2], [0, 0, -2]];
const scored = [];
for (const p of survivors) {
  let good = 0, tot = 0;
  for (const s of samples) for (const d of dirs) { tot++; const r = feasible(p, s, 5, d); if (r.feasible && Math.max(...r.t) < 150) good++; }
  scored.push({ p, frac: good / tot });
}
scored.sort((a, b) => b.frac - a.frac);
if (RUN) console.log('best pairings (lug i -> anchor index), fraction of sampled (pose, umbilical-direction) cases held with all cords in [5,150] N:');
if (RUN) scored.slice(0, 8).forEach(s => console.log('  ', s.p.join(' '), (s.frac * 100).toFixed(0) + '%'));
if (RUN) console.log('median fraction over survivors:', scored.length ? (scored[Math.floor(scored.length / 2)].frac * 100).toFixed(0) + '%' : '-');
