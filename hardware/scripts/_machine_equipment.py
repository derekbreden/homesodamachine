"""Scalar inputs and model references for the machine's above-core equipment.

The Rust program places the purchased references, cuts the installed pump joints,
mounting hardware and compressed insulation, and sweeps the selected warm tubes.
This module prepares numbers and port frames; it constructs no Python CAD objects.
"""
from __future__ import annotations

import ast
from functools import cache
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / 'hardware'
LAYOUT = HW / 'manifold-layout'
if str(LAYOUT) not in sys.path:
    sys.path.insert(0, str(LAYOUT))
import above_core as layout
from above_core_bom import stem_elbow_names, union_elbow_names, reservoir_gate_elbow_hosts

IDENTITY = {'rotation': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
            'translation_mm': [0., 0., 0.]}


def _read(relative):
    return json.loads((HW / relative).read_text())


def _literal(relative, name):
    """Read an authored numeric profile without importing its native CAD builder."""
    source = HW / relative
    for statement in ast.parse(source.read_text(), filename=str(source)).body:
        if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name
                for target in statement.targets):
            return ast.literal_eval(statement.value)
    raise KeyError(f'{source}: numeric profile {name}')


def frame(rotation=None, translation=None):
    return {'rotation': rotation or IDENTITY['rotation'],
            'translation_mm': translation or IDENTITY['translation_mm']}


def compose(a, b):
    ar, br = a['rotation'], b['rotation']
    return frame([[sum(ar[i][k] * br[k][j] for k in range(3))
                   for j in range(3)] for i in range(3)],
                 list(layout.point(a, b['translation_mm'])))


def transform(pose):
    return [list(row) + [translation] for row, translation in
            zip(pose['rotation'], pose['translation_mm'], strict=True)]


def _along_y(point, axis):
    """The reference reducer's +Y axis on the installed valve's outlet axis."""
    length = math.sqrt(sum(v * v for v in axis))
    end = [v / length for v in axis]
    cross = [end[2], 0., -end[0]]
    sine = math.sqrt(sum(v * v for v in cross))
    if sine < 1e-9:
        rotation = IDENTITY['rotation'] if end[1] >= 0. else [[1., 0., 0.], [0., -1., 0.], [0., 0., -1.]]
    else:
        u = [v / sine for v in cross]
        cosine = max(-1., min(1., end[1]))
        skew = [[0., -u[2], u[1]], [u[2], 0., -u[0]], [-u[1], u[0], 0.]]
        rotation = [[cosine * (i == j) + (1. - cosine) * u[i] * u[j] + sine * skew[i][j]
                     for j in range(3)] for i in range(3)]
    return frame(rotation, list(point))


def plan():
    return layout.specification()['rear_plumbing']


def _source(relative, input_root=None):
    """Prefer a producer's fine model; frozen references declare a fine payload."""
    path = (Path(input_root).resolve() / 'hardware' if input_root else HW) / relative
    authored = HW / relative
    manifest = authored.parent / 'frozen-asset.json'
    if manifest.is_file():
        selected = json.loads(manifest.read_text()).get('fine_models', {}).get(path.name)
        if selected:
            supplied = path.parent / selected['path']
            return str(supplied if supplied.is_file() else authored.parent / selected['path'])
    model = Path(str(path) + '.npz')
    if relative.startswith('printed-parts/') or model.is_file():
        return str(model)
    return str(Path(str(path) + '.mesh'))


@cache
def _stem():
    return _read('reference/neofit-stem-elbow/reference-parameters.json')


@cache
def _reducer():
    return _read('reference/jg-pp061208w/reference-parameters.json')


def _check_profile():
    return _literal('reference/neofit-acvus44-check/neofit_acvus44_check.py', 'PROFILE')


def _bfp_port(name):
    # The frozen Multiplex reference keeps these public scalar interfaces.
    sys.path.insert(0, str(HW / 'reference/multiplex-asse1022'))
    import multiplex_asse1022
    return getattr(multiplex_asse1022, name)()


def _chain_parts():
    return _read('reference/asse1022-threaded-chain/reference-parameters.json')['components']


def _chain_inlet():
    row = _chain_parts()['pp010822e']
    x = row['visible_profile'][0][0]
    return tuple(row['origin_mm'][i] + row['rotation'][i][0] * x for i in range(3)), \
        tuple(-row['rotation'][i][0] for i in range(3))


