// travel-20: where does each joint of a UR-type 6R arm move the dot, and how does that depend on where the arm's base stands
// around the tube? (mm at the dot per 0.01 degree of one joint, and mm per newton for a given joint stiffness.)
// The gun is the kit proxy in the reference scene's opening pose (ILLUSTRATIVE); the arm carries it by a flange lug on the
// housing top (a printed adaptor, 40 mm long). Radial = world +X at the station, tangent = world Y, vertical = Z.
//   node explorers/travel/calc/15-arm-radial-line.mjs
import { fk, jac, ikBest, baseMat, DH } from './arm6r.mjs';

const DEG = Math.PI / 180;
// kit proxy, opening pose, nominal (no hand-set error): frame axes of the gun in the world, origin = nozzle tip
const G = { o: [54.6, -8.58, 157.44], x: [0.77, 0.16, 0.61], y: [-0.44, 0.83, 0.34], z: [-0.45, -0.54, 0.71] };
const dotW = [61.85, 0, 146.05];
const lw = (l) => [G.o[0] + l[0] * G.x[0] + l[1] * G.y[0] + l[2] * G.z[0], G.o[1] + l[0] * G.x[1] + l[1] * G.y[1] + l[2] * G.z[1], G.o[2] + l[0] * G.x[2] + l[1] * G.y[2] + l[2] * G.z[2]];
const lvec = (l) => [l[0] * G.x[0] + l[1] * G.y[0] + l[2] * G.z[0], l[0] * G.x[1] + l[1] * G.y[1] + l[2] * G.z[1], l[0] * G.x[2] + l[1] * G.y[2] + l[2] * G.z[2]];
const norm = v => { const n = Math.hypot(...v); return v.map(a => a / n); };

export function armTarget(lugLocal, normalLocal, adaptor, rollDeg) {
  const lug = lw(lugLocal), n = norm(lvec(normalLocal));
  const zf = n.map(a => -a);
  // flange x: the gun's own x axis projected off zf, then rolled about zf
  let xr = lvec([1, 0, 0]); const d = xr[0] * zf[0] + xr[1] * zf[1] + xr[2] * zf[2]; xr = norm(xr.map((a, i) => a - d * zf[i]));
  const yr = [zf[1] * xr[2] - zf[2] * xr[1], zf[2] * xr[0] - zf[0] * xr[2], zf[0] * xr[1] - zf[1] * xr[0]];
  const c = Math.cos(rollDeg * DEG), s = Math.sin(rollDeg * DEG);
  const xf = xr.map((a, i) => a * c + yr[i] * s);
  return { p: lug.map((a, i) => a + n[i] * adaptor), z: zf, x: xf, lug };
}

export function place(Rb, psiDeg, zb, target) {
  const bx = Rb * Math.cos(psiDeg * DEG), by = Rb * Math.sin(psiDeg * DEG);
  // base yaw: J1 zero points from the base toward the axis (any value works; J1 turns +-360 deg)
  const base = baseMat(bx, by, zb, (psiDeg + 180) * DEG);
  const r = ikBest(target, base);
  return { base, r };
}

// per-joint dot motion for dtheta = 0.01 deg, and the Cartesian compliance for joint stiffness k (N.m/rad, all joints equal)
export function maps(r, kNmPerRad) {
  const J = jac(r.F, dotW), out = [];
  for (let i = 0; i < 6; i++) { const s = 0.01 * DEG; out.push({ j: i + 1, rad: J[0][i] * s, tan: J[1][i] * s, vert: J[2][i] * s, wx: J[3][i] * s / DEG, wy: J[4][i] * s / DEG, wz: J[5][i] * s / DEG }); }
  // compliance: C = Jv K^-1 Jv^T (Jv in m per rad -> mm per N.m ... force at the dot F (N) makes joint torque tau = Jv^T F (N.mm); deflection dq = tau/1000 / k (rad))
  const C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) { let s = 0; for (let i = 0; i < 6; i++) s += J[a][i] * J[b][i] / 1000 / kNmPerRad; C[a][b] = s; }   // mm per N
  return { steps: out, C };
}

