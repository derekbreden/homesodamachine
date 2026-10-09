// 10 - which terms of a seam signature need a per-revolution stage, and what the hold does between the dry turn and the weld turn
// (exchange on datum-02-seam-signature). Terms are the scene's own defaults for its tube: scene truth radial 0.20 (setup offset), 0.13 (1x), 0.05 (2x);
// height -0.15, 0.15, 0.03. Everything is illustrative except the rig-doc limits that motivated them. Holder compliance per newton is calc/06's
// handbook beam numbers; the change of force between the dry turn and the weld turn is [unknown].
// Run: node explorers/travel/calc/10-signature-assign.mjs
import { fmt } from './lib.mjs';

const R = { off: 0.20, a1: 0.13, a2: 0.05 }, Z = { off: -0.15, a1: 0.15, a2: 0.03 };
const rms = t => Math.sqrt(t.off * t.off + t.a1 * t.a1 / 2 + t.a2 * t.a2 / 2), peak = t => Math.abs(t.off) + t.a1 + t.a2;
const comb = (r, z) => Math.hypot(rms(r), rms(z));
const rowf = (label, r, z, note) => console.log('   ' + label.padEnd(58) + ' radial rms ' + fmt(rms(r), 3) + ' peak<= ' + fmt(peak(r), 2) + '   vertical rms ' + fmt(rms(z), 3) + ' peak<= ' + fmt(peak(z), 2) + '   both rms ' + fmt(comb(r, z), 3) + (note ? '   ' + note : ''));
console.log('A. Who takes which term (illustrative amplitudes from datum-02\'s default tube; rms of a sinusoid is amplitude / sqrt 2; peak is the in-phase worst case)\n');
rowf('nothing (as hand-aimed, uncompensated)', R, Z, '(the scene says 0.29)');
rowf('static trim: one number per axis per tube (hand, shim, or a stage set once)', { off: 0, a1: R.a1, a2: R.a2 }, { off: 0, a1: Z.a1, a2: Z.a2 });
rowf('  + radial 1x taken out at its source (nest screws, travel-06: 90 percent)', { off: 0, a1: 0.1 * R.a1, a2: R.a2 }, { off: 0, a1: Z.a1, a2: Z.a2 });
rowf('  + vertical 1x by a Z follow under the work (95 percent)', { off: 0, a1: 0.1 * R.a1, a2: R.a2 }, { off: 0, a1: 0.05 * Z.a1, a2: Z.a2 });
rowf('  + 2x terms replayed too (all terms, ideal)', { off: 0, a1: 0, a2: 0 }, { off: 0, a1: 0, a2: 0 }, '(fit noise leaves about 0.022 in the scene)');
console.log('\n   So: the constant terms are two thirds of the uncompensated rms (0.29 -> 0.15 by a static trim). Against a window of +-0.30 mm the static trim alone leaves');
console.log('   the dot inside the window everywhere (peaks 0.18 radial, 0.18 vertical); a replay stage earns its place only when the window is below about 0.2 mm, and');
console.log('   then it is the vertical axis that is needed first (the 1x face wobble cannot be taken out by any screw in the nest).\n');

console.log('B. The hold between the dry turn and the weld turn. The replay applies the dry-turn constant term; anything that moves the gun relative to the room between');
console.log('   the two turns adds a constant the fit never saw. Error = change of force x compliance of the chain from gun to room. Change of force: [unknown]');
console.log('   (wire feeder starting and its conduit, gas hose, fibre emitting, hands off). Compliance per newton from calc/06:');
const holders = [['20 mm steel rod, 300 mm, bolted', 5.7], ['12 mm steel rod, 300 mm, bolted', 44.2], ['12 mm aluminium rod, 300 mm', 128.1]];
console.log('   holder'.padEnd(84), '0.3 N     1 N       3 N   (mm of constant error)');
for (const [n, c] of holders) console.log('   ' + n.padEnd(81), [0.3, 1, 3].map(F => fmt(F * c / 1000, 3).padStart(8)).join(' '));
console.log('   (A friction-locked joint is not a spring: calc/06 B gives 0.087 mm for 0.02 degree of creep at a 250 mm lever, whatever the force.)');
console.log('   Compare with the fit residual, 0.022 rms: a 1 N change against a 12 mm steel rod is twice that and the same sign every lap.');
console.log('   A stage carried in the gun\'s shell is in series with the holder: add its stiffness. A 20 N/mm stage gives 0.05 mm per newton on top of the holder.\n');
console.log('   Requirement to keep the parity error under 0.02 mm at a 1 N change: chain compliance under 20 um/N, i.e. stiffer than 50 N/mm gun-to-room, stage included.\n');

console.log('C. Backlash on a horizontal axis. The replay reverses at the peaks of a sinusoid. With a backlash b in the stage and no preload (a horizontal axis has no gravity),');
console.log('   the load sits on one flank and lags the command by up to b at each reversal: the swing is b peak to peak, so b/2 either side once the mean is trimmed:');
for (const b of [0.02, 0.05, 0.10]) {
  let worst = 0, sq = 0, n = 0, pos = 0, dir = 1;
  for (let i = 0; i <= 3600; i++) { const th = i / 3600 * 2 * Math.PI, cmd = R.a1 * Math.cos(th) + R.a2 * Math.cos(2 * th + 0.5); if (cmd - pos > b / 2) pos = cmd - b / 2; else if (cmd - pos < -b / 2) pos = cmd + b / 2; const e = cmd - pos; worst = Math.max(worst, Math.abs(e)); sq += e * e; n++; }
  console.log('   backlash ' + fmt(b, 2) + ' mm -> residual amplitude ' + fmt(worst, 3) + ' mm, rms ' + fmt(Math.sqrt(sq / n), 3) + ' mm (radial 1x + 2x terms replayed)');
}
console.log('   A vertical axis is loaded one way by the gun\'s (or the rotator\'s) weight and does not see this; a horizontal one wants a light spring preload or a flexure.');
