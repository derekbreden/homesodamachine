"""The above-core arrangement rebuilt from the rear ports inward, hardest part to place first.

Each part goes where it has to be and is measured against what is already placed; nothing is
routed before its turn. Placed so far, on back-top's port corner cut down to its walls:

- the PISCO regulator, its long-neck inlet through a hole of its own at the CO2 station;
- the scanned threaded ASSE chain on TAP, out of its PP061208W on a stub of tube into a JG PP0208E
  union tee;
- the four remaining bulkheads, dropped with the grid;
- the label tiles, in channels between side rails;
- the DIGITEN meter, straight into the soda bulkhead with no tube showing, larger side down;
- the meter's inlet turned straight down by production's bend holder, foam and tube, to the
  cold-core cap's face;
- V-K, the stem elbow into its top port and its wall, as production stands them, moved with the
  tee; the wall reaches the side wall instead of the cap, and the stub is the shortest that stands
  V-K clear of the soda inlet;
- the G Ganen carbonator pump, where production stands it on the cap, without its elbows;
- the neoFit ACVUS-44 stem check valve in the Pisco's outlet;
- the CO2 tube, off the check's socket in one bend, then an S onto the cap between V-K and the
  pump, and straight down past the carbonator's rim;
- a seat on back-top for each of the ASSE chain, the Pisco and the meter, and a snap cap that holds
  each in its seat (slide_seats.py).

Back-top is today's piece with its six old bores plugged, both roof pockets filled back to the
full roof, the clamping land carried down to the dropped bottom nuts, the new bores, each column's
chip pockets opened into one channel, and no mounting brackets. It is cropped to the port corner,
CROP.

Writes the scenes page.json draws into hardware/assembly/scenes/out/, the measurements to
study.json, and their figures into README.md.

    tools/cad-venv/bin/python hardware/manifold-layout/studies/rear-port-rebuild/study.py
"""
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
for p in ('scripts', 'manifold-layout', 'printed-parts/cadlib', 'reference/asse1022-threaded-chain',
          'reference/jg-pp0208e-tee', 'reference/jg-pp061208w', 'reference/neofit-acvus44-check',
          'reference/neofit-stem-elbow',
          'cold-core-layout', 'printed-parts/cold-core', 'printed-parts/cold-core/foam-assembly'):
    sys.path.insert(0, str(HW / p))

import cadquery as cq  # noqa: E402
from OCP.BRepAdaptor import BRepAdaptor_Surface  # noqa: E402
from OCP.gp import gp_Trsf  # noqa: E402
import above_core as layout  # noqa: E402
import above_core_parts as acp  # noqa: E402
import asse1022_threaded_chain as tc  # noqa: E402
import cold_core_assembly as cca  # noqa: E402
import fits  # noqa: E402
import jg_pp0208e_tee as union_tee  # noqa: E402
import jg_pp061208w as reducer_ref  # noqa: E402
import neofit_acvus44_check as acvus  # noqa: E402
import neofit_stem_elbow as stem_elbow  # noqa: E402
import slide_seats  # noqa: E402
import soda_inlet  # noqa: E402
import _above_core_mounts as mounts  # noqa: E402
import valve_seat  # noqa: E402
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import (M_ALUMINIUM, M_JG_BLACK_PP, M_JG_GREY_ACETAL, M_MOULDED_BLACK,  # noqa: E402
                        M_NEOFIT_WHITE_ACETAL, M_NITRILE_BLACK, M_PETGF_BLACK)
from _routing import SPOOLS  # noqa: E402

OUT = HW / 'assembly' / 'scenes' / 'out'
facts = json.load(open(HW / 'manifold-layout' / 'enclosure-assembly.facts.json'))
MOUTH_Y = facts['card_ports']['bulkhead-water']['outboard']['pos'][1]
ROW_OLD = facts['card_ports']['bulkhead-water']['outboard']['pos'][2]
PITCH = 32.0
ROWS = (328.0, 296.0, 264.0)
ROWS_OLD = (ROW_OLD, ROW_OLD - PITCH, ROW_OLD - 2 * PITCH)
GRID_DROP = ROW_OLD - ROWS[0]
X_W, X_E = 37.25, 77.5
CEILING = 346.0                                       # the 9 mm roof's inner face
WALL_IN, FLOOR_Y, FACE_Y = 465.3, 469.3, 471.3        # land inner face, chip floor, flange plane
SIDE_WALL_X = 98.5                                    # the east side wall's inner face
CROP = cq.Solid.makeBox(108., 474. - 285., 356. - 230., cq.Vector(0., 285., 230.))
CAP_Z = facts['faces']['foam-assembly.cap']

# --- the scanned chain on TAP -------------------------------------------------------------------
ports = tc.ports()
t = gp_Trsf()
t.SetValues(0, 0, 1, X_W - tc.bfp.BODY_CENTER_Z, -1, 0, 0, MOUTH_Y + ports['inlet'][0][0], 0, -1, 0, ROWS[0])
TO_WORLD = cq.Location(t)
native = tc.parts()
names = {'pp010822e': 'jg-pp010822e', 'gagira': 'gagira-coupling', 'multiplex-asse1022': 'multiplex-asse1022',
         'pi4512f6s': 'jg-pi4512f6s', 'pp061208w': 'jg-pp061208w'}
parts = {names[k]: (native[k].moved(TO_WORLD), tc.COLORS[k]) for k in names}
tap_axis = cq.Vertex.makeVertex(*ports['inlet'][0]).moved(TO_WORLD).Center()

# --- the Pisco: native +Z (flow) runs world -Y, its inlet release face on the mouth plane --------
dims = json.load(open(HW / 'reference/compact-inline-candidates/dimensions.json'))['pisco_rvfup_quarter']
ranges = dims['fitted_exterior']['component_ranges_mm']
t = gp_Trsf()
t.SetValues(1, 0, 0, X_E, 0, 0, -1, MOUTH_Y, 0, 1, 0, ROWS[0])
COLOURS = {'inlet_collet': M_JG_GREY_ACETAL, 'body': M_MOULDED_BLACK,
           'outlet_fitting': M_ALUMINIUM, 'outlet_collet': M_JG_GREY_ACETAL}
pisco_native = {}
for solid in acp.native_reference('gas-regulator').Solids():
    key = next(k for k, (lo, hi) in ranges.items() if lo <= solid.Center().z <= hi)
    pisco_native[key] = solid
    parts['pisco-' + key.replace('_', '-')] = (solid.moved(cq.Location(t)), COLOURS[key])
PISCO = [n for n in parts if n.startswith('pisco-')]
# The ACVUS-44's stem in the Pisco's outlet, its collar on the outlet's release face; its +X runs
# with the Pisco's flow.
check_tip = dims['ports']['outlet']['point_mm'][2] - acvus.SHOULDER
t2 = gp_Trsf()
t2.SetValues(0, 1, 0, X_E, -1, 0, 0, MOUTH_Y - check_tip, 0, 0, 1, ROWS[0])
parts['co2-check'] = (acvus.build().moved(cq.Location(t2)), M_NEOFIT_WHITE_ACETAL)
# Its hole is one slip (enclosure_assembly.PORT_HOLE_SLIP) over the widest of what passes it.
vs = np.array([(v.x, v.y, v.z) for s in pisco_native.values() for v in s.tessellate(0.01, 0.1)[0]])
through = vs[vs[:, 2] <= MOUTH_Y - WALL_IN]
PISCO_HOLE = 2. * np.hypot(through[:, 0], through[:, 1]).max() + 2. * fits.slip

