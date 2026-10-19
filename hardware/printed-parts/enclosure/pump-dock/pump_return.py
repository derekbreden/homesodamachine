"""Permanent compound TPU returns and their broad factory mounting buttons.

A shared declaration owns every port and straight-link datum. The body turns
45 degrees, crosses to the original valve station and turns90 degrees upward.
All sealing lands stay circular. Only the last flow turn receives a45-degree
internal roof; its crown is outside the socket stop planes.
"""
from functools import lru_cache
import json
from pathlib import Path
import math
import cadquery as cq
import fixed_returns as plumbing
from flow_roof import cached_flow_cap
from exterior_roof import cached_exterior_cap

BODY_OD=11.72
SEAL_BORE_D=6.10
ENTRY_RADIAL=.25
MATERIAL='Siraya Tech Flex TPU85A Clear'
COLOR=cq.Color(.92,.92,.90,.60)
KEY_ROOT_W=3.0
KEY_BACK_W=10.60
KEY_FRONT_W=13.60
BASE_FRONT_W=3.425
COVER_FRONT_W=7.60
COVER_BACK_W=10.60
KEY_NECK_U=4.0
KEY_NECK_BOTTOM=-6.0
KEY_NECK_TOP=7.0
KEY_NECK_SHOULDER=KEY_NECK_TOP-KEY_NECK_U
KEY_HEAD_TOP=10.5
KEY_TIP_TOP=9.0
KEY_SEAT_SQUEEZE=.10
PRINT_HEEL_TRIM=.70
OUTPUT_KEY_FORWARD=2.5


def frame(layout):
    middle=layout['flow_segments'][2]
    h=cq.Vector(*middle['start_tangent']).normalized()
    n=cq.Vector(h.y,-h.x,0).normalized()
    return cq.Vector(*layout['input']['point']),n,h


def _point(p,origin,n,h):
    q=cq.Vector(*p)-origin
    return (q.dot(n),q.dot(h),q.z)


def _direction(p,n,h):
    q=cq.Vector(*p)
    return (q.dot(n),q.dot(h),q.z)


def local_layout(layout):
    origin,n,h=frame(layout);out=dict(layout)
    out['flow_segments']=tuple({k:_point(v,origin,n,h)
              if k in ('start_mm','midpoint_mm','end_mm') else
              _direction(v,n,h) if k in ('start_tangent','end_tangent') else v
              for k,v in segment.items()} for segment in layout['flow_segments'])
    for port in ('input','output'):
        out[port]=dict(layout[port])
        for field in ('point','tube_stop'):out[port][field]=_point(layout[port][field],origin,n,h)
        out[port]['axis']=_direction(layout[port]['axis'],n,h)
    return out


def to_world(shape,layout):
    origin,n,h=frame(layout)
    angle=math.degrees(math.atan2(n.y,n.x))
    return shape.rotate((0,0,0),(0,0,1),angle).translate(origin)


def _wire(segments):
    return cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(cq.Vector(*s['start_mm']),cq.Vector(*s['midpoint_mm']),cq.Vector(*s['end_mm']))
             if s['kind']=='arc' else cq.Edge.makeLine(cq.Vector(*s['start_mm']),cq.Vector(*s['end_mm'])) for s in segments])


def _sweep(diameter,segments):
    s=segments[0]
    return cq.Solid.sweep(cq.Wire.makeCircle(diameter/2,cq.Vector(*s['start_mm']),cq.Vector(*s['start_tangent'])),[],_wire(segments),makeSolid=True,isFrenet=True)


def _profile(w,u,v,points,side):
    vertices=[cq.Vector(side*w,u+a,v+b) for a,b in points]
    return cq.Wire.makePolygon(vertices+[vertices[0]])


def _button_support(shape,center,side,build_direction,*,installed=False):
    """Trim the head/neck to a45degree underside rooted inside the cuff."""
    build=cq.Vector(*build_direction).normalized();escape=cq.Vector(side,0,0)
    c=build.dot(escape);h=(1-c*c)**.5
    normal=build*(h+c)-escape
    q=cq.Vector(0,center[1],center[2])+escape*KEY_ROOT_W
    level=normal.dot(q)-h*6.0
    if installed:level+=KEY_SEAT_SQUEEZE*normal.Length
    origin=normal*(level/normal.Length**2)
    tangent=cq.Vector(0,1,0).cross(normal)
    if tangent.Length<1e-6:tangent=cq.Vector(0,0,1).cross(normal)
    keep=cq.Workplane(cq.Plane(origin=origin,xDir=tangent,normal=normal)).box(400,400,400,centered=(True,True,False)).val()
    return shape.intersect(keep).clean()


