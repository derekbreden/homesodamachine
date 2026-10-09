"""Wave 4 follow-up: variant C' keeps one-knob purity. The sixth wire (vertical-angle
constraint, no longer a knob because yaw moved to the couch Y slide) must meet both
the grip axis and the hole axis for W_grip and W_hole to stay single: it lies in the
(grip axis, hole axis) plane. Their W_vert was one such line from the grip-base loop;
here it may attach anywhere on the grip axis (s = 60..330 mm from the dot, a shell
boss or the butt sleeve) at any direction within that plane. Loads: variant B's
(sequence-of-use load cases). Also re-runs A for its feasible count."""
import math
import numpy as np
import wave4_wire_search as S
W = S.W
rng = np.random.default_rng(23)
g = W.g_ax; h = W.h_ax
n_gh = W.unit(np.cross(g, h))


def w6_in_plane():
    s = rng.uniform(60, 330)
    a = W.D + s * g
    ang = rng.uniform(0, 2 * math.pi)
    e2 = W.unit(np.cross(n_gh, g))       # in-plane, perpendicular to g
    u = W.unit(math.cos(ang) * g + math.sin(ang) * e2)
    return ("W_6", a, u, 400)


def run_cprime(n=40000):
    feas = []
    best = (-1e9, None, None)
    for _ in range(n):
        q = W.random_q()
        wires = W.layout(q)[:5] + [w6_in_plane()]
        if np.linalg.cond(W.jac(wires)) > 1e5:
            continue
        if any(W.line_hits(a, u, L) for _, a, u, L in wires):
            continue
        pre = S.preloads()
        if pre is None:
            continue
        m = S.worst_seq(wires, pre)
        if m >= 5.0:
            feas.append((W.compliance(wires), m, wires, pre))
        if m > best[0]:
            best = (m, wires, pre)
    return feas, best


if __name__ == "__main__":
    feasA, bestA = S.run("A")
    print(f"== A (theirs): {len(feasA)} of 40000 feasible, best margin {bestA[0]:.2f} N")
    feas, best = run_cprime()
    ms = sorted([f[1] for f in feas], reverse=True)
    print(f"== C' (yaw on couch, sixth wire fixed in the (grip, hole) plane anywhere along the grip axis): {len(feas)} feasible; best margin {best[0]:.1f} N; top {[round(x,1) for x in ms[:6]]}")
    if feas:
        c, m, wires, pre = max(feas, key=lambda f: f[1])
        print(f"   highest-margin layout: margin {m:.1f} N, worst dot motion under 5 N {c*1000:.0f} um")
        for nm, a, u, L in wires:
            s_along = np.dot(a - W.D, g) if nm == "W_6" else None
            print(f"     {nm:6s} attach {np.round(a,0)} dir {np.round(u,2)}" + (f"  (s = {s_along:.0f} mm along the grip axis)" if s_along is not None else ""))
        for site, dd, f in pre:
            print(f"     preload at {np.round(site,0)} dir {np.round(dd,2)} {f:.1f} N")
        K = W.knob_matrix(wires)
        print("   first-order effect of 1 mm (X mm, Z mm, S deg, V deg, H deg, G deg):")
        for i, (nm, *_ ) in enumerate(wires):
            col = K[:, i]
            print(f"     {nm:6s} X {col[0]:+.3f} Z {col[1]:+.3f} S {math.degrees(col[2]):+.3f} V {math.degrees(col[3]):+.3f} H {math.degrees(col[4]):+.3f} G {math.degrees(col[5]):+.3f}")
        c2, m2, w2, p2 = min(feas, key=lambda f: f[0])
        print(f"   stiffest feasible: {c2*1000:.0f} um, margin {m2:.1f} N")


def run_cprime_their_loads(n=40000):
    feas = []
    for _ in range(n):
        q = W.random_q()
        wires = W.layout(q)[:5] + [w6_in_plane()]
        if np.linalg.cond(W.jac(wires)) > 1e5:
            continue
        if any(W.line_hits(a, u, L) for _, a, u, L in wires):
            continue
        pre = S.preloads()
        if pre is None:
            continue
        m = W.worst_tension(wires, pre)
        if m >= 5.0:
            feas.append(m)
    return feas