# --- the four remaining bulkheads, dropped with the grid ------------------------------------
comps = acp.components()
down = cq.Location(cq.Vector(0., 0., -GRID_DROP))
for name in ('bulkhead-carb', 'bulkhead-drain', 'bulkhead-flavor-a', 'bulkhead-flavor-b'):
    for n in (name, name + '-nut'):
        solid, colour, _ = comps[n]
        parts[n] = (solid.moved(down), colour)

# --- back-top ---------------------------------------------------------------------------------
back = import_step(str(HW / 'printed-parts/enclosure/enclosure/enclosure-back-top.step')).val()
OLD = {'tap': (X_W, 0, 17.44), 'over': (X_W, 1, 15.3), 'flavor-b': (X_W, 2, 15.3),
       'co2': (X_E, 0, 17.3), 'soda': (X_E, 1, 17.44), 'flavor-a': (X_E, 2, 15.3)}
# TAP is a plain hole for the scanned PP010822E, and its tile is bored the same way: each clears
# what that fitting puts through it, on the fitting's own axis, one slip each side.
CLEAR, HALF, CHIP_T = 0.15, 16.0, 1.8
pp = parts['jg-pp010822e'][0]
vs = np.array([(v.x, v.y, v.z) for v in pp.tessellate(0.01, 0.1)[0]])


def bore_over(y0, y1):
    band = vs[(vs[:, 1] >= y0 - 0.05) & (vs[:, 1] <= y1 + 0.05)]
    return 2. * np.hypot(band[:, 0] - tap_axis.x, band[:, 2] - tap_axis.z).max() + 2. * CLEAR


TAP_HOLE, TAP_BORE = bore_over(WALL_IN, FLOOR_Y), bore_over(FLOOR_Y, FLOOR_Y + CHIP_T)
NEW = {k: (x, ROWS[row], d) for k, (x, row, d) in OLD.items()}
NEW['co2'] = (X_E, ROWS[0], PISCO_HOLE)
NEW['tap'] = (tap_axis.x, tap_axis.z, TAP_HOLE)
for x, row, d in OLD.values():
    back = back.fuse(cq.Solid.makeCylinder(d / 2. + 0.05, FACE_Y - WALL_IN, cq.Vector(x, WALL_IN, ROWS_OLD[row]),
                                           cq.Vector(0., 1., 0.)))
# Both 6 mm roof pockets back to the full 9 mm roof.
for x0, x1, y0 in ((24., 50., 321.), (64., 91., 310.)):
    back = back.fuse(cq.Solid.makeBox(x1 - x0 + 0.2, WALL_IN - y0 + 0.15, 6.1, cq.Vector(x0 - 0.1, y0 - 0.1, CEILING - 0.05)))
# The 6 mm land carried down to the dropped bottom nuts.
back = back.cut(cq.Solid.makeBox(67., 3.3, 16., cq.Vector(24., 462.0, ROWS[2] - 14.0)))
for x, z, d in NEW.values():
    back = back.cut(cq.Solid.makeCylinder(d / 2., 20., cq.Vector(x, 455., z), cq.Vector(0., 1., 0.)))
STOP_Z = ROWS[2] - 12.0                                # the bottom tiles' seat
# The channel floor stands 1 um under today's pocket floors: coplanar, the cut leaves slabs behind.
for x in (X_W, X_E):
    back = back.cut(cq.Solid.makeBox(2 * (HALF + CLEAR), 3.5, 357. - STOP_Z,
                                     cq.Vector(x - HALF - CLEAR, FLOOR_Y - 0.001, STOP_Z)))
back = back.intersect(CROP).clean()
# No mounting brackets: everything inside the ceiling, rear-wall and side-wall planes goes, except
# the fillet where the side wall meets the rear wall.
inside = cq.Solid.makeBox(SIDE_WALL_X, 462.3 - 285., CEILING - 230., cq.Vector(0., 285., 230.))
fillet = [s for s in back.intersect(inside).Solids() if s.BoundingBox().xmin > 94.]
back = back.cut(inside)
for s in fillet:
    back = back.fuse(s)
back = back.clean()
# Side rails only: the bottom tiles stand on the floor of their channel.
LIP_T, OVER, LAND = 1.6, 2.0, 2.0                      # rail thickness, overhang on the tile, land on the wall
rails = [(X_W - HALF - CLEAR - LAND, X_W - HALF + OVER), (X_W + HALF - OVER, X_E - HALF + OVER),
         (X_E + HALF - OVER, X_E + HALF + CLEAR + LAND)]
for i, (x0, x1) in enumerate(rails):
    parts[f'face-rail-{i + 1}'] = (cq.Solid.makeBox(x1 - x0, LIP_T, 355. - STOP_Z, cq.Vector(x0, FACE_Y, STOP_Z)),
                                   M_PETGF_BLACK)
parts['enclosure-back-top'] = (back, M_PETGF_BLACK)

# --- the flow meter, straight into the soda bulkhead with no tube showing ---------------------
# Its outlet collet face meets the union's inboard collet face on one axis; native +Z (the side
# the round housing stands off the port axis) turns down.
meter = acp._module('above_core_digiten', 'reference/digiten-flow-sensor/digiten_flow_sensor.py')
soda_in = facts['card_ports']['bulkhead-carb']['tube-in']['pos']
t = gp_Trsf()
t.SetValues(0, 1, 0, soda_in[0], 1, 0, 0, soda_in[1] - meter.outlet()[0][0], 0, 0, -1, soda_in[2] - GRID_DROP)
METER = cq.Location(t)
parts['digiten-flow'] = (acp.native_reference('digiten-flow').moved(METER), acp.C_DIGITEN)

# --- the soda inlet, turned straight down at the meter's inlet ----------------------------------
# Production's continuous inlet (soda_inlet.plan) laid off this meter's mouth: the holder its gap
# off the meter, its leg, the bend, and a straight drop to the cap's face. One piece of foam runs
# from just over the cap to just short of the meter, as production cuts it.
sel = layout.specification()['soda_inlet']
H = sel['holder']
BEND_R = H['centreline_bend_r_mm']
mouth = np.array(cq.Vertex.makeVertex(*meter.inlet()[0]).moved(METER).Center().toTuple())
fwd, up = np.array([0., 1., 0.]), np.array([0., 0., 1.])     # flow into the meter, and up
end = mouth - fwd * (H['leg_mm'] + sel['holder_to_meter_mm'])
centre = end - up * BEND_R
start = centre - fwd * BEND_R
middle = centre + (up - fwd) * BEND_R / math.sqrt(2.)
low = np.array([start[0], start[1], CAP_Z])
inserted = mouth + fwd * sel['meter_insertion_estimate_mm']


def seg(kind, *points):
    return {'kind': kind, 'points_mm': [[float(c) for c in p] for p in points]}


arc = seg('arc', start, middle, end)
tube = soda_inlet.sweep([seg('line', low, start), arc, seg('line', end, inserted)],
                        sel['tube_od_mm'] / 2., sel['tube_id_mm'] / 2.)
foam = soda_inlet.sweep([seg('line', low + up * sel['foam']['start_above_guide_mm'], start), arc,
                         seg('line', end, mouth - fwd * sel['foam']['end_before_meter_mm'])],
                        sel['foam']['stock_od_mm'] / 2., sel['foam']['stock_id_mm'] / 2.)
