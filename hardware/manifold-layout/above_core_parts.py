"""Native components and tube routes in the above-core arrangement.

Purchased references remain exterior layout geometry. The ASSE's straight TPU
cuffs are fit candidates; their displayed installed sections do not establish
sealing, retention or pressure capacity. Tube insertions retain the named
estimates in ``above-core.json``. All shapes are native CAD; the exploratory
mesh libraries and study inheritance chain are not runtime inputs.
"""

from functools import cache
import importlib.util
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parent
ROOT = HW.parent
sys.path.insert(0, str(HW / 'scripts'))

import above_core as layout
from above_core_bom import (stem_elbow_names, core_stem_elbow_names, reservoir_gate_elbow_hosts,
                            union_elbow_names, core_union_elbow_names)
from _cadq_export import import_step
from _materials import (C_C14, C_DIGITEN, C_PCBA, C_PSU, C_RELAY, C_VALVE,
                        M_BRASS, M_DONOR_BLACK, M_JG_BLACK_PP,
                        M_JG_WHITE_PP, M_NEOFIT_ACETAL, M_NEOFIT_WHITE_ACETAL, M_STAINLESS,
                        M_TPU_BLACK, M_NITRILE_BLACK, M_PETGF_BLACK)

IDENTITY = ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
ORIGIN = (0., 0., 0.)

# Native sources are spelled out so the build dependency scanner sees each
# reference as well as the production arrangement data.
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
def native_reference(name):
    return import_step(REFERENCES[name]).val()


@cache
def valve_native(name):
    """One purchased reference, with its movable release collets clocked.

    Clock angles are about native +Y through the port centre. The inlet and
    outlet collet solids occupy the observed end-mouth bands; every other
    reference solid keeps its exact native shape and frame.
    """
    native = native_reference('valve')
    angles = layout.pose(name).get('collet_clock_degrees', {})
    if not angles:
        return native
    ref = _module('above_core_beduan',
                  'reference/beduan-solenoid/beduan_solenoid.py')
    mouth_start = ref.port_length/2. - ref.port_mouth_depth
    solids = []
    for solid in native.Solids():
        box = solid.BoundingBox()
        port = ('inlet' if box.ymax < -mouth_start else
                'outlet' if box.ymin > mouth_start else None)
        angle = angles.get(port, 0.)
        if angle:
            solid = solid.rotate((0., 0., ref.port_center_z),
                                 (0., 1., ref.port_center_z), angle)
        solids.append(solid)
    return cq.Compound.makeCompound(solids)


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


def _frame(rotation=IDENTITY, translation=ORIGIN):
    return {'rotation': rotation, 'translation_mm': translation}


def _compose(outer, inner):
    a, b = outer['rotation'], inner['rotation']
    rotation = tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3))
                           for j in range(3)) for i in range(3))
    return _frame(rotation, layout.point(outer, inner['translation_mm']))


def _carry(frame):
    def carried(station):
        xyz, axis = station
        return layout.point(frame, xyz), layout.vector(frame['rotation'], axis)
    carried.where = layout.frame_location(frame)
    return carried


def _snapshot(name, local=None):
    pose = layout.snapshot_pose(name)
    return pose if local is None else _compose(pose, local)


def _placed(shape, frame):
    carry = _carry(frame)
    return shape.moved(carry.where), carry


def _compound(shapes):
    return cq.Compound.makeCompound(list(shapes))


@cache
def pump_native():
    """Corrected rigid reference plus four identical installed rubber feet."""
    pump = _module('above_core_pump', 'reference/g-ganen-pump/g_ganen_pump.py')
    foot = _module('above_core_foot', 'reference/g-ganen-pump/common-foot/g_ganen_foot.py')
    parts = [part for name, part in pump.build_parts().items()
             if 'rubber_slider' not in name]
    parts.extend(foot.placed_foot(x, side, 38.5)
                 for x in (9.5, 67.5) for side in (-1, 1))
    return _compound(parts)


def _asse_cuff(outlet=False):
    cuffs = _module('above_core_asse_cuffs', 'printed-parts/asse-straight-cuffs/asse_straight_cuffs.py')
    return cuffs.assembly_shape('outlet' if outlet else 'inlet')


