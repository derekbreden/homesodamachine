"""Native45-degree flow-roof construction for permanent TPU wet parts.

The roof triangles are expressed in the selected print frame. Their lower
roots overlap the round passage; both roof edges rise at least45degrees.
A ruled loft joins the sections. Socket sealing lands are not supplied to
this function.
"""
import math
import cadquery as cq
from scipy.optimize import minimize_scalar
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections


def _pt(v):
    return cq.Vector(*v)


def _vtuple(v):
    return (v.x,v.y,v.z)


def _section_edges(solid,y):
    b=solid.BoundingBox()
    face=cq.Face.makePlane(b.xlen+4,b.zlen+4,
                           cq.Vector((b.xmin+b.xmax)/2,y,(b.zmin+b.zmax)/2),
                           cq.Vector(0,1,0))
    return solid.intersect(face).Edges()


def _support(edges,sx):
    """Native edge maximizer for z+sx*x; split each edge before optimizing."""
    best=(-math.inf,None)
    for edge in edges:
        def f(t):
            p=edge.positionAt(float(t));return p.z+sx*p.x,p
        grid=[i/12 for i in range(13)]
        values=[f(t) for t in grid]
        for value,p in values:
            if value>best[0]:best=(value,p)
        for i in range(13):
            if (i==0 or values[i][0]>=values[i-1][0]) and (i==12 or values[i][0]>=values[i+1][0]):
                opt=minimize_scalar(lambda t:-f(t)[0],bounds=(grid[max(0,i-1)],grid[min(12,i+1)]),
                                    method='bounded',options={'xatol':2e-10})
                value,p=f(opt.x)
                if value>best[0]:best=(value,p)
    if best[1] is None:raise ValueError('No closed native flow section')
    return best


