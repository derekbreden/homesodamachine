"""Nameplate face and its two plate-owned PET-GF snap tabs, in millimetres.

The plate's back is Y=0; its face is +Y. Tabs run into -Y. The receiving
shoulders are rigid and open into the enclosure behind each tab.
"""

from collections import namedtuple
import math

import cadquery as cq

WIDTH = 104.53
HEIGHT = 38.0
THICK = 2.4
CORNER_R = 3.0
BEVEL = 0.4
SLIP = 0.15
WALL = 6.0

TAB_X = 45.0
TAB_Z = -2.5
TAB_WIDTH = 8.0
TAB_THICK = 0.8
TAB_LENGTH = 9.0
TAB_ROOT_R = 0.6
LIP_START = 7.5
LIP = 0.6
SIDE_SLIP = 0.15
END_SLIP = 0.30
BEARING_SLIP = 0.48

# The water pump's rear bearing remains on this full-width ledge. Its top
# sits 13 mm above the cold-core cap; the plate centre is 9.5 mm above it.
CENTRE_ABOVE_CAP = 9.5
LEDGE_WIDTH = 97.73
LEDGE_HEIGHT = 7.0
LEDGE_DEPTH = 5.0

Nameplate = namedtuple("Nameplate", "x z width height corner bevel slip thick wall")


def station(x, z):
    return Nameplate(x, z, WIDTH, HEIGHT, CORNER_R, BEVEL, SLIP, THICK, WALL)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def tabs():
    """Two straight cantilevers with square catches and tapered insertion noses."""
    parts = []
    for side in (-1, 1):
        inner, outer = TAB_X-TAB_THICK/2, TAB_X+TAB_THICK/2
        profile = [(inner, 0), (outer, 0), (outer, -LIP_START),
                   (outer+LIP, -LIP_START), (outer, -TAB_LENGTH),
                   (inner, -TAB_LENGTH)]
        parts.append(cq.Workplane("XY").workplane(offset=TAB_Z-TAB_WIDTH/2)
                     .polyline([(side*x, y) for x, y in profile]).close()
                     .extrude(TAB_WIDTH).val())
    return parts


def receiver_additions(supported=0.25):
    """Pump ledge and two solid shoulder blocks, relative to the plate back."""
    pad_y = THICK-WALL
    back_y = pad_y-LEDGE_DEPTH
    parts = [box(-LEDGE_WIDTH/2, LEDGE_WIDTH/2, back_y, pad_y,
                 -LEDGE_HEIGHT/2-supported, LEDGE_HEIGHT/2-supported)]
    for side in (-1, 1):
        x = side*TAB_X
        parts.append(box(x-2.5, x+2.5, back_y, pad_y,
                         TAB_Z-TAB_WIDTH/2-END_SLIP-1.5,
                         LEDGE_HEIGHT/2-supported))
    return parts


def receiver_cuts(supported=0.25, up=-1.0):
    """Through slots with an inward flex lane and open-backed retaining shoulders.

    The shoulder starts 0.48 mm ahead of the lip. The enlarged rear opening
    exposes the complete catch to support removal from inside the enclosure.
    Only the print-down end of each slot receives supported-surface relief.
    """
    cuts = []
    z0 = TAB_Z-TAB_WIDTH/2-END_SLIP + min(0, up*supported)
    z1 = TAB_Z+TAB_WIDTH/2+END_SLIP + max(0, up*supported)
    for side in (-1, 1):
        inward = TAB_X-TAB_THICK/2-(LIP-SIDE_SLIP)-SIDE_SLIP
        neck = TAB_X+TAB_THICK/2+SIDE_SLIP
        outside = TAB_X+2.6
        x0, x1 = sorted((side*inward, side*neck))
        cuts.append(box(x0, x1, -TAB_LENGTH-1, .8, z0, z1))
        x0, x1 = sorted((side*inward, side*outside))
        cuts.append(box(x0, x1, -TAB_LENGTH-1, -LIP_START+BEARING_SLIP, z0, z1))
        # Root fillets grow only inward, inside a short flared mouth.
        x0, x1 = sorted((side*(TAB_X-TAB_THICK/2-TAB_ROOT_R-SIDE_SLIP), side*neck))
        cuts.append(box(x0, x1, -TAB_ROOT_R-SIDE_SLIP, .8, z0, z1))
    return cuts


def apply(solid, plate, y_outer, *, wall=3.0, supported=0.25, up=-1.0):
    """Cut the same pocket/shoulders in an enclosure wall or a fit coupon."""
    y_inner, y_pad = y_outer-wall, y_outer-plate.wall
    floor = y_outer-plate.thick
    pw, ph = plate.width+2*plate.slip, plate.height+2*plate.slip
    pr = plate.corner+plate.slip
    pad = (cq.Workplane("XY").rect(pw+2*wall, ph+2*wall).extrude(y_inner-y_pad)
           .edges("|Z").fillet(pr+wall).val().rotate((0,0,0),(1,0,0),-90)
           .translate((plate.x,y_pad,plate.z)))
    rise = y_inner-y_pad
    zedge = plate.z-up*(ph/2+wall)
    xhalf = pw/2+wall
    ramp = (cq.Workplane("YZ", origin=(plate.x-xhalf-1,0,0))
            .polyline([(y_pad,zedge),(y_pad,zedge+up*rise),(y_inner,zedge)])
            .close().extrude(2*xhalf+2).val())
    pad = pad.cut(ramp)
    solid = solid.fuse(pad, pad.translate((0,0,up*supported)))
    placement = (plate.x,floor,plate.z)
    for addition in receiver_additions(supported if up<0 else 0):
        solid = solid.fuse(addition.translate(placement))
    bevel = plate.bevel-(math.sqrt(2)-1)*plate.slip
    mouth = (cq.Workplane("XY").rect(pw,ph).extrude(plate.thick+1)
             .edges("|Z").fillet(pr).faces("<Z").chamfer(bevel).val()
             .rotate((0,0,0),(1,0,0),-90).translate(placement))
    solid = solid.cut(mouth.fuse(mouth.translate((0,0,up*supported))))
    for cutter in receiver_cuts(supported,up):
        solid = solid.cut(cutter.translate(placement))
    return solid
