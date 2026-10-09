"""carry-and-locate's all-taut six-wire layout, driven as a cable robot: how far must each anchor
move, and do all six wires stay taut, across a working neighbourhood around the opening pose?

Layout = their wire_layout_search.py result (as of 2026-09-28 05:28, corrected pose):
  W1-W3: attachments at dot + 70*u(az, 55 deg), az 90 / -30 / 210, anchors 400 mm further on
  W4, W5 at the grip base, az/el (32, 43) and (184, 72); W6 at housing back top, (-158, 12); 330 mm free
  preload 1: 37.5 N at the grip base, direction az/el (-133, -88)
  preload 2: 35.6 N straight down from a shell arm at scene (115, 9, 200)
Anchors are FIXED points here; a cable robot changes wire lengths (winch or anchor slide).
Gun 1 kg, CoM local (0, -25, 190), trigger point local (0, -40, 175): their assumptions.
Also checks whether W1 crosses the joint camera's line of sight (camera at dot + (-45, 70, 85)).
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from cl_pose_snapshot import pose_point, LOCAL, JOINT  # noqa: E402  (snapshot of their module, dial offset applied)

POSE = (45, 30, -15)
D = JOINT.copy()
W = 9.81


def unit(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])


gp = lambda l: pose_point(np.asarray(l, float), *POSE)
gb, ht = gp(LOCAL["grip_base"]), gp(LOCAL["housing_top_back"])
com, tp = gp([0, -25, 190]), gp([0, -40, 175])
Rm = np.column_stack([gp(e) - gp([0, 0, 0]) for e in np.eye(3)])
arm = np.array([115.0, 9.0, 200.0])

att = [D + 70 * unit(a, 55) for a in (90, -30, 210)] + [gb, gb, ht]
dirs = [unit(a, 55) for a in (90, -30, 210)] + [unit(32, 43), unit(184, 72), unit(-158, 12)]
free = [400, 400, 400, 330, 330, 330]
anch = [p + L * u for p, u, L in zip(att, dirs, free)]
b1dir, b1F = unit(-133, -88), 37.5
b2F = 35.6
EA = 130e3  # 1/16 in 7x7 stainless, their figure


def rot(n, deg):
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    K = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])
    th = np.radians(deg)
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


AXES = {"grip axis": gb - D, "hole axis": np.array([-1.0, 0, 0]), "vertical": np.array([0, 0, 1.0])}
pushes = [np.array(v, float) for v in ([5, 0, 0], [-5, 0, 0], [0, 5, 0], [0, -5, 0], [0, 0, 5], [0, 0, -5])]


def evaluate(Rr, t):
    mv = lambda p: D + Rr @ (p - D) + t
    A_ = [mv(p) for p in att]
    L0 = [np.linalg.norm(a - p) for a, p in zip(anch, att)]
    L1 = [np.linalg.norm(a - p) for a, p in zip(anch, A_)]
    U = [(a - p) / np.linalg.norm(a - p) for a, p in zip(anch, A_)]
    dotn = mv(D)
    Amat = np.zeros((6, 6))
    for i, (p, u) in enumerate(zip(A_, U)):
        Amat[:3, i] = u
        Amat[3:, i] = np.cross(p - dotn, u)
    base = [(mv(com), np.array([0, 0, -W])), (mv(gb), b1F * b1dir), (mv(arm), np.array([0, 0, -b2F]))]
    cases = [base] + [base + [(dotn, f)] for f in pushes] + [base + [(mv(tp), Rr @ Rm @ np.array([0, 5.0, 0]))]]
    tmin = 1e9
    for c in cases:
        F = sum(f for _, f in c)
        M = sum(np.cross(p - dotn, f) for p, f in c)
        tt = np.linalg.solve(Amat, -np.concatenate([F, M]))
        tmin = min(tmin, tt.min())
    k = [EA / l for l in L1]
    J = np.array([np.concatenate([u, np.cross(p - dotn, u)]) for p, u in zip(A_, U)])
    K = J.T @ np.diag(k) @ J
    C = np.linalg.inv(K)
    dmax = max(np.linalg.norm((C @ np.concatenate([f, np.zeros(3)]))[:3]) for f in pushes)
    return np.array(L1) - np.array(L0), tmin, dmax


print("slide travel per wire (mm), worst-case minimum tension (N), dot deflection under 5 N (um)")
worst_t = 1e9
for name, ax in AXES.items():
    for deg in (-10, -5, 5, 10):
        dl, tmin, dmax = evaluate(rot(ax, deg), np.zeros(3))
        worst_t = min(worst_t, tmin)
        flag = "" if tmin > 0 else "   <- a wire goes slack"
        print(f"  {deg:+3d} deg about {name:9s}: dL = {np.round(dl, 1)}  min T {tmin:6.1f}  5 N -> {dmax*1000:5.1f} um{flag}")
for t in ([5, 0, 0], [-5, 0, 0], [0, 5, 0], [0, -5, 0], [0, 0, 5], [0, 0, -5]):
    dl, tmin, dmax = evaluate(np.eye(3), np.array(t, float))
    flag = "" if tmin > 0 else "   <- a wire goes slack"
    print(f"  translate {str(t):12s}: dL = {np.round(dl, 1)}  min T {tmin:6.1f}  5 N -> {dmax*1000:5.1f} um{flag}")

# W1 vs the joint camera sightline
cam = D + np.array([-45.0, 70.0, 85.0])
p, u = att[0], dirs[0]
best = 1e9
for s in np.linspace(0, 1, 201):
    q = D + s * (cam - D)
    for tt in np.linspace(0, free[0], 401):
        best = min(best, np.linalg.norm(p + tt * u - q))
print(f"\nclosest approach of W1 to the joint camera's line of sight: {best:.0f} mm")
for i, a in enumerate(att[:3]):
    rel = a - D
    # distance of the attachment from the barrel axis
    b = Rm[:, 2]
    print(f"W{i+1} attachment {np.round(rel,0)} from the dot; {np.linalg.norm(rel - np.dot(rel, b)*b):.0f} mm from the barrel axis")

print("\nplan angle by translation instead of rotation (circle symmetry): -psi about the vertical == move along the tangent")
for psi in (-15, -10, 10, 15):
    t = np.array([-(R_ := 61.85) * (1 - np.cos(np.radians(psi))), -R_ * np.sin(np.radians(psi)), 0.0])
    dl, tmin, dmax = evaluate(np.eye(3), t)
    flag = "" if tmin > 0 else "   <- a wire goes slack"
    print(f"  plan angle {psi:+d} deg as translation {np.round(t, 1)}: dL = {np.round(dl, 1)}  min T {tmin:5.1f}{flag}")
