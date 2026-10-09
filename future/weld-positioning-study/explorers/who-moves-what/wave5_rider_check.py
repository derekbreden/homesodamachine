"""Wave 5: at the true opening pose, does the rim rider's plate-face tripod (3a) clear
the barrel? Pads: 5/8 in ball transfers, housing ~22 mm tall above the plate face,
radius ~12 mm, at r = 47 / 30 mm; a carriage member straddling the lip at rim + 12 mm.
Gun = capsule proxy at dials 45 / 30 / -15. Scene frame: plate face at CAP_TOP."""
import math
import numpy as np
from geometry import world, CAPSULES, R_IN, RIM, CAP_TOP

POSE = (45, 30, -15)
barrel = []
for name in ("nozzle", "grad_tube", "thin_tube", "coupling"):
    a, b, rad = CAPSULES[name]
    for t in np.linspace(0, 1, 30):
        p = world((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), POSE)
        barrel.append((p, rad))


def clearance(pad_xyz, pad_r):
    return min(np.linalg.norm(p - pad_xyz) - rad - pad_r for p, rad in barrel)


print("== barrel sector (angle about the tube axis, r, height above the plate face)")
for name in ("nozzle", "grad_tube", "thin_tube"):
    a, b, rad = CAPSULES[name]
    for t in (0.0, 1.0):
        p = world((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), POSE)
        print(f"   {name:10s} {t:.0f}: angle {math.degrees(math.atan2(p[1], p[0])):+6.1f} deg, r {math.hypot(p[0], p[1]):5.1f}, z {p[2]-CAP_TOP:+6.1f} mm")
print("\n== clearance of a pad column (plate face to +22 mm) and a lip-straddling member (rim + 12 mm, r 47..70) at each angle")
for ang in (-10, -25, -40, -60, -80, -100, -120, 10, 25, 40):
    th = math.radians(ang)
    col = min(clearance(np.array([47 * math.cos(th), 47 * math.sin(th), CAP_TOP + z]), 12) for z in np.linspace(0, 22, 12))
    mem = min(clearance(np.array([r * math.cos(th), r * math.sin(th), RIM + 12]), 6) for r in np.linspace(47, 70, 12))
    print(f"   angle {ang:+4d}: pad column {col:+6.1f} mm, straddle member {mem:+6.1f} mm")