def button_neck(center,side,*,installed=False,clearance=0.,build_direction=(0.,-2**-.5,2**-.5)):
    _,u,v=center
    air=(-KEY_SEAT_SQUEEZE if installed else 0.)+clearance
    a=KEY_NECK_U+air;top=KEY_NECK_TOP+air*2**.5
    neck=[(-a,KEY_NECK_BOTTOM-air),(a,KEY_NECK_BOTTOM-air),(a,top-a),(0,top),(-a,top-a)]
    root=_profile(KEY_ROOT_W-clearance,u,v,neck,side)
    shank=cq.Solid.extrudeLinear(root,[],cq.Vector(side*(KEY_BACK_W-KEY_ROOT_W+2*clearance),0,0))
    return _button_support(shank,center,side,build_direction,installed=installed)


def _head_supported_sides(head,center,side,build_direction,*,installed=False,clearance=0.):
    """Clip lower head wings to45degree faces rooted on the actual shank.

    The shank, head back station and pull-through lead remain separate. The
    two planes open upward in the print frame; their roots are the shank's
    exact intersection with the existing underside at the head back.
    """
    build=cq.Vector(*build_direction).normalized();escape=cq.Vector(side,0,0)
    b=cq.Vector(0,build.y,build.z).normalized();t=cq.Vector(0,b.z,-b.y)
    air=(-KEY_SEAT_SQUEEZE if installed else 0.)+clearance
    a=KEY_NECK_U+air;top=KEY_NECK_TOP+air*2**.5
    poly=[(-a,KEY_NECK_BOTTOM-air),(a,KEY_NECK_BOTTOM-air),(a,top-a),(0,top),(-a,top-a)]
    c=build.dot(escape);h=(1-c*c)**.5
    normal=build*(h+c)-escape
    hub=cq.Vector(0,center[1],center[2]);q=hub+escape*KEY_ROOT_W
    level=normal.dot(q)-h*6.
    if installed:level+=KEY_SEAT_SQUEEZE*normal.Length
    floor=(level-normal.dot(hub+escape*KEY_BACK_W))/normal.dot(b)
    ends=[]
    for p0,p1 in zip(poly,poly[1:]+poly[:1]):
        aa=cq.Vector(0,*p0);bb=cq.Vector(0,*p1);ba=aa.dot(b);bv=bb.dot(b)
        if (ba-floor)*(bv-floor)<=0 and abs(bv-ba)>1e-9:
            ends.append((aa+(bb-aa)*((floor-ba)/(bv-ba))).dot(t))
    # Start both supported sides on the actual shank projection. The broad
    # shared back face supplies the join without exposed shank-corner tips.
    lo,hi=min(ends),max(ends)
    for inward,rhs in ((b+t,floor+lo),(b-t,floor-hi)):
        origin=hub+inward*(rhs/inward.Length**2)
        keep=cq.Workplane(cq.Plane(origin=origin,xDir=escape,normal=inward)).box(400,400,400,centered=(True,True,False)).val()
        head=head.intersect(keep)
    return head.clean()


def button(center,side,*,installed=False,clearance=0.,build_direction=(0.,-2**-.5,2**-.5)):
    """A local pull-through head with a45degree print-supported underside."""
    _,u,v=center
    shank=button_neck(center,side,installed=installed,clearance=clearance,build_direction=build_direction)
    back=[(-6-clearance,-7-clearance),(6+clearance,-7-clearance),(6+clearance,KEY_HEAD_TOP+clearance),(-6-clearance,KEY_HEAD_TOP+clearance)]
    tip=[(-4.5-clearance,-5.5-clearance),(4.5+clearance,-5.5-clearance),(4.5+clearance,KEY_TIP_TOP+clearance),(-4.5-clearance,KEY_TIP_TOP+clearance)]
    head=cq.Solid.makeLoft([_profile(KEY_BACK_W-clearance,u,v,back,side),_profile(KEY_FRONT_W+clearance,u,v,tip,side)],True)
    head=_head_supported_sides(head,center,side,build_direction,installed=installed,clearance=clearance)
    return _button_support(shank.fuse(head),center,side,build_direction,installed=installed)


def mount_stations(layout):
    """Two broad keys; the outlet head clears the original valve-tray face."""
    _,_,h=frame(layout)
    return (tuple(layout['input']['tube_stop']),
            (cq.Vector(*layout['output']['tube_stop'])-h*OUTPUT_KEY_FORWARD).toTuple())


