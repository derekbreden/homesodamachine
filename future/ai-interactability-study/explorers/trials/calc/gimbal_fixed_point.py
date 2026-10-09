#!/usr/bin/env python3
"""Where the gimbal-on-gantry formula (borrowed-02) is silently sensitive, and what a fixed-point (pivot) trial recovers.

borrowed-02: with the gimbal centre C on the roll line at distance t from the dot, dot = C - t g(v, h) and the gantry moves C to
J + t g so the dot stays on the seam J.  The formula assumes the gun-frame position of C is exactly DOT + t * AXIS.  A printed
cradle, a hand-balanced gun and a gimbal whose centre is only nominal make that position uncertain by delta (3 numbers, mm).
The dot then lands at J - (R - R0) delta after a touch-off at the home pose.  The scene's error sliders cover angle error
(t * angle: 0.17 mm per 0.05 deg at t = 200) but not this.

Section 1: dot error over the swing for 1 mm of delta along each gun axis, and the angle-error term for comparison.
Section 2: fixed-point trial. The gantry runs the formula through N orientations with the beam on a board; a camera reads the board
xy of the spot (noise sigma); least squares recovers delta (and the board's height and a frame shift). Fresh-pose error after
correction is reported.  ILLUSTRATIVE: geometry is borrowed's gun proxy and dial model (calc/gimbal_geometry.py); noise,
spans and delta are made up; the gantry and gimbal are assumed to do what they are told.
"""
import math, sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'borrowed', 'calc'))
from gimbal_geometry import gun_rotation, AXIS, CLEAR

DOT = np.array([0.0, 0.0, -CLEAR])
J = np.array([61.849, 0.0, 146.05])
R0 = gun_rotation(-15.0, 30.0, 45.0)

def cmd_center(R, t):
    """Where the gantry puts C so the dot should be at J: C = J + R (c_est - DOT), c_est = DOT + t AXIS."""
    return J + R @ (t * AXIS)

def dot_error(v, h, r, delta, t=200.0, ang_err=(0, 0, 0)):
    """World error of the dot (or nozzle-referenced point) for a pose: -(R - R0) delta plus the angle error (deg on yaw, hole, roll)."""
    Rc = gun_rotation(v, h, r)                                   # commanded
    Ra = gun_rotation(v + ang_err[0], h + ang_err[1], r + ang_err[2])   # what the gimbal actually turned to
    C = cmd_center(Rc, t)
    c_true = DOT + t * AXIS + delta
    dot = C - Ra @ (c_true - DOT)
    # home-pose touch-off removes the constant: compare with the same formula at the home pose
    C0 = cmd_center(R0, t); dot0 = C0 - R0 @ (c_true - DOT)
    return (dot - J) - (dot0 - J)

def span_stats(delta=(0, 0, 0), ang=(0, 0, 0), span=30, t=200.0, n=9, roll_span=None):
    rs = np.linspace(-span, span, n)
    roll_span = span if roll_span is None else roll_span
    errs = []
    for a in rs:
        for b in rs:
            for c in np.linspace(-roll_span, roll_span, 3):
                errs.append(np.linalg.norm(dot_error(-15 + a, 30 + b, 45 + c, np.array(delta, float), t, ang)))
    e = np.array(errs)
    return math.sqrt((e ** 2).mean()), e.max()

def hit_board(v, h, r, delta, t, zb, ang_err=(0, 0, 0)):
    """The beam line from the true nozzle meets the board plane z = zb: where."""
    Rc = gun_rotation(v, h, r); Ra = gun_rotation(v + ang_err[0], h + ang_err[1], r + ang_err[2])
    C = cmd_center(Rc, t)
    c_true = DOT + t * AXIS + delta
    N = C - Ra @ c_true                                          # nozzle (gun-local origin) in the world
    d = Ra @ np.array([0.0, 0.0, -1.0])
    s = (zb - N[2]) / d[2]
    return (N + s * d)

def fixed_point_trial(n=30, span=20, delta=(1.0, -0.8, 0.6), noise=0.05, t=200.0, seed=0, zb_err=0.0, ang_err_sd=0.0):
    """Estimate delta from N orientations with the beam on a board whose height is only known to zb_err."""
    rng = np.random.default_rng(seed)
    delta = np.array(delta, float)
    zb = J[2]
    rows, obs = [], []
    poses = []
    for i in range(n):
        v, h, r = -15 + rng.uniform(-span, span), 30 + rng.uniform(-span, span), 45 + rng.uniform(-span, span)
        ae = rng.normal(0, ang_err_sd, 3)
        poses.append((v, h, r, ae))
    def hits(dhat, zbhat):
        return np.array([hit_board(v, h, r, dhat, t, zbhat, ae)[:2] for v, h, r, ae in poses])
    true_hits = hits(delta, zb)
    cam = true_hits + rng.normal(0, noise, true_hits.shape)
    # unknowns: delta (3), board height offset (1), frame shift (2). The model's own hits use the NOMINAL formula (delta_hat).
    p = np.zeros(6)
    def resid(pv):
        h = np.array([hit_board(v, hh, r, pv[:3], t, zb + zb_err + pv[3], 0 * ae)[:2] for v, hh, r, ae in poses])
        return ((h - pv[4:6]) - cam).ravel()
    for it in range(15):
        r0 = resid(p); Jm = np.zeros((r0.size, 6))
        for k in range(6):
            dp = np.zeros(6); dp[k] = 1e-2
            Jm[:, k] = (resid(p + dp) - resid(p - dp)) / 2e-2
        step = np.linalg.solve(Jm.T @ Jm + 1e-6 * np.eye(6) + np.diag([0, 0, 0, 1e-4, 1e-6, 1e-6]), -Jm.T @ r0)
        p += step
        if np.linalg.norm(step) < 1e-9: break
    return p, delta, poses, zb


