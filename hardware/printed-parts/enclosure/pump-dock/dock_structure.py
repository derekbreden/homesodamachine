"""Dry structure for four permanent receivers and their fixed plumbing.

Coordinates share the enclosure frame. The receiver module owns the wet
geometry; this module owns flat keepers, their guides, factory locks and
side-opening fixed-return cradles. No customer operation reaches these parts.
"""
from pathlib import Path
import sys
import json
import math
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
FIXTURE_FORE_ANCHOR_INBOARD=16.0
FIXTURE_AFT_ANCHOR_INBOARD=16.0
FIXTURE_AFT_LOCK_ABOVE_BED=6.75
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
FIXTURE_LOCK_RELIEF = 1.75
FIXTURE_COVER_SPACER = .15
FIXTURE_TAB_THICK = 3.0
FIXTURE_SCREW_LENGTH = 12.0
FIXTURE_ANCHOR_BELOW = 7.0 + 3.0 + fits.running
FIXTURE_COVER_ENTRY = returned.KEY_FRONT_W-returned.COVER_FRONT_W+fits.running
FIXTURE_RECEIVER_APPROACH = 50.0
FIXTURE_RETURN_LIFT = plumbing.SEAL_LAND+plumbing.ENTRY_LEAD
FACTORY_DRIVER_SHAFT_LENGTH = 100.0
FACTORY_DRIVER_HANDLE_LENGTH = 104.0
FACTORY_DRIVER_HANDLE_D = 23.0
FACTORY_DRIVER_ACCESS_D = 4.5
FACTORY_DRIVER_APPROACH = 20.0
FACTORY_DRIVER_PITCH = 15.0
FACTORY_DRIVER_SOCKET_ENGAGEMENT = 1.5
LOCK_WASHER_OD = 7.0
LOCK_WASHER_ID = 3.2
LOCK_WASHER_T = .5
GUIDE_INNER_X = 9.25
GUIDE_OUTER_X = 16.4
GUIDE_Z = (-11.0, 8.5)
RECESS_Z = (-14.0, 40.0)


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


def _bed_corbel(x0, x1, y0, y1, top, bed):
    """45-degree underside rising aft, clipped at the part's print bed."""
    points=[cq.Vector(x0,y0,top-(y1-y0)),cq.Vector(x0,y1,top),
            cq.Vector(x0,y0,top)]
    wire=cq.Wire.makePolygon(points+[points[0]])
    raw=cq.Solid.extrudeLinear(wire,[],cq.Vector(x1-x0,0,0))
    return raw.intersect(box(x0,x1,y0,y1,bed,top+.1)).clean()



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


def _house_wire(w,u,v,side=1,air=.25):
    # Offset roof by normal clearance; bottom and vertical flanks carry the
    # ordinary axis allowance. This is a rigid-to-rigid throat, not TPU squeeze.
    top=returned.KEY_NECK_TOP+air*2**.5
    a=returned.KEY_NECK_U+air
    shoulder=top-a
    pts=[(-a,returned.KEY_NECK_BOTTOM-air),(a,returned.KEY_NECK_BOTTOM-air),
         (a,shoulder),(0,top),(-a,shoulder)]
    vertices=[cq.Vector(side*w,u+y,v+z) for y,z in pts]
    return cq.Wire.makePolygon(vertices+[vertices[0]])


def _key_seat_cut(wall_fore_y,x,z):
    pieces=[]
    for sign in (-1,1):
        cx=x+sign*(receiver.KEY_ROOT_X+receiver.KEY_OUTER_X)/2
        half=3.+fits.running
        top=z+receiver.KEY_TOP_Z+fits.running*2**.5
        pts=[(cx-half,z+receiver.KEY_BASE_Z-fits.running),(cx+half,z+receiver.KEY_BASE_Z-fits.running),
             (cx+half,top-half),(cx,top),(cx-half,top-half)]
        y0=wall_fore_y+receiver.REAR_COLLAR_Y[0]-.01
        y1=wall_fore_y+receiver.REAR_COLLAR_Y[1]+3
        wire=cq.Wire.makePolygon([cq.Vector(a,y0,b) for a,b in pts]+[cq.Vector(pts[0][0],y0,pts[0][1])])
        pieces.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,y1-y0,0)))
    return fused(pieces)


def mount_side(x):
    """Outward mounting heads leave the appliance centre clear."""
    return 1 if x>0 else -1


def _anchor_x(layout,y,w):
    origin,n,h=returned.frame(layout)
    return origin.x+(w-n.y*(y-origin.y))/n.x


def _tray_anchor(plate,x):
    layout=plumbing.layouts(plate)[str(x)]['return']
    station=min(plate['valve_trays'],key=lambda row:abs(row[0]-layout['target']['point'][1]))
    plane,sign,seats=station
    face=plane-sign*valve_tray.SEAT
    near=min(face,face-sign*valve_tray.THICK)
    return (_anchor_x(layout,near,-FIXTURE_AFT_ANCHOR_INBOARD*mount_side(x)),near,plate['fixture_print_bed_z']+FIXTURE_AFT_LOCK_ABOVE_BED)


def fixture_anchors(plate,x):
    layout=plumbing.layouts(plate)[str(x)]['return']
    y=plate['wall_aft_y'];row=dict(plate['holes'])[x]
    return ((_anchor_x(layout,y,-FIXTURE_FORE_ANCHOR_INBOARD*mount_side(x)),y,row-19.),_tray_anchor(plate,x))


def key_approach_cut(shape,guide_back_y):
    """Exact straight+Y sweep of the fitted key until it clears the guides."""
    travel=max(0.,guide_back_y-shape.BoundingBox().ymin+fits.running)
    pieces=[shape]
    if travel:
        for face in shape.Faces():
            if face.normalAt().y>1e-7:
                pieces.append(cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),cq.Vector(0,travel,0)))
    return fused(pieces)


