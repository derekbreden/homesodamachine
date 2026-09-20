"""Compare preserved DIGITEN exterior observations to the analytic reference.

Regional masks select physical features before distances are computed. There is
no distance-based inlier rejection. The flexible lead, support and alternate
collet configurations are excluded when preparing the observation cloud.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
DEFAULT_ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-20-flow-meter'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_cloud(path):
    with Path(path).open('rb') as stream:
        header = []
        while True:
            line = stream.readline()
            if not line:
                raise ValueError('Incomplete PLY header')
            header.append(line.decode().strip())
            if line.strip() == b'end_header':
                break
        if 'format binary_little_endian 1.0' not in header:
            raise ValueError('Expected binary little-endian PLY')
        count = int(next(s.split()[-1] for s in header if s.startswith('element vertex ')))
        properties = [s for s in header if s.startswith('property ')]
        if properties != [f'property float {p}' for p in ('x', 'y', 'z', 'nx', 'ny', 'nz')]:
            raise ValueError(f'Unexpected properties: {properties}')
        points = np.frombuffer(stream.read(), dtype='<f4').reshape(-1, 6).astype(float)
    if len(points) != count:
        raise ValueError('PLY vertex count mismatch')
    return points


def downsample(points, spacing):
    _, indices = np.unique(np.floor(points[:, :3] / spacing).astype(np.int64),
                           axis=0, return_index=True)
    return points[indices]


def summary(distances):
    return {
        'samples': len(distances),
        'distance_p50_p90_p95_p99_max_mm': np.quantile(distances, [.5, .9, .95, .99, 1]).tolist(),
        'fraction_over_0_25mm': float(np.mean(distances > .25)),
        'fraction_over_0_5mm': float(np.mean(distances > .5)),
        'fraction_over_1mm': float(np.mean(distances > 1)),
    }


def feature_masks(points):
    x, y, z = points[:, :3].T
    return {
        'mounting_collars': (abs(x) > 20) & (abs(x) < 26.3) & (np.hypot(y, z) > 8.5),
        'rotor_shell': (abs(x) < 10) & (y > -7) & (y < 6),
        'label_cover': (y > 16) & (abs(x) < 17),
        'underside': y < -8,
        'collet_configuration_04_05': abs(x) > 26.8,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument('--voxel', type=float, default=.3)
    parser.add_argument('--tessellation', type=float, default=.05)
    args = parser.parse_args()
    if args.voxel <= 0 or args.tessellation <= 0:
        parser.error('Spacing and tessellation tolerance must be positive')
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    source = HERE / 'digiten_flow_sensor.py'
    spec = importlib.util.spec_from_file_location('digiten_scan_check_model', source)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    source_sha = sha256(source)
    parts = [builder() for _, builder, _ in model._PARTS]
    if any(not shape.isValid() for shape in parts):
        raise ValueError('Invalid analytic model component')
    exterior = parts[0]
    for part in parts[1:]:
        exterior = exterior.fuse(part)
    exterior = exterior.clean()
    vertices, faces = exterior.tessellate(args.tessellation, .1)
    mesh = trimesh.Trimesh(vertices=np.asarray([v.toTuple() for v in vertices]),
                           faces=np.asarray(faces), process=False)
    cloud_path = args.archive / 'processing/measured-exterior.ply'
    observations = read_cloud(cloud_path)
    cloud_sha = sha256(cloud_path)
    evidence_path = HERE / 'scan-evidence.json'
    if evidence_path.exists():
        expected = json.loads(evidence_path.read_text())['registration']['merged_cloud_sha256']
        if cloud_sha != expected:
            raise ValueError('Observation SHA differs from scan-evidence.json')
    points = downsample(observations, args.voxel)
    distances = np.empty(len(points))
    closest = np.empty((len(points), 3))
    for start in range(0, len(points), 1000):
        end = min(start + 1000, len(points))
        closest[start:end], distances[start:end], _ = trimesh.proximity.closest_point(mesh, points[start:end, :3])
    report = {
        'units': 'mm',
        'method': 'Observed exterior points to closest tessellated surface of the fused analytic exterior.',
        'model_source_sha256': source_sha,
        'hash_scope': 'Exact full repository digiten_flow_sensor.py bytes; not Bazel-normalized producer bytes.',
        'validation_script_sha256': sha256(Path(__file__)),
        'observations_sha256': cloud_sha,
        'observation_count': len(observations),
        'observation_voxel_mm': args.voxel,
        'cad_tessellation_tolerance_mm': args.tessellation,
        'cad_triangles': len(mesh.faces),
        'sampling': 'Deterministic first observation per voxel; physical feature masks, with no distance-based exclusion.',
        'all_retained_observations': summary(distances),
        'features': {name: summary(distances[mask]) for name, mask in feature_masks(points).items()},
        'collet_configuration': 'Passes 04/05 only beyond the fixed collar; upright clip positions are excluded.',
        'intentional_simplifications': [
            'Small moulding blends, lettering, screw-drive recesses, surface texture and the underside centre recess.',
            'Hidden turbine, seals, electronics and unobserved bore depths are not reconstructed.',
            'The lead root is a routing envelope; the flexible pigtail is excluded.',
        ],
        'limits': [
            'Discrepancy includes registration disagreement, measurement noise, rounded dimensions and analytic simplifications.',
            'Neither fusion spacing nor residuals establish absolute dimensional accuracy or manufacturing tolerances.',
            'The scan does not establish the molded arrow direction or correctness of unobserved model faces.',
        ],
    }
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2) + '\n')
    np.savez_compressed(args.archive / 'processing/evidence-cad-distances.npz',
                        points=points, distances=distances, closest=closest)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    for ax, (i, j) in zip(axes, [(0, 2), (0, 1), (2, 1)]):
        order = np.argsort(distances)
        sc = ax.scatter(points[order, i], points[order, j], c=distances[order],
                        s=1.1, cmap='turbo', vmin=0, vmax=1)
        ax.set_aspect('equal')
        ax.set_xlabel('XYZ'[i]); ax.set_ylabel('XYZ'[j]); ax.grid(alpha=.2)
    fig.colorbar(sc, ax=axes, label='Distance to CAD, mm (colours saturate at 1 mm)', fraction=.025, pad=.02)
    fig.suptitle('DIGITEN observed exterior → CAD; all sampled observations')
    fig.savefig(args.archive / 'processing/evidence-cad-residuals.png', dpi=170, bbox_inches='tight')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
