// wall-window.mjs (eyes, wave 2) - numbers behind scenes/eyes-14-wall-as-window (branch of room-03, the wall port).
// The gun sits on a rod through a ball in a lid; outside the lid the rod carries the tail, actuators and (proposed) scales.
// One bending moment M0 = F d passes through the ball: it bends the inside segment (gun end) and the outside tail. Beam model:
//   inside  s in [0, d]  : y_b(s) = -F s^2 (3d - s) / (6 EI)
//   outside s in [-Lt,0] : y_b(s) = -(F d / (Lt EI)) (Lt s^2 / 2 + s^3 / 6)
// with y_b(0) = 0 and zero slope at the ball. The actuators hold the tail point at its commanded place (y = 0 at s = -Lt) and the
// ball sits delta off its commanded place, so the real rod is y(s) = y_b(s) + tau s + delta, tau = (y_b(-Lt) + delta) / Lt.
// Everything here is [illustrative] (aluminium tube wall 2 mm, E 69 GPa, load at the dot end). Run: node explorers/eyes/calc/wall-window.mjs
const G = 9.81, E = 69000;
function model(p) {
  const I = Math.PI / 64 * (p.OD ** 4 - (p.OD - 4) ** 4), EI = E * I;
  const F = p.m * G * Math.sin(p.phi * Math.PI / 180) + p.Fc;
  const yb = (s, F_ = F, EI_ = EI) => s >= 0 ? -F_ * s * s * (3 * p.d - s) / (6 * EI_) : -(F_ * p.d / (p.Lt * EI_)) * (p.Lt * s * s / 2 + s ** 3 / 6);
  const tau = (yb(-p.Lt) + p.delta) / p.Lt;
  const y = s => yb(s) + tau * s + p.delta;
  return { I, EI, F, yb, tau, y };
}
export function errors(p) {
  const M = model(p), s1 = -p.a1, s2 = -p.a2, d = p.d;
  const yt = M.y(d);                                        // truth at the dot end, lateral, vs the commanded line
  const e1 = -yt;                                            // step counts believe 0
  const k = (d - s1) / (s2 - s1), m1 = M.y(s1), m2 = M.y(s2), e2 = m1 * (1 - k) + m2 * k;   // naive straight line through the two stations
  const n2 = p.sS * Math.hypot(1 - k, k);
  // model-based: subtract a bend model with (F_est, EI_est), fit the rigid line through the two residuals, extrapolate, add the model back
  const est = (Fe, EIe) => {
    const r1 = m1 - M.yb(s1, Fe, EIe), r2 = m2 - M.yb(s2, Fe, EIe);
    return M.yb(d, Fe, EIe) + r1 * (1 - k) + r2 * k;
  };
  const e3 = est(M.F, M.EI * (1 + p.eEI));
  const dF = 0.01, dydF = (est(M.F + dF, M.EI) - est(M.F, M.EI)) / dF;
  const n3 = Math.hypot(n2, dydF * p.sF * p.Lt / d);
  return { yt, tail: M.yb(-p.Lt), tipflex: M.yb(d), tauMrad: M.tau * 1000, EI: M.EI,
    steps: { bias: yt, noise: 0, total: Math.abs(yt) },
    line: { bias: e2 - yt, noise: n2, total: Math.hypot(e2 - yt, n2) },
    model: { bias: e3 - yt, noise: n3, total: Math.hypot(e3 - yt, n3) },
    playAtDot: p.delta * (1 + d / p.Lt) };
}
const base = { d: 400, Lt: 800, OD: 20, m: 1.5, Fc: 2, phi: 45, delta: 0.05, a1: 120, a2: 400, sS: 0.01, sF: 0.1, eEI: 0.05 };
if (process.argv[1] && process.argv[1].endsWith('wall-window.mjs')) {
  const f = x => x.toFixed(3);
  const show = (tag, p) => { const r = errors(p); console.log(tag.padEnd(34), 'tail droop', f(r.tail), 'tip flex', f(r.tipflex), '| dot error: steps', f(r.steps.total), ' line', f(r.line.total), '(bias ' + f(r.line.bias) + ')', ' model', f(r.model.total), '(bias ' + f(r.model.bias) + ', noise ' + f(r.model.noise) + ')'); };
  show('default (OD 20)', base);
  for (const OD of [12, 16, 25, 30, 40, 50]) show('OD ' + OD, { ...base, OD });
  show('OD 40, no play', { ...base, OD: 40, delta: 0 });
  show('OD 20, stations near ball 60,180', { ...base, a1: 60, a2: 180 });
  show('OD 20, a1 120 a2 800', { ...base, a2: 800 });
  show('OD 20, Lt 400', { ...base, Lt: 400 });
  show('OD 20, Fc 0', { ...base, Fc: 0 });
  show('OD 20, EI unc 0', { ...base, eEI: 0 });
  show('OD 20, EI unc 20%', { ...base, eEI: 0.2 });
  show('OD 30', { ...base, OD: 30 });
}
