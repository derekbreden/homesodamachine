// ring-seat.mjs - seat amplification for a three-ball, three-groove coupling (a Maxwell coupling of six contacts), ported from
// scenes/use-02-swing-head (couplingMatrix / amplification): RMS displacement of the dot per unit contact error, as a function of
// the contact-circle radius Rc and the distance from the coupling centre to the dot. Used for room-12 (a ring seat at gun-local z 138
// with a wider circle) against use-02's fork (Rc 30, seat at z 116).
// Run: node explorers/room/calc/ring-seat.mjs
const DEG = Math.PI / 180;
function inv6(A) {
  const n = 6, M = A.map((r, i) => r.concat(Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))));
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    const d = M[c][c]; for (let k = 0; k < 2 * n; k++) M[c][k] /= d;
    for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let k = 0; k < 2 * n; k++) M[r][k] -= f * M[c][k]; }
  }
  return M.map(r => r.slice(n));
}
function amp(Rc, zDot) {   // zDot: distance from the coupling centre to the dot along the axis (mm)
  const G = [], a = 45 * DEG;
  for (let i = 0; i < 3; i++) {
    const phi = Math.PI + (i === 0 ? 0 : (i === 1 ? 1 : -1) * 2 * Math.PI / 3);
    const p = [Rc * Math.cos(phi), Rc * Math.sin(phi), 0], t = [-Math.sin(phi), Math.cos(phi), 0];
    [1, -1].forEach(s => {
      const n = [s * t[0] * Math.sin(a), s * t[1] * Math.sin(a), Math.cos(a)];
      G.push([n[0], n[1], n[2], p[1] * n[2] - p[2] * n[1], p[2] * n[0] - p[0] * n[2], p[0] * n[1] - p[1] * n[0]]);
    });
  }
  const Gi = inv6(G), r = [0, 0, -zDot];
  const J = [[1, 0, 0, 0, r[2], -r[1]], [0, 1, 0, -r[2], 0, r[0]], [0, 0, 1, r[1], -r[0], 0]];
  let s = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 6; j++) { let v = 0; for (let k = 0; k < 6; k++) v += J[i][k] * Gi[k][j]; s += v * v; }
  return Math.sqrt(s);
}
console.log('seat amplification (RMS dot shift per unit random contact error)');
console.log('use-02 default: flange 116 behind the nozzle, seat centre about 113 mm behind the nozzle, dot 16 mm ahead of it -> dot 129 mm from the coupling centre');
for (const [nm, Rc, zd] of [['use-02 fork, Rc 30, seat 116', 30, 16 + 116 - 3.2], ['use-02 fork, Rc 60, seat 116', 60, 16 + 116 - 3.2], ['room-12 ring, Rc 30, seat plane 138', 30, 16 + 138 + 3.6], ['room-12 ring, Rc 45, seat plane 138', 45, 16 + 138 + 3.6], ['room-12 ring, Rc 60, seat plane 138', 60, 16 + 138 + 3.6], ['room-12 ring, Rc 45, seat plane 100', 45, 16 + 100 + 3.6], ['room-12 ring, Rc 45, seat plane 160', 45, 16 + 160 + 3.6]]) {
  const a = amp(Rc, zd); console.log(nm.padEnd(40), 'dot', zd.toFixed(0).padStart(4), 'mm from centre  amplification', a.toFixed(2), ' 5 um at every contact -> ', (a * 5 / Math.sqrt(6) * Math.sqrt(6)).toFixed(0), 'um RMS at the dot (as the scene reports it: sigma x amplification)');
}
