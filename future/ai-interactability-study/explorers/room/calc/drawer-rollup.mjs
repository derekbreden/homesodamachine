// Fine-stage range each coarse arrangement leaves: a worst-case sum and a root-sum-square of the contributions that move the
// tube's corner relative to the gun.  Tags: [repo] rotator/rig docs, [illustrative] my numbers.  Not a ranking: it lists what each
// arrangement leaves for the fine stage; the inputs are the uncertain part.   Run: node explorers/room/calc/drawer-rollup.mjs
const rss = a => Math.sqrt(a.reduce((s, v) => s + v * v, 0));
const rows = {
  'bench, rotator hand-clamped, gun structure on the bench': { xy: [5, 0.2, 0.125], z: [3, 0.15], note: 'hand placement +/-5 (illustrative); nest 0.20 [repo]; runout 0.25 TIR [repo] (half = 0.125)' },
  'table hole, loose (D160 around D127)':   { xy: [16.5, 0.2, 0.125], z: [3, 0.15], note: 'hole clearance +/-16.5 (derived); rest as above' },
  'table hole with a fitted collar':        { xy: [0.2, 0.2, 0.125], z: [3, 0.15], note: 'collar centring 0.2 (illustrative)' },
  'drawer cell, kinematic dock':            { xy: [0.04, 0.2, 0.125], z: [3, 0.15, 0.04], note: 'dock repeat 0.04 (illustrative)' },
  'orbit, steady ring on the OD':           { xy: [0.08, 0.16, 0.2], z: [3, 0.15], note: 'ring 0.08 (illustrative); wall-thickness eccentricity 0.16 (10 % of the 1.65 mm wall, illustrative); no runout of the tube because it does not turn but the orbit bearing has its own 0.2 (illustrative)' },
};
console.log('mm; seat depth +/-3 (illustrative) and face runout 0.30 TIR / 2 [repo] in Z');
for (const [k, r] of Object.entries(rows)) {
  const xy = r.xy, z = r.z;
  console.log(k.padEnd(56), 'XY worst-case +/-' + xy.reduce((s, v) => s + v, 0).toFixed(2), ' RSS +/-' + rss(xy).toFixed(2), '  Z worst-case +/-' + z.reduce((s, v) => s + v, 0).toFixed(2), ' RSS +/-' + rss(z).toFixed(2));
  console.log('   ' + r.note);
}
