"""Measure the archived feet-up G Ganen scan in a mounting-plane reference frame.

The selected surface identities are from the retained orthographic diagnostics.
This single-pass report does not complete the complementary-surface qualification.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from scipy.optimize import least_squares

from scan_tools import (cylinder, cylinder_residual, load_cloud, plane,
                        stats, transform_points, unit)

HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/Users/derekbredensteiner/Documents/3D Scans/2026-09-20-g-ganen-pump')
PASS_ONE = 'pass-01-feet-up/Fused 0920_1 (0.10mm).ply'
PASS_ONE_SHA = '9b400d7a738aa8b69f5d8023f6a2ad4bb2fae7f542e7db0f85ef66cdcd64c05b'
FOOT_REGIONS = (
    ('rear_yplus', [-23, -20, 297], [-4, 0, 316]),
    ('rear_yminus', [-23, -59, 234], [-3, -40, 251]),
    ('head_yplus', [38, -16, 289], [59, 6, 308]),
    ('head_yminus', [38, -54, 226], [59, -34, 245]),
)


def robust_plane(points, normal_hint):
    center = np.mean(points, axis=0)
    n0 = unit(normal_hint)
    u = unit(np.cross(n0, np.eye(3)[np.argmin(abs(n0))]))
    v = np.cross(n0, u)

    def unpack(parameters):
        a, b, distance = parameters
        return center+distance*n0, unit(n0+a*u+b*v)

    def residual(parameters):
        c, n = unpack(parameters)
        return (points-c) @ n

    result = least_squares(residual, [0, 0, 0], loss='soft_l1', f_scale=.08)
    if not result.success:
        raise ValueError('Selected plane fit did not converge')
    c, n = unpack(result.x)
    return c, n, stats(residual(result.x))


def fit_slot(points_xy, center_hint):
    """An obround opening in its section plane; no circular-bore assumption."""
    points_xy = np.asarray(points_xy)

    def residual(parameters):
        cx, cy, angle, half_straight, radius = parameters
        along = np.array([np.sin(angle), np.cos(angle)])
        relative = points_xy-[cx, cy]
        station = np.clip(relative @ along, -half_straight, half_straight)
        return np.linalg.norm(relative-np.outer(station, along), axis=1)-radius

    result = least_squares(residual, [*center_hint, 0, 1.5, 2.5], loss='soft_l1', f_scale=.06,
                           bounds=([center_hint[0]-3, center_hint[1]-3, -.4, 0, 1],
                                   [center_hint[0]+3, center_hint[1]+3, .4, 5, 4.5]))
    cx, cy, angle, half_straight, radius = result.x
    along = np.array([np.sin(angle), np.cos(angle)])
    across = np.array([np.cos(angle), -np.sin(angle)])
    relative = points_xy-[cx, cy]
    t, b = relative @ along, relative @ across
    radial = relative-np.outer(np.clip(t, -half_straight, half_straight), along)
    angles = np.arctan2(radial @ along, radial @ across)
    sectors = len(np.unique(np.floor((angles+np.pi)/(2*np.pi)*12).astype(int)))
    coverage = {
        'positive_flank': int(np.sum((b > .7*radius) & (abs(t) < half_straight+.25*radius))),
        'negative_flank': int(np.sum((b < -.7*radius) & (abs(t) < half_straight+.25*radius))),
        'positive_end': int(np.sum((t > half_straight+.7*radius) & (abs(b) < .8*radius))),
        'negative_end': int(np.sum((t < -half_straight-.7*radius) & (abs(b) < .8*radius))),
    }
    complete = sectors >= 10 and min(coverage.values()) >= 5 and not np.any(result.active_mask)
    return {'center_xy_mm': [float(cx), float(cy)],
            'long_axis_xy': [float(np.sin(angle)), float(np.cos(angle))],
            'width_mm': float(2*radius), 'total_length_mm': float(2*(half_straight+radius)),
            'residual_mm': stats(residual(result.x)), 'fit_success': bool(result.success),
            'at_parameter_bound': bool(np.any(result.active_mask)),
            'observed_angular_sectors_of_12': sectors, 'surface_coverage_points': coverage,
            'status': 'complete_section_observed' if complete else 'partial_profile_only',
            'dimension_scope': 'A partial profile fit does not qualify total opening width or screw passage.'}


def foot_slots(points, normals):
    regions = [('rear_yminus', (31.5, -38.5), 20, 50, -1),
               ('rear_yplus', (39., 38.5), 20, 50, 1),
               ('head_yminus', (-24.5, -38.5), -42, -12, -1),
               ('head_yplus', (-26., 38.5), -42, -12, 1)]
    rows = []
    for name, center, xa, xb, side in regions:
        center = np.array(center)
        delta = points[:, :2]-center
        inward = np.sum(delta*normals[:, :2], axis=1) < -.4
        selected = ((abs(delta[:, 0]) < 5) & (abs(delta[:, 1]) < 4.8)
                    & (points[:, 1]*side > 34.3) & (points[:, 1]*side < 43)
                    & (abs(normals[:, 2]) < .75) & inward)
        sections = []
        for z in (.5, 1.5, 2.5, 3.5):
            mask = selected & (abs(points[:, 2]-z) < .18)
            if mask.sum() < 40:
                sections.append({'height_above_average_plane_mm': z,
                                 'status': 'insufficient_surface_observations', 'points': int(mask.sum())})
                continue
            measured = fit_slot(points[mask, :2], center)
            sections.append({'height_above_average_plane_mm': z, 'points': int(mask.sum()), **measured})
        rows.append({'id': name, 'sections': sections,
                     'selection': {'center_hint_xy': center.tolist(),
                                   'xy_half_window_mm': [5, 4.8], 'outboard_y_mm': [34.3, 43],
                                   'absolute_normal_z_below': .75,
                                   'inward_normal_dot_relative_xy_below': -.4},
                     'qualification': 'Observed slot sections in the unloaded foot pose; not a common bore diameter or loaded mounting pattern.'})
    return rows


def port_profiles(points, normals):
    rows = []
    for side in (-1, 1):
        profiles = []
        # A port is hollow. Near its tip, inward-facing bore observations must
        # not enter the exterior barb fit merely because they share a Y station.
        hint_relative = points[:, [0, 2]]-np.array([-69., 26.9])
        outward_surface = np.sum(hint_relative*normals[:, [0, 2]], axis=1) > .5
        selected = ((points[:, 0] > -77) & (points[:, 0] < -60)
                    & (points[:, 2] > 17) & (points[:, 2] < 37)
                    & (abs(normals[:, 1]) < .90) & outward_surface)
        for station in np.arange(23.125, 38.0, .25):
            mask = selected & (abs(points[:, 1]*side-station) < .125)
            q = points[mask][:, [0, 2]]
            if len(q) < 40:
                continue
            def residual(parameters):
                return np.linalg.norm(q-parameters[:2], axis=1)-parameters[2]
            result = least_squares(residual, [-69, 26.9, 5], loss='soft_l1', f_scale=.06)
            center, radius = result.x[:2], result.x[2]
            angles = np.arctan2(*(q-center).T[::-1])
            sectors = len(np.unique(np.floor((angles+np.pi)/(2*np.pi)*12).astype(int)))
            profiles.append({'outward_station_mm': float(station), 'points': len(q),
                             'center_xz_mm': center.tolist(), 'radius_mm': float(radius),
                             'observed_angular_sectors_of_12': sectors,
                             'circle_residual_mm': stats(residual(result.x))})
        usable = [row for row in profiles if row['observed_angular_sectors_of_12'] >= 8
                  and row['circle_residual_mm']['abs_p95'] < .4
                  and 26 < row['outward_station_mm'] < 36]
        if len(usable) < 8:
            axis = None
        else:
            station = np.array([row['outward_station_mm'] for row in usable])
            centers = np.array([row['center_xz_mm'] for row in usable])
            origin_station = float(np.mean(station))
            design = np.column_stack((np.ones(len(station)), station-origin_station))
            fitted, _, _, _ = np.linalg.lstsq(design, centers, rcond=None)
            direction = unit([fitted[1, 0], side, fitted[1, 1]])
            center = [fitted[0, 0], side*origin_station, fitted[0, 1]]
            axis = {'point_mm': center, 'outward_direction': direction.tolist(),
                    'profiles_used': len(usable),
                    'centerline_fit_residual_mm': stats(np.linalg.norm(centers-design @ fitted, axis=1))}
        rows.append({'id': 'port_yminus' if side < 0 else 'port_yplus',
                     'flow_identity': None, 'profiles': profiles, 'axis': axis,
                     'selection': {'x_mm': [-77, -60], 'z_mm': [17, 37],
                                   'absolute_normal_y_below': .90, 'station_bin_mm': .25,
                                   'exterior_normal_dot_xz_relative_above': .5,
                                   'exterior_xz_center_hint_mm': [-69., 26.9]},
                     'qualification': 'Single-pass exterior sections; usable hose length and final tip station await endpoint and complementary-surface review.'})
    return rows


def render_diagnostics(points, x_shift, ports, source):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
    regions = [('rear negative Y', 20, 50, -1), ('rear positive Y', 20, 50, 1),
               ('head negative Y', -42, -12, -1), ('head positive Y', -42, -12, 1)]
    for ax, (label, xa, xb, side) in zip(axes.ravel(), regions):
        mask = ((points[:, 0] > xa) & (points[:, 0] < xb)
                & (points[:, 1]*side > 27) & (points[:, 1]*side < 49)
                & (points[:, 2] > -2) & (points[:, 2] < 5))
        q = points[mask].copy()
        q = q[np.argsort(-q[:, 2])]
        q[:, 0] += x_shift
        ax.scatter(q[:, 0], q[:, 1], c=q[:, 2], s=.7, vmin=-1, vmax=4,
                   cmap='viridis', linewidths=0)
        ax.set_title(label)
        ax.set_aspect('equal')
        ax.grid(alpha=.2)
        ax.set_xlabel('Reference X (mm)')
        ax.set_ylabel('Reference Y (mm)')
    fig.suptitle('Observed feet; color shows height above average unloaded mounting plane\n'
                 'No circular-bore or flat-pad substitution · input '+source['sha256'][:16], fontsize=11)
    fig.savefig(HERE/'pass-01-feet.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    for port, color in zip(ports, ('#246681', '#ab6d2f')):
        rows = port['profiles']
        x = [row['outward_station_mm'] for row in rows]
        axes[0].plot(x, [2*row['radius_mm'] for row in rows], '.-', color=color, label=port['id'])
        axes[1].plot(x, [row['observed_angular_sectors_of_12'] for row in rows], '.-', color=color)
    axes[0].set_ylabel('Fitted section diameter (mm)')
    axes[0].set_ylim(8, 15)
    axes[0].legend()
    axes[1].set_ylabel('Observed angular sectors / 12')
    axes[1].set_xlabel('Outward Y station from motor-axis plane (mm)')
    axes[1].set_ylim(0, 13)
    axes[1].axhline(8, color='#777777', linestyle='--', linewidth=.8)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle('First-pass barb sections and observed coverage\n'
                 'Partial-circle fits do not qualify an axis or usable hose length', fontsize=12)
    fig.savefig(HERE/'pass-01-port-profiles.png', dpi=180)
    plt.close(fig)


def component_observations(points, x_shift):
    """Inspected first-pass regions; no missing surface is filled by classification."""
    rows = []
    regions = [
        ('motor_casing', 'rigid_casing', [-35.3, -26, 9], [47, 26, 60]),
        ('head_casing', 'rigid_casing', [-80.5, -26, 4], [-35.3, 26, 60]),
        ('switch_housing', 'rigid_casing', [-114, -23, 6], [-80.5, 23, 51]),
        ('port_yminus', 'rigid_barb', [-77, -39, 17], [-60, -23, 38]),
        ('port_yplus', 'rigid_barb', [-77, 23, 17], [-60, 39, 38]),
        ('feet_yminus', 'mounting_feet_compliance_unqualified', [-42, -49, -2], [50, -27, 25]),
        ('feet_yplus', 'mounting_feet_compliance_unqualified', [-42, 27, -2], [50, 49, 25]),
        ('head_support_putty', 'fixture_excluded', [-85, -10, 61], [-50, 30, 82]),
        ('motor_support_putty', 'fixture_excluded', [5, -10, 61], [36, 30, 79]),
        ('loose_leads_below_mounting_plane', 'loose_leads_excluded', [-95, -50, -40], [50, 70, -4]),
        ('loose_leads_outboard', 'loose_leads_excluded', [-100, 49, -40], [50, 70, 30]),
    ]
    union = np.zeros(len(points), dtype=bool)
    for name, role, lo, hi in regions:
        mask = np.all((points >= lo) & (points <= hi), axis=1)
        union |= mask
        if not mask.any():
            continue
        bounds = np.array([points[mask].min(0), points[mask].max(0)])
        bounds[:, 0] += x_shift
        rows.append({'name': name, 'role': role, 'intermediate_selection_mm': [lo, hi],
                     'sampled_points': int(mask.sum()), 'observed_reference_bounds_mm': bounds.tolist(),
                     'selected_index_sha256': hashlib.sha256(np.flatnonzero(mask).astype('<i8').tobytes()).hexdigest()})
    return {'regions': rows, 'unclassified_sampled_points': int((~union).sum()),
            'sampling': 'Every third native observation after the proper rigid reference transform.',
            'scope': 'Inspected region membership and observed bounds only. These regions do not certify complete envelopes or separate every crossing lead from a casing surface.',
            'screw_features': {'status': 'individual external heads and recesses remain under complementary-view inspection'},
            'fixed_lead_exit': {'status': 'retained as a rigid-casing interface to inspect; loose leads are not its envelope'}}


def run(archive):
    points, normals, source = load_cloud(archive/PASS_ONE, PASS_ONE_SHA)
    motor_mask = ((points[:, 0] > 0) & (points[:, 0] < 30)
                  & (points[:, 1] > -25) & (points[:, 1] < 25)
                  & (points[:, 2] > 227) & (points[:, 2] < 247)
                  & (abs(normals[:, 0]) < .25))
    motor_points = points[motor_mask]
    fit_indices = np.arange(len(motor_points)) % 5 != 0
    motor = cylinder(motor_points[fit_indices][::3], [1, .09, -.09], 24)
    motor['held_out_point_residual_mm'] = stats(cylinder_residual(motor_points[~fit_indices], motor))
    motor['held_out_scope'] = 'Every fifth selected native observation withheld from parameter fitting; not independent scanner calibration.'
    motor['native_selection'] = {'min': [0, -25, 227], 'max': [30, 25, 247],
                                  'absolute_normal_x_below': .25}
    hint = unit([.12744, -.8503, .51063])
    feet, selected = [], np.zeros(len(points), dtype=bool)
    for name, lo, hi in FOOT_REGIONS:
        mask = np.all((points >= lo) & (points <= hi), axis=1) & (normals @ hint > .985)
        selected |= mask
        feet.append((name, mask, lo, hi))
    center, zaxis, _ = robust_plane(points[selected][::3], -hint)
    actual_axis = -np.array(motor['axis_direction'])
    xaxis = unit(actual_axis-zaxis*(actual_axis @ zaxis))
    yaxis = np.cross(zaxis, xaxis)
    axis_point = np.asarray(motor['axis_point'])
    origin = axis_point-zaxis*((axis_point-center) @ zaxis)
    rotation = np.vstack((xaxis, yaxis, zaxis))
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = -rotation @ origin
    p = transform_points(points, transform)
    n = normals @ rotation.T
    seam_mask = ((p[:, 0] > -36.8) & (p[:, 0] < -35.3)
                 & (abs(n[:, 0]) > .99) & (abs(p[:, 1]) < 26)
                 & (p[:, 2] > 9) & (p[:, 2] < 60))
    seam_center, seam_normal, seam_residual = plane(p[seam_mask])
    if seam_normal[0] < 0:
        seam_normal = -seam_normal
    motor_origin = transform_points([axis_point], transform)[0]
    motor_axis = rotation @ actual_axis
    seam_distance = np.dot(seam_center-motor_origin, seam_normal)/np.dot(motor_axis, seam_normal)
    seam_axis_point = motor_origin+seam_distance*motor_axis
    datum_shift = seam_axis_point[0]
    reference = transform.copy()
    reference[0, 3] -= datum_shift
    foot_report = [{'id': name, 'native_bounds_mm': [lo, hi], 'points': int(mask.sum()),
                    'height_from_average_mounting_plane_mm': stats((points[mask]-center) @ zaxis)}
                   for name, mask, lo, hi in feet]
    # Feature selections are in the preserved intermediate mounting frame. Every
    # output center is translated into the explicit motor/head reference frame.
    sampled_p, sampled_n = p[::3], n[::3]
    slots = foot_slots(sampled_p, sampled_n)
    for foot in slots:
        for row in foot['sections']:
            if 'center_xy_mm' in row:
                row['center_xy_mm'][0] -= datum_shift
    ports = port_profiles(sampled_p, sampled_n)
    for port in ports:
        for row in port['profiles']:
            row['center_xz_mm'][0] -= datum_shift
        if port['axis']:
            port['axis']['point_mm'][0] -= datum_shift
    motor_reference_point = transform_points([axis_point], reference)[0]
    render_diagnostics(sampled_p, -datum_shift, ports, source)
    return {
        'status': 'first_pass_measurements_read_with_registered_complementary_passes',
        'source': source, 'coordinate_scale_factor': 1.0,
        'native_to_reference': reference.tolist(),
        'native_to_intermediate_mounting_frame': transform.tolist(),
        'reference_x_shift_from_intermediate_mm': float(-datum_shift),
        'frame': {'x_zero': 'Motor-axis intersection with the observed exterior motor/head seam, projected to the average mounting plane.',
                  'positive_x': 'Toward motor rear', 'positive_z': 'Toward the body from the average unloaded foot plane',
                  'motor_axis_inclination_to_mounting_plane_degrees': float(np.degrees(np.arcsin(actual_axis @ zaxis)))},
        'motor': {**motor, 'reference_axis_point': motor_reference_point.tolist(),
                  'reference_axis_direction_toward_rear': motor_axis.tolist(),
                  'diameter_mm': float(2*motor['radius_mm'])},
        'mounting_plane': {'native_center': center.tolist(), 'native_body_normal': zaxis.tolist(),
                           'all_selected_residual_mm': stats((points[selected]-center) @ zaxis),
                           'feet': foot_report, 'material': 'flexible rubber, identified by Derek',
                           'motion': 'Independent removable fore/aft sliders, identified by Derek',
                           'loaded_stiffness': 'not established from surface scans'},
        'motor_head_seam': {'intermediate_center': seam_center.tolist(),
                            'intermediate_normal': seam_normal.tolist(),
                            'residual_mm': seam_residual,
                            'intermediate_selection': {'x': [-36.8, -35.3], 'y': [-26, 26], 'z': [9, 60],
                                                       'absolute_normal_x_above': .99}},
        'mounting_slots': slots, 'ports': ports,
        'component_observations': component_observations(sampled_p, -datum_shift),
        'unobserved_or_unqualified': [
            'First-pass crown surfaces and areas contacting scan putty; consult the complementary-pass report.',
            'Loaded or compressed mounting-foot positions and material stiffness.',
            'Actual hose engagement and hydraulic performance. Flow identity comes from Derek in scan-evidence.json.',
            'Complete rigid envelope, screw-head and lead-exit feature qualification.',
        ],
        'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                        for name in ('analyze_scan.py', 'scan_tools.py')},
        'diagnostic_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                             for name in ('pass-01-feet.png', 'pass-01-port-profiles.png')},
        'production_geometry_changed': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ARCHIVE)
    parser.add_argument('--out', type=Path, default=HERE/'scan-measurements.json')
    args = parser.parse_args()
    report = run(args.archive)
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    (HERE/'pass-01-reference-transform.json').write_text(
        json.dumps(report['native_to_reference'], indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'motor_diameter_mm': report['motor']['diameter_mm'],
                      'motor_held_out_abs_p95_mm': report['motor']['held_out_point_residual_mm']['abs_p95'],
                      'mounting_slots': [{'id': foot['id'], 'sections': [
                          {key: row[key] for key in ('height_above_average_plane_mm', 'status', 'points',
                                                   'width_mm', 'total_length_mm') if key in row}
                          for row in foot['sections']]}
                                          for foot in report['mounting_slots']],
                      'port_axes': [{'id': port['id'], 'axis': port['axis']} for port in report['ports']]}, indent=2))