def local_ports(name):
    """Native port points, outward axes and tube diameters, independent of geometry."""
    if name == 'bulkhead-water':
        p, u = _chain_inlet()
        return {'outboard': (p, u, 6.35),
                'inboard': (p, tuple(-x for x in u), 6.35)}
    if name in ('gas-regulator', 'co2-inlet'):
        return {'inlet': ((0., 0., 0.), (0., 0., -1.), 6.35),
                'outlet': ((0., 0., 62.814), (0., 0., 1.), 6.35),
                'outboard': ((0., 0., 0.), (0., 0., -1.), 6.35),
                'inboard': ((0., 0., 62.814), (0., 0., 1.), 6.35)}
    if name in ('gas-check', 'discharge-chain'):
        end = _check_profile()[-1][0]
        return {'inlet': ((0., 0., 0.), (-1., 0., 0.), 6.35),
                'outlet': ((end, 0., 0.), (1., 0., 0.), 6.35),
                'tube-port': ((end, 0., 0.), (1., 0., 0.), 6.35)}
    if name == 'water-split':
        return {'supply': ((0., 19.5, 0.), (0., 1., 0.), 6.35),
                'to-vk': ((0., 0., 19.5), (0., 0., 1.), 6.35),
                'to-flavor': ((0., 0., -19.5), (0., 0., -1.), 6.35)}
    if name in ('suction-reducer', 'discharge-reducer'):
        mouth = _reducer()['length_mm'] - (_reducer()['nominal_free_stem_to_shoulder_mm'] - 10.)
        return {'tube': ((mouth, 0., 0.), (1., 0., 0.), 6.35)}
    if name == 'jg-pp061208w':
        row = _chain_parts()['pp061208w']
        x = row['visible_axial_range_mm'][1]
        p = tuple(row['origin_mm'][i] + row['rotation'][i][0] * x for i in range(3))
        return {'tube': (p, tuple(row['rotation'][i][0] for i in range(3)), 6.35)}
    if name in stem_elbow_names() or name in reservoir_gate_elbow_hosts():
        return {'socket': ((0., _stem()['socket_mouth_y_mm'], 0.), (0., 1., 0.), 6.35)}
    if name in ('valve-v-a', 'valve-v-b', 'vk-solenoid'):
        return {'inlet': ((0., -29.75, 11.05), (0., -1., 0.), 6.35),
                'outlet': ((0., 29.75, 11.05), (0., 1., 0.), 6.35)}
    if name == 'asse1022-assembly':
        return {'tube-in': (*_bfp_port('inlet'), 17.15),
                'tube-out': (*_bfp_port('outlet'), 15.88),
                'vent-tip': (*_bfp_port('vent'), 7.7)}
    if name == 'flow-regulator':
        return {'inlet': ((0., 0., 0.), (-1., 0., 0.), 6.35),
                'outlet': ((68.117, 0., 0.), (1., 0., 0.), 6.35)}
    if name == 'asse-drain-adapter':
        p = _bfp_port('vent')[0]
        return {'tube': ((p[0] - 25.4, p[1], p[2] - 9.55), (-1., 0., 0.), 4.)}
    if name == 'g-ganen-pump':
        data = _read('reference/g-ganen-pump/reference-parameters.json')['ports']
        crest = max(2. * row['radius_mm'] for port in data.values()
                    for row in port['profile'] if -row['distance_from_tip_mm'] <= 11.)
        cuff_diameter = math.sqrt(14.6 ** 2 + crest ** 2 - 9. ** 2) + 1.2
        return {name: (data[key]['tip_mm'], data[key]['outward_axis'], cuff_diameter)
                for name, key in (('suction', 'port_yminus'), ('discharge', 'port_yplus'))}
    if name == 'digiten-flow':
        return {'inlet': ((-30.5, 0., 0.), (-1., 0., 0.), 6.35),
                'outlet': ((30.5, 0., 0.), (1., 0., 0.), 6.35)}
    for row in _grid():
        if name != row['name']:
            continue
        if row['native_kind'] == 'quarter':
            a, b = 9.5, -24.79
        else:
            d = _read('reference/neofit-drain-bulkhead/reference-parameters.json')
            a, b = d['near_ring_face_y_mm'], d['far_ring_face_y_mm']
        outer = ((0., a, 0.), (0., 1., 0.), row['tube_od_mm'])
        inner = ((0., b, 0.), (0., -1., 0.), row['tube_od_mm'])
        return {'outboard': outer, 'inboard': inner} if name == 'bulkhead-drain' else {
            'tube-out': outer, 'tube-in': inner}
    return {}


def _grid():
    s = layout.specification()
    g = s['fluid_grid']
    for ir, names in enumerate(g['assignment']):
        for ic, name in enumerate(names):
            gas = name == 'co2-inlet'
            quarter = name in ('bulkhead-water', 'bulkhead-carb') or gas
            yield {'name': name, 'x': g['columns_x_mm'][ic], 'z': g['rows_z_mm'][ir],
                   'tube_od_mm': 6.35 if quarter else 4., 'flange_y': s['enclosure']['rear_y_mm'],
                   'nut_af_mm': 21.0058 if gas else 20. if quarter else 18.,
                   'nut_depth_mm': 7.0104 if gas else 4. if quarter else 6.5,
                   'barrel_d_mm': 17. if gas else 17.14 if quarter else 15.,
                   'native_kind': 'gas' if gas else 'quarter' if quarter else 'four'}


def _joint_numbers(port):
    """Installed cuff bore and clamp stations from the scanned pump barb."""
    pump = _read('reference/g-ganen-pump/reference-parameters.json')
    profile = pump['ports']['port_yminus' if port == 'suction' else 'port_yplus']['profile']
    rows = sorted((p['distance_from_tip_mm'], p['radius_mm']) for p in profile)
    start = rows[0][0] + .9

    def interp(x, points):
        xs, rs = zip(*points)
        return float(np.interp(x, xs, rs))

    rows = [(start, interp(start, rows)), *((x, r) for x, r in rows if x > start)]
    r0, bore = 9.525 / 2., []
    for (x, a), (y, b) in zip(rows, rows[1:]):
        bore.append((x, max(a, r0)))
        if (a - r0) * (b - r0) < 0.:
            bore.append((x + (r0 - a) / (b - a) * (y - x), r0))
    bore += [(0., max(rows[-1][1], r0)), (0., _reducer()['nominal_stem_diameter_mm'] / 2.),
             (10., _reducer()['nominal_stem_diameter_mm'] / 2.)]
    opened = lambda r: math.sqrt(r * r + (15.088 ** 2 - 9.525 ** 2) / 4.)
    bands = {name: [xc, 2. * opened(float(np.interp(np.linspace(xc - 4.5, xc + 4.5, 181),
                                                  *zip(*bore)).max()))]
             for name, xc in (('barb', start / 2.), ('stem', 5.))}
    return {'bore': bore, 'bands': bands, 'pivot_z': -rows[-1][1],
            'tube_od_mm': 15.088, 'tube_id_mm': 9.525}


