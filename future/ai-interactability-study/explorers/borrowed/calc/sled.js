/* sled.js - wave 2. The small model behind scenes/borrowed-15-sled-keel (a branch of freedom-08's plumb-bob gun).
 * ILLUSTRATIVE numbers only: gun mass, centre of mass, cable pull and every damper value are not measured.
 *
 * One rotation (pitch about a gimbal pivot above the gun) of a hanging body. The angle th is measured from the plumb
 * equilibrium (the working pose, after the trim has been set for the steady pull). The model has:
 *   gravity: S = M*lc + mk*dk (kg*m, the pendulum "moment"); torque -S g sin(th); spring K = S g at th = 0
 *   inertia: I = Igk*M + M lc^2 + mk dk^2  (Igk*M is the gun's own about its centre of mass)
 *   damper : c (N*m*s/rad, viscous) plus a little bearing friction c0
 *   step   : at t = t0 the cable's pull changes by dF at lever e from the pivot, plus a couple dC at the exit (a clamped, bent
 *            fibre pushes back with a moment as well as a force); torque tau = dF*e + dC
 *   trim   : optional loop. A tilt sensor reads th; a trim mass ms on a screw moves x from the centre (torque -ms g x),
 *            integral action x' = ki*th, limited to +-xmax and to a slew rate
 * The dot moves by elldot * th (small angle); the scene draws the real rotation.
 */
(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else root.SledModel = factory(); })(typeof self !== 'undefined' ? self : this, function () {
  const G = 9.80665;
  const DEF = { M: 1.2, lc: 0.036, mk: 0.6, dk: 0.20, Igk: 0.0075, c: 0.02, c0: 0.004, e: 0.145, dF: 1.0, dC: 0, elldot: 0.202, t0: 0.5,
    trim: false, ms: 0.1, xmax: 0.03, slew: 0.005, ki: 0.06, tol: 0.15, speed: 8 };
  function derived(opts) {
    const p = Object.assign({}, DEF, opts);
    const S = p.M * p.lc + p.mk * p.dk, K = S * G, I = p.Igk * p.M + p.M * p.lc * p.lc + p.mk * p.dk * p.dk;
    const w0 = Math.sqrt(K / I), T = 2 * Math.PI / w0, ctot = p.c + p.c0, ccrit = 2 * Math.sqrt(I * K), zeta = ctot / ccrit;
    const tau = p.dF * p.e + p.dC;                          // step torque about the pivot, N*m
    const thss = tau / K;                                   // small-angle static lean, rad
    const trimAuth = p.ms * G * p.xmax;                     // N*m the trim mass can supply
    return { p, S, K, I, w0, T, zeta, ccrit, tau, thss, dotss: thss * p.elldot * 1000, trimAuth, trimPull: p.e > 0 ? trimAuth / p.e : Infinity,
      drop: 1.18 * T / 4,                                   // horizontal to vertical, as a Steadicam operator's drop test reads it
      mtot: p.M + p.mk, mmPerN: (p.e / K) * p.elldot * 1000, mmPerNm: (1 / K) * p.elldot * 1000 };
  }
  function simulate(opts, tEnd, dt) {
    const d = derived(opts), p = d.p; dt = dt || 0.002; const n = Math.round(tEnd / dt), ctot = p.c + p.c0;
    let th = 0, om = 0, x = 0, t = 0, peak = 0, peakT = 0, timeOut = 0, lastOut = 0; const trace = [];
    // I th'' = -S g sin th - ctot th' + tau_step - ms g x
    function f(th, om, x, t) { const step = t >= p.t0 ? d.tau : 0, tt = p.trim ? -p.ms * G * x : 0; return (-d.S * G * Math.sin(th) - ctot * om + step + tt) / d.I; }
    for (let i = 0; i <= n; i++) {
      const dotmm = th * p.elldot * 1000; trace.push({ t, th, dot: dotmm, x });
      const a = Math.abs(dotmm); if (t >= p.t0) { if (a > peak) { peak = a; peakT = t; } if (a > p.tol) { timeOut += dt; lastOut = t; } }
      const k1v = f(th, om, x, t), k1x = om;
      const k2v = f(th + 0.5 * dt * k1x, om + 0.5 * dt * k1v, x, t + 0.5 * dt), k2x = om + 0.5 * dt * k1v;
      const k3v = f(th + 0.5 * dt * k2x, om + 0.5 * dt * k2v, x, t + 0.5 * dt), k3x = om + 0.5 * dt * k2v;
      const k4v = f(th + dt * k3x, om + dt * k3v, x, t + dt), k4x = om + dt * k3v;
      th += dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6; om += dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6;
      if (p.trim) { let dx = p.ki * th * dt; const lim = p.slew * dt; dx = Math.max(-lim, Math.min(lim, dx)); x = Math.max(-p.xmax, Math.min(p.xmax, x + dx)); }
      t += dt;
    }
    return Object.assign(d, { trace, peak, peakT, timeOut, beadOut: timeOut * p.speed, lastOut });
  }
  return { simulate, derived, DEF, G };
});
