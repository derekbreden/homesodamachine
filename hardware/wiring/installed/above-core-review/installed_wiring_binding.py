"""Manual installed-wiring STEP/source binding; run through tmp/takeover/cadq.
No mechanical generation or recurring check.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import enclosure_assembly as ea
from hardware.wiring.installed import build
from _cadq_export import import_assembly
OUT=ROOT/'hardware/wiring/installed/above-core-review/installed-wiring-binding.json'
STEP=ROOT/'hardware/wiring/enclosure-wiring.step';MANIFEST=STEP.with_suffix('.json');EA=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sig(s):
 b=s.BoundingBox()
 return {'valid':s.isValid(),'solids':len(s.Solids()),'faces':len(s.Faces()),'volume_mm3':s.Volume(),'center_mm':s.Center().toTuple(),'bounds_mm':[getattr(b,k)for k in('xmin','ymin','zmin','xmax','ymax','zmax')]}
actual={n.rsplit('/',1)[-1]:s for n,(s,_c)in import_assembly(STEP).items()}
manifest=json.loads(MANIFEST.read_text())
print('Source-only wiring composition',flush=True)
source,expected=build.compose(import_assembly(EA),ea)
native={n:s for n,s,_c in ea.ml.placed_leaves(source)}
record={'schema':1,'units':'mm','scope':'Manual actual installed-wiring STEP/manifest binding to source-native102 conductors and23 termination bodies. No equipment/contact sweep or mechanical regeneration. Unchanged accepted contact receipts remain separately scoped.','actual_step_sha256':sha(STEP),'actual_manifest_sha256':sha(MANIFEST),'physical_EA_sha256':sha(EA),'source_sha256':{str(p.relative_to(ROOT)):sha(p)for p in(Path(build.__file__),ROOT/'hardware/wiring/installed/route-overrides.json',ROOT/'hardware/manifold-layout/above-core.json')},'source_body_count':len(native),'actual_body_count':len(actual),'missing':sorted(set(native)-set(actual)),'extra':sorted(set(actual)-set(native)),'bodies':{}}
def numbers(x):
 if isinstance(x,dict):return sum((numbers(v)for v in x.values()),[])
 if isinstance(x,(tuple,list)):return sum((numbers(v)for v in x),[])
 return [x]if isinstance(x,(int,float))else[]
expected_routes={r['id']:r for r in expected['routes']};actual_routes={r['id']:r for r in manifest['routes']}
record['source_curve_comparisons']={}
for n,r in expected_routes.items():
 a=numbers(r['segments']);b=numbers(actual_routes[n]['segments'])
 record['source_curve_comparisons'][n]={'numeric_count_equal':len(a)==len(b),'maximum_numeric_delta_mm':max((abs(x-y)for x,y in zip(a,b)),default=0.),'source_curve_sha256':hashlib.sha256(json.dumps(r['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'manifest_curve_sha256':hashlib.sha256(json.dumps(actual_routes[n]['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest()}
for n,s in native.items():
 a=sig(s);b=sig(actual[n])
 record['bodies'][n]={'source':a,'actual_readback':b,'absolute_deltas':{'volume_mm3':abs(a['volume_mm3']-b['volume_mm3']),'center_mm':max(abs(x-y)for x,y in zip(a['center_mm'],b['center_mm'])),'bounds_mm':max(abs(x-y)for x,y in zip(a['bounds_mm'],b['bounds_mm']))}}
record['source_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['source']['valid']]
record['actual_readback_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['actual_readback']['valid']]
record['maximum_volume_delta_mm3']=max(r['absolute_deltas']['volume_mm3']for r in record['bodies'].values())
record['maximum_bounds_delta_mm']=max(r['absolute_deltas']['bounds_mm']for r in record['bodies'].values())
record['all_102_source_curves_match']=len(record['source_curve_comparisons'])==102 and all(r['numeric_count_equal']and r['maximum_numeric_delta_mm']<1e-9 for r in record['source_curve_comparisons'].values())
record['all_125_native_shapes_bound']=len(native)==len(actual)==125 and not record['missing']and not record['extra']and not record['source_invalid_bodies']and all(r['absolute_deltas']['bounds_mm']<1e-5 and r['absolute_deltas']['center_mm']<1e-5 and r['absolute_deltas']['volume_mm3']<.001 for r in record['bodies'].values())
record['exchange_scope']='Native source solids and geometric agreement are distinct from STEP reader orientation validity. Any listed readback-invalid bodies retain their explicit exchange limitation; no per-wire geometry is altered to silence it.'
OUT.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k]for k in('source_body_count','actual_body_count','source_invalid_bodies','actual_readback_invalid_bodies','maximum_volume_delta_mm3','maximum_bounds_delta_mm','all_102_source_curves_match','all_125_native_shapes_bound')},indent=2),flush=True)
