// End-of-bead escape model (wave 3). Kit proxy gun at the opening pose (ILLUSTRATIVE), the tube turning at 8 mm/s under a
// fixed pedal. Everything here is a simple kinematic and static model; the scene use-18-end-of-bead-escapes runs the same code.
//
// State at the start of the escape (t = 0): the trigger is held, the laser is on, the wire is fed at f = 12 mm/s [repo], the
// tube turns 8 mm/s [repo]. The wire tip is at the puddle P, which from now on rides with the tube (the tip freezes into the
// bead). The guide exit G is on the gun. The free wire needs length l(t) = |G - P|; the feeder supplies l0 + f t. When the
// need exceeds the supply by the slack allowance d_b the wire is in tension and breaks at the fused tip: in the air.
//   deficit(t) = l(t) - l0 - f t      (negative: the wire is being fed into a freezing bead = a stub, the stuck-wire risk)
// Unknown: d_b (elastic stretch, roll slip and conduit slack: illustrative 0.3 mm), the fused joint's strength Fb, the mover's limit.
import { world, sub, add, mul, unit, dot, cross, norm, fmt, DEG, rotAbout } from './pose.mjs';

const W = l => world(l, 45, 30, -15);
const N0 = W([0, 0, 0]), D0 = W([0, 0, -16]);
const beam = unit(sub(D0, N0)), aBack = mul(beam, -1);
// kit constants: guide back (0,-24.7,87.1), direction to the tip length 106.0; guide length 40 -> guide end at 66 mm from the dot
const gb = [0, -24.7, 87.1], tipL = [0, 0, -16];
const gv = sub(gb, tipL), gl = norm(gv), gdir = mul(gv, 1 / gl);
const geL = sub(gb, mul(gdir, 40));
const G0 = W(geL), wOut = unit(sub(G0, D0)), L0 = norm(sub(G0, D0));
const Zb = [0, 0, 1];
const U = 8, F = 12;                                             // mm/s: seam speed and wire feed [repo]
const omega = U / 61.85;                                         // rad/s of the work about the tube axis (CCW from above)

