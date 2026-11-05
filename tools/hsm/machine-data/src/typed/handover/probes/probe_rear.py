"""Call every rear_snaps / rear_plumbing function with fixed inputs and print a digest of each
result (or its error) as JSON. Run under the step harness from a staged work-dir clone:

    python harness.py <bindir> <machine-data> probe_rear.py <out.json>
"""
import hashlib, io, json, os, sys, types, traceback

work = os.getcwd()
for sub in ('hardware/reference/multiplex-asse1022', 'hardware/printed-parts/cadlib',
            'hardware/manifold-layout', 'hardware/scripts'):
    sys.path.insert(0, os.path.join(work, sub))

import numpy as np
import cadquery as cq
import rear_snaps as rs
import rear_plumbing as rp


def digest(v):
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, int):
        return {'int': v}
    if isinstance(v, float):
        return {'float': repr(v)}
    if isinstance(v, np.ndarray):
        return {'ndarray': str(v.dtype), 'shape': list(v.shape),
                'sha': hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()}
    if isinstance(v, np.generic):
        return {'np': type(v).__name__, 'v': repr(v.item())}
    if isinstance(v, tuple):
        return {'tuple': [digest(x) for x in v]}
    if isinstance(v, list):
        return {'list': [digest(x) for x in v]}
    if isinstance(v, dict):
        return {'dict': [[digest(k), digest(x)] for k, x in v.items()]}
    if isinstance(v, cq.Shape):
        b = io.BytesIO()
        v.exportBrep(b)
        return {'shape': type(v).__name__, 'brep': hashlib.sha256(b.getvalue()).hexdigest(),
                'volume': repr(v.Volume())}
    if isinstance(v, types.ModuleType):
        return {'module': v.__name__}
    return {'other': type(v).__name__, 'repr': repr(v)[:200]}


out = {}


def probe(name, thunk):
    try:
        out[name] = digest(thunk())
    except Exception as e:  # noqa: BLE001
        out[name] = {'error': type(e).__name__, 'message': str(e).replace(work, '<WORK>')[:600]}


def fake_station(name, port):
    return ((float(len(name)), float(len(port)), 0.5), (0., 0., 1.), 6.35)


names = ['SLIDE', 'THREAD', 'WALL', 'SPLIT', 'INTO', 'WING', 'REACH', 'SIDE', 'FREE_LENGTH',
         'ROOT_RADIUS', 'REAR_ROOT_DROP', 'ASSE_HEX_SEATING_DEPTH', 'ASSE_BODY_SEATING_DEPTH',
         'PISCO_RADIAL_RELIEF', 'PISCO_CAP_AIR', 'PISCO_CAP_FIT', 'PISCO_BEARING_LENGTH',
         'METER_AIR', 'METER_BACK', 'METER_CAP_AIR', 'METER_HOUSING_FIT', 'METER_BEARING_DEPTH',
         'LEDGE', 'NOSE_LAND', 'TIP_RISE', 'TOOL_SLOT_WIDTH', 'TOOL_SLOT_HEIGHT',
         'TOOL_APPROACH_DEGREES', 'HOOK', 'CATCH', 'VAR', 'METER_COLLAR_AXIAL_AIR', 'CHAIN',
         'SOLIDS', 'SEATS', 'CAPS', 'ON']
probe('constants', lambda: [getattr(rs, n) for n in names])

st = rs.station(100., 7.2, 400., 430.)
probe('station', lambda: st)
probe('station-kw', lambda: rs.station(100., 7.2, 400., 430., 340., wing_root=320., free_length=20.,
                                       tool_angle_degrees=-65., tool_end_stock=10.))
probe('station-int', lambda: rs.station(100, 7, 400, 430, 335))
probe('station-split-kw', lambda: rs.station(0., 9.5, 397., 435., split=0., wing_root=-12.))
probe('half_width', lambda: [rs.half_width(9., 337., 330.), rs.half_width(3, 5, 1),
                             rs.half_width(1., 5., 0.), rs.half_width(10, 3, 0)])
