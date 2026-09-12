"""Discrete elastic rod relaxation of a routed tube between the things that really hold it.

The authored run is a centreline sampled every `ds` along its arcs. The tube is that many nodes
joined by inextensible edges, with a bending energy at every interior joint, gravity on every node,
the nodes inside a fitting's grip or an anchor's seat pinned where the author put them, and a
penalty that keeps every free node one tube radius clear of the environment's signed-distance
field. What the solver returns is a local minimum of that energy from a given seed; several seeds
give the alternate bows a tube can take, and none of them is a measured prediction.

    E = sum_j EI/(2 ds) |t_j - t_{j-1} - c_j|^2      bending, c_j the natural turn at joint j
      + sum_j K_s/2 (|e_j| - ds)^2                    stretch (stiff, so the cut length is kept)
      + sum_i w ds z_i                                gravity, +Z up
      + sum_i k_c/2 max(0, r_clear - sdf(x_i))^2      contact with the environment

t_j is the unit tangent of edge j (x_{j+1} - x_j). The gradient is analytic. Units: mm, N.
"""
import math
import numpy as np
from scipy.optimize import minimize

# --- materials --------------------------------------------------------------------------------


def tube_section(od, id_, E_MPa, density_g_cm3, fill_g_cm3=1.0):
    """EI (N mm^2), EA (N), weight per length empty and full (N/mm) of a round tube."""
    I = math.pi * (od ** 4 - id_ ** 4) / 64.0
    A = math.pi * (od ** 2 - id_ ** 2) / 4.0
    bore = math.pi * id_ ** 2 / 4.0
    g = 9.81e-3                         # N per gram
    w_empty = density_g_cm3 * 1e-3 * A * g
    w_full = w_empty + fill_g_cm3 * 1e-3 * bore * g
    return {"EI": E_MPa * I, "EA": E_MPa * A, "w_empty": w_empty, "w_full": w_full,
            "I": I, "A": A}


LLDPE_QUARTER = dict(od=6.35, id_=4.32, E_MPa=250.0, density_g_cm3=0.925)


# --- geometry helpers ---------------------------------------------------------------------------


def resample(points, ds, s=None):
    """`points` (polyline, N x 3) resampled every `ds` of arc length; returns (P, s).

    `s` is the arc length of each point when the caller knows it — the exporter's samples are
    taken ALONG THE ARCS and carry their developed length, which a chord walk understates on
    every bend. Without it the polyline's own chords are the parameter."""
    P = np.asarray(points, float)
    if s is None:
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])
    s = np.asarray(s, float)
    n = max(int(round(s[-1] / ds)), 1)
    ss = np.linspace(0.0, s[-1], n + 1)
    out = np.column_stack([np.interp(ss, s, P[:, k]) for k in range(3)])
    return out, ss


def tangents(P):
    e = np.diff(P, axis=0)
    L = np.linalg.norm(e, axis=1)
    return e, L, e / L[:, None]


def natural_turns(P0, set_fraction=0.0, coil=None):
    """The natural turn vector c_j at every interior joint, from the authored shape.

    `set_fraction` of the authored turn is kept (0: straight stock, 1: as drawn). `coil`, if
    given, is (radius_mm, normal, sign): the reel's curvature laid on the authored tangents —
    a turn of ds/R per joint about `normal`, in the world frame (an approximation that holds
    while the tube stays near its authored orientation)."""
    _e, L, t = tangents(P0)
    dt = t[1:] - t[:-1]
    c = set_fraction * dt
    if coil is not None:
        R, n, sign = coil
        n = np.asarray(n, float); n /= np.linalg.norm(n)
        ds = 0.5 * (L[1:] + L[:-1])
        c = c + sign * (ds / R)[:, None] * np.cross(n, t[:-1])
    return c


# --- energy and gradient ------------------------------------------------------------------------


_BAND = 8      # a node couples nodes within two of it: 2 * 3 coordinates + 2


def _solve_banded(H, damping, rhs):
    """(H + damping I) d = rhs, on the band the rod's coupling actually fills."""
    from scipy.linalg import solve_banded
    n = len(rhs)
    u = min(_BAND, n - 1)
    ab = np.zeros((2 * u + 1, n))
    for k in range(-u, u + 1):
        diag = np.diagonal(H, offset=k)
        if k >= 0:
            ab[u - k, k:k + len(diag)] = diag
        else:
            ab[u - k, :len(diag)] = diag
    ab[u] += damping
    return solve_banded((u, u), ab, rhs)


