"""Shared cable paths and parallel-transported insulated conductors."""
import json
import math
from pathlib import Path
from .model import Route, add, sub, mul, unit, dot, norm, rounded_segments

SOURCE=Path(__file__).with_name('bundle-routes.json')


def definitions(): return json.loads(SOURCE.read_text())


def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def rotate(v,axis,angle):
    return add(add(mul(v,math.cos(angle)),mul(cross(axis,v),math.sin(angle))),
               mul(axis,dot(axis,v)*(1-math.cos(angle))))


def circle(segment):
    a,mid,b=(segment[k] for k in ('start_mm','midpoint_mm','end_mm'))
    u,v=sub(mid,a),sub(b,a);n=cross(u,v)
    centre=add(a,mul(add(mul(cross(n,u),dot(v,v)),mul(cross(v,n),dot(u,u))),1/(2*dot(n,n))))
    return centre,unit(n)


def offset_path(segments,section):
    """Carry a section offset through every bend without twisting its plane.

    Lines retain their section. At a circular bend the whole section rotates
    about that bend's axis, yielding concentric circular core paths. The two
    section axes start with projected world X and its right-handed complement.
    """
    tangent=unit(sub(segments[0]['end_mm'],segments[0]['start_mm']))
    reference=(1.,0.,0.) if abs(tangent[0])<.9 else (0.,0.,1.)
    u=unit(sub(reference,mul(tangent,dot(reference,tangent))));v=cross(tangent,u)
    offset=add(mul(u,section[0]),mul(v,section[1]));out=[]
    for s in segments:
        row=dict(s);row['start_mm']=add(s['start_mm'],offset)
        if s['kind']=='line':
            row['end_mm']=add(s['end_mm'],offset)
        else:
            centre,axis=circle(s);angle=s['angle_radians']
            row['midpoint_mm']=add(s['midpoint_mm'],rotate(offset,axis,angle/2))
            new_offset=rotate(offset,axis,angle)
            row['end_mm']=add(s['end_mm'],new_offset)
            core_centre=add(centre,mul(axis,dot(offset,axis)))
            row['radius_mm']=norm(sub(row['start_mm'],core_centre))
            row['length_mm']=row['radius_mm']*angle
            offset=new_offset
        out.append(row)
    return out


def trimmed(segments,front,back):
    """Trim the jacket while retaining the cores' exact bend centres."""
    end=sum(s['length_mm'] for s in segments)-back
    position=0.;out=[]
    for s in segments:
        length=s['length_mm'];lo=max(front-position,0.);hi=min(end-position,length)
        position+=length
        if hi<=lo:continue
        a,b=lo/length,hi/length;row=dict(s);row['length_mm']=hi-lo
        if s['kind']=='line':
            direction=sub(s['end_mm'],s['start_mm'])
            row['start_mm']=add(s['start_mm'],mul(direction,a))
            row['end_mm']=add(s['start_mm'],mul(direction,b))
        else:
            centre,axis=circle(s);radial=sub(s['start_mm'],centre);angle=s['angle_radians']
            row['start_mm']=add(centre,rotate(radial,axis,angle*a))
            row['midpoint_mm']=add(centre,rotate(radial,axis,angle*(a+b)/2))
            row['end_mm']=add(centre,rotate(radial,axis,angle*b))
            row['angle_radians']=angle*(b-a)
        out.append(row)
    return out


def centreline(b,attachments):
    if 'passage' in b:
        cached=getattr(attachments,'_shared_cap_cables',{})
        if b['passage'] in cached:
            return cached[b['passage']]
        import _above_core_mounts
        import _internal_routes
        corridor=_above_core_mounts.cable_guide_points(b['passage'])
        source_points=list(reversed(corridor['points_mm']))
        if b.get('above_cap_stations_mm'):
            source_points=[*map(tuple,b['above_cap_stations_mm']),*source_points]
        native=_internal_routes.route_wire(source_points,
            b.get('above_cap_bend_radius_mm',corridor['bend_radius_mm']))
        # Read the actual native bore's edges, including its own fitted radii.
        # A different polyline fillet rule can drift outside this narrow bore.
        remaining=list(native.Edges());segments=[];cursor=tuple(source_points[0])
        while remaining:
            i,edge,reverse=next((i,e,reverse) for i,e in enumerate(remaining)
                                for reverse in (False,True)
                                if math.dist(cursor,(e.endPoint() if reverse else e.startPoint()).toTuple())<1e-6)
            remaining.pop(i)
            end=(edge.startPoint() if reverse else edge.endPoint()).toTuple()
            row={'kind':'line','start_mm':cursor,'end_mm':end,'length_mm':edge.Length()}
            if edge.geomType()=='CIRCLE':
                radius=edge.radius()
                row.update(kind='arc',midpoint_mm=edge.positionAt(.5).toTuple(),
                           radius_mm=radius,angle_radians=edge.Length()/radius)
            segments.append(row);cursor=end
        first=tuple(source_points[0])
        points=source_points
        if not b.get('above_cap_stations_mm'):
            top=(first[0],first[1],270.)
            segments.insert(0,{'kind':'line','start_mm':top,'end_mm':first,
                               'length_mm':math.dist(top,first)})
            points=[top,*source_points]
        cached[b['passage']]=(points,segments)
        attachments._shared_cap_cables=cached
        return points,segments
    else:
        points=[attachments.station(s) for s in b['stations']]
    return points,rounded_segments(points,b['bend_radius_mm'],keep_collinear=True)