// profile: distance s(t) for a trapezoid to distance D with vmax, amax
function profile(D, vmax, amax) {
  const ta = vmax / amax, da = 0.5 * amax * ta * ta;
  let tp, vp; if (2 * da >= D) { tp = Math.sqrt(D / amax); vp = amax * tp; return { T: 2 * tp, s: t => t <= tp ? 0.5 * amax * t * t : t <= 2 * tp ? D - 0.5 * amax * (2 * tp - t) ** 2 : D, v: t => t <= tp ? amax * t : t <= 2 * tp ? amax * (2 * tp - t) : 0, vpk: vp }; }
  const tc = (D - 2 * da) / vmax, T = 2 * ta + tc;
  return { T, s: t => t <= ta ? 0.5 * amax * t * t : t <= ta + tc ? da + vmax * (t - ta) : t <= T ? D - 0.5 * amax * (T - t) ** 2 : D, v: t => t <= ta ? amax * t : t <= ta + tc ? vmax : t <= T ? amax * (T - t) : 0, vpk: vmax };
}
// arrangement -> function of path parameter s giving {gunShift (world vector for gun points), work: {dz}} and derived direction
export function escapeSim(o) {
  const pr = profile(o.stroke, o.vmax, o.amax);
  const T = Math.max(pr.T, 0.001) + 0.3;                        // keep turning 0.3 s after the stroke
  const dt = 0.001, n = Math.ceil(T / dt);
  let gunAt, workDz;
  if (o.kind === 'line') { const d = o.dir; gunAt = (p, s) => add(p, mul(d, s)); workDz = () => 0; }
  else if (o.kind === 'pivot') {
    const H = add(N0, mul([0, -1, 0], o.R)); const ax = [1, 0, 0];  // hinge about a radial line, R behind the nozzle, level with it
    gunAt = (p, s) => rotAbout(p, H, ax, s / o.R); workDz = () => 0;
  } else if (o.kind === 'drop') { gunAt = p => p; workDz = s => -s; }
  const rows = []; let broke = null, fused = true, deficit = 0, sBreak = null, tBreak = null, stall = null, maxTen = 0;
  let P = D0.slice(), prevL = L0;
  const sIn = t => Math.min(t, pr.T);
  const stopAt = o.stallStroke != null ? o.stallStroke : null;
  let sHold = null;
  for (let i = 0; i <= n; i++) {
    const t = i * dt;
    let s = pr.s(Math.min(t, pr.T));
    if (sHold != null) s = Math.min(s, sHold);
    // bead point rides with the tube: rotate D0 about the tube axis by omega t, then the work drop
    const th = omega * t, c = Math.cos(th), sn = Math.sin(th);
    P = [D0[0] * c - D0[1] * sn, D0[0] * sn + D0[1] * c, D0[2] + workDz(s)];
    const G = gunAt(G0, o.kind === 'drop' ? 0 : s), N = gunAt(N0, o.kind === 'drop' ? 0 : s);
    const ell = norm(sub(G, P));
    deficit = ell - L0 - F * t;
    // fused: tension once deficit exceeds 0; mover stalls if the tension the mover can deliver along the wire is below Fb
    if (fused && deficit >= o.slack) {
      const wdir = unit(sub(G, P));                            // guide -> tip line, wire tension acts along it
      const along = Math.max(0.05, Math.abs(dot(o.moveDir || wOut, wdir)));
      const Tdel = o.Flim / along;                             // wire tension when the mover pushes its limit: T along the wire has T*along in the mover's direction
      if (Tdel >= o.Fb) { fused = false; broke = 'in the air during the escape'; tBreak = t; sBreak = s; }
      else if (sHold == null) { sHold = s; stall = { t, s, T: Tdel }; }
      maxTen = Math.max(maxTen, Math.min(o.Fb, Tdel));
    }
    rows.push({ t, s, ell, deficit, P, G, N, fused });
    if (!fused && t > tBreak + 0.05) break;
  }
  return { rows, broke, tBreak, sBreak, stall, T, pr };
}
// quick self-test with plausible settings
if (process.argv[1] && process.argv[1].endsWith('w3_escape.mjs')) {
  const base = { slack: 0.3, Fb: 20, stroke: 20, vmax: 40, amax: 800 };
  const cases = {
    'plunge along the barrel, 40 mm/s': { ...base, kind: 'line', dir: aBack, Flim: 25 },
    'plunge along the wire axis, 40 mm/s': { ...base, kind: 'line', dir: wOut, Flim: 25 },
    'vertical lift, 40 mm/s': { ...base, kind: 'line', dir: Zb, Flim: 25 },
    'pivot 262 mm, tip 60 mm/s': { ...base, kind: 'pivot', R: 262, vmax: 60, Flim: 25 },
    'work drop 28 mm at 60 mm/s': { ...base, kind: 'drop', stroke: 28, vmax: 60, Flim: 30, moveDir: Zb },
    'work drop, limit 8 N': { ...base, kind: 'drop', stroke: 28, vmax: 60, Flim: 8, moveDir: Zb },
    'plunge, slow 8 mm/s': { ...base, kind: 'line', dir: aBack, vmax: 8, Flim: 25 },
    'plunge, fused hard (Fb 60 N, limit 25 N)': { ...base, kind: 'line', dir: aBack, Flim: 25, Fb: 60 },
  };
  console.log('wire axis', fmt(wOut, 3), 'free length', L0.toFixed(1), 'mm; barrel axis back', fmt(aBack, 3));
  for (const [k, c] of Object.entries(cases)) {
    const r = escapeSim(c);
    const last = r.rows[r.rows.length - 1];
    const minDef = Math.min(...r.rows.map(x => x.deficit));
    console.log(k.padEnd(44), '| break:', r.broke ? r.broke + ' at t=' + (r.tBreak * 1000).toFixed(0) + ' ms, stroke ' + r.sBreak.toFixed(2) + ' mm' : (r.stall ? 'STALLS at stroke ' + r.stall.s.toFixed(2) + ' mm (mover can deliver ' + r.stall.T.toFixed(1) + ' N along the wire)' : 'no break'), '| most slack (stub) ', (-minDef).toFixed(2), 'mm');
  }
}
