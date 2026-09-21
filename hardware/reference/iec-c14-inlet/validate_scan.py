"""Compare the registered C14 scan with the analytical model, feature by feature.

Scan-to-model distances only: regional masks in the part frame pick physical
features by position and normal; no distance-based inlier filter is applied, so
a feature the model draws wrong shows up in its own row rather than vanishing.
Putty regions were removed when the registered cloud was written.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
DEFAULT_CLOUD = Path.home() / 'Documents/3D Scans/2026-09-21-iec-c14-inlet/c14-inlet-measured-cloud.ply'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_cloud(path):
    raw = Path(path).read_bytes()
    stop = raw.index(b'end_header\n') + len(b'end_header\n')
    count = int(next(line.split()[-1] for line in raw[:stop].decode().splitlines() if line.startswith('element vertex ')))
    data = np.frombuffer(raw, dtype='<f4', offset=stop).reshape(count, 6).astype(float)
    return data[:, :3], data[:, 3:]


def downsample(points, normals, voxel):
    _, idx = np.unique(np.floor(points / voxel).astype(np.int64), axis=0, return_index=True)
    return points[idx], normals[idx]


def summary(distances):
    if not len(distances):
        return {'samples': 0}
    return {'samples': int(len(distances)),
            'distance_p50_p90_p95_p99_max_mm': np.quantile(distances, [.5, .9, .95, .99, 1]).tolist(),
            'fraction_over_0_25mm': float(np.mean(distances > .25)),
            'fraction_over_0_5mm': float(np.mean(distances > .5))}


def feature_masks(p, n, m):
    x, y, z = p.T
    nx, ny, nz = n.T
    ear = (np.abs(x) > 14.5) & (np.abs(x) < 25.5)
    return {
        'flange_front_faces_ears': ear & (np.abs(y) < 0.6) & (ny > 0.9) & (np.hypot(np.abs(x) - m.SCREW_PITCH / 2, z) > 3.3),
        'flange_back_face': (np.abs(y + m.FLANGE_T) < 0.7) & (ny < -0.9) & (np.abs(x) < 25) & ((np.abs(x) > 13.5) | (np.abs(z) > 9.3)),
        'flange_outline_edges': (y > -2.9) & (y < -0.4) & (np.abs(ny) < 0.3) & (np.abs(x) < 25.5) & (np.abs(z) < 12),
        'screw_hole_walls': (y > -3.0) & (y < -1.4) & (np.abs(ny) < 0.4) & (np.hypot(np.abs(x) - m.SCREW_PITCH / 2, z) < 2.0),
        'countersinks': (y > -1.5) & (y < 0.2) & (np.abs(ny) > 0.5) & (np.abs(ny) < 0.85) & (np.hypot(np.abs(x) - m.SCREW_PITCH / 2, z) < 3.2),
        'rim_top_face': (y > 1.3) & (y < 2.4) & (ny > 0.9) & (np.abs(x) < 16) & (np.abs(z) < 11.5),
        'rim_outer_walls': (y > 0.3) & (y < 1.6) & (np.abs(ny) < 0.35) & (np.abs(x) < 17) & (np.abs(z) < 12) & ((np.abs(x) > 13.8) | (np.abs(z) > 9.0)),
        'cavity_mouth_walls': (y > -3.0) & (y < 1.6) & (np.abs(ny) < 0.35) & (np.abs(x) < 13.5) & (np.abs(z) < 8.8),
        'cavity_walls_deep': (y > -13.5) & (y < -3.0) & (np.abs(ny) < 0.35) & (np.abs(x) < 13.5) & (np.abs(z) < 8.8) & ((np.abs(x) > 10.5) | (np.abs(z) > 6.5)),
        'blades': (y > -13.5) & (y < -1.0) & (np.abs(x) < 9.5) & (np.abs(z) < 5.5) & ~((np.abs(z) > 4.5) & (np.abs(x) > 8)),
        'body_faces_x': (y > -16) & (y < -4) & (np.abs(nx) > 0.9) & (np.abs(z) < 6),
        'body_faces_z': (y > -16) & (y < -4) & (np.abs(nz) > 0.9) & (np.abs(x) < 8) & (np.abs(x) > 0),
        'body_lower_chamfers': (y > -16) & (y < -4) & (np.abs(nx) > 0.5) & (nz < -0.5) & (np.abs(x) > 6) & (z < -3),
        'body_end_face': (y > -17.4) & (y < -16.4) & (ny < -0.9) & (np.abs(x) < 13) & (np.abs(z) < 9),
        'tab_bosses': (y > -18.6) & (y < -16.95) & (np.abs(x) < 12) & (np.abs(z) < 9),
        'tabs': (y < -18.7) & (y > -25.2) & (np.abs(x) < 10) & (np.abs(z) < 7),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud', type=Path, default=DEFAULT_CLOUD)
    parser.add_argument('--voxel', type=float, default=.3)
    parser.add_argument('--tessellation', type=float, default=.03)
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    spec = importlib.util.spec_from_file_location('c14_scan_check_model', HERE / 'iec_c14_inlet.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    compound = model.build_iec_c14_inlet().val()
    vertices, faces = compound.tessellate(args.tessellation, .1)
    mesh = trimesh.Trimesh(vertices=np.asarray([v.toTuple() for v in vertices]), faces=np.asarray(faces), process=False)
    points, normals = downsample(*read_cloud(args.cloud), args.voxel)
    distances = np.empty(len(points)); closest = np.empty_like(points)
    for start in range(0, len(points), 2000):
        end = min(start + 2000, len(points))
        closest[start:end], distances[start:end], _ = trimesh.proximity.closest_point(mesh, points[start:end])
    masks = feature_masks(points, normals, model)
    # signed distance: positive where the observation lies outside the model along its own normal
    signed = np.sum((points - closest) * normals, axis=1)
    features = {}
    for name, mask in masks.items():
        row = summary(distances[mask])
        if mask.sum():
            row['signed_median_mm'] = float(np.median(signed[mask]))
        features[name] = row
    report = {
        'units': 'mm',
        'method': 'Registered scan observations to the closest tessellated model surface.',
        'model_source_sha256': sha256(HERE / 'iec_c14_inlet.py'),
        'observations_sha256': sha256(args.cloud),
        'observation_voxel_mm': args.voxel,
        'cad_tessellation_tolerance_mm': args.tessellation,
        'cad_triangles': int(len(mesh.faces)),
        'sampling': 'Deterministic first observation in each voxel; regional geometry and normal masks, no distance-based exclusion.',
        'all_retained_observations': summary(distances),
        'features': features,
        'intentional_simplifications': [
            'Blade and tab sections are IEC nominal; the tab holes, rim side windows, knuckle rounds and upper housing rounds are estimates.',
            'The ear front faces crown about 0.2 mm toward their tips; the model keeps them flat.',
            'The cavity floor is drawn at the deepest plane the scan reached; the blade roots below it are unobserved.'],
        'limits': [
            'Distances include the scan coating, registration disagreement between passes and the chosen simplifications.',
            'Agreement with the observations is not absolute dimensional accuracy.',
            'Unobserved model faces (the cavity floor, blade roots, tab undersides) are not assessed.'],
    }
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2) + '\n')
    np.savez_compressed(HERE / '.scan-check-cache.npz', points=points, normals=normals, distances=distances, closest=closest)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(21, 7))
    for ax, (cam, up, title) in zip(axes, [((0.55, 0.75, 0.45), (0, 0, 1), 'mating side'), ((-0.5, -0.7, 0.5), (0, 0, 1), 'wiring side'), ((0.35, 0.55, -0.75), (0, 0, 1), 'from below')]):
        cam = np.asarray(cam, float); cam /= np.linalg.norm(cam); right = np.cross(up, cam); right /= np.linalg.norm(right); up2 = np.cross(cam, right)
        u, w, depth = points @ right, points @ up2, points @ cam
        order = np.argsort(depth)
        sc = ax.scatter(u[order], w[order], c=distances[order], s=0.6, cmap='turbo', vmin=0, vmax=0.6, linewidths=0, rasterized=True)
        ax.set_aspect('equal'); ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(sc, ax=axes, label='distance to model, mm (saturates at 0.6)', fraction=.02, pad=.02)
    fig.suptitle('IEC C14 inlet: registered scan vs model')
    fig.savefig(HERE / 'scan-model-check.png', dpi=110, bbox_inches='tight')
    print(json.dumps({k: (round(v['distance_p50_p90_p95_p99_max_mm'][0], 3), round(v['distance_p50_p90_p95_p99_max_mm'][2], 3), round(v.get('signed_median_mm', 0), 3), v['samples']) for k, v in features.items()}, indent=1))
    print('all:', json.dumps(report['all_retained_observations']))


if __name__ == '__main__':
    main()
