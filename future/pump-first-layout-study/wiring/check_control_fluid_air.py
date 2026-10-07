"""Exact running air between complete controls and full tube/hose/foam exteriors."""
from pathlib import Path
import hashlib,json,sys
from io import BytesIO
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import loaded_digest
from native_harness import broad,bounds
import audit
from evidence_binding import content_sha256,manifest_content_sha256

def main():
 source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in [Path(__file__),HERE/'controls_looms.py',HERE/'native_harness.py',STUDY/'audit.py',STUDY/'evidence_binding.py']}
 manifest_inputs={};manifest_content={}
 for relative in ['wiring/controls-candidate.json','pump/candidate.json','pump/fluid24-candidate.json','routing/candidate.json','routing/tube-hosts.json']:
  p=STUDY/relative
  if p.exists():
   raw=p.read_bytes();key=str(p.relative_to(ROOT));manifest_inputs[key]=hashlib.sha256(raw).hexdigest();manifest_content[key]=content_sha256(json.loads(raw))
 published=json.loads((HERE/'controls-candidate.json').read_text());parts=published.get('parts',{})
 groups=sum('from_dock' in r for r in published.get('control_routes',{}).values());statics=len(parts)-groups
 native_inputs={};controls={}
 for name,r in parts.items():
  raw=(ROOT/r['brep']).read_bytes()
  native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
  controls[name]=cq.Shape.importBrep(BytesIO(raw))
 models,records,_,_,_=audit.collect();fluids={name:s for name,s in models.items() if name.startswith(('tube-','carb-foam-'))}
 for name in fluids:
  r=records[name];raw=(ROOT/r['brep']).read_bytes()
  native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
  fluids[name]=cq.Shape.importBrep(BytesIO(raw))
 rows=[];boxes={name:bounds(s) for name,s in fluids.items()}
 for name,s in controls.items():
  b=bounds(s)
  for fluid,t in fluids.items():
   if not broad(b,boxes[fluid],1.):continue
   gap=s.distance(t);common=audit.common(s,t) if gap<1e-6 else 0.
   rows.append({'control':name,'fluid':fluid,'air_mm':gap,'common_mm3':common,'pass':gap>=1.-1e-6 and common<.001})
 failures=[r for r in rows if not r['pass']]
 drift=[n for n,r in native_inputs.items() if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
 drift+=[n for n,h in source_inputs.items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
 manifest_drift=[n for n,h in manifest_content.items() if manifest_content_sha256(ROOT/n)!=h]
 report={'checks':rows,'failures':failures,'completed_grouped_routes':groups,'required_grouped_routes':26,'counted_static_regions':statics,
  'current_completed_geometry_pass':not failures,'pass':not failures and groups==26 and statics==49 and not drift and not manifest_drift,'input_geometry_sha256':{name:loaded_digest(s) for name,s in {**controls,**fluids}.items()},
  'native_inputs':native_inputs,'source_inputs':source_inputs,'read_time_manifest_sha256':manifest_inputs,'manifest_content_sha256':manifest_content,'source_drift':drift,'manifest_drift':manifest_drift,
  'scope':'Full native tubes, braided hoses and insulation foam require1mm unrelated air to counted control regions. An incomplete set is not a full controls pass. Purchased component terminations remain in the separate named interface/owner scope.'}
 (HERE/'control-fluid-air-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'groups':groups,'static_regions':statics,'current_geometry_pass':not failures,'failures':failures},indent=2),flush=True)
if __name__=='__main__':main()
