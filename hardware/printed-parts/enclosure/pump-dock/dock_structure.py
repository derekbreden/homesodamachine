"""Front-top's tee wall and the pump tees that stand in it.

Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch stands in the TEE
WALL: front-top's bay bulkhead, one flat slab the bay's whole width and height
(`enclosure._bulkhead`), whose fore 3.175 mm is the collet plate. Behind the plate each tee has
one collar-clear bore through the rest of the wall; ahead of the bore a smaller tube hole leaves
a face under the collet. The bore holds the tee in X and Z and lets it slide along Y: the plate
stops the collet at the fore end of its 1.5 mm stroke, and in service the bottomed pump tube
holds the tee at `connected`.

Both are horizontal bores in a piece printed on Z, so each is teardropped.
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

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
# The tee at each station, in the plate's hole order (west to east).
TEES = {'west-outer': 'Y-G', 'west-inner': 'Y-F', 'east-inner': 'Y-C', 'east-outer': 'Y-D'}

# The bore round the branch collar: the scanned tee's sampled collar envelope and one running
# clearance.
BORE_R = tee.COLLAR_ENVELOPE_D / 2.0 + fits.running
# The wall's aft face stands this far fore of the tee's run barrel with the tee at released, its
# most forward station, so the wall never ends the tee's travel.
BODY_AIR = 1.454
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


def wall_aft_y(fore_y):
    """The tee wall's aft face: `BODY_AIR` fore of the run barrel of a tee at released."""
    return plumbing.tee_axis_y(fore_y, 'released') - tee.BARREL_R - BODY_AIR


def bore_depth(plate):
    """Each tee's bore along the branch: from the release face to the wall's aft face."""
    return plate['wall_aft_y'] - plumbing.plate_aft_y(plate['fore_y'])


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


def tee_bores(plate):
    """One teardropped collar-clear bore per tee, from the release face out through the wall's
    aft face."""
    y0, y1 = plumbing.plate_aft_y(plate['fore_y']), plate['wall_aft_y'] + 1.0
    return [teardrop_y(BORE_R, x, z, y0, y1) for x, z in plate['holes']]


def wall_cuts(plate):
    """Everything the dock takes out of the tee wall."""
    return plate_holes(plate) + tee_bores(plate)


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
    return {'tee-' + name.lower(): tee_body(plate, x, z) for _station, name, x, z in stations(plate)}


def part_color(_name):
    from _materials import M_JG_BLACK_PP
    return M_JG_BLACK_PP


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
