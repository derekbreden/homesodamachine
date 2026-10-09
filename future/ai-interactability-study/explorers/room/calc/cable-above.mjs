// cable-above.mjs - use-07-two-stations reads the fibre's bend in plan view only ("conservative for a climbing cable").
// The fibre leaves the grip base along the dot-to-grip line, which climbs at about 65 degrees from horizontal at the opening pose.
// If the hook is ABOVE the head (a ceiling track or a gallows), the climb is used instead of fought. Same Bezier rule as the kit and
// as use-07's calc/two_stations.mjs (handle = 0.4 x chord, minimum 15 mm), same radii (350 emitting at a seat, 240 in transit
// [manual p.20]), same two seats 520 mm apart, same cart 500 mm beyond the rail. Only the height of the hook is new.
// Bezier is a stand-in: it has no bending stiffness, weight or twist. Illustrative gun proxy and opening pose.
// Run: node explorers/room/calc/cable-above.mjs
import { world, worldDir, ANCHORS, ROLL_AXIS, unit, fmt } from './pose.mjs';

const roll = 45, hole = 30, vert = -15, EXIT = 70;
const dir0 = unit(worldDir(ROLL_AXIS, roll, hole, vert));
const grip0 = world(ANCHORS.gripBase, roll, hole, vert);
console.log('cable exit (grip base) world', fmt(grip0), ' exit direction', fmt(dir0, 3), ' climb angle', (Math.asin(dir0[2]) * 180 / Math.PI).toFixed(1), 'deg above horizontal, plan heading', (Math.atan2(dir0[1], dir0[0]) * 180 / Math.PI).toFixed(0), 'deg');

const add = (a, b, k = 1) => a.map((v, i) => v + k * b[i]);
function bez(a, da, b, db, k = 0.4, n = 120) {
  const d = Math.hypot(...b.map((v, i) => v - a[i])), kk = Math.max(15, k * d), c1 = add(a, da, kk), c2 = add(b, db, -kk), p = [];
  for (let i = 0; i <= n; i++) { const t = i / n, u = 1 - t; p.push(a.map((_, j) => u * u * u * a[j] + 3 * u * u * t * c1[j] + 3 * u * t * t * c2[j] + t * t * t * b[j])); }
  return p;
}
function minR(p) {
  let m = Infinity;
  for (let i = 1; i < p.length - 1; i++) {
    const a = p[i - 1], b = p[i], c = p[i + 1], ab = b.map((v, j) => v - a[j]), bc = c.map((v, j) => v - b[j]), ca = c.map((v, j) => v - a[j]);
    const cr = [ab[1] * bc[2] - ab[2] * bc[1], ab[2] * bc[0] - ab[0] * bc[2], ab[0] * bc[1] - ab[1] * bc[0]], a2 = Math.hypot(...cr);
    if (a2 < 1e-9) continue; m = Math.min(m, Math.hypot(...ab) * Math.hypot(...bc) * Math.hypot(...ca) / (2 * a2));
  }
  return m;
}
// Layout (plan, +X along the row of tubes, -Y toward the back): seat A at x = -S/2, seat B at x = +S/2 (the head translates along X).
// Rail (hook line) is D behind the exit point; the cart (fixed cable end) sits C beyond the rail at height zc. Hook height above the exit point: H.
function bestTangent(a, hook, anchor, k) {   // a fairlead that can swivel and tilt: the cable passes through it in whatever direction bends it least
  const chord = unit(hook.map((v, i) => v - a[i])), back = [0, -1, 0];
  let best = -1, bd = null;
  for (let t = 0; t <= 1.0001; t += 0.1) for (let lift = -0.3; lift <= 0.61; lift += 0.1) {
    const d = unit(chord.map((v, i) => (1 - t) * v + t * back[i]).map((v, i) => (i === 2 ? v + lift : v)));
    const r = Math.min(minR(bez(a, dir0, hook, d, k)), minR(bez(hook, d, anchor, back, k)));
    if (r > best) { best = r; bd = d; }
  }
  return best;
}
function worst(P, mode) {
  let atSeat = Infinity, over = Infinity, need = Infinity;
  for (let i = 0; i <= 40; i++) {
    const u = i / 40, x = -P.S / 2 + u * P.S;
    const a = add(add(grip0, [x, 0, 0]), dir0, EXIT);
    const hx = mode === 'mid' ? 0 : mode === 'half' ? x / 2 : a[0];
    const hook = [hx, grip0[1] - P.D, grip0[2] + P.H], anchor = [0, hook[1] - P.C, P.zc == null ? hook[2] : P.zc];
    const back = [0, -1, 0];
    const r = P.free ? bestTangent(a, hook, anchor, P.k) : Math.min(minR(bez(a, dir0, hook, back, P.k)), minR(bez(hook, back, anchor, back, P.k)));
    const req = (i === 0 || i === 40) ? 350 : 240;
    over = Math.min(over, r); need = Math.min(need, r - req); if (i === 0) atSeat = r;
  }
  return { atSeat, over, short: need };
}
const S = 520, C = 500;
console.log('\nHook at the height of the exit point (H = 0) reproduces use-07\'s plan-view model only roughly (3D exit direction keeps its climb here).');
console.log('  rows: hook height H above the exit point, rail D behind it; cart 500 beyond the rail at the hook height. Values: min radius at seat A | worst in travel | meets 350 (seats) / 240 (between)?\n');
console.log('  H mm   D mm  mode  |  at seat | worst in travel | verdict');
for (const H of [0, 200, 400, 600, 800, 1000, 1200]) for (const D of [400, 600, 800]) for (const mode of ['mid', 'half', 'head']) {
  const w = worst({ S, D, C, H, k: 0.4 }, mode);
  console.log(String(H).padStart(6), String(D).padStart(6), ' ', mode.padEnd(5), '|', w.atSeat.toFixed(0).padStart(8), '|', w.over.toFixed(0).padStart(14), '   |', w.short >= 0 ? 'meets' : 'short by ' + (-w.short).toFixed(0));
}
console.log('\nCart lower than the hook (cable drops to a bench-height cart 900 mm below the hook):');
for (const H of [600, 800, 1000]) for (const D of [600, 800]) for (const mode of ['half']) {
  const w = worst({ S, D, C, H, k: 0.4, zc: grip0[2] - 300 }, mode);
  console.log(String(H).padStart(6), String(D).padStart(6), ' ', mode.padEnd(5), '|', w.atSeat.toFixed(0).padStart(8), '|', w.over.toFixed(0).padStart(14), '   |', w.short >= 0 ? 'meets' : 'short by ' + (-w.short).toFixed(0));
}

console.log('\nSame layouts with a fairlead at the hook that may swivel and tilt (cable passes through in the direction that bends it least; leg 2 continues from it):');
console.log('  H mm   D mm  mode  |  at seat | worst in travel | verdict');
for (const H of [0, 400, 800, 1200]) for (const D of [400, 600, 800]) for (const mode of ['mid', 'half']) {
  const w = worst({ S, D, C, H, k: 0.4, free: true }, mode);
  console.log(String(H).padStart(6), String(D).padStart(6), ' ', mode.padEnd(5), '|', w.atSeat.toFixed(0).padStart(8), '|', w.over.toFixed(0).padStart(14), '   |', w.short >= 0 ? 'meets' : 'short by ' + (-w.short).toFixed(0));
}