def _geometry(layout,*,installed=False,mount_side=-1):
    """Return local wet body/envelope/void and the common fixture frame."""
    local=local_layout(layout)
    seal=plumbing.TUBE_OD if installed else SEAL_BORE_D
    od=math.sqrt(BODY_OD**2+plumbing.TUBE_OD**2-SEAL_BORE_D**2) if installed else BODY_OD
    outer=_sweep(od,local['flow_segments'])
    void=_sweep(plumbing.TUBE_ID,local['flow_segments'])
    void=void.fuse(cached_flow_cap(local['flow_segments'][3],plumbing.TUBE_ID/2))
    for port in ('input','output'):
        p=local[port];d=cq.Vector(*p['axis']);stop=cq.Vector(*p['tube_stop'])
        seal_end=stop+d*plumbing.SEAL_LAND
        void=void.fuse(cq.Solid.makeCylinder(seal/2,plumbing.SEAL_LAND,stop,d),
                      cq.Solid.makeCone(seal/2,seal/2+ENTRY_RADIAL,plumbing.ENTRY_LEAD,seal_end,d),
                      cq.Solid.makeCylinder(seal/2+ENTRY_RADIAL,.05,cq.Vector(*p['point']),d))
    # A flat outer heel cuts0.70mm from the3.71mm round flow wall on the
    # outside of the last bend. The roof augmentation is on its inner side.
    posed=outer.rotate((0,0,0),(1,0,0),-45)
    heel=posed.BoundingBox().zmin+PRINT_HEEL_TRIM
    bounds=posed.BoundingBox();margin=20
    keep=cq.Solid.makeBox(bounds.xlen+2*margin,bounds.ylen+2*margin,bounds.zlen+margin,
        cq.Vector(bounds.xmin-margin,bounds.ymin-margin,heel)).rotate((0,0,0),(1,0,0),45)
    # The complete occupied arc section, rather than its centreline extent,
    # defines a45degree exterior heel. Reflection puts the roof construction
    # below the bend in the selected print frame; the flat bed stays fixed.
    def reflected_print(v):
        x,y,z=v;return (x,(y+z)/2**.5,(y-z)/2**.5)
    segment=local['flow_segments'][3]
    reflected={k:reflected_print(v) if k in ('start_mm','midpoint_mm','end_mm','start_tangent','end_tangent') else v for k,v in segment.items()}
    heel_cap=cached_exterior_cap(reflected,od/2,print_angle=0).mirror('XY').rotate((0,0,0),(1,0,0),45)
    outer=outer.fuse(heel_cap).intersect(keep).clean()
    keys=[button(point,mount_side,installed=installed) for point in mount_stations(local)]
    envelope=outer.fuse(*keys).clean()
    return {'body':envelope.cut(void).clean(),'envelope':envelope,'bare_envelope':outer,
            'void':void.clean(),'layout':local,'mount_side':mount_side,'heel_print_z':heel,
            'keys':tuple(keys)}


@lru_cache(maxsize=24)
def _cached_geometry(declaration,installed,mount_side):
    return _geometry(json.loads(declaration),installed=installed,mount_side=mount_side)


def geometry(layout,*,installed=False,mount_side=-1):
    return _cached_geometry(json.dumps(layout,sort_keys=True),installed,mount_side)


def build_return(layout,*,installed=False,mount_side=None):
    if mount_side is None:mount_side=1 if layout['input']['point'][0]>0 else -1
    return to_world(geometry(layout,installed=installed,mount_side=mount_side)['body'],layout)


def return_envelope(layout,*,installed=False,mount_side=None):
    if mount_side is None:mount_side=1 if layout['input']['point'][0]>0 else -1
    return to_world(geometry(layout,installed=installed,mount_side=mount_side)['envelope'],layout)


def print_solid(layout,*,mount_side=-1):
    body=geometry(layout,mount_side=mount_side)['body'].rotate((0,0,0),(1,0,0),-45)
    return body.translate((0,0,-body.BoundingBox().zmin))


def engineering_record():
    return {'material':MATERIAL,'relaxed_body_od_mm':BODY_OD,
       'occupied_body_od_mm':math.sqrt(BODY_OD**2+plumbing.TUBE_OD**2-SEAL_BORE_D**2),
       'seal_bore_mm':SEAL_BORE_D,'seal_land_mm':plumbing.SEAL_LAND,
       'entry_axial_mm':plumbing.ENTRY_LEAD,'entry_radial_mm':ENTRY_RADIAL,
       'flow_reach_before_curve_mm':plumbing.FLOW_REACH,'flow_radius_mm':plumbing.RETURN_ARC_R,
       'heel_trim_mm':PRINT_HEEL_TRIM,'output_key_forward_mm':OUTPUT_KEY_FORWARD,'mount_neck_w_mm':[KEY_ROOT_W,KEY_BACK_W],
       'mount_head_w_mm':[KEY_BACK_W,KEY_FRONT_W],'cover_w_mm':[COVER_FRONT_W,COVER_BACK_W],
       'mount_neck_profile_uv_mm':[[-4,-6],[4,-6],[4,KEY_NECK_SHOULDER],[0,KEY_NECK_TOP],[-4,KEY_NECK_SHOULDER]],
       'scope':'Factory permanent wet fitting. Geometry and local mounting only; no measured insertion force, seal, pressure, retention, wet-service or lifetime rating.'}
