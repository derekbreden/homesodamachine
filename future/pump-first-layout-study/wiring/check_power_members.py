"""Check and publish the same exact circular members used for power admission.

Whole swept-pipe Boolean classification can miss a crossing. Every straight
cylinder and arc is therefore tested independently, including the received
clearance cutter, and those physical members are the published conductor.
"""
from pathlib import Path
from io import BytesIO
import argparse, hashlib, json, math, sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent; ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
import audit
from native_harness import sweep, bounds, broad
from circular_clearance import paired_members,CircularSelfIntersection
from evidence_binding import content_sha256
from controls_harness import passed_body_models
from power_harness import received_fluid_models,terminal_approach_members
sys.path.insert(0,str(STUDY/'routing'))
from fluid_members import received_member_compound,lateral_records,compare_lateral

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check published members without changing conductor files')
    args=parser.parse_args()
    source_paths=[Path(__file__),HERE/'power.py',HERE/'power_harness.py',HERE/'recover_power.py',HERE/'adopt_power_recipes.py',HERE/'native_harness.py',HERE/'circular_clearance.py',
        HERE/'controls_harness.py',HERE/'ground_interfaces.py',STUDY/'routing/fluid_members.py',
        STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']
    sources={str(p.relative_to(ROOT)):sha(p)for p in source_paths}
    models,records,_,mates,manifest_hashes=audit.collect()
    manifests=dict(manifest_hashes.content_sha256)
    raw_bindings={}
    def read_manifest(path):
        raw=path.read_bytes();key=str(path.relative_to(ROOT));value=json.loads(raw)
        raw_bindings[key]=hashlib.sha256(raw).hexdigest();manifests[key]=content_sha256(value)
        return value
    power=read_manifest(HERE/'power-candidate.json')
    for filename in ['controls-candidate.json','control-reserves.json','control-fanouts-check.json','lower-lead-exits.json']:
        path=HERE/filename
        if path.exists():
            for name,rec in read_manifest(path).get('parts',{}).items():records[name]=rec
    for filename in ['needle-candidate.json','wr-candidate.json','check-tee-candidate.json']:
        path=STUDY/'mounts'/filename
        if path.exists():read_manifest(path)
    body_models,body_records=passed_body_models();records.update(body_records)
    roof=read_manifest(STUDY/'mounts/roof-candidate.json')
    for name,rec in roof.get('working_envelopes',{}).items():records['lever-space-'+name]=rec['levers']
    shell=read_manifest(STUDY/'funnel/shells.json')
    routing=read_manifest(STUDY/'routing/candidate.json')
    move=routing.get('interface_moves',{}).get('nameplate',{})
    records['protected-nameplate-stock']=move.get('new_receiver',shell['interfaces']['retained-nameplate-stock'])
    if move.get('new_backing'):records['protected-nameplate-backing']=move['new_backing']
    native={}
    for name,rec in records.items():
        if rec is None or name.startswith(('wire-AC','wire-DC','wire-PE','power-','enclosure-back-top','enclosure-front-top')):continue
        path=ROOT/rec['brep'];raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        declared=rec.get('sha256')
        if isinstance(declared,str) and digest!=declared:raise ValueError('Stale occupied native record '+name)
        models[name]=cq.Shape.importBrep(BytesIO(raw))
        native[name]={'brep':rec['brep'],'sha256':digest}
    models={n:models[n]for n in native}
    fluids,fluid_proofs=received_fluid_models(models,records,native)
    models.update(fluids)
    members={};tools={};proofs={};input_parts={};input_cutters={};failures=[];checks=[]
    if len(power.get('power_routes',{}))!=19:failures.append({'check':'19 complete power/earth routes','pass':False})
    for name,route in power.get('power_routes',{}).items():
        key='wire-'+name;rec=power['parts'][key];path=ROOT/rec['brep'];raw=path.read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=rec['sha256']:raise ValueError('Changed received power conductor '+name)
        input_parts[key]={'brep':rec['brep'],'sha256':digest}
        received=cq.Shape.importBrep(BytesIO(raw))
        authored,_=sweep(route['points_mm'],route['diameter_mm'],route['radius_mm'])
        try:
            physical,clearance,proof=paired_members(authored,route['diameter_mm'],gap=1.,fuse_clearance=False)
        except CircularSelfIntersection as error:
            row={'part':key,'check':'distinct physical member self clearance','members':error.indices,
                'common_mm3':error.volume,'overlap_bounds_mm':bounds(error.overlap),'pass':False}
            failures.append(row);print(json.dumps(row),flush=True)
            continue
        if abs(received.Volume(tol=1e-9)-physical.Volume(tol=1e-9))>.001:raise ValueError('Received conductor section differs '+name)
        correspondence=compare_lateral(lateral_records(received,route['diameter_mm']/2),
            lateral_records(authored,route['diameter_mm']/2))
        if not correspondence['pass']:raise ValueError('Received conductor lateral recipe differs '+name)
        proof['received_lateral_recipe_correspondence']=correspondence
        if route.get('physical_section_proof'):
            received_members,received_sections=received_member_compound(received,route['diameter_mm'])
            if not received_sections['pass']:raise ValueError('Received physical section receipt differs '+name)
            unmatched=list(enumerate(received_members.Solids()));receipt=[]
            for index,member in enumerate(physical.Solids()):
                matches=[(j,solid)for j,solid in unmatched if compare_lateral(
                    lateral_records(solid,route['diameter_mm']/2),lateral_records(member,route['diameter_mm']/2))['pass']]
                if len(matches)!=1:raise ValueError(f'{name}: expected member{index} has no unique received section')
                received_index,solid=matches[0]
                missing=abs(member.cut(solid,tol=.0001).Volume(tol=1e-9))
                if missing>.001:raise ValueError(f'{name}: received member{index} differs by{missing:g}mm³')
                receipt.append({'expected_member':index,'received_member':received_index,'missing_mm3':missing,'pass':True})
                unmatched=[row for row in unmatched if row[0]!=received_index]
            if unmatched:raise ValueError('Received conductor has extra physical sections '+name)
            proof['received_physical_section_receipt']=received_sections
            proof['received_member_correspondence']=receipt
        cutter_rec=power['clearance_cutters'][key];cutter_path=ROOT/cutter_rec['brep'];cutter_raw=cutter_path.read_bytes()
        if hashlib.sha256(cutter_raw).hexdigest()!=cutter_rec['sha256']:raise ValueError('Changed power cutter '+name)
        input_cutters[key]={'brep':cutter_rec['brep'],'sha256':hashlib.sha256(cutter_raw).hexdigest()}
        cutter=cq.Shape.importBrep(BytesIO(cutter_raw))
        if not cutter.isValid() or len(cutter.Solids())!=1:raise ValueError('Power cutter is not one valid solid '+name)
        containment=[]
        for index,grown in enumerate(clearance.Solids()):
            missing=abs(grown.cut(cutter,tol=.0001).Volume(tol=1e-9));passed=missing<=.001
            row={'member':index,'enlarged_missing_mm3':missing,'pass':passed};containment.append(row)
            if not passed:failures.append({'part':key,'check':'complete1mm radial cutter containment',**row})
        proof['received_clearance_union_checks']=containment
        members[key]=physical;tools[key]=cutter;proofs[key]=proof
        print('power members reconstructed',name,len(physical.Solids()),flush=True)
    names=list(members)
    fluid_air_checks=[]
    from fluid_members import closest_members
    for i,name in enumerate(names):
        shape=members[name];route=power['power_routes'][name.removeprefix('wire-')]
        owners,terminal_witnesses=terminal_approach_members(shape,
            power['ports'][route['from_key']],power['ports'][route['to_key']],route['diameter_mm'])
        proofs[name]['localized_terminal_approach_witnesses']=terminal_witnesses
        for other,obstacle in {**models,**{n:members[n]for n in names[i+1:]}}.items():
            if other==name or not broad(bounds(shape),bounds(obstacle)):continue
            exempt=owners.get(other,set());solids=shape.Solids()
            occupied=cq.Compound.makeCompound([s for j,s in enumerate(solids)if j not in exempt])
            overlap=audit.common(occupied,obstacle);passed=overlap<=.001
            row={'parts':[name,other],'common_mm3':overlap,'pass':passed}
            if exempt:
                terminal=cq.Compound.makeCompound([solids[j]for j in sorted(exempt)])
                row.update(exempt_normal_approach_member_indices=sorted(exempt),
                    nominal_terminal_contact_common_mm3=audit.common(terminal,obstacle))
            checks.append(row)
            if not passed:failures.append(row);print(json.dumps(row),flush=True)
        for other,fluid in fluids.items():
            if not broad(bounds(shape),bounds(fluid),1.):continue
            air,overlap,pairs,closest=closest_members(shape,fluid)
            passed=air>=1.-1e-6 and overlap<=.001
            row={'parts':[name,other],'minimum_air_mm':air if math.isfinite(air)else None,
                'no_member_within_1mm_broad_phase':not math.isfinite(air),'common_mm3':overlap,
                'member_pair_count':pairs,'closest':closest,'pass':passed}
            fluid_air_checks.append(row)
            if not passed:failures.append(row);print(json.dumps(row),flush=True)
        print('power native members checked',name,flush=True)
    source_drift=[p for p,h in sources.items()if sha(ROOT/p)!=h]
    native_drift=[n for n,r in native.items()if sha(ROOT/r['brep'])!=r['sha256']]
    native_drift+=[n for n,r in input_parts.items()if sha(ROOT/r['brep'])!=r['sha256']]
    native_drift+=['clearance-'+n for n,r in input_cutters.items()if sha(ROOT/r['brep'])!=r['sha256']]
    manifest_drift=[p for p,h in manifests.items()if content_sha256(json.loads((ROOT/p).read_bytes()))!=h]
    passed=not failures and not source_drift and not native_drift and not manifest_drift
    report={'pass':passed,'checks':checks,'failures':failures,'source_inputs':sources,
        'native_inputs':native,'received_power_inputs':input_parts,'received_clearance_inputs':input_cutters,'inputs_sha256':raw_bindings,
        'manifest_content_sha256':manifests,'source_drift':source_drift+native_drift,'manifest_drift':manifest_drift,
        'physical_section_proofs':proofs,'route_count':len(members),'full_fluid_air_checks':fluid_air_checks,
        'received_fluid_section_proofs':fluid_proofs,
        'scope':'All19 selected Ø3.2 power/earth paths use exact straight-cylinder and circular-arc members, with continuous full-section tangent seams, no self overlap, and complete1mm radial cutter containment. Every physical member is tested against installed bodies, lever working envelopes, all control regions and other power wires; unrelated fluid paths retain at least1mm air, including full25.4mm occupied chilled sleeves. Only the actual first/last normal straight terminal members may engage their named terminal owner; every other physical section is tested against that owner. Shell recesses are separately checked in final composed stock. This is geometry evidence, not electrical, thermal or wire-bend qualification.'}
    if passed and not args.check:
        for name,shape in members.items():
            rec=power['parts'][name];path=ROOT/rec['brep'];shape.exportBrep(str(path))
            rec['sha256']=sha(path);rec['bounds']=bounds(shape)
            route=power['power_routes'][name.removeprefix('wire-')]
            route['physical_section_proof']=proofs[name]
            route['physical_section_proof']['published_native_sha256']=rec['sha256']
        power['physical_member_gate']={'report':'wiring/power-members-check.json','source_sha256':sources[str(Path(__file__).relative_to(ROOT))],'pass':True}
        (HERE/'power-candidate.json').write_text(json.dumps(power,indent=2)+'\n')
        key=str((HERE/'power-candidate.json').relative_to(ROOT))
        report['inputs_sha256'][key]=sha(HERE/'power-candidate.json')
        report['manifest_content_sha256'][key]=content_sha256(power)
    report['published_power_inputs']={n:power['parts'][n]for n in members}
    report['native_inputs'].update({n:{'brep':r['brep'],'sha256':r['sha256']}
        for n,r in report['published_power_inputs'].items()})
    (HERE/'power-members-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':passed,'routes':len(members),'checks':len(checks),'failures':failures,
        'source_drift':report['source_drift'],'manifest_drift':manifest_drift}),flush=True)

if __name__=='__main__':main()
