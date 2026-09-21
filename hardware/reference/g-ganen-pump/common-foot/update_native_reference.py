"""Replace exactly four purchased feet, retaining every rigid native component.

This bounded updater reads the frozen predecessor B-reps. It does not refit scans
or reduce the rigid envelopes. A normal detailed regeneration uses the same
unchanged rigid parameters/functions and the common-foot module.
"""
from pathlib import Path
import ast
import hashlib
import json
import struct
import sys
import time

import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent
REF=HERE.parent
ROOT=REF.parents[2]
ENV=REF/'integration-envelope'
PRIOR=HERE/'prior-evidence'
CACHE=ROOT/'.cache/g-ganen-common-foot'
sys.path.insert(0,str(HERE))
from g_ganen_foot import observed_foot, build_foot, parameters as foot_parameters


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,value): p.write_text(json.dumps(value,indent=2)+'\n')
def bounds(s):
 b=s.BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def volume(s): return s.Volume()
def vertices(s):
 a=np.unique(np.round([v.toTuple() for v in s.Vertices()],7),axis=0)
 return a[np.lexsort((a[:,2],a[:,1],a[:,0]))]
def mapped(path,rows):
 remaining=list(cq.importers.importStep(str(path)).val().Solids());out={}
 for row in rows:
  found=[s for s in remaining if np.allclose(bounds(s),row['bounds_mm'],atol=1e-5,rtol=0)]
  if len(found)!=1:raise ValueError('Native identification is not unique: '+row['name'])
  out[row['name']]=found[0];remaining.remove(found[0])
 if remaining:raise ValueError('Unidentified native solids')
 return out

def export_and_check(kind,parts,path):
 sys.path.insert(0,str(ROOT/'hardware/scripts'))
 from _cadq_export import export_assembly
 assembly=cq.Assembly(name=path.stem)
 rows=[]
 for name,shape in parts.items():
  if not shape.isValid() or len(shape.Solids())!=1:raise ValueError('Invalid '+name)
  c=(.18,.19,.20) if 'rubber_slider' in name else (.45,.58,.63)
  assembly.add(shape,name=name,color=cq.Color(*c))
  rows.append({'name':name,'bounds_mm':bounds(shape)})
 export_assembly(assembly,path)
 print(kind,'export complete',sha(path),flush=True)
 imported=mapped(path,rows);checks=[]
 for name,before in parts.items():
  after=imported[name];dv=abs(volume(after)-volume(before));vb,va=vertices(before),vertices(after)
  vertex_equal=vb.shape==va.shape and np.allclose(vb,va,atol=2e-7,rtol=0)
  ok=(after.isValid() and len(after.Solids())==1 and len(after.Faces())==len(before.Faces())
      and dv<max(1e-5,volume(before)*1e-8) and vertex_equal)
  checks.append({'name':name,'pass':bool(ok),'valid':after.isValid(),'solids':len(after.Solids()),
    'faces':len(after.Faces()),'bounds_mm':bounds(after),'volume_mm3':volume(after),
    'volume_roundtrip_delta_mm3':dv,'vertices_unchanged_within_mm':2e-7,
    'same_native_input_as_predecessor': 'rubber_slider' not in name})
  if not ok:raise ValueError('Native round trip failed '+name)
 mesh=path.with_suffix('.step.mesh')
 with mesh.open('rb') as f: header=json.loads(f.read(struct.unpack('<I',f.read(4))[0]))
 if header.get('src')!=sha(path):raise ValueError('Payload source mismatch')
 return imported,checks


