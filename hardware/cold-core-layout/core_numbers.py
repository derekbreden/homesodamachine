"""Current cold-core bodies, source-frame placements and routing inputs for Rust."""

import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_rust_part.py').is_file())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import cold_core_assembly as source
import _core_points as points
from _materials import linear


def _constants(module, names):
    return {name: getattr(module, name) for name in names.split()}


def _rotation_to_z(axis):
    axis = points.unit(axis)
    dot = max(-1., min(1., axis[2]))
    if dot > 1. - 1e-12:
        return []
    if dot < -1. + 1e-12:
        return [{'axis': (1., 0., 0.), 'degrees': 180.}]
    return [{'axis': points.cross((0., 0., 1.), axis), 'degrees': math.degrees(math.acos(dot))}]


def _rotate(vector, rotations):
    for rotation in rotations:
        vector = points.turned(vector, points.unit(rotation['axis']),
                               math.radians(rotation['degrees']))
    return vector


def _world_to_cap():
    layout = source._above_mounts.above_core
    pose = layout.cap_lid_pose()
    rows = tuple(zip(*pose['rotation']))
    translation = [-points.dot(row, pose['translation_mm']) for row in rows]
    return {'columns': list(zip(*rows)), 'translation': translation}


def numbers():
    V, C, I, F, R = source._V, source._C, source._I, source._F, source._routes
    core = sys.modules['_cold_core_interface']
    reservoir = sys.modules['reservoir']
    floating = sys.modules['_float_interface']
    bridge = sys.modules['reed_bridge']
    ports = source._tube_ports
    rows = []

    def body(kind, name, **data):
        color = source._style.colour_for(name)
        row = {'kind': kind, 'name': name, 'color': linear(color),
               'alpha': color.toTuple()[3], **data}
        rows.append(row)
        return row

    def model(name, folder, stem=None, **placement):
        return body('model', name,
                    model=f'hardware/printed-parts/cold-core/{folder}/{stem or name}.step.npz',
                    printed_presentation=folder in ('foam-shell', 'foam-cap'),
                    **placement)

    for side, seat, direction in (
            ('top', source._foam.cap_face_z - core.head_cbore_depth, -1.),
            ('bottom', source._foam.stack_floor_z + core.head_pad_height, 1.)):
        for i, xy in enumerate(core.attachment_xy_positions, 1):
            body('cap-clamp', f'cap-clamp-{side}-{i}', xy=xy, seat=seat, direction=direction)

    import _reservoir_b_fill as b_fill
    x, y, z = b_fill.passage()['bend_end_world_mm']
    model('reservoir-b-fill-guide', 'foam-cap',
          rotations=[{'axis': (0., 1., 0.), 'degrees': -90.}],
          translation=(x + b_fill.CHANNEL_CENTRE, y - b_fill.BEND_RADIUS, z),
          transform=_world_to_cap(),
          after_rotations=[{'axis': (0., 0., 1.), 'degrees': 180.}],
          after_translation=(0., 0., source.foam_shell_outer_height + source._foam.top_cap_height))

    from foam_numbers import stack_numbers
    for piece in stack_numbers()['models']:
        body('model', piece['name'], model=piece['model'],
             rotations=[{'axis': (0., 0., 1.), 'degrees': piece['rotation_z_degrees']}],
             translation=piece['translation'])

    body('carbonator-tube', 'carbonator-tube')
    for which in ('bottom', 'top'):
        body('endcap', f'endcap-{which}', side=which)
    body('carbonator-rod', 'float-rod-carb')
    body('carbonator-stop', 'float-stop-carb-top')
    for name in ('carbonator-earth-screw', 'carbonator-earth-lockwasher'):
        body(name, name)

    mouths = {}
    for name, port in V.PORTS.items():
        if name in V.PORT_LINES:
            line, which = V.PORT_LINES[name]
            route = R.routes[line]
            a, b = (route[0], route[1]) if which == 'start' else (route[-1], route[-2])
            out = points.unit(points.sub(b, a))
        else:
            out = V.PRV_OUT
        corner, up = V.port_corner(name), V.port_up(name)
        kind = 'male-elbow' if port['plate'] == 'bottom' else 'street-elbow'
        data = {'corner': corner, 'up': up, 'out': out}
        if kind == 'street-elbow':
            data.update(up_leg=V.ELBOW_AXIS_OFFSET, out_leg=F.ELBOW_LEG,
                        male_len=V.male_len(name))
        body(kind, f'carbonator-elbow-{name}', **data)
        reach = F.MALE_ELBOW_MOUTH_REACH if kind == 'male-elbow' else F.ELBOW_LEG
        mouths[name] = {'position': points.add(corner, points.scale(points.unit(out), reach)),
                        'axis': points.unit(out)}

    for name, stem in source.RESERVOIRS.items():
        model(name, 'reservoir', stem)
        model(f'{name}-cap', 'reservoir', stem.replace('reservoir', 'reservoir-cap'),
              translation=(0., 0., reservoir.cap_assembly_lift))
        model(f'{name}-gasket', 'reservoir', 'reservoir-gasket',
              mirror_x=stem.endswith('-left'), seat_top=reservoir.cap_assembly_lift)

    grip_z = reservoir.cap_assembly_lift + reservoir.cap_wall_height
    for letter, side in (('a', 1), ('b', -1)):
        for port, xy in (('fill', reservoir.fill_position[side]),
                         ('draw', reservoir.draw_position[side])):
            body('grommet', f'reservoir-grip-{letter}-{port}', xy=xy, z=grip_z,
                 specification=ports.liquid_grip)
        body('grommet', f'reservoir-grip-{letter}-air', xy=ports.air_position[side],
             z=grip_z, specification=ports.air_grip)
        body('air-tube', f'tube-reservoir-air-{letter}', xy=ports.air_position[side],
             z0=grip_z - ports.air_tube_below_lid,
             z1=source._foam.cap_face_z + ports.air_tube_above_casing)

    body('coil', 'evap-coil')
    for which in ('inlet', 'outlet'):
        body('coil-tail', f'evap-tail-{which}', segments=C.tail_layout(which))

    water_corner, water_up = V.port_corner('water-in'), V.port_up('water-in')
    tip = points.add(water_corner, points.scale(water_up,
                     V.axis_offset('water-in') + V.male_len('water-in')))
    body('jet', 'water-inlet-jet-cap-nominal', at=tip, axis=water_up)
    for name in I.PTC_PORTS:
        mouth = mouths[name]
        origin = points.add(mouth['position'], points.scale(mouth['axis'], I.PTC_STANDOFF))
        body('collet', f'collet-{name}', at=origin, axis=points.scale(mouth['axis'], -1.))

    body('float', 'float-carb', at=(*(V.ROD_RADIUS * v for v in core.carbonator_sensor_axis),
                                   bridge.reed_high_z + V.carbonator_bottom_z))
    for i, z in enumerate(I.carbonator_reed_z(), 1):
        body('reed', f'reed-carb-{i}', at=(*I.carbonator_reed_xy(), z))
    for name, side in (('a', 1), ('b', -1)):
        body('reservoir-rod', f'float-rod-{name}', reservoir=f'reservoir-{name}',
             x=side * I.RES_ROD_X, y=I.RES_ROD_Y)
        body('float', f'float-{name}', at=(side * I.RES_ROD_X, I.RES_ROD_Y,
                                         sum(I.FLOAT_TRAVEL_Z) / 2.))
        for i, z in enumerate(I.reservoir_reed_z(), 1):
            body('reed', f'reed-{name}-{i}', at=(side * I.REED_COLUMN_X, I.reed_y_center, z))
    probe_z = C.gap_z_near(180., sum(V.interior_z) / 2.)
    body('probe', 'probe-carbonator-ds18b20',
         at=(-(core.carbonator_outer_radius + I.PROBE_STANDOFF), 0., probe_z))
    body('probe', 'probe-coil-ds18s20',
         at=C._at_xyz(C.AZ_OUT, C.evap_tail_high_z, C.WIND_R + C.TUBE_R + F.TO92_W / 2.))

    prv = mouths['prv']
    axis = prv['axis']
    rotations = _rotation_to_z(axis)
    vent = _rotate(source.VENT_LOCAL, rotations)
    down = source.VENT_WORLD
    roll = math.degrees(math.atan2(points.dot(axis, points.cross(vent, down)), points.dot(vent, down)))
    rotations.append({'axis': axis, 'degrees': roll})
    body('prv', 'prv-sv125', at=prv['position'], axis=axis)
    model('prv-shroud', 'prv-shroud', rotations=rotations, translation=prv['position'])
    model('reed-bridge', 'reed-bridge',
          rotations=[{'axis': (0., 0., 1.), 'degrees': core.carbonator_sensor_azimuth}],
          translation=(0., 0., V.carbonator_bottom_z))

    trimmed = {name: list(route) for name, route in R.routes.items()}
    for port, (line, which) in V.PORT_LINES.items():
        trimmed[line][0 if which == 'start' else -1] = mouths[port]['position']
    shroud = source._shroud
    local = (0., -shroud.outer_diameter / 2., shroud.vent_station_z)
    vent_mouth = points.add(_rotate(local, rotations), prv['position'])
    trimmed['prv-vent'][0] = tuple(round(v, 6) for v in vent_mouth)
    route_rows = [{'name': name, 'points': trimmed[name],
                   'exempt': source.MADE_UP_ON.get(name, ())}
                  for name in sorted(trimmed)]
    alpha = {row['name']: row['alpha'] for row in rows}
    for route in route_rows:
        name = 'line-' + route['name']
        color = source._style.colour_for(name)
        route.update(color=linear(color), alpha=color.toTuple()[3])
        alpha[name] = route['alpha']

    import _carbonator_bond as bond
    from _cadq_export import note_read
    from _payload_rules import LINEAR_DEFLECTION_RATIO
    for row in rows:
        if row['kind'] == 'model':
            note_read(ROOT / row['model'])
    return {
        'bodies': rows, 'routes': route_rows, 'mouths': mouths,
        'fittings': _constants(F, '''ELBOW_HEX_AF ELBOW_BORE ELBOW_MALE_R SOCKET_R SOCKET_DEPTH
            MALE_ELBOW_BODY_D MALE_ELBOW_MOUTH_REACH MALE_ELBOW_AXIS_REACH MALE_ELBOW_THREAD
            MALE_ELBOW_POST_W MALE_ELBOW_INSERTION MALE_ELBOW_TUBE_OD MALE_ELBOW_FLOW_BORE
            PRV_MALE_LEN PRV_HEX_H PRV_HEX_AF PRV_CAP_R PRV_CAP_H
            REED_GLASS_LEN REED_GLASS_R TO92_W TO92_H TO92_CORNER_R'''),
        'float': _constants(floating, '''height diameter bore_diameter magnet_seat pocket_od
            pocket_id pocket_depth magnet_od magnet_id magnet_thickness'''),
        'collet': _constants(I._ptc, '''COLLET_D COLLET_LENGTH HEX_ACROSS_CORNERS HEX_LENGTH SHANK_D SHANK_LENGTH'''),
        'carbonator': {**_constants(V, '''TUBE_OD TUBE_ID carbonator_height carbonator_bottom_z
            PLATE_D PLATE_T PORT_TAP_D ROD_D ROD_XY REGISTER_DEPTH UPPER_STOP_H
            UPPER_STOP_D UPPER_STOP_BORE bottom_plate_z top_plate_z interior_z'''),
            'register_diameter': V._endcap.register_drill_diameter * V.IN,
            'ports': [{'name': name, **port} for name, port in V.PORTS.items()]},
        'cap_clamp': source.CAP_CLAMP,
        'bond': {**bond.datums(V.top_plate_z[1]), **_constants(bond, '''TUBE_WALL THREAD_DIAMETER
            SCREW_DIAMETER SCREW_LENGTH SCREW_HEAD_DIAMETER SCREW_HEAD_HEIGHT
            WASHER_DIAMETER WASHER_BORE WASHER_THICKNESS''')},
        'coil': {**_constants(C, 'TUBE_R WIND_R TOTAL_WRAPS PITCH WIND_HEIGHT evap_tail_low_z AZ_IN'),
                 'stock': vars(C.COPPER_STOCK), 'bend_floor': C.COPPER_BEND,
                 'path_chord_mm': .0035},
        'ports': _constants(ports, 'plate_thickness air_tube_od air_tube_id'),
        'internals': _constants(I, 'RES_ROD_LEN RES_ROD_X RES_ROD_Y FLOAT_TRAVEL_Z'),
        'jet': _constants(I, 'JET_CAP_D JET_CAP_T JET_PASSAGE_D'),
        'routing': {'radius': R.line_radius, 'stock_bend': R.route_bend_radius,
                    'floor': R.bend_floor, 'ladder': R.bend_ladder,
                    'touch_volume': R.touch_volume, 'tail_names': source.TAIL_LINES,
                    'prv_flank_y': R.prv_vent_flank_y},
        'presentation': {'deflection_ratio': LINEAR_DEFLECTION_RATIO, 'simplification_fraction': .5},
        'card': {'touch_volume': source._card.TOUCH_VOLUME,
                 'joined': sorted(sorted(pair) for pair in source.JOINED),
                 'rides_on': sorted(sorted(pair) for pair in source.RIDES_ON)},
        'document': {'frame': 'foam assembly source', 'schema': 'hsm-cold-core-model-1',
                     'alpha_by_name': alpha},
    }