def factory_driver_axes(plate,x):
    """Wiha26305 ball-end factory approach, with the front-top loose.

    The fore lock approaches from aft and below. The aft lock approaches
    from fore and above; a small handed yaw clears the keeper, magnet and
    opposite front-insert stock. The20mm coaxial entry keeps the full handle
    outside the mounted wet group. These are tool-room declarations, not a
    measured hand-clearance or tightening-torque qualification.
    """
    pitch=math.radians(FACTORY_DRIVER_PITCH);side=mount_side(x);out=[]
    stack=fits.running+2*FIXTURE_TAB_THICK+FIXTURE_COVER_SPACER+LOCK_WASHER_T+3.0
    for index,(ax,ay,az) in enumerate(fixture_anchors(plate,x)):
        sign=1 if index==0 else -1
        tip=(ax,ay+sign*(stack-FACTORY_DRIVER_SOCKET_ENGAGEMENT),az)
        if index==0:axis=(0.,math.cos(pitch),-math.sin(pitch));yaw=0.
        else:
            yaw=4.5 if abs(x)>50 else -5.0;y=math.radians(yaw)
            axis=(side*math.sin(y)*math.cos(pitch),-math.cos(y)*math.cos(pitch),math.sin(pitch))
        out.append({'index':index,'tip':tip,'axis':axis,'pitch_deg':FACTORY_DRIVER_PITCH,
                    'yaw_outboard_deg':yaw,'shaft_mm':FACTORY_DRIVER_SHAFT_LENGTH,
                    'axial_approach_mm':FACTORY_DRIVER_APPROACH})
    return tuple(out)


def _driver_lane(declaration,build,point_transform=None):
    tip=cq.Vector(*declaration['tip']);axis=cq.Vector(*declaration['axis'])
    start=tip-axis*.2
    end=tip+axis*(FACTORY_DRIVER_SHAFT_LENGTH+FACTORY_DRIVER_APPROACH+.2)
    if point_transform is not None:
        start=cq.Vector(*point_transform(start.toTuple()));end=cq.Vector(*point_transform(end.toTuple()))
    return _axis_crown(FACTORY_DRIVER_ACCESS_D/2,start.toTuple(),end.toTuple(),build)


def fixed_features(plate):
    """Wall seats/flat keepers plus permanent anchors for the loose cradles."""
    fore=plate['fore_y'];stocks=[];cuts=[wall_recess(plate)]
    for x,z in plate['holes']:
        side=keeper_side(x)
        stocks.append(guides(fore,x,z,plate['wall_aft_y']))
        stocks.append(ycyl(4.,x+side*8.5,z+LOCK_Z,fore+receiver.WALL_THICKNESS,fore+receiver.KEEPER_Y[0]))
        cuts.extend((receiver.receiver_wall_cut(fore,x,z),
                     lock_cut(fore,x+side*8.5,z),
                     _key_seat_cut(fore,x,z)))
        declared=plumbing.layouts(plate)[str(x)]
        layout=declared['return'];origin,n,h=returned.frame(layout)
        for point in receiver.mount_stations(declared['junction']):
            center=returned._point(point,origin,n,h)
            build=receiver.print_build_direction(declared['junction'])
            bd=(build.dot(n),build.dot(h),build.z)
            key=returned.to_world(returned.button(center,mount_side(x),clearance=fits.slip,build_direction=bd),layout)
            cuts.append(key_approach_cut(key,plate['wall_aft_y']))
        front,aft=fixture_anchors(plate,x)
        fx,fy,fz=front
        root=fore+receiver.WALL_THICKNESS
        stocks.extend((box(fx-5,fx+5,root,fy,fz-5,fz+LOCK_INSERT_D/2*2**.5+3),
                       _bed_corbel(fx-5,fx+5,root,fy,fz-5,plate['z0']+fits.supported_surface)))
        for index,(ax,ay,az) in enumerate((front,aft)):
            py0,py1=(ay,ay+fits.running) if index==0 else (ay-fits.running,ay)
            stocks.append(box(ax-4,ax+4,py0,py1,az-4,az+4))
            #45degree underside of each small supported axial bearing land.
            yroot,yedge=(ay,py1) if index==0 else (ay,py0)
            vv=[cq.Vector(ax-4,yroot,az-4-fits.running),cq.Vector(ax-4,yedge,az-4),cq.Vector(ax-4,yroot,az-4)]
            wire=cq.Wire.makePolygon(vv+[vv[0]])
            stocks.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(8,0,0)))
            a,b=(ay-LOCK_INSERT_LENGTH-FIXTURE_LOCK_RELIEF,ay+fits.running+.01) if index==0 else (ay-fits.running-.01,ay+LOCK_INSERT_LENGTH+FIXTURE_LOCK_RELIEF)
            cuts.append(ycrown(LOCK_INSERT_D/2,ax,az,a,b))
        # Continue the existing valve port channel down the tray foot. The
        # occupied exterior heel has the same fixed outlet axis and must not
        # bear on the tray; this is an open-to-bed relief, not a blind pocket.
        outlet=layout["output"]["point"]
        cuts.append(cq.Solid.makeCylinder(valve_tray._valve.port_radius+valve_tray.PORT_SLIP,
                    outlet[2]+3.0-plate["fixture_print_bed_z"],
                    cq.Vector(outlet[0],outlet[1],plate["fixture_print_bed_z"]-.01),cq.Vector(0,0,1)))
        for driver in factory_driver_axes(plate,x):cuts.append(_driver_lane(driver,(0,0,1)))
    return stocks,cuts


def _local_point(point,layout):
    origin,n,h=returned.frame(layout)
    return returned._point(point,origin,n,h)


def _profile_extrude(points,w0,w1):
    vertices=[cq.Vector(w0,u,v) for u,v in points]
    wire=cq.Wire.makePolygon(vertices+[vertices[0]])
    return cq.Solid.extrudeLinear(wire,[],cq.Vector(w1-w0,0,0))


