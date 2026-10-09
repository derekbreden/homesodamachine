// A4 swing head / A5 cartridge: how much does a small error at a kinematic seat move the dot?
// Model: Maxwell kinematic coupling, three V-grooves at 120 degrees on a circle of radius Rc in the plane z = 0,
// each groove has two contact normals tilted 45 deg from the axis. Six contacts fix six degrees of freedom.
// Each contact's position error d_i (along its normal) ~ N(0, sigma). Solve G [t; w] = d for the body motion; the dot sits at
// distance L from the coupling centre along the coupling's axis (z) and a lateral offset e.
// Everything is ILLUSTRATIVE geometry: it shows how the amplification scales, it does not measure a seat.
// Usage: node calc/seat_amplification.mjs
function solve6(A, b) {                       // Gaussian elimination, 6x6
  const n = 6, M = A.map((r, i) => r.concat([b[i]]));
  for (let c = 0; c < n; c++) {
    let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    for (let r = c + 1; r < n; r++) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
  }
  const x = Array(n).fill(0);
  for (let r = n - 1; r >= 0; r--) { let s = M[r][n]; for (let k = r + 1; k < n; k++) s -= M[r][k] * x[k]; x[r] = s / M[r][r]; }
  return x;
}
function coupling(Rc, alpha = 45) {
  const G = [];
  for (let i = 0; i < 3; i++) {
    const phi = (90 + 120 * i) * Math.PI / 180;
    const p = [Rc * Math.cos(phi), Rc * Math.sin(phi), 0], tang = [-Math.sin(phi), Math.cos(phi), 0];
    for (const s of [+1, -1]) {
      const a = alpha * Math.PI / 180;
      const n = [s * tang[0] * Math.sin(a), s * tang[1] * Math.sin(a), Math.cos(a)];
      const c = [p[1] * n[2] - p[2] * n[1], p[2] * n[0] - p[0] * n[2], p[0] * n[1] - p[1] * n[0]];
      G.push([n[0], n[1], n[2], c[0], c[1], c[2]]);
    }
  }
  return G;
}
function gauss() { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
function rmsAtDot(Rc, L, e, sigma, N = 4000) {
  const G = coupling(Rc); let s2 = 0, sTilt = 0;
  for (let k = 0; k < N; k++) {
    const d = G.map(() => sigma * gauss());
    const x = solve6(G, d), t = x.slice(0, 3), w = x.slice(3);
    const r = [e, 0, L];                          // dot position relative to the coupling centre
    const u = [t[0] + w[1] * r[2] - w[2] * r[1], t[1] + w[2] * r[0] - w[0] * r[2], t[2] + w[0] * r[1] - w[1] * r[0]];
    s2 += u[0] * u[0] + u[1] * u[1] + u[2] * u[2];
    sTilt += Math.hypot(w[0], w[1]);
  }
  return { dot: Math.sqrt(s2 / N), tilt_urad: Math.sqrt(sTilt * sTilt / N / N) };
}
const sigma = 0.005;   // 5 micron contact position error per contact [illustrative]
console.log('RMS dot displacement per contact error sigma = 5 um [illustrative], 6 contacts');
console.log('Rc = contact circle radius, L = dot distance from coupling centre along the axis, e = lateral offset');
console.log(' Rc(mm)  L(mm)  e(mm) | dot RMS (um)  amplification');
for (const Rc of [15, 30, 45, 60]) for (const L of [60, 150, 280]) {
  const e = 30, r = rmsAtDot(Rc, L, e, sigma);
  console.log(String(Rc).padStart(6), String(L).padStart(6), String(e).padStart(6), ' |', (r.dot * 1000).toFixed(1).padStart(8), (r.dot / sigma).toFixed(1).padStart(12) + 'x');
}
// Cable pull: lift-off check. A pull F at lever arm d (from the coupling centre) needs preload P >= F*d/Rc (moment balance about a contact line, crude).
console.log('\nPreload needed so a cable pull does not lift a contact (crude moment balance, P >= F*d/Rc, gun weight ignored):');
for (const F of [2, 5, 10]) for (const d of [150, 250]) for (const Rc of [30, 60]) console.log(` pull ${F} N at ${d} mm, Rc ${Rc} mm -> preload >= ${(F * d / Rc).toFixed(0)} N`);
console.log('(F is illustrative: umbilical stiffness and weight are [unknown]; gun mass is [unknown].)');
