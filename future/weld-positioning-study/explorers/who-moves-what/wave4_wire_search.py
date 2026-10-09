"""Wave 4 exchange: one-knob-one-parameter's knob-wired suspension, re-searched under
three allocation changes. Uses a vendored copy of their search
(vendored_okop_diagonal_wires.py; credit one-knob-one-parameter).

A  their layout constraints + their load cases (reproduce: few feasible, ~5.9 N)
B  their layout constraints + load cases taken from the sequence of use:
   - no trigger push (the trigger closes inside the shell, digest/K2)
   - gravity for 1.2 and 2.0 kg, CG shifted +/-20 mm in the gun's local y and z
   - umbilical 5 N at the grip base ALONG its exit direction (+ a 5 N sag case)
   - stuck-wire drag 5 N at the dot in the ONE direction the table drags it
     (+Y: the wire is on the arriving -Y side, so the station surface moves +Y)
   - 3 N wire-touch reaction at the dot, back up the wire
C  B's loads, and the vertical-axis angle moved to a couch Y slide (tube symmetry,
   1.08 mm per degree): the sixth wire is no longer a knob, so its attachment
   and direction are free (still clear of tube and gun)
D  C, and every wire must lean up the corner's escape direction d
   (u.d >= 0.15, d = (-0.537, 0, 0.844)): lifting the gun along d then slackens
   all six wires at once, so lift-off needs no unhooking; preloads pull within
   35 deg of -d (a balancer or weight hanging along -d).
Run: tools/cad-venv/bin/python wave4_wire_search.py
"""
import math
import numpy as np
import vendored_okop_diagonal_wires as W
from vendored_okop_geometry import pose_point

rng = np.random.default_rng(11)
D = W.D
GB = W.GB
d_esc = np.array([-math.sin(math.radians(32.5)), 0.0, math.cos(math.radians(32.5))])
gp = W.gp
fiber = W.unit(gp([0, -118 + 100 * -0.866, 237 + 100 * 0.5]) - GB)   # QBH exit along the grip rake (30 deg)
wire_dir = W.unit(gp([0, -24.7, 87.1]) - D)                            # dot -> guide back (scene proxy)


def gravity_cases():
    out = []
    for m in (1.2, 2.0):
        for dy, dz in ((0, 0), (20, 0), (-20, 0), (0, 20), (0, -20)):
            out.append((gp([0, -20 + dy, 190 + dz]), np.array([0, 0, -m * W.G0])))
    return out


DIST = [(), ((GB, 5.0 * fiber),), ((GB, np.array([0, 0, -5.0])),), ((D, np.array([0, 5.0, 0])),), ((D, -3.0 * wire_dir),),
        ((GB, 5.0 * fiber), (D, np.array([0, 5.0, 0])), (D, -3.0 * wire_dir))]


def tensions(wires, pre, grav, extra):
    A = np.zeros((6, 6))
    for i, (_, a, u, _) in enumerate(wires):
        A[:3, i] = u
        A[3:, i] = np.cross(a - D, u)
    loads = [grav] + [(p, f * dd) for p, dd, f in pre] + list(extra)
    F = sum(f for _, f in loads)
    M = sum(np.cross(p - D, f) for p, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


def worst_seq(wires, pre):
    return min(tensions(wires, pre, g, e).min() for g in gravity_cases() for e in DIST)


def rand_unit():
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)


FREE_SITES = [GB, D + np.array([70.0, -25.0, 60.0]), gp([0, 17, 200]), gp([0, 17, 120])]


def free_wire(escape=False):
    for _ in range(200):
        site = FREE_SITES[rng.integers(len(FREE_SITES))]
        u = rand_unit()
        if escape and np.dot(u, d_esc) < 0.15:
            continue
        return ("W_6", site, u, 400)
    return None


def dot_wires_escape():
    out = []
    names = ("W_d1", "W_d2", "W_d3")
    for nm in names:
        for _ in range(500):
            u = rand_unit()
            if np.dot(u, d_esc) >= 0.15:
                break
        ac = rng.uniform(40, 90)
        out.append((nm, D + ac * u, u, 400))
    return out


