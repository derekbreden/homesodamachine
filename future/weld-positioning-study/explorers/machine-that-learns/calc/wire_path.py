"""Numbers for idea F (the wire and the interlock as instruments).

Wire: ER316L 0.030 in (0.762 mm) [Repo], E ~193 GPa, yield ~400-700 MPa (as carry-and-locate used).
Wire approach: the scene's straight wire guide (pose.js WIRE_GUIDE_BACK -> WIRE_TIP) at the opening
pose - an illustrative proxy, not the real bracket. Friction coefficients and cast radii are assumptions.
"""
import math
from pose_points import pose_point, R_IN

d = 0.030 * 25.4
E = 193e3            # N/mm^2
I = math.pi * d ** 4 / 64
EI = E * I

print("1. Where the wire comes from at the opening pose (scene proxy)")
tip = pose_point((0, 0, -16), 45, 30, -15)
back = pose_point((0, -24.7, 87.1), 45, 30, -15)
u = [a - b for a, b in zip(back, tip)]
n = math.sqrt(sum(v * v for v in u))
u = [v / n for v in u]
print(f"   wire direction (dot -> guide) {tuple(round(v, 3) for v in u)}")
print(f"   angle above the cap face {math.degrees(math.asin(u[2])):.0f} deg; angle from the wall "
      f"{math.degrees(math.asin(-u[0])):.0f} deg (wall normal is -X); plan azimuth {math.degrees(math.atan2(u[1], u[0])):.0f} deg")
beam = [a - b for a, b in zip(pose_point((0, 0, 0), 45, 30, -15), tip)]
nb = math.sqrt(sum(v * v for v in beam))
print(f"   angle between wire and beam {math.degrees(math.acos(sum(a*b for a, b in zip(u, beam))/nb)):.0f} deg")

print("\n2. Conduit drag: capstan ratio exp(mu * total bend angle)")
for mu in (0.15, 0.25):
    for name, deg in (("fixed short conduit, one 60 deg bend", 60), ("fixed conduit, 90 deg", 90),
                      ("hanging 3 m conduit, ~1.5 turns accumulated", 540)):
        print(f"   mu {mu}: {name:45s} -> x{math.exp(mu*math.radians(deg)):.2f}")

print("\n3. Cast: tip offset of a curved stick-out, L^2 / 2R")
for R in (300, 600, 1000):
    print("   cast radius %4d mm: " % R + ", ".join(f"L={L} mm -> {L*L/(2*R):.2f} mm" for L in (8, 12, 16)))

print("\n4. The stick-out as a spring and as a touch probe")
for L in (8, 12, 16):
    k = 3 * EI / L ** 3
    for sy in (400.0, 700.0):
        Mp = sy * d ** 3 / 6
        print(f"   L={L} mm: lateral tip stiffness {k:5.1f} N/mm; plastic at {Mp/L:4.1f} N (yield {sy:.0f} MPa) "
              f"-> tip moves {Mp/L/k:.2f} mm before it yields")
print("   one camera pixel (23 um at 100 mm; 10-16 um for a PTZ at 0.6-1 m) of tip deflection at L=12 mm "
      f"is {3*EI/12**3*0.023:.2f} N of contact force")

print("\n5. Touch-off by moving the stage vs jogging the feeder")
for v, name in ((0.1, "stage at 0.1 mm/s"), (0.5, "stage at 0.5 mm/s"), (5.0, "feeder jog 5 mm/s (manual p.13 test speed)"),
                (12.0, "feeder at 12 mm/s (rig's recorded wire speed)")):
    over = v / 30.0 + v * 0.06
    print(f"   {name:44s}: overtravel before a 30 fps camera with 60 ms latency reacts ~{over:.3f} mm")
