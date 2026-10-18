"""Accepted face-up nameplate wings and receiver, in the plate X/Y/Z frame."""
import math
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
BACK_AIR = fits.slip
# Full-depth body-width clearance; retain the ordinary Z gaps.
FACE_X_AIR = .15
# Local relief above each wing; the back has its own static clearance.
THICKNESS_AIR = .45
# The body locates X. Wing tips retain static clearance at full body travel.
TIP_AIR = FACE_X_AIR + fits.slip
END_AIR = fits.slip
SUPPORTED_END_AIR = fits.supported_surface
FLOOR_STOCK = 3.6
# A production pad keeps its full floor stock this far past the mouth's print-down edge
# before its 45-degree run-out, so the corner between pocket floor and run-out keeps one
# 3 mm wall: (FLOOR_STOCK + RUNOUT_LEAD) / sqrt(2) = 3.
RUNOUT_LEAD = 3.0 * math.sqrt(2.0) - FLOOR_STOCK
ENTRY_BEVEL_WIDTH = 1.10
ENTRY_BEVEL_DEPTH = .40
# The installed PSU terminal corner needs 1 mm behind the east wing's backing.
# Mating faces and the retaining lip are independent of this hidden rear relief.
EAST_BACKING = 2.14
EAST_RELIEF_START = WIDTH/2+.125
box = dimensions.box


def wings(*, width=WIDTH, span=WING_SPAN):
    """The full-height roots overlap the plate; both wings begin at back Y=0."""
    parts = []
    for side in (-1, 1):
        wing = (cq.Workplane('XY').rect(PROJECTION+1, span)
                .extrude(WING_THICK).edges('|Z').fillet(END_RADIUS).val()
                .rotate((0,0,0),(1,0,0),-90)
                .translate((side*(width/2+(PROJECTION-1)/2),0,0)))
        parts.append(wing)
    return parts


def blank(*, width=WIDTH, height=HEIGHT, thick=THICK):
    plate = (cq.Workplane('XY').rect(width,height).extrude(thick)
             .edges('|Z').fillet(dimensions.CORNER_R).val()
             .rotate((0,0,0),(1,0,0),-90))
    return plate.fuse(*wings(width=width)).clean()


def apply(solid, station, y_outer, *, supported=SUPPORTED_END_AIR, up=-1,
          width=WIDTH, height=HEIGHT, wing_span=WING_SPAN, wall_face=None, access=True,
          runout_lead=0.0):
    """Flush plate pocket and two sideways slots; no cantilevers behind the face.

    Body X has 0.15 mm per side; Z uses the shared static allowance.
    Nonlocating wing tips have 0.30 mm centered X clearance, retaining
    0.15 mm at maximum body travel. The plate back and wing
    undersides have static clearance from their receiving floors. The Y slot has
    0.45 mm of local relief above the nominal wing. Its walls print vertically,
    so only the print-down mouth and slot ends receive the extra
    supported-surface allowance. This hand-inserted plate has no low-force fit.
    """
    floor = y_outer-THICK
    shift = (station.x,floor,station.z)
    pw, ph = width+2*FACE_SLIP, height+2*FACE_SLIP
    # Keep the full floor section behind the body, and `runout_lead` past its print-down
    # edge, before the run-out. The opposite end retains its two-millimetre margin.
    runout_margin = max(2.0, FLOOR_STOCK + runout_lead)
    # On a base wall the east end runs square into its hidden relief
    # (`production_backing`); a corner round there leaves only a sliver.
    rounds = '|Z' if wall_face is None else '|Z and <X'
    pad = (cq.Workplane('XY').rect(pw+2*(PROJECTION+2),ph+2+runout_margin)
           .extrude(FLOOR_STOCK+BACK_AIR+THICK).edges(rounds).fillet(dimensions.CORNER_R+2).val()
           .rotate((0,0,0),(1,0,0),-90)
           .translate((0,-FLOOR_STOCK-BACK_AIR,-up*(runout_margin-2)/2)))
    # A 45-degree inboard run-out carries the added pocket floor in the wall pose.
    zedge = -up*(ph/2+runout_margin)
    ramp = (cq.Workplane('YZ',origin=(-pw,0,0))
            .polyline([(-FLOOR_STOCK-BACK_AIR,zedge),
                       (-FLOOR_STOCK-BACK_AIR,zedge+up*FLOOR_STOCK),(-BACK_AIR,zedge)])
            .close().extrude(2*pw).val())
    pad = pad.cut(ramp)
    if wall_face is not None:
        # The opposite pad end meets the base wall on a 45-degree plane.
        # Cut the pad alone so existing host feet keep their complete profiles.
        rear, wall_y = -FLOOR_STOCK-BACK_AIR, wall_face-floor
        run = wall_y-rear
        if run > 0:
            end = up*(ph/2+2.0)
            finish = (cq.Workplane('YZ',origin=(-pw,0,0))
                      .polyline([(rear,end),(wall_y,end),(rear,end-up*run)])
                      .close().extrude(2*pw).val())
            pad = pad.cut(finish)
    solid = solid.fuse(pad.translate(shift))
    mouth = (cq.Workplane('XY').rect(width+2*FACE_X_AIR,ph).extrude(THICK+1+BACK_AIR)
             .edges('|Z').fillet(dimensions.CORNER_R+FACE_SLIP).val()
             .rotate((0,0,0),(1,0,0),-90).translate((0,-BACK_AIR,0)))
    # The print-down mouth edge gets the same rough-surface allowance as the
    # slot end; otherwise that edge can bind before the wings are seated.
    mouth=mouth.fuse(mouth.translate((0,0,up*supported)))
    solid = solid.cut(mouth.translate(shift))
    z0 = -wing_span/2-END_AIR+min(0,up*supported)
    z1 = wing_span/2+END_AIR+max(0,up*supported)
    for side in (-1,1):
        xa,xb = sorted((side*(width/2-.1),side*(width/2+PROJECTION+TIP_AIR)))
        solid = solid.cut(box(xa,xb,-BACK_AIR,WING_THICK+THICKNESS_AIR,z0,z1).translate(shift))
        # Entry bevel clears the rotating wing during hand-bent insertion.
        # The outer flat bearing retains the trial thickness gap.
        # The bevel follows the slot roof with its width and slope fixed.
        mouth_x = width/2+FACE_SLIP
        roof_y = WING_THICK+THICKNESS_AIR
        lead = (cq.Workplane('XY').workplane(offset=z0)
                .polyline([(side*mouth_x,roof_y),
                           (side*(mouth_x+ENTRY_BEVEL_WIDTH),roof_y),
                           (side*mouth_x,roof_y+ENTRY_BEVEL_DEPTH)])
                .close().extrude(z1-z0).val())
        solid = solid.cut(lead.translate(shift))
    # Back access permits pushing the centre outward to release the wings.
    # Its diamond ceiling is self-supporting in the enclosure wall orientation.
    # A plate with its own opening is released through it and takes no diamond.
    if access:
        diamond=(cq.Workplane('XY').polyline([(-9,0),(0,10),(9,0),(0,-10)])
                 .close().extrude(FLOOR_STOCK+BACK_AIR+1).val()
                 .rotate((0,0,0),(1,0,0),-90).translate((0,-FLOOR_STOCK-BACK_AIR-.5,0)))
        solid=solid.cut(diamond.translate(shift))
    return solid.clean()


