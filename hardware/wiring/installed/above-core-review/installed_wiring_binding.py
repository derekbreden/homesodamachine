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
parser.add_argument('--update-routing-review',action='store_true',help='Bind existing mesh witnesses and their scoped native resolutions; do not rerun contacts or packing.')
args=parser.parse_args()
def sig(s):
 b=s.BoundingBox()
 return {'valid':s.isValid(),'solids':len(s.Solids()),'faces':len(s.Faces()),'volume_mm3':s.Volume(),'center_mm':s.Center().toTuple(),'bounds_mm':[getattr(b,k)for k in('xmin','ymin','zmin','xmax','ymax','zmax')]}
actual={n.rsplit('/',1)[-1]:s for n,(s,_c)in import_assembly(STEP).items()}
assembly=import_assembly(EA)
installed={n.rsplit('/',1)[-1]:s for n,(s,_c)in assembly.items()if n.rsplit('/',1)[-1]in actual}
manifest=json.loads(MANIFEST.read_text())
cache_errors=[]
if args.source_cache:
    from hardware.wiring.installed.connections import connections
    from hardware.wiring.installed.routes import routed
    from hardware.wiring.installed.terminals import Attachments
    cache=json.loads(args.source_cache.read_text())
    print('Resolve source curves; reuse explicitly bound native signatures',flush=True)
    attachments=Attachments(assembly,ea)
    attachments.resolve()
    expected={'routes':[r.record() for r in routed(connections(),attachments)]}
    native_signatures={n:r['signature'] for n,r in cache['bodies'].items()}
    for name,want in cache.get('generator_sha256',{}).items():
        if sha(ROOT/name)!=want:cache_errors.append('Native source generator differs: '+name)
    for n,row in cache['bodies'].items():
        path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
        if sha(path)!=row['sha256']:cache_errors.append('Native cache hash differs: '+n)
else:
    print('Source-only wiring composition',flush=True)
    source,expected=build.compose(assembly,ea)
    native_signatures={n:sig(s) for n,s,_c in ea.ml.placed_leaves(source)}
record={'schema':2,'units':'mm','scope':'Manual actual installed-wiring STEP/manifest binding to the current source electrical graph and native wiring bodies, including their placements inside the complete appliance STEP. No equipment/contact sweep or mechanical regeneration. Unchanged accepted contact receipts remain separately scoped.','reader_sha256':sha(Path(__file__)),'actual_step_sha256':sha(STEP),'actual_manifest_sha256':sha(MANIFEST),'physical_EA_sha256':sha(EA),'source_sha256':{str(p.relative_to(ROOT)):sha(p)for p in(Path(build.__file__),ROOT/'hardware/wiring/installed/route-overrides.json',ROOT/'hardware/manifold-layout/above-core.json')},'source_body_count':len(native_signatures),'actual_body_count':len(actual),'installed_body_count':len(installed),'installed_missing':sorted(set(actual)-set(installed)),'missing':sorted(set(native_signatures)-set(actual)),'extra':sorted(set(actual)-set(native_signatures)),'bodies':{}}
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
    record['native_source_cache']={'path':str(args.source_cache),'sha256':sha(args.source_cache),'proofs':cache['proofs'],'generator_sha256':cache.get('generator_sha256',{}),'body_sha256':{n:r['sha256']for n,r in cache['bodies'].items()},'source_curve_comparisons':comparisons,'termination_metadata_maximum_delta_mm':termination_delta,'jacket_geometry_maximum_delta_mm':jacket_comparisons,'errors':cache_errors,'scope':'Reuse unchanged native source solids only after matching current source curves, termination records and jacket geometry. All actual STEP wiring bodies are read back in this command.'}
