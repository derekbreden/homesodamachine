"""Wave 2 numbers for workspace-as-structure on work-as-datum.

1. Corner-height sensitivity at the scene's true opening pose (dial 30 ->
   parameter -5) vs the dial-65 pose that work-as-datum's pose_geometry.py
   shows when it passes 30 straight to pose_point.
2. The paddle compass: two rollers on the plate on the dot's radius, one foot
   on the room plane under the grip, a centre pin at the plate centre, a fence
   at the foot. Support triangle, load split, tipping margins, what each
   disturbance does, and what tube length does to it.
3. A follower that reads the wall ahead of the puddle: how much runout and
   ovality it removes, single contact vs symmetric pair.

All gun numbers use the scene proxy [Agent]; gun mass and CG are [Unknown],
two candidates are run. Run: python3 wave2_calcs.py
"""
import math
import numpy as np
import geom


def cross2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])

R = geom.R_IN

print("== 1. corner height -> dot, gun fixed in space ==")
for label, dial in (("scene opening pose (dial 30)", 30), ("dial 65 (param 30)", 65)):
    hp = dial - geom.HOLE_OFFSET
    tip = geom.pose_point([0, 0, 0], 45, hp, -15)
    dot = geom.pose_point([0, 0, -geom.CLEAR], 45, hp, -15)
    b = (dot - tip) / np.linalg.norm(dot - tip)
    down = -b[2]
    print(f"  {label}: beam {math.degrees(math.asin(down)):.1f} deg below horizontal; "
          f"corner 1 mm high -> dot {b[0]/down:.2f} mm onto the plate (radial), "
          f"{b[1]/down:.2f} mm along the seam; focus {1/down:.2f} mm; "
          f"corner 1 mm low -> dot 1.00 mm up the wall")

print("\n== 2. paddle compass ==")
P1 = np.array([36.0, 0.0])     # roller on plate, on the dot's radius (toward the dot)
P2 = np.array([-40.0, 0.0])    # roller on plate, same line, far side of centre
for P3x in (-15.0, 10.0, 30.0):
    P3 = np.array([P3x, -250.0])   # foot on the room plane under the grip
    tri = np.array([P1, P2, P3])
    area = 0.5 * abs(cross2(P2 - P1, P3 - P1))
    sides = [np.linalg.norm(P2 - P1), np.linalg.norm(P3 - P2), np.linalg.norm(P1 - P3)]
    rin = area / (sum(sides) / 2)
    print(f"  P3 at ({P3x:.0f}, -250): triangle inradius {rin:.1f} mm "
          f"(work-as-datum A2 ball triangle: 17.5 mm)")
    for cg_label, CG, W in (("CG (-20,-120), 21 N", np.array([-20.0, -120.0]), 21.0),
                            ("CG (-40,-150), 21 N", np.array([-40.0, -150.0]), 21.0)):
        A = np.column_stack([tri, np.ones(3)])
        w = np.linalg.solve(A.T, np.array([CG[0], CG[1], 1.0]))
        loads = w * W
        # distance of CG to each edge (positive inside)
        def edge_dist(a, b, p):
            d = b - a
            return abs(cross2(d, p - a)) / np.linalg.norm(d)
        dP1 = edge_dist(P2, P3, CG)  # moment that lifts P1 turns about P2-P3
        dP2 = edge_dist(P1, P3, CG)
        dP3 = edge_dist(P1, P2, CG)
        print(f"    {cg_label}: loads P1 {loads[0]:.1f} N, P2 {loads[1]:.1f} N, P3 {loads[2]:.1f} N; "
              f"moment to lift P1 {W*dP1/1000:.2f} N*m, P2 {W*dP2/1000:.2f}, P3 {W*dP3/1000:.2f}")

print("  disturbances (P3 at (10,-250), CG (-20,-120), 21 N):")
grip_base = np.array([-0.8, -233.5])
print(f"    trigger push down 15 N at the grip (~(-10,-190)): adds load, lifts nothing")
for up in (5, 10, 20):
    # upward pull at the grip base: moment about P1-P2 line (y=0) vs weight moment
    restoring = 21 * 120 / 1000
    disturbing = up * abs(grip_base[1]) / 1000
    print(f"    cable lifting {up:2d} N at the grip base: {disturbing:.2f} N*m vs weight {restoring:.2f} N*m about the P1-P2 line"
          f" -> {'holds' if disturbing < restoring else 'P3 lifts'}")
print("    the same pulls on work-as-datum A2 (balls at r=35, 10-20 N residual): 0.09-0.35 N*m limit")

print("  tube length -> paddle angle (dot on the P1-P2 line, so it does not move):")
for dl in (0.5, 1.0, 3.2):
    ang = math.degrees(math.atan(dl / 250))
    print(f"    plate {dl:.1f} mm high/low vs the room plane -> roll about the dot's radius {ang:.2f} deg")
dot_x = R
k1 = (dot_x - P2[0]) / (P1[0] - P2[0])
print(f"  dot height = {k1:.2f}*P1 {1-k1:+.2f}*P2 (roller/plate height errors)")
print(f"  roller-centre height 5 mm: a 1 mrad roll about P1-P2 moves the dot {5*1e-3*1000:.0f} um along the seam")

print("\n== 3. follower reading the wall ahead of the puddle ==")
for lead in (10, 25, 40):
    L = math.radians(lead)
    single_runout = 2 * math.sin(L / 2)
    single_oval = 2 * math.sin(L)
    pair_runout = 1 - math.cos(L)
    pair_oval = 1 - math.cos(2 * L)
    print(f"  lead {lead:2d} deg ({R*L:4.1f} mm of arc): residual after following, as a fraction of the error "
          f"without following: runout single {single_runout:.2f} / symmetric pair {pair_runout:.2f}; "
          f"ovality single {single_oval:.2f} / pair {pair_oval:.2f}")