def preloads(escape=False):
    pre = []
    for site in (GB, D + np.array([70.0, -25.0, 60.0])):
        if escape:
            for _ in range(500):
                dd = rand_unit()
                if np.dot(dd, -d_esc) >= math.cos(math.radians(35)):
                    break
        else:
            az, el = rng.uniform(-180, 180), rng.uniform(-90, -35)
            dd = np.array([math.cos(math.radians(el)) * math.cos(math.radians(az)),
                           math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))])
        if W.line_hits(site, dd, 500, own_skip=5):
            return None
        pre.append((site, dd, rng.uniform(0, 45)))
    return pre


def run(variant, n=40000):
    feas, best = [], (-1e9, None, None)
    for _ in range(n):
        q = W.random_q()
        wires = W.layout(q)
        if variant in ("C", "D"):
            fw = free_wire(escape=(variant == "D"))
            wires = wires[:5] + [fw]                      # drop W_vert, add the free wire
            wires = [w for w in wires if w[0] != "W_vert"] if False else wires
            wires = [wires[i] for i in (0, 1, 2, 3, 4)] + [fw]
            wires = [w for w in wires]
            # layout() order: W_x, W_y, W_z, W_grip, W_hole, W_vert -> keep first five, replace sixth
        if variant == "D":
            dw = dot_wires_escape()
            if any(np.dot(u, d_esc) < 0.15 for _, _, u, _ in wires[3:5]):
                continue
            wires = dw + wires[3:]
        if np.linalg.cond(W.jac(wires)) > 1e5:
            continue
        if any(W.line_hits(a, u, L) for _, a, u, L in wires):
            continue
        pre = preloads(escape=(variant == "D"))
        if pre is None:
            continue
        m = W.worst_tension(wires, pre) if variant == "A" else worst_seq(wires, pre)
        if m >= 5.0:
            feas.append((W.compliance(wires), m, wires, pre))
        if m > best[0]:
            best = (m, wires, pre)
    return feas, best


if __name__ == "__main__":
    results = {}
    for v in ("A", "B", "C", "D"):
        feas, best = run(v)
        results[v] = (feas, best)
        ms = sorted([f[1] for f in feas], reverse=True)
        print(f"== variant {v}: {len(feas)} of 40000 layouts keep every wire >= 5 N; best worst-case margin {best[0]:.1f} N;"
              f" top margins {[round(x,1) for x in ms[:5]]}")
        if feas:
            feas.sort(key=lambda f: f[0])
            c, m, wires, pre = feas[0]
            print(f"   stiffest feasible: worst-case dot motion under 5 N {c*1000:.0f} um, margin {m:.1f} N")
            best_m = max(feas, key=lambda f: f[1])
            print(f"   highest-margin feasible: margin {best_m[1]:.1f} N, dot motion {best_m[0]*1000:.0f} um")
            for nm, a, u, L in best_m[2]:
                print(f"     {nm:6s} attach {np.round(a,0)} dir {np.round(u,2)}  u.d_escape {np.dot(u, d_esc):+.2f}")
            for site, dd, f in best_m[3]:
                print(f"     preload at {np.round(site,0)} dir {np.round(dd,2)} {f:.1f} N")
    # knob purity check for C: W_grip and W_hole still single (first order), with the free wire held
    feas, best = results["C"]
    if feas:
        c, m, wires, pre = max(feas, key=lambda f: f[1])
        K = W.knob_matrix(wires)
        names = [w[0] for w in wires]
        print("\n== variant C, highest-margin layout: first-order effect of 1 mm on each wire (X mm, Z mm, S deg, V deg, H deg, G deg)")
        for i, nm in enumerate(names):
            col = K[:, i]
            print(f"   {nm:6s} X {col[0]:+.3f} Z {col[1]:+.3f} S {math.degrees(col[2]):+.3f} V {math.degrees(col[3]):+.3f} H {math.degrees(col[4]):+.3f} G {math.degrees(col[5]):+.3f}")
