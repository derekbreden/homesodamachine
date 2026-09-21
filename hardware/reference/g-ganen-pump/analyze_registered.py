"""Compare independently observed pump features after rigid native-scan alignment.

Each pass is measured separately. Complementary observations are not averaged to
hide surface disagreement or movement of the unloaded mounting feet.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np

from analyze_scan import fit_slot, foot_slots, port_profiles, robust_plane
from scan_tools import cylinder, cylinder_residual, load_cloud, stats, transform_points, unit

HERE = Path(__file__).resolve().parent


def measure_motor(points, normals):
    selection = ((points[:, 0] > 35) & (points[:, 0] < 50)
                 & (abs(points[:, 1]) < 26) & (points[:, 2] > 27)
                 & (points[:, 2] < 60) & (abs(normals[:, 0]) < .15))
    q = points[selection]
    withheld = np.arange(len(q)) % 5 == 0
    fitted = cylinder(q[~withheld], [1, 0, 0], 24.5)
    relative = q-np.asarray(fitted['axis_point'])
    angles = np.arctan2(relative[:, 2], relative[:, 1])
    sectors = len(np.unique(np.floor((angles+np.pi)/(2*np.pi)*12).astype(int)))
    return {**fitted, 'diameter_mm': fitted['radius_mm']*2,
            'held_out_residual_mm': stats(cylinder_residual(q[withheld], fitted)),
            'selected_points': len(q),
            'observed_angular_sectors_of_12': sectors,
            'status': 'local_exposed_arc_fit_not_complete_cylinder_qualification',
            'selection_reference_mm': {'min': [35, -26, 27], 'max': [50, 26, 60],
                                       'absolute_normal_x_below': .15},
            'scope': 'Observed middle-can arcs above the molded lower flanges; the two views have different angular coverage. Their fitted diameters and center offsets are retained separately, not treated as independent calibrated bore readings.'}


def measure_feet(points, normals):
    rows = []
    for end, xa, xb in [('rear', 58, 84), ('head', 0, 25)]:
        for side in (-1, 1):
            selected = ((points[:, 0] > xa) & (points[:, 0] < xb)
                        & (points[:, 1]*side > 32) & (points[:, 1]*side < 47)
                        & (points[:, 2] > -2) & (points[:, 2] < 3)
                        & (normals[:, 2] < -.985))
            q = points[selected]
            row = {'id': end+('_yminus' if side < 0 else '_yplus'),
                   'selected_points': len(q),
                   'selection_reference_mm': {'x': [xa, xb], 'outward_y': [32, 47],
                                              'z': [-2, 3], 'normal_z_below': -.985}}
            if len(q) >= 40:
                center, normal, residual = robust_plane(q, [0, 0, 1])
                row.update({'observed_face_center_mm': center.tolist(),
                            'body_side_normal': normal.tolist(),
                            'plane_residual_mm': residual,
                            'observed_height_mm': stats(q[:, 2])})
            else:
                row['status'] = 'insufficient_observed_bearing_face'
            rows.append(row)
    return rows


def local_foot_slots(points, normals, faces):
    """Opening sections along each observed foot normal, not an assumed flat pad."""
    hints = {'rear_yminus': [68.6, -38.5], 'rear_yplus': [74.5, 38.5],
             'head_yminus': [11.8, -38.5], 'head_yplus': [10.3, 38.5]}
    rows = []
    for face in faces:
        if 'body_side_normal' not in face:
            rows.append({'id': face['id'], 'status': 'bearing_plane_not_observed'})
            continue
        z = np.asarray(face['body_side_normal'])
        x = unit(np.array([1., 0., 0.])-z*z[0])
        y = np.cross(z, x)
        rotation = np.array([x, y, z])
        plane_center = np.asarray(face['observed_face_center_mm'])
        hint = np.array([*hints[face['id']], 0.])
        hint[2] = plane_center[2]-np.dot(hint[:2]-plane_center[:2], z[:2])/z[2]
        q = (points-hint) @ rotation.T
        n = normals @ rotation.T
        selected = ((abs(q[:, 0]) < 5.5) & (abs(q[:, 1]) < 4.7)
                    & (abs(n[:, 2]) < .75)
                    & (np.sum(q[:, :2]*n[:, :2], axis=1) < -.4))
        sections = []
        for depth in (.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.0, 6.5, 7.0):
            mask = selected & (abs(q[:, 2]-depth) < .18)
            if mask.sum() < 40:
                sections.append({'depth_above_local_bearing_plane_mm': depth,
                                 'status': 'insufficient_surface_observations',
                                 'points': int(mask.sum())})
                continue
            measured = fit_slot(q[mask, :2], [0, 0])
            center = np.array([*measured['center_xy_mm'], depth])
            along = np.array([*measured['long_axis_xy'], 0.])
            sections.append({'depth_above_local_bearing_plane_mm': depth,
                             'points': int(mask.sum()), **measured,
                             'center_reference_mm': (center @ rotation+hint).tolist(),
                             'long_axis_reference': (along @ rotation).tolist()})
        rows.append({'id': face['id'], 'local_origin_reference_mm': hint.tolist(),
                     'reference_to_local_rotation': rotation.tolist(),
                     'sections': sections,
                     'scope': 'Cross-sections in the observed unloaded foot pose. A local bearing normal is not a separately measured straight bore axis or loaded mounting pose.'})
    return rows


def measure_tip(points, normals, port):
    side = -1 if port['id'] == 'port_yminus' else 1
    axis = port['axis']
    if not axis:
        return {'status': 'axis_not_qualified'}
    center = np.array(axis['point_mm'])
    direction = np.array(axis['outward_direction'])
    delta = points-center
    axial = delta @ direction
    radial = np.linalg.norm(delta-np.outer(axial, direction), axis=1)
    select = ((radial > 2.5) & (radial < 4.5)
              & (points[:, 1]*side > 36.6) & (points[:, 1]*side < 38.5)
              & (normals @ direction > .92))
    q = points[select]
    if len(q) < 40:
        return {'status': 'insufficient_terminal_face', 'selected_points': len(q)}
    relative = q-center
    angles = np.arctan2(relative[:, 2], relative[:, 0])
    sectors = len(np.unique(np.floor((angles+np.pi)/(2*np.pi)*12).astype(int)))
    plane_center, normal, residual = robust_plane(q, direction)
    tip = center+direction*np.dot(plane_center-center, normal)/np.dot(direction, normal)
    return {'status': ('terminal_face_observed' if sectors >= 9
                       else 'partial_terminal_face_only'),
            'tip_axis_intersection_mm': tip.tolist(), 'plane_normal': normal.tolist(),
            'selected_points': len(q), 'observed_angular_sectors_of_12': sectors,
            'plane_residual_mm': residual,
            'selection': {'radial_mm': [2.5, 4.5], 'outward_y_mm': [36.6, 38.5],
                          'normal_dot_outward_axis_above': .92},
            'scope': 'Terminal annular face fit only; a partial arc does not complete the end-plane qualification.'}


def measure_pass(item, transform, x_shift, baseline_foot_faces=None):
    points, normals, source = load_cloud(item['path'], item['sha256'])
    points, normals = points[::3], normals[::3]
    points = transform_points(points, transform)
    normals = normals @ np.array(transform)[:3, :3].T
    intermediate = points.copy()
    intermediate[:, 0] -= x_shift
    slots = foot_slots(intermediate, normals)
    for foot in slots:
        for section in foot['sections']:
            if 'center_xy_mm' in section:
                section['center_xy_mm'][0] += x_shift
    ports = port_profiles(intermediate, normals)
    for port in ports:
        for profile in port['profiles']:
            profile['center_xz_mm'][0] += x_shift
        if port['axis']:
            port['axis']['point_mm'][0] += x_shift
        port['terminal_face'] = measure_tip(points, normals, port)
    faces = measure_feet(points, normals)
    section_frames = []
    for face in faces:
        if 'body_side_normal' in face:
            section_frames.append({**face, 'plane_source': 'current_observed_bearing_face'})
        elif baseline_foot_faces:
            baseline = next(row for row in baseline_foot_faces if row['id'] == face['id'])
            section_frames.append({**baseline, 'plane_source': 'first_pass_bearing_frame_only'})
        else:
            section_frames.append(face)
    local_sections = local_foot_slots(points, normals, section_frames)
    for foot, frame in zip(local_sections, section_frames):
        foot['plane_source'] = frame.get('plane_source')
    return {'source': source, 'native_to_reference': transform,
            'measurement_stride': 3, 'mounting_slots': slots,
            'mounting_faces': faces, 'local_mounting_slot_sections': local_sections,
            'motor_can': measure_motor(points, normals), 'ports': ports}


def run(registrations):
    initial = json.loads((HERE/'scan-measurements.json').read_text())
    passes = [{'id': 'pass-01-feet-up', **measure_pass(initial['source'],
                initial['native_to_reference'], initial['reference_x_shift_from_intermediate_mm'])}]
    inputs = {'scan-measurements.json': hashlib.sha256((HERE/'scan-measurements.json').read_bytes()).hexdigest()}
    for path in registrations:
        registration = json.loads(path.read_text())
        if registration['scale_factor'] != 1.0:
            raise ValueError('Scaled registration is not accepted')
        fixed = registration['fixed']
        if fixed['sha256'] != initial['source']['sha256']:
            raise ValueError('Expected direct registration to the retained first-pass frame')
        moving = registration['moving']
        identity = Path(moving['path']).parent.name
        passes.append({'id': identity, **measure_pass(moving,
                       registration['moving_native_to_shared'],
                       initial['reference_x_shift_from_intermediate_mm'],
                       passes[0]['mounting_faces'])})
        inputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {'status': 'independent_pass_measurements', 'scale_factor': 1.0,
            'frame': initial['frame'], 'passes': passes,
            'input_sha256': inputs,
            'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                            for name in ('analyze_registered.py', 'analyze_scan.py', 'scan_tools.py')},
            'limits': ['Independent removable rubber feet remain separate observed slider poses; no fixed mounting pattern is inferred.',
                       'Scan residuals are not absolute dimensional tolerance.',
                       'Partial circles and terminal-face arcs remain unqualified.',
                       'No symmetry or fitted scale substitutes for unobserved surfaces.'],
            'production_geometry_changed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('registration', type=Path, nargs='*',
                        default=[HERE/'pass-02-registration.json', HERE/'pass-03-registration.json'])
    parser.add_argument('--out', type=Path, default=HERE/'registered-measurements.json')
    args = parser.parse_args()
    report = run(args.registration)
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    for row in report['passes']:
        print(row['id'], 'motor diameter', round(row['motor_can']['diameter_mm'], 4))
        for port in row['ports']:
            print(port['id'], 'axis', port['axis'], 'tip', port['terminal_face'])