class RodProblem:
    def __init__(self, P0, fixed, EI, EA, w, radius, c=None, sdf=None, clearance=0.5,
                 k_contact=20.0, gravity=True, rest=None):
        self.P0 = np.asarray(P0, float)
        self.N = len(self.P0)
        self.fixed = np.asarray(fixed, bool)
        self.free = ~self.fixed
        _e, L, _t = tangents(self.P0)
        # rest length of every edge: the authored line's, unless the stock is longer or shorter
        # than the line it is being pushed into (`rest`)
        self.ds = L if rest is None else np.asarray(rest, float)
        self.EI, self.EA, self.w = EI, EA, w
        self.radius, self.clearance = radius, clearance
        self.r_clear = radius + clearance
        self.c = np.zeros((self.N - 2, 3)) if c is None else np.asarray(c, float)
        self.sdf = sdf
        self.k_c = k_contact
        self.gravity = gravity
        # A JOINT AT A CLAMP BENDS OVER HALF AN ELEMENT. The rest length a joint's curvature is
        # lumped over is half of each edge beside it, and an edge held rigid on both its nodes
        # contributes none — so the joint where a free edge meets a fixed one is EI/(ds/2) stiff,
        # which is what makes a clamped cantilever's tip land on w L^4 / 8 EI instead of 4 % over.
        edge_free = self.free[:-1] | self.free[1:]
        self.dsj = 0.5 * (self.ds[:-1] * edge_free[:-1] + self.ds[1:] * edge_free[1:])
        self.dsj = np.where(self.dsj > 0, self.dsj, 0.5 * (self.ds[:-1] + self.ds[1:]))

    # variables are the free nodes' positions, flattened
    def unpack(self, x):
        P = self.P0.copy()
        P[self.free] = x.reshape(-1, 3)
        return P

    def energy_grad(self, x):
        P = self.unpack(x)
        e = np.diff(P, axis=0)
        L = np.linalg.norm(e, axis=1)
        t = e / L[:, None]
        G = np.zeros_like(P)
        # bending: v_j = (t_j - t_{j-1}) - c_j for joints j = 1..N-2 (edge index j and j-1)
        v = (t[1:] - t[:-1]) - self.c
        k = self.EI / self.dsj
        E = 0.5 * np.sum(k[:, None] * v * v)
        dE_dt = np.zeros_like(t)
        dE_dt[1:] += k[:, None] * v            # edge j in joint j with +
        dE_dt[:-1] -= k[:, None] * v           # edge j-1 in joint j with -
        # t = e/|e|: dE/de = (I - t t^T) dE/dt / |e|
        dE_de = (dE_dt - np.sum(dE_dt * t, axis=1)[:, None] * t) / L[:, None]
        # stretch
        Ks = self.EA / self.ds
        stretch = L - self.ds
        E += 0.5 * np.sum(Ks * stretch * stretch)
        dE_de += (Ks * stretch)[:, None] * t
        G[1:] += dE_de
        G[:-1] -= dE_de
        # gravity
        if self.gravity:
            m = self.w * np.concatenate([[self.ds[0] / 2], 0.5 * (self.ds[1:] + self.ds[:-1]),
                                         [self.ds[-1] / 2]])
            E += np.sum(m * P[:, 2])
            G[:, 2] += m
        # contact
        if self.sdf is not None:
            d, n = self.sdf(P)
            pen = np.maximum(0.0, self.r_clear - d)
            E += 0.5 * self.k_c * np.sum(pen * pen)
            G -= (self.k_c * pen)[:, None] * n
        return E, G[self.free].ravel()

    def hessian(self, x, g0, h=1e-4):
        """The energy's Hessian on the free variables by finite differences of the analytic
        gradient. Each joint couples three consecutive nodes, so a node's column only reaches
        nodes within two of it: perturbing every fifth node at once (one coordinate at a time)
        reads a whole colour's columns from one gradient — 15 evaluations for the lot."""
        n = int(self.free.sum())
        idx = np.arange(n)
        H = np.zeros((3 * n, 3 * n))
        for colour in range(5):
            nodes = idx[idx % 5 == colour]
            for k in range(3):
                xp = x.copy()
                cols = 3 * nodes + k
                xp[cols] += h
                _E, g = self.energy_grad(xp)
                dg = (g - g0) / h
                for c, node in zip(cols, nodes):
                    lo, hi = max(node - 2, 0), min(node + 3, n)
                    H[3 * lo:3 * hi, c] = dg[3 * lo:3 * hi]
        return 0.5 * (H + H.T)

    def solve(self, seed=None, maxiter=300, gtol=1e-6, step_max=3.0, kick=0.05):
        """Damped Newton (Levenberg–Marquardt) on the free nodes: a step solves
        (H + lam I) d = -g and is kept when the energy falls. A STEP IS CAPPED at `step_max`
        mm per node so a seed settles into its own basin instead of leaping across the straight
        line into the bow gravity prefers — the alternate bows are the point of seeding.

        A SEED ON A SADDLE HAS NO GRADIENT TO FOLLOW (a straight tube pushed end-on is one), so a
        converged point is kicked by `kick` mm at random and re-solved; a point that was a
        minimum comes back to itself and a saddle falls off it."""
        x = (self.P0 if seed is None else np.asarray(seed, float))[self.free].ravel()
        if len(x) == 0:                                   # a stub held end to end has nothing to move
            E, _g = self.energy_grad(x)
            return self.P0.copy(), float(E), {"nit": 0, "gmax": 0.0, "lam": 0.0, "converged": True}
        P, E, info = self._newton(x, maxiter, gtol, step_max)
        if kick and len(x):
            rng = np.random.default_rng(0)
            xk = P[self.free].ravel() + rng.normal(0.0, kick, size=x.shape)
            Pk, Ek, infok = self._newton(xk, maxiter, gtol, step_max)
            if Ek < E - 1e-9 * max(abs(E), 1.0):
                P, E, info = Pk, Ek, dict(infok, kicked=True)
        return P, E, info

    def _newton(self, x, maxiter, gtol, step_max):
        E, g = self.energy_grad(x)
        lam, it = 1e-3, 0
        for it in range(1, maxiter + 1):
            if np.max(np.abs(g)) < gtol:
                break
            H = self.hessian(x, g)
            scale = max(float(np.max(np.abs(np.diag(H)))), 1e-12)
            while True:
                try:
                    d = _solve_banded(H, lam * scale, -g)
                except (np.linalg.LinAlgError, ValueError):
                    lam *= 10.0
                    if lam > 1e6:
                        break
                    continue
                if np.max(np.abs(d)) > step_max:
                    lam *= 10.0
                    if lam > 1e6:
                        break
                    continue
                E1, g1 = self.energy_grad(x + d)
                if np.isfinite(E1) and E1 <= E + 1e-12 * max(abs(E), 1.0):
                    x, E, g = x + d, E1, g1
                    lam = max(lam / 3.0, 1e-9)
                    break
                lam *= 10.0
                if lam > 1e6:
                    break
            if lam > 1e6:
                break
        P = self.unpack(x)
        gmax = float(np.max(np.abs(g)))
        return P, float(E), {"nit": it, "gmax": gmax, "lam": lam, "converged": bool(gmax < gtol)}


