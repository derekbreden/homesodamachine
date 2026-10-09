// pad-selectivity.mjs (eyes, wave 3) - answers freedom's questions on eyes-04 (exchange/freedom--on--eyes-w2.md section 5):
//   (a) which pad reads only the wall and which only the plate at the 40 deg facet?
//   (b) if the wall-facing pair were replaced by a contact, would the remaining plate pair still have a fold?
//   (c) how much of a wall-pad gain error does "span from a known nudge of the trim stage" remove, and what does it leave?
// The model is a COPY of the capacitive model in scenes/eyes-04-proximity-skin (illustrative: C = eps0 A/(d+1 mm) x facing factor squared;
// noise 0.5 fF). Section plane: plate top z=0 for r<0, wall face r=0 for 0<z<6.35. Defaults of the scene: pad 6 mm, front pads 20 mm back,
// rear pads 46 mm back, beam tilt 32 deg, facet 40 deg.
const eps0 = 8.854e-12, RIM = 6.35, DEG = Math.PI / 180;
const respCap = (d, size) => eps0 * (size * size * 0.94 * 1e-6) / ((d + 1) * 1e-3) * 1e15;
const shellR = L => Math.max(5.2, Math.min(11.5, 5.2 + (L - 16) * (11.5 - 5.2) / 23));
export function geometry(g, p) {
  const b = { x: Math.sin(p.beta), y: -Math.cos(p.beta) }, n = { x: Math.cos(p.beta), y: Math.sin(p.beta) };
  const mW = { x: Math.sin(p.beta + p.phi), y: -Math.cos(p.beta + p.phi) }, mP = { x: Math.sin(p.beta - p.phi), y: -Math.cos(p.beta - p.phi) };
  const pads = [];
  [[p.L1, 'front'], [p.L1 + 26, 'rear']].forEach(([L, st]) => {
    const w = shellR(L) + 0.8, c = { x: g.r - L * b.x, y: g.z - L * b.y };
    pads.push({ id: st + ' wall', pos: { x: c.x + w * n.x, y: c.y + w * n.y }, m: mW, face: 'wall' });
    pads.push({ id: st + ' plate', pos: { x: c.x - w * n.x, y: c.y - w * n.y }, m: mP, face: 'plate' });
  });
  return pads;
}
const qPlate = pos => ({ x: Math.min(0, pos.x), y: 0 }), qWall = pos => ({ x: 0, y: Math.max(0, Math.min(RIM, pos.y)) });
function term(pad, q, size) {
  const dx = q.x - pad.pos.x, dy = q.y - pad.pos.y, d = Math.max(0.5, Math.hypot(dx, dy));
  const f = Math.pow(Math.max(0, (pad.m.x * dx + pad.m.y * dy) / d), 2);
  return { d, f, v: respCap(d, size) * f };
}
export const parts = (pad, p) => ({ plate: term(pad, qPlate(pad.pos), p.size).v, wall: term(pad, qWall(pad.pos), p.size).v });
export const readings = (g, p, pert) => geometry(g, p).map(pad => { const t = parts(pad, p); return t.plate + t.wall * 1 + 0; }).map((v, i) => v);
function read(g, p, gain) {   // gain: per-pad multiplicative error on the wall-facing pads only
  return geometry(g, p).map((pad, i) => { const t = parts(pad, p); const k = pad.face === 'wall' ? 1 + (gain || 0) : 1; return (t.plate + t.wall) * k; });
}
function solve(y, p, use, x0, gainsAssumed) {   // Gauss-Newton on (r, z) with the nominal model, using pads whose index is in `use`
  let x = { r: x0.r, z: x0.z };
  for (let it = 0; it < 30; it++) {
    const f = q => read(q, p, 0).map((v, i) => v * (gainsAssumed ? gainsAssumed[i] : 1)), y0 = f(x), h = 0.02, yr = f({ r: x.r + h, z: x.z }), yz = f({ r: x.r, z: x.z + h });
    let a = 0, b = 0, c = 0, d1 = 0, d2 = 0;
    use.forEach(i => { const jr = (yr[i] - y0[i]) / h, jz = (yz[i] - y0[i]) / h, res = y[i] - y0[i]; a += jr * jr; b += jr * jz; c += jz * jz; d1 += jr * res; d2 += jz * res; });
    const det = a * c - b * b; if (Math.abs(det) < 1e-18) return { ok: false, r: x.r, z: x.z };
    x.r = Math.max(-30, Math.min(30, x.r + (c * d1 - b * d2) / det)); x.z = Math.max(-30, Math.min(30, x.z + (a * d2 - b * d1) / det));
  }
  return { ok: true, r: x.r, z: x.z };
}
function sigma(g, p, use) {
  const y0 = read(g, p, 0), h = 0.02, yr = read({ r: g.r + h, z: g.z }, p, 0), yz = read({ r: g.r, z: g.z + h }, p, 0);
  let a = 0, b = 0, c = 0; use.forEach(i => { const jr = (yr[i] - y0[i]) / h, jz = (yz[i] - y0[i]) / h; a += jr * jr; b += jr * jz; c += jz * jz; });
  const det = a * c - b * b; if (det < 1e-18) return { r: Infinity, z: Infinity, cond: Infinity };
  return { r: 0.5 * Math.sqrt(c / det), z: 0.5 * Math.sqrt(a / det), det };
}
const p = { size: 6, L1: 20, beta: 32 * DEG, phi: 40 * DEG };
const g0 = { r: 0, z: 0 };
console.log('(a) share of each pad\'s reading that comes from the plate and from the wall, dot on the corner, facet 40 deg (front pads 20 mm back, rear 46 mm)');
geometry(g0, p).forEach(pad => { const t = parts(pad, p), s = t.plate + t.wall; console.log('  ' + pad.id.padEnd(12) + ' reading ' + s.toFixed(1).padStart(6) + ' fF   from plate ' + (100 * t.plate / s).toFixed(0).padStart(3) + ' %   from wall ' + (100 * t.wall / s).toFixed(0).padStart(3) + ' %'); });
console.log('   at the working offsets (radial, vertical) = (2, -1.5) and (-2, 1.5):');
[{ r: 2, z: -1.5 }, { r: -2, z: 1.5 }].forEach(g => geometry(g, p).forEach(pad => { const t = parts(pad, p), s = t.plate + t.wall; console.log('   (' + g.r + ',' + g.z + ') ' + pad.id.padEnd(12) + ' plate ' + (100 * t.plate / s).toFixed(0).padStart(3) + ' %  wall ' + (100 * t.wall / s).toFixed(0).padStart(3) + ' %'); }));
console.log('\n   facet angle sweep, front wall pad and front plate pad, share from its own surface (dot on the corner):');
for (const phi of [0, 20, 30, 40, 50, 60]) { const q = Object.assign({}, p, { phi: phi * DEG }), pads = geometry(g0, q), tw = parts(pads[0], q), tp = parts(pads[1], q); console.log('   phi ' + String(phi).padStart(2) + '  wall pad: wall ' + (100 * tw.wall / (tw.wall + tw.plate)).toFixed(0).padStart(3) + ' %   plate pad: plate ' + (100 * tp.plate / (tp.wall + tp.plate)).toFixed(0).padStart(3) + ' %'); }

