"""One wire per parameter: a wire-located suspension whose knobs are decoupled.

Builds on carry-and-locate's wire-located suspension (three wire lines meeting
at the dot = a virtual ball joint; three more set orientation; bungees only
keep wires taut).  Here the orientation wires are placed so that each one's
length changes exactly ONE of Derek's rotations, to first order:

  * a rotation wire must have zero moment about the axes of the other two
    rotations  ->  it lies in the plane through the dot spanned by those two
    axes (any line from a point on an axis, lying in that plane, qualifies);
  * with the three concurrent wires fixed, the dot cannot move, so changing
    one rotation wire then turns the gun about its own axis only.

  W_hole  (hole knob)     : in the plane (grip axis, vertical)  -> a vertical wire from the grip-base loop
  W_vert  (vertical knob) : in the plane (grip axis, hole axis) -> a wire along the hole-axis direction from the same loop
  W_grip  (roll knob)     : in the plane (hole axis, vertical)  -> a vertical wire from an outrigger over the rim
  W_x, W_y, W_z           : lines through the dot; W_x horizontal, W_y along the tangent, W_z in the tangent plane,
                            which makes the X and Z knobs move the dot along X and Z only

The script searches the free choices (directions within those planes, attachment
offsets, two downward preloads) for a layout where all six wires stay taut
under gravity, the preloads and 5 N disturbances, then reports:
  1. the knob -> parameter matrix (first order),
  2. finite moves (nonlinear): parasitic changes when one knob is turned,
  3. dot stiffness with 1/16 in stainless rope,
  4. knob resolution for a 0.01 mm anchor micrometer.

Frame and gun proxy: geometry.py (scene frame, dial convention, pose 45/30/-15).
Masses [assumed]: gun 1.2 kg + shell 0.3 kg at borrowed-ecosystems' CG proxy (0,-20,190) local.
Run: python3 diagonal_wires.py
"""
import math
import numpy as np
from geometry import pose_point, proxy_points, JOINT, GRIP_BASE, R_IN, R_OUT, TUBE_H

POSE = (45, 30, -15)
D = JOINT.copy()
G0 = 9.81
MASS = 1.5
rng = np.random.default_rng(7)


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


gp = lambda p: pose_point(np.asarray(p, float), *POSE)
GB = gp(GRIP_BASE)
CG = gp([0, -20, 190])
TRIG = gp([0, -40, 175])
g_ax = unit(GB - D)                                   # grip axis
phi = math.radians(POSE[2])
h_ax = np.array([math.cos(phi), math.sin(phi), 0.0])  # hole axis (turned by the vertical axis)
z_ax = np.array([0.0, 0.0, 1.0])
x_ax, y_ax = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
Rg = np.column_stack([gp(e) - gp([0, 0, 0]) for e in np.eye(3)])   # gun local -> world rotation

# gun proxy samples for wire-clearance checks
GUN = np.vstack([np.array([gp(p) for p in v]) for v in proxy_points().values()])

# parameter twists (v at the dot [mm], omega [rad]); S = rotation about the tube axis (seam position, weld-irrelevant)
TW = {
    "X":  (x_ax, np.zeros(3)),
    "Z":  (z_ax, np.zeros(3)),
    "S":  (R_IN * y_ax, z_ax),
    "V":  (np.zeros(3), z_ax),
    "H":  (np.zeros(3), h_ax),
    "G":  (np.zeros(3), g_ax),
}
PNAMES = list(TW)
T = np.array([np.concatenate(TW[k]) for k in PNAMES]).T     # 6x6, columns = parameter twists


def perp_in_plane(a, b):
    """unit vector in plane(a,b) perpendicular to b"""
    return unit(a - np.dot(a, b) * b)


