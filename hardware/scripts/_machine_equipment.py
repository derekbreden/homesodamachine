"""Compatibility interfaces for Rust's equipment dimensions, placements and tube recipes.

Python resolves the existing scalar providers and model files for callers that still
import this module. Rust computes the construction recipe and installed port frames.
"""
from __future__ import annotations

from functools import cache
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / 'hardware'
LAYOUT = HW / 'manifold-layout'
if str(LAYOUT) not in sys.path:
    sys.path.insert(0, str(LAYOUT))
import above_core as layout
from above_core_bom import stem_elbow_names, union_elbow_names, reservoir_gate_elbow_hosts

IDENTITY = {'rotation': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
            'translation_mm': [0., 0., 0.]}


def _request(op, **values):
    from _rust_data import request
    return request('machine-data', 'machine-data', {'op': op, **values})


def _read(relative):
    from _cadq_export import note_read
    path = HW / relative
    note_read(path)
    return _request('read_json', path=str(path))


def frame(rotation=None, translation=None):
    return {'rotation': rotation or IDENTITY['rotation'],
            'translation_mm': translation or IDENTITY['translation_mm']}


def compose(a, b):
    return _request('equipment_compose', a=a, b=b)


def transform(pose):
    return _request('equipment_transform', pose=pose)


def _along_y(point, axis):
    return _request('equipment_along_y', point=point, axis=axis)


def plan():
    return layout.specification()['rear_plumbing']


def _source(relative, input_root=None):
    from _cadq_export import note_read
    manifest = (HW / relative).parent / 'frozen-asset.json'
    if manifest.is_file():
        note_read(manifest)
    return _request('model_source', mode='equipment', relative=relative,
                    authored_root=str(HW),
                    input_root=str(Path(input_root).resolve() / 'hardware' if input_root else HW))


@cache
def _stem():
    return _read('reference/neofit-stem-elbow/reference-parameters.json')


@cache
def _reducer():
    return _read('reference/jg-pp061208w/reference-parameters.json')


@cache
def _check():
    return _read('reference/neofit-acvus44-check/reference-parameters.json')


def _bfp_port(name):
    sys.path.insert(0, str(HW / 'reference/multiplex-asse1022'))
    import multiplex_asse1022
    return getattr(multiplex_asse1022, name)()


def _chain_parts():
    return _read('reference/asse1022-threaded-chain/reference-parameters.json')['components']


def _inputs():
    return {'stem': _stem(), 'reducer': _reducer(), 'check': _check(),
            'chain': _read('reference/asse1022-threaded-chain/reference-parameters.json'),
            'pump': _read('reference/g-ganen-pump/reference-parameters.json'),
            'jg': _read('reference/jg-bulkhead-union/reference-parameters.json'),
            'drain': _read('reference/neofit-drain-bulkhead/reference-parameters.json'),
            'multiplex_ports': {name: _bfp_port(name) for name in ('inlet', 'outlet', 'vent')}}


def _context(op, **values):
    spec = layout.specification()
    return _request(op, spec=spec, data=_inputs(),
                    fore_tube_order=list(spec['fore_routes']['tubes']), **values)


def _chain_inlet():
    point, axis = _context('equipment_chain_inlet')
    return tuple(point), tuple(axis)


def local_ports(name):
    result = _context('equipment_ports', name=name)
    return {port: (tuple(result['ports'][port][0]), tuple(result['ports'][port][1]), result['ports'][port][2])
            for port in result['order']}


def _grid():
    yield from _request('equipment_grid', spec=layout.specification())


def _joint_numbers(port):
    return _context('equipment_joint', port=port)


def _palette():
    import _materials as m
    return {key: list(m.linear(getattr(m, key))) for key in (
        'C_PCBA', 'C_PSU', 'C_RELAY', 'C_C14', 'M_BRASS', 'C_DIGITEN', 'C_VALVE',
        'M_DONOR_BLACK', 'M_PETGF_BLACK', 'M_TPU_BLACK', 'M_JG_BLACK_PP',
        'M_NEOFIT_WHITE_ACETAL', 'M_NEOFIT_ACETAL', 'M_JG_WHITE_PP',
        'M_STAINLESS', 'M_POM_ORANGE', 'M_PVC_CLEAR', 'M_NITRILE_BLACK')}


