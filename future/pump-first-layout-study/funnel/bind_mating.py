"""Bind the selected receiver evidence to the final relieved frame."""
from pathlib import Path
import hashlib,json
import cadquery as cq
from frame_stock import selected_frame
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
manifest=json.loads((HERE/'candidate.json').read_text());mating=json.loads((HERE/'mating.json').read_text())
frame,frame_record=selected_frame(manifest);frame_path=ROOT/frame_record['brep'];checks=[]
for name in ['front-receivers','back-receivers']:
 r=mating['interfaces'][name];shape=cq.Shape.importBrep(str(ROOT/r['brep']));common=abs(frame.intersect(shape,tol=.0001).Volume(tol=1e-9))
 checks.append({'test':'selected relieved frame versus '+name,'common_mm3':common,'gap_mm':frame.distance(shape),'pass':common<.001})
checks.extend(manifest['underframe_reliefs']['checks'])
bound={'frame_brep':str(frame_path.relative_to(ROOT)),'frame_sha256':hashlib.sha256(frame_path.read_bytes()).hexdigest(),
 'interfaces_sha256':{r['brep']:hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest() for r in mating['interfaces'].values()},
 'checks':checks,'pass':all(c['pass'] for c in checks),'scope':'Seated native frame/receiver clearance and unchanged rail roots/brim bearing, bound to the selected relieved frame. Full populated back-top motion is qualified by the integrated factory audit.'}
(HERE/'mating-final-frame.json').write_text(json.dumps(bound,indent=2)+'\n')
mating['selected_frame_binding']=bound;(HERE/'mating.json').write_text(json.dumps(mating,indent=2)+'\n')
assert bound['pass'],checks
print(json.dumps(bound,indent=2),flush=True)