def layout(q):
    """q: free choices -> list of (name, attach, direction, free length)"""
    ax_az, zel, zside, ysgn, ga, gb_, gtilt, htilt, vtilt, vsgn, ac = q
    wires = []
    ux = np.array([math.cos(math.radians(ax_az)), math.sin(math.radians(ax_az)), 0.0])
    wires.append(("W_x", D + max(ac, 62) * ux, ux, 400))
    uy = ysgn * y_ax
    wires.append(("W_y", D + max(ac, 62) * uy, uy, 400))
    uz = unit([0, zside * math.cos(math.radians(zel)), math.sin(math.radians(zel))])
    wires.append(("W_z", D + ac * uz, uz, 400))
    # grip-roll wire: attach in plane(h, z) on an outrigger; direction in the same plane
    ag = D + ga * h_ax + gb_ * z_ax
    ug = unit(math.cos(math.radians(gtilt)) * z_ax + math.sin(math.radians(gtilt)) * h_ax)
    wires.append(("W_grip", ag, ug, 400))
    # hole wire: from the grip-base loop, in plane(g, z)
    e1 = perp_in_plane(g_ax, z_ax)                      # horizontal direction of the grip axis
    uh = unit(math.cos(math.radians(htilt)) * z_ax + math.sin(math.radians(htilt)) * e1)
    wires.append(("W_hole", GB, uh, 400))
    # vertical-angle wire: from the grip-base loop, in plane(g, h)
    e2 = perp_in_plane(g_ax, h_ax)
    uv = unit(vsgn * (math.cos(math.radians(vtilt)) * h_ax + math.sin(math.radians(vtilt)) * e2))
    wires.append(("W_vert", GB, uv, 400))
    return wires


def jac(wires):
    return np.array([np.concatenate([u, np.cross(a - D, u)]) for _, a, u, _ in wires])


def line_hits(a, u, L, own_skip=25.0):
    pts = a[None, :] + np.linspace(own_skip, L, 60)[:, None] * u[None, :]
    r = np.hypot(pts[:, 0], pts[:, 1])
    tube = ((r < R_OUT + 8) & (pts[:, 2] > -90) & (pts[:, 2] < TUBE_H + 6)).any()
    d = np.min(np.linalg.norm(GUN[None, :, :] - pts[:, None, :], axis=2))
    return tube or d < 12


def tensions(wires, pre, extra=()):
    A = np.zeros((6, 6))
    for i, (_, a, u, _) in enumerate(wires):
        A[:3, i] = u
        A[3:, i] = np.cross(a - D, u)
    loads = [(CG, np.array([0, 0, -MASS * G0]))] + [(p, f * d) for p, d, f in pre] + list(extra)
    F = sum(f for _, f in loads)
    M = sum(np.cross(p - D, f) for p, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


PUSHES = [np.array(v, float) for v in ([5, 0, 0], [-5, 0, 0], [0, 5, 0], [0, -5, 0], [0, 0, 5], [0, 0, -5])]


def worst_tension(wires, pre):
    cases = [()] + [((D, f),) for f in PUSHES] + [((TRIG, Rg @ np.array([0, 5.0, 0])),)]
    cases += [((GB, f),) for f in ([0, -5.0, 0], [0, 0, -5.0], [5.0, 0, 0])]     # umbilical residual pulls
    return min(tensions(wires, pre, c).min() for c in cases)


def random_q():
    return (rng.uniform(-30, 30), rng.uniform(25, 88), rng.choice([-1, 1]), rng.choice([-1, 1]),
            rng.uniform(40, 130), rng.uniform(40, 170), rng.uniform(-40, 40),
            rng.uniform(-40, 40), rng.uniform(-35, 35), rng.choice([-1, 1]), rng.uniform(40, 90))


def compliance(wires):
    Jw = jac(wires)
    k = np.array([130e3 / L for *_, L in wires])
    C = np.linalg.inv(Jw.T @ np.diag(k) @ Jw)
    worst = 0.0
    for pt, f in [(D, np.array(v, float)) for v in ([5, 0, 0], [0, 5, 0], [0, 0, 5])] + [(GB, np.array([0, -5.0, 0])), (GB, np.array([0, 0, -5.0]))]:
        x = C @ np.concatenate([f, np.cross(pt - D, f)])
        worst = max(worst, np.linalg.norm(x[:3]))
    return worst


def search(n=40000):
    best = (-1e9, None, None)
    cands = []
    for _ in range(n):
        q = random_q()
        w = layout(q)
        if np.linalg.cond(jac(w)) > 1e5:
            continue
        if any(line_hits(a, u, L) for _, a, u, L in w):
            continue
        pre = []
        ok = True
        for site in (GB, D + np.array([70.0, -25.0, 60.0])):
            az, el = rng.uniform(-180, 180), rng.uniform(-90, -35)
            d = np.array([math.cos(math.radians(el)) * math.cos(math.radians(az)),
                          math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))])
            if line_hits(site, d, 500, own_skip=5):
                ok = False
                break
            pre.append((site, d, rng.uniform(0, 45)))
        if not ok:
            continue
        m = worst_tension(w, pre)
        if m >= 5.0:
            cands.append((compliance(w), m, q, pre))
        if m > best[0]:
            best = (m, q, pre)
    if cands:
        cands.sort(key=lambda c: c[0])
        c, m, q, pre = cands[0]
        print(f"{len(cands)} layouts keep every wire >= 5 N; stiffest worst-case dot motion under 5 N: {c*1000:.0f} um")
        return m, q, pre
    return best


