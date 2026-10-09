"""Wave 3: tilting the work axis. The recipe (Derek's three dials) fixes the gun
relative to the joint; tilting the work rotates BOTH about the dot, so only their
relation to gravity changes. This computes, for tilts of the tube axis about the
station's tangent line (Y through the dot) and about its radial line (X through the
dot), where the beam, the fillet bisector, the gun's own plane, the cable exit and the
tube axis end up relative to gravity. Plus: lift-off straight along the beam (vendored
proxy point cloud), the existing rotator's tipping margin, the float condition at the
second closure, argon spill from the recess, and a Bond-number estimate.

Poses are the scene's dials (grip, hole dial, vertical). Opening pose 45 / 30 / -15.
Run: tools/cad-venv/bin/python tilt_calcs.py
"""
import math
import numpy as np
from geometry import pose_dial, world, FEATURES, R_IN, R_OUT, RIM, CAP_TOP, FIBER_DIR_LOCAL, CAPSULES
import vendored_sou_proxy as V

DOT = np.array([R_IN, 0.0, CAP_TOP])
RECIPE = (45, 30, -15)


def Ry(t):
    c, s = math.cos(math.radians(t)), math.sin(math.radians(t))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rx(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def tilt(tau, alpha=0.0):
    """Work tilt: about X (radial) by alpha, then about Y (tangent) by tau, both through the dot.
    Positive tau tips the tube's top toward +X (toward the station side)."""
    return Ry(tau) @ Rx(alpha)


def unit(v):
    return v / np.linalg.norm(v)


def gun_dirs(recipe=RECIPE):
    dot = world(FEATURES['dot'], recipe)
    beam = unit(np.array(pose_dial((0, 0, 0), *recipe)) - dot)  # dot -> nozzle (up the beam)
    side = unit(np.array(pose_dial((1, 0, 0), *recipe)) - np.array(pose_dial((0, 0, 0), *recipe)))  # pistol side normal
    gb = world(FEATURES['grip_base_QBH'], recipe)
    grip_axis = unit(gb - dot)
    gb2 = world((FEATURES['grip_base_QBH'][0] + 100 * FIBER_DIR_LOCAL[1], FEATURES['grip_base_QBH'][1] + 100 * FIBER_DIR_LOCAL[2]), recipe)
    fiber = unit(gb2 - gb)
    com = world((0.0, 185.5), recipe) - dot
    return beam, side, grip_axis, fiber, com


def ang_from_vertical(v):
    return math.degrees(math.acos(abs(v[2]) / np.linalg.norm(v))) if v[2] >= 0 else 180 - math.degrees(math.acos(abs(v[2]) / np.linalg.norm(v)))


if __name__ == "__main__":
    beam, side, g, fiber, com = gun_dirs()
    bis = unit(np.array([-1.0, 0, 1.0]))    # fillet bisector at the station, tube frame
    axis = np.array([0, 0, 1.0])            # tube axis (toward the open, working end)
    seam = np.array([0, 1.0, 0])            # seam tangent at the station
    print("== tube frame (upright), recipe 45 / 30 / -15")
    print(f"   beam (dot->nozzle) {np.round(beam,3)}, {ang_from_vertical(beam):.1f} deg from vertical")
    tau_star = math.degrees(math.atan2(-beam[0], beam[2]))
    print(f"   tilt about the station tangent that puts the beam in the vertical tangent plane: tau* = {tau_star:.1f} deg")
    print("\n== tilt about the station tangent (Y through the dot); + tips the tube top toward the station")
    print("   tau | tube axis from vert | fillet bisector from vert (0 = 1F flat, 45 = 2F) | beam from vert | beam out of tangent plane | pistol side vs +-X | grip-axis elev | fiber dir (room)")
    for tau in (0, 10, 20, 30, round(tau_star, 1), 40, 45, 60, 75, 90):
        R = tilt(tau)
        b, s, gg, f = R @ beam, R @ side, R @ g, R @ fiber
        print(f"   {tau:5.1f} | {ang_from_vertical(R @ axis):5.1f} | {ang_from_vertical(R @ bis):5.1f} | {ang_from_vertical(b):5.1f} | {math.degrees(math.asin(b[0])):+6.1f} | "
              f"{math.degrees(math.acos(min(1, abs(s[0])))):5.1f} | {math.degrees(math.asin(gg[2])):5.1f} | {np.round(f,2)}")
    print("\n   combined with a tilt about the station radial (X through the dot): alpha slopes the seam at the station")
    for tau, alpha in ((tau_star, 0), (tau_star, -15), (tau_star, -33), (0, -33)):
        R = tilt(tau, alpha)
        b = R @ beam
        print(f"   tau {tau:5.1f}, alpha {alpha:+4.0f}: seam slope {math.degrees(math.asin((R @ seam)[2])):+5.1f} deg, beam {ang_from_vertical(b):5.1f} deg from vertical, "
              f"fillet bisector {ang_from_vertical(R @ bis):5.1f} deg from vertical")

    print("\n== lift-off by a straight retreat (vendored proxy point cloud incl. its straight wire; tube frame)")
    PTS, TAGS = V.proxy_points()
    P0 = [np.array(pose_dial(p, *RECIPE)) for p in PTS]
    wire_dir = unit(P0[30] - P0[0])
    Rs = tilt(tau_star)
    up_in_tube = Rs.T @ np.array([0, 0, 1.0])     # room-vertical at tau*, expressed in the tube frame
    for lab, d in (("along the beam", beam), ("along the wire", wire_dir), ("room-vertical at tau*", up_in_tube)):
        hit = None
        clear_at = None
        for t in np.arange(0.0, 250.1, 0.25):
            Q = [p + t * d for p in P0]
            for q, tag in zip(Q, TAGS):
                if V.collides_tube(tuple(q), margin=0.0 if t < 3 else 1.0):
                    hit = (round(float(t), 2), tag)
                    break
            if hit:
                break
            if clear_at is None and all((math.hypot(q[0], q[1]) > R_OUT + 5) or (q[2] > RIM + 30) for q in Q):
                clear_at = float(t)
        print(f"   {lab:22s}: {'collides at ' + str(hit) if hit else 'clear to 250 mm'}; gun clear of the tube cylinder (r > 68.5 or above rim+30) after {clear_at} mm")
    tip_rim = (RIM + 1 - DOT[2]) / beam[2]
    print(f"   along the beam the wire tip is 1 mm above the rim after {tip_rim:.1f} mm")

    print("\n== existing rotator tipping (gravity-seated turntable, spool catch 1 mm)")
    for h in (100, 116, 140):
        print(f"   CG {h} mm above the race (estimate): turntable starts to lift at tau = {math.degrees(math.atan(82.5 / h)):.1f} deg")

    print("\n== second closure: float slides to the LOW end of its rod")
    print("   the plate being welded is the tube's upper end while the axis is < 90 deg from vertical;")
    print("   past 90 deg the float (printed/harvested plastic) slides toward the plate being welded.")

    print("\n== argon in the recess: the rim's low point moves to the station for any tau > 0")
    print(f"   recess spills over the station lip once tau > atan(6.35/123.7) = {math.degrees(math.atan(6.35 / 123.7)):.1f} deg (argon is ~1.38x air density)")

    print("\n== Bond number Bo = rho g L^2 / sigma (liquid steel rho ~7000 kg/m3, sigma ~1.8 N/m; handbook-order values)")
    for L in (1.0, 1.5, 2.0, 3.0, 6.0):
        print(f"   pool length scale {L} mm: Bo = {7000 * 9.81 * (L / 1000) ** 2 / 1.8:.3f}")

    print("\n== where the gun sits at tau* (room coords relative to the dot, mm)")
    R = tilt(tau_star)
    for k in ("nozzle_tip", "body_front", "body_back", "grip_base_QBH"):
        p = R @ (world(FEATURES[k], RECIPE) - DOT)
        print(f"   {k:14s} x {p[0]:+7.1f}  y {p[1]:+7.1f}  z {p[2]:+7.1f}")
    c = R @ com
    print(f"   CoM proxy      x {c[0]:+7.1f}  y {c[1]:+7.1f}  z {c[2]:+7.1f}")
    # the tube in the room at tau*: axis direction and centre of the working rim
    ax = R @ axis
    rim_c = R @ (np.array([0, 0, RIM]) - DOT)
    print(f"   tube axis dir {np.round(ax,3)}; rim centre at {np.round(rim_c,1)} relative to the dot")
    low = min(((R @ (np.array([R_IN * math.cos(a), R_IN * math.sin(a), RIM]) - DOT))[2], math.degrees(a)) for a in np.linspace(0, 2 * math.pi, 361))
    print(f"   lowest point of the rim: {low[0]:+.1f} mm relative to the dot, at {low[1]:.0f} deg around the tube (0 = station)")


def orientation(dials):
    """Gun orientation matrix (columns = local x, y, z axes in the tube frame) for scene dials."""
    o = np.array(pose_dial((0, 0, 0), *dials))
    cols = [np.array(pose_dial(tuple(e), *dials)) - o for e in np.eye(3)]
    return np.column_stack(cols)


def dials_equivalent_to_work_tilt(tau, alpha=0.0, d0=RECIPE):
    """Which dial change reproduces, relative to the joint, a work tilt (tau about the tangent,
    alpha about the radial, both through the dot)? Solve R(d) = tilt(tau,alpha)^T R(d0)."""
    target = tilt(tau, alpha).T @ orientation(d0)
    d = np.array(d0, float)
    for _ in range(30):
        R = orientation(d)
        err = (R - target).ravel()
        J = np.zeros((9, 3))
        for k in range(3):
            dd = d.copy(); dd[k] += 1e-4
            J[:, k] = ((orientation(dd) - R).ravel()) / 1e-4
        step = np.linalg.lstsq(J, -err, rcond=None)[0]
        d += step
        if np.linalg.norm(step) < 1e-9:
            break
    resid = np.abs(orientation(d) - target).max()
    return d - np.array(d0, float), resid


if __name__ == "__main__":
    print("\n== which of Derek's dials a work tilt replaces (relative to the joint), at 45 / 30 / -15")
    for tau, alpha in ((1, 0), (10, 0), (32.5, 0), (0, 1), (0, 10)):
        dd, res = dials_equivalent_to_work_tilt(tau, alpha)
        print(f"   work tilt tau {tau:5.1f} (tangent), alpha {alpha:4.1f} (radial) == dial change grip {dd[0]:+6.2f}, hole {dd[1]:+6.2f}, vertical {dd[2]:+6.2f}  (fit residual {res:.1e})")

    print("\n== isocentric cradle for the existing rotator: holding torque (estimates)")
    # axis = station tangent through the dot; assembly CG ~62 mm inboard (-X) and ~130 mm below the dot at tau = 0
    for m in (8.0, 10.0):
        for tau in (0, 20, 32.5):
            r = Ry(tau) @ np.array([-61.85, 0, -130.0])
            print(f"   {m} kg, tau {tau:4.1f}: CG at x {r[0]:+6.1f}, z {r[2]:+6.1f} mm from the axis -> gravity torque {m*9.81*r[0]/1000:+6.2f} N*m (negative = back toward tau < 0)")

    print("\n== a rail fixed to the work along d = (-0.537, 0, 0.844) (room-vertical at tau*): does a straight lift clear for other recipes?")
    d_rail = np.array([-math.sin(math.radians(tau_star)), 0, math.cos(math.radians(tau_star))])
    PTS, TAGS = V.proxy_points()
    rows = []
    for grip in (30, 45, 60):
        for hole in (15, 30, 45):
            for yaw in (-30, -15, 0, 5):
                P0 = [np.array(pose_dial(p, grip, hole, yaw)) for p in PTS]
                if any(V.collides_tube(tuple(q), margin=0.0) for q in P0):
                    rows.append((grip, hole, yaw, "infeasible at rest"))
                    continue
                res = "clear"
                for t in np.arange(0.25, 120.1, 0.25):
                    if any(V.collides_tube(tuple(q + t * d_rail), margin=0.0 if t < 3 else 1.0) for q in P0):
                        res = f"collides at {t:.2f} mm"
                        break
                rows.append((grip, hole, yaw, res))
    ok = [r for r in rows if r[3] == "clear"]
    bad = [r for r in rows if r[3] not in ("clear", "infeasible at rest")]
    inf = [r for r in rows if r[3] == "infeasible at rest"]
    print(f"   {len(ok)} clear, {len(bad)} collide, {len(inf)} infeasible at rest (of {len(rows)})")
    for r in bad:
        print("   collide:", r)
