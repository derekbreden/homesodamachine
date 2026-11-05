"""Differential probe of the enclosure_assembly namespace: run once per machine-data binary
(through harness.py) and diff the JSON lines.  usage: ea_probe.py <out.jsonl>"""
import collections, json, math, os, sys, traceback, types
from pathlib import Path

OUT = open(sys.argv[1], 'w')
ROOT = os.environ.get('HSM_REPO_ROOT', '')


def describe(v, depth=0):
    from _rust_objects import NativeProxy
    if depth > 9:
        return '<deep>'
    t = type(v)
    if v is None or t is bool:
        return repr(v)
    if t is int:
        return f'i:{v}'
    if t is float:
        return f'f:{v!r}'
    if t is str:
        return 's:' + v.replace(ROOT, '<root>') if ROOT else 's:' + v
    if isinstance(v, Path):
        return 'p:' + str(v).replace(ROOT, '<root>')
    if isinstance(v, NativeProxy):
        tag = v._tag['$native']
        kind = tag.get('kind')
        if kind in ('dict', 'list', 'tuple', 'set', 'frozenset'):
            try:
                return {'native-' + kind: describe(v._invoke('snapshot'), depth + 1)}
            except Exception as e:  # noqa: BLE001
                return f'native-{kind}:snapshot-failed:{type(e).__name__}'
        return 'native:' + str(kind)
    if isinstance(v, tuple):
        if hasattr(v, '_fields'):
            return {'nt:' + t.__name__: [[f, describe(x, depth + 1)] for f, x in zip(v._fields, v)]}
        return {'tuple': [describe(x, depth + 1) for x in v]}
    if isinstance(v, list):
        return {'list': [describe(x, depth + 1) for x in v]}
    if isinstance(v, dict):
        return {t.__name__: [[describe(k, depth + 1), describe(x, depth + 1)] for k, x in v.items()]}
    if isinstance(v, (set, frozenset)):
        return {t.__name__: sorted(json.dumps(describe(x, depth + 1)) for x in v)}
    if isinstance(v, types.ModuleType):
        return 'module:' + v.__name__
    if isinstance(v, types.GeneratorType):
        return {'generator': [describe(x, depth + 1) for x in v]}
    if t.__name__ == 'Vector':
        return f'vec:{v.x!r},{v.y!r},{v.z!r}'
    if isinstance(v, FakeBox):
        return f'box:{v.lo!r},{v.hi!r}'
    if t.__name__ == 'BoundBox':
        return f'bb:{(v.xmin, v.ymin, v.zmin, v.xmax, v.ymax, v.zmax)!r}'
    if callable(v):
        return 'callable:' + getattr(v, '__qualname__', getattr(v, '__name__', t.__name__))
    if hasattr(v, '__dict__') and not isinstance(v, type):
        return {'obj:' + t.__name__: [[k, describe(x, depth + 1)] for k, x in sorted(vars(v).items())
                                       if not k.startswith('__')]}
    return f'{t.__module__}.{t.__name__}:' + repr(v).replace(ROOT, '<root>')[:400]


def rec(label, value):
    OUT.write(json.dumps({'k': label, 'r': value}) + '\n')
    OUT.flush()


def probe(label, fn):
    try:
        v = fn()
        rec(label, ['ok', describe(v)])
        return v
    except BaseException as e:  # noqa: BLE001
        msg = str(e).replace(ROOT, '<root>')
        rec(label, ['err', type(e).__name__, msg[:1500]])
        return None


class FakeBox:
    """Stands in for a placed solid: `_boxes.boxed` is patched to hand it back as its own box."""

    def __init__(self, lo, hi):
        self.lo, self.hi = tuple(lo), tuple(hi)
        self.xmin, self.ymin, self.zmin = self.lo
        self.xmax, self.ymax, self.zmax = self.hi

    xlen = property(lambda s: s.xmax - s.xmin)
    ylen = property(lambda s: s.ymax - s.ymin)
    zlen = property(lambda s: s.zmax - s.zmin)

    def add(self, other):
        return FakeBox(tuple(min(a, b) for a, b in zip(self.lo, other.lo)),
                       tuple(max(a, b) for a, b in zip(self.hi, other.hi)))

    def __repr__(self):
        return f'FakeBox({self.lo!r}, {self.hi!r})'


def fb(cx, cy, cz, dx=10.0, dy=10.0, dz=10.0):
    return FakeBox((cx - dx / 2, cy - dy / 2, cz - dz / 2), (cx + dx / 2, cy + dy / 2, cz + dz / 2))


def ident(st):
    return (tuple(st[0]), tuple(st[1]))


def yaw(st):
    (x, y, z), (a, b, c) = st
    return ((y, -x, z), (b, -a, c))


def shifted(dx, dy, dz):
    def carry(st):
        (x, y, z), d = st
        return ((x + dx, y + dy, z + dz), tuple(d))
    return carry


sys.path.insert(0, os.path.abspath('hardware/manifold-layout'))
import enclosure_assembly as ea  # noqa: E402

C = ea._compiled

# --- A. the namespace as initialize leaves it --------------------------------------------
names = probe('names', lambda: C.names())
for n in names or ():
    probe('get:' + n, lambda n=n: C.get(n))

import _boxes  # noqa: E402
_boxes.boxed = lambda shape: shape
import _cold_core_interface as cci  # noqa: E402
import above_core as above  # noqa: E402