xaxis = -fwd
zaxis = np.array([xaxis[1], -xaxis[0], 0.])
holder = soda_inlet.holder_native().moved(layout.frame_location({
    'rotation': [[xaxis[i], up[i], zaxis[i]] for i in range(3)],
    'translation_mm': [float(c) for c in centre - zaxis * (H['wall_mm'] + H['channel_d_mm'] / 2.)]}))
parts['soda-tube'] = (tube, cq.Color(*(c / 255. for c in SPOOLS['blue'].rgb)))
parts['soda-bend-holder'] = (holder, M_PETGF_BLACK)
parts['soda-insulation'] = (foam.cut(holder).clean(), M_NITRILE_BLACK)
SODA = ('soda-tube', 'soda-bend-holder', 'soda-insulation')

CLOUDS = {}


def pts(shape, step=0.3):
    """Points over the shape's surface, `step` apart, kept for the next ask. A shape of thousands
    of faces, the pump's scanned envelope, tessellates coarsely and is sampled 0.5 mm apart by area
    alone, without its vertices."""
    heavy = len(shape.Faces()) > 5000
    step = max(step, 0.5) if heavy else step
    key = (id(shape), step)
    if key in CLOUDS:
        return CLOUDS[key]
    vs, ts = shape.tessellate(0.2, 0.5) if heavy else shape.tessellate(0.03, 0.1)
    vs = np.array([(q.x, q.y, q.z) for q in vs])
    tri = vs[np.array(ts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    rng = np.random.default_rng(1)
    n = (np.floor(area / step ** 2 + rng.random(len(area))) if heavy else np.ceil(area / step ** 2)).astype(int)
    i = np.repeat(np.arange(len(tri)), n)
    r1, r2 = np.sqrt(rng.random(len(i)))[:, None], rng.random(len(i))[:, None]
    cloud = (1 - r1) * a[i] + r1 * (1 - r2) * b[i] + r1 * r2 * c[i]
    CLOUDS[key] = cloud if heavy else np.concatenate([cloud, vs])
    return CLOUDS[key]


TREES = {}


def tree(shape, step=0.4):
    cloud = pts(shape, step)
    if id(cloud) not in TREES:
        TREES[id(cloud)] = cKDTree(cloud)
    return TREES[id(cloud)]


# --- the water split: a JG PP0208E union tee on a stub of tube out of the PP061208W -------------
# A stub of 1/4" tube runs from the reducer's collet into the union tee's branch, and the tee's run
# stands square to it, east-west.
reducer = tc.parameters()['pp061208w']


def chain_point(record, x):
    return np.array(tc.placed(cq.Vertex.makeVertex(x, 0., 0.), record).moved(TO_WORLD).Center().toTuple())


nose = chain_point(reducer, reducer['visible_axial_range_mm'][1])     # the reducer's 1/4" collet face
flow = chain_point(reducer, reducer['visible_axial_range_mm'][1] + 1.) - nose
east = np.array([1., 0., 0.]) - flow * flow[0]
east /= np.linalg.norm(east)


def tee_centre(stub):
    return nose + flow * (stub + union_tee.REACH)


# --- V-K, its stem elbow and its wall, as production stands them, moved with the tee ------------
# Production stands V-K on tee-fold's stem and presses V-K's posts into an upright wall rooted on
# the cap. All three move together until tee-fold's release face, from its reference, is on the
# union tee's east collet face; the wall reaches the side wall instead of the cap.
fold_face, fold_axis = comps['tee-fold'][2](stem_elbow.socket())


def vk_shift(stub):
    return tee_centre(stub) + east * union_tee.REACH - np.array(fold_face)


seat = mounts.valve_support_datums('vk-solenoid')
lo, hi = seat['bearing_min_world_mm'], seat['bearing_max_world_mm']
at_vk = layout.location('vk-solenoid')
wall = cq.Solid.makeBox(*(hi[i] - lo[i] for i in range(3)), cq.Vector(*lo)).cut(
    valve_seat.build_sockets().val().moved(at_vk),
    valve_seat.build_port_channel(2. * valve_seat.seat_half_y + 2.).val().moved(at_vk))
# The stub is the shortest, in half millimetres, that stands the group VK_CLEAR off the soda inlet.
VK_CLEAR = 1.0
group = np.concatenate([pts(comps['vk-solenoid'][0]), pts(comps['tee-fold'][0]), pts(wall)])
inlet = cKDTree(np.concatenate([pts(parts[n][0], 0.4) for n in SODA]))
STUB = next(float(s) for s in np.arange(0., 30.01, 0.5) if inlet.query(group + vk_shift(s))[0].min() >= VK_CLEAR)
SHIFT = vk_shift(STUB)
MOVE = cq.Location(cq.Vector(*SHIFT))
for n in ('vk-solenoid', 'tee-fold'):
    parts[n] = (comps[n][0].moved(MOVE), comps[n][1])
arm = cq.Solid.makeBox(SIDE_WALL_X - hi[0] - SHIFT[0], hi[1] - lo[1], hi[2] - lo[2],
                       cq.Vector(hi[0] + SHIFT[0], lo[1] + SHIFT[1], lo[2] + SHIFT[2]))
parts['vk-wall'] = (wall.moved(MOVE).fuse(arm).clean(), M_PETGF_BLACK)
VK = ('vk-solenoid', 'tee-fold', 'vk-wall')
tee_at = tee_centre(STUB)
tee_x = np.cross(-flow, east)                      # the tee's run on its Z, its branch on its +Y
parts['jg-pp0208e'] = (union_tee.build_jg_pp0208e_tee().val().moved(layout.frame_location({
    'rotation': [[tee_x[i], -flow[i], east[i]] for i in range(3)],
    'translation_mm': [float(c) for c in tee_at]})), M_JG_BLACK_PP)
stub_from = nose - flow * reducer_ref.TUBE_INSERTION_DEPTH
stub_len = reducer_ref.TUBE_INSERTION_DEPTH + STUB + union_tee.INSERTION
parts['water-split-stub'] = (cq.Solid.makeCylinder(sel['tube_od_mm'] / 2., stub_len, cq.Vector(*stub_from), cq.Vector(*flow))
                             .cut(cq.Solid.makeCylinder(sel['tube_id_mm'] / 2., stub_len, cq.Vector(*stub_from),
                                                        cq.Vector(*flow))),
                             cq.Color(*(c / 255. for c in SPOOLS['white'].rgb)))

# --- the carbonator pump, where production stands it on the cap, without its elbows -------------
parts['g-ganen-pump'] = comps['g-ganen-pump'][:2]

# --- the cold core, where the machine stands it, for the drop below the cap ----------------------
# The core builds in foam-assembly's frame; the machine turns that frame a quarter about +Z and
# stands it on the foam assembly's box in the facts.
yaw = cq.Location(cq.Vector(), cq.Vector(0., 0., 1.), 90.)
fb = import_step(str(HW / 'printed-parts/cold-core/foam-assembly/foam-assembly.step')).val().moved(yaw).BoundingBox()
wb = facts['bodies']['foam-assembly']
CORE = cq.Location(cq.Vector(wb[0] - fb.xmin, wb[1] - fb.ymin, wb[2] - fb.zmin)) * yaw
core = {n: (s.val() if hasattr(s, 'val') else s).moved(CORE) for n, s in cca.build_bodies().items()}

# --- label tiles --------------------------------------------------------------------------------
WHITE, BLUE = cq.Color(0.92, 0.92, 0.90), cq.Color(0.16, 0.36, 0.76)
RED, BLACK = cq.Color(0.78, 0.12, 0.12), cq.Color(0.10, 0.10, 0.11)
TILES = {  # name: (x, row, bore, bore centre, colour, word, word colour)
    'tile-flavor-b': (X_W, 2, 15.3, None, BLACK, 'FLAVOR', WHITE),
    'tile-flavor-a': (X_E, 2, 15.3, None, BLACK, 'FLAVOR', WHITE),
    'tile-over': (X_W, 1, 15.3, None, WHITE, 'OVER', BLACK),
    'tile-soda': (X_E, 1, 17.44, None, BLUE, 'SODA', WHITE),
    'tile-tap': (X_W, 0, TAP_BORE, (tap_axis.x, tap_axis.z), WHITE, 'TAP', BLACK),
    'tile-co2': (X_E, 0, PISCO_HOLE, None, RED, 'CO2', WHITE),
}
for name, (x, row, bore, centre_xz, colour, text, ink) in TILES.items():
    z0, z1 = ROWS[row] - 12.0, (355.0 if row == 0 else ROWS[row] + 19.8)
    cx, cz = centre_xz or (x, ROWS[row])
    tile = cq.Solid.makeBox(2 * HALF, CHIP_T, z1 - z0, cq.Vector(x - HALF, FLOOR_Y, z0)).cut(
        cq.Solid.makeCylinder(bore / 2., 10., cq.Vector(cx, 465., cz), cq.Vector(0., 1., 0.)))
    parts[name] = (tile, colour)
    plane = cq.Plane(origin=(0., FLOOR_Y + CHIP_T, 0.), xDir=(-1., 0., 0.), normal=(0., 1., 0.))
    word = cq.Workplane(plane).center(-x, (ROWS[row] + 12.0 + z1) / 2.).text(
        text, 5.0, 0.48, halign='center', valign='center', font='Helvetica', kind='bold').val()
    parts[name + '-word'] = (word, ink)

# --- the seats on back-top, and the snap caps that hold the parts in them ------------------------
# With back-top inverted on the bench, the ASSE chain, the Pisco and the meter each slide aft into a
# seat, and a snap cap holds each there. The seats print as part of back-top; they are drawn apart
# from it until the scenes.
seated, seat_numbers = slide_seats.build(parts, (X_W, ROWS[0]), TO_WORLD, (X_E, ROWS[0]), MOUTH_Y, CEILING,
                                         WALL_IN, SIDE_WALL_X, meter, METER)
for n, s in seated.items():
    parts[n] = (s, M_PETGF_BLACK)
HOLDS = {'asse': slide_seats.CHAIN, 'pisco': (*PISCO, 'co2-check'), 'meter': ('digiten-flow',)}

# --- the CO2 tube, off the check's socket in one bend, then an S onto a straight past the rim ----
# The tube leaves the check's socket straight forward and turns down in one bend no tighter than
# CO2_BEND onto a straight drop. Of the bends that do, it is the shortest that stands CO2_GAP off
# every part. Under the cap the tube runs straight from the coil's top up to the floor, on the
# bend's drop pushed straight out from the carbonator's axis until the tube just touches the
# carbonator's rim. From the floor, the gentlest S that stands CO2_GAP off every part brings it
# onto the bend's foot.
CO2_BEND, CO2_GAP = 25.0, 3.0
co2_r = sel['tube_od_mm'] / 2.
check_mouth = MOUTH_Y - check_tip - acvus.LENGTH
co2_from = np.array([X_E, check_mouth, ROWS[0]])
neighbours = cKDTree(np.concatenate([pts(s, 0.4) for n, (s, _) in parts.items()
                                     if not n.startswith(('tile-', 'face-rail-', 'co2-check')) and not n.endswith('-word')]))
ts = np.linspace(0., 1., 81)[None, :, None]


def curve(c):
    """Samples, tightest radius and length of the cubic Beziers on control points c."""
    B = (1 - ts) ** 3 * c[0] + 3 * (1 - ts) ** 2 * ts * c[1] + 3 * (1 - ts) * ts ** 2 * c[2] + ts ** 3 * c[3]
    d1 = 3 * (1 - ts) ** 2 * (c[1] - c[0]) + 6 * (1 - ts) * ts * (c[2] - c[1]) + 3 * ts ** 2 * (c[3] - c[2])
    d2 = 6 * (1 - ts) * (c[2] - 2 * c[1] + c[0]) + 6 * ts * (c[3] - 2 * c[2] + c[1])
    k = np.linalg.norm(np.cross(d1, d2), axis=2) / np.linalg.norm(d1, axis=2) ** 3
    return B, 1. / k.max(1), np.linalg.norm(np.diff(B, axis=1), axis=2).sum(1)


def co2_route(top, a, b):
    """The bends off the socket onto a drop from `top`, for arrays of tangent lengths `a` off the socket
    and `b` onto the drop: (samples, tightest radius, length to the cap)."""
    a, b, top = np.asarray(a, float)[:, None, None], np.asarray(b, float)[:, None, None], np.asarray(top, float)
    B, radius, length = curve((co2_from, co2_from + a * np.array([0., -1., 0.]), top + b * up, top))
    return B, radius, length + top[2] - CAP_Z


def co2_length(v):
    """The route's length for v = (drop x, drop y, drop top z, a, b), or infinity where it bends tighter
    than CO2_BEND or comes within CO2_GAP of a part."""
    if v[2] < CAP_Z or v[3] <= 0. or v[4] <= 0.:
        return math.inf
    B, radius, length = co2_route(v[:3], [v[3]], [v[4]])
    drop = np.column_stack([np.full(40, v[0]), np.full(40, v[1]), np.linspace(v[2], CAP_Z, 40)])
    gap = neighbours.query(np.concatenate([B[0], drop]))[0].min() - co2_r
    return length[0] if radius[0] >= CO2_BEND and gap >= CO2_GAP else math.inf


# The shortest on a coarse grid, then walked shorter in halving steps.
ab = np.array(list(itertools.product(np.arange(5., 60.1, 5.), repeat=2)))
grid = []
for top in itertools.product(np.arange(40., 64.1, 2.), np.arange(292., 368.1, 4.), np.arange(CAP_Z, 316., 6.)):
    _, radius, length = co2_route(top, ab[:, 0], ab[:, 1])
    grid += [(length[i], *top, *ab[i]) for i in np.nonzero(radius >= CO2_BEND)[0]]
v = np.array(next(g[1:] for g in sorted(grid) if co2_length(g[1:]) < math.inf))
f, step = co2_length(v), np.array([1., 2., 3., 2.5, 2.5])
while step.max() > 0.05:
    for i, sign in itertools.product(range(5), (1., -1.)):
        w = v.copy()
        w[i] += sign * step[i]
        if (fw := co2_length(w)) < f - 1e-6:
            v, f = w, fw
            break
    else:
        step = step / 2.
co2_top, CO2_A, CO2_B = v[:3], float(v[3]), float(v[4])
co2_ctrl = (co2_from, co2_from + CO2_A * np.array([0., -1., 0.]), co2_top + CO2_B * up, co2_top)
_, r, n = curve(co2_ctrl)
co2_radius, co2_bend_len = float(r[0]), float(n[0])
# The carbonator's rim is its tube's outer cylinder, the largest; the straight stands a tube radius
# outside it, under the cap from the coil's top up.
carb_axis, carb_r = max(((np.array([c.Location().X(), c.Location().Y()]), c.Radius())
                         for c in (BRepAdaptor_Surface(f.wrapped).Cylinder() for f in core['carbonator-tube'].Faces()
                                   if f.geomType() == 'CYLINDER')), key=lambda ar: ar[1])
out = co2_top[:2] - carb_axis
co2_push = carb_r + co2_r - float(np.linalg.norm(out))
co2_land = np.array([*(carb_axis + out / np.linalg.norm(out) * (carb_r + co2_r)), CAP_Z])
co2_low = np.array([co2_land[0], co2_land[1], core['evap-coil'].BoundingBox().zmax])
pq = np.array(list(itertools.product(np.arange(1., 30.01, 0.25), repeat=2)))
S, r, n = curve((co2_land, co2_land + pq[:, 0, None, None] * up, co2_top - pq[:, 1, None, None] * up, co2_top))
i = next(i for i in np.argsort(-r) if neighbours.query(S[i])[0].min() - co2_r >= CO2_GAP)
CO2_P, CO2_Q = (float(q) for q in pq[i])
co2_s_radius, co2_len = float(r[i]), co2_bend_len + float(n[i])     # the S, and the tube from the socket to the floor
co2_s = (co2_top, co2_top - CO2_Q * up, co2_land + CO2_P * up, co2_land)
co2_end = co2_from + np.array([0., acvus.INSERTION, 0.])            # the tube's end in the check's socket
path = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*co2_end), cq.Vector(*co2_from)),
                              cq.Edge.makeBezier([cq.Vector(*q) for q in co2_ctrl]),
                              cq.Edge.makeBezier([cq.Vector(*q) for q in co2_s]),
                              cq.Edge.makeLine(cq.Vector(*co2_land), cq.Vector(*co2_low))])