def _capsule(a,b,r,w0,w1):
    # A planar capsule extruded on the flat print normal; no enclosed roof.
    av=cq.Vector(0,a[1],a[2]);bv=cq.Vector(0,b[1],b[2]);d=bv-av
    length=d.Length;t=d.normalized();n=cq.Vector(1,0,0).cross(t)*r
    points=[(av+n).toTuple()[1:],(bv+n).toTuple()[1:],(bv-n).toTuple()[1:],(av-n).toTuple()[1:]]
    plate=_profile_extrude(points,w0,w1)
    for q in (a,b):plate=plate.fuse(cq.Solid.makeCylinder(r,w1-w0,cq.Vector(w0,q[1],q[2]),cq.Vector(1,0,0)))
    return plate.clean()


def _open_cut(cylinder,layout,wmax):
    # Project only the intended pocket to the open side. The3mm cover closes
    # this opening after the supported wet group has been assembled.
    face=cylinder.intersect(cq.Face.makePlane(300,300,cq.Vector(0,0,0),cq.Vector(1,0,0)))
    out=cylinder
    for f in face.Faces():
        out=out.fuse(cq.Solid.extrudeLinear(f.outerWire(),f.innerWires(),cq.Vector(wmax,0,0)))
    return out


def _to_local(shape,layout,side):
    origin,n,h=returned.frame(layout)
    angle=-__import__('math').degrees(__import__('math').atan2(n.y,n.x))
    shape=shape.translate(origin*-1).rotate((0,0,0),(0,0,1),angle)
    return shape if side>0 else shape.mirror('YZ')


def _axis_crown(radius,start,end,build):
    """Round clearance and a tangent45degree roof in its actual print frame."""
    a=cq.Vector(*start);b=cq.Vector(*end);axis=(b-a).normalized()
    build=cq.Vector(*build).normalized()
    crown=(build-axis*axis.dot(build)).normalized()
    across=axis.cross(crown).normalized();r=radius/2**.5
    vertices=[a+across*r+crown*r,a-across*r+crown*r,a+crown*radius*2**.5]
    wire=cq.Wire.makePolygon(vertices+[vertices[0]])
    return cq.Solid.makeCylinder(radius,(b-a).Length,a,axis).fuse(
        cq.Solid.extrudeLinear(wire,[],b-a))


def _extrude_profile(profile,w0,w1):
    section=profile.intersect(cq.Face.makePlane(500,500,cq.Vector(.5,0,0),cq.Vector(1,0,0)))
    return fused(cq.Solid.extrudeLinear(f.outerWire(),[],cq.Vector(w1-w0,0,0)).translate((w0-.5,0,0)) for f in section.Faces())


def _arm_static_pocket(arm,air):
    """Parallel static allowance around the arm's constant-Z silhouette.

    The polygon offset keeps its45degree print roof parallel. The pocket
    opens on the same flat back as the base; no buried support ceiling is
    introduced. Hard spacer lands are restored after the complementary cut.
    """
    bounds=arm.BoundingBox();level=(bounds.zmin+bounds.zmax)/2
    section=arm.intersect(cq.Face.makePlane(500,500,cq.Vector(0,0,level),cq.Vector(0,0,1)))
    pieces=[]
    for face in section.Faces():
        wires=face.outerWire().offset2D(air,kind='intersection')
        for wire in wires:
            pieces.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,bounds.zlen+2*air)).translate((0,0,bounds.zmin-air-level)))
    return fused(pieces)


def _terminal_clearance(plate,layout,side,build):
    """Open terminal pockets with45degree roofs in the dry print frame.

    The aft valves' spades face the diagonal guide. Their reference width
    defines each pocket; the central closed guide remains intact. Loading
    edges retain running air and the terminal tip has static seating air.
    """
    valve=valve_tray._valve
    plane,sign,seats=min(plate['valve_trays'],
        key=lambda row:abs(row[0]-layout['target']['point'][1]))
    sx,sz=min(seats,key=lambda q:abs(q[0]-layout['target']['point'][0]))
    y=plane+sign*valve.spade_z_center
    pieces=[]
    for hand in (-1,1):
        x=sx+hand*valve.spade_x_spacing/2
        keepout=box(x-valve.spade_width/2-fits.running,
                    x+valve.spade_width/2+fits.running,
                    y-valve.spade_thickness/2-fits.running,
                    y+valve.spade_thickness/2+fits.running,
                    sz-valve.coil_face_y-valve.spade_length-fits.slip,
                    sz-valve.coil_face_y+fits.slip)
        bounds=_to_local(keepout,layout,side).BoundingBox()
        lo,hi=bounds.xmin,bounds.xmax;u0,u1=bounds.ymin,bounds.ymax
        half=(u1-u0)/2;mid=(u1+u0)/2
        if build>0:
            points=[(lo,u0),(hi,u0),(hi+half,mid),(hi,u1),(lo,u1)]
        else:
            points=[(lo,u0),(hi,u0),(hi,u1),(lo,u1),(lo-half,mid)]
        vertices=[cq.Vector(w,u,bounds.zmin) for w,u in points]
        wire=cq.Wire.makePolygon(vertices+[vertices[0]])
        pieces.append(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,500-bounds.zmin)))
    return fused(pieces)


