"""Accepted face-up display cover and its receiver in display-local coordinates.

X is across the display, Y runs up it, and Z points out of the visible face.
The cover back and both wings share a bed plane. Pocket exits follow world
print-down so supports leave through the empty display storey.
"""
import math

import cadquery as cq

from _swept_top import rounded_prism

COVER_X, COVER_Y, CORNER_R = 125.5, 83.0, 6.0
WINDOW_X, WINDOW_Y, WINDOW_R = 107.5, 71.0, 2.5
THICK, WING_THICK, WING_REACH, WING_SPAN, WING_END_R = 3.84, 1.44, 3.60, 70.0, .60
BODY_X_AIR, BODY_Y_AIR, TIP_AIR, END_AIR, BEARING_AIR = .30, .15, .55, .15, .60
BACK = -THICK
GLASS_SEAT = BACK-2.0
LIP_THICK = THICK-WING_THICK-BEARING_AIR
ANGLE = 30.0


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def wing(side):
    return rounded_prism(WING_REACH+1, WING_SPAN, WING_END_R, BACK, BACK+WING_THICK).translate(
        (side*(COVER_X/2+(WING_REACH-1)/2),0,0))


def cover():
    bezel=rounded_prism(COVER_X,COVER_Y,CORNER_R,BACK,0)
    window=rounded_prism(WINDOW_X,WINDOW_Y,WINDOW_R,BACK-1,1)
    return bezel.fuse(wing(-1),wing(1)).cut(window).clean()


def support_exits(depth, inset=0., roof_drop=0.):
    roof=BACK+WING_THICK+BEARING_AIR-roof_drop
    shift_y=-depth*math.tan(math.radians(ANGLE))
    exits=[]
    for side in (-1,1):
        xa,xb=sorted((side*(COVER_X/2-.1),side*(COVER_X/2+WING_REACH+TIP_AIR)))
        xa,xb=xa+inset,xb-inset
        y0,y1=-WING_SPAN/2-END_AIR+inset,WING_SPAN/2+END_AIR-inset
        wire=cq.Wire.makePolygon([cq.Vector(x,y,roof) for x,y in
                                 ((xa,y0),(xb,y0),(xb,y1),(xa,y1),(xa,y0))])
        exits.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,shift_y,-depth)))
    return exits


def cuts(pcb_depth, exit_depth):
    inset=rounded_prism(COVER_X+2*BODY_X_AIR,COVER_Y+2*BODY_Y_AIR,
                        CORNER_R+BODY_Y_AIR,BACK,1)
    glass=rounded_prism(113.8,77.3,2.65,GLASS_SEAT,1)
    pcb=box(.5-106.3/2,.5+106.3/2,-1-69.3/2,-1+69.3/2,-pcb_depth,1)
    result=inset.fuse(glass,pcb)
    for side in (-1,1):
        xa,xb=sorted((side*(COVER_X/2-.1),side*(COVER_X/2+WING_REACH+TIP_AIR)))
        result=result.fuse(box(xa,xb,-WING_SPAN/2-END_AIR,WING_SPAN/2+END_AIR,
                               BACK,BACK+WING_THICK+BEARING_AIR))
    return result.fuse(*support_exits(exit_depth)).clean()