ring = cq.Workplane(cq.Plane(origin=tuple(co2_end), xDir=(1., 0., 0.), normal=(0., -1., 0.))).circle(
    co2_r).circle(sel['tube_id_mm'] / 2.)
parts['co2-tube'] = (ring.sweep(path).val(), cq.Color(*(c / 255. for c in SPOOLS['red'].rgb)))

# --- measurements -----------------------------------------------------------------------------
result = {'rows_z': ROWS, 'grid_drop_mm': round(GRID_DROP, 3), 'tile_seat_z': STOP_Z,
          'tap_hole_d': round(TAP_HOLE, 3), 'tap_tile_bore_d': round(TAP_BORE, 3),
          'pisco_hole_d': round(PISCO_HOLE, 3)}
print(f'rows Z{ROWS}; grid drop {GRID_DROP:.3f}; tile seat Z{STOP_Z}; TAP hole d{TAP_HOLE:.2f}, tile bore '
      f'd{TAP_BORE:.2f}, on ({tap_axis.x:.2f}, {tap_axis.z:.2f}); Pisco bore d{PISCO_HOLE:.3f}')


def bbox(shape):
    b = shape.BoundingBox()
    return [round(v, 2) for v in (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)]


print('== exact overlaps (mm^3)')
overlaps = {}
names_all = [n for n in parts if not n.endswith('-word')]
# The pump meets a part in an exact boolean only where their sampled surfaces come within 0.5 mm.
pump_cloud = tree(parts['g-ganen-pump'][0], 0.5)
for i, a in enumerate(names_all):
    for b in names_all[i + 1:]:
        if a.startswith('pisco-') and b.startswith('pisco-'):
            continue
        if 'enclosure-back-top' in (a, b) and {a, b} & set(slide_seats.SEATS):
            continue
        sa, sb = parts[a][0], parts[b][0]
        ba, bb = sa.BoundingBox(), sb.BoundingBox()
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        if 'g-ganen-pump' in (a, b) and pump_cloud.query(pts(sb if a == 'g-ganen-pump' else sa, 0.5))[0].min() > 0.5:
            continue
        common = sa.intersect(sb)
        v = common.Volume()
        if v > 1e-3:
            overlaps[f'{a} x {b}'] = {'mm3': round(v, 3), 'bbox': bbox(common),
                                      'pieces': [bbox(x) for x in common.Solids()]}
            print(f'  {a} x {b}: {v:.3f} at {bbox(common)}')
