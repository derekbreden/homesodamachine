#!/usr/bin/env python3
"""Independent check of scene borrowed-03-encoded-arm: how joint-encoder errors become dot errors.

Same model as the scene (all ILLUSTRATIVE): a six-joint arm (base yaw, shoulder pitch, elbow pitch, then a spherical
wrist with axes x, y, z in XYZ Euler order), post 260 mm above the bench, links 260 + 260 mm, wrist centre at local
(0, 0, 150) of the gun proxy. Encoder model: reading = quantise(angle + INL*sin(angle + 1.3*i)) + offset_i, with
offset_i = +-OFF and INL, OFF in degrees. The dot is placed at the seam (reference dials 45 / 30 / -15).

Also prints a scale-free lever-arm table: dot error ~ sum of lever_i * dtheta_i. [derived]
"""
import math
import numpy as np
from gimbal_geometry import gun_rotation, CLEAR

J = np.array([61.849, 0.0, 146.05])              # weld joint, WK.JOINT [repo dims]
BENCH_Z = -86.0                                  # bench top in the kit's world (illustrative frame)
BASE = np.array([-300.0, -330.0, BENCH_Z + 260.0])
W_LOCAL = np.array([0.0, 0.0, 150.0])
DOT_LOCAL = np.array([0.0, 0.0, -CLEAR])
SIGN = [1, -1, 1, -1, 1, -1]

def euler_xyz(R):
    """R = Rx(a) Ry(b) Rz(c) (three.js 'XYZ')."""
    b = math.asin(max(-1, min(1, R[0, 2])))
    if abs(R[0, 2]) < 0.9999999:
        a = math.atan2(-R[1, 2], R[2, 2]); c = math.atan2(-R[0, 1], R[0, 0])
    else:
        a = math.atan2(R[2, 1], R[1, 1]); c = 0.0
    return a, b, c

def Rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def arm_frame(t1, t23):
    c1, s1 = math.cos(t1), math.sin(t1)
    f = np.array([c1 * math.cos(t23), s1 * math.cos(t23), math.sin(t23)])
    y = np.array([-s1, c1, 0.0]); z = np.cross(f, y)
    return f, np.column_stack([f, y, z])

def fk(th, L1, L2):
    c1, s1, c2, s2 = math.cos(th[0]), math.sin(th[0]), math.cos(th[1]), math.sin(th[1])
    E = BASE + L1 * np.array([c1 * c2, s1 * c2, s2])
    f, Ra = arm_frame(th[0], th[1] + th[2])
    Wc = E + L2 * f
    Rt = Ra @ (Rx(th[3]) @ Ry(th[4]) @ Rz(th[5]))
    pos = Wc - Rt @ W_LOCAL
    return Wc, Rt, pos + Rt @ DOT_LOCAL

def ik(Rt, pos, L1, L2):
    Wc = pos + Rt @ W_LOCAL
    d = Wc - BASE; D = np.linalg.norm(d)
    if D > L1 + L2 or D < abs(L1 - L2): raise ValueError('out of reach')
    u = d / D; a = (L1 * L1 - L2 * L2 + D * D) / (2 * D); hh = math.sqrt(max(0, L1 * L1 - a * a))
    hint = np.array([0, 0, 1.0]); hint = hint - hint.dot(u) * u; hint /= np.linalg.norm(hint)
    E = BASE + a * u + hh * hint
    t1 = math.atan2(d[1], d[0]); c1, s1 = math.cos(t1), math.sin(t1)
    e = E - BASE; t2 = math.atan2(e[2], e[0] * c1 + e[1] * s1)
    fv = Wc - E; t23 = math.atan2(fv[2], fv[0] * c1 + fv[1] * s1)
    f, Ra = arm_frame(t1, t23)
    a4, b5, c6 = euler_xyz(Ra.T @ Rt)
    return [t1, t2, t23 - t2, a4, b5, c6]

def measured(th, bits, inl, off):
    q = 360.0 / 2 ** bits; out = []
    for i in range(6):
        d = math.degrees(th[i]); raw = d + inl * math.sin(th[i] + i * 1.3)
        out.append(math.radians(round(raw / q) * q + off * SIGN[i]))
    return out

def dot_error(bits, inl, off, L1=260.0, L2=260.0, dials=(45, 30, -15)):
    r, h, v = dials[0], dials[1], dials[2]
    Rt = gun_rotation(v, h, r)
    pos = J - Rt @ DOT_LOCAL
    th = ik(Rt, pos, L1, L2)
    _, _, dot_true = fk(th, L1, L2)
    _, _, dot_est = fk(measured(th, bits, inl, off), L1, L2)
    return dot_est - dot_true, th

if __name__ == '__main__':
    e, th = dot_error(16, 0, 0)
    print('sanity: true dot - J with perfect encoders (16 bit) error vector:', np.round(e, 3))
    print('joint angles (deg):', np.round(np.degrees(th), 1))
    print()
    print('%-44s %8s   %s' % ('setting', 'total mm', '(x=radial, y=along, z=vertical)'))
    for label, args in [('8 bit, no INL, no offset', (8, 0, 0)), ('12 bit, no INL, no offset', (12, 0, 0)), ('14 bit, no INL, no offset', (14, 0, 0)),
                        ('12 bit, INL 0.2 deg', (12, 0.2, 0)), ('12 bit, offset 0.3 deg', (12, 0, 0.3)),
                        ('12 bit, offset 0.3 deg after touch-off (x0.1)', (12, 0, 0.03)),
                        ('14 bit, INL 0.05, offset 0.05 x0.1 (touch-off)', (14, 0.05, 0.005)),
                        ('AS5600 datasheet max INL 1.0 deg, 12 bit, zeroed', (12, 1.0, 0)),
                        ('12 bit, INL 0.5 deg (a typical-looking figure)', (12, 0.5, 0))]:
        e, _ = dot_error(*args)
        print('%-44s %8.2f   (%.2f, %.2f, %.2f)' % (label, np.linalg.norm(e), e[0], e[1], e[2]))
    print()
    print('Lever arms from each joint axis to the dot at the seam (mm):')
    Rt = gun_rotation(-15, 30, 45); pos = J - Rt @ DOT_LOCAL; th = ik(Rt, pos, 260, 260)
    Wc, Rt2, dot = fk(th, 260, 260)
    # numeric Jacobian columns: dot displacement per radian of each joint
    eps = 1e-6; base = np.array(th)
    for i in range(6):
        t2 = base.copy(); t2[i] += eps
        _, _, d2 = fk(t2, 260, 260)
        print('  joint %d: %.0f mm per radian (%.2f mm per 0.1 deg)' % (i + 1, np.linalg.norm(d2 - dot) / eps, np.linalg.norm(d2 - dot) / eps * math.radians(0.1)))
    lev = []
    for i in range(6):
        t2 = base.copy(); t2[i] += eps
        _, _, d2 = fk(t2, 260, 260); lev.append(np.linalg.norm(d2 - dot) / eps)
    lev = np.array(lev)
    print('  sum of lever arms %.0f mm; RSS %.0f mm. Worst-case dot error for angle error d deg per joint: %.2f mm per 0.1 deg; RSS: %.2f mm per 0.1 deg'
          % (lev.sum(), np.sqrt((lev ** 2).sum()), lev.sum() * math.radians(0.1), np.sqrt((lev ** 2).sum()) * math.radians(0.1)))
