"""Manual installed-wiring STEP/source binding; run through tmp/takeover/cadq.
No mechanical generation or recurring check.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import enclosure_assembly as ea
from hardware.wiring.installed import build
from _cadq_export import import_assembly
OUT=ROOT/'hardware/wiring/installed/above-core-review/installed-wiring-binding.json'
STEP=ROOT/'hardware/wiring/enclosure-wiring.step';MANIFEST=STEP.with_suffix('.json');EA=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-cache',type=Path,help='Optional explicitly bound native signatures/curves, avoiding unchanged source sweeps.')
args=parser.parse_args()
def sig(s):
 b=s.BoundingBox()
 return {'valid':s.isValid(),'solids':len(s.Solids()),'faces':len(s.Faces()),'volume_mm3':s.Volume(),'center_mm':s.Center().toTuple(),'bounds_mm':[getattr(b,k)for k in('xmin','ymin','zmin','xmax','ymax','zmax')]}
actual={n.rsplit('/',1)[-1]:s for n,(s,_c)in import_assembly(STEP).items()}
manifest=json.loads(MANIFEST.read_text())
cache_errors=[]
if args.source_cache:
    from hardware.wiring.installed.connections import connections
    from hardware.wiring.installed.routes import routed
    from hardware.wiring.installed.terminals import Attachments
    cache=json.loads(args.source_cache.read_text())
    print('Resolve source curves; reuse explicitly bound native signatures',flush=True)
    attachments=Attachments(import_assembly(EA),ea)
    attachments.resolve()
    expected={'routes':[r.record() for r in routed(connections(),attachments)]}
    native_signatures={n:r['signature'] for n,r in cache['bodies'].items()}
    for n,row in cache['bodies'].items():
        path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
        if sha(path)!=row['sha256']:cache_errors.append('Native cache hash differs: '+n)
else:
    print('Source-only wiring composition',flush=True)
    source,expected=build.compose(import_assembly(EA),ea)
    native_signatures={n:sig(s) for n,s,_c in ea.ml.placed_leaves(source)}
record={'schema':2,'units':'mm','scope':'Manual actual installed-wiring STEP/manifest binding to the current source electrical graph and native wiring bodies. No equipment/contact sweep or mechanical regeneration. Unchanged accepted contact receipts remain separately scoped.','actual_step_sha256':sha(STEP),'actual_manifest_sha256':sha(MANIFEST),'physical_EA_sha256':sha(EA),'source_sha256':{str(p.relative_to(ROOT)):sha(p)for p in(Path(build.__file__),ROOT/'hardware/wiring/installed/route-overrides.json',ROOT/'hardware/manifold-layout/above-core.json')},'source_body_count':len(native_signatures),'actual_body_count':len(actual),'missing':sorted(set(native_signatures)-set(actual)),'extra':sorted(set(actual)-set(native_signatures)),'bodies':{}}
def numbers(x):
 if isinstance(x,dict):return sum((numbers(v)for v in x.values()),[])
 if isinstance(x,(tuple,list)):return sum((numbers(v)for v in x),[])
 return [x]if isinstance(x,(int,float))else[]
def metadata_delta(a,b):
 if isinstance(a,dict) and isinstance(b,dict) and set(a)==set(b):
  values=[metadata_delta(a[k],b[k])for k in a]
 elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)) and len(a)==len(b):
  values=[metadata_delta(x,y)for x,y in zip(a,b)]
 elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
  return abs(a-b)
 else:return 0. if a==b else None
 return None if any(v is None for v in values)else max(values,default=0.)
expected_routes={r['id']:r for r in expected['routes']};actual_routes={r['id']:r for r in manifest['routes']}
record['source_route_count']=len(expected_routes)
record['actual_route_count']=len(actual_routes)
record['manifest_connection_count']=manifest['connection_count']
record['graph_body_count']=len(expected_routes)+len(manifest['terminations'])+sum(bool(b.get('geometry_name'))for b in manifest['bundles'].values())
record['missing_routes']=sorted(set(expected_routes)-set(actual_routes))
record['extra_routes']=sorted(set(actual_routes)-set(expected_routes))
if args.source_cache:
    comparisons={}
    if set(cache['routes'])!=set(expected_routes):
        cache_errors.append('Native cache route IDs differ from the current graph')
    for n,r in expected_routes.items():
        if n not in cache['routes']:continue
        a=numbers(r['segments']);b=numbers(cache['routes'][n]['segments'])
        comparisons[n]={'numeric_count_equal':len(a)==len(b),'maximum_numeric_delta_mm':max((abs(x-y)for x,y in zip(a,b)),default=0.)}
        if len(a)!=len(b) or comparisons[n]['maximum_numeric_delta_mm']>1e-7:
            cache_errors.append('Source curve differs from native cache: '+n)
    termination_delta=metadata_delta(manifest['terminations'],cache['terminations'])
    if termination_delta is None or termination_delta>1e-7:
        cache_errors.append('Termination metadata differs from bound cache')
    jacket_comparisons={}
    for n,row in cache['jackets'].items():
        actual_jacket={k:manifest['bundles'][n][k] for k in row}
        jacket_comparisons[n]=metadata_delta(actual_jacket,row)
        if jacket_comparisons[n]is None or jacket_comparisons[n]>1e-7:cache_errors.append('Jacket geometry differs from bound cache: '+n)
    record['native_source_cache']={'path':str(args.source_cache),'sha256':sha(args.source_cache),'proofs':cache['proofs'],'source_curve_comparisons':comparisons,'termination_metadata_maximum_delta_mm':termination_delta,'jacket_geometry_maximum_delta_mm':jacket_comparisons,'errors':cache_errors,'scope':'Reuse unchanged native source solids only after matching current source curves, termination records and jacket geometry. All actual STEP wiring bodies are read back in this command.'}
record['source_curve_comparisons']={}
for n,r in expected_routes.items():
 if n not in actual_routes:continue
 a=numbers(r['segments']);b=numbers(actual_routes[n]['segments'])
 record['source_curve_comparisons'][n]={'numeric_count_equal':len(a)==len(b),'maximum_numeric_delta_mm':max((abs(x-y)for x,y in zip(a,b)),default=0.),'source_curve_sha256':hashlib.sha256(json.dumps(r['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'manifest_curve_sha256':hashlib.sha256(json.dumps(actual_routes[n]['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest()}
for n,a in native_signatures.items():
    if n not in actual:continue
    b=sig(actual[n])
    record['bodies'][n]={'source':a,'actual_readback':b,'absolute_deltas':{'volume_mm3':abs(a['volume_mm3']-b['volume_mm3']),'center_mm':max(abs(x-y)for x,y in zip(a['center_mm'],b['center_mm'])),'bounds_mm':max(abs(x-y)for x,y in zip(a['bounds_mm'],b['bounds_mm']))}}
record['source_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['source']['valid']]
record['actual_readback_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['actual_readback']['valid']]
record['maximum_volume_delta_mm3']=max(r['absolute_deltas']['volume_mm3']for r in record['bodies'].values())
record['maximum_bounds_delta_mm']=max(r['absolute_deltas']['bounds_mm']for r in record['bodies'].values())
record['all_source_curves_match']=not record['missing_routes'] and not record['extra_routes'] and len(record['source_curve_comparisons'])==len(expected_routes)==manifest['connection_count'] and all(r['numeric_count_equal']and r['maximum_numeric_delta_mm']<1e-9 for r in record['source_curve_comparisons'].values())
record['all_native_shapes_bound']=bool(native_signatures) and len(native_signatures)==len(actual)==record['graph_body_count'] and not cache_errors and not record['missing']and not record['extra']and not record['source_invalid_bodies']and all(r['absolute_deltas']['bounds_mm']<1e-5 and r['absolute_deltas']['center_mm']<1e-5 and r['absolute_deltas']['volume_mm3']<.001 for r in record['bodies'].values())
record['exchange_scope']='Native source solids and geometric agreement are distinct from STEP reader orientation validity. Any listed readback-invalid bodies retain their explicit exchange limitation; no per-wire geometry is altered to silence it.'
OUT.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k]for k in('source_body_count','actual_body_count','source_invalid_bodies','actual_readback_invalid_bodies','maximum_volume_delta_mm3','maximum_bounds_delta_mm','all_source_curves_match','all_native_shapes_bound')},indent=2),flush=True)
