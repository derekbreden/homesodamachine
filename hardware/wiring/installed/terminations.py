"""Installed housings, dressed fuse leads and joint insulation.

These are purchased-part layout envelopes. Latches, crimp barrels and the
on-hand copies' manufacturing tolerances remain outside this representation.
"""
from __future__ import annotations


def final_join_placements():
    """The three unmounted joins dressed below the removable funnel frame."""
    return {
        'compressor-h': (-65., 247., 290.5),
        'compressor-n': (-65., 221., 290.5),
        'pump-positive': (-45., 255., 278.),
    }


def carbonator_ring(ea):
    """Closed M3 lug on the existing upper tube rim, barrel pointing up."""
    import cadquery as cq
    from .terminals import carbonator_bond_datums
    d = carbonator_bond_datums(ea)
    plane = cq.Plane(origin=d['contact_point_mm'], xDir=d['wire_outward'],
                     normal=d['contact_outward'])
    return ea._gnd._ring(0., 0.).val().moved(cq.Location(plane))


def add_terminations(assembly,attachments,connections,routes):
    import cadquery as cq
    records={}
    terminals=attachments.terminals
    from _cadq_export import import_step
    import above_core as layout
    import above_core_wiring as junctions
    native = import_step(junctions.REFERENCES['413']).val()
    for id, point in final_join_placements().items():
        name = 'wiring-junction-'+id
        pose = {'rotation':junctions.PORTS_FORE, 'translation_mm':point}
        assembly.add(native.moved(layout.frame_location(pose)), name=name,
                     color=junctions.C_AC_HUB)
        used = sorted({t for c in connections for t in (c.start,c.end)
                       if t.startswith('join-'+id+'.')})
        records[name] = {
            'kind':'WAGO 221-413 final connection', 'size':'413',
            'parent':'final-connections', 'translation_mm':point,
            'rotation':junctions.PORTS_FORE,
            'terminal_ids':used,
            'unused_ports':[i for i in (1,2,3) if f'join-{id}.{i}' not in used],
            'mount':'Free connector retained by its dressed leads',
            'assembly':'Connect through the open funnel after closing the quadrants; fit the frame afterward.',
        }
    name = 'terminal-carbonator-pe'
    assembly.add(carbonator_ring(attachments.ea), name=name,
                 color=cq.Color(.32, .55, .30))
    records[name] = {
        'kind': 'M3 closed-ring earth terminal',
        'terminal_ids': ['carbonator.PE'],
        'attachment': 'cold-core/carbonator-tube',
        'status': 'Nominal owned M3 / 22–16 AWG ring envelope; metal clamp defined by shared rim datums',
        'tongue_thickness_mm': attachments.ea._gnd.tongue_t,
        'barrel_diameter_mm': attachments.ea._gnd.barrel_d,
        'barrel_length_mm': attachments.ea._gnd.barrel_len,
    }
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
