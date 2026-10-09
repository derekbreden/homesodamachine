// Where the gun proxy's named points land at the reference scene's opening pose (roll 45, hole dial 30, vertical -15).
const F = require('./statics.js'); const M = F.math;
const pose = F.dialsToPose(45, 30, -15);
const local = { nozzleTip:[0,0,0], dot:[0,0,-16], barrelMid:[0,0,77], collar:[0,0,109], housingTop:[0,17,185.5], housingCtr:[0,0,185.5], housingBack:[0,0,253], gripMid:[0,-68,202], gripBase:[0,-118,237], cablePair:[0,-118,237].map((v,i)=>v+F.ROLL_AXIS[i]*20) };
for (const k in local) { const p = M.add(pose.origin, M.mv(pose.R, local[k])); console.log(k.padEnd(12), p.map(v=>v.toFixed(1)).join('  ')); }
console.log('joint', F.JOINT.map(v=>v.toFixed(2)).join(' '));
console.log('roll axis world dir', M.mv(pose.R, F.ROLL_AXIS).map(v=>v.toFixed(3)).join(' '));
console.log('barrel axis world dir (local +Z)', M.mv(pose.R,[0,0,1]).map(v=>v.toFixed(3)).join(' '));
