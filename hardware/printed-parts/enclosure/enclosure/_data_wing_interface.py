"""DATA is the accepted nameplate construction with a narrower, wing-thick face.

The centred jack opening is cut through the continuous plate. Broad wings and
matching receiving slots use the nameplate geometry and its seating datum.
Y=0 is the flat print-bed back; +Y is the customer-facing direction.
"""
from collections import namedtuple

import cadquery as cq
import _nameplate_wing_interface as nameplate
import port_chip

WIDTH = 32.0
TOP = 18.789
BOTTOM = 11.0
HEIGHT = TOP+BOTTOM
CENTER_Z = (TOP-BOTTOM)/2
THICK = nameplate.WING_THICK
POCKET_DEPTH = nameplate.THICK
INK_DEPTH = .72
OPENING_W = 20.8
OPENING_H = 18.3
OPENING_R = .4
WING_THICK = nameplate.WING_THICK
WING_END_INSET = (nameplate.HEIGHT-nameplate.WING_SPAN)/2
WING_SPAN = HEIGHT-2*WING_END_INSET
PROJECTION = nameplate.PROJECTION
FACE_AIR = nameplate.FACE_X_AIR
TIP_AIR = nameplate.TIP_AIR
END_AIR = nameplate.END_AIR
THICKNESS_AIR = nameplate.THICKNESS_AIR
SUPPORTED_AIR = nameplate.SUPPORTED_END_AIR
FLOOR_STOCK = nameplate.FLOOR_STOCK
ENTRY_WIDTH = nameplate.ENTRY_BEVEL_WIDTH
ENTRY_DEPTH = nameplate.ENTRY_BEVEL_DEPTH
CORNER_R = port_chip.LOWER_CORNER_RADIUS
box = nameplate.box
Station = namedtuple('Station', 'x z')


def aperture(y0,y1):
    return (cq.Workplane('XY').rect(OPENING_W,OPENING_H).extrude(y1-y0)
            .edges('|Z').fillet(OPENING_R).val()
            .rotate((0,0,0),(1,0,0),-90).translate((0,y0,0)))


def blank():
    """Continuous plate and two full-span wings share one flat bed face."""
    plate = port_chip.outline(WIDTH,TOP,BOTTOM,THICK)
    wings = [wing.translate((0,0,CENTER_Z))
             for wing in nameplate.wings(width=WIDTH,span=WING_SPAN)]
    return plate.fuse(*wings).cut(aperture(-.01,THICK+.01)).clean()


def apply(solid,station,y_outer,*,up=-1,supported=SUPPORTED_AIR):
    x,z=station
    solid=nameplate.apply(solid,Station(x,z+CENTER_Z),y_outer,up=up,
                          supported=supported,width=WIDTH,height=HEIGHT,wing_span=WING_SPAN)
    mouth=port_chip.outline(WIDTH+2*FACE_AIR,TOP+FACE_AIR,BOTTOM+FACE_AIR,
                           POCKET_DEPTH+1,radius=CORNER_R+FACE_AIR)
    mouth=mouth.fuse(mouth.translate((0,0,up*supported)))
    return solid.cut(mouth.translate((x,y_outer-POCKET_DEPTH,z))).clean()


def plain_lips(station,y_outer):
    x,z=station
    return nameplate.plain_lips(Station(x,z+CENTER_Z),y_outer,
                               width=WIDTH,wing_span=WING_SPAN)
