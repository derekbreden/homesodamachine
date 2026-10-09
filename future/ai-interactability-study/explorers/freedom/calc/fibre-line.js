/* fibre-line.js - freedom W3: where the fibre umbilical (with the wire conduit) leaves the gun, and what it does to the gun there.
 *
 * The question this answers for a route: what wrench (a force, and a couple) does the cable put on the gun's shell where the last
 * rigid part of the shell lets go of it, how far does the line of that force pass from the dot, and what does the support do with it?
 *
 * Geometry is the kit's proxy gun at a chosen pose (statics.js dialsToPose is a port of WK.dialsToPose). Two facts of that proxy matter:
 *   - the roll axis runs from the dot D to the grip base E (LOCAL_ROLL_AXIS, 279 mm long, 30 degrees above horizontal at the reference pose);
 *   - the umbilical stub leaves E along the GRIP'S RAKE (the direction of the grip), about 30 degrees away from the roll axis,
 *     and only then bends toward it (kit gun builder). The scene calls the angle between the exit tangent and the roll axis `alpha`.
 * Whether the real fibre leaves E along the rake is [unknown]; alpha is a slider.
 *
 * Routes:
 *   clip   : the fibre leaves E along its exit tangent and is clamped by a clip on a gallows; planar elastica in the vertical plane through E
 *            and the tangent's horizontal direction (cable-rod.js, both ends clamped).
 *   tether : a rigid printed boot fixed to the shell turns the fibre onto the roll axis (a single arc, or an S-curve that lands on the line
 *            through the dot); a straight span leaves the boot exit and is held by a swivel collar riding a rail that points along the axis,
 *            pulled along the rail by a constant force (dead weight over a pulley). The bend and its recoil are internal to shell + boot;
 *            only the span's wrench reaches the gun.
 *
 * Everything numeric that describes the cable (EI, weight per metre, GJ) is ILLUSTRATIVE: the real fibre is [unknown].
 * Units: mm, N, N*mm for torques and couples (M vectors here are N*mm), except where a name says N*m.
 * UMD: window.FibreLine or module.exports. Needs statics.js (for the kit's pose port) and cable-rod.js.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./statics.js'), require('./cable-rod.js'));
  else root.FibreLine = factory(root.FreedomStatics, root.CableRod);
})(typeof self !== 'undefined' ? self : this, function (FS, CR) {
  'use strict';
  const M = FS.math, DEG = Math.PI / 180, G = 9.80665;
  const add = M.add, sub = M.sub, mul = M.mul, dot = M.dot, cross = M.cross, len = M.len, norm = M.norm;
  const Z = [0, 0, 1];

  // ------------------------------------------------------------------------------------------------ geometry of the gun at a pose
  const rotX = (v, a) => [v[0], v[1] * Math.cos(a) - v[2] * Math.sin(a), v[1] * Math.sin(a) + v[2] * Math.cos(a)];
  function frame(dials, alphaDeg) {
    const pose = FS.dialsToPose(dials.roll, dials.holeDial, dials.vertical);
    const W = l => add(pose.origin, M.mv(pose.R, l)), dW = l => M.mv(pose.R, l);
    const a = alphaDeg * DEG, uL = FS.ROLL_AXIS;
    const fr = { pose: pose, W: W, dW: dW, alpha: alphaDeg,
      D: W([0, 0, -16]), E: W(FS.GRIP_BASE), u: dW(uL), t: dW(rotX(uL, a)), n: dW(rotX(uL, Math.PI / 2)), X: dW([1, 0, 0]),
      tLocal: rotX(uL, a) };
    fr.localOf = p => { const d = sub(p, pose.origin), R = pose.R; return [R[0] * d[0] + R[3] * d[1] + R[6] * d[2], R[1] * d[0] + R[4] * d[1] + R[7] * d[2], R[2] * d[0] + R[5] * d[1] + R[8] * d[2]]; };
    fr.ell = len(sub(fr.E, fr.D));
    return fr;
  }
  const horiz = v => { const h = [v[0], v[1], 0], l = len(h); return l < 1e-9 ? [1, 0, 0] : mul(h, 1 / l); };
  const toWorld2 = (o, e1, e2, p) => add(o, add(mul(e1, p[0]), mul(e2, p[1])));

  // ------------------------------------------------------------------------------------------------ boots (in the plane of u and the exit tangent)
  // coordinates: x along the roll axis u (away from the dot), y along n (the side the exit tangent lies on); heading measured from u toward n.
  function bootPath(kind, alphaDeg, R) {
    const a = alphaDeg * DEG, pts = [[0, 0]];
    if (kind === 'none' || a < 1e-6) return { pts: pts, end: [0, 0], heading: a, length: 0, offAxis: 0, R: R };
    if (kind === 'arc') {
      const n = Math.max(8, Math.ceil(a / (3 * DEG)));
      for (let i = 1; i <= n; i++) { const th = a - a * i / n; pts.push([R * (Math.sin(a) - Math.sin(th)), R * (Math.cos(th) - Math.cos(a))]); }
      const end = pts[pts.length - 1];
      return { pts: pts, end: end, heading: 0, length: R * a, offAxis: end[1], R: R };
    }
    // S: clockwise from heading a down to -b, then counter-clockwise from -b back to 0; ends on the axis when cos b = (1 + cos a) / 2
    const b = Math.acos((1 + Math.cos(a)) / 2);
    const n1 = Math.max(10, Math.ceil((a + b) / (3 * DEG)));
    for (let i = 1; i <= n1; i++) { const th = a - (a + b) * i / n1; pts.push([R * (Math.sin(a) - Math.sin(th)), R * (Math.cos(th) - Math.cos(a))]); }
    const p1 = pts[pts.length - 1], C2 = [p1[0] + R * Math.sin(b), p1[1] + R * Math.cos(b)];
    const n2 = Math.max(6, Math.ceil(b / (3 * DEG)));
    for (let i = 1; i <= n2; i++) { const th = -b + b * i / n2; pts.push([C2[0] + R * Math.sin(th), C2[1] - R * Math.cos(th)]); }
    const end = pts[pts.length - 1];
    return { pts: pts, end: end, heading: 0, length: R * (a + 2 * b), offAxis: end[1], R: R, beta: b };
  }

  // ------------------------------------------------------------------------------------------------ wrench helpers
  function planarToWrench(res, e1, e2, at) {
    const F2 = res.forceOnStartClamp, F = add(mul(e1, F2[0]), mul(e2, F2[1]));
    const axis = cross(e1, e2), Mv = mul(axis, res.momentOnStartClamp * 1000);            // N*m -> N*mm
    return { at: at, F: F, M: Mv };
  }
  function torqueAbout(P, w) { return add(cross(sub(w.at, P), w.F), w.M); }               // N*mm
  function sumWrenches(P, list) { let F = [0, 0, 0], T = [0, 0, 0]; list.forEach(w => { F = add(F, w.F); T = add(T, torqueAbout(P, w)); }); return { F: F, T: T }; }
  // perpendicular distance from point P to the line of force F through `at` (mm); 0 when F is zero
  function lineOffset(P, at, F) { const l = len(F); return l < 1e-9 ? 0 : len(cross(sub(P, at), F)) / l; }

  // ------------------------------------------------------------------------------------------------ route 1: clip on a gallows
  // The designed route is a circular arc that leaves E along the exit tangent, turns by psi in the vertical plane through the tangent's horizontal
  // direction (up: turn = +1, down: turn = -1) at radius R, and ends in a clip that holds the fibre in the arc's own direction: the fibre is then
  // stress-free apart from its bending moment EI/R, its weight and whatever the clip's mismatch adds.
  // p = { dials, alpha, R (mm, route radius; the manual asks for at least 350), psi (deg), turn (+1 up / -1 down), errPos (mm, clip off the arc's end, normal to the arc),
  //       errAng (deg, clip direction off the arc's), slack (mm of extra fibre), EI, w (bundle N*m^2, N/m), N, dFar (mm the clip gives, normal to the chord), init }
  function routeClip(p) {
    const fr = frame(p.dials, p.alpha), h = horiz(fr.t), e2 = Z, E = fr.E;
    const th0 = Math.atan2(dot(fr.t, e2), dot(fr.t, h)), psi = p.psi * DEG, turn = p.turn >= 0 ? 1 : -1, R = p.R;
    const t0 = [Math.cos(th0), Math.sin(th0)], nrm0 = turn > 0 ? [-t0[1], t0[0]] : [t0[1], -t0[0]];          // toward the centre of the turn
    const cen = [R * nrm0[0], R * nrm0[1]], r0 = [-cen[0], -cen[1]];
    const rot = (v, a) => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a)];
    const thEnd = th0 + turn * psi, rEnd = rot(r0, turn * psi), Cnat = [cen[0] + rEnd[0], cen[1] + rEnd[1]];
    const arcLen = R * psi, L = arcLen + (p.slack || 0);
    const tEnd = [Math.cos(thEnd), Math.sin(thEnd)], nEnd = [-tEnd[1], tEnd[0]];
    let C = [Cnat[0] + (p.errPos || 0) * nEnd[0], Cnat[1] + (p.errPos || 0) * nEnd[1]];
    if (p.dFar) { const ch = Math.hypot(C[0], C[1]) || 1, px = -C[1] / ch, py = C[0] / ch; C = [C[0] + p.dFar * px, C[1] + p.dFar * py]; }
    const thClip = thEnd + (p.errAng || 0) * DEG, chord = Math.hypot(C[0], C[1]);
    const res = CR.solve({ p0: [0, 0], th0: th0, L: L, EI: p.EI, w: p.w, g: [0, -1], N: p.N || 80, init: p.init, end: { type: 'clamp', p: C, th: thClip } });
    if (!res.ok) return { ok: false, fr: fr, reason: res.reason || 'no equilibrium', res: res, arcLen: arcLen, chord: chord };
    const wr = planarToWrench(res, h, e2, E);
    return { ok: true, fr: fr, res: res, wrench: wr, h: h, e1: h, e2: e2, origin: E, curve: res.pts.map(q => toWorld2(E, h, e2, q)), clip: toWorld2(E, h, e2, C),
      clipDir: add(mul(h, Math.cos(thClip)), mul(e2, Math.sin(thClip))), minR: res.minR, length: L, arcLen: arcLen, chord: chord, exitAt: E, exitDir: fr.t, hasBoot: false, th0: th0, thClip: thClip };
  }

  // ------------------------------------------------------------------------------------------------ route 2: boot + straight span on a rail
  // p = { dials, alpha, boot ('S'|'arc'|'none'), Rb, Ls (span length), F (rail force N), Lp (rail length beyond the collar's nominal place), aimV, aimS (mm the
  //       pulley end of the rail is off the line, in the vertical plane / sideways), EI, w, N, dFar (extra pulley move, in plane), mBoot (kg) }
  function routeTether(p) {
    const fr = frame(p.dials, p.alpha), bp = bootPath(p.boot, p.alpha, p.Rb || 350);
    const B = p.boot === 'none' ? fr.E : add(fr.E, add(mul(fr.u, bp.end[0]), mul(fr.n, bp.end[1])));
    const d0 = p.boot === 'none' ? fr.t : fr.u, h = horiz(d0), e2 = Z, th0 = Math.atan2(dot(d0, e2), dot(d0, h)), side = norm(cross(e2, h));
    // the rail (pulley end) is aimed at the reference roll and stays in the world when the gun rolls
    const fr0 = p.dialsRef ? frame(p.dialsRef, p.alpha) : fr, bp0 = bootPath(p.boot, p.alpha, p.Rb || 350);
    const B0 = p.boot === 'none' ? fr0.E : add(fr0.E, add(mul(fr0.u, bp0.end[0]), mul(fr0.n, bp0.end[1])));
    const d00 = p.boot === 'none' ? fr0.t : fr0.u, h0 = horiz(d00), th00 = Math.atan2(dot(d00, e2), dot(d00, h0)), side0 = norm(cross(e2, h0));
    const dist = p.Ls + p.Lp, nv0 = add(mul(h0, -Math.sin(th00)), mul(e2, Math.cos(th00)));
    const aimV = (p.aimV || 0) + (p.dFar || 0);
    const Pw = add(add(B0, mul(d00, dist)), add(mul(nv0, aimV), mul(side0, p.aimS || 0)));
    const rel = sub(Pw, B), P2 = [dot(rel, h), dot(rel, e2)], sideOff = dot(rel, side);
    const sh = norm2(P2), nrm = [-sh[1], sh[0]];
    const res = CR.solve({ p0: [0, 0], th0: th0, L: p.Ls, EI: p.EI, w: p.w, g: [0, -1], N: p.N || 60, init: p.init, end: { type: 'rail', p: P2, n: nrm, F: mul2(sh, p.F) } });
    if (!res.ok) return { ok: false, fr: fr, boot: bp, reason: res.reason || 'no equilibrium', res: res };
    const wr = planarToWrench(res, h, e2, B);
    // sideways aim: string part F*delta on the gun, beam part 3 EI delta / L^2 at the collar (a lateral tip load on a cantilever)
    const dS = sideOff / Math.max(1, Math.hypot(P2[0], P2[1])), EIm = p.EI * 1e6, fBeam = 3 * EIm * dS / (p.Ls * p.Ls), fStr = p.F * dS;
    const wrS = { at: B, F: mul(side, fBeam + fStr), M: mul(cross(d0, side), p.Ls * fBeam) };
    const curveSpan = res.pts.map(q => toWorld2(B, h, e2, q)), C = curveSpan[curveSpan.length - 1];
    const bootWorld = bp.pts.map(q => add(fr.E, add(mul(fr.u, q[0]), mul(fr.n, q[1]))));
    return { ok: true, fr: fr, res: res, boot: bp, bootWorld: bootWorld, wrench: { at: B, F: add(wr.F, wrS.F), M: add(wr.M, wrS.M) }, list: [wr, wrS], h: h, e1: h, e2: e2, origin: B,
      span: curveSpan, collar: C, pulley: Pw, minR: res.minR, exitAt: B, exitDir: d0, hasBoot: p.boot !== 'none', sag: sagOf(res.pts), side: side, rail: sh, dist: dist, sideOff: sideOff };
  }
  const norm2 = v => { const l = Math.hypot(v[0], v[1]) || 1; return [v[0] / l, v[1] / l]; }, mul2 = (v, s) => [v[0] * s, v[1] * s];
  function sagOf(pts) { const a = pts[0], b = pts[pts.length - 1], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; let m = 0; pts.forEach(q => { m = Math.max(m, Math.abs((q[0] - a[0]) * dy - (q[1] - a[1]) * dx) / l); }); return m; }

  // ------------------------------------------------------------------------------------------------ roll: twist and swing of the exit tangent
  // The gun rolls by dRollDeg about the roll axis u (E and D stay fixed). The fibre's clamp frame rotates with it: the part of that rotation about the
  // (new) tangent is twist; the rest turns the tangent (swing).
  function quatAxisAngle(axis, ang) { const s = Math.sin(ang / 2), a = norm(axis); return [a[0] * s, a[1] * s, a[2] * s, Math.cos(ang / 2)]; }
  function qmul(a, b) { return [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0], a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]]; }
  const qinv = q => [-q[0], -q[1], -q[2], q[3]];
  function qrot(q, v) { const p = [v[0], v[1], v[2], 0], r = qmul(qmul(q, p), qinv(q)); return [r[0], r[1], r[2]]; }
  function qfromTo(a, b) { const c = cross(a, b), d = dot(a, b); if (d < -0.999999) { const o = Math.abs(a[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0]; return quatAxisAngle(cross(a, o), Math.PI); } const q = [c[0], c[1], c[2], 1 + d], l = Math.hypot(q[0], q[1], q[2], q[3]); return q.map(v => v / l); }
  function twistSwing(alphaDeg, dRollDeg) {
    const uL = FS.ROLL_AXIS, tL = rotX(uL, alphaDeg * DEG);
    const q = quatAxisAngle(uL, dRollDeg * DEG), t1 = qrot(q, tL);
    const sw = qfromTo(tL, t1), tw = qmul(qinv(sw), q);                                        // q = sw * tw ; tw is a rotation about tL
    const twAngle = 2 * Math.atan2(dot([tw[0], tw[1], tw[2]], tL), tw[3]);
    const swing = Math.acos(Math.max(-1, Math.min(1, dot(tL, t1)))) / DEG;
    const wrap = a => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };
    return { twistDeg: wrap(twAngle) / DEG, swingDeg: swing, tangentAfter: t1 };
  }
  // Linearised beam response of a clamped-clamped fibre of free length L (mm) to the roll: twist torque, bending moment, lateral force on the gun.
  // EI, GJ in N*m^2. Returns N*mm and N. (Small-angle: the swing part uses 4EI/L and 6EI/L^2 for one clamped end rotated by the swing angle.)
  function rollWrenchClamped(alphaDeg, dRollDeg, L, EI, GJ) {
    const ts = twistSwing(alphaDeg, dRollDeg), EIm = EI * 1e6, GJm = GJ * 1e6, sw = ts.swingDeg * DEG, tw = ts.twistDeg * DEG;
    return { twistDeg: ts.twistDeg, swingDeg: ts.swingDeg, torqueTwist: GJm * tw / L, momentBend: 4 * EIm * sw / L, forceLat: 6 * EIm * sw / (L * L) };
  }

  // ------------------------------------------------------------------------------------------------ what a support does with a change of wrench
  // A deliberately plain support: it holds the gun at a pivot P (a mm from the dot) with translational stiffness kt (N/mm) and rotational stiffness kr (N*m/rad).
  //   translation of the pivot       = dF / kt
  //   torque about the pivot         = dTau_D + (D - P) x dF        (dTau_D is the change of torque about the dot, N*mm)
  //   rotation about the pivot       = torque / kr                   (rad, as a vector)
  //   dot shift                      = translation + rotation x (D - P)
  // The presets are round numbers chosen to be consistent with the statics of freedom-01b and freedom-11 (calc/30, calc/35): they are illustrative.
  const SUPPORTS = {
    arm: { label: 'arm with a rigid grip (0.5 N/mm at the housing top, rotation held)', kt: 0.5, krot: 100, a: 200 },
    seat: { label: 'nose seat and tail bridle (about 10 N/mm, 20 N*m/rad, pivot 70 mm from the dot)', kt: 10, krot: 20, a: 70 },
    elastic: { label: 'one elastic line, rotation held only by gravity (0.5 N/mm, 0.42 N*m/rad)', kt: 0.5, krot: 0.42, a: 140 },
  };
  function supportShift(sup, fr, dF, dTau) {
    const kr = sup.krot * 1000, D = fr.D;
    // pivot P: a mm from the dot toward the grip along the barrel (kit local +Z)
    const P = fr.W([0, 0, -16 + sup.a]);
    const rDP = sub(D, P), transl = mul(dF, 1 / sup.kt);
    const tauP = add(dTau, cross(rDP, dF)), rot = mul(tauP, 1 / kr), fromRot = cross(rot, rDP);
    const dot3 = add(transl, fromRot);
    return { dot: dot3, total: len(dot3), turnDeg: len(rot) / DEG, translation: len(transl), fromRotation: len(fromRot) };
  }

  return { frame: frame, bootPath: bootPath, routeClip: routeClip, routeTether: routeTether, twistSwing: twistSwing, rollWrenchClamped: rollWrenchClamped,
    torqueAbout: torqueAbout, sumWrenches: sumWrenches, lineOffset: lineOffset, supportShift: supportShift, SUPPORTS: SUPPORTS, horiz: horiz, G: G };
});
