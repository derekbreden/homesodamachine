// verify the searched layouts on a finer direction set (6000) and against the shipped layout
const path = '/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/explorers/freedom/calc/';
const FS = require(path + 'statics.js'), FR = require(path + 'ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15); const W = l => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0, 0, -16]); const lugsLocal = [[30, 0, 60], [-30, 0, 60], [34, 0, 170], [-34, 0, 170], [60, -118, 237], [-60, -118, 237]]; const lugsW = lugsLocal.map(W);
const Wt = D.mass * FS.G, comW = W(D.com), gripW = W(FS.GRIP_BASE), rg = M.sub(gripW, dot0);
const wg = [0, 0, -Wt].concat(M.cross(M.sub(comW, dot0), [0, 0, -Wt]));
function tens(us, w) { const A = new Float64Array(36); for (let i = 0; i < 6; i++) { const u = us[i], r = M.sub(lugsW[i], dot0), m = M.cross(r, u); for (let k = 0; k < 3; k++) { A[k * 6 + i] = u[k]; A[(k + 3) * 6 + i] = m[k]; } } return Array.from(FS.math.solveLinear(A, w.map(v => -v), 6)); }
const wrenchOf = d => d.concat(M.cross(rg, d));
function stats(us, P, N) { const wP = wg.map((v, i) => v + (P ? wrenchOf([0, 0, -P])[i] : 0)); const tg = tens(us, wP); const res = []; let worst = { f: Infinity };
  for (let i = 0; i < N; i++) { const z = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - z * z), ph = i * 2.399963; const d = [r * Math.cos(ph), r * Math.sin(ph), z]; const t1 = tens(us, wP.map((v, j) => v + wrenchOf(d)[j])); const dt = t1.map((v, j) => v - tg[j]); let f = Infinity; for (let j = 0; j < 6; j++) if (dt[j] < -1e-9) f = Math.min(f, tg[j] / -dt[j]); res.push(f); if (f < worst.f) worst = { f, d }; }
  res.sort((a, b) => a - b); const pc = p => res[Math.floor(p * (N - 1))]; const frac = L => (100 * res.filter(x => x < L).length / N).toFixed(0) + '%';
  return { tg, worst, p05: pc(0.05), med: pc(0.5), b1: frac(1), b2: frac(2), b4: frac(4), b87: frac(8.7) }; }
const shipped = JSON.parse(require('fs').readFileSync(path + '22-cable-layout.json')).dirs;
const J = JSON.parse(require('fs').readFileSync('./w2-robust-layout.json'));
function show(label, us, P) { const s = stats(us, P, 6000); console.log(label.padEnd(34), 'P', String(P).padEnd(3), '| T0', s.tg.map(v => v.toFixed(1)).join('/'), '| worst', s.worst.f.toFixed(2), 'N at', s.worst.d.map(v => v.toFixed(2)).join(','), '| p05', s.p05.toFixed(2), 'median', s.med.toFixed(2), '| dirs slack<1N', s.b1, '<2N', s.b2, '<4N', s.b4, '<8.7N', s.b87); }
show('shipped (freedom-03)', shipped, 0);
show('shipped with 10 N down at grip', shipped, 10);
show('robust search, gravity only', J.layouts.P0.dirs, 0);
show('robust search, 10 N down at grip', J.layouts.P10.dirs, 10);
show('robust(P=10) layout without preload', J.layouts.P10.dirs, 0);
console.log(JSON.stringify({ P0: J.layouts.P0.dirs.map(u => u.map(v => +v.toFixed(4))), P10: J.layouts.P10.dirs.map(u => u.map(v => +v.toFixed(4))) }));
