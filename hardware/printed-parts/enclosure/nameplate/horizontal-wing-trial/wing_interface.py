"""Face-up nameplate wings and their recessed side slots, in the plate's X/Y/Z frame."""
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'enclosure'))
import _nameplate_interface as dimensions

WIDTH, HEIGHT = dimensions.WIDTH, dimensions.HEIGHT
FIELD_THICK = 2.40
THICK = 3.36
FRAME_WIDTH = 3.0
PROJECTION = 2.40
WING_THICK = 1.68
WING_SPAN = 30.0
END_RADIUS = .6
FACE_SLIP = .20
THICKNESS_AIR = .48
TIP_AIR = .50
END_AIR = .30
SUPPORTED_END_AIR = .75
FLOOR_STOCK = 3.6
box = dimensions.box


def wings():
    """The full-height roots overlap the plate; both wings begin at back Y=0."""
    parts = []
    for side in (-1, 1):
        wing = (cq.Workplane('XY').rect(PROJECTION+1, WING_SPAN)
                .extrude(WING_THICK).edges('|Z').fillet(END_RADIUS).val()
                .rotate((0,0,0),(1,0,0),-90)
                .translate((side*(WIDTH/2+(PROJECTION-1)/2),0,0)))
        parts.append(wing)
    return parts


def blank():
    plate = (cq.Workplane('XY').rect(WIDTH,HEIGHT).extrude(THICK)
             .edges('|Z').fillet(dimensions.CORNER_R).val()
             .rotate((0,0,0),(1,0,0),-90))
    # A recessed field leaves a bendable 2.4 mm web. The 3.36 mm perimeter
    # supplies stock for thick wings and a 1.2 mm receiver retaining ledge.
    field = (cq.Workplane('XY').rect(WIDTH-2*FRAME_WIDTH,HEIGHT-2*FRAME_WIDTH)
             .extrude(THICK-FIELD_THICK+1).edges('|Z').fillet(1.0).val()
             .rotate((0,0,0),(1,0,0),-90).translate((0,FIELD_THICK,0)))
    return plate.cut(field).fuse(*wings()).clean()


def apply(solid, station, y_outer, *, supported=SUPPORTED_END_AIR, up=-1):
    """Flush plate pocket and two sideways slots; no cantilevers behind the face.

    Y slot walls print vertically in the enclosure. Their .48 mm total thickness
    air is a smooth-wall trial, independent of the rough supported-face allowance.
    The print-down slot end alone receives the latter allowance.
    """
    floor = y_outer-THICK
    shift = (station.x,floor,station.z)
    pw, ph = WIDTH+2*FACE_SLIP, HEIGHT+2*FACE_SLIP
    pad = (cq.Workplane('XY').rect(pw+2*(PROJECTION+2),ph+4)
           .extrude(FLOOR_STOCK+THICK).edges('|Z').fillet(dimensions.CORNER_R+2).val()
           .rotate((0,0,0),(1,0,0),-90).translate((0,-FLOOR_STOCK,0)))
    # A 45-degree inboard run-out carries the added pocket floor in the wall pose.
    zedge = -up*(ph/2+2)
    ramp = (cq.Workplane('YZ',origin=(-pw,0,0))
            .polyline([(-FLOOR_STOCK,zedge),(-FLOOR_STOCK,zedge+up*FLOOR_STOCK),(0,zedge)])
            .close().extrude(2*pw).val())
    solid = solid.fuse(pad.cut(ramp).translate(shift))
    mouth = (cq.Workplane('XY').rect(pw,ph).extrude(THICK+1)
             .edges('|Z').fillet(dimensions.CORNER_R+FACE_SLIP).val()
             .rotate((0,0,0),(1,0,0),-90))
    # The print-down mouth edge gets the same rough-surface allowance as the
    # slot end; otherwise that edge can bind before the wings are seated.
    mouth=mouth.fuse(mouth.translate((0,0,up*supported)))
    solid = solid.cut(mouth.translate(shift))
    z0 = -WING_SPAN/2-END_AIR+min(0,up*supported)
    z1 = WING_SPAN/2+END_AIR+max(0,up*supported)
    for side in (-1,1):
        xa,xb = sorted((side*(WIDTH/2-.1),side*(WIDTH/2+PROJECTION+TIP_AIR)))
        solid = solid.cut(box(xa,xb,0,WING_THICK+THICKNESS_AIR,z0,z1).translate(shift))
    # Back access permits pushing the centre outward to release the wings.
    # Its diamond ceiling is self-supporting in the enclosure wall orientation.
    access=(cq.Workplane('XY').polyline([(-9,0),(0,10),(9,0),(0,-10)])
            .close().extrude(FLOOR_STOCK+1).val()
            .rotate((0,0,0),(1,0,0),-90).translate((0,-FLOOR_STOCK-.5,0)))
    solid=solid.cut(access.translate(shift))
    return solid.clean()


def receiver():
    shell = box(-WIDTH/2-PROJECTION-3,WIDTH/2+PROJECTION+3,
                THICK-3,THICK,-HEIGHT/2-4,HEIGHT/2+4)
    return apply(shell,dimensions.station(0,0),THICK)