probe('receiver_tool_ports', lambda: rs.receiver_tool_ports(st))
sp = rs.pisco_station(150., 9.3, 330., 400., 430.)
probe('pisco_station', lambda: sp)
probe('pisco_cap_span', lambda: [rs.pisco_cap_span(420., 12., 465.3), rs.pisco_cap_span(420, 12, 465)])
no_root = {k: v for k, v in st.items() if k not in ('root', 'root_radius')}
sections = {
    'bottom': lambda: rs.cap_section(st, 330., 300.),
    'hexed': lambda: rs.cap_section(st, 330., None, 330., hexed=True),
    'tangent': lambda: rs.cap_section(st, 330., 310., 330.),
    'tangent-low-base': lambda: rs.cap_section(st, 300., 310., 330.),
    'no-root': lambda: rs.cap_section(no_root, 330., 300.),
    'no-root-axis': lambda: rs.cap_section(no_root, 330., 310., 325.),
    'pisco': lambda: rs.cap_section(sp, sp['root'], 315.),
}
for key, thunk in sections.items():
    probe('cap_section-' + key, thunk)
    probe('section_solid-' + key, lambda thunk=thunk: rs.section_solid(thunk()))
probe('cap-bottom', lambda: rs.cap(st, 330., 300.))
probe('cap-hexed', lambda: rs.cap(st, 330., None, 330., True))
probe('cap-tangent', lambda: rs.cap(st, 330., 310., axis_z=330.))
probe('pockets', lambda: rs.pockets(st))
probe('pockets-pisco', lambda: rs.pockets(sp))
probe('pockets-plain', lambda: rs.pockets(json.loads(json.dumps(dict(st, tool_inner_slope=2., axis_x=0)))))
probe('pisco_cap_service_cuts', lambda: rs.pisco_cap_service_cuts(sp))
probe('asse_service_corner', lambda: rs.asse_service_corner(st))
runs = [(400., 410., 5.), (410., 418.5, 6.), (418.5, 425., 6.5)]
profile = [[0., 3.], [5., 6.5], [8., 7.], [12., 5.]]
probe('pisco_bearing_profile', lambda: rs.pisco_bearing_profile(runs, profile, 420.))
probe('pisco_bearing_profile-np', lambda: rs.pisco_bearing_profile(runs, np.array(profile), 420.))
probe('pisco_grip_stock', lambda: rs.pisco_grip_stock(sp, 330., 8., 6., 415.))
wrenches = [([400., 410.], 10., 90.3, 12.), ([420., 430.], 12., 90.9, 13.)]
probe('asse_cap_profile', lambda: rs.asse_cap_profile(wrenches, 0.15))
probe('meter_cap_corner_room', lambda: rs.meter_cap_corner_room(10., 300., (397., 435.)))
probe('box', lambda: [rs.box(0, 1, 0, 2, 0, 3), rs.box(0., 1.5, -1., 2., 0., 3.)])
probe('prism_x', lambda: rs.prism_x(0., 5., [(0., 0.), (1., 0.), (1., 1.)]))
probe('stadium_x', lambda: rs.stadium_x(400., 300., 5., 3., 2., 10., 20.))
probe('radial_profile', lambda: rs.radial_profile([(0., 3.), (5., 4.), (10., 2.)]))
probe('stadium_profile_x', lambda: rs.stadium_profile_x([(0., 3.), (5., 4.), (5., 4.5), (10., 2.), (14., 2.)],
                                                        (400., 300.), 3., 2.))
probe('stadium_profile_x-flat', lambda: rs.stadium_profile_x([(0., 3.), (5., 4.)], (400., 300.), 0., 0.))
frame = rp.plan()['chain_frame']
points = [(0., 3.), (5., 4.), (10., 2.)]
probe('radial_room', lambda: rs.radial_room({'points': points, 'frame': frame}))
probe('radial_room-wrench', lambda: rs.radial_room({'points': points, 'frame': frame,
                                                    'wrench': {'apothem': 3.5, 'clock': 10.}}))
probe('radial_room-outline', lambda: rs.radial_room({'points': points, 'frame': frame, 'wrench': {
    'apothem': 3.5, 'clock': 10., 'outline': [(-5., -5.), (5., -5.), (5., 5.), (-5., 5.)],
    'relief_span': (1., 4.), 'relief_corner': 4.5}}))
