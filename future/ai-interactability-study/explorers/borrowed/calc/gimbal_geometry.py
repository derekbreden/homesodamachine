#!/usr/bin/env python3
"""Numbers behind scene borrowed-02-gimbal-on-gantry.

Uses the reference scene's dial model (port of posePoint / dialsToPose in kit/weldkit.js, which is a port of
web/public/js/weld-position/pose.js). Gun proxy: local frame origin at the nozzle tip, +Z toward the back,
-Y toward the grip, dot at (0,0,-16), cable exit ('grip base') at (0,-118,237). Pitch 60 deg and clearance
16 mm are the reference scene's ILLUSTRATIVE values; the 253 x 143 x 34 mm envelope is [manual] p. 17.

Claim tested: if the gimbal centre C lies on the line from the dot to the cable exit at distance t from the dot,
then for angles (yaw v, hole h, roll r):
    dot = C - t * g(v, h)        where g is the world direction of the roll axis
so roll never moves the dot, and the gantry must move C by t * (g - g0) to hold the dot. [derived]
"""
import math
import numpy as np

PITCH = math.radians(60)
CLEAR = 16.0
GRIP_BASE = np.array([0.0, -118.0, 237.0])
AXIS = np.array([0.0, GRIP_BASE[1], GRIP_BASE[2] + CLEAR])
AXIS = AXIS / np.linalg.norm(AXIS)          # dot -> cable exit direction, local frame
HOLE_OFFSET = 35.0                           # dial reads 35 at the reference mounting inclination

def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def pitch60(d):
    """Direction d (local) -> pitched frame (posePoint's first step, for directions)."""
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = d[2]
    return np.array([d[0], -c * along + s * d[1], s * along + c * d[1]])

def rot_about(axis, ang):
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)

def gun_rotation(v_deg, h_dial, r_deg):
    """Rotation matrix taking gun-local directions to world for the three dials (about the dot)."""
    a0 = pitch60(AXIS)
    Ra = rot_about(a0, math.radians(r_deg))
    Rx = rx(-math.radians(h_dial - HOLE_OFFSET))       # pose maths turns the hole roll by -(dial-35)
    Rz = rz(math.radians(v_deg))
    P = np.column_stack([pitch60(np.array(e)) for e in np.eye(3)])
    return Rz @ Rx @ Ra @ P

def g_axis(v, h, r):
    return gun_rotation(v, h, r) @ AXIS

if __name__ == '__main__':
    v0, h0, r0 = -15.0, 30.0, 45.0   # reference opening pose (illustrative)
    g0 = g_axis(v0, h0, r0)
    print('roll-axis direction at the opening pose (world):', np.round(g0, 3))
    print('roll does not move it: g(v0,h0,0) =', np.round(g_axis(v0, h0, 0), 3))
    print()
    print('Dot swing per degree if the gantry did not compensate (mm/deg) = t * |dg/dangle|:')
    for t in (120, 160, 200, 240, 262):
        dv = np.linalg.norm(g_axis(v0 + 1, h0, r0) - g_axis(v0, h0, r0)) * t
        dh = np.linalg.norm(g_axis(v0, h0 + 1, r0) - g_axis(v0, h0, r0)) * t
        print('  t=%3d mm: yaw %.2f  hole %.2f  (small-angle limit t*pi/180 = %.2f)' % (t, dv, dh, t * math.pi / 180))
    print()
    print('Gantry travel (x, y, z ranges of C, mm) to serve yaw +-span and hole +-span, 3x3 grid:')
    print('   span |  t   |    x     y     z')
    for span in (10, 20, 30, 45):
        for t in (120, 200, 262):
            pts = np.array([t * g_axis(v0 + a * span, h0 + b * span, r0) for a in (-1, 0, 1) for b in (-1, 0, 1)])
            ext = pts.max(0) - pts.min(0)
            print('   %3d  | %3d  | %5.0f %5.0f %5.0f' % (span, t, ext[0], ext[1], ext[2]))
    print()
    print('Dot error from an angle error d (deg) at distance t: t * d * pi/180 [derived]:')
    for d in (0.02, 0.05, 0.1, 0.3):
        print('  %.2f deg: ' % d + '  '.join('t=%d -> %.2f mm' % (t, t * d * math.pi / 180) for t in (120, 200, 262)))
    print()
    print('Holding torque about C if the centre of mass is offset by e from C (illustrative masses, unknown gun mass):')
    for m in (0.8, 1.2, 2.0):
        print('  m=%.1f kg: ' % m + '  '.join('e=%d mm -> %.2f N m' % (e, m * 9.81 * e / 1000) for e in (10, 30, 60)))