result['overlaps'] = overlaps


def nearest(name, others, reach=15.):
    P = pts(parts[name][0])
    found = {}
    for n in others:
        d, _ = tree(parts[n][0]).query(P, k=1)
        j = d.argmin()
        if d[j] < reach:
            found[n] = round(float(d[j]), 2)
            print(f'  {n:28} {d[j]:6.2f} mm at ({P[j][0]:.1f}, {P[j][1]:.1f}, {P[j][2]:.1f})')
    return found


placed = [n for n in names_all if not n.startswith(('tile-', 'face-rail-'))]
print(f'== flow meter {bbox(parts["digiten-flow"][0])}; outlet collet face Y{soda_in[1]:.2f} on the soda '
      f'union\'s inboard collet face')
result['meter'] = {'bbox': bbox(parts['digiten-flow'][0]), 'inlet_mouth': [round(c, 3) for c in mouth],
                   'nearest_mm': nearest('digiten-flow', [n for n in placed if n != 'digiten-flow' and n not in SODA])}
P = np.concatenate([pts(parts[n][0]) for n in PISCO])
B = pts(back, 0.5)
print('== the Pisco to back-top (nearest, by region of back-top)')
result['pisco_to_back_top_mm'] = {}
for label, m in (('rear wall, the 6 mm field', (B[:, 1] > 460) & (B[:, 0] > 25) & (B[:, 0] < 90.5)),
                 ('ceiling', B[:, 2] > 345.5), ('east side wall', B[:, 0] > 95.),
                 ('9 mm stock east of the field', (B[:, 0] >= 90.5) & (B[:, 0] <= 95.) & (B[:, 1] > 455))):
    d, i = cKDTree(B[m]).query(P, k=1)
    j = d.argmin()
    result['pisco_to_back_top_mm'][label] = round(float(d[j]), 2)
    print(f'  {label:30} {d[j]:6.2f} mm at Pisco ({P[j][0]:.1f}, {P[j][1]:.1f}, {P[j][2]:.1f})')
for n in ('multiplex-asse1022', 'gagira-coupling'):
    top = parts[n][0].BoundingBox().zmax
    result[f'{n}_under_ceiling_mm'] = round(CEILING - top, 2)
    print(f'  {n} top Z{top:.2f}: {CEILING - top:.2f} under the ceiling')

print(f'== soda inlet: holder {sel["holder_to_meter_mm"]} mm off the meter mouth Y{mouth[1]:.2f}, bend centre '
      f'({centre[0]:.2f}, {centre[1]:.2f}, {centre[2]:.2f}); the drop comes down at X{start[0]:.2f} Y{start[1]:.2f} '
      f'from Z{start[2]:.2f} to the cap face Z{CAP_Z}')
# Carried on straight down past the cap face, the tube runs among the core's bodies; the foam it
# passes through is left out.
drop = cq.Solid.makeCylinder(sel['tube_od_mm'] / 2., CAP_Z, cq.Vector(start[0], start[1], 0.), cq.Vector(0., 0., 1.))
below = {}
for n, s in core.items():
    b = s.BoundingBox()
    if not n.startswith('foam-') and b.xmin - 30. < start[0] < b.xmax + 30. and b.ymin - 30. < start[1] < b.ymax + 30.:
        below[n] = round(drop.distance(s), 2)