# --- B. calls -----------------------------------------------------------------------------
P = probe
P('wago_step 413', lambda: ea.wago_step('413'))
P('wago_step 999', lambda: ea.wago_step('999'))
b1 = fb(10.0, 20.0, 30.0, 4.0, 6.0, 8.0)
P('box', lambda: ea.box(b1))
P('_shift none', lambda: ea._shift(b1))
P('_shift cx y0 z0 dz', lambda: ea._shift(b1, cx=1.0, y0=2.0, z0=3.0, dz=0.5))
P('_shift x0 x1 cy y1', lambda: ea._shift(b1, x0=1, x1=2.5, cy=7, y1=3))
P('_shift dz0', lambda: ea._shift(b1, dz=0))
P('_turned z90', lambda: ea._turned((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0))
P('_turned skew', lambda: ea._turned((1.0, 2.0, 3.0), (1.0, 1.0, 0.0), 33.0))
P('_turned int', lambda: ea._turned((1, 2, 3), (0, 1, 0), -90))
P('record_seat planes', lambda: ea.record_seat('probe-a', planes={'cx': 1.0, 'z0': None, 'y1': 3.0, 'foo': 2.0},
                                               got=b1, turns=[((0.0, 0.0, 1.0), 90.0)], members=['x', 'y']))
P('record_seat station', lambda: ea.record_seat('probe-b', station=[1.0, 2.0, 3.0], got=(1.5, 2.0, 3.25)))
P('record_seat bare', lambda: ea.record_seat('probe-c', got=b1))
P('record_seat replace', lambda: ea.record_seat('probe-c', planes={'x0': 9.0}, got=b1))
P('note_room a', lambda: ea.note_room('probe-a', 'lane', 1.0, 2.0))
P('note_room b', lambda: ea.note_room('probe-a', 'more', 1.5, None))
P('note_room missing', lambda: ea.note_room('nobody', 'lane', 1.0, 2.0))
P('SEATS after', lambda: C.get('SEATS'))
seats = C.get('SEATS')
for nm in ('probe-a', 'probe-b', 'probe-c'):
    P('seat_off ' + nm, lambda nm=nm: ea.seat_off(seats[nm]))
P('seat_off fake', lambda: ea.seat_off(types.SimpleNamespace(rule={'cx': 1.0, 'z0': 2}, got={'cx': 1.5})))
P('seat_off empty', lambda: ea.seat_off(types.SimpleNamespace(rule={}, got={})))

enc = ea._enc
P('east_lane_free low', lambda: ea.east_lane_free(fb(100.0, -200.0, 20.0)))
P('east_lane_free high', lambda: ea.east_lane_free(fb(100.0, -200.0, 2000.0)))
P('power_face_station ident', lambda: ea.power_face_station(ident))
P('power_face_station yaw', lambda: ea.power_face_station(yaw))
P('cap_face', lambda: ea.cap_face(fb(0.0, 0.0, 100.0)))
P('mq6_cradle', lambda: ea.mq6_cradle(shifted(1.0, 2.0, 3.0)))
P('record_bound', lambda: ea.record_bound(ea.Bound('probe', 'Probe bound', True, 1.0, 2.0, 'detail')))
P('record_bound replace', lambda: ea.record_bound(ea.Bound('probe', 'Probe bound 2', False, 1.0, 2.0, 'detail', 'note')))
P('carry_enclosure_bounds', lambda: ea.carry_enclosure_bounds())
P('carry_stated_bounds', lambda: ea.carry_stated_bounds())
P('BOUNDS after', lambda: C.get('BOUNDS'))
P('_core_frame', lambda: ea._core_frame(yaw))
P('cap_xy', lambda: ea.cap_xy(yaw, (10.0, 20.0)))
P('cap_xy shifted', lambda: ea.cap_xy(shifted(5.0, -3.0, 1.0), (10, 20)))

cradles = list(cci.cap_cradles)
placed_cradles = {name: fb(10.0 * i, 5.0 * i, 250.0, 20.0 + i, 30.0 - i, 15.0) for i, name in enumerate(cradles)}
rows = P('cradle_rows', lambda: ea.cradle_rows(fb(0.0, 0.0, 100.0, 300.0, 300.0, 240.0), yaw, placed_cradles))
if rows:
    P('cradles_land', lambda: ea.cradles_land(rows))
St = collections.namedtuple('St', 'centre yaw seat')
P('cradles_land synth', lambda: ea.cradles_land([('a', St((1.0, 2.0), 0.0, 3.0), (1.0, 2.0, 0.0, 3.0), 1, 1),
                                                ('b', St((1.0, 2.0), 0.0, 3.0), (1.0, 2.5, 0.0, 3.0), 1, 1),
                                                ('c', St((1.0, 2.0), 90.0, 3.0), (1.0, 2.0, 90.005, 3.0), 1, 1)]))

placed_valves = {
    'valve-v-zz1': fb(10.0, 100.0, 50.0), 'coil-v-zz1': fb(10.0, 130.0, 50.0),
    'valve-v-zz2': fb(40.0, 100.0, 60.0), 'coil-v-zz2': fb(40.0, 130.0, 60.0),
    'valve-v-zz3': fb(70.0, 100.0, 60.0), 'coil-v-zz3': fb(70.0, 70.0, 60.0),
    'valve-v-zz4': fb(90.0, 100.0, 60.0, 12.0), 'coil-v-zz4': fb(90.0, 100.0, 90.0),
    'other': fb(0.0, 0.0, 0.0),
}
P('_valve_up zz1', lambda: ea._valve_up(placed_valves, 'valve-v-zz1'))
P('_valve_up zz4', lambda: ea._valve_up(placed_valves, 'valve-v-zz4'))
P('_valve_up missing', lambda: ea._valve_up({'valve-v-q': fb(0, 0, 0)}, 'valve-v-q'))
P('_bodies', lambda: ea._bodies({'a': b1, 'b': (b1, 'red'), 'c': [b1]}))
for nm in ['valve-v-zz1', 'valve-v-a', 'coil-v-a', 'valve-x'] + list(above.valve_names())[:2] + cradles[:1]:
    P('_tray_valve ' + nm, lambda nm=nm: ea._tray_valve(nm))
bounds_valves = {k: (v.lo, v.hi) for k, v in placed_valves.items()}
P('valve_tray_decks_from_bounds', lambda: ea.valve_tray_decks_from_bounds(bounds_valves))
P('valve_tray_decks_from_bounds missing', lambda: ea.valve_tray_decks_from_bounds({'valve-v-zz9': ((0, 0, 0), (1, 1, 1))}))
P('valve_tray_decks', lambda: ea.valve_tray_decks(placed_valves))
P('valve_tray_decks pairs', lambda: ea.valve_tray_decks({k: (v, 'c') for k, v in placed_valves.items()}))
P('tray_name fresh', lambda: ea.tray_name(1, 1.0, 12.3, {}))
P('tray_name taken', lambda: ea.tray_name(1, 1.0, 12.5, {'valve-tray-fore': 1}))
P('tray_name west', lambda: ea.tray_name(0, -1.0, 5.0, {}))
P('tray_name bad', lambda: ea.tray_name(3, 1.0, 5.0, {}))
fore_only = {k: v for k, v in placed_valves.items() if k[-1] in '12'}
P('valve_tray_stations', lambda: ea.valve_tray_stations(fore_only))
P('valve_tray_stations axis0', lambda: ea.valve_tray_stations(placed_valves))
P('valve_tray_stations_from_bounds', lambda: ea.valve_tray_stations_from_bounds({k: (v.lo, v.hi) for k, v in fore_only.items()}))
P('_valve_tray_stations', lambda: ea._valve_tray_stations({'b': (1, -1.0, 3.5, (('v1', 1.0000004, 2), ('v2', 3, 4.25)))}))

placed_pumps = {
    'pump-a-head': fb(10.0, 0.0, 50.0, 20.0, 20.0, 10.0), 'pump-a-motor': fb(10.0, 1.0, 70.0, 18.0, 18.0, 30.0),
    'pump-b-head': fb(60.0, 0.0, 50.0, 20.0, 20.0, 10.0), 'pump-b-motor': fb(60.0, 0.5, 75.0, 18.0, 18.0, 30.0),
    'pump-c-head': fb(90.0, 0.0, 50.0), 'pump-c-motor': fb(90.0, 30.0, 50.0),
    'valve-v-x': fb(0, 0, 0),
}
up_only = {k: v for k, v in placed_pumps.items() if not k.startswith('pump-c')}
P('_pump_up a', lambda: ea._pump_up(placed_pumps, 'pump-a-head'))
P('_pump_up c', lambda: ea._pump_up(placed_pumps, 'pump-c-head'))
P('_pump_up missing', lambda: ea._pump_up({'pump-q-head': b1}, 'pump-q-head'))
P('pump_tray_seats', lambda: ea.pump_tray_seats(placed_pumps))
P('pump_tray_seats_from_bounds', lambda: ea.pump_tray_seats_from_bounds({k: (v.lo, v.hi) for k, v in placed_pumps.items()}))
P('pump_tray_seats_from_bounds missing', lambda: ea.pump_tray_seats_from_bounds({'pump-z-head': ((0, 0, 0), (1, 1, 1))}))
P('pump_tray_stations', lambda: ea.pump_tray_stations(up_only))
P('pump_tray_stations side', lambda: ea.pump_tray_stations(placed_pumps))
mcarry = ea.manifold_carry(5.0)
P('manifold_carry station', lambda: mcarry(((1.0, 2.0, 3.0), (0.0, 0.0, 1.0))))
P('manifold_carry int', lambda: ea.manifold_carry(2)(((1, 2, 3), (0, 1, 0))))
trays = P('manifold_pump_trays', lambda: ea.manifold_pump_trays(mcarry))
P('manifold_pump_trays ident', lambda: ea.manifold_pump_trays(ident))
spec = P('collet_plate_spec', lambda: ea.collet_plate_spec(mcarry, trays or ((0.0, 0.0, 0.0),)))
P('collet_plate_spec trays', lambda: ea.collet_plate_spec(ident, trays or ((0.0, 0.0, 0.0),), [(1.0, 2.0)]))
if spec:
    parts = collections.defaultdict(lambda: fb(1.0, 2.0, 3.0))
    P('record_pump_dock_seats', lambda: ea.record_pump_dock_seats(types.SimpleNamespace(pack=types.SimpleNamespace(collet_plate=spec)), parts))
    P('SEATS after dock', lambda: C.get('SEATS'))
foam_box = fb(0.0, 0.0, 100.0, 300.0, 300.0, 240.0)
P('vent_chase', lambda: ea.vent_chase(foam_box, yaw))
P('core_holds', lambda: ea.core_holds(foam_box))
J = collections.namedtuple('J', 'id frm to made mm')
P('refrigerant_mates', lambda: ea.refrigerant_mates([J('a', 'x', 'y', 'mate', 0.01), J('b', 'x', 'y', 'mate', None),
                                                     J('c', 'x', 'y', 'drawn', 0.0), J('d', 'x', 'y', 'mate', 0.05),
                                                     J('e', 'x', 'y', 'mate', 0.06), J('f', 'p', 'q', 'mate', 0)]))
P('pump_mount_rows', lambda: ea.pump_mount_rows(ident, ident))
anchor_names = list(cci.cap_anchors)
side_names = list(cci.cap_side_anchors)
for nm in anchor_names:
    P('cap_anchor ' + nm, lambda nm=nm: ea.cap_anchor(nm))
    P('cap_conduit ' + nm, lambda nm=nm: ea.cap_conduit(nm))
for nm in side_names:
    P('cap_side_anchor ' + nm, lambda nm=nm: ea.cap_side_anchor(nm))
P('cap_anchor bad', lambda: ea.cap_anchor('nothing'))
P('cap_conduit bad', lambda: ea.cap_conduit('nothing'))
for fn in ('water_pump_west_limit', 'water_pump_port_lane_limit', 'bulkhead_seat_y', 'bulkhead_mouth_y',
           'west_interior_face', 'west_exterior_face', 'west_seam_crown', 'interior_ceiling',
           'c14_mount_half', 'c14_seat_y', 'c14_stations', 'c14_cutout', 'co2_inlet_mouth_y',
           'east_wall_seat', '_wago_skirt', 'wago_row_reach', 'above_core_ceiling_reliefs'):
    P(fn + '()', lambda fn=fn: getattr(ea, fn)())
P('c14_cutout extra arg', lambda: ea.c14_cutout(1))
P('c14_cutout bogus kw', lambda: ea.c14_cutout(bogus=1))
P('port_clamp_stack bogus kw', lambda: ea.port_clamp_stack(3.0, bogus=1))
P('port_clamp_stack missing', lambda: ea.port_clamp_stack())
P('port_clamp_stack missing and bogus', lambda: ea.port_clamp_stack(bogus=1))
P('port_clamp_stack twice', lambda: ea.port_clamp_stack(3.0, t=4.0))
P('y_wall_ports', lambda: ea.y_wall_ports(ident, {'bulkhead-carb': yaw, 'bulkhead-flavor-a': shifted(1, 2, 3)}))
P('y_wall_ports bad', lambda: ea.y_wall_ports(ident, {'nothing': yaw}))
stations = P('wall_stations', lambda: ea.wall_stations(ident, {'bulkhead-carb': yaw, 'bulkhead-flavor-a': shifted(1, 2, 3),
                                                               'bulkhead-flavor-b': ident}, shifted(-5, 0, 7), ident))
if stations:
    P('y_wall_field', lambda: ea.y_wall_field(stations))
for nm in ('union', 'water', 'flavor-a', 'drain', 'co2'):
    P('ring_name ' + nm, lambda nm=nm: ea.ring_name(nm))
    P('word_name ' + nm, lambda nm=nm: ea.word_name(nm))
    P('customer_tube_name ' + nm, lambda nm=nm: ea.customer_tube_name(nm))
    P('collar_name ' + nm, lambda nm=nm: ea.collar_name(nm))
    P('collar_word_name ' + nm, lambda nm=nm: ea.collar_word_name(nm))
    P('port_pocket_d ' + nm, lambda nm=nm: ea.port_pocket_d(nm))
    P('port_pocket_rise ' + nm, lambda nm=nm: ea.port_pocket_rise(nm))
P('port_pocket_d()', lambda: ea.port_pocket_d())
P('port_pocket_d kw', lambda: ea.port_pocket_d(ring='neofit'))
P('port_pocket_rise()', lambda: ea.port_pocket_rise())
P('port_pocket_rise None', lambda: ea.port_pocket_rise(None))
for t in (3.0, 10, 2, 0, 7.25):
    P(f'port_clamp_stack {t!r}', lambda t=t: ea.port_clamp_stack(t))
for st in ((0.0, 100.0), (50, 150), (10.0, 20.0, 30.0)):
    P(f'nameplate_cut {st!r}', lambda st=st: ea.nameplate_cut(st))
P('flavor_storey', lambda: ea.flavor_storey(100.0, ident))
P('flavor_storey int', lambda: ea.flavor_storey(100, ident))
for nm in ('bulkhead-flavor-a', 'bulkhead-flavor-b', 'bulkhead-carb'):
    P('panel_z ' + nm, lambda nm=nm: ea.panel_z(nm, 1.0, 2))
for nm, cr in (('ident', ident), ('yaw', yaw), ('shifted', shifted(3.0, -4.0, 5.0))):
    P('digiten_anchors ' + nm, lambda cr=cr: ea.digiten_anchors(cr))
    P('asse_sections ' + nm, lambda cr=cr: ea.asse_sections(cr))
    P('asse_ties ' + nm, lambda cr=cr: ea.asse_ties(cr))
    P('asse_reach_down ' + nm, lambda cr=cr: ea.asse_reach_down(cr))
    P('_asse_section_drops ' + nm, lambda cr=cr: ea._asse_section_drops(cr))
    P('asse_cradle ' + nm, lambda cr=cr: ea.asse_cradle(cr))
    P('body_anchors ' + nm, lambda cr=cr: ea.body_anchors({'wr1110': cr, 'gasher-co2': cr, 'water-split': cr}))
    P('co2_wall_port ' + nm, lambda cr=cr: ea.co2_wall_port(cr))
    P('floor_mounts ' + nm, lambda cr=cr: ea.floor_mounts((cr, [(1.0, 2.0), (3, 4)], 5.0, 6.0), (ident, ((1, 1),), 2, 3)))
P('body_anchors none', lambda: ea.body_anchors({}))
P('body_anchors yaw-only', lambda: ea.body_anchors({'water-split': yaw}))
P('floor_mounts none', lambda: ea.floor_mounts())
P('floor_mounts kw', lambda: ea.floor_mounts(mounted=1))
P('keystone_cutout', lambda: ea.keystone_cutout((1.0, 2.0)))
P('keystone_cutout int', lambda: ea.keystone_cutout([3, 4]))
for nm in ('compressor', 'enclosure-x', 'foo', 'wago-mana', 'anchor-cap-carb-1', 'tee-y-a', 'valve-v-a'):
    P('_manifold ' + nm, lambda nm=nm: ea._manifold(nm))
P('_on_leg mid', lambda: ea._on_leg((0.5, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
P('_on_leg past', lambda: ea._on_leg((2.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
P('_on_leg off', lambda: ea._on_leg((0.5, 0.001, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
P('_on_leg off tol', lambda: ea._on_leg((0.5, 0.001, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1e-2))
P('_on_leg tiny', lambda: ea._on_leg((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
P('_on_leg ints', lambda: ea._on_leg((1, 1, 1), (0, 0, 0), (2, 2, 2)))
P('_on_leg end', lambda: ea._on_leg((1, 0, 0), (0, 0, 0), (1, 0, 0)))

# --- runs ---------------------------------------------------------------------------------
Run = collections.namedtuple('Run', 'id pts radii bends diam')
carb = Run('carb-1', [(0.0, -300.0, 150.0), (0.0, -200.0, 150.0), (150.0, -200.0, 150.0), (150.0, -200.0, 60.0)],
           {1: 12.0, 2: 15.0}, [(1, 90.0, 0, 1), (2, 90.0, 1, 2)], 6.35)
co2 = Run('co2-2', [(-50.0, 0.0, 200.0), (-50.0, 100.0, 200.0), (60.0, 100.0, 200.0)], {1: 10.0},
          [(1, 90.0, 0, 1)], 6.35)
fl28 = Run('fluid-28', [(100.0, -200.0, 270.0), (100.0, -100.0, 270.0), (-80.0, -100.0, 270.0), (-80.0, 320.0, 270.0),
                        (-80.0, 320.0, 100.0)], {1: 10.0, 2: 10.0, 3: 8.0}, [(1, 90.0, 0, 1), (2, 90.0, 1, 2), (3, 90.0, 2, 3)], 4.0)
fl28_short = fl28._replace(pts=[(100.0, -200.0, 270.0), (100.0, -100.0, 270.0), (-80.0, -100.0, 270.0), (-80.0, 300.0, 270.0),
                                (-80.0, 300.0, 100.0)])
short = Run('carb-1', [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 2.0, 0.0)], {}, [], 6.35)
plain = Run('fluid-2', [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (100.0, 50.0, 0.0)], {1: 5.0}, [(1, 90.0, 0, 1)], 4.0)
for r in (carb, co2, fl28, plain):
    for leg in range(len(r.pts) - 1):
        P(f'tube_anchor_midpoint {r.id} {leg}', lambda r=r, leg=leg: ea.tube_anchor_midpoint(r, leg))
sites = P('tube_anchor_sites', lambda: ea.tube_anchor_sites([carb, co2, fl28, plain]))
P('tube_anchor_sites fl28 short', lambda: ea.tube_anchor_sites([carb, co2, fl28_short]))
P('tube_anchor_sites none', lambda: ea.tube_anchor_sites([]))
P('tube_anchor_sites short', lambda: ea.tube_anchor_sites([short]))
P('tube_anchor_sites co2', lambda: ea.tube_anchor_sites([co2]))
P('tube_anchor_sites co2 across', lambda: ea.tube_anchor_sites([co2._replace(pts=[(-50.0, 0.0, 200.0), (-50.0, 0.0, 300.0), (60.0, 0.0, 300.0)])]))
station_rows = [st for _rid, st in sites] if sites else []
station_rows += [((50.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.0), ((100.0, 25.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 3.0)]
P('unsupported_spans', lambda: ea.unsupported_spans([carb, co2, fl28, plain], station_rows))
P('unsupported_spans none', lambda: ea.unsupported_spans([plain], []))
import _reservoir_a_anchors  # noqa: E402
ra_ids = [i for row in _reservoir_a_anchors.datums().values() for i in row['routes_west_to_east']]
ra_runs = [Run(i, [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], {}, [], 4.0) for i in ra_ids]
P('reservoir_a_anchor_sites', lambda: ea.reservoir_a_anchor_sites(ra_runs + [plain]))
P('reservoir_a_anchor_sites none', lambda: ea.reservoir_a_anchor_sites([plain]))
import above_core_routes  # noqa: E402
specs = above_core_routes.reservoir_a_route_specs()
for rid in ('fluid-14', 'fluid-16'):
    if rid not in specs:
        continue
    pts = [tuple(p) for p in specs[rid]['points_mm']]
    run = Run(rid, pts, {}, [], 4.0)
    held = []
    for seg in specs[rid]['segments']:
        if seg['kind'] == 'line':
            p, q = seg['points_mm']
            held.append(tuple((a + b) / 2.0 for a, b in zip(p, q)))
            held.append(tuple(p))
        else:
            held.append(tuple(seg['points_mm'][-1]))
            held.append(tuple(seg['points_mm'][0]))
    P(f'reservoir_a_developed_stations {rid}', lambda run=run, held=held: ea.reservoir_a_developed_stations(run, held))
    P(f'reservoir_a_developed_stations {rid} none', lambda run=run: ea.reservoir_a_developed_stations(run, []))
    P(f'reservoir_a_developed_stations {rid} moved', lambda run=run: ea.reservoir_a_developed_stations(run._replace(pts=run.pts[:-1]), []))
    P(f'unsupported_spans {rid}', lambda run=run, held=held: ea.unsupported_spans([run], [(h, (1, 0, 0), (0, 0, 1), 2.0) for h in held]))
P('reservoir_a_developed_stations other', lambda: ea.reservoir_a_developed_stations(plain, []))

foam_carry = shifted(10.0, -20.0, 5.0)
cap_runs = []
for nm in anchor_names:
    st = ea.cap_anchor(nm)
    mid = foam_carry(st)[0]
    cap_runs.append(Run(nm, [tuple(m - 10.0 for m in mid), tuple(mid), tuple(m + 10.0 * (k == 0) for k, m in enumerate(mid))], {}, [], 4.0))
for nm in side_names:
    st = ea.cap_side_anchor(nm)
    mid = foam_carry(st)[0]
    cap_runs.append(Run(nm, [tuple(mid[k] - (5.0 if k == 1 else 0.0) for k in range(3)),
                             tuple(mid[k] + (5.0 if k == 1 else 0.0) for k in range(3))], {}, [], 4.0))
P('cap_tube_anchors', lambda: ea.cap_tube_anchors(foam_carry, cap_runs))
P('cap_tube_anchors none', lambda: ea.cap_tube_anchors(foam_carry, []))
P('cap_tube_anchors miss', lambda: ea.cap_tube_anchors(ident, cap_runs))
P('lid_cap_stations', lambda: ea.lid_cap_stations(foam_carry, cap_runs))
P('lid_cap_stations miss', lambda: ea.lid_cap_stations(ident, cap_runs))
Mod = types.SimpleNamespace
mod = Mod(inlet=lambda: ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), outlet=lambda: ((100.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
          sections=lambda: [('thin', 2.0, 0.0, 30.0), ('fat', 5.0, 20.0, 80.0), ('tail', 3.5, 70.0, 100.0)])
bodies = {nm: (shifted(float(i), 0.0, 0.0), mod) for i, nm in enumerate(anchor_names)}
P('anchor_rows', lambda: ea.anchor_rows(foam_carry, bodies))
P('anchor_rows none', lambda: ea.anchor_rows(foam_carry, {}))
P('_whole', lambda: ea._whole([fb(0, 0, 0), fb(5.0, 6.0, 7.0, 1, 2, 30)]))
P('_whole none', lambda: ea._whole([]))
P('manifold_references none', lambda: ea.manifold_references(types.SimpleNamespace()))
P('manifold_references nil', lambda: ea.manifold_references(types.SimpleNamespace(manifold_reading=None)))
Ch = types.SimpleNamespace
tree = types.SimpleNamespace(children=[Ch(name='x'), Ch(name='manifold-layout'), Ch(name='y')])
P('_with_manifold_rows', lambda: ea._with_manifold_rows(tree, {'x': 1, 'manifold-layout': 2, 'y': 3}, {'r1': 10, 'r2': 20}))
P('_with_manifold_rows tail', lambda: ea._with_manifold_rows(tree, {'x': 1}, {'r1': 10}))
P('_with_manifold_rows none', lambda: ea._with_manifold_rows(types.SimpleNamespace(children=[]), {}, {'r1': 10}))

# --- reliefs ------------------------------------------------------------------------------
tol = enc.stated_bound_tol
face = enc.back_top_ceiling_face()
wall = enc.wall
rel = (
    ('asse1022-assembly', 0.0, 10.0, 0.0, 20.0, face + 3.0),
    ('asse1022-assembly', 1.0, 9.0, 1.0, 19.0, face + 3.0),
    ('asse1022-assembly', -1.0, 11.0, 0.0, 20.0, face + 3.0),
    ('digiten-flow', 20.0, 30.0, 0.0, 10.0, face + 2.5),
    ('digiten-flow', 25.0, 35.0, 5.0, 15.0, face + 4.0),
    ('digiten-flow', 50.0, 55.0, 5.0, 15.0, face + 4.0),
    ('wr1110', 40.0, 50.0, 0.0, 10.0, face + 5.0),
    ('gasher-co2', 60.0, 70.0, 0.0, 10.0, face + 0.5),
    ('bulkhead-water', 0.0, 10.0, 21.0, 30.0, face + 4.0),
    ('other', 0.0, 1.0, 0.0, 1.0, face),
)
P('_contained_reliefs', lambda: ea._contained_reliefs(rel))
P('_enveloped_reliefs', lambda: ea._enveloped_reliefs(rel))
P('_enveloped_reliefs apart', lambda: ea._enveloped_reliefs(rel[3:4] + rel[5:6]))
P('_level_reliefs', lambda: ea._level_reliefs(rel))
P('_level_reliefs list', lambda: ea._level_reliefs(list(rel[:3])))
P('_full_depth_reliefs', lambda: ea._full_depth_reliefs(rel))
P('_full_depth_reliefs ok', lambda: ea._full_depth_reliefs(rel[:3]))
P('_minimum_depth_reliefs', lambda: ea._minimum_depth_reliefs(rel))
cr = P('asse_cradle for reliefs', lambda: ea.asse_cradle(yaw))
P('_asse_end_reliefs none', lambda: ea._asse_end_reliefs(rel, ()))
P('_asse_end_reliefs synth', lambda: ea._asse_end_reliefs(rel + (('asse1022-assembly', 0.0, 1.0, 9.0, 21.0, 1.0),
                                                                  ('asse1022-assembly', 0.0, 1.0, -0.5, 30.0, 1.0)),
                                                         (0.0, ((10.0, 12.0), (12.0, 18.0), (18.0, 20.0)))))
if cr:
    P('_asse_end_reliefs cradle', lambda: ea._asse_end_reliefs(rel, cr))
P('_connected_reliefs', lambda: ea._connected_reliefs(rel))
P('_connected_reliefs twice', lambda: ea._connected_reliefs(ea._connected_reliefs(rel)))
P('_connected_reliefs x', lambda: ea._connected_reliefs((('digiten-flow', 0.0, 10.0, 0.0, 10.0, 5.0),
                                                         ('wr1110', 11.0, 20.0, 2.0, 8.0, 4.0),
                                                         ('wr1110', 10.5, 20.0, 2.0, 8.0, 4.0),
                                                         ('wr1110', 0.0, 9.0, 10.5, 18.0, 3.0),
                                                         ('wr1110', 30.0, 40.0, 30.0, 40.0, 3.0))))
P('_connected_reliefs empty', lambda: ea._connected_reliefs(()))
P('above_core reliefs chain', lambda: ea._connected_reliefs(ea._minimum_depth_reliefs(ea._level_reliefs(
    ea._enveloped_reliefs(ea._contained_reliefs(ea.above_core_ceiling_reliefs()))))))

# --- anchors and wells --------------------------------------------------------------------
roots_lane = P('back_top_frames', lambda: enc.back_top_frames())
owned = []
for y in range(-300, 451, 15):
    for z in (face - 30.0, face - 15.0, face - 5.0, 150.0, 250.0):
        for x in (-60.0, 0.0, 60.0):
            if enc.back_top_owns((x, float(y), z)):
                owned.append((x, float(y), z))
rec('owned', [len(owned), owned[:3]])
anchor_stations = list(station_rows)
for pt in owned[::max(1, len(owned) // 5)][:5]:
    anchor_stations += [(pt, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('column', 'corbel')),
                        (pt, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('corbel', 'column'), 'cap'),
                        (pt, (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), 3.2, ('column', 'column')),
                        (pt, (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 3.2, ('corbel', 'corbel'), 'cap'),
                        (pt, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2)]
anchor_stations += [((0.0, 150.0, face - 10.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('column', 'corbel')),
                    ((0.0, 150.0, face - 10.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('corbel', 'column'), 'cap'),
                    ((0.0, -900.0, 10.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('corbel', 'corbel')),
                    ((0.0, -900.0, 10.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('corbel', 'corbel'), 'cap'),
                    ((0.0, 150.0, face - 10.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 3.2, ('arch', 'corbel'))]
for i, st in enumerate(anchor_stations):
    P(f'stand_anchors {i}', lambda st=st: ea.stand_anchors([st]))
    P(f'authored_anchor_corbels {i}', lambda st=st: ea.authored_anchor_corbels([st]))
axes = [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
combo_points = owned[::max(1, len(owned) // 3)][:3] + [pt for pt in ((-95.0, 210.0, 300.0), (95.0, 250.0, 300.0), (-95.0, 300.0, 200.0))
                                                       if enc.back_top_owns(pt)]
ok_columns = 0
for pt in combo_points:
    for u in axes:
        for root in axes:
            if sum(a * b for a, b in zip(u, root)) != 0.0:
                continue
            got = P(f'stand_anchors combo {pt} {u} {root}', lambda pt=pt, u=u, root=root:
                    ea.stand_anchors([(pt, u, root, 3.2, ('column', 'column'))]))
            ok_columns += got is not None
            P(f'authored_anchor_corbels combo {pt} {u} {root}', lambda pt=pt, u=u, root=root:
              ea.authored_anchor_corbels([(pt, u, root, 3.2, ('corbel', 'corbel'))]))
rec('ok columns', ok_columns)
P('stand_anchors sites', lambda: ea.stand_anchors(station_rows))
P('authored_anchor_corbels sites', lambda: ea.authored_anchor_corbels(station_rows))
wells = [(+1, 10.0, 322.25, '413', 200.0, True), (-1, 20.0, 270.0, '413', 190.0, False),
         (-1, 30.0, 270.00001, '413', 190.0, False), (1, 40.0, 100.0, '415', None, True),
         (1, 50.0, 120.0, '415', 150.0, True, 'extra')]
P('stand_wells', lambda: ea.stand_wells(wells))
P('stand_wells missing', lambda: ea.stand_wells(wells[1:]))
P('stand_wells none-clear', lambda: ea.stand_wells(wells + [(+1, 11.0, 322.25, '413', None, True)]))
row = [('wago-v12', fb(300.0, 100.0, 322.25, 10, 20, 30), None), ('wago-gnd', fb(300.0, 112.0, 322.25, 10, 20, 30), None)]
cluster = [('wago-mana', fb(169.0, 280.0, 250.0), None, '420'), ('wago-manb', fb(169.0, 246.0, 250.0), None, '415'),
           ('wago-sensors', fb(-335.0, 270.0, 280.0), None, '413')]
P('wago_wells', lambda: ea.wago_wells(row, cluster, 200.0))
P('wago_wells empty', lambda: ea.wago_wells([], [], 1))
P('_wago_skirt 415', lambda: ea._wago_skirt('415'))
P('_wago_skirt 420 kw', lambda: ea._wago_skirt(size='420'))

# --- the flank pockets and the remaining readers --------------------------------------------
ref = types.SimpleNamespace(summaries=[{'name': 'coil-v-f'}, {'name': 'coil-v-f/2'}, {'name': 'valve-v-f'},
                                       {'name': 'coil-v-i'}, {'name': 'valve-v-i'}],
                            raw_bounds={'coil-v-f': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                                        'coil-v-i': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                                        'valve-v-f': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                                        'valve-v-i': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))},
                            model=None)
P('front_flank_reliefs_fine', lambda: ea.front_flank_reliefs_fine(ref))
P('front_flank_reliefs_fine kw', lambda: ea.front_flank_reliefs_fine(ref, transform=None))
P('funnel_centre', lambda: ea.funnel_centre(types.SimpleNamespace(inner=(1.0, 4.0))))
P('funnel_centre int', lambda: ea.funnel_centre(types.SimpleNamespace(inner=(1, 4))))
P('funnel_centre odd', lambda: ea.funnel_centre(types.SimpleNamespace(inner=(1, 2))))

import _assembly_model  # noqa: E402


def fake_commons(model, requests, *, transform=None):
    out = []
    for r in requests:
        box = r['box']
        if model == 'empty':
            out.append({'raw': {'min': None, 'max': None}})
        else:
            shift = 0.0 if transform is None else 0.25
            out.append({'raw': {'min': [v + shift for v in box[0]], 'max': [v + shift for v in box[1]]},
                        'indices': list(r['indices'])})
    return out


_assembly_model.box_commons = fake_commons
_assembly_model.instance = lambda model, **kw: ('instance', model, tuple(kw.get('indices') or ()), kw.get('transform'))
ff = P('front_top_flank_face', lambda: enc.front_top_flank_face())
west, east = ff[0], ff[1]
ref2 = types.SimpleNamespace(
    summaries=[{'name': 'coil-v-f'}, {'name': 'valve-v-f/1'}, {'name': 'valve-v-f'}, {'name': 'coil-v-i'},
               {'name': 'valve-v-i'}, {'name': 'coil-v-f/x'}, {'name': 'coil-v-f/2'}],
    raw_bounds={'coil-v-f': ((east - 6.0, 10.0, 20.0), (east + 2.0, 30.0, 40.0)),
                'valve-v-f': ((east - 20.0, 12.0, 22.0), (east + 1.0, 28.0, 38.0)),
                'coil-v-i': ((west - 2.0, -30.0, 20.0), (west + 6.0, -10.0, 40.0)),
                'valve-v-i': ((west - 1.0, -28.0, 22.0), (west + 20.0, -12.0, 38.0))},
    model='m')
P('front_flank_reliefs_fine fake', lambda: ea.front_flank_reliefs_fine(ref2))
P('front_flank_reliefs_fine fake transform', lambda: ea.front_flank_reliefs_fine(ref2, transform=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0))))
P('front_flank_reliefs_fine empty', lambda: ea.front_flank_reliefs_fine(types.SimpleNamespace(**{**vars(ref2), 'model': 'empty'})))
ref3 = types.SimpleNamespace(**{**vars(ref2), 'raw_bounds': {**ref2.raw_bounds,
                                                            'coil-v-f': ((east + 30.0, 10.0, 20.0), (east + 40.0, 30.0, 40.0))}})
P('front_flank_reliefs_fine wall', lambda: ea.front_flank_reliefs_fine(ref3))
P('front_flank_reliefs_fine positional transform', lambda: ea.front_flank_reliefs_fine(ref2, None))
reading = types.SimpleNamespace(summaries=[{'name': 'a'}, {'name': 'b'}, {'name': 'a'}], model='m')
P('manifold_references fake', lambda: ea.manifold_references(types.SimpleNamespace(manifold_reading=reading)))

# --- the namespace after the calls ----------------------------------------------------------
for n in ('SEATS', 'BOUNDS', '_ROUTED', 'STANDALONE', 'TUBE_ANCHOR_SITES', 'CEILING_RELIEF_LEVEL_GROUPS'):
    P('after:' + n, lambda n=n: C.get(n))
P('names after', lambda: C.names())
rec('cad modules', sorted(m for m in sys.modules if m.split('.')[0] in ('cadquery', 'OCP')))
rec('done', True)