def knob_matrix(wires):
    Jp = jac(wires) @ T               # d(lengths) / d(parameters)
    return np.linalg.inv(Jp)          # d(parameters) / d(lengths): column i = effect of 1 mm on wire i


def rotvec_to_R(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def lengths(wires, s):
    v, r = s[:3], s[3:]
    R = rotvec_to_R(r)
    out = []
    for _, a, u, L in wires:
        anchor = a + L * u
        a2 = D + v + R @ (a - D)
        out.append(np.linalg.norm(anchor - a2))
    return np.array(out)


def solve_pose(wires, target, s0=None):
    s = np.zeros(6) if s0 is None else s0.copy()
    for _ in range(30):
        f = lengths(wires, s) - target
        Jn = np.zeros((6, 6))
        for j in range(6):
            ds = np.zeros(6); ds[j] = 1e-6
            Jn[:, j] = (lengths(wires, s + ds) - lengths(wires, s)) / 1e-6
        step = np.linalg.solve(Jn, -f)
        s += step
        if np.linalg.norm(step) < 1e-10:
            break
    return s


def decompose(s):
    v, r = s[:3], s[3:]
    A = np.column_stack([g_ax, h_ax, z_ax])
    G, H, V = np.linalg.solve(A, r)
    return dict(X=v[0], Y=v[1], Z=v[2], G=math.degrees(G), H=math.degrees(H), V=math.degrees(V),
                Veff=math.degrees(V - v[1] / R_IN))


if __name__ == "__main__":
    import json, pathlib
    m, q, pre = search()
    pathlib.Path(__file__).with_name("diagonal_wires_layout.json").write_text(json.dumps(
        {"q": [float(v) for v in q], "pre": [[list(map(float, site)), list(map(float, d)), float(f)] for site, d, f in pre],
         "min_tension": float(m)}, indent=1))
    wires = layout(q)
    print(f"best layout: worst-case minimum tension {m:.1f} N over gravity, preloads, +/-5 N at the dot, 5 N trigger, 5 N umbilical pulls")
    names = [w[0] for w in wires]
    t0 = tensions(wires, pre)
    for (nm, a, u, L), t in zip(wires, t0):
        el = math.degrees(math.asin(u[2])); az = math.degrees(math.atan2(u[1], u[0]))
        print(f"  {nm:7s} attach {np.round(a,0)}  pulls toward az {az:6.1f} el {el:5.1f}  tension at rest {t:5.1f} N")
    for site, d, f in pre:
        el = math.degrees(math.asin(d[2])); az = math.degrees(math.atan2(d[1], d[0]))
        print(f"  preload at {np.round(site,0)} pulling az {az:6.1f} el {el:5.1f} with {f:4.1f} N")

    K = knob_matrix(wires)
    print("\n1. First-order knob effects: 1 mm longer on each wire changes (X mm, Z mm, S deg, V deg, H deg, G deg)")
    for i, nm in enumerate(names):
        col = K[:, i]
        vals = [col[0], col[1], math.degrees(col[2]), math.degrees(col[3]), math.degrees(col[4]), math.degrees(col[5])]
        print(f"  {nm:7s} " + "  ".join(f"{p}={v:+8.4f}" for p, v in zip(PNAMES, vals)))

    print("\n2. Finite moves (exact wire geometry): turn one knob, others fixed")
    base_len = lengths(wires, np.zeros(6))
    targets = {"W_grip": ("G", [2, 5, 10]), "W_hole": ("H", [2, 5, 10]), "W_vert": ("V", [2, 5, 10]),
               "W_x": ("X", [0.5, 1, 2]), "W_z": ("Z", [0.5, 1, 2])}
    for nm, (pk, amounts) in targets.items():
        i = names.index(nm); j = PNAMES.index(pk)
        per = K[j, i] if pk in ("X", "Z") else math.degrees(K[j, i])     # parameter per mm of this wire
        for amt in amounts:
            dL = np.zeros(6); dL[i] = amt / per
            s = solve_pose(wires, base_len + dL)
            dct = decompose(s)
            dot_move = math.hypot(dct["X"], dct["Z"])
            print(f"  {nm:7s} for {pk} {amt:>4}: X {dct['X']:+.3f} Z {dct['Z']:+.3f} Y {dct['Y']:+.3f} mm | "
                  f"G {dct['G']:+.3f} H {dct['H']:+.3f} V {dct['V']:+.3f} (V incl. tangent {dct['Veff']:+.3f}) deg")

    print("\n3. Stiffness at the dot, 1/16 in 7x7 stainless (EA ~130 kN), 400 mm free lengths, frame rigid")
    Jw = jac(wires)
    k = np.array([130e3 / L for *_, L in wires])
    C = np.linalg.inv(Jw.T @ np.diag(k) @ Jw)
    for label, (pt, f) in {"5 N +X at dot": (D, [5, 0, 0]), "5 N +Y at dot": (D, [0, 5, 0]), "5 N +Z at dot": (D, [0, 0, 5]),
                           "5 N umbilical pull -Y at grip base": (GB, [0, -5, 0])}.items():
        f = np.asarray(f, float); w = np.concatenate([f, np.cross(pt - D, f)])
        x = C @ w
        print(f"  {label:36s}: dot moves {np.linalg.norm(x[:3])*1000:5.1f} um, gun turns {math.degrees(np.linalg.norm(x[3:]))*60:5.2f} arcmin")

    print("\n4. Knob resolution with a 0.01 mm micrometer anchor slide")
    for nm, pk in (("W_grip", "G"), ("W_hole", "H"), ("W_vert", "V"), ("W_x", "X"), ("W_z", "Z")):
        i = names.index(nm); j = PNAMES.index(pk)
        per = K[j, i]
        if pk in ("X", "Z"):
            print(f"  {nm:7s}: 0.01 mm -> {pk} {abs(per)*0.01*1000:.1f} um;  25 mm micrometer travel spans {abs(per)*25:.1f} mm")
        else:
            print(f"  {nm:7s}: 0.01 mm -> {pk} {abs(math.degrees(per))*0.01:.4f} deg; 25 mm travel spans {abs(math.degrees(per))*25:.1f} deg "
                  f"(lever {1/abs(per):.0f} mm per rad)")