below = dict(sorted(below.items(), key=lambda kv: kv[1]))
for n, d in below.items():
    print(f'  straight down past the cap: {n:32} {d:6.2f} mm')
soda = {'mouth': mouth, 'arc_end': end, 'bend_centre': centre, 'arc_start': start, 'on_cap': low}
result['soda_inlet'] = {k: [round(float(c), 3) for c in v] for k, v in soda.items()}
result['soda_inlet'].update({
    'straight_down_to_core_mm': below,
    'foam_length_mm': round(start[2] - low[2] - sel['foam']['start_above_guide_mm'] + BEND_R * math.pi / 2.
                            + H['leg_mm'] + sel['holder_to_meter_mm'] - sel['foam']['end_before_meter_mm'], 2),
    'bboxes': {n: bbox(parts[n][0]) for n in SODA}})
for n in SODA:
    print(f'== {n} {bbox(parts[n][0])}')
    result['soda_inlet'][f'{n}_nearest_mm'] = nearest(n, [m for m in placed if m not in SODA])
print(f'== water split: a {STUB:g} mm stub out of the reducer\'s collet face ({nose[0]:.2f}, {nose[1]:.2f}, '
      f'{nose[2]:.2f}); the union tee stands at ({tee_at[0]:.2f}, {tee_at[1]:.2f}, {tee_at[2]:.2f}); the tube is cut '
      f'{stub_len:.1f} mm')
result['water_split'] = {'stub_mm': STUB, 'stub_cut_mm': round(stub_len, 2),
                         'tee_centre': [round(float(c), 3) for c in tee_at],
                         'nearest_mm': {n: nearest(n, [m for m in placed if m not in ('jg-pp0208e', 'water-split-stub')])
                                        for n in ('jg-pp0208e', 'water-split-stub')}}
tee_mouth = tee_at + east * union_tee.REACH
tilt = math.degrees(math.acos(min(1., abs(float(np.dot(east, fold_axis))))))
vk_gap = float(inlet.query(group + SHIFT)[0].min())
print(f'== V-K, tee-fold and the wall moved ({SHIFT[0]:.2f}, {SHIFT[1]:.2f}, {SHIFT[2]:.2f}) to the tee\'s east run '
      f'mouth ({tee_mouth[0]:.2f}, {tee_mouth[1]:.2f}, {tee_mouth[2]:.2f}); tee-fold\'s socket is {tilt:.2f} deg off '
      f'the run; the arm out to the side wall is {SIDE_WALL_X - hi[0] - SHIFT[0]:.2f} mm; {vk_gap:.2f} mm off the soda inlet')
result['vk'] = {'shift_mm': [round(float(c), 3) for c in SHIFT], 'tee_east_mouth': [round(float(c), 3) for c in tee_mouth],
                'socket_tilt_deg': round(tilt, 2), 'arm_mm': round(SIDE_WALL_X - hi[0] - SHIFT[0], 2),
                'to_soda_inlet_mm': round(vk_gap, 2),
                'bboxes': {n: bbox(parts[n][0]) for n in VK}}
for n in VK:
    print(f'== {n} {bbox(parts[n][0])}')
    result['vk'][f'{n}_nearest_mm'] = nearest(n, [m for m in placed if m not in VK])
for n in ('g-ganen-pump', 'co2-check'):
    print(f'== {n} {bbox(parts[n][0])}')
    result[n] = {'bbox': bbox(parts[n][0]), 'nearest_mm': nearest(n, [m for m in placed if m != n])}
result['co2-check'].update({
    'socket_mouth_y': round(check_mouth, 2),
    'tip_short_of_tube_stop_mm': round(dims['ports']['outlet']['insertion_mm'] - acvus.SHOULDER, 2),
    'under_ceiling_mm': round(CEILING - parts['co2-check'][0].BoundingBox().zmax, 2)})
print(f'== the check\'s collar on the Pisco\'s outlet face Y{MOUTH_Y - check_tip - acvus.SHOULDER:.2f}, its stem tip '
      f'{result["co2-check"]["tip_short_of_tube_stop_mm"]} mm short of the tube stop, its socket mouth Y{check_mouth:.2f}')


# Under the cap, the straight against the core's bodies; the foam it passes through is left out.
straight = cq.Solid.makeCylinder(co2_r, CAP_Z - co2_low[2], cq.Vector(*co2_low), cq.Vector(0., 0., 1.))
co2_core = {}
for n, s in core.items():
    b = s.BoundingBox()
    if not n.startswith('foam-') and b.xmin - 30. < co2_land[0] < b.xmax + 30. and b.ymin - 30. < co2_land[1] < b.ymax + 30.:
        co2_core[n] = round(straight.distance(s), 2)
co2_core = dict(sorted(co2_core.items(), key=lambda kv: kv[1]))
result['co2_tube'] = {
    'from': [round(float(c), 3) for c in co2_from], 'bend_foot': [round(float(c), 3) for c in co2_top],
    'floor': [round(float(c), 3) for c in co2_land], 'low': [round(float(c), 3) for c in co2_low],
    'bend_tangents_mm': [round(CO2_A, 2), round(CO2_B, 2)], 'bend_radius_mm': round(co2_radius, 2),
    's_tangents_mm': [CO2_P, CO2_Q], 's_radius_mm': round(co2_s_radius, 2),
    'carbonator_axis': [round(float(c), 3) for c in carb_axis], 'carbonator_r': round(carb_r, 3),
    'pushed_out_mm': round(co2_push, 2), 'to_floor_mm': round(co2_len, 1),
    'straight_mm': round(CAP_Z - co2_low[2], 1), 'straight_to_core_mm': co2_core}
print(f'== CO2 tube: one bend off the check\'s socket mouth Y{check_mouth:.2f} onto its foot at ({co2_top[0]:.2f}, '
      f'{co2_top[1]:.2f}, {co2_top[2]:.1f}), tangents {CO2_A:.1f} and {CO2_B:.1f} mm, R{co2_radius:.1f} at its tightest; '
      f'an S onto the floor at X{co2_land[0]:.2f} Y{co2_land[1]:.2f}, {co2_push:.2f} mm out from under the foot, '
      f'tangents {CO2_P:g} and {CO2_Q:g} mm, R{co2_s_radius:.1f} at its tightest; {co2_len:.1f} mm to the floor, then '
      f'straight down {CAP_Z - co2_low[2]:.1f} mm to the coil\'s top')
for n, d in co2_core.items():
    print(f'  the straight under the cap: {n:32} {d:6.2f} mm')
result['co2_tube']['nearest_mm'] = nearest('co2-tube', [m for m in placed if m not in ('co2-tube', 'co2-check')])

