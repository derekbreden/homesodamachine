"""Rough numbers behind the machine-that-learns arrangements.

Every gun position here comes from the scene proxy (pose_points.py), which is
illustrative. Camera numbers use the ELP-USB16MP01-KAF68 on hand (IMX298,
4656 x 3496, 1.12 um pixels, 68 deg diagonal lens) from the purchase ledger.
Everything else is labelled where it is assumed.
"""
import math
from pose_points import pose_point, JOINT, GRIP_BASE, R_IN

OPEN = (45, 30, -15)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def rot_z(p, deg, centre=(0.0, 0.0)):
    a = math.radians(deg)
    x, y = p[0] - centre[0], p[1] - centre[1]
    return (centre[0] + x * math.cos(a) - y * math.sin(a), centre[1] + x * math.sin(a) + y * math.cos(a), p[2])


def rot_axis(p, origin, axis, deg):
    """Rodrigues rotation of point p about a line (origin, unit axis)."""
    a = math.radians(deg)
    k = tuple(x / norm(axis) for x in axis)
    v = sub(p, origin)
    kxv = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
    kdv = sum(x * y for x, y in zip(k, v))
    r = tuple(v[i] * math.cos(a) + kxv[i] * math.sin(a) + k[i] * kdv * (1 - math.cos(a)) for i in range(3))
    return tuple(origin[i] + r[i] for i in range(3))


print("1. Plan angle is a translation (tube symmetry)")
pts = [(0, 0, 0), (0, 0, 118), GRIP_BASE, (0, 17, 253)]
for psi in (-15, 10, 30):
    moved = [rot_z(pose_point(p, 45, 30, psi), -psi) for p in pts]   # undo by turning the tube frame
    base = [pose_point(p, 45, 30, 0) for p in pts]
    d = [sub(m, b) for m, b in zip(moved, base)]
    spread = max(norm(sub(x, d[0])) for x in d)
    print(f"   vertical {psi:+d} deg == gun translated by {tuple(round(x, 2) for x in d[0])} mm "
          f"(spread over points {spread:.1e} mm); |t| = {norm(d[0]):.1f} mm, 2R sin(psi/2) = {2*R_IN*math.sin(math.radians(abs(psi))/2):.1f}")
print("   A 0.1 mm error along the tangent changes the plan angle by", round(math.degrees(0.1 / R_IN), 3), "deg")

print("\n2. Camera at the joint (ELP 16MP, 68 deg diag, IMX298)")
px = 1.12e-3
w_px, h_px = 4656, 3496
sensor_w, sensor_h = w_px * px, h_px * px
diag = math.hypot(sensor_w, sensor_h)
f = (diag / 2) / math.tan(math.radians(34))
print(f"   sensor {sensor_w:.2f} x {sensor_h:.2f} mm, implied focal length {f:.2f} mm")
for D in (60, 100, 150, 250):
    fov_w = sensor_w * D / f
    mmpp = fov_w / w_px
    print(f"   at {D:3d} mm: field {fov_w:5.1f} x {sensor_h*D/f:5.1f} mm, {mmpp*1000:5.1f} um/pixel")
# triangulation of the red dot along the beam
for alpha in (20, 30, 45):
    for D in (100, 150):
        mmpp = sensor_w * D / f / w_px
        lateral = math.sin(math.radians(alpha))
        print(f"   camera {alpha} deg off the beam at {D} mm: 0.1 mm of standoff moves the dot image "
              f"{0.1*lateral/mmpp:.1f} px")

print("\n3. Runout seen at the dot (procedure acceptance limits, not measurements)")
tir_r, tir_f = 0.25, 0.30
print(f"   radial TIR {tir_r} -> dot swings +/-{tir_r/2:.3f} mm across the joint once per rev")
print(f"   face TIR {tir_f} -> cap face moves +/-{tir_f/2:.3f} mm vertically at the weld circle")
for v in (5, 8, 15):
    per = 388.61 / v
    peak_speed = (tir_r / 2) * 2 * math.pi / per
    print(f"   at {v} mm/s: one rev {per:.1f} s; following the radial swing needs {peak_speed*1000:.1f} um/s peak")

print("\n4. Where the grip base (cable exit) goes when the beam direction changes")
dot = JOINT
gb = pose_point(GRIP_BASE, *OPEN)
for name, axis in (("tangent line (work angle)", (0, 1, 0)), ("radial line (hole axis)", (1, 0, 0)),
                   ("grip axis", sub(gb, dot))):
    for deg in (5, 10):
        g2 = rot_axis(gb, dot, axis, deg)
        print(f"   {deg:2d} deg about the {name:28s}: grip base moves {norm(sub(g2, gb)):5.1f} mm")

print("\n5. Rotating about an axis that misses the dot (off-centre angle heads, tilting beds)")
for d in (80, 150, 250, 320):
    print(f"   pivot {d} mm from the dot: 1 deg -> {d*math.radians(1):.2f} mm; 10 deg -> {2*d*math.sin(math.radians(5)):.1f} mm to re-centre")

print("\n6. Arc (goniometer) drive resolution")
for R in (150, 200, 250):
    belt_step = 40 / (200 * 16)  # GT2 20T pulley 40 mm/rev, 1.8 deg, 1/16 microstep
    print(f"   arc radius {R}: GT2 20T at 1/16 step = {belt_step*1000:.1f} um of arc = {math.degrees(belt_step/R)*3600:.1f} arcsec; "
          f"+/-25 deg of arc is {2*R*math.radians(25):.0f} mm long")

print("\n7. Tube change clearance (gun fixed at the opening pose)")
for name, p in (("nozzle tip", (0, 0, 0)), ("nozzle back", (0, 0, 54)), ("body front", (0, 0, 118))):
    q = pose_point(p, *OPEN)
    r = math.hypot(q[0], q[1])
    print(f"   {name:12s} plan radius {r:6.1f} mm, {q[2]-dot[2]:6.1f} mm above the dot")
print("   rim is 6.35 mm above the dot; tube OD radius 63.5 mm")
