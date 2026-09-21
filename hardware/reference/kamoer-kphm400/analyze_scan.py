#!/usr/bin/env python3
"""Reproduce measured Kamoer contact planes and native CAD comparisons at unit scale.

Raw fused clouds and the pre-correction native CAD exports remain in the external
capture archive. Every input is verified by digest. Output is observations, not
an unrestricted scan-to-CAD fit or a claim of physical assembly acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from scipy.optimize import least_squares
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy

from register_scan import load_cloud, plane, stats, transform_points, unit

HERE = Path(__file__).resolve().parent


def face_footprint(mesh, z, sign):
    selected = ((mesh.face_normals[:, 2] * sign > .99999)
                & (abs(mesh.triangles_center[:, 2] - z) < .002))
    return unary_union([Polygon(t[:, :2]) for t in mesh.triangles[selected]])


def scan_observations(evidence, registration, archive):
    points, normals, pass_ids = [], [], []
    for pass_id, role, transform_key in [
        (1, 'fixed', 'fixed_native_to_shared'),
        (2, 'moving', 'moving_native_to_shared_final'),
    ]:
        source = registration[role]
        old_path = Path(source['path'])
        path = archive / old_path.parent.name / old_path.name
        p, n, metadata = load_cloud(path)
        if metadata['sha256'] != source['sha256']:
            raise ValueError(f'Raw cloud changed: {path}')
        transform = np.asarray(registration[transform_key])
        points.append(transform_points(p[::6], transform))
        normals.append(n[::6] @ transform[:3, :3].T)
        pass_ids.append(np.full(len(points[-1]), pass_id))
    return np.vstack(points), np.vstack(normals), np.concatenate(pass_ids)


def bearing_frame(p, n, pass_id):
    regions = [
        ('xminus', [-31, -22, -8.6], [-26, 22, -7.4]),
        ('xplus', [26, -22, -8.6], [31, 22, -7.4]),
        ('yminus', [-21, -32, -8.6], [21, -26, -7.4]),
    ]
    selected = np.zeros(len(p), bool)
    rows = []
    for name, lo, hi in regions:
        for current_pass in (1, 2):
            mask = (np.all((p >= lo) & (p <= hi), axis=1)
                    & (abs(n[:, 2]) > .96) & (pass_id == current_pass))
            selected |= mask
            observed = p[mask]
            if len(observed) < 30:
                continue
            center, normal, _ = plane(observed)
            if normal[2] < 0:
                normal = -normal
            rows.append({
                'region': name, 'pass': current_pass, 'points': len(observed),
                'plane_center': center.tolist(), 'plane_normal': normal.tolist(),
                'intercept_mm': float(center @ normal / normal[2]),
                'untrimmed_plane_residual_mm': stats((observed - center) @ normal),
            })
    # Select the exposed halves; do not discard points for disagreeing with CAD.
    exposed = (((pass_id == 1) & (p[:, 1] > -18))
               | ((pass_id == 2) & (p[:, 1] < 16)))
    support = p[selected & exposed]
    center, zaxis, _ = plane(support)
    if zaxis[2] < 0:
        zaxis = -zaxis
    xaxis = unit(np.array([1., 0, 0]) - zaxis * zaxis[0])
    basis = np.column_stack([xaxis, np.cross(zaxis, xaxis), zaxis])
    origin = np.array([0., 0., float(center @ zaxis / zaxis[2])])
    return (p - origin) @ basis, n @ basis, exposed, selected, {
        'selected_points': len(support), 'center_common': center.tolist(),
        'normal_common': zaxis.tolist(), 'origin_common': origin.tolist(),
        'common_to_bearing_rotation': basis.T.tolist(),
        'untrimmed_residual_mm': stats((support - center) @ zaxis),
        'per_region_per_pass': rows,
    }


def casing_sections(p, n, pass_ids):
    rows = []
    for pass_id in (1, 2):
        for side, cx in [('xminus', -29.875), ('xplus', 29.875)]:
            for lo, hi in [(16, 18), (19, 21), (22, 24)]:
                radius = np.hypot(p[:, 0] - cx, p[:, 2] + 28.48)
                selected = ((pass_ids == pass_id) & (p[:, 1] >= lo) & (p[:, 1] <= hi)
                            & (radius > 6.2) & (radius < 7.2) & (abs(n[:, 1]) < .25))
                section = p[selected][:, [0, 2]]
                if len(section) < 50:
                    raise ValueError(f'Insufficient molded casing section: {pass_id}, {side}')

                def error(v):
                    return ((np.sqrt(np.sum(((section - v[:2]) / v[2:]) ** 2, axis=1)) - 1)
                            * np.sqrt(v[2] * v[3]))

                fit = least_squares(
                    error, [cx, -28.48, 6.4, 6.9], loss='soft_l1', f_scale=.04,
                    bounds=([cx - 1, -29.5, 5, 5], [cx + 1, -27.5, 8, 8]))
                rows.append({
                    'pass': pass_id, 'side': side, 'y_range_common_mm': [lo, hi],
                    'points': len(section), 'center_xz_common_mm': fit.x[:2].tolist(),
                    'fitted_width_x_mm': float(2 * fit.x[2]),
                    'fitted_height_z_mm': float(2 * fit.x[3]),
                    'approx_geometric_residual_mm': stats(error(fit.x)),
                })
    return rows


def casing_clearance(p, bearing_world, pass_ids, cradle):
    """Sample all observed rigid casing roots, without rejecting CAD disagreements."""
    rows = []
    for pass_id in (1, 2):
        for side, sign in [('xminus', -1), ('xplus', 1)]:
            mask = ((pass_ids == pass_id) & (sign * p[:, 0] > 22)
                    & (sign * p[:, 0] < 38) & (p[:, 1] > 16) & (p[:, 1] < 24)
                    & (p[:, 2] > -36.5) & (p[:, 2] < -21))
            indices = np.flatnonzero(mask)[::5]
            observed = bearing_world[indices]
            inside = cradle.contains(observed)
            row = {'pass': pass_id, 'side': side, 'observations': len(indices),
                   'inside_native_cradle': int(inside.sum())}
            if inside.any():
                _closest, distance, _face = trimesh.proximity.closest_point(cradle, observed[inside])
                row['inside_distance_mm'] = stats(distance)
                row['deepest_common_xyz'] = p[indices[inside][np.argmax(distance)]].tolist()
            rows.append(row)
    return {
        'sampling': 'Every fifth selected observation from the every-sixth raw sample; molded casing roots Y16..24 only.',
        'rows': rows,
        'interpretation': 'Sub-quarter-millimetre discrepancy is not consistent between passes and is comparable to cross-pass/spray uncertainty. It does not establish a large repeatable interference or justify altering the fitted opening. Physical insertion remains required.',
    }


def analyze(evidence, registration, archive, native_dir):
    p, n, pass_ids = scan_observations(evidence, registration, archive)
    bearing, bn, exposed, underside, fitted_plane = bearing_frame(p, n, pass_ids)
    files = evidence['native_baseline']['sha256']
    for name, expected in files.items():
        actual = hashlib.sha256((native_dir / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Native baseline changed: {name}; expected {expected}, read {actual}')
    cap = trimesh.load(native_dir / 'enclosure-pump-cap.stl', process=True)
    cradle = trimesh.load(native_dir / 'enclosure-pump-cartridge.stl', process=True)
    front_top = trimesh.load(native_dir / 'enclosure-front-top.stl', process=False)
    cap_z = float(cap.bounds[0, 2])
    support_z = 205.49400329589844
    floor_z = 165.615
    support_foot = face_footprint(cradle, support_z, 1)
    cap_foot = face_footprint(cap, cap_z, -1)
    floor_foot = face_footprint(front_top, floor_z, 1)
    if min(support_foot.area, cap_foot.area, floor_foot.area) < 100:
        raise ValueError('Expected native bearing face is absent')
    world_origin = np.array([49.945, 44.909, support_z])
    world = bearing + world_origin
    over_cap = contains_xy(cap_foot, world[:, 0], world[:, 1])
    over_support = contains_xy(support_foot, world[:, 0], world[:, 1])
    over_floor = contains_xy(floor_foot, world[:, 0], world[:, 1])
    pressing = ((abs(p[:, 0]) < 31.5) & (abs(p[:, 1]) < 31.5)
                & (np.linalg.norm(p[:, :2], axis=1) > 26)
                & (p[:, 2] > -.7) & (p[:, 2] < .7)
                & (abs(n[:, 2]) > .95) & exposed & over_cap)
    topography = ((abs(p[:, 0]) < 33) & (p[:, 1] > -32) & (p[:, 1] < 32)
                  & (p[:, 2] > -.8) & (p[:, 2] < 20) & exposed & over_cap)
    front = ((abs(p[:, 0]) < 32) & (p[:, 1] > -31) & (p[:, 1] < 33)
             & (p[:, 2] > -50) & (p[:, 2] < -45) & (abs(bn[:, 2]) > .9))
    rails = []
    for pass_id in (1, 2):
        for side, sign in [('xminus', -1), ('xplus', 1)]:
            selected = ((pass_ids == pass_id) & (sign * bearing[:, 0] > 29)
                        & (sign * bearing[:, 0] < 32) & (abs(bearing[:, 1]) < 16)
                        & (bearing[:, 2] > 7.1) & (bearing[:, 2] < 8.9)
                        & (abs(bn[:, 2]) > .95))
            rails.append({
                'pass': pass_id, 'side': side,
                'bearing_frame_x_range_mm': sorted([sign * 29., sign * 32.]),
                'bearing_frame_y_range_mm': [-16., 16.],
                'observed_height_above_land_mm': stats(bearing[selected, 2]),
            })
    result = {
        'schema': 1, 'status': 'independent_rigid_measurements_and_frozen_native_contact_comparison',
        'registration': 'scan-registration.json', 'scale_factor': 1.,
        'selection_authority': 'Inspected rigid regions and normals; no CAD-residual trimming. Complete outlet stack excluded from registration.',
        'limits': evidence['limits'], 'native_baseline_sha256': files,
        'skirt_bearing_plane': fitted_plane,
        'native_placement': {
            'bearing_frame_world_origin': world_origin.tolist(),
            'native_cradle_bearing_z_mm': support_z,
            'native_cap_underside_z_mm': cap_z, 'native_floor_z_mm': floor_z,
            'support_footprint_area_mm2': support_foot.area,
            'cap_underside_footprint_area_mm2': cap_foot.area,
            'floor_footprint_area_mm2': floor_foot.area,
            'method': 'Actual observed underside strips seated on actual native lower lands. X is paired head-side midpoint; Y aligns observed motor axis to native motor opening. No extra plate assumed.',
        },
        'baseline_broad_cap_gap_mm': stats(cap_z - world[pressing, 2]),
        'baseline_broad_cap_gap_by_pass': [
            {'pass': k, 'gap_mm': stats(cap_z - world[pressing & (pass_ids == k), 2])}
            for k in (1, 2)
        ],
        'rigid_topography_under_cap': {
            'observations': int(topography.sum()),
            'observations_above_cap_underside': int((topography & (world[:, 2] > cap_z)).sum()),
            'relative_heights_to_cap_mm': stats(world[topography, 2] - cap_z),
        },
        'projected_underside_points_on_native_land': int((underside & exposed & over_support).sum()),
        'baseline_front_rim': {
            'head_front_height_above_skirt_land_mm': stats(bearing[front & over_floor, 2]),
            'floor_gap_mm': stats(world[front & over_floor, 2] - floor_z),
            'selected_points_outside_floor': int((front & ~over_floor).sum()),
            'identity': 'Repeated rigid molded cover/rim in both views, including its native screw recess surrounds; flexible outlets and fixtures are outside the selected region.',
            'per_pass': [
                {'pass': k, 'floor_gap_mm': stats(world[front & over_floor & (pass_ids == k), 2] - floor_z)}
                for k in (1, 2)
            ],
        },
        'corrected_cap_rail_observations': rails,
        'molded_casing_sections': casing_sections(p, n, pass_ids),
        'molded_casing_native_clearance': casing_clearance(p, world, pass_ids, cradle),
        'casing_interpretation': 'Oval exterior sections describe station and size; they do not prove a circular interference fit. Silicone and inserted LLDPE are excluded.',
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--native-dir', type=Path)
    parser.add_argument('--out', type=Path, default=HERE / 'scan-measurements.json')
    args = parser.parse_args()
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    registration = json.loads((HERE / 'scan-registration.json').read_text())
    archive = args.archive or Path(evidence['capture_archive'])
    native_dir = args.native_dir or archive / evidence['native_baseline']['directory']
    result = analyze(evidence, registration, archive, native_dir)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Wrote {args.out}: native cap median gap {result["baseline_broad_cap_gap_mm"]["median"]:.3f} mm; '
          f'front-floor minimum {result["baseline_front_rim"]["floor_gap_mm"]["min"]:.3f} mm')


if __name__ == '__main__':
    main()
