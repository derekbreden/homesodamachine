"""DATA is the accepted nameplate construction with a narrower, wing-thick face.

The centred jack opening is cut through the continuous plate. Broad wings and
matching receiving slots use the nameplate geometry and its seating datum.
Y=0 is the flat print-bed back; +Y is the customer-facing direction.
"""
from collections import namedtuple

import cadquery as cq
import _nameplate_wing_interface as nameplate
import port_chip

from _enclosure_data import dimensions as _dimensions, read as _read

globals().update(_dimensions()['data'])
box = nameplate.box
Station = namedtuple('Station', 'x z')


def jack_face_y(y_outer):
    """Purchased jack and complete receptacle datum, independent of the DATA plate."""
    return _read('data-jack-face', data=_dimensions()['data'], y_outer=y_outer)


def pad_runout(station,y_outer,*,up=-1):
    """Where the pad's 45-degree print-down run-out leaves its inboard face, as (y, z)."""
    return tuple(_read('data-pad-runout', data=_dimensions()['data'],
                       nameplate=_dimensions()['nameplate'], z=station[1],
                       y_outer=y_outer, up=up))


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
                          supported=supported,width=WIDTH,height=HEIGHT,wing_span=WING_SPAN,
                          access=False,runout_lead=nameplate.RUNOUT_LEAD)
    mouth=port_chip.outline(WIDTH+2*FACE_AIR,TOP+FACE_AIR,BOTTOM+FACE_AIR,
                           POCKET_DEPTH+1+BACK_AIR,radius=CORNER_R+FACE_AIR)
    mouth=mouth.fuse(mouth.translate((0,0,up*supported)))
    return solid.cut(mouth.translate((x,y_outer-POCKET_DEPTH-BACK_AIR,z))).clean()


def plain_lips(station,y_outer):
    x,z=station
    return nameplate.plain_lips(Station(x,z+CENTER_Z),y_outer,
                               width=WIDTH,wing_span=WING_SPAN)