if (process.argv[1].endsWith('15-arm-radial-line.mjs') && !process.argv[2]) {
  const tgt = armTarget([0, 17, 185.5], [0, 1, 0], 40, 0);
  console.log('lug', tgt.lug.map(v => v.toFixed(1)).join(', '), ' flange', tgt.p.map(v => v.toFixed(1)).join(', '), ' zf', tgt.z.map(v => v.toFixed(2)).join(', '));
  const K = 8000;   // N.m/rad per joint: illustrative
  for (const zb of [0, 150, 300]) for (const Rb of [300, 400]) {
    console.log(`\nbase radius ${Rb} mm, height above the bench plane ${zb} mm (dot is 232 mm above the bench at nominal)`);
    for (const psi of [0, 30, 60, 90, 120, 150, 180]) {
      const bench = -186;
      const { r } = place(Rb, psi, bench + zb, tgt);
      if (!r) { console.log(String(psi).padStart(4), ' no solution'); continue; }
      const m = maps(r, K);
      const rss = f => Math.sqrt(m.steps.reduce((t, s) => t + f(s) ** 2, 0));
      console.log(String(psi).padStart(4), 'q(deg)', r.q.map(v => (v / DEG).toFixed(0).padStart(5)).join(' '),
        '| J1 dot motion r,t,z', [m.steps[0].rad, m.steps[0].tan, m.steps[0].vert].map(v => (v * 1000).toFixed(0).padStart(5)).join(' '), 'um/0.01deg',
        '| RSS r,z of J1-J6', (rss(s => s.rad) * 1000).toFixed(0), (rss(s => s.vert) * 1000).toFixed(0), 'tan', (rss(s => s.tan) * 1000).toFixed(0),
        '| compliance r,t,z mm/N', m.C[0][0].toFixed(3), m.C[1][1].toFixed(3), m.C[2][2].toFixed(3));
    }
  }
}

// ---- the table the idea file and scene 20 quote (run: node 15-arm-radial-line.mjs table) -------------------------------------------
if (process.argv[2] === 'table') {
  const RSS = (m, f) => Math.sqrt(m.steps.reduce((t, s) => t + f(s) ** 2, 0)) * 1000;
  const grips = { 'housing top': [[0, 17, 185.5], [0, 1, 0]], 'barrel': [[0, 14, 77], [0, 1, 0]], 'from behind, along the beam': [[0, 0, 253], [0, 0, 1]] };
  console.log('Six-axis (UR3e link lengths), base 300 mm from the axis, 150 mm above the bench, 40 mm adaptor. Each joint 0.01 degree off. Micrometres at the dot.');
  for (const [name, [l, n]] of Object.entries(grips)) {
    const tgt = armTarget(l, n, 40, 0), fd = Math.hypot(tgt.p[0] - 61.85, tgt.p[1], tgt.p[2] - 146.05);
    console.log(`\n${name}: flange ${fd.toFixed(0)} mm from the dot`);
    console.log('  azimuth  reachable  radial+vertical  tangent   per joint J1..J6 (r+z)');
    for (const psi of [0, 30, 60, 90, 120, 150, 180, 210, 270, 330]) {
      const { r } = place(300, psi, -186 + 150, tgt);
      if (!r) { console.log(String(psi).padStart(6), '   no'); continue; }
      const m = maps(r, 8000);
      console.log(String(psi).padStart(6), '     yes   ', Math.hypot(RSS(m, s => s.rad), RSS(m, s => s.vert)).toFixed(0).padStart(6), '        ', RSS(m, s => s.tan).toFixed(0).padStart(5), '   ', m.steps.map(s => (Math.hypot(s.rad, s.vert) * 1000).toFixed(0).padStart(3)).join(' '));
    }
  }
  // SCARA (two links 225 + 175, quill above the lug) and a gantry: same gun, housing-top grip
  const lug = armTarget([0, 17, 185.5], [0, 1, 0], 40, 0).lug, dot = [61.85, 0, 146.05];
  const perp = (a, b) => [-(dot[1] - b), dot[0] - a];
  console.log('\nSCARA (225 + 175 mm), quill on the housing-top lug, joint 0.01 degree; slides 0.01 mm:');
  for (const psi of [0, 90, 180]) {
    const bx = 300 * Math.cos(psi * DEG), by = 300 * Math.sin(psi * DEG), L1 = 225, L2 = 175, dx = lug[0] - bx, dy = lug[1] - by, d = Math.hypot(dx, dy);
    if (d > 399 || d < 51) { console.log(String(psi).padStart(6), '  unreachable at 300 mm (' + d.toFixed(0) + ' mm to the lug)'); continue; }
    const a = Math.atan2(dy, dx), c2 = (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2), t2 = Math.acos(c2), t1 = a - Math.atan2(L2 * Math.sin(t2), L1 + L2 * Math.cos(t2));
    const ex = bx + L1 * Math.cos(t1), ey = by + L1 * Math.sin(t1);
    const s = 0.01 * DEG, v1 = perp(bx, by), v2 = perp(ex, ey), v4 = perp(lug[0], lug[1]);
    const rz = [Math.abs(v1[0]) * s, Math.abs(v2[0]) * s, 0.01, Math.abs(v4[0]) * s], tn = [Math.abs(v1[1]) * s, Math.abs(v2[1]) * s, 0, Math.abs(v4[1]) * s];
    console.log(String(psi).padStart(6), '  radial+vertical', (Math.sqrt(rz.reduce((t, v) => t + v * v, 0)) * 1000).toFixed(0), ' tangent', (Math.sqrt(tn.reduce((t, v) => t + v * v, 0)) * 1000).toFixed(0), ' per axis r+z', rz.map(v => (v * 1000).toFixed(0)).join(' '));
  }
  console.log('gantry aligned with the radial (azimuth 0): radial+vertical', (Math.hypot(10, 10)).toFixed(0), 'tangent 10 (0.01 mm per slide); azimuth 45: radial+vertical 17 (both horizontal slides feed the radial)');
}

