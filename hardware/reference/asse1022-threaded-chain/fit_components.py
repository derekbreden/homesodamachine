"""Fit the visible adapters and tee in the registered full-chain capture.

Circular surface-normal rays locate each inline axis independently of radius
and molding draft. The compact piecewise-linear radius profiles describe the
observed exterior; they do not reconstruct hidden joint contacts.
"""
from pathlib import Path
import json
import sys

import numpy as np
from scipy.ndimage import median_filter
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud, unit, stats
from analyze_capture import sha


def rays_axis(p, n, bands):
    selected = np.zeros(len(p), dtype=bool)
    for lo, hi in bands:
        selected |= (p[:, 0] > lo) & (p[:, 0] < hi)
    selected &= (abs(n[:, 0]) < .8) & (abs(p[:, 1]) < 16)
    q, nn = p[selected][::3], n[selected][::3]
    radial = q - [0, 0, 27.45]
    radial[:, 0] = 0
    facing = np.sum(radial * nn, axis=1) / np.maximum(np.linalg.norm(radial, axis=1), 1e-6)
    q, nn = q[facing > .55], nn[facing > .55]
    anchor = float(np.mean(q[:, 0]))
    x = q[:, 0] - anchor
    length = np.hypot(nn[:, 1], nn[:, 2])

    def residual(v):
        return ((nn[:, 2] * (q[:, 1] - v[0] - v[2] * x)
                 - nn[:, 1] * (q[:, 2] - v[1] - v[3] * x)) / length)

    fit = least_squares(residual, [0, 27.45, 0, 0], loss='soft_l1', f_scale=.10)
    a = unit([1, fit.x[2], fit.x[3]])
    origin = np.array([anchor, fit.x[0], fit.x[1]])
    ey = unit(np.cross([0, 0, 1], a))
    rotation = np.column_stack([a, ey, np.cross(a, ey)])
    return origin, rotation, {'bands_mm': bands, 'samples': len(q),
                              'normal_ray_residual_mm': stats(residual(fit.x))}


def simplify(points, tolerance=.06):
    points = np.asarray(points, dtype=float)
    if len(points) <= 2:
        return points.tolist()
    predicted = np.interp(points[:, 0], points[[0, -1], 0], points[[0, -1], 1])
    error = abs(points[:, 1] - predicted)
    index = int(np.argmax(error))
    if error[index] <= tolerance:
        return points[[0, -1]].tolist()
    return simplify(points[:index+1], tolerance)[:-1] + simplify(points[index:], tolerance)


def profile(q, nn, lo, hi, axis=0, center=(0, 0), clean=None):
    radial_axes = [i for i in range(3) if i != axis]
    rv = q[:, radial_axes] - center
    radius = np.linalg.norm(rv, axis=1)
    facing = np.sum(rv * nn[:, radial_axes], axis=1) / np.maximum(radius, 1e-6)
    valid = (facing > .35) & (abs(nn[:, axis]) < .9)
    if clean is not None:
        valid &= clean
    values = []
    for x in np.arange(lo + .1, hi, .2):
        hit = valid & (abs(q[:, axis] - x) < .1)
        if hit.sum() > 12:
            values.append([float(x), float(np.quantile(radius[hit], .975))])
    values = np.asarray(values)
    if len(values) < 3:
        raise ValueError('Insufficient exposed profile observations')
    values[:, 1] = median_filter(values[:, 1], size=3, mode='nearest')
    values = np.vstack([[lo, values[0, 1]], values, [hi, values[-1, 1]]])
    return [[round(x, 3), round(r, 3)] for x, r in simplify(values)]


def hex_draft(q, nn, lo, hi, clock):
    theta = np.arctan2(nn[:, 2], nn[:, 1])
    base = np.radians(clock + 30)
    index = np.round((theta - base) / (np.pi / 3))
    angle = base + index * np.pi / 3
    angular_error = np.angle(np.exp(1j * (theta - angle)))
    hit = (q[:, 0] > lo) & (q[:, 0] < hi) & (abs(angular_error) < np.radians(4)) & (abs(nn[:, 0]) < .2)
    heights = q[hit, 1] * np.cos(angle[hit]) + q[hit, 2] * np.sin(angle[hit])
    x = q[hit, 0]
    fit = least_squares(lambda v: heights - v[0] - v[1] * x,
                        [np.median(heights), 0], loss='soft_l1', f_scale=.05)
    if abs(fit.x[1]) < .003:
        fit.x[:] = [np.median(heights), 0.]
    return {'range_mm': [float(lo), float(hi)], 'clock_degrees': clock,
            'apothem_at_x_zero_mm': float(fit.x[0]), 'apothem_slope': float(fit.x[1]),
            'fit_residual_mm': stats(heights - fit.x[0] - fit.x[1] * x)}


