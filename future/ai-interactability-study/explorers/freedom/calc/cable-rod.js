/* cable-rod.js - freedom W3: a planar elastic rod (the fibre umbilical or the wire conduit) between two clamps, with weight.
 *
 * What it models: an inextensible rod of length L, bending stiffness EI, weight per length w, in ONE plane, held at its start by a clamp
 * (position and direction) and at its end by a clamp (position and direction) or a pin (position only). It finds the shape that minimises
 * bending energy plus gravity and reports the force and moment the clamps exert. Discretised as N straight segments whose tangent angles
 * are the unknowns; the two end-position constraints are handled by Newton on the KKT system (tridiagonal + two multipliers), with
 * damping and a backtracking line search.
 *
 * What it does NOT model: twist (see freedom-18), the out-of-plane part of gravity, friction against a hook or a table, hysteresis or
 * creep of the sheath, a change of EI with bend, contact with the tube, the bench or the gun. EI and w of the real fibre are [unknown];
 * every number that goes in is a slider, not a measurement.
 *
 * Units: geometry in mm, EI in N*m^2, w in N/m, forces in N, moments in N*m (converted inside). Angles in radians, measured from +x toward +y.
 * The plane's "down" is g = [gx, gy] (unit), default [0,-1].
 * UMD: window.CableRod or module.exports.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CableRod = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ---- Hermite-spline initial guess with total length L
  function hermiteGuess(p0, th0, p1, th1, L, N) {
    const chord = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
    const t0 = [Math.cos(th0), Math.sin(th0)], t1 = [Math.cos(th1), Math.sin(th1)];
    function curve(m) {
      const pts = [];
      for (let k = 0; k <= 400; k++) {
        const s = k / 400, h00 = 2 * s ** 3 - 3 * s * s + 1, h10 = s ** 3 - 2 * s * s + s, h01 = -2 * s ** 3 + 3 * s * s, h11 = s ** 3 - s * s;
        pts.push([h00 * p0[0] + h10 * m * t0[0] + h01 * p1[0] + h11 * m * t1[0], h00 * p0[1] + h10 * m * t0[1] + h01 * p1[1] + h11 * m * t1[1]]);
      }
      return pts;
    }
    const lenOf = pts => { let l = 0; for (let i = 1; i < pts.length; i++) l += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return l; };
    let lo = 0.05 * chord, hi = 6 * chord + L, pts = curve(lo);
    if (lenOf(curve(hi)) < L) return null;
    for (let i = 0; i < 60; i++) { const mid = 0.5 * (lo + hi); if (lenOf(curve(mid)) < L) lo = mid; else hi = mid; }
    pts = curve(0.5 * (lo + hi));
    // resample to N equal-arclength segments
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    const tot = cum[cum.length - 1], out = [];
    let j = 0;
    for (let i = 0; i <= N; i++) {
      const s = tot * i / N; while (j < cum.length - 2 && cum[j + 1] < s) j++;
      const f = (s - cum[j]) / Math.max(1e-12, cum[j + 1] - cum[j]);
      out.push([pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])]);
    }
    const th = []; for (let i = 0; i < N; i++) th.push(Math.atan2(out[i + 1][1] - out[i][1], out[i + 1][0] - out[i][0]));
    th[0] = th0; return th;
  }

  // a straight chord plus a sine bump of amplitude a (mm, sign = side), scaled so the arclength is L; returns node tangents th[0..N]
  function bumpGuess(p0, p1, L, N, side) {
    const dx = p1[0] - p0[0], dy = p1[1] - p0[1], c = Math.hypot(dx, dy), nx = -dy / c, ny = dx / c;
    const len = a => { let l = 0, px = p0[0], py = p0[1]; for (let k = 1; k <= 400; k++) { const s = k / 400, x = p0[0] + s * dx + side * a * Math.sin(Math.PI * s) * nx, y = p0[1] + s * dy + side * a * Math.sin(Math.PI * s) * ny; l += Math.hypot(x - px, y - py); px = x; py = y; } return l; };
    let lo = 0, hi = L; if (len(hi) < L) return null;
    for (let i = 0; i < 60; i++) { const mid = 0.5 * (lo + hi); if (len(mid) < L) lo = mid; else hi = mid; }
    const a = 0.5 * (lo + hi), pts = []; for (let k = 0; k <= 4 * N; k++) { const s = k / (4 * N); pts.push([p0[0] + s * dx + side * a * Math.sin(Math.PI * s) * nx, p0[1] + s * dy + side * a * Math.sin(Math.PI * s) * ny]); }
    const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    const tot = cum[cum.length - 1], out = []; let j = 0;
    for (let i = 0; i <= N; i++) { const s = tot * i / N; while (j < cum.length - 2 && cum[j + 1] < s) j++; const f = (s - cum[j]) / Math.max(1e-12, cum[j + 1] - cum[j]); out.push([pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])]); }
    const th = []; for (let i = 0; i < N; i++) th.push(Math.atan2(out[i + 1][1] - out[i][1], out[i + 1][0] - out[i][0])); th.push(th[N - 1]); return th;
  }

  // tridiagonal solve for several right-hand sides. a: sub, b: diag, c: super (length n), rhs: array of arrays
  function thomas(a, b, c, rhs) {
    const n = b.length, cp = new Float64Array(n), out = rhs.map(r => new Float64Array(r));
    let denom = b[0]; if (Math.abs(denom) < 1e-300) return null;
    cp[0] = c[0] / denom; out.forEach(d => { d[0] /= denom; });
    for (let i = 1; i < n; i++) {
      denom = b[i] - a[i] * cp[i - 1]; if (Math.abs(denom) < 1e-300) return null;
      cp[i] = c[i] / denom; out.forEach(d => { d[i] = (d[i] - a[i] * d[i - 1]) / denom; });
    }
    for (let i = n - 2; i >= 0; i--) out.forEach(d => { d[i] -= cp[i] * d[i + 1]; });
    return out;
  }

  /* solveFrom(o, thInit): Newton on the KKT system for the rod between a clamp at the start and an end condition.
   * o = { p0:[x,y], th0, L, EI (N*m^2), w (N/m), g:[gx,gy] (down), N,
   *       end: { type:'clamp', p:[x,y], th } | { type:'pin', p:[x,y] } | { type:'rail', p:[x,y] (on the rail), n:[nx,ny] (unit normal of the rail), F:[fx,fy] (constant force on the end, N) } }
   * Unknowns: tangent angle th[i] at the N+1 nodes (th[0] clamped; th[N] clamped for 'clamp', free otherwise). Second-order scheme: bending
   * EI/(2 ds) (th[i+1]-th[i])^2 per interval; chord and weight by the trapezoid rule. */
  function solveFrom(o, initTh) {
    const N = o.N || 100, L = o.L, ds = L / N, EI = o.EI * 1e6, wl = (o.w || 0) / 1000, g = o.g || [0, -1], p0 = o.p0, th0 = o.th0, E = o.end;
    const clamped = E.type === 'clamp', last = clamped ? N - 1 : N;
    // constraints: list of { n:[nx,ny], b } with n . P_end = b
    const cl = E.type === 'rail' ? [{ n: E.n, b: E.n[0] * E.p[0] + E.n[1] * E.p[1] }] : [{ n: [1, 0], b: E.p[0] }, { n: [0, 1], b: E.p[1] }];
    const nc = cl.length, Fx = E.type === 'rail' ? E.F : [0, 0];
    const cw = i => (i === 0 || i === N ? 0.5 : 1), gw = i => (i === 0 ? N / 2 : (i === N ? 0 : N - i));
    let th = initTh.slice(); th[0] = th0; if (clamped) th[N] = E.th;
    const pend = t => { let x = 0, y = 0; for (let i = 0; i <= N; i++) { x += cw(i) * ds * Math.cos(t[i]); y += cw(i) * ds * Math.sin(t[i]); } return [p0[0] + x, p0[1] + y]; };
    const cons = t => { const p = pend(t); return cl.map(c => c.n[0] * p[0] + c.n[1] * p[1] - c.b); };
    function gradU(t) {
      const g0 = new Float64Array(N + 1);
      for (let i = 0; i < N; i++) { const d = t[i + 1] - t[i]; g0[i + 1] += EI / ds * d; g0[i] -= EI / ds * d; }
      if (wl) for (let i = 0; i <= N; i++) g0[i] -= wl * ds * ds * gw(i) * (-g[0] * Math.sin(t[i]) + g[1] * Math.cos(t[i]));
      for (let i = 0; i <= N; i++) g0[i] -= cw(i) * ds * (Fx[0] * (-Math.sin(t[i])) + Fx[1] * Math.cos(t[i]));      // potential of the constant end force: -F . P_end
      return g0;
    }
    const aOf = (t, k) => [cw(k) * ds * (-Math.sin(t[k])), cw(k) * ds * Math.cos(t[k])];
    let lam = new Array(nc).fill(0), iters = 0, ok = false, mu = 1e-6;
    const gradL = (t, l, k, gu) => { const a = aOf(t, k); let r = gu[k]; for (let j = 0; j < nc; j++) r += l[j] * (cl[j].n[0] * a[0] + cl[j].n[1] * a[1]); return r; };
    const resid = (t, l) => { const gu = gradU(t), c = cons(t); let sq = 0; for (let k = 1; k <= last; k++) { const r = gradL(t, l, k, gu); sq += r * r; } let cn = 0; for (let j = 0; j < nc; j++) cn += c[j] * c[j]; return Math.sqrt(sq) / (EI / ds) + Math.sqrt(cn) / ds; };
    for (; iters < 200; iters++) {
      const gu = gradU(th), c = cons(th), n = last;
      const a = new Float64Array(n), b = new Float64Array(n), cc = new Float64Array(n), rg = new Float64Array(n), Aj = [];
      for (let j = 0; j < nc; j++) Aj.push(new Float64Array(n));
      for (let k = 1; k <= n; k++) {
        const i = k - 1, ak = aOf(th, k), w = cw(k) * ds;
        let diag = (k === N ? 1 : 2) * EI / ds;
        if (wl) diag -= wl * ds * ds * gw(k) * (-g[0] * Math.cos(th[k]) - g[1] * Math.sin(th[k]));
        let q0 = -Fx[0], q1 = -Fx[1]; for (let j = 0; j < nc; j++) { q0 += lam[j] * cl[j].n[0]; q1 += lam[j] * cl[j].n[1]; }
        diag += w * (q0 * (-Math.cos(th[k])) + q1 * (-Math.sin(th[k])));
        b[i] = diag + mu * EI / ds; a[i] = i > 0 ? -EI / ds : 0; cc[i] = i < n - 1 ? -EI / ds : 0;
        rg[i] = gradL(th, lam, k, gu);
        for (let j = 0; j < nc; j++) Aj[j][i] = cl[j].n[0] * ak[0] + cl[j].n[1] * ak[1];
      }
      const sol = thomas(a, b, cc, [rg].concat(Aj));
      if (!sol) { mu = Math.max(mu * 10, 1e-3); continue; }
      const Hg = sol[0], Ha = sol.slice(1);
      const S = [], v = [];
      for (let p = 0; p < nc; p++) { S.push(new Array(nc).fill(0)); v.push(0); for (let i = 0; i < n; i++) v[p] += Aj[p][i] * Hg[i]; for (let q = 0; q < nc; q++) for (let i = 0; i < n; i++) S[p][q] += Aj[p][i] * Ha[q][i]; }
      const rhs = c.map((cv, p) => cv - v[p]);
      let dl;
      if (nc === 1) { if (Math.abs(S[0][0]) < 1e-30) { mu = Math.max(mu * 10, 1e-3); continue; } dl = [rhs[0] / S[0][0]]; }
      else { const det = S[0][0] * S[1][1] - S[0][1] * S[1][0]; if (Math.abs(det) < 1e-30) { mu = Math.max(mu * 10, 1e-3); continue; } dl = [(S[1][1] * rhs[0] - S[0][1] * rhs[1]) / det, (-S[1][0] * rhs[0] + S[0][0] * rhs[1]) / det]; }
      const dth = new Float64Array(N + 1);
      for (let i = 0; i < n; i++) { let x = Hg[i]; for (let j = 0; j < nc; j++) x += Ha[j][i] * dl[j]; dth[i + 1] = -x; }
      const r0 = resid(th, lam);
      let stepMax = 0; for (let k = 1; k <= n; k++) stepMax = Math.max(stepMax, Math.abs(dth[k]));
      let alpha = stepMax > 0.5 ? 0.5 / stepMax : 1, accepted = false;
      for (let ls = 0; ls < 30; ls++) {
        const tn = th.slice(); for (let k = 1; k <= n; k++) tn[k] += alpha * dth[k];
        const ln = lam.map((x, j) => x + alpha * dl[j]);
        if (resid(tn, ln) < r0 * (1 - 1e-4 * alpha) || r0 < 1e-12) { th = tn; lam = ln; accepted = true; break; }
        alpha *= 0.5;
      }
      if (!accepted) { mu = Math.max(mu * 10, 1e-4); if (mu > 1e3) break; continue; }
      mu = Math.max(mu * 0.3, 1e-9);
      if (resid(th, lam) < 1e-9) { ok = true; break; }
    }
    if (!ok && resid(th, lam) < 1e-6) ok = true;
    const pts = [[p0[0], p0[1]]]; for (let i = 0; i < N; i++) pts.push([pts[i][0] + 0.5 * ds * (Math.cos(th[i]) + Math.cos(th[i + 1])), pts[i][1] + 0.5 * ds * (Math.sin(th[i]) + Math.sin(th[i + 1]))]);
    const kap = []; for (let i = 0; i < N; i++) kap.push((th[i + 1] - th[i]) / ds);
    let maxK = 0; kap.forEach(k => { maxK = Math.max(maxK, Math.abs(k)); });
    // force of the constraints on the rod's end: -sum lam_j n_j ; plus the external end force; plus the weight
    const fCon = [0, 0]; for (let j = 0; j < nc; j++) { fCon[0] -= lam[j] * cl[j].n[0]; fCon[1] -= lam[j] * cl[j].n[1]; }
    const fEnd = [fCon[0] + Fx[0], fCon[1] + Fx[1]], Wv = [wl * L * g[0], wl * L * g[1]];
    const fStart = [-fEnd[0] - Wv[0], -fEnd[1] - Wv[1]];
    const gu = gradU(th);
    const mStart = gradL(th, lam, 0, gu);
    const mEnd = clamped ? gradL(th, lam, N, gu) : 0;
    let energy = 0; for (let i = 0; i < N; i++) { const d = th[i + 1] - th[i]; energy += EI / (2 * ds) * d * d; } if (wl) for (let i = 0; i <= N; i++) energy -= wl * ds * ds * gw(i) * (g[0] * Math.cos(th[i]) + g[1] * Math.sin(th[i]));
    return { ok: ok, energy: energy, iters: iters, th: th, pts: pts, kappa: kap, maxKappa: maxK, minR: maxK > 1e-12 ? 1 / maxK : Infinity,
      startForceOnRod: fStart, startMomentOnRod: mStart / 1000, endForceOnRod: fEnd, endMomentOnRod: mEnd / 1000, lambda: lam,
      forceOnStartClamp: [-fStart[0], -fStart[1]], momentOnStartClamp: -mStart / 1000, length: L, N: N, endPos: pts[N] };
  }
  function solve(o) {
    const N = o.N || 100, E = o.end, p1 = E.p;
    const dx = p1[0] - o.p0[0], dy = p1[1] - o.p0[1], chord = Math.hypot(dx, dy);
    if (E.type !== 'rail' && o.L < chord * 1.0005) return { ok: false, reason: 'the rod is too short to reach' };
    const g = o.g || [0, -1], nx = -dy / (chord || 1), ny = dx / (chord || 1), sideDown = (nx * g[0] + ny * g[1]) >= 0 ? 1 : -1;
    const guesses = [];
    if (o.init && o.init.length === N + 1) guesses.push(o.init);
    if (E.type === 'rail') { guesses.push(new Array(N + 1).fill(o.th0)); }
    else {
      const t1 = E.type === 'clamp' ? E.th : Math.atan2(dy, dx), hg = hermiteGuess(o.p0, o.th0, p1, t1, o.L, N);
      if (hg) guesses.push(hg.concat([hg[N - 1]]));
      [sideDown, -sideDown].forEach(sd => { const b = bumpGuess(o.p0, p1, o.L, N, sd); if (b) guesses.push(b); });
    }
    let best = null;
    for (let k = 0; k < guesses.length; k++) {
      const r = solveFrom(o, guesses[k]);
      if (r.ok && (!best || r.energy < best.energy - 1e-9)) best = r;
      if (best && k === 0 && o.init) break;
      if (best && k >= 1 && !o.exhaustive) break;
    }
    return best || { ok: false, reason: 'no equilibrium found (try a different slack or end direction)' };
  }

  // ---------------------------------------------------------------------------------------------------------------------------
  // Force-controlled far end: a rope (a dead weight over a pulley, or a constant-force balancer) pulls the end of the rod toward a
  // fixed pulley P with constant tension W; the end is a pin (position free, direction free). The potential of the rope is W*|P - end|.
  // opts: { p0, th0 (clamped start), P:[x,y], W (N), L, EI, w, g, N }. Dense Newton on th[1..N] with a backtracking line search.
  function solveRope(o) {
    const N = o.N || 60, L = o.L, ds = L / N, EI = o.EI * 1e6, wl = (o.w || 0) / 1000, Wt = o.W, g = o.g || [0, -1], p0 = o.p0, P = o.P;
    const cw = i => (i === 0 || i === N ? 0.5 : 1), gw = i => (i === 0 ? N / 2 : (i === N ? 0 : N - i));
    let th = o.init && o.init.length === N + 1 ? o.init.slice() : new Array(N + 1).fill(o.th0);
    th[0] = o.th0;
    const endPos = t => { let x = p0[0], y = p0[1]; for (let i = 0; i < N; i++) { x += 0.5 * ds * (Math.cos(t[i]) + Math.cos(t[i + 1])); y += 0.5 * ds * (Math.sin(t[i]) + Math.sin(t[i + 1])); } return [x, y]; };
    const energy = t => { let e = 0; for (let i = 0; i < N; i++) { const d = t[i + 1] - t[i]; e += EI / (2 * ds) * d * d; } if (wl) for (let i = 0; i <= N; i++) e -= wl * ds * ds * gw(i) * (g[0] * Math.cos(t[i]) + g[1] * Math.sin(t[i])); const pe = endPos(t); e += Wt * Math.hypot(P[0] - pe[0], P[1] - pe[1]); return e; };
    let iters = 0, ok = false, mu = 1e-6;
    for (; iters < 120; iters++) {
      const pe = endPos(th), rx = P[0] - pe[0], ry = P[1] - pe[1], rho = Math.max(1e-9, Math.hypot(rx, ry)), ux = -rx / rho, uy = -ry / rho;   // u = (Pend - P)/rho
      const n = N, gr = new Float64Array(n), H = new Float64Array(n * n), a = [];
      for (let k = 1; k <= n; k++) a.push([cw(k) * ds * (-Math.sin(th[k])), cw(k) * ds * Math.cos(th[k])]);
      for (let k = 1; k <= n; k++) {
        const i = k - 1; let gk = 0;
        gk += EI / ds * (th[k] - th[k - 1]); if (k < N) gk -= EI / ds * (th[k + 1] - th[k]);
        if (wl) gk -= wl * ds * ds * gw(k) * (-g[0] * Math.sin(th[k]) + g[1] * Math.cos(th[k]));
        gk += Wt * (ux * a[i][0] + uy * a[i][1]);
        gr[i] = gk;
        H[i * n + i] += (k < N ? 2 : 1) * EI / ds;
        if (k < N) { H[i * n + i + 1] -= EI / ds; H[(i + 1) * n + i] -= EI / ds; }
        if (wl) H[i * n + i] -= wl * ds * ds * gw(k) * (-g[0] * Math.cos(th[k]) - g[1] * Math.sin(th[k]));
        H[i * n + i] += Wt * cw(k) * ds * (ux * (-Math.cos(th[k])) + uy * (-Math.sin(th[k])));
      }
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) H[i * n + j] += Wt / rho * ((a[i][0] * a[j][0] + a[i][1] * a[j][1]) - (a[i][0] * ux + a[i][1] * uy) * (a[j][0] * ux + a[j][1] * uy));
      let gn = 0; for (let i = 0; i < n; i++) gn = Math.max(gn, Math.abs(gr[i]));
      if (gn < 1e-7 * EI / ds) { ok = true; break; }
      let dth = null;
      for (let tries = 0; tries < 12 && !dth; tries++) {
        const A = new Float64Array(H); for (let i = 0; i < n; i++) A[i * n + i] += mu * EI / ds + 1e-12;
        const x = solveDense(A, gr.map(v => -v), n); if (x) { let descent = 0; for (let i = 0; i < n; i++) descent += x[i] * gr[i]; if (descent < 0) dth = x; }
        if (!dth) mu = Math.max(mu * 10, 1e-3);
      }
      if (!dth) break;
      let st = 0; for (let i = 0; i < n; i++) st = Math.max(st, Math.abs(dth[i]));
      let alpha = st > 0.6 ? 0.6 / st : 1, e0 = energy(th), acc = false;
      for (let ls = 0; ls < 30; ls++) { const tn = th.slice(); for (let k = 1; k <= n; k++) tn[k] += alpha * dth[k - 1]; if (energy(tn) < e0 - 1e-12 * Math.abs(e0) - 1e-14) { th = tn; acc = true; break; } alpha *= 0.5; }
      if (!acc) { mu = Math.max(mu * 10, 1e-4); if (mu > 1e3) break; } else mu = Math.max(mu * 0.3, 1e-9);
    }
    const pe = endPos(th), rx = P[0] - pe[0], ry = P[1] - pe[1], rho = Math.hypot(rx, ry) || 1e-9;
    const fEnd = [Wt * rx / rho, Wt * ry / rho], Wv = [wl * L * g[0], wl * L * g[1]], fStart = [-fEnd[0] - Wv[0], -fEnd[1] - Wv[1]];
    // moment of the start clamp on the rod = dE/dth0 (the rope term uses the end position's dependence on th0, weight 1/2)
    let m0 = -EI / ds * (th[1] - th[0]); if (wl) m0 -= wl * ds * ds * gw(0) * (-g[0] * Math.sin(th[0]) + g[1] * Math.cos(th[0]));
    m0 += Wt * (((pe[0] - P[0]) / rho) * (0.5 * ds * (-Math.sin(th[0]))) + ((pe[1] - P[1]) / rho) * (0.5 * ds * Math.cos(th[0])));
    const pts = [[p0[0], p0[1]]]; for (let i = 0; i < N; i++) pts.push([pts[i][0] + 0.5 * ds * (Math.cos(th[i]) + Math.cos(th[i + 1])), pts[i][1] + 0.5 * ds * (Math.sin(th[i]) + Math.sin(th[i + 1]))]);
    const kap = []; for (let i = 0; i < N; i++) kap.push((th[i + 1] - th[i]) / ds); let maxK = 0; kap.forEach(k => { maxK = Math.max(maxK, Math.abs(k)); });
    return { ok: ok, iters: iters, th: th, pts: pts, kappa: kap, maxKappa: maxK, minR: maxK > 1e-12 ? 1 / maxK : Infinity, end: pe, endForceOnRod: fEnd, startForceOnRod: fStart,
      forceOnStartClamp: [-fStart[0], -fStart[1]], momentOnStartClamp: -m0 / 1000, length: L, N: N };
  }
  function solveDense(A, b, n) {
    const M = new Float64Array(n * (n + 1));
    for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) M[i * (n + 1) + j] = A[i * n + j]; M[i * (n + 1) + n] = b[i]; }
    for (let c = 0; c < n; c++) {
      let p = c, best = Math.abs(M[c * (n + 1) + c]);
      for (let r = c + 1; r < n; r++) { const v = Math.abs(M[r * (n + 1) + c]); if (v > best) { best = v; p = r; } }
      if (best < 1e-300) return null;
      if (p !== c) for (let j = c; j <= n; j++) { const t = M[c * (n + 1) + j]; M[c * (n + 1) + j] = M[p * (n + 1) + j]; M[p * (n + 1) + j] = t; }
      for (let r = c + 1; r < n; r++) { const f = M[r * (n + 1) + c] / M[c * (n + 1) + c]; if (f !== 0) for (let j = c; j <= n; j++) M[r * (n + 1) + j] -= f * M[c * (n + 1) + j]; }
    }
    const x = new Float64Array(n);
    for (let i = n - 1; i >= 0; i--) { let s = M[i * (n + 1) + n]; for (let j = i + 1; j < n; j++) s -= M[i * (n + 1) + j] * x[j]; x[i] = s / M[i * (n + 1) + i]; }
    return x;
  }
  return { solve: solve, solveRope: solveRope, hermiteGuess: hermiteGuess, bumpGuess: bumpGuess };
});
