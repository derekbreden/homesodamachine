"""Complete mechanical bearings and dressed ties for the reorganized large runs.

Every fixed body has a declared print root. Nominal ties include their complete
band and an8×8×5mm locking head; keys include actual M3 screws and blind pilots.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
from io import BytesIO
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3];STUDY=ROOT/'future/pump-first-layout-study'
HERE=STUDY/'routing';OUT=ROOT/'.cache/pump-first-layout/routing/tube-hosts'
sys.path[:0]=[str(HERE),str(STUDY)];import audit,evidence_binding
from split_seat import split_seat
from received_native import receive,material_equivalence

def box(x0,y0,z0,x1,y1,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def localshape(s,p,u,n):
    n=cq.Vector(*n).normalized();u=cq.Vector(*u).normalized()
    return s.moved(cq.Location(cq.Plane(origin=cq.Vector(*p),xDir=n,normal=n.cross(u))))

def tied_seat(p,u,n,root,head_side=0,reach=6.325,tie_slip=0):
    """Nine-and-a-half-mm bearing with a3.5mm dressed-band tunnel."""
    r=3.325;outer=reach;length=9.5
    seat=box(0,-length/2,-outer,root,length/2,outer)
    bore=cq.Solid.makeCylinder(r,length+2,cq.Vector(0,-length/2-1,0),cq.Vector(0,1,0))
    tunnel=cq.Solid.makeCylinder(4.525+tie_slip,3.5,cq.Vector(0,-1.75,0),cq.Vector(0,1,0))
    seat=seat.cut(bore).cut(tunnel).clean()
    tie=cq.Solid.makeCylinder(4.175+tie_slip,2.5,cq.Vector(0,-1.25,0),cq.Vector(0,1,0)).cut(
        cq.Solid.makeCylinder(3.175+tie_slip,2.5,cq.Vector(0,-1.25,0),cq.Vector(0,1,0)))
    head_edge=outer+.325
    if head_side==0:head=box(-8.425,-4,-4,-3.425,4,4)
    elif head_side>0:head=box(0,-4,head_edge,5,4,head_edge+8)
    else:head=box(0,-4,-head_edge-8,5,4,-head_edge)
    tie=tie.fuse(head).clean()
    # The purchased head sits in an open-ended dressed pocket, leaving the
    # actual three-millimetre axial bearing webs on the opposite side.
    if head_side:
        vlo,vhi=(3.8,head_edge+.55)if head_side>0 else(-head_edge-.55,-3.8)
        tail=box(-.5,-1.25,vlo,.5,1.25,vhi)
        tie=tie.fuse(tail).clean()
        seat=seat.cut(box(-.6,-1.75,vlo-.15,.6,1.75,vhi+.15)).clean()
    q={k:localshape(s,p,u,n)for k,s in [('fixed',seat),('tie',tie),('tunnel',tunnel)]}
    for k in ['fixed','tie']:
        if not q[k].isValid()or len(q[k].Solids())!=1:raise ValueError(k+' not one valid solid')
    return q

def load():
    models,records,changed,mates,inputs=audit.collect()
    content_inputs={p:h for p,h in inputs.content_sha256.items()
                    if p!='future/pump-first-layout-study/routing/tube-hosts.json'}
    aliases={'funnel':'funnel/candidate.json','pump':'pump/candidate.json','pump-fluid24':'pump/fluid24-candidate.json',
        'routing':'routing/candidate.json','structure':'structure/candidate.json','mounts':'mounts/candidate.json',
        'wiring':'wiring/candidate.json','fluid-mounts':'mounts/fluid-candidate.json','body-mounts':'mounts/body-candidate.json',
        'water5-mounts':'mounts/water5-hosts.json','roof-hatch':'structure/roof-hatch.json','scene-stock':'structure/scene-stock.json'}
    inputs={aliases[k]:v for k,v in inputs.items()if k in aliases}
    circuit_scope={}
    for path in ['routing/co2-candidate.json','mounts/needle-candidate.json','mounts/wr-candidate.json','mounts/check-tee-candidate.json','wiring/control-reserves.json','wiring/control-fanouts-check.json','wiring/lower-lead-exits.json','wiring/power-candidate.json','wiring/controls-candidate.json']:
        f=STUDY/path
        if not f.exists():continue
        raw=f.read_bytes();m=json.loads(raw);inputs[path]=hashlib.sha256(raw).hexdigest()
        content_inputs[str(f.relative_to(ROOT))]=evidence_binding.content_sha256(m)
        if path=='wiring/power-candidate.json':circuit_scope['power_routes']=len(m.get('power_routes',{}))
        if path=='wiring/controls-candidate.json':
            circuit_scope['grouped_controls']=sum(bool(v.get('from_dock')) for v in m.get('control_routes',{}).values())
            circuit_scope['static_controls']=m.get('coverage',{}).get('completed_static_parts',0)
        for n,r in m.get('parts',{}).items():
            records[n]=r;models[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
    return models,records,inputs,content_inputs,circuit_scope

def build():
    parts={};owners={};roots={};pilots={};stations={};contacts=[];clearances={}
    def add(name,q,owner,root=None):
        parts[name]=q;owners[name]=owner
        if root:roots[name]=root
    p=(-100.325,310,281.5);q=split_seat(p,normal=(-1,0,0),screw_side=-1,key_thickness=3.25,
        screw_axial_stations=[8.5,19.5])
    # The lower flavor is captured by a broad upper U. Its two3mm side
    # bearings continue2.5mm below the tube axis; the4.384mm lower mouth
    # captures the6.35mm tube while staying2.1mm above the entire pan rim.
    # The shared key releases it laterally. The upper tube is threaded with
    # its end free; that split has a measured6.293mm lateral mouth.
    a=box(-106.65,305.25,268.5,-94.,314.75,281.5)
    for z in [271.,281.5]:
        a=a.cut(cq.Solid.makeCylinder(3.325,11.5,cq.Vector(-100.325,304.25,z),cq.Vector(0,1,0)))
    fixed_a=a.intersect(box(-107.5,304,268.5,-100.325,316,282))
    key_a=a.intersect(box(-100.325,304,268.5,-93.,316,282))
    fixed=q['fixed'].fuse(fixed_a).clean()
    key=q['key'].fuse(key_a).cut(fixed,tol=.0001).clean()
    add('flavor-pair-wall-seat',fixed,['tube-fluid-18','tube-fluid-28'],'enclosure-back-top')
    add('flavor-pair-wall-key',key,['tube-fluid-18','tube-fluid-28'])
    key_air=key
    for hole in q['key_holes']:key_air=key_air.fuse(hole)
    clearances['flavor-pair-wall-key-entry']={'shape':key_air,'print_owner':'enclosure-back-top',
        'target_host':'flavor-pair-wall-seat','scope':'Complete removable key and3.2mm screw entry holes clear the joined parent stock on the key side. Blind4mm pilots and their3mm closed covers remain fixed print stock.'}
    contacts.append(['flavor-pair-wall-key','flavor-pair-wall-seat'])
    for i,(s,t)in enumerate(zip(q['screws'],q['pilots']),1):
        add('flavor-pair-wall-screw-'+str(i),s,'flavor-pair-wall-key')
        contacts.extend([['flavor-pair-wall-screw-'+str(i),'flavor-pair-wall-key'],['flavor-pair-wall-screw-'+str(i),'flavor-pair-wall-seat']])
        pilots['flavor-pair-wall-pilot-'+str(i)]={'shape':t,'print_owner':'enclosure-back-top','target_host':'flavor-pair-wall-seat'}
    for flavor,z in [('a',271.),('b',281.5)]:
        stations['flavor-'+flavor]={**q['properties'],'tube':'tube-fluid-'+('18'if flavor=='a'else'28'),'centre_mm':[-100.325,310,z],
            'part_prefix':'flavor-pair-wall','fixed_part':'flavor-pair-wall-seat','key_part':'flavor-pair-wall-key',
            'screw_datum_centre_mm':list(p),'fastener_station':'flavor-pair-wall',
            'screw_parts':['flavor-pair-wall-screw-1','flavor-pair-wall-screw-2'],'print_owner':'enclosure-back-top',
            'pilot_cutters':['flavor-pair-wall-pilot-1','flavor-pair-wall-pilot-2'],
            'pan_rim_air_mm':2.1,'lower_capture_mouth_mm':4.38463,'rigid_lateral_release':flavor=='a','assembly':'UpperB tube end remains free for axial threading; shared3.25mm key is fitted after tube dressing.'}
    # The fixed broad lid supplies the lower bearing floor and closed pilot
    # cover. Its datum is unchanged; both keys thread on before final collets.
    p=(-33.9,201.5,259.75);q=split_seat(p,normal=(0,0,-1),axis=(1,0,0),screw_side=-1,key_thickness=3.25,screw_pitch=3.5)
    add('flavor-a-fore-seat',q['fixed'],'tube-fluid-18','cold-core/foam-cap-lid-top')
    add('flavor-a-fore-key',q['key'],'tube-fluid-18')
    contacts.append(['flavor-a-fore-key','flavor-a-fore-seat'])
    for i,(s,t)in enumerate(zip(q['screws'],q['pilots']),1):
        name='flavor-a-fore-screw-'+str(i);add(name,s,'flavor-a-fore-key')
        contacts.extend([[name,'flavor-a-fore-key'],[name,'flavor-a-fore-seat']])
        pilots['flavor-a-fore-pilot-'+str(i)]={'shape':t,'print_owner':'cold-core-lid','target_host':'flavor-a-fore-seat'}
    stations['flavor-a-fore']={**q['properties'],'tube':'tube-fluid-18','centre_mm':p,
        'part_prefix':'flavor-a-fore','fixed_part':'flavor-a-fore-seat','key_part':'flavor-a-fore-key',
        'screw_datum_centre_mm':list(p),'fastener_station':'flavor-a-fore',
        'screw_parts':['flavor-a-fore-screw-1','flavor-a-fore-screw-2'],'print_owner':'cold-core-lid',
        'pilot_cutters':['flavor-a-fore-pilot-1','flavor-a-fore-pilot-2']}
    p=(66.725,366,347)
    q=split_seat(p,normal=(0,0,1),axis=(0,1,0),screw_side=1,
                 key_thickness=3.25,screw_pitch=3.5,screw_radial_offset=5.)
    add('water2-tube-seat',q['fixed'],'tube-water-2','enclosure-back-top')
    add('water2-tube-key',q['key'],'tube-water-2')
    key_air=q['key']
    for hole in q['key_holes']:key_air=key_air.fuse(hole)
    clearances['water2-tube-key-entry']={'shape':key_air,'print_owner':'enclosure-back-top',
        'target_host':'water2-tube-seat','scope':'Complete removable key and3.2mm screw entry holes clear the joined roof below the blind-pilot mouths; every5.25mm pilot retains3mm closed print stock.'}
    contacts.append(['water2-tube-key','water2-tube-seat'])
    for i,(s,t)in enumerate(zip(q['screws'],q['pilots']),1):
        name='water2-tube-screw-'+str(i);add(name,s,'water2-tube-key')
        contacts.extend([[name,'water2-tube-key'],[name,'water2-tube-seat']])
        pilots['water2-tube-pilot-'+str(i)]={'shape':t,'print_owner':'enclosure-back-top','target_host':'water2-tube-seat'}
    stations['water2']={**q['properties'],'tube':'tube-water-2','centre_mm':list(p),
        'part_prefix':'water2-tube','fixed_part':'water2-tube-seat','key_part':'water2-tube-key',
        'screw_datum_centre_mm':list(p),'fastener_station':'water2-tube',
        'screw_parts':['water2-tube-screw-1','water2-tube-screw-2'],'print_owner':'enclosure-back-top',
        'pilot_cutters':['water2-tube-pilot-1','water2-tube-pilot-2'],
        'minimum_pilot_to_tube_bore_stock_mm':3.,'native_pcba_air_mm':.6,
        'scope':'Three-millimetre exact bore/pilot stock and.6mm native controller-edge air; actual printed tolerance/vibration clearance requires qualification.'}
    configs=[('supply',(-55.225,349.15,317.125),(0,1,0),(0,0,1),16.135,'tube-water-supply-link',-1),
             ('water3-east',(72.325,320.6,328.1),(0,0,1),(0,1,0),12.4,'tube-water-3',-1),
             ('water3-west',(-75.55,299,326),(0,0,1),(0,1,0),16.,'tube-water-3',0),
             ('needle-feed',(45,335,304),(1,0,0),(0,-1,0),10.,'tube-fluid-1',0),
             ('gate-a-upper',(57.5,282,295.4),(0,1,0),(0,0,1),7.61,'tube-fluid-14',0),
             ('gate-a-east',(88,348,268.325),(0,1,0),(0,0,-1),14.935,'tube-fluid-14',1),
             ('gas-inlet-east',(70,307,258),(1,0,0),(0,0,-1),4.61,'tube-co2-0',0),
             ('gas-inlet-west',(-35,275.325,261.5),(1,0,0),(0,0,-1),8.11,'tube-co2-0',0)]
    for name,p,u,n,d,tube,hs in configs:
        q=tied_seat(p,u,n,d,hs,6.35 if name=='supply'else 6.325);host=q['fixed']
        if name=='supply':
            live=json.loads((HERE/'candidate.json').read_text());route=live['parts'][tube]['route']
            from curves import swept
            path=cq.Shape.importBrep(str(ROOT/route['centreline_brep']));host=host.cut(swept(path.Edges(),path.Edges()[0].tangentAt(0),6.65)).clean()
        if name=='water3-east':
            host=host.fuse(box(60,330,323.35,78.65,333,332.85)).fuse(box(60,330,329.85,63,333,355))
        elif name=='water3-west':
            host=host.fuse(box(-81.875,312,327.75,-69.225,315,335.3)).fuse(box(-99.5,312,332.3,-69.225,315,335.3)).fuse(box(-99.5,312,332.3,-96.5,315,355))
        elif name=='needle-feed':
            host=host.fuse(box(24,322,297.675,49.75,325,310.325)).fuse(box(24,322,297.675,33.5,330,300.675)).fuse(box(24,327,253.39,33.5,330,300.675))
        elif name=='gate-a-upper':
            host=host.fuse(box(51.175,277.25,300.925,63.825,286.75,321.))
        owner=('funnel-frame'if name=='gate-a-upper'else'cold-core/foam-cap-lid-top'if name in['needle-feed','gate-a-east','gas-inlet-east','gas-inlet-west']else'enclosure-back-top')
        add(name+'-tube-seat',host.clean(),tube,owner)
        add(name+'-tube-tie',q['tie'],tube)
        contacts.append([name+'-tube-tie',tube])
        contacts.append([name+'-tube-seat',name+'-tube-tie'])
        if name=='supply':contacts.append([name+'-tube-seat','west-junction-platform'])
        stations[name]={'tube':tube,'centre_mm':p,'bearing_section_mm':9.5,'bore_radius_mm':3.325,'ordinary_stock_mm':3.,'tunnel_width_mm':3.5,'tie_width_mm':2.5,'tie_thickness_mm':1.,
            'part_prefix':name+'-tube','fixed_part':name+'-tube-seat','retainer_part':name+'-tube-tie',
            'print_owner':'funnel-frame'if owner=='funnel-frame'else'cold-core-lid'if owner=='cold-core/foam-cap-lid-top'else'enclosure-back-top'}
        if name=='needle-feed':
            stations[name].update({'root_footprint_mm':[24.,327.,253.39,33.5,330.,300.675],
                'load_path':'Nine-and-a-half-mm-wide by3mm fore pillar joins the cold-core lid, then a3mm rail and full bearing crossweb carry the unchanged tube seat. No part of this guide follows the roof during factory travel.',
                'factory_fixed_part':name+'-tube-seat','factory_deferred_retainer':name+'-tube-tie'})
        if name=='gate-a-upper':pilots['gate-a-upper-tie-tunnel']={'shape':q['tunnel'],'print_owner':'funnel-frame','target_host':name+'-tube-seat'}
    gas=json.loads((HERE/'co2-candidate.json').read_text())
    run=gas['parts']['tube-co2-1']['route'];w=cq.Shape.importBrep(str(ROOT/run['centreline_brep']))
    p=cq.Vector(68.2,445,284.);u=cq.Vector(0,0,-1);n=cq.Vector(0,1,0)
    q=tied_seat(p.toTuple(),u.toTuple(),n.toTuple(),6.325,-1,7.325,.15)
    from curves import swept
    exact_bore=swept(w.Edges(),w.Edges()[0].tangentAt(0),6.65)
    seat=q['fixed'].cut(exact_bore).fuse(box(64,449.5,253.39,74,452.5,288.75)).clean()
    # Both the exact post and its floor web share the lid print; the new
    # saddle joins that rooted stock and carries the same small gas load.
    contacts.extend([['gas-outlet-tube-seat','supply-lid-boss-4'],['gas-outlet-tube-seat','supply-lid-web-2']])
    # Preserve the complete dressed head/strap pocket in the fused root.
    seat=seat.cut(q['tunnel']).clean()
    tie_clearance=q['tie'].translate((0,.15,0)).fuse(q['tie'].translate((0,-.15,0)))
    seat=seat.cut(tie_clearance).clean()
    inlet_tool=cq.Shape.importBrep(str(ROOT/gas['clearance_cutters']['tube-co2-0']['brep']))
    seat=seat.cut(inlet_tool).clean()
    pilots['gas-outlet-inlet-air']={'shape':inlet_tool,'print_owner':'cold-core-lid','target_host':'gas-outlet-tube-seat','radial_air_mm':1.,'scope':'Exact frozen gas0 air tool removes the outer corner of the10mm-wide lid foot while retaining its complete3mm fore/aft bearing stock.'}
    add('gas-outlet-tube-seat',seat,'tube-co2-1','cold-core/foam-cap-lid-top')
    add('gas-outlet-tube-tie',q['tie'],'tube-co2-1')
    contacts.append(['gas-outlet-tube-tie','tube-co2-1'])
    contacts.append(['gas-outlet-tube-seat','gas-outlet-tube-tie'])
    stations['gas-outlet']={'tube':'tube-co2-1','centre_mm':list(p.toTuple()),'axis':list(u.toTuple()),'root_direction':list(n.toTuple()),'bearing_section_mm':9.5,'bore_radius_mm':3.325,'outer_radius_mm':7.325,'ordinary_stock_mm':3.,'tie_bore_slip_mm':.15,
        'part_prefix':'gas-outlet-tube','fixed_part':'gas-outlet-tube-seat','retainer_part':'gas-outlet-tube-tie','print_owner':'cold-core-lid',
        'scope':'TrueR14 elbow clearance cuts the9.5mm tangent bearing;7.325mm outer envelope retains at least3mm around the curved bore. Full tie follows the actual straight local tangent. Printed upperface288.75 leaves1mm native supply-base air; local thermal retention remains a qualification limit.'}
    return parts,owners,roots,pilots,stations,contacts,clearances

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--received','--check-only',action='store_true',
        help='Prove the in-memory selected recipe against every saved part/cutter, without writing native geometry.')
    args=parser.parse_args()
    old=json.loads((HERE/'tube-hosts.json').read_bytes())if args.received else None
    sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
             for f in [Path(__file__),HERE/'split_seat.py',HERE/'received_native.py',
                       STUDY/'structure/assemble_prints_verified.py',HERE/'fluid_members.py',
                       STUDY/'wiring/circular_clearance.py',STUDY/'evidence_binding.py',STUDY/'audit.py']}
    models,records,inputs,content_inputs,circuit_scope=load()
    native_inputs={}
    for n in models:
        r=records[n]
        raw=(ROOT/r['brep']).read_bytes();models[n]=cq.Shape.importBrep(BytesIO(raw))
        native_inputs[n]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
    parts,owners,roots,pilots,stations,contacts,clearances=build()
    # Own previous outputs are never obstacles or inputs of their successor.
    for n in set(parts)|set(pilots)|set(clearances):models.pop(n,None);records.pop(n,None);native_inputs.pop(n,None)
    ignore={'enclosure-front-top','enclosure-back-top','rear-roof-hatch'}|set(parts)
    rows=[];serialized={}
    if args.received:
        if set(parts)!=set(old['parts'])or set(pilots)!=set(old.get('pilot_cutters',{}))or set(clearances)!=set(old.get('clearance_cutters',{})):
            raise ValueError('Selected part/pilot/clearance names differ from the saved guide recipe')
        for name,expected in list(parts.items()):
            received=receive(ROOT,old['parts'][name],'received-guide/'+name,native_inputs)
            rows.append(material_equivalence(received,expected,name));parts[name]=received
    else:OUT.mkdir(parents=True,exist_ok=True)
    for name,q in parts.items():
        hits=[];near=[]
        for n,b in models.items():
            own=owners[name]if isinstance(owners[name],list)else[owners[name]]
            if n in ignore or n in own or n==roots.get(name)or frozenset([name,n])in[frozenset(p)for p in contacts]:continue
            if not audit.broad(audit.bbox(q),audit.bbox(b),1):continue
            d=q.distance(b)
            if d>=.999999:continue
            v=audit.common(q,b)if d<1e-6 else 0.
            row={'part':n,'gap_mm':d,'common_mm3':v};near.append(row)
            if v>.001 or d<.15-1e-5:hits.append(row)
        for other,b in parts.items():
            if other<=name or[frozenset([name,other])in [frozenset(p)for p in contacts]][0]:continue
            if not audit.broad(audit.bbox(q),audit.bbox(b),.15):continue
            d=q.distance(b);v=audit.common(q,b)if d<1e-6 else 0.
            if v>.001 or d<.15-1e-5:hits.append({'part':other,'gap_mm':d,'common_mm3':v})
        if args.received:serialized[name]=old['parts'][name]
        else:
            f=OUT/(name+'.brep');q.exportBrep(str(f))
            serialized[name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bounds':audit.bbox(q),'role':'structure','detail':'Complete nominal tube bearing/retainer; named print root and9.5mm section, ordinary3mm stock and exact occupied fastener/tie envelope.'}
        rows.append({'part':name,'valid_one_solid':q.isValid()and len(q.Solids())==1,'interferences':hits,'close_pairs':near,'pass':q.isValid()and len(q.Solids())==1 and not hits})
        print(name,rows[-1],flush=True)
        ownerlist=owners[name]if isinstance(owners[name],list)else[owners[name]]
        for tube in ownerlist:
            if not tube.startswith('tube-')or tube not in models:continue
            v=audit.common(q,models[tube]);d=q.distance(models[tube])
            rows.append({'check':'controlled bearing/tie fits its actual curved tube','part':name,'tube':tube,'common_mm3':v,'air_mm':d,'pass':v<.001})
    lid_parent=models['cold-core/foam-cap-lid-top'];lid_host=parts['needle-feed-tube-seat']
    lid_contact=audit.common(lid_parent,lid_host,exact_root_fallback=True)
    lid_joined=lid_parent.fuse(lid_host,tol=.0001)
    rows.append({'check':'needle feed guide has a complete fixed lid load path',
        'part':'needle-feed-tube-seat','print_owner':'cold-core-lid',
        'root_contact_mm3':lid_contact,'joined_valid':lid_joined.isValid(),
        'joined_solids':len(lid_joined.Solids()),'pillar_section_mm':[9.5,3.],
        'minimum_rail_stock_mm':3.,'seat_centre_mm':[45.,335.,304.],
        'pass':lid_contact>.001 and lid_joined.isValid()and len(lid_joined.Solids())==1})
    key_common=audit.common(parts['flavor-pair-wall-seat'],parts['flavor-pair-wall-key'])
    rows.append({'check':'shared flavor key partitions both bearings without common stock',
        'common_mm3':key_common,'fixed_valid_one_solid':parts['flavor-pair-wall-seat'].isValid()and len(parts['flavor-pair-wall-seat'].Solids())==1,
        'key_valid_one_solid':parts['flavor-pair-wall-key'].isValid()and len(parts['flavor-pair-wall-key'].Solids())==1,
        'screw_axial_stations_mm':[8.5,19.5],'bridge_stock_mm':3.,'pass':key_common<.001})
    frame_part='gate-a-upper-tube-seat';parent=models['funnel-frame'];host=parts[frame_part]
    joint=audit.common(host,parent,exact_root_fallback=True)
    joined=parent.fuse(host,tol=.0001).cut(pilots['gate-a-upper-tie-tunnel']['shape'],tol=.0001)
    # Imported shared spline edges can be mutated by the optional cleaner.
    # Keep and validate the native Boolean article without that simplifier.
    other=models['funnel'];silhouette=audit.bbox(joined)
    inherited=audit.bbox(parent);added=audit.bbox(host)
    # The under-frame guide deliberately extends4.5mm below the old underside.
    # Width, fore/aft footprint and upper brim silhouette stay inside the parent.
    unchanged_silhouette=all(silhouette[i]>=inherited[i]-1e-5 for i in [0,1])and all(silhouette[i]<=inherited[i]+1e-5 for i in range(3,6))
    rows.append({'check':'complete frame root and forming silicone remain valid','part':frame_part,
                 'root_common_mm3':joint,'joined_valid':joined.isValid(),'joined_solids':len(joined.Solids()),
                 'silicone_common_mm3':audit.common(joined,other),'silicone_air_mm':joined.distance(other),
                 'added_guide_silicone_air_mm':host.distance(other),'added_guide_silicone_common_mm3':audit.common(host,other),
                 'joined_silhouette_mm':silhouette,'rail_protection_z_mm':306.9,
                 'inherited_frame_bounds_mm':inherited,'added_guide_bounds_mm':added,
                 'frame_width_fore_aft_upper_silhouette_preserved':unchanged_silhouette,
                 'guide_tunnel_max_z_mm':audit.bbox(pilots['gate-a-upper-tie-tunnel']['shape'])[5],
                 'pass':joint>.001 and joined.isValid()and len(joined.Solids())==1 and audit.common(joined,other)<.001 and host.distance(other)>=3 and unchanged_silhouette and added[0]>=-107.5-1e-6 and added[3]<=107.5+1e-6 and added[2]>=253.4-1e-6 and added[5]<=355+1e-6})
    # Supports are evaluated along the actual developed centreline, including
    # the two fitting endpoints. Every guide datum lies on a serialized straight.
    live=json.loads((HERE/'candidate.json').read_text());spans={}
    for cid,run in live['routes'].items():
        rec=live['parts']['tube-'+cid]['route'];positions=[]
        for station,spec in stations.items():
            if spec['tube']!='tube-'+cid:continue
            p=cq.Vector(*spec['centre_mm']);best=None
            for seg in rec['straight_segments']:
                a=cq.Vector(*seg['start']);b=cq.Vector(*seg['end']);v=b-a
                t=max(0.,min(1.,(p-a).dot(v)/v.dot(v)));d=(p-(a+v*t)).Length
                candidate=(d,seg['start_developed_mm']+t*seg['length_mm'])
                if best is None or candidate[0]<best[0]:best=candidate
            if best is None or best[0]>1e-5:raise ValueError(station+' is not on its exact straight tube')
            positions.append({'station':station,'developed_mm':best[1],'position_error_mm':best[0]})
        positions.sort(key=lambda p:p['developed_mm']);d=[0.]+[p['developed_mm']for p in positions]+[rec['length_mm']]
        free=[b-a for a,b in zip(d,d[1:])]
        spans[cid]={'developed_length_mm':rec['length_mm'],'support_stations':positions,'unsupported_spans_mm':free,
                    'maximum_unsupported_mm':max(free),'limit_mm':200.,'pass':max(free)<=200.+1e-5}
        rows.append({'check':'developed free tube support span','route':cid,**spans[cid]})
    drift=['native:'+n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    drift+=['source:'+p for p,h in sources.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    circuit_complete=circuit_scope.get('power_routes')==19 and circuit_scope.get('grouped_controls')==26 and circuit_scope.get('static_controls')==49
    report={'parts':serialized,'checks':rows,'pass':all(r['pass']for r in rows)and not drift and circuit_complete,'retained_components':owners,
            'current_circuit_scope':circuit_scope,'complete_circuit_scope_pass':circuit_complete,
            'shell_fuse_part_names':[n for n,p in roots.items()if p=='enclosure-back-top'],
            'lid_fuse_part_names':[n for n,p in roots.items()if p=='cold-core/foam-cap-lid-top'],
            'frame_fuse_part_names':[n for n,p in roots.items()if p=='funnel-frame'],
            'front_carried_part_names':[n for n,p in roots.items()if p=='funnel-frame'],
            'factory_carried_part_names':[n for n,p in roots.items()if p=='enclosure-back-top'],
            'root_owner_overrides':{n:p for n,p in roots.items()if p!='cold-core/foam-cap-lid-top'},
            'named_print_roots':{n:('cold-core-lid'if p=='cold-core/foam-cap-lid-top'else p)for n,p in roots.items()},
            'intended_contacts':contacts,
            'stations':stations,'support_spans':spans,'manifests_sha256':inputs,'manifest_content_sha256':content_inputs,'native_inputs':native_inputs,'source_inputs':sources,'source_drift':drift,
            'factory_deferred_part_names':[n for n in parts if n.endswith(('-tie','-key'))or'-screw-'in n],
            'standalone_print_parts':{n:{**serialized[n],'rotation_x_deg':0,
                'detail':'Separate3.25mm removable tube key; complete native article, bores and socket-head working face.'}
                for n in parts if n.endswith('-key')},
            'factory_handling':[
                'Fixed guide stock follows its named roof, lid or front-frame print. Leave every tube with endpoints on different assembly owners free during shell travel; final installed curves are seated occupancy only.',
                'Thread FlavorB, the fore FlavorA key and the water2 key while the tube end is free; their6.293mm split mouths do not claim rigid lateral release of a6.35mm tube. The lower FlavorA U releases with the shared removable key.',
                'Fit all3.25mm keys andM3x8 screws after final tube dressing. Complete ties and their dressed locking heads are separate deferred parts. The frame-carried GateA guide is fixed during front travel; its final tie is dressed after seating.'],
            'scope':'Native occupied geometry and bearing stock. Carrying/free-port dressing and final joined-print closure proof are separate; load, creep, vibration and retention require physical qualification.'}
    for n,r in pilots.items():
        if args.received:
            received=receive(ROOT,old['pilot_cutters'][n],'received-guide-pilot/'+n,native_inputs)
            rows.append(material_equivalence(received,r['shape'],n));report.setdefault('pilot_cutters',{})[n]=old['pilot_cutters'][n]
        else:
            f=OUT/(n+'.brep');r['shape'].exportBrep(str(f));r={k:v for k,v in r.items()if k!='shape'};r.update({'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});report.setdefault('pilot_cutters',{})[n]=r
    for n,r in clearances.items():
        if args.received:
            received=receive(ROOT,old['clearance_cutters'][n],'received-guide-clearance/'+n,native_inputs)
            rows.append(material_equivalence(received,r['shape'],n));report.setdefault('clearance_cutters',{})[n]=old['clearance_cutters'][n]
        else:
            f=OUT/(n+'.brep');r['shape'].exportBrep(str(f));r={k:v for k,v in r.items()if k!='shape'};r.update({'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});report.setdefault('clearance_cutters',{})[n]=r
    # Received output proofs are completed before the final drift snapshot.
    drift=['native:'+n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    drift+=['source:'+p for p,h in sources.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    report['source_drift']=drift
    if args.received:
        before=evidence_binding.content_sha256(old);recipe=evidence_binding.content_sha256(report)
        rows.append({'check':'received guide recipe preserves every selected substantive record',
            'received_content_sha256':before,'recipe_content_sha256':recipe,'pass':before==recipe})
        # All selected fields remain exactly as received, even if the fresh
        # recipe/parity check fails. Only its proof receipt is republished.
        report={**old,**{key:report[key]for key in ['checks','manifests_sha256','manifest_content_sha256',
                    'native_inputs','source_inputs','source_drift']}}
    report['pass']=all(r['pass']for r in rows)and not drift and circuit_complete
    report_path=HERE/('tube-hosts.json' if args.received or report['pass'] else 'tube-hosts-probe.json')
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    if report['pass']and not args.received:(HERE/'tube-hosts-probe.json').unlink(missing_ok=True)
    if args.received:print('received content parity',before,evidence_binding.content_sha256(report),flush=True)
    print(json.dumps({'pass':report['pass'],'parts':len(parts),'blockers':sum(len(r.get('interferences',[]))for r in rows),'source_drift':drift},indent=2),flush=True)

if __name__=='__main__':main()
