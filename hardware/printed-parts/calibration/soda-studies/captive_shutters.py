"""Three captive port dust shutters, built from the back-top bed plane.

This reference addition pairs a solid-skin release gap with the support ladder.
It is not a production enclosure mechanism.
"""
from __future__ import annotations
import math
import cadquery as cq

CENTRES = (-63., 0., 63.)
GAPS = (.24,.48,.72)
WIDTH = 30.
TRAVEL = 26.
Y_WALL = 216.
Y_FACE = Y_WALL+3.35
HEIGHT = 140.
# The foot's final model plane lies on the normal .20 + n*.24 layer grid.
FOOT_BOTTOM = 89.88
FOOT_TOP = FOOT_BOTTOM + 3.36
LOWER_AIR = 1.44
SIDE_AIR = .35


def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))


def flag(cx):
    """One bed-start flag and a broad foot held by the two frame ledges."""
    width=WIDTH
    # First millimetre retracts the same-layer moving gap from bed squish.
    panel=box(cx-width/2,cx+width/2,Y_WALL+SIDE_AIR,Y_FACE,
              FOOT_BOTTOM,HEIGHT-1.)
    chamfer=(cq.Workplane('YZ',origin=(cx-width/2,0,0))
             .polyline([(Y_WALL+SIDE_AIR,HEIGHT-1.),
                        (Y_WALL+SIDE_AIR+.35,HEIGHT),
                        (Y_FACE-.35,HEIGHT),(Y_FACE,HEIGHT-1.)])
             .close().extrude(width).val())
    foot=box(cx-width/2,cx+width/2,Y_WALL+SIDE_AIR,Y_WALL+6.35,
             FOOT_BOTTOM,FOOT_TOP)
    # Touch areas and two raised symbols are outside the running foot.
    legend=(cq.Workplane('XY').text(f'{GAPS[CENTRES.index(cx)]:.2f}',4.,.48,
               font='Helvetica',kind='bold',halign='center',valign='center',
               combine=False).val().rotate((0,0,0),(1,0,0),-90)
            .translate((cx,Y_FACE-.01,115.)))
    return panel.fuse(chamfer,foot,legend).clean()


def frame(cx,gap):
    """Rooted frame; both closed ends stop the flag before it can escape."""
    xmin=cx-WIDTH/2-TRAVEL/2-SIDE_AIR
    xmax=cx+WIDTH/2+TRAVEL/2+SIDE_AIR
    bottom=FOOT_BOTTOM-gap-3.
    top=FOOT_TOP+LOWER_AIR
    # Roof and end columns stand on the same bed as the back-top and flags.
    # Their broad roots meet the native roof inside its rear corner rounds.
    roof=box(xmin-3.,xmax+3.,Y_WALL-10.,Y_WALL+9.7,HEIGHT-3.,HEIGHT)
    ends=[box(x-1.5,x+1.5,Y_WALL-10.,Y_WALL+9.7,bottom,HEIGHT)
          for x in (xmin-1.5,xmax+1.5)]
    lower=box(xmin,xmax,Y_WALL+4.,Y_WALL+9.7,top,top+3.)
    upper=box(xmin,xmax,Y_WALL-3.,Y_WALL+9.7,bottom,bottom+3.)
    outer=box(xmin,xmax,Y_WALL+6.70,Y_WALL+9.7,bottom,top+3.)
    stock=roof.fuse(*ends,lower,upper,outer)
    panel_room=box(xmin,xmax,Y_WALL, Y_FACE+SIDE_AIR,
                   FOOT_BOTTOM-gap,HEIGHT+1.)
    foot_room=box(xmin,xmax,Y_WALL,Y_WALL+6.70,
                  FOOT_BOTTOM-gap,FOOT_TOP+LOWER_AIR)
    return stock.cut(panel_room).cut(foot_room).clean()


def added_frames():
    return cq.Compound.makeCompound([frame(x,g) for x,g in zip(CENTRES,GAPS)])


def members():
    return {f'Q{round(g*100):02d}':flag(x) for x,g in zip(CENTRES,GAPS)}


def witnesses():
    out={}
    for x,g in zip(CENTRES,GAPS):
        out[f'Q{round(g*100):02d}']={
            'nominal_top_release_gap_mm':g,
            'nominal_lower_release_gap_mm':LOWER_AIR,
            'side_air_per_face_mm':SIDE_AIR,
            'travel_x_mm':TRAVEL,
            'break_in_handle':'Complete raised flag above its captive foot',
            'convention':'Z gap measured in manufacturing build direction; side air per face',
            'source_scope':'Reference port-dust-shutter addition; source appliance has no print-in-place parts',
            'foot_surface_world_z_mm':FOOT_BOTTOM,
            'cap_surface_world_z_mm':FOOT_BOTTOM-g,
            'world_foot_probe_mm':[x,Y_WALL+5.1,FOOT_BOTTOM],
            'world_cap_probe_mm':[x,Y_WALL+5.1,FOOT_BOTTOM-g],
            'initial_states':['Free off bed','Gently freed at intended handle','Fused'],
        }
    return out


def support_blockers():
    """Only the intended moving gaps; retain automatic supports elsewhere."""
    blockers=[]
    for x,g in zip(CENTRES,GAPS):
        # Clear exactly the swept running foot and its two intentional air bands.
        blockers.append(box(x-WIDTH/2-TRAVEL/2-SIDE_AIR,
                            x+WIDTH/2+TRAVEL/2+SIDE_AIR,
                            Y_WALL+.05,Y_WALL+6.65,
                            FOOT_BOTTOM-g-.05,FOOT_TOP+LOWER_AIR+.05))
    return blockers
