// w2-taut-set.cjs - wave 2. For freedom-03's six-line layout (explorers/freedom/calc/22-cable-layout.json), which pulls at the
// grip base keep every line taut? Rigid-line statics at the reference pose (linear: t = tg + F * td). ILLUSTRATIVE: freedom's
// layout, 1.2 kg, COM and grip-base point are freedom's illustrative numbers; nothing here is measured.
const path = '/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/explorers/freedom/calc/';
const FS = require(path + 'statics.js'), FR = require(path + 'ringmodel.js'); const M = FS.math;
const LAY = JSON.parse(require('fs').readFileSync(path + '22-cable-layout.json'));
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15);
const W = l => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0, 0, -16]);
const lugsW = LAY.lugsLocal.map(W), us = LAY.dirs;
const Wt = D.mass * FS.G, comW = W(D.com);
const gripW = W(FS.GRIP_BASE);
function tens(w) { const n = 6, A = new Float64Array(36); for (let i = 0; i < n; i++) { const u = us[i], r = M.sub(lugsW[i], dot0), m = M.cross(r, u); for (let k = 0; k < 3; k++) { A[k * n + i] = u[k]; A[(k + 3) * n + i] = m[k]; } } return Array.from(FS.math.solveLinear(A, w.map(v => -v), 6)); }
const wg = [0, 0, -Wt].concat(M.cross(M.sub(comW, dot0), [0, 0, -Wt]));
const tg = tens(wg);
console.log('gravity only, line tensions N:', tg.map(v => v.toFixed(2)).join(' '));
function td(d) { const f = d, tau = M.cross(M.sub(gripW, dot0), d); return tens(f.concat(tau)); }   // per newton of pull along d, expressed as (t(wg+F w_d) - t(wg)) / F
function tperN(d) { const a = tens(wg.map((v, i) => v + (i < 3 ? d[i] : M.cross(M.sub(gripW, dot0), d)[i - 3]))); return a.map((v, i) => v - tg[i]); }
function fmax(d) { const dt = tperN(d); let f = Infinity, which = -1; for (let i = 0; i < 6; i++) if (dt[i] < -1e-9) { const c = tg[i] / -dt[i]; if (c < f) { f = c; which = i; } } return { f, which }; }
// exit direction as in freedom's scene (roll axis in the world, blended toward straight down by droop)
const ex = M.mv(pose.R, FS.ROLL_AXIS);
for (const droop of [0, 0.5, 1]) { const pd = M.norm(M.add(M.mul(ex, 1 - droop), [0, 0, -droop])); const r = fmax(pd); console.log('pull along exit blended to down, droop', droop, 'dir', pd.map(v => v.toFixed(2)).join(','), 'slack at', r.f.toFixed(2), 'N (line', r.which + 1, ')'); }
// sphere scan
let worst = { f: Infinity }, byLine = {}; const N = 6000; const list = [];
for (let i = 0; i < N; i++) { const z = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - z * z), ph = i * 2.399963; const d = [r * Math.cos(ph), r * Math.sin(ph), z]; const a = fmax(d); list.push({ d, f: a.f, which: a.which }); if (a.f < worst.f) worst = { f: a.f, d, which: a.which }; byLine[a.which] = (byLine[a.which] || 0) + 1; }
console.log('worst direction over the sphere: slack at', worst.f.toFixed(2), 'N, dir', worst.d.map(v => v.toFixed(2)).join(','), 'line', worst.which + 1);
const fs = list.map(x => x.f).sort((a, b) => a - b); const pct = p => fs[Math.floor(p * (fs.length - 1))];
console.log('slack pull over directions: min', fs[0].toFixed(2), '5th pct', pct(0.05).toFixed(2), 'median', pct(0.5).toFixed(2), 'N; lines that give way first (count of directions):', JSON.stringify(byLine));
// how many of the directions in the "cable region" (upper hemisphere, pointing back/up like an overhead route) slacken below 4 N and 8.7 N
for (const lim of [1, 2, 4, 8.7]) { const c = list.filter(x => x.f < lim).length; console.log('directions whose slack pull is below', lim, 'N: ', (100 * c / N).toFixed(1) + '% of the sphere'); }
// pull direction that points up (z>0.5): the overhead route
const up = list.filter(x => x.d[2] > 0.5); const fu = up.map(x => x.f).sort((a, b) => a - b);
console.log('upward pulls (z>0.5): min slack pull', fu[0].toFixed(2), 'N; median', fu[Math.floor(fu.length / 2)].toFixed(2));
const lat = list.filter(x => Math.abs(x.d[2]) < 0.3); const fl = lat.map(x => x.f).sort((a, b) => a - b);
console.log('sideways pulls (|z|<0.3): min slack pull', fl[0].toFixed(2), 'N; median', fl[Math.floor(fl.length / 2)].toFixed(2));

// ---- a seventh line: a constant downward pull P (a spring balancer under the bench) at a point on the shell
console.log('\nSeventh line: constant downward force P at a shell point (a spring balancer pulling down; adds no stiffness in this rigid-line model)');
function tperNat(pt, d) { const tau = M.cross(M.sub(pt, dot0), d); const a = tens(wg.map((v, i) => v + (i < 3 ? d[i] : tau[i - 3]))); return a.map((v, i) => v - tg[i]); }
const sites = { 'grip base': gripW, 'housing back (local z 253)': W([0, 0, 253]), 'mid barrel (local z 110)': W([0, 0, 110]) };
for (const [name, pt] of Object.entries(sites)) {
  const dn = [0, 0, -1], tdn = tperNat(pt, dn);
  for (const P of [0, 5, 10, 15, 20]) {
    const tg2 = tg.map((v, i) => v + P * tdn[i]);
    let mn = Infinity, cnt1 = 0, cnt87 = 0, cnt4 = 0, arr = [];
    for (let i = 0; i < N; i++) { const d = list[i].d; const dt = tperN(d); let f = Infinity; for (let j = 0; j < 6; j++) if (dt[j] < -1e-9) f = Math.min(f, tg2[j] / -dt[j]); if (tg2.some(v => v < 0)) f = 0; arr.push(f); if (f < mn) mn = f; if (f < 1) cnt1++; if (f < 4) cnt4++; if (f < 8.7) cnt87++; }
    arr.sort((a, b) => a - b);
    console.log((name + ' P=' + P).padEnd(38), 'line T', tg2.map(v => v.toFixed(1)).join('/'), '| worst-direction slack pull', mn.toFixed(2), 'N, 5th pct', arr[Math.floor(0.05 * (N - 1))].toFixed(2), 'median', arr[Math.floor(0.5 * (N - 1))].toFixed(2), '| dirs below 1 N', (100 * cnt1 / N).toFixed(0) + '%, below 4 N', (100 * cnt4 / N).toFixed(0) + '%, below 8.7 N', (100 * cnt87 / N).toFixed(0) + '%');
  }
}
