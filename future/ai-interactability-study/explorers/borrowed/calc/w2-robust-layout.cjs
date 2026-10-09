// w2-robust-layout.cjs - wave 2. Same random search as freedom's calc/22-cable-layout.cjs (same lugs, clearance rule, frame
// height, same 1.2 kg and COM), but the objective is the smallest pull, over EVERY direction of the umbilical's pull at the
// grip base, that slackens a line, with gravity alone as the preload (P = 0) or with a constant downward pull P at the grip base
// (a spring balancer under the bench). ILLUSTRATIVE numbers throughout; nothing is measured.
const path = '/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/explorers/freedom/calc/';
const FS = require(path + 'statics.js'), FR = require(path + 'ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15);
const W = l => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0, 0, -16]);
const lugsLocal = [[30, 0, 60], [-30, 0, 60], [34, 0, 170], [-34, 0, 170], [60, -118, 237], [-60, -118, 237]];
const lugsW = lugsLocal.map(W);
const Wt = D.mass * FS.G, comW = W(D.com), gripW = W(FS.GRIP_BASE);
const zTop = 600;
const RT = [pose.R[0], pose.R[3], pose.R[6], pose.R[1], pose.R[4], pose.R[7], pose.R[2], pose.R[5], pose.R[8]];
function clearOk(i, u) { const p0 = lugsW[i]; const sTop = (zTop - p0[2]) / u[2]; for (let s = 25; s <= sTop; s += 10) { const p = M.add(p0, M.mul(u, s)); const rel = M.sub(p, pose.origin); const lo = M.mv(RT, rel); const z = Math.max(0, Math.min(253, lo[2])); if (Math.hypot(lo[0], lo[1], lo[2] - z) < 32) return false; } return true; }
function rnd(a, b) { return a + (b - a) * Math.random(); }
function randDir(maxAng) { const th = rnd(0, maxAng * Math.PI / 180), ph = rnd(0, 2 * Math.PI); return [Math.sin(th) * Math.cos(ph), Math.sin(th) * Math.sin(ph), Math.cos(th)]; }
// 6x6 inverse (Gauss-Jordan)
function inv6(A) { const n = 6, a = []; for (let i = 0; i < n; i++) { a.push([]); for (let j = 0; j < n; j++) a[i].push(A[i][j]); for (let j = 0; j < n; j++) a[i].push(i === j ? 1 : 0); }
  for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(a[r][c]) > Math.abs(a[p][c])) p = r; if (Math.abs(a[p][c]) < 1e-9) return null; [a[c], a[p]] = [a[p], a[c]]; const d = a[c][c]; for (let j = 0; j < 2 * n; j++) a[c][j] /= d; for (let r = 0; r < n; r++) if (r !== c) { const f = a[r][c]; if (f) for (let j = 0; j < 2 * n; j++) a[r][j] -= f * a[c][j]; } }
  return a.map(r => r.slice(n)); }
const wg = [0, 0, -Wt].concat(M.cross(M.sub(comW, dot0), [0, 0, -Wt]));
const rg = M.sub(gripW, dot0);
function wrenchOf(d) { return d.concat(M.cross(rg, d)); }
const NDIR = 240, dirs = []; for (let i = 0; i < NDIR; i++) { const z = 1 - 2 * (i + 0.5) / NDIR, r = Math.sqrt(1 - z * z), ph = i * 2.399963; dirs.push([r * Math.cos(ph), r * Math.sin(ph), z]); }
const wd = dirs.map(wrenchOf);
function evalLayout(us, P) {
  const A = [[], [], [], [], [], []]; for (let i = 0; i < 6; i++) { const u = us[i], r = M.sub(lugsW[i], dot0), m = M.cross(r, u); for (let k = 0; k < 3; k++) { A[k][i] = u[k]; A[k + 3][i] = m[k]; } }
  const Ai = inv6(A); if (!Ai) return null; const mul = v => Ai.map(row => row.reduce((s, x, j) => s + x * v[j], 0));
  const wP = wg.map((v, i) => v + (P ? wrenchOf([0, 0, -P])[i] : 0)); const tg = mul(wP).map(v => -v); if (tg.some(v => v < 0.3)) return { min: 0, tg };
  let mn = Infinity; for (let k = 0; k < NDIR; k++) { const td = mul(wd[k]).map(v => -v); for (let j = 0; j < 6; j++) if (td[j] < -1e-9) { const f = tg[j] / -td[j]; if (f < mn) mn = f; } }
  return { min: mn, tg };
}
const iters = Number(process.argv[2] || 200000);
const PL = (process.argv[3] || '0,5,10,15').split(',').map(Number); const OUT = {};
for (const P of PL) {
  let best = null; let n = 0;
  for (let it = 0; it < iters; it++) {
    const us = lugsW.map(() => randDir(58)); let ok = true; for (let i = 0; i < 6; i++) if (!clearOk(i, us[i])) { ok = false; break; } if (!ok) continue; n++;
    const r = evalLayout(us, P); if (!r) continue; if (!best || r.min > best.min) best = { min: r.min, us, tg: r.tg };
  }
  console.log('P =', String(P).padEnd(3), 'N downward at the grip base | feasible layouts tried', n, '| best worst-direction slack pull', best.min.toFixed(2), 'N | line tensions with no pull', best.tg.map(v => v.toFixed(1)).join('/'), '| max line', Math.max(...best.tg).toFixed(1), 'N');
  OUT['P' + P] = { P, min: best.min, dirs: best.us, tg: best.tg };
}
require('fs').writeFileSync(__dirname + '/w2-robust-layout.json', JSON.stringify({ iters, lugsLocal, zTop, layouts: OUT }, null, 1));