def _palette():
    import _materials as m
    return {key: list(m.linear(getattr(m, key))) for key in (
        'C_PCBA', 'C_PSU', 'C_RELAY', 'C_C14', 'M_BRASS', 'C_DIGITEN', 'C_VALVE',
        'M_DONOR_BLACK', 'M_PETGF_BLACK', 'M_TPU_BLACK', 'M_JG_BLACK_PP',
        'M_NEOFIT_WHITE_ACETAL', 'M_NEOFIT_ACETAL', 'M_JG_WHITE_PP',
        'M_STAINLESS', 'M_POM_ORANGE', 'M_PVC_CLEAR', 'M_NITRILE_BLACK')}


def numbers(external_ports=None, extra_routes=(), *, input_root=None):
    """The whole equipment piece, with already-placed manifold/core ports supplied by its caller."""
    import soda_inlet
    spec, rear, colors = layout.specification(), plan(), _palette()
    modelpath = lambda relative: _source(relative, input_root)
    inputs_hw = Path(input_root).resolve() / 'hardware' if input_root else HW
    items, frames = [], {}

    def add(name, op='reference', *, pose=None, color=None, **parameters):
        pose = pose or IDENTITY
        if op == 'reference' and parameters.get('source', '').endswith('.npz'):
            from _assembly_model import document
            model = Path(parameters['source'])
            if not document(model).get('presentation') and not Path(str(model)[:-4] + '.mesh').is_file():
                parameters['presentation'] = False
        items.append({'name': name, 'op': op, 'transform': transform(pose),
                      'color': colors[color], **parameters})
        frames[name] = {'transform': transform(pose), 'ports': local_ports(name)}

    references = (
        ('pcba', 'printed-parts/electronics/pcba-tray/pcba-board.step', 'C_PCBA'),
        ('psu', 'reference/meanwell-irm90/meanwell-irm90.step', 'C_PSU'),
        ('relay-1', 'reference/teyleten-relay/teyleten-relay.step', 'C_RELAY'),
        ('relay-2', 'reference/teyleten-relay/teyleten-relay.step', 'C_RELAY'),
        ('c14-inlet', 'reference/iec-c14-inlet/iec-c14-inlet.step', 'C_C14'),
        ('asse1022-assembly', 'reference/multiplex-asse1022/multiplex-asse1022.step', 'M_BRASS'),
        ('digiten-flow', 'reference/digiten-flow-sensor/digiten-flow-sensor.step', 'C_DIGITEN'))
    for name, source, color in references:
        add(name, pose=layout.pose(name), color=color, source=modelpath(source))
    for valve in ('valve-v-g', 'valve-v-j'):
        if valve not in (external_ports or {}):
            continue
        mouth, axis, diameter = external_ports[valve]['outlet']
        # The existing tube-frame interface names the reducer's 4 mm mouth.
        # The purchased reducer's shoulder remains at the 1/4-inch valve mouth.
        if diameter == 4.:
            proud = (1.445 - .827) * 25.4
            mouth = [p - u * proud for p, u in zip(mouth, axis)]
        add('flavor-reducer-' + valve.removeprefix('valve-'),
            pose=_along_y(mouth, axis), color='M_NEOFIT_ACETAL',
            source=modelpath('reference/neofit-flavor-reducer/neofit-flavor-reducer.step'))
    for name in layout.valve_names():
        add(name, 'valve', pose=layout.pose(name), color='C_VALVE',
            source=modelpath('reference/beduan-solenoid/beduan-solenoid.step'),
            clock=layout.pose(name).get('collet_clock_degrees', {}))
    add('g-ganen-pump', pose=layout.pose('g-ganen-pump'), color='M_DONOR_BLACK',
        source=modelpath('reference/g-ganen-pump/g-ganen-pump.step'))
    pump = json.loads((inputs_hw / 'printed-parts/cold-core/foam-cap/foam-cap.numbers.json').read_text())['pump']
    st = pump['snap_station']
    cx, _, cz = pump['centre_world_mm']
    roof = -(pump['bore_radius_mm'] + pump['selected']['cap_arch_wall_mm'])
    add('pump-snap-cap', color='M_PETGF_BLACK',
        source=modelpath('printed-parts/cold-core/foam-cap/pump-snap-cap.step'),
        pose=frame([[1., 0., 0.], [0., 0., 1.], [0., -1., 0.]],
                   [cx, st['y0'], cz - (st['tip'] + roof) / 2.]))
    frames['pump-snap-cap'] = {'transform': transform(IDENTITY), 'ports': {}}
    add('asse-drain-adapter', 'vent-adapter', pose=layout.pose('asse1022-assembly'),
        color='M_TPU_BLACK', vent_tip=_bfp_port('vent')[0])
    for original, name, color in (
            ('pp010822e', 'bulkhead-water', 'M_JG_BLACK_PP'),
            ('gagira', 'gagira-coupling', 'M_STAINLESS'),
            ('pi4512f6s', 'jg-pi4512f6s', None),
            ('pp061208w', 'jg-pp061208w', 'M_JG_WHITE_PP')):
        if color is None:
            import _materials as m
            colors['M_JG_GREY_ACETAL'] = list(m.linear(m.M_JG_GREY_ACETAL))
            color = 'M_JG_GREY_ACETAL'
        pose = rear['chain_frame']
        if original == 'gagira':
            pose = frame(pose['rotation'],
                         [p + (rear['asse_adapter_rise_mm'] if i==2 else 0.)
                          for i,p in enumerate(pose['translation_mm'])])
        add(name, pose=pose, color=color,
            source=modelpath('reference/asse1022-threaded-chain/asse1022-threaded-chain.step'),
            select=[original])
    add('water-split', pose=layout.snapshot_pose('water-split'), color='M_JG_BLACK_PP',
        source=modelpath('reference/jg-pp0208e-tee/jg-pp0208e-tee.step'))
    add('flow-regulator', pose=layout.snapshot_pose('reg'), color='M_NEOFIT_WHITE_ACETAL',
        source=modelpath('reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step'))
    regulator = modelpath('reference/compact-inline-candidates/geometry/candidate-regulator.step')
    add('co2-inlet', pose=rear['gas_frame'], color='M_JG_BLACK_PP', source=regulator,
        select=['inlet_collet'])
    add('gas-regulator', pose=rear['gas_frame'], color='M_JG_BLACK_PP', source=regulator,
        exclude=['inlet_collet'])
    for name, pose in (('gas-check', rear['gas_check_frame']),
                       ('discharge-chain', layout.pose('discharge-chain'))):
        add(name, 'stem-check', pose=pose, color='M_NEOFIT_WHITE_ACETAL', profile=_check_profile())
    j = rear['joint']
    for side in ('suction', 'discharge'):
        add(side + '-tube', 'pump-tube', pose=rear[side + '-joint'], color='M_PVC_CLEAR',
            side=side, joint=_joint_numbers(side), bend=j[side + '_bend'])
        end = j[side + '_bend']['end_frame']
        add(side + '-reducer', 'pump-reducer', color='M_JG_WHITE_PP',
            pose=compose(rear[side + '-joint'], end),
            source=modelpath('reference/jg-pp061208w/jg-pp061208w.step'),
            cut_x=_reducer()['nominal_free_stem_to_shoulder_mm'] - 10.)
        for station, (xc, diameter) in _joint_numbers(side)['bands'].items():
            angle = (j[side + '_barb_roll'] if station == 'barb' else
                     0. if side == 'suction' else j['STEM_ROLL'])
            turn = math.radians(angle)
            pose = frame([[1., 0., 0.], [0., math.cos(turn), -math.sin(turn)],
                          [0., math.sin(turn), math.cos(turn)]])
            if station == 'stem':
                pose = compose(end, pose)
            pose = compose(rear[side + '-joint'], pose)
            keys = j.get('suction_stem_keys', j['suction_keys']) \
                if side == 'suction' and station == 'stem' else j[side + '_keys']
            for kind, color in (('clamp', 'M_STAINLESS'), ('key', 'M_POM_ORANGE')):
                add(f'{side}-{station}-{kind}', 'pump-clamp', pose=pose, color=color,
                    diameter=diameter, xc=xc, keys=keys, kind=kind)
    face = spec['rear_wall']['dry_openings']['keystone']['face_center_mm']
    add('keystone-jack', pose=frame(translation=face), color='C_C14',
        source=modelpath('reference/riteav-keystone/riteav-keystone.step'))
    insert = _stem()['published_socket_insertion_mm']
    depths = {'tee-fold': 12.7, 'lower-valve-elbow': 12.7,
              'lower-pump-elbow': insert + rear['water_male_shoulder_land_mm'],
              'reg-va-elbow': 12.7, 'va-outlet-elbow': 12.7, 'va-south-elbow': insert,
              'carbonator-fold': _reducer()['length_mm'] - (
                  _reducer()['body_face_x_mm'] - _reducer()['body_face_to_stop_display_mm'])
                  + rear['water_male_shoulder_land_mm'],
              'ya-stem-elbow': 10., 'yb-stem-elbow': 10.,
              'drain-outlet-stem': spec['fore_routes']['drain_stem_length_mm'],
              'vb-inlet-turn': 12.7, 'vb-outlet-stem': 12.7, 'vb-outlet-return': 16.891,
              **{name: 12.7 for name in reservoir_gate_elbow_hosts()}}
    for name in stem_elbow_names():
        add(name, 'stem-elbow', pose=layout.snapshot_pose(name), color='M_NEOFIT_WHITE_ACETAL',
            source=modelpath('reference/neofit-stem-elbow/neofit-stem-elbow.step'),
            tip_x=_stem()['stem_shoulder_x_mm'] - depths[name])
    for name in union_elbow_names():
        add(name, pose=layout.snapshot_pose(name), color='M_JG_BLACK_PP',
            source=modelpath('reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step'))
    add('soda-bend-holder', pose=layout.pose('soda-bend-holder'), color='M_PETGF_BLACK',
        source=modelpath('printed-parts/soda-bend-holder/soda-bend-holder.step'))
    insulation = {'plan': soda_inlet.plan(), 'neighbors': list(soda_inlet.SOFT_NEIGHBORS),
                  'valve_pose': layout.pose('vk-solenoid'), 'color': colors['M_NITRILE_BLACK']}
    for row in _grid():
        if row['name'] in ('bulkhead-water', 'co2-inlet'):
            continue
        name = row['name']
        color = 'M_JG_BLACK_PP' if row['native_kind'] == 'quarter' else 'M_NEOFIT_ACETAL'
        source = modelpath('reference/neofit-drain-bulkhead/neofit-drain-bulkhead.step')
        add(name, 'bulkhead', color=color, data=row, source=source,
            pose=frame(translation=[row['x'], row['flange_y'], row['z']]))
        add(name + '-nut', 'bulkhead-nut', color=color, data=row)
    caps = modelpath('printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step')
    for name in ('asse-snap-cap', 'pisco-snap-cap', 'meter-snap-cap', 'regulator-snap-cap'):
        add(name, color='M_PETGF_BLACK', source=caps, select=[name])
    for name, holes, reach, length, setback in (
            ('psu', [(sx * 16.5, sy * 49.) for sx in (-1., 1.) for sy in (-1., 1.)], 6.7, 10., 0.),
            *[(n, [(-33., -6.5), (-33., 6.5)], 1.5, 8., 2.5)
              for n in ('relay-1', 'relay-2')]):
        pose = layout.pose(name)
        axis = layout.vector(pose['rotation'], (0., 0., 1.))
        for number, hole in enumerate(holes, 1):
            point = layout.point(pose, (*hole, 0.))
            for kind, color in (('screw', 'M_STAINLESS'), ('insert', 'M_BRASS')):
                add(f'{name}-{kind}-{number}', 'mount-hardware', color=color,
                    kind=kind, axis=axis, point=point, head_reach=reach,
                    length=length, setback=setback)
    ports = dict(external_ports or {})
    for name, row in frames.items():
        pose = {'rotation': [r[:3] for r in row['transform']],
                'translation_mm': [r[3] for r in row['transform']]}
        ports[name] = {key: [layout.point(pose, p), layout.vector(pose['rotation'], u), d]
                       for key, (p, u, d) in row['ports'].items()}
    routes = local_routes()
    if external_ports is not None:
        import above_core_routes
        routes.update(above_core_routes.route_specifications(
            lambda name, port: ports[name][port], plumbing=sys.modules[__name__]))
    native_routes = dict(routes)
    for route in extra_routes:
        routes[route['name'].removeprefix('tube-')] = {k: v for k, v in route.items() if k != 'name'}
    import _routing
    for name, route in routes.items():
        if 'color' in route:
            continue
        _routing.SPOOL_OF[name] = route['spool']
        import _materials
        route['color'] = list(_materials.linear(_routing.tube_color(name)))
    return {'name': 'machine-equipment', 'items': items, 'frames': frames,
            'world_ports': ports, 'routes': routes,
            'native_connections': layout.logical_connections(),
            'native_route_specs': native_routes, 'native_route_order': list(native_routes),
            'keystone_station': [face[0], face[2]], 'keystone_clearances': [],
            'route_order': list(routes),
            'component_order': [row['name'] for row in items],
            'core_equipment': sorted(layout.core_equipment_names()),
            'colors': colors, 'insulation': insulation}


