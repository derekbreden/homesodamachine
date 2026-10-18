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
sys.path.insert(0, str(HW / 'printed-parts' / 'cadlib'))
import fits
import pump_receiver as receiver
import tee_connector as tee
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
GUIDE_OUTER_X = 16.4
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


def _bed_corbel(x0, x1, y0, y1, top, bed):
    """45-degree underside rising aft, clipped at the part's print bed."""
    points=[cq.Vector(x0,y0,top-(y1-y0)),cq.Vector(x0,y1,top),
            cq.Vector(x0,y0,top)]
    wire=cq.Wire.makePolygon(points+[points[0]])
    raw=cq.Solid.extrudeLinear(wire,[],cq.Vector(x1-x0,0,0))
    return raw.intersect(box(x0,x1,y0,y1,bed,top+.1)).clean()


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
    x0,x1=plate['x0']+6.0,plate['x1']-6.0
    y0,y1=plate['fore_y']+receiver.WALL_THICKNESS,plate['wall_aft_y']+.1
    roof=row+RECESS_Z[1]
    pocket=box(x0,x1,y0,y1,row+RECESS_Z[0],roof)
    points=[cq.Vector(x0,y0,roof),cq.Vector(x0,y1,roof),
            cq.Vector(x0,y1,roof+y1-y0)]
    wire=cq.Wire.makePolygon(points+[points[0]])
    return pocket.fuse(cq.Solid.extrudeLinear(wire,[],cq.Vector(x1-x0,0,0))).clean()


def guides(wall_fore_y,x,z,wall_aft_y=None):
    back = wall_fore_y+receiver.WALL_THICKNESS
    slot_back = wall_fore_y+receiver.GROOVE_Y[1]
    rear = slot_back+3 if wall_aft_y is None else wall_aft_y
    stocks=[]
    for side in (-1,1):
        a,b = sorted((x+side*12.25,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,back,rear,z+GUIDE_Z[0]-.35,z+GUIDE_Z[1]))
        a,b = sorted((x+side*GUIDE_INNER_X,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,slot_back,rear,z+GUIDE_Z[0]-.35,z+GUIDE_Z[1]))
    # Stop under both uninterrupted plate wings; the U opening stays clear.
    for side in (-1,1):
        a,b=sorted((x+side*6.5,x+side*GUIDE_OUTER_X))
        stocks.append(box(a,b,back,rear,z+GUIDE_Z[0]-3.35,z+GUIDE_Z[0]-.35))
    return fused(stocks)


def lock_cut(wall_fore_y,x,z):
    """Dry through-pilot for the keeper's full-length short M3 insert."""
    face=wall_fore_y+receiver.WALL_THICKNESS
    return ycyl(LOCK_INSERT_D/2,x,z+LOCK_Z,
                wall_fore_y-.1,face+.01)


