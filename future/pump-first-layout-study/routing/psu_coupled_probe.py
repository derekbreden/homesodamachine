"""Read-only +45 funnel / fore-shifted rigid-package spacing hypothesis.

Selected manifests, parts, tubes and conductors are never written. Boundary
tubing, wiring, joined stock, assembly motion and print proofs do not transfer
to this hypothesis. The probe identifies concrete rigid placement limits.
"""
from pathlib import Path
from io import BytesIO
import hashlib,importlib.util,itertools,json,math,re,sys,time
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3];STUDY=ROOT/'future/pump-first-layout-study';HERE=STUDY/'routing'
OUT=ROOT/'.cache/pump-first-layout/routing/psu-coupled-probe'
sys.path[:0]=[str(STUDY),str(HERE)]
import audit,evidence_binding

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def preview_funnel():
    sys.path.insert(0,str(STUDY/'funnel'))
    spec=importlib.util.spec_from_file_location('coupled_funnel_builder',STUDY/'funnel/build_candidate.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    f=module.f;ff=module.ff;extra=45.;cy=ff.center_y+extra/2
    f.collar_d+=extra;f.neck_dy=-extra/2;ff.center_y=cy;ff.depth=f.collar_d+24.6
    ff.corbel_foot_half_depth+=extra/2;f.build_solids=module.layout_funnel.build_solids
    ff.forming_clearance.cache_clear();ff.build.cache_clear()
    outer,cavity,meta=f.build_solids()
    silicone=outer.cut(cavity,tol=.0001).clean().translate((0,cy,349))
    capacity=cavity.intersect(f._box(1000,1000,meta['end_z'],meta['top_z'],0,0),tol=.0001).Volume(tol=1e-9)/1000
    frame=ff.build((-104.5,104.5,14,468.3,0,352),200,(0,cy),349)
    import funnel_cover as cover
    result={'funnel':silicone,'funnel-frame':frame,'funnel-cover':cover.placed(0,cy,355)}
    inputs=[Path(module.__file__),Path(module.layout_funnel.__file__),Path(f.__file__),Path(ff.__file__),Path(cover.__file__)]
    return result,capacity,inputs

def main():
    started=time.time();OUT.mkdir(parents=True,exist_ok=True)
    sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    loaded,records,changed,mates,inputs=audit.collect();content=dict(inputs.content_sha256)
    roots={};retained={};extra_manifests=['routing/co2-candidate.json','mounts/needle-candidate.json','mounts/wr-candidate.json','mounts/check-tee-candidate.json','mounts/fluid-candidate.json','mounts/body-candidate.json','mounts/water5-hosts.json','routing/tube-hosts.json']
    for relative in ['pump/candidate.json','routing/candidate.json','structure/candidate.json','mounts/candidate.json',*extra_manifests]:
        path=STUDY/relative;raw=path.read_bytes();m=json.loads(raw);content[str(path.relative_to(ROOT))]=evidence_binding.content_sha256(m)
        for n,r in m.get('parts',{}).items():records[n]=r;changed.add(n)
        for pair in m.get('intended_contacts',[]):mates[frozenset(pair)]='declared mating contact'
        owners=m.get('retained_components',{})
        if isinstance(owners,dict):retained.update(owners)
        for key,parent in [('shell_fuse_part_names','enclosure-back-top'),('lid_fuse_part_names','cold-core/foam-cap-lid-top'),('frame_fuse_part_names','funnel-frame')]:
            for n in m.get(key,[]):roots[n]=parent
        roots.update(m.get('root_owner_overrides',{}))
        if relative=='routing/candidate.json':
            for field,move in m.get('interface_moves',{}).items():
                for k in ['new_receiver','new_backing']:
                    if k in move:records[field+'-'+k]=move[k]
    for i in range(1,5):roots['controller-roof-boss-'+str(i)]='enclosure-back-top';roots['supply-lid-boss-'+str(i)]='cold-core/foam-cap-lid-top'
    roots.update({'ground-roof-boss':'enclosure-back-top','vk-cradle':'cold-core/foam-cap-lid-top','source-a-cradle':'cold-core/foam-cap-lid-top','source-b-cradle':'cold-core/foam-cap-lid-top','suction-chain-anchor':'cold-core/foam-cap-lid-top','discharge-chain-anchor':'enclosure-back-top','supply-lid-web-1':'cold-core/foam-cap-lid-top','supply-lid-web-2':'cold-core/foam-cap-lid-top'})
    models={};native={}
    for n,r in records.items():
        if not r or n.startswith(('enclosure-','wire-','control-','power-','carb-foam-','hose-engagement-')) or r.get('role')=='wiring' or n=='rear-roof-hatch':continue
        if re.match(r'^tube-(?:fluid-\d+|water-\d+|water-supply-link|carb-\d+|co2-\d+|customer-)',n):continue
        raw=(ROOT/r['brep']).read_bytes();models[n]=cq.Shape.importBrep(BytesIO(raw))
        native[n]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
    # Preserve the complete current rear carbonated envelope as a fixed rear
    # interface assessment. Its fore end must be rerouted to the moved meter;
    # using its present occupied envelope here does not establish that reroute.
    sys.path.insert(0,str(STUDY/'wiring'))
    from fluid_members import sealed_sleeve_parity
    sleeve_inputs={}
    for n in ['tube-carb-2','carb-foam-carb-2']:
        rec=records[n];raw=(ROOT/rec['brep']).read_bytes()
        sleeve_inputs[n]=cq.Shape.importBrep(BytesIO(raw));native[n]={'brep':rec['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
    cp=ROOT/records['tube-carb-2']['route']['centreline_brep'];raw=cp.read_bytes()
    centreline=cq.Shape.importBrep(BytesIO(raw));native['fixed-carb2-centreline']={'brep':str(cp.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
    models['fixed-rear-carb2-occupied-envelope'],sleeve_proof=sealed_sleeve_parity(sleeve_inputs['tube-carb-2'],sleeve_inputs['carb-foam-carb-2'],centreline.Edges())
    sources.update({str(p.relative_to(ROOT)):sha(p) for p in [HERE/'fluid_members.py',STUDY/'wiring/circular_clearance.py',STUDY/'wiring/native_harness.py']})
    print('rigid input count',len(models),flush=True)
    preview,capacity,extra_sources=preview_funnel()
    sources.update({str(p.relative_to(ROOT)):sha(p) for p in extra_sources})
    # Preserve the fixed compact-valve underside pocket and fixed front lead
    # reliefs; their native tools are not translated with the aft group.
    frame=preview['funnel-frame'];cutters=[]
    for n in ['vk-solenoid','vk-cradle']:
        b=models[n].BoundingBox();cutters.append(cq.Solid.makeBox(b.xlen+2,b.ylen+104.2,b.zlen+2,cq.Vector(b.xmin-1,b.ymin-1,b.zmin-1)))
    routing=json.loads((HERE/'candidate.json').read_bytes())
    for path in [ROOT/routing['clearance_cutters']['tube-fluid-14']['brep'],ROOT/json.loads((STUDY/'wiring/frame-j13-relief.json').read_bytes())['clearance_cutter']['brep']]:
        raw=path.read_bytes();cutters.append(cq.Shape.importBrep(BytesIO(raw)));native['fixed-relief-'+path.stem]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
    for cutter in cutters:frame=frame.cut(cutter,tol=.0001)
    preview['funnel-frame']=frame
    preview_records={}
    for n,q in preview.items():
        path=OUT/(n+'-aft45.brep');q.exportBrep(str(path));preview_records[n]={'brep':str(path.relative_to(ROOT)),'sha256':sha(path),'bounds_mm':audit.bbox(q),'valid_one_solid':q.isValid() and len(q.Solids())==1};models[n]=q
        native['preview-'+n+'-aft45']={'brep':str(path.relative_to(ROOT)),'sha256':preview_records[n]['sha256']}
    fixed_prefixes=('cold-core/','bulkhead-','union-','nameplate-','keystone-','c14-','tube-collar-','label-','funnel')
    fixed_names={'co2-inlet','vk-solenoid','vk-cradle','valve-v-a','valve-v-b','source-a-cradle','source-b-cradle','nameplate','nameplate-ink','fixed-rear-carb2-occupied-envelope'}
    moving=set()
    for n,q in models.items():
        if n not in changed or n.startswith(fixed_prefixes) or n in fixed_names:continue
        if audit.bbox(q)[4]>=295.6915 or n in ['psu','pcba','asse1022-assembly','asse-drip-pan','asse-drip-sensor-plate','flow-regulator','suction-chain']:
            moving.add(n)
    # Any measured source valve/manifold and its own host remain fixed.
    for n in list(moving):
        owner=retained.get(n);owner=owner if isinstance(owner,list) else [owner]
        if any(o in fixed_names or isinstance(o,str) and o.startswith('valve-v-') for o in owner):moving.remove(n)
    # Both purchased screws follow the whole moved suction-chain host. Their
    # original fore station lies just outside the simple aft-seed Y band.
    moving.update(n for n in models if n.startswith('suction-chain-clip-screw-'))
    roots['nameplate-new_backing']='enclosure-back-top'
    for n in models:
        if n.startswith('relay-') and '-mount-screw-' in n:
            mates[frozenset([n,'cold-core/foam-cap-lid-top'])]='declared relocated blind-pilot station requiring parent-stock recut'
    for n in ['suction-chain-clip-screw-1','suction-chain-clip-screw-2']:
        for p in ['suction-chain-anchor','suction-chain-upper-key']:
            mates[frozenset([n,p])]='preserved suction-chain screw/pilot assembly'
    transforms={n:[0.,-8.,0.] for n in moving}
    for n in moving:
        if n=='pcba' or n.startswith(('controller-roof-boss-','controller-screw-')):transforms[n]=[0.,-14.,0.]
    for n,p in transforms.items():models[n]=models[n].translate(p)
    pairs=[];interferences=[];close=[];contacts=[];relocated_pilot_recuts=[]
    names=list(models)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if a not in moving and b not in moving:continue
            if not audit.broad(audit.bbox(models[a]),audit.bbox(models[b]),1.):continue
            screw=next((n for n in [a,b] if n in moving and n in ['pump-screw-1','pump-screw-2','pump-screw-3','pump-screw-4']),None)
            if screw is not None and 'cold-core/foam-cap-lid-top' in [a,b]:
                gap=models[a].distance(models[b]);v=audit.common(models[a],models[b]) if gap<1e-6 else 0.
                relocated_pilot_recuts.append({'parts':[a,b],'air_mm':gap,'common_mm3':v,
                    'fastener':screw,'fastener_translation_mm':transforms[screw],
                    'hypothetical_fastener_bounds_mm':audit.bbox(models[screw]),'print_owner':'cold-core-lid',
                    'required_action':'Recut the translated fastener pilot in the redesigned hypothetical lid parent.',
                    'scope':'Measured contact with the selected old pilot station. This is a required relocated-pilot recut, not an additional packing interference; the hypothetical fastener clearance, insert annulus, engagement and closed cap remain unproved.'})
                continue
            why=audit.intended(a,b,records,mates)
            if roots.get(a)==b or roots.get(b)==a:why='declared print root'
            if roots.get(a) is not None and roots.get(a)==roots.get(b):why='joined stock sharing a declared parent'
            if why:
                contacts.append({'parts':[a,b],'reason':why});continue
            gap=models[a].distance(models[b]);v=audit.common(models[a],models[b]) if gap<1e-6 else 0.
            row={'parts':[a,b],'air_mm':gap,'common_mm3':v};pairs.append(row)
            if v>.001:interferences.append(row);print('coupled rigid collision',row,flush=True)
            elif gap<1.-1e-5:close.append(row)
    psu=models['psu'];pcb=models['pcba'];pb=audit.bbox(psu);surround=[]
    controller_scan=[]
    for total_fore in [12.,12.5,13.,14.]:
        board=pcb.translate((0,14.-total_fore,0))
        controller_scan.append({'controller_translation_mm':[0,-total_fore,0],
            'supply_air_mm':psu.distance(board),
            'asse_roof_seat_2_air_mm':board.distance(models['asse-roof-seat-2']),
            'asse_roof_seat_2_common_mm3':audit.common(board,models['asse-roof-seat-2']),
            'asse_carrier_air_mm':board.distance(models['asse-removable-carrier']),
            'funnel_frame_air_mm':board.distance(models['funnel-frame']),
            'scope':'Local board/ASSE holder spacing only. Complete controller supports and all other body/route constraints are not re-proved by this small scan.'})
    selected_pan=models['asse-drip-pan'].translate((0,8,0));kept_pan_pairs=[]
    for n,q in models.items():
        if n in ['asse-drip-pan','moisture-plate'] or n.startswith('cold-core/') or n not in moving:continue
        if not audit.broad(audit.bbox(selected_pan),audit.bbox(q),1.):continue
        d=selected_pan.distance(q)
        kept_pan_pairs.append({'part':n,'air_mm':d,'common_mm3':audit.common(selected_pan,q) if d<1e-6 else 0.})
    for n in ['gas-inlet-west-tube-seat','gas-inlet-west-tube-tie']:
        q=models[n];d=selected_pan.distance(q)
        kept_pan_pairs.append({'part':n,'air_mm':d,'common_mm3':audit.common(selected_pan,q) if d<1e-6 else 0.})
    for n,q in models.items():
        if n=='psu' or n.startswith(('supply-lid-','supply-screw-','supply-washer-')):continue
        if not audit.broad(pb,audit.bbox(q),12.):continue
        d=psu.distance(q);below=audit.bbox(q)[5]<=pb[2]+1e-5;required=5. if below else 10.
        if d<12.:surround.append({'part':n,'air_mm':d,'required_distance_mm':required,'below_base_plane':below,'pass':d>=required-1e-5})
    core_approaches=[];operation_errors=[]
    for n,x,y in [('a-fill',57.5,426.3),('b-fill',-43.5,233.3),('b-draw',-43.5,188.9),('a-draw',43.5,188.9),('carb',77.5,271.6),('co2',77.5,322.3),('water',-56,188.9)]:
        reserve=cq.Solid.makeCylinder(3.175,14,cq.Vector(x,y,253.4))
        for other in moving:
            if not audit.broad(audit.bbox(reserve),audit.bbox(models[other]),0):continue
            try:v=audit.common(reserve,models[other])
            except RuntimeError as error:
                operation_errors.append({'check':'fixed core normal approach','mouth':n,'part':other,'error':str(error)});continue
            if v>.001:core_approaches.append({'fixed_core_mouth':n,'moved_part':other,'normal_reserve_mm':14,'common_mm3':v})
    root_checks=[]
    for n,parent in roots.items():
        if n not in models or parent not in models or n not in moving:continue
        joint=audit.common(models[n],models[parent],exact_root_fallback=True)
        root_checks.append({'part':n,'parent':parent,'root_common_mm3':joint,'pass':joint>.001})
    drift=['native:'+n for n,r in native.items() if sha(ROOT/r['brep'])!=r['sha256']]
    drift+=['source:'+p for p,h in sources.items() if sha(ROOT/p)!=h]
    drift+=['manifest-content:'+p for p,h in content.items() if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    report={'selected_geometry_changed':False,'complete_layout_feasible':False,
        'hypothesis':{'aft_funnel_growth_mm':45.,'group_translation_mm':[0,-8,0],'controller_translation_mm':[0,-14,0]},
        'capacity_to_brim_ml':capacity,'preview_funnel_parts':preview_records,
        'fixed_rear_carb2_envelope_parity':sleeve_proof,
        'moved_parts':transforms,'fixed_rigid_parts':sorted(set(models)-moving),
        'supply_bounds_mm':pb,'controller_bounds_mm':audit.bbox(pcb),'supply_controller_air_mm':psu.distance(pcb),
        'supply_rear_wall_air_mm':465.3-pb[4],'supply_pump_air_mm':psu.distance(models['g-ganen-pump']),
        'supply_fixed_rear_carb2_full_envelope_air_mm':psu.distance(models['fixed-rear-carb2-occupied-envelope']),
        'controller_local_fore_scan':controller_scan,
        'pan_kept_at_selected_pose_probe':{'bounds_mm':audit.bbox(selected_pan),
            'moved_vent_y_mm':302.3,'selected_flat_floor_y_interval_mm':[288.1,330.1],
            'vent_full_9_53mm_footprint_y_air_mm':302.3-4.765-288.1,
            'native_pairs':kept_pan_pairs,
            'scope':'Holding the complete selected pan keeps the moved ASSE vent footprint over its flat floor. These pair checks determine whether the moved rigid package permits that held pan; its factory removal and sensing need a new coupled proof.'},
        'supply_rigid_surround':surround,'surround_distance_failures':[r for r in surround if not r['pass']],
        'rigid_interferences':interferences,'close_rigid_pairs':close,'checked_rigid_pairs':len(pairs),'declared_contacts':contacts,
        'required_relocated_pilot_recuts':relocated_pilot_recuts,
        'fixed_core_normal_approach_blockers':core_approaches,'moved_print_root_checks':root_checks,'operation_errors':operation_errors,
        'controller_pilot_cover_mm':3.,'boundary_routing_reproof_required':True,
        'native_inputs':native,'source_inputs':sources,'manifest_content_sha256':content,'source_drift':drift,
        'source_binding_pass':not drift,'elapsed_seconds':time.time()-started,
        'scope':'Rigid-only bounded hypothesis. Fixed rear fittings, cap mouths, source manifold and valves remain at selected datums. Plain aft-bay bodies and hosts translate8mm fore; controller and its bosses/screws translate14mm fore at unchangedZ. Complete+45 funnel preview uses the fixed VK and front lead underside reliefs. Existing boundary tubes/wires, custom shell channels, print-root support, joined stock, fasteners, motion, Mylar/insulation, derating, ventilation and physical performance require redesign/reproof; this file does not establish a complete feasible installation.'}
    (HERE/'psu-coupled-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['supply_controller_air_mm','supply_rear_wall_air_mm','supply_pump_air_mm','rigid_interferences','surround_distance_failures','fixed_core_normal_approach_blockers','source_drift']},indent=2),flush=True)

if __name__=='__main__':main()
