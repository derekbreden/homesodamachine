"""Dry structure for four permanent receivers and their fixed plumbing.

Coordinates share the enclosure frame. The receiver module owns the wet
geometry; this module owns the flat keepers, their wall guides and locks, and
the one return block that seats all four compound returns. No customer
operation reaches these parts.
"""
from pathlib import Path
import sys
import json
from functools import lru_cache

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'printed-parts' / 'cadlib'))
import fits
import pump_receiver as receiver
import dock_retention as retention
import fixed_returns as plumbing
import pump_return as returned
sys.path.insert(0,str(HERE.parent/"valve-tray"))
import valve_tray

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
KEEPER_HALF_WIDTH = 12.0
KEEPER_Z = (-11.0, 19.5)
KEEPER_BOSS_THICKNESS = 5.0
KEEPER_BOSS_RADIUS = 5.3
KEEPER_COUNTERBORE_DEPTH = 3.75
KEEPER_COUNTERBORE_D = 7.3
KEEPER_WING_X = 14.0
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

# The return block: one solid under the front-top's seam that all four returns
# snap down into. Its top face is the front-top's own print bed plane and it is
# printed on that face; each seat's arcs stand within 22 degrees of vertical there.
# The slots open its underside, so every wall beside a seat is a wide one.
BLOCK_SIDE = 7.0
BLOCK_SEAT_AIR = fits.slip
BLOCK_LIP = .20
BLOCK_FLOOR_BREAK = 1.0
BLOCK_TERMINAL_AIR = 3.5
BLOCK_COLLET_AIR = 1.10
BLOCK_REAR_AIR = 1.0
BLOCK_SCREW_X = (-48.0, 0.0, 48.0)
BLOCK_SCREW_LENGTH = 12.0
BLOCK_SCREW_ENGAGEMENT = 4.0
BLOCK_INSERT_RELIEF = 1.75
BLOCK_CLEARANCE_D = 3.4
BLOCK_COUNTERBORE_D = 6.5
BLOCK_SCREW_WALL = 3.0
BLOCK_BOSS_HALF = 5.5
BLOCK_BOSS_DEPTH = 3.1
BLOCK_BOSS_HEIGHT = 7.5
OCCUPIED_BODY_R = plumbing.OCCUPIED_CUFF_OD/2


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def ycyl(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))


def ycrown(radius,x,z,y0,y1,*,toward_x=0):
    """Full round screw/insert room with a tangent45degree print crown."""
    a=radius/2**.5
    if toward_x:
        points=[(x+toward_x*a,z-a),(x+toward_x*a,z+a),(x+toward_x*radius*2**.5,z)]
    else:points=[(x-a,z+a),(x+a,z+a),(x,z+radius*2**.5)]
    vertices=[cq.Vector(px,y0,pz) for px,pz in points]
    wire=cq.Wire.makePolygon(vertices+[vertices[0]])
    return ycyl(radius,x,z,y0,y1).fuse(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,y1-y0,0))).clean()


def fused(parts):
    parts = tuple(parts)
    return (parts[0].fuse(*parts[1:]) if len(parts)>1 else parts[0]).clean()


def keeper(wall_fore_y=0.,x=0.,z=0.,*,side=1,clamped=True):
    """Flat axial keeper with a front-driven lock and five-mm insert boss."""
    y0,y1=(wall_fore_y+y for y in receiver.KEEPER_Y)
    slab=box(x-12,x+12,y0,y1,z+KEEPER_Z[0],z+KEEPER_Z[1])
    a,b=sorted((x+side*12,x+side*KEEPER_WING_X))
    slab=slab.fuse(box(a,b,y0,y1,z+8.75,z+KEEPER_Z[1]))
    rear=y0+KEEPER_BOSS_THICKNESS
    r=receiver.KEEPER_SLOT_D/2
    notch=ycyl(r,x,z,y0-.1,rear+.1).fuse(box(x-r,x+r,y0-.1,rear+.1,z+KEEPER_Z[0]-.1,z))
    cx=x+side*8.5
    boss=ycyl(KEEPER_BOSS_RADIUS,cx,z+LOCK_Z,y0,rear)
    result=slab.fuse(boss).cut(notch).cut(ycyl(LOCK_INSERT_D/2,cx,z+LOCK_Z,y0-.1,rear+.1)).clean()
    return result if clamped else result.translate((0,fits.sliding_extra,0))


def keeper_side(x):
    return 1 if x<-50 or 0<x<50 else -1


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
    """Front-driven keeper screw room; the insert belongs to the keeper."""
    return ycrown(KEEPER_COUNTERBORE_D/2,x,z+LOCK_Z,wall_fore_y-.1,wall_fore_y+KEEPER_COUNTERBORE_DEPTH).fuse(
        ycrown(LOCK_BORE_D/2,x,z+LOCK_Z,wall_fore_y-.1,wall_fore_y+receiver.KEEPER_Y[0]+.01)).clean()


