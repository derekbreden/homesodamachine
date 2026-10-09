"""Wave 3: can the three angle wires each set ONE of Derek's angles? (one-knob-one-parameter's question)

Result of the first attempt (kept below as 'strict'): a fully diagonal map is impossible with point
attachments. At one attachment point every rotation about the dot produces a velocity in the same 2-D
plane (perpendicular to the radius), so a wire insensitive to two rotations there is insensitive to all
three. What works: plan angle done as a tangent translation (never a vertical rotation), W5 holds the
vertical rotation at zero, W4 alone sets hole tilt, W6 alone sets grip-axis roll. Constraints:
u5 . (x x r_gb) = 0 (W5 blind to hole), u6 . (x x r6) = 0 (W6 blind to hole); roll never moves the grip
base, so W4 and W5 are blind to roll. 'mode = "practical"' below.

W1-W3 stay concurrent at the dot (dot XYZ). Rotations about the dot do not change them (1st order).
Choose W4, W5 at the grip base and W6 at the housing back so that, to first order:
  W4 changes only with hole-axis rotation, W5 only with vertical-axis rotation, W6 only with grip-axis roll.
A wire attached at r (from the dot) with unit direction u changes length by u . (w x r) for rotation w.
Grip base lies on the grip axis, so roll never changes W4/W5. So: u4 . (z x r_gb) = 0, u5 . (x x r_gb) = 0,
u6 . (x x r6) = 0 and u6 . (z x r6) = 0.  Then search the remaining freedoms (and two bungee preloads)
for a layout that stays taut under gravity + the wave-1 disturbance set. Pose: opening pose, dial convention.
"""
import numpy as np
from pose import pose_point, JOINT, LOCAL, rot_matrix

rng = np.random.default_rng(3)
D = JOINT.copy(); POSE = (45, 30, -15); W = 9.81
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
GB = gp(LOCAL["grip_base"]); HT = gp(LOCAL["housing_top_back"]); COM = gp([0, -25, 190]); TP = gp([0, -40, 175])
Rg = rot_matrix(*POSE)
ga = (GB - D) / np.linalg.norm(GB - D)
xh, zh = np.array([1.0, 0, 0]), np.array([0, 0, 1.0])


def uw(az, el):
    az, el = np.radians(az), np.radians(el); return np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])


def unit(v): return v / np.linalg.norm(v)


conc = [(D + 70 * uw(a, 55), uw(a, 55)) for a in (90, -30, 210)]
rgb, r6 = GB - D, HT - D
n4 = unit(np.cross(zh, rgb))          # u4 must be perpendicular to this
n5 = unit(np.cross(xh, rgb))          # u5 must be perpendicular to this
n6 = unit(np.cross(xh, r6))            # practical mode: u6 perpendicular to this (blind to hole tilt)
pushes = [np.array(v, float) for v in ([5,0,0],[-5,0,0],[0,5,0],[0,-5,0],[0,0,5],[0,0,-5])]


def in_plane(n, t):
    a = unit(np.cross(n, [0.3, 0.2, 1.0])); b = np.cross(n, a)
    return np.cos(t) * a + np.sin(t) * b


def solve(wires, loads):
    A = np.zeros((6, 6))
    for i, (p, u) in enumerate(wires):
        A[:3, i] = u; A[3:, i] = np.cross(p - D, u)
    F = sum(f for _, f in loads); M = sum(np.cross(p - D, f) for p, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


best = None
for _ in range(40000):
    u4 = uw(rng.uniform(-180, 180), rng.uniform(5, 85)); u5 = in_plane(n5, rng.uniform(0, 2*np.pi)); u6 = in_plane(n6, rng.uniform(0, 2*np.pi))
    if min(u4[2], u5[2], u6[2]) < 0.05:      # anchors must be above their attachments
        continue
    wires = conc + [(GB, u4), (GB, u5), (HT, u6)]
    b1 = uw(rng.uniform(-180, 180), rng.uniform(-90, -40)); F1 = rng.uniform(5, 60)
    arm = np.array([115.0, rng.uniform(-40, 40), 200.0]); F2 = rng.uniform(0, 60)
    ts = np.linspace(0, 600, 61); pts = GB[None, :] + ts[:, None] * b1[None, :]
    if ((np.hypot(pts[:, 0], pts[:, 1]) < 66) & (pts[:, 2] > -90) & (pts[:, 2] < 160)).any():
        continue
    base = [(COM, np.array([0, 0, -W * 1.0])), (GB, F1 * b1), (arm, np.array([0, 0, -F2]))]
    try:
        cases = [base] + [base + [(D, f)] for f in pushes] + [base + [(TP, Rg @ np.array([0, 5.0, 0]))]]
        m = min(solve(wires, c).min() for c in cases)
    except np.linalg.LinAlgError:
        continue
    if best is None or m > best[0]:
        best = (m, u4, u5, u6, b1, F1, arm, F2, solve(wires, base))

m, u4, u5, u6, b1, F1, arm, F2, t0 = best
el = lambda u: np.degrees(np.arcsin(u[2])); az = lambda u: np.degrees(np.arctan2(u[1], u[0]))
print(f"best worst-case min tension {m:.2f} N (gun 1 kg)")
for name, u in (("W4 (hole)", u4), ("W5 (vertical)", u5), ("W6 (roll)", u6)):
    print(f"  {name:13s} az {az(u):7.1f}  el {el(u):5.1f}")
print(f"  bungee 1 at grip base az {az(b1):.0f} el {el(b1):.0f}, {F1:.1f} N; bungee 2 down from shell arm at {np.round(arm,0)}, {F2:.1f} N")
print("  nominal tensions:", np.round(t0, 1))
# check the Jacobian: length change per degree for each rotation
rows = []
for name, wv in (("hole", xh), ("vertical", zh), ("roll", ga)):
    w = np.radians(1) * wv
    dl = [np.dot(u, np.cross(w, p - D)) for p, u in (conc + [(GB, u4), (GB, u5), (HT, u6)])]
    rows.append(dl)
    print(f"  1 deg about {name:8s}: dL W1..W6 = {np.round(dl, 2)} mm")