def build(output, *, external_ports=None, extra_routes=(), input_root=None):
    import _rust_part
    _rust_part.start()
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('machine', 'machine-equipment',
                   numbers(external_ports, extra_routes, input_root=input_root), output)
    result = json.loads((output / 'machine-equipment.json').read_text())
    model = str(output / 'machine-equipment.step.npz')
    for instance in result['instances']:
        instance['model'] = model
    result['model'] = model
    return result



def _reducer_insertion():
    d = _reducer()
    return d['length_mm'] - d['body_face_x_mm'] + d['body_face_to_stop_display_mm']


def route_port_frame(name):
    if name == 'suction-reducer':
        return compose(plan()['suction-joint'], plan()['joint']['suction_bend']['end_frame'])
    return layout.snapshot_pose('reg' if name == 'flow-regulator' else name)


def _offset(point, vector, length=1.):
    return [point[i] + vector[i] * length for i in range(3)]


def _link(a, axis_a, depth_a, b, axis_b, depth_b):
    """Tube between two facing sockets, each end at its receiving depth.

    Where one release face stands past the other, the two sockets overlap
    and the tube runs straight between the two receiving depths.
    """
    ends = _offset(a, axis_a, -depth_a), _offset(b, axis_b, -depth_b)
    if sum((q - p) * u for p, q, u in zip(a, b, axis_a)) < 0.:
        return list(ends)
    return [ends[0], list(a), list(b), ends[1]]


