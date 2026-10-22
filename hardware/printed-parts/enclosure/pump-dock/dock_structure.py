"""Front-top's tee anchors, the tee caps that snap down on top of the tees, and the tees.

Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch lies in a TEE
ANCHOR: a rib rooted on front-top's seam plane behind the collet plate, its top a half
journal round the branch collar. A TEE CAP snaps down on top of the branch and closes the
journal: the anchor cap's section (`_anchor_cap_interface`), its half pipe sized to the
journal, two spring wings down the rib's flanks and a lip on each clicking into a window.
The journal holds the tee in X and Z and lets it slide along Y: the plate stops the collet at
the fore end of its 1.5 mm stroke, and in service the bottomed pump tube holds the tee at
`connected`.

The collet plate itself is front-top's bulkhead (`enclosure._bulkhead`); this module cuts its
tube holes and supplies the anchors, the caps and the magnet bosses that back the plate's
SB443-IN slots.
"""
from functools import lru_cache
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
for _p in (HW / 'printed-parts' / 'cadlib', HW / 'printed-parts' / 'enclosure' / 'enclosure',
           HW / 'reference' / 'tee-connector', HW / 'scripts'):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fits  # noqa: E402
import tee_connector as tee  # noqa: E402
import dock_retention as retention  # noqa: E402
import fixed_returns as plumbing  # noqa: E402
import _anchor_cap_interface as anchor  # noqa: E402

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
# The tee at each station, in the plate's hole order (west to east).
TEES = {'west-outer': 'Y-G', 'west-inner': 'Y-F', 'east-inner': 'Y-C', 'east-outer': 'Y-D'}

