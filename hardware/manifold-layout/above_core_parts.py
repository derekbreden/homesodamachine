"""Reference frames, port stations and tube routes in the above-core arrangement.

Purchased references remain exterior layout geometry. The ASSE's straight TPU
cuffs are fit candidates; their displayed installed sections do not establish
sealing, retention or pressure capacity. Tube insertions retain the named
estimates in ``above-core.json``.
"""

from functools import cache
import importlib.util
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parent
ROOT = HW.parent
sys.path.insert(0, str(HW / 'scripts'))

import above_core as layout
from above_core_bom import (stem_elbow_names, core_stem_elbow_names, reservoir_gate_elbow_hosts,
                            union_elbow_names, core_union_elbow_names)

IDENTITY = ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
ORIGIN = (0., 0., 0.)

# Reference paths declare the models alongside the production arrangement data.
REFERENCES = {
    'pcba': HW / 'printed-parts/electronics/pcba-tray/pcba-board.step',
    'psu': HW / 'reference/meanwell-irm90/meanwell-irm90.step',
    'relay-1': HW / 'reference/teyleten-relay/teyleten-relay.step',
    'relay-2': HW / 'reference/teyleten-relay/teyleten-relay.step',
    'c14-inlet': HW / 'reference/iec-c14-inlet/iec-c14-inlet.step',
    'keystone-jack': HW / 'reference/riteav-keystone/riteav-keystone.step',
    'asse1022-assembly': HW / 'reference/multiplex-asse1022/multiplex-asse1022.step',
    'discharge-chain': HW / 'reference/neofit-achv44-check/neofit-achv44-check.step',
    'valve': HW / 'reference/beduan-solenoid/beduan-solenoid.step',
    'water-split': HW / 'reference/branch-stem-tees/neofit-atbu444-e-estimate.step',
    'stem-elbow': HW / 'reference/neofit-stem-elbow/neofit-stem-elbow.step',
    'jg-turn-elbow': HW / 'reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step',
    'flow-regulator': HW / 'reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step',
    'gas-regulator': HW / 'reference/compact-inline-candidates/geometry/candidate-regulator.step',
    'gas-check': HW / 'reference/neofit-achv44-check/neofit-achv44-check.step',
    'digiten-flow': HW / 'reference/digiten-flow-sensor/digiten-flow-sensor.step',
}


@cache
def _module(name, relative):
    spec = importlib.util.spec_from_file_location(name, HW / relative)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def check_reference():
    """One ACHV44-E native frame and insertion estimate for water and CO₂."""
    return _module('above_core_achv44',
                   'reference/neofit-achv44-check/neofit_achv44_check.py')


def tee_reference():
    """The measured PP0208E: Y-A and Y-B take their stems to its tube stop."""
    return _module('above_core_pp0208e', 'reference/tee-connector/tee_connector.py')


def stem_elbow_reference():
    """The scan-fitted ATEU44W: its socket release face and stem shoulder."""
    return _module('above_core_ateu44w', 'reference/neofit-stem-elbow/neofit_stem_elbow.py')


def _frame(rotation=IDENTITY, translation=ORIGIN):
    return {'rotation': rotation, 'translation_mm': translation}


def _compose(outer, inner):
    a, b = outer['rotation'], inner['rotation']
    rotation = tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3))
                           for j in range(3)) for i in range(3))
    return _frame(rotation, layout.point(outer, inner['translation_mm']))


def _snapshot(name, local=None):
    pose = layout.snapshot_pose(name)
    return pose if local is None else _compose(pose, local)


def route_port_frame(name):
    """Reference port frame of a fitting in the short above-core tube routes."""
    if name == 'suction-reducer':
        import rear_plumbing
        data = rear_plumbing.plan()
        return _compose(data['suction-joint'], data['joint']['suction_bend']['end_frame'])
    return _snapshot('reg' if name == 'flow-regulator' else name)


