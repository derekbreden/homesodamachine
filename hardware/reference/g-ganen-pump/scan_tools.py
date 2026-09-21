"""Unit-scale native-cloud measurements for the G Ganen reference.

No source cloud is rewritten. Regions and physical feature identities belong to
the inspected selection file; a fit never decides which surface is pump material.
"""
from pathlib import Path
import hashlib

import numpy as np
from scipy.optimize import least_squares


def unit(vector):
    vector = np.asarray(vector, dtype=float)
    length = np.linalg.norm(vector)
    if length < 1e-10:
        raise ValueError('Degenerate direction')
    return vector / length


def stats(values):
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.all(np.isfinite(values)):
        raise ValueError('Residuals must contain finite observations')
    return {key: float(value) for key, value in {
        'mean': np.mean(values), 'median': np.median(values),
        'rms': np.sqrt(np.mean(values**2)), 'p05': np.percentile(values, 5),
        'p95': np.percentile(values, 95),
        'abs_p95': np.percentile(np.abs(values), 95),
        'min': np.min(values), 'max': np.max(values),
    }.items()} | {'n': len(values)}


def load_cloud(path, expected_sha256=None):
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError(f'Archived input digest mismatch: {path}')
    stop = raw.index(b'end_header\n') + len(b'end_header\n')
    header = raw[:stop].decode('ascii')
    properties = [line for line in header.splitlines() if line.startswith('property ')]
    expected = [f'property float {key}' for key in ('x', 'y', 'z', 'nx', 'ny', 'nz')]
    if 'format binary_little_endian 1.0' not in header or properties != expected:
        raise ValueError('Inspect the PLY header: expected native XYZ/normal float32 data')
    count = int(next(line.split()[-1] for line in header.splitlines()
                     if line.startswith('element vertex ')))
    if len(raw) - stop != count * 24:
        raise ValueError('Unexpected PLY record size or trailing data')
    data = np.frombuffer(raw, dtype='<f4', offset=stop).reshape(count, 6).astype(float)
    if not np.all(np.isfinite(data)):
        raise ValueError('Native cloud contains nonfinite coordinates or normals')
    return data[:, :3], data[:, 3:], {
        'path': str(path.resolve()), 'sha256': digest, 'points': count,
        'coordinate_scale_factor': 1.0,
    }


def transform_points(points, transform):
    transform = np.asarray(transform, dtype=float)
    if transform.shape != (4, 4):
        raise ValueError('Expected a 4 by 4 homogeneous transform')
    rotation = transform[:3, :3]
    if (not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-7)
            or not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-7)
            or not np.allclose(transform[3], [0, 0, 0, 1], atol=1e-9)):
        raise ValueError('The native-to-reference transform must be proper rigid at unit scale')
    return np.asarray(points) @ rotation.T + transform[:3, 3]


def plane(points):
    points = np.asarray(points, dtype=float)
    if len(points) < 3:
        raise ValueError('A plane needs at least three observations')
    center = np.mean(points, axis=0)
    _, singular, vectors = np.linalg.svd(points - center, full_matrices=False)
    if singular[1] < 1e-8:
        raise ValueError('Plane observations are collinear')
    normal = unit(vectors[-1])
    return center, normal, stats((points - center) @ normal)


def cylinder(points, axis_hint, radius_hint):
    """Five-parameter surface fit; the center lies on a fixed transverse gauge plane."""
    points = np.asarray(points, dtype=float)
    if len(points) < 30:
        raise ValueError('A cylinder needs at least thirty selected surface observations')
    axis0 = unit(axis_hint)
    trial = np.eye(3)[np.argmin(np.abs(axis0))]
    u = unit(np.cross(axis0, trial))
    v = np.cross(axis0, u)
    anchor = np.mean(points, axis=0)

    def unpack(parameters):
        du, dv, tilt_u, tilt_v, radius = parameters
        axis = unit(axis0 + tilt_u*u + tilt_v*v)
        center = anchor + du*u + dv*v
        return center, axis, radius

    def residual(parameters):
        center, axis, radius = unpack(parameters)
        relative = points - center
        radial = relative - np.outer(relative @ axis, axis)
        return np.linalg.norm(radial, axis=1) - radius

    fit = least_squares(residual, [0, 0, 0, 0, radius_hint],
                        loss='soft_l1', f_scale=.08,
                        bounds=([-np.inf, -np.inf, -.3, -.3, .1],
                                [np.inf, np.inf, .3, .3, np.inf]))
    if not fit.success or np.linalg.matrix_rank(fit.jac) < 5:
        raise ValueError('Selected observations do not constrain the cylinder fit')
    center, axis, radius = unpack(fit.x)
    return {'axis_point': center.tolist(), 'axis_direction': axis.tolist(),
            'radius_mm': float(radius), 'untrimmed_residual_mm': stats(residual(fit.x)),
            'fit_status': fit.message}


def cylinder_residual(points, fitted):
    center = np.asarray(fitted['axis_point'])
    axis = np.asarray(fitted['axis_direction'])
    relative = np.asarray(points) - center
    radial = relative - np.outer(relative @ axis, axis)
    return np.linalg.norm(radial, axis=1) - fitted['radius_mm']


def select(points, bounds):
    """Union of named axis-aligned regions in an explicitly identified physical frame."""
    mask = np.zeros(len(points), dtype=bool)
    for region in bounds:
        if region.get('enabled', True):
            mask |= np.all((points >= region['min']) & (points <= region['max']), axis=1)
    return mask


def selftest():
    # A translated, tilted cylinder tests all fitted degrees of freedom and scale.
    axis = unit([1, .024, -.031])
    u = unit(np.cross(axis, [0, 0, 1]))
    v = np.cross(axis, u)
    center = np.array([12., -8., 31.])
    angles, stations = np.meshgrid(np.linspace(0, 2*np.pi, 97)[:-1], np.linspace(-20, 20, 13))
    points = (center + stations.ravel()[:, None]*axis
              + 17.4*np.cos(angles.ravel())[:, None]*u
              + 17.4*np.sin(angles.ravel())[:, None]*v)
    measured = cylinder(points, [1, 0, 0], 17)
    assert abs(measured['radius_mm']-17.4) < 1e-7
    assert np.linalg.norm(np.cross(measured['axis_direction'], axis)) < 1e-7
    assert stats(cylinder_residual(points, measured))['abs_p95'] < 1e-7
    wrong = np.eye(4); wrong[0, 0] = 1.001
    try:
        transform_points(points, wrong)
    except ValueError:
        pass
    else:
        raise AssertionError('A scaled transform was accepted')
    print('Synthetic translated/tilted cylinder recovered; scaled transform rejected.')


if __name__ == '__main__':
    selftest()
