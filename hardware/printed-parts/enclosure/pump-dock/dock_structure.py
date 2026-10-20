"""Dry structure for four permanent receivers and their fixed plumbing.

Coordinates share the enclosure frame. The receiver module owns the wet
geometry; this module owns the flat keepers, the wall bays they slide in, and
the one return block that seats all four compound returns. No customer
operation reaches these parts.

Each keeper is a flat PET-GF plate that slides up its slot behind the wall
from front-top's seam face while front-top lies inverted, until each receiver
neck snaps through the keyhole's mouth into its grip. The slot's two faces
back it in Y; the TPU neck holds it in X and Z. The magnet column between each
pump's two ports divides the wall into three bays: one keeper for each outer
receiver and one for the inner pair.
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
# Keepers by the receivers they hold: one per outer receiver, one for the inner pair.
KEEPERS = {'west': ('west-outer',), 'middle': ('west-inner', 'east-inner'),
           'east': ('east-outer',)}
# Plate reach past each held receiver axis; the slot keeps the sliding allowance past it.
KEEPER_REACH = 12.0
# The keeper's crown stands this far over the receiver axis, three millimetres over its grip.
KEEPER_CROWN = 9.0
# Its foot stands this far inside front-top's bed face, where the thumb pushes it home.
KEEPER_BED_AIR = fits.running
# The receiver bay round each rear collar and branch root: radial room and floor.
BAY_HALF = receiver.COLLAR_OD / 2 + 0.5
BAY_FLOOR = 12.0
# The bay's ceiling stands three millimetres over the keeper's crown at the wall face, room for
# the factory tool that presses a keeper back down off its necks, and rises 45 degrees aft.
BAY_ROOF = KEEPER_CROWN + 3.0

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
BLOCK_INSERT_D = 4.0
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


def fused(parts):
    parts = tuple(parts)
    return (parts[0].fuse(*parts[1:]) if len(parts)>1 else parts[0]).clean()


def keeper_groups(plate):
    """Each keeper's held receiver axes and their common row height."""
    xs = dict(zip(STATIONS, (x for x, _z in plate['holes'])))
    row = plate['holes'][0][1]
    return {name: ([xs[st] for st in held], row) for name, held in KEEPERS.items()}


def keeper(plate, name):
    """One flat keeper in place: plate from the seam face to its crown, a keyhole per neck."""
    xs, row = keeper_groups(plate)[name]
    fore = plate['fore_y']
    y0, y1 = (fore + y for y in receiver.KEEPER_Y)
    bed = plate['fixture_print_bed_z'] + KEEPER_BED_AIR
    body = box(min(xs) - KEEPER_REACH, max(xs) + KEEPER_REACH, y0, y1, bed, row + KEEPER_CROWN)
    for x in xs:
        mouth = receiver.NECK_MOUTH_W / 2
        body = body.cut(ycyl(receiver.NECK_GRIP_D / 2, x, row, y0 - .1, y1 + .1)
                        .fuse(box(x - mouth, x + mouth, y0 - .1, y1 + .1, row, row + KEEPER_CROWN + 1)))
    return body.clean()


def _yz_prism(x0, x1, points):
    wire = cq.Wire.makePolygon([cq.Vector(x0, y, z) for y, z in points], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(x1 - x0, 0, 0))


def keeper_bays(plate):
    """Each keeper's slot from the seam face and each receiver's bay, under one 45-degree roof."""
    fore, aft = plate['fore_y'], plate['wall_aft_y'] + .1
    bed = plate['fixture_print_bed_z'] - .01
    face = fore + receiver.KEEPER_SLOT_Y[0]
    back = fore + receiver.KEEPER_SLOT_Y[1]
    cuts = []
    for xs, row in keeper_groups(plate).values():
        roof = row + BAY_ROOF
        slide = fits.running
        cuts.append(_yz_prism(min(xs) - KEEPER_REACH - slide, max(xs) + KEEPER_REACH + slide,
                              [(face, bed), (back, bed), (back, roof + back - face), (face, roof)]))
        for x in xs:
            cuts.append(_yz_prism(x - BAY_HALF, x + BAY_HALF,
                                  [(face, row - BAY_FLOOR), (aft, row - BAY_FLOOR),
                                   (aft, roof + aft - face), (face, roof)]))
    return fused(cuts)


