// 09 - what a gun that need not lie along the tangent could do (exchange on datum-09-preplaced-filler-ring, with datum-03 and datum-03b).
// The kit's proxy gun in two attitudes (cable exit direction = the kit's: along the line from the dot through the grip base)
// The kit's proxy gun in two attitudes about the same dot: A = the reference scene's opening pose (barrel along the tangent, wire arrives
// from the -y side); B = barrel in the radial plane, over the bore (dials roll 0, hole 35, vertical -90: the far end of the reference
// scene's own 'vertical' range). Gun geometry, mass split and cable exit are the kit's ILLUSTRATIVE proxy, not measured.
// Run: node explorers/travel/calc/09-radial-plane.mjs
import { ANCHORS, ROLL_AXIS, world, sub, add, mul, dot3, cross, norm, unit, fmt, RIM_Z, JOINT, DEG, INNER_RADIUS } from './lib.mjs';

const POSES = {
  'A  opening pose, barrel tangent (fed wire)': { roll: 45, hole: 30, vert: -15 },
  'B  radial plane, over the bore (no wire)   ': { roll: 0, hole: 35, vert: -90 },
  'B2 radial plane, grip up, over the axis    ': { roll: 0, hole: 95, vert: 90 },
};
const P = (name, d) => world(ANCHORS[name] || name, d.roll, d.hole, d.vert);
function cog(d) {                                   // the same three-point mass split as scenes/datum-03-rim-crown (0.15 / 0.55 / 0.30)
  const pts = [[[0, 0, 60], 0.15], [[0, 0, 185.5], 0.55], [ANCHORS.gripMid, 0.30]];
  let c = [0, 0, 0]; for (const [p, w] of pts) c = add(c, mul(world(p, d.roll, d.hole, d.vert), w)); return c;
}
console.log('1. Where the gun is, per attitude (kit proxy)\n');
console.log('pose'.padEnd(46), 'COM r (mm)', 'tip r', 'tip over rim', 'beam in-section / along-tangent tilt (deg from vertical)', ' grip base r, height over rim, exit direction');
const rows = {};
for (const [name, d] of Object.entries(POSES)) {
  const c = cog(d), tip = P('nozzleTip', d), dt = P('dot', d), b = unit(sub(dt, tip));
  const gb = P('gripBase', d), cd = unit(sub(world(add(ANCHORS.gripBase, mul(ROLL_AXIS, 100)), d.roll, d.hole, d.vert), gb));   // the kit's cable exit direction: along the dot-to-grip-base line, away from the dot
  rows[name] = { d, c, tip, b, gb, cd };
  console.log(name.padEnd(46), fmt(Math.hypot(c[0], c[1]), 0).padStart(9), fmt(Math.hypot(tip[0], tip[1]), 1).padStart(8), fmt(tip[2] - RIM_Z, 1).padStart(9),
    ('   ' + fmt(Math.atan2(b[0], -b[2]) / DEG, 1) + ' / ' + fmt(Math.atan2(b[1], -b[2]) / DEG, 1)).padEnd(38), ' r ' + fmt(Math.hypot(gb[0], gb[1]), 0) + ', ' + fmt(gb[2] - RIM_Z, 0) + ', dir (' + cd.map(v => fmt(v, 2)).join(', ') + ')');
}
console.log('\n   The crown of scenes/datum-03-rim-crown balances the gun about its ball ring (radius 66 mm): A has the centre of mass 118 mm out, which is why');
console.log('   round 3 there needs a counterweight about as heavy as the gun. B has it about 50 mm out, inside the ring.\n');

// 2. yaw is not free even with no wire: it turns the beam. In-section tilt against the vertical dial, other dials held at pose A.
console.log('2. With the pose-A roll and hole dials held, the vertical (yaw) dial changes the beam angle in the radial-vertical section:');
for (const v of [-45, -30, -15, 0, 15, 30]) {
  const d = { roll: 45, hole: 30, vert: v }, tip = P('nozzleTip', d), dt = P('dot', d), b = unit(sub(dt, tip));
  console.log('   vertical dial ' + String(v).padStart(4) + ' deg : in-section tilt ' + fmt(Math.atan2(b[0], -b[2]) / DEG, 1).padStart(5) + ' deg, along-tangent tilt ' + fmt(Math.atan2(b[1], -b[2]) / DEG, 1).padStart(5) + ' deg');
}
console.log('   The in-section tilt sets how much of the beam goes to the wall side and how much to the plate side. What removing the wire frees is the');
console.log('   rotation about the BEAM axis (below), not yaw about the vertical.\n');

// 3. spin about the beam axis: displacement of the grip base per degree, twist fraction of the cable exit, wobble projection
console.log('3. Rotation about the beam axis through the dot (turns the gun about its own optical axis; the round beam does not change)\n');
for (const [name, r] of Object.entries(rows)) {
  const axis = r.b, arm = sub(r.gb, r.tip), perp = norm(cross(arm, axis));
  const twist = Math.abs(dot3(axis, r.cd));
  console.log('   ' + name.trim().slice(0, 44).padEnd(44), ' grip base moves ' + fmt(perp * DEG, 2) + ' mm per degree of spin (lever ' + fmt(perp, 0) + ' mm); fibre twist per degree of spin ' + fmt(twist, 2) + ' deg');
}
console.log('   The wobble sweep (2 mm at 80 Hz in the recorded settings) runs along the gun\'s local x; spin turns it away from across-the-seam: width across the seam x cos(spin):');
for (const s of [5, 10, 20, 30]) console.log('   spin ' + s + ' deg -> ' + fmt(Math.cos(s * DEG) * 100, 1) + ' % of the swing width across the seam (and ' + fmt(Math.sin(s * DEG) * 2, 2) + ' mm of a 2 mm swing along it)');
console.log('   With a fed wire the wire bracket fixes the spin; with none, the wobble direction and the fibre are what limit it. Both numbers are the proxy\'s.\n');