def _key_seat_cut(wall_fore_y,x,z):
    pieces=[]
    for sign in (-1,1):
        cx=x+sign*(receiver.KEY_ROOT_X+receiver.KEY_OUTER_X)/2
        half=3.+fits.running
        top=z+receiver.KEY_TOP_Z+fits.running*2**.5
        # End the crown at the guide's open inner face. An apex centred on
        # the ear leaves a triangular skin beside that face.
        apex=x+sign*GUIDE_INNER_X
        roof=top+abs(cx-apex)
        pts=[(cx-half,z+receiver.KEY_BASE_Z-fits.running),(cx+half,z+receiver.KEY_BASE_Z-fits.running),
             (cx+half,top-half),(apex,roof),(cx-half,top-half)]
        y0=wall_fore_y+receiver.REAR_COLLAR_Y[0]-.01
        y1=wall_fore_y+receiver.REAR_COLLAR_Y[1]+3
        wire=cq.Wire.makePolygon([cq.Vector(a,y0,b) for a,b in pts]+[cq.Vector(pts[0][0],y0,pts[0][1])])
        pieces.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,y1-y0,0)))
    return fused(pieces)


def aft_tray(plate):
    """The valve tray the returns land under: its plane row and (front, back) Y."""
    target=next(iter(plumbing.layouts(plate).values()))['return']['target']['point'][1]
    row=min(plate['valve_trays'],key=lambda r:abs(r[0]-target))
    plane,sign,_seats=row
    face=plane-sign*valve_tray.SEAT
    return row,tuple(sorted((face,face-sign*valve_tray.THICK)))


def block_screws(plate):
    """The return block's vertical M3 stations, a nominal wall ahead of its back face."""
    _row,(_front,back)=aft_tray(plate)
    y=back-BLOCK_REAR_AIR-BLOCK_COUNTERBORE_D/2-BLOCK_SCREW_WALL
    return tuple((x,y) for x in BLOCK_SCREW_X)


def _channel(plate,x,top,front):
    """One return's channel: a straight slot through the block, narrower than the
    relaxed TPU body, and a round seat along the return's own path. The seat
    cuts into both slot walls, so the body springs out into it."""
    layout=plumbing.layouts(plate)[str(x)]['return']
    local=returned.local_layout(layout)
    origin,_n,h=returned.frame(layout)
    r=OCCUPIED_BODY_R+BLOCK_SEAT_AIR
    segments=local['flow_segments']
    a=cq.Vector(*segments[0]['start_mm']);d=cq.Vector(*segments[0]['start_tangent']).normalized()
    # The link continues the seat forward of the block's front face.
    reach=max(0.,(a.y-(front-origin.y)/h.y)/abs(d.y))+2*r
    lead=a-d*reach
    b=cq.Vector(*segments[-1]['end_mm'])
    rise=cq.Vector(b.x,b.y,top-origin.z+2*r)
    path=[cq.Edge.makeLine(lead,a)]
    for s in segments:
        p0,p1=cq.Vector(*s['start_mm']),cq.Vector(*s['end_mm'])
        path.append(cq.Edge.makeThreePointArc(p0,cq.Vector(*s['midpoint_mm']),p1) if s['kind']=='arc' else cq.Edge.makeLine(p0,p1))
    path.append(cq.Edge.makeLine(b,rise))
    seat=cq.Solid.sweep(cq.Wire.makeCircle(r,lead,d),[],cq.Wire.assembleEdges(path),makeSolid=True,isFrenet=False)
    # Front face to the outlet's back, top face to underside.
    w=returned.BODY_OD/2-BLOCK_LIP
    slot=box(-w,w,lead.y,b.y+r,lead.z-200,rise.z)
    envelope=returned.geometry(layout,installed=True)['envelope']
    return returned.to_world(fused((seat,slot,envelope)),layout)


@lru_cache(maxsize=4)
def _cached_block(declaration):
    plate=json.loads(declaration)
    top=plate['fixture_print_bed_z']
    row,(_tray_front,tray_back)=aft_tray(plate)
    plane,sign,_seats=row
    # Ahead of the block stand the aft coils' spade receptacles.
    front=plane+sign*valve_tray._valve.spade_z_center+BLOCK_TERMINAL_AIR
    back=tray_back-BLOCK_REAR_AIR
    r=OCCUPIED_BODY_R+BLOCK_SEAT_AIR
    channels={x:_channel(plate,x,top,front) for x,_z in plate['holes']}
    span=box(-300,300,front,back,0,400)
    reach=max(max(abs(b.xmin),abs(b.xmax)) for b in
              (c.intersect(span).BoundingBox() for c in channels.values()))+BLOCK_SIDE
    layouts=plumbing.layouts(plate)
    def floor(xs):
        return min(layouts[str(x)]['return']['minimum_flow_centerline_z_mm'] for x in xs)-r+BLOCK_FLOOR_BREAK
    inner=[x for x,_z in plate['holes'] if abs(x)<50];outer=[x for x,_z in plate['holes'] if abs(x)>=50]
    deep=max(abs(x) for x in inner)+r+BLOCK_SIDE
    body=box(-reach,reach,front,back,floor(outer),top).fuse(box(-deep,deep,front,back,floor(inner),top))
    room=max(valve_tray._valve.collet_ear_radius,valve_tray._valve.collet_clip_radius,
             valve_tray._valve.collet_radius)+BLOCK_COLLET_AIR
    for x,channel in channels.items():
        body=body.cut(channel)
        port=layouts[str(x)]['return']['target']['point']
        collet=port[2]-BLOCK_COLLET_AIR
        if collet<top:
            # The outlet's collet keeps its air: a 45-degree countersink round the seat.
            start=collet-(room-r)
            body=body.cut(cq.Solid.makeCone(r,r+top+1-start,top+1-start,
                                            cq.Vector(port[0],port[1],start),cq.Vector(0,0,1)))
    clamp=BLOCK_SCREW_LENGTH-BLOCK_SCREW_ENGAGEMENT
    low=min(floor(inner),floor(outer))-1
    for x,y in block_screws(plate):
        body=body.cut(cq.Solid.makeCylinder(BLOCK_CLEARANCE_D/2,top+1-low,cq.Vector(x,y,low),cq.Vector(0,0,1)))
        body=body.cut(cq.Solid.makeCylinder(BLOCK_COUNTERBORE_D/2,top-clamp-low,cq.Vector(x,y,low),cq.Vector(0,0,1)))
    return body.clean()


