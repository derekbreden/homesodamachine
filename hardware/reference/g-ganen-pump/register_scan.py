"""Rigid alignment of two inspected G Ganen scans, with disjoint held-out patches."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from scan_tools import load_cloud, select, stats, transform_points

HERE = Path(__file__).resolve().parent


def voxel_sample(points, normals, spacing):
    _, indices = np.unique(np.floor(points/spacing).astype(np.int64),
                           axis=0, return_index=True)
    return points[indices], normals[indices]


def refine(fixed, fixed_normals, moving, moving_normals, max_distance=.8):
    """Six-degree point-to-plane alignment; no shape, scale or feature dimensions fitted."""
    tree = cKDTree(fixed)
    total = np.eye(4)
    points, normals = moving.copy(), moving_normals.copy()
    history = []
    for iteration in range(40):
        distances, indices = tree.query(points, workers=1)
        targets, target_normals = fixed[indices], fixed_normals[indices]
        selected = ((distances < max_distance)
                    & (np.sum(normals*target_normals, axis=1) > .75))
        if selected.sum() < 100:
            raise ValueError('Insufficient compatible rigid surface overlap')
        p, q, n = points[selected], targets[selected], target_normals[selected]
        residuals = np.sum((p-q)*n, axis=1)
        weights = np.sqrt(np.minimum(1., .08/np.maximum(np.abs(residuals), 1e-12)))
        design = np.column_stack((np.cross(p, n), n))
        step, _, rank, singular = np.linalg.lstsq(
            design*weights[:, None], -residuals*weights, rcond=None)
        if rank < 6:
            raise ValueError('Selected rigid surfaces do not constrain all six degrees')
        if np.linalg.norm(step[:3]) > .05 or np.linalg.norm(step[3:]) > 2:
            raise ValueError('Inspect the physical initial frames before large ICP motion')
        delta = np.eye(4)
        delta[:3, :3] = Rotation.from_rotvec(step[:3]).as_matrix()
        delta[:3, 3] = step[3:]
        points = transform_points(points, delta)
        normals = normals @ delta[:3, :3].T
        total = delta @ total
        history.append({'iteration': iteration, 'pairs': int(selected.sum()),
                        'point_plane_residual_mm': stats(residuals),
                        'step_rotation_degrees': float(np.degrees(np.linalg.norm(step[:3]))),
                        'step_translation_mm': float(np.linalg.norm(step[3:])),
                        'design_singular_values': singular.tolist()})
        if np.linalg.norm(step[:3]) < 1e-6 and np.linalg.norm(step[3:]) < 1e-4:
            break
    else:
        raise ValueError('Rigid refinement did not converge within forty steps')
    angle = np.degrees(np.linalg.norm(Rotation.from_matrix(total[:3, :3]).as_rotvec()))
    if angle > 5 or np.linalg.norm(total[:3, 3]) > 3:
        raise ValueError('Refinement exceeds the inspected initial-frame allowance')
    return total, history


def compare(source, source_normals, target, target_normals):
    distances, indices = cKDTree(target).query(source, workers=1)
    compatible = np.sum(source_normals*target_normals[indices], axis=1) > .75
    overlap = compatible & (distances < .75)
    result = {'all_nearest_distance_mm': stats(distances),
              'normal_compatible_fraction': float(np.mean(compatible)),
              'overlap_within_0_75mm_fraction': float(np.mean(overlap)),
              'overlap_points': int(overlap.sum())}
    if overlap.any():
        result['overlap_point_plane_mm'] = stats(np.sum(
            (source[overlap]-target[indices[overlap]])*target_normals[indices[overlap]], axis=1))
    return result


def run(configuration):
    clouds = []
    for role in ('fixed', 'moving'):
        item = configuration[role]
        points, normals, metadata = load_cloud(item['path'], item['sha256'])
        transform = np.asarray(item['native_to_shared_initial'])
        points = transform_points(points, transform)
        normals = normals @ transform[:3, :3].T
        lengths = np.linalg.norm(normals, axis=1)
        valid = lengths > .9
        points, normals = points[valid], normals[valid]/lengths[valid, None]
        points, normals = voxel_sample(points, normals, configuration.get('spacing_mm', .30))
        fit = select(points, configuration['fit_regions'])
        withheld = select(points, configuration['held_out_regions'])
        if np.any(fit & withheld):
            raise ValueError(f'{role}: fitting and held-out observations overlap')
        clouds.append((points, normals, metadata, transform, fit))
    fixed, fn, fixed_meta, ft, fixed_fit = clouds[0]
    moving, mn, moving_meta, mt, moving_fit = clouds[1]
    correction, history = refine(fixed[fixed_fit], fn[fixed_fit],
                                 moving[moving_fit], mn[moving_fit])
    moved = transform_points(moving, correction)
    moved_normals = mn @ correction[:3, :3].T
    validation = []
    for region in configuration['held_out_regions']:
        if not region.get('enabled', True):
            continue
        # Membership belongs to the initial physical frame and is never optimized
        # to retain only observations that agree after alignment.
        fa, ma = select(fixed, [region]), select(moving, [region])
        row = {'region': region['name'], 'fixed_points': int(fa.sum()),
               'moving_points': int(ma.sum())}
        if min(fa.sum(), ma.sum()) < 30:
            row['status'] = 'insufficient_common_coverage'
        else:
            row['fixed_to_moving'] = compare(fixed[fa], fn[fa], moved[ma], moved_normals[ma])
            row['moving_to_fixed'] = compare(moved[ma], moved_normals[ma], fixed[fa], fn[fa])
        validation.append(row)
    return {'status': 'rigid_scan_alignment', 'configuration': configuration,
            'scale_factor': 1.0, 'fixed': fixed_meta, 'moving': moving_meta,
            'fixed_native_to_shared': ft.tolist(),
            'moving_native_to_shared': (correction @ mt).tolist(),
            'moving_correction': correction.tolist(), 'fit_history': history,
            'held_out_bidirectional_residuals': validation,
            'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                            for name in ('register_scan.py', 'scan_tools.py')},
            'limits': ['No CAD surfaces or catalog dimensions define alignment or scale.',
                       'Residuals describe common observed surfaces; they are not dimensional tolerance.',
                       'Missing surfaces, flexible feet, loose leads and fixture putty are not inferred.']}


def selftest():
    grid = np.linspace(-12, 12, 27)
    points, normals = [], []
    for axis in range(3):
        for side in (-1, 1):
            for a in grid:
                for b in grid:
                    p = [a, b]; p.insert(axis, side*15)
                    normal = np.zeros(3); normal[axis] = side
                    points.append(p); normals.append(normal)
    fixed, fn = np.array(points), np.array(normals)
    truth = np.eye(4)
    truth[:3, :3] = Rotation.from_euler('xyz', [.4, -.3, .2], degrees=True).as_matrix()
    truth[:3, 3] = [.2, -.25, .17]
    moving = transform_points(fixed, truth)
    recovered, _ = refine(fixed, fn, moving, fn @ truth[:3, :3].T)
    assert np.allclose(recovered @ truth, np.eye(4), atol=1e-6)
    print('Synthetic six-degree rigid alignment recovered at unit scale.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration', nargs='?')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        if not args.configuration or not args.out:
            parser.error('configuration and --out are required')
        saved = json.loads(Path(args.configuration).read_text())
        args.out.write_text(json.dumps(run(saved.get('configuration', saved)), indent=2)+'\n')
