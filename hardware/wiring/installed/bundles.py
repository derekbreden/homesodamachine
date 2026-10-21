"""Common jacket routes and the conductors physically inside them."""
import json
from pathlib import Path
from .model import Connection,Route,add,sub,mul,unit,rounded_segments

SOURCE=Path(__file__).with_name('bundle-routes.json')


def definitions(): return json.loads(SOURCE.read_text())


def core_guide(connection,attachments):
    for id,b in definitions().items():
        if connection.id not in b['cores']:continue
        points=[add(attachments.station(s),b['cores'][connection.id]) for s in b['stations']]
        a=attachments.terminals[connection.start]
        head=add(points[0],mul(unit(sub(points[0],points[1])),15.))
        return id,[add(a.point,mul(a.outward,12.)),head,*points],b['bend_radius_mm']
    return None


def add_jackets(assembly,attachments):
    import cadquery as cq
    records={}
    for id,b in definitions().items():
        points=[attachments.station(s) for s in b['stations']]
        trim=b['end_trim_mm']
        points[0]=add(points[0],mul(unit(sub(points[1],points[0])),trim))
        points[-1]=add(points[-1],mul(unit(sub(points[-2],points[-1])),trim))
        route=Route(Connection(id,id,'','', ''),points)
        route.segments=rounded_segments(points,b['bend_radius_mm'])
        edges=[]
        for s in route.segments:
            a,end=cq.Vector(*s['start_mm']),cq.Vector(*s['end_mm'])
            edges.append(cq.Edge.makeLine(a,end) if s['kind']=='line' else
                         cq.Edge.makeThreePointArc(a,cq.Vector(*s['midpoint_mm']),end))
        wire=cq.Wire.assembleEdges(edges);start=cq.Vector(*points[0]);axis=edges[0].tangentAt(0)
        outer=cq.Wire.makeCircle(b['outer_diameter_mm']/2,start,axis)
        inner=cq.Wire.makeCircle(b['inner_diameter_mm']/2,start,axis)
        jacket=cq.Solid.sweep(outer,[inner],wire,makeSolid=True,isFrenet=False)
        name='terminal-'+id+'-jacket'
        assembly.add(jacket,name=name,color=cq.Color(.035,.035,.04))
        records[id]={**b,'geometry_name':name,'points_mm':points,'segments':route.segments,
                     'length_mm':sum(s['length_mm'] for s in route.segments)}
    return records
