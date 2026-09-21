"""Check native G Ganen external solids against disjoint scan observations.

Residuals assess the external clearance model, not scanner calibration. Positive
signed values lie inside a filled occupied envelope; negative values identify
observations outside it. Internal vents, crown recesses and purchased rubber
cavities are intentionally filled. No material mass is inferred from volume.
"""
from pathlib import Path
import argparse
import hashlib
import json

import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree

from derive_casing import casing_selection
from g_ganen_pump import build_parts, parameters, suction, discharge
from scan_tools import load_cloud, stats, transform_points

HERE = Path(__file__).resolve().parent


def native_mesh(shape):
    vertices, faces = shape.tessellate(.08, .15)
    mesh = trimesh.Trimesh(vertices=[[p.x, p.y, p.z] for p in vertices], faces=faces, process=True)
    if not mesh.is_watertight or not mesh.is_winding_consistent:
        raise ValueError('Native validation mesh is not closed and consistently oriented')
    return mesh


def signed(mesh, points):
    output = []
    for start in range(0, len(points), 400):
        output.extend(trimesh.proximity.signed_distance(mesh, points[start:start+400]))
    return np.array(output)


def cylinder_distance(points, row):
    axis = np.array(row['axis_direction'])
    center = np.array(row['axis_point_mm'])
    a, b = row['x_stations_mm']
    start = center+axis*(a-center[0])/axis[0]
    length = (b-a)/axis[0]
    delta = points-start
    station = delta @ axis
    radial = np.linalg.norm(delta-station[:, None]*axis, axis=1)-row['radius_mm']
    axial_out = np.maximum(-station, station-length)
    outer = np.hypot(np.maximum(radial, 0), np.maximum(axial_out, 0))
    inside = np.minimum(-radial, -axial_out)
    return np.where((radial <= 0) & (axial_out <= 0), inside, -outer)


def summary(values):
    return {'signed_distance_mm': stats(values),
            'outside_distance_mm': stats(np.maximum(-values, 0)),
            'observations_outside_0_5_mm': int((-values > .5).sum()),
            'observations_outside_1_0_mm': int((-values > 1.).sum()),
            'scope': 'Positive is inside the occupied envelope; negative is outside. Filled openings can have large positive values and do not represent measured material.'}


def check_inputs(data):
    checked = {}
    for group in ('input_sha256', 'tool_sha256'):
        for filename, expected in data[group].items():
            actual = hashlib.sha256((HERE/filename).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f'Reference parameter input changed: {filename}')
            checked[filename] = actual
    return checked


