"""Dry structure for four permanent receivers and their fixed plumbing.

Coordinates share the enclosure frame. The receiver module owns the wet
geometry; this module owns flat keepers, their guides, factory locks and
stationary tee saddles. No customer operation reaches these parts.
"""
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'reference' / 'tee-connector'))
import pump_receiver as receiver
import tee_connector as tee
import stub_grip as stems
import dock_retention as retention

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
KEEPER_HALF_WIDTH = 12.0
KEEPER_Z = (-11.0, 18.75)
KEEPER_LIFT = 20.0
LOCK_Z = 14.0
LOCK_BORE_D = 3.5
LOCK_INSERT_D = 4.0
LOCK_INSERT_LENGTH = 4.0
LOCK_RELIEF = 1.25
LOCK_WASHER_OD = 7.0
LOCK_WASHER_ID = 3.2
LOCK_WASHER_T = .5
GUIDE_INNER_X = 9.25
GUIDE_OUTER_X = 15.25
GUIDE_Z = (-11.0, 8.5)
RECESS_Z = (-14.0, 40.0)
SUPPORT_LOCK_Z = 22.5
SUPPORT_POST_LIGAMENT = 3.0
SUPPORT_SEAT_AIR = 0.0
SUPPORT_BRIDGE_Z = (17.75, 27.25)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def ycyl(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))


def fused(parts):
    parts = tuple(parts)
    return parts[0].fuse(*parts[1:]).clean()


def support_lock_x(plate):
    """Frame locks align with the two columns between the fluid ports."""
    return tuple(x for x, _ in retention.column_stations(plate['holes']))


def keeper(wall_fore_y=0.0, x=0.0, z=0.0):
    y0,y1 = (wall_fore_y+y for y in receiver.KEEPER_Y)
    slab = box(x-KEEPER_HALF_WIDTH,x+KEEPER_HALF_WIDTH,y0,y1,
               z+KEEPER_Z[0],z+KEEPER_Z[1])
    r = receiver.KEEPER_SLOT_D/2
    notch = ycyl(r,x,z,y0-.1,y1+.1).fuse(
        box(x-r,x+r,y0-.1,y1+.1,z+KEEPER_Z[0]-.1,z))
    return slab.cut(notch).cut(ycyl(LOCK_BORE_D/2,x,z+LOCK_Z,y0-.1,y1+.1)).clean()


def wall_recess(plate):
    """Broad keeper access pocket with a 45-degree roof rising aft."""
    row = plate['holes'][0][1]
    x0,x1=plate['x0']+6.25,plate['x1']-6.25
    y0,y1=plate['fore_y']+receiver.WALL_THICKNESS,plate['wall_aft_y']+.1
    roof=row+RECESS_Z[1]
    pocket=box(x0,x1,y0,y1,row+RECESS_Z[0],roof)
    points=[cq.Vector(x0,y0,roof),cq.Vector(x0,y1,roof),
            cq.Vector(x0,y1,roof+y1-y0)]
    wire=cq.Wire.makePolygon(points+[points[0]])
    return pocket.fuse(cq.Solid.extrudeLinear(wire,[],cq.Vector(x1-x0,0,0))).clean()


def guides(wall_fore_y,x,z):
    back = wall_fore_y+receiver.WALL_THICKNESS
    slot_back = wall_fore_y+receiver.GROOVE_Y[1]
    stocks=[]
    for side in (-1,1):
        a,b = sorted((x+side*12.25,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,back,slot_back+3,z+GUIDE_Z[0],z+GUIDE_Z[1]))
        a,b = sorted((x+side*GUIDE_INNER_X,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,slot_back,slot_back+3,z+GUIDE_Z[0],z+GUIDE_Z[1]))
    # Stop under both uninterrupted plate wings; the U opening stays clear.
    for side in (-1,1):
        a,b=sorted((x+side*6.5,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,back,slot_back+3,z+GUIDE_Z[0]-3.35,z+GUIDE_Z[0]-.35))
    return fused(stocks)


def lock_cut(wall_fore_y,x,z):
    face=wall_fore_y+receiver.WALL_THICKNESS
    return ycyl(LOCK_INSERT_D/2,x,z+LOCK_Z,
                face-LOCK_INSERT_LENGTH-LOCK_RELIEF,face+.01)


