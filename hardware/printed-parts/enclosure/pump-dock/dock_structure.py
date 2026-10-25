"""Front-top's tee wall, the pump tees that stand in it and the stem elbows of their returns.

Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch stands in the TEE
WALL: front-top's bay bulkhead, one flat slab the bay's whole width and height
(`enclosure._bulkhead`). Each tee has one collar-clear bore through the wall from its bore
face; ahead of the bore a collet recess lets the branch collet stand extended and grip its
pump tube, and a smaller tube hole passes that tube through the wall's fore band. The bore
holds the tee in X and Z. Its fixed branch barrel stops it fore on the bore face, clear of the
collet, and its lower return, anchored in the rear valve, stops it aft.

Each lower return carries a NeoFit stem elbow in the tee's lower collet and another in the rear
valve's bottom collet, their stems cut to stand where `fixed_returns.elbow_return` puts them.

Every wall cut is a horizontal bore in a piece printed on Z, so each is teardropped.
"""
from functools import lru_cache
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
for _p in (HW / 'printed-parts' / 'cadlib', HW / 'printed-parts' / 'enclosure' / 'enclosure',
           HW / 'reference' / 'tee-connector', HW / 'reference' / 'neofit-stem-elbow',
           HW / 'scripts'):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fits  # noqa: E402
import tee_connector as tee  # noqa: E402
import fixed_returns as plumbing  # noqa: E402
import neofit_stem_elbow as stem_elbow  # noqa: E402

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
# The tee at each station, in the plate's hole order (west to east).
TEES = {'west-outer': 'Y-G', 'west-inner': 'Y-F', 'east-inner': 'Y-C', 'east-outer': 'Y-D'}

# The bore round the branch collar: the scanned tee's sampled collar envelope and one running
# clearance.
BORE_R = tee.COLLAR_ENVELOPE_D / 2.0 + fits.running
# The wall's aft face stands this far fore of the tee's run barrel.
BODY_AIR = 1.454
HOLE_R = 4.25                          # the fore band's tube hole
# The extended branch collet's room ahead of the bore face: its clearance radius and one running
# air round it, and deep enough that the collet still stands clear with the tee pushed fore onto
# its fixed barrel.
RECESS_R = tee.COLLET_NOSE_R + fits.running
RECESS_DEPTH = tee.COLLET_PROUD + fits.running
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
    """The tee wall's aft face: `BODY_AIR` fore of the tee's run barrel."""
    return plumbing.tee_axis_y(fore_y) - tee.BARREL_R - BODY_AIR


def bore_depth(plate):
    """Each tee's bore along the branch: from the bore face to the wall's aft face."""
    return plate['wall_aft_y'] - plumbing.plate_aft_y(plate['fore_y'])


def return_clearances(plate):
    """Under each rear valve, its port channel carried down through front-top to the seam:
    the valve's bottom collet and the stem elbow under it."""
    out = []
    for port in plate['return_ports'].values():
        x, y, z = port['point']
        out.append(cq.Solid.makeCylinder(RETURN_CHANNEL_R, z + 20.0 - (plate['z0'] - 1.0),
                                         cq.Vector(x, y, plate['z0'] - 1.0),
                                         cq.Vector(0, 0, 1)))
    return out


def plate_holes(plate):
    """One teardropped tube hole through the wall's fore band per tee."""
    y0, y1 = plate['fore_y'] - 1.0, plumbing.plate_aft_y(plate['fore_y']) + 1.0
    return [teardrop_y(HOLE_R, x, z, y0, y1) for x, z in plate['holes']]


def collet_recesses(plate):
    """One teardropped recess per tee, `RECESS_DEPTH` fore of the bore face, where the branch
    collet stands extended."""
    face = plumbing.plate_aft_y(plate['fore_y'])
    if RECESS_DEPTH >= plumbing.PLATE_T:
        raise ValueError(f"a {RECESS_DEPTH:g} mm collet recess opens through the "
                         f"{plumbing.PLATE_T:g} mm fore band")
    return [teardrop_y(RECESS_R, x, z, face - RECESS_DEPTH, face + 0.01)
            for x, z in plate['holes']]


def tee_bores(plate):
    """One teardropped collar-clear bore per tee, from the bore face out through the wall's
    aft face."""
    y0, y1 = plumbing.plate_aft_y(plate['fore_y']), plate['wall_aft_y'] + 1.0
    return [teardrop_y(BORE_R, x, z, y0, y1) for x, z in plate['holes']]


def wall_cuts(plate):
    """Everything the dock takes out of the tee wall."""
    return plate_holes(plate) + collet_recesses(plate) + tee_bores(plate)


@lru_cache(maxsize=1)
def _tee_native():
    """The scanned tee with its branch collet extended, gripping its pump tube."""
    from _cadq_export import import_step
    return import_step(str(HW / 'reference' / 'tee-connector' / 'tee-connector.step')).val()


def tee_body(plate, x, z):
    """The purchased tee at its station: run upright, branch toward the pump."""
    y = plumbing.tee_axis_y(plate['fore_y'])
    pose = cq.Location(cq.Plane(origin=(x, y, z), xDir=(-1, 0, 0), normal=(0, 0, 1)))
    return _tee_native().moved(pose)