def _line(a, b):
    return {'kind': 'line', 'points_mm': [a, b]}


def _bezier(control):
    return {'kind': 'bezier', 'control_points_mm': control}


def _crowned_beziers(control, crown, intervals=16):
    """Native cubics for a cubic plus ``crown*sin(pi*t)**2`` in Z.

    Cubic Hermite spans preserve position and tangent at every join. For a
    2 mm crown and 16 spans, the position error is bounded by 0.000062 mm
    from the sinusoid's fourth derivative; the base cubic is exact.
    """
    def at(t):
        weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
        point = [sum(w*p[k] for w,p in zip(weights,control)) for k in range(3)]
        derivative = [3*((1-t)**2*(control[1][k]-control[0][k])
                       +2*(1-t)*t*(control[2][k]-control[1][k])
                       +t*t*(control[3][k]-control[2][k])) for k in range(3)]
        point[2] += crown*math.sin(math.pi*t)**2
        derivative[2] += crown*math.pi*math.sin(2*math.pi*t)
        return point, derivative
    result=[]
    h=1/intervals
    for index in range(intervals):
        a,da=at(index*h)
        b,db=at((index+1)*h)
        result.append(_bezier([a,[p+h*d/3 for p,d in zip(a,da)],
                              [p-h*d/3 for p,d in zip(b,db)],b]))
    return result


