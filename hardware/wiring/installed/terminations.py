"""Installed housings, dressed fuse leads and joint insulation.

These are purchased-part layout envelopes. Latches, crimp barrels and the
on-hand copies' manufacturing tolerances remain outside this representation.
"""
from __future__ import annotations
import math


def _lead_prefix(route, length, reverse=False):
    """The sleeve follows the wire's exact initial lines and circular bends."""
    from .bundles import trimmed
    segments = route.segments
    if reverse:
        segments = [{**s, 'start_mm': s['end_mm'], 'end_mm': s['start_mm']}
                    for s in reversed(segments)]
    return trimmed(segments, 0., max(0., sum(s['length_mm'] for s in segments)-length))


def add_terminations(assembly,attachments,connections,routes):
    import cadquery as cq
    records={}
    terminals=attachments.terminals
    for header in ('J1','J2','J3','J4','J5','J6','J7','J9','J11','J13'):
        # Include empty cavities in the physical housing, independently of
        # whether their contact is populated in the electrical graph.
        pins=sorted((t for id,t in terminals.items() if id.startswith(header+'.')),
                    key=lambda t:int(t.pin))
        first,last=pins[0],pins[-1]
        centre=tuple((a+b)/2 for a,b in zip(first.point,last.point))
        row=cq.Vector(*last.point)-cq.Vector(*first.point)
        axis=cq.Vector(*first.outward)
        floor=cq.Vector(*centre)-axis*7.5
        plane=cq.Plane(origin=floor,xDir=row,normal=axis)
        width=(len(pins)-1)*2.5+4.8
        housing=cq.Workplane(plane).box(width,5.7,7.5,centered=(True,True,False)).val()
        # Wire throats are separate from the detailed internal contact cavities.
        for pin in pins:
            p=cq.Vector(*pin.point)-axis*7.6
            housing=housing.cut(cq.Solid.makeCylinder(.98,7.7,p,axis))
        name='terminal-'+header
        assembly.add(housing,name=name,color=cq.Color(.86,.85,.79))
        records[name]={'kind':'JST-XH housing envelope','housing':f'XHP-{len(pins)}',
                       'dimensions_mm':[width,5.7,7.5],'assembled_height_above_board_mm':9.8,
                       'source':'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf',
                       'status':'nominal envelope; latch detail and on-hand clone fit unqualified',
                       'terminal_ids':[p.id for p in pins],
                       'mating_terminals':{
                           p.id:{'part':p.part,'point':p.point,'outward':p.outward,
                                 'pin':p.pin} for p in pins}}
    from .model import Route,Connection,rounded_segments,shape
    for side in ('male','female'):
        for i in range(1,5):
            terminal=terminals[f'pogo-{side}.{i}']
            wire=next(r for r in routes if terminal.id in (r.connection.start,r.connection.end))
            segments=_lead_prefix(wire,4.,reverse=wire.connection.end==terminal.id)
            sleeve_route=Route(wire.connection,[],segments)
            sleeve=shape(sleeve_route,2.3,1.72)
            name=f'terminal-pogo-{side}-{i}'
            assembly.add(sleeve,name=name,color=cq.Color(.04,.04,.045))
            records[name]={'kind':'Individual solder-joint heat shrink','outer_diameter_mm':2.3,
                           'length_mm':4.,'status':'proposed recovered profile; actual sleeve/finished joint unmeasured',
                           'wire':wire.connection.id,'segments':segments,
                           'terminal_ids':[terminal.id]}
    for label,lead in attachments.fuse_leads.items():
        segments=rounded_segments(lead['points_mm'],lead['bend_radius_mm'],keep_collinear=True)
        route=Route(Connection('fuse-'+label,'Compressor','','',''),lead['points_mm'],segments)
        name='terminal-fuse-'+label+'-lead'
        assembly.add(shape(route,lead['lead_diameter_mm']),name=name,color=cq.Color(.62,.63,.65))
        records[name]={**lead,'kind':'Dressed thermal-fuse lead','segments':segments,
                       'retained_lead_length_mm':lead['native_straight_mm']+sum(s['length_mm'] for s in segments)-1.5,
                       'reference_stub_overlap_mm':1.5,'terminal_ids':['fuse.'+label]}
        t=terminals['fuse.'+label];p=cq.Vector(*t.point);axis=cq.Vector(*t.outward)
        sleeve=cq.Solid.makeCylinder(1.6,6.,p,axis).cut(cq.Solid.makeCylinder(1.3,6.02,p-axis*.01,axis))
        name='terminal-fuse-'+label+'-splice'
        assembly.add(sleeve,name=name,color=cq.Color(.04,.04,.045))
        records[name]={'kind':'Insulated fuse-splice envelope','outer_diameter_mm':3.2,
                       'length_mm':6.,'status':'proposed joint and recovered sleeve profile',
                       'terminal_ids':['fuse.'+label]}
    return records