def _convex_hull_2d(points):
    points=sorted(set(points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[];upper=[]
    for q in points:
        while len(lower)>1 and cross(lower[-2],lower[-1],q)<=1e-10:lower.pop()
        lower.append(q)
    for q in reversed(points):
        while len(upper)>1 and cross(upper[-2],upper[-1],q)<=1e-10:upper.pop()
        upper.append(q)
    return lower[:-1]+upper[:-1]


def _axis_crown_sweep(radius,start,end,build,sweep):
    """Full round tool room with a45degree crown throughout a translation."""
    a=cq.Vector(*start);b=cq.Vector(*end);axis=(b-a).normalized()
    travel=cq.Vector(*sweep);along=travel.dot(axis);cross_travel=travel-axis*along
    a=a+axis*min(0.,along);b=b+axis*max(0.,along);length=(b-a).Length
    normal=cq.Vector(*build);crown=(normal-axis*axis.dot(normal)).normalized()
    across=axis.cross(crown).normalized();r=radius/2**.5
    pieces=[cq.Solid.makeCylinder(radius,length,a,axis)]
    if cross_travel.Length>1e-10:
        pieces.append(cq.Solid.makeCylinder(radius,length,a+cross_travel,axis))
        width=axis.cross(cross_travel).normalized()*radius
        vertices=[a+width,a-width,a+cross_travel-width,a+cross_travel+width]
        wire=cq.Wire.makePolygon(vertices+[vertices[0]])
        pieces.append(cq.Solid.extrudeLinear(wire,[],axis*length))
    profile=[(r,r),(-r,r),(0.,radius*2**.5)]
    dx,dy=cross_travel.dot(across),cross_travel.dot(crown)
    outline=_convex_hull_2d(profile+[(u+dx,v+dy) for u,v in profile])
    vertices=[a+across*u+crown*v for u,v in outline]
    wire=cq.Wire.makePolygon(vertices+[vertices[0]])
    pieces.append(cq.Solid.extrudeLinear(wire,[],axis*length))
    return fused(pieces)


def _arm_entry_pocket(arm,travel,air):
    """Exact convex silhouette sweep for the empty bench assembly."""
    bounds=arm.BoundingBox();z=(bounds.zmin+bounds.zmax)/2;pieces=[]
    section=arm.intersect(cq.Face.makePlane(500,500,cq.Vector(0,0,z),cq.Vector(0,0,1)))
    for face in section.Faces():
        points=[(v.X,v.Y) for v in face.Vertices()]
        outline=_convex_hull_2d(points+[(w+travel[0],u+travel[1]) for w,u in points])
        vertices=[cq.Vector(w,u,bounds.zmin-air) for w,u in outline]
        wire=cq.Wire.makePolygon(vertices+[vertices[0]])
        for offset in wire.offset2D(air,kind='intersection'):
            pieces.append(cq.Solid.extrudeLinear(offset,[],cq.Vector(0,0,bounds.zlen+2*air)))
    return fused(pieces)


def _diagonal_link_guide(base,cover,layout,junction,jbody,side):
    """A four-mm channel band confines the straight link during service."""
    point=cq.Vector(*junction['lower']['point'])
    end=cq.Vector(*layout['input']['point']);axis=(end-point).normalized()
    _,normal,_=returned.frame(layout);normal=normal*side
    upper=(cq.Vector(0,0,1)-axis*axis.z).normalized()
    radius=plumbing.TUBE_OD/2+fits.running
    first=(point.z+upper.z*(radius+3.)-(jbody.BoundingBox().zmin-fits.running))/(-axis.z)+fits.running
    def prism(start,w0,w1,b0,b1,length):
        center=point+axis*start
        vertices=[center+normal*w+upper*b for w,b in ((w0,b0),(w1,b0),(w1,b1),(w0,b1))]
        wire=cq.Wire.makePolygon(vertices+[vertices[0]])
        return cq.Solid.extrudeLinear(wire,[],axis*length)
    bed=base.BoundingBox().xmin
    band=prism(first,bed,radius,radius,radius+3.,4.)
    band=band.fuse(prism(first,bed,-radius,-radius,radius,4.))
    fore=plumbing.OCCUPIED_CUFF_OD/2+fits.running+.05-.1
    trim=prism(fore,-radius-3.,radius,0.,radius+3.1,first-fore+.001)
    return base.cut(_to_local(trim,layout,side)).fuse(_to_local(band,layout,side)).clean()


def _factory_loading_fit(base,cover,plate,x,item,layout,side,centers,cuffs,arms,return_bare,jbody,profile,host_window):
    """Open loading troughs and the cover's closing shoulder supports.

    The empty pair assembles on the bench. In the loose front-top it stays
    parked outside the fixed wet parts until their straight loading strokes
    are complete. Broad cover fingers then close the near-body support.
    """
    origin,n,h=returned.frame(layout)
    def lp(point):
        w,u,v=_local_point(point,layout);return(side*w,u,v)
    def world(shape):return returned.to_world(shape if side>0 else shape.mirror('YZ'),layout)
    def bounds_tool(shape,translation=(0.,0.,0.),air=fits.running):
        b=shape.BoundingBox();dx,dy,dz=translation
        return box(b.xmin+min(0.,dx)-air,b.xmax+max(0.,dx)+air,
                   b.ymin+min(0.,dy)-air,b.ymax+max(0.,dy)+air,
                   b.zmin+min(0.,dz)-air,b.zmax+max(0.,dz)+air)
    build=receiver.print_build_direction(item['junction'])
    junction_build=(side*build.dot(n),build.dot(h),build.z)
    roots=[returned.button_neck(c,1,installed=True,
              build_direction=junction_build if i<2 else (0.,-2**-.5,2**-.5))
           for i,c in enumerate(centers)]
    frontbody=receiver._place(receiver._outside(True).fuse(receiver.anti_rotation_keys()),plate['fore_y'],x,dict(plate['holes'])[x])
    diameter=math.sqrt(receiver.BRANCH_OD**2+plumbing.TUBE_OD**2-receiver.SEAL_BORE_D**2)
    junction_parts=[frontbody,*[receiver._sweep(diameter,item['junction'][key+'_flow_segments']) for key in ('upper','lower')],*[world(q) for q in roots[:2]]]
    loading_world=[bounds_tool(q,(0.,FIXTURE_RECEIVER_APPROACH,0.)) for q in junction_parts]
    line=item['upper_tube'];a=cq.Vector(*line['start_mm']);b=cq.Vector(*line['end_mm'])
    upper=cq.Solid.makeCylinder(plumbing.TUBE_OD/2+fits.running,(b-a).Length,a,(b-a).normalized())
    loading_world.append(bounds_tool(upper,(0.,FIXTURE_RECEIVER_APPROACH,0.),air=0.))
    returned_group=cq.Compound.makeCompound([world(return_bare),*[world(q) for q in roots[2:]]])
    loading_world.append(bounds_tool(returned_group,(0.,0.,-FIXTURE_RETURN_LIFT)))
    loading=_to_local(fused(loading_world),layout,side)
    static_base=base
    raw_w0=-max(FIXTURE_FORE_ANCHOR_INBOARD,FIXTURE_AFT_ANCHOR_INBOARD)-5.5*abs(n.x)-4*abs(n.y)
    raw_material=_extrude_profile(profile,raw_w0,returned.BASE_FRONT_W).intersect(host_window)
    removed=raw_material.intersect(loading)
    section_w=returned.BASE_FRONT_W-.001
    section=removed.intersect(cq.Face.makePlane(500,500,cq.Vector(section_w,0,0),cq.Vector(1,0,0)))
    finger_w=returned.KEY_BACK_W+fits.running-FIXTURE_COVER_ENTRY
    fingers=fused(cq.Solid.extrudeLinear(f.outerWire(),f.innerWires(),
                      cq.Vector(returned.COVER_FRONT_W-finger_w+.01,0,0)).translate((finger_w-section_w,0,0))
                  for f in section.Faces())
    ears=receiver._place(receiver.anti_rotation_keys(),plate['fore_y'],x,dict(plate['holes'])[x])
    ear_loading=bounds_tool(ears,(0.,FIXTURE_RECEIVER_APPROACH,0.))
    fingers=fingers.cut(_to_local(ear_loading,layout,side))
    # Circular branch room follows the actual outboard sector rather than
    # the larger centre-plane projection used for the open base pockets.
    for key in ('upper','lower'):
        branch=receiver._sweep(diameter+2*fits.running,item['junction'][key+'_flow_segments'])
        fingers=fingers.cut(_to_local(branch,layout,side))
    radius=plumbing.OCCUPIED_CUFF_OD/2+fits.running
    section_radius=math.sqrt(radius**2-finger_w**2)
    local_return=returned.local_layout(layout)
    return_room=returned._sweep(2*section_radius,local_return['flow_segments'][1:-1])
    plane=return_room.intersect(cq.Face.makePlane(500,500,cq.Vector(0,0,0),cq.Vector(1,0,0)))
    for f in plane.Faces():
        cut=cq.Solid.extrudeLinear(f.outerWire(),f.innerWires(),cq.Vector(returned.COVER_FRONT_W-finger_w+.02,0,0)).translate((finger_w,0,0))
        fingers=fingers.cut(cut)
    fingers=fingers.intersect(host_window)
    base=base.cut(loading);cover=cover.fuse(fingers)
    ear_loading=ear_loading.translate((-side*FIXTURE_COVER_ENTRY/n.x,0.,0.))
    cover=cover.cut(_to_local(ear_loading,layout,side))
    sv=side*h.x/n.x;relative=(-FIXTURE_COVER_ENTRY,-sv*FIXTURE_COVER_ENTRY,0.)
    cuff_r=plumbing.OCCUPIED_CUFF_OD/2+fits.running
    for a,b in cuffs:cover=cover.cut(_axis_crown_sweep(cuff_r,a.toTuple(),b.toTuple(),(-1,0,0),relative))
    out=lp(layout['output']['point']);port_r=valve_tray._valve.port_radius+valve_tray.PORT_SLIP
    cover=cover.cut(_axis_crown_sweep(port_r,(out[0],out[1],out[2]+2-fits.running),(out[0],out[1],350.),(-1,0,0),relative))
    w0=base.BoundingBox().xmin;back=returned.COVER_BACK_W
    for _,u,v in centers:
        wire=_house_wire(w0-.1,u,v,air=-returned.KEY_SEAT_SQUEEZE+.01)
        cover=cover.cut(cq.Solid.extrudeLinear(wire,[],cq.Vector(back-w0+.2,0,0)))
    front,aft=fixture_anchors(plate,x)
    for index,(ax,ay,az) in enumerate((front,aft)):
        sign=1 if index==0 else -1;cface=ay+sign*(fits.running+2*FIXTURE_TAB_THICK+FIXTURE_COVER_SPACER)
        a,b=sorted((ay-sign*.05,cface+sign*.05))
        cover=cover.cut(_axis_crown(LOCK_BORE_D/2,lp((ax,a,az)),lp((ax,b,az)),(-1,0,0)))
        for radius,start,end in ((LOCK_WASHER_OD/2+fits.slip,0,LOCK_WASHER_T+fits.slip),(2.75+fits.slip,LOCK_WASHER_T-.01,LOCK_WASHER_T+3+fits.slip)):
            a,b=sorted((cface+sign*start,cface+sign*end))
            cover=cover.cut(_axis_crown(radius,lp((ax,a,az)),lp((ax,b,az)),(-1,0,0)))
    for station_x,_ in plate['holes']:
        for driver in factory_driver_axes(plate,station_x):cover=cover.cut(_driver_lane(driver,(-1,0,0),lp))
    cover=cover.cut(_terminal_clearance(plate,layout,side,-1))
    bench=math.ceil(returned.BASE_FRONT_W-min(q.BoundingBox().xmin for q in arms)+fits.running)
    base=base.cut(fused(_arm_entry_pocket(q,(bench,sv*bench,0.),fits.running) for q in arms))
    for index,(ax,ay,az) in enumerate((front,aft)):
        sign=1 if index==0 else -1;face=ay+sign*(fits.running+FIXTURE_TAB_THICK)
        a,b=sorted((ay+sign*fits.running,face+sign*FIXTURE_COVER_SPACER))
        zone=_to_local(box(ax-5.5,ax+5.5,a,b,az-FIXTURE_ANCHOR_BELOW,az+7),layout,side)
        if abs(x)>50:
            # The clocked tab's nonbearing inboard corners use exact45degree
            # print bevels. The8mm hard land and3mm bore surround stay whole.
            ex=cq.Vector(n.x,side*h.x,0);ey=cq.Vector(side*n.y,h.y,0)
            low=cq.Vector(-1,-1,0);high=cq.Vector(-1,1,0)
            d0=fits.running*abs(low.dot(ey)/low.dot(ex))
            d1=fits.running*abs(high.dot(ey)/high.dot(ex))
            xin=ax-side*5.5;xout=ax+side*5.5
            vertices=[cq.Vector(xx,yy,az-FIXTURE_ANCHOR_BELOW) for xx,yy in
                      ((xin+side*d0,a),(xout,a),(xout,b),(xin+side*d1,b),
                       (xin,b-fits.running),(xin,a+fits.running))]
            wire=cq.Wire.makePolygon(vertices+[vertices[0]])
            zone=_to_local(cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,FIXTURE_ANCHOR_BELOW+7)),layout,side)
        base=base.fuse(static_base.intersect(zone))
    base=_diagonal_link_guide(base,cover,layout,item['junction'],jbody,side)
    if abs(x)>50:
        fore_cover_face=front[1]+fits.running+FIXTURE_TAB_THICK+FIXTURE_COVER_SPACER
        keep=_to_local(box(-220,220,fore_cover_face-2*fits.running,500,0,400),layout,side)
        cover=cover.intersect(keep)
    return base.clean(),cover.clean(),{'cover_local_N_park_mm':FIXTURE_COVER_ENTRY,
        'cover_world_X_park_mm':side*FIXTURE_COVER_ENTRY/n.x,'bench_local_N_entry_mm':bench,
        'receiver_world_Y_approach_mm':FIXTURE_RECEIVER_APPROACH,'return_world_Z_raise_mm':FIXTURE_RETURN_LIFT,
        'finger_front_W_mm':finger_w}