// 4. cable laid flat behind an orbiting gun (datum-03b geometry). The fibre is 5 m; minimum bend radius 350 mm while emitting [manual p.20].
// Construction (G1 continuous, checked): from the exit, in plan, an arc of radius Rb = 350 turning toward the trailing side until the heading is
// perpendicular to the position vector, i.e. tangent to a circle round the tube axis; then that circle (radius Rt = the radius reached) for the orbit angle.
// A quarter turn does not end on a concentric circle (the heading is not tangent to it there), so the route needs the longer turn computed below. The vertical component of the exit (it leaves 30 to 35 degrees above horizontal) is not
// counted here; a level-off bend adds about 0.2 m.
console.log('4. Cable laid flat behind an orbiting gun (datum-03b geometry, G1 route, plan view only)');
const RB = 350, FIBRE = 5000;
function route(pe, he, s) {            // pe exit point (plan), he unit heading (plan), s = +1 turn left (CCW), -1 turn right (CW)
  const th0 = Math.atan2(he[1], he[0]);
  const pos = phi => { const th = th0 + s * phi; return [pe[0] + RB / s * (Math.sin(th) - Math.sin(th0)), pe[1] + RB / s * (Math.cos(th0) - Math.cos(th))]; };
  let prev = null;
  for (let phi = 0.001; phi < 2 * Math.PI; phi += 0.0005) {
    const th = th0 + s * phi, p = pos(phi), f = p[0] * Math.cos(th) + p[1] * Math.sin(th);
    if (prev != null && Math.sign(f) !== Math.sign(prev.f) && prev.phi > 0.05) return { phi: phi, Rt: Math.hypot(p[0], p[1]), arc: RB * phi };
    prev = { f: f, phi: phi };
  }
  return null;
}
for (const [name, r] of Object.entries(rows)) {
  if (name.startsWith('B2')) continue;
  const pe = [r.gb[0], r.gb[1]], he = unit([r.cd[0], r.cd[1], 0]);
  const az = Math.atan2(pe[1], pe[0]), out = [Math.cos(az), Math.sin(az)];
  const lean = Math.atan2(out[0] * he[1] - out[1] * he[0], out[0] * he[0] + out[1] * he[1]) / DEG;   // + = heading leans counterclockwise of radial outward
  console.log('   ' + name.trim() + ': exit at r = ' + fmt(Math.hypot(pe[0], pe[1]), 0) + ' mm, plan heading ' + fmt(lean, 0) + ' deg from radially outward (+ = counterclockwise)');
  for (const [lab, sgn] of [['trailing side clockwise ', -1], ['trailing side counter-clockwise', +1]]) {
    const ro = route(pe, he, sgn);
    if (!ro) continue;
    const t380 = ro.Rt * 380 * DEG, t190 = ro.Rt * 190 * DEG;
    console.log('     ' + lab + ': turn ' + fmt(ro.phi / DEG, 0) + ' deg (arc ' + fmt(ro.arc, 0) + ' mm), then a circle of radius ' + fmt(ro.Rt, 0) + ' mm.  380 deg: ' + fmt((ro.arc + t380) / 1000, 2) + ' m' + (ro.arc + t380 > FIBRE ? ' OVER 5 m' : '') + '   190 deg: ' + fmt((ro.arc + t190) / 1000, 2) + ' m' + (ro.arc + t190 > FIBRE ? ' OVER 5 m' : ''));
  }
}
console.log('   So the exit direction in B is not the fix: both A and B leave the grip base radially outward, need a turn of 140 to 160 degrees before the fibre can');
console.log('   run round the tube, and need about 5.8 to 6 m for a continuous 380 degrees. What the missing wire buys is a bidirectional weld (each half 190 degrees');
console.log('   from the first tack, cable unwound between): about 3.4 m, inside the 5 m, with every bend at or above 350 mm by construction.');
console.log('   (datum-03b\'s scene, pose A at a fixed 700 mm track: 5.6 m and a 262 mm bend, which is consistent with the above: the track radius that satisfies the 350 mm bend is about 740 to 800 mm.)\n');

// 5. tube swap / lift-off geometry in B: which directions are open?
console.log('5. The nozzle tip in B sits ' + fmt(rows['B  radial plane, over the bore (no wire)   '].tip[2] - RIM_Z, 1) + ' mm above the rim plane and ' + fmt(Math.hypot(rows['B  radial plane, over the bore (no wire)   '].tip[0], rows['B  radial plane, over the bore (no wire)   '].tip[1]), 1) + ' mm from the axis (bore wall at 61.85): inside the bore, as in A.');
console.log('   The barrel then runs up and toward the axis, so nothing of it crosses the rim. For a room-fixed gun (not a crown, where the gun rides with the tube) the tube can then');
console.log('   slide out either way along y, the tangent at the station, because the barrel lies in the x-z plane and the tip is 7.5 mm above the rim; in A the barrel lies along -y, so only the');
console.log('   slide away from it (+y) is free. (calc/05 and calc/07 hold for A: the horizontal shuttle clears while 16 cos(beta) > 6.35 mm, with the wire retracted; a straight lift-out needs about 144 mm.)');
