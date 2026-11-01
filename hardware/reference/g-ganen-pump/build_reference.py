"""Derive native-reference parameters from retained unit-scale scan observations.

Casing profiles preserve the molded lower housing/rails. Ports use the third
pass's observed axes/end faces. Roots and the movable rubber sliders have explicit
external hulls; those filled envelopes do not qualify internal mounting passages.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from scipy.spatial import ConvexHull

from scan_tools import load_cloud, transform_points

HERE = Path(__file__).resolve().parent


def hull(points):
    shape = ConvexHull(points)
    chosen = np.unique(shape.simplices)
    mapping = {old: new for new, old in enumerate(chosen)}
    vertices = points[chosen]
    triangles = []
    for simplex, equation in zip(shape.simplices, shape.equations):
        a, b, c = points[simplex]
        if np.dot(np.cross(b-a, c-a), equation[:3]) < 0:
            simplex = simplex[::-1]
        triangles.append([mapping[int(index)] for index in simplex])
    return {'vertices_mm': vertices.tolist(), 'triangles': triangles,
            'observed_point_count': len(points), 'bounds_mm': [points.min(0).tolist(), points.max(0).tolist()],
            'scope': 'Convex external clearance envelope of selected observations; holes and hidden clip cavities are filled, not measured material.'}


def _sample_outline(outline, count):
    """Keep each measured corner while sharing the remaining vertices by length."""
    lengths = np.linalg.norm(np.diff(outline, axis=0), axis=1)
    shares = lengths/lengths.sum()*(count-1)
    counts = np.maximum(1, np.floor(shares).astype(int))
    while counts.sum() < count-1:
        counts[np.argmax(shares-counts)] += 1
    while counts.sum() > count-1:
        counts[np.argmax(np.where(counts > 1, counts-shares, -np.inf))] -= 1
    vertices = [outline[0]]
    for first, last, steps in zip(outline, outline[1:], counts):
        vertices.extend(first+(last-first)*t/steps for t in range(1, steps+1))
    return vertices


def motor_underside(sections, observation, motor):
    """Continue observed rigid features through slider occlusions, excluding leads.

    The rail profile is observed between the sliders in both exposed views.
    Its axial continuation preserves the transverse grooves. The molded wire
    cover has an observed end face; beyond it the motor can and rear cap supply
    the rigid surface, independently of the flexible wires crossing them.
    """
    original = json.loads(json.dumps(sections))
    stations = np.array([row['x_mm'] for row in original])
    vertices = np.array([row['vertices_mm'] for row in original])
    training = np.array(observation['rail_profile_stations_mm'])
    known = np.array([next(row['vertices_mm'] for row in original if row['x_mm'] == x)
                      for x in training])
    fit = np.linalg.lstsq(np.column_stack((training, np.ones(len(training)))),
                          known[:, :, 1:3].reshape(len(training), -1), rcond=None)[0]
    template = known[len(known)//2, :, 1:3]
    rails = (np.abs(template[:, 0]) > 14.) & (template[:, 1] < 24.)
    center = (np.abs(template[:, 0]) < 14.) & (template[:, 1] < 16.)
    cover_ids = np.flatnonzero((np.abs(template[:, 0]) < 8.) & (template[:, 1] < 14.))
    angles = np.arctan2(template[:, 1]-32., template[:, 0])
    cover_end = observation['wire_cover_rear_end_x_mm']
    rail_end = observation['fixed_rail_rear_end_x_mm']
    half_step = observation['end_face_axial_allowance_mm']
    added = [cover_end-half_step, cover_end+half_step,
             rail_end-half_step, rail_end+half_step]

    # The clean negative-Y cap arc is visible in both scans. The photographed
    # leads cross its positive-Y side, whose radial measurements are excluded.
    cap_stations = observation['rear_cap_profile_stations_mm']
    cap_radii = []
    for x in cap_stations:
        row = next(item for item in original if item['x_mm'] == x)
        yz = np.array(row['vertices_mm'])[:, 1:3]
        radius = np.linalg.norm(yz-[0., 32.], axis=1)
        for i, angle in enumerate(angles):
            if -np.pi/2 < angle < 0.:
                radius[i] = radius[len(radius)//2-1-i]
        cap_radii.append(radius)

    result = []
    for x in sorted(set(stations.tolist()+added)):
        index = int(np.clip(np.searchsorted(stations, x), 1, len(stations)-1))
        share = (x-stations[index-1])/(stations[index]-stations[index-1])
        points = vertices[index-1]*(1-share)+vertices[index]*share
        points[:, 0] = x
        if 0. <= x <= rail_end-half_step:
            continued = (np.array([x, 1.]) @ fit).reshape(-1, 2)
            axis = np.array(motor['reference_axis_direction_toward_rear'])
            origin = np.array(motor['reference_axis_point'])
            axis_z = origin[2]+axis[2]*(x-origin[0])/axis[0]
            for rail in observation['rail_face_planes']:
                side = rail['side']
                ids = np.flatnonzero(rails & (template[:, 0]*side > 0.))
                a, b, c = [np.array(rail['planes'][name]['z_ax_plus_by_plus_c'])
                           for name in ('outer_upper', 'outer_lower', 'inner_return')]

                def intersection(u, v):
                    y = ((v[0]-u[0])*x+v[2]-u[2])/(u[1]-v[1])
                    return np.array([y, u[0]*x+u[1]*y+u[2]])

                offset = c[0]*x+c[2]-axis_z
                roots = np.roots([1.+c[1]**2, 2.*c[1]*offset,
                                  offset**2-motor['radius_mm']**2])
                y = min((float(v.real) for v in roots if abs(v.imag) < 1e-8 and v.real*side > 0.),
                        key=lambda v: abs(abs(v)-15.))
                join = np.array([y, c[0]*x+c[1]*y+c[2]])
                outer = ids[0] if side < 0 else ids[-1]
                z = continued[outer, 1]
                start = np.array([(z-a[0]*x-a[2])/a[1], z])
                outline = [start, intersection(a, b), intersection(b, c), join]
                rail_vertices = _sample_outline(outline, len(ids))
                if side > 0:
                    rail_vertices.reverse()
                points[ids, 1:3] = rail_vertices
            if x <= cover_end-half_step:
                floor_x, floor_y, floor_c = observation['wire_cover_floor_plane']['coefficients']
                floor_z = floor_x*x+floor_c
                bottom_normal = np.array([-floor_y, 1.])
                bottom_normal /= np.linalg.norm(bottom_normal)
                outline = []
                for cover in observation['wire_cover_side_profiles']:
                    side = cover['side']
                    a, b, c = cover['side_plane']['coefficients']
                    d = a*x+c
                    z = min(np.roots([1.+b*b, 2.*(b*d-axis_z),
                                      d*d+axis_z*axis_z-motor['radius_mm']**2]))
                    join = np.array([d+b*z, z])
                    y = (d+b*floor_z)/(1.-b*floor_y)
                    corner = np.array([y, floor_y*y+floor_z])
                    side_normal = np.array([-float(side), side*b])
                    side_normal /= np.linalg.norm(side_normal)
                    radius = cover['bottom_corner_radius_mm']
                    center_round = corner+radius*np.linalg.solve(
                        np.vstack((bottom_normal, side_normal)), np.ones(2))
                    lower = center_round-radius*bottom_normal
                    wall = center_round-radius*side_normal
                    first, last = (wall, lower) if side < 0 else (lower, wall)
                    angle = np.arctan2(*(first-center_round)[::-1])
                    turn = (np.arctan2(*(last-center_round)[::-1])-angle) % (2.*np.pi)
                    outline.extend([join, wall] if side < 0 else [lower])
                    for fraction in (1./3., 2./3., 1.):
                        theta = angle+turn*fraction
                        outline.append(center_round+radius*np.array([np.cos(theta), np.sin(theta)]))
                    if side > 0:
                        outline.append(join)
                points[cover_ids, 1:3] = _sample_outline(outline, len(cover_ids))
        if cover_end+half_step <= x <= rail_end-half_step:
            axis = np.array(motor['reference_axis_direction_toward_rear'])
            origin = np.array(motor['reference_axis_point'])
            z = origin[2]+axis[2]*(x-origin[0])/axis[0]
            dz = 32.-z
            radius = (-dz*np.sin(angles)
                      + np.sqrt(motor['radius_mm']**2-dz**2*np.cos(angles)**2))
            points[center, 1] = radius[center]*np.cos(angles[center])
            points[center, 2] = 32.+radius[center]*np.sin(angles[center])
        if x >= rail_end+half_step:
            share_cap = np.clip((x-cap_stations[0])/(cap_stations[1]-cap_stations[0]), 0., 1.)
            radius = cap_radii[0]*(1-share_cap)+cap_radii[1]*share_cap
            yz = np.column_stack((radius*np.cos(angles), 32.+radius*np.sin(angles)))
            lower = (points[:, 2] < 24.) | (yz[:, 1] < 24.)
            points[lower, 1:3] = yz[lower]
        row = next((json.loads(json.dumps(item)) for item in original if item['x_mm'] == x),
                   {'x_mm': x, 'scope': 'Axial end of a photographed rigid underside feature.'})
        row['vertices_mm'] = points.tolist()
        if x >= 0.:
            row['underside_source'] = 'underside-observation/rigid-underside.json'
            coverage = {key: row.pop(key) for key in
                        ('observed_bins', 'angular_bins', 'longest_interpolated_angle_degrees') if key in row}
            if coverage:
                row['source_radial_coverage'] = coverage
        result.append(row)
    return result


def run():
    paths = [HERE/'registered-measurements.json', HERE/'casing-sections.json', HERE/'scan-evidence.json',
             HERE/'scan-measurements.json', HERE/'interface-measurements.json',
             HERE/'underside-observation/rigid-underside.json']
    measured, section_ledger, evidence, initial, interfaces, underside = [json.loads(path.read_text()) for path in paths]
    sections = []
    for item in section_ledger['sections']:
        angle = np.array([row['angle_radians'] for row in item['bins']])
        observed = np.array([row['status'] == 'observed' for row in item['bins']])
        radius = np.array([row.get('equal_pass_median_radius_mm', np.nan) for row in item['bins']])
        interpolated = np.interp(angle,
                                 np.r_[angle[observed]-2*np.pi, angle[observed], angle[observed]+2*np.pi],
                                 np.tile(radius[observed], 3))
        vertices = np.column_stack((np.full(len(angle), item['x_mm']),
                                    interpolated*np.cos(angle), 32+interpolated*np.sin(angle)))
        sections.append({'x_mm': item['x_mm'], 'vertices_mm': vertices.tolist(),
                         'observed_bins': int(observed.sum()), 'angular_bins': len(angle),
                         'longest_interpolated_angle_degrees': item['longest_unobserved_angle_degrees']})
    sections = motor_underside(sections, underside, initial['motor'])
    # Observed planar ends are measured separately from radial sections. Their
    # native facets can extend the nearest complete section by less than 0.5 mm.
    clouds = []
    for item in measured['passes']:
        source = item['source']
        p, n, checked = load_cloud(source['path'], source['sha256'])
        p, n = p[::3], n[::3]
        t = np.array(item['native_to_reference'])
        clouds.append((transform_points(p, t), n @ t[:3, :3].T, item['id']))
    end_planes = []
    for label, xa, xb in [('switch_front', -78., -77.3), ('motor_rear', 81.8, 82.7)]:
        values = []
        for p, n, identity in clouds:
            selected = ((p[:, 0] > xa) & (p[:, 0] < xb) & (abs(n[:, 0]) > .99)
                        & (abs(p[:, 1]) < 20) & (p[:, 2] > 10) & (p[:, 2] < 45))
            if selected.sum() > 50:
                values.append({'pass': identity, 'x_median_mm': float(np.median(p[selected, 0])),
                               'points': int(selected.sum()),
                               'x_p05_p95_mm': np.percentile(p[selected, 0], [5, 95]).tolist()})
        station = float(np.median([row['x_median_mm'] for row in values]))
        end_planes.append({'id': label, 'station_mm': station, 'observations': values,
                           'scope': 'Observed axial outer face; the reference cap uses its median X station.'})
    for which, end in [(0, end_planes[0]), (-1, end_planes[1])]:
        copy = json.loads(json.dumps(sections[which]))
        copy['x_mm'] = end['station_mm']
        for point in copy['vertices_mm']:
            point[0] = end['station_mm']
        copy['scope'] = 'Nearest observed radial section at the independently observed axial end plane.'
        if which == 0:
            sections.insert(0, copy)
        else:
            sections.append(copy)
    third = measured['passes'][-1]
    if third['id'] != 'pass-03-feet-down':
        raise ValueError('Complete three-pass measurements are required')
    ports = {}
    for port in third['ports']:
        if port['axis'] is None or port['terminal_face']['status'] != 'terminal_face_observed':
            raise ValueError('Both third-pass port axes and terminal faces must be observed')
        axis = np.array(port['axis']['outward_direction'])
        tip = np.array(port['terminal_face']['tip_axis_intersection_mm'])
        side = 1 if port['id'] == 'port_yplus' else -1
        profile = []
        for row in port['profiles']:
            if row['outward_station_mm'] < 23.875 or row['circle_residual_mm']['abs_p95'] > .35:
                continue
            distance = (side*row['outward_station_mm']-tip[1])/axis[1]
            if distance < -.1:
                profile.append({'distance_from_tip_mm': float(distance), 'radius_mm': row['radius_mm'],
                                'observed_angular_sectors_of_12': row['observed_angular_sectors_of_12']})
        profile.append({'distance_from_tip_mm': 0., 'radius_mm': profile[-1]['radius_mm'],
                        'scope': 'Nearest measured terminal bevel radius at the observed end face.'})
        root_points = []
        for p, n, identity in clouds:
            selected = ((p[:, 1]*side > 20.3) & (p[:, 1]*side < 24.15)
                        & (p[:, 0] > -42.0) & (p[:, 0] < -24.3)
                        & (p[:, 2] > 17.7) & (p[:, 2] < 36.5))
            root_points.append(p[selected])
        ports[port['id']] = {'tip_mm': tip.tolist(), 'outward_axis': axis.tolist(),
                             'flow_identity': 'discharge' if side > 0 else 'suction',
                             'profile': profile, 'root_envelope': hull(np.vstack(root_points)),
                             'measurement_pass': third['id'], 'terminal_face': port['terminal_face'],
                             'profiled_exterior_length_mm': -profile[0]['distance_from_tip_mm'],
                             'hose_engagement_limit': 'The scanned exterior length is not a hose insertion test or a retention rating.'}
    feet = []
    for name, xa, xb, side in [('rear_yminus', 58, 81, -1), ('rear_yplus', 63, 86, 1),
                                ('head_yminus', 0, 24, -1), ('head_yplus', -1, 22, 1)]:
        points, observations = [], []
        nominal_x = {'rear_yminus': 68.6, 'rear_yplus': 74.5,
                     'head_yminus': 11.8, 'head_yplus': 10.3}[name]
        flank_positions = []
        for p, n, identity in clouds:
            region = ((p[:, 0] > xa) & (p[:, 0] < xb) & (p[:, 1]*side > 30)
                      & (p[:, 1]*side < 40) & (p[:, 2] > -.5) & (p[:, 2] < 8.5))
            left = region & (p[:, 0] < nominal_x-5) & (n[:, 0] < -.90)
            right = region & (p[:, 0] > nominal_x+5) & (n[:, 0] > .90)
            if min(left.sum(), right.sum()) >= 20:
                flanks = [float(np.median(p[left, 0])), float(np.median(p[right, 0]))]
                flank_positions.append({'pass': identity, 'outer_flank_x_mm': flanks,
                                        'center_x_mm': float(np.mean(flanks)),
                                        'points': [int(left.sum()), int(right.sum())]})
            else:
                flank_positions.append({'pass': identity, 'center_x_mm': None,
                                        'status': 'insufficient_two_flank_overlap'})
        baseline_face = next(row for row in measured['passes'][0]['mounting_faces'] if row['id'] == name)
        baseline_p, baseline_n, _ = clouds[0]
        face_center, face_normal = np.array(baseline_face['observed_face_center_mm']), np.array(baseline_face['body_side_normal'])
        face_mask = ((baseline_p[:, 0] > xa) & (baseline_p[:, 0] < xb)
                     & (baseline_p[:, 1]*side > 27) & (baseline_p[:, 1]*side < 49)
                     & (baseline_n @ face_normal < -.97)
                     & (abs((baseline_p-face_center) @ face_normal) < .4))
        footprint_points = baseline_p[face_mask, :2]
        footprint = ConvexHull(footprint_points)
        equations = footprint.equations
        baseline_center_x = flank_positions[0]['center_x_mm']
        for p, n, identity in clouds:
            selected = ((p[:, 0] > xa) & (p[:, 0] < xb) & (p[:, 1]*side > 27)
                        & (p[:, 1]*side < 49) & (p[:, 2] > -2) & (p[:, 2] < 18.5))
            q = p[selected]
            pose = next(row for row in flank_positions if row['pass'] == identity)
            dx = ((baseline_center_x-pose['center_x_mm'])
                  if baseline_center_x is not None and pose['center_x_mm'] is not None else 0.)
            aligned = q.copy()
            aligned[:, 0] += dx
            # The observed planar underside identifies the rubber pad outline.
            # A 0.75 mm selection margin admits its rounded edge and bending;
            # this does not add artificial points or expand the output hull.
            in_footprint = np.max(aligned[:, :2] @ equations[:, :2].T+equations[:, 2], axis=1) <= .75
            aligned = aligned[in_footprint]
            points.append(aligned)
            slot = next(row for row in next(row for row in measured['passes']
                        if row['id'] == identity)['local_mounting_slot_sections'] if row['id'] == name)
            observations.append({'pass': identity, 'observed_bounds_mm': [q.min(0).tolist(), q.max(0).tolist()],
                                 'native_foot_pose_translation_to_first_pass_mm': [float(dx), 0., 0.],
                                 'translation_basis': pose,
                                 'observed_bearing_face': next(row for row in next(row for row in measured['passes']
                                         if row['id'] == identity)['mounting_faces'] if row['id'] == name),
                                 'local_slot_sections': slot})
        feet.append({'id': name, 'material': 'flexible rubber',
                     'motion': 'Independent removable fore/aft slider on fixed casing rails.',
                     'external_envelope': hull(np.vstack(points)), 'pose_observations': observations,
                     'baseline_pad_outline_xy_mm': footprint_points[footprint.vertices].tolist(),
                     'outline_source': 'Observed first-pass underside within 0.4 mm of its fitted plane; outer points with normals opposed to the bearing normal.',
                     'selected_outline_margin_mm': .75,
                     'top_plane_observations': next(row for row in interfaces['foot_top_planes'] if row['id'] == name),
                     'fixed_hole_pattern': False, 'through_slot_qualified': False,
                     'scope': 'External envelope at the first-pass slider station; independently observed outer flanks align subsequent foot views along X. Internal slot/rail cavities are not solid material and are deliberately not qualified by this filled clearance volume.'})
    casing_shells = []
    for name, lo, hi in [('head_outer_shell', [-45.5, -24.5, 14.], [-.4, 24.5, 57.9]),
                          ('switch_outer_shell', [-77.9, -23., 14.], [-45.9, 23., 50.2])]:
        selected = []
        for p, n, identity in clouds:
            selected.append(p[np.all((p > lo) & (p < hi), axis=1)])
            if name == 'head_outer_shell' and identity == 'pass-03-feet-down':
                upper = hi.copy()
                upper[2] = 61.
                selected.append(p[np.all((p > lo) & (p < upper), axis=1) & (p[:, 2] >= hi[2])])
        casing_shells.append({'id': name, 'external_envelope': hull(np.vstack(selected)),
                              'selection_window_mm': [lo, hi],
                              'scope': 'External shell envelope spanning visible sidewall features. Ventilation openings and casing recesses are filled conservatively; the lower section model and separate crown features retain the surrounding envelope.'})
    for side in (-1, 1):
        selected = []
        for p, n, identity in clouds:
            mask = ((p[:, 0] > -18) & (p[:, 0] < 0) & (p[:, 1]*side > 19.)
                    & (p[:, 1]*side < 33.5) & (p[:, 2] > 25.) & (p[:, 2] < 42.))
            selected.append(p[mask])
        casing_shells.append({'id': 'head_side_'+('yminus' if side < 0 else 'yplus'),
                              'external_envelope': hull(np.vstack(selected)),
                              'selection_window_mm': {'x': [-18., 0.], 'outward_y': [19., 33.5], 'z': [25., 42.]},
                              'scope': 'Observed rigid side lug at the head/motor end. Its leading shoulder and outboard extent are retained separately from the coarse axial casing sections; any recess is filled for external clearance.'})
    lower_vertices = np.array([point for section in sections for point in section['vertices_mm']
                               if 0 <= point[0] <= 76 and point[2] < 24])
    casing_shells.append({'id': 'lower_cradle_occupied', 'external_envelope': hull(lower_vertices),
                          'rendered': False,
                          'selection_window_mm': {'x': [0., 76.], 'z_upper': 24.},
                          'scope': 'Coarse convex clearance bound of the rigid underside profiles. It is metadata only; the casing profiles supply the visible grooves and finite wire cover. Bearing surfaces use the separately observed wire-cover plane and extent.'})
    for side in (-1, 1):
        selected = []
        for p, n, identity in clouds[1:]:
            mask = ((p[:, 0] > 5.5) & (p[:, 0] < 10.8) & (p[:, 1]*side > 23.)
                    & (p[:, 1]*side < 26.6) & (p[:, 2] > 30.) & (p[:, 2] < 41.))
            selected.append(p[mask])
        casing_shells.append({'id': 'motor_surface_'+('yminus' if side < 0 else 'yplus'),
                              'external_envelope': hull(np.vstack(selected)),
                              'selection_window_mm': {'x': [5.5, 10.8], 'outward_y': [23., 26.6], 'z': [30., 41.]},
                              'scope': 'Localized exterior surface relief confirmed in the second and third views, retained beyond the fitted plain motor cylinder. Shape identity does not imply hidden material or fastening details.'})
    motor = initial['motor']
    return {'status': 'scan_derived_external_reference_with_separate_fit_qualification', 'envelope_only': True,
            'not_for_mass_or_strength': True, 'frame': measured['frame'], 'end_planes': end_planes,
            'casing_sections': sections, 'ports': ports, 'mounting_feet': feet,
            'casing_shell_envelopes': casing_shells,
            'motor_can_envelope': {'axis_point_mm': motor['reference_axis_point'],
                                   'axis_direction': motor['reference_axis_direction_toward_rear'],
                                   'radius_mm': motor['radius_mm'], 'x_stations_mm': [0., 76.],
                                   'scope': 'Measured exposed motor-can cylinder through the straight barrel. Real ventilation openings and internals are filled for external clearance; the separately observed rear-cap profile supplies X beyond 76 mm.'},
            'crown_round_heads': interfaces['crown_round_heads'],
            'crown_molded_features': interfaces['crown_molded_features'],
            'sliding_rails': interfaces['sliding_rails'],
            'lead_exit_regions': interfaces['lead_exit_regions'],
            'rigid_underside': underside,
            'flow_authority': evidence['flow_port_identity'],
            'input_sha256': {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
            'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                            for name in ('build_reference.py', 'g_ganen_pump.py', 'scan_tools.py')},
            'limits': ['Occupied envelopes are not actual material or mass volumes.',
                       'Casing profiles interpolate across occupied branch connections and small angular gaps.',
                       'The four removable rubber sliders do not establish one fixed rectangular hole pattern.',
                       'External foot hulls cover the recorded poses and fill slot/clip cavities; hardware passage and loaded clamp stack remain separate qualifications.',
                       'Visible casing/lead transitions are retained as inspection regions; their flexible lead route and any distinct rigid strain relief remain unqualified.',
                       'World translation, mounting locations, and tubing integration are not inherited from SeaFlo.']}


if __name__ == '__main__':
    output = run()
    path = HERE/'reference-parameters.json'
    path.write_text(json.dumps(output, indent=2)+'\n')
    print(path)
