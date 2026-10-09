"""Wave-2 exchange calculations on one-knob-one-parameter's ideas.

Corrected opening pose (grip 45, hole DIAL 30, vertical -15; geometry.pose_point
applies the scene's 35 deg dial offset). Masses and stiffnesses are assumptions,
labelled. Run: python3 calcs_exchange.py
"""
import sys, os
import numpy as np
import geometry as G
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sketches'))
import svgkit as K

g0 = 9.81
POSE = (45, 30, -15)
R = G.R_IN

print("== 1. Couch Y (tangent) is a yaw knob ==")
# one-knob-one-parameter's table: per 1 deg of vertical-axis angle at the opening pose
per_deg = {"work": 0.54, "travel": -0.54, "wobble-crossing": -0.78}
for s in (0.05, 0.1, 0.3, 0.5, 1.0):
    yaw = np.degrees(s / R)
    print(f"Y off by {s:4.2f} mm -> yaw {yaw:.3f} deg (dot stays on the corner; radial {s*s/2/R*1000:.2f} um) -> "
          + ", ".join(f"{k} {v*yaw:+.3f} deg" for k, v in per_deg.items()))
print("A drawer slide's end stop repeating to ~0.1-0.3 mm [estimate] is a 0.1-0.3 deg yaw scatter the dot camera cannot see.")

print("\n== 2. Vertical-axis angle by translation (circle symmetry) ==")
for phi in (1, 3, 5, 10, 15):
    p = np.radians(phi)
    print(f"phi {phi:2d} deg == move the work {R*np.sin(p):6.2f} mm along the tangent and {R*(1-np.cos(p)):5.3f} mm radially")

print("\n== 3. Closed roll ring passed nose-first along the grip axis (scene proxy) ==")
dot = G.JOINT
gb = G.pose_point(G.GRIP_BASE, *POSE)
g = (gb - dot) / np.linalg.norm(gb - dot)
e1 = np.cross(g, [0, 0, 1]); e1 /= np.linalg.norm(e1); e2 = np.cross(g, e1)
proj = np.array([[np.dot(G.pose_point(q, *POSE) - dot, e1), np.dot(G.pose_point(q, *POSE) - dot, e2)]
                 for pts in K.GUN_PARTS.values() for q in pts])
best = None
for cx in np.linspace(proj[:, 0].min(), proj[:, 0].max(), 90):
    for cy in np.linspace(proj[:, 1].min(), proj[:, 1].max(), 90):
        r = np.max(np.hypot(proj[:, 0] - cx, proj[:, 1] - cy))
        if best is None or r < best:
            best = r
print(f"smallest circle containing the bare proxy gun seen along the grip axis: {2*best:.0f} mm "
      "(add the shell if it goes on first) -> 6816 (80 mm) and 32011 (55 mm) do not pass; ~150 mm bore needed")

print("\n== 4. Gravity torques over the working range (m = gun + shell) ==")
def torques(pose, m):
    gbp = G.pose_point(G.GRIP_BASE, *pose)
    ga = (gbp - dot) / np.linalg.norm(gbp - dot)
    v = np.radians(pose[2]); ha = np.array([np.cos(v), np.sin(v), 0])
    cg = G.pose_point(G.CG_LOCAL, *pose)
    tau = np.cross((cg - dot) / 1000, [0, 0, -m * g0])
    return float(np.dot(tau, ga)), float(np.dot(tau, ha))
for m in (1.0, 2.0):
    hs = [torques((45, h, -15), m)[1] for h in (15, 20, 30, 40, 45)]
    rs = [torques((r, 30, -15), m)[0] for r in (10, 30, 45, 60, 75)]
    print(f"m={m} kg: hole torque over dial 15-45 {min(hs):.2f}-{max(hs):.2f} N*m; grip torque over roll 10-75 {min(rs):.2f}-{max(rs):.2f} N*m")

print("\n== 5. Hole angle as a sine arm on a gauge stack ==")
L = 200.0
for m in (1.0, 2.0):
    for hole in (20, 30, 45):
        th = torques((45, hole, -15), m)[1]
        F = th / (L / 1000 * np.cos(np.radians(hole)))
        print(f"m={m} hole {hole}: ball load on the stack {F:5.1f} N")
step = 0.0001 * 25.4  # smallest increment of an inch 81-piece set
print(f"L = {L:.0f} mm: 0.0001 in step -> {np.degrees(step/L):.4f} deg; a 0.25 um block error -> {np.degrees(0.00025/L)*3600:.2f} arcsec")
for hole in (20, 30, 45):
    print(f"   stack height above a reference 100 mm below the ball at hole 30: hole {hole} -> "
          f"{100 + L*(np.sin(np.radians(hole)) - np.sin(np.radians(30))):.2f} mm")

print("\n== 6. Roll on hinged rings + micrometer lever ==")
lever = 100.0
for m in (1.0, 2.0):
    for roll in (10, 45, 75):
        t = torques((roll, 30, -15), m)[0]
        print(f"m={m} roll {roll}: micrometer tip load {t/(lever/1000):4.1f} N")
print(f"0.01 mm at the micrometer = {np.degrees(0.01/lever):.4f} deg of roll")
# clamp friction needed to lock without the micrometer
for t in (0.9,):
    for mu in (0.2, 0.3):
        print(f"to lock {t} N*m by clamp alone on a 84 mm sleeve, mu {mu}: normal force {t/(mu*0.042):.0f} N")

print("\n== 7. Tilt stiffness: ring pair vs single arc bearing ==")
F_nozzle, lever_dot = 2.0, 300.0   # 2 N change at the nozzle, ~300 mm from the roll element [assumption]
for name, kr, s in (("printed arc on rollers, contacts 70 mm apart", 50.0, 70.0),
                    ("two clamped rings 95 mm apart, 500 N/mm each (printed sleeve)", 500.0, 95.0),
                    ("two clamped rings 95 mm apart, 2000 N/mm each (aluminium)", 2000.0, 95.0)):
    kt = kr * s ** 2 / 2
    dth = F_nozzle * lever_dot / kt
    print(f"{name}: tilt stiffness {kt:.2e} N*mm/rad -> dot moves {dth*lever_dot:.3f} mm for {F_nozzle} N at the nozzle")
