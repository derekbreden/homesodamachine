/* arm.js - wave 2. The small model behind scenes/borrowed-14-arm-mass-window (a branch of freedom-02's balanced arm).
 * ILLUSTRATIVE numbers only. One balanced boom of length L about a shoulder, joint friction taf (N*m), a payload m at the tip.
 * Three springs:
 *   gas   : freedom-02's model, torque = md g L cos(th) (1 + eps (th - th0)); exact at th0, drifting with slope eps elsewhere
 *   coil  : an Anglepoise/mic-boom spring. One end on the arm at distance a from the shoulder, the other on the base at height b
 *           above the shoulder. Length l(th)^2 = a^2 + b^2 - 2 a b sin th. Force k (l - l0). Torque about the shoulder
 *           = k a b cos th (1 - l0 / l). With l0 = 0 (a "zero-length" spring) this is exactly proportional to cos th, so the arm is
 *           balanced at every angle for one payload. A plain spring (l0 > 0) leaves an error that varies with th.
 *   Both are "set for" md kg (the spring rate or preload is chosen so the balance is exact at th0).
 * Net torque = spring - m g L cos th. The arm stays where it is put while |net| <= taf.
 */
(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else root.ArmModel = factory(); })(typeof self !== 'undefined' ? self : this, function () {
  const G = 9.80665, D2R = Math.PI / 180;
  const DEF = { type: 'coil0', L: 0.45, md: 2.3, taf: 0.4, eps: 0.15, th0: 5, a: 0.18, b: 0.12, l0: 0.04, thMin: -20, thMax: 50 };
  function springTorque(p, thDeg) {
    p = Object.assign({}, DEF, p);
    const th = thDeg * D2R, th0 = p.th0 * D2R;
    if (p.type === 'gas') return p.md * G * p.L * Math.cos(th) * (1 + p.eps * (th - th0));
    const len = t => Math.sqrt(p.a * p.a + p.b * p.b - 2 * p.a * p.b * Math.sin(t));
    const l0eff = p.type === 'coil0' ? 0 : p.l0;
    const k = p.md * G * p.L * Math.cos(th0) / (p.a * p.b * Math.cos(th0) * (1 - l0eff / len(th0)));
    return k * p.a * p.b * Math.cos(th) * (1 - l0eff / len(th));
  }
  function net(p, m, thDeg) { p = Object.assign({}, DEF, p); return springTorque(p, thDeg) - m * G * p.L * Math.cos(thDeg * D2R); }
  function analyse(opts, m) {
    const p = Object.assign({}, DEF, opts); const out = { p, m, win: [], holdsAt: null };
    let inW = false, s = 0;
    for (let a = p.thMin; a <= p.thMax + 1e-9; a += 0.25) { const ok = Math.abs(net(p, m, a)) <= p.taf; if (ok && !inW) { inW = true; s = a; } if (!ok && inW) { inW = false; out.win.push([s, a - 0.25]); } }
    if (inW) out.win.push([s, p.thMax]);
    return out;
  }
  // holds at th? if not, where does it go (creeps toward the nearest angle where it sticks, or to a stop)
  function settle(opts, m, thDeg) {
    const p = Object.assign({}, DEF, opts); const n0 = net(p, m, thDeg);
    if (Math.abs(n0) <= p.taf) return { holds: true, th: thDeg, state: 'holds', net: n0 };
    const dir = n0 > 0 ? 1 : -1; let a = thDeg;
    while (a > p.thMin && a < p.thMax && Math.abs(net(p, m, a)) > p.taf) a += dir * 0.05;
    const th = Math.min(p.thMax, Math.max(p.thMin, a)), stop = th <= p.thMin + 0.06 || th >= p.thMax - 0.06;
    return { holds: false, th, state: (dir > 0 ? 'rises' : 'sinks') + (stop ? ' to its stop' : ' until it sticks'), net: n0 };
  }
  // the mismatch (kg) the friction can hold at angle th: |md - m| g L cos th <= taf  ->  taf / (g L cos th)
  function tolKg(p, thDeg) { p = Object.assign({}, DEF, p); return p.taf / (G * p.L * Math.cos(thDeg * D2R)); }
  return { DEF, G, springTorque, net, analyse, settle, tolKg };
});
