#!/usr/bin/env python3
"""Read local tube end and barrel dimensions from the archived native fused cloud."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-20-lldpe-tubes'
CLOUD = ARCHIVE / 'pass-02-ends-30deg/Fused 0920_1 (0.10mm).ply'
SHA256 = '8ba10c2cc6d9ad7b2d180bee95a531d33d7d0287791fae84beb0e94a015e1a79'


def read_cloud():
    assert hashlib.sha256(CLOUD.read_bytes()).hexdigest() == SHA256
    with CLOUD.open('rb') as stream:
        header = []
        while True:
            line = stream.readline().decode().strip()
            header.append(line)
            if line == 'end_header':
                break
        assert [s for s in header if s.startswith('property')] == [
            'property float ' + n for n in ('x', 'y', 'z', 'nx', 'ny', 'nz')]
        data = np.frombuffer(stream.read(), dtype='<f4').reshape(-1, 6).copy()
    assert len(data) == 358070
    return data


def circle(points, start=None):
    if start is None:
        center = points.mean(0)
        start = np.r_[center, np.linalg.norm(points-center, axis=1).mean()]
    return least_squares(lambda a: np.linalg.norm(points-a[:2], axis=1)-a[2],
                         start, loss='soft_l1', f_scale=.025).x


def residual(a, points):
    axis = np.r_[a[2:4], 1.]
    axis /= np.linalg.norm(axis)
    delta = points - np.r_[a[:2], 11.]
    return np.linalg.norm(delta - np.outer(delta @ axis, axis), axis=1) - a[4]


def cylinder(q, lo, hi, start):
    a = start.copy()
    for _ in range(3):
        selected = (q[:, 2] > lo) & (q[:, 2] < hi) & (abs(residual(a, q)) < .3)
        a = least_squares(lambda a: residual(a, q[selected]), a,
                          loss='soft_l1', f_scale=.025).x
    return a, selected


def main():
    raw = read_cloud()
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    result = {
        'cloud': str(CLOUD), 'cloud_sha256': SHA256,
        'source': 'Revo Scan native 0.10 mm fused cloud; bare white LLDPE.',
        'scale': 1.0,
        'method': 'Independent manual spatial selections; PCA supplies an initial axis. '
                  'A robust five-parameter cylinder fits the outer barrel. A free plane fits '
                  'end-facing normals. An independent inner circle fits the shallow bore '
                  'projected perpendicular to the fitted barrel axis. No nominal dimension '
                  'enters a fit; no rescaling, surface smoothing or hole filling is applied.',
        'scope': 'Optical observations of these two samples. Residuals describe agreement '
                 'with the fused cloud, not dimensional accuracy or manufacturing tolerance. '
                 'The shallow visible bores do not establish bore shape through the tube. '
                 'The side-wall pass is archived but is not used in these end measurements.',
        'samples': []}
    for row, (name, nominal, xlo, xhi) in enumerate([
            ('3/8-inch sample', 9.525, 2., 25.),
            ('1/4-inch sample', 6.35, 26., 46.)]):
        selected = ((raw[:, 0] > xlo) & (raw[:, 0] < xhi) & (raw[:, 2] < 172.)
                    & (raw[:, 1] > -42.) & (raw[:, 1] < 15.))
        points, normals = raw[selected, :3], raw[selected, 3:]
        origin = points.mean(0)
        _, vectors = np.linalg.eigh(np.cov(points.T))
        axis = vectors[:, -1] * np.sign(vectors[2, -1])
        u = np.cross(axis, [1., 0., 0.]); u /= np.linalg.norm(u)
        basis = np.array([u, np.cross(axis, u), axis])
        q, n = (points-origin) @ basis.T, normals @ basis.T
        tmin = np.quantile(q[:, 2], .002); q[:, 2] -= tmin
        seed = circle(q[abs(q[:, 2]-11.) < .25, :2])
        start = np.r_[seed[:2], 0., 0., seed[2]]
        a, outer = cylinder(q, 8., 16., start)
        axis = np.r_[a[2:4], 1.]; axis /= np.linalg.norm(axis)
        u = np.cross(axis, [1., 0., 0.]); u /= np.linalg.norm(u)
        local_basis = np.array([u, np.cross(axis, u), axis])
        p, n = (q-np.r_[a[:2], 11.]) @ local_basis.T, n @ local_basis.T
        face = (abs(n[:, 2]) > .75) & (p[:, 2] < -7.)
        plane = least_squares(lambda a: p[face, 2]-p[face, :2]@a[:2]-a[2],
                              [0., 0., -10.], loss='soft_l1', f_scale=.025).x
        height = p[:, 2]-p[:, :2]@plane[:2]-plane[2]
        radius = np.linalg.norm(p[:, :2], axis=1)
        inner = ((height > .6) & (height < 3.) & (radius < a[4]-.45)
                 & (abs(n[:, 2]) < .65))
        inside = p[inner, :2]
        bore = circle(inside, [0., 0., np.median(radius[inner])])
        inliers = abs(np.linalg.norm(inside-bore[:2], axis=1)-bore[2]) < .2
        bore = circle(inside[inliers], bore)
        sensitivity = []
        for lo, hi in [(6., 12.), (8., 16.), (10., 18.)]:
            fit, fit_points = cylinder(q, lo, hi, start)
            sensitivity.append({'initial_axis_band_mm': [lo, hi],
                                'outer_diameter_mm': 2*fit[4],
                                'selected_points': int(fit_points.sum()),
                                'absolute_residual_p95_mm': float(np.quantile(
                                    abs(residual(fit, q[fit_points])), .95))})
        angles = np.arctan2(p[outer, 1], p[outer, 0])
        coverage = np.histogram(angles, bins=np.linspace(-np.pi, np.pi, 73))[0]
        item = {
            'sample': name, 'nominal_od_mm_identity_only': nominal,
            'world_selection_mm': {'x': [xlo, xhi], 'y': [-42., 15.], 'z_max': 172.},
            'points_in_selection': len(points),
            'initial_origin_mm': origin.tolist(), 'initial_basis': basis.tolist(),
            'initial_axial_zero_shift_mm': float(tmin),
            'cylinder_parameters': a.tolist(),
            'axis_in_native_cloud': (basis.T@axis).tolist(),
            'outer_diameter_mm': float(2*a[4]),
            'inner_diameter_mm': float(2*bore[2]),
            'derived_mean_wall_mm': float(a[4]-bore[2]),
            'outer_absolute_residual_p95_mm': float(np.quantile(abs(residual(a,q[outer])), .95)),
            'inner_absolute_residual_p95_mm': float(np.quantile(
                abs(np.linalg.norm(inside[inliers]-bore[:2],axis=1)-bore[2]), .95)),
            'outer_selected_points': int(outer.sum()),
            'inner_selected_points': int(inliers.sum()),
            'outer_observed_angular_bins': int((coverage >= 5).sum()),
            'outer_total_angular_bins': 72, 'angular_bin_degrees': 5,
            'inner_center_offset_in_local_plane_mm': bore[:2].tolist(),
            'cut_plane_local_coefficients': plane.tolist(),
            'cut_face_points': int(face.sum()),
            'cut_face_absolute_residual_p95_mm': float(np.quantile(abs(height[face]), .95)),
            'cut_plane_angle_to_perpendicular_degrees': float(np.degrees(np.arctan(np.linalg.norm(plane[:2])))),
            'outer_fit_band_sensitivity': sensitivity}
        result['samples'].append(item)
        ax = axes[row, 0]
        end = abs(height) < .2
        ax.scatter(p[end, 0], p[end, 1], s=1, color='#287b8e', rasterized=True)
        ax.set_aspect('equal'); ax.set_title(name + ': observed cut face')
        ax.set_xlabel('Local X (mm)'); ax.set_ylabel('Local Y (mm)')
        ax = axes[row, 1]
        ax.scatter(height[::5], radius[::5], s=.7, color='#287b8e', rasterized=True)
        ax.axhline(a[4],color='#bf6319',lw=1,label='Fitted outer radius')
        ax.axhline(bore[2],color='#7146a0',lw=1,label='Fitted shallow-bore radius')
        ax.set(xlim=(-1,20),ylim=(0,6),xlabel='Distance inward from cut plane (mm)',ylabel='Radius from barrel axis (mm)')
        ax.set_title(f'Observed OD {2*a[4]:.2f} mm / ID {2*bore[2]:.2f} mm')
        ax.legend(fontsize=8)
        print(name, 'OD', round(2*a[4],3), 'ID', round(2*bore[2],3),
              'OD sensitivity', [round(x['outer_diameter_mm'],3) for x in sensitivity])
    result['analysis_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/'scan-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    fig.suptitle('Bare LLDPE tube samples · native scale · optical observations')
    fig.tight_layout(); fig.savefig(HERE/'scan-sections.svg'); fig.savefig(HERE/'scan-sections.png',dpi=150)


if __name__ == '__main__':
    main()
