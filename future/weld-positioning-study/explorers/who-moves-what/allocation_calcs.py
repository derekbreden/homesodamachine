"""Small calculations behind the who-moves-what arrangements (wave 1).

All inputs other than the repo tube/cap values and the manual's gun envelope are
labelled estimates. Run: tools/cad-venv/bin/python <this file>
"""
import numpy as np
from geometry import pose_point, pose_dial, world, FEATURES, R_IN, BENCH, RIM, CAPSULES, FIBER_DIR_LOCAL, clearance

print("== 1. Relative yaw by moving the work (tube symmetry), exact")
print("   Gun fixed in the room; station point P fixed. Work centre moves so the seam")
print("   still passes through P with its radius turned by phi -> relative yaw = -phi.")
for phi in (1, 2, 5, 10, 15, 20, 30):
    p = np.radians(phi)
    print(f"   phi {phi:3d} deg: work moves {R_IN*np.sin(p):6.2f} mm along the tangent, {R_IN*(1-np.cos(p)):5.2f} mm toward the station")
print(f"   small-angle rate: {R_IN*np.pi/180:.3f} mm per degree")

print("\n== 2. Protractor (hole-axis arc centred on the dot), gun room-yaw 0, roll 45; h = hole DIAL")
dot = world(FEATURES['dot'], (45, 0, 0))
for h in (0, 15, 30, 45, 60, 65):
    gb = world(FEATURES['grip_base_QBH'], (45, h, 0))
    bb = world(FEATURES['body_back'], (45, h, 0))
    d = gb - dot
    ang = np.degrees(np.arctan2(d[2], d[1]))
    print(f"   hole dial {h:2d}: QBH at y {gb[1]:7.1f} x {gb[0]:6.1f} bench+{gb[2]-BENCH:6.1f}; YZ-distance from dot {np.hypot(d[1], d[2]):6.1f}, "
          f"angle from -Y {180-ang:5.1f} deg; body back bench+{bb[2]-BENCH:6.1f}")

print("\n== 3. Seat (kinematic coupling) holding against a cable pull")
print("   Tipping needs preload P > 2 F L / b  (F cable pull at lever L from seat centre, b ball span)")
for b in (75, 150, 200):
    for F, L in ((5, 100), (10, 150), (10, 250)):
        print(f"   span {b:3d} mm, F {F:2d} N at {L:3d} mm -> P > {2*F*L/b:6.1f} N")
print("   Thorlabs KB75/M magnets: 6.5 lbf = 28.9 N (observed spec); gun+shell weight assumed 15-25 N")

print("\n== 4. Printed recipe block: angle error and dot error before re-zero")
for tol in (0.05, 0.1, 0.2):
    for base in (60, 100):
        a = tol / base
        print(f"   face error {tol:.2f} mm over {base:3d} mm -> {np.degrees(a):.3f} deg -> dot moves {a*250:.3f} mm at 250 mm lever")

print("\n== 5. Fiber exit swing when rolling about the grip axis (exit 35 deg off the axis)")
cone = np.radians(35.0)
for rho in (10, 20, 30, 45, 60, 90):
    r = np.radians(rho)
    swing = 2 * np.degrees(np.arcsin(np.sin(cone) * np.sin(r / 2)))
    print(f"   roll {rho:3d} deg: exit direction swings {swing:5.1f} deg; about {rho*np.cos(cone):4.1f} deg of it is twist about the fiber's own axis")

print("\n== 6. Suspension stiffness (pendulum): lateral k = W / L")
for W in (15, 25):
    for Lw in (0.5, 1.0, 1.5):
        k = W / (Lw * 1000)
        print(f"   weight {W} N on {Lw} m wire: {k:.3f} N/mm -> 1 N side pull moves it {1/k:6.1f} mm")

print("\n== 7. Rim rider: which contact to trust")
print("   Offset phi between follower contact and the dot; error multipliers from geometry.py:")
for phi in (15, 20, 30):
    ph = np.radians(phi)
    print(f"   phi {phi}: eccentricity x{2*np.sin(ph/2):.2f}, ovality x{2*np.sin(ph):.2f}; straddling pair (+/-phi averaged): ecc x{1-np.cos(ph):.2f}, ovality x{1-np.cos(2*ph):.2f}")

print("\n== 8. Tube leaving sideways under a still gun: nozzle tip vs rim (wire tip stays in the corner regardless)")
for dial, lab in ((30, "opening pose, dial 30"), (65, "dial 65 (wave-1 first numbers)")):
  print(f"   {lab}:")
  for clear in (16, 10, 5, 2):
    # standoff scales the nozzle-to-dot distance along the beam; beam elevation at opening pose = 65 deg (grip-axis proxy)
    # nozzle tip height above the dot along a beam ~26 deg from vertical (pose.js 60 deg pitch + 30 deg hole tilt)
    tip = pose_dial((0, 0, 0), 45, dial, -15)
    d = pose_dial((0, 0, -16), 45, dial, -15)
    u = (tip - d) / np.linalg.norm(tip - d)
    tip_c = d + clear * u
    print(f"     standoff {clear:2d} mm: nozzle tip {tip_c[2]-RIM:+5.1f} mm relative to the rim (beam {np.degrees(np.arcsin(u[2])):.0f} deg above horizontal)")

print("\n== 9. Where the tube limits the orientation (dials; gun body excluding nozzle)")
for h in (0, 5, 10, 15, 20):
    row = []
    for r in (0, 30, 45, 60, 75, 90):
        c, w = clearance((r, h, -15))
        row.append(f"{r}:{c:5.1f}{'' if c > 0 else ' ' + w}")
    print(f"   hole dial {h:2d}: " + "  ".join(row))
