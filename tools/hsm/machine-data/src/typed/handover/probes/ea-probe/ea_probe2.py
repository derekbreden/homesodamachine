"""Second differential probe: the cold-core anchor and cradle tables are empty in the current
design, so this one installs synthetic tables (and the foam readers that answer for them) BEFORE
the module initializes, then drives the readers that walk them.  usage: ea_probe2.py <out.jsonl>"""
import collections, json, math, os, sys, types
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(_HERE, 'ea_probe.py')).read().split(
    "sys.path.insert(0, os.path.abspath('hardware/manifold-layout'))")[0])

sys.path.append(os.path.abspath('hardware/printed-parts/cold-core'))
sys.path.append(os.path.abspath('hardware/printed-parts/cold-core/foam-assembly'))
import _cold_core_interface as cci  # noqa: E402
import foam_assembly as foam  # noqa: E402

NS = types.SimpleNamespace
cci.cap_cradles = {'valve-v-zz1': NS(centre=(10.0, 20.0), yaw=0.0, seat=5.0),
                   'valve-v-zz2': NS(centre=(30.0, -20.0), yaw=90.0, seat=5.5),
                   'valve-v-zz3': NS(centre=(-40.0, 0.0), yaw=0.0, seat=4.0)}
cci.cap_anchors = {'probe-1': NS(seat_r=3.3, closure='cap', centre=(1.0, 2.0)),
                   'probe-2': NS(seat_r=2.0, closure='tie', centre=(5.0, 6.0)),
                   'probe-3': NS(seat_r=4.1, closure='cap', centre=(7.0, 8.0))}
cci.cap_side_anchors = {'probe-s': NS(seat_r=3.0, over_face=12.0),
                        'probe-t': NS(seat_r=2.5, over_face=6.5)}
_axis_over = {'probe-1': 7.5, 'probe-2': 8.25, 'probe-3': 6}
cci.cap_anchor_axis_over_face = lambda name: _axis_over[name]
cci.cap_anchor_len = 12.0
_stations = {'probe-1': (10.0, 20.0), 'probe-2': (-15.0, 5.0), 'probe-3': (0.5, -60.25)}
foam.cap_anchor_station = lambda name: _stations[name]
_side = {'probe-s': (40.0, -30.0), 'probe-t': (-20.0, 35.5)}
foam.cap_side_anchor_station = lambda name: _side[name]
foam.cap_conduit_mouth = lambda name: ((1.0, 2.0, 3.0), (0.0, 0.0, 1.0)) if name in _stations else _stations[name]

sys.path.insert(0, os.path.abspath('hardware/manifold-layout'))
import enclosure_assembly as ea  # noqa: E402

C = ea._compiled
P = probe
P('names', lambda: C.names())
for n in ('STANDALONE', '_ROUTED', 'TUBE_ANCHOR_CLOSURES'):
    P('get:' + n, lambda n=n: C.get(n))
import _boxes  # noqa: E402
_boxes.boxed = lambda shape: shape

for nm in ('valve-v-zz1', 'valve-v-zz4', 'anchor-cap-probe-1', 'anchor-cap-probe-2', 'anchor-cap-probe-3'):
    P('_tray_valve ' + nm, lambda nm=nm: ea._tray_valve(nm))
    P('_manifold ' + nm, lambda nm=nm: ea._manifold(nm))
foam_box = fb(0.0, 0.0, 100.0, 300.0, 300.0, 240.0)
placed = {'valve-v-zz1': fb(10.0, 20.0, 230.0, 30.0, 10.0, 12.0),
          'valve-v-zz2': fb(-20.0, 30.0, 232.0, 10.0, 30.0, 12.0),
          'valve-v-zz3': fb(0.0, 40.0, 226.6, 12.0, 12.0, 12.0)}
for label, carry in (('ident', ident), ('yaw', yaw), ('shifted', shifted(10.0, -20.0, 5.0))):
    rows = P('cradle_rows ' + label, lambda carry=carry: ea.cradle_rows(foam_box, carry, placed))
    if rows:
        P('cradles_land ' + label, lambda rows=rows: ea.cradles_land(rows))
