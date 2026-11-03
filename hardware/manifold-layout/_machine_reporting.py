"""Scalar wiring context and reports from the machine's Rust reference plan."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / 'hardware'
LAYOUT = HW / 'manifold-layout'
_GRID = 2.0 ** -30
_INDEX = re.compile(r'/\d+$')
_ANCHOR_SITES = (
    ('carb-1', 1, (0., 0., 1.), 'enclosure-back-top'),
    ('co2-2', 1, (0., 0., 1.), 'enclosure-back-top'),
    ('fluid-28', 2, (-1., 0., 0.), 'enclosure-back-top'),
)


def _paths():
    for path in (ROOT, HW / 'scripts', LAYOUT, HW / 'cold-core-layout',
                 HW / 'printed-parts/cold-core', HW / 'printed-parts/cold-core/foam-assembly',
                 HW / 'printed-parts/enclosure/enclosure',
                 HW / 'printed-parts/enclosure/bulkhead-ring',
                 HW / 'printed-parts/enclosure/pump-tray',
                 HW / 'printed-parts/electronics/pcba-tray',
                 HW / 'reference/digiten-flow-sensor',
                 HW / 'reference/sf76e-thermal-fuse', HW / 'reference/jg-bulkhead-union'):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def plain(value):
    """Source named records and JSON containers, without a geometry-object protocol."""
    if hasattr(value, '_asdict'):
        return {key: plain(row) for key, row in value._asdict().items()}
    if isinstance(value, dict):
        if '__hsm_namedtuple__' in value:
            return {key: plain(row) for key, row in zip(value['fields'], value['values'], strict=True)}
        if '__hsm_dict__' in value:
            return {str(key): plain(row) for key, row in value['__hsm_dict__']}
        if '__hsm_list__' in value:
            return [plain(row) for row in value['__hsm_list__']]
        return {str(key): plain(row) for key, row in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [plain(row) for row in value]
    if isinstance(value, Path):
        return str(value)
    return value


def scalar_namespace(spec=None):
    """The numeric installed-wiring providers, independent of the CAD assembly driver."""
    _paths()
    import _enclosure_datums
    enc = _enclosure_datums.load()
    import _cold_core_interface as cci
    import foam_assembly as foam
    import _carbonator as carbonator
    import pcba_tray as pcba
    import sf76e_thermal_fuse as fuse
    import digiten_flow_sensor as digiten

    x, y, z = (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)
    relay = ((z, 270.), (y, 270.))
    wagos = {size: HW / f'reference/wago-221/wago-221-{size}.step'
             for size in ('413', '415', '420')}
    values = dict(
        _enc=enc, _cci=cci, _foam=foam, _pcba=pcba, _fuse=fuse, _digiten=digiten,
        _cca=SimpleNamespace(_V=SimpleNamespace(
            _bond=carbonator._bond, top_plate_z=carbonator.top_plate_z)),
        ml=SimpleNamespace(VALVE_STEP=HW / 'reference/beduan-solenoid/beduan-solenoid.step'),
        PCBA_STEP=HW / 'printed-parts/electronics/pcba-tray/pcba-board.step',
        PSU_STEP=HW / 'reference/meanwell-irm90/meanwell-irm90.step',
        RELAY_STEP=HW / 'reference/teyleten-relay/teyleten-relay.step',
        MQ6_STEP=HW / 'reference/mq6-gas-sensor/mq6-gas-sensor.step',
        DIGITEN_STEP=HW / 'reference/digiten-flow-sensor/digiten-flow-sensor.step',
        C14_STEP=HW / 'reference/iec-c14-inlet/iec-c14-inlet.step',
        PCBA_TURN=((y, -90.), (x, -90.)), PSU_TURN=((y, -90.),),
        RELAY_TURN=relay, RELAY2_TURN=relay + ((x, 90.),),
        WAGO_TURN=((x, 90.), (y, -90.)), WAGO_TURN_WEST=((x, 90.), (y, 90.)),
        FUSE_TURN=((x, 90.), (z, 90.)), MQ6_TURN=((x, -90.), (z, 90.)),
        DIGITEN_TURN=((z, 90.), (y, 90.)),
        DISPLAY_TILT=(x, enc.display_facet_angle_deg - 90.),
        wago_step=wagos.__getitem__, WAGO_POLES=('wago-v12', 'wago-gnd', 'wago-g', 'wago-h', 'wago-n'),
        CRADLE_TOL=.01, PORT_NUT_GAP=7., FLOOR_GROMMET_SQUEEZE=.4,
        DIGITEN_COLLET_FREE=digiten.port_face - digiten.port_collar_end,
    )
    values.update((spec or {}).get('metadata', {}).get('wiring_context', {}))
    return SimpleNamespace(**values)


def _point(frame, point):
    return [sum(frame[i][j] * point[j] for j in range(3)) + frame[i][3] for i in range(3)]


def _unit(start, end):
    length = math.dist(start, end)
    return [(b-a) / length for a, b in zip(start, end)]


def _bounds(spec):
    metadata = spec['metadata']
    aliases = spec.get('aliases', {})
    external = set(metadata.get('core_external_names', metadata.get('core_external_components', ())))
    result = {}
    for source, value in metadata['raw_bounds'].items():
        name = aliases.get(source, source)
        if name.startswith('cold-core/'):
            leaf = name[len('cold-core/'):]
            if leaf not in external:
                continue
            name = leaf
        if name.startswith(('wire-', 'wiring-', 'terminal-')):
            continue
        low, high = (value[:3], value[3:]) if len(value) == 6 else value
        if name in result:
            low = [min(a, b) for a, b in zip(result[name][:3], low)]
            high = [max(a, b) for a, b in zip(result[name][3:], high)]
        result[name] = [*low, *high]
    frame = metadata['frames'].get('foam-assembly')
    if frame and 'bb' in frame:
        x0, x1, y0, y1, z0, z1 = frame['bb']
        result['foam-assembly'] = [x0, y0, z0, x1, y1, z1]
    return result


def _ports(frame):
    return {name: ({'pos': plain(row[0]), 'axis': plain(row[1]), 'diam': float(row[2])}
                   if not isinstance(row, dict) else
                   {'pos': plain(row['pos']), 'axis': plain(row['axis']), 'diam': float(row['diam'])})
            for name, row in frame.get('ports', {}).items()}


def _route_rows(metadata):
    specs = metadata.get('native_route_specs', metadata.get('routes', {}))
    lengths = metadata.get('route_lengths', {})
    native = {}
    for name in metadata.get('native_route_order', specs):
        spec = specs[name]
        owners = spec.get('owners', [''])
        native[name] = {
            'id': name, 'frm': spec.get('frm', spec.get('from', owners[0])),
            'to': spec.get('to', owners[-1]), 'length': float(lengths[name]),
            'corners': sum(row['kind'] != 'line' for row in spec['segments']),
            'bend': float(spec.get('minimum_radius_mm') or 0.), 'diam': float(spec['od_mm']),
            'made': 'drawn', 'segments': plain(spec['segments']), 'spool': spec.get('spool'),
        }
    runs = [{'id': row['id'], 'frm': row['frm'], 'to': row['to'],
             'length': _run_length(row), 'corners': len(row['bends']),
             'bend': float(row['bend']), 'diam': float(row['diam']),
             'made': 'drawn', 'status': 'complete'}
            for row in metadata.get('runs', ()) if row['id'] not in specs]
    groups = metadata.get('native_connections', {})
    names = set(metadata['raw_bounds'])
    names.update(name.rsplit('/', 1)[-1] for name in tuple(names))
    grouped = {name for group in groups.values() for name in group['native_routes']}
    for name in metadata.get('connection_order', metadata.get('native_connection_order', groups)):
        group = groups[name]
        rows = [native[key] for key in group['native_routes'] if key in native]
        missing = [key for key in group['native_routes'] if key not in native]
        fittings = [key for key in group.get('fittings', ()) if key not in names]
        complete = not missing and not fittings
        runs.append({'id': name, 'frm': group['from'], 'to': group['to'],
                     'length': sum(row['length'] for row in rows) if complete else None,
                     'corners': sum(row['corners'] for row in rows),
                     'bend': min((row['bend'] for row in rows if row['bend'] > 0.), default=0.),
                     'diam': max((row['diam'] for row in rows), default=0.),
                     'made': group['made'], 'native_routes': list(group['native_routes']),
                     'fittings': list(group.get('fittings', ())),
                     'status': 'complete' if complete else 'incomplete',
                     'missing_native_routes': missing, 'missing_fittings': fittings})
    runs.extend({**row, 'status': 'complete'} for name, row in native.items() if name not in grouped)
    return runs, list(native.values())


def _run_length(row):
    if 'length' in row:
        return float(row['length'])
    straight = sum(math.dist(a, b) for a, b in zip(row['pts'], row['pts'][1:]))
    radii = {int(key): value for key, value in row['radii'].items()}
    return straight-sum(2*radii[index]*math.tan(math.radians(turn)/2)-radii[index]*math.radians(turn)
                        for index, turn, _in, _out in row['bends'])


def route_metadata(spec, checked):
    """The existing tube handoff, from exact numeric routes, ports and anchor stations."""
    metadata = spec['metadata']
    if 'route_metadata' in metadata:
        return plain({**metadata['route_metadata'],
                      'unsupported_spans': checked.get('unsupported_spans',
                          metadata['route_metadata'].get('unsupported_spans', {}))})
    ea = scalar_namespace(spec)
    import _routing
    specs = metadata.get('native_route_specs', metadata.get('routes', {}))
    frames = {name: _ports({'ports': ports}) for name, ports in metadata.get('world_ports', {}).items()}
    frames.update({name: _ports(row) for name, row in metadata['frames'].items()})
    ends, spools = {}, {}
    for run in metadata['runs']:
        name = run['id']
        ends[name] = {}
        for which, owner, point, tangent in (
                ('frm', run['frm'], run['pts'][0], _unit(*run['pts'][:2])),
                ('to', run['to'], run['pts'][-1], _unit(*run['pts'][-1:-3:-1]))):
            component, _, port = owner.partition('.')
            table = frames.get(component, {})
            if table:
                port = port or min(table, key=lambda key: math.dist(table[key]['pos'], point))
                held = table[port]
                ends[name][which] = {'frame': component, 'port': port,
                                     'at': held['pos'], 'normal': held['axis'], 'diam': held['diam']}
            else:
                if port:
                    raise KeyError(f'{component}.{port}: the placement plan has no named port frame')
                ends[name][which] = {'frame': component, 'port': 'socket',
                                     'at': point, 'normal': tangent, 'diam': run['diam']}
        spool = (_routing.SPOOLS[specs[name]['spool']] if name in specs and specs[name].get('spool')
                 else _routing.spool_of(name))
        spools[name] = {key: plain(getattr(spool, key)) for key in
                       ('name', 'rgb', 'alpha', 'roughness', 'metalness', 'names')}
    carry = metadata['core_carry']
    ids = {row['id'] for row in metadata['runs']}
    cap = {name: _point(carry, (*ea._foam.cap_anchor_station(name),
                               ea._foam.cap_face_z + ea._cci.cap_anchor_axis_over_face(name)))
           for name in ea._cci.cap_anchors if name in ids}
    side = {name: _point(carry, (*ea._foam.cap_side_anchor_station(name),
                                ea._foam.cap_face_z + row.over_face))
            for name, row in ea._cci.cap_side_anchors.items() if name in ids}
    return plain({'schema': 1, 'native_route_specs': specs,
                  'anchor_sites': metadata.get('anchor_sites', _ANCHOR_SITES),
                  'tube_anchor_sites': metadata.get('tube_anchor_sites'), 'ends': ends,
                  'cap_anchor_points': cap, 'cap_side_anchor_points': side, 'spools': spools,
                  'unsupported_spans': checked['unsupported_spans']})


def scene_document(spec, checked, *, taken=None):
    """The schema-one scene document, before the exporter adds ordered body groups."""
    _paths()
    import _rust_part
    _rust_part.start()
    import _machine
    import _routing
    metadata = spec['metadata']
    frames = {name: {'ports': {port: [row['pos'], row['axis'], row['diam']]
                               for port, row in _ports(frame).items()}, 'bb': frame['bb']}
              for name, frame in metadata['frames'].items()}
    result = plain({'schema': 1, 'taken': time.time() if taken is None else taken,
                  'sources': _machine.stamps(), 'solids': metadata.get('solids', ()),
                  'core': metadata.get('core_body_names', ()),
                  'runs': [{key: value for key, value in row.items() if key in _routing.Run.__dataclass_fields__}
                           for row in metadata.get('runs', ())],
                  'frames': frames,
                  'anchors': {name: metadata.get(name, metadata.get('anchors', {}).get(name, ()))
                              for name in ('tube_anchors', 'cap_tube_anchors', 'body_anchors')},
                  'card': checked['scorecard'], 'drain': checked['drain']})
    result['box'] = deepcopy(metadata.get('box'))
    if result['box'] is not None and 'box_fields' in result['box']:
        result['box']['bounds'] = []
    return result


def _tray_reports(bounds, ea):
    import above_core
    groups = defaultdict(list)
    for name in bounds:
        if not name.startswith('valve-v-') or name in set(above_core.valve_names()) | set(ea._cci.cap_cradles) | set(above_core.core_equipment_names()):
            continue
        lower, upper = bounds[name][:3], bounds[name][3:]
        coil = bounds[name.replace('valve-', 'coil-')]
        delta = [(coil[i] + coil[i+3] - lower[i] - upper[i])/2 for i in range(3)]
        axis = max(range(3), key=lambda i: abs(delta[i]))
        sign = 1. if delta[axis] > 0 else -1.
        plane = round((lower if sign > 0 else upper)[axis], 6)
        groups[axis, sign, plane].append((name, [(a+b)/2 for a, b in zip(lower, upper)]))
    x0, x1 = ea._enc.interior_x()
    plans, stations = {}, []
    where = {(0, 1.): 'west', (0, -1.): 'east', (1, 1.): 'fore', (1, -1.): 'aft',
             (2, 1.): 'bottom', (2, -1.): 'top'}
    for (axis, sign, plane), members in sorted(groups.items()):
        across = 0 if axis != 0 else 1
        along = next(i for i in range(3) if i not in (axis, across))
        seats = [(name, center[across], center[along]) for name, center in sorted(members)]
        name = 'valve-tray-' + where[axis, sign]
        if name in plans:
            name += f'-{plane:.0f}'
        middle = (min(v for _n, _u, v in seats) + max(v for _n, _u, v in seats))/2
        plans[name] = [x1-x0, [[round(u-(x0+x1)/2, 6), round(v-middle, 6)] for _n, u, v in seats]]
        stations.append([plane, sign, [[round(u, 6), round(v, 6)] for _n, u, v in seats]])
    pumps = {}
    for name in sorted(bounds):
        if name.startswith('pump-') and name.endswith('-head'):
            head, can = bounds[name], bounds[name.replace('-head', '-motor')]
            delta = [(can[i]+can[i+3]-head[i]-head[i+3])/2 for i in range(3)]
            axis = max(range(3), key=lambda i: abs(delta[i]))
            sign = 1. if delta[axis] > 0 else -1.
            center = [(can[i]+can[i+3])/2 for i in range(3)]
            center[axis] = head[axis+3] if sign > 0 else head[axis]
            if (axis, sign) == (2, 1.):
                center[1] -= ea._enc._tray.rear_axis_y_shift
                center[2] += ea._enc._interface.pump_seated_drop
            pumps[name] = round(round(center[1], 6)-ea._enc.pump_relief_floor, 6)
    return plans, stations, pumps


def gather(spec, checked, physical_model, *, scene_path=None, step_path=None, scorecard_path=None):
    """Schema-two facts from a completed plan, native checks and their written outputs.

    ``piece_bounds`` describes printable source pieces; ``raw_bounds`` describes
    their installed bodies. ``route_lengths`` and ``unsupported_spans`` are the
    native programs' existing developed-length readings, not newly measured CAD.
    """
    _paths()
    import _facts
    import _realized
    import above_core
    import bulkhead_ring
    import jg_bulkhead_union
    ea = scalar_namespace(spec)
    metadata = spec['metadata']
    physical_model = Path(physical_model)
    step_path = Path(step_path) if step_path is not None else Path(str(physical_model).removesuffix('.npz'))
    scene_path = Path(scene_path) if scene_path is not None else step_path.with_suffix('.scene.npz')
    scorecard_path = Path(scorecard_path) if scorecard_path is not None else step_path.with_suffix('.scorecard.json')
    box = plain(metadata['box']['box'] if 'box_fields' in metadata['box'] else metadata['box'])
    pack = {**box.pop('pack'), **plain(metadata.get('pack', {}))}
    box_facts = {name: plain(({**pack, **box})[name]) for name in _facts._BOX_FACT_ORDER}
    bounds = _bounds(spec)
    valves, stations, pumps = _tray_reports(bounds, ea)
    wet = {row['name']: ['round', row['center_x_mm'], row['center_z_mm'], row['bore_diameter_mm']]
           for row in above_core.specification()['rear_wall']['wet_ports']}
    ports = {name: _ports(metadata['frames'][name]) for name in _facts.CARD_PORT_BODIES}
    mouths = {name: rows['inboard' if 'inboard' in rows else 'tube-in']['pos']
              for name, rows in ports.items() if name.startswith('bulkhead-') and name != 'bulkhead-water-nut'}
    pitch = max(jg_bulkhead_union.panel_footprint()[0]+ea.PORT_NUT_GAP+7.5,
                bulkhead_ring.od('union')+2*importlib.import_module('fits').slip+3.)
    west = ea._enc.interior_x()[0]+ea._enc.side_band_inset+1.+jg_bulkhead_union.BODY_D/2
    constants = {'C14_STATION': [above_core.pose('c14-inlet')['translation_mm'][i] for i in (0, 2)],
                 'DIGITEN_COLLET_FREE': ea.DIGITEN_COLLET_FREE,
                 'FLOOR_GROMMET_SQUEEZE': ea.FLOOR_GROMMET_SQUEEZE,
                 'KEYSTONE_CLEARANCES': metadata.get('keystone_clearances', ()),
                 'KEYSTONE_STATION': metadata['keystone_station'],
                 'PANEL_X': {'bulkhead-flavor-b': west, 'bulkhead-flavor-a': west+pitch, 'bulkhead-carb': west+pitch},
                 'CRADLE_TOL': ea.CRADLE_TOL, 'PORT_NUT_GAP': ea.PORT_NUT_GAP, 'WAGO_POLES': ea.WAGO_POLES,
                 **{name: getattr(ea._enc, name) for name in ('appliance_width', 'side_band_inset', 'wall')}}
    constants.update(metadata.get('constants', {}))
    runs, native = _route_rows(metadata)
    pieces = {}
    for name, bound in bounds.items():
        if name in {'enclosure-'+part for part in ('front-bottom', 'front-top', 'back-bottom', 'back-top', 'pump-retainer')}:
            part = name.removeprefix('enclosure-')
            # The printed spring and the installed spring have distinct frames.
            # The source piece is what the existing piece facts describe.
            if part == 'pump-retainer':
                bound = metadata['piece_bounds'][part]
            else:
                bound = metadata.get('piece_bounds', {}).get(part, bound)
            pieces[part] = {'box': [round(v/_GRID)*_GRID for v in bound]}
    carried = {}
    if 'digiten-flow' in metadata['frames']:
        frame = metadata['frames']['digiten-flow']['transform']
        point, direction = ea._digiten.wire_exit()
        carried['digiten-flow.wire_exit'] = {'pos': _point(frame, point),
            'axis': [sum(frame[i][j]*direction[j] for j in range(3)) for i in range(3)]}
    def artifact(path):
        with path.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        return {'path': str(path.relative_to(ROOT)), 'sha256': digest}
    routing = route_metadata(spec, checked)
    standalone = set(metadata.get('standalone_names', (
        'compressor', 'condenser+fan', 'foam-assembly', 'g-ganen-pump', 'funnel',
        'discharge-chain', 'display', 'display-cover', 'display-gasket', 'psu', 'pcba',
        'relay-1', 'relay-2', 'asse1022-assembly', 'bulkhead-drain', 'asse-drain-adapter',
        'mq6-sensor', 'thermal-fuse', 'fuse-clamp', *ea.WAGO_POLES,
        'wago-mana', 'wago-manb', 'wago-reeds-b', 'wago-sensors', 'water-split',
        'flow-regulator', 'vk-solenoid', 'bulkhead-water', 'c14-inlet', 'co2-inlet',
        'gasher-co2', 'wr1110', 'nameplate', 'nameplate-ink', 'bulkhead-flavor-a',
        'bulkhead-flavor-b', 'bulkhead-carb', 'digiten-flow')))
    manifold = metadata.get('fact_manifold_names')
    if manifold is None:
        manifold = [name for name in bounds if name not in standalone and not name.startswith('enclosure-')
                    and not name.startswith('anchor-cap-')
                    and name not in set(metadata.get('routed_body_names',
                        ('tube-'+row['id'] for row in metadata['runs'] if row.get('kind') == 'refrigerant')))]
    cap = _point(metadata['core_carry'], (0., 0., ea._foam.cap_face_z))[2]
    return plain({
        'schema': 2, 'card': _realized.code_digest(scorecard_path), 'step': _realized.code_digest(step_path),
        'sources': _facts.source_digest(), 'box': box_facts, 'constants': constants,
        'hopper_hole': ea._enc._funnel_hole(tuple(pack['funnel'])), 'manifold_bodies': sorted(manifold),
        'valve_trays': valves, 'valve_tray_stations': stations, 'pump_trays': pumps,
        'pack': {'placed': sorted(pack['placed']), 'body_anchors': metadata.get('body_anchors', ()),
                 'tube_anchors': metadata.get('tube_anchors', ())},
        'bodies': bounds, 'mouths': mouths, 'card_ports': ports, 'run_near': {},
        'runs': runs, 'native_runs': native,
        'tube_export': {'schema': 1, 'step': artifact(step_path), 'fine_model': artifact(physical_model),
                        'scene': artifact(scene_path), 'routing': routing},
        'wall_ports': {'union': [wet[name] for name in ('bulkhead-water', 'bulkhead-carb', 'bulkhead-flavor-a', 'bulkhead-flavor-b')],
                       'co2': wet['co2-inlet'], 'drain': wet['bulkhead-drain']},
        'pieces': pieces, 'faces': {'foam-assembly.cap': round(cap, 4)},
        'carried_points': carried, 'gaps': {},
    })


def write(spec, checked, physical_model, **paths):
    """Write the existing fact artifact beside already completed model/card/scene outputs."""
    target = Path(paths.pop('facts_path', LAYOUT / 'enclosure-assembly.facts.json'))
    value = gather(spec, checked, physical_model, **paths)
    from _cadq_export import _atomic_write
    _atomic_write(target, lambda path: Path(path).write_text(json.dumps(value, indent=1, sort_keys=True)+'\n'))
    return target