def _return_fixture(plate,x):
    """Two host bolts close a flat-backed cradle and its outside3mm cover.

    The cover is outside the complete occupied wet body. Four substantial
    TPU heads bear directly on its throat surrounds. Both integral cover
    arms share the two M3x12 host locks with the cradle. The empty pair
    assembles on the bench and enters the loose front-top with the cover
    parked6.25mm outward. Junction groups load forward, returns rise into
    their sockets, and the cover closes in worldX over the local TPU heads.
    Closing fingers support the sockets; the straight link has a closed guide.
    """
    item=plumbing.layouts(plate)[str(x)];layout=item['return'];local=returned.local_layout(layout)
    side=mount_side(x);origin,n,h=returned.frame(layout)
    def lp(point):
        w,u,v=_local_point(point,layout)
        return (side*w,u,v)
    points={key:lp(item['junction'][key]['point']) for key in ('lower','upper')}
    stops={key:lp(item['junction'][key]['tube_stop']) for key in ('lower','upper')}
    jm,js=points['lower'],stops['lower']
    im,istop=local['input']['point'],local['input']['tube_stop']
    om,ostop=local['output']['point'],local['output']['tube_stop']
    centers=tuple(lp(p) for p in receiver.mount_stations(item['junction']))+returned.mount_stations(local)
    front,aft=fixture_anchors(plate,x)
    w0=-max(FIXTURE_FORE_ANCHOR_INBOARD,FIXTURE_AFT_ANCHOR_INBOARD)-5.5*abs(n.x)-4.*abs(n.y)
    surface=returned.BASE_FRONT_W;cover_fore=returned.COVER_FRONT_W;back=returned.COVER_BACK_W
    cuff_r=plumbing.OCCUPIED_CUFF_OD/2+fits.running
    guide_r=plumbing.TUBE_OD/2+fits.running
    # One constant outside profile is shared by the base and flat cover.
    # Both parts use the flatWface as their manufacturing bed. The base
    # pockets open toward its opposite face.
    profiles=[_capsule(js,istop,6.45,0,1),_capsule(istop,ostop,9.20,0,1),
              _capsule(js,stops['upper'],9.20,0,1),_capsule(jm,im,guide_r+3,0,1)]
    cuffs=[]
    for start,end in ((js,jm),(stops['upper'],points['upper']),(istop,im),(ostop,om)):
        aa=cq.Vector(*start);bb=cq.Vector(*end);d=(bb-aa).normalized()
        across=cq.Vector(0,-d.z,d.y).normalized()*(cuff_r+3)
        lo=aa-d*3;hi=bb+d*3
        profiles.append(_profile_extrude([(q.y,q.z) for q in (lo+across,hi+across,hi-across,lo-across)],0,1))
        cuffs.append((aa-d*3.01,bb+d*3.01))
    frame_top=returned.KEY_NECK_TOP+3.25
    for _,u,v in centers:profiles.append(box(0,1,u-10.5,u+10.5,v-10,v+frame_top))
    for anchor,from_point in ((front,js),(aft,ostop)):
        ax,ay,az=anchor;ap=lp(anchor)
        profiles.extend((_capsule(from_point,ap,5,0,1),box(0,1,ap[1]-6,ap[1]+6,ap[2]-FIXTURE_ANCHOR_BELOW,ap[2]+7)))
    profile=fused(profiles)
    base=_extrude_profile(profile,w0,surface)
    cover=_extrude_profile(profile,cover_fore,back)
    aft_face=aft[1]
    host_window=_to_local(box(-220,220,plate['wall_aft_y']+fits.running,
                             aft_face-fits.running,0,400),layout,side)
    base=base.intersect(host_window);cover=cover.intersect(host_window)
    # The empty dry pair installs before the wet group. The cover remains
    # parked outside the loading troughs until the sockets and links seat.
    a=cq.Vector(*jm);b=cq.Vector(*im);d=(b-a).normalized()
    guide=cq.Solid.makeCylinder(guide_r,(b-a).Length+.02,a-d*.01,d)
    pockets=[guide]
    for aa,bb in cuffs:pockets.append(cq.Solid.makeCylinder(cuff_r,(bb-aa).Length,aa,(bb-aa).normalized()))
    base=base.cut(_open_cut(fused(pockets),layout,back+.02))
    return_bare=returned.geometry(layout,installed=True,mount_side=1)['bare_envelope']
    jbody=receiver.receiver_envelope(plate['fore_y'],x,dict(plate['holes'])[x],installed=True,junction=item['junction'],include_mounts=False)
    bare=return_bare.fuse(_to_local(jbody,layout,side))
    base=base.cut(_open_cut(bare,layout,back+.02))
    # A small solid inward boss closes the diagonal guide between the cuff
    # mouths. It starts after the full cuff radius, retaining real clearance.
    span=(b-a).Length;reserve=cuff_r+.05
    ga=a+d*reserve;gb=b-d*reserve
    if span>2*reserve:
        cover=cover.fuse(_capsule(ga.toTuple(),gb.toTuple(),guide_r,
                         surface+fits.slip,cover_fore+.01))
    # Cover arms cross in front of the aft cuff, then return to the inboard
    # lock. A45degree growing silhouette supports the return leg as the
    # cover builds inward from its flat outer face.
    cover_arms=[];tab_bearing=[]
    target=layout['target']['point'];port_r=valve_tray._valve.port_radius+valve_tray.PORT_SLIP
    for index,(ax,ay,az) in enumerate((front,aft)):
        sign=1 if index==0 else -1
        tab0,tab1=sorted((ay+sign*fits.running,ay+sign*(fits.running+3)))
        # Full3mm base tab, backed by its broad constant outside profile.
        base=base.fuse(_to_local(box(ax-5.5,ax+5.5,tab0,tab1,az-FIXTURE_ANCHOR_BELOW,az+7),layout,side))
        face=ay+sign*(fits.running+3)
        c0,c1=sorted((face+sign*FIXTURE_COVER_SPACER,face+sign*(FIXTURE_COVER_SPACER+3)))
        if index==0:
            arm_world=box(ax-6.5 if side>0 else ax-50,ax+50 if side>0 else ax+6.5,c0,c1,az-7,az+7)
            arm=_to_local(arm_world,layout,side)
        else:
            cross_y=target[1]-port_r-3
            # In local print coordinates the far edge grows at45degrees.
            cross0=lp((ax,cross_y,az))[1];cross1=lp((ax,cross_y+3,az))[1]
            # The shared lock bears on a world-Y plane, including clocked
            # outer hands. Extend the raw silhouette through that plane,
            # then trim to it; a constant-U end is not the bearing datum.
            end_u=max((c1-origin.y-side*w*n.y)/h.y for w in (w0,back))+.01
            ap=lp((ax,ay,az));u0=min(cross0,cross1);u1=max(cross0,cross1)
            poly=[(back,u0),(back,u1),(back-(end_u-u1),end_u),(w0,end_u),(w0,u0)]
            # The arm starts3mm below the Ø3.5 hole, above the occupied
            # heel. The upper rail extends7mm above the lock axis.
            lower=LOCK_BORE_D/2+3.0
            vertices=[cq.Vector(w,u,ap[2]-lower) for w,u in poly]
            wire=cq.Wire.makePolygon(vertices+[vertices[0]])
            arm=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,lower+7))
            arm=arm.intersect(_to_local(box(-220,220,-50,c1,0,400),layout,side))
        arm=arm.intersect(host_window).intersect(box(w0,back,-350,350,-350,350))
        cover_arms.append(arm)
        # A broad integral0.15mm land fixes the shared two-plate bearing
        # pose. Its width is supported by the3mm tab, not a flexible fin.
        p0,p1=sorted((face,face+sign*FIXTURE_COVER_SPACER))
        tab_bearing.append(_to_local(box(ax-4,ax+4,p0,p1,az-4,az+4),layout,side))
        # The thin axial land begins with a steep supported ramp at its
        # inboard print-leading edge, rather than a0.15mm free ledge.
        lead=ax-side*4;run=2*FIXTURE_COVER_SPACER
        vv=[cq.Vector(lead-side*run,face,az-4),
            cq.Vector(lead,face+sign*FIXTURE_COVER_SPACER,az-4),
            cq.Vector(lead,face,az-4)]
        ww=cq.Wire.makePolygon(vv+[vv[0]])
        tab_bearing.append(_to_local(cq.Solid.extrudeLinear(ww,[],cq.Vector(0,0,8)),layout,side))
    base=base.fuse(*tab_bearing)
    cover=cover.fuse(*cover_arms)
    # The complete growing arm needs a complementary base pocket, beyond
    # the small shared-lock slots. Both mating roofs remain45degrees.
    base=base.cut(fused(_arm_static_pocket(arm,fits.slip) for arm in cover_arms)).fuse(*tab_bearing)
    # Every arm clears the complete occupied sockets with a45degree roof in
    # the cover's build direction. The circular6mm wet lands are untouched.
    for aa,bb in cuffs:cover=cover.cut(_axis_crown(cuff_r,aa.toTuple(),bb.toTuple(),(-1,0,0)))
    # The existing purchased-valve channel continues through both dry parts.
    # Its unchanged axis and radius clear the actual collet and tray foot.
    out=layout['output']['point'];outlocal=lp(out)
    valve_lo=(outlocal[0],outlocal[1],outlocal[2]+2-fits.running)
    valve_hi=(outlocal[0],outlocal[1],350.)
    for_cover=_axis_crown(port_r,valve_lo,valve_hi,(-1,0,0))
    for_base=_axis_crown(port_r,valve_lo,valve_hi,(1,0,0))
    cover=cover.cut(for_cover);base=base.cut(for_base)
    # Complete house throats, with intentional0.10mm TPU flank squeeze.
    # Their outer surrounds retain the heads' broad bearing faces.
    jb=receiver.print_build_direction(item['junction'])
    junction_build=(side*jb.dot(n),jb.dot(h),jb.z)
    for index,(_,u,v) in enumerate(centers):
        bd=junction_build if index<2 else (0.,-2**-.5,2**-.5)
        cut=returned.button_neck((0,u,v),1,installed=True,clearance=.01,build_direction=bd)
        # The cover arm can reach inward beyond the wet key's root. Open
        # its house passage through that entire arm rather than ending a
        # blind cutter at the wet root and creating a print ceiling.
        house=_house_wire(w0-.1,u,v,air=-returned.KEY_SEAT_SQUEEZE+.01)
        cover=cover.cut(cq.Solid.extrudeLinear(house,[],cq.Vector(back-w0+.2,0,0)))
        base=base.cut(cut)
    # The two shared bolts clamp the base and cover to explicit hard lands.
    # Stepped metal pockets leave both3mm tabs and expose washer bearings.
    for index,(ax,ay,az) in enumerate((front,aft)):
        sign=1 if index==0 else -1
        cface=ay+sign*(fits.running+3+FIXTURE_COVER_SPACER+3)
        for part_name,build in (('base',(1,0,0)),('cover',(-1,0,0))):
            shape=base if part_name=='base' else cover
            lo,hi=sorted((ay-sign*.05,cface+sign*.05))
            shape=shape.cut(_axis_crown(LOCK_BORE_D/2,lp((ax,lo,az)),lp((ax,hi,az)),build))
            for radius,start,end in ((LOCK_WASHER_OD/2+fits.slip,0,LOCK_WASHER_T+fits.slip),
                                     (2.75+fits.slip,LOCK_WASHER_T-.01,LOCK_WASHER_T+3+fits.slip)):
                y0,y1=sorted((cface+sign*start,cface+sign*end))
                shape=shape.cut(_axis_crown(radius,lp((ax,y0,az)),lp((ax,y1,az)),build))
            if part_name=='base':base=shape
            else:cover=shape
    # Cut the selected ball-end driver axes through all fixtures, including
    # the small
    # opposite-inner crossing, with each part's own45degree print crown.
    for station_x,_ in plate['holes']:
        for driver in factory_driver_axes(plate,station_x):
            base=base.cut(_driver_lane(driver,(1,0,0),lp))
            cover=cover.cut(_driver_lane(driver,(-1,0,0),lp))
    base=base.cut(_terminal_clearance(plate,layout,side,1))
    cover=cover.cut(_terminal_clearance(plate,layout,side,-1))
    base,cover,loading_record=_factory_loading_fit(base,cover,plate,x,item,layout,side,centers,cuffs,cover_arms,return_bare,jbody,profile,host_window)
    base=base.clean();cover=cover.clean()
    world_base=returned.to_world(base if side>0 else base.mirror('YZ'),layout)
    world_cover=returned.to_world(cover if side>0 else cover.mirror('YZ'),layout)
    local_base=base if side>0 else base.mirror('YZ')
    local_cover=cover if side>0 else cover.mirror('YZ')
    return {'cradle':world_base,'cover':world_cover,'local_cradle':local_base,
            'local_cover':local_cover,'layout':layout,'mount_side':side,
            'anchors':(front,aft),'key_centers_local':centers,
            'stop_centers_local':(js,stops['upper'],istop,ostop),
            'cover_w_mm':(cover_fore,back),'key_frame_top_offset_mm':frame_top,'factory_loading':loading_record,
            'factory_lock':{'screw_length_mm':FIXTURE_SCREW_LENGTH,'insert_depth_mm':LOCK_INSERT_LENGTH+FIXTURE_LOCK_RELIEF,
                            'cover_spacer_mm':FIXTURE_COVER_SPACER,'driver_model':'Wiha26305',
                            'drivers':factory_driver_axes(plate,x)}}


