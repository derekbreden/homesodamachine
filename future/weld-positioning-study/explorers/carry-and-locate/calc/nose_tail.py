"""Wave 4 combination (idea F, nose on the work, tail on a table):
nose = work-as-datum's work-hung V-loop ball joint (barrel z = 30, 46 mm from the dot), preloaded inside the loop;
tail = a two-ball switchable-magnet shoe on a horizontal room plate at the base-loop position
(grip base + 40 mm along the grip axis), balls 60 mm apart across the nose-tail line;
float = balancer near the CoM, biased so both tail balls stay loaded.
Plate height and cross-tilt are two screws; the tail's slide on the plate is locked by the magnet.
Opening pose, dial convention (pose.py). Masses are estimates (1.6 kg gun + shell, work-as-datum's).
"""
import numpy as np
from pose import pose_point, JOINT, LOCAL, rot_matrix

POSE = (45, 30, -15)
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
D = JOINT.copy()
N = gp([0, 0, 30]); GB = gp(LOCAL["grip_base"])
ga = (GB - D) / np.linalg.norm(GB - D)
T = GB + 40 * ga
nt = (T - N); L = np.linalg.norm(nt); nt /= L
across = np.cross([0, 0, 1.0], nt); across /= np.linalg.norm(across)   # horizontal, perpendicular to N-T
B1, B2 = T + 30 * across, T - 30 * across
hole_ax = np.array([-1.0, 0, 0]); vert_ax = np.array([0, 0, 1.0])
print(f"nose {np.round(N - D,1)} from dot, tail {np.round(T - D,0)}, nose-tail {L:.0f} mm, angle to grip axis "
      f"{np.degrees(np.arccos(abs(np.dot(nt, ga)))):.1f} deg")


def rot_for(dh1, dh2, ds):
    """Rotation vector about the nose giving ball height changes dh1, dh2 and a horizontal tail slide ds
    (perpendicular to N-T in plan). Solve 3 linear equations for w."""
    rows, rhs = [], []
    for B, dh in ((B1, dh1), (B2, dh2)):
        r = B - N
        rows.append(np.cross(r, [0, 0, 1.0]))   # (w x r).z = w . (r x z)
        rhs.append(dh)
    r = T - N
    rows.append(np.cross(r, across)); rhs.append(ds)
    return np.linalg.solve(np.array(rows), np.array(rhs))


def describe(w, label):
    ang = np.degrees(np.linalg.norm(w))
    dd = np.cross(w, D - N)
    comps = {"grip": np.dot(w, ga), "hole": np.dot(w, hole_ax), "vertical": np.dot(w, vert_ax)}
    print(f"  {label:32s}: turns {ang:.3f} deg (grip {np.degrees(comps['grip']):+.3f}, hole {np.degrees(comps['hole']):+.3f}, "
          f"vertical {np.degrees(comps['vertical']):+.3f}); dot moves {np.round(dd, 3)} mm")


print("== what each tail control does (per 1 mm) ==")
describe(rot_for(1, 1, 0), "plate up 1 mm (both balls)")
describe(rot_for(1, -1, 0), "plate cross-tilt +/-1 mm")
describe(rot_for(0, 0, 1), "tail slid 1 mm across")

print("\n== tube-length error: the nose rises d with the plate; the balls stay on the plate; the tail's across-slide stays at its stop ==")
for d in (1.0, 3.2):
    # gun motion = translation d*z at the nose + rotation w about the nose; constraints:
    # ball heights unchanged, tail across position unchanged
    rows = [np.cross(B1 - N, [0, 0, 1.0]), np.cross(B2 - N, [0, 0, 1.0]), np.cross(T - N, across)]
    rhs = [-d, -d, -d * np.dot([0, 0, 1.0], across)]
    w = np.linalg.solve(np.array(rows), np.array(rhs))
    err = np.cross(w, D - N)
    print(f"  {d} mm: gun turns {np.degrees(np.linalg.norm(w)):.2f} deg (hole {np.degrees(np.dot(w, hole_ax)):+.2f}); "
          f"dot off the moved corner by {np.round(err, 2)} mm = {np.linalg.norm(err):.2f} mm")

print("\n== loads: float at 90 % near the CoM, nose preloaded 25 N inside its loop ==")
W = 1.6 * 9.81; COM = gp([0, -30, 200]); TRIG = gp([0, -40, 175]); R = rot_matrix(*POSE)


def solve(loads):
    """Unknowns: nose force (3), ball normals n1, n2 (vertical), tail friction (1, along 'across').
    Locked state: the tail's in-plane friction also takes a component along N-T (plan) - folded into the nose."""
    A = np.zeros((6, 6))
    for i, e in enumerate(np.eye(3)):
        A[:3, i] = e; A[3:, i] = np.cross(N - D, e)
    A[:3, 3] = [0, 0, 1]; A[3:, 3] = np.cross(B1 - D, [0, 0, 1])
    A[:3, 4] = [0, 0, 1]; A[3:, 4] = np.cross(B2 - D, [0, 0, 1])
    A[:3, 5] = across; A[3:, 5] = np.cross(T - D, across)
    F = sum(f for _, f in loads); M = sum(np.cross(p - D, f) for p, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


cases = {
    "gravity + float only": [],
    "stuck-wire drag 5 N +Y at the dot": [(D, np.array([0, 5.0, 0]))],
    "stuck-wire drag 5 N -Y at the dot": [(D, np.array([0, -5.0, 0]))],
    "cable residual 2 N up at the butt": [(GB, np.array([0, 0, 2.0]))],
    "cable residual 2 N -Y at the butt": [(GB, np.array([0, -2.0, 0]))],
    "hand on trigger 10 N": [(TRIG, R @ np.array([0, 10.0, 0]))],
}
for f_float in (0.9, 0.8):
    print(f"  float carries {f_float:.0%} at the CoM:")
    for name, extra in cases.items():
        x = solve([(COM, np.array([0, 0, -W])), (COM, np.array([0, 0, f_float * W]))] + extra)
        print(f"    {name:36s}: nose {np.round(-x[:3],1)} N, balls {x[3]:5.1f} / {x[4]:5.1f} N, tail friction {x[5]:+5.1f} N"
              f"{'   <- a ball lifts' if min(x[3], x[4]) < 0 else ''}")

print("\n== room-plate motion reaching the dot (lever nose->dot / nose->tail) ==")
print(f"  {np.linalg.norm(D - N):.0f} / {L:.0f} = {np.linalg.norm(D - N)/L:.3f} of the tail's motion")

print("\n== unlocked state: where to hook the float so both tail balls stay seated (no magnet) ==")
rng = np.random.default_rng(4)
mild = [[], [(GB, np.array([0, 0, 1.0]))], [(GB, np.array([0, -1.0, 0]))], [(GB, np.array([0, 1.0, 0]))]]
best = None
for _ in range(20000):
    e = rng.uniform(-60, 60, 3); f = rng.uniform(0.75, 0.97)
    att = COM + R @ e
    m = 1e9
    for extra in mild:
        x = solve([(COM, np.array([0, 0, -W])), (att, np.array([0, 0, f * W]))] + extra)
        m = min(m, x[3], x[4])
    if best is None or m > best[0]:
        best = (m, e, f)
m, e, f = best
x = solve([(COM, np.array([0, 0, -W])), (COM + R @ e, np.array([0, 0, f * W]))])
print(f"  float {f:.0%} hooked at CoM + {np.round(e,0)} mm (gun frame): balls {x[3]:.1f} / {x[4]:.1f} N, nose {np.round(-x[:3],1)} N;"
      f" worst ball with 1 N cable pushes {m:.1f} N")