def run():
 start=time.perf_counter();baseline=json.loads((PRIOR/'baseline.json').read_text())
 cache=Path(baseline['native_cache'])
 source=REF/'g_ganen_pump.py';oldsource=PRIOR/'g_ganen_pump.py'
 def rigid_functions(p):
  return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body
          if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name!='_foot'}
 if rigid_functions(source)!=rigid_functions(oldsource):raise ValueError('A non-foot generator function changed')
 data=json.loads((REF/'reference-parameters.json').read_text())
 keep={k:v for k,v in data.items() if k not in ('input_sha256','tool_sha256')}
 if hashlib.sha256(json.dumps(keep,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=baseline['unchanged_parameter_values_sha256']:
  raise ValueError('A measured parameter value changed')
 if data['ports']!=baseline['ports']:raise ValueError('A measured port changed')
 for name in ['g-ganen-pump.step','g-ganen-integration-envelope.step']:
  key=name if name=='g-ganen-pump.step' else 'integration-envelope/'+name
  if sha(cache/name)!=baseline['prior_sha256'][key]:raise ValueError('Predecessor native cache changed')
 old_d=json.loads((PRIOR/'native-validation.json').read_text())
 old_e=json.loads((PRIOR/'integration-envelope/native-validation.json').read_text())
 d=mapped(cache/'g-ganen-pump.step',old_d['native_solids'])
 e=mapped(cache/'g-ganen-integration-envelope.step',old_e['components'])
 print('predecessor native components mapped',len(d),len(e),flush=True)
 feet={row['id']+'_observed_rubber_slider_envelope':observed_foot(row) for row in data['mounting_feet']}
 if len(feet)!=4:raise ValueError('Expected exactly four common feet')
 for kind,parts in [('detailed',d),('integration',e)]:
  if len(parts)!=26 or len([k for k in parts if 'rubber_slider' not in k])!=22:raise ValueError('Unexpected component set')
  for name,shape in feet.items():parts[name]=shape
 detailed,dc=export_and_check('detailed',d,REF/'g-ganen-pump.step')
 integrated,ec=export_and_check('integration',e,ENV/'g-ganen-integration-envelope.step')
 # Binding metadata changes; all measured geometric parameter values remain exact.
 data['input_sha256']['scan-evidence.json']=sha(REF/'scan-evidence.json')
 data['tool_sha256']['g_ganen_pump.py']=sha(source)
 data['tool_sha256']['common-foot/g_ganen_foot.py']=sha(HERE/'g_ganen_foot.py')
 dump(REF/'reference-parameters.json',data)
 report={'schema':1,'status':'pass','scope':'Exactly four common-foot replacements. Twenty-two rigid native components are reused unchanged before export; round trips verify topology, vertices, volume and validity.',
  'source_sha256':{str(p.relative_to(REF)):sha(p) for p in [source,HERE/'g_ganen_foot.py',Path(__file__)]},
  'prior_evidence_sha256':{str(p.relative_to(HERE)):sha(p) for p in [PRIOR/'baseline.json',PRIOR/'native-validation.json',PRIOR/'integration-envelope/native-validation.json',oldsource]},
  'unchanged_rigid_functions':True,'unchanged_measured_parameter_values':True,'unchanged_ports':True,
  'common_foot_parameters':foot_parameters(),'common_foot_volume_mm3':build_foot().Volume(),
  'four_rigid_copies_same_geometry':True,'rigid_components_reused':22,
  'detailed_roundtrip':dc,'integration_roundtrip':ec,
  'output_sha256':{str(p.relative_to(REF)):sha(p) for p in [REF/'g-ganen-pump.step',REF/'g-ganen-pump.step.mesh',ENV/'g-ganen-integration-envelope.step',ENV/'g-ganen-integration-envelope.step.mesh']},
  'elapsed_seconds':time.perf_counter()-start,
  'limits':['Reference shapes describe the purchased feet, not a printable replacement or rubber stiffness model.','The C-mouth is visibly observed; hidden rail contact and partial-overhang retention are not measured.','Prior rigid scan residuals remain attributed to their unchanged native components. Whole-pump benchmark timings are historical.']}
 dump(HERE/'native-update.json',report)
 validation=old_d
 validation['status']='native_valid_common_foot_and_unchanged_rigid_scan_evidence'
 validation['native_solids']=[{k:r[k] for k in ['name','valid','solids','faces','bounds_mm']} for r in dc]
 validation['reference_parameters_sha256']=sha(REF/'reference-parameters.json')
 validation['tool_sha256']['g_ganen_pump.py']=sha(source)
 validation['tool_sha256']['common-foot/g_ganen_foot.py']=sha(HERE/'g_ganen_foot.py')
 validation['verified_parameter_input_digests']={**data['input_sha256'],**data['tool_sha256']}
 validation['rigid_readings_provenance']={'predecessor_validation':'common-foot/prior-evidence/native-validation.json','sha256':sha(PRIOR/'native-validation.json'),'basis':'All 22 queried rigid native components are reused exactly; source functions and measured geometric values are unchanged. No prior reading sampled the rubber-foot model.','native_replacement_proof':'common-foot/native-update.json','proof_sha256':sha(HERE/'native-update.json')}
 validation['limits']=[s for s in validation['limits'] if 'filled foot' not in s]
 validation['limits'].append('Common foot visible geometry does not qualify hidden rail retention, rubber stiffness or a replacement foot.')
 dump(REF/'native-validation.json',validation)
 # Replace the four containment rows with exact shared native copies. All old
 # non-foot outer-supporting-plane proofs retain their exact source/target solids.
 bound=json.loads((PRIOR/'integration-envelope/containment.json').read_text())
 desc=json.loads((PRIOR/'integration-envelope/envelope-parameters.json').read_text())
 derived=CACHE/'common-derived';derived.mkdir(exist_ok=True)
 by_name={r['name']:r for r in ec}
 for i,row in enumerate(bound['components']):
  name=row['name']
  if name in feet:
   s=integrated[name];r=by_name[name];p=derived/(name+'.brep');s.exportBrep(str(p))
   bound['components'][i]={'name':name,'method':'exact_frozen_native_copy','source_faces':r['faces'],'envelope_faces':r['faces'],'source_bounds_mm':bounds(detailed[name]),'envelope_bounds_mm':bounds(s),'max_outward_surface_distance_mm':0.0,'added_axis_extents_mm':[[0,0,0],[0,0,0]],'source_volume_mm3':volume(detailed[name]),'envelope_volume_mm3':volume(s)}
   bound['derived_native_cache'][name]={'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
   desc['components'][i]={'name':name,'method':'exact_frozen_native_copy'}
 bound['detailed_native_sha256']=sha(REF/'g-ganen-pump.step')
 bound['source_faces']=sum(r['faces'] for r in dc)
 bound['tool_sha256']['derive_envelope.py']=sha(ENV/'derive_envelope.py')
 bound['component_replacement_proof']={'path':'../common-foot/native-update.json','sha256':sha(HERE/'native-update.json'),'basis':'Only four feet changed; all other detailed and integration B-reps retain the prior containment proof exactly.'}
 # The reference manifest is filled after current source/docs are frozen.
 bound['frozen_reference_manifest_sha256']=None
 dump(ENV/'containment.json',bound)
 desc['detailed_native_sha256']=bound['detailed_native_sha256'];desc['containment_sha256']=sha(ENV/'containment.json')
 dump(ENV/'envelope-parameters.json',desc)
 current={'schema':1,'status':'native_envelope_roundtrip_pass','input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [HERE/'native-update.json',REF/'reference-parameters.json',HERE/'g_ganen_foot.py']},
 'native_sha256':sha(ENV/'g-ganen-integration-envelope.step'),'viewer_payload_sha256':sha(ENV/'g-ganen-integration-envelope.step.mesh'),'viewer_payload_matches_step':True,'native_containment_proof':'containment.json','native_containment_sha256':sha(ENV/'containment.json'),'all_native_solids_valid':True,'solids':26,'faces':sum(r['faces'] for r in ec),
 'components':[{**r,'method':next(v['method'] for v in bound['components'] if v['name']==r['name'])} for r in ec]}
 dump(ENV/'native-validation.json',current)
 print('both native references and component proofs updated',flush=True)

if __name__=='__main__':run()