def _sample_bezier(control, samples=65):
    points = []
    for index in range(samples):
        t = index / (samples - 1)
        weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
        points.append([sum(weight * p[axis] for weight, p in zip(weights, control))
                       for axis in range(3)])
    return points


def local_routes():
    """Explicit native tube paths, including the named socket insertions.

    The fore, pump and folded-gas connections are complete to their stated
    interfaces. Rear soda, vent and flavor continuations beyond their local
    departures are provided for the integration router to finish.
    """
    specification = layout.specification()
    fore = specification['fore_routes']
    result = {}

    def add(name, points, owners, *, segments=None, od=6.35, inside=4.24,
            status='complete_between_named_interfaces', basis='Nominal socket insertion', minimum_radius=None):
        result[name] = {'points_mm': points, 'centerline_mm': points, 'od_mm': od, 'id_mm': inside,
                        'owners': list(owners), 'status': status, 'basis': basis,
                        'segments': segments or [_line(a, b) for a, b in zip(points, points[1:])],
                        'spool': 'red' if 'gas-' in name else
                                 'black' if any(k in name for k in ('drain-vb', 'vb-yb')) else 'white'}
        result[name]['minimum_radius_mm'] = minimum_radius

    ownership = {
        'ya-concealed-link': ('ya-stem-elbow', 'ya-fold-inner'),
        'drain-vb-east-link': ('drain-outlet-stem', 'vb-inlet-turn'),
        'drain-vb-inlet-link': ('vb-inlet-turn', 'valve-v-b'),
        'vb-yb-cross': ('vb-outlet-stem', 'vb-outlet-return'),
        'vb-yb-link': ('vb-outlet-return', 'yb-stem-elbow'),
    }
    for name, points in fore['tubes'].items():
        if name.startswith('soda-') or name in ('va-fore-feed', 'ya-concealed-link'):
            continue
        segments = fore.get('native_segments', {}).get(name)
        if segments is not None:
            pass
        elif name == 'drain-vb-east-link':
            control = fore.get('vb_drain_control_mm', fore.get('b_plumbing', {}).get('inlet_control_mm'))
            if fore.get('b_plumbing', {}).get('inlet_minimum_radius_mm') is None:
                points = [points[0], points[-1]]
                segments = [_line(*points)]
            else:
                segments = [_line(points[0], control[0]), _bezier(control),
                            _line(control[-1], points[-1])]
        elif name == 'vb-yb-link':
            control = fore.get('vb_return_control_mm', fore.get('b_plumbing', {}).get('return_control_mm'))
            crown = fore.get('b_plumbing', {}).get('return_crown_mm', 0.)
            segments = [_line(points[0], control[0]),
                        *(_crowned_beziers(control, crown) if crown else [_bezier(control)]),
                        _line(control[-1], points[-1])]
        radius_key = {'drain-vb-east-link': 'vb_drain_minimum_radius_mm',
                      'vb-yb-link': 'vb_return_minimum_radius_mm'}.get(name)
        radius = fore.get(radius_key) if radius_key else None
        if name == 'drain-vb-east-link' and radius is None:
            radius = fore.get('b_plumbing', {}).get('inlet_minimum_radius_mm')
        add('above-core-' + name, points, ownership[name], segments=segments, minimum_radius=radius)

    result.update(_rear_routes())
    return result


def _arc_three(points):
    a,m,b = (np.array(p,float) for p in points)
    u,v = m-a,b-a
    normal = np.cross(u,v)
    centre = a+(float(u@u)*np.cross(v,normal)+float(v@v)*np.cross(normal,u))/(2.*float(normal@normal))
    normal /= np.linalg.norm(normal)
    start,end = a-centre,b-centre
    angle = math.atan2(float(np.cross(start,end)@normal),float(start@end))
    if angle<0.: angle+=2.*math.pi
    return {'kind':'arc','points_mm':[list(p) for p in points],
            'center_mm':centre.tolist(),'axis':normal.tolist(),
            'angle_rad':angle,'radius_mm':float(np.linalg.norm(start))}


