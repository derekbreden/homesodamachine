"""Measure the prepared YZMSZ exterior from its preserved native MINI 2 scan.

The table plane, long cylindrical housing and exposed inlet mouth establish a
rigid frame at native scale. Physical selections precede any CAD comparison.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import median_filter

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-yzmsz-water-regulator'
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud, plane, stats, unit


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
        hit = abs((sample - tri[0]) @ normal) < .2
        if hit.sum() < 50 or (best is not None and hit.sum() <= best[0]):
            continue
        spread = np.linalg.svd(sample[hit] - sample[hit].mean(0), compute_uv=False) / np.sqrt(hit.sum())
        if spread[1] > 12:
            best = (int(hit.sum()), tri[0], normal)
    if best is None:
        raise ValueError('No broad marker-table plane found')
    c, z, residual = plane(raw[abs((raw - best[1]) @ best[2]) < .3])
    z *= np.sign(-c @ z)
    x = unit(np.cross(z, [1, 0, 0]))
    return c, np.array([x, np.cross(z, x), z]), residual


def initial_frame(raw):
    center, rotation, residual = table_frame(raw)
    q = (raw - center) @ rotation.T
    high = q[:, 2] > 15
    pc = q[high].mean(0)
    _, _, vectors = np.linalg.svd(q[high] - pc, full_matrices=False)
    x = vectors[0].copy(); x[2] = 0
    x = unit(x) * np.sign(x[0])
    r = np.array([x, np.cross([0, 0, 1], x), [0, 0, 1]])
    return center, rotation, pc, r, residual


def housing_axis(p, n, height):
    hit = ((p[:, 0] > -4) & (p[:, 0] < 14) & (height > 15)
           & (abs(n[:, 0]) < .25) & (abs(p[:, 1]) < 16))
    q = p[hit][::3]

    def unpack(v):
        return np.array([0, v[0], v[1]]), unit([1, v[2], v[3]])

    def residual(v):
        c, a = unpack(v)
        relative = q - c
        t = relative @ a
        radius = np.linalg.norm(relative - t[:, None] * a, axis=1)
        return radius - v[4] - v[5] * t

    fit = least_squares(residual, [0, -4, 0, 0, 12.5, 0],
                        loss='soft_l1', f_scale=.08,
                        bounds=([-5, -10, -.15, -.15, 10, -.06],
                                [5, 2, .15, .15, 15, .06]))
    c, x = unpack(fit.x)
    z = unit(np.array([0, 0, 1]) - x * x[2])
    r = np.array([x, np.cross(z, x), z])
    return c, r, {'selection': 'Initial axial -4..14 mm, table height >15 mm, |normal.X|<0.25, |Y|<16 mm',
                  'samples': len(q), 'axis_point_initial_mm': c.tolist(),
                  'axis_direction_initial': x.tolist(), 'radius_at_initial_x_zero_mm': float(fit.x[4]),
                  'radial_draft_per_mm': float(fit.x[5]), 'residual_mm': stats(residual(fit.x))}


def write_cloud(path, p, n):
    header = ('ply\nformat binary_little_endian 1.0\n' + f'element vertex {len(p)}\n'
              + ''.join(f'property float {k}\n' for k in ('x', 'y', 'z', 'nx', 'ny', 'nz'))
              + 'end_header\n')
    path.write_bytes(header.encode() + np.column_stack([p, n]).astype('<f4').tobytes())


def simplify(points, tolerance=.04):
    points = np.asarray(points)
    if len(points) <= 2:
        return points.tolist()
    predicted = np.interp(points[:, 0], points[[0, -1], 0], points[[0, -1], 1])
    error = abs(points[:, 1] - predicted)
    i = int(np.argmax(error))
    if error[i] <= tolerance:
        return points[[0, -1]].tolist()
    return simplify(points[:i+1], tolerance)[:-1] + simplify(points[i:], tolerance)


def main():
    manifest = json.loads((ARCHIVE / 'capture-manifest.json').read_text())
    capture = manifest['passes'][0]
    raw_path = Path(capture['native_project_archive']) / 'raw_preview.ply'
    raw_sha = next(f['sha256'] for f in capture['native_files'] if f['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(raw_path, raw_sha)
    p, n, meta = load_cloud(capture['cloud'], capture['sha256'])
    tc, tr, pc, pr, table_residual = initial_frame(raw)
    table = (p - tc) @ tr.T
    initial = (table - pc) @ pr.T
    c, r, axis_fit = housing_axis(initial, n @ tr.T @ pr.T, table[:, 2])
    q = (initial - c) @ r.T
    nn = n @ tr.T @ pr.T @ r.T
    radius = np.hypot(q[:, 1], q[:, 2])
    keep = ((table[:, 2] > 15) & (q[:, 0] > -35) & (q[:, 0] < 40) & (radius < 16))
    mouths = {}
    for name, lo, hi, sign in [('inlet', -31.9, -31.0, -1), ('outlet', 35.9, 36.8, 1)]:
        hit = (keep & (q[:, 0] > lo) & (q[:, 0] < hi) & (radius > 5.5)
               & (radius < 6.5) & (nn[:, 0] * sign > .9))
        x = float(np.median(q[hit, 0]))
        mouths[name] = {'initial_x_mm': x, 'samples': int(hit.sum()),
                        'selection': f'Initial X {lo}..{hi} mm; radius 5.5..6.5 mm; axial outward normal >0.9',
                        'axial_residual_mm': stats(q[hit, 0] - x)}
    inlet = mouths['inlet']['initial_x_mm']
    length = mouths['outlet']['initial_x_mm'] - inlet
    q[:, 0] -= inlet
    cache = HERE.parents[2] / '.cache/yzmsz-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'axis-cloud.npz', p=q[keep], n=nn[keep], height=table[keep, 2])
    profile = []
    facing = (q[:, 1] * nn[:, 1] + q[:, 2] * nn[:, 2]) / np.maximum(radius, 1e-8)
    for x in np.arange(.075, length, .15):
        hit = keep & (abs(q[:, 0] - x) < .075) & (facing > .1)
        if hit.sum() >= 12:
            profile.append({'x_mm': float(x), 'samples': int(hit.sum()),
                            'radius_p05_p50_p75_p95_mm': np.quantile(radius[hit], [.05, .5, .75, .95]).tolist()})
    outline = np.array([[r['x_mm'], r['radius_p05_p50_p75_p95_mm'][3]] for r in profile])
    outline[:, 1] = median_filter(outline[:, 1], 3, mode='nearest')
    outline = np.vstack([[0, outline[0, 1]], outline, [length, outline[-1, 1]]])
    windows = []
    theta = np.degrees(np.arctan2(q[:, 2], q[:, 1]))
    for angle in [30, 140, -150]:
        angular = abs((theta - angle + 180) % 360 - 180)
        hit = (keep & (q[:, 0] > -15.5-inlet) & (q[:, 0] < -13.7-inlet)
               & (radius > 10.8) & (radius < 11.9) & (angular < 15))
        center, normal, residual = plane(q[hit])
        normal *= np.sign(normal @ nn[hit].mean(0))
        windows.append({'initial_angle_degrees': angle, 'samples': int(hit.sum()),
                        'bottom_plane_center_mm': center.tolist(), 'bottom_plane_normal': normal.tolist(),
                        'bottom_plane_residual_mm': residual})
    transform = np.eye(4)
    transform[:3, :3] = r @ pr @ tr
    transform[:3, 3] = r @ (-pr @ (tr @ tc + pc) - c) - [inlet, 0, 0]
    out = ARCHIVE / 'registered-yzmsz.ply'
    write_cloud(out, q[keep], nn[keep])
    evidence = {'units': 'mm', 'coordinate_scale_factor': 1.0, 'capture': manifest,
                'raw_preview': raw_meta, 'fused_cloud': meta, 'table_plane_residual_mm': table_residual,
                'housing_axis_fit': axis_fit, 'mouth_fits': mouths, 'window_bottom_fits': windows,
                'native_to_reference': transform.tolist(),
                'selection': 'Table height >15 mm; initial axis X -35..40 mm; radius <16 mm. No CAD-distance rejection.',
                'retained_cloud': {'path': str(out), 'sha256': sha(out), 'points': int(keep.sum())},
                'axial_profiles': profile,
                'limits': ['Paint thickness and optical scale are not independently calibrated.',
                           'Putty-hidden lower sectors continue the fitted rotational exterior.',
                           'Window cutters approximate the exposed openings; the obscured fourth window follows opposing symmetry.',
                           'Collet finger gaps, embossed lettering and the flow arrow are omitted.',
                           'Mouth recesses and 15 mm insertion are display estimates; hidden regulator internals and seals are unqualified.']}
    (HERE / 'scan-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    release_recesses = {}
    for name, x0, sign in [('inlet', 0, 1), ('outlet', length, -1)]:
        inward = (q[:, 0] - x0) * sign
        points = []
        for station in np.arange(.25, 3.01, .5):
            hit = (keep & (abs(inward-station) < .2) & (radius > 4.2)
                   & (radius < 6.4) & (facing > .5))
            points.append([float(station), float(np.median(radius[hit]))])
        release_recesses[name] = {'inner_profile_inward_radius_mm': [[0, points[0][1]], *points, [3.35, 6.5]],
                                  'outer_radius_mm': 6.5,
                                  'scope': 'Rotational approximation to the visible split-collet recess; obscured floor is a display closure.'}
    parameters = {'units': 'mm', 'length_mm': length,
                  'profile_x_radius_mm': [[round(x, 4), round(radius, 4)] for x, radius in simplify(outline)],
                  'profile_method': '95th percentile of outward-facing radius in 0.15 mm axial bins; three-bin median; 0.04 mm radial simplification.',
                  'windows': {'x_range_mm': [-15.9-inlet, -13.2-inlet], 'tangent_width_mm': 8.5,
                              'bottom_radius_mm': 11.35, 'angles_degrees': [30, 140, 210, 320],
                              'scope': 'Approximate opening edges and flat bottoms; fourth opening continued by opposing symmetry.'},
                  'release_recesses': release_recesses,
                  'tube_od_mm': 6.35, 'insertion_estimate_mm': 15.,
                  'scan_evidence_sha256': sha(HERE / 'scan-evidence.json')}
    (HERE / 'reference-parameters.json').write_text(json.dumps(parameters, indent=2) + '\n')
    print(json.dumps({'retained': int(keep.sum()), 'axis_fit': axis_fit,
                      'bounds_mm': [q[keep].min(0).tolist(), q[keep].max(0).tolist()]}, indent=2))


if __name__ == '__main__':
    main()