@lru_cache(maxsize=16)
def _cached_fixture(declaration,x):
    return _return_fixture(json.loads(declaration),x)


def return_fixture(plate,x):
    return _cached_fixture(json.dumps(plate,sort_keys=True),x)


def parts(plate,*,installed=True):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)]
        out['pump-receiver-'+name]=receiver.build_receiver(plate['fore_y'],x,z,installed=installed,junction=data['junction'])
        out['pump-receiver-keeper-'+name]=keeper(plate['fore_y'],x,z,side=keeper_side(x))
        out['pump-return-'+name]=returned.build_return(data['return'],installed=installed)
        fixture=return_fixture(plate,x)
        out['pump-return-cradle-'+name]=fixture['cradle']
        out['pump-return-cover-'+name]=fixture['cover']
    return out


def part_color(name):
    return receiver.COLOR if name.startswith('pump-receiver-') and not name.startswith('pump-receiver-keeper-') or name.startswith('pump-return-') and not name.startswith(('pump-return-cradle-','pump-return-cover-')) else cq.Color(.16,.16,.16)


def _on_x_face(shape,*,cover=False,mount_side=1):
    angle=(90 if cover else -90)*mount_side
    posed=shape.rotate((0,0,0),(0,1,0),angle)
    return posed.translate((0,0,-posed.BoundingBox().zmin))


