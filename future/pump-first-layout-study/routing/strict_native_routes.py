"""SHA-bound native proof for every selected large exterior fluid route.

An unexpectedly zero OCC common is never a clearance result: actual distance
must meet the stated one-millimetre air target. Controlled end engagements
and the route's own explicitly named bearing interfaces are reported apart.
"""
from pathlib import Path
from io import BytesIO
import hashlib,itertools,json,math,re,sys,time
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3];STUDY=ROOT/'future/pump-first-layout-study';HERE=STUDY/'routing'
sys.path[:0]=[str(HERE),str(STUDY/'wiring'),str(STUDY)];import audit,evidence_binding
from fluid_members import circular_parity,sealed_sleeve_parity,received_member_compound,closest_members

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def power_member_distance(a,b):
    """Exact closest physical members, with only proven AABB pruning."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    aa=[(s,audit.bbox(s)) for s in a.Solids()];bb=[(s,audit.bbox(s)) for s in b.Solids()]
    candidates=[]
    for i,(s,sb) in enumerate(aa):
        for j,(t,tb) in enumerate(bb):
            lower=math.sqrt(sum(max(sb[k]-tb[k+3],tb[k]-sb[k+3],0.)**2 for k in range(3)))
            candidates.append((lower,i,j))
    candidates.sort();minimum=math.inf;overlap=0.;count=0;closest=None
    for lower,i,j in candidates:
        if lower>minimum+1e-7:break
        s=aa[i][0];t=bb[j][0];gap=s.distance(t);count+=1
        if gap<minimum:minimum=gap;closest={'a_member':i,'b_member':j,'air_mm':gap}
        if gap<1e-5:overlap+=audit.common(s,t)
    if closest is not None:
        operation=BRepExtrema_DistShapeShape(aa[closest['a_member']][0].wrapped,bb[closest['b_member']][0].wrapped)
        if not operation.IsDone():raise ValueError('Fluid–power member distance did not complete')
        for key,point in [('a_point_mm',operation.PointOnShape1(1)),('b_point_mm',operation.PointOnShape2(1))]:
            closest[key]=[point.X(),point.Y(),point.Z()]
    return minimum,overlap,count,closest

def load():
    models,records,changed,mates,inputs=audit.collect()
    content_inputs=dict(inputs.content_sha256)
    aliases={'funnel':'funnel/candidate.json','pump':'pump/candidate.json','pump-fluid24':'pump/fluid24-candidate.json',
        'routing':'routing/candidate.json','structure':'structure/candidate.json','mounts':'mounts/candidate.json',
        'wiring':'wiring/candidate.json','fluid-mounts':'mounts/fluid-candidate.json','body-mounts':'mounts/body-candidate.json',
        'water5-mounts':'mounts/water5-hosts.json','tube-hosts':'routing/tube-hosts.json',
        'roof-hatch':'structure/roof-hatch.json','scene-stock':'structure/scene-stock.json'}
    manifest_inputs={aliases[k]:v for k,v in inputs.items()if k in aliases}
    extras=['routing/co2-candidate.json','routing/tube-hosts.json',
            'mounts/needle-candidate.json','mounts/wr-candidate.json','mounts/check-tee-candidate.json',
            'mounts/water5-hosts.json','wiring/lower-lead-exits.json','wiring/controls-candidate.json',
            'wiring/power-candidate.json',
            'wiring/control-reserves.json','wiring/control-fanouts-check.json']
    contact=set(mates);control_scope={}
    for relative in extras:
        path=STUDY/relative
        if not path.exists():continue
        raw=path.read_bytes();m=json.loads(raw);manifest_inputs[relative]=hashlib.sha256(raw).hexdigest()
        content_inputs[str(path.relative_to(ROOT))]=evidence_binding.content_sha256(m)
        if relative=='wiring/controls-candidate.json':
            control_scope.update({'grouped_routes':sum(bool(v.get('from_dock')) for v in m.get('control_routes',{}).values()),
                                 'static_parts':m.get('coverage',{}).get('completed_static_parts',0)})
        if relative=='wiring/power-candidate.json':
            control_scope['power_routes']=len(m.get('power_routes',{}))
            control_scope['power_part_diameters_mm']={'wire-'+n:v['diameter_mm'] for n,v in m.get('power_routes',{}).items()}
        for n,r in m.get('parts',{}).items():records[n]=r;models[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
        for pair in m.get('intended_contacts',[]):contact.add(frozenset(pair))
        for host,tube in m.get('retained_components',{}).items():
            for p in tube if isinstance(tube,list)else[tube]:
                if p.startswith('tube-'):
                    contact.add(frozenset([host,p]))
                    control_scope.setdefault('controlled_bearing_owners',{}).setdefault(host,[]).append(p)
    raw=(HERE/'candidate.json').read_bytes();r=json.loads(raw)
    manifest_inputs['routing/candidate.json']=hashlib.sha256(raw).hexdigest()
    content_inputs[str((HERE/'candidate.json').relative_to(ROOT))]=evidence_binding.content_sha256(r)
    for pair in r.get('intended_contacts',[]):contact.add(frozenset(pair))
    for field,move in r.get('interface_moves',{}).items():
        for part in ['new_receiver','new_backing']:
            if part in move:
                n=field+'-'+part;rec=move[part];records[n]=rec;models[n]=cq.Shape.importBrep(str(ROOT/rec['brep']))
    pump_path=STUDY/'pump/candidate.json';raw=pump_path.read_bytes();pump=json.loads(raw)
    manifest_inputs['pump/candidate.json']=hashlib.sha256(raw).hexdigest()
    content_inputs[str(pump_path.relative_to(ROOT))]=evidence_binding.content_sha256(pump)
    return models,records,contact,r,manifest_inputs,content_inputs,pump,control_scope

def main():
    started=time.time()
    source_inputs={str(p.relative_to(STUDY)):sha(p)for p in
                   [HERE/'strict_native_routes.py',HERE/'fluid_members.py',
                    STUDY/'wiring/circular_clearance.py',STUDY/'wiring/native_harness.py',
                    STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    models,records,contact,r,manifest_inputs,content_inputs,pump,control_scope=load()
    fixed_ports={'core.carb':([77.5,271.6,253.4000001],[0,0,1]),
        'core.co2':([77.5,322.3,253.4000001],[0,0,1]),
        'core.a-fill':([57.5,426.3,253.4000001],[0,0,1]),
        'valve-v-f.outlet':([82.1,105.29,282.175],[0,0,1]),
        'valve-v-g.outlet':([73.82,166.24,229.675],[0,0,1]),
        'valve-v-j.outlet':([-73.82,166.24,229.675],[0,0,1]),
        'bulkhead-flavor-a.inboard':([-37.81,446.51,269.024],[0,-1,0]),
        'bulkhead-flavor-b.inboard':([-78.07,446.51,269.024],[0,-1,0])}
    def endpoint(name):
        body,port=name.split('.')
        if body in r['ports']:
            v=r['ports'][body][port];return cq.Vector(*v['pos']),cq.Vector(*v['axis'])
        if body in pump['poses']and port in pump['poses'][body]:
            p,n=pump['poses'][body][port];return cq.Vector(*p),cq.Vector(*n)
        p,n=fixed_ports[name];return cq.Vector(*p),cq.Vector(*n)
    # Shell joining/closure is bound by the separate complete-print proofs.
    power_parts=set(control_scope.get('power_part_diameters_mm',{}))
    models={n:q for n,q in models.items()if not n.startswith('enclosure-')and (not n.startswith('wire-') or n in power_parts)and n not in ['rear-roof-hatch']}
    routes={};geometry=[];excluded=[];native={};path_inputs={};neighbor_parity={};section_errors=[];declared_mismatches=[]
    # Import the exact bytes being hashed, rather than hash a path after its
    # shape was imported. End-of-run drift checks guard every received asset.
    for n in models:
        p=ROOT/records[n]['brep'];raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        q=cq.Shape.importBrep(BytesIO(raw));models[n]=q
        native[n]={'brep':records[n]['brep'],'sha256':digest,'bounds':audit.bbox(q),'valid':q.isValid(),'solids':len(q.Solids())};path_inputs[str(p)]=digest
        declared=records[n].get('sha256')
        if isinstance(declared,str) and declared!=digest:
            declared_mismatches.append({'part':n,'brep':records[n]['brep'],'declared_sha256':declared,'received_sha256':digest})
    all_route_parts={p for run in r['routes'].values()for p in run['parts']}
    # Other long fluid exteriors are received independently too. Printed
    # collars, hose clamps and short engagement annuli retain their actual
    # native stock; each of their solids is checked separately below.
    for n,q in list(models.items()):
        if n in all_route_parts or not re.match(r'^tube-(?:fluid-\d+|water-\d+|customer-(?:water|co2))$',n):continue
        diameter=15.1 if n in ['tube-water-6','tube-water-7'] else 6.35
        try:
            models[n],proof=circular_parity(q,diameter)
            proof['received_brep']=native[n]['brep'];proof['received_sha256']=native[n]['sha256']
            neighbor_parity[n]=proof
            if not proof['pass']:section_errors.append({'part':n,'reason':'Received neighboring circular section correspondence failed'})
        except ValueError as error:
            section_errors.append({'part':n,'reason':str(error)})
        print('neighbor section',n,len(models[n].Solids()),'pass',n in neighbor_parity and neighbor_parity[n]['pass'],flush=True)
    for n in sorted(power_parts):
        if n not in models:
            section_errors.append({'part':n,'reason':'Declared power route has no received native exterior'});continue
        try:
            models[n],proof=received_member_compound(models[n],control_scope['power_part_diameters_mm'][n])
            proof['received_brep']=native[n]['brep'];proof['received_sha256']=native[n]['sha256'];neighbor_parity[n]=proof
            if not proof['pass']:section_errors.append({'part':n,'reason':'Received power member section correspondence failed'})
        except ValueError as error:section_errors.append({'part':n,'reason':str(error)})
        print('power section',n,len(models[n].Solids()),'pass',n in neighbor_parity and neighbor_parity[n]['pass'],flush=True)
    for cid,run in r['routes'].items():
        parts=run['parts'];rec=r['parts']['tube-'+cid]['route'];cpath=ROOT/rec['centreline_brep']
        raw=cpath.read_bytes();centreline_digest=hashlib.sha256(raw).hexdigest();w=cq.Shape.importBrep(BytesIO(raw));edges=w.Edges()
        path_inputs[str(cpath)]=centreline_digest
        radii=[e.radius()for e in edges if e.geomType()=='CIRCLE'];tangent=[]
        for a,b in zip(edges,edges[1:]):
            tangent.append({'gap_mm':(a.endPoint()-b.startPoint()).Length,'angle_deg':math.degrees(a.tangentAt(1).getAngle(b.tangentAt(0)))})
        radius=min(radii)if radii else math.inf
        source,normal=endpoint(run['from']);dest,dest_normal=endpoint(run['to'])
        endpoint_errors=[(edges[0].startPoint()-source).Length,(edges[-1].endPoint()-dest).Length]
        normal_errors=[math.degrees(edges[0].tangentAt(0).getAngle(normal)),
                       math.degrees(edges[-1].tangentAt(1).getAngle(-dest_normal))]
        allowed_skew=rec.get('source_attachment_skew_deg',0.)
        # The gas producer records the same native assertions as two arrays.
        # Normalize their names without replacing any geometric assertion.
        if 'endpoint_error_mm'in rec:
            rec={**rec,'source_position_error_mm':rec['endpoint_error_mm'][0],
                 'destination_position_error_mm':rec['endpoint_error_mm'][1],
                 'source_normal_error_deg':math.degrees(rec['endpoint_angle_rad'][0]),
                 'destination_normal_error_deg':math.degrees(rec['endpoint_angle_rad'][1])}
        volume=math.pi*3.175**2*w.Length();physical=models['tube-'+cid].Volume(tol=1e-9)
        section=None
        try:
            tube=models['tube-'+cid]
            if any(n.startswith('carb-foam-') for n in parts):
                foam=next(models[n] for n in parts if n.startswith('carb-foam-'))
                # The source tube and the received sleeve both have their
                # own section correspondence; occupancy uses the full outer
                # envelope, including the lumen, for every clearance test.
                _,tube_section=circular_parity(tube,6.35,edges)
                q,section=sealed_sleeve_parity(tube,foam,edges)
                section['received_tube_section_proof']=tube_section
                section['pass']=section['pass'] and tube_section['pass']
            else:q,section=circular_parity(tube,6.35,edges)
            section['received_native_parts']={n:{'brep':native[n]['brep'],'sha256':native[n]['sha256']} for n in parts}
            section['saved_centreline_brep']=rec['centreline_brep'];section['saved_centreline_sha256']=centreline_digest
        except ValueError as error:
            section_errors.append({'route':cid,'reason':str(error)})
            q=cq.Compound.makeCompound([models[n] for n in parts]) if len(parts)>1 else models[parts[0]]
        row={'route':cid,'from':run['from'],'to':run['to'],'developed_mm':w.Length(),
             'minimum_radius_mm':radius,'stock_radius_pass':radius>=14-1e-6,
             'normal_position_assertions':{k:rec.get(k)for k in ['source_position_error_mm','destination_position_error_mm','source_normal_error_deg','destination_normal_error_deg']},
             'native_endpoint_errors_mm':endpoint_errors,'native_normal_errors_deg':normal_errors,
             'allowed_source_attachment_skew_deg':allowed_skew,
             'tangent_continuity_pass':all(x['gap_mm']<1e-5 and x['angle_deg']<.001 for x in tangent),
             'sweep_volume_mm3':physical,'area_length_volume_mm3':volume,
             'volume_pass':abs(physical-volume)<max(.05,volume*1e-6),
             'complete_insulation':any(n.startswith('carb-foam-')for n in parts),
             'centreline_brep':rec['centreline_brep'],'centreline_sha256':centreline_digest,
             'physical_section_proof':section,'physical_section_pass':section is not None and section['pass']}
        row['pass']=row['physical_section_pass']and row['stock_radius_pass']and row['tangent_continuity_pass']and row['volume_pass']and max(endpoint_errors)<1e-5 and normal_errors[0]<=allowed_skew+1e-5 and normal_errors[1]<1e-5 and rec.get('source_position_error_mm',math.inf)<1e-5 and rec.get('destination_position_error_mm',math.inf)<1e-5
        geometry.append(row);routes[cid]=(q,parts)
        print('route section',cid,len(q.Solids()),'pass',row['physical_section_pass'],flush=True)
    failures=[];checks=0;member_checks=0;minimum=math.inf;closest=None;perroute={cid:[]for cid in routes};bearing_checks=[];power_checks=[]
    for cid,(q,parts)in routes.items():
        for other,b in models.items():
            if other in all_route_parts:continue
            if any(frozenset([n,other])in contact for n in parts):
                bearing=control_scope.get('controlled_bearing_owners',{}).get(other,[])
                if any(n in bearing for n in parts):
                    gap,v,count,member=closest_members(q,b);member_checks+=count
                    row={'route':cid,'other':other,'air_mm':gap,'common_mm3':v,
                         'closest_physical_members':member,'pass':v<.001,
                         'scope':'Controlled bearing/tie air is separate from1mm running air; every full physical route member must remain free of its retainer material.'}
                    bearing_checks.append(row)
                    if not row['pass']:
                        failures.append(row);perroute[cid].append(row);print('controlled bearing interference',row,flush=True)
                excluded.append({'route':cid,'component':other,'reason':'Explicit fitting endpoint or controlled bearing air; declared bearing material overlaps are tested separately.'});continue
            if other in power_parts:
                gap,v,count,member=power_member_distance(q,b)
                power_checks.append({'route':cid,'power_part':other,'air_mm':gap,'common_mm3':v,
                                     'closest_physical_members':member,'pass':gap>=1.-1e-5})
            else:
                if not audit.broad(audit.bbox(q),audit.bbox(b),1.):continue
                gap,v,count,member=closest_members(q,b)
            checks+=1;member_checks+=count
            if gap<minimum:minimum=gap;closest={'route':cid,'other':other,'air_mm':gap}
            if gap>=1.-1e-5:continue
            row={'route':cid,'other':other,'air_mm':gap,'common_mm3':v,'closest_physical_members':member,'pass':False}
            failures.append(row);perroute[cid].append(row);print('route margin',row,flush=True)
    for a,b in itertools.combinations(routes,2):
        qa,pa=routes[a];qb,pb=routes[b]
        if not audit.broad(audit.bbox(qa),audit.bbox(qb),1.):continue
        checks+=1;gap,v,count,member=closest_members(qa,qb);member_checks+=count
        if gap<minimum:minimum=gap;closest={'route':a,'other':'route '+b,'air_mm':gap}
        if gap>=1.-1e-5:continue
        row={'route':a,'other':'route '+b,'air_mm':gap,'common_mm3':v,'closest_physical_members':member,'pass':False}
        failures.append(row);perroute[a].append(row);perroute[b].append(row);print('route margin',row,flush=True)
    drift=[p for p,h in path_inputs.items()if sha(Path(p))!=h]
    drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(ROOT/p)!=h]
    drift+=['source:'+p for p,h in source_inputs.items()if sha(STUDY/p)!=h]
    invalid=[n for n,v in native.items()if not v['valid']]
    control_complete=control_scope.get('grouped_routes')==26 and control_scope.get('static_parts')==49
    power_complete=control_scope.get('power_routes')==19 and power_parts.issubset(models)
    result={'pass':not drift and not failures and not invalid and not section_errors and not declared_mismatches and all(g['pass']for g in geometry)and len(routes)==13 and control_complete and power_complete,
        'invalid_inputs':invalid,
        'source_drift':drift,'source_inputs':source_inputs,'native_inputs':native,'manifests_sha256':manifest_inputs,
        'manifest_content_sha256':content_inputs,
        'route_geometry':geometry,'unexpected_pairs':failures,'controlled_contacts':excluded,
        'controlled_bearing_material_checks':bearing_checks,
        'fluid_power_air_checks':power_checks,
        'minimum_fluid_power_air_mm':min((p['air_mm'] for p in power_checks),default=None),
        'closest_fluid_power_pair':min(power_checks,key=lambda p:p['air_mm']) if power_checks else None,
        'physical_section_errors':section_errors,'neighboring_fluid_section_proofs':neighbor_parity,
        'declared_native_sha_mismatches':declared_mismatches,
        'minimum_unrelated_air_mm':minimum,'closest_unrelated_pair':closest,'native_pairs_checked':checks,
        'physical_member_pairs_checked':member_checks,
        'routes_checked':len(routes),'components_checked':len(models),
        'current_control_scope':control_scope,'complete_control_scope_pass':control_complete,
        'complete_power_scope_pass':power_complete,'power_exteriors_checked':len(power_parts),
        'boolean_fuzzy_mm':.0001,'common_volume_tolerance':1e-9,'minimum_unrelated_air_target_mm':1.,
        'distance_acceptance_tolerance_mm':1e-5,
        'scope':'All13 received large-bore exterior paths are matched to exact circular cylinder/arc members and saved native centrelines. Full25.4mm occupied carbonated envelopes are matched to the received sleeve outer/inner lateral faces, annular ends and material volumes. Distances and commons use individual physical members against every current purchased/printed bay neighbor, complete26 grouped control exteriors,49+ control reservations/fanouts, all19 actual power exteriors and exact lower lead exits. This proof enforces1mm nominal unrelated fluid-to-power air; conductor network/terminal correspondence receives its separate19-conductor proof. End engagement and explicitly controlled bearings are separate. Whole-shell movement/stock and physical load/lifetime remain separate proofs.',
        'elapsed_seconds':time.time()-started}
    if result['pass']:
        r['routing_status']={'constructed':list(routes),'finished':list(routes),'pending':[],
            'native_clearance_status':'pass','native_proof':'future/pump-first-layout-study/routing/strict-route-audit.json',
            'note':'All13 exactR14 paths pass the SHA-bound native exterior/full-insulation package proof; mechanical retention, print stock, whole-shell closure and physical qualification are separately bound.'}
        for cid in routes:r['routes'][cid]['native_clearance_status']='pass';r['parts']['tube-'+cid]['route']['native_clearance_status']='pass'
        (HERE/'candidate.json').write_text(json.dumps(r,indent=2)+'\n')
        # Geometry was already bound. Bind the final status-bearing manifest
        # after its intentional metadata write, before publishing this proof.
        result['manifests_sha256']['routing/candidate.json']=sha(HERE/'candidate.json')
        result['manifest_content_sha256'][str((HERE/'candidate.json').relative_to(ROOT))]=evidence_binding.content_sha256(r)
    (HERE/'strict-route-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'route_geometry':geometry,'unexpected_pairs':failures,'source_drift':drift,'minimum_air_mm':minimum},indent=2),flush=True)
    return result['pass']

if __name__=='__main__':
    if not main():raise SystemExit(1)