@cache
def stem_elbow(depth=12.7):
    """Stock NeoFit elbow, cut to the receiving socket's specified depth."""
    shoulder = -6.0452
    tip = shoulder - float(depth)
    # Only the straight male stem is cut. The body, collet and shoulder are
    # the same native reference for every receiving family.
    trim = cq.Solid.makeBox(100. + tip, 100., 100., cq.Vector(-100., -50., -50.))
    return native_reference('stem-elbow').cut(trim)


@cache
def branch_tee():
    tee = _module('above_core_branch_tee', 'reference/branch-stem-tees/branch_stem_tees.py')
    shoulder = tee.specification('neofit')['model_mm']['stem_shoulder_y']
    end = shoulder + 15.
    trim = cq.Solid.makeBox(100., 100., 100., cq.Vector(-50., end, -50.))
    return native_reference('water-split').cut(trim)


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


def _nut(row):
    plane = cq.Plane(origin=(row['x'], row['flange_y'] - 6., row['z']),
                     xDir=(1, 0, 0), normal=(0, -1, 0))
    shape = (cq.Workplane(plane).polygon(6, row['nut_af_mm'] / math.cos(math.pi / 6))
             .circle(row['barrel_d_mm'] / 2).extrude(row['nut_depth_mm']).val())
    # Selected bare-nut clocking: flats on +/-X and corners above/below.
    return shape.rotate((row['x'], 0., row['z']), (row['x'], 1., row['z']), 30.)


@cache
def pp1208e_bulkhead():
    """Selected PP1208E with a pass-through inboard installation envelope.

    John Guest's PP4608_01/23 drawing specifies a 17.0 mm mounting hole
    (N), an outside fixed flange and a smaller inboard end. The inboard
    envelope here is bounded by the reference's conservative 17.14 mm
    nominal thread diameter. Its larger outside flange is retained.

    The drawing dimensions include released collets. Operating collet
    extension and the inboard body's detailed profile are unmeasured;
    both selected nominal port planes remain those of the reference.
    This exterior envelope does not specify seals or thread engagement.

    https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf
    """
    source = _module('above_core_water_bulkhead',
                     'reference/jg-bulkhead-union/jg_bulkhead_union.py')
    passage = cq.Solid.makeCylinder(source.THREAD_D/2., -source.far_ring_face_y,
                                   cq.Vector(0.,0.,0.), cq.Vector(0.,-1.,0.))
    far = source.build_far_end().val().intersect(passage)
    return source.build_near_end().union(source.build_threading()).union(far).val()


@cache
def abu44m_bulkhead():
    """Selected ABU44M-E with its M15 inboard pass-through envelope.

    The manufacturer's drawing places the inboard body and collet inside
    the M15 x 1.5 barrel's diameter beyond the removable H2 nut. A 15.0 mm
    envelope bounds that undimensioned profile. The conservative outside
    flange and both selected nominal mouth planes remain unchanged.
    B1/B2 are tube stop depths; operating collet details are unmeasured.

    https://assets.freshwatersystems.com/image/upload/qnbgcy8djx3nj2weqz9v.pdf
    """
    source = _module('above_core_four_bulkhead',
                     'reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py')
    # The outside flange keeps the complete source envelope. The inboard
    # barrel and collet must pass through the panel's M15 clearance hole.
    lo = source.far_ring_face_y
    outside = cq.Solid.makeBox(2.*source.FLANGE_D, source.near_ring_face_y,
                               2.*source.FLANGE_D,
                               cq.Vector(-source.FLANGE_D,0.,-source.FLANGE_D))
    inboard = cq.Solid.makeCylinder(source.THREAD_D/2., -lo,
                                    cq.Vector(0.,lo,0.), cq.Vector(0.,1.,0.))
    return source.build().intersect(outside.fuse(inboard))


def core_components():
    """The removable fore tube cap carried by the cold-core lid."""
    snap = _module('above_core_reservoir_a_snap',
                   'printed-parts/cold-core/_reservoir_a_snap.py')
    solid, carry = _placed(snap.installed_cap(),
                           {'rotation': IDENTITY, 'translation_mm': ORIGIN})
    return {'reservoir-a-fore-snap-cap': (solid, M_PETGF_BLACK, carry)}


