"""Wave 2, on machine-that-learns' C (hexapod with a software pivot).

Part 1 - their rigid-leg hexapod, their proposal geometry (hexapod_check.py): do the six legs keep one
sign of force across +/-7 deg about the dot and a set of disturbances? If a leg's force crosses zero,
its nut/rod-end play changes side and becomes random dot error (their 0.12 mm median, 0.20 mm 95th pct
for +/-0.05 mm leg play). If every leg keeps one sign, the same play is a constant offset that the
camera calibrates out once. How much constant preload does that take?

Part 2 - the same software-pivot idea built from my six wires (idea B): anchor travel needed for
+/-10 deg and +/-10 mm, and whether every wire stays taut across that workspace.

Loads (assumed): gun + shell 2.0 kg at the 'toward grip' CoM; trigger 5 N and cable 5 N as below.
"""
import numpy as np
from pose import pose_point, JOINT, LOCAL, rot_matrix

D = JOINT.copy()
W = 2.0 * 9.81
POSE = (45, 30, -15)
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
COM = gp([0, -25, 190])
TRIG = gp([0, -40, 175])
GB = gp(LOCAL["grip_base"])
Rg = rot_matrix(*POSE)


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


def rodrigues(n, deg):
    n = unit(n); th = np.radians(deg)
    K = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


AXES = {"grip": GB - D, "hole": np.array([-1.0, 0, 0]), "vertical": np.array([0, 0, 1.0])}
ROTS = [("nominal", None, 0)] + [(f"{a} {s:+d}", a, s) for a in AXES for s in (-7, 7)]
DIST = {"none": [], "trigger +z_local": [(TRIG, 5 * Rg[:, 2])], "trigger -z_local": [(TRIG, -5 * Rg[:, 2])],
        "trigger +y_local": [(TRIG, 5 * Rg[:, 1])], "cable -Y": [(GB, np.array([0, -5.0, 0]))],
        "cable +Y": [(GB, np.array([0, 5.0, 0]))], "cable down": [(GB, np.array([0, 0, -5.0]))],
        "cable up": [(GB, np.array([0, 0, 5.0]))], "wire tip drag +Y": [(D, np.array([0, 3.0, 0]))],
        "wire tip drag -Y": [(D, np.array([0, -3.0, 0]))]}

# ---------------- Part 1: rigid hexapod, their geometry ----------------
P0 = D + np.array([-77.9, -105.1, 153.5]); n = unit([0.775, 0.158, 0.612])
u = unit(np.cross(n, [0, 0, 1])); v = np.cross(n, u)
H, RP, RB = 190.0, 60.0, 120.0
B0 = P0 + H * n
plat0 = [P0 + RP * (np.cos(np.radians(a)) * u + np.sin(np.radians(a)) * v) for a in (-10, 10, 110, 130, 230, 250)]
base = [B0 + RB * (np.cos(np.radians(a)) * u + np.sin(np.radians(a)) * v) for a in (-50, 50, 70, 170, 190, 290)]