P('cradle_rows missing', lambda: ea.cradle_rows(foam_box, ident, {'valve-v-zz1': placed['valve-v-zz1']}))
for nm in _stations:
    P('cap_anchor ' + nm, lambda nm=nm: ea.cap_anchor(nm))
    P('cap_conduit ' + nm, lambda nm=nm: ea.cap_conduit(nm))
for nm in _side:
    P('cap_side_anchor ' + nm, lambda nm=nm: ea.cap_side_anchor(nm))

Run = collections.namedtuple('Run', 'id pts radii bends diam')
slip = ea.CHAIN_SEAT_SLIP
for label, foam_carry in (('ident', ident), ('yaw', yaw), ('shifted', shifted(10.0, -20.0, 5.0))):
    runs = []
    for k, nm in enumerate(_stations):
        mid = foam_carry(ea.cap_anchor(nm))[0]
        u = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.6, 0.8, 0.0)][k]
        runs.append(Run(nm, [tuple(m - 50.0 for m in mid), tuple(m - 20.0 * c for m, c in zip(mid, u)),
                             tuple(m + 30.0 * c for m, c in zip(mid, u))], {}, [], 4.0))
    for k, nm in enumerate(_side):
        mid = foam_carry(ea.cap_side_anchor(nm))[0]
        runs.append(Run(nm, [tuple(mid[i] - (8.0 if i == k else 0.0) for i in range(3)),
                             tuple(mid[i] + (8.0 if i == k else 0.0) for i in range(3)),
                             tuple(mid[i] + (8.0 if i == k else 0.0) + (5.0 if i == 2 else 0.0) for i in range(3))],
                        {}, [], 4.0))
    P('cap_tube_anchors ' + label, lambda fc=foam_carry, runs=runs: ea.cap_tube_anchors(fc, runs))
    P('lid_cap_stations ' + label, lambda fc=foam_carry, runs=runs: ea.lid_cap_stations(fc, runs))
    P('cap_tube_anchors some ' + label, lambda fc=foam_carry, runs=runs: ea.cap_tube_anchors(fc, runs[1:2] + runs[4:]))
    P('cap_tube_anchors side miss ' + label, lambda fc=foam_carry, runs=runs: ea.cap_tube_anchors(
        fc, runs[:3] + [runs[3]._replace(pts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])]))
    P('lid_cap_stations miss ' + label, lambda fc=foam_carry, runs=runs: ea.lid_cap_stations(
        fc, [runs[2]._replace(pts=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])]))
    P('unsupported_spans caps ' + label, lambda fc=foam_carry, runs=runs: ea.unsupported_spans(runs, ea.cap_tube_anchors(fc, runs)))
    P('stand_anchors caps ' + label, lambda fc=foam_carry, runs=runs: ea.stand_anchors(ea.cap_tube_anchors(fc, runs)))
    mods = []
    for k, nm in enumerate(_stations):
        axis = foam_carry(ea.cap_anchor(nm))[0]
        tip = tuple(a - (20.0 + 15.0 * k) for a in axis[:1]) + tuple(axis[1:])
        outlet = (tip[0] + 100.0,) + tuple(tip[1:])
        seat_r = cci.cap_anchors[nm].seat_r
        sections = [
            [('thin', 2.0, 0.0, 30.0), ('fill', seat_r - slip, 10.0, 60.0), ('fat', seat_r + 1.0, 55.0, 100.0)],
            [('fat', seat_r + 1.0, 0.0, 100.0)],
            [('thin', 0.5, 0.0, 5.0)],
        ][k]
        mods.append((nm, (lambda st: (tuple(st[0]), tuple(st[1]))),
                     NS(inlet=lambda tip=tip: (tip, (1.0, 0.0, 0.0)), outlet=lambda outlet=outlet: (outlet, (1.0, 0.0, 0.0)),
                        sections=lambda sections=sections: sections)))
    bodies = {nm: (carry, mod) for nm, carry, mod in mods}
    P('anchor_rows ' + label, lambda fc=foam_carry, bodies=bodies: ea.anchor_rows(fc, bodies))
    P('anchor_rows partial ' + label, lambda fc=foam_carry, bodies=bodies: ea.anchor_rows(fc, {'probe-2': bodies['probe-2']}))
P('after:STANDALONE', lambda: C.get('STANDALONE'))
rec('done', True)
