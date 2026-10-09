#!/usr/bin/env python3
"""Touch calibration of an encoded balanced arm (borrowed-03) against a dot board (trials-05 rung 1, trials-13 method).

Question asked of borrowed-03: its cheap joint encoders carry a per-turn linearity error (AS5600 datasheet: +-1 deg system INL,
about 15 mm of dot error on the scene's arm) and unknown zeros. Can a hand-moved arm calibrate itself by putting the dot near one
printed cross on a board in many orientations, with a camera reading where on the board the dot fell?  A fixed-point calibration.

Model (ALL ILLUSTRATIVE; the arm, its links and the encoder error model are borrowed-03's, calc/encoder_error.py):
  - six-joint arm: base yaw, shoulder pitch, elbow pitch, spherical wrist (x, y, z Euler), post 260, links 260 + 260 mm, wrist
    centre 150 mm behind the nozzle tip, beam along local -Z (dot 16 mm ahead of the tip).
  - encoder i reads quantise(theta_i + A_i sin(theta_i + phi_i)) + off_i.  borrowed's scene uses one A for all joints and
    phi_i = 1.3 i; here A_i is drawn in [0.5 A, A] with a random phase and offsets up to 'off' (a less tidy truth).
  - the true link lengths and wrist offset differ from the drawing by up to 2 mm; the true beam differs from the drawn -Z by
    a few milliradians and starts up to about half a millimetre off the drawn tip.
  - each touch: the hand puts the beam within +-0.3 mm of the cross in a chosen orientation of the dial window; the camera reads
    the board xy of the spot (noise sigma_cam); the standoff is whatever the hand leaves (+-2 mm); random joint play (deg)
    moves the real pose and is invisible to the encoders.
  - calibration model: per-joint offset and one cos/sin harmonic (12 numbers), link corrections (2), wrist offset (1), beam
    origin lateral (2) and beam tilt (2), plus a shift between the camera's frame and the arm's (2) and the board height (1):
    28 numbers from 2 N equations; light priors keep unobservable directions near zero.
  - score: on FRESH poses from the same window (never fitted), the rms error of where the arm says the beam meets the board
    against where the camera-truth says it did, after removing a constant (what one touch-off removes).  Uncalibrated =
    the nominal model.  This is the error a coach or a recorder would carry into the weld neighbourhood.
Numpy only.
"""
import math, sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'borrowed', 'calc'))
import encoder_error as ee                             # borrowed's arm geometry (read only)
from gimbal_geometry import gun_rotation

L1_0, L2_0, W0 = 260.0, 260.0, 150.0
SIGN = np.array([1, -1, 1, -1, 1, -1], float)
ZB = 60.0                                              # board height in the kit's frame (illustrative: near the plate face height range)

def _r(a, kind):
    c, s = np.cos(a), np.sin(a); o, z = np.ones_like(a), np.zeros_like(a)
    if kind == 'x': m = [[o, z, z], [z, c, -s], [z, s, c]]
    elif kind == 'y': m = [[c, z, s], [z, o, z], [-s, z, c]]
    else: m = [[c, -s, z], [s, c, z], [z, z, o]]
    return np.stack([np.stack(r, -1) for r in m], -2)

def fk_batch(th, L1, L2, W):
    """th (N,6) radians -> nozzle position (N,3), rotation (N,3,3)."""
    c1, s1, c2, s2 = np.cos(th[:, 0]), np.sin(th[:, 0]), np.cos(th[:, 1]), np.sin(th[:, 1])
    E = ee.BASE + L1 * np.stack([c1 * c2, s1 * c2, s2], -1)
    t23 = th[:, 1] + th[:, 2]
    f = np.stack([c1 * np.cos(t23), s1 * np.cos(t23), np.sin(t23)], -1)
    y = np.stack([-s1, c1, np.zeros_like(s1)], -1)
    z = np.cross(f, y)
    Ra = np.stack([f, y, z], -1)
    Wc = E + L2 * f
    Rt = Ra @ (_r(th[:, 3], 'x') @ _r(th[:, 4], 'y') @ _r(th[:, 5], 'z'))
    pos = Wc - Rt[:, :, 2] * W
    return pos, Rt

def hit_plane(pos, Rt, zb, o=(0.0, 0.0), tilt=(0.0, 0.0)):
    org = pos + Rt[:, :, 0] * o[0] + Rt[:, :, 1] * o[1]
    dl = np.array([tilt[0], tilt[1], -1.0]); dl /= np.linalg.norm(dl)
    d = Rt @ dl
    s = (zb - org[:, 2]) / d[:, 2]
    return org + s[:, None] * d

