// A4: the fixed seat fork must stay out of the tube-swap volume (illustrative: radius 95 mm, top 217 mm) or the tube cannot be lifted out.
// Where along the barrel (gun-local z of the seat flange) can the coupling sit, and what does it cost in sensitivity at the dot?
// Fork = square plate of half-size (Rc + 14) in the gun's local x,y plane, 4 mm thick, just forward of the flange.
// Usage: node calc/fork_clearance.mjs
import { world, sub, add, mul, unit, fmt } from './pose.mjs';
const D = [45, 30, -15];
const W = l => world(l, ...D);
const O = W([0, 0, 0]);
const ex = unit(sub(W([1, 0, 0]), O)), ey = unit(sub(W([0, 1, 0]), O)), ez = unit(sub(W([0, 0, 1]), O));
const RIM = 152.4, SWAP = { r: 95, z0: -20, z1: RIM + 25 + 40 };
const distSwap = p => { const rho = Math.hypot(p[0], p[1]), dr = rho - SWAP.r, dz = Math.max(SWAP.z0 - p[2], p[2] - SWAP.z1); return dr < 0 && dz < 0 ? Math.max(dr, dz) : Math.hypot(Math.max(0, dr), Math.max(0, dz)); };
// amplification for an on-axis dot at distance L from the coupling centre (same Maxwell coupling as seat_amplification.mjs)
function inv6(A) { const n = 6, M = A.map((r, i) => r.concat(Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)))); for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;[M[c], M[p]] = [M[p], M[c]]; const d = M[c][c]; for (let k = 0; k < 2 * n; k++) M[c][k] /= d; for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let k = 0; k < 2 * n; k++) M[r][k] -= f * M[c][k]; } } return M.map(r => r.slice(n)); }
function amp(Rc, L) {
  const G = [], a = 45 * Math.PI / 180;
  for (let i = 0; i < 3; i++) { const phi = Math.PI / 2 + 2 * Math.PI * i / 3, p = [Rc * Math.cos(phi), Rc * Math.sin(phi), 0], t = [-Math.sin(phi), Math.cos(phi), 0]; for (const s of [1, -1]) { const n = [s * t[0] * Math.sin(a), s * t[1] * Math.sin(a), Math.cos(a)]; G.push([n[0], n[1], n[2], p[1] * n[2] - p[2] * n[1], p[2] * n[0] - p[0] * n[2], p[0] * n[1] - p[1] * n[0]]); } }
  const Gi = inv6(G), J = [[1, 0, 0, 0, -L, 0], [0, 1, 0, L, 0, 0], [0, 0, 1, 0, 0, 0]]; let s = 0;
  for (let i = 0; i < 3; i++) for (let j = 0; j < 6; j++) { let v = 0; for (let k = 0; k < 6; k++) v += J[i][k] * Gi[k][j]; s += v * v; }
  return Math.sqrt(s);
}
console.log('ZF = local z of the flange; fork plane is 8 mm forward of it. Dot is 16 mm ahead of the nozzle tip (local z = -16).');
console.log(' ZF   Rc | fork lowest z | worst swap-volume clearance (mm, negative = intrudes) | L to dot | amplification (RMS dot / contact error)');
for (const ZF of [100, 116, 130, 145, 160]) for (const Rc of [20, 30, 45]) {
  const rr = Rc + 14; let worst = Infinity, lowZ = Infinity;
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) for (const dz of [0, -4]) {
    const p = add(O, add(mul(ex, sx * rr), add(mul(ey, sy * rr), mul(ez, ZF - 8 + dz))));
    worst = Math.min(worst, distSwap(p)); lowZ = Math.min(lowZ, p[2]);
  }
  const L = ZF - 3.2 + 16;
  console.log(String(ZF).padStart(4), String(Rc).padStart(4), '|', lowZ.toFixed(0).padStart(9), '|', worst.toFixed(1).padStart(12), '|', L.toFixed(0).padStart(8), '|', amp(Rc, L).toFixed(1).padStart(6));
}
console.log('\nreading: the fork plate is tilted (its normal is the barrel axis), so its low corner dips. Moving the seat back along the barrel lifts it out of the volume at the price of a longer lever to the dot.');
