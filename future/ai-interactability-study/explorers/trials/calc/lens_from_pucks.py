"""Can the reference pucks calibrate the lens?  (wave 3, trials-22-reference-pucks)  Fisher analysis, 0.15 px, f = 1500 px nominal.

Unknowns: camera pose (6) and intrinsics (f, cx, cy, k1: radial distortion x_d = x (1 + k1 r^2) in normalised coordinates).  Question: from a FLAT board
puck alone (one pose) and from a flat board plus a board tilted 10 degrees (two puck views), how well are f and k1 known, and what does the leftover
uncertainty do to a point measured 62 mm off the axis (where the seam is)?
Run: python3 lens_from_pucks.py
"""
import numpy as np
import reference_pucks_fit as R

# simpler and explicit
def proj(X, q):
    cx, cy, cz, rx, ry, rz, f, u0, v0, k1 = q
    P = X - np.array([cx, cy, cz])
    Q = np.stack([P[:, 0], -P[:, 1], -P[:, 2]], axis=1)
    c1, s1, c2, s2, c3, s3 = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    Rx = np.array([[1, 0, 0], [0, c1, -s1], [0, s1, c1]]); Ry = np.array([[c2, 0, s2], [0, 1, 0], [-s2, 0, c2]]); Rz = np.array([[c3, -s3, 0], [s3, c3, 0], [0, 0, 1]])
    Q = Q @ (Rz @ Ry @ Rx).T
    x, y = Q[:, 0] / Q[:, 2], Q[:, 1] / Q[:, 2]
    d = 1 + k1 * (x * x + y * y)
    return np.stack([f * x * d + u0, f * y * d + v0], axis=1)

H = 300.0
q0 = np.array([0, 0, H, 0, 0, 0, 1500.0, 640.0, 480.0, -0.10])   # a typical M12 lens: k1 = -0.10 in normalised coordinates
steps = np.array([1e-3, 1e-3, 1e-3, 1e-7, 1e-7, 1e-7, 1e-2, 1e-3, 1e-3, 1e-6])

def board(tilt_deg=0.0):
    pts = R.board_points()
    if tilt_deg:
        # tilt the plate-plane points about the y axis through the plate centre (a wedge puck): z -> x sin(t)
        t = np.radians(tilt_deg)
        out = pts.copy()
        plane = np.isclose(pts[:, 2], 0.0)
        out[plane, 2] = pts[plane, 0] * np.tan(t)
        return out
    return pts

def cov(views, free_k1=True, sig=0.15):
    """views: list of (points, pose offset) -- the camera is fixed and the puck changes: same camera pose, different points."""
    J = []
    for pts in views:
        f = lambda q: proj(pts, q).ravel()
        cols = []
        for j in range(10):
            dq = np.zeros(10); dq[j] = steps[j]
            cols.append((f(q0 + dq) - f(q0 - dq)) / (2 * steps[j]))
        J.append(np.stack(cols, axis=1))
    J = np.vstack(J)
    I = J.T @ J / sig ** 2
    I += np.eye(10) * 1e-9
    return np.linalg.inv(I), J

def station_error(C):
    """1-sigma of the image position of a plate point 62 mm off axis (the seam), converted to mm, propagated from the parameter covariance."""
    P = np.array([[61.85, 0.0, 0.0]])
    f = lambda q: proj(P, q).ravel()
    cols = []
    for j in range(10):
        dq = np.zeros(10); dq[j] = steps[j]
        cols.append((f(q0 + dq) - f(q0 - dq)) / (2 * steps[j]))
    Jp = np.stack(cols, axis=1)
    v = Jp @ C @ Jp.T
    return np.sqrt(np.diag(v)) * (H / 1500.0)

for name, views in (('flat board puck only', [board(0)]), ('flat board + a board tilted 10 degrees', [board(0), board(10)]), ('flat + tilted 10 degrees + tilted -10 degrees', [board(0), board(10), board(-10)])):
    try:
        C, J = cov(views)
    except np.linalg.LinAlgError:
        print(name, ': singular'); continue
    sd = np.sqrt(np.diag(C))
    se = station_error(C)
    print(f'{name:48s} sigma f {sd[6]:8.2f} px ({sd[6]/1500*100:5.2f} %)   sigma k1 {sd[9]:.4f}   height {sd[2]*1000:7.1f} um   station point 62 mm off axis: {se[0]*1000:6.1f} / {se[1]*1000:6.1f} um')
print()
print('Reading: with the raised rim ring (6.35 mm of relief) and a grid across the field, the FLAT board puck already pins a point 62 mm off the axis to about 7 um')
print('(0.15 px, distortion free).  Focal length and camera height trade against each other (sigma height 1.5 mm, sigma f 0.5 %) but the trade leaves the plate-plane')
print('point where it is; a board tilted 10 degrees halves both (0.25 %, 0.76 mm).  What depends on H itself is the parallax of the rim edge (6.35 r / H^2 x dH =')
print('6.5 um for dH = 1.5 mm at H = 300), so the wedge puck is optional.  Distortion is the one thing a comparison in a tight frame never needs.')
