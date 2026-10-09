// wall_clip.js - a clip that straddles the tube wall at the station: a roller on the bore, a rim wheel, an outside pad.
// Statics, contact, and the room it needs beside the kit's proxy wire and nozzle. ILLUSTRATIVE except geometry from the repo and the kit's proxy gun
// (opening pose, probed from scenes/datum-03-rim-crown: tip (55.16, -5.23, 157.39), dot (61.86, 3.75, 145.97), wire guide end (42.5, -44.62, 186.51)).
// Run: node explorers/datum/calc/wall_clip.js > explorers/datum/calc/wall_clip.out
const DEG = Math.PI / 180, R = 61.85, RO = 63.5, RIM = 152.4, t = 1.65, E = 193000, nu = 0.3;
const f = (x, n = 3) => x.toFixed(n);

console.log('A. Preload against the umbilical\'s pull: the clip holds a radial pull toward the axis only up to its preload; a pull outward loads the roller into the wall');
console.log('   pull toward the axis (N)   preload 4 N   8 N   15 N     (margin = preload - pull; the roller lifts when negative)');
for (const pull of [0.5, 1.5, 3, 6]) console.log('   ' + String(pull).padStart(6) + '                    ' + [4, 8, 15].map(p => f(p - pull, 1).padStart(6)).join('   '));
console.log('   The cable\'s pull direction at the gun is [unknown]; the exit leaves 234 mm out and 0.13 m above the rim in the proxy pose [derived].\n');

console.log('B. What the pinch does to the wall: roller inside, pad outside, on one radial line, so the wall sees a local squeeze and no net force');
const Eeff = E / (2 * (1 - nu * nu));                      // contact modulus for two steel bodies
for (const [Rr, F, Lc] of [[2.5, 8, 5], [2.5, 15, 5], [4, 15, 6]]) {
  const p = F / Lc, Reff = 1 / (1 / Rr - 1 / R);           // roller on the concave bore
  const b = Math.sqrt(4 * p * Reff / (Math.PI * Eeff));    // Hertz line contact half width
  console.log('   roller R ' + Rr + ' mm, force ' + F + ' N over ' + Lc + ' mm: line load ' + f(p, 2) + ' N/mm, contact half width ' + f(b * 1000, 1) + ' um; the elastic approach is of the order of a micrometre, about 0.001 mm');
}
console.log('   A pinch OFF the radial line (pad displaced a along the axis) makes a couple F a on the wall: 8 N x 3 mm = 24 N mm, a local rotation of the wall, not a diameter change.');
console.log('   Pinching a thin ring at TWO OPPOSITE points instead would ovalise it: a 1.65 mm wall of R 62.7 mm loaded across a diameter gives about 0.15 PL^3/EI, roughly 50 N/mm over a 27 mm axial spread (ring model, order of magnitude), i.e. about 0.15 mm at 8 N.');
console.log('   That is why the clip pinches ONE place from both sides rather than gripping the tube from opposite sides.\n');

console.log('C. Stiffness of the hook: a finger from the rim down the bore (cantilever, length L from the rim), a strip b wide and h thick, steel or stiff plastic');
console.log('   The radial stiffness that matters is the finger\'s, in series with the spine over the rim. k = E b h^3 / (4 L^3) for a cantilever with a tip load.');
for (const [mat, Em] of [['steel strip', 193000], ['PA-CF print', 9000], ['PETG print', 2100]]) for (const [b, h, L] of [[6, 1.5, 5], [6, 2.5, 8], [6, 1.5, 12]]) {
  const k = Em * b * h ** 3 / (4 * L ** 3);
  console.log('   ' + mat.padEnd(12) + ' b ' + b + ' h ' + h + ' L ' + String(L).padStart(2) + ' mm: ' + f(k, 0).padStart(7) + ' N/mm, so 3 N moves the roller ' + f(3 / k * 1000, 1).padStart(6) + ' um');
}
console.log('   A printed strip 1.5 mm thick and 12 mm long is soft (0.02 N/um is not available): the finger should be short (5 mm) and steel, or a roller bearing on a stiff printed post.\n');

console.log('D. Rolling and sliding drag along the tangent (the tube turns under the clip; the clip is free along the seam, so a drag is a force the holder must react)');
for (const [what, mu, N] of [['ball transfer or roller, rolling', 0.01, 5], ['printed skid on the rim, dry', 0.25, 5], ['PTFE-faced skid on the rim', 0.08, 5]]) console.log('   ' + what.padEnd(36) + ' mu ' + f(mu, 2) + ' x ' + N + ' N = ' + f(mu * N, 2) + ' N along the seam');
console.log('   A skid at 0.25 gives more drag than the umbilical\'s 1.5 to 3 N would leave room for; a rolling contact does not.\n');