def tee_saddle(wall_fore_y, x, z, center_y):
    """Fixed open-aft cradle on the two measured run collars.

    Two ties at Z +/-13.5 capture fixed collar stock, away from all three
    operating sleeves. Side webs join the permanent wall and keeper guides.
    The branch passes through the centre of this saddle during straight
    factory insertion from the interior.
    """
    near=center_y-11.5
    stock=box(x-13.5,x+13.5,near,center_y,z-18.25,z+18.25)
    trunk=cq.Solid.makeCylinder(8.5,36.7,cq.Vector(x,center_y,z-18.35),cq.Vector(0,0,1))
    stock=stock.cut(trunk).cut(ycyl(8.5,x,z,near-.1,center_y+.1))
    for dz in (-13.5,13.5):
        stock=stock.cut(box(x-10.5,x+10.5,near-.1,center_y+.1,
                            z+dz-1.75,z+dz+1.75))
    parts=[stock]
    for side in (-1,1):
        a,b=sorted((x+side*12.25,x+side*15.25))
        parts.append(box(a,b,wall_fore_y+receiver.WALL_THICKNESS,center_y,
                         z-11,z+8.5))
    return fused(parts)


def fixed_features(plate):
    fore=plate['fore_y']
    stocks=[]
    cuts=[wall_recess(plate)]
    for (x,z),center_y in zip(plate['holes'],plate['fixed_tee_center_y']):
        stocks.extend((guides(fore,x,z),tee_saddle(fore,x,z,center_y)))
        cuts.extend((receiver.receiver_wall_cut(fore,x,z),lock_cut(fore,x,z)))
    row=plate['holes'][0][1]
    face=fore+receiver.REAR_SUPPORT_Y[0]-SUPPORT_SEAT_AIR
    half=LOCK_INSERT_D/2+SUPPORT_POST_LIGAMENT
    for x in support_lock_x(plate):
        stocks.append(box(x-half,x+half,fore+receiver.WALL_THICKNESS,face,
                          row+SUPPORT_LOCK_Z-half,row+SUPPORT_LOCK_Z+half))
        cuts.append(ycyl(2,x,row+SUPPORT_LOCK_Z,
                         face-LOCK_INSERT_LENGTH-LOCK_RELIEF,face+.01))
    return stocks,cuts


def parts(plate, *, installed=True):
    out={}
    for name,(x,z) in zip(STATIONS,plate['holes']):
        out['pump-receiver-'+name]=receiver.build_receiver(plate['fore_y'],x,z,installed=installed)
        out['pump-receiver-keeper-'+name]=keeper(plate['fore_y'],x,z)
    out['pump-receiver-rear-support']=rear_support(plate)
    return out


def rear_support(plate):
    """One removable four-hole bar supports the permanent factory sockets.

    It installs after the receiver flanges and flat keepers, before tails and
    tees. No retaining flange has to pass through this closed support.
    """
    row=plate['holes'][0][1]
    y0,y1=(plate['fore_y']+y for y in receiver.REAR_SUPPORT_Y)
    span=receiver.WALL_BORE_D/2+3
    pieces=[box(plate['holes'][0][0]-span,plate['holes'][-1][0]+span,
                y0,y1,row+SUPPORT_BRIDGE_Z[0],row+SUPPORT_BRIDGE_Z[1])]
    for x,z in plate['holes']:
        pieces.append(ycyl(span,x,z,y0,y1).cut(
            receiver.rear_support_cut(plate['fore_y'],x,z)))
        for side in (-1,1):
            a,b=sorted((x+side*3.75,x+side*6.75))
            pieces.append(box(a,b,y0,y1,z+6,z+27))
    stock=fused(pieces)
    for x in support_lock_x(plate):
        stock=stock.cut(ycyl(LOCK_BORE_D/2,x,row+SUPPORT_LOCK_Z,y0-.1,y1+.1))
    return stock.clean()


def tube_setting_jig(plate, cartridge_face_y):
    """Factory gauge seats on the cartridge back and catches the four tube tips.

    Four open channels admit the stubs; the blind ends are the tip datum.
    The tool is removed before connecting the cartridge to the machine.
    """
    row=plate['holes'][0][1]
    tip=plate['fore_y']+receiver.CUSTOMER_TIP_Y
    body=box(plate['holes'][0][0]-8,plate['holes'][-1][0]+8,
             cartridge_face_y,tip+3,row-8,row+8)
    for x,z in plate['holes']:
        # Full axial bore with open top, ending at the tube's cut-face datum.
        bore=ycyl(3.5,x,z,cartridge_face_y-.1,tip)
        opening=box(x-3.5,x+3.5,cartridge_face_y-.1,tip,z,row+8.1)
        body=body.cut(bore.fuse(opening))
        guard_half=stems.GUARD_OD/2+.25
        body=body.cut(box(x-guard_half,x+guard_half,
                          cartridge_face_y-.1,stems.GUARD_AFT_Y+.25,
                          row-8.1,row+8.1))
    # The two magnet guards also project behind the retained cartridge plane.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+retention.SIDE_KEY+retention.STRUCTURAL_STOCK+.25
        end=cartridge_face_y+retention.MOVING_POLE_PROJECTION-retention.GUARD_POLE_PROUD+.25
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,end,row-9,row+9))
    return body.clean()
