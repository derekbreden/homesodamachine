"""Rebuild only the authored manifold transition and its clearance envelope.

All other control natives are received byte-for-byte. The complete control and
parent-dependent receipts are refreshed after the selected shell is rebuilt.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
import audit,baseline
from controls_looms import manifold_transition,clearance_envelope
from received_cutters import correspondence
from evidence_binding import content_sha256

NAME='control-manifold-aft-fanout'

def main():
    path=HERE/'controls-candidate.json';old_bytes=path.read_bytes();packet=json.loads(old_bytes)
    if len(packet['parts'])!=75 or len(packet['clearance_cutters'])!=75:raise ValueError('Complete received control packet required')
    held={}
    for name,part in packet['parts'].items():
        for kind,record in [('body',part),('cutter',packet['clearance_cutters'][name])]:
            p=ROOT/record['brep'];raw=p.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Changed received native: '+name+' '+kind)
            held[(name,kind)]=(p,raw)
    source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in
        [Path(__file__),HERE/'controls_looms.py',HERE/'received_cutters.py',STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    models,records,_,mates,inputs=audit.collect();native_inputs={}
    for name,record in records.items():
        if name not in models:continue
        raw=(ROOT/record['brep']).read_bytes();models[name]=cq.Shape.importBrep(BytesIO(raw))
        native_inputs[name]={'brep':record['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
    saved=baseline.prepare()
    for name,record in saved['parts'].items():
        if name in models or not audit.broad(record['bounds'],[88,324,240,105,466,289],pad=1):continue
        p=baseline.CACHE/record['file'];raw=p.read_bytes();models[name]=cq.Shape.importBrep(BytesIO(raw))
        native_inputs[name]={'brep':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
    body,docks,route=manifold_transition();cutter=clearance_envelope(body,fused_union=route['clearance_fused_union'])
    checks=[];box=audit.bbox(body)
    for name,model in models.items():
        if name==NAME or not audit.broad(box,audit.bbox(model),pad=.0001):continue
        common=sum(audit.common(a,b)for a in body.Solids()for b in model.Solids())
        declared=frozenset([NAME,name])in mates
        checks.append({'part':name,'common_mm3':common,'declared_continuity':declared,'pass':declared or common<.001})
    for name,model in models.items():
        if not name.startswith(('tube-fluid-','tube-water-','tube-co2-','tube-carb-','carb-foam-')):continue
        if not audit.broad(box,audit.bbox(model),pad=1.):continue
        air=body.distance(model);checks.append({'part':name,'fluid_air_mm':air,'pass':air>=.9999})
    lower=models['enclosure-back-top'].copy(mesh=False).intersect(cq.Solid.makeBox(240,520,253.4,cq.Vector(-120,0,0)),tol=.0001)
    lower_common=sum(audit.common(a,b)for a in body.Solids()for b in lower.Solids())
    lower_air=body.distance(lower);core_air=body.distance(models['cold-core/foam-cap-top'])
    checks.append({'part':'protected lower-back stock','common_mm3':lower_common,'nominal_air_mm':lower_air,'pass':lower_common<.001})
    checks.append({'part':'retained cold-core cap','nominal_air_mm':core_air,'pass':core_air>0})
    proof=correspondence(body,cutter,route);checks.append({'check':'complete clearance correspondence',**proof})
    for index,solid in enumerate(body.Solids()):
        missing=abs(solid.copy(mesh=False).cut(cutter.copy(mesh=False),tol=.0001).Volume(tol=1e-9))
        checks.append({'check':'occupied member contained in its enlarged cutter','member':index,'missing_mm3':missing,'pass':missing<.001})
    checks.append({'check':'both aft connection mouths held','mouths':docks,'pass':docks['J1']['point']==[100.3,460.2,284.] and docks['J2']['point']==[94.7,460.2,276.5]})
    source_drift=[p for p,h in source_inputs.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    native_drift=[n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    manifest_drift=[p for p,h in inputs.content_sha256.items()if content_sha256(json.loads((ROOT/p).read_bytes()))!=h]
    if source_drift or native_drift or manifest_drift or not all(r['pass']for r in checks):
        raise ValueError(json.dumps({'checks':[r for r in checks if not r['pass']],'source_drift':source_drift,'native_drift':native_drift,'manifest_drift':manifest_drift}))
    body_path=held[(NAME,'body')][0];cutter_path=held[(NAME,'cutter')][0]
    body.exportBrep(str(body_path));cutter.exportBrep(str(cutter_path))
    part=packet['parts'][NAME];part.update(sha256=hashlib.sha256(body_path.read_bytes()).hexdigest(),bounds=audit.bbox(body),detail=route['scope'])
    packet['clearance_cutters'][NAME]['sha256']=hashlib.sha256(cutter_path.read_bytes()).hexdigest()
    route.update(native_interferences=[],hardware_interferences=[]);packet['control_routes'][NAME]=route
    packet['pass']=False;packet['publication_status']='Selected single-static geometry published; parent-bound control receipts await no-change refresh.'
    vertices,triangles=body.tessellate(.15,.10)
    (ROOT/part['mesh']).write_text(json.dumps({'vertices':[[v.x,v.y,v.z]for v in vertices],'triangles':[list(t)for t in triangles]},separators=(',',':'))+'\n')
    body_path.with_suffix('.route.json').write_text(json.dumps({'part':part,'record':route},indent=2)+'\n')
    path.write_text(json.dumps(packet,indent=2)+'\n')
    merged_path=HERE/'candidate.json';merged=json.loads(merged_path.read_text())
    merged['parts'][NAME]=part;merged['clearance_cutters'][NAME]=packet['clearance_cutters'][NAME];merged['control_routes'][NAME]=route
    merged['pass']=False;merged['publication_status']=packet['publication_status'];merged_path.write_text(json.dumps(merged,indent=2)+'\n')
    interface_path=HERE/'controls-loom-interfaces.json';interface=json.loads(interface_path.read_text());interface['service_sections'][NAME]=route
    interface_path.write_text(json.dumps(interface,indent=2)+'\n')
    reserve_path=HERE/'control-reserves.json';reserve=json.loads(reserve_path.read_text());reserve['parts'][NAME].update(brep=part['brep'],sha256=part['sha256'],bounds=part['bounds'],detail=part['detail'])
    reserve['pass']=False;reserve['publication_status']=packet['publication_status'];reserve_path.write_text(json.dumps(reserve,indent=2)+'\n')
    byte_checks=[]
    for (name,kind),(p,raw)in held.items():
        if name==NAME:continue
        unchanged=p.read_bytes()==raw;byte_checks.append({'part':name,'kind':kind,'sha256':hashlib.sha256(raw).hexdigest(),'pass':unchanged})
    native_inputs.pop(NAME,None)
    final_contents={p:content_sha256(json.loads((ROOT/p).read_bytes()))for p in inputs.content_sha256}
    report={'part':NAME,'checks':checks,'held_native_checks':byte_checks,'native_inputs':native_inputs,
        'source_inputs':source_inputs,'manifest_content_sha256':final_contents,'source_drift':source_drift,
        'manifest_drift':manifest_drift,'published_native_inputs':{'body':{'brep':str(body_path.relative_to(ROOT)),'sha256':part['sha256']},
        'cutter':{'brep':str(cutter_path.relative_to(ROOT)),'sha256':packet['clearance_cutters'][NAME]['sha256']}},
        'old_native_sha256':{kind:hashlib.sha256(held[(NAME,kind)][1]).hexdigest()for kind in ['body','cutter']},
        'pass':all(r['pass']for r in checks+byte_checks),'scope':'The authored 11-conductor ribbon retains its full section, both actual aft mouths, named continuity and every other148 control native bytes. Nominal occupied fit is checked against complete received hardware, electrical peers and retained lower stock. It does not qualify printing tolerance, insulation, individual conductor dressing or lifetime.'}
    (HERE/'manifold-transition-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':len(checks),'held_native_files':len(byte_checks),'lower_back_air_mm':lower_air,'core_air_mm':core_air,'body_sha256':part['sha256'],'cutter_sha256':packet['clearance_cutters'][NAME]['sha256']},indent=2),flush=True)

if __name__=='__main__':main()