def return_block(plate):
    return _cached_block(json.dumps(plate,sort_keys=True))


def fixed_features(plate):
    """Wall seats and flat keepers, outlet reliefs, and the block's insert bosses."""
    fore=plate['fore_y'];stocks=[];cuts=[wall_recess(plate)]
    bed=plate['fixture_print_bed_z']
    for x,z in plate['holes']:
        side=keeper_side(x)
        stocks.append(guides(fore,x,z,plate['wall_aft_y']))
        stocks.append(ycyl(4.,x+side*8.5,z+LOCK_Z,fore+receiver.WALL_THICKNESS,fore+receiver.KEEPER_Y[0]))
        cuts.extend((receiver.receiver_wall_cut(fore,x,z),
                     lock_cut(fore,x+side*8.5,z),
                     _key_seat_cut(fore,x,z)))
        # Continue the existing valve port channel down the tray foot. The
        # occupied exterior heel has the same fixed outlet axis and must not
        # bear on the tray; this is an open-to-bed relief, not a blind pocket.
        outlet=plumbing.layouts(plate)[str(x)]['return']["output"]["point"]
        cuts.append(cq.Solid.makeCylinder(valve_tray._valve.port_radius+valve_tray.PORT_SLIP,
                    outlet[2]+3.0-bed,cq.Vector(outlet[0],outlet[1],bed-.01),cq.Vector(0,0,1)))
    _row,(tray_front,_back)=aft_tray(plate)
    for x,y in block_screws(plate):
        stocks.append(box(x-BLOCK_BOSS_HALF,x+BLOCK_BOSS_HALF,tray_front-BLOCK_BOSS_DEPTH,tray_front+.01,
                          bed,bed+BLOCK_BOSS_HEIGHT))
        cuts.append(cq.Solid.makeCylinder(LOCK_INSERT_D/2,BLOCK_SCREW_ENGAGEMENT+BLOCK_INSERT_RELIEF+.01,
                                          cq.Vector(x,y,bed-.01),cq.Vector(0,0,1)))
    return stocks,cuts


def parts(plate,*,installed=True):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)]
        out['pump-receiver-'+name]=receiver.build_receiver(plate['fore_y'],x,z,installed=installed,junction=data['junction'])
        out['pump-receiver-keeper-'+name]=keeper(plate['fore_y'],x,z,side=keeper_side(x))
        out['pump-return-'+name]=returned.build_return(data['return'],installed=installed)
    out['pump-return-block']=return_block(plate)
    return out


def part_color(name):
    wet=(name.startswith(('pump-receiver-','pump-return-'))
         and not name.startswith(('pump-receiver-keeper-','pump-return-block')))
    return receiver.COLOR if wet else cq.Color(.16,.16,.16)


def manufacturing_parts(plate):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)];local=receiver._local_junction(data['junction'],(x,plate['fore_y'],z))
        keep=keeper(0,0,0,side=keeper_side(x)).rotate((0,0,0),(1,0,0),90)
        keep=keep.translate((0,0,-keep.BoundingBox().zmin))
        rows={'pump-receiver-'+name:receiver.print_solid(junction=local),'pump-receiver-keeper-'+name:keep,
              'pump-return-'+name:returned.print_solid(data['return'])}
        for part,shape in rows.items():out['enclosure-'+part]={'shape':shape,'color':part_color(part)}
    # The block prints on its top face, the front-top's own bed plane.
    block=return_block(plate).rotate((0,0,0),(1,0,0),180)
    block=block.translate((0,0,-block.BoundingBox().zmin))
    out['enclosure-pump-return-block']={'shape':block,'color':part_color('pump-return-block')}
    return out


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
    # The two moving pole columns stand proud of the cartridge back to the wall face.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+1.0
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,plate['fore_y']+.75,row-9,row+9))
    return body.clean()
