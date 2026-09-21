"""Retain separately observed rail, crown-fastener and lead-exit evidence.

Selections are in the retained reference frame. Rail planes describe visible
stock only; purchased rubber clip cavities and their retention force are not
reverse-engineered. Round crown features are external head envelopes, with no
assumption about thread, driver, hidden shank or material.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from scipy.optimize import least_squares

from analyze_scan import robust_plane
from build_reference import hull
from scan_tools import load_cloud, stats, transform_points

HERE = Path(__file__).resolve().parent


def run():
    measurement_path = HERE/'registered-measurements.json'
    measured = json.loads(measurement_path.read_text())
    clouds = []
    for item in measured['passes']:
        p, n, source = load_cloud(item['source']['path'], item['source']['sha256'])
        transform = np.array(item['native_to_reference'])
        clouds.append((transform_points(p[::3], transform), n[::3] @ transform[:3, :3].T,
                       item['id'], source))
    p, n, identity, _ = clouds[-1]
    fasteners = []
    for index, hint in enumerate([[-42, 18], [-42, -18], [-3.6, 18.6], [-3.6, -19.0],
                                  [-23, 16], [-23, -16.6], [-40, 0]], 1):
        relative = p[:, :2]-hint
        radius = np.linalg.norm(relative, axis=1)
        select = ((radius > 2) & (radius < 4.2) & (p[:, 2] > 57.2) & (p[:, 2] < 59.7)
                  & (abs(n[:, 2]) < .8) & (np.sum(relative*n[:, :2], axis=1) > 1))
        q = p[select]
        withheld = np.arange(len(q)) % 5 == 0
        fit = least_squares(lambda v: np.linalg.norm(q[~withheld, :2]-v[:2], axis=1)-v[2],
                            [*hint, 3.], bounds=([hint[0]-1.2, hint[1]-1.2, 2.],
                                                [hint[0]+1.2, hint[1]+1.2, 4.2]),
                            loss='soft_l1', f_scale=.05).x
        residual = np.linalg.norm(q[:, :2]-fit[:2], axis=1)-fit[2]
        radius = np.linalg.norm(p[:, :2]-fit[:2], axis=1)
        top = (radius < fit[2]-.3) & (p[:, 2] > 58) & (p[:, 2] < 60.5) & (n[:, 2] > .85)
        envelope_points = p[(radius < 3.65) & (p[:, 2] > 56.8) & (p[:, 2] < 60.5)]
        fasteners.append({'id': f'crown_round_head_{index:02}', 'measurement_pass': identity,
                          'center_xy_mm': fit[:2].tolist(), 'wall_fit_radius_mm': float(fit[2]),
                          'top_z_p05_p50_p95_mm': np.percentile(p[top, 2], [5, 50, 95]).tolist(),
                          'wall_fit_held_out_residual_mm': stats(residual[withheld]),
                          'selected_wall_points': len(q),
                          'external_envelope': hull(envelope_points),
                          'selection': {'hint_xy_mm': hint, 'wall_radius_band_mm': [2., 4.2],
                                        'wall_z_mm': [57.2, 59.7], 'envelope_radius_limit_mm': 3.65,
                                        'envelope_z_mm': [56.8, 60.5]},
                          'scope': 'Separately visible round external head feature. Filled driver recesses and clipped base are clearance modeling, not a fastener specification.'})
    rails = []
    for side in (-1, 1):
        all_points = np.vstack([p[((p[:, 0] > 25) & (p[:, 0] < 55)
                                   & (p[:, 1]*side > 24) & (p[:, 1]*side < 27.7)
                                   & (p[:, 2] > 17.2) & (p[:, 2] < 22.5))]
                                for p, n, _, _ in clouds])
        center, normal, residual = robust_plane(all_points, [0, side, .65])
        observations = []
        for p, n, name, _ in clouds:
            select = ((p[:, 0] > -3) & (p[:, 0] < 84) & (p[:, 1]*side > 23.5)
                      & (p[:, 1]*side < 28) & (p[:, 2] > 17.2) & (p[:, 2] < 22.5)
                      & (abs((p-center) @ normal) < .45) & (n @ normal > .9))
            q = p[select]
            if len(q) < 10:
                observations.append({'pass': name, 'points': len(q),
                                     'status': 'outer_rail_face_not_observed_in_this_view'})
                continue
            outside_fit = q[(q[:, 0] < 20) | (q[:, 0] > 60)]
            bins = np.arange(-3, 84.25, .25)
            count, edges = np.histogram(q[:, 0], bins)
            present = count >= 3
            observations.append({'pass': name, 'points': len(q),
                                 'outer_face_x_p001_p999_mm': np.percentile(q[:, 0], [.1, 99.9]).tolist(),
                                 'occupied_quarter_mm_axial_bins': [[float(a), float(b)] for a, b in
                                                                  zip(edges[:-1][present], edges[1:][present])],
                                 'end_region_plane_residual_mm': stats((outside_fit-center) @ normal)})
        rails.append({'id': 'rail_yminus' if side < 0 else 'rail_yplus',
                      'sliding_direction': [1., 0., 0.],
                      'observed_outer_plane_point_mm': center.tolist(),
                      'observed_outer_plane_normal': normal.tolist(), 'fit_residual_mm': residual,
                      'plane_fit_selection': {'x_mm': [25., 55.], 'outward_y_mm': [24., 27.7],
                                              'z_mm': [17.2, 22.5]},
                      'independent_end_region_observations': observations,
                      'scope': 'Visible fixed upper rail face and its axial continuation under/along the feet. This does not qualify the hidden rubber clip profile, a hard travel stop, or pull-off force.'})
    molded = []
    p, n, identity, _ = clouds[-1]
    for name, center, half_straight, radius_limit in [
            ('crown_round_molded_boss', [-33.8, -9.8], 0., 6.6),
            ('crown_long_molded_boss', [-12.0, -.15], 5.6, 6.7)]:
        relative = p[:, :2]-center
        distance = np.hypot(relative[:, 0], np.maximum(abs(relative[:, 1])-half_straight, 0.))
        selected = ((distance < radius_limit) & (p[:, 2] > 56.7) & (p[:, 2] < 61.))
        molded.append({'id': name, 'measurement_pass': identity,
                       'external_envelope': hull(p[selected]),
                       'selection': {'center_xy_mm': center, 'axial_half_straight_y_mm': half_straight,
                                     'radial_limit_mm': radius_limit, 'z_mm': [56.7, 61.]},
                       'scope': 'Visible molded crown feature, separate from the seven round head features. Convex external envelope fills shallow detail for clearance.'})
    lead_regions = []
    for name, lo, hi in [('switch_lead_transition', [-67., -8., 5.], [-59., 4., 20.]),
                          ('motor_lead_transition', [75., -8., 5.], [85., 10., 21.])]:
        observations = []
        for p, n, name_pass, _ in clouds:
            q = p[np.all((p > lo) & (p < hi), axis=1)]
            observations.append({'pass': name_pass, 'points': len(q),
                                 'observed_bounds_mm': ([q.min(0).tolist(), q.max(0).tolist()]
                                                        if len(q) else None)})
        lead_regions.append({'id': name, 'inspection_window_mm': [lo, hi],
                             'observations': observations,
                             'scope': 'Observed casing/lead transition region. A protruding rigid strain-relief boundary cannot be separated from the flexible lead by these surface data; no rigid lump or fixed wire route is invented.',
                             'rigid_protrusion_qualified': False})
    foot_tops = []
    for name, center_x, side in [('rear_yminus', 68.6, -1), ('rear_yplus', 74.5, 1),
                                 ('head_yminus', 11.8, -1), ('head_yplus', 10.3, 1)]:
        observations = []
        for p, n, pass_name, _ in clouds:
            selected = ((abs(p[:, 0]-center_x) < 7) & (p[:, 1]*side > 34)
                        & (p[:, 1]*side < 46) & (p[:, 2] > 4) & (p[:, 2] < 10)
                        & (n[:, 2] > .95))
            q = p[selected]
            if len(q) < 40:
                observations.append({'pass': pass_name, 'points': len(q), 'status': 'top_face_not_observed'})
                continue
            center, normal, residual = robust_plane(q, [0, 0, 1])
            observations.append({'pass': pass_name, 'points': len(q),
                                 'top_plane_point_mm': center.tolist(), 'top_plane_normal': normal.tolist(),
                                 'plane_residual_mm': residual,
                                 'z_p05_p50_p95_mm': np.percentile(q[:, 2], [5, 50, 95]).tolist()})
        foot_tops.append({'id': name, 'observations': observations,
                          'scope': 'Unloaded visible pad top in each pose. A top plane paired with another view\'s underside is not a measured compressed clamp stack.'})
    return {'status': 'observed_interfaces_with_explicit_limits', 'scale_factor': 1.,
            'crown_round_heads': fasteners, 'crown_molded_features': molded, 'sliding_rails': rails,
            'lead_exit_regions': lead_regions,
            'foot_top_planes': foot_tops,
            'mounting_limit': 'Rail continuation and removable sliding feet are established. Final pad stations, through-slot hardware passage, washer coverage and loaded clamp stack require integration and a hardware fit check; observed feet are not a fixed bolt pattern.',
            'input_sha256': {measurement_path.name: hashlib.sha256(measurement_path.read_bytes()).hexdigest()},
            'tool_sha256': {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                            for name in ('measure_interfaces.py', 'build_reference.py', 'analyze_scan.py', 'scan_tools.py')},
            'sources': [source for _, _, _, source in clouds]}


if __name__ == '__main__':
    report = run()
    path = HERE/'interface-measurements.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(path)
