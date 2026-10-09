// freedom W3: the nose seat with its ball moved from the barrel onto the roll-axis line (the line through the dot and the cable exit).
// Both are set up the same way: the stage command (cone apex), the two tail winches and the yaw bungee are solved so that the dot sits on the seam
// and the gun has the reference orientation under gravity and the setup wrench. Then a wrench is added at the cable exit and the dot's shift is read.
// ILLUSTRATIVE: every stiffness (calc/eye-support.js), mass 1.2 kg, COM (0,-18,178).
const FS = require('./statics.js'), FR = require('./ringmodel.js'), ES = require('./eye-support.js'), FL = require('./fibre-line.js'); const M = FS.math;
const dials = { roll: 45, holeDial: 30, vertical: -15 }, fr = FL.frame(dials, 30.2);
function build(cfg, s, list) {
  const c = Object.assign({}, ES.DEFAULT, cfg);
  const o = ES.opts(c, 0, [s[0], s[1], s[2]]); o.umbilical = { F: 0, droop: 0 }; o.extra = FL.extraOf(fr, list || []);
  o.tail.wireCmd = [s[3], s[4]]; o.tail.yawCmd = s[5];
  return FR.build(o);
}
function solveAt(cfg, s, list, x0) { const m = build(cfg, s, list); const r = m.solve(x0 || new Float64Array(m.n), { maxIter: 200 }); return { m, r }; }
function setup(cfg, list) {
  let s = [0, 0, 0, 0, 0, 0], cur = solveAt(cfg, s, list), x0 = cur.r.x;
  for (let it = 0; it < 14 && cur.r.converged; it++) {
    const res = Array.from(cur.r.x.slice(0, 6));
    const nrm = Math.max(...res.map(Math.abs)); if (nrm < 0.004) break;
    const J = [];      // columns: d residual / d s_k
    for (let k = 0; k < 6; k++) { const s2 = s.slice(); s2[k] += 0.5; const r2 = solveAt(cfg, s2, list, cur.r.x); J.push(r2.r.converged ? Array.from(r2.r.x.slice(0, 6)).map((v, i) => (v - res[i]) / 0.5) : new Array(6).fill(0)); }
    const A = new Float64Array(36), b = new Float64Array(6);
    for (let i = 0; i < 6; i++) { for (let j = 0; j < 6; j++) A[i * 6 + j] = J[j][i]; b[i] = -res[i]; }
    for (let i = 0; i < 6; i++) A[i * 6 + i] += 1e-6;
    const d = FS.math.solveLinear(A, b, 6); if (!d) break;
    const sn = s.map((v, i) => v + 0.8 * d[i]); const nxt = solveAt(cfg, sn, list, cur.r.x);
    if (!nxt.r.converged) break; s = sn; cur = nxt;
  }
  return { s, cur };
}
const seatLine = q => Object.assign({}, FL.CFG.seatLine, { seatLocal: FL.onLine(q) });
const w0 = [{ at: fr.E, F: [0, 0, 0], M: [0, 0, 0] }];
const rows = [['seat on the barrel, s=70', FL.CFG.seat], ['seat ball on the roll axis, q=70', seatLine(70)], ['seat ball on the roll axis, q=110', seatLine(110)], ['seat ball on the roll axis, q=150', seatLine(150)]];
const events = [['1 N along the roll axis (through the ball and the dot)', fr.u], ['1 N across it, in the gun plane', fr.n], ['1 N down', [0, 0, -1]], ['1 N sideways (gun X)', fr.X]];
for (const [name, cfg] of rows) {
  const t0 = Date.now(), st = setup(cfg, w0);
  const x = st.cur.r.x, ok = st.cur.r.converged;
  const out = events.map(([en, F]) => { const r = solveAt(cfg, st.s, [{ at: fr.E, F: F.slice(), M: [0, 0, 0] }], st.cur.r.x); if (!r.r.converged) return en + ': no eq'; const d = Array.from(r.r.x.slice(0, 3)).map((v, i) => v - x[i]); const rr = ES.rad(r.r.x) - ES.rad(x); return en.split(' (')[0] + ': dot ' + [rr, d[1], d[2]].map(v => v.toFixed(3)).join('/') + ' mm (|' + Math.hypot(rr, d[1], d[2]).toFixed(3) + '|), beam ' + ES.angleBetween(ES.beam(r.m, r.r.x), ES.beam(st.cur.m, x)).toFixed(3) + ' deg'; });
  console.log(name.padEnd(36), 'setup residual', Math.max(...Array.from(x.slice(0, 6)).map(Math.abs)).toFixed(4), ok ? '' : 'NOT CONVERGED', '|', (Date.now() - t0) + ' ms');
  out.forEach(l => console.log('     ' + l));
}