# --- seeds, spans and metrics -------------------------------------------------------------------


def spans(fixed):
    """(a, b) index pairs of every maximal run of free nodes, with the pinned nodes either side."""
    out, i, N = [], 0, len(fixed)
    while i < N:
        if not fixed[i]:
            j = i
            while j < N and not fixed[j]:
                j += 1
            out.append((max(i - 1, 0), min(j, N - 1)))
            i = j
        else:
            i += 1
    return out


def bump_seeds(P0, fixed, rest=None, amplitude_frac=0.15, nudge_frac=0.04):
    """The authored shape with each free span bowed along +-x, +-y, +-z — the seeds that find a
    tube's alternate bows.

    A SEED KEEPS THE STOCK'S LENGTH. A bump laid on a span that has slack (its rest length is
    longer than the line it is drawn on) takes the largest amplitude the slack allows, up to
    `amplitude_frac` of the span; a span with no slack gets a small nudge, whose stretch the
    solver relieves by straightening the corners on the side the nudge points to."""
    P0 = np.asarray(P0, float)
    seg = np.linalg.norm(np.diff(P0, axis=0), axis=1)
    rest = seg if rest is None else np.asarray(rest, float)
    seeds = {"authored": P0.copy()}
    for a, b in spans(fixed):
        n = b - a
        if n < 4:
            continue
        s = np.linspace(0.0, 1.0, n + 1)
        w = np.sin(math.pi * s)[:, None]
        L = float(np.sum(rest[a:b]))
        slack = L - float(np.sum(seg[a:b]))
        for axis, name in ((0, "x"), (1, "y"), (2, "z")):
            for sign in (1.0, -1.0):
                d = np.zeros(3); d[axis] = sign

                def bumped(A):
                    Q = P0.copy()
                    Q[a:b + 1] += w * (A * d)
                    return Q

                def length(A):
                    Q = bumped(A)
                    return float(np.sum(np.linalg.norm(np.diff(Q[a:b + 1], axis=0), axis=1)))

                A = nudge_frac * L
                if slack > 1e-6:
                    lo, hi = 0.0, amplitude_frac * L
                    if length(hi) <= L:
                        A = hi
                    else:
                        for _ in range(30):
                            mid = 0.5 * (lo + hi)
                            lo, hi = (mid, hi) if length(mid) <= L else (lo, mid)
                        A = max(lo, nudge_frac * L)
                seeds[f"{'+' if sign > 0 else '-'}{name}@{a}"] = bumped(A)
    return seeds


