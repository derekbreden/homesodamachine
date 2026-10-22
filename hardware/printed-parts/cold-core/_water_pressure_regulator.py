"""Internal water regulator and its single tied cradle, in the top lid's frame."""
from functools import lru_cache
from pathlib import Path
import math
import sys
import cadquery as cq

HW = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'reference/shok-blok-regulator'))
import shok_blok_regulator as regulator

# The cap installs spun 180 degrees inside the core. The appliance then yaws
# the core 90 degrees. These datums belong to the lid, so the body and cradle
# follow its placement together.
INLET_XY = (-5.2, -49.3)
INLET_OVER_FACE = 48.6
AXIS = cq.Vector(-0.985, -0.08, -0.152).normalized().toTuple()
BEARING_S = 96.0
SEAT_R = 9.45
HALF_WIDTH = SEAT_R + 3.25
LENGTH = 8.8
TIE_WIDTH = 2.8
TIE_HEIGHT = 3.25
UNDER_BORE = 4.5


def inlet(face_z):
    return cq.Vector(*INLET_XY, face_z + INLET_OVER_FACE)


def bearing(face_z):
    return inlet(face_z) + cq.Vector(*AXIS) * BEARING_S


@lru_cache(maxsize=8)
def cradle(face_z):
    """A solid vertical post, an inclined open saddle and one horizontal tie passage."""
    mid = bearing(face_z)
    along = cq.Vector(*AXIS)
    slope = along.z / along.x
    x0, x1 = mid.x - LENGTH/2, mid.x + LENGTH/2
    y0 = mid.y - HALF_WIDTH
    wire = cq.Wire.makePolygon([
        cq.Vector(x0, y0, face_z), cq.Vector(x1, y0, face_z),
        cq.Vector(x1, y0, mid.z + slope*(x1-mid.x)),
        cq.Vector(x0, y0, mid.z + slope*(x0-mid.x)),
        cq.Vector(x0, y0, face_z)])
    post = cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 2*HALF_WIDTH, 0))
    bore = cq.Solid.makeCylinder(SEAT_R, 30, mid-along*15, along)
    roof = mid.z - SEAT_R - UNDER_BORE
    passage = cq.Solid.makeBox(TIE_WIDTH, 2*HALF_WIDTH+2, TIE_HEIGHT,
                               cq.Vector(mid.x-TIE_WIDTH/2, y0-1, roof-TIE_HEIGHT))
    return post.cut(bore).cut(passage).clean()


def proud():
    return cradle(0.0).BoundingBox().zmax


def tie_loop():
    """Conservative rectangle/circle loop in the body's normal plane, millimetres."""
    axis = cq.Vector(*AXIS)
    horizontal = abs(axis.x) / math.hypot(axis.x, axis.y)
    w = HALF_WIDTH / horizontal
    h = (SEAT_R + UNDER_BORE) / math.sqrt(1-axis.z**2)
    r = SEAT_R
    return 2*w + 2*h + 2*math.sqrt(w*w-r*r) + r*(math.pi-2*math.acos(r/w))
