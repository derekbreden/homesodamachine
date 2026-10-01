"""Accepted face-up nameplate wings and receiver, in the plate X/Y/Z frame."""
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'cadlib'))
import _nameplate_interface as dimensions
import fits

WIDTH, HEIGHT = dimensions.WIDTH, dimensions.HEIGHT
THICK = 3.36
FIELD_THICK = THICK
PROJECTION = 2.40
WING_THICK = 1.68
WING_SPAN = 30.0
END_RADIUS = .6
FACE_SLIP = fits.slip
# Full-depth body-width clearance; retain the ordinary Z gaps.
FACE_X_AIR = .15
# Local Y fit trial: keep the seating floor fixed and relieve the retaining face.
THICKNESS_AIR = .45
# The body locates X. Keep nonlocating wing tips clear of rounded slot corners.
TIP_AIR = .25
END_AIR = fits.slip
SUPPORTED_END_AIR = fits.supported_surface
FLOOR_STOCK = 3.6
ENTRY_BEVEL_WIDTH = 1.10
ENTRY_BEVEL_DEPTH = .40
# The installed PSU terminal corner needs 1 mm behind the east wing's backing.
# Mating faces and the retaining lip are independent of this hidden rear relief.
EAST_BACKING = 2.14
EAST_RELIEF_START = WIDTH/2+.125
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
    return plate.fuse(*wings()).clean()


def apply(solid, station, y_outer, *, supported=SUPPORTED_END_AIR, up=-1):
    """Flush plate pocket and two sideways slots; no cantilevers behind the face.

    Body X has 0.15 mm per side; Z uses the shared static allowance.
    Nonlocating wing tips have 0.25 mm centered X clearance, retaining
    0.10 mm at maximum body travel. The plate back and wing
    undersides share the zero-clearance seating datum. The Y slot has 0.45 mm
    of local trial relief above the seated wing. Its walls print vertically,
    so only the print-down mouth and slot ends receive the extra
    supported-surface allowance. This hand-inserted plate has no low-force fit.
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
    mouth = (cq.Workplane('XY').rect(WIDTH+2*FACE_X_AIR,ph).extrude(THICK+1)
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
        # Entry bevel clears the rotating wing during hand-bent insertion.
        # The outer flat bearing retains the trial thickness gap.
        # The bevel follows the slot roof with its width and slope fixed.
        mouth_x = WIDTH/2+FACE_SLIP
        roof_y = WING_THICK+THICKNESS_AIR
        lead = (cq.Workplane('XY').workplane(offset=z0)
                .polyline([(side*mouth_x,roof_y),
                           (side*(mouth_x+ENTRY_BEVEL_WIDTH),roof_y),
                           (side*mouth_x,roof_y+ENTRY_BEVEL_DEPTH)])
                .close().extrude(z1-z0).val())
        solid = solid.cut(lead.translate(shift))
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


def production_backing(solid, station, y_outer):
    """Relieve the hidden east backing beside the installed PSU terminal corner."""
    keepout=box(EAST_RELIEF_START,WIDTH/2+PROJECTION+4,
                -FLOOR_STOCK-1,-EAST_BACKING,-HEIGHT/2-5,HEIGHT/2+5)
    return solid.cut(keepout.translate((station.x,y_outer-THICK,station.z))).clean()


def plain_lips(station, y_outer):
    """Preserve the coupon's complete retaining thickness through the show flutes."""
    fields=[]
    for side in (-1,1):
        x0,x1=sorted((side*(WIDTH/2+FACE_X_AIR),side*(WIDTH/2+PROJECTION+TIP_AIR)))
        fields.append((station.x+x0-.4,station.x+x1+.4,y_outer-THICK,y_outer+1,
                       station.z-WING_SPAN/2-END_AIR-SUPPORTED_END_AIR-.4,
                       station.z+WING_SPAN/2+END_AIR+.4))
    return tuple(fields)
