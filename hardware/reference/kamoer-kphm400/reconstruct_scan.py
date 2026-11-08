#!/usr/bin/env python3
"""Reconstruct the purchased pump's observed exterior from its registered captures.

This manual reference preparation writes a closed native mesh for scan_model.rs.
It selects observed pump regions, independently of the holder's geometry.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from scipy.optimize import least_squares
import trimesh

from analyze_scan import bearing_frame, scan_observations
from register_scan import load_cloud, transform_points, voxel_sample

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def isolated(p, exposed):
    body = ((abs(p[:, 0]) < 38) & (p[:, 1] > -33) & (p[:, 1] < 33)
            & (p[:, 2] > -50.5) & (p[:, 2] < 74))
    outlets = ((abs(abs(p[:, 0]) - 29.875) < 8) & (p[:, 1] >= 24)
               & (p[:, 1] < 42) & (abs(p[:, 2] + 28.5) < 8))
    body &= ((p[:, 2] < 21) | ((abs(p[:, 0]) < 20) & (abs(p[:, 1]) < 20)))
    return (body | outlets) & exposed


def barrel_fit(p, n, exposed):
    selected = (exposed & (p[:, 2] > 29) & (p[:, 2] < 55)
                & (np.hypot(p[:, 0], p[:, 1]) > 16)
                & (np.hypot(p[:, 0], p[:, 1]) < 19.5) & (abs(n[:, 2]) < .15))
    q = p[selected]

    def residual(v):
        return np.linalg.norm(q[:, :2] - (v[:2] + (q[:, 2:3] - 42) * v[2:4]), axis=1) - v[4]

    fitted = least_squares(residual, [0, 0, 0, 0, 17.85], loss='soft_l1', f_scale=.05)
    return {'at_z_mm': 42., 'center_xy_mm': fitted.x[:2].tolist(),
            'axis_tilt_xy': fitted.x[2:4].tolist(), 'radius_mm': float(fitted.x[4]),
            'points': len(q), 'absolute_residual_p95_mm': float(np.quantile(abs(residual(fitted.x)), .95))}


def native_mesh(path, meshes):
    fields = {'names': ['observed-exterior'], 'colors': [None],
              'records': [[{'kind': 'MESH', 'src': str(Path(__file__).relative_to(ROOT)),
                            'op': 'registered scan reconstruction'}]]}
    mesh = trimesh.util.concatenate(meshes)
    arrays = {key: np.frombuffer(json.dumps(value).encode(), np.uint8) for key, value in fields.items()}
    np.savez_compressed(path, V0=np.asarray(mesh.vertices, np.float64),
                        T0=np.asarray(mesh.faces, np.uint32), F0=np.zeros(len(mesh.faces), np.uint32), **arrays)


def reconstruct(archive, out, runtime):
    sys.path.insert(0, str(runtime))
    import pymeshlab as ml
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    registration = json.loads((HERE / 'scan-registration.json').read_text())
    p, n, ids = scan_observations(evidence, registration, archive)
    p, n, exposed, _, frame = bearing_frame(p, n, ids)
    p[:, 2] -= 8
    selected = isolated(p, exposed)
    q, qn = voxel_sample(p[selected], n[selected], .20)
    print(f'Reconstructing {len(q)} observed samples', flush=True)
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertex_matrix=q, v_normals_matrix=qn))
    ms.generate_surface_reconstruction_screened_poisson(
        depth=10, pointweight=8, samplespernode=2, threads=1, preclean=True)
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_duplicate_faces()
    ms.meshing_repair_non_manifold_edges(method=0)
    ms.meshing_close_holes(maxholesize=1000, newfaceselected=False, selfintersection=True)
    mesh = trimesh.Trimesh(ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix(), process=True)
    components = sorted(mesh.split(only_watertight=False), key=lambda m: -len(m.faces))
    # Disconnected electrical tabs remain; tiny spray and fusion islands do not.
    components = [m for m in components if m.volume > 1]
    original_triangles = sum(len(m.faces) for m in components)
    ms = ml.MeshSet()
    whole = trimesh.util.concatenate(components)
    ms.add_mesh(ml.Mesh(vertex_matrix=whole.vertices, face_matrix=whole.faces))
    ms.meshing_decimation_quadric_edge_collapse(
        targetfacenum=90000, preservenormal=True, preservetopology=True,
        preserveboundary=True, qualitythr=.5, optimalplacement=True, planarquadric=True)
    whole = trimesh.Trimesh(ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix(), process=True)
    whole.fix_normals()
    if not whole.is_volume:
        raise ValueError('The reconstructed exterior is not a closed volume')
    out.mkdir(parents=True, exist_ok=True)
    native_mesh(out / 'observed-exterior.npz', [whole])
    report = {'schema': 1, 'unit': evidence['unit'], 'raw_clouds': evidence['clouds'],
              'registration_sha256': hashlib.sha256((HERE / 'scan-registration.json').read_bytes()).hexdigest(),
              'scale_factor': 1., 'bearing_frame': frame, 'bearing_to_flange_z_mm': -8.,
              'native_fit_stride': 6, 'native_validation_offset': 1, 'voxel_spacing_mm': .2,
              'screened_poisson': {'depth': 10, 'pointweight': 8, 'samplespernode': 2, 'threads': 1},
              'runtime': {'pymeshlab': '2025.7.post1'}, 'samples': len(q),
              'reconstructed_triangles': original_triangles, 'reference_triangles': len(whole.faces),
              'closed': bool(whole.is_volume), 'barrel_fit': barrel_fit(p, n, exposed),
              'scope': 'Observed exterior. Closed seams and occluded internals are not an internal pump model. Flexible sleeves are shown separately; inserted LLDPE stubs are excluded.',
              'limits': evidence['limits']}
    (out / 'scan-model-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'closed': report['closed'], 'triangles': len(whole.faces), 'barrel_fit': report['barrel_fit']}), flush=True)


def validate(model, out, archive):
    a = np.load(model)
    names = json.loads(a['names'].tobytes())
    meshes = [trimesh.Trimesh(a[f'V{i}'] - [35, 34, 0], a[f'T{i}'], process=False) for i in range(len(names))]
    model_mesh = trimesh.util.concatenate(meshes)
    report = json.loads(out.read_text())
    frame = report['bearing_frame']
    rotation = np.asarray(frame['common_to_bearing_rotation'])
    registration = json.loads((HERE / 'scan-registration.json').read_text())
    rows = []
    for pass_id, role, key in [(1, 'fixed', 'fixed_native_to_shared'), (2, 'moving', 'moving_native_to_shared_final')]:
        source = registration[role]
        old = Path(source['path'])
        p, n, meta = load_cloud(archive / old.parent.name / old.name)
        if meta['sha256'] != source['sha256']:
            raise ValueError('Raw validation cloud digest changed')
        transform = np.asarray(registration[key])
        common = transform_points(p[1::6], transform)
        p = (common - frame['origin_common']) @ rotation.T
        p[:, 2] -= 8
        exposed = common[:, 1] > -18 if pass_id == 1 else common[:, 1] < 16
        keep = isolated(p, exposed) & (p[:, 1] < 27.4)
        regions = {'head': p[:, 2] < -8.8,
                   'flange': (p[:, 2] > -8.8) & (p[:, 2] < .7),
                   'adapter': (p[:, 2] >= .7) & (p[:, 2] < 20.8),
                   'motor': p[:, 2] >= 20.8,
                   'rigid_casings': (abs(p[:, 0]) > 25) & (abs(p[:, 2] + 28.5) < 8) & (p[:, 1] > 16)}
        for region, mask in regions.items():
            q = p[keep & mask][::4]
            distances = []
            for start in range(0, len(q), 2000):
                distances.extend(trimesh.proximity.closest_point(model_mesh, q[start:start + 2000])[1])
            d = np.asarray(distances)
            rows.append({'pass': pass_id, 'region': region, 'points': len(q),
                         'median_mm': float(np.median(d)), 'p95_mm': float(np.quantile(d, .95)),
                         'p99_mm': float(np.quantile(d, .99)), 'max_mm': float(d.max())})
    report['held_out_validation'] = {'sampling': 'Disjoint native point indices; geometric selection only, no rejection by distance to model.',
                                     'rows': rows, 'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest()}
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(rows, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path, default=Path(json.loads((HERE / 'scan-evidence.json').read_text())['capture_archive']))
    parser.add_argument('--runtime', type=Path, default=ROOT / '.cache/runtimes/pymeshlab-2025.7.post1')
    parser.add_argument('--validate', type=Path)
    args = parser.parse_args()
    if args.validate:
        validate(args.validate, args.out, args.archive)
    else:
        reconstruct(args.archive, args.out, args.runtime)


if __name__ == '__main__':
    main()