record['source_curve_comparisons']={}
for n,r in expected_routes.items():
 if n not in actual_routes:continue
 a=numbers(r['segments']);b=numbers(actual_routes[n]['segments'])
 record['source_curve_comparisons'][n]={'numeric_count_equal':len(a)==len(b),'maximum_numeric_delta_mm':max((abs(x-y)for x,y in zip(a,b)),default=0.),'source_curve_sha256':hashlib.sha256(json.dumps(r['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'manifest_curve_sha256':hashlib.sha256(json.dumps(actual_routes[n]['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest()}
for n,a in native_signatures.items():
    if n not in actual:continue
    b=sig(actual[n])
    record['bodies'][n]={'source':a,'actual_readback':b,'absolute_deltas':{'volume_mm3':abs(a['volume_mm3']-b['volume_mm3']),'center_mm':max(abs(x-y)for x,y in zip(a['center_mm'],b['center_mm'])),'bounds_mm':max(abs(x-y)for x,y in zip(a['bounds_mm'],b['bounds_mm']))}}
    if n in installed:
        c=sig(installed[n])
        record['bodies'][n]['installed_readback']=c
        record['bodies'][n]['installed_vs_standalone_deltas']={'volume_mm3':abs(b['volume_mm3']-c['volume_mm3']),'center_mm':max(abs(x-y)for x,y in zip(b['center_mm'],c['center_mm'])),'bounds_mm':max(abs(x-y)for x,y in zip(b['bounds_mm'],c['bounds_mm']))}
record['source_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['source']['valid']]
record['actual_readback_invalid_bodies']=[n for n,r in record['bodies'].items()if not r['actual_readback']['valid']]
record['installed_readback_invalid_bodies']=[n for n,r in record['bodies'].items()if 'installed_readback'in r and not r['installed_readback']['valid']]
record['maximum_volume_delta_mm3']=max(r['absolute_deltas']['volume_mm3']for r in record['bodies'].values())
record['maximum_bounds_delta_mm']=max(r['absolute_deltas']['bounds_mm']for r in record['bodies'].values())
record['all_source_curves_match']=not record['missing_routes'] and not record['extra_routes'] and len(record['source_curve_comparisons'])==len(expected_routes)==manifest['connection_count'] and all(r['numeric_count_equal']and r['maximum_numeric_delta_mm']<1e-9 for r in record['source_curve_comparisons'].values())
record['maximum_installed_bounds_delta_mm']=max((r['installed_vs_standalone_deltas']['bounds_mm']for r in record['bodies'].values()if 'installed_vs_standalone_deltas'in r),default=None)
record['all_native_shapes_bound']=bool(native_signatures) and len(native_signatures)==len(actual)==len(installed)==record['graph_body_count'] and not cache_errors and not record['missing']and not record['extra']and not record['installed_missing']and not record['source_invalid_bodies']and all(r['absolute_deltas']['bounds_mm']<1e-5 and r['absolute_deltas']['center_mm']<1e-5 and r['absolute_deltas']['volume_mm3']<.001 and r['installed_vs_standalone_deltas']['bounds_mm']<1e-5 and r['installed_vs_standalone_deltas']['center_mm']<1e-5 and r['installed_vs_standalone_deltas']['volume_mm3']<.001 for r in record['bodies'].values())
record['exchange_scope']='Native source solids and geometric agreement are distinct from STEP reader orientation validity. Any listed readback-invalid bodies retain their explicit exchange limitation; no per-wire geometry is altered to silence it.'
OUT.write_text(json.dumps(record,indent=2)+'\n')
if args.update_routing_review:
    review_path=ROOT/'hardware/wiring/installed/routing-review.json'
    review=json.loads(review_path.read_text())
    witness_path=OUT.with_name('routing-witness-native-review.json')
    witness=json.loads(witness_path.read_text())
    bound=record['all_source_curves_match']and record['all_native_shapes_bound']
    artifact_binding={'scope':'Actual wire-body and source-curve binding only. The contact subsets retain their named fixtures and query scopes; no equipment or packing query is repeated.','readback_record':{'path':str(OUT.relative_to(ROOT)),'sha256':sha(OUT)},'assembly_step_sha256':record['physical_EA_sha256'],'wiring_step_sha256':record['actual_step_sha256'],'manifest_sha256':record['actual_manifest_sha256'],'all_source_curves_match':record['all_source_curves_match'],'all_native_shapes_bound':record['all_native_shapes_bound']}
    ground_path=OUT.with_name('ground-j2-wiring-review.json')
    ground=json.loads(ground_path.read_text())
    ground['actual_export_binding_pending']=not bound
    ground['current_artifact_binding']=artifact_binding
    ground_path.write_text(json.dumps(ground,indent=2)+'\n')
    witness['current_artifact_binding']=artifact_binding
    if 'J2_OUT3_pump_correction'in witness:
        witness['J2_OUT3_pump_correction']['actual_export_binding_pending']=not bound
    witness_path.write_text(json.dumps(witness,indent=2)+'\n')
    a_path=ROOT/'hardware/mechanical-qualification/enclosure-above-core/reservoir-a-route-review.json'
    a_review=json.loads(a_path.read_text())['current_free_curves']
    def evidence(path,pointer):
        value=json.loads(path.read_text())
        for key in pointer.strip('/').split('/'):
            if key:value=value[int(key)]if isinstance(value,list)else value[key]
        return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'json_pointer':pointer,'canonical_json_sha256':hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    def canonical(name):
        bits=name.removeprefix('cold-core/').split('/')
        return '/'.join(bits[:-1])if bits[-1].isdigit()else '/'.join(bits)
    dispositions=[]
    for index,pair in enumerate(review['physical_interference_pairs']):
        wire,part=pair['wire'],canonical(pair['part'])
        row={'mesh_pair_index':index,'wire':wire,'part':pair['part']}
        if part in ('tube-fluid-14','tube-fluid-16'):
            row.update(status='addressed_by_scoped_native_route_and_wire_receipts',evidence=evidence(a_path,'/current_free_curves'),tube_brep_sha256=a_review['native_exports'][part[5:]]['brep_sha256'])
        elif wire=='DC3-negative'and part=='foam-cap-lid-top':
            row.update(status='addressed_by_local_native_wire_correction',evidence=evidence(witness_path,'/DC3_negative_correction'))
        elif wire=='J2-OUT3'and part=='g-ganen-pump':
            if witness.get('J2_OUT3_pump_correction',{}).get('geometrically_clear_in_changed_scope'):
                row.update(status='addressed_by_local_native_wire_correction',evidence=evidence(witness_path,'/J2_OUT3_pump_correction'))
            else:row.update(status='unresolved_positive_pump_subsolid_reading',evidence=evidence(witness_path,'/pairs/0'))
        else:
            matches=[(i,p)for i,p in enumerate(witness['pairs'])if p['wire']==wire and p['part']==part]
            if len(matches)==1 and matches[0][1]['raw_common_mm3']==0 and not matches[0][1].get('positive_subsolid_contacts'):
                i,native=matches[0]
                row.update(status='native_zero_mesh_witness',native_reading_mm3=native['raw_common_mm3'],evidence=evidence(witness_path,'/pairs/'+str(i)),endpoint_scope='Raw native common is zero; no new mask or body exclusion is used.')
            else:row['status']='unresolved_mesh_witness'
        dispositions.append(row)
    bundle_dispositions=[]
    for index,pair in enumerate(review['bundle_interference_pairs']):
        row={'mesh_pair_index':index,'bundle':pair['bundle'],'part':pair['part']}
        if canonical(pair['part'])in('tube-fluid-14','tube-fluid-16'):
            row.update(status='addressed_by_scoped_native_route_receipt',evidence=evidence(a_path,'/current_free_curves'))
        else:row['status']='unresolved_mesh_witness'
        bundle_dispositions.append(row)
    review['scope']='The mesh and packing fields describe only their explicit artifact hashes. The separate current_artifact_binding records actual wiring readback and scoped native resolutions of the listed witnesses; it does not rerun the mesh scene, contacts or wire packing.'
    review['current_artifact_binding']={
        'scope':'Actual current wiring/manifest readback plus scoped dispositions of the recorded mesh witnesses. Equipment receipts keep their named geometry and query scopes. This is not a new whole-scene contact, packing, closing-motion or physical harness qualification.',
        'readback_record':{'path':str(OUT.relative_to(ROOT)),'sha256':sha(OUT)},
        'assembly_step_sha256':record['physical_EA_sha256'],
        'wiring_step_sha256':record['actual_step_sha256'],
        'manifest_sha256':record['actual_manifest_sha256'],
        'mesh_snapshot_is_current':review['assembly_step_sha256']==record['physical_EA_sha256']and review['manifest_sha256']==record['actual_manifest_sha256'],
        'native_snapshot_is_current':review.get('native',{}).get('wiring_step_sha256')==record['actual_step_sha256'],
        'source_route_count':record['source_route_count'],'actual_body_count':record['actual_body_count'],
        'status':'bound'if record['all_source_curves_match']and record['all_native_shapes_bound']else'binding_incomplete',
        'all_source_curves_match':record['all_source_curves_match'],'all_native_shapes_bound':record['all_native_shapes_bound'],
        'source_invalid_bodies':record['source_invalid_bodies'],'actual_readback_invalid_bodies':record['actual_readback_invalid_bodies'],'installed_readback_invalid_bodies':record['installed_readback_invalid_bodies'],
        'exchange_scope':record['exchange_scope'],
        'physical_pair_dispositions':dispositions,'bundle_pair_dispositions':bundle_dispositions,
        'unresolved_recorded_witnesses':[r for r in dispositions+bundle_dispositions if r['status'].startswith('unresolved')],
        'wire_packing_scope':'The original mesh packing rows and original native bundle readings retain their own artifact scope. No current wire-packing or flexible handling claim is added by this binding.'}
    review_path.write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({k:record[k]for k in('source_body_count','actual_body_count','source_invalid_bodies','actual_readback_invalid_bodies','maximum_volume_delta_mm3','maximum_bounds_delta_mm','all_source_curves_match','all_native_shapes_bound')},indent=2),flush=True)