console.log('E. Room beside the kit\'s proxy wire and barrel: the wire arrives from the -Y (arriving) side; the clip sits at s mm arc ahead of the dot on the same side');
const wire = [[42.5, -44.62, 186.51], [61.86, 3.75, 145.97]], barrel = [[55.16, -5.23, 157.39], [22.9, -48.47, 212.33]];
function segDist(p, a, b) { const ab = b.map((v, i) => v - a[i]), ap = p.map((v, i) => v - a[i]); const tt = Math.max(0, Math.min(1, ap.reduce((s, v, i) => s + v * ab[i], 0) / ab.reduce((s, v) => s + v * v, 0))); return Math.hypot(...ap.map((v, i) => v - tt * ab[i])); }
function nozzleGap(p) {                                            // distance from a point to the nozzle+shell surface (axis tip -> barrelMid, radius grows 2.2 -> 5 over 23 mm, +3 shell)
  const a = barrel[0], b = barrel[1], ab = b.map((v, i) => v - a[i]), ap = p.map((v, i) => v - a[i]), L = Math.hypot(...ab);
  const tt = Math.max(0, Math.min(1, ap.reduce((q, v, i) => q + v * ab[i], 0) / (L * L)));
  const d = Math.hypot(...ap.map((v, i) => v - tt * ab[i])), z = tt * L, r = (z < 23 ? 2.2 + 2.8 * z / 23 : 8.5) + 3;
  return d - r;
}
console.log('   s (mm)   roller-to-wire  rim wheel-to-wire  outside pad-to-wire  hook top-to-wire  roller-to-nozzle+shell   (clearances: distance minus radii; roller 2.5, wheel 3, pad 4, hook half thickness 1.5; nozzle radius 2.2 to 5 plus a 3 mm shell)');
for (const s of [-12, -6, 0, 4, 6, 10, 14, 18, 25]) {
  const a = -s / R;                                                   // ahead = toward -Y
  const P = (r, z) => [r * Math.cos(a), r * Math.sin(a), z];
  const roller = P(R - 2.5, RIM - 3.5), wheel = P((R + RO) / 2, RIM + 3), pad = P(RO + 4, RIM - 5), hook = P((R + RO) / 2, RIM + 1.5);
  const d = (p, r) => segDist(p, wire[0], wire[1]) - r;
  console.log('   ' + String(s).padStart(4) + '     ' + f(d(roller, 2.5), 1).padStart(8) + '        ' + f(d(wheel, 3), 1).padStart(8) + '           ' + f(d(pad, 4), 1).padStart(8) + '            ' + f(d(hook, 1.5), 1).padStart(8) + '          ' + f(nozzleGap(roller) - 2.5, 1).padStart(8));
}
for (const s of [-12, -6, 6, 10, 14, 18]) {
  const a = -s / R, P = (r, z) => [r * Math.cos(a), r * Math.sin(a), z], d = (p, r) => segDist(p, wire[0], wire[1]) - r;
  const c = [d(P(R - 2.5, RIM - 3.5), 2.5), d(P((R + RO) / 2, RIM + 3), 3), d(P(RO + 4, RIM - 5), 4), d(P((R + RO) / 2, RIM + 1.5), 1.5), nozzleGap(P(R - 2.5, RIM - 3.5)) - 2.5];
  console.log('   tightest gap at s = ' + String(s).padStart(3) + ' mm: ' + f(Math.min(...c), 1) + ' mm');
}
console.log('   s < 0 is the trailing side (behind the dot, over the bead: hot). On the arriving side the proxy wire and nozzle leave a gap of 1.5 to 2 mm at s = 6 to 10 mm');
console.log('   and 3.6 mm or more from s = 14 mm; how much gap the real wire bracket and its outward lean (datum-20) leave is [unknown].');
console.log('   Clearances of the kit\'s proxy geometry are illustrative; the wire guide bracket of the real gun and its lean (datum-20) decide.\n');

console.log('F. What the clip cannot know: the tube\'s longitudinal weld seam on the bore (if the tube is welded tube: [unknown]) is a bump under the roller once per revolution.');
for (const h of [0.03, 0.08, 0.15]) console.log('   bump ' + f(h, 2) + ' mm high, 3 mm wide, roller R 2.5: the roller rises ' + f(h, 2) + ' mm and the gun with it for ' + f(3 / (8) , 2) + ' s at 8 mm/s (a step, not a harmonic); a rigid ring on the OD never sees it.');
