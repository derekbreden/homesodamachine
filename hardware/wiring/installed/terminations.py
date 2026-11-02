"""Installed housings, dressed fuse leads and joint insulation.

These are purchased-part layout envelopes. Latches, crimp barrels and the
on-hand copies' manufacturing tolerances remain outside this representation.
"""
from __future__ import annotations


def final_join_placements():
    """The three unmounted joins dressed below the removable funnel frame."""
    return {
        'compressor-h': (-65., 247., 290.5),
        'compressor-n': (-85., 247., 290.5),
        'pump-positive': (-45., 255., 278.),
    }


RING_BORE = 3.2  # M3 clearance through the ring's eye


def _cylinder(radius,height,base=(0.,0.,0.),axis=(0.,0.,1.)):
    return {'radius_mm':radius,'height_mm':height,'base_mm':base,'axis':axis}


def _ring_input(ea):
    from .terminals import carbonator_bond_datums
    d = carbonator_bond_datums(ea)
    t, eye = d['ring_tongue_thickness_mm'], d['ring_eye_diameter_mm']
    barrel, reach = d['ring_barrel_diameter_mm'], d['ring_barrel_length_mm']
    return {'kind':'ring','eye':_cylinder(eye/2,t),
            'bore':_cylinder(RING_BORE/2,t+2,(0.,0.,-1.)),
            'barrel':_cylinder(barrel/2,reach,(eye/2-1,0.,barrel/2),(1.,0.,0.)),
            'origin_mm':d['contact_point_mm'],'x_dir':d['wire_outward'],
            'normal':d['contact_outward']},d


def inputs(attachments,connections,routes):
    """Ordered source geometry inputs and the installed termination facts."""
    from .model import sub,mul,rounded_segments
    records={};bodies=[]
    terminals=attachments.terminals
    import above_core_wiring as junctions
    for id, point in final_join_placements().items():
        name = 'wiring-junction-'+id
        pose = {'rotation':junctions.PORTS_FORE, 'translation_mm':point}
        bodies.append((name,{'kind':'import','step':junctions.REFERENCES['413'],
                             'pose':pose},junctions.C_AC_HUB))
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
    ring,bond = _ring_input(attachments.ea)
    bodies.append((name,ring,(.32,.55,.30)))
    records[name] = {
        'kind': 'M3 closed-ring earth terminal',
        'terminal_ids': ['carbonator.PE'],
        'attachment': 'cold-core/carbonator-tube',
        'status': 'Nominal owned M3 / 22–16 AWG ring envelope; metal clamp defined by shared rim datums',
        'tongue_thickness_mm': bond['ring_tongue_thickness_mm'],
        'barrel_diameter_mm': bond['ring_barrel_diameter_mm'],
        'barrel_length_mm': bond['ring_barrel_length_mm'],
    }
    for header in ('J1','J2','J3','J4','J5','J6','J7','J9','J11','J13'):
        # Include empty cavities in the physical housing, independently of
        # whether their contact is populated in the electrical graph.
        pins=sorted((t for id,t in terminals.items() if id.startswith(header+'.')),
                    key=lambda t:int(t.pin))
        first,last=pins[0],pins[-1]
        centre=tuple((a+b)/2 for a,b in zip(first.point,last.point))
        row=sub(last.point,first.point)
        axis=first.outward
        floor=sub(centre,mul(axis,7.5))
        width=(len(pins)-1)*2.5+4.8
        name='terminal-'+header
        bodies.append((name,{'kind':'housing','origin_mm':floor,'x_dir':row,'normal':axis,
                             'dimensions_mm':[width,5.7,7.5],
                             'bores':[_cylinder(.98,7.7,sub(pin.point,mul(axis,7.6)),axis)
                                      for pin in pins]},(.86,.85,.79)))
        records[name]={'kind':'JST-XH housing envelope','housing':f'XHP-{len(pins)}',
                       'dimensions_mm':[width,5.7,7.5],'assembled_height_above_board_mm':9.8,
                       'source':'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf',
                       'status':'nominal envelope; latch detail and on-hand clone fit unqualified',
                       'terminal_ids':[p.id for p in pins],
                       'mating_terminals':{
                           p.id:{'part':p.part,'point':p.point,'outward':p.outward,
                                 'pin':p.pin} for p in pins}}
    for label,lead in attachments.fuse_leads.items():
        segments=rounded_segments(lead['points_mm'],lead['bend_radius_mm'],keep_collinear=True)
        name='terminal-fuse-'+label+'-lead'
        bodies.append((name,{'kind':'sweep','connection_id':'fuse-'+label,
                             'points_mm':lead['points_mm'],'segments':segments,
                             'diameter_mm':lead['lead_diameter_mm']},(.62,.63,.65)))
        records[name]={**lead,'kind':'Dressed thermal-fuse lead','segments':segments,
                       'retained_lead_length_mm':lead['native_straight_mm']+sum(s['length_mm'] for s in segments)-1.5,
                       'reference_stub_overlap_mm':1.5,'terminal_ids':['fuse.'+label]}
        t=terminals['fuse.'+label];p=t.point;axis=t.outward
        name='terminal-fuse-'+label+'-splice'
        bodies.append((name,{'kind':'sleeve','outer':_cylinder(1.6,6.,p,axis),
                             'inner':_cylinder(1.3,6.02,sub(p,mul(axis,.01)),axis)},
                       (.04,.04,.045)))
        records[name]={'kind':'Insulated fuse-splice envelope','outer_diameter_mm':3.2,
                       'length_mm':6.,'status':'proposed joint and recovered sleeve profile',
                       'terminal_ids':['fuse.'+label]}
    return bodies,records


def _native(recipe,steps):
    import cadquery as cq
    def cylinder(r):
        return cq.Solid.makeCylinder(r['radius_mm'],r['height_mm'],
                                     cq.Vector(*r['base_mm']),cq.Vector(*r['axis']))
    def plane(r):
        return cq.Plane(origin=r['origin_mm'],xDir=r['x_dir'],normal=r['normal'])
    kind=recipe['kind']
    if kind=='import':
        from _cadq_export import import_step
        import above_core as layout
        path=recipe['step']
        if path not in steps:steps[path]=import_step(path).val()
        return steps[path].moved(layout.frame_location(recipe['pose']))
    if kind=='ring':
        ring=cylinder(recipe['eye']).cut(cylinder(recipe['bore'])).fuse(cylinder(recipe['barrel'])).clean()
        return ring.moved(cq.Location(plane(recipe)))
    if kind=='housing':
        housing=cq.Workplane(plane(recipe)).box(*recipe['dimensions_mm'],centered=(True,True,False)).val()
        for bore in recipe['bores']:housing=housing.cut(cylinder(bore))
        return housing
    if kind=='sweep':
        from .model import Route,Connection,shape
        return shape(Route(Connection(recipe['connection_id'],'Compressor','','',''),
                           recipe['points_mm'],recipe['segments']),
                     recipe['diameter_mm'])
    if kind=='sleeve':return cylinder(recipe['outer']).cut(cylinder(recipe['inner']))
    raise ValueError(('Unknown termination geometry',kind))


def carbonator_ring(ea):
    """Closed M3 lug on the existing upper tube rim, barrel pointing up."""
    return _native(_ring_input(ea)[0],{})


def add_terminations(assembly,attachments,connections,routes):
    import cadquery as cq
    bodies,records=inputs(attachments,connections,routes)
    steps={}
    for name,recipe,color in bodies:
        if isinstance(color,tuple):color=cq.Color(*color)
        assembly.add(_native(recipe,steps),name=name,color=color)
    return records