def receiver():
    shell = box(-WIDTH/2-PROJECTION-3,WIDTH/2+PROJECTION+3,
                THICK-3,THICK,-HEIGHT/2-4,HEIGHT/2+4)
    return apply(shell,dimensions.station(0,0),THICK)


def production_backing(solid, station, y_outer, *, wall_face=None, column=None):
    """Relieve the hidden east backing, with run-outs beyond the complete pad.

    Given the room's corner `column` as `(x, y, radius)`, the relief runs to it and ends
    on the column's own round."""
    xa, xb = EAST_RELIEF_START, WIDTH/2+PROJECTION+4
    if column is not None:
        xb = column[0]-station.x
    ya, yb = -FLOOR_STOCK-BACK_AIR-1, -EAST_BACKING-BACK_AIR
    za, zb = -HEIGHT/2-5, HEIGHT/2+5
    keepout=box(xa,xb,ya,yb,za,zb)
    if wall_face is not None:
        wall_y = wall_face - (y_outer-THICK)
        run = yb - wall_y
        if run > 0:
            # Only the shallow bite into the base wall runs out. Both triangles
            # lie beyond the existing full pad/body/wing relief footprint.
            for profile in (((wall_y,za-run),(yb,za),(wall_y,za)),
                            ((wall_y,zb),(yb,zb),(wall_y,zb+run))):
                end = (cq.Workplane('YZ',origin=(xa,0,0)).polyline(profile)
                       .close().extrude(xb-xa).val())
                keepout=keepout.fuse(end)
    # The relief's west end is a 45-degree face from the pad's back at EAST_RELIEF_START to
    # its full depth, so the body's backing ends without a step as tall as the relief is deep.
    rear = -FLOOR_STOCK-BACK_AIR
    head = (cq.Workplane('XY').workplane(offset=za-HEIGHT)
            .polyline([(xa,rear),(xa+yb-rear,yb),(xa,yb)]).close()
            .extrude(zb-za+2*HEIGHT).val())
    keepout = keepout.cut(head)
    keepout = keepout.translate((station.x,y_outer-THICK,station.z))
    if column is not None:
        x, y, r = column
        keepout = keepout.cut(cq.Solid.makeCylinder(
            r, 3*HEIGHT, cq.Vector(x, y, station.z-1.5*HEIGHT), cq.Vector(0, 0, 1)))
    return solid.cut(keepout).clean()


def plain_lips(station, y_outer, *, width=WIDTH, wing_span=WING_SPAN):
    """Preserve the coupon's complete retaining thickness through the show flutes."""
    fields=[]
    for side in (-1,1):
        x0,x1=sorted((side*(width/2+FACE_X_AIR),side*(width/2+PROJECTION+TIP_AIR)))
        fields.append((station.x+x0-.4,station.x+x1+.4,y_outer-THICK-BACK_AIR,y_outer+1,
                       station.z-wing_span/2-END_AIR-SUPPORTED_END_AIR-.4,
                       station.z+wing_span/2+END_AIR+.4))
    return tuple(fields)