def _rear_routes():
    """Short quarter-inch tubes, ending at their actual receiving stops."""
    parts = sys.modules[__name__]
    import above_core_routes as routes
    result = {}

    def station(name, port):
        p,u,d = local_ports(name)[port]
        frame = route_port_frame(name)
        return layout.point(frame, p), layout.vector(frame['rotation'], u)

    def add(name, segments, owners, radius=None):
        points = routes._points(segments)
        result[name] = {'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':6.35,'id_mm':4.32,'spool':'white','owners':list(owners),
            'from':owners[0],'to':owners[-1],'minimum_radius_mm':radius,
            'status':'complete_between_named_interfaces','basis':'Named receiving socket depths'}

    d = plan()['water_split_stub']
    a,m,b = d['points_mm']
    before = routes._sub(a,routes._mul(d['flow_in'],_reducer_insertion()))
    after = routes._add(b,routes._mul(d['flow_out'],15.7))
    add('above-core-water-split-stub', [routes._line(before,a),_arc_three([a,m,b]),
        routes._line(b,after)], ('jg-pp061208w','water-split'),d['radius_mm'])
    for name, first, port_a, depth_a, second, port_b, depth_b in (
            ('tee-vk-link','water-split','to-vk',15.7,'tee-fold','socket',16.891),
            ('reg-va-link','flow-regulator','outlet',15.,'reg-va-elbow','socket',16.891),
            ('tee-regulator','water-split','to-flavor',15.7,'flow-regulator','inlet',15.),
            ('pump-inlet-link','suction-reducer','tube',_reducer_insertion(),
             'lower-pump-elbow','socket',_stem()['published_socket_insertion_mm'])):
        flex = plan().get('flex_links', {}).get(name)
        if flex:
            if flex['kind'] == 'tangent_cubic':
                a,ua = station(first,port_a)
                b,ub = station(second,port_b)
                a = routes._sub(a,routes._mul(ua,depth_a))
                b = routes._sub(b,routes._mul(ub,depth_b))
                length = math.dist(a,b)
                control = [a,routes._add(a,routes._mul(ua,length/3.)),
                           routes._add(b,routes._mul(ub,length/3.)),b]
                # Derivative controls bound speed along the chord from below;
                # the two acceleration controls bound its norm from above.
                # Consequently curvature <= max_acceleration / min_speed².
                chord = [(b[i]-a[i])/length for i in range(3)]
                velocity = [[3.*(q[i]-p[i]) for i in range(3)]
                            for p,q in zip(control,control[1:])]
                speed = min(sum(v[i]*chord[i] for i in range(3)) for v in velocity)
                acceleration = max(math.sqrt(sum((6.*(r[i]-2.*q[i]+p[i]))**2
                                                  for i in range(3)))
                                   for p,q,r in zip(control,control[1:],control[2:]))
                radius = (speed*speed/acceleration if acceleration else None) if speed>0. else 0.
                add('above-core-'+name,[routes._bezier(control)],(first,second),radius)
                result['above-core-'+name]['radius_basis'] = 'Conservative derivative bound on the tangent cubic'
                continue
            segment = (_arc_three(flex['points_mm']) if flex['kind'] == 'arc'
                       else routes._bezier(flex['points_mm']))
            add('above-core-'+name, [segment], (first, second),
                flex['minimum_radius_mm'])
            continue
        a,ua = station(first,port_a); b,ub = station(second,port_b)
        points = parts._link(a,ua,depth_a,b,ub,depth_b)
        add('above-core-'+name,[routes._line(points[0],points[-1])],(first,second))
    return result


def continuations(station):
    """Water, gas, vent and flavor handoffs to the production core and manifold."""
    import above_core_routes as r
    result = {}

    def add(name, segments, source, destination, radius, *, spool='white', od=6.35, inside=4.32):
        points = r._points(segments)
        result[name] = {'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':od,'id_mm':inside,'spool':spool,'owners':[source[0],destination[0]],
            'from':'.'.join(source),'frm':'.'.join(source),'to':'.'.join(destination),
            'minimum_radius_mm':radius,'radius_mm':radius,'status':'selected_native_layout'}

    data = plan()['water5_bend']
    arcs = data['segments']
    a = arcs[0]['points_mm'][0]
    b = arcs[-1]['points_mm'][-1]
    inserted = r._sub(a,r._mul(data['flow'],16.891))
    segments = [r._line(inserted,a),*arcs]
    add('water-5',segments,('discharge-chain','outlet'),('foam-assembly','water-in'),
        data['radius_mm'])
    a,ua,_ = station('digiten-flow','outlet');b,ub,_ = station('bulkhead-carb','tube-in')
    add('soda-meter-bulkhead',[r._line(r._sub(a,r._mul(ua,15.7)),r._sub(b,r._mul(ub,12.7)))],
        ('digiten-flow','outlet'),('bulkhead-carb','tube-in'),None,spool='blue')

    gas = plan()['co2_tube']
    a = list(station('gas-check','outlet')[0]); top = gas['bend_foot']; floor = list(layout.specification()['gas_guide_world_mm'])
    da,db = gas['bend_tangents_mm']; pa,pb = gas['s_tangents_mm']
    c1 = [a,[a[0],a[1]-da,a[2]],[top[0],top[1],top[2]+db],top]
    c2 = [top,[top[0],top[1],top[2]-pb],[floor[0],floor[1],floor[2]+pa],floor]
    add('above-core-gas-core-drop',[r._line((a[0],a[1]+16.891,a[2]),a),r._bezier(c1),r._bezier(c2)],
        ('gas-check','outlet'),('foam-assembly','co2-in'),gas['minimum_radius_mm'],spool='red')

    # Full receiving straights and tangent bends through the occupied layout.
    add('above-core-va-fore-feed',layout.specification()['fore_routes']['native_segments']['va-fore-feed'],
        ('va-south-elbow','socket'),('ya-stem-elbow','socket'),14.)

    # The integral aft-facing socket keeps the LLDPE straight between the
    # downward vent and OVER. Its small lateral correction is a gentle cubic.
    a,ua,_ = station('asse-drain-adapter','tube');b,ub,_ = station('bulkhead-drain','inboard')
    span = b[1]-a[1]
    control = [a,r._add(a,r._mul(ua,span/3.)),r._add(b,r._mul(ub,span/3.)),b]
    add('drain-vent',[r._line(r._sub(a,r._mul(ua,14.)),a),r._bezier(control),
        r._line(b,r._sub(b,r._mul(ub,10.)))],('asse-drain-adapter','tube'),('bulkhead-drain','inboard'),25.,
        spool='drain-white',od=4.,inside=2.5)
    return result