def distinct(solutions, tol=2.0):
    """Keep one solution per basin: two are the same bow when no node differs by more than tol."""
    kept = []
    for sol in sorted(solutions, key=lambda s: s["energy"]):
        if all(np.max(np.linalg.norm(sol["P"] - k["P"], axis=1)) > tol for k in kept):
            kept.append(sol)
    return kept


def metrics(P, P0, s, prob, body_of=None):
    dev = np.linalg.norm(P - P0, axis=1)
    i = int(np.argmax(dev))
    _e, L, _t = tangents(P)
    out = {"max_deviation_mm": float(dev[i]), "at_s": float(s[i]),
           "sag_max_mm": float(np.max(P0[:, 2] - P[:, 2])),
           "stretch_max_pct": float(100.0 * np.max(np.abs(L - prob.ds) / prob.ds))}
    if prob.sdf is not None:
        d, _n = prob.sdf(P)
        free = prob.free
        # the physical figures: the field's distance less the tube's own radius, and how far
        # any node sits inside the world (a residual the penalty did not close)
        out["min_clearance_mm"] = float(np.min(d[free] - prob.radius)) if free.any() else None
        out["max_penetration_mm"] = float(np.max(np.maximum(0.0, prob.radius - d[free]))) if free.any() else 0.0
        touching = free & (d <= prob.r_clear + 0.3)
        contacts, j = [], 0
        while j < len(P):
            if touching[j]:
                k = j
                while k < len(P) and touching[k]:
                    k += 1
                names = sorted(set(body_of(P[j:k]))) if body_of else []
                contacts.append({"s_range": [float(s[j]), float(s[k - 1])], "bodies": names})
                j = k
            else:
                j += 1
        out["contacts"] = contacts
    return out


# --- self-test against beam theory --------------------------------------------------------------


