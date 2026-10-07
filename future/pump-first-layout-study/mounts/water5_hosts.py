"""A front-carried discharge-tube saddle with a continuous closing chase.

The front seat travels under the installed water5 cross tube. Its aft mouth
stays open throughout the102.2mm rail entry; the complete tie is dressed after seating.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/water5'
sys.path[:0]=[str(STUDY),str(STUDY/'routing')];import audit
from split_seat import split_seat
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources,received_native

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true',help='Verify held native articles against the analytic recipe and refresh evidence without exporting.')
    args=parser.parse_args()
    sources=proof_sources.snapshot(__file__,sys.modules[split_seat.__module__].__file__,received_native.__file__)
    received=received_native.ReceivedNative(ROOT,json.loads((HERE/'water5-hosts.json').read_text()))if args.check else None
    models,records,changed,mates,inputs=audit.collect()
    for fname in ['controls-candidate.json','control-reserves.json','control-fanouts-check.json','lower-lead-exits.json']:
        path=STUDY/'wiring'/fname
        if path.exists():
            raw=path.read_bytes();packet=json.loads(raw);records.update(packet.get('parts',{}))
            inputs[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
            inputs.content_sha256[str(path.relative_to(ROOT))]=content_sha256(packet)
            for n,r in packet.get('parts',{}).items():models[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
    x,y,z=82.,195.5,285.8;length=9.5;reach=7.525
    bore=cq.Solid.makeCylinder(3.425,length,cq.Vector(x-length/2,y,z),cq.Vector(1,0,0))
    seat=box(x-length/2,x+length/2,y-reach,y+reach,z-reach,z).cut(bore)
    # The full3mm bridge clears the normal valve terminal wire by1mm and
    # remains0.175mm below the tube. This bearing's aft mouth uses0.15mm
    # slip; the enclosing front-shell chase retains its separate1mm air.
    seat=seat.fuse(box(x-1.5,104.5,201.,204.,279.45,282.45))
    tie=cq.Solid.makeCylinder(4.175,2.5,cq.Vector(x-1.25,y,z),cq.Vector(1,0,0)).cut(
        cq.Solid.makeCylinder(3.175,2.5,cq.Vector(x-1.25,y,z),cq.Vector(1,0,0)))
    tie=tie.fuse(box(x-4,x+4,y+3.1,y+11.1,z+.8,z+5.8)).clean()
    tunnel=cq.Solid.makeCylinder(4.525,3.5,cq.Vector(x-1.75,y,z),cq.Vector(1,0,0))
    seat=seat.cut(tunnel)
    chase=box(x-length/2-.01,x+length/2+.01,y,y+102.2+3.325,z-3.325,z+3.325)
    seat=seat.cut(chase).clean()
    shapes={'water5-front-seat':seat,'water5-front-retention-tie':tie}
    # A25degree aft clock puts the lower screw ears into the wall while
    # retaining a6.3546mm open mouth for the6.35mm tube after key removal.
    angle=math.radians(25)
    clamp=split_seat((100.325,304.6,317),normal=(math.cos(angle),math.sin(angle),0),axis=(0,0,1),
                     split=-.98,root=7.27,screw_side=-1,key_thickness=3.25)
    shapes['water5-east-drop-seat']=clamp['fixed'];shapes['water5-east-drop-key']=clamp['key']
    for i,q in enumerate(clamp['screws'],1):shapes[f'water5-east-drop-screw-{i}']=q
    if received:
        shapes={n:received.shape(n,s)for n,s in shapes.items()}
        seat=shapes['water5-front-seat'];tie=shapes['water5-front-retention-tie']
        clamp['fixed']=shapes['water5-east-drop-seat'];clamp['key']=shapes['water5-east-drop-key']
    native={n:{'brep':r['brep'],'sha256':hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()}for n,r in records.items()if n in models and n not in shapes}
    parts={};checks=[];OUT.mkdir(parents=True,exist_ok=True)
    ignored={'enclosure-front-top','enclosure-back-top','rear-roof-hatch'}|set(shapes)
    for name,shape in shapes.items():
        hits=[]
        for other,body in models.items():
            if other in ignored or other=='tube-water-5':continue
            if not audit.broad(audit.bbox(shape),audit.bbox(body),0):continue
            v=audit.common(shape,body)
            if v>.001:hits.append({'part':other,'common_mm3':v})
        own=audit.common(shape,models['tube-water-5'])
        if own>.001:hits.append({'part':'tube-water-5','common_mm3':own})
        path=OUT/(name+'.brep')
        if not received:shape.exportBrep(str(path))
        parts[name]=(received.record(name,shape)if received else{'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'bounds':audit.bbox(shape),'role':'structure',
                     'detail':('Front-shell-carried9.5mm discharge cross-tube saddle: R3.425 slip,3mm end webs and tie-channel cover,3mm below-tube wall bridge; aft-open0.15mm slip chase throughout102.2mm closing travel.' if name=='water5-front-seat'else
                               'Complete2.5×1mm tie with conservative8×8×5mm locking head, threaded after the front shell is seated.' if name=='water5-front-retention-tie' else
                               'Exact M3×8 key fastener with4.75mm engagement and0.5mm pilot tip reserve.' if 'screw' in name else
                               '9.5mm discharge-drop split bearing/key: R3.325 slip and3mm radial stock,25degree aft mounting clock,5.25mm blind insert pilot and3mm closed cover.')})
        checks.append({'part':name,'single_valid_solid':shape.isValid()and len(shape.Solids())==1,'hits':hits,'pass':shape.isValid()and len(shape.Solids())==1 and not hits})
    overlap=audit.common(seat,tie)
    checks.append({'test':'complete dressed tie clears real tunnel','common_mm3':overlap,'pass':overlap<.001})
    gap=seat.distance(models['enclosure-front-top']);root=audit.common(seat,models['enclosure-front-top'])
    checks.append({'test':'bridge reaches native front shell','gap_mm':gap,'common_mm3':root,'pass':gap<1e-6})
    drop_root=clamp['fixed'].distance(models['enclosure-back-top'])
    checks.append({'test':'drop bearing reaches native back east wall','gap_mm':drop_root,'pass':drop_root<1e-6})
    for left,right in [('water5-east-drop-seat','water5-east-drop-key')]:
        v=audit.common(shapes[left],shapes[right]);checks.append({'test':'split bearing and key clear','common_mm3':v,'pass':v<.001})
    poses=[]
    for travel in [102.2,90,70,40,20,10,5,2,1,.5,.25,0]:
        moved=seat.translate((0,-travel,0));v=audit.common(moved,models['tube-water-5'])
        poses.append({'travel_mm':travel,'common_mm3':v,'pass':v<.001})
    checks.append({'test':'bare front saddle closes around installed tube','poses':poses,'pass':all(p['pass']for p in poses)})
    # Complete30mm straight2.5AF Allen approach, including12mm entry travel.
    # The front/funnel assembly remains off while these two screws are made up.
    # A2mm socket engagement is explicit; the representative screw has no
    # modeled socket, so only that screw's engagement is an intended contact.
    n=cq.Vector(math.cos(angle),math.sin(angle),0);u=cq.Vector(0,0,1);v=n.cross(u)
    tooling=[];absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover'}|set(shapes)
    for i,side in enumerate([-1,1],1):
        p=cq.Vector(100.325,304.6,317)+n*(-7.23)+u*(side*8.5)+v*(-8.825)
        tool=cq.Solid.makeCylinder(2.5/math.sqrt(3),32,p+n*2,-n)
        for travel in [12,8,4,0]:
            q=tool.translate((-n*travel).toTuple());hits=[]
            for other,body in {**models,**shapes}.items():
                if other in absent and other not in shapes:continue
                if other==f'water5-east-drop-screw-{i}':continue
                if not audit.broad(audit.bbox(q),audit.bbox(body),0):continue
                volume=audit.common(q,body)
                if volume>.001:hits.append({'part':other,'common_mm3':volume})
            tooling.append({'screw':i,'entry_travel_mm':travel,'hits':hits,'pass':not hits})
    checks.append({'test':'both drop-key screws have full Allen approach through open front','poses':tooling,'pass':all(p['pass']for p in tooling)})
    pilots={}
    for i,q in enumerate(clamp['pilots'],1):
        name=f'water5-east-drop-pilot-{i}';path=OUT/(name+'.brep')
        if not received:q.exportBrep(str(path))
        pilots[name]=(received.record(name,q)if received else{'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'print_owner':'enclosure-back-top','target_host':'water5-east-drop-seat'})
    if received:
        checks.extend(received.checks);native.update(received.inputs)
    properties=dict(clamp['properties'])
    if received and 'screw_axial_stations_mm'not in received.manifest['split_seat_properties']:
        held_properties=received.manifest['split_seat_properties']
        half_pitch=held_properties['screw_half_pitch_mm']
        stations=properties.pop('screw_axial_stations_mm')
        expected=[-half_pitch,half_pitch]
        equivalent=len(stations)==2 and all(abs(a-b)<1e-6 for a,b in zip(stations,expected))
        checks.append({'check':'explicit screw stations equal held symmetric half-pitch',
                       'generated_stations_mm':stations,'held_stations_mm':expected,'pass':equivalent})
        if not equivalent or properties!=held_properties:
            raise ValueError('Received water5 split-seat properties differ from the held recipe')
        properties=dict(held_properties)
    drift=[n for n,r in native.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]+proof_sources.changed(sources)
    manifest_drift=[p for p,h in inputs.content_sha256.items()if manifest_content_sha256(ROOT/p)!=h]
    contacts=[['water5-front-retention-tie','tube-water-5']]
    for i in [1,2]:
        for owner in ['water5-east-drop-seat','water5-east-drop-key','enclosure-back-top']:
            contacts.append([f'water5-east-drop-screw-{i}',owner])
    report={'parts':parts,'checks':checks,'pass':not drift and not manifest_drift and all(c['pass']for c in checks),
            'front_shell_fuse_part_names':['water5-front-seat'],
            'shell_fuse_part_names':['water5-east-drop-seat'],
            'factory_deferred_part_names':['water5-front-retention-tie','water5-east-drop-key','water5-east-drop-screw-1','water5-east-drop-screw-2'],
            'standalone_print_parts':{'water5-east-drop-key':{'source_part':'water5-east-drop-key','rotation_x_deg':0}},
            'pilot_cutters':pilots,'split_seat_properties':properties,
            'tool_approach':{'hex_across_flats_mm':2.5,'straight_reach_mm':30,'socket_engagement_mm':2,
                             'entry_travel_mm':12,'absent_names':['enclosure-front-top','funnel','funnel-frame','funnel-cover']},
            'intended_contacts':contacts,
            'native_inputs':native,'manifests_sha256':inputs,'source_drift':drift,
            'manifest_content_sha256':inputs.content_sha256,'manifest_drift':manifest_drift,'source_inputs':sources,
            'scope':'Complete nominal front restraint and below-tube rooted stock. Physical tie dressing, load, creep and vibration remain unqualified.'}
    if received:
        before=content_sha256(received.manifest);after=content_sha256(report)
        unchanged=before==after
        report['checks'].append({'check':'received refresh preserves complete semantic manifest content',
                                'before_content_sha256':before,'after_content_sha256':after,'pass':unchanged})
        if not unchanged:raise ValueError('Received water5-host refresh changes substantive manifest fields')
    (HERE/'water5-hosts.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':checks},indent=2),flush=True)
    if not report['pass']:raise SystemExit(1)

if __name__=='__main__':main()
