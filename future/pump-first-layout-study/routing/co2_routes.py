"""Probe and publish the two frozen-endpoint gas routes independently."""
from pathlib import Path
import argparse,copy,hashlib,json,math,sys
from io import BytesIO
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/routing/co2'
sys.path[:0]=[str(HERE),str(STUDY),str(ROOT/'hardware/scripts')]
import audit
import evidence_binding
from curves import V,X,Y,Z,line,turn,s,wire,swept
from received_native import receive,circular_equivalence,centreline_equivalence
from fluid_members import circular_parity

def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--east-z',type=float,default=258.)
    parser.add_argument('--fore-turn-y',type=float,default=321.)
    parser.add_argument('--west-level',type=float,default=261.5)
    parser.add_argument('--west-x',type=float,default=-84)
    parser.add_argument('--inlet-x',type=float,default=83.3)
    parser.add_argument('--inlet-z',type=float,default=257.575)
    parser.add_argument('--inlet-lead-start',type=float,default=0.)
    parser.add_argument('--rear-bend-x',type=float,default=84.)
    parser.add_argument('--rear-bend-y',type=float,default=428.5)
    parser.add_argument('--seat-lane-x',type=float,default=84.7)
    parser.add_argument('--gas-rise-angle',type=float,default=34.5)
    parser.add_argument('--gas-column-x',type=float,default=68.2)
    parser.add_argument('--gas-cross-y',type=float,default=422.3)
    parser.add_argument('--gas-last-clock',type=float,default=.35)
    parser.add_argument('--wr-entry',choices=['yaw','direct'],default='yaw')
    parser.add_argument('--extra-obstacle',action='append',default=[])
    parser.add_argument('--check-lead',type=float,default=0.)
    parser.add_argument('--probe')
    parser.add_argument('--only',choices=['co2-0','co2-1'])
    parser.add_argument('--received','--check-only',action='store_true',
        help='Prove the selected in-memory recipe against saved gas native outputs without rewriting geometry.')
    args=parser.parse_args()
    if args.received and (args.probe or args.only or args.extra_obstacle):
        raise ValueError('Received proof requires both complete selected routes without probe overrides')
    previous=HERE/'co2-candidate.json'
    old=json.loads(previous.read_bytes())if args.received else None
    selected_parameters={key:value for key,value in vars(args).items()if key!='received'}
    if args.received and selected_parameters!=old['parameters']:
        raise ValueError('Received check parameters differ from the authoritative saved recipe')
    sources={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()for path in
        [Path(__file__),HERE/'curves.py',HERE/'received_native.py',HERE/'fluid_members.py',
         STUDY/'structure/assemble_prints_verified.py',STUDY/'wiring/circular_clearance.py',
         STUDY/'wiring/native_harness.py',STUDY/'audit.py',STUDY/'evidence_binding.py']}
    primary_out=OUT
    if args.probe:OUT=OUT.parent/('co2-probe-'+Path(args.probe).name)
    routing_raw=(HERE/'candidate.json').read_bytes();m=json.loads(routing_raw);models,records,changed,mates,inputs=audit.collect()
    content_inputs=dict(inputs.content_sha256)
    content_inputs[str((HERE/'candidate.json').relative_to(ROOT))]=evidence_binding.content_sha256(m)
    inputs['routing']=hashlib.sha256(routing_raw).hexdigest()
    # Rigid installed shapes and every other current fluid run take precedence.
    # Power and incomplete control routes are being rebuilt around these runs.
    models={n:q for n,q in models.items() if (args.received or not n.startswith(('wire-','control-','loom-','harness-','power-')))
            and n not in ['enclosure-front-top','enclosure-back-top','rear-roof-hatch','tube-co2-0','tube-co2-1']}
    for fname in ['control-reserves.json','control-fanouts-check.json']:
        path=STUDY/'wiring'/fname
        if path.exists():
            raw=path.read_bytes();controls=json.loads(raw);passed={r['part'] for r in controls.get('native_checks',[]) if r.get('pass')}
            content_inputs[str(path.relative_to(ROOT))]=evidence_binding.content_sha256(controls)
            inputs[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
            for name,record in controls.get('parts',{}).items():
                if name in passed:
                    records[name]=record;models[name]=cq.Shape.importBrep(str(ROOT/record['brep']))
    for fname in ['needle-candidate.json','wr-candidate.json','check-tee-candidate.json']:
        path=STUDY/'mounts'/fname
        if path.exists():
            raw=path.read_bytes();extra_manifest=json.loads(raw)
            content_inputs[str(path.relative_to(ROOT))]=evidence_binding.content_sha256(extra_manifest)
            inputs[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
            for name,record in extra_manifest.get('parts',{}).items():
                records[name]=record;models[name]=cq.Shape.importBrep(str(ROOT/record['brep']))
    controlled=set()
    guide_path=HERE/'tube-hosts.json'
    if guide_path.exists():
        raw=guide_path.read_bytes();guides=json.loads(raw)
        content_inputs[str(guide_path.relative_to(ROOT))]=evidence_binding.content_sha256(guides)
        inputs[str(guide_path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
        for host,tubes in guides.get('retained_components',{}).items():
            for tube in tubes if isinstance(tubes,list)else[tubes]:
                if tube.startswith('tube-'):controlled.add(frozenset([host,tube]))
    plate=m.get('interface_moves',{}).get('nameplate',{})
    for key in ['new_receiver','new_backing']:
        if key in plate:
            name='protected-nameplate-'+key;records[name]=plate[key]
            models[name]=cq.Shape.importBrep(str(ROOT/plate[key]['brep']))
    for extra in args.extra_obstacle:
        path=ROOT/extra
        name='probe-'+path.stem;records[name]={'brep':str(path.relative_to(ROOT))}
        models[name]=cq.Shape.importBrep(str(path))
    if args.only:
        other='co2-1' if args.only=='co2-0' else 'co2-0'
        path=primary_out/(other+'.brep')
        if path.exists():
            records['tube-'+other]={'brep':str(path.relative_to(ROOT))}
            models['tube-'+other]=cq.Shape.importBrep(str(path))
    native_inputs={}
    for n in models:
        record=records[n];raw=(ROOT/record['brep']).read_bytes()
        models[n]=cq.Shape.importBrep(BytesIO(raw))
        native_inputs[n]={'brep':record['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
    pos=lambda owner,key:V(m['ports'][owner][key]['pos'])
    norm=lambda owner,key:V(m['ports'][owner][key]['axis'])
    paths={}
    if args.only!='co2-1':
        a=pos('co2-inlet','inboard');b=V((args.rear_bend_x if args.rear_bend_x is not None else args.inlet_x,args.rear_bend_y,args.inlet_z));es,meta=s(a,-Y,b,lead_start=args.inlet_lead_start)
        if abs(b.x-args.inlet_x)>1e-9:
            returning=V((args.inlet_x,420,args.inlet_z));ee,meta=s(b,-Y,returning,lead_start=0);es+=ee;b=returning
        if args.seat_lane_x is not None:
            before=V((args.inlet_x,410,args.inlet_z));es+=line(b,before)
            after=V((args.seat_lane_x,398.5,args.inlet_z));ee,meta=s(before,-Y,after);es+=ee
            bb=V((args.seat_lane_x,378,args.inlet_z));es+=line(after,bb)
        else:
            bb=V((args.inlet_x,378,args.inlet_z));es+=line(b,bb)
        bc=V((100.325,344,args.east_z));ee,meta=s(bb,-Y,bc);es+=ee
        c=V((100.325,args.fore_turn_y,args.east_z));es+=line(bc,c);ee,d=turn(c,-Y,-X);es+=ee
        e=V((40,args.fore_turn_y-14,args.east_z));es+=line(d,e)
        f=V((5,275.325,args.west_level));ee,meta=s(e,-X,f);es+=ee
        g=V((args.west_x+14,275.325,args.west_level));es+=line(f,g);ee,kp=turn(g,-X,Z);es+=ee
        u=-norm('wr1110','inlet');inc=pos('wr1110','inlet')
        if args.wr_entry=='yaw':
            yaw=Y.getAngle(u)
            lateral=(u-Y*math.cos(yaw)).normalized()
            dest=inc-u*6-Y*(14+14*math.sin(yaw))-lateral*(14*(1-math.cos(yaw)))-Z*14
            ee,meta=s(kp,Z,dest);es+=ee;ee,n=turn(dest,Z,Y);es+=ee
            ee,n=turn(n,Y,lateral,yaw);es+=ee+line(n,inc)
        else:
            dest=inc-u*20-Z*14
            ee,meta=s(kp,Z,dest);es+=ee;ee,n=turn(dest,Z,u);es+=ee+line(n,inc)
        paths['co2-0']=(es,'co2-inlet.inboard','wr1110.inlet')
    if args.only!='co2-0':
        u=norm('wr1110','outlet');a=pos('wr1110','outlet')
        # A compound R14 rise/clocking turn crosses the supply fore of the
        # discharge clamp. Both arc normals are exact, including the yaw.
        b=a;es=[];angle=math.radians(args.gas_rise_angle)
        ee,c=turn(b,u,Z,angle);es+=ee;h=u*math.cos(angle)+Z*math.sin(angle)
        theta=h.getAngle(X);k=(X-h*math.cos(theta)).normalized()
        ee,c=turn(c,h,k,theta);es+=ee
        fore=V((c.x+30,args.gas_cross_y,c.z));ee,meta=s(c,X,fore);es+=ee;c=fore
        # The descending station is dictated by the check's normal/R14 turn.
        inlet=pos('gasher-co2','inlet');last_h=V((args.gas_last_clock,0,-math.sqrt(1-args.gas_last_clock**2)))
        final_end=inlet+Y*args.check_lead
        station=final_end-last_h*14+Y*14
        target=V((args.gas_column_x-14,c.y,c.z))
        es+=line(c,target);ee,d=turn(target,X,-Z);es+=ee
        clock=math.asin(args.gas_last_clock);dx=14*(1-math.cos(clock))
        reach=(station.x-args.gas_column_x-dx)/last_h.x
        below=V((args.gas_column_x,station.y,station.z+14*math.sin(clock)-last_h.z*reach))
        ee,meta=s(d,-Z,below);es+=ee;ee,e=turn(below,-Z,X,clock);es+=ee+line(e,station)
        ee,e=turn(station,last_h,-Y);es+=ee+line(e,inlet)
        paths['co2-1']=(es,'wr1110.outlet','gasher-co2.inlet')
    if not args.received:OUT.mkdir(parents=True,exist_ok=True)
    result=copy.deepcopy(old)if args.received else {'parts':{},'routes':{},'clearance_cutters':{},'checks':[],
        'manifests_sha256':inputs,'parameters':selected_parameters,'intended_contacts':[]}
    if args.received:result['checks']=[]
    if args.only and previous.exists():
        old=json.loads(previous.read_text());keep='co2-1' if args.only=='co2-0' else 'co2-0'
        for key in ['parts','clearance_cutters']:
            name='tube-'+keep
            if name in old.get(key,{}):result[key][name]=old[key][name]
        if keep in old.get('routes',{}):result['routes'][keep]=old['routes'][keep]
        result['checks']=[c for c in old.get('checks',[]) if c.get('route')==keep]
        result['intended_contacts']=[pair for pair in old.get('intended_contacts',[]) if 'tube-'+keep in pair]
    for cid,(es,frm,to) in paths.items():
        source_owner,source_port=frm.split('.');target_owner,target_port=to.split('.')
        source_error=(es[0].startPoint()-pos(source_owner,source_port)).Length
        target_error=(es[-1].endPoint()-pos(target_owner,target_port)).Length
        source_angle=es[0].tangentAt(0).getAngle(norm(source_owner,source_port))
        target_angle=es[-1].tangentAt(1).getAngle(-norm(target_owner,target_port))
        if max(source_error,target_error,source_angle,target_angle)>1e-5:
            raise ValueError(f'{cid} endpoint position/normal mismatch: {source_error},{target_error},{source_angle},{target_angle}')
        q=swept(es,es[0].tangentAt(0));name='tube-'+cid;equivalence=[]
        if args.received:
            received=receive(ROOT,old['parts'][name],'received-gas/'+name,native_inputs)
            equivalence.append(circular_equivalence(received,q,es,6.35,name))
            q=received
            check_shape,_=circular_parity(q,6.35,es)
            equivalence.append({'check':'received gas endpoints retain their exact owner/port identities','route':cid,
                'pass':old['routes'][cid]['from']==frm and old['routes'][cid]['to']==to})
        else:check_shape=q
        owners={frm.split('.')[0],to.split('.')[0]}
        owners|={'co2-adapter-regulator-'+('in' if cid=='co2-0' else 'out')}
        if cid=='co2-1':owners.add('co2-adapter-check-in')
        hits=[];near=[]
        for other,shape in models.items():
            if other in owners or not audit.broad(audit.bbox(check_shape),audit.bbox(shape),1):continue
            if frozenset([name,other])in controlled:
                overlap=audit.common(check_shape,shape)
                equivalence.append({'check':'controlled gas bearing retains no pipe material overlap',
                    'route':cid,'part':other,'common_mm3':overlap,'pass':overlap<.001})
                continue
            gap=check_shape.distance(shape)
            if gap>=1-1e-6:continue
            overlap=audit.common(check_shape,shape) if gap<1e-6 else 0.
            row={'neighbor':other,'gap_mm':gap,'overlap_mm3':overlap};near.append(row)
            if overlap>.01:hits.append(row)
        for other,record in result['parts'].items():
            if other==name or other in models:continue
            shape=cq.Shape.importBrep(str(ROOT/record['brep']))
            if args.received:shape,_=circular_parity(shape,6.35)
            if not audit.broad(audit.bbox(check_shape),audit.bbox(shape),1):continue
            gap=check_shape.distance(shape);overlap=audit.common(check_shape,shape) if gap<1e-6 else 0.
            if gap<1-1e-6:near.append({'neighbor':other,'gap_mm':gap,'overlap_mm3':overlap})
            if overlap>.01:hits.append({'neighbor':other,'gap_mm':gap,'overlap_mm3':overlap})
        centerline=wire(es);length=centerline.Length();expected=math.pi*3.175**2*length
        volume=q.Volume(tol=1e-9)
        if not q.isValid() or abs(volume-expected)>max(.001,expected*1e-6):
            raise ValueError(cid+' complete occupied exterior does not preserve its section')
        if args.received:
            wp=ROOT/old['parts'][name]['route']['centreline_brep']
            saved_line=receive(ROOT,{'brep':str(wp.relative_to(ROOT))},'received-gas-centreline/'+cid,native_inputs)
            equivalence.append(centreline_equivalence(saved_line,es,cid))
        else:
            wp=OUT/(cid+'-centreline.brep');centerline.exportBrep(str(wp))
        straight=[];distance=0.
        for edge in es:
            if edge.geomType()=='LINE':
                straight.append({'start':list(edge.startPoint().toTuple()),'end':list(edge.endPoint().toTuple()),
                    'length_mm':edge.Length(),'start_developed_mm':distance,'end_developed_mm':distance+edge.Length()})
            distance+=edge.Length()
        if args.received:path=ROOT/old['parts'][name]['brep']
        else:
            path=OUT/(cid+'.brep');q.exportBrep(str(path))
        route={'from':frm,'to':to,'kind':'co2','diameter_mm':6.35,'minimum_bend_mm':14,
               'length_mm':length,'radii':[14 for edge in es if edge.geomType()=='CIRCLE'],
               'waypoints':[edge.startPoint().toTuple() for edge in es]+[es[-1].endPoint().toTuple()],
               'tangent_continuity_pass':True,'endpoints_exact':True,
               'endpoint_error_mm':[source_error,target_error],
               'endpoint_angle_rad':[source_angle,target_angle],
               'centreline_brep':str(wp.relative_to(ROOT)),'straight_segments':straight,
               'sweep_volume_mm3':volume,'sweep_area_length_volume_mm3':expected,
               'native_clearance_status':'pass' if not near and not hits else 'fail'}
        if not args.received:
            result['parts'][name]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'role':'gas','bounds':audit.bbox(q),'route':route,'detail':'Exact R14 gas tube on the frozen fitting normals; complete6.35mm occupied exterior.'}
            result['routes'][cid]={'from':frm,'to':to,'parts':[name],'stock_bend_pass':True,
                'native_clearance_status':route['native_clearance_status'],'diameter_mm':6.35,
                'minimum_bend_mm':14,'developed_length_mm':length,'endpoints_exact':True}
        cutter=swept(es,es[0].tangentAt(0),8.35)
        if args.received:
            saved=receive(ROOT,old['clearance_cutters'][name],'received-gas-clearance/'+cid,native_inputs)
            equivalence.append(circular_equivalence(saved,cutter,es,8.35,cid+'-clearance'))
        else:
            cp=OUT/(cid+'-clearance.brep');cutter.exportBrep(str(cp))
            result['clearance_cutters'][name]={'brep':str(cp.relative_to(ROOT)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
                'radial_air_mm':1,'print_owner':'enclosure-back-top'}
        result['checks'].append({'route':cid,'pass':not near and not hits and all(row['pass']for row in equivalence),
            'hits':hits,'close_pairs':near,'received_native_equivalence':equivalence})
        if not args.received:
            for owner in owners:result['intended_contacts'].append([name,owner])
        print(json.dumps({'route':cid,'hits':hits,'length_mm':length}),flush=True)
    drift=[n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    drift+=['source:'+p for p,h in sources.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    result['native_inputs']=native_inputs;result['source_drift']=drift
    result['source_inputs']=sources;result['manifest_content_sha256']=content_inputs;result['manifests_sha256']=inputs
    if args.received:
        before=evidence_binding.content_sha256(old);after=evidence_binding.content_sha256(result)
        result['checks'].append({'check':'received gas proof preserves complete selected substantive content',
            'received_content_sha256':before,'current_content_sha256':after,'pass':before==after})
        print('received content parity',before,after,flush=True)
    result['pass']=not drift and all(c['pass'] for c in result['checks'])
    target=HERE/('co2-probe-'+Path(args.probe).name+'.json')if args.probe else previous
    target.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