def main():
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    source = evidence['retained_cloud']
    p, n, _ = load_cloud(source['path'], source['sha256'])
    components = {}
    specs = [
        ('pp010822e', 'John Guest PP010822E', [(-36.3, -31.0), (-25.2, -21.2)], -36.55, -20.75, (-30.5, -25.1, -.3)),
        ('gagira', 'GAGIRA reducing coupling', None, -20.725, 5.925, (-12.45, -2.5, -27.64)),
        ('pi4512f6s', 'John Guest PI4512F6S', [(68.0, 71.0), (72.5, 84.0), (85.0, 88.0)], 52.125, 88.175, (53.4, 65.9, -27.0)),
        ('pp061208w', 'John Guest PP061208W', [(88.5, 93.6), (94.5, 107.6)], 88.175, 107.825, None),
    ]
    # The coupling's undrafted flats directly constrain its axis and centre.
    for key, label, bands, lo, hi, wrench in specs:
        if bands is None:
            # Coaxial three-flat fit, reconstructed directly from its observations.
            from scan_tools import plane
            ns, ds = [], []
            theta = np.degrees(np.arctan2(n[:, 2], n[:, 1]))
            for angle in [2, -58, -118]:
                hit = (p[:, 0] > -11) & (p[:, 0] < -4) & (abs(theta-angle) < 4) & (abs(n[:, 0]) < .15)
                c, normal, _ = plane(p[hit]); normal *= np.sign(normal @ n[hit].mean(0))
                ns.append(normal); ds.append(normal @ c)
            ns = np.array(ns); _, _, v = np.linalg.svd(ns)
            axis = v[-1] * np.sign(v[-1, 0])
            origin = np.linalg.solve(np.vstack([np.column_stack([ns, np.ones(3)]), [1, 0, 0, 0]]), [*ds, 0])[:3]
            ey = unit(np.cross([0, 0, 1], axis))
            rotation = np.column_stack([axis, ey, np.cross(axis, ey)])
            fit_record = {'method': 'Three undrafted wrench planes'}
        else:
            origin, rotation, fit_record = rays_axis(p, n, bands)
        # Gauge every profile at global X=0 on its fitted axis.
        origin = origin - rotation[:, 0] * origin[0] / rotation[0, 0]
        q = (p-origin) @ rotation
        nn = n @ rotation
        outline = profile(q, nn, lo, hi)
        record = {'name': label, 'origin_mm': origin.tolist(), 'rotation': rotation.tolist(),
                  'visible_profile': outline, 'axis_fit': fit_record,
                  'visible_axial_range_mm': [lo, hi]}
        if wrench:
            record['wrench'] = hex_draft(q, nn, *wrench)
        components[key] = record

    # The tee run is the observed common cylinder of its two socket collars.
    from scan_tools import cylinder
    rv = p - [119, 0, 27.4]; rv[:, 1] = 0
    facing = np.sum(rv*n, axis=1) / np.maximum(np.linalg.norm(rv, axis=1), 1e-6)
    hit = ((p[:, 0] > 110) & (p[:, 0] < 128) & (abs(p[:, 1]) > 9)
           & (abs(p[:, 1]) < 15) & (abs(n[:, 1]) < .3) & (facing > .7))
    fitted = cylinder(p[hit][::3], [0, 1, 0], 7.7)
    run = np.array(fitted['axis_direction'])
    c = np.array(fitted['axis_point'])
    host = components['pp061208w']
    h = np.array(host['origin_mm']); flow = np.array(host['rotation'])[:, 0]
    offsets = np.linalg.lstsq(np.column_stack([run, -flow]), h-c, rcond=None)[0]
    origin = (c + run*offsets[0] + h + flow*offsets[1]) / 2
    y = unit(run - (run@flow)*flow)
    rotation = np.column_stack([flow, y, np.cross(flow, y)])
    q, nn = (p-origin) @ rotation, n @ rotation
    profiles = {}
    for sign, key in [(1, 'plus'), (-1, 'minus')]:
        qq, normals = q.copy(), nn.copy()
        qq[:, 1] *= sign; normals[:, 1] *= sign
        near = ((abs(qq[:, 0]) < 9) & (qq[:, 1] > 5.5)
                & (np.hypot(qq[:, 0], qq[:, 2]) < 9))
        end = float(np.quantile(qq[near, 1], .999))
        measured = profile(qq, normals, 5.6, end, axis=1, clean=near)
        profiles[key] = [[0, 5.15], [4.9, 5.15], *measured]
    components['atbu444-e'] = {'name': 'neoFit ATBU444-E branch stem tee',
                              'origin_mm': origin.tolist(), 'rotation': rotation.tolist(),
                              'run_profiles': profiles, 'run_cylinder_fit': fitted,
                              'branch_profile': [[-27.05, 2.95], [-26.8, 3.175], [-6.0, 3.175], [-5.7, 3.90], [0, 3.90]],
                              'buried_stem': 'The unobserved stem continuation uses the manufacturer-derived 27.05 mm tip station; it is not a measured insertion stop.'}
    report = {'units': 'mm', 'frame': 'The separately scanned ASSE frame: +X flow, bare inlet rim X=0, vent tip Z=0.',
              'scan_evidence_sha256': sha(HERE / 'scan-evidence.json'),
              'components': components,
              'profile_method': '0.2 mm axial bins, outward normals, 97.5th percentile radius, three-bin median, piecewise-linear approximation at 0.06 mm radial tolerance. Native observations are unchanged.',
              'buried_geometry': 'Closed joint volumes and bore continuations are display geometry, not material or hydraulic specifications.'}
    (HERE / 'reference-parameters.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, value in components.items():
        print(name, 'origin', value['origin_mm'], 'axis', np.array(value['rotation'])[:, 0].tolist(),
              'wrench', value.get('wrench', {}))


if __name__ == '__main__':
    main()
