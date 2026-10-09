const path = __dirname + '/';
const FS = require(path + 'statics.js'), FR = require(path + 'ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15); const W = l => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0, 0, -16]); const lugsLocal = [[30, 0, 60], [-30, 0, 60], [34, 0, 170], [-34, 0, 170], [60, -118, 237], [-60, -118, 237]]; const lugsW = lugsLocal.map(W);
const Wt = D.mass * FS.G, comW = W(D.com), gripW = W(FS.GRIP_BASE), rg = M.sub(gripW, dot0);
const wg = [0, 0, -Wt].concat(M.cross(M.sub(comW, dot0), [0, 0, -Wt]));
function tens(us, w) { const A = new Float64Array(36); for (let i = 0; i < 6; i++) { const u = us[i], r = M.sub(lugsW[i], dot0), m = M.cross(r, u); for (let k = 0; k < 3; k++) { A[k * 6 + i] = u[k]; A[(k + 3) * 6 + i] = m[k]; } } return Array.from(FS.math.solveLinear(A, w.map(v => -v), 6)); }
const wrenchOf = d => d.concat(M.cross(rg, d));
function slack(us, d) { const tg = tens(us, wg); const t1 = tens(us, wg.map((v, j) => v + wrenchOf(d)[j])); let f = Infinity; for (let j = 0; j < 6; j++) { const dt = t1[j] - tg[j]; if (dt < -1e-9) f = Math.min(f, tg[j] / -dt); } return f; }
const shipped = JSON.parse(require('fs').readFileSync(path + '22-cable-layout.json')).dirs;
const ex = M.mv(pose.R, FS.ROLL_AXIS);
for (const droop of [0]) {
  const c = M.norm(M.add(M.mul(ex, 1 - droop), [0, 0, -droop]));
  let a = Math.abs(c[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]; const u = M.norm(M.cross(c, a)), v = M.cross(c, u);
  for (const half of [0, 1, 2, 3, 5, 8, 10, 15]) {
    let mn = Infinity, worst=null; for (let i = 0; i < 800; i++) { const th = half * Math.PI / 180 * Math.sqrt((i + 0.5) / 800), ph = i * 2.399963; const d = M.add(M.mul(c, Math.cos(th)), M.add(M.mul(u, Math.sin(th) * Math.cos(ph)), M.mul(v, Math.sin(th) * Math.sin(ph)))); const s = slack(shipped, M.norm(d)); if (s < mn) { mn = s; worst = [th*180/Math.PI, ph]; } }
    console.log('exit axis, cone half-angle', half, 'deg: min slack pull', mn.toFixed(2), 'N');
  }
}