# The seats and snap caps, exactly: each against the parts it holds, in place, along the slide and
# along the cap's way on; and the pump under them as back-top rides forward over the core, which in
# back-top's frame takes the pump through every station fore of its own.
print('== seats and snap caps')
result['seats'] = {'built_from': seat_numbers}
pump_pts = pts(parts['g-ganen-pump'][0], 0.5)
for n in slide_seats.SOLIDS:
    s = parts[n][0]
    b = s.BoundingBox()
    print(f'  {n:16} {len(s.Faces()):3d} faces, {s.Volume() / 1000.:5.2f} cm^3, {bbox(s)}')
    P = pump_pts[(pump_pts[:, 0] > b.xmin - 6.) & (pump_pts[:, 0] < b.xmax + 6.) & (pump_pts[:, 2] > b.zmin - 6.)
                 & (pump_pts[:, 2] < b.zmax + 6.)]
    ride = (math.inf, 0.)
    for t in np.arange(0., 160.01, 0.5):
        Q = P - np.array([0., t, 0.])
        Q = Q[(Q[:, 1] > b.ymin - 6.) & (Q[:, 1] < b.ymax + 6.)]
        if len(Q) and (d := float(tree(s, 0.2).query(Q)[0].min())) < ride[0]:
            ride = (d, float(t))
    if ride[0] < math.inf:
        print(f'    the pump rides past {ride[0]:.2f} mm off, {ride[1]:.1f} mm fore of its station')
    result['seats'][n] = {'bbox': bbox(s), 'faces': len(s.Faces()), 'cm3': round(s.Volume() / 1000., 2),
                          'pump_ride_mm': round(ride[0], 2) if ride[0] < math.inf else None, 'pump_ride_at_mm': ride[1],
                          'nearest_mm': nearest(n, [m for m in placed if m != n and not (
                              n in slide_seats.SEATS and m in (*slide_seats.SEATS, 'enclosure-back-top'))], 6.)}
for key, held in HOLDS.items():
    seat_n, snap_n = f'{key}-seat', f'{key}-snap-cap'
    seat, snap = parts[seat_n][0], parts[snap_n][0]
    way = np.array(slide_seats.ON[snap_n])
    fore = list(np.arange(0., slide_seats.SLIDE + 0.01, 1.)) + ([slide_seats.SLIDE + slide_seats.VAR] if key == 'meter' else [])
    slide = min((seat.distance(parts[h][0].moved(cq.Location(cq.Vector(0., -t, 0.)))), float(t), h) for t in fore for h in held)
    way_on = min((snap.moved(cq.Location(cq.Vector(*(-t * way)))).distance(parts[h][0]), float(t), h)
                 for t in np.arange(0., 12.01, 1.) for h in held)
    seat_at, snap_at = (min((x.distance(parts[h][0]), h) for h in held) for x in (seat, snap))
    result['seats'][seat_n].update({'held_mm': round(seat_at[0], 3), 'held_nearest': seat_at[1],
                                    'slide_mm': round(slide[0], 3), 'slide_at_mm': slide[1], 'slide_nearest': slide[2]})
    result['seats'][snap_n].update({'held_mm': round(snap_at[0], 3), 'held_nearest': snap_at[1],
                                    'way_on_mm': round(way_on[0], 3), 'way_on_at_mm': way_on[1], 'way_on_nearest': way_on[2]})
    print(f'  {key}: seat {seat_at[0]:.3f} mm off {seat_at[1]}, {slide[0]:.3f} mm on the slide ({slide[2]}, {slide[1]:g} mm '
          f'fore); cap {snap_at[0]:.3f} mm off {snap_at[1]}, {way_on[0]:.3f} mm on its way on ({way_on[2]}, {way_on[1]:g} mm out)')
# The seats print as part of back-top.
back_top = parts['enclosure-back-top'][0]
for n in slide_seats.SEATS:
    back_top = back_top.fuse(parts.pop(n)[0])
parts['enclosure-back-top'] = (back_top.clean(), M_PETGF_BLACK)
result['seats']['back_top_solids'] = len(parts['enclosure-back-top'][0].Solids())
print(f'  back-top with its seats: {result["seats"]["back_top_solids"]} solid')
json.dump(result, open(HERE / 'study.json', 'w'), indent=1)

# --- scenes -----------------------------------------------------------------------------------


def scene(name, keep=None, only=None, moves={}):
    a = cq.Assembly(name=name)
    box = keep.BoundingBox() if keep is not None else None
    for n, (s, colour) in parts.items():
        if only is not None and n not in only:
            continue
        if n in moves:
            s = s.moved(moves[n])
        b = s.BoundingBox()
        if keep is None or (box.xmin <= b.xmin and b.xmax <= box.xmax and box.ymin <= b.ymin and b.ymax <= box.ymax
                            and box.zmin <= b.zmin and b.zmax <= box.zmax):
            pass
        elif b.xmax < box.xmin or box.xmax < b.xmin or b.ymax < box.ymin or box.ymax < b.ymin:
            continue
        else:
            s = s.intersect(keep)
            if s.Volume() < 1e-3:
                continue
        a.add(s, name=n, color=colour)
    export_assembly(a, str(OUT / f'{name}.step'))


scene('rear-port-rebuild')
# West of the Pisco and meter axis, X77.5, to show the wall's section and the inlet's.
scene('rear-port-rebuild-section', cq.Solid.makeBox(X_E + 100., 250., 200., cq.Vector(-100., 250., 200.)))
# East of X60, so the Pisco and the meter can be seen side-on against the side wall from inside.
scene('rear-port-rebuild-corner', cq.Solid.makeBox(60., 250., 200., cq.Vector(60., 250., 200.)))
# Under the cap: the carbonator, the coil wound on it and the two reservoirs, drawn with the whole
# scene to show where the CO2 tube lands on the core.
under = cq.Assembly(name='rear-port-rebuild-core')
for n in ('carbonator-tube', 'endcap-top', 'evap-coil', 'reservoir-a', 'reservoir-b'):
    under.add(core[n], name=n, color=cca._style.colour_for(n))
export_assembly(under, str(OUT / 'rear-port-rebuild-core.step'))
# The seats and snap caps, among the parts they hold and their neighbours: in place, with the caps
# 24 mm back along their way on, and cut across at the outlet bonnet, the vent and the inlet thread.
SNAP = ('enclosure-back-top', *slide_seats.CHAIN, *PISCO, 'co2-check', 'digiten-flow', *slide_seats.CAPS, *SODA,
        'bulkhead-carb', 'bulkhead-carb-nut', 'bulkhead-flavor-a', 'bulkhead-flavor-a-nut')
SNAP_CUTS = (401.5, 419.6, 436.0)
around = cq.Solid.makeBox(120., 97., 120., cq.Vector(-10., 383., 240.))
scene('rear-port-rebuild-snaps', around, SNAP)
scene('rear-port-rebuild-snaps-off', around, SNAP,
      {n: cq.Location(cq.Vector(*(-24. * np.array(slide_seats.ON[n])))) for n in slide_seats.CAPS})
for y in SNAP_CUTS:
    scene(f'rear-port-rebuild-snaps-at-{y:g}', cq.Solid.makeBox(120., 480. - y, 120., cq.Vector(-10., y, 240.)), SNAP)

# --- the README's figures ---------------------------------------------------------------------
sys.path.insert(0, str(HW.parent / 'tools'))
from docgen import substitute_md  # noqa: E402
to_back = result['pisco_to_back_top_mm']
near = result['soda_inlet']
past_cap = near['straight_down_to_core_mm']
vk = result['vk']
pump = result['g-ganen-pump']['nearest_mm']
check = result['co2-check']
co2 = result['co2_tube']
snaps = result['seats']
CHAIN = ('jg-pp010822e', 'gagira-coupling', 'multiplex-asse1022', 'jg-pi4512f6s', 'jg-pp061208w')


