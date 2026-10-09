/* ringmodel.js - builds the ring-and-bungee suspension of freedom-01 (and its branches) as a FreedomStatics model.
 *
 * Everything numeric here is ILLUSTRATIVE: mass, centre of mass, umbilical pull, bungee stiffness, ring fit
 * stiffness, arm stiffness. The kit's gun geometry is a proxy (kit/README.md). The point of the model is the
 * pattern (which motion is free, what carries what, how a command reaches the dot), not the digits.
 *
 * UMD: window.FreedomRing or module.exports. Needs statics.js first (window.FreedomStatics / require).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./statics.js'));
  else root.FreedomRing = factory(root.FreedomStatics);
})(typeof self !== 'undefined' ? self : this, function (FS) {
  'use strict';
  const M = FS.math;

  // named body-local points (kit gun proxy frame: origin nozzle tip, +Z back, -Y grip side)
  const LOCAL = {
    dot: [0, 0, -16], nozzleTip: [0, 0, 0], barrelMid: [0, 0, 77], collar: [0, 0, 109],
    housingTop: [0, 17, 185.5], housingCtr: [0, 0, 185.5], housingBack: [0, 0, 253],
    gripMid: [0, -68, 202], gripBase: [0, -118, 237],
    cablePair: [11.5, -118 + FS.ROLL_AXIS[1] * 20, 237 + FS.ROLL_AXIS[2] * 20],
  };
  const DEFAULTS = {
    pose: { roll: 45, holeDial: 30, vertical: -15 },       // the reference scene's opening pose (illustrative)
    mass: 1.2,                                             // kg gun + shell (ILLUSTRATIVE; gun mass is [unknown])
    com: [0, -18, 178],                                    // local; ILLUSTRATIVE
    umbilical: { F: 2.0, droop: 0.5 },                     // N pull at the cable exit; droop 0 = along exit, 1 = straight down
    trigger: 0,                                            // N pushed into the grip along local -Y? (kept simple: local +Y push at gripTop)
    wireL: 500,                                            // mm hanging wires
    cableW: 2,                                             // N of cable weight a pickup ring takes (ILLUSTRATIVE)
    fmax: 4,                                               // N axial friction hold of a rubber-coated loop (ILLUSTRATIVE)
    carry: 0.9,                                            // fraction of the weight the wires are adjusted to carry at setup
    kWire: 200, kLat: 50, kSeat: 50, kCable: 0.03,         // N/mm (ILLUSTRATIVE)
    arm: { mode: 'point', at: 'housingTop', k: 5, kRot: 1e5, cmd: [0, 0, 0] },
    rings: [
      { id: 'tip', at: 'tip', s: 40, contact: 'loop', axis: 'y', kb: 0.15, pre: 3 },
      { id: 'base', at: 'base', contact: 'loop', axis: 'x', kb: 0.15, pre: 3 },
    ],
  };
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function merge(a, b) { for (const k in b) { if (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]) && a[k] && typeof a[k] === 'object' && !Array.isArray(a[k])) merge(a[k], b[k]); else a[k] = b[k]; } return a; }

  // body-local station for a ring: {local point on the axis, axis (local), radius}
  function ringGeom(r) {
    if (r.at === 'tip') return { local: [0, 0, r.s == null ? 40 : r.s], axis: [0, 0, 1] };
    if (r.at === 'housing') return { local: [0, 0, r.s == null ? 185 : r.s], axis: [0, 0, 1] };
    if (r.at === 'base') { const d = r.d == null ? 20 : r.d; return { local: [11.5, FS.GRIP_BASE[1] + FS.ROLL_AXIS[1] * d, FS.GRIP_BASE[2] + FS.ROLL_AXIS[2] * d], axis: FS.ROLL_AXIS.slice() }; }
    if (r.at === 'gripBase') return { local: LOCAL.gripBase.slice(), axis: FS.ROLL_AXIS.slice() };
    throw new Error('unknown ring station ' + r.at);
  }

  function build(opts) {
    const o = merge(clone(DEFAULTS), opts || {});
    const pose = FS.dialsToPose(o.pose.roll, o.pose.holeDial, o.pose.vertical);
    const body = { mass: o.mass, com: o.com, ref: pose, dotLocal: LOCAL.dot };
    const wp = (l) => M.add(pose.origin, M.mv(pose.R, M.sub(l, [0, 0, 0])));
    const nodes = [], els = [];
    const g = { W: o.mass * FS.G };
    const rings = o.rings.filter(r => !r.off);
    // nodes and their supports
    const wireEls = [];
    rings.forEach(function (r, i) {
      const gm = ringGeom(r), p = wp(gm.local);
      nodes.push({ name: r.id, p0: p });
      r._i = i; r._geom = gm; r._p = p;
      const top = [p[0], p[1], p[2] + o.wireL];
      const wire = { type: 'spring', a: { node: i }, b: { world: top }, k: o.kWire, L0: o.wireL, slack: true, name: 'wire ' + r.id, group: 'wires', ringId: r.id };
      els.push(wire); wireEls.push(wire);
      // bungee pair along world X or Y (D mm each side)
      const D = 260, ax = r.axis === 'x' ? [1, 0, 0] : [0, 1, 0];
      [1, -1].forEach(function (sgn) {
        const anchor = M.add(p, M.mul(ax, sgn * D));
        els.push({ type: 'spring', a: { node: i }, b: { world: anchor }, k: r.kb, L0: D - r.pre / r.kb, slack: true, name: 'bungee ' + r.id + (sgn > 0 ? '+' : '-'), group: 'bungees', ringId: r.id });
      });
      // contact between ring node and the body
      if (r.contact === 'cable') {
        // ring picks up the umbilical/wire bundle: the ring is NOT on the shell. The cable is a weak spring from
        // the grip base to the ring.
        els.push({ type: 'spring', a: { local: LOCAL.gripBase }, b: { node: i }, k: o.kCable, L0: M.len(M.sub(wp(LOCAL.gripBase), p)), name: 'cable to ' + r.id, group: 'cable' });
        if (o.cableW) els.push({ type: 'force', pt: { node: i }, F: [0, 0, -o.cableW], name: 'cable weight on ' + r.id, group: 'cable' });
      } else {
        els.push({ type: 'ring', node: i, local: gm.local, axis: gm.axis, k: o.kLat, name: 'ring ' + r.id, group: 'rings' });
        if (r.contact === 'rubber') els.push({ type: 'slip', node: i, local: gm.local, axis: gm.axis, k: 20, Fmax: o.fmax, name: 'rubber grip ' + r.id, group: 'friction' });
        if (r.contact === 'seat') els.push({ type: 'stop', node: i, local: gm.local, axis: gm.axis, side: +1, k: o.kSeat, name: 'seat ' + r.id, group: 'seats' });
      }
    });
    // preload the wires to carry a fraction of the weight: least-squares split over the wire attachment points
    (function () {
      const target = o.carry * g.W;
      if (!wireEls.length) return;
      // unknown T_i >= 0: sum T_i = target; moment about the dot in x/y matches target acting at the COM.
      const dotW = wp(LOCAL.dot), comW = wp(o.com);
      const rows = [];   // Fz, Mx, My
      const cols = rings.map(r => { const rr = M.sub(r._p, dotW); return [1, rr[1] * 1, -rr[0] * 1]; });   // moment of upward force at rr about the dot: (rr x Fz)=(ry*F, -rx*F)
      const b = [target, (comW[1] - dotW[1]) * target, -(comW[0] - dotW[0]) * target];
      // normal equations with a little regularisation toward an equal split
      const m = cols.length, A = new Array(m * m).fill(0), rhs = new Array(m).fill(0);
      const wt = [1, 1 / 150, 1 / 150];
      for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) for (let k = 0; k < 3; k++) A[i * m + j] += cols[i][k] * cols[j][k] * wt[k] * wt[k]; for (let k = 0; k < 3; k++) rhs[i] += cols[i][k] * b[k] * wt[k] * wt[k]; A[i * m + i] += 1e-4; rhs[i] += 1e-4 * target / m; }
      let T = FS.math.solveLinear(A, rhs, m); T = T ? Array.from(T) : new Array(m).fill(target / m);
      T = T.map(v => Math.max(0, v));
      if (o.wireT) T = wireEls.map((w, i) => (o.wireT[i] == null ? T[i] : o.wireT[i]));
      wireEls.forEach((w, i) => { w.preload = T[i]; w.L0 = o.wireL - T[i] / w.k; w.T0 = T[i]; });
    })();

    // nose seat: a spherical collar on the shell resting in a cone ring near the nozzle (branch freedom-01b)
    let noseEl = null;
    if (o.nose) {
      const n = o.nose, local = n.local || [0, 0, n.s], c = wp(local), phi = (n.phi || 45) * Math.PI / 180, rc = n.rc || 12, h0 = rc / Math.sin(phi);
      const apex = [c[0] + (n.cmd ? n.cmd[0] : 0), c[1] + (n.cmd ? n.cmd[1] : 0), c[2] - h0 + (n.cmd ? n.cmd[2] : 0)];
      noseEl = { type: 'cone', local: local, a: apex, sinPhi: Math.sin(phi), cosPhi: Math.cos(phi), rc: rc, k: n.k || 100, name: 'nose seat', group: 'seat', h0: h0 };
      els.push(noseEl);
      if (n.preload) els.push({ type: 'force', pt: { local: local }, F: [0, 0, -n.preload], name: 'seat preload', group: 'preload' });
    }
    // tail bridle (branch 01b): two vertical wires to lugs either side of the grip base (pitch and roll) and a horizontal
    // bungee pair perpendicular to the barrel's horizontal projection (yaw). Together with the nose seat this is six constraints.
    let tailEls = null;
    if (o.tail) {
      const t = o.tail, dx = t.dx || 22, gb = LOCAL.gripBase, bh = M.norm([M.mv(pose.R, [0, 0, 1])[0], M.mv(pose.R, [0, 0, 1])[1], 0]), yawAxis = [-bh[1], bh[0], 0];
      tailEls = { wires: [], bungees: [] };
      [+1, -1].forEach(function (sg) {
        const loc = [sg * dx, gb[1], gb[2]], p = wp(loc), top = [p[0], p[1], p[2] + t.wireL];
        const w = { type: 'spring', a: { local: loc }, b: { world: top }, k: o.kWire, L0: t.wireL - (t.wireCmd ? t.wireCmd[sg > 0 ? 0 : 1] : 0), slack: true, name: 'tail wire ' + (sg > 0 ? 'A' : 'B'), group: 'tail wires' };
        els.push(w); tailEls.wires.push(w);
      });
      const pc = wp(gb);
      [+1, -1].forEach(function (sg) {
        const a = M.add(pc, M.mul(yawAxis, sg * 260 + (t.yawCmd || 0)));
        const b = { type: 'spring', a: { local: gb }, b: { world: a }, k: t.kb, L0: 260 - t.pre / t.kb, slack: true, name: 'tail bungee ' + (sg > 0 ? '+' : '-'), group: 'tail bungees' };
        els.push(b); tailEls.bungees.push(b);
      });
    }
    els.push({ type: 'gravity', name: 'gravity', group: 'gravity' });
    // umbilical pull at the grip base: along the exit direction blended with straight down (droop)
    const exitDir = M.mv(pose.R, FS.ROLL_AXIS);
    const pullDir = M.norm(M.add(M.mul(exitDir, 1 - o.umbilical.droop), [0, 0, -o.umbilical.droop]));
    els.push({ type: 'force', pt: { local: LOCAL.gripBase }, F: M.mul(pullDir, o.umbilical.F), name: 'umbilical pull', group: 'umbilical', dirWorld: pullDir });
    // freedom W3: extra raw elements (for example constant forces and couples at any body point), appended as they are
    if (o.extra) o.extra.forEach(function (e) { els.push(e); });
    // trigger press: N, straight into the grip face (local +Z direction... push along -grip normal); ILLUSTRATIVE simple push along local +Y
    if (o.trigger) els.push({ type: 'force', pt: { local: [0, -25 - 22 * 0.5, 172 + 22 * 0.87] }, F: M.mv(pose.R, [0, o.trigger, 0]), name: 'trigger press', group: 'trigger' });
    // arm
    let armEl = null, armRot = null, armAnchor = null;
    if (o.arm && o.arm.mode !== 'none') {
      const at = typeof o.arm.at === 'string' ? LOCAL[o.arm.at] : o.arm.at;
      const p = wp(at);
      armAnchor = [p[0] + o.arm.cmd[0], p[1] + o.arm.cmd[1], p[2] + o.arm.cmd[2]];
      armEl = { type: 'pin', a: { local: at }, b: { world: armAnchor }, k: o.arm.k, name: 'arm', group: 'arm' };
      els.push(armEl);
      if (o.arm.mode === 'rigid') { armRot = { type: 'rot', k: o.arm.kRot, name: 'arm grip (rotation)', group: 'arm' }; els.push(armRot); }
    }
    const model = FS.makeModel({ body: body, nodes: nodes, elements: els });
    model.noseEl = noseEl; model.tailEls = tailEls; model.opts = o; model.rings = rings; model.pose0 = pose; model.armEl = armEl; model.armAnchor = armAnchor; model.wireEls = wireEls;
    model.LOCAL = LOCAL; model.g = g;
    return model;
  }

  // What a software loop could do with a load cell in the arm end: adjust the wire tensions (winches on the wires)
  // until the arm carries as little force as it can. Gauss-Newton on the solved arm force; wire tensions stay >= 0.
  function armForce(opts, T) {
    const m = build(Object.assign({}, opts, { wireT: T }));
    const r = m.solve(new Float64Array(m.n));
    const f = m.armEl ? m.springForce(r.x, m.armEl).F : [0, 0, 0];
    return { f: f, converged: r.converged, x: r.x, model: m };
  }
  function nullWires(opts, iters) {
    const base = build(opts);
    let T = base.wireEls.map(w => w.T0);
    if (!base.armEl || !T.length) return { T: T, f: [0, 0, 0], iters: 0 };
    let cur = armForce(opts, T);
    for (let it = 0; it < (iters || 5); it++) {
      const J = T.map((t, i) => { const T2 = T.slice(); T2[i] = t + 0.4; const f2 = armForce(opts, T2).f; return M.mul(M.sub(f2, cur.f), 1 / 0.4); });
      // solve (J^T J + lam I) dT = -J^T f
      const m = T.length, A = new Array(m * m).fill(0), b = new Array(m).fill(0);
      for (let i = 0; i < m; i++) { for (let j = 0; j < m; j++) A[i * m + j] = M.dot(J[i], J[j]) + (i === j ? 1e-3 : 0); b[i] = -M.dot(J[i], cur.f); }
      const d = FS.math.solveLinear(A, b, m); if (!d) break;
      const Tn = T.map((t, i) => Math.max(0, t + d[i]));
      const nxt = armForce(opts, Tn);
      if (M.len(nxt.f) < M.len(cur.f)) { T = Tn; cur = nxt; } else break;
    }
    return { T: T, f: cur.f, iters: iters };
  }

  // Counterweight that moves the centre of mass onto the line between the tip ring point and the base ring point
  // (the "hinge" the two rings define). f = 0..1 of the full balancing amount. ILLUSTRATIVE: weight placed 60 mm
  // from the line on the side opposite the centre of mass.
  function hingeBalance(opts, f) {
    const o = merge(clone(DEFAULTS), opts || {});
    const tipR = (o.rings.find(r => r.at === 'tip') || { s: 40 });
    const A = [0, 0, tipR.s == null ? 40 : tipR.s], B = LOCAL.cablePair, d = M.norm(M.sub(B, A));
    const rel = M.sub(o.com, A), along = M.dot(rel, d), perp = M.sub(rel, M.mul(d, along)), e = M.len(perp), dc = 90;
    const mFull = e < 1e-6 ? 0 : o.mass * e / dc, mc = f * mFull;
    if (mc <= 1e-9) return { mass: o.mass, com: o.com.slice(), cwMass: 0, cwPos: null, offset: e, line: [A, B] };
    const pos = M.sub(M.add(A, M.mul(d, along)), M.mul(M.norm(perp), dc));
    const mass = o.mass + mc, com = M.mul(M.add(M.mul(o.com, o.mass), M.mul(pos, mc)), 1 / mass);
    return { mass: mass, com: com, cwMass: mc, cwPos: pos, offset: M.len(M.sub(com, M.add(A, M.mul(d, M.dot(M.sub(com, A), d))))), line: [A, B] };
  }

  // dot offset relative to the reference position, split into the seam's radial / tangent / vertical (station at +X)
  function dotOffset(model, x) { return { radial: x[0], tangent: x[1], vertical: x[2] }; }   // world x,y,z = radial, tangent, vertical at the +X station

  return { build: build, hingeBalance: hingeBalance, nullWires: nullWires, armForce: armForce, LOCAL: LOCAL, DEFAULTS: DEFAULTS, dotOffset: dotOffset, clone: clone, merge: merge };
});
