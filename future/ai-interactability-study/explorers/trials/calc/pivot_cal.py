"""Pivot calibration of the dot in the shell frame: tilt the shell about the assumed dot while the dot rests on a board;
if the assumed dot is d mm off along the beam, the real dot wanders on the board. Solve for d (and lateral offsets) by least squares.

ILLUSTRATIVE: tilt range, board-reading noise, the offsets. The technique is the standard 'pivot calibration' for tracked
tools; the geometry below is first-order.
"""
import numpy as np
rng = np.random.default_rng(3)
def run(true_off=(0.0, 0.0, 3.0), tilts_deg=(-12, -6, 0, 6, 12), noise_mm=0.03, n_dirs=8):
    """true_off = (ox, oy, oz) dot offset from the assumed dot, in the shell frame (z along the beam, toward the board).
    Software rotates the shell about the ASSUMED dot (fixed point on the board) by tilt t about direction phi (tilt axis).
    The real dot = R * true_off + assumed; its board position moves. We observe board xy of the real dot (a board gives x,y)."""
    rows, obs = [], []
    for t in tilts_deg:
        for k in range(n_dirs):
            phi = 2*np.pi*k/n_dirs
            axis = np.array([-np.sin(phi), np.cos(phi), 0.0])      # tilt axis in the board plane, beam along -z (pointing at the board)
            th = np.radians(t)
            K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
            R = np.eye(3) + np.sin(th)*K + (1-np.cos(th))*K@K
            p = R @ np.array(true_off)                               # real dot relative to the assumed dot, world
            obs.append(p[:2] + rng.normal(0, noise_mm, 2))
            rows.append(R[:2, :])                                    # p_xy = R[:2,:] @ off
    A = np.vstack(rows); b = np.hstack([o for o in obs])
    b = np.array(obs).reshape(-1)
    A = np.vstack(rows)
    # p_xy(off) = R[:2,:] off ; the tilt=0 rows give ox, oy directly; the tilted rows give oz
    est, res, rk, sv = np.linalg.lstsq(A, b, rcond=None)
    return est
for noise in (0.01, 0.03, 0.1, 0.3):
    e = run(noise_mm=noise)
    print(f"board noise {noise:4.2f} mm -> estimated dot offset (x,y,z) = {np.round(e,3)}  (true 0, 0, 3 mm)")
print("Range of tilt matters: with only +-2 deg the z estimate is poor:")
for tl in ((-2, 0, 2), (-6, 0, 6), (-12, -6, 0, 6, 12)):
    zs = [run(tilts_deg=tl, noise_mm=0.05)[2] for _ in range(50)]
    print(f"  tilts {tl}: z estimate mean {np.mean(zs):.2f}, sd {np.std(zs):.2f} mm (noise 0.05 mm on the board)")