def _grid():
    specification = layout.specification()
    g = specification['fluid_grid']
    rows = []
    for row, names in enumerate(g['assignment']):
        for column, name in enumerate(names):
            gas = name == 'co2-inlet'
            quarter = name in ('bulkhead-water', 'bulkhead-carb') or gas
            rows.append({
                'name': name, 'x': g['columns_x_mm'][column],
                'z': g['rows_z_mm'][row], 'tube_od_mm': 6.35 if quarter else 4.,
                'flange_y': specification['enclosure']['rear_y_mm'],
                'nut_af_mm': 21.0058 if gas else 20. if quarter else 18.,
                'nut_depth_mm': 7.0104 if gas else 4. if quarter else 6.5,
                'barrel_d_mm': 17. if gas else 17.14 if quarter else 15.,
                'native_kind': 'gas' if gas else 'quarter' if quarter else 'four',
            })
    return rows


def _grid_module(row):
    kind = row['native_kind']
    if kind == 'gas':
        return _module('above_core_co2_bulkhead', 'reference/neofit-bulkhead/neofit_bulkhead.py')
    if kind == 'quarter':
        return _module('above_core_water_bulkhead', 'reference/jg-bulkhead-union/jg_bulkhead_union.py')
    return _module('above_core_four_bulkhead', 'reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py')


def core_components():
    """Additional removable core-owned routing bodies."""
    return {}


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


def port_stations(name):
    """Selected reference's native ``port -> (position, axis, diameter)``.

    The ASSE aliases describe its metal connections. The threaded adapters,
    union tee and stem checks expose their own native interfaces separately.
    """
    import rear_plumbing
    rear = rear_plumbing.ports(name)
    if rear is not None:
        return rear
    if name in stem_elbow_names():
        return {'socket': (*stem_elbow_reference().socket(), 6.35)}
    if name in reservoir_gate_elbow_hosts():
        return {'socket': (*stem_elbow_reference().socket(), 6.35)}
    if name in ('valve-v-a', 'valve-v-b', 'vk-solenoid'):
        return {'inlet': ((0., -29.75, 11.05), (0., -1., 0.), 6.35),
                'outlet': ((0., 29.75, 11.05), (0., 1., 0.), 6.35)}
    if name == 'asse1022-assembly':
        return {'tube-in': (*rear_plumbing.chain().bfp.inlet(), 17.15),
                'tube-out': (*rear_plumbing.chain().bfp.outlet(), 15.88),
                'vent-tip': (*rear_plumbing.chain().bfp.vent(), 7.7)}
    if name == 'water-split':
        return {'supply': ((0., 6.0452, 0.), (0., 1., 0.), 6.35),
                'stem-tip': ((0., 21.0452, 0.), (0., 1., 0.), 6.35),
                'to-vk': ((20.1041, 0., 0.), (1., 0., 0.), 6.35),
                'to-flavor': ((-20.1041, 0., 0.), (-1., 0., 0.), 6.35)}
    if name == 'flow-regulator':
        return {'inlet': (ORIGIN, (-1., 0., 0.), 6.35),
                'outlet': ((68.117, 0., 0.), (1., 0., 0.), 6.35)}
    if name == 'gas-regulator':
        return {'inlet': (ORIGIN, (0., 0., -1.), 6.35),
                'outlet': ((0., 0., 62.4), (0., 0., 1.), 6.35)}
    if name in ('gas-check', 'discharge-chain'):
        ports = {key: (row['position'], row['outward'], row['tube_od_mm'])
                 for key, row in check_reference().ports().items()}
        if name == 'discharge-chain':
            ports['tube-port'] = ports['outlet']
        return ports
    if name.startswith('asse-') and name.endswith('-tpu'):
        inlet = name == 'asse-inlet-tpu'
        return {'tube': (((-20. if inlet else 85.), 0., 0.),
                         ((-1. if inlet else 1.), 0., 0.), 6.35)}
    if name == 'asse-drain-adapter':
        adapter = _module('above_core_vent_adapter', 'printed-parts/asse-drain-adapter/asse_drain_adapter.py')
        return {'tube': (adapter.tube_mouth(rear_plumbing.chain().bfp.vent()[0]), (-1., 0., 0.), 4.)}
    return None


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


def route_specs():
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

    result.update(__import__('rear_plumbing').route_specs())
    return result