def entry_stations(connection,b,attachments,first):
    """Dress moved endpoint fanouts to the complete shared cable route."""
    p=attachments.terminals[connection.start].point
    fan=b.get('fanouts',{}).get(connection.id,{})
    if fan.get('entry_stations'):
        return [attachments.station(s) for s in fan['entry_stations']]
    if b.get('entry_family')=='cap-cable':
        if b['passage']=='reed-cable-a':
            z=300.+(int(connection.start[-1]) if connection.start[-1].isdigit() else 0)*1.8
            return [(p[0],p[1],282.),(-49.,p[1],282.),(-49.,280.5,282.),
                    (-49.,280.5,z),(-49.,first[1],z),(first[0],first[1],z)]
        return [(p[0],p[1],282.),(p[0],280.5,282.),(-49.,280.5,282.),
                (-49.,first[1],282.),(first[0],first[1],282.)]
    return [attachments.station(s) for s in b['fanouts'][connection.id].get('entry_stations',[])]


def core_route(connection,attachments):
    for id,b in definitions().items():
        if connection.id not in b['cores']:continue
        _points,shared=centreline(b,attachments)
        core=offset_path(shared,b['cores'][connection.id])
        a,end=(attachments.terminals[x] for x in (connection.start,connection.end))
        first,last=core[0]['start_mm'],core[-1]['end_mm']
        entry_land,exit_land=b.get('fanout_tangent_mm',[6.,6.])
        head=sub(first,mul(unit(sub(core[0]['end_mm'],first)),entry_land))
        tail=add(last,mul(unit(sub(last,core[-1]['start_mm'])),exit_land))
        fan=b['fanouts'][connection.id]
        entry=[a.point,add(a.point,mul(a.outward,fan['end_lands_mm'][0])),
               *entry_stations(connection,b,attachments,first),head,first]
        exit=[last,tail,*[attachments.station(s) for s in fan.get('exit_stations',[])],
              add(end.point,mul(end.outward,fan['end_lands_mm'][1])),end.point]
        fixed_stations=b.get('jacket',True)
        segments=(rounded_segments(entry,fan.get('bend_radius_mm',4.),keep_collinear=fixed_stations,
                                   endpoint_tangent_fraction=fan.get('endpoint_tangent_fraction',.44))+
                  core+rounded_segments(exit,fan.get('bend_radius_mm',4.),keep_collinear=fixed_stations))
        radii=[s['radius_mm'] for s in segments if s['kind']=='arc']
        route=Route(connection,entry+[s['end_mm'] for s in core]+exit[1:],segments,
                    sum(s['length_mm'] for s in segments),min(radii) if radii else None,
                    fan.get('route_status',b['route_status']),
                    b.get('description','Shared SJOOW jacket with transported core sections and individually dressed end fanouts.'))
        return route
    return None


def add_jackets(assembly,attachments):
    import cadquery as cq
    records={}
    for id,b in definitions().items():
        points,shared=centreline(b,attachments)
        if not b.get('jacket',True):
            records[id]={**b,'geometry_name':None,'points_mm':points,'segments':shared,
                         'length_mm':sum(s['length_mm'] for s in shared),
                         'minimum_bend_mm':min((s['radius_mm'] for s in shared if s['kind']=='arc'),default=None)}
            continue
        segments=trimmed(shared,b['end_trim_mm'],b['end_trim_mm'])
        edges=[]
        for s in segments:
            a,end=cq.Vector(*s['start_mm']),cq.Vector(*s['end_mm'])
            edges.append(cq.Edge.makeLine(a,end) if s['kind']=='line' else
                         cq.Edge.makeThreePointArc(a,cq.Vector(*s['midpoint_mm']),end))
        wire=cq.Wire.assembleEdges(edges);start=edges[0].startPoint();axis=edges[0].tangentAt(0)
        outer=cq.Wire.makeCircle(b['outer_diameter_mm']/2,start,axis)
        inner=cq.Wire.makeCircle(b['inner_diameter_mm']/2,start,axis)
        jacket=cq.Solid.sweep(outer,[inner],wire,makeSolid=True,isFrenet=False)
        name='terminal-'+id+'-jacket'
        assembly.add(jacket,name=name,color=cq.Color(.035,.035,.04))
        records[id]={**b,'geometry_name':name,'points_mm':points,'segments':segments,
                     'length_mm':sum(s['length_mm'] for s in segments),
                     'minimum_bend_mm':min((s['radius_mm'] for s in segments if s['kind']=='arc'),default=None)}
    return records
