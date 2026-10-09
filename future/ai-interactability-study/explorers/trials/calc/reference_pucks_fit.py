"""What a board puck tells the camera, and what it lets the tube's own rim and ports say (wave 3, scene trials-22-reference-pucks).

Pinhole camera over the bore looking down; world +Z up, the plate face is z = 0, the tube's rim is at z = 6.35 + d (d = how much deeper this
tube's plate sits than nominal: [unknown], datum-19 and eyes-16 both need it).  Fisher (linearised) analysis, numerical Jacobians, 1-sigma.
Pose = 6 numbers (camera x, y, height, three small rotations).  Pixel noise on every feature 0.15 px unless stated.  f = 1500 px, 1280 x 960.

Three sets of features:
  BOARD  : the board puck: a 9 x 9 grid (12 mm pitch) in the plate plane, the seam ring (r = 61.85), two port circles (+-19.05, radius 5.55),
           and a raised ring at the nominal rim height (inner r 61.85, outer r 63.5) so the same fit code runs on the board and on a tube.
  TUBE   : what a real tube shows: rim ring (z = 6.35 + d) and the two ports (plate plane).  No grid.
  Both are 'known correspondences' (the ports give the roll modulo 180, a mark gives the rest), as in datum-19.

Questions answered:
  A. Camera pose from the board puck alone: 1-sigma of x, y, height (micrometres) and tilt (millidegrees) at camera heights 150, 300, 450 mm.
  B. Seat depth d of a tube from its own rim and ports with the pose free (datum-19's case) and with the pose given by the board (prior covariance from A,
     inflated for what the camera can have moved since: 0.05 mm and 0.005 deg between calibrations).
  C. Where the corner appears in the picture: error of the predicted corner position (mm at the station) for the two routes.
Run: python3 reference_pucks_fit.py
"""
import numpy as np

F = 1500.0
U0, V0 = 640.0, 480.0
RI, RO, PORT, PR = 61.85, 63.5, 19.05, 5.55
TAU = 2 * np.pi


def project(X, pose):
    """X: (n,3) world points; pose = [cx, cy, cz, rx, ry, rz]: camera at (cx,cy,cz) looking down (-Z), small rotations applied after."""
    cx, cy, cz, rx, ry, rz = pose
    P = X - np.array([cx, cy, cz])
    # base: camera x = world x, camera y = -world y, camera z = -world z (looking down)
    Q = np.stack([P[:, 0], -P[:, 1], -P[:, 2]], axis=1)
    cxr, sxr, cyr, syr, czr, szr = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cxr, -sxr], [0, sxr, cxr]])
    Ry = np.array([[cyr, 0, syr], [0, 1, 0], [-syr, 0, cyr]])
    Rz = np.array([[czr, -szr, 0], [szr, czr, 0], [0, 0, 1]])
    Q = Q @ (Rz @ Ry @ Rx).T
    return np.stack([U0 + F * Q[:, 0] / Q[:, 2], V0 + F * Q[:, 1] / Q[:, 2]], axis=1)


def circle(r, z, n, cx=0.0, cy=0.0):
    a = np.arange(n) * TAU / n
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a), np.full(n, z)], axis=1)


def board_points(rim_z=6.35):
    g = np.arange(-4, 5) * 12.0
    grid = np.array([[x, y, 0.0] for x in g for y in g])
    pts = [grid, circle(RI, 0.0, 24), circle(PORT, 0, 1)[:0]]
    for sx in (-1, 1):
        pts.append(circle(PR, 0.0, 8, sx * PORT, 0.0))
    pts += [circle(RI, rim_z, 24), circle(RO, rim_z, 24)]
    return np.vstack(pts)


def tube_points(d):
    pts = [circle(RI, 6.35 + d, 24), circle(RO, 6.35 + d, 24)]
    for sx in (-1, 1):
        pts.append(circle(PR, 0.0, 8, sx * PORT, 0.0))
    return np.vstack(pts)


def jac(fun, p, h):
    p = np.asarray(p, float)
    cols = []
    for j in range(len(p)):
        dp = np.zeros(len(p)); dp[j] = h[j]
        cols.append((fun(p + dp) - fun(p - dp)).ravel() / (2 * h[j]))
    return np.stack(cols, axis=1)


POSE_H = np.array([1e-3, 1e-3, 1e-3, 1e-7, 1e-7, 1e-7])


def cov_board(H, sig_px=0.15):
    pose0 = np.array([0, 0, H, 0, 0, 0.0])
    pts = board_points()
    J = jac(lambda p: project(pts, p), pose0, POSE_H)
    return np.linalg.inv(J.T @ J / sig_px ** 2)


