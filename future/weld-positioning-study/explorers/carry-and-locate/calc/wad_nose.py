"""Wave 4, on work-as-datum's work-hung suspension (D1): what the nose V has to hold, and whether
gravity seating is enough. Geometry and masses copied from their suspension_calcs.py (not imported):
nose collar on the barrel at local z = 30; base loop 40 mm beyond the grip butt along the grip axis;
third ring at the housing top back; gun + shell 1.6 kg, CoM at local (0, -30, 200) [their estimate].
Constraints: nose = ball joint (3 forces, work); base = X line (bilateral) + Z wire (tension only), room;
third ring = Z wire (tension only), room. Opening pose, dial convention (pose.py).
"""
import numpy as np
from pose import pose_point, JOINT, LOCAL, rot_matrix

POSE = (45, 30, -15)
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
D = JOINT.copy()
NOSE = gp([0, 0, 30]); GB = gp(LOCAL["grip_base"])
ga = (GB - D) / np.linalg.norm(GB - D)
BASE = GB + 40 * ga
RING = gp(LOCAL["housing_top_back"])
COM = gp([0, -30, 200]); W = 1.6 * 9.81
TRIG = gp([0, -40, 175]); R = rot_matrix(*POSE)
bar = gp([0, 0, 31]) - NOSE; bar /= np.linalg.norm(bar)
g = np.array([0, 0, -1.0])
seat_dir = g - np.dot(g, bar) * bar; seat_dir /= np.linalg.norm(seat_dir)   # into the V's bottom
side_dir = np.cross(bar, seat_dir)                                           # across the V
print(f"nose {np.round(NOSE - D, 1)} from the dot ({np.linalg.norm(NOSE - D):.0f} mm); base {np.round(BASE - D,0)}; ring {np.round(RING - D,0)}")


def reactions(loads, ring_share=None):
    """Unknowns: nose force (3, applied BY the loop ON the collar), base X, base Z, ring Z."""
    A = np.zeros((6, 6)); cols = []
    for i, e in enumerate(np.eye(3)):
        A[:3, i] = e; A[3:, i] = np.cross(NOSE - D, e)
    A[:3, 3] = [1, 0, 0]; A[3:, 3] = np.cross(BASE - D, [1, 0, 0])
    A[:3, 4] = [0, 0, 1]; A[3:, 4] = np.cross(BASE - D, [0, 0, 1])
    A[:3, 5] = [0, 0, 1]; A[3:, 5] = np.cross(RING - D, [0, 0, 1])
    F = sum(f for _, f in loads); M = sum(np.cross(p - D, f) for p, f in loads)
    return np.linalg.solve(A, -np.concatenate([F, M]))


def nose_check(x, preload):
    Rn = x[:3]                         # force of the loop on the collar
    seat = -np.dot(Rn, seat_dir) + preload   # collar pressed into the V (gravity + internal preload)
    side = abs(np.dot(Rn, side_dir))
    axial = abs(np.dot(Rn, bar))
    return seat, side, axial


cases = {
    "gravity only": [],
    "stuck-wire drag 5 N, +Y at the dot": [(D, np.array([0, 5.0, 0]))],
    "stuck-wire drag 5 N, -Y at the dot": [(D, np.array([0, -5.0, 0]))],
    "cable 5 N, -Y at the grip butt": [(GB, np.array([0, -5.0, 0]))],
    "cable 5 N, up at the grip butt": [(GB, np.array([0, 0, 5.0]))],
    "hand on trigger 10 N (grip-local +y)": [(TRIG, R @ np.array([0, 10.0, 0]))],
    "wire push 2 N back along the barrel": [(D, 2.0 * bar)],
}
for preload in (0.0, 25.0):
    print(f"\n== internal preload in the loop: {preload:.0f} N ==")
    for name, extra in cases.items():
        x = reactions([(COM, np.array([0, 0, -W]))] + extra)
        seat, side, axial = nose_check(x, preload)
        cap = seat * 1.0          # 90 deg V: sideways capacity ~ seating force (tan 45), groove likewise (assumed 90 deg)
        ok = side < cap and axial < cap and x[4] > 0 and x[5] > 0
        print(f"  {name:40s}: seat {seat:5.1f} N, sideways {side:4.1f}, along barrel {axial:4.1f}; base Z {x[4]:5.1f}, ring {x[5]:5.1f}, base X {x[3]:+5.1f}"
              f"  -> {'holds' if ok else 'CLIMBS / SLACK'}")

# third ring taking more weight: add an upward force at the ring (a balancer on the ring line) and see the nose
print("\n== a constant-force balancer on the third ring takes extra weight ==")
for extra_up in (0, 5, 10):
    x = reactions([(COM, np.array([0, 0, -W])), (RING, np.array([0, 0, extra_up]))])
    seat, side, axial = nose_check(x, 0.0)
    nose_down = -x[2]
    print(f"  +{extra_up:2d} N at the ring: nose vertical load {nose_down:5.1f} N (gravity seat {seat:4.1f} N), base Z {x[4]:5.1f}, ring wire {x[5]:5.1f}")

# what the tube sees
print("\n== moment the nose puts on the plate-borne hub (about the tube's lower rim, crude) ==")
x = reactions([(COM, np.array([0, 0, -W]))])
Fn = -x[:3]    # force of the collar on the loop -> into the hub
r = np.hypot(NOSE[0], NOSE[1])
print(f"  gravity case: nose load {np.round(Fn,1)} N at r {r:.0f} mm from the tube axis -> ~{abs(Fn[2])*r/1000:.2f} N*m (work-as-datum: 0.9-2.5 N*m lifts the tube)")
