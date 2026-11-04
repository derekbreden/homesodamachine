"""Reference frames, port stations and tube routes in the above-core arrangement.

Purchased references remain exterior layout geometry. The ASSE's straight TPU
cuffs are fit candidates; their displayed installed sections do not establish
sealing, retention or pressure capacity. Tube insertions retain the named
estimates in ``above-core.json``.
"""

from functools import cache
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parent
ROOT = HW.parent
sys.path.insert(0, str(HW / 'scripts'))

import above_core as layout
from _layout_data import data as _data
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
    'discharge-chain': HW / 'reference/neofit-acvus44-check/neofit-acvus44-check.step',
    'valve': HW / 'reference/beduan-solenoid/beduan-solenoid.step',
    'water-split': HW / 'reference/branch-stem-tees/neofit-atbu444-e-estimate.step',
    'stem-elbow': HW / 'reference/neofit-stem-elbow/neofit-stem-elbow.step',
    'jg-turn-elbow': HW / 'reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step',
    'flow-regulator': HW / 'reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step',
    'gas-regulator': HW / 'reference/compact-inline-candidates/geometry/candidate-regulator.step',
    'gas-check': HW / 'reference/neofit-acvus44-check/neofit-acvus44-check.step',
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
    result = _data('compose', outer=outer, inner=inner)
    return _frame(tuple(tuple(row) for row in result['rotation']), tuple(result['translation_mm']))


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
    return _data('grid', spec=layout.specification())


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
    return _data('offset', point=point, vector=vector, length=length)


def _link(a, axis_a, depth_a, b, axis_b, depth_b):
    return _data('link', a=a, axis_a=axis_a, depth_a=depth_a, b=b, axis_b=axis_b, depth_b=depth_b)


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
    return _data('line', a=a, b=b)


def _bezier(control):
    return _data('bezier', control=control)


def _crowned_beziers(control, crown, intervals=16):
    return _data('crowned-beziers', control=control, crown=crown, intervals=intervals)


def _sample_bezier(control, samples=65):
    return _data('sample-bezier', control=control, samples=samples)


def route_specs():
    """Rust native tube recipes, with the rear reference ports supplied by their provider."""
    import rear_plumbing
    rear = rear_plumbing.route_specs()
    spec = layout.specification()
    return dict(_data('fore-routes', spec=spec, rear=rear,
                      order=list(spec['fore_routes']['tubes']), rear_order=list(rear)))


