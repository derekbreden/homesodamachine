"""Follow-up to wave2_lid_checks.py: slide-yaw limit for the fixed lid hinge, whether the
hole-15/yaw+15 failures are infeasible start poses, and the minimum wire-to-lip clearance
during the first 5 degrees of lid opening. Uses sequence-of-use's proxy read-only."""
import math
from wave2_lid_checks import P, PTS, TAGS, HINGE, U, posed_points, sweep

def start_ok(pts):
    return not any(P.collides_tube(q, margin=0.0) for q, t in zip(pts, TAGS) if t != 'wire' or True)

def wire_clearance(pts, upto=5.0):
    """min distance of wire points from the wall/lip solid during 0..upto deg (approx, 2D rho-z)."""
    best = 1e9
    d = 0.0
    while d <= upto:
        Q = [P.rot_about_axis(p, HINGE, U, math.radians(d)) for p in pts]
        for q, t in zip(Q, TAGS):
            if t != 'wire':
                continue
            r = math.hypot(q[0], q[1]); z = q[2]
            if z > P.RIM:
                dd = math.hypot(max(P.R_IN - r, 0, r - P.R_OUT), z - P.RIM)
            else:
                dd = min(abs(r - P.R_IN), abs(r - P.R_OUT)) if not (P.R_IN < r < P.R_OUT) else 0.0
                if r < P.R_IN and z < P.CAP_TOP:
                    dd = 0.0
            # ignore the tip's own contact with the corner at d = 0
            if d > 0.2 and dd < best:
                best = dd
        d += 0.1
    return best

print("== slide-yaw limit at grip 45 / hole dial 30 (hinge fixed || room Y)")
for yaw in (-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20):
    pts = posed_points(45, 30, yaw, "slide")
    r = sweep(pts, 1)
    print(f"   yaw {yaw:+3d} by slide: {r[0]:7s} {r[1:]}  min wire-to-lip clearance in first 5 deg: {wire_clearance(pts):.2f} mm")
print("\n== same, yaw by rotation about the vertical through the dot")
for yaw in (-30, -15, 0, 15, 30):
    pts = posed_points(45, 30, yaw, "rotate")
    r = sweep(pts, 1)
    print(f"   yaw {yaw:+3d} by rotate: {r[0]:7s} {r[1:]}  min wire clearance first 5 deg: {wire_clearance(pts):.2f} mm")
print("\n== are the hole-dial-15 / yaw+15 cases feasible poses at all (before any lid motion)?")
for mode in ("rotate", "slide"):
    for roll in (30, 45):
        pts = posed_points(roll, 15, 15, mode)
        bad = [t for q, t in zip(pts, TAGS) if P.collides_tube(q, margin=0.0)]
        print(f"   {mode} roll {roll} hole 15 yaw +15: points inside tube at rest: {len(bad)} ({set(bad)})")