def leg_forces(R, extra):
    plat = [D + R @ (p - D) for p in plat0]
    A = np.zeros((6, 6))
    for i, (p, b) in enumerate(zip(plat, base)):
        e = unit(b - p)                          # tension pulls the platform toward the base
        A[:3, i] = e; A[3:, i] = np.cross(p - D, e)
    loads = [(D + R @ (COM - D), np.array([0, 0, -W]))] + [(D + R @ (pt - D), f) for pt, f in extra]
    F = sum(f for _, f in loads); M = sum(np.cross(pt - D, f) for pt, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


print("== Part 1: rigid-leg hexapod (their geometry), leg force range across +/-7 deg and disturbances ==")
for preload in (0, 20, 40, 80):
    allf = []
    for name, ax, s in ROTS:
        R = np.eye(3) if ax is None else rodrigues(AXES[ax], s)
        Pc = D + R @ (P0 - D)
        for dname, extra in DIST.items():
            ex = list(extra) + ([(P0, -preload * (R @ n))] if preload else [])
            allf.append(leg_forces(R, ex))
    allf = np.array(allf)
    lo, hi = allf.min(0), allf.max(0)
    flips = [i + 1 for i in range(6) if lo[i] < 0 < hi[i]]
    print(f"  extra pull {preload:3d} N away from the base: leg force min {np.round(lo,1)}  max {np.round(hi,1)}"
          f"  -> {'legs changing sign: ' + str(flips) if flips else 'every leg keeps one sign'}")

print("  -- with a float carrying the gun at its CoM (constant upward W) plus the same central pull --")
for preload in (0, 20, 40, 80):
    allf = []
    for name, ax, s_ in ROTS:
        R = np.eye(3) if ax is None else rodrigues(AXES[ax], s_)
        Pc = D + R @ (P0 - D)
        for dname, extra in DIST.items():
            ex = list(extra) + [(COM, np.array([0, 0, W]))] + ([(P0, -preload * (R @ n))] if preload else [])
            allf.append(leg_forces(R, ex))
    allf = np.array(allf)
    lo, hi = allf.min(0), allf.max(0)
    flips = [i + 1 for i in range(6) if lo[i] < 0 < hi[i]]
    print(f"  float + pull {preload:3d} N: leg force min {np.round(lo,1)}  max {np.round(hi,1)}"
          f"  -> {'legs changing sign: ' + str(flips) if flips else 'every leg keeps one sign'}")


# ---------------- Part 2: six wires (idea B layout) as the software-pivot hexapod ----------------
def uw(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
HT = gp(LOCAL["housing_top_back"])
att0 = [D + 70 * uw(a, 55) for a in (90, -30, 210)] + [GB, GB, HT]
dirs0 = [uw(a, 55) for a in (90, -30, 210)] + [uw(32, 43), uw(184, 72), uw(-158, 12)]
Ls = [400, 400, 400, 330, 330, 330]
anch = [a + L * d for a, d, L in zip(att0, dirs0, Ls)]
ARM = np.array([115.0, 9.0, 200.0])
bung = [(GB, 37.5 * uw(-133, -88)), (ARM, np.array([0, 0, -35.6]))]


def wire_state(R, t):
    att = [D + R @ (a - D) + t for a in att0]
    lengths = np.array([np.linalg.norm(an - a) for an, a in zip(anch, att)])
    A = np.zeros((6, 6))
    for i, (a, an) in enumerate(zip(att, anch)):
        e = unit(an - a); A[:3, i] = e; A[3:, i] = np.cross(a - D, e)
    return A, lengths, att


print("\n== Part 2: the six-wire layout as a software-pivot hexapod ==")
worst = 1e9; travel = np.zeros(6)
cases = []
for ax in AXES:
    for s in (-10, -5, 5, 10):
        cases.append((f"{ax} {s:+d} deg", rodrigues(AXES[ax], s), np.zeros(3)))
for t in ([10, 0, 0], [-10, 0, 0], [0, 10, 0], [0, -10, 0], [0, 0, 10], [0, 0, -10]):
    cases.append((f"translate {t}", np.eye(3), np.array(t, float)))
L0 = wire_state(np.eye(3), np.zeros(3))[1]
for name, R, t in cases:
    A, lengths, att = wire_state(R, t)
    travel = np.maximum(travel, np.abs(lengths - L0))
    mins = []
    for dname, extra in DIST.items():
        loads = [(D + R @ (COM - D) + t, np.array([0, 0, -W]))] + [(D + R @ (p - D) + t, f) for p, f in bung] \
                + [(D + R @ (p - D) + t, f) for p, f in extra]
        F = sum(f for _, f in loads); M = sum(np.cross(p - D, f) for p, f in loads)
        mins.append(np.linalg.solve(A, -np.concatenate([F, M])).min())
    worst = min(worst, min(mins))
    print(f"  {name:22s}: wire length change {np.round(lengths - L0, 1)} mm; min tension {min(mins):5.1f} N")
print(f"  largest length change per wire over this workspace: {np.round(travel, 1)} mm; worst min tension {worst:.1f} N")


# ---------------- Part 3: how much central preload keeps every leg one-signed? ----------------
print("\n== Part 3: smallest central pull (away from the base) that keeps every rigid leg one-signed ==")
SETS = {
    "all disturbances (hand trigger 5 N, cable 5 N, wire drag 3 N)": list(DIST.keys()),
    "trigger closed in the shell, cable carried (residual 1 N), wire drag 3 N":
        ["none", "wire tip drag +Y", "wire tip drag -Y", "cable1 -Y", "cable1 +Y", "cable1 down", "cable1 up"],
}
DIST.update({"cable1 -Y": [(GB, np.array([0, -1.0, 0]))], "cable1 +Y": [(GB, np.array([0, 1.0, 0]))],
             "cable1 down": [(GB, np.array([0, 0, -1.0]))], "cable1 up": [(GB, np.array([0, 0, 1.0]))]})
for sname, keys in SETS.items():
    for floated in (False, True):
        found = None
        for P in range(0, 601, 5):
            allf = []
            for name, ax, s_ in ROTS:
                R = np.eye(3) if ax is None else rodrigues(AXES[ax], s_)
                Pc = D + R @ (P0 - D)
                for k in keys:
                    ex = list(DIST[k]) + ([(COM, np.array([0, 0, W]))] if floated else []) + ([(P0, -P * (R @ n))] if P else [])
                    allf.append(leg_forces(R, ex))
            allf = np.array(allf)
            if all(not (lo < 0 < hi) for lo, hi in zip(allf.min(0), allf.max(0))):
                found = (P, allf.min(0), allf.max(0)); break
        tag = "gun floated at CoM" if floated else "gun weight on the legs"
        if found:
            print(f"  {sname}; {tag}: {found[0]} N  (leg forces {np.round(found[1],0)} .. {np.round(found[2],0)})")
        else:
            print(f"  {sname}; {tag}: none up to 600 N")