def cov_tube(H, d=0.0, pose_prior=None, sig_px=0.15):
    """Unknowns: pose (6) and d.  pose_prior: covariance (6x6) of what the board says about the pose (None = pose free)."""
    pose0 = np.array([0, 0, H, 0, 0, 0.0])
    def model(q):
        return project(tube_points(q[6]), q[:6])
    q0 = np.concatenate([pose0, [d]])
    J = jac(model, q0, np.concatenate([POSE_H, [1e-3]]))
    I = J.T @ J / sig_px ** 2
    if pose_prior is not None:
        I[:6, :6] += np.linalg.inv(pose_prior)
    else:
        pass
    return np.linalg.inv(I), J


def corner_error(H, d, cov, sig_px=0.15):
    """1-sigma error (mm) of the predicted radial position of the corner at the station (61.85, 0, -(6.35+d) below the rim) as the camera sees it
    against a nominal one: propagate the parameter covariance through the mapping 'image point of the corner -> plate-plane position'.
    Approximation: the corner is on the plate plane z = 0 (the dot sits on the plate), rim reference at z = 6.35 + d; we report the sensitivity of the
    corner's image position to (pose, d) and convert with the local scale mm/px."""
    pose0 = np.array([0, 0, H, 0, 0, 0.0])
    corner = np.array([[RI, 0.0, 0.0]])
    def cimg(q):
        return project(corner, q[:6])[0]
    q0 = np.concatenate([pose0, [d]])
    Jc = jac(lambda q: cimg(q).reshape(1, 2), q0, np.concatenate([POSE_H, [1e-3]]))     # 2 x 7 (d does not move the corner: it is on the plate)
    var = Jc @ cov @ Jc.T
    scale = (H - 0.0) / F      # mm per pixel at the plate plane
    return np.sqrt(var[0, 0]) * scale, np.sqrt(var[1, 1]) * scale


if __name__ == '__main__':
    print('A. Camera pose from the board puck alone (0.15 px feature noise, 1-sigma)')
    print('   H (mm)   x,y (um)     height (um)   tilt (mdeg)   roll about the axis (mdeg)   mm per pixel at the plate')
    for H in (150, 300, 450):
        C = cov_board(H)
        sd = np.sqrt(np.diag(C))
        print(f'   {H:5d}   {sd[0]*1000:6.1f}/{sd[1]*1000:6.1f}   {sd[2]*1000:8.1f}      {np.degrees(sd[3])*1000:5.2f}/{np.degrees(sd[4])*1000:5.2f}      {np.degrees(sd[5])*1000:6.2f}                    {H/F:.3f}')
    print('   (a flat board at one pose cannot separate focal length from height; f is assumed known here.  Section D of the idea file says how f is found.)')
    print()
    print('B. Seat depth d of a tube from its rim and ports (0.15 px), pose free vs pose given by the board.  1-sigma in mm')
    print('   H (mm)   pose free   pose from board   with drift since calibration 0.05 mm & 0.005 deg')
    for H in (150, 300, 450):
        Cfree, _ = cov_tube(H)
        Cb = cov_board(H)
        Cpost, _ = cov_tube(H, pose_prior=Cb)
        drift = np.diag([0.05 ** 2, 0.05 ** 2, 0.05 ** 2, np.radians(0.005) ** 2, np.radians(0.005) ** 2, np.radians(0.005) ** 2])
        Cpd, _ = cov_tube(H, pose_prior=Cb + drift)
        print(f'   {H:5d}    {np.sqrt(Cfree[6,6]):6.3f}      {np.sqrt(Cpost[6,6]):6.3f}            {np.sqrt(Cpd[6,6]):6.3f}')
    print()
    print('C. Predicted corner position at the station (mm 1-sigma along the image x and y axes) from the two routes')
    print('   H (mm)   tube alone (pose free, d free)    board pose + tube (drift as above)')
    for H in (150, 300, 450):
        Cfree, _ = cov_tube(H)
        Cb = cov_board(H)
        drift = np.diag([0.05 ** 2] * 3 + [np.radians(0.005) ** 2] * 3)
        Cpd, _ = cov_tube(H, pose_prior=Cb + drift)
        a = corner_error(H, 0.0, Cfree); b = corner_error(H, 0.0, Cpd)
        print(f'   {H:5d}    {a[0]:.3f} / {a[1]:.3f}                         {b[0]:.3f} / {b[1]:.3f}')
    print()
    print('D. Seat repeatability of a puck (10 um per landing at the balls, ball circle 172 mm): lateral 20 um and vertical 4 um at the weld circle [swap_budget.py]')
    print('   so a calibration made on the board puck carries an extra 20 um lateral / 4 um vertical when read on any puck, and nothing else.')
