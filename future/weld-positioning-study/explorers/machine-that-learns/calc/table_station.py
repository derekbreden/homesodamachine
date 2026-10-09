"""Numbers for idea E, Derek's table opening as a motorised, observed station.

Frame: mm relative to the dot (scene frame, +Z up, dot on +X of the tube, tangent +/-Y).
Rim flush with the table top => table top at z = +6.35. Gun = scene proxy (dial values,
pose_points.py subtracts the 35 deg hole offset). Masses and CoM are assumptions:
gun + shell 2.0 kg at local (0, -25, 190) ('toward grip', carry-and-locate's case);
roll/tilt head hardware 1.0 kg at its own location (stated per case).
"""
import math
from pose_points import pose_point, R_IN, GRIP_BASE

G = 9.81
TABLE_Z = 6.35
TUBE_AXIS = (-R_IN, 0.0)


def rel(p):
    return (p[0] - R_IN, p[1], p[2] - (6 * 25.4 - 6.35))


def com_at(roll, hole):
    return rel(pose_point((0, -25, 190), roll, hole, -15))


def ga_at(roll, hole):
    g = rel(pose_point(GRIP_BASE, roll, hole, -15))
    n = math.sqrt(sum(v * v for v in g))
    return tuple(v / n for v in g)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dotp(a, b):
    return sum(x * y for x, y in zip(a, b))


print("1. Where the gun's weight sits relative to the opening (opening pose 45/30/-15, rim flush)")
c = com_at(45, 30)
print(f"   gun CoM {tuple(round(v) for v in c)} from the dot; {c[2]-TABLE_Z:.0f} mm above the table; "
      f"{math.hypot(c[0]-TUBE_AXIS[0], c[1]):.0f} mm from the tube axis in plan")
for d_open in (150, 160):
    print(f"   opening D{d_open}: edge {d_open/2:.0f} mm from the tube axis -> a beam along X at y = -{d_open/2+30:.0f} "
          f"clears the edge by 30 mm")

print("\n2. Gravity moment on the gun-side stage nearest the gun, over roll 30-60, hole dial 20-40, vertical fixed")
cases = {
    "B as drawn: Y carriage at (40,-330,420)": ((40, -330, 420), (40, -245, 150)),
    "table: X carriage on a beam at y=-190, z=+30": ((-90, -190, 30), (-60, -230, 110)),
    "table: X carriage on a beam at y=-110, z=+30": ((-90, -110, 30), (-60, -200, 110)),
}
for name, (car, head) in cases.items():
    ms = []
    for roll in (30, 45, 60):
        for hole in (20, 30, 40):
            cg = com_at(roll, hole)
            m1 = cross(tuple((a - b) / 1000 for a, b in zip(cg, car)), (0, 0, -2.0 * G))
            m2 = cross(tuple((a - b) / 1000 for a, b in zip(head, car)), (0, 0, -1.0 * G))
            m = tuple(a + b for a, b in zip(m1, m2))
            ms.append(math.sqrt(dotp(m, m)))
    dist = math.sqrt(sum(v * v for v in car))
    print(f"   {name:45s}: {dist:4.0f} mm from the dot; moment {min(ms):.1f} .. {max(ms):.1f} N·m")

print("\n3. Gravity torque about the grip axis (roll drive), gun + shell 2 kg, CoM local (0,-25,190)")
for rolls, holes in (((20, 45, 70), (5, 30, 55)), ((30, 45, 60), (20, 30, 40)), ((35, 45, 55), (25, 30, 35))):
    vals = []
    for roll in rolls:
        for hole in holes:
            cg = com_at(roll, hole)
            m = cross(tuple(v / 1000 for v in cg), (0, 0, -2.0 * G))
            vals.append(dotp(m, ga_at(roll, hole)))
    print(f"   roll {rolls[0]}-{rolls[-1]}, hole dial {holes[0]}-{holes[-1]}: {min(vals):+.2f} .. {max(vals):+.2f} N·m"
          f"{'   one-signed' if min(vals) * max(vals) > 0 else '   CHANGES SIGN'}")

print("\n4. Stylus in the annular gap between tube OD and the opening")
for d_open in (150, 160):
    print(f"   opening D{d_open}: radial gap {d_open/2 - 63.5:.1f} mm; stylus tip 15 mm below the table top "
          f"(9 mm below the joint), at the dot's own angle (+X)")

print("\n5. Seeing into the recess from the table plane")
print(f"   across the bore: the near rim is 124 mm from the dot and 6.35 mm up -> slope >= "
      f"{math.degrees(math.atan(6.35/124)):.1f} deg")
for D, H in ((600, 250), (1000, 400), (1200, 300)):
    print(f"   PTZ at {D} mm, {H} mm above the table, looking across the bore: slope "
          f"{math.degrees(math.atan((H+6.35)/D)):.0f} deg; ")
# PTZ resolution estimate: 1/2.8 in 16:9 sensor ~5.4 mm wide, 3840 px; 20x zoom ~ 4.4-88 mm focal (assumed)
for D in (600, 1000, 1500):
    fov = 5.4 * D / 88
    print(f"   20x PTZ at full zoom (f ~88 mm assumed), {D} mm away: field {fov:.0f} mm wide, {fov/3840*1000:.0f} um/px")

print("\n6. Z shelf travel per tube (tube cut tolerance +/-3.2 mm, OnlineMetals) and load drop 70 mm")
print(f"   stroke >= {70 + 2*3.2:.0f} mm; Tr8x2 at 2 mm/rev, NEMA 17 at 300 rpm: load drop in {70/2/300*60:.0f} s")
print("   1 mm of corner height at the opening pose moves the dot 0.64 mm across the seam (workspace-as-structure)")
