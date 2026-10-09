// slack pull over a CONE of pull directions around the exit axis blended toward down (freedom-03's droop), for the three layouts.
const path = '/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/explorers/freedom/calc/';
const FS = require(path + 'statics.js'), FR = require(path + 'ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15); const W = l => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0, 0, -16]); const lugsLocal = [[30, 0, 60], [-30, 0, 60], [34, 0, 170], [-34, 0, 170], [60, -118, 237], [-60, -118, 237]]; const lugsW = lugsLocal.map(W);
const Wt = D.mass * FS.G, comW = W(D.com), gripW = W(FS.GRIP_BASE), rg = M.sub(gripW, dot0);
const wg = [0, 0, -Wt].concat(M.cross(M.sub(comW, dot0), [0, 0, -Wt]));
function tens(us, w) { const A = new Float64Array(36); for (let i = 0; i < 6; i++) { const u = us[i], r = M.sub(lugsW[i], dot0), m = M.cross(r, u); for (let k = 0; k < 3; k++) { A[k * 6 + i] = u[k]; A[(k + 3) * 6 + i] = m[k]; } } return Array.from(FS.math.solveLinear(A, w.map(v => -v), 6)); }
const wrenchOf = d => d.concat(M.cross(rg, d));
function slack(us, P, d) { const wP = wg.map((v, i) => v + (P ? wrenchOf([0, 0, -P])[i] : 0)); const tg = tens(us, wP); if (tg.some(v => v < 0)) return 0; const t1 = tens(us, wP.map((v, j) => v + wrenchOf(d)[j])); let f = Infinity; for (let j = 0; j < 6; j++) { const dt = t1[j] - tg[j]; if (dt < -1e-9) f = Math.min(f, tg[j] / -dt); } return f; }
const shipped = JSON.parse(require('fs').readFileSync(path + '22-cable-layout.json')).dirs;
const J = JSON.parse(require('fs').readFileSync('./w2-robust-layout.json'));
const L = { 'shipped': [shipped, 0], 'robust gravity only': [J.layouts.P0.dirs, 0], 'robust + 10 N preload': [J.layouts.P10.dirs, 10] };
const ex = M.mv(pose.R, FS.ROLL_AXIS);
for (const droop of [0, 0.5, 1]) {
  const c = M.norm(M.add(M.mul(ex, 1 - droop), [0, 0, -droop]));
  // orthonormal frame around c
  let a = Math.abs(c[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]; const u = M.norm(M.cross(c, a)), v = M.cross(c, u);
  for (const half of [15, 30, 45, 60]) {
    const out = []; for (const [k, [us, P]] of Object.entries(L)) { let mn = Infinity; for (let i = 0; i < 400; i++) { const th = half * Math.PI / 180 * Math.sqrt((i + 0.5) / 400), ph = i * 2.399963; const d = M.add(M.mul(c, Math.cos(th)), M.add(M.mul(u, Math.sin(th) * Math.cos(ph)), M.mul(v, Math.sin(th) * Math.sin(ph)))); const s = slack(us, P, M.norm(d)); if (s < mn) mn = s; } out.push(k + ' ' + mn.toFixed(2)); }
    console.log('droop', droop, 'cone half-angle', half, 'deg: min slack pull N |', out.join(' | '));
  }
}