def run():
    data = parameters()
    input_digests = check_inputs(data)
    source_names = ('validate_reference.py', 'g_ganen_pump.py', 'derive_casing.py', 'scan_tools.py')
    source_digests = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in source_names}
    parts = build_parts()
    native = []
    for name, shape in parts.items():
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError('Invalid native solid: '+name)
        bound = shape.BoundingBox()
        native.append({'name': name, 'valid': True, 'solids': 1, 'faces': len(shape.Faces()),
                       'bounds_mm': [[bound.xmin, bound.ymin, bound.zmin],
                                     [bound.xmax, bound.ymax, bound.zmax]]})
    print('native solids valid', len(parts), flush=True)
    meshes = {name: native_mesh(shape) for name, shape in parts.items()
              if 'rubber_slider' not in name and 'motor_can_vent' not in name}
    body_mesh = meshes['rigid_casing_envelope']
    measured = json.loads((HERE/'registered-measurements.json').read_text())
    corroboration = {}
    for item in measured['passes']:
        p, n, _ = load_cloud(item['source']['path'], item['source']['sha256'])
        transform = np.array(item['native_to_reference'])
        p, n = transform_points(p[1::12], transform), n[1::12] @ transform[:3, :3].T
        selected = casing_selection(p, n) & (p[:, 0] > 24) & (p[:, 0] < 56) & (p[:, 2] < 25)
        corroboration[item['id']] = (cKDTree(p[selected]), n[selected])
    stations = np.array([row['x_mm'] for row in data['casing_sections']])
    readings, plot_data = [], []
    for item in measured['passes']:
        points, normals, source = load_cloud(item['source']['path'], item['source']['sha256'])
        # Every source index here is 1 mod 12, disjoint from the 0 mod 3
        # observations that generated casing sections and third-pass barbs.
        points, normals = points[1::12], normals[1::12]
        transform = np.array(item['native_to_reference'])
        p, n = transform_points(points, transform), normals @ transform[:3, :3].T
        x, y, z = p.T
        disjoint_x = np.min(abs(x[:, None]-stations[None, :]), axis=1) > .36
        selection = casing_selection(p, n) & disjoint_x
        regions = [
            ('head_switch_outer_walls', selection & (x > -77.0) & (x < -.5) & (z > 14) & (z < 53)),
            ('head_side_lug_exteriors', disjoint_x & (x > -18) & (x < -.5) & (abs(y) > 22)
             & (abs(y) < 33.5) & (z > 25) & (z < 42)),
            ('motor_barrel_outer_surface', selection & (x > 3) & (x < 75) & (z > 24)
             & (np.hypot(y, z-34.1) > 23.6)),
            ('fixed_lower_cradle_between_feet', selection & (x > 25) & (x < 55) & (z < 24)),
            ('motor_rear_cap', selection & (x > 76.3) & (x < 81.4) & (z > 20)),
        ]
        if item['id'] == 'pass-03-feet-down':
            regions.append(('head_crown_complementary_view', selection & (x > -44) & (x < -.5) & (z > 53)))
        for name, mask in regions:
            if name == 'fixed_lower_cradle_between_feet':
                matched = np.zeros(int(mask.sum()), dtype=bool)
                for identity, (tree, other_normals) in corroboration.items():
                    if identity != item['id']:
                        distance, index = tree.query(p[mask], k=4)
                        matched |= np.any((distance < .45) &
                                          (np.sum(other_normals[index]*n[mask, None, :], axis=2) > .85), axis=1)
                active = np.flatnonzero(mask)
                mask[active[~matched]] = False
            q = p[mask]
            q = q[::max(1, int(np.ceil(len(q)/2400)))]
            if len(q) < 20:
                readings.append({'pass': item['id'], 'region': name, 'status': 'insufficient_observations', 'points': len(q)})
                continue
            values = signed(body_mesh, q)
            values = np.maximum(values, cylinder_distance(q, data['motor_can_envelope']))
            if name.startswith(('head_', 'motor_', 'fixed_lower')):
                for key, mesh in meshes.items():
                    if key.startswith(('crown_', 'head_outer_shell', 'switch_outer_shell', 'head_side_',
                                       'lower_cradle_occupied', 'motor_surface_')):
                        bounds = mesh.bounds
                        affected = np.all((q > bounds[0]-1) & (q < bounds[1]+1), axis=1)
                        if np.any(affected):
                            values[affected] = np.maximum(values[affected], signed(mesh, q[affected]))
            row = {'pass': item['id'], 'region': name, 'points': len(q), **summary(values),
                   'holdout': 'Native indices 1 mod 12; at least 0.36 mm from every fitted X section (fit half-width 0.24 mm). Additional explicit feature hulls use disjoint native indices. Motor cylinder is independently checked beyond its local source arc.',
                   'largest_outside_observations': [{'point_mm': q[index].tolist(), 'outside_distance_mm': float(-values[index])}
                                                     for index in np.argsort(values)[:10] if values[index] < -.5]}
            readings.append(row)
            plot_data.append((item['id'], name, q, values))
            print(item['id'], name, 'outside p95', round(row['outside_distance_mm']['p95'], 4), 'max', round(row['outside_distance_mm']['max'], 4), flush=True)
        for name, side in [('port_yminus', -1), ('port_yplus', 1)]:
            row = data['ports'][name]
            axis, tip = np.array(row['outward_axis']), np.array(row['tip_mm'])
            delta = p-tip
            axial = delta @ axis
            radial_vectors = delta-axial[:, None]*axis
            radius = np.linalg.norm(radial_vectors, axis=1)
            selected = ((p[:, 1]*side > 24.4) & (p[:, 1]*side < 36.4)
                        & (radius > 3.5) & (radius < 7.)
                        & (np.sum(n*radial_vectors, axis=1) > 2))
            q = p[selected][::2]
            if len(q) < 20:
                readings.append({'pass': item['id'], 'region': name, 'status': 'insufficient_observations', 'points': len(q)})
                continue
            values = signed(meshes[name+'_barb_envelope'], q)
            readings.append({'pass': item['id'], 'region': name+'_barb', 'points': len(q),
                             **summary(values),
                             'holdout': ('Independent earlier pass against the third-pass port model.' if item['id'] != 'pass-03-feet-down'
                                         else 'Native indices 1 mod 12 are disjoint from 0 mod 3 used for profile fitting.')})
            print(item['id'], name, 'abs p95', round(stats(values)['abs_p95'], 4), flush=True)
    joins = []
    for port in ('port_yminus', 'port_yplus'):
        root = parts[port+'_root_envelope']
        joins.append({'port': port, 'root_casing_overlap_mm3': root.intersect(parts['rigid_casing_envelope']).Volume(),
                      'root_barb_overlap_mm3': root.intersect(parts[port+'_barb_envelope']).Volume(),
                      'scope': 'Native continuity check only; occupied-envelope overlap is not actual material volume.'})
        if min(joins[-1]['root_casing_overlap_mm3'], joins[-1]['root_barb_overlap_mm3']) <= 1:
            raise ValueError('Port external envelope is disconnected')
    rotation = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    if np.dot(rotation @ discharge()[1], [-1, 0, 0]) < .999 or np.dot(rotation @ suction()[1], [1, 0, 0]) < .999:
        raise ValueError('Intended flow mapping is inconsistent')
    if any(foot['fixed_hole_pattern'] or foot['through_slot_qualified'] for foot in data['mounting_feet']):
        raise ValueError('The reference must not claim unobserved slot or fixed-pattern qualification')
    if check_inputs(data) != input_digests or any(hashlib.sha256((HERE/name).read_bytes()).hexdigest() != digest
                                                 for name, digest in source_digests.items()):
        raise ValueError('Reference source or parameter input changed during validation')
    report = {'status': 'native_valid_and_measured_residuals_recorded',
              'production_mount_and_route_qualified': False, 'native_solids': native,
              'native_port_continuity': joins, 'readings': readings,
              'native_tessellation': {'linear_deflection_mm': .08, 'angular_tolerance_radians': .15},
              'all_native_solids_valid': True, 'unit_scale_transforms': True,
              'flow_mapping_check': 'Reference +Y discharge maps to enclosure -X under intended +90 degree Z rotation.',
              'reference_parameters_sha256': hashlib.sha256((HERE/'reference-parameters.json').read_bytes()).hexdigest(),
              'verified_parameter_input_digests': input_digests,
              'tool_sha256': source_digests,
              'lower_cradle_corroboration': 'Each selected observation has a second scan surface within 0.45 mm and normal dot product above 0.85. Noncorroborated loose leads are excluded before model comparison.',
              'limits': ['Residuals are comparison to a sprayed optical scan, not absolute scanner tolerance.',
                         'Loose wires, scanning putty and rubber-foot poses are excluded from rigid casing comparison.',
                         'Barb cross-view disagreement remains explicit; no scale or symmetry is used to erase it.',
                         'The four filled foot envelopes cannot qualify through-slot screw passage, washer coverage, clip retention or the loaded clamp stack.',
                         'Native bodies are occupied external envelopes and cannot supply material mass or strength.']}
    render(plot_data)
    report['diagnostic_sha256'] = {'native-validation.png': hashlib.sha256((HERE/'native-validation.png').read_bytes()).hexdigest()}
    return report


def render(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(3, 1, figsize=(12, 8), constrained_layout=True)
    for index, ax in enumerate(axes):
        for identity, region, q, values in rows:
            if identity.startswith(f'pass-0{index+1}'):
                artist = ax.scatter(q[:, 0], q[:, 2], c=-values, s=3,
                                    vmin=-1, vmax=1, cmap='coolwarm')
        ax.set_title(f'Pass {index+1}: held-out external observations')
        ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)'); ax.set_aspect('equal'); ax.grid(alpha=.2)
    figure.colorbar(artist, ax=axes, shrink=.6, label='Outside signed distance (mm); negative = inside filled envelope')
    figure.suptitle('Native G Ganen envelope versus disjoint scan observations\n'
                    'Selected rigid regions; scanner accuracy and mounting fit remain separate', fontsize=12)
    figure.savefig(HERE/'native-validation.png', dpi=160)
    plt.close(figure)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'native-validation.json')
    args = parser.parse_args()
    report = run()
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(args.out)
