#!/usr/bin/env python3
"""Fit the barrel midpoint and housing roll to the supplied partial scan."""
from pathlib import Path
import argparse
import json
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent


def fit():
    raw = np.load(HERE/'source/fused-scan.npz')['xyz_normals']
    origin0 = raw[:, :3].mean(axis=0)
    basis0 = np.linalg.eigh(np.cov(raw[:, :3].T))[1][:, ::-1].T
    if basis0[0, 0] > 0:
        basis0[0] *= -1
    if basis0[1, 1] < 0:
        basis0[1] *= -1
    basis0[2] = np.cross(basis0[0], basis0[1])
    q = (raw[:, :3]-origin0) @ basis0.T
    n = raw[:, 3:] @ basis0.T
    stem = (q[:, 0] > 85.) & (q[:, 0] < 105.) & (q[:, 1] > 0.)
    sleeve = (q[:, 0] > 118.) & (q[:, 0] < 137.) & (q[:, 1] > 0.)
    selected = stem | sleeve
    p = q[selected]
    labels = sleeve[selected].astype(int)

    def residual(a):
        centers = a[:2] + (p[:, 0]-100.)[:, None]*a[2:4]
        return np.linalg.norm(p[:, 1:]-centers, axis=1)-a[4:6][labels]

    a = least_squares(residual, [16.47, 5.67, -.045, -.025, 6.04, 8.95],
                      loss='soft_l1', f_scale=.03).x
    x = np.r_[1., a[2:4]]
    x /= np.linalg.norm(x)
    rear = (q[:, 0] < -40.) & (q[:, 1] > 8.) & (q[:, 1] < 32.) & (n[:, 2] < -.98)
    p2 = q[rear]
    plane = least_squares(
        lambda v: p2[:, 2]-np.c_[p2[:, :2], np.ones(len(p2))] @ v,
        [0., 0., -5.], loss='soft_l1', f_scale=.02).x
    y = np.r_[plane[:2], -1.]
    y -= x*(y @ x)
    y /= np.linalg.norm(y)
    basis = np.array([x, y, np.cross(x, y)])
    origin = np.r_[100., a[:2]]
    qq, nn = (q-origin) @ basis.T, n @ basis.T
    front = ((qq[:, 0] > -62.) & (qq[:, 0] < -51.) &
             (qq[:, 2] > -17.) & (qq[:, 2] < 18.) & (nn[:, 0] > .98))
    xf = np.median(qq[front, 0])
    qq[:, 0] -= xf
    origin += x*xf
    return {
        'native_to_model': {'origin': (origin0+origin @ basis0).tolist(),
                            'basis_rows': (basis @ basis0).tolist()},
        'cylinders': {'shared_parameters_pca': a.tolist(),
                      'radius_stem': float(a[4]), 'radius_sleeve': float(a[5]),
                      'residual_mm_p50_p95': np.quantile(abs(residual(a)), [.5, .95]).tolist()},
        'side_plane_pca': plane.tolist(), 'front_x_pca': float(origin[0]),
        'bounds_mm': [qq.min(0).tolist(), qq.max(0).tolist()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'alignment.json')
    args = parser.parse_args()
    args.output.write_text(json.dumps(fit(), indent=2)+'\n')
    print(args.output)


if __name__ == '__main__':
    main()