class Truth:
    def __init__(self, rng, bits=12, inl=0.5, off=0.3, dl=2.0, play=0.01, tidy=False, sag=0.0, harm=0.0, lean=0.0):
        # harm: 2nd and 3rd INL harmonics as a fraction of the 1st (the fit models only the 1st); lean: the post leans (deg),
        # an unmodelled axis error the fit can only partly absorb
        self.bits, self.play, self.sagdeg, self.harm = bits, play, sag, harm
        ax = rng.normal(size=3); ax[2] = 0.0; ax /= np.linalg.norm(ax)
        a = math.radians(lean); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        self.Rlean = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
        self.ph2, self.ph3 = rng.uniform(0, 2 * np.pi, 6), rng.uniform(0, 2 * np.pi, 6)
        self.A = np.full(6, inl) if tidy else rng.uniform(0.5, 1.0, 6) * inl
        self.phi = np.arange(6) * 1.3 if tidy else rng.uniform(0, 2 * np.pi, 6)
        self.off = off * SIGN if tidy else off * rng.choice([-1, 1], 6) * rng.uniform(0.5, 1.0, 6)
        self.dL1, self.dL2, self.dW = rng.uniform(-dl, dl, 3)
        self.tilt = rng.normal(0, 0.003, 2)
        self.o = rng.normal(0, 0.4, 2)
    def sag(self, th):
        """Pose-dependent deflection beyond the encoders (deg): the shoulder and elbow bend with the load torque, which
        follows the arm's own angles (the spring balances the weight at one pose only)."""
        d = np.zeros(6)
        d[1] = self.sagdeg * math.cos(th[1]); d[2] = self.sagdeg * math.cos(th[1] + th[2])
        return np.radians(d)
    def encode(self, th):
        q = 360.0 / 2 ** self.bits
        d = np.degrees(th) + self.A * (np.sin(th + self.phi) + self.harm * np.sin(2 * th + self.ph2) + 0.5 * self.harm * np.sin(3 * th + self.ph3))
        return np.radians(np.round(d / q) * q + self.off)
    def ik(self, Rt, pos):
        Ru = self.Rlean.T @ Rt; pu = self.Rlean.T @ (pos - ee.BASE) + ee.BASE       # undo the lean, solve the plain arm
        old = ee.W_LOCAL.copy(); ee.W_LOCAL = np.array([0.0, 0.0, W0 + self.dW])
        try: return np.array(ee.ik(Ru, pu, L1_0 + self.dL1, L2_0 + self.dL2))
        finally: ee.W_LOCAL = old
    def hit(self, th):
        pos, Rt = fk_batch(th[None, :], L1_0 + self.dL1, L2_0 + self.dL2, W0 + self.dW)
        pos = (self.Rlean @ (pos[0] - ee.BASE) + ee.BASE)[None, :]; Rt = self.Rlean @ Rt
        return hit_plane(pos, Rt, ZB, self.o, self.tilt)[0]

def make_poses(tr, n, window, target, rng, sigma_cam, hand=0.3, stand=2.0, dials0=(45.0, 30.0, -15.0)):
    """The hand puts the beam near the cross in a random orientation within the window (half-widths in deg for roll, hole, vertical).
    Returns encoder readings, camera readings and the true hit (board xy)."""
    enc, cam, hit = [], [], []
    tries = 0
    while len(enc) < n and tries < 40 * n:
        tries += 1
        r = dials0[0] + rng.uniform(-1, 1) * window[0]; h = dials0[1] + rng.uniform(-1, 1) * window[1]; v = dials0[2] + rng.uniform(-1, 1) * window[2]
        Rt = gun_rotation(v, h, r)
        d = Rt @ np.array([0.0, 0.0, -1.0])
        want = np.array([target[0] + rng.normal(0, hand), target[1] + rng.normal(0, hand), ZB])
        pos = want - (16.0 + rng.normal(0, stand)) * d
        try: th = tr.ik(Rt, pos)
        except (ValueError, ZeroDivisionError): continue
        if not np.all(np.isfinite(th)) or abs(th[4]) > math.radians(80): continue
        # the encoders read the joint; play and sag act beyond it, on the load path, so they move the real pose only
        real = tr.hit(th + rng.normal(0, np.radians(tr.play), 6) + tr.sag(th))
        enc.append(tr.encode(th)); hit.append(real[:2]); cam.append(real[:2] + rng.normal(0, sigma_cam, 2))
    return np.array(enc), np.array(cam), np.array(hit)

