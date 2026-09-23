#!/usr/bin/env python3
"""Read all three collets of the PP0208E, pass by pass.

The three ports carry the same collet. Each of the five native passes is registered onto the
merged scan's production frame by a trimmed point-to-plane ICP, and each port's collet is read
there: its front face as a plane, the fixed barrel face behind it, and its side wall. A collet
is loose in its port and can shift between passes, so a pass is a single captured state where
the merged mesh blends them.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
import trimesh

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-09-19-jg-pp0208e-tee/passes'
PASSES = {
    'pass-1-1716-f346c65f.ply': '985418dcf35de9065eb97ef1c21acea1ec384b04f8c1f68d5fef6ee92e8f326a',
    'pass-2-1946-4934837e.ply': 'e7409306a5faf8072ab01be37e7163efdfd92d9a8b4a6b5f222920663b905b05',
    'pass-3-1959-0d8a423d.ply': '3fffe22bac5d082d33cf1860286e96bad75bd626ef69244f39f166836dc42bfe',
    'pass-4-2011-b0a6db20.ply': '62b8fcd527410ca7da287bf90163eaed69fa8bfa751128b964f3d35d0f5294bb',
    'pass-5-2025-fafe8d00.ply': '0e10c4c421733d3f6823a83e15890843b18f8d59715e6c2b0d80adfc7ebc697c',
}
# (port, axis index, sign, face search window, barrel-face search window), stations in mm
PORTS = (('branch', 1, 1, (19.8, 23.3), (18.4, 20.4)),
         ('run_plus', 2, 1, (18.3, 22.4), (16.8, 19.0)),
         ('run_minus', 2, -1, (18.3, 22.4), (16.8, 19.0)))
MIN_SECTORS = 30        # of 36; fewer reads a partial arc, and partial arcs read diameters low
BORE_FILLED = 0.10      # outward points inside r3.0 per point on the face annulus


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_cloud(path):
    raw = Path(path).read_bytes()
    end = raw.index(b'end_header\n') + len(b'end_header\n')
    header = raw[:end].decode()
    count = int(header.split('element vertex ')[1].split()[0])
    props = [line.split()[-1] for line in header.splitlines() if line.startswith('property')]
    data = np.frombuffer(raw[end:end + 4 * len(props) * count], dtype='<f4')
    data = data.reshape(count, len(props)).astype(float)
    col = {name: i for i, name in enumerate(props)}
    return data[:, [col['x'], col['y'], col['z']]], data[:, [col['nx'], col['ny'], col['nz']]]


def rotation(v):
    angle = np.linalg.norm(v)
    if angle < 1e-12:
        return np.eye(3)
    k = v / angle
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K


def principal(X):
    centre = np.median(X, axis=0)
    _, vectors = np.linalg.eigh(np.cov((X - centre).T))
    return centre, vectors[:, ::-1]


def register(source, target, normals, tree):
    """Best of the right-handed principal-axis starts, each refined by trimmed ICP."""
    tc, tv = principal(target)
    sc, sv = principal(source)
    best = None
    for signs in np.array(np.meshgrid([1, -1], [1, -1], [1, -1])).T.reshape(-1, 3):
        R = tv @ np.diag(signs) @ sv.T
        if np.linalg.det(R) < 0:
            continue
        t = tc - R @ sc
        for i in range(60):
            X = source @ R.T + t
            d, j = tree.query(X)
            keep = d < max(3.0 * 0.85 ** i, 0.35)
            if keep.sum() < 200:
                break
            x, y, n = X[keep], target[j[keep]], normals[j[keep]]
            step, *_ = np.linalg.lstsq(np.c_[np.cross(x, n), n],
                                       np.einsum('ij,ij->i', y - x, n), rcond=None)
            dR = rotation(step[:3])
            R, t = dR @ R, dR @ t + step[3:]
        d = tree.query(source @ R.T + t)[0]
        inliers = d < 0.35
        fraction = float(inliers.mean())
        median = float(np.median(d[inliers])) if inliers.any() else np.inf
        if (best is None or fraction > best[2] + .02
                or (abs(fraction - best[2]) <= .02 and median < best[3])):
            best = (R, t, fraction, median)
    return best


def read_port(P, N, axis, sign, face_window, barrel_window):
    t = sign * P[:, axis]
    q = np.delete(P, axis, 1)
    r = np.linalg.norm(q, axis=1)
    outward = sign * N[:, axis]
    face = (outward > .8) & (r > 3.4) & (r < 5.3) & (t > face_window[0]) & (t < face_window[1])
    barrel = (outward > .8) & (r > 5.6) & (r < 7.4) & (t > barrel_window[0]) & (t < barrel_window[1])
    if face.sum() < 40 or barrel.sum() < 40:
        return {'seen': False}
    fit = least_squares(lambda a: t[face] - a[0] - q[face, 0] * a[1] - q[face, 1] * a[2],
                        [np.median(t[face]), 0, 0], loss='soft_l1', f_scale=.05)
    residual = t[face] - fit.x[0] - q[face, 0] * fit.x[1] - q[face, 1] * fit.x[2]
    barrel_face = float(np.median(t[barrel]))
    wall = (abs(outward) < .3) & (r > 4.6) & (r < 5.8) & (t > barrel_face + .25) & (t < fit.x[0] - .4)
    angles = np.arctan2(q[face, 1], q[face, 0])
    filled = (outward > .8) & (r < 3.0) & (t > barrel_face) & (t < fit.x[0] + 1.0)
    return {
        'seen': True,
        'face_station_mm': float(fit.x[0]),
        'face_tilt_deg': float(np.degrees(np.arctan(np.hypot(fit.x[1], fit.x[2])))),
        'face_residual_abs_p95_mm': float(np.quantile(abs(residual), .95)),
        'face_sectors_of_36': int(np.count_nonzero(np.histogram(angles, 36, (-np.pi, np.pi))[0])),
        'barrel_face_station_mm': barrel_face,
        'protrusion_beyond_barrel_face_mm': float(fit.x[0] - barrel_face),
        'side_wall_diameter_mm': float(2 * np.median(r[wall])) if wall.sum() > 20 else None,
        'side_wall_points': int(wall.sum()),
        'bore_filled_ratio': float(filled.sum() / face.sum()),
    }


def main():
    registration = json.loads((HERE / 'scan-registration.json').read_text())
    operating = json.loads((HERE / 'branch-operating-measurements.json').read_text())
    merged_path = Path(registration['mesh_archive_path'])
    if sha(merged_path) != registration['mesh_sha256']:
        raise ValueError('Merged scan digest differs from its registered frame')
    for name, digest in PASSES.items():
        if sha(ARCHIVE / name) != digest:
            raise ValueError(f'{name} differs from its recorded digest')
    origin = np.array(registration['frame']['origin_in_scan_mm'])
    basis = np.array(registration['frame']['reference_axes_in_scan_columns'])
    merged = trimesh.load(merged_path, process=False)
    target = (merged.vertices - origin) @ basis
    normals = merged.vertex_normals @ basis
    tree = cKDTree(target)

    stations = operating['derived_nominal_stations']
    calipered = {'branch': (stations['pressed_branch_face_from_run_axis_mm'],
                            stations['extended_branch_face_from_run_axis_mm']),
                 'run': (39.2 / 2, 42.5 / 2)}
    passes = {}
    for name in PASSES:
        points, point_normals = read_cloud(ARCHIVE / name)
        sample = points[np.random.default_rng(0).choice(len(points), min(20000, len(points)), replace=False)]
        R, t, inlier_fraction, inlier_median = register(sample, target, normals, tree)
        P, N = points @ R.T + t, point_normals @ R.T
        ports = {}
        for port, axis, sign, face_window, barrel_window in PORTS:
            reading = read_port(P, N, axis, sign, face_window, barrel_window)
            if reading['seen']:
                pressed, extended = calipered['branch' if port == 'branch' else 'run']
                reading['calipered_stroke_fraction'] = (reading['face_station_mm'] - pressed) / (extended - pressed)
                reading['clean'] = (reading['face_sectors_of_36'] >= MIN_SECTORS
                                    and reading['bore_filled_ratio'] < BORE_FILLED)
            ports[port] = reading
        passes[name] = {'registration_inlier_fraction': inlier_fraction,
                        'registration_inlier_median_mm': inlier_median,
                        'rotation': R.tolist(), 'translation_mm': t.tolist(), 'ports': ports}

    clean = [(p, port, reading) for p, record in passes.items() for port, reading in record['ports'].items()
             if reading.get('clean')]
    diameters = [reading['side_wall_diameter_mm'] for _, _, reading in clean if reading['side_wall_diameter_mm']]
    protrusions = [reading['protrusion_beyond_barrel_face_mm'] for _, _, reading in clean]
    report = {
        'scope': __doc__,
        'input_sha256': {'merged_scan': registration['mesh_sha256'], **PASSES,
                         'scan-registration.json': sha(HERE / 'scan-registration.json'),
                         'branch-operating-measurements.json': sha(HERE / 'branch-operating-measurements.json')},
        'source_sha256': sha(__file__),
        'pass_archive': str(ARCHIVE),
        'method': ('Five native fused clouds, unscaled. Each is registered onto the registered merged mesh '
                   '(principal-axis starts, trimmed point-to-plane ICP, 0.35 mm final inlier band). Per port: '
                   'front face r3.4-5.3 with outward normals fitted as a plane; fixed barrel face r5.6-7.4; '
                   'side wall r4.6-5.8 between them. A reading is clean with at least 30 of 36 face '
                   'sectors present and an open bore.'),
        'passes': passes,
        'summary': {
            'clean_readings': len(clean),
            'readings_excluded': sorted(f'{p} {port}' for p, record in passes.items()
                                        for port, reading in record['ports'].items()
                                        if reading.get('seen') and not reading.get('clean')),
            'side_wall_diameter_mm': {'median': float(np.median(diameters)), 'min': float(min(diameters)),
                                      'max': float(max(diameters)), 'count': len(diameters)},
            'protrusion_beyond_barrel_face_mm': {'min': float(min(protrusions)), 'max': float(max(protrusions))},
            'calipered_stroke_fraction': {'min': float(min(r['calipered_stroke_fraction'] for *_, r in clean)),
                                          'max': float(max(r['calipered_stroke_fraction'] for *_, r in clean))},
        },
        'limits': [
            'Every clean reading rests near the pressed end; no pass holds a collet drawn out, so the stroke stays the calipered one.',
            'Side-wall diameters are optical readings of bare black polypropylene, not a manufacturing tolerance.',
            'The collet seam inside the fixed barrel is never in view.',
        ],
    }
    (HERE / 'collet-passes.json').write_text(json.dumps(report, indent=2) + '\n')
    for p, record in passes.items():
        print(f"{p}: registered {record['registration_inlier_fraction']:.3f} within 0.35 mm, "
              f"median {record['registration_inlier_median_mm']:.3f} mm")
        for port, reading in record['ports'].items():
            if not reading['seen']:
                print(f'  {port:9s} not in view')
                continue
            print(f"  {port:9s} face {reading['face_station_mm']:6.2f} tilt {reading['face_tilt_deg']:3.1f} deg "
                  f"sectors {reading['face_sectors_of_36']:2d} | protrusion {reading['protrusion_beyond_barrel_face_mm']:4.2f} "
                  f"| wall {reading['side_wall_diameter_mm'] or float('nan'):5.2f} | stroke {reading['calipered_stroke_fraction']:+.2f} "
                  f"| {'clean' if reading['clean'] else 'EXCLUDED'}")
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