@cache
def components():
    """Return ``name -> (placed native shape, material color, port carry)``."""
    result = {}

    def add(name, shape, color, frame):
        solid, carry = _placed(shape, frame)
        result[name] = solid, color, carry

    for name, color in (('pcba', C_PCBA), ('psu', C_PSU),
                        ('relay-1', C_RELAY), ('relay-2', C_RELAY),
                        ('c14-inlet', C_C14), ('asse1022-assembly', M_BRASS),
                        ('discharge-chain', M_NEOFIT_ACETAL),
                        ('digiten-flow', C_DIGITEN)):
        add(name, native_reference(name), color, layout.pose(name))
    for name in layout.valve_names():
        add(name, valve_native(name), C_VALVE, layout.pose(name))
    add('g-ganen-pump', pump_native(), M_DONOR_BLACK, layout.pose('g-ganen-pump'))

    # Cuffs share the ASSE flow-axis frame, with X=0 at the bare inlet tip.
    cuff_frame = _compose(layout.pose('asse1022-assembly'),
                          _frame(translation=(0., 0., 27.)))
    for side in ('inlet', 'outlet'):
        add('asse-' + side + '-tpu', _asse_cuff(side == 'outlet'), M_TPU_BLACK, cuff_frame)
    adapter = _module('above_core_vent_adapter', 'printed-parts/asse-drain-adapter/asse_drain_adapter.py')
    add('asse-drain-adapter', adapter.placed((32., 0., 0.)), M_TPU_BLACK,
        layout.pose('asse1022-assembly'))

    sleeve = _module('above_core_pump_sleeve', 'printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py')
    inlet_base = _frame(((-1., 0., 0.), (0., 0., 1.), (0., 1., 0.)))
    outlet_base = _frame(((1., 0., 0.), (0., -1., 0.), (0., 0., -1.)),
                         (74.27843332243481, -.029465054624836284, .0445200642486725))
    band_shapes = sleeve.bands(ORIGIN, (1., 0., 0.), (0., 1., 0.))
    for side, base in (('inlet', inlet_base), ('outlet', outlet_base)):
        frame = _snapshot('pump-' + side + '-tpu', base)
        add('pump-' + side + '-tpu', sleeve.build_local(installed=True), sleeve.COLOR, frame)
        for band, shape in band_shapes.items():
            add('pump-' + side + '-' + band + '-band', shape, M_STAINLESS, frame)

    add('water-split', branch_tee(), M_NEOFIT_ACETAL, _snapshot('tee'))
    add('flow-regulator', native_reference('flow-regulator'), M_NEOFIT_ACETAL, _snapshot('reg'))
    for name in ('gas-regulator', 'gas-check'):
        add(name, native_reference(name), M_NEOFIT_ACETAL, _snapshot(name))
    # The RJ11 reference origin is its show face, rather than the frozen
    # assembly-world reference carried by the visualization snapshot.
    face = layout.specification()['rear_wall']['dry_openings']['keystone']['face_center_mm']
    add('keystone-jack', native_reference('keystone-jack'), C_C14, _frame(translation=face))

    depths = dict((
        ('tee-fold', 12.7), ('lower-valve-elbow', 12.7), ('lower-pump-elbow', 16.891),
        ('reg-va-elbow', 12.7), ('va-outlet-elbow', 12.7),
        ('carbonator-fold', check_reference().socket_depth('outlet')),
        ('gas-inlet-elbow', 17.), ('gas-lower-a', 17.), ('gas-lower-b', 16.891),
        ('gas-upper-a', check_reference().socket_depth('outlet')),
        ('gas-upper-b', 16.891), ('soda-stem-elbow', 12.7),
        ('soda-outlet-return-stem', 16.891 + layout.specification()['fore_routes']['soda_route']['metrics']['rear_stem_exposure_mm']),
        ('ya-stem-elbow', tee_reference().INSERTION),
        ('drain-outlet-stem', layout.specification()['fore_routes']['drain_stem_length_mm']),
        ('vb-inlet-turn', 12.7), ('vb-outlet-stem', 12.7),
        ('vb-outlet-return', 16.891), ('yb-stem-elbow', tee_reference().INSERTION)))
    depths.update({name: 12.7 for name in reservoir_gate_elbow_hosts()})
    for name in ('carbonator-fold', 'gas-inlet-elbow', 'gas-lower-a',
                 'gas-lower-b', 'gas-upper-a', 'gas-upper-b'):
        depths[name] += layout.snapshot_pose(name).get('exposed_stem_mm', 0.)
    for name in stem_elbow_names():
        add(name, stem_elbow(depths[name]), M_NEOFIT_WHITE_ACETAL, _snapshot(name))
    for name in union_elbow_names():
        add(name, native_reference('jg-turn-elbow'), M_JG_BLACK_PP, _snapshot(name))

    import soda_inlet
    add('soda-bend-holder', soda_inlet.holder_native(), M_PETGF_BLACK,
        layout.pose('soda-bend-holder'))
    neighbors = {name: result[name][0] for name in soda_inlet.SOFT_NEIGHBORS}
    add('soda-continuous-insulation', soda_inlet.foam_occupied(neighbors),
        M_NITRILE_BLACK, _frame())

    for row in _grid():
        source = _grid_module(row)
        if row['native_kind'] == 'gas':
            shape = source.build_neofit_bulkhead().val()
            color = M_NEOFIT_ACETAL
        elif row['native_kind'] == 'quarter':
            shape = pp1208e_bulkhead()
            color = M_JG_BLACK_PP
        else:
            shape = abu44m_bulkhead()
            color = M_NEOFIT_ACETAL
        add(row['name'], shape, color,
            _frame(translation=(row['x'], row['flange_y'], row['z'])))
        result[row['name'] + '-nut'] = _nut(row), color, _carry(_frame())
    return result