console.log('\n(b) the fold: 1-sigma of the solved (r, z) from noise alone (0.5 fF), all four pads vs the plate-facing pair only, on a grid of offsets (mm); "-" = not solvable');
const sets = { 'all four': [0, 1, 2, 3], 'plate pair only (front plate, rear plate)': [1, 3], 'wall pair only': [0, 2] };
for (const [name, use] of Object.entries(sets)) {
  console.log('  ' + name);
  const zs = [4, 2, 0, -2, -4], rs = [-6, -4, -2, 0, 2, 4, 6];
  console.log('        r:' + rs.map(r => String(r).padStart(11)).join(''));
  for (const z of zs) console.log('   z=' + String(z).padStart(3) + '  ' + rs.map(r => { const s = sigma({ r, z }, p, use); return (isFinite(s.r) ? s.r.toFixed(2) + '/' + s.z.toFixed(2) : '-').padStart(11); }).join(''));
}
// fraction of the plotted +-8 mm square with both sigmas under 0.05 mm
for (const [name, use] of Object.entries(sets)) { let n = 0, good = 0; for (let r = -8; r <= 8; r += 0.4) for (let z = -8; z <= 8; z += 0.4) { n++; const s = sigma({ r, z }, p, use); if (s.r < 0.05 && s.z < 0.05) good++; } console.log('  ' + name.padEnd(42) + 'fraction of +-8 mm with both 1-sigma < 0.05 mm: ' + (100 * good / n).toFixed(0) + ' %'); }
// with the wall pair replaced by a CONTACT: r known at the moment of contact, 0 elsewhere; the plate pair then gives z from the plate gap, r from the contact
console.log('\n   contact replaces the wall pair: at the instant of contact r is known to the trigger repeatability (say 0.01 mm); the plate pair is then solved for z only with r fixed:');
for (const r of [-4, -2, 0]) for (const z of [4, 2, 0, -2]) { const g = { r, z }, y0 = read(g, p, 0), h = 0.02, yz = read({ r, z: z + h }, p, 0); let a = 0; [1, 3].forEach(i => { const jz = (yz[i] - y0[i]) / h; a += jz * jz; }); console.log('   at (r ' + r + ', z ' + z + '): sigma z from the plate pair, r known = ' + (0.5 / Math.sqrt(a)).toFixed(3) + ' mm'); }

