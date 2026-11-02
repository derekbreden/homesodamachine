"""The casing's source-frame placements, without importing its native route builders."""

from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_rust_part.py').is_file())
COLD = ROOT / 'hardware/printed-parts/cold-core'
for path in (ROOT / 'hardware/scripts', COLD, ROOT / 'hardware/printed-parts/cadlib'):
    sys.path.insert(0, str(path))


def stack_numbers():
    from _cadq_export import note_read
    from _foam_cap import cap_face_z, lid_total_height, stack_floor_z
    from _materials import linear, C_FOAM_SHELL, C_CAP_LID_TOP, C_CAP_BOTTOM

    def piece(name, folder, color, rotation=0., z=0.):
        model = f'hardware/printed-parts/cold-core/{folder}/{name}.step.npz'
        note_read(ROOT / model)
        return {'name': name,
                'model': model,
                'color': list(linear(color)),
                'rotation_z_degrees': rotation, 'translation': [0., 0., z]}

    return {
        'models': [piece('foam-shell', 'foam-shell', C_FOAM_SHELL),
                   piece('foam-cap-lid-top', 'foam-cap', C_CAP_LID_TOP,
                         180., cap_face_z-lid_total_height),
                   piece('foam-cap-bottom', 'foam-cap', C_CAP_BOTTOM, z=stack_floor_z)],
        'document': {'frame': 'foam assembly source', 'schema': 'hsm-foam-assembly-1'},
    }


def numbers():
    from _cadq_export import note_read
    import foam_assembly as source
    from _materials import linear
    from _payload_rules import LINEAR_DEFLECTION_RATIO
    route = source.routes
    probes = []
    for name in source.cap_conduits:
        radius = route.line_radius if name == 'reservoir-b-fill' else source.cap_conduit_bore_radius - .3
        if name in source.cap_cable_guides:
            passage = source._above_mounts.cable_guide_points(name)
            probe = {'kind': 'route', 'points': [route.world_point_in_shell(p) for p in passage['points_mm']],
                     'bend': passage['bend_radius_mm']}
        elif name in source.cap_passive_guides or name in ('water-in', 'carb-water-out', 'reservoir-b-fill'):
            probe = {'kind': 'route', 'points': route.routes[name], 'bend': route.route_bend_radius}
        else:
            x, y = source.cap_conduit_station(name)
            probe = {'kind': 'cylinder', 'at': (x, y, source.foam_shell_outer_height - 1.),
                     'height': source.cap_face_z - source.foam_shell_outer_height + 2.}
        probes.append({'name': name, 'radius': radius, **probe,
                       'lower_xy': source.spin_xy(source.cap_conduit_floor_xy[name]),
                       'mouth': source.cap_conduit_mouth(name)[0]})
    obstacles = []
    for name, stem in source.RESERVOIRS.items():
        for label, item, z in ((name, stem, 0.),
                               (f"{name}'s cap", stem.replace('reservoir', 'reservoir-cap'), source.RESERVOIR_CAP_Z)):
            model = f'hardware/printed-parts/cold-core/reservoir/{item}.step.npz'
            note_read(ROOT / model)
            obstacles.append({'name': label,
                              'model': model,
                              'translation': (0., 0., z)})
    return {**stack_numbers(),
            'obstacles': obstacles,
            'envelope': {'tank_radius': route.carbonator_outer_radius,
                         'tank_z': route.carbonator_envelope_z_range,
                         'coil_radius': route.carbonator_coil_envelope_radius,
                         'coil_z': (route.evap_tail_low_z - route.lldpe_tube_od / 2.,
                                    route.evap_tail_high_z + route.lldpe_tube_od / 2.)},
            'routes': [{'name': name, 'points': points, 'color': linear(source.ROUTE_COLORS[name])}
                       for name, points in sorted(route.routes.items())],
            'routing': {'stock_bend': route.route_bend_radius, 'radius': route.line_radius,
                        'floor': route.bend_floor, 'ladder': route.bend_ladder,
                        'touch_volume': route.touch_volume, 'stock': vars(route.route_stock),
                        'prv_flank_y': route.prv_vent_flank_y},
            'report': {'floor': source.stack_floor_z, 'face': source.cap_face_z,
                       'lid_height': source.lid_total_height, 'probes': probes,
                       'co2_points': route.routes['co2-in'],
                       'co2_radius': source.co2_inlet_tube_radius - .3,
                       'co2_height': source.co2_inlet_xyz[2],
                       'lower_probe_radius': source.cap_conduit_bore_radius - .3,
                       'screw_xy': source.attachment_xy_positions,
                       'screw_probe_radius': source.screw_clearance_radius - .3},
            'presentation': {'deflection_ratio': LINEAR_DEFLECTION_RATIO, 'simplification_fraction': .5}}
