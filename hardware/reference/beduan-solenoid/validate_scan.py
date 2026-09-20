"""Compare observed Beduan exterior points with its analytical CAD surfaces.

This is a scan-to-model distance check. Regional masks select physical features
and surface normals before any distances are computed; no distance-based inlier
filter is applied. Hidden model faces are not assessed against missing scans.
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
DEFAULT_ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-19-beduan-valve'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summary(distances):
    if not len(distances):
        return {'samples': 0}
    return {
        'samples': len(distances),
        'distance_p50_p90_p95_p99_max_mm': np.quantile(distances, [.5, .9, .95, .99, 1]).tolist(),
        'fraction_over_0_25mm': float(np.mean(distances > .25)),
        'fraction_over_0_5mm': float(np.mean(distances > .5)),
        'fraction_over_1mm': float(np.mean(distances > 1)),
    }


def feature_masks(points, normals, model):
    x, y, z = points.T
    nx, ny, nz = normals.T
    radial_xy = np.hypot(x, y)
    radial_xz = np.hypot(x, z - model.port_center_z)
    outward_xy = (x * nx + y * ny) / np.maximum(radial_xy, 1e-6)
    outward_xz = (x * nx + (z - model.port_center_z) * nz) / np.maximum(radial_xz, 1e-6)
    post_distance = np.min([np.hypot(x-cx, y-cy) for cx, cy in model.mounting_centers()], axis=0)
    masks = {
        'mounting_post_walls': (post_distance > 3) & (post_distance < 3.85) & (z > .8) & (z < 10) & (abs(nz) < .35),
        'mounting_post_end_annuli': (post_distance > 1.9) & (post_distance < 2.8) & (abs(z) < .4) & (nz < -.9),
        'lower_bearing_boss': (radial_xy < 12.7) & (z > 4.7) & (z < 10.7) & ((nz < -.7) | (outward_xy > .8)),
        'upper_moulded_body': (z > 11.5) & (z < 24.0) & (abs(y) < 16.9) & (abs(x) > 8) & (abs(nz) < .75),
        'cap_and_base_plate': (z > 24.6) & (z < 27.9) & (radial_xy > 12.5),
        'port_barrel_walls': (abs(y) > 19) & (abs(y) < 26.2) & (radial_xz > 7.0) & (radial_xz < 8.0) & (outward_xz > .8) & (abs(ny) < .4),
        'port_necks': (abs(y) > 14) & (abs(y) < 16) & (radial_xz > 5.7) & (radial_xz < 6.5) & (outward_xz > .8) & (abs(ny) < .4),
        'collet_ring_and_visible_mouths': (abs(y) > 28.3) & (abs(y) < 29.9) & (radial_xz > 2.7) & (radial_xz < 5.6) & (z < 20),
        'collet_collar_and_release_ears': (abs(y) > 27.3) & (abs(y) < 29.9) & (radial_xz > 5.8) & (radial_xz < 7.2) & (z < 20),
        'coil_cylinder': (z > 30) & (z < 49) & (abs(x) < 10) & (radial_xy > 10) & (radial_xy < 13.3) & (outward_xy > .8) & (abs(nz) < .4),
        'yoke_outer_walls': (abs(x) > 15.5) & (z > 32) & (z < 53) & (abs(y) < 7.8) & (abs(nx) > .9),
        'yoke_inner_walls': (abs(x) > 13.8) & (abs(x) < 15) & (z > 32) & (z < 52) & (abs(y) < 7.0) & (x * nx < 0) & (abs(nx) > .9),
        'yoke_top': (z > 56) & (z < 56.8) & (abs(x) < 13) & (abs(x) > 7) & (abs(y) < 6) & (nz > .9),
        'terminal_blades': (y > 20) & (y < 26.3) & (z > 51) & (z < 53.2) & (abs(x) > 4) & (abs(x) < 11) & (abs(nz) > .8),
        'terminal_block_and_roots': (y > 9.5) & (y < 18.7) & (z > 47) & (z < 57.6),
        'rounded_roof_extension': (z > 54.5) & (z < 56.8) & (abs(y) > 8.7) & (abs(y) < 14.6) & ((radial_xy < 12.8) | ((abs(x) < 5.5) & (y > 0))),
        'screw_head_envelopes': (post_distance < 3.6) & (z > 28.1) & (z < 30.6),
    }
    return masks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument('--voxel', type=float, default=.4)
    parser.add_argument('--tessellation', type=float, default=.04)
    args = parser.parse_args()
    sys.path.insert(0, str(args.archive / 'processing'))
    from cloud_tools import read_cloud, downsample
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    spec = importlib.util.spec_from_file_location('beduan_scan_check_model', HERE / 'beduan_solenoid.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    source_sha = sha256(HERE / 'beduan_solenoid.py')
    compound = model.build_beduan_solenoid().val()
    vertices, faces = compound.tessellate(args.tessellation, .1)
    mesh = trimesh.Trimesh(vertices=np.asarray([v.toTuple() for v in vertices]), faces=np.asarray(faces), process=False)
    cloud_path = args.archive / 'beduan-valve-measured-cloud.ply'
    cloud_sha = sha256(cloud_path)
    observations = downsample(read_cloud(cloud_path), args.voxel)
    points, normals = observations[:, :3], observations[:, 3:]
    distances = np.empty(len(points))
    closest = np.empty_like(points)
    for start in range(0, len(points), 1000):
        end = min(start + 1000, len(points))
        closest[start:end], distances[start:end], _ = trimesh.proximity.closest_point(mesh, points[start:end])
    np.savez_compressed(args.archive / "processing/evidence-cad-distances.npz", points=points, normals=normals, distances=distances, closest=closest)
    masks = feature_masks(points, normals, model)
    features = {name: summary(distances[mask]) for name, mask in masks.items()}
    report = {
        'units': 'mm',
        'method': 'Observed scan points to closest tessellated CAD component surface.',
        'model_source_sha256': source_sha,
        'observations_sha256': cloud_sha,
        'observation_voxel_mm': args.voxel,
        'cad_tessellation_tolerance_mm': args.tessellation,
        'cad_triangles': len(mesh.faces),
        'sampling': 'Deterministic first observation in each voxel; regional geometry and normal masks, with no distance-based exclusion.',
        'all_retained_observations': summary(distances),
        'features': features,
        'intentional_simplifications': ['Screw-drive recesses, stamped markings, coating texture and hidden interiors are not represented. Their observed points remain in the distance report.'],
        'limits': [
            'Distances include coating, scan registration disagreement, rounding and chosen analytical simplifications.',
            'The check establishes agreement with observations, not absolute dimensional accuracy.',
            'Scan-to-model distance does not establish that all unobserved model faces are correct.',
            'Selected regions are named exterior features, not a filtered global inlier population.',
        ],
    }
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    for ax, (a, b, title) in zip(axes, [(0, 2, 'X–Z'), (1, 2, 'Y–Z'), (0, 1, 'X–Y')]):
        order = np.argsort(distances)
        sc = ax.scatter(points[order, a], points[order, b], c=distances[order], s=1.1, cmap='turbo', vmin=0, vmax=1)
        ax.set_aspect('equal'); ax.set_title(title); ax.grid(alpha=.2)
    fig.colorbar(sc, ax=axes, label='Distance to CAD, mm (colors saturate at 1 mm)', fraction=.025, pad=.02)
    fig.suptitle('Beduan observed exterior → CAD; all sampled observations')
    fig.savefig(args.archive / 'processing/evidence-cad-residuals.png', dpi=170, bbox_inches='tight')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