def overlap_depth(a, b, axis):
    o = next((v for k, v in result['overlaps'].items() if set(k.split(' x ')) == {a, b}), None)
    return o['bbox'][axis + 3] - o['bbox'][axis] if o else float('nan')


# tee-fold in V-K: the stem's tip below the port's floor, and the hub on the port's boss, low to high.
fold_in_vk = sorted(next(v for k, v in result['overlaps'].items() if set(k.split(' x ')) == {'tee-fold', 'vk-solenoid'})
                    ['pieces'], key=lambda b: b[2])


substitute_md(HERE / 'README.md', {
    'PISCO_HOLE_D': f'{PISCO_HOLE:.2f}', 'TAP_HOLE_D': f'{TAP_HOLE:.2f}', 'TAP_BORE_D': f'{TAP_BORE:.2f}',
    'GRID_DROP': f'{GRID_DROP:.2f}', 'TILE_SEAT_Z': f'{STOP_Z:g}',
    'CO2_X': f'{X_E:g}', 'ROW_1': f'{ROWS[0]:g}', 'ROW_2': f'{ROWS[1]:g}', 'ROW_3': f'{ROWS[2]:g}',
    'MOUTH_Y': f'{MOUTH_Y:.1f}', 'TILE_T': f'{CHIP_T:g}', 'CHANNEL_DEPTH': f'{FACE_Y - FLOOR_Y:g}',
    'ROOF_T': f'{355. - CEILING:g}', 'LAND_T': f'{FACE_Y - WALL_IN:g}',
    'PISCO_ON_LAND': f'{to_back["rear wall, the 6 mm field"]:.2f}',
    'PISCO_UNDER_CEILING': f'{to_back["ceiling"]:.1f}', 'PISCO_TO_SIDE_WALL': f'{to_back["east side wall"]:.1f}',
    'PISCO_TO_STOCK': f'{to_back["9 mm stock east of the field"]:.1f}',
    'ASSE_UNDER_CEILING': f'{result["multiplex-asse1022_under_ceiling_mm"]:.2f}',
    'METER_UNDER_PISCO': f'{result["meter"]["nearest_mm"]["pisco-body"]:.1f}',
    'METER_TO_SIDE_WALL': f'{result["meter"]["nearest_mm"]["enclosure-back-top"]:.1f}',
    'METER_INSERTION': f'{sel["meter_insertion_estimate_mm"]:g}',
    'BEND_OFF_METER': f'{H["leg_mm"] + sel["holder_to_meter_mm"]:g}', 'BEND_R': f'{BEND_R:g}',
    'DROP_X': f'{start[0]:.1f}', 'DROP_Y': f'{start[1]:.1f}', 'DROP_LEN': f'{start[2] - CAP_Z:.1f}',
    'FOAM_LEN': f'{near["foam_length_mm"]:.0f}',
    'FOAM_TO_SIDE_WALL': f'{near["soda-insulation_nearest_mm"].get("enclosure-back-top", float("nan")):.1f}',
    'DROP_TO_RESERVOIR': f'{past_cap["reservoir-a"]:.1f}', 'DROP_TO_COIL': f'{past_cap["evap-coil"]:.1f}',
    'DROP_TO_CARBONATOR': f'{past_cap["carbonator-tube"]:.1f}',
    'VK_EAST': f'{SHIFT[0]:.1f}', 'VK_AFT': f'{SHIFT[1]:.1f}', 'VK_DOWN': f'{-SHIFT[2]:.1f}', 'VK_TILT': f'{tilt:.1f}',
    'VK_ARM': f'{vk["arm_mm"]:.1f}', 'VK_TO_SODA': f'{vk["to_soda_inlet_mm"]:.1f}',
    'VK_TO_SIDE_WALL': f'{vk["vk-solenoid_nearest_mm"]["enclosure-back-top"]:.1f}',
    'FOLD_INTO_TEE': f'{overlap_depth("tee-fold", "jg-pp0208e", 0):.2f}',
    'STUB': f'{STUB:g}', 'STUB_CUT': f'{stub_len:.1f}', 'VK_CLEAR': f'{VK_CLEAR:g}',
    'PUMP_TO_OVER': f'{pump["bulkhead-drain"]:.1f}', 'PUMP_TO_ASSE': f'{min(pump[n] for n in CHAIN if n in pump):.1f}',
    'PUMP_TO_TEE': f'{pump["jg-pp0208e"]:.1f}', 'PUMP_TO_FOAM': f'{pump["soda-insulation"]:.1f}',
    'CHECK_MOUTH_Y': f'{check["socket_mouth_y"]:.1f}', 'CHECK_TIP_SHORT': f'{check["tip_short_of_tube_stop_mm"]:.1f}',
    'CHECK_UNDER_CEILING': f'{check["under_ceiling_mm"]:.1f}',
    'CHECK_TO_FOAM': f'{check["nearest_mm"]["soda-insulation"]:.1f}',
    'CO2_LAND_X': f'{co2_land[0]:.1f}', 'CO2_LAND_Y': f'{co2_land[1]:.1f}', 'CO2_LEN': f'{co2_len:.0f}',
    'CO2_BEND': f'{CO2_BEND:g}', 'CO2_GAP': f'{CO2_GAP:g}', 'CO2_DROP': f'{co2_top[2] - CAP_Z:.0f}',
    'CO2_S_R': f'{co2_s_radius:.0f}', 'CO2_PUSH': f'{co2_push:.1f}', 'CO2_STRAIGHT': f'{CAP_Z - co2_low[2]:.0f}',
    'CO2_LOW_Z': f'{co2_low[2]:.1f}', 'CAP_FACE': f'{CAP_Z:g}',
    'CO2_TO_RIM': f'{co2["straight_to_core_mm"]["carbonator-tube"]:.1f}',
    'CO2_TO_RESERVOIR': f'{co2["straight_to_core_mm"]["reservoir-a"]:.1f}',
    'CO2_TO_VK': f'{co2["nearest_mm"]["vk-solenoid"]:.1f}', 'CO2_TO_PUMP': f'{co2["nearest_mm"]["g-ganen-pump"]:.1f}',
    'STEM_PAST_PORT': f'{fold_in_vk[0][5] - fold_in_vk[0][2]:.1f}',
    'HUB_INTO_VK': f'{fold_in_vk[-1][5] - fold_in_vk[-1][2]:.2f}',
    'SLIDE': f'{slide_seats.SLIDE:g}', 'SNAP_THREAD': f'{slide_seats.THREAD:g}', 'SNAP_WING': f'{slide_seats.WING:g}',
    'SNAP_REACH': f'{slide_seats.REACH:g}', 'SNAP_WALL': f'{slide_seats.WALL:g}',
    'SLIDE_GAP': f'{min(snaps[n]["slide_mm"] for n in slide_seats.SEATS):.2f}',
    'CAP_GAP': f'{min(snaps[n]["held_mm"] for n in slide_seats.CAPS):.2f}',
    'WAY_ON_GAP': f'{min(snaps[n]["way_on_mm"] for n in slide_seats.CAPS):.2f}',
    'PUMP_UNDER_ASSE_CAP': f'{snaps["asse-snap-cap"]["pump_ride_mm"]:.1f}',
    'METER_SEAT_TO_FOAM': f'{snaps["meter-seat"]["nearest_mm"]["soda-insulation"]:.1f}',
    'METER_SEAT_TO_UNION': f'{snaps["meter-seat"]["nearest_mm"]["bulkhead-carb"]:.1f}',
})
