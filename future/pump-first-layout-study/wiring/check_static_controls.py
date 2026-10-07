"""Pairwise occupied clearance between the complete counted controls interfaces."""
from pathlib import Path
import hashlib,json,sys
from io import BytesIO
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1];sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import STATIC_JOINTS
from native_harness import broad,bounds
from audit import common
from evidence_binding import content_sha256,manifest_content_sha256

def main():
 source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in [Path(__file__),HERE/'controls_looms.py',STUDY/'audit.py',STUDY/'evidence_binding.py']}
 manifest_inputs={};manifest_content={};parts={}
 for filename,prefix in [('control-reserves.json',''),('control-fanouts-check.json','control-')]:
  path=HERE/filename;raw=path.read_bytes();key=str(path.relative_to(ROOT));manifest_inputs[key]=hashlib.sha256(raw).hexdigest();module=json.loads(raw);manifest_content[key]=content_sha256(module)
  if not module.get('pass'):raise ValueError('Complete native-passed static interface packet required: '+filename)
  parts.update({prefix+name:record for name,record in module['parts'].items()})
 native_inputs={};models={}
 for name,r in parts.items():
  raw=(ROOT/r['brep']).read_bytes()
  native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
  models[name]=cq.Shape.importBrep(BytesIO(raw))
 allowed={frozenset(pair) for pair in STATIC_JOINTS};checks=[];names=list(models);boxes={n:bounds(s) for n,s in models.items()}
 for i,name in enumerate(names):
  for other in names[i+1:]:
   if not broad(boxes[name],boxes[other]):continue
   overlap=common(models[name],models[other]);mate=frozenset([name,other]) in allowed
   checks.append({'parts':[name,other],'common_mm3':overlap,'declared_continuity':mate,'pass':mate or overlap<.001})
 drift=[n for n,r in native_inputs.items() if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
 drift+=[n for n,h in source_inputs.items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
 manifest_drift=[n for n,h in manifest_content.items() if manifest_content_sha256(ROOT/n)!=h]
 report={'parts_count':len(models),'canonical_jobs':71,'required_network_routes':26,'checks':checks,'failures':[r for r in checks if not r['pass']],
  'native_inputs':native_inputs,'source_inputs':source_inputs,'read_time_manifest_sha256':manifest_inputs,'manifest_content_sha256':manifest_content,'source_drift':drift,'manifest_drift':manifest_drift,
  'pass':len(models)==49 and all(r['pass'] for r in checks) and not drift and not manifest_drift,
  'scope':'Exact per-solid fuzzy native intersections between all13 counted fixed service regions and36 published nominal fanout regions. Only named continuous splice interfaces are exempt.'}
 (HERE/'static-controls-pair-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'parts':report['parts_count'],'checks':len(checks),'pass':report['pass'],'failures':report['failures']}),flush=True)
if __name__=='__main__':main()
