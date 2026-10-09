"""Statics behind scenes/datum-03-rim-crown.

Where does the gun's centre of mass sit against the ring that would carry it, and what
counterweight and tether does that ask for? The gun mass, its distribution, the umbilical
drag and every part mass are ILLUSTRATIVE (nobody has weighed the gun [unknown]).
Geometry: proxy gun (253 x 143 x 34 mm envelope [manual]; sections illustrative) placed with
the reference scene's opening pose (roll 45, hole dial 30, vertical -15; illustrative),
joint at (61.85, 0, 146.05) [repo][derived]. posePoint ported from web/public/js/weld-position/pose.js
as the kit ports it.
"""
import math
import numpy as np

DEG = math.pi / 180
IN = 25.4
INNER_R = 2.5 * IN - 0.065 * IN     # 61.85
CAP_TOP = 6 * IN - 0.25 * IN        # 146.05
RIM_Z = 6 * IN                      # 152.4
JOINT = np.array([INNER_R, 0, CAP_TOP])
PITCH = 60 * DEG
CLEAR = 16
GRIP_BASE = np.array([0, -118, 237.0])
ax_len = math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR)
ROLL_AXIS = np.array([0, GRIP_BASE[1] / ax_len, (GRIP_BASE[2] + CLEAR) / ax_len])


def pose_point(p, roll_deg, hole_roll_deg, vert_deg):
    x, y, z = p
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = z + CLEAR
    py = -c * along + s * y
    pz = s * along + c * y
    roll = roll_deg * DEG
    ay = -c * ROLL_AXIS[2] + s * ROLL_AXIS[1]
    az = s * ROLL_AXIS[2] + c * ROLL_AXIS[1]
    dot = ay * py + az * pz
    cr, sr = math.cos(roll), math.sin(roll)
    rx = x * cr + (ay * pz - az * py) * sr
    ry = py * cr + az * x * sr + ay * dot * (1 - cr)
    rz = pz * cr - ay * x * sr + az * dot * (1 - cr)
    h = hole_roll_deg * DEG
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = vert_deg * DEG
    cv, sv = math.cos(v), math.sin(v)
    return np.array([JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz])


def world(local, roll=45, hole_dial=30, vert=-15):
    return pose_point(local, roll, hole_dial - 35, vert)


NOZZLE = world([0, 0, 0])
DOT = world([0, 0, -CLEAR])
HOUS = world([0, 0, 185.5])
BARREL = world([0, 0, 60])
GRIPMID = world([0, (-25 - 111) / 2, (172 + 232) / 2])
GRIPB = world(GRIP_BASE)


def horiz(p):
    return math.hypot(p[0], p[1])


def report():
    print("dot", DOT.round(2), "(should be the joint", JOINT.round(2), ")")
    for name, p in [("nozzle tip", NOZZLE), ("barrel mid", BARREL), ("housing centre", HOUS), ("grip mid", GRIPMID), ("grip base / cable exit", GRIPB)]:
        az = math.degrees(math.atan2(p[1], p[0]))
        print("  %-22s x %7.1f y %7.1f z %7.1f   horizontal radius %6.1f mm at azimuth %6.1f deg, %5.1f mm above the rim" % (name, p[0], p[1], p[2], horiz(p), az, p[2] - RIM_Z))
    print("  nozzle tip is %.1f mm from the axis, %.1f mm above the rim (inside a ring of inner radius > %.0f mm)" % (horiz(NOZZLE), NOZZLE[2] - RIM_Z, horiz(NOZZLE) + 6))

    print("\nGun centre of mass (mass split: barrel .15, housing .55, grip .30; illustrative)")
    cg = 0.15 * BARREL + 0.55 * HOUS + 0.30 * GRIPMID
    print("  cg x %.1f y %.1f z %.1f, horizontal radius %.1f mm at azimuth %.1f deg" % (cg[0], cg[1], cg[2], horiz(cg), math.degrees(math.atan2(cg[1], cg[0]))))

    for mg in (0.6, 1.0, 1.5):
        # upper assembly: gun mass mg + shell 0.15 kg, boom+stage 0.25 kg beside the barrel, upper ring 0.30 kg at the axis
        parts = [(mg + 0.15, cg[:2]), (0.25, np.array([32.5, -48.5])), (0.30, np.array([0.0, 0.0]))]   # boom + stage sit beside the barrel, as in the scene
        M = sum(m for m, _ in parts)
        cgxy = sum(m * p for m, p in parts) / M
        r_support = 66.0   # ball pitch radius, illustrative
        # counterweight opposite the combined cg direction at radius rc
        d = cgxy / (np.linalg.norm(cgxy) + 1e-9)
        out = []
        for rc in (70.0, 100.0):
            # (M cgxy - mc*rc*d)/(M+mc) = 0  ->  mc = M|cgxy|/rc
            mc = M * np.linalg.norm(cgxy) / rc
            out.append((rc, mc))
        print("\n  gun+shell %.2f kg: upper assembly %.2f kg, combined cg %.1f mm from the axis (ball pitch radius %.0f mm: %s)" % (mg + 0.15, M, np.linalg.norm(cgxy), r_support, "OVER the ring" if np.linalg.norm(cgxy) > r_support else "inside the ring"))
        for rc, mc in out:
            print("     counterweight at r=%3.0f mm opposite: %.2f kg brings the combined cg to the axis (assembly %.2f kg)" % (rc, mc, M + mc))
        # rim pressure with everything (lower ring 0.15 kg extra) on the rim annulus
        Mtot = M + out[1][1] + 0.15
        area = math.pi * (2.5 * IN) ** 2 - math.pi * INNER_R ** 2
        print("     total on the rim %.2f kg: %.1f N over %.0f mm^2 rim annulus = %.3f MPa (316L yield ~ 170-200 MPa, wall in compression) " % (Mtot, Mtot * 9.81, area, Mtot * 9.81 / area))

    print("\nAnti-rotation tether: torque about the tube axis from umbilical drag at the cable exit")
    arm = horiz(GRIPB)
    print("  cable exit is %.0f mm from the axis" % arm)
    for F in (1, 3, 10):
        T = F * arm / 1000
        for rt in (90.0, 150.0):
            print("  drag %4.1f N at the exit: %.2f N.m; tether at r=%3.0f mm carries %.1f N" % (F, T, rt, T / (rt / 1000)))
    print("\nBearing drag: printed ball race, illustrative friction coefficient 0.01 at pitch 66 mm carrying 30 N: %.3f N.m" % (0.01 * 30 * 0.066))
    print("Rotating the whole upper assembly about the tube axis moves the dot along the seam and leaves gun-to-corner pose unchanged.")
    print("  a tether that lets the ring turn 2 deg moves the dot %.2f mm along the seam" % (INNER_R * 2 * DEG))


if __name__ == "__main__":
    report()