def manufacturing_parts(plate):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)];local=receiver._local_junction(data['junction'],(x,plate['fore_y'],z))
        wet=receiver.print_solid(junction=local,mount_side=mount_side(x))
        keep=keeper(0,0,0,side=keeper_side(x)).rotate((0,0,0),(1,0,0),90)
        keep=keep.translate((0,0,-keep.BoundingBox().zmin))
        fixture=return_fixture(plate,x)
        rows={'pump-receiver-'+name:wet,'pump-receiver-keeper-'+name:keep,
              'pump-return-'+name:returned.print_solid(data['return'],mount_side=fixture['mount_side']),
              'pump-return-cradle-'+name:_on_x_face(fixture['local_cradle'],mount_side=fixture['mount_side']),
              'pump-return-cover-'+name:_on_x_face(fixture['local_cover'],cover=True,mount_side=fixture['mount_side'])}
        for part,shape in rows.items():out['enclosure-'+part]={'shape':shape,'color':part_color(part)}
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
    # The two magnet guards also project behind the retained cartridge plane.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+retention.SIDE_KEY+retention.STRUCTURAL_STOCK+.25
        end=cartridge_face_y+max(3.0,retention.MOVING_POLE_PROJECTION-retention.GUARD_POLE_PROUD+.25)
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,end,row-9,row+9))
    return body.clean()
