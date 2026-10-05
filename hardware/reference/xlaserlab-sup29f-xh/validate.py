#!/usr/bin/env python3
"""Check exported topology, symmetry, scale, openings and scan agreement."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import trimesh
from reconstruct import aligned_cloud, ROOT, NAME, WIRE_ORIGIN, WIRE_AXIS


def distances(mesh, points):
    values = []
    for start in range(0, len(points), 256):
        _, d, _ = trimesh.proximity.closest_point(mesh, points[start:start+256])
        values.extend(d.tolist())
    return np.array(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output'/NAME)
    args = parser.parse_args()
    output = args.output.resolve()
    path = output/(NAME+'.stl')
    mesh = trimesh.load_mesh(path)
    cad = trimesh.load_mesh(output/(NAME+'-cad.stl'))
    if not mesh.is_volume or len(mesh.split()) != 1 or not cad.is_volume:
        raise ValueError('Exported STL is not a valid closed volume')
    q, _ = aligned_cloud()
    rng = np.random.default_rng(2905)
    wire_t = (q-WIRE_ORIGIN) @ WIRE_AXIS
    wire_r = np.linalg.norm(np.cross(q-WIRE_ORIGIN, WIRE_AXIS), axis=1)
    groups = {
        'rear-housing': (q[:, 0] < -90.) & (q[:, 2] > -18.),
        'front-housing': (q[:, 0] > -90.) & (q[:, 0] < 0.) & (q[:, 2] > -19.),
        'grip': (q[:, 0] < -35.) & (q[:, 2] < -25.) & (q[:, 2] > -80.),
        'barrel-stem': (q[:, 0] > 28.) & (q[:, 0] < 61.) & (q[:, 2] > -10.),
        'barrel-sleeve': (q[:, 0] > 67.) & (q[:, 0] < 93.) & (q[:, 2] > -12.),
        'barrel-ring': (q[:, 0] > 7.) & (q[:, 0] < 17.) & (q[:, 2] > -15.),
        'wire-feed-hardware': (q[:, 0] > 0.) & (q[:, 2] < -21.) & (q[:, 2] > -65.),
        'wire-feed-guide': (wire_t < -50.) & (wire_t > -130.) & (wire_r < 8.)}
    comparison = {}
    for name, mask in groups.items():
        indices = np.flatnonzero(mask & (q[:, 1] >= 0.))
        indices = rng.choice(indices, min(3500, len(indices)), replace=False)
        result = {'observations': len(indices)}
        for label, model in [('detailed_stl', mesh), ('editable_cad', cad)]:
            d = distances(model, q[indices])
            result[label] = {'median_mm': float(np.median(d)),
                             'p95_mm': float(np.quantile(d, .95)),
                             'p99_mm': float(np.quantile(d, .99))}
        comparison[name] = result
        print(name, result['detailed_stl'], flush=True)

    v = mesh.vertices[rng.choice(len(mesh.vertices), 1800, replace=False)].copy()
    v[:, 1] *= -1.
    symmetry = distances(mesh, v)
    if symmetry.max() > .001:
        raise ValueError(f'Reflection discrepancy: {symmetry.max()} mm')
    probes = np.array([[x, y, z] for x in [15.8, 44.7]
                       for y in [-3., 0., 3.] for z in [-40., -30., -20.]])
    if mesh.contains(probes).any():
        raise ValueError('Wire-feed opening was closed')
    scene = trimesh.load(output/(NAME+'.glb'))
    # Convert the expected CAD bounds into glTF axes and metres.
    expected = np.array([[mesh.bounds[0, 0], mesh.bounds[0, 2], -mesh.bounds[1, 1]],
                          [mesh.bounds[1, 0], mesh.bounds[1, 2], -mesh.bounds[0, 1]]])*.001
    if not np.allclose(scene.bounds, expected, atol=.000001):
        raise ValueError('GLB scale/orientation differs from the STL')
    result = {
        'detailed_stl_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'mesh': {'watertight': bool(mesh.is_watertight),
                 'consistent_winding': bool(mesh.is_winding_consistent),
                 'volumes': len(mesh.split()),
                 'reflected_surface_probes': len(symmetry),
                 'reflection_max_surface_error_mm': float(symmetry.max())},
        'wire_feed_openings': {'axis': 'Z; gap between paired Y arms',
                               'probe_locations_mm': probes.tolist(), 'all_clear': True},
        'scan_to_model': comparison,
        'scan_comparison_scope':
            'Distances to retained-side observed surfaces. Inferred nozzle, front grip face, '
            'trigger and boot have no scan accuracy claim. Optical paint, scanner accuracy '
            'and physical mount fit are not bounded by these residuals.',
        'glb': {'coordinates': 'metres, Y-up', 'bounds_metres': scene.bounds.tolist()},
        'physical_mount_fit': 'Unmeasured'}
    (output/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['mesh'], indent=2), flush=True)


if __name__ == '__main__':
    main()