def selfsupport_flow_cap(arc_segment,radius=2.15,*,print_angle=-45.,blend=.8,
                         max_step=.20,support_error=.003,crown_air=.006,
                         record=None,tangent_overlap=.10):
    """Return a cap-only native solid in the input frame for one flow arc.

    Use the last90degree arc and its short straight blends, outside all tube
    stops. Caller owns the actual outside stock and confirms deposition from
    the native slice. Adaptive support samples bound the reviewed local
    interpolation error; this is not a material or printer qualification.
    """
    start=_pt(arc_segment['start_mm']);mid=_pt(arc_segment['midpoint_mm']);end=_pt(arc_segment['end_mm'])
    ta=_pt(arc_segment['start_tangent']).normalized();tb=_pt(arc_segment['end_tangent']).normalized()
    pre=start-ta*blend;post=end+tb*blend
    pre_flow=start-ta*(blend+4*radius);post_flow=end+tb*(blend+4*radius)
    edges=[cq.Edge.makeLine(pre_flow,start),cq.Edge.makeThreePointArc(start,mid,end),cq.Edge.makeLine(end,post_flow)]
    wire=cq.Wire.assembleEdges(edges)
    flow=cq.Solid.sweep(cq.Wire.makeCircle(radius,pre_flow,ta),[],wire,makeSolid=True,isFrenet=True)
    flowp=flow.rotate((0,0,0),(1,0,0),print_angle)
    def rotate_point(p):
        a=math.radians(print_angle);return cq.Vector(p.x,p.y*math.cos(a)-p.z*math.sin(a),p.y*math.sin(a)+p.z*math.cos(a))
    a,b,p0,p1=map(rotate_point,(start,end,pre,post))
    if not(p0.y<a.y<b.y<p1.y):raise ValueError('Roof arc must progress monotonically along printY')
    y0,y1=p0.y,p1.y
    cache={};stats={'sections':0,'edge_count':0,'max_refinement_depth':0,'max_terminal_error_mm':0.}
    def section(y):
        if y in cache:return cache[y]
        es=_section_edges(flowp,y);stats['sections']+=1;stats['edge_count']+=len(es)
        hp,pp=_support(es,1);hm,pm=_support(es,-1);_,top=_support(es,0)
        apex=cq.Vector((hp-hm)/2,y,(hp+hm)/2)
        f=1. if a.y<=y<=b.y else (y-y0)/(a.y-y0) if y<a.y else (y1-y)/(y1-b.y)
        f=max(0.,min(1.,f))
        # A tiny outward allowance covers accepted sub-section interpolation.
        shift=cq.Vector(0,0,crown_air*f)
        # Bury both lower roots in the round passage. Moving the root down
        # twice its lateral reach keeps each roof side steeper than45degrees
        # while the crown allowance and fade leave the apex unchanged.
        tri=[top+(pm-top)*f+shift+cq.Vector(-tangent_overlap*f,0,-2*tangent_overlap*f),
             top+(pp-top)*f+shift+cq.Vector(tangent_overlap*f,0,-2*tangent_overlap*f),
             top+(apex-top)*f+shift]
        row={'y':y,'support':[hp,hm],'tri':tri,'top':top,'fade':f}
        cache[y]=row;return row
    # Avoid the exact swept end faces while finding the fade endpoint crown.
    first=section(y0);last=section(y1)
    # Crown of the ellipse section on the end plane has the same finite limit.
    first_point=cq.Vector(first['top'].x,y0,first['top'].z)
    last_point=cq.Vector(last['top'].x,y1,last['top'].z)
    accepted=[]
    def refine(left,right,depth=0):
        stats['max_refinement_depth']=max(stats['max_refinement_depth'],depth)
        test=[];err=0.
        for f in (.25,.5,.75):
            y=left['y']+(right['y']-left['y'])*f;r=section(y);test.append(r)
            for i in (0,1):err=max(err,abs(r['support'][i]-((1-f)*left['support'][i]+f*right['support'][i])))
        if (right['y']-left['y']>max_step or err>support_error) and depth<18:
            middle=test[1];refine(left,middle,depth+1);refine(middle,right,depth+1)
        else:
            accepted.append(left);stats['max_terminal_error_mm']=max(stats['max_terminal_error_mm'],err)
    anchors=[first,section(a.y),section(b.y),last]
    for left,right in zip(anchors,anchors[1:]):refine(left,right)
    accepted.append(last)
    loft=BRepOffsetAPI_ThruSections(True,True,1e-7)
    loft.AddVertex(cq.Vertex.makeVertex(*_vtuple(first_point)).wrapped)
    for row in accepted:
        if row['fade']<1e-6:continue
        tri=row['tri'];w=cq.Wire.makePolygon(tri+[tri[0]])
        loft.AddWire(w.wrapped)
    loft.AddVertex(cq.Vertex.makeVertex(*_vtuple(last_point)).wrapped)
    loft.CheckCompatibility(False);loft.Build()
    cap=cq.Shape.cast(loft.Shape()).clean().rotate((0,0,0),(1,0,0),-print_angle)
    # Global-Y sections contain inclined ellipses extending beyond their
    # centerline station. These exact local end planes keep augmentation
    # outside the socket stops; their printed slopes are at least45degrees.
    extent=cap.BoundingBox().DiagonalLength+8*radius+10
    for origin,normal in ((pre,ta),(post,tb*-1)):
        xd=cq.Vector(1,0,0) if abs(normal.x)<.9 else cq.Vector(0,1,0)
        xd=(xd-normal*xd.dot(normal)).normalized()
        keep=cq.Workplane(cq.Plane(origin=origin,xDir=xd,normal=normal)).box(extent,extent,extent,centered=(True,True,False)).val()
        cap=cap.intersect(keep).clean()
    if record is not None:
        record.update(print_angle_X_deg=print_angle,flow_radius_mm=radius,blend_mm=blend,
                      max_section_step_mm=max_step,requested_support_error_mm=support_error,
                      outward_roof_allowance_mm=crown_air,tangent_overlap_mm=tangent_overlap,
                      root_downward_overlap_mm=2*tangent_overlap,loft_sections=len(accepted),
                      exact_axial_clip_planes=[dict(point=_vtuple(pre),inward=_vtuple(ta)),dict(point=_vtuple(post),inward=_vtuple(tb*-1))],**stats,
                      cap_valid=cap.isValid(),cap_solids=len(cap.Solids()),cap_volume_mm3=cap.Volume(),
                      scope='Native adaptive roof construction only. Caller validates outside stock, stop separation and actual sliced deposition; no material/pressure/lifetime qualification.')
    return cap

# A translated copy of the same circular arc has the same roof. Cache the
# native construction by its local declaration, not by assembly position.
import functools
import json


@functools.lru_cache(maxsize=8)
def _cached_cap(declaration,radius,print_angle,blend):
    return selfsupport_flow_cap(json.loads(declaration),radius,
                                print_angle=print_angle,blend=blend)


def cached_flow_cap(arc_segment,radius=2.15,*,print_angle=-45.,blend=.8):
    origin=arc_segment['start_mm']
    local={k:tuple(round(v[i]-origin[i],12) for i in range(3))
             if k in ('start_mm','midpoint_mm','end_mm') else v
           for k,v in arc_segment.items()}
    shape=_cached_cap(json.dumps(local,sort_keys=True),radius,print_angle,blend)
    return shape.translate(origin)
