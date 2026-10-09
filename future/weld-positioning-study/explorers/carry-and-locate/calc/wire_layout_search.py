"""Idea B repair: search orientation-wire directions (W4, W5 at the grip base; W6 at the housing back or
grip front) and the bungee's line so all six wires stay taut under gravity + bungee and under 5 N pushes
at the dot in six directions and a 5 N trigger push. Anchors must be above their attachment (el >= 10 deg);
wires at the grip base avoid the umbilical's exit sector (az -130..-30 deg). Random search, fixed seed."""
import numpy as np
from pose import pose_point, LOCAL, JOINT
rng = np.random.default_rng(1)
POSE = (45, 30, -15)
D = JOINT.copy()
def unit(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
gb, ht, hf = gp(LOCAL["grip_base"]), gp(LOCAL["housing_top_back"]), gp(LOCAL["housing_top_front"])
com = gp([0, -25, 190]); tp = gp([0, -40, 175])
R = np.column_stack([gp(e) - gp([0,0,0]) for e in np.eye(3)])
W = 9.81
concurrent = [(D + 70*unit(a, 55), unit(a, 55)) for a in (90, -30, 210)]
pushes = [np.array(v, float) for v in ([5,0,0],[-5,0,0],[0,5,0],[0,-5,0],[0,0,5],[0,0,-5])]
def min_tension(wires, bpt, bdir, Fb, extra=()):
    A = np.zeros((6, 6))
    for i, (p, u) in enumerate(wires):
        A[:3, i] = u; A[3:, i] = np.cross(p - D, u)
    if np.linalg.cond(A) > 1e4:
        return -1e9, None
    base = [(com, np.array([0, 0, -W])), (bpt, Fb * bdir)] + list(extra)
    worst = 1e9; t0 = None
    cases = [base] + [base + [(D, f)] for f in pushes] + [base + [(tp, R @ np.array([0, 5.0, 0]))]]
    for c in cases:
        F = sum(f for _, f in c); M = sum(np.cross(p - D, f) for p, f in c)
        t = np.linalg.solve(A, -np.concatenate([F, M]))
        if t0 is None: t0 = t
        worst = min(worst, t.min())
    return worst, t0
best = (-1e9,)
for it in range(60000):
    a4, a5 = rng.uniform(-30, 230, 2)      # avoid umbilical sector -130..-30
    e4, e5 = rng.uniform(10, 85, 2)
    site6 = [ht, hf, gb][rng.integers(3)]
    a6, e6 = rng.uniform(-180, 180), rng.uniform(10, 85)
    wires = concurrent + [(gb, unit(a4, e4)), (gb, unit(a5, e5)), (site6, unit(a6, e6))]
    bsite = gb
    baz, bel = rng.uniform(-180, 180), rng.uniform(-90, -30)   # bungee pulls downward-ish
    bd_ = unit(baz, bel)
    # reject a bungee line that passes through the tube (scene z 0..152.4, r < 66)
    ts = np.linspace(0, 600, 121); pts = gb[None, :] + ts[:, None] * bd_[None, :]
    inside = (np.hypot(pts[:, 0], pts[:, 1]) < 66) & (pts[:, 2] > -90) & (pts[:, 2] < 160)
    if inside.any():
        continue
    Fb = rng.uniform(5, 40)
    F2 = rng.uniform(0, 40)
    arm = np.array([115.0, rng.uniform(-40, 40), 200.0])  # shell arm reaching out over the rim at +X (scene coords)
    m, t0 = min_tension(wires, bsite, unit(baz, bel), Fb, extra=[(arm, np.array([0, 0, -F2]))])
    if m > best[0]: arm_best = (arm.copy(), F2)
    if m > best[0]:
        best = (m, (a4, e4), (a5, e5), (a6, e6), ["ht", "hf", "gb"][[id(ht), id(hf), id(gb)].index(id(site6))],
                (baz, bel), ["gb", "ht", "com"][[id(gb), id(ht), id(com)].index(id(bsite))], Fb, t0)
m, w4, w5, w6, s6, bd, bs, Fb, t0 = best
print(f"best worst-case minimum tension {m:.2f} N")
print(f"W4 at grip base az/el {np.round(w4,0)}, W5 at grip base az/el {np.round(w5,0)}, W6 at {s6} az/el {np.round(w6,0)}")
print(f"bungee at {bs}, pulling az/el {np.round(bd,0)} with {Fb:.1f} N")
print("tensions under gravity + bungee:", np.round(t0, 1))
print("second bungee: straight down from a shell arm at", np.round(arm_best[0],0), "(scene) with", round(arm_best[1],1), "N")
