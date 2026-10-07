"""Join complete controls and power only after the occupied native pair proof."""
from pathlib import Path
import hashlib,json,sys
from io import BytesIO
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from native_harness import bounds,broad
from audit import common as native_common
from evidence_binding import content_sha256

def main():
 module_bytes={name:(HERE/name).read_bytes()for name in ['controls-candidate.json','power-candidate.json']}
 controls=json.loads(module_bytes['controls-candidate.json'])
 power=json.loads(module_bytes['power-candidate.json'])
 content_bindings={str((HERE/name).relative_to(ROOT)):content_sha256(json.loads(raw))for name,raw in module_bytes.items()}
 source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in [Path(__file__),HERE/'native_harness.py',STUDY/'audit.py',STUDY/'evidence_binding.py']}
 failures=[];coverage=controls.get('coverage',{})
 if not controls.get('pass'):failures.append({'check':'complete native controls module','pass':False})
 if not power.get('pass'):failures.append({'check':'complete native power module','pass':False})
 if coverage.get('completed_routes')!=26 or coverage.get('completed_static_parts')!=49:
  failures.append({'check':'26 grouped controls and49 static occupied regions','coverage':coverage,'pass':False})
 if len(power.get('power_routes',{}))!=19:failures.append({'check':'19 required power/earth routes','actual':len(power.get('power_routes',{})),'pass':False})
 mapped=controls.get('canonical_job_coverage',{})
 jobs=controls.get('jobs',[])
 if len(jobs)!=71 or {j['name'] for j in jobs}!=set(mapped):failures.append({'check':'complete71 canonical control nets','actual_jobs':len(jobs),'actual_mapped':len(mapped),'pass':False})
 parts={};models={};sources={}
 for module in [controls,power]:
  for name,r in module.get('parts',{}).items():
   if name in parts:raise ValueError('Duplicate occupied wiring body '+name)
   path=ROOT/r['brep'];raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
   if digest!=r['sha256']:raise ValueError('Changed occupied wiring body '+name)
   shape=cq.Shape.importBrep(BytesIO(raw))
   if not shape.isValid() or not shape.Solids():failures.append({'check':'valid occupied native exterior','part':name,'pass':False})
   parts[name]=r;models[name]=shape;sources[name]=digest
 for name,record in mapped.items():
  required=record['static_continuations']+([record['grouped_route']] if record['grouped_route'] else [])
  missing=[p for p in required if p not in parts]
  if missing:failures.append({'check':'canonical net occupied continuity','net':name,'missing':missing,'pass':False})
 contacts=[pair for module in [controls,power] for pair in module.get('intended_contacts',[])]
 allowed={frozenset(pair) for pair in contacts};checks=[];boxes={n:bounds(s) for n,s in models.items()};names=list(models)
 for i,name in enumerate(names):
  for other in names[i+1:]:
   if not broad(boxes[name],boxes[other]):continue
   common=native_common(models[name],models[other]);mate=frozenset([name,other]) in allowed
   row={'parts':[name,other],'common_mm3':common,'declared_continuity':mate,'pass':mate or common<.001};checks.append(row)
   if not row['pass']:failures.append(row);print(json.dumps(row),flush=True)
 source_drift=[p for p,h in source_inputs.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
 native_drift=[n for n,h in sources.items()if hashlib.sha256((ROOT/parts[n]['brep']).read_bytes()).hexdigest()!=h]
 manifest_drift=[p for p,h in content_bindings.items()if content_sha256(json.loads((ROOT/p).read_bytes()))!=h]
 if source_drift or native_drift or manifest_drift:failures.append({'check':'stable read-time geometry and producer inputs','source_drift':source_drift,'native_drift':native_drift,'manifest_drift':manifest_drift,'pass':False})
 report={'checks':checks,'failures':failures,'native_geometry_sha256':sources,
  'native_inputs':{n:{'brep':r['brep'],'sha256':sources[n]}for n,r in parts.items()},
  'controls_manifest_sha256':hashlib.sha256(module_bytes['controls-candidate.json']).hexdigest(),
  'power_manifest_sha256':hashlib.sha256(module_bytes['power-candidate.json']).hexdigest(),
  'source_inputs':source_inputs,'manifest_content_sha256':content_bindings,
  'source_drift':source_drift+native_drift,'manifest_drift':manifest_drift,'pass':not failures,
  'scope':'Complete required module counts,71 canonical pin mappings and exact fuzzy native pair intersections of every occupied control/power exterior. Only named physically continuous joins are exempt. Hardware and complete factory assembly remain separately bound by the parent integrated audit.'}
 (HERE/'join-check.json').write_text(json.dumps(report,indent=2)+'\n')
 if failures:print(json.dumps({'pass':False,'parts':len(parts),'failures':len(failures)}),flush=True);return
 cutters={n:r for module in [controls,power] for n,r in module['clearance_cutters'].items()}
 result={'parts':parts,'replacement_names':[],'intended_contacts':contacts,'clearance_cutters':cutters,
  'control_routes':controls['control_routes'],'power_routes':power['power_routes'],'canonical_jobs':jobs,
  'canonical_job_coverage':mapped,'connectors':controls['connectors'],'ports':{'controls':controls['ports'],'power':power['ports']},
  'bench_cut_review':controls['bench_cut_review'],'coverage':{'canonical_control_jobs':71,'grouped_control_routes':26,'fixed_control_sections':13,'nominal_control_fanouts':36,'power_earth_routes':19,'lower_power_exteriors':3},
  'native_pair_report':'wiring/join-check.json','module_sha256':{'controls-candidate.json':report['controls_manifest_sha256'],'power-candidate.json':report['power_manifest_sha256']},
  'manifest_content_sha256':content_bindings,'source_inputs':source_inputs,
  'qualification_limits':list(dict.fromkeys(controls['qualification_limits']+power['qualification_limits'])),
  'source_sha256':{'future/pump-first-layout-study/wiring/compose.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'pass':True}
 (HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':True,'parts':len(parts),'checks':len(checks)}),flush=True)

if __name__=='__main__':main()