def numbers(external_ports=None, extra_routes=(), *, input_root=None):
    import soda_inlet
    import _materials
    import _routing
    from _assembly_model import document
    sources = {}
    for relative in _request('equipment_sources'):
        path = _source(relative, input_root)
        sources[relative] = {'path': path}
        if path.endswith('.npz'):
            sources[relative]['presentation'] = bool(document(path).get('presentation')
                                                      or Path(path[:-4] + '.mesh').is_file())
    colors = _palette()
    colors['M_JG_GREY_ACETAL'] = list(_materials.linear(_materials.M_JG_GREY_ACETAL))
    inputs_hw = Path(input_root).resolve() / 'hardware' if input_root else HW
    from _cadq_export import note_read
    pump_path = inputs_hw / 'printed-parts/cold-core/foam-cap/foam-cap.numbers.json'
    note_read(pump_path)
    value = _context('equipment_numbers', external_ports=external_ports, sources=sources,
        colors=colors, pump_cap=_request('read_json', path=str(pump_path))['pump'],
        insulation_plan=soda_inlet.plan(), soft_neighbors=list(soda_inlet.SOFT_NEIGHBORS))
    routes = {}
    if external_ports is not None:
        import above_core_routes
        routes = above_core_routes.route_specifications(
            lambda name, port: value['world_ports'][name][port], plumbing=sys.modules[__name__])
    result = _request('equipment_finalize', equipment=value, integrated_routes=routes,
        integrated_order=list(routes), extra_routes=list(extra_routes),
        spool_colors={key: list(_materials.linear(_routing.color(key))) for key in _routing.SPOOLS})
    result['routes'] = {name: result['routes'][name] for name in result['route_order']}
    result['native_route_specs'] = {name: result['native_route_specs'][name]
                                    for name in result['native_route_order']}
    port_order = result.pop('_frame_port_order')
    result['frames'] = {name: result['frames'][name] for name in result['component_order']}
    for name, row in result['frames'].items():
        row['ports'] = {port: row['ports'][port] for port in port_order[name]}
    world_order = dict.fromkeys([*(external_ports or {}), *result['component_order']])
    result['world_ports'] = {name: result['world_ports'][name] for name in world_order}
    for name, ports in result['world_ports'].items():
        order = port_order.get(name, (external_ports or {}).get(name, {}))
        result['world_ports'][name] = {port: ports[port] for port in order}
    result['native_connections'] = {name: result['native_connections'][name]
                                     for name in layout.logical_connections()}
    result['colors'] = {name: result['colors'][name] for name in colors}
    # This existing registry lets downstream tube renderers resolve the same spool.
    for name, route in result['routes'].items():
        if 'spool' in route:
            _routing.SPOOL_OF[name] = route['spool']
    return result


def build(output, *, external_ports=None, extra_routes=(), input_root=None):
    import _rust_part
    _rust_part.start()
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('machine', 'machine-equipment',
                   numbers(external_ports, extra_routes, input_root=input_root), output)
    result = _request('read_json', path=str(output / 'machine-equipment.json'))
    model = str(output / 'machine-equipment.step.npz')
    for instance in result['instances']:
        instance['model'] = model
    result['model'] = model
    return result


def _reducer_insertion():
    return _context('equipment_reducer_insertion')


def route_port_frame(name):
    return _request('equipment_route_frame', spec=layout.specification(), name=name)


def _offset(point, vector, length=1.):
    from _layout_data import data
    return data('offset', point=point, vector=vector, length=length)


def _link(a, axis_a, depth_a, b, axis_b, depth_b):
    from _layout_data import data
    return data('link', a=a, axis_a=axis_a, depth_a=depth_a, b=b, axis_b=axis_b, depth_b=depth_b)


def _line(a, b):
    from _layout_data import data
    return data('line', a=a, b=b)


def _bezier(control):
    from _layout_data import data
    return data('bezier', control=control)


def _crowned_beziers(control, crown, intervals=16):
    from _layout_data import data
    return data('crowned-beziers', control=control, crown=crown, intervals=intervals)


def _sample_bezier(control, samples=65):
    from _layout_data import data
    return data('sample-bezier', control=control, samples=samples)


def local_routes():
    result = _context('equipment_local_routes')
    return {name: result['routes'][name] for name in result['order']}


def _arc_three(points):
    from _layout_data import data
    return data('arc-three', points=points)


def _rear_routes():
    return dict(_context('equipment_rear_routes'))


def continuations(station):
    names = [('digiten-flow', 'outlet'), ('bulkhead-carb', 'tube-in'), ('gas-check', 'outlet'),
             ('asse-drain-adapter', 'tube'), ('bulkhead-drain', 'inboard')]
    return dict(_context('equipment_continuations',
                        stations={name+'.'+port: station(name, port) for name, port in names}))


def _flavor_s_bend(start, heading, offset, axis):
    from _layout_data import data
    segments, end = data('flavor-s-bend', start=start, heading=heading, offset=offset, axis=axis)
    return segments, tuple(end)


def _flavor_rear(flavor, destination):
    from _layout_data import data
    return data('flavor-rear', flavor=flavor, destination=destination)


def flavor_routes(station):
    names = [('valve-v-g', 'outlet'), ('valve-v-j', 'outlet'),
             ('bulkhead-flavor-a', 'tube-in'), ('bulkhead-flavor-b', 'tube-in')]
    return dict(_request('equipment_flavor_routes',
                        stations={name+'.'+port: station(name, port) for name, port in names}))
