"""Wave-4 numbers: the hand stays the actuator, a work-referenced cup gives the dot.

Three balls on the shell sit in a concave spherical band (the cup) centred on the
dot; the band is carried by the plate hanger (port seat + wheels, see
ideas/work-hung-suspension.md). A grip-base boss drops into a fork. The hand
holds roll about Derek's grip axis, presses, and pulls the trigger.

Scene opening pose (grip 45, hole dial 30, vertical -15), dial offset applied.
[Agent] proxy, [Est] estimate, [Unknown] unmeasured. Run: python3 guided_hand_calcs.py
"""
import math
import numpy as np
from pose_geometry import pose_point, GRIP_BASE, R_IN, R_OUT, RECESS

POSE = (45, 30, -15)
P = lambda p: np.array(pose_point(p, *POSE))
dot = P((0, 0, -16))
bar = P((0, 0, 1)) - P((0, 0, 0))
bar /= np.linalg.norm(bar)                       # barrel direction, away from the dot
gb = P(GRIP_BASE)
grip_axis = (gb - dot) / np.linalg.norm(gb - dot)

print("=== the cup: three balls on the shell, a spherical band centred on the dot ===")
# a basis perpendicular to the barrel; e1 = steepest-down in that plane
g = np.array([0, 0, -1.0])
e1 = g - np.dot(g, bar) * bar
e1 /= np.linalg.norm(e1)
e2 = np.cross(bar, e1)


def lip_clear(p, rb):
    """clearance of a ball (centre p, radius rb) to the lip annulus and the plate face"""
    r = math.hypot(p[0], p[1])
    out = []
    # plate face z=0 inside the bore
    if r < R_IN:
        out.append(p[2] - rb)
    # lip: annulus R_IN..R_OUT, z 0..RECESS; nearest point
    rn = min(max(r, R_IN), R_OUT)
    zn = min(max(p[2], 0.0), RECESS)
    out.append(math.hypot(r - rn, p[2] - zn) - rb if not (R_IN <= r <= R_OUT and 0 <= p[2] <= RECESS) else -rb)
    return min(out)


for Rs, alpha in ((40, 30), (45, 35), (50, 35)):
    rho = Rs * math.sin(math.radians(alpha))     # ball-centre circle radius around the barrel
    ax = Rs * math.cos(math.radians(alpha))      # along the barrel from the dot
    rb = 4.0                                      # 8 mm balls [Est]
    worst = None
    for phase in (0, 60):                        # rotate the triangle of balls
        pts = []
        for k in range(3):
            th = math.radians(phase + 120 * k)
            c = dot + ax * bar + rho * (math.cos(th) * e1 + math.sin(th) * e2)
            pts.append(c)
        cl = min(lip_clear(c, rb) for c in pts)
        zs = [round(float(c[2]), 1) for c in pts]
        if worst is None or cl > worst[0]:
            worst = (cl, phase, zs, [round(float(math.hypot(c[0], c[1])), 1) for c in pts])
    cap = math.tan(math.radians(alpha))
    print(f"  cup radius {Rs} mm, contact angle {alpha} deg: balls on a {2*rho:.0f} mm circle, {ax:.0f} mm up the barrel;"
          f" best phase {worst[1]} deg -> ball heights {worst[2]}, radii {worst[3]}, min clearance to lip/plate {worst[0]:.1f} mm;"
          f" lateral capacity {cap:.2f} x preload")

print("\n=== what the hand holds ===")
beam_back = -np.array(pose_point((0, 0, -16), *POSE)) + np.array(pose_point((0, 0, 0), *POSE))
beam_back /= np.linalg.norm(beam_back)
ang = math.degrees(math.acos(np.dot(beam_back, grip_axis)))
print(f"  beam is {ang:.0f} deg off the grip axis: 1 deg of hand roll turns the beam {math.sin(math.radians(ang)):.2f} deg; the dot stays")
for wander in (1, 2, 3, 5):
    print(f"    roll wander +/-{wander} deg -> beam direction +/-{wander*math.sin(math.radians(ang)):.1f} deg")
# gravity roll moment about the grip axis (CoM guesses) and what a balancer at the CoM removes
W = 1.6 * 9.81
for label, cg_local in (("CoM at housing centre", (0, 0, 185)), ("CoM toward the grip", (0, -30, 200))):
    cg = P(cg_local)
    v = cg - dot
    off = np.linalg.norm(v - np.dot(v, grip_axis) * grip_axis)
    # horizontal component of the lever for gravity about an inclined axis
    m = abs(np.dot(np.cross(v, W * g), grip_axis)) / 1000   # N*mm -> N*m
    print(f"  {label}: {off:.0f} mm off the grip axis; gravity roll moment {m:.2f} N*m unless a balancer hangs at the CoM")

print("\n=== preload the cup needs ===")
for alpha in (30, 35):
    for F in (3.0, 5.0):
        print(f"  contact angle {alpha} deg, {F} N stuck-wire drag at the dot (passes through the cup's centre): "
              f"preload >= {F/math.tan(math.radians(alpha)):.1f} N along the barrel")
print("  hand tremor 8-12 Hz, ~0.1-0.5 mm at the hand [Est]; against the cup it becomes force ripple of"
      " ~0.2-1 N/mm x that = 0.02-0.5 N, well inside a 7-15 N preload")

print("\n=== the tail fork ===")
L = np.linalg.norm(gb - dot)
print(f"  grip base {L:.0f} mm from the dot at ({gb[0]:.0f},{gb[1]:.0f},{gb[2]:.0f})")
for d in (0.125, 1.0, 3.2):
    print(f"  corner moves {d} mm, fork fixed in the room: gun angles change {math.degrees(d/L):.2f} deg; dot stays at the cup centre")

print("\n=== the loose tube under a hand push taken entirely by the cup (bound) ===")
b = -bar  # push direction along the barrel toward the dot
h = 30.0 + 146.05      # cup ~30 mm above the plate face; nest seat 146 mm below it [Repo geometry]
for m_v in (1.40, 2.01):
    for F in (5.0, 10.0, 15.0):
        horiz = F * math.hypot(b[0], b[1])
        vert = -F * b[2]
        tip = horiz * h / 1000
        restore = (m_v * 9.81 + 8.0 + vert) * R_OUT / 1000   # vessel + ~8 N nose share + push's vertical part
        print(f"  vessel {m_v} kg, push {F:>4} N: tipping {tip:.2f} N*m vs restoring ~{restore:.2f} N*m "
              f"-> {'holds' if tip < restore else 'rim lifts'}")
print("  (the tail fork shares the push in practice; this is the case where the hand pushes straight down the barrel)")
