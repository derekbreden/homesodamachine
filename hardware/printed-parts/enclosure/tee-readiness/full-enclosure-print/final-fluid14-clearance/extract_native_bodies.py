from pathlib import Path
import os,sys,hashlib,json,time
os.environ['HSM_NO_BUILD_LOCK']='1'
R=Path('/Users/derekbredensteiner/Developer/homesodamachine'); O=Path('/tmp/scanner-review/fluid14-current-aggregate')
sys.path[:0]=[str(R/'hardware/scripts'),str(R/'hardware/manifold-layout')]
from _cadq_export import import_assembly
import _clearing,_boxes
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=R/'hardware/manifold-layout/enclosure-assembly.step';before=sha(P);start=time.monotonic()
print('Reading',before,flush=True)
a=import_assembly(P); print('Loaded',len(a),time.monotonic()-start,flush=True)
records={}
for n,(s,_c) in a.items():
 p=O/(n.replace('/','--')+'.brep');s.exportBrep(str(p)); b=s.BoundingBox()
 records[n]={'brep':p.name,'sha256':sha(p),'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]}
print('Extracted',len(a),flush=True)
report={'assembly_step_sha256':before,'assembly_step':str(P),'bodies':records,'stable_input':sha(P)==before}
(O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
for n in ('valve-v-a','vk-solenoid','coil-v-a'):
 t=a['tube-fluid-14'][0];s=a[n][0]
 print(n,'OCC',t.distance(s),'scorecard_mesh',_clearing.gap(t,s,2),flush=True)
print('DONE',time.monotonic()-start,flush=True)
