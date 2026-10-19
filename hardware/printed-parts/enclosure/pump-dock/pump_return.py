"""Permanent compound TPU returns.

A shared declaration owns every port and straight-link datum. The body turns
45 degrees, crosses to the original valve station and turns 90 degrees upward.
All sealing lands stay circular. Only the last flow turn receives 45-degree
print roofs: inside its passage, and outside on the heel that rests on the bed.
The round body snaps into the return block's channel; it carries no other
mounting feature.
"""
from functools import lru_cache
import json
import math
import cadquery as cq
import fixed_returns as plumbing
from flow_roof import teardrop_sweep

BODY_OD=11.72
SEAL_BORE_D=6.10
ENTRY_RADIAL=.25
MATERIAL='Siraya Tech Flex TPU85A Clear'
COLOR=cq.Color(.92,.92,.90,.60)
PRINT_HEEL_TRIM=.70
STOP_WALL=3.0


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


def _geometry(layout,*,installed=False):
    """Return local wet body/envelope/void in the return's own frame."""
    local=local_layout(layout)
    seal=plumbing.TUBE_OD if installed else SEAL_BORE_D
    od=math.sqrt(BODY_OD**2+plumbing.TUBE_OD**2-SEAL_BORE_D**2) if installed else BODY_OD
    turn=local['flow_segments'][3]
    outer=_sweep(od,local['flow_segments'])
    # The flat heel is cut from the round body; its outward teardrop leaves a foot on the bed.
    # In place, the heel stops at the body's own underside.
    posed=outer.rotate((0,0,0),(1,0,0),-45)
    heel=posed.BoundingBox().zmin+PRINT_HEEL_TRIM
    bounds=posed.BoundingBox();margin=20
    keep=cq.Solid.makeBox(bounds.xlen+2*margin,bounds.ylen+2*margin,bounds.zlen+margin,
        cq.Vector(bounds.xmin-margin,bounds.ymin-margin,heel)).rotate((0,0,0),(1,0,0),45)
    level=outer.BoundingBox()
    above=cq.Solid.makeBox(level.xlen+2*margin,level.ylen+2*margin,level.zlen+2*margin,
        cq.Vector(level.xmin-margin,level.ymin-margin,level.zmin))
    outer=outer.fuse(teardrop_sweep(turn,od/2,inward=False)).intersect(keep).intersect(above).clean()
    # The passage roof ends a wall short of the outlet's tube stop, which bears on solid TPU.
    roof=teardrop_sweep(turn,plumbing.TUBE_ID/2,inward=True);span=roof.BoundingBox()
    floor=local['output']['tube_stop'][2]-STOP_WALL
    roof=roof.intersect(cq.Solid.makeBox(span.xlen+2,span.ylen+2,floor-span.zmin+1,
        cq.Vector(span.xmin-1,span.ymin-1,span.zmin-1)))
    void=_sweep(plumbing.TUBE_ID,local['flow_segments']).fuse(roof)
    for port in ('input','output'):
        p=local[port];d=cq.Vector(*p['axis']);stop=cq.Vector(*p['tube_stop'])
        seal_end=stop+d*plumbing.SEAL_LAND
        void=void.fuse(cq.Solid.makeCylinder(seal/2,plumbing.SEAL_LAND,stop,d),
                      cq.Solid.makeCone(seal/2,seal/2+ENTRY_RADIAL,plumbing.ENTRY_LEAD,seal_end,d),
                      cq.Solid.makeCylinder(seal/2+ENTRY_RADIAL,.05,cq.Vector(*p['point']),d))
    return {'body':outer.cut(void).clean(),'envelope':outer,
            'void':void.clean(),'layout':local,'heel_print_z':heel}


@lru_cache(maxsize=24)
def _cached_geometry(declaration,installed):
    return _geometry(json.loads(declaration),installed=installed)


def geometry(layout,*,installed=False):
    return _cached_geometry(json.dumps(layout,sort_keys=True),installed)


def build_return(layout,*,installed=False):
    return to_world(geometry(layout,installed=installed)['body'],layout)


def return_envelope(layout,*,installed=False):
    return to_world(geometry(layout,installed=installed)['envelope'],layout)


def print_solid(layout):
    body=geometry(layout)['body'].rotate((0,0,0),(1,0,0),-45)
    return body.translate((0,0,-body.BoundingBox().zmin))


def engineering_record():
    return {'material':MATERIAL,'relaxed_body_od_mm':BODY_OD,
       'occupied_body_od_mm':math.sqrt(BODY_OD**2+plumbing.TUBE_OD**2-SEAL_BORE_D**2),
       'seal_bore_mm':SEAL_BORE_D,'seal_land_mm':plumbing.SEAL_LAND,
       'entry_axial_mm':plumbing.ENTRY_LEAD,'entry_radial_mm':ENTRY_RADIAL,
       'flow_reach_before_curve_mm':plumbing.FLOW_REACH,'flow_radius_mm':plumbing.RETURN_ARC_R,
       'heel_trim_mm':PRINT_HEEL_TRIM,
       'scope':'Factory permanent wet fitting. Geometry only; no measured insertion force, seal, pressure, retention, wet-service or lifetime rating.'}
