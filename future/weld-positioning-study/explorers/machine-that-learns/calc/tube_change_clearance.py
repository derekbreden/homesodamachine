"""How far must the tube move (radially, -X) before the whole gun proxy is outside
its plan footprint, so the tube lifts straight up? Gun = scene proxy at 45/30/-15."""
import math
from svgkit import gun_parts_local
from pose_points import pose_point, R_IN, CAP_TOP

pts = []
for name, loc in gun_parts_local().items():
    for p in loc:
        q = pose_point(p, 45, 30, -15)
        pts.append((q[0] - R_IN, q[1], q[2] - CAP_TOP, name))
# also sample the barrel axis densely
for z in range(0, 119, 2):
    q = pose_point((0, 0, z), 45, 30, -15)
    pts.append((q[0] - R_IN, q[1], q[2] - CAP_TOP, "axis"))
for d in (0, 10, 20, 30, 40, 50, 60, 80):
    cx = -R_IN - d
    worst = min(pts, key=lambda p: math.hypot(p[0] - cx, p[1]))
    r = math.hypot(worst[0] - cx, worst[1])
    print(f"tube moved {d:3d} mm toward -X: closest gun point r={r:5.1f} mm from the tube axis "
          f"({worst[3]}, {worst[2]:.0f} mm above the dot)  {'CLEAR of OD 63.5' if r > 63.5 + 3 else ''}")
for d in (0, 30, 60, 90, 120):
    worst = min(pts, key=lambda p: math.hypot(p[0] + R_IN, p[1] - d))
    r = math.hypot(worst[0] + R_IN, worst[1] - d)
    print(f"tube moved {d:3d} mm toward +Y: closest r={r:5.1f} ({worst[3]})  {'CLEAR' if r > 66.5 else ''}")