console.log('\n(c) wall pads read 5 % high (gain error); solve as if calibrated, vs after a span calibration by nudging the trim stage 1 mm in r and 1 mm in z (known to 0.01 mm) and estimating one gain per pad');
const gTrue = { r: 2, z: -1.5 };
for (const gain of [0.03, 0.05, 0.10]) {
  const y = read(gTrue, p, gain), plain = solve(y, p, [0, 1, 2, 3], { r: 0, z: 0 });
  // nudge: the stage moves the gun by +1 mm in r, then +1 mm in z; the pad readings change by (1+gain_i) x the nominal slope; estimate each pad's gain by least squares over the two nudges
  const gEst = [0, 1, 2, 3].map(i => { let num = 0, den = 0; [[1, 0], [0, 1]].forEach(([dr, dz]) => { const a = read({ r: gTrue.r + dr, z: gTrue.z + dz }, p, gain)[i] - read(gTrue, p, gain)[i], nom = read({ r: gTrue.r + dr, z: gTrue.z + dz }, p, 0)[i] - read(gTrue, p, 0)[i]; num += a * nom; den += nom * nom; }); return num / den; });
  const cal = solve(y, p, [0, 1, 2, 3], { r: 0, z: 0 }, gEst.map(v => 1 / v).map((_, i) => gEst[i]));
  console.log('  gain ' + (gain * 100).toFixed(0) + ' %: solved error uncalibrated (' + (plain.r - gTrue.r).toFixed(3) + ', ' + (plain.z - gTrue.z).toFixed(3) + ') mm;  estimated pad gains ' + gEst.map(v => v.toFixed(3)).join(' ') + ';  error after span calibration (' + (cal.r - gTrue.r).toFixed(3) + ', ' + (cal.z - gTrue.z).toFixed(3) + ') mm');
}
console.log('  (an offset, a nearby conductor or drift is a ZERO error: a nudge cannot see it. With a 0.5 fF offset on the front wall pad:)');
{
  const y = read(gTrue, p, 0); y[0] += 0.5 * 3; const plain = solve(y, p, [0, 1, 2, 3], { r: 0, z: 0 });
  console.log('  offset 1.5 fF on the front wall pad: solved error (' + (plain.r - gTrue.r).toFixed(3) + ', ' + (plain.z - gTrue.z).toFixed(3) + ') mm');
}