def _offset(point, vector, length=1.):
    return [point[i] + vector[i] * length for i in range(3)]


def port_stations(name):
    """Selected reference's native ``port -> (position, axis, diameter)``.

    The ASSE entry/exit aliases are its bare metal interfaces; the straight
    TPU cuffs own the 1/4-inch tube sockets. ``water-split.supply`` is the
    trimmed branch's shoulder at the cuff mouth, while ``stem-tip`` names
    its engaged cut end.
    """
    if name in reservoir_gate_elbow_hosts():
        return {'socket': ((0., 19.05, 0.), (0., 1., 0.), 6.35)}
    if name in ('valve-v-a', 'valve-v-b', 'vk-solenoid'):
        return {'inlet': ((0., -29.75, 11.05), (0., -1., 0.), 6.35),
                'outlet': ((0., 29.75, 11.05), (0., 1., 0.), 6.35)}
    if name == 'asse1022-assembly':
        return {'tube-in': ((0., 0., 27.), (-1., 0., 0.), 17.15),
                'tube-out': ((65., 0., 27.), (1., 0., 0.), 15.88),
                'vent-tip': ((32., 0., 0.), (0., 0., -1.), 8.)}
    if name == 'water-split':
        return {'supply': ((0., 6.0452, 0.), (0., 1., 0.), 6.35),
                'stem-tip': ((0., 21.0452, 0.), (0., 1., 0.), 6.35),
                'to-vk': ((20.1041, 0., 0.), (1., 0., 0.), 6.35),
                'to-flavor': ((-20.1041, 0., 0.), (-1., 0., 0.), 6.35)}
    if name == 'flow-regulator':
        return {'inlet': (ORIGIN, (-1., 0., 0.), 6.35),
                'outlet': ((67., 0., 0.), (1., 0., 0.), 6.35)}
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
        return {'tube': (adapter.tube_mouth((32., 0., 0.)), (0., 0., -1.), 4.)}
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
    fore, under = specification['fore_routes'], specification['under_head_route']
    result = {}

    def add(name, points, owners, *, segments=None, od=6.35, inside=4.24,
            status='complete_between_named_interfaces', basis='Nominal socket insertion', minimum_radius=None):
        result[name] = {'points_mm': points, 'centerline_mm': points, 'od_mm': od, 'id_mm': inside,
                        'owners': list(owners), 'status': status, 'basis': basis,
                        'segments': segments or [_line(a, b) for a, b in zip(points, points[1:])],
                        'spool': 'red' if 'gas-' in name else
                                 'black' if any(k in name for k in ('drain-vb', 'vb-yb')) else 'white'}
        result[name]['minimum_radius_mm'] = minimum_radius

    control = under['under_head_bezier_control_points_mm']
    points = under['under_head_centerline_mm']
    add('above-core-va-under-head', points, ('va-outlet-elbow', 'va-east-turn'),
        segments=[_line(points[0], control[0]), _bezier(control), _line(control[-1], points[-1])],
        minimum_radius=under.get('under_head_minimum_radius_mm', under.get('minimum_centerline_radius_mm')))
    ownership = {
        'va-fore-feed': ('va-east-turn', 'ya-stem-elbow'),
        'ya-concealed-link': ('ya-stem-elbow', 'ya-fold-inner'),
        'drain-vb-east-link': ('drain-outlet-stem', 'vb-inlet-turn'),
        'drain-vb-inlet-link': ('vb-inlet-turn', 'valve-v-b'),
        'vb-yb-cross': ('vb-outlet-stem', 'vb-outlet-return'),
        'vb-yb-link': ('vb-outlet-return', 'yb-stem-elbow'),
    }
    for name, points in fore['tubes'].items():
        if name.startswith('soda-'):
            continue
        segments = None
        if name == 'va-fore-feed':
            controls = fore.get('va_fore_controls_mm', [fore.get('va_fore_control_mm')])
            segments = [_line(points[0], controls[0][0]),
                        *[_bezier(control) for control in controls],
                        _line(controls[-1][-1], points[-1])]
        elif name == 'drain-vb-east-link':
            control = fore.get('vb_drain_control_mm', fore.get('b_plumbing', {}).get('inlet_control_mm'))
            if fore.get('b_plumbing', {}).get('inlet_arm_lift_degrees') == 0.:
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
        radius_key = {'va-fore-feed': 'va_fore_minimum_radius_mm',
                      'drain-vb-east-link': 'vb_drain_minimum_radius_mm',
                      'vb-yb-link': 'vb_return_minimum_radius_mm'}.get(name)
        radius = fore.get(radius_key) if radius_key else None
        if name == 'drain-vb-east-link' and radius is None:
            radius = fore.get('b_plumbing', {}).get('inlet_minimum_radius_mm')
        add('above-core-' + name, points, ownership[name], segments=segments, minimum_radius=radius)

    # Water header socket-to-socket links. Flush shoulder locations set the
    # exterior pose; each tube extends to the named receiving depth.
    part = components()
    elbow_socket = ((0., 19.05, 0.), (0., 1., 0.))
    for name, first, second, depth in (
        ('pump-inlet-link', 'lower-pump-elbow', 'pump-inlet-tpu', 15.),
        ('pump-check-link', 'pump-outlet-tpu', 'discharge-chain', check_reference().socket_depth('inlet')),
        ('tee-vk-link', 'water-split', 'tee-fold', 16.891),
        ('reg-va-link', 'flow-regulator', 'reg-va-elbow', 16.891),
    ):
        if name == 'pump-inlet-link':
            a, axis_a = part[first][2](elbow_socket)
            b, axis_b = part[second][2](((4.916132605004726, 18.5, 0.), (0., 1., 0.)))
            da = 16.891
        elif name == 'pump-check-link':
            a, axis_a = part[first][2](((4.916132605004726, 18.5, 0.), (0., 1., 0.)))
            b, axis_b = part[second][2](check_reference().inlet())
            da = 15.
        elif name == 'tee-vk-link':
            tee = _module('above_core_branch_tee', 'reference/branch-stem-tees/branch_stem_tees.py')
            p = tee.specification('neofit')['ports']['run_plus']
            a, axis_a = part[first][2]((p['position'], p['outward']))
            b, axis_b = part[second][2](elbow_socket)
            da = 16.891
        else:
            a, axis_a = part[first][2](((67., 0., 0.), (1., 0., 0.)))
            b, axis_b = part[second][2](elbow_socket)
            da = 15.
        add('above-core-' + name,
            [_offset(a, axis_a, -da), list(a), list(b), _offset(b, axis_b, -depth)],
            (first, second))

    tee = _module('above_core_branch_tee', 'reference/branch-stem-tees/branch_stem_tees.py')
    p = tee.specification('neofit')['ports']['run_minus']
    tee_mouth, tee_axis = part['water-split'][2]((p['position'], p['outward']))
    regulator_in, regulator_axis = part['flow-regulator'][2]((ORIGIN, (-1., 0., 0.)))
    add('above-core-tee-regulator',
        [_offset(tee_mouth, tee_axis, -16.891), _offset(regulator_in, regulator_axis, -15.)],
        ('water-split', 'flow-regulator'))

    inlet = part['asse-inlet-tpu'][2](((-20., 0., 0.), (-1., 0., 0.)))[0]
    water_port = part['bulkhead-water'][2](((0., -24.79, 0.), (0., -1., 0.)))[0]
    span = water_port[1] - inlet[1]
    controls = [[list(inlet), _offset(inlet, (0., 1., 0.), span/3),
                 _offset(water_port, (0., -1., 0.), span/3), list(water_port)]]
    points = [_offset(inlet, (0., -1., 0.), 15.),
              *[p for control in controls for p in _sample_bezier(control)],
              _offset(water_port, (0., 1., 0.), 12.7)]
    add('above-core-water-in', points, ('asse-inlet-tpu', 'bulkhead-water'),
        segments=[_line(points[0], inlet), *[_bezier(control) for control in controls],
                  _line(water_port, points[-1])],
        minimum_radius=span**2/
        (6*math.hypot(water_port[0]-inlet[0], water_port[2]-inlet[2])))

    d = specification['gas_datums']
    gas_inlet = d.get('inlet_route', {})
    gas_inlet_points = gas_inlet.get('points_mm', [
        _offset(d['inlet'], (0., 1., 0.), 12.7),
        _offset(d['c0'], (0., 1., 0.), 19.05-16.891)])
    add('above-core-gas-inlet', gas_inlet_points,
        ('co2-inlet', 'gas-inlet-elbow'), segments=gas_inlet.get('segments'),
        minimum_radius=gas_inlet.get('minimum_radius_mm'))
    gas_feed, gas_feed_axis = part['gas-lower-b'][2](elbow_socket)
    check_in, check_in_axis = part['gas-check'][2](check_reference().inlet())
    add('above-core-gas-check-link', [_offset(gas_feed, gas_feed_axis, -16.891),
                                    list(gas_feed), list(check_in),
                                    _offset(check_in, check_in_axis, -check_reference().socket_depth('inlet'))],
        ('gas-lower-b', 'gas-check'))
    gas_drop = d.get('core_drop_route', {})
    gas_drop_points = gas_drop.get('points_mm', [
        _offset(d['drop'], (0., 0., 1.), 16.891), list(d['guide'])])
    add('above-core-gas-core-drop', gas_drop_points,
        ('gas-upper-b', 'core-co2-guide'), segments=gas_drop.get('segments'),
        minimum_radius=gas_drop.get('minimum_radius_mm'))
    return result


