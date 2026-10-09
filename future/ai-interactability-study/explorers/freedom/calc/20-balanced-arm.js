/* balanced-arm.js - the small model behind freedom-02-balanced-arm. UMD. ILLUSTRATIVE numbers only.
 * A single-joint boom (shoulder) of length L carries a payload. A spring set for design payload md gives torque
 * taus(th) = md g L cos(th) (1 + eps (th - th0)): exact at th0, drifting with slope eps (per rad) elsewhere.
 * Joint friction taf holds the arm while |net torque| <= taf; inside that band the tip still deflects by net/kms
 * (pre-sliding stiffness kms, N*m/rad). Outside it the arm creeps toward the nearest angle where it sticks, or to a stop.
 */
(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else root.FreedomArm = factory(); })(typeof self !== 'undefined' ? self : this, function () {
  const G = 9.80665, D2R = Math.PI / 180;
  const DEF = { th: 5, L: 0.45, m: 1.5, ballast: 0, md: 2.0, eps: 0.15, th0: 5, taf: 0.4, kms: 40, dF: 0, cableOnArm: false, brake: false, thMin: -30, thMax: 50 };
  function net(p, thDeg) {
    const th = thDeg * D2R, mTot = p.m + p.ballast + (p.cableOnArm ? 0.35 : 0);
    const taus = p.md * G * p.L * Math.cos(th) * (1 + p.eps * (th - p.th0 * D2R));
    const taug = mTot * G * p.L * Math.cos(th);
    const dF = p.cableOnArm ? p.dF * 0.25 : p.dF;                   // a cable clipped along the arm passes only part of its pull to the gun
    return { taus: taus, taug: taug, ext: dF * p.L * Math.cos(th), res: taus - taug, net: taus - taug - dF * p.L * Math.cos(th), mTot: mTot, dF: dF };
  }
  function analyse(opts) {
    const p = Object.assign({}, DEF, opts), taf = p.taf * (p.brake ? 20 : 1);
    const cur = net(p, p.th), holds = Math.abs(cur.net) <= taf;
    // window: angles where |net| <= taf
    const win = []; let inW = false, start = 0;
    for (let a = p.thMin; a <= p.thMax + 1e-9; a += 0.25) { const ok = Math.abs(net(p, a).net) <= taf; if (ok && !inW) { inW = true; start = a; } if (!ok && inW) { inW = false; win.push([start, a - 0.25]); } }
    if (inW) win.push([start, p.thMax]);
    let thEq = p.th, state = 'holds';
    if (!holds) {                          // creep in the direction of the net torque until it sticks
      const dir = cur.net > 0 ? 1 : -1; let a = p.th; state = dir > 0 ? 'creeps up' : 'sinks';
      while (a > p.thMin && a < p.thMax && Math.abs(net(p, a).net) > taf) a += dir * 0.05;
      thEq = Math.min(p.thMax, Math.max(p.thMin, a));
      if (thEq <= p.thMin + 0.06 || thEq >= p.thMax - 0.06) state += ' to the stop';
    }
    const eq = net(p, thEq), dth = (Math.abs(eq.net) <= taf ? eq.net / p.kms : 0);
    const th = thEq * D2R, th0 = p.th0 * D2R;
    const tip = { x: p.L * Math.cos(th) - Math.sin(th) * p.L * dth, z: p.L * Math.sin(th) + Math.cos(th) * p.L * dth };
    const tip0 = { x: p.L * Math.cos(th0), z: p.L * Math.sin(th0) };
    return { p: p, taf: taf, cur: cur, holds: holds, state: state, win: win, thEq: thEq, eq: eq, micro: { dth: dth, mm: p.L * 1000 * Math.abs(dth) },
      tipErr: { x: (tip.x - tip0.x) * 1000, z: (tip.z - tip0.z) * 1000 },
      motorBalanced: Math.abs(eq.net) + taf, motorUnbalanced: eq.taug + taf };
  }
  return { analyse: analyse, net: net, DEF: DEF, G: G };
});
