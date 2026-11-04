"""Nameplate face and its two plate-owned PET-GF snap tabs, in millimetres.

The plate's back is Y=0; its face is +Y. Tabs run into -Y. One bar behind
the pocket receives both: its shoulders are rigid, and each tab's slot and
catch pocket stand in it with the bar's full frame above and below.
"""

from collections import namedtuple
import math

import cadquery as cq

from _enclosure_data import dimensions as _dimensions, read as _read

globals().update(_dimensions()['face'])


Nameplate = namedtuple("Nameplate", "x z width height corner bevel slip thick wall")


def station(x, z):
    return Nameplate(x, z, WIDTH, HEIGHT, CORNER_R, BEVEL, SLIP, THICK, WALL)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def neck():
    """The slot's outer side: the tab's outer face and its side slip."""
    return _read('face-values', face=_dimensions()['face'])['neck']


def inward():
    """The slot's inner side, where the lip passes as the tab flexes."""
    return _read('face-values', face=_dimensions()['face'])['inward']


def bar_end():
    """The bar's end, one shoulder beyond the slot."""
    return _read('face-values', face=_dimensions()['face'])['bar_end']


def slot_z(supported=0.25, up=-1.0):
    """The slot's Z span. Only its print-down end takes the supported-surface allowance."""
    return tuple(_read('face-slots', face=_dimensions()['face'],
                       supported=supported, up=up))


def tabs():
    """Two straight cantilevers with square catches and tapered insertion noses."""
    parts = []
    for side in (-1, 1):
        inner, outer = TAB_X-TAB_THICK/2, TAB_X+TAB_THICK/2
        profile = [(inner, 0), (outer, 0), (outer, -LIP_START),
                   (outer+LIP, -LIP_START), (outer+LIP, -LIP_START-LIP_LAND),
                   (outer, -TAB_LENGTH),
                   (inner, -TAB_LENGTH)]
        parts.append(cq.Workplane("XY").workplane(offset=TAB_Z-TAB_WIDTH/2)
                     .polyline([(side*x, y) for x, y in profile]).close()
                     .extrude(TAB_WIDTH).val())
    return parts


def receiver_additions(supported=0.25, up=-1.0):
    """The receiving bar and its corbel, relative to the plate back.

    The bar spans both shoulders and runs from the wall to SHOULDER_STOCK
    inboard of the bearing faces, BAR_FRAME above and below the slots. A 45°
    corbel carries its print-down face to the wall.
    """
    pad_y = THICK-WALL
    front = -LIP_START+BEARING_SLIP-SHOULDER_STOCK
    z0, z1 = slot_z(supported, up)
    lo, hi = z0-BAR_FRAME, z1+BAR_FRAME
    crown = hi if up < 0 else lo
    x = bar_end()
    corbel = (cq.Workplane("YZ", origin=(-x, 0, 0))
              .polyline([(front, crown), (pad_y, crown), (pad_y, crown-up*(pad_y-front))])
              .close().extrude(2*x).val())
    return [box(-x, x, front, pad_y, lo, hi), corbel]


def receiver_cuts(supported=0.25, up=-1.0):
    """Each tab's slot and catch pocket, relative to the plate back.

    The slot passes through the pocket floor and the bar. The catch pocket
    runs from the slot's inner side out through the bar's end, ahead of the
    shoulder's bearing face.
    """
    z0, z1 = slot_z(supported, up)
    far = -TAB_LENGTH-1
    cuts = []
    for side in (-1, 1):
        x0, x1 = sorted((side*inward(), side*neck()))
        cuts.append(box(x0, x1, far, .8, z0, z1))
        x0, x1 = sorted((side*inward(), side*(bar_end()+1)))
        cuts.append(box(x0, x1, far, -LIP_START+BEARING_SLIP, z0, z1))
    return cuts


def apply(solid, plate, y_outer, *, wall=3.0, supported=0.25, up=-1.0):
    """Cut the same pocket and receiving bar in an enclosure wall or a fit coupon."""
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
    for addition in receiver_additions(supported, up):
        solid = solid.fuse(addition.translate(placement))
    bevel = plate.bevel-(math.sqrt(2)-1)*plate.slip
    mouth = (cq.Workplane("XY").rect(pw,ph).extrude(plate.thick+1)
             .edges("|Z").fillet(pr).faces("<Z").chamfer(bevel).val()
             .rotate((0,0,0),(1,0,0),-90).translate(placement))
    solid = solid.cut(mouth.fuse(mouth.translate((0,0,up*supported))))
    for cutter in receiver_cuts(supported,up):
        solid = solid.cut(cutter.translate(placement))
    return solid
