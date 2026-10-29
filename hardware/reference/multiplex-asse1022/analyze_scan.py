"""Measure the coated ASSE exterior from its archived native MINI 2 capture.

The selections identify physical surfaces in this capture. No scale fit,
smoothing, mesh reconstruction or distance-to-CAD rejection is applied.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-multiplex-asse1022'
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import cylinder, load_cloud, plane, unit


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table_frame(raw):
    sample = raw[::max(1, len(raw) // 20000)]
    rng = np.random.default_rng(71)
    best = None
    for _ in range(800):
        tri = sample[rng.choice(len(sample), 3, replace=False)]
        cross = np.cross(tri[1] - tri[0], tri[2] - tri[0])
        if np.linalg.norm(cross) < 1e-6:
            continue
        normal = unit(cross)
        selected = abs((sample - tri[0]) @ normal) < .2
        if selected.sum() < 50 or (best and selected.sum() <= best[0]):
            continue
        spread = np.linalg.svd(sample[selected] - sample[selected].mean(0),
                               compute_uv=False) / np.sqrt(selected.sum())
        if spread[1] > 12:
            best = (selected.sum(), tri[0], normal)
    if best is None:
        raise ValueError('The broad marker-table plane was not found')
    selected = abs((raw - best[1]) @ best[2]) < .3
    center, normal, residual = plane(raw[selected])
    if (-center) @ normal < 0:
        normal = -normal
    x = unit(np.cross(normal, [1, 0, 0]))
    return center, np.vstack([x, np.cross(normal, x), normal]), residual


def write_cloud(path, p, n):
    header = ('ply\nformat binary_little_endian 1.0\n'
              f'element vertex {len(p)}\n'
              + ''.join(f'property float {k}\n' for k in ('x', 'y', 'z', 'nx', 'ny', 'nz'))
              + 'end_header\n')
    path.write_bytes(header.encode() + np.column_stack([p, n]).astype('<f4').tobytes())


def main():
    manifest = json.loads((ARCHIVE / 'capture-manifest.json').read_text())
    capture = manifest['passes'][0]
    native = Path(capture['native_project_archive'])
    raw_sha = next(r['sha256'] for r in capture['native_files'] if r['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(native / 'raw_preview.ply', raw_sha)
    p, n, cloud_meta = load_cloud(capture['cloud'], capture['sha256'])
    tc, tr, table_residual = table_frame(raw)
    table = (p - tc) @ tr.T
    raw_table = (raw - tc) @ tr.T
    high = (raw_table[:, 2] > 13) & (raw_table[:, 2] < 37)
    pc = raw_table[high].mean(0)
    _, _, vectors = np.linalg.svd(raw_table[high] - pc, full_matrices=False)
    pa = vectors[0].copy()
    pa[2] = 0
    pa = unit(pa)
    if pa[0] > 0:
        pa = -pa
    pr = np.array([pa, np.cross([0, 0, 1], pa), [0, 0, 1]])
    q = (table - pc) @ pr.T
    nn = n @ tr.T @ pr.T

    fits = {}
    for name, lo, hi in [('outlet_cap', -14, -5), ('inlet_body', 5, 13)]:
        rows, normals, offsets = [], [], []
        angle = np.degrees(np.arctan2(nn[:, 2], nn[:, 1]))
        for theta in [24, 84, 144]:
            selected = ((q[:, 0] > lo) & (q[:, 0] < hi) & (table[:, 2] > 14)
                        & (abs(nn[:, 0]) < .15)
                        & (np.linalg.norm(q[:, 1:] - [0, -6], axis=1) < 18)
                        & (abs(angle - theta) < 4))
            c, normal, residual = plane(q[selected])
            normal *= np.sign(normal @ nn[selected].mean(0))
            normals.append(normal)
            offsets.append(normal @ c)
            rows.append({'normal': normal.tolist(), 'offset_mm': float(normal @ c),
                         'observations': int(selected.sum()), 'residual_mm': residual,
                         'provisional_normal_angle_deg': theta})
        normals = np.array(normals)
        _, _, vectors = np.linalg.svd(normals)
        axis = vectors[-1] * np.sign(vectors[-1, 0])
        matrix = np.vstack([np.column_stack([normals, np.ones(3)]), [1, 0, 0, 0]])
        center_h = np.linalg.solve(matrix, [*offsets, 0])
        fits[name] = {'planes': rows, 'axis': axis.tolist(),
                      'axis_point': center_h[:3].tolist(),
                      'regular_hex_across_flats_mm': float(2 * center_h[-1]),
                      'provisional_axial_selection_mm': [lo, hi]}

    main_axis = unit(np.mean([f['axis'] for f in fits.values()], axis=0))
    main_center = np.mean([f['axis_point'] for f in fits.values()], axis=0)
    selected = ((q[:, 2] > 14) & (q[:, 2] < 20.5)
                & (q[:, 0] > 3) & (q[:, 0] < 13) & (abs(nn[:, 2]) < .5))
    radial = q - [8.16, 1.74, 17.4]
    radial[:, 2] = 0
    facing_out = np.sum(radial * nn, axis=1) / np.maximum(np.linalg.norm(radial, axis=1), 1e-5)
    selected &= facing_out > .7
    vent_fit = cylinder(q[selected][::2], [0, 0, 1], 3.45)
    vent_axis = unit(vent_fit['axis_direction'])
    z = -unit(vent_axis - (vent_axis @ main_axis) * main_axis)
    x = -main_axis
    r = np.array([x, np.cross(z, x), z])
    centered = (q - main_center) @ r.T
    normals = nn @ r.T
    vent_center = (np.array(vent_fit['axis_point']) - main_center) @ r.T

    # Fixed physical datums selected from the observed end rim and vent tip.
    # The model rounds these stations to 0.05 mm. They are not a scale correction.
    inlet_station, axis_height = -31.90, 27.45
    translation = np.array([-inlet_station, 0, axis_height])
    registered = centered + translation
    transform = np.eye(4)
    transform[:3, :3] = r @ pr @ tr
    transform[:3, 3] = r @ (-pr @ (tr @ tc + pc) - main_center) + translation
    keep = ((table[:, 2] > 15.5) & (registered[:, 0] > -.5)
            & (registered[:, 0] < 65.7) & (abs(registered[:, 1]) < 18.5)
            & (centered[:, 2] > -29) & (centered[:, 2] < 18))
    measured = ARCHIVE / 'asse-measured-cloud.ply'
    write_cloud(measured, registered[keep], normals[keep])

    radius = np.hypot(centered[:, 1], centered[:, 2])
    angle = np.degrees(np.arctan2(centered[:, 2], centered[:, 1]))
    corners = ((abs(angle + 60) < 6) | (abs(angle + 120) < 6))
    profile = []
    for lo in np.arange(-32, 33.2, .2):
        selected = ((centered[:, 0] >= lo) & (centered[:, 0] < lo + .2)
                    & (table[:, 2] > 16) & (radius < 18) & corners)
        if selected.sum() >= 10:
            profile.append({'x_mm': float(lo + .1 - inlet_station),
                            'observations': int(selected.sum()),
                            'radius_p05_p50_p95_p99_mm': np.quantile(radius[selected], [.05, .5, .95, .99]).tolist()})
    vr = np.hypot(centered[:, 0] - vent_center[0], centered[:, 1] - vent_center[1])
    vent_profile = []
    for lo in np.arange(-27.6, -14.4, .2):
        selected = (centered[:, 2] >= lo) & (centered[:, 2] < lo + .2) & (vr < 8)
        if selected.sum() >= 10:
            vent_profile.append({'z_mm': float(lo + .1 + axis_height),
                                 'observations': int(selected.sum()),
                                 'radius_p05_p50_p95_p99_mm': np.quantile(vr[selected], [.05, .5, .95, .99]).tolist()})

    report = {
        'units': 'mm', 'coordinate_scale_factor': 1.0,
        'capture': {k: v for k, v in manifest.items() if k != 'passes'},
        'manifest': {'path': str(ARCHIVE / 'capture-manifest.json'), 'sha256': sha(ARCHIVE / 'capture-manifest.json')},
        'native_files': capture['native_files'], 'native_project_archive': str(native),
        'sources': {'fused_cloud': cloud_meta, 'raw_preview': raw_meta},
        'native_to_reference': transform.tolist(),
        'table_plane_residual_mm': table_residual,
        'wrench_fits_in_provisional_frame': fits,
        'vent_cylinder_fit_in_provisional_frame': vent_fit,
        'vent_axis_to_flow_axis_degrees': float(np.degrees(np.arccos(abs(vent_axis @ main_axis)))),
        'vent_center_reference': (vent_center + translation).tolist(),
        'retained_cloud': {'path': str(measured), 'sha256': sha(measured), 'points': int(keep.sum())},
        'selection': {'table_height_min_mm': 15.5, 'reference_x_mm': [-.5, 65.7],
                      'reference_abs_y_max_mm': 18.5, 'axis_relative_z_mm': [-29, 18],
                      'purpose': 'Exclude the table and putty by a fixed support plane; no CAD-distance rejection.'},
        'axial_corner_profiles': profile, 'vent_radial_profiles': vent_profile,
        'limits': ['The coated optical scale and paint thickness are not independently calibrated.',
                   'One putty-mounted orientation leaves the lower body sectors unobserved; the CAD continues fitted regular hexes and turned profiles there.',
                   'The two fitted wrench axes differ slightly; the reference uses their mean axis and coaxial ports.',
                   'Threads use crest envelopes. Bore depths and pressure-bearing interiors are not established by this capture.'],
    }
    (HERE / 'scan-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'retained_points': int(keep.sum()),
                      'hex_across_flats_mm': {k: v['regular_hex_across_flats_mm'] for k, v in fits.items()},
                      'vent_diameter_fit_mm': 2 * vent_fit['radius_mm'],
                      'vent_center_reference': report['vent_center_reference']}, indent=2))


if __name__ == '__main__':
    main()
