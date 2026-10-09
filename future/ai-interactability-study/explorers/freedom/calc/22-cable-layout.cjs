// Search for a six-line (gravity-closed) suspension layout for the gun shell that keeps every line taut with margin.
// ILLUSTRATIVE: mass, COM, lug positions and the frame envelope are choices, not requirements.
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15);
const W = (l) => M.add(pose.origin, M.mv(pose.R, l));
const dot0 = W([0,0,-16]);
const lugsLocal = [ [30,0,60], [-30,0,60], [34,0,170], [-34,0,170], [60,-118,237], [-60,-118,237] ];
const lugsW = lugsLocal.map(W);
const Wt = D.mass * FS.G, comW = W(D.com);
// external wrench on the body about the dot: gravity at COM, umbilical at grip base
function wrench(F, droop) { const exitDir = M.mv(pose.R, FS.ROLL_AXIS), pd = M.norm(M.add(M.mul(exitDir, 1-droop), [0,0,-droop])); const f = M.add([0,0,-Wt], M.mul(pd, F)); const tau = M.add(M.cross(M.sub(comW,dot0),[0,0,-Wt]), M.cross(M.sub(W(FS.GRIP_BASE),dot0), M.mul(pd,F))); return f.concat(tau); }
function tensions(us, w) { // A t = -w
  const n = us.length; const A = new Float64Array(6*n);
  for (let i=0;i<n;i++){ const u=us[i], r=M.sub(lugsW[i],dot0), m=M.cross(r,u); for(let k=0;k<3;k++){A[k*n+i]=u[k];A[(k+3)*n+i]=m[k];} }
  if (n !== 6) return null;
  const t = FS.math.solveLinear(A, w.map(v=>-v), 6); return t ? Array.from(t) : null; }
function rnd(a,b){return a+(b-a)*Math.random();}
function randDir(maxAng){ const th = rnd(0, maxAng*Math.PI/180), ph = rnd(0, 2*Math.PI); return [Math.sin(th)*Math.cos(ph), Math.sin(th)*Math.sin(ph), Math.cos(th)]; }
// clearance: a cable must stay >= 32 mm from the gun's barrel/housing axis (local z 0..253) after its first 25 mm, and reach the top plane
const zTop = 600;
function clearOk(i, u) { const p0 = lugsW[i]; const sTop = (zTop - p0[2]) / u[2]; for (let s = 25; s <= sTop; s += 10) { const p = M.add(p0, M.mul(u, s)); const rel = M.sub(p, pose.origin); const l = [0,1,2].map(k=>rel[0]*pose.R[0*3+k]*0 + 0); /* placeholder */ const RT = [pose.R[0],pose.R[3],pose.R[6],pose.R[1],pose.R[4],pose.R[7],pose.R[2],pose.R[5],pose.R[8]]; const lo = M.mv(RT, rel); const z = Math.max(0, Math.min(253, lo[2])); const d = Math.hypot(lo[0], lo[1], lo[2] - z); if (d < 32) return false; } return true; }
let best = null;
const w0 = wrench(2, 0.5), wA = wrench(4, 0), wB = wrench(4, 1);
for (let it=0; it<1200000; it++) {
  const us = lugsW.map((p,i)=>randDir(58)); if (!us.every((u,i)=>clearOk(i,u))) continue;
  const t0 = tensions(us, w0); if (!t0 || t0.some(v=>v<1.5)) continue;
  const tA = tensions(us, wA), tB = tensions(us, wB); if (!tA || !tB) continue;
  const mn = Math.min(...t0, ...tA, ...tB); const mx = Math.max(...t0);
  const score = mn - 0.05*mx; if (!best || score > best.score) best = { score, us, t0, tA, tB, mn, mx };
}
console.log('best min tension across gravity+umbilical cases', best.mn.toFixed(2), 'N; max', best.mx.toFixed(1));
console.log('directions', best.us.map(u=>u.map(v=>v.toFixed(2)).join(',')).join(' | '));
console.log('t0', best.t0.map(v=>v.toFixed(1)).join(','));
require('fs').writeFileSync(__dirname + '/22-cable-layout.json', JSON.stringify({ lugsLocal, dirs: best.us, t0: best.t0, zTop }, null, 1));