// ---- extra: closer, bigger pads (the scene's best case: 8 mm pads, front pads 17 mm back), the plate pair only, and the noisy span calibration
console.log('\n(b2) same fold question with 8 mm pads, front pads 17 mm back (the closest the shell allows in the scene)');
{
  const q = { size: 8, L1: 17, beta: 32 * DEG, phi: 40 * DEG };
  for (const [name, use] of Object.entries(sets)) { let n = 0, good = 0, medR = [], medZ = []; for (let r = -6; r <= 6; r += 0.5) for (let z = -6; z <= 6; z += 0.5) { n++; const s = sigma({ r, z }, q, use); if (isFinite(s.r)) { medR.push(s.r); medZ.push(s.z); } if (s.r < 0.1 && s.z < 0.1) good++; } medR.sort((a, b) => a - b); medZ.sort((a, b) => a - b); console.log('  ' + name.padEnd(42) + 'median sigma r ' + medR[medR.length >> 1].toFixed(2) + ' mm, z ' + medZ[medZ.length >> 1].toFixed(2) + ' mm;  fraction of +-6 mm with both < 0.1 mm: ' + (100 * good / n).toFixed(0) + ' %'); }
}
console.log('\n(c2) span calibration with noise, one gain for the wall pair and one for the plate pair: nudge the trim stage by a known step in r and in z (stage known to 0.01 mm), average n repeats, regress; residual position error on the solve (rms over 300 draws; 5 % wall-pad gain error; dot at (2, -1.5); pads 6 mm at 20 mm; noise 0.5 fF per reading)');
let seed = 12345; const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }, gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());
const gT = { r: 2, z: -1.5 };
const solveNoiseOnly = (() => { let se = 0, N = 300; for (let k = 0; k < N; k++) { const y = read(gT, p, 0.05).map(v => v + 0.5 * gauss()); const sol = solve(y, p, [0, 1, 2, 3], { r: 0, z: 0 }); se += (sol.r - gT.r) ** 2 + (sol.z - gT.z) ** 2; } return Math.sqrt(se / N); })();
console.log('  reference: the same solve with NO calibration and a single noisy reading: rms error ' + solveNoiseOnly.toFixed(2) + ' mm (bias 0.24 mm plus noise)');
for (const step of [1, 3, 6]) for (const nrep of [1, 4, 16]) {
  let se = 0, N = 300, gwSd = 0;
  for (let k = 0; k < N; k++) {
    const gain = 0.05, y = read(gT, p, gain).map(v => v + 0.5 * gauss());   // one measurement at the working point (also noisy)
    let nw = 0, dw = 0, np = 0, dp = 0;
    [[step, 0], [0, step]].forEach(([dr, dz]) => {
      const A = read({ r: gT.r + dr, z: gT.z + dz }, p, gain), B = read(gT, p, gain), An = read({ r: gT.r + dr, z: gT.z + dz }, p, 0), Bn = read(gT, p, 0);
      [0, 1, 2, 3].forEach(i => { let a = 0; for (let m = 0; m < nrep; m++) a += (A[i] + 0.5 * gauss()) - (B[i] + 0.5 * gauss()); a /= nrep; const nom = An[i] - Bn[i]; if (i % 2 === 0) { nw += a * nom; dw += nom * nom; } else { np += a * nom; dp += nom * nom; } });
    });
    const gw = nw / dw, gp = np / dp; gwSd += (gw - 1.05) ** 2;
    const cal = solve(y, p, [0, 1, 2, 3], { r: 0, z: 0 }, [gw, gp, gw, gp]);
    se += (cal.r - gT.r) ** 2 + (cal.z - gT.z) ** 2;
  }
  console.log('  step ' + step + ' mm, ' + String(nrep).padStart(2) + ' repeats: rms position error ' + Math.sqrt(se / N).toFixed(2) + ' mm;  rms error of the wall gain estimate ' + (100 * Math.sqrt(gwSd / N)).toFixed(1) + ' %');
}