def _selftest():
    sec = tube_section(**LLDPE_QUARTER)
    EI, EA, w = sec["EI"], sec["EA"], sec["w_full"]
    ds = 4.0
    print(f"1/4in LLDPE: EI {EI:.0f} N mm^2, EA {EA:.0f} N, w_full {w:.3e} N/mm")

    # 1. cantilever, tip deflection w L^4 / (8 EI)
    L = 200.0
    P0, s = resample([(0, 0, 0), (L, 0, 0)], ds)
    fixed = np.zeros(len(P0), bool); fixed[:3] = True
    prob = RodProblem(P0, fixed, EI, EA, w, 3.175)
    P, E, res = prob.solve()
    tip, theory = P0[-1, 2] - P[-1, 2], w * (L - 2 * ds) ** 4 / (8 * EI)   # clamped at node 2
    print(f"cantilever {L:.0f}: tip sag {tip:.3f} mm vs theory {theory:.3f} ({100*(tip/theory-1):+.1f} %)  iters {res['nit']}")
    assert abs(tip / theory - 1) < 0.05

    # 2. clamped-clamped, mid sag w L^4 / (384 EI)
    L = 300.0
    P0, s = resample([(0, 0, 0), (L, 0, 0)], ds)
    fixed = np.zeros(len(P0), bool); fixed[:3] = True; fixed[-3:] = True
    prob = RodProblem(P0, fixed, EI, EA, w, 3.175)
    P, E, res = prob.solve()
    mid, theory = np.max(P0[:, 2] - P[:, 2]), w * (L - 4 * ds) ** 4 / (384 * EI)   # clamped at nodes 2 and -3
    print(f"clamped-clamped {L:.0f}: mid sag {mid:.3f} mm vs theory {theory:.3f} ({100*(mid/theory-1):+.1f} %)  iters {res['nit']}")
    assert abs(mid / theory - 1) < 0.05

    # 3. an authored L with a 25.4 corner, both ends clamped, springs back: length kept, bow grows
    path = [(0, 0, 0), (100, 0, 0)] + [(100 + 25.4 * math.sin(a), 25.4 * (1 - math.cos(a)), 0)
                                        for a in np.linspace(0, math.pi / 2, 12)] + [(125.4, 125.4, 0)]
    P0, s = resample(path, ds)
    fixed = np.zeros(len(P0), bool); fixed[:3] = True; fixed[-3:] = True
    prob = RodProblem(P0, fixed, EI, EA, w, 3.175, gravity=False)
    P, E, res = prob.solve()
    m = metrics(P, P0, s, prob)
    print(f"L-corner springback: max deviation {m['max_deviation_mm']:.2f} mm at s {m['at_s']:.0f}, "
          f"stretch {m['stretch_max_pct']:.2f} %, energy {E:.2f} N mm, iters {res['nit']}")
    assert m["max_deviation_mm"] > 5.0 and m["stretch_max_pct"] < 0.5
    # half-set keeps some of the corner
    prob2 = RodProblem(P0, fixed, EI, EA, w, 3.175, c=natural_turns(P0, 0.5), gravity=False)
    P2, E2, _ = prob2.solve()
    m2 = metrics(P2, P0, s, prob2)
    print(f"  half-set: max deviation {m2['max_deviation_mm']:.2f} mm, energy {E2:.2f}")
    assert m2["max_deviation_mm"] < m["max_deviation_mm"]

    # 4. contact: a clamped-clamped rod 2 mm over a floor at z=0 must not sag through it
    L = 400.0
    P0, s = resample([(0, 0, 3.7), (L, 0, 3.7)], ds)   # 0.5 mm clear of the floor at the clamps
    fixed = np.zeros(len(P0), bool); fixed[:3] = True; fixed[-3:] = True
    floor = lambda P: (P[:, 2].copy(), np.tile(np.array([0.0, 0.0, 1.0]), (len(P), 1)))
    prob = RodProblem(P0, fixed, EI, EA, w, 3.175, sdf=floor, clearance=0.0)
    P, E, res = prob.solve()
    free_sag = w * L ** 4 / (384 * EI)
    print(f"floor contact: free sag would be {free_sag:.2f} mm, lowest free node z {P[prob.free, 2].min():.3f} "
          f"(radius 3.175), contacts {metrics(P, P0, s, prob)['contacts']}")
    assert P[prob.free, 2].min() > 3.175 - 0.3 and free_sag > 0.6

    # 5. alternate bows: a straight tube 20 mm longer than the gap between its clamped ends.
    #    Under gravity a bow between collinear clamps rolls about the chord to the bottom, so
    #    this one runs without it; the real runs have corners, which is what makes their basins.
    L = 300.0
    P0, s = resample([(0, 0, 0), (L, 0, 0)], ds)
    rest = np.full(len(P0) - 1, ds)                 # the stock is L long ...
    P0[:, 0] *= (L - 20.0) / L                      # ... and its ends are 20 closer: it must bow
    fixed = np.zeros(len(P0), bool); fixed[:3] = True; fixed[-3:] = True
    prob = RodProblem(P0, fixed, EI, EA, w, 3.175, rest=rest, gravity=False)   # no gravity: every bow is a basin
    sols = []
    for name, seed in bump_seeds(P0, fixed, rest).items():
        P, E, res = prob.solve(seed)
        sols.append({"seed": name, "energy": E, "P": P})
    kept = distinct(sols)
    print("compressed tube: distinct bows " + ", ".join(
        f"{k['seed']} E={k['energy']:.2f} amp={np.max(np.linalg.norm(k['P'] - P0, axis=1)):.1f}" for k in kept))
    assert len(kept) >= 2
    print("selftest OK")


if __name__ == "__main__":
    _selftest()