@lru_cache(maxsize=1)
def _elbow_native():
    """The stem elbow's body and release collet in its own frame: axes crossing at the origin,
    stem out -X, socket out +Y."""
    return tuple(piece.val() for _name, piece in stem_elbow.build())


def elbow_body(row):
    """One `fixed_returns.elbow_return` elbow: its stem cut `row['stem']` past the shoulder and
    standing up into its collet, its socket opening along `row['socket']`."""
    body, collet = _elbow_native()
    keep = stem_elbow.HUB_BACK_REACH + row['stem']
    body = body.cut(cq.Solid.makeBox(40.0, 40.0, 40.0, cq.Vector(-keep - 40.0, -20.0, -20.0)))
    ux, uy, _uz = row['socket']
    pose = cq.Location(cq.Plane(origin=row['crossing'], xDir=(0, 0, -1), normal=(uy, -ux, 0)))
    return cq.Compound.makeCompound([body.moved(pose), collet.moved(pose)])


def elbow_host(name):
    """The body a return's stem elbow stands in, by assembly name: its tee, or its rear valve."""
    host = name[len('stem-elbow-'):]
    return ('tee-' if host.startswith('y-') else 'valve-') + host


def stem_overlap(elbow, host):
    """`(inside, outside)`: the volume a placed stem elbow shares with the fitting its stem is
    bottomed in, and how much of that lies outside the stem itself.

    The tee is drawn with a tube-clear bore and the valve without its port's full bore, so the two
    share at most the stem. Anything they share outside it, the elbow's hub or shoulder in its
    host, is an interference."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    r = stem_elbow.STEM_OD / 2.0

    def outer(face):
        # The stem's surface faces away from its axis; the socket's bore, the one other
        # cylinder of its radius, faces in.
        axis = BRepAdaptor_Surface(face.wrapped).Cylinder().Axis()
        o = cq.Vector(axis.Location().X(), axis.Location().Y(), axis.Location().Z())
        d = cq.Vector(axis.Direction().X(), axis.Direction().Y(), axis.Direction().Z())
        p = face.positionAt(0.5, 0.5)
        off = p - (o + d * (p - o).dot(d))
        return face.normalAt(p).dot(off) > 0.0

    faces = [face for face in elbow.Faces() if face.geomType() == 'CYLINDER'
             and abs(BRepAdaptor_Surface(face.wrapped).Cylinder().Radius() - r) < 1e-3
             and outer(face)]
    axis = BRepAdaptor_Surface(faces[0].wrapped).Cylinder().Axis()
    o = cq.Vector(axis.Location().X(), axis.Location().Y(), axis.Location().Z())
    d = cq.Vector(axis.Direction().X(), axis.Direction().Y(), axis.Direction().Z())
    t = [(p - o).dot(d) for face in faces for p in (v.Center() for v in face.Vertices())]
    stem = cq.Solid.makeCylinder(r + 0.01, max(t) - min(t) + 0.02, o + d * (min(t) - 0.01), d)
    common = elbow.intersect(host)
    inside = common.Volume()
    return inside, (common.cut(stem).Volume() if inside > 0 else 0.0)


def parts(plate):
    """Each tee, and the stem elbows of its return: `stem-elbow-y-c` in the tee's lower collet
    and `stem-elbow-v-c` in its rear valve's."""
    out = {}
    for _station, name, x, z in stations(plate):
        out['tee-' + name.lower()] = tee_body(plate, x, z)
        target = plate['return_ports'][str(x)]
        lower = plumbing.tee_ports(plate['fore_y'], x, z)['lower']['point']
        at_tee, at_valve = plumbing.elbow_return(lower, tuple(target['point']))['elbows']
        out['stem-elbow-' + name.lower()] = elbow_body(at_tee)
        out['stem-elbow-' + target['valve'].lower()] = elbow_body(at_valve)
    return out


def part_color(name):
    from _materials import M_JG_BLACK_PP, M_NEOFIT_WHITE_ACETAL
    return M_NEOFIT_WHITE_ACETAL if name.startswith('stem-elbow-') else M_JG_BLACK_PP


def tube_setting_jig(plate, cradle_back_y):
    """Factory gauge that seats on the cradle's flat back and catches the four tube tips.

    Four open channels admit the tubes; the blind ends are the seated tip datum, where each
    tube bottoms in its tee with the cradle home. The tool comes off before the cradle goes into
    the bay.
    """
    row = plate['holes'][0][1]
    tip = plumbing.tip_y(plate['fore_y'])
    body = box(plate['holes'][0][0] - 8, plate['holes'][-1][0] + 8,
               cradle_back_y, tip + 3, row - 8, row + 8)
    for x, z in plate['holes']:
        # Full axial bore with open top, ending at the tube's cut-face datum.
        bore = ycyl(3.5, x, z, cradle_back_y - .1, tip)
        opening = box(x - 3.5, x + 3.5, cradle_back_y - .1, tip, z, row + 8.1)
        body = body.cut(bore.fuse(opening))
    return body.clean()