def route_wire(specification):
    """Exact line/Bezier wire, omitting coincident illustrative mouth points."""
    edges = []
    for segment in specification['segments']:
        if segment['kind'] == 'line':
            a, b = (cq.Vector(*p) for p in segment['points_mm'])
            if (b-a).Length > 1e-6:
                edges.append(cq.Edge.makeLine(a, b))
        elif segment['kind'] == 'bezier':
            edges.append(cq.Edge.makeBezier([cq.Vector(*p) for p in segment['control_points_mm']]))
        elif segment['kind'] == 'arc':
            edges.append(cq.Edge.makeThreePointArc(*[cq.Vector(*p) for p in segment['points_mm']]))
        else:
            raise ValueError('Unknown native route segment: ' + segment['kind'])
    return cq.Wire.assembleEdges(edges)


def route_shape(specification):
    wire = route_wire(specification)
    first = wire.Edges()[0]
    start, normal = first.startPoint(), first.tangentAt(0.)
    return (cq.Workplane(cq.Plane(origin=start, normal=normal))
            .circle(specification['od_mm']/2).circle(specification['id_mm']/2)
            .sweep(wire, isFrenet=False, transition='round').val())


def tubes():
    """Placed hollow native tube solids for the explicit completed local routes."""
    return {name: route_shape(specification) for name, specification in route_specs().items()}
