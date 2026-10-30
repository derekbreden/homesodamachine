"""Register the full-chain native capture to the separately scanned ASSE frame.

The marker table and exposed ASSE flats provide the initial frame. Rigid
point-to-plane registration uses only the ASSE body and vent. Fittings do not
participate in the registration, and no scale fit is allowed.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-asse1022-threaded-chain'
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud, plane, cylinder, unit, stats
from register_scan import voxel_sample


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_cloud(path, p, n):
    header = ('ply\nformat binary_little_endian 1.0\n'
              f'element vertex {len(p)}\n'
              + ''.join(f'property float {k}\n' for k in ('x', 'y', 'z', 'nx', 'ny', 'nz'))
              + 'end_header\n')
    path.write_bytes(header.encode() + np.column_stack([p, n]).astype('<f4').tobytes())


def table_frame(p):
    center = p.mean(0)
    _, _, vectors = np.linalg.svd(p - center, full_matrices=False)
    axis = vectors[0]
    d = p - center
    radial = np.linalg.norm(d - np.outer(d @ axis, axis), axis=1)
    # The complete chain is narrow. Distant observations belong to the marker
    # table, avoiding a false plane through the long row of wrench flats.
    sample = p[radial > 32][::2]
    rng = np.random.default_rng(71)
    best = None
    for _ in range(600):
        tri = sample[rng.choice(len(sample), 3, replace=False)]
        cross = np.cross(tri[1] - tri[0], tri[2] - tri[0])
        if np.linalg.norm(cross) < 1e-5:
            continue
        normal = unit(cross)
        hit = abs((sample - tri[0]) @ normal) < .3
        if hit.sum() < 50 or (best and hit.sum() <= best[0]):
            continue
        spread = np.linalg.svd(sample[hit] - sample[hit].mean(0), compute_uv=False) / np.sqrt(hit.sum())
        if spread[1] > 18:
            best = (int(hit.sum()), tri[0], normal)
    if best is None:
        raise ValueError('No broad marker-table plane was found')
    hit = (abs((p - best[1]) @ best[2]) < .4) & (radial > 28)
    center, normal, residual = plane(p[hit])
    normal *= np.sign(-center @ normal)
    x = unit(np.cross(normal, [1, 0, 0]))
    return center, np.array([x, np.cross(normal, x), normal]), residual


def initial_frame(raw, p, n):
    tc, tr, table_residual = table_frame(raw)
    raw_table = (raw - tc) @ tr.T
    table = (p - tc) @ tr.T
    high = raw_table[:, 2] > 14
    pc = raw_table[high].mean(0)
    _, _, vectors = np.linalg.svd(raw_table[high] - pc, full_matrices=False)
    axis = vectors[0].copy()
    axis[2] = 0
    axis = unit(axis) * np.sign(axis[0])
    pr = np.array([axis, np.cross([0, 0, 1], axis), [0, 0, 1]])
    q = (table - pc) @ pr.T
    nn = n @ tr.T @ pr.T
    records = {}
    for name, lo, hi, angles in [('outlet_cap', 1, 9, [25, 85, 145]),
                                  ('inlet_body', 18, 27, [26, 86, 146])]:
        normals, offsets, rows = [], [], []
        theta = np.degrees(np.arctan2(nn[:, 2], nn[:, 1]))
        for angle in angles:
            hit = ((q[:, 0] > lo) & (q[:, 0] < hi) & (table[:, 2] > 16)
                   & (abs(nn[:, 0]) < .15)
                   & (np.linalg.norm(q[:, 1:] - [0, -6], axis=1) < 18)
                   & (abs(theta - angle) < 4))
            c, normal, residual = plane(q[hit])
            normal *= np.sign(normal @ nn[hit].mean(0))
            normals.append(normal)
            offsets.append(normal @ c)
            rows.append({'normal': normal.tolist(), 'offset_mm': float(normal @ c),
                         'samples': int(hit.sum()), 'residual_mm': residual})
        normals = np.array(normals)
        _, _, vectors = np.linalg.svd(normals)
        a = vectors[-1] * np.sign(vectors[-1, 0])
        matrix = np.vstack([np.column_stack([normals, np.ones(3)]), [1, 0, 0, 0]])
        center_h = np.linalg.solve(matrix, [*offsets, 0])
        records[name] = {'planes': rows, 'axis': a.tolist(),
                         'axis_point': center_h[:3].tolist(),
                         'across_flats_mm': float(2 * center_h[-1])}
    a = unit(np.mean([v['axis'] for v in records.values()], axis=0))
    c = np.mean([v['axis_point'] for v in records.values()], axis=0)
    radial = q - [24.4, 1.0, 16.5]
    radial[:, 2] = 0
    facing = np.sum(radial * nn, axis=1) / np.maximum(np.linalg.norm(radial, axis=1), 1e-5)
    hit = ((q[:, 2] > 13) & (q[:, 2] < 19) & (q[:, 0] > 19)
           & (q[:, 0] < 30) & (abs(nn[:, 2]) < .5) & (facing > .7))
    vent = cylinder(q[hit][::3], [0, 0, 1], 3.45)
    va = np.array(vent['axis_direction'])
    z = -unit(va - (va @ a) * a)
    x = -a
    r = np.array([x, np.cross(z, x), z])
    vc = (np.array(vent['axis_point']) - c) @ r.T
    shift = np.array([24.65 - vc[0], 0, 27.45])
    transform = np.eye(4)
    transform[:3, :3] = r @ pr @ tr
    transform[:3, 3] = r @ (-pr @ (tr @ tc + pc) - c) + shift
    return transform, table[:, 2], {'table_plane_residual_mm': table_residual,
                                  'wrench_fits': records, 'vent_fit': vent}


def body_selection(p):
    radius = np.hypot(p[:, 1], p[:, 2] - 27.45)
    body = (p[:, 0] > 14) & (p[:, 0] < 48.5) & (radius < 17.8)
    vent = ((p[:, 0] > 19) & (p[:, 0] < 31) & (abs(p[:, 1]) < 7)
            & (p[:, 2] > .5) & (p[:, 2] < 13))
    return body | vent


def register_body(p, n, height, transform):
    evidence = json.loads((HERE.parent / 'multiplex-asse1022/scan-evidence.json').read_text())
    source = evidence['retained_cloud']
    target, normals, _ = load_cloud(source['path'], source['sha256'])
    target, normals = voxel_sample(target[body_selection(target)], normals[body_selection(target)], .25)
    initial = p @ transform[:3, :3].T + transform[:3, 3]
    hit = body_selection(initial) & (height > 16)
    samples, _ = voxel_sample(p[hit], n[hit], .3)
    tree = cKDTree(target)
    updates = []
    for _ in range(25):
        q = samples @ transform[:3, :3].T + transform[:3, 3]
        distance, index = tree.query(q)
        normal = normals[index]
        residual = np.sum((q - target[index]) * normal, axis=1)
        matrix = np.column_stack([np.cross(q, normal), normal])
        weight = 1 / np.sqrt(1 + (residual / .15) ** 2)
        delta = np.linalg.lstsq(matrix * weight[:, None], -residual * weight, rcond=None)[0]
        update = np.eye(4)
        update[:3, :3] = Rotation.from_rotvec(delta[:3]).as_matrix()
        update[:3, 3] = delta[3:]
        transform = update @ transform
        updates.append(float(np.linalg.norm(delta)))
        if np.linalg.norm(delta) < 1e-5:
            break
    q = samples @ transform[:3, :3].T + transform[:3, 3]
    distance, index = tree.query(q)
    return transform, {'source': source, 'sample_count': len(samples),
                       'method': 'Rigid point-to-plane ICP; soft residual weighting at 0.15 mm; all physically selected points retained.',
                       'update_norms': updates,
                       'nearest_source_distance_mm': stats(distance),
                       'signed_plane_residual_mm': stats(np.sum((q - target[index]) * normals[index], axis=1))}


def main():
    manifest = json.loads((ARCHIVE / 'capture-manifest.json').read_text())
    capture = manifest['passes'][0]
    raw_file = Path(capture['native_project_archive']) / 'raw_preview.ply'
    raw_sha = next(r['sha256'] for r in capture['native_files'] if r['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(raw_file, raw_sha)
    p, n, meta = load_cloud(capture['cloud'], capture['sha256'])
    transform, height, initial = initial_frame(raw, p, n)
    transform, registration = register_body(p, n, height, transform)
    q = p @ transform[:3, :3].T + transform[:3, 3]
    nn = n @ transform[:3, :3].T
    keep = ((height > 15.5) & (q[:, 0] > -40) & (q[:, 0] < 140)
            & (abs(q[:, 1]) < 24) & (q[:, 2] > -1) & (q[:, 2] < 45))
    out = ARCHIVE / 'registered-chain.ply'
    write_cloud(out, q[keep], nn[keep])
    radius = np.hypot(q[:, 1], q[:, 2] - 27.45)
    profile = []
    for lo in np.arange(-36, 120, .2):
        hit = keep & (q[:, 0] >= lo) & (q[:, 0] < lo + .2) & (radius < 18)
        if hit.sum() >= 10:
            profile.append({'x_mm': float(lo + .1), 'samples': int(hit.sum()),
                            'radius_p05_p50_p95_p99_mm': np.quantile(radius[hit], [.05, .5, .95, .99]).tolist()})
    report = {'units': 'mm', 'coordinate_scale_factor': 1.0,
              'capture': {k: v for k, v in manifest.items() if k != 'passes'},
              'native_project_archive': capture['native_project_archive'],
              'manifest_sha256': sha(ARCHIVE / 'capture-manifest.json'),
              'native_files': capture['native_files'], 'raw_preview': raw_meta, 'fused_cloud': meta,
              'native_to_reference': transform.tolist(), 'initial_frame': initial,
              'asse_registration': registration,
              'retained_cloud': {'path': str(out), 'sha256': sha(out), 'points': int(keep.sum())},
              'selection': 'Table height >15.5 mm; reference X -40..140, |Y|<24, Z -1..45 mm. No distance-to-CAD rejection.',
              'axial_profiles': profile,
              'limits': ['Optical scale and paint thickness are not independently calibrated.',
                         'Putty-hidden underside sectors use continuation of fitted analytic profiles.',
                         'The capture locates visible assembled surfaces, not hidden thread contacts, collet teeth, seals or pressure-bearing internals.']}
    (HERE / 'scan-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    cache = HERE.parents[2] / '.cache/asse-chain-scan'
    cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'registered.npz', p=q[keep], n=nn[keep], height=height[keep])
    print(json.dumps({'retained': int(keep.sum()), 'registration': registration,
                      'bounds_mm': [q[keep].min(0).tolist(), q[keep].max(0).tolist()]}, indent=2))


if __name__ == '__main__':
    main()
