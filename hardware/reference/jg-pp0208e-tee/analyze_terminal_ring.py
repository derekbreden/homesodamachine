#!/usr/bin/env python3
"""Read terminal-ring evidence without changing the registered scan frame or scale.

The merged scan's sleeve state is unknown. This report separates the terminal
surface from the larger fixed reduced barrel; it does not claim an exact seam,
production tolerance, minimum rim thickness, or physical release force.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
import trimesh

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stats(residual):
    return {
        'count': len(residual),
        'signed_median_mm': float(np.median(residual)),
        'absolute_p95_mm': float(np.quantile(abs(residual), .95)),
        'absolute_max_mm': float(np.max(abs(residual))),
    }


def main():
    registration = json.loads((HERE/'scan-registration.json').read_text())
    operating = json.loads((HERE/'branch-operating-measurements.json').read_text())
    path = Path(registration['mesh_archive_path'])
    if sha(path) != registration['mesh_sha256']:
        raise ValueError('Archived scan digest differs from its registered frame')
    mesh = trimesh.load(path, process=False)
    origin = np.array(registration['frame']['origin_in_scan_mm'])
    basis = np.array(registration['frame']['reference_axes_in_scan_columns'])
    points = (mesh.triangles_center-origin) @ basis
    normals = mesh.face_normals @ basis
    areas = mesh.area_faces
    radial = np.linalg.norm(points[:, [0, 2]], axis=1)

    mask = ((points[:, 1] > 20.0) & (points[:, 1] < 20.75)
            & (radial > 4.5) & (radial < 6.0) & (abs(normals[:, 1]) < .35))
    p = points[mask]
    weights = np.sqrt(areas[mask] / np.mean(areas[mask]))
    heldout = np.arange(len(p)) % 2 == 1
    mid = 20.375

    def wall_residual(a):
        t = p[:, 1]-mid
        return (np.hypot(p[:, 0]-a[0]-a[2]*t, p[:, 2]-a[1]-a[3]*t)
                - a[4]-a[5]*t)

    fit = least_squares(lambda a: (wall_residual(a)*weights)[~heldout],
                        [0, 0, 0, 0, 5.3, 0], loss='soft_l1', f_scale=.05)
    residual = wall_residual(fit.x)
    angles = np.arctan2(p[:, 2]-fit.x[1], p[:, 0]-fit.x[0])
    wall_report = {
        'selection': 'Y20.0..20.75, radius4.5..6.0, absolute axial normal below0.35.',
        'mid_station_mm': mid,
        'diameter_at_mid_station_mm': float(2*fit.x[4]),
        'center_at_mid_station_xz_mm': fit.x[:2].tolist(),
        'axis_slopes_xz_per_y': fit.x[2:4].tolist(),
        'radius_taper_per_y': float(fit.x[5]),
        'angular_bins_10_degrees_present': int(np.count_nonzero(
            np.histogram(angles, 36, (-np.pi, np.pi))[0])),
        'all_surface_residual': stats(residual),
        'held_out_surface_residual': stats(residual[heldout]),
        'qualification': 'Approximate observed terminal surface only; reconstructed wall distortion and unknown sleeve state prevent an exact seam/OD claim.',
    }

    face_mask = ((points[:, 1] > 21.0) & (points[:, 1] < 21.8)
                 & (radial > 3.6) & (radial < 5.1) & (normals[:, 1] > .85))
    face = points[face_mask]
    weights = np.sqrt(areas[face_mask] / np.mean(areas[face_mask]))
    heldout = np.arange(len(face)) % 2 == 1

    def face_residual(a):
        return face[:, 1]-a[0]-face[:, 0]*a[1]-face[:, 2]*a[2]

    fit_face = least_squares(lambda a: (face_residual(a)*weights)[~heldout],
                             [21.35, 0, 0], loss='soft_l1', f_scale=.03)
    fixed = []
    for axis, sign, label, near in ((1, 1, 'branch', 17),
                                    (2, 1, 'run_plus', 15),
                                    (2, -1, 'run_minus', 15)):
        t = sign*points[:, axis]
        radius = np.linalg.norm(np.delete(points, axis, 1), axis=1)
        selected = ((t > near) & (t < 23) & (radius > 6) & (radius < 7.8)
                    & (abs(normals[:, axis]) > .65))
        fixed.append({'arm': label, 'count': int(sum(selected)),
                      'outer_face_station_quantiles_mm': dict(zip(
                          ('p95', 'p99', 'p99_9', 'max'),
                          np.quantile(t[selected], [.95, .99, .999, 1]).tolist()))})

    nominal = operating['derived_nominal_stations']
    observed = float(fit_face.x[0])
    report = {
        'scope': __doc__,
        'input_sha256': {'scan': sha(path), 'scan-registration.json': sha(HERE/'scan-registration.json'),
                         'branch-operating-measurements.json': sha(HERE/'branch-operating-measurements.json')},
        'source_sha256': sha(__file__), 'scale': 1.0,
        'method': 'Registered triangle centers and areas; alternate selected triangles held out of area-weighted soft-L1 fits. No scan rescaling or collet relocation.',
        'terminal_wall': wall_report,
        'terminal_face': {'axis_intercept_y_mm': observed,
                          'plane_slopes_xz': fit_face.x[1:].tolist(),
                          'all_surface_residual': stats(face_residual(fit_face.x)),
                          'held_out_surface_residual': stats(face_residual(fit_face.x)[heldout])},
        'fixed_reduced_barrel_face_candidates': fixed,
        'capture_state': {
            'nominal_extended_y_mm': nominal['extended_branch_face_from_run_axis_mm'],
            'nominal_pressed_y_mm': nominal['pressed_branch_face_from_run_axis_mm'],
            'observed_face_y_mm': observed,
            'inference': 'The observed face lies between the measured nominal pressed and extended stations. Its state is intermediate or merged; it cannot qualify an absolute moving-ring seam.'},
        'release_qualification': {
            'exact_terminal_od_qualified': False, 'exact_terminal_seam_qualified': False,
            'physical_release_qualified': False,
            'circular_bore_diameter_mm': 8.5,
            'approximate_fitted_radial_bearing_mm': float(fit.x[4]-8.5/2),
            'qualification': 'This approximate radial difference is not a guaranteed minimum annular bearing or a manufacturing tolerance.'},
    }
    (HERE/'terminal-ring-scan.json').write_text(json.dumps(report, indent=2)+'\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4.8))
    selected = ((points[:, 1] > 16) & (points[:, 1] < 23)
                & (radial > 3) & (radial < 9))
    ax.scatter(points[selected, 1][::3], radial[selected][::3], s=1.2,
               c='#65828e', alpha=.28, rasterized=True)
    ax.axvspan(20, 20.75, color='#12879c', alpha=.13, label='Fitted terminal side-wall patch')
    ax.axvline(observed, color='#12879c', lw=2, label=f'Observed terminal face Y{observed:.3f}')
    for value, label in ((nominal['pressed_branch_face_from_run_axis_mm'], 'Measured nominal pressed'),
                         (nominal['extended_branch_face_from_run_axis_mm'], 'Measured nominal extended')):
        ax.axvline(value, color='#a66225', ls='--', lw=1.5, label=f'{label} Y{value:.2f}')
    ax.axhline(4.25, color='#202e38', ls=':', label='Circular release bore R4.25')
    ax.set(xlabel='Branch station from registered run axis [mm]', ylabel='Radius from registered branch axis [mm]',
           xlim=(16, 23), ylim=(3, 9), title='PP0208E terminal ring — unknown captured sleeve state')
    ax.legend(fontsize=8, loc='upper right');ax.grid(alpha=.15)
    fig.text(.5, .015, f'Approximate terminal OD {2*fit.x[4]:.2f} mm; held-out radial p95 {wall_report["held_out_surface_residual"]["absolute_p95_mm"]:.3f} mm. Exact seam and OD remain unqualified.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .045, 1, 1])
    fig.savefig(HERE/'terminal-ring-scan.svg')
    fig.savefig('/tmp/scanner-review/tee-branch-propagation/terminal-ring-scan.png', dpi=160)
    print(json.dumps({'terminal_wall': wall_report, 'terminal_face': report['terminal_face']}, indent=2))


if __name__ == '__main__':
    main()
