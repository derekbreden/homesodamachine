"""Measure the WR1110 from archived native MINI 2 point clouds at unit scale.

The barrel axis, inlet face and wrench-flat normals define each part frame.
Only the upper hemisphere and exposed ends enter the merged observations;
putty and the table remain in the untouched captures.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-23-wr1110-regulator'
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import cylinder, cylinder_residual, load_cloud, plane, stats, unit
from register_scan import voxel_sample, compare


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
        residual = np.sum((sample - tri[0]) * normal, axis=1)
        selected = np.abs(residual) < .2
        if selected.sum() < 50 or (best is not None and selected.sum() <= best[0]):
            continue
        spread = np.linalg.svd(sample[selected] - sample[selected].mean(0),
                               compute_uv=False) / np.sqrt(selected.sum())
        # The marker-covered table spans two wide directions. A regulator flat
        # can be denser, but is only 20 mm wide and cannot satisfy this bound.
        if spread[1] > 12:
            best = (selected.sum(), tri[0], normal)
    if best is None:
        raise ValueError('No spatially broad table plane was found in the raw preview')
    selected = np.abs(np.sum((raw - best[1]) * best[2], axis=1)) < .3
    center, normal, residual = plane(raw[selected])
    if (-center) @ normal < 0:
        normal = -normal
    x = unit(np.cross(normal, [1, 0, 0]))
    rotation = np.vstack([x, np.cross(normal, x), normal])
    return center, rotation, residual


def local_frame(points, normals, raw, rolled=False):
    center, table_rotation, table_residual = table_frame(raw)
    q = (points - center) @ table_rotation.T
    n = normals @ table_rotation.T
    top = np.quantile(q[:, 2], .995)
    high = q[:, 2] > top - 15
    centroid = q[high].mean(0)
    _, _, vectors = np.linalg.svd(q[high][::8] - centroid, full_matrices=False)
    axis = vectors[0]
    along = (q - centroid) @ axis
    fit_selection = (np.abs(along) < 9) & (q[:, 2] > top - 10)
    fitted = cylinder(q[fit_selection][::8], axis, 9.5)
    axis = unit(fitted['axis_direction'])
    origin = np.array(fitted['axis_point'])
    t = (q - origin) @ axis
    radial = np.linalg.norm(q - origin - t[:, None] * axis, axis=1)
    ends = np.quantile(t[high], [.001, .999])
    first = high & (t < ends[0] + 4)
    last = high & (t > ends[1] - 4)
    if np.quantile(radial[first], .9) < np.quantile(radial[last], .9):
        axis = -axis
    x = unit(np.cross(axis, [0, 0, 1]))
    rotation = np.vstack([x, axis, np.cross(x, axis)])
    p = (q - origin) @ rotation.T
    m = n @ rotation.T
    radial = np.hypot(p[:, 0], p[:, 2])
    axial_min = np.quantile(p[high, 1], .001)
    face = ((p[:, 1] < axial_min + 1) & (m[:, 1] < -.96)
            & (radial > 7.2) & (radial < 9.0) & (p[:, 2] > -3))
    face_y = float(np.mean(p[face, 1]))
    p[:, 1] -= face_y
    flat = ((p[:, 1] > 2) & (p[:, 1] < 12) & (radial > 8.5)
            & (abs(m[:, 1]) < .1) & (p[:, 2] > -3))
    angle = np.arctan2(m[flat, 2], m[flat, 0])
    clock = np.angle(np.mean(np.exp(6j * angle))) / 6
    if rolled:
        clock += np.pi
    cs, sn = np.cos(clock), np.sin(clock)
    turn = np.array([[cs, 0, sn], [0, 1, 0], [-sn, 0, cs]])
    retained = ((p[:, 2] > -1) & (p[:, 1] > -.6) & (p[:, 1] < 65)
                & (radial < 12))
    p = p @ turn.T
    m = m @ turn.T
    transform = np.eye(4)
    transform[:3, :3] = turn @ rotation @ table_rotation
    transform[:3, 3] = turn @ (-rotation @ (table_rotation @ center + origin)
                               - np.array([0, face_y, 0]))
    fit_residual = cylinder_residual(q[fit_selection], fitted)
    return p[retained], m[retained], {
        'native_to_reference': transform.tolist(),
        'barrel_fit': fitted,
        'barrel_all_selected_residual_mm': stats(fit_residual),
        'inlet_face_axis_residual_mm': stats((q[face] - origin) @ axis - face_y),
        'table_plane_residual_mm': table_residual,
        'clock_degrees_from_table_frame': float(np.degrees(clock)),
        'retained_points': int(retained.sum()),
        'selection': 'Local table-up coordinate above -1 mm relative to the barrel axis; Y -0.6..65 mm; radial distance below 12 mm.',
    }


def axial_peaks(points, normals, sign, radial_band):
    r = np.hypot(points[:, 0], points[:, 2])
    sel = ((normals[:, 1] * sign > .96)
           & (r > radial_band[0]) & (r < radial_band[1]))
    hist, edges = np.histogram(points[sel, 1], bins=np.arange(-.5, 65, .025))
    peaks, _ = find_peaks(hist, prominence=100, distance=12)
    return [{'y_mm': float((edges[i] + edges[i+1]) / 2), 'count': int(hist[i])}
            for i in peaks]


def write_cloud(path, points, normals):
    values = np.column_stack([points, normals]).astype('<f4')
    header = ('ply\nformat binary_little_endian 1.0\n'
              f'element vertex {len(values)}\n'
              + ''.join(f'property float {name}\n' for name in ('x', 'y', 'z', 'nx', 'ny', 'nz'))
              + 'end_header\n')
    path.write_bytes(header.encode('ascii') + values.tobytes())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, default=ARCHIVE)
    args = ap.parse_args()
    archive = args.archive
    manifest = json.loads((archive / 'capture-manifest.json').read_text())
    points, normals, records = [], [], []
    for i, entry in enumerate(manifest['passes']):
        p, n, metadata = load_cloud(entry['cloud'], entry['sha256'])
        raw_sha = next(row['sha256'] for row in entry['native_files']
                       if row['file'] == 'raw_preview.ply')
        raw, _, raw_metadata = load_cloud(
            Path(entry['native_project_archive']) / 'raw_preview.ply', raw_sha)
        p, n, measured = local_frame(p, n, raw, rolled=i == 1)
        points.append(p); normals.append(n)
        records.append({'name': entry['name'], 'source': metadata,
                        'table_frame_source': raw_metadata, **measured})
        write_cloud(archive / f"{entry['name']}-registered.ply", p, n)
        print(entry['name'], 'barrel diameter', 2 * measured['barrel_fit']['radius_mm'],
              'retained', len(p), flush=True)
    p, n = np.concatenate(points), np.concatenate(normals)
    measured_cloud = archive / 'wr1110-measured-cloud.ply'
    write_cloud(measured_cloud, p, n)
    barrel = (p[:, 1] > 16) & (p[:, 1] < 49) & (abs(n[:, 1]) < .2)
    fitted = cylinder(p[barrel][::12], [0, 1, 0], 9.5)
    report = {
        'units': 'mm', 'scale_factor': 1.0,
        'capture_manifest_sha256': hashlib.sha256((archive / 'capture-manifest.json').read_bytes()).hexdigest(),
        'passes': records,
        'merged_cloud': {'path': str(measured_cloud), 'points': len(p),
                         'sha256': hashlib.sha256(measured_cloud.read_bytes()).hexdigest()},
        'barrel_fit': fitted,
        'barrel_all_selected_residual_mm': stats(cylinder_residual(p[barrel], fitted)),
        'inlet_facing_planes': axial_peaks(p, n, -1, (7.2, 9)),
        'outlet_facing_planes': axial_peaks(p, n, 1, (7.2, 9)),
        'axial_features': {},
        'limits': ['Native optical scale and spray thickness are not independently calibrated.',
                   'The hex clock is observable modulo 60 degrees; the owner-confirmed half turn selects the complementary hemisphere.',
                   'Internal pressure-control geometry and thread sealing are not measured by the exterior scan.'],
    }
    r = np.hypot(p[:, 0], p[:, 2])
    for name, sel in {
        'inlet_face': (p[:, 1] < .7) & (r > 7.2) & (r < 9) & (n[:, 1] < -.96),
        'outlet_hex_shoulder': (p[:, 1] > 54) & (p[:, 1] < 55)
                              & (r > 7.2) & (r < 9) & (n[:, 1] > .96),
        'outlet_tip_annulus': (p[:, 1] > 63) & (r > 3.6) & (r < 4.2) & (n[:, 1] > .9),
    }.items():
        report['axial_features'][name] = {
            'samples': int(sel.sum()),
            'y_p05_median_p95_mm': np.quantile(p[sel, 1], [.05, .5, .95]).tolist()}
    if len(points) == 2:
        seam = [(abs(pp[:, 2]) < .7) & (pp[:, 0] < -7) for pp in points]
        a, an = voxel_sample(points[0][seam[0]], normals[0][seam[0]], .2)
        b, bn = voxel_sample(points[1][seam[1]], normals[1][seam[1]], .2)
        report['pass_comparison'] = {
            'region': 'Observed overlap strip X < -7 mm and |Z| < 0.7 mm; the opposite side is not fully common to both retained hemispheres.',
            'first_to_second': compare(a, an, b, bn),
            'second_to_first': compare(b, bn, a, an)}
    (HERE / 'scan-measurements.json').write_text(json.dumps(report, indent=2) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(13, 8))
    for i, (pp, nn) in enumerate(zip(points, normals)):
        pp = pp[::12]
        for ax, (a, b) in zip(axs.ravel()[:3], [(1, 2), (1, 0), (0, 2)]):
            ax.scatter(pp[:, a], pp[:, b], s=.6, alpha=.5, label=f'Pass {i+1}')
            ax.set_aspect('equal'); ax.set_xlabel('XYZ'[a] + ', mm'); ax.set_ylabel('XYZ'[b] + ', mm')
        axs[1, 1].scatter(pp[:, 1], np.hypot(pp[:, 0], pp[:, 2]), s=.6, alpha=.5)
    for ax in axs.ravel():
        ax.grid(alpha=.2)
    axs[0, 0].legend()
    axs[1, 1].set_xlabel('Y, mm'); axs[1, 1].set_ylabel('Radius, mm')
    fig.suptitle('WR1110: independent native scan frames, putty excluded')
    fig.tight_layout(); fig.savefig(HERE / 'scan-profiles.png', dpi=150)
    print(json.dumps({'barrel': fitted, 'planes': report['outlet_facing_planes']}, indent=2))


if __name__ == '__main__':
    main()