# ------------------------------------------------------------------ calibration
NP = 6 + 12 + 2 + 1 + 2 + 2 + 2 + 1
def model_hit(p, enc):
    off, c, s = p[0:6], p[6:12], p[12:18]
    th = enc - np.radians(off) - np.radians(c) * np.cos(enc) - np.radians(s) * np.sin(enc)
    pos, Rt = fk_batch(th, L1_0 + p[18], L2_0 + p[19], W0 + p[20])
    return hit_plane(pos, Rt, ZB + p[27], p[21:23], p[23:25])[:, :2]

def fit(enc, cam, use_harm=True, use_geom=True, sigma_cam=0.05, iters=40):
    p = np.zeros(NP)
    p[25:27] = (model_hit(p, enc) - cam).mean(0)               # frame shift between arm and camera
    free = np.ones(NP, bool)
    if not use_harm: free[6:18] = False
    if not use_geom: free[18:25] = False; free[27] = False
    prior_sd = np.array([1.0] * 6 + [1.5] * 12 + [5, 5, 5] + [2, 2] + [0.02, 0.02] + [1e3, 1e3] + [20])
    def resid(pv): return ((model_hit(pv, enc) - pv[25:27]) - cam).ravel() / max(sigma_cam, 1e-3)
    lam = 1e-3
    for it in range(iters):
        r0 = resid(p)
        J = np.zeros((r0.size, NP))
        for k in np.where(free)[0]:
            d = 1e-5 if k in (23, 24) else 2e-2
            dp = np.zeros(NP); dp[k] = d
            J[:, k] = (resid(p + dp) - resid(p - dp)) / (2 * d)
        Jf = J[:, free]; W = np.diag(1.0 / prior_sd[free] ** 2)
        step = np.linalg.solve(Jf.T @ Jf + W + lam * np.eye(Jf.shape[1]), -(Jf.T @ r0 + W @ p[free]))
        p[free] += step
        if np.linalg.norm(step) < 1e-8: break
    return p

def rms_err(model_xy, hit_true):
    e = model_xy - hit_true
    e = e - e.mean(0)                                          # a constant is removed by one touch-off
    return math.sqrt((e ** 2).sum(1).mean())

def experiment(n_fit=100, n_test=200, window=15, bits=12, inl=0.5, off=0.3, sigma_cam=0.05, play=0.01, seed=1,
               use_harm=True, use_geom=True, tidy=False, sag=0.0, test_window=None, harm=0.0, lean=0.0):
    rng = np.random.default_rng(seed)
    tr = Truth(rng, bits, inl, off, 2.0, play, tidy, sag, harm, lean)
    target = np.array([-100.0, -100.0])
    w = (window, window, window); wt = (test_window or window,) * 3
    enc, cam, _ = make_poses(tr, n_fit, w, target, rng, sigma_cam)
    encT, camT, hitT = make_poses(tr, n_test, wt, target, rng, sigma_cam)
    p0 = np.zeros(NP)
    u = rms_err(model_hit(p0, encT), hitT)
    p = fit(enc, cam, use_harm=use_harm, use_geom=use_geom, sigma_cam=sigma_cam)
    pc = p.copy()
    c = rms_err(model_hit(pc, encT) - pc[25:27], hitT)
    return dict(uncal=u, cal=c, params=p, n=len(enc))

if __name__ == '__main__':
    import time
    t0 = time.time()
    print('rms error of the arm\'s idea of where the beam met the board, 200 FRESH poses, constant removed (mm).  seeds averaged: 4')
    print('12 bit, zero offsets up to 0.3 deg, links off by up to 2 mm, camera 0.05 mm, hand +-0.3 mm of the cross, play 0.01 deg')
    for inl in (0.2, 0.5, 1.0):
        print('\nINL amplitude %.1f deg' % inl)
        print('  %-10s %-8s | %-10s %-10s' % ('window+-', 'touches', 'uncal', 'calibrated'))
        for win in (5, 10, 15, 25):
            for n in (40, 100, 200):
                res = [experiment(n_fit=n, window=win, inl=inl, seed=s) for s in range(4)]
                print('  %-10s %-8d | %-10.2f %-10.2f' % (win, n, np.mean([r['uncal'] for r in res]), np.mean([r['cal'] for r in res])), flush=True)
    print('elapsed %.0f s' % (time.time() - t0))