def _flavor_s_bend(start, heading, offset, axis):
    import above_core_routes as r
    radius = 25.
    # Two equal opposite arcs restore the original tangent.
    distance = math.sqrt(sum(c*c for c in offset))
    angle = math.acos(1.-distance/(2.*radius))
    first,end = r._arc(start,heading,axis,angle,radius)
    u = np.array(heading,float); n = np.array(axis,float)
    tangent = math.cos(angle)*u+math.sin(angle)*np.cross(n,u)
    second,end = r._arc(end,tangent,tuple(-c for c in axis),angle,radius)
    return [first,second],end


def _flavor_rear(flavor, destination):
    """Shared descending bend, lower straight and rear socket approach."""
    import above_core_routes as r
    radius = 25.
    if flavor=='a':
        # Finish the descent ahead of the meter's complete lower spring.
        # The rear straight passes above that leaf, beneath the housing.
        start = (61.,369.5,276.5)
        low_z = 262.
        offset = (destination[0]-start[0],0.,low_z-start[2])
        normal = r._unit(r._cross((0.,1.,0.),offset))
        fall,low = _flavor_s_bend(start,(0.,1.,0.),offset,normal)
        rise = (0.,0.,destination[2]-low_z)
        angle = math.acos(1.-r._norm(rise)/(2.*radius))
        shift_start = (low[0],destination[1]-2.*radius*math.sin(angle),low_z)
        shift,stop = _flavor_s_bend(shift_start,(0.,1.,0.),rise,(1.,0.,0.))
        return [*fall,r._line(low,shift_start),*shift]
    peak, low_z = 303.5, destination[2]
    start = (35.,348.,peak)
    offset = (0.,0.,low_z-peak)
    normal = r._unit(r._cross((0.,1.,0.),offset))
    fall, low = _flavor_s_bend(start,(0.,1.,0.),offset,normal)
    offset = (destination[0]-low[0],0.,destination[2]-low_z)
    angle = math.acos(1.-r._norm(offset)/(2.*radius))
    shift_start = (low[0],destination[1]-2.*radius*math.sin(angle),low_z)
    normal = r._unit(r._cross((0.,1.,0.),offset))
    shift, stop = _flavor_s_bend(shift_start,(0.,1.,0.),offset,normal)
    return [*fall,r._line(low,shift_start),*shift]


def flavor_routes(station):
    """Two 4 mm dispense lines through the pump's east aisle, below the meter."""
    import above_core_routes as r
    result = {}
    radius = 25.

    for flavor, valve, lane, cross_y, aisle, cross_z, lift_y in (
            ('a','valve-v-g',-33.,266.,55.5,296.,291.),
            ('b','valve-v-j',-40.,274.,35.,293.,299.)):
        source,axis,_ = station(valve,'outlet')
        destination,outward,_ = station('bulkhead-flavor-'+flavor,'tube-in')
        if flavor=='a':
            lead = r._rounded([r._sub(source,r._mul(axis,10.)),source,
                (source[0],source[1],292.5),(35.,156.,288.5),(-45.,156.,288.5),(-45.,181.,288.5)],radius)
            lead_end = (-45.,181.,288.5)
        else:
            lead = r._rounded([r._sub(source,r._mul(axis,10.)),source,
                (source[0],source[1],288.5),(source[0],source[1]+radius,288.5)],radius)
            lead_end = (source[0],source[1]+radius,288.5)
        approach = (lane,cross_y-radius-10.,cross_z)
        lane_segments = [r._ease_lane(lead_end,approach)]
        if flavor=='b':
            offset = (lane-lead_end[0],0.,cross_z-lead_end[2])
            normal = r._unit(r._cross((0.,1.,0.),offset))
            lane_segments,approach = _flavor_s_bend(lead_end,(0.,1.,0.),offset,normal)
        crossing = r._rounded([approach,(lane,cross_y,cross_z),(aisle,cross_y,cross_z),
                                (aisle,lift_y,cross_z)],radius)
        peak,low_z = (276.5,262.) if flavor=='a' else (303.5,destination[2])
        offset = (5.5 if flavor=='a' else 0.,0.,peak-cross_z)
        normal = r._unit(r._cross((0.,1.,0.),offset))
        rise,end = _flavor_s_bend((aisle,lift_y,cross_z),(0.,1.,0.),offset,normal)
        rear = _flavor_rear(flavor,destination)
        stop = rear[-1]['points_mm'][-1]
        segments = [*lead,*lane_segments,*crossing,*rise,
                    r._line(end,rear[0]['points_mm'][0]),*rear,
                    r._line(stop,r._sub(destination,r._mul(outward,10.)))]
        points = r._points(segments)
        result['fluid-'+('18' if flavor=='a' else '28')] = {
            'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':4.,'id_mm':2.5,'spool':'flavor-black-4mm',
            'owners':[valve,'bulkhead-flavor-'+flavor],
            'from':valve+'.outlet','frm':valve+'.outlet','to':'bulkhead-flavor-'+flavor+'.tube-in',
            'minimum_radius_mm':radius,'radius_mm':radius,'status':'selected_native_layout'}
    return result