# The half journal round the branch collar: the tee reference's printed journal, its sampled
# collar envelope and one running clearance.
JOURNAL_R = tee.COLLAR_ENVELOPE_D / 2.0 + fits.running
# The bore's mouth ease runs out over a longer arc on this bore than on the anchor cap's, so the
# rib's wall and the cap's saddle each stand a quarter thicker than the anchor cap's: the saddle
# keeps its 2.5 mm past the ease, and the wing gap stays the anchor cap's.
THICKER = 0.25
RIB_R = JOURNAL_R + anchor.WALL + THICKER
WING_IN = RIB_R + anchor.WING_AIR
WING_OUT = WING_IN + anchor.WING
SADDLE_R = JOURNAL_R + anchor.SADDLE + THICKER
# The cap's crown to the bulkhead overhead.
CAP_TOP_AIR = 1.0
HOLE_R = 4.25                          # the plate's tube hole: a face left under each collet
RETURN_CHANNEL_R = 8.1                 # a rear valve's port channel in its tray (`valve_tray`)
TEARDROP_DEG = 36.0                    # front-top's printable roof angle over a horizontal bore


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def ycyl(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def fused(parts):
    parts = tuple(parts)
    return (parts[0].fuse(*parts[1:]) if len(parts) > 1 else parts[0]).clean()


def teardrop_y(r, x, z, y0, y1):
    """A bore on Y with its crown carried to an apex at the printable roof angle."""
    a = math.radians(TEARDROP_DEG)
    half, tangent, apex = r * math.sin(a), z + r * math.cos(a), z + r / math.cos(a)
    roof = cq.Workplane('XZ', origin=(0, y0, 0)).polyline(
        [(x - half, tangent), (x + half, tangent), (x, apex)]).close().extrude(-(y1 - y0)).val()
    return ycyl(r, x, z, y0, y1).fuse(roof)


def stations(plate):
    """(station name, tee name, x, z) for each of the plate's four holes, west to east."""
    return [(name, TEES[name], x, z) for name, (x, z) in zip(STATIONS, plate['holes'])]


def frame(plate, x, z):
    """The anchor's frame (`_anchor_cap_interface.Frame`): its origin on the branch axis at
    the release face, `u` aft along the branch, `n` down toward the seam plane."""
    return anchor.Frame((x, plumbing.plate_aft_y(plate['fore_y']), z), (0.0, 1.0, 0.0),
                        (0.0, 0.0, -1.0))


def rib_length(plate):
    """The anchor along the branch: from the release face to the bulkhead's aft face, the
    plane the front rail channels open on, so the anchor ends flush with both."""
    return plate['wall_aft_y'] - plumbing.plate_aft_y(plate['fore_y'])


def window_length(plate):
    """Each catch window: from the plate to the anchor's aft end web."""
    return rib_length(plate) - anchor.END_WEB


def cap_crown_z(z):
    return z + WING_OUT


def plate_top_z(z):
    """Where the collet plate ends and the full bulkhead begins over the caps."""
    return cap_crown_z(z) + CAP_TOP_AIR


def rib(plate, x, z):
    """One tee anchor: the rib from the seam plane up to the branch axis, its half journal
    bored and its outer top edges chamfered for the cap's lips to ride over."""
    f, c = frame(plate, x, z), anchor.RIB_CHAMFER
    length, b_root = rib_length(plate), z - plate['z0']
    body = f.prism([(-RIB_R + c, 0.0), (RIB_R - c, 0.0), (RIB_R, c), (RIB_R, b_root),
                    (-RIB_R, b_root), (-RIB_R, c)], 0.0, length)
    return body


def rib_cuts(plate, x, z):
    """The anchor's journal and its two catch windows, each a closed pocket between the plate
    and the anchor's aft end web, so its bearing face prints as a bridge."""
    f = frame(plate, x, z)
    cuts = [f.bore(JOURNAL_R, -0.01, rib_length(plate) + 1.0)]
    length = window_length(plate)
    for side in (1, -1):
        a_in, a_out = side * (RIB_R - anchor.WINDOW_DEPTH), side * (RIB_R + 2.0)
        cuts.append(f.prism([(a_in, anchor.WINDOW_B0), (a_out, anchor.WINDOW_B0),
                             (a_out, anchor.SLOT_TOP), (a_in, anchor.SLOT_TOP)], 0.0, length))
    return cuts


def _half_pipe(f, seat_r, s0, s1):
    ca, sa = math.cos(math.radians(anchor.MOUTH_DEG)), math.sin(math.radians(anchor.MOUTH_DEG))
    return f.section((WING_OUT, 0.0), [
        ("A", (0.0, -WING_OUT), (-WING_OUT, 0.0)),
        ("L", (-seat_r - anchor.MOUTH, 0.0)), ("L", (-seat_r * ca, -seat_r * sa)),
        ("A", (0.0, -seat_r), (seat_r * ca, -seat_r * sa)),
        ("L", (seat_r + anchor.MOUTH, 0.0)),
    ], s0, s1)


def _lip(side):
    pts = [(WING_IN + 0.05, anchor.LIP_B), (WING_IN - anchor.ENGAGE, anchor.LIP_B),
           (WING_IN - anchor.ENGAGE, anchor.LIP_B + anchor.LIP_TIP),
           (WING_IN, anchor.LIP_B + anchor.LIP_H), (WING_IN + 0.05, anchor.LIP_B + anchor.LIP_H)]
    return [(side * a, b) for a, b in pts]


def _cavity(f, side, s0, s1):
    """The gap between half pipe and wing, round-ended `CAVITY_DEG` round the pipe."""
    t = math.radians(anchor.CAVITY_DEG)
    r0, r1 = SADDLE_R, WING_IN
    rm, rh = (r0 + r1) / 2.0, (r1 - r0) / 2.0
    end = (rm * math.cos(t) - rh * math.sin(t), -rm * math.sin(t) - rh * math.cos(t))
    pts = [("L", (r1, 0.5)), ("L", (r1, 0.0)),
           ("A", (r1 * math.cos(t / 2), -r1 * math.sin(t / 2)), (r1 * math.cos(t), -r1 * math.sin(t))),
           ("A", end, (r0 * math.cos(t), -r0 * math.sin(t))),
           ("A", (r0 * math.cos(t / 2), -r0 * math.sin(t / 2)), (r0, 0.0))]
    mirror = [(k, *[(side * p[0], p[1]) for p in rest]) for k, *rest in pts]
    return f.section((side * r0, 0.5), mirror, s0, s1)


def cap(plate, x, z):
    """One tee cap snapped home: shoulders on the anchor's lips at the branch axis, wings and
    lips centred in their windows. One section the whole length of the window, less a slip at
    each end, the way the anchor cap is one section the length of its own."""
    f = frame(plate, x, z)
    air = anchor.END_AIR
    w0, w1 = air, window_length(plate) - air
    body = _half_pipe(f, JOURNAL_R, w0, w1)
    for side in (1, -1):
        wing = [(side * WING_IN, 0.0), (side * WING_OUT, 0.0), (side * WING_OUT, anchor.WING_TOP),
                (side * WING_IN, anchor.WING_TOP)]
        body = body.fuse(f.prism(wing, w0, w1)).fuse(f.prism(_lip(side), w0, w1))
    for side in (1, -1):
        body = body.cut(_cavity(f, side, w0 - 1.0, w1 + 1.0))
    return body.clean()


def cap_print_pose(plate):
    """The cap standing on its fore end, the section on the bed and the branch axis upright:
    every layer is the whole section and each wing bends along its own extrusion lines."""
    x, z = plate['holes'][0]
    shape = cap(plate, x, z).rotate((0, 0, 0), (1, 0, 0), 90)
    b = shape.BoundingBox()
    return shape.translate((-b.center.x, -b.center.y, -b.zmin))


def wing_strain():
    """The anchor cap's beam estimate of a wing's peak strain going on, for this section."""
    rm = (WING_IN + WING_OUT) / 2.0
    load_b = anchor.LIP_B + anchor.LIP_TIP / 2.0
    pts = [(rm * math.cos(-math.radians(anchor.CAVITY_DEG) * (1 - i / 40)),
            rm * math.sin(-math.radians(anchor.CAVITY_DEG) * (1 - i / 40))) for i in range(41)]
    pts += [(rm, load_b * i / 20) for i in range(1, 21)]
    integral = sum((load_b - (p[1] + q[1]) / 2.0) ** 2 * math.dist(p, q)
                   for p, q in zip(pts, pts[1:]))
    lever = max(abs(load_b - p[1]) for p in pts)
    return anchor.ENGAGE * lever * (anchor.WING / 2.0) / integral


def magnet_bosses(plate, interface):
    """Behind each fixed SB443-IN slot, the stock the collet plate is too thin to hold it in:
    one wall past the slot's floor, sides and roof, standing on the seam plane."""
    out = []
    for x, z in retention.column_stations(plate['holes']):
        _y0, floor = interface.at('fixed', 0.0, interface.floor_depth)
        _bottom, roof = retention.column_limits(z)
        half = retention.SLOT_HALF + anchor.WALL
        out.append(box(x - half, x + half, plumbing.plate_aft_y(plate['fore_y']) - 0.01,
                       floor + anchor.WALL, plate['z0'], roof + anchor.WALL))
    return out


def return_clearances(plate):
    """Under each rear valve, its port channel carried down through front-top to the seam:
    the valve's bottom collet and the hairpin rising into it."""
    out = []
    for port in plate['return_ports'].values():
        x, y, z = port['point']
        out.append(cq.Solid.makeCylinder(RETURN_CHANNEL_R, z + 20.0 - (plate['z0'] - 1.0),
                                         cq.Vector(x, y, plate['z0'] - 1.0),
                                         cq.Vector(0, 0, 1)))
    return out


def plate_holes(plate):
    """One teardropped tube hole through the collet plate per tee."""
    y0, y1 = plate['fore_y'] - 1.0, plumbing.plate_aft_y(plate['fore_y']) + 1.0
    return [teardrop_y(HOLE_R, x, z, y0, y1) for x, z in plate['holes']]


def fixed_features(plate, interface):
    """Front-top's dock: (stocks to fuse, cutters to cut) after the bulkhead and floor."""
    stocks = [rib(plate, x, z) for x, z in plate['holes']] + magnet_bosses(plate, interface)
    cuts = plate_holes(plate)
    for x, z in plate['holes']:
        cuts += rib_cuts(plate, x, z)
    return stocks, cuts


@lru_cache(maxsize=1)
def _tee_native():
    from _cadq_export import import_step
    return import_step(str(HW / 'reference' / 'tee-connector' / 'tee-connector.step')).val()


def tee_body(plate, x, z, state='connected'):
    """The purchased tee at its station: run upright, branch toward the pump."""
    y = plumbing.tee_axis_y(plate['fore_y'], state)
    pose = cq.Location(cq.Plane(origin=(x, y, z), xDir=(-1, 0, 0), normal=(0, 0, 1)))
    return _tee_native().moved(pose)


def parts(plate):
    out = {}
    for _station, name, x, z in stations(plate):
        out['tee-' + name.lower()] = tee_body(plate, x, z)
    for _station, name, x, z in stations(plate):
        out['tee-cap-' + name.lower()] = cap(plate, x, z)
    return out


def part_color(name):
    from _materials import M_JG_BLACK_PP, M_PETGF_BLACK
    return M_PETGF_BLACK if name.startswith('tee-cap-') else M_JG_BLACK_PP


def manufacturing_parts(plate):
    """The four tee caps are one part; it prints standing on its fore end."""
    from _materials import M_PETGF_BLACK
    return {'enclosure-tee-cap': {'shape': cap_print_pose(plate), 'color': M_PETGF_BLACK}}


def tube_setting_jig(plate, cartridge_face_y):
    """Factory gauge seats on the cartridge back and catches the four tube tips.

    Four open channels admit the tubes; the blind ends are the seated tip datum, where each
    tube bottoms in its tee at connected. The tool is removed before docking the cartridge.
    """
    row = plate['holes'][0][1]
    tip = plumbing.tip_y(plate['fore_y'])
    body = box(plate['holes'][0][0] - 8, plate['holes'][-1][0] + 8,
               cartridge_face_y, tip + 3, row - 8, row + 8)
    for x, z in plate['holes']:
        # Full axial bore with open top, ending at the tube's cut-face datum.
        bore = ycyl(3.5, x, z, cartridge_face_y - .1, tip)
        opening = box(x - 3.5, x + 3.5, cartridge_face_y - .1, tip, z, row + 8.1)
        body = body.cut(bore.fuse(opening))
    # The two moving pole columns stand proud of the cartridge back to the wall face. Each
    # clears in one full-height groove 3 mm deep, so its walls are stock and not strips.
    for x, z in retention.column_stations(plate['holes']):
        half = retention.SLOT_HALF + 1.0
        body = body.cut(box(x - half, x + half, cartridge_face_y - .1, cartridge_face_y + 3,
                            row - 9, row + 9))
    return body.clean()