probe('turned', lambda: rs.turned([(400., 410., 5.), (410., 420., 6.), (420., 425., 6.)], (100., 300.)))
probe('hex_prism', lambda: rs.hex_prism((100., 300.), 8., 0.3, 400., 420., 9.))
probe('at_world', lambda: rs.at_world(cq.Location(cq.Vector(1, 2, 3)), (1., 2., 3.)))
probe('surface_points', lambda: rs.surface_points(cq.Solid.makeBox(2, 2, 2)))
probe('surface_points-step', lambda: rs.surface_points(cq.Solid.makeBox(2, 2, 2), 0.5))
probe('envelope-one', lambda: rs.envelope(np.array([[0., 401., 0.]]), (0., 0.), 370., 482.))
probe('envelope-many', lambda: rs.envelope(np.array([[0., 401., 0.], [1., 402., 1.]]), (0., 0.), 370., 482.))
probe('swept', lambda: rs.swept(np.array([0., 1., 2., 0.5, 0., 3.]), 0.2, 0.3))
probe('swept-step', lambda: rs.swept(np.array([0., 1., 2., 0.5, 0., 3.]), 1, 2, 0.5))
ys = np.arange(370., 380., 0.1)
rr = np.where((ys > 371.) & (ys < 378.), 5. + 0.3 * np.floor((ys - 371.) / 0.7), 0.)
probe('steps', lambda: rs.steps(ys, rr))
probe('steps-tol', lambda: rs.steps(ys, rr, 0.5, 0.1, 3.))
probe('steps-list', lambda: rs.steps(ys.tolist(), rr.tolist()))
probe('steps-merge', lambda: rs.steps([0., 1., 2., 3., 4., 5.], [1., 1., 2., 2., 1., 1.], 0.2, 1., 2.5))
parts = {n: (cq.Solid.makeBox(1, 1, 1),) for n in (*rs.CHAIN, 'co2-check', 'pisco-x')}
probe('build', lambda: rs.build(parts, (100., 300.), cq.Location(), 90., (150., 330.), 420., 360.,
                                465.3, 98.5, None, cq.Location()))

probe('plan', lambda: rp.plan())
probe('snap_datums', lambda: rp.snap_datums())
probe('meter_spans', lambda: rp.meter_spans())
probe('reference', lambda: rp.reference('pp1208e', 'reference/jg-bulkhead-union/jg_bulkhead_union.py').TUBE_STOP_DEPTH)
probe('modules', lambda: [rp.chain().bfp.BODY_CENTER_Z, rp.union_tee().INSERTION, rp.check().INSERTION,
                          rp.joint().CUT_X, rp.joint().reducer.LENGTH])
for name in ('bulkhead-water', 'gas-regulator', 'co2-inlet', 'gas-check', 'discharge-chain', 'water-split',
             'suction-reducer', 'discharge-reducer', 'jg-pp061208w', 'unknown', 5):
    probe(f'ports-{name}', lambda name=name: rp.ports(name))
probe('_arc_three', lambda: rp._arc_three([(0., 0., 0.), (1., 1., 0.), (2., 0., 0.)]))
probe('_route_stations', lambda: rp._route_stations('rear-route-specs', fake_station))
probe('route_specs', lambda: rp.route_specs())
probe('continuations', lambda: rp.continuations(fake_station))
probe('flavor_routes', lambda: rp.flavor_routes(fake_station))
probe('_flavor_s_bend', lambda: rp._flavor_s_bend((0., 0., 0.), (1., 0., 0.), 10., (0., 0., 1.)))
probe('_flavor_rear', lambda: rp._flavor_rear('a', (0., 0., 0.)))
probe('regulator_datums', lambda: rp.regulator_datums())
probe('pockets-regulator', lambda: rs.pockets(rp.regulator_datums()['station']))
probe('clearance_profile', lambda: rs.clearance_profile([(0., 3.), (5., 4.), (10., 2.)], 0.15, 0.15))

with open(sys.argv[1], 'w') as f:
    json.dump(out, f, indent=1, sort_keys=True)
print(len(out), 'probes')