def fresh_hit_error(p, delta, t, zb, ang_err_sd=0.0, span=20, n=200, seed=99, correct=True, zb_err=0.0):
    """rms error of where the beam meets the board on fresh poses, constant removed (touch-off), with delta_hat applied or not."""
    rng = np.random.default_rng(seed)
    e = []
    for i in range(n):
        v, h, r = -15 + rng.uniform(-span, span), 30 + rng.uniform(-span, span), 45 + rng.uniform(-span, span)
        truth = hit_board(v, h, r, delta, t, zb)[:2]
        est = hit_board(v, h, r, p[:3] if correct else np.zeros(3), t, zb + zb_err + (p[3] if correct else 0))[:2] - (p[4:6] if correct else 0)
        e.append(est - truth)
    e = np.array(e); e = e - e.mean(0)
    return math.sqrt((e ** 2).sum(1).mean())

if __name__ == '__main__':
    print('Section 1: RMS / max dot error over the swing (yaw, hole, roll each +-span) after a touch-off at the home pose, t = 200 mm')
    print('%-40s %-6s %-9s %-9s' % ('error', 'span', 'rms mm', 'max mm'))
    for span in (10, 20, 30):
        for label, delta, ang in [('cradle delta 1 mm along gun x', (1, 0, 0), (0, 0, 0)), ('cradle delta 1 mm along gun y', (0, 1, 0), (0, 0, 0)),
                                  ('cradle delta 1 mm along gun z (t error)', (0, 0, 1), (0, 0, 0)), ('delta 1 mm, all three (0.58 each)', (0.577,) * 3, (0, 0, 0))]:
            a, b = span_stats(delta, ang, span)
            print('%-40s %-6d %-9.3f %-9.3f' % (label, span, a, b))
        # an angle error that is a constant is removed by the touch-off; a gimbal that reads 0.05 deg wrong by a per-axis SCALE (0.1 %)
        print()
    print('angle-error term for comparison: t * angle = %.2f mm per 0.05 deg (constant, removed by a touch-off at home)' % (200 * math.radians(0.05)))
    print()
    print('Section 2: fixed-point trial, beam on a board, camera reads board xy.  True delta = (1.0, -0.8, 0.6) mm in the gun frame')
    print('(x, y are perpendicular to the beam; z is along it).  Fitted: delta (3), board height (1), frame shift (2).')
    print('%-8s %-7s %-7s | %-22s %-22s | %-14s %-14s' % ('span', 'poses', 'cam mm', 'lateral |dx,dy| err', 'along-beam err', 'fresh hit err', 'uncorrected'))
    for span in (10, 20, 30):
        for n in (10, 20, 40):
            for noise in (0.05, 0.15):
                lat, alo, fh, un = [], [], [], []
                for s in range(6):
                    p, true, poses, zb = fixed_point_trial(n=n, span=span, noise=noise, seed=s)
                    lat.append(np.linalg.norm(p[:2] - true[:2])); alo.append(abs(p[2] - true[2]))
                    fh.append(fresh_hit_error(p, true, 200.0, zb, span=span)); un.append(fresh_hit_error(p, true, 200.0, zb, span=span, correct=False))
                print('%-8s %-7d %-7.2f | %-22.3f %-22.3f | %-14.3f %-14.3f' % ('+-%d' % span, n, noise, np.mean(lat), np.mean(alo), np.mean(fh), np.mean(un)))
    print('board height known only to 0 / 0.3 / 1.0 mm (span 20, 30 poses, cam 0.05; a free height term is fitted):')
    for zbe in (0.0, 0.3, 1.0):
        lat, fh = [], []
        for s in range(6):
            p, true, poses, zb = fixed_point_trial(n=30, span=20, noise=0.05, seed=s, zb_err=zbe)
            lat.append(np.linalg.norm(p[:2] - true[:2])); fh.append(fresh_hit_error(p, true, 200.0, zb, span=20, zb_err=zbe))
        print('  zb error %.1f: lateral err %.3f  fresh hit err %.3f' % (zbe, np.mean(lat), np.mean(fh)))