def keeper_backing(plate):
    """Per keeper, the wall stock behind its slot that takes the receivers' aft load:
    [x0, x1, y0, y1, z0, z1] from the slot's back face to the wall's aft face."""
    fore, bed = plate['fore_y'], plate['fixture_print_bed_z']
    out = {}
    for name, (xs, row) in keeper_groups(plate).items():
        reach = KEEPER_REACH + fits.running
        out[name] = [min(xs) - reach, max(xs) + reach, fore + receiver.KEEPER_SLOT_Y[1],
                     plate['wall_aft_y'], bed, row + BAY_ROOF]
    return out


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
    """Wall bores and keeper bays, outlet reliefs, and the block's insert bosses."""
    fore=plate['fore_y'];stocks=[];cuts=[keeper_bays(plate)]
    bed=plate['fixture_print_bed_z']
    for x,z in plate['holes']:
        cuts.append(receiver.receiver_wall_cut(fore,x,z))
        # Continue the existing valve port channel down the tray foot. The
        # occupied exterior heel has the same fixed outlet axis and must not
        # bear on the tray; this is an open-to-bed relief, not a blind pocket.
        outlet=plumbing.layouts(plate)[str(x)]['return']["output"]["point"]
        cuts.append(cq.Solid.makeCylinder(valve_tray._valve.port_radius+valve_tray.PORT_SLIP,
                    outlet[2]+3.0-bed,cq.Vector(outlet[0],outlet[1],bed-.01),cq.Vector(0,0,1)))
    _row,(tray_front,_back)=aft_tray(plate)
    depth=BLOCK_SCREW_ENGAGEMENT+BLOCK_INSERT_RELIEF
    for x,y in block_screws(plate):
        stocks.append(box(x-BLOCK_BOSS_HALF,x+BLOCK_BOSS_HALF,tray_front-BLOCK_BOSS_DEPTH,tray_front+.01,
                          bed,bed+BLOCK_BOSS_HEIGHT))
        # Each insert pilot ends in a 45-degree cone over its relief, a roof the bed-up print draws.
        cuts.append(cq.Solid.makeCylinder(BLOCK_INSERT_D/2,depth+.01,cq.Vector(x,y,bed-.01),cq.Vector(0,0,1))
                    .fuse(cq.Solid.makeCone(BLOCK_INSERT_D/2,0.,BLOCK_INSERT_D/2,cq.Vector(x,y,bed+depth),cq.Vector(0,0,1))))
    return stocks,cuts


def parts(plate,*,installed=True):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)]
        out['pump-receiver-'+name]=receiver.build_receiver(plate['fore_y'],x,z,installed=installed,junction=data['junction'])
        out['pump-return-'+name]=returned.build_return(data['return'],installed=installed)
    for name in KEEPERS:
        out['pump-keeper-'+name]=keeper(plate,name)
    out['pump-return-block']=return_block(plate)
    return out


def part_color(name):
    wet=(name.startswith(('pump-receiver-','pump-return-'))
         and not name.startswith('pump-return-block'))
    return receiver.COLOR if wet else cq.Color(.16,.16,.16)


def manufacturing_parts(plate):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)];local=receiver._local_junction(data['junction'],(x,plate['fore_y'],z))
        rows={'pump-receiver-'+name:receiver.print_solid(junction=local),
              'pump-return-'+name:returned.print_solid(data['return'])}
        for part,shape in rows.items():out['enclosure-'+part]={'shape':shape,'color':part_color(part)}
    # Keepers print flat on their wall face; the two outer keepers are one part.
    for stem,name in (('pump-keeper-outer','west'),('pump-keeper-middle','middle')):
        keep=keeper(plate,name).rotate((0,0,0),(1,0,0),-90)
        b=keep.BoundingBox()
        out['enclosure-'+stem]={'shape':keep.translate((-b.center.x,-b.center.y,-b.zmin)),
                                'color':part_color(stem)}
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
    # The two moving pole columns stand proud of the cartridge back to the wall face. Each
    # clears in one full-height groove 3 mm deep, so its walls are stock and not strips.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+1.0
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,cartridge_face_y+3,row-9,row+9))
    return body.clean()