def tee_saddle(wall_fore_y, x, z, center_y, *, side_limits=None, outer_side=0,
               print_bed_z=None):
    """Fixed open-aft cradle on the two measured run collars.

    Two ties at Z +/-13.5 capture fixed collar stock, away from all three
    operating sleeves. The 4.25 mm side webs and a lower floor join the
    permanent wall and keeper guides. The outer two saddles stop at the
    enclosure's slide-channel plane and omit the rail-crossing side web.
    Tie heads clock fore of the saddle; their bands surround its two rails
    together with the tee's fixed collar.
    The branch passes through the centre of this saddle during straight
    factory insertion from the interior.
    Each outboard saddle has an open outer side at branch-port height.
    Both tie-band rails remain complete. The floor and side-arm undersides
    rise at 45 degrees from the print bed. The lower collar's tie tunnel
    passes through added side-arm corbel stock and leaves the rails intact.
    """
    near,aft=center_y-12.0,center_y-3.0
    radius=tee.BARREL_R+.25
    end=tee.RUN_FIXED_END-.25
    stock=box(x-13.5,x+13.5,near,aft,z-end,z+end)
    trunk=cq.Solid.makeCylinder(radius,2*(end+.1),
                                cq.Vector(x,center_y,z-end-.1),cq.Vector(0,0,1))
    stock=stock.cut(trunk).cut(ycyl(radius,x,z,near-.1,aft+.1))
    for dz in (-13.5,13.5):
        stock=stock.cut(box(x-8,x+8,near-.1,aft+.1,
                            z+dz-1.75,z+dz+1.75))
    if outer_side:
        a,b=sorted((x,x+outer_side*20))
        stock=stock.cut(box(a,b,near-.1,aft+.1,z-8.75,z+8.75))
    parts=[stock,box(x-13.5,x+13.5,wall_fore_y+receiver.WALL_THICKNESS,
                     center_y-9.0,z-end-3,z-end)]
    if print_bed_z is not None:
        y0,y1=wall_fore_y+receiver.WALL_THICKNESS,center_y-9.0
        bottom=z-end-3
        parts.append(_bed_corbel(x-13.5,x+13.5,y0,y1,bottom,print_bed_z))
        # Continue the underside beneath the lower collar, retaining its
        # complete vertical trunk opening for the tee and run tube.
        corbel=_bed_corbel(x-13.5,x+13.5,center_y-9.0,aft,
                           z-end,print_bed_z)
        trunk=cq.Solid.makeCylinder(radius,6.2,
                                    cq.Vector(x,center_y,z-end-6.1),
                                    cq.Vector(0,0,1))
        parts.append(corbel.cut(trunk))
    for side in (-1,1):
        if side==outer_side:
            continue
        a,b=sorted((x+side*9.25,x+side*13.5))
        parts.append(box(a,b,wall_fore_y+receiver.GROOVE_Y[1],aft,
                         z-11.35,z+8.5))
        if print_bed_z is not None:
            corbel=_bed_corbel(a,b,wall_fore_y+receiver.GROOVE_Y[1],aft,
                               z-11.35,print_bed_z)
            # Open only the new corbel for the lower strap. The original
            # fixed-collar rails and the full arm above remain unchanged.
            tunnel=box(x-20,x+20,center_y-15.25,center_y-11.75,
                       z-15.25,z-11.75)
            parts.append(corbel.cut(tunnel))
    joined=fused(parts)
    if side_limits is not None:
        bounds=joined.BoundingBox()
        joined=joined.intersect(box(*side_limits,bounds.ymin-1,bounds.ymax+1,
                                    bounds.zmin-1,bounds.zmax+1)).clean()
    return joined


def fixed_features(plate):
    fore=plate['fore_y']
    stocks=[]
    cuts=[wall_recess(plate)]
    for index,((x,z),center_y) in enumerate(zip(plate['holes'],plate['fixed_tee_center_y'])):
        outer_side=-1 if index==0 else 1 if index==len(plate['holes'])-1 else 0
        stocks.extend((guides(fore,x,z,plate['wall_aft_y']),
                       tee_saddle(fore,x,z,center_y,
                                  side_limits=plate['tee_saddle_x_limits'],
                                  outer_side=outer_side,
                                  print_bed_z=plate['z0']+fits.supported_surface)))
        cuts.extend((receiver.receiver_wall_cut(fore,x,z),lock_cut(fore,x,z)))
    row=plate['holes'][0][1]
    face=fore+receiver.REAR_SUPPORT_Y[0]-SUPPORT_SEAT_AIR
    half=max(LOCK_INSERT_D/2+SUPPORT_POST_LIGAMENT,
             retention.SLOT_HALF+retention.SIDE_KEY+retention.STRUCTURAL_STOCK)
    for x,z in retention.column_stations(plate['holes']):
        bottom=row+RECESS_Z[0]
        top=row+SUPPORT_LOCK_Z+LOCK_INSERT_D/2+SUPPORT_POST_LIGAMENT
        stocks.append(box(x-half,x+half,fore+receiver.WALL_THICKNESS,face,
                          bottom,top))
        cuts.append(ycyl(LOCK_INSERT_D/2,x,row+SUPPORT_LOCK_Z,
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
    # The two magnet guards also project behind the retained cartridge plane.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+retention.SIDE_KEY+retention.STRUCTURAL_STOCK+.25
        end=cartridge_face_y+max(3.0,retention.MOVING_POLE_PROJECTION-retention.GUARD_POLE_PROUD+.25)
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,end,row-9,row+9))
    return body.clean()
