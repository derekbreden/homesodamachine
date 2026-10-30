"""The above-core arrangement rebuilt from the rear ports inward, hardest part to place first.

Each part goes where it has to be and is measured against what is already placed; nothing is
routed before its turn. Placed so far, on back-top's port corner cut down to its walls:

- the PISCO regulator, its long-neck inlet through a hole of its own at the CO2 station;
- the scanned threaded ASSE chain on TAP;
- the four remaining bulkheads, dropped with the grid;
- the label tiles, in channels between side rails;
- the DIGITEN meter, straight into the soda bulkhead with no tube showing, larger side down;
- the meter's inlet turned straight down by production's bend holder, foam and tube, to the
  cold-core cap's face;
- V-K, the stem elbow into its top port and its wall, as production stands them, moved with the
  tee; the wall reaches the side wall instead of the cap.

Back-top is today's piece with its six old bores plugged, both roof pockets filled back to the
full roof, the clamping land carried down to the dropped bottom nuts, the new bores, each column's
chip pockets opened into one channel, and no mounting brackets. It is cropped to the port corner,
CROP.

Writes the three scenes page.json draws into hardware/assembly/scenes/out/, the measurements to
study.json, and their figures into README.md.

    tools/cad-venv/bin/python hardware/manifold-layout/studies/rear-port-rebuild/study.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
for p in ('scripts', 'manifold-layout', 'printed-parts/cadlib', 'reference/asse1022-threaded-chain',
          'cold-core-layout', 'printed-parts/cold-core', 'printed-parts/cold-core/foam-assembly'):
    sys.path.insert(0, str(HW / p))

import cadquery as cq  # noqa: E402
from OCP.gp import gp_Trsf  # noqa: E402
import above_core as layout  # noqa: E402
import above_core_parts as acp  # noqa: E402
import asse1022_threaded_chain as tc  # noqa: E402
import cold_core_assembly as cca  # noqa: E402
import fits  # noqa: E402
import soda_inlet  # noqa: E402
import _above_core_mounts as mounts  # noqa: E402
import valve_seat  # noqa: E402
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import (M_ALUMINIUM, M_JG_GREY_ACETAL, M_MOULDED_BLACK, M_NITRILE_BLACK,  # noqa: E402
                        M_PETGF_BLACK)
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
CROP = cq.Solid.makeBox(108., 474. - 305., 356. - 230., cq.Vector(0., 305., 230.))
CAP_Z = facts['faces']['foam-assembly.cap']

# --- the scanned chain on TAP -------------------------------------------------------------------
ports = tc.ports()
t = gp_Trsf()
t.SetValues(0, 0, 1, X_W - tc.bfp.BODY_CENTER_Z, -1, 0, 0, MOUTH_Y + ports['inlet'][0][0], 0, -1, 0, ROWS[0])
TO_WORLD = cq.Location(t)
native = tc.parts()
tee_rec = tc.parameters()['atbu444-e']
T0 = cq.Vector(*tee_rec['origin_mm'])
STEMAX = cq.Vector(*[tee_rec['rotation'][i][0] for i in range(3)])
native['atbu444-e'] = native['atbu444-e'].rotate(T0, T0 + STEMAX, 90.)
names = {'pp010822e': 'jg-pp010822e', 'gagira': 'gagira-coupling', 'multiplex-asse1022': 'multiplex-asse1022',
         'pi4512f6s': 'jg-pi4512f6s', 'pp061208w': 'jg-pp061208w', 'atbu444-e': 'neofit-atbu444e'}
parts = {names[k]: (s.moved(TO_WORLD), tc.COLORS[k]) for k, s in native.items()}
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
inside = cq.Solid.makeBox(SIDE_WALL_X, 462.3 - 305., CEILING - 230., cq.Vector(0., 305., 230.))
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

# --- V-K, its stem elbow and its wall, as production stands them, moved with the tee ------------
# Production butts tee-fold's socket mouth on the tee's east run mouth, stands V-K on tee-fold's
# stem and presses V-K's posts into an upright wall rooted on the cap. All three move with the
# scanned tee's east run mouth; the wall reaches the side wall instead of the cap.


def tee_run(name):
    point, outward = ports['outlet_' + name]
    a, b = (cq.Vertex.makeVertex(*p).rotate(T0, T0 + STEMAX, 90.).moved(TO_WORLD).Center()
            for p in (point, [point[i] + outward[i] for i in range(3)]))
    return np.array(a.toTuple()), np.array((b - a).toTuple())


tee_mouth, tee_axis = max((tee_run(n) for n in ('plus', 'minus')), key=lambda run: run[1][0])
run_plus = acp._module('above_core_branch_tee', 'reference/branch-stem-tees/branch_stem_tees.py').specification(
    'neofit')['ports']['run_plus']
prod_mouth, prod_axis = comps['water-split'][2]((run_plus['position'], run_plus['outward']))
SHIFT = tee_mouth - np.array(prod_mouth)
MOVE = cq.Location(cq.Vector(*SHIFT))
for n in ('vk-solenoid', 'tee-fold'):
    parts[n] = (comps[n][0].moved(MOVE), comps[n][1])
seat = mounts.valve_support_datums('vk-solenoid')
lo, hi = seat['bearing_min_world_mm'], seat['bearing_max_world_mm']
at_vk = layout.location('vk-solenoid')
wall = cq.Solid.makeBox(*(hi[i] - lo[i] for i in range(3)), cq.Vector(*lo)).cut(
    valve_seat.build_sockets().val().moved(at_vk),
    valve_seat.build_port_channel(2. * valve_seat.seat_half_y + 2.).val().moved(at_vk)).moved(MOVE)
arm = cq.Solid.makeBox(SIDE_WALL_X - hi[0] - SHIFT[0], hi[1] - lo[1], hi[2] - lo[2],
                       cq.Vector(hi[0] + SHIFT[0], lo[1] + SHIFT[1], lo[2] + SHIFT[2]))
parts['vk-wall'] = (wall.fuse(arm).clean(), M_PETGF_BLACK)
VK = ('vk-solenoid', 'tee-fold', 'vk-wall')

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
for i, a in enumerate(names_all):
    for b in names_all[i + 1:]:
        if a.startswith('pisco-') and b.startswith('pisco-'):
            continue
        sa, sb = parts[a][0], parts[b][0]
        ba, bb = sa.BoundingBox(), sb.BoundingBox()
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        common = sa.intersect(sb)
        v = common.Volume()
        if v > 1e-3:
            overlaps[f'{a} x {b}'] = {'mm3': round(v, 3), 'bbox': bbox(common)}
            print(f'  {a} x {b}: {v:.3f} at {bbox(common)}')
result['overlaps'] = overlaps


def pts(shape, step=0.3):
    vs, ts = shape.tessellate(0.03, 0.1)
    vs = np.array([(q.x, q.y, q.z) for q in vs])
    tri = vs[np.array(ts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    n = np.ceil(area / step ** 2).astype(int)
    i = np.repeat(np.arange(len(tri)), n)
    rng = np.random.default_rng(1)
    r1, r2 = np.sqrt(rng.random(len(i)))[:, None], rng.random(len(i))[:, None]
    return np.concatenate([(1 - r1) * a[i] + r1 * (1 - r2) * b[i] + r1 * r2 * c[i], vs])


def nearest(name, others, reach=15.):
    P = pts(parts[name][0])
    found = {}
    for n in others:
        d, _ = cKDTree(pts(parts[n][0], 0.4)).query(P, k=1)
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
tilt = math.degrees(math.acos(min(1., abs(float(np.dot(tee_axis, prod_axis))))))
print(f'== V-K, tee-fold and the wall moved ({SHIFT[0]:.2f}, {SHIFT[1]:.2f}, {SHIFT[2]:.2f}) to the tee\'s east run '
      f'mouth ({tee_mouth[0]:.2f}, {tee_mouth[1]:.2f}, {tee_mouth[2]:.2f}); the scanned run is {tilt:.2f} deg off '
      f'production\'s; the arm out to the side wall is {SIDE_WALL_X - hi[0] - SHIFT[0]:.2f} mm')
result['vk'] = {'shift_mm': [round(float(c), 3) for c in SHIFT], 'tee_east_mouth': [round(float(c), 3) for c in tee_mouth],
                'run_tilt_deg': round(tilt, 2), 'arm_mm': round(SIDE_WALL_X - hi[0] - SHIFT[0], 2),
                'bboxes': {n: bbox(parts[n][0]) for n in VK}}
for n in VK:
    print(f'== {n} {bbox(parts[n][0])}')
    result['vk'][f'{n}_nearest_mm'] = nearest(n, [m for m in placed if m not in VK])
json.dump(result, open(HERE / 'study.json', 'w'), indent=1)

# --- scenes -----------------------------------------------------------------------------------


def scene(name, keep=None):
    a = cq.Assembly(name=name)
    for n, (s, colour) in parts.items():
        if keep is not None:
            s = s.intersect(keep)
            if s.Volume() < 1e-3:
                continue
        a.add(s, name=n, color=colour)
    export_assembly(a, str(OUT / f'{name}.step'))


scene('rear-port-rebuild')
# West of the Pisco and meter axis, X77.5, to show the wall's section and the inlet's.
scene('rear-port-rebuild-section', cq.Solid.makeBox(X_E, 200., 200., cq.Vector(0., 300., 200.)))
# East of X60, so the Pisco and the meter can be seen side-on against the side wall from inside.
scene('rear-port-rebuild-corner', cq.Solid.makeBox(60., 200., 200., cq.Vector(60., 300., 200.)))

# --- the README's figures ---------------------------------------------------------------------
sys.path.insert(0, str(HW.parent / 'tools'))
from docgen import substitute_md  # noqa: E402
to_back = result['pisco_to_back_top_mm']
near = result['soda_inlet']
past_cap = near['straight_down_to_core_mm']
vk = result['vk']
vk_back = vk['bboxes']['vk-solenoid'][4]


def overlap_depth(a, b, axis):
    o = next((v for k, v in result['overlaps'].items() if set(k.split(' x ')) == {a, b}), None)
    return o['bbox'][axis + 3] - o['bbox'][axis] if o else float('nan')


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
    'VK_AFT': f'{SHIFT[1]:.1f}', 'VK_DOWN': f'{-SHIFT[2]:.1f}', 'VK_TILT': f'{tilt:.1f}', 'VK_ARM': f'{vk["arm_mm"]:.1f}',
    'VK_BACK_Y': f'{vk_back:.1f}', 'VK_PAST_DROP': f'{vk_back - start[1]:.1f}',
    'VK_TO_METER': f'{vk["vk-solenoid_nearest_mm"]["digiten-flow"]:.1f}',
    'VK_TO_SIDE_WALL': f'{vk["vk-solenoid_nearest_mm"]["enclosure-back-top"]:.1f}',
    'VK_INTO_HOLDER': f'{overlap_depth("vk-solenoid", "soda-bend-holder", 1):.1f}',
    'FOLD_INTO_TEE': f'{overlap_depth("tee-fold", "neofit-atbu444e", 0):.1f}',
    'STEM_PAST_PORT': f'{overlap_depth("tee-fold", "vk-solenoid", 2):.1f}',
})
