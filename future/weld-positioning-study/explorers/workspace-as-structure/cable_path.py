"""Wave 3: the umbilical as a fixed-shape structure on the welding cart.

The umbilical leaves the grip butt; the scene models it continuing along the
grip axis (dot -> cable exit). From there: a short straight lead to a clamp,
then one bend at radius R (>= 350 mm while emitting [Manual]) in the vertical
plane of the grip axis, turning it from its exit elevation to straight down.

Frame: tube axis at origin, dot at (R_in, 0, 0) (plate face = 0). Heights on
the cart assume the weld module stands on the Weldpro's upper tray; tray
height is [assumed] (listing gives only 30.7 in overall).

Run: python3 cable_path.py
"""
import math
import numpy as np
import geom

LEAD = 80.0          # straight from the cable exit to the clamp on the module [proposal]
TRAY_Z = 740.0       # upper tray above floor [assumed]
MODULE_Z = 12.0      # module plate on the tray [proposal]
DOT_ABOVE_FEET = 238.4 - 6.35   # rotator feet to dot [Repo]


def path(roll, dial, vert, R):
    hp = dial - geom.HOLE_OFFSET
    dot = geom.JOINT
    gb = geom.pose_point(geom.GRIP_BASE, roll, hp, vert)
    d = (gb - dot) / np.linalg.norm(gb - dot)
    elev = math.asin(d[2])
    heading = math.atan2(d[1], d[0])
    start = gb + d * LEAD
    # bend in the vertical plane of the heading: from elev down to -90 deg
    horiz = R * (math.sin(elev) + 1.0)
    apex_rise = R * (1 - math.cos(elev)) if elev > 0 else 0.0
    drop_xy = start[:2] + horiz * np.array([math.cos(heading), math.sin(heading)])
    arc_len = R * (elev + math.pi / 2)
    return dict(gb=gb - dot, elev=math.degrees(elev), heading=math.degrees(heading),
                start=start - dot, apex=(start[2] - dot[2]) + apex_rise,
                drop_xy=drop_xy, horiz_from_dot=np.linalg.norm(drop_xy - dot[:2]),
                arc=arc_len)


if __name__ == "__main__":
    for pose in ((45, 30, -15), (45, 10, -15), (45, 50, -15), (45, 30, 0)):
        for R in (350.0, 400.0):
            p = path(*pose, R)
            floor_dot = TRAY_Z + MODULE_Z + DOT_ABOVE_FEET
            print(f"pose {pose} R {R:.0f}: cable exit {p['elev']:.0f} deg up, heading {p['heading']:.0f} deg; "
                  f"apex {p['apex']:.0f} mm above the dot ({floor_dot + p['apex']:.0f} above floor); "
                  f"vertical drop at tube-frame ({p['drop_xy'][0]:.0f}, {p['drop_xy'][1]:.0f}) = "
                  f"{p['horiz_from_dot']:.0f} mm from the dot in plan; arc length {p['arc']:.0f} mm")
    floor_dot = TRAY_Z + MODULE_Z + DOT_ABOVE_FEET
    print(f"\ndot above floor with the rotator on the upper tray: ~{floor_dot:.0f} mm "
          f"(rim ~{floor_dot + 6.35:.0f}); cart overall 40.5 x 18.2 x 30.7 in [Obs]")
    # umbilical budget, opening pose, R 375
    p = path(45, 30, -15, 375.0)
    drop_len = floor_dot + p['apex'] - 450.0   # down to a unit port ~450 mm above floor [assumed]
    used = LEAD + p['arc'] + drop_len + 300.0   # + ~300 mm across to the port [assumed]
    print(f"umbilical used from grip to unit at R 375: ~{used:.0f} mm of 5000; stored ~{5000-used:.0f} mm")
    print(f"one 180 deg turn at R 350 uses {math.pi*350:.0f} mm and spans {700} mm")
