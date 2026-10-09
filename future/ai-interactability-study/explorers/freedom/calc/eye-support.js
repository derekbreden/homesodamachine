/* eye-support.js - freedom W2: what a gun-borne eye's trim stage has to absorb, for two ways of holding the gun.
 *
 * Built on statics.js and ringmodel.js (one rigid body on springs; every number ILLUSTRATIVE: mass 1.2 kg, COM, elastic k,
 * seat stiffness, umbilical pull). Two supports, both solved at the kit's opening pose:
 *   'lug'  the eyes-01 arrangement: a rod from the housing top to a stage, the stage hung from one elastic line.
 *          The pivot is the elastic's attachment, `rod` mm above the lug (world up at the reference pose). k = the elastic's stiffness
 *          (N/mm, all three translations); krot = rotational stiffness the stage/support adds about the dot (N*m/rad), 0 = a ball hang.
 *   'seat' freedom-01b: ball collar in a cone seat at station s behind the nozzle + tail bridle (two wires and a yaw bungee pair).
 * The trim is a command on the stage (radial x, vertical z), limited to +/- limit mm.
 * UMD: window.EyeSupport or module.exports.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./statics.js'), require('./ringmodel.js'));
  else root.EyeSupport = factory(root.FreedomStatics, root.FreedomRing);
})(typeof self !== 'undefined' ? self : this, function (FS, FR) {
  'use strict';
  const M = FS.math, DEG = Math.PI / 180;
  const POSE = FS.dialsToPose(45, 30, -15);
  const LUG = [0, 20, 185.5];                     // housing top of the printed sleeve (17 mm + 3 mm clearance)
  const upLocal = len => { const R = POSE.R; return [R[6] * len, R[7] * len, R[8] * len]; };   // R^T (0,0,len)
  const RI = FS.INNER_RADIUS;
  const rad = x => Math.hypot(RI + x[0], x[1]) - RI;      // radial distance of the dot from the seam circle (what an eye sees); a tangent slide s costs s^2/2r
  const DEFAULT = { sup: 'lug', k: 0.5, krot: 0, rod: 70, s: 70, pre: 3, phi: 40, dx: 160, droop: 0.5, Fset: 2, limit: 6 };

  function opts(cfg, F, cmd) {
    const c = Object.assign({}, DEFAULT, cfg);
    const o = { rings: [], kWire: 200, umbilical: { F: F, droop: c.droop } };
    if (c.sup === 'seat') {
      o.arm = { mode: 'none' };
      o.nose = { s: c.s, local: c.seatLocal || null, phi: c.phi, rc: 12, k: 100, preload: c.pre, cmd: cmd.slice() };
      o.tail = { dx: c.dx, wireL: 300, kb: 0.15, pre: 3, wireCmd: [0, 0], yawCmd: 0 };
    } else {
      o.nose = null; o.tail = null;
      const piv = M.add(LUG, upLocal(c.rod));
      if (c.krot > 0) o.arm = { mode: 'rigid', at: piv, k: c.k, kRot: c.krot * 1000, cmd: cmd.slice() };   // N*m/rad -> N*mm/rad
      else o.arm = { mode: 'point', at: piv, k: c.k, cmd: cmd.slice() };
    }
    return o;
  }
  function solve(cfg, F, cmd, x0) {
    const model = FR.build(opts(cfg, F, cmd));
    const res = model.solve(x0 || new Float64Array(model.n), { maxIter: 200 });
    return { model: model, res: res, x: res.x, ok: res.converged };
  }
  // beam direction (local (0,0,-1)) in the world at pose x, and the angle between two poses' beams (deg)
  function beam(model, x) { return M.mv(model.rotOf(x), [0, 0, -1]); }
  function angleBetween(a, b) { return Math.acos(Math.max(-1, Math.min(1, M.dot(a, b)))) / DEG; }

  // The gun is placed by hand at the setup pull: choose the stage command that puts the dot on the seam.
  function setup(cfg) {
    const c = Object.assign({}, DEFAULT, cfg);
    let cmd = [0, 0, 0], r = solve(c, c.Fset, cmd, null);
    for (let i = 0; i < 6 && r.ok; i++) {
      const u = r.x;
      if (Math.max(Math.abs(u[0]), Math.abs(u[1]), Math.abs(u[2])) < 0.003) break;
      cmd = [cmd[0] - u[0] * 0.95, cmd[1] - u[1] * 0.95, cmd[2] - u[2] * 0.95];
      r = solve(c, c.Fset, cmd, r.x);
    }
    return { cmd0: cmd, r: r, beam0: r.ok ? beam(r.model, r.x) : null, tilt0: r.ok ? Math.hypot(r.x[3], r.x[4], r.x[5]) / FS.S / DEG : NaN };
  }
  // one pull change, trim closed on the eye's two numbers (radial and vertical): returns what happened
  function respond(cfg, F, st, trim0, warm) {
    const c = Object.assign({}, DEFAULT, cfg), L = c.limit;
    let trim = (trim0 || [0, 0]).slice(), r = null, x0 = warm || (st.r.ok ? st.r.x : null);
    for (let it = 0; it < 14; it++) {
      const cmd = [st.cmd0[0] + trim[0], st.cmd0[1], st.cmd0[2] + trim[1]];
      r = solve(c, F, cmd, x0); if (!r.ok) break; x0 = r.x;
      const eR = rad(r.x), eZ = r.x[2];
      if (Math.max(Math.abs(eR), Math.abs(eZ)) < 0.004) break;
      trim[0] = Math.max(-L, Math.min(L, trim[0] - 0.85 * eR)); trim[1] = Math.max(-L, Math.min(L, trim[1] - 0.85 * eZ));
    }
    return { r: r, trim: trim, atLimit: Math.abs(trim[0]) >= L - 1e-6 || Math.abs(trim[1]) >= L - 1e-6 };
  }
  // open-loop: dot displacement per newton of pull change (no trim), radial / tangent / vertical, and tilt change (deg per N)
  function perNewton(cfg, dF) {
    const c = Object.assign({}, DEFAULT, cfg), st = setup(c); if (!st.r.ok) return null;
    const r1 = solve(c, c.Fset + (dF || 1), st.cmd0, st.r.x); if (!r1.ok) return null;
    const u = [(rad(r1.x) - rad(st.r.x)) / (dF || 1), (r1.x[1] - st.r.x[1]) / (dF || 1), (r1.x[2] - st.r.x[2]) / (dF || 1)];
    return { u: u, tiltPerN: angleBetween(beam(r1.model, r1.x), st.beam0) / (dF || 1), tilt0: st.tilt0 };
  }
  return { opts: opts, solve: solve, setup: setup, respond: respond, perNewton: perNewton, rad: rad, beam: beam, angleBetween: angleBetween, DEFAULT: DEFAULT, POSE: POSE, LUG: LUG, upLocal: upLocal, DEG: DEG };
});