// ---- SCARA straightening: as the two links line up along the radial, the elbow's radial authority goes to zero -----------------------
if (process.argv[2] === 'scara-straight') {
  const lug = armTarget([0, 17, 185.5], [0, 1, 0], 40, 0).lug, dot = [61.85, 0, 146.05], L1 = 225, L2 = 175, kj = 8000;
  console.log('SCARA on the radial line (azimuth 0), housing-top lug; base distance sets how straight the arm is. 0.01 deg per joint, 0.01 mm Z; stiffness 8000 N.m/rad per joint');
  console.log(' base mm  elbow deg  radial+vertical um  tangent um   compliance mm/N (radial, tangent)');
  for (const Rb of [280, 300, 320, 340, 350, 356, 360]) {
    const bx = Rb, by = 0, dx = lug[0] - bx, dy = lug[1] - by, d = Math.hypot(dx, dy);
    if (d > 399.5) { console.log(String(Rb).padStart(7), ' unreachable (' + d.toFixed(0) + ' mm)'); continue; }
    const a = Math.atan2(dy, dx), c2 = (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2), t2 = Math.acos(c2), t1 = a - Math.atan2(L2 * Math.sin(t2), L1 + L2 * Math.cos(t2));
    const ex = bx + L1 * Math.cos(t1), ey = by + L1 * Math.sin(t1), s = 0.01 * DEG;
    const v = [[-(dot[1] - by), dot[0] - bx], [-(dot[1] - ey), dot[0] - ex], [-(dot[1] - lug[1]), dot[0] - lug[0]]];
    const rz = Math.sqrt(v.reduce((t, w) => t + (w[0] * s) ** 2, 0) + 0.01 ** 2), tn = Math.sqrt(v.reduce((t, w) => t + (w[1] * s) ** 2, 0));
    const Cr = v.reduce((t, w) => t + w[0] * w[0] / 1000 / kj, 0), Ct = v.reduce((t, w) => t + w[1] * w[1] / 1000 / kj, 0);
    // radial authority of the elbow: d(dot radial)/d theta2 = -(dot - elbow).y  (perp component), per degree
    console.log(String(Rb).padStart(7), (t2 / DEG).toFixed(0).padStart(9), (rz * 1000).toFixed(0).padStart(14), (tn * 1000).toFixed(0).padStart(14), '   ', Cr.toFixed(4), Ct.toFixed(4));
  }
}
