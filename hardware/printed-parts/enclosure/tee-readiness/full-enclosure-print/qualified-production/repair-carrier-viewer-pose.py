#!/usr/bin/env python3
"""Restore only two viewer entries to the current native assembly's working pose."""
from pathlib import Path
import hashlib, json, os, sys
import numpy as np

ROOT = Path('/Users/derekbredensteiner/Developer/homesodamachine')
WORK = Path('/tmp/scanner-review/integration-correction')
os.environ['HSM_NO_BUILD_LOCK'] = '1'
sys.path.insert(0, str(ROOT/'hardware/scripts'))
import _facts, _mesh_payload, flute_payload

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
host = ROOT/'hardware/manifold-layout/enclosure-assembly.step.mesh'
step = ROOT/'hardware/manifold-layout/enclosure-assembly.step'
before = WORK/'assembly-before-final-publication.step.mesh'
report_path = WORK/'carrier-viewer-pose-repair.json'
if report_path.exists(): raise ValueError('Preserve the earlier repair record')
facts = _facts.read()
assert facts.agrees_with_card() and facts.agrees_with_step() and facts.agrees_with_sources()
doc = json.loads((ROOT/'hardware/manifold-layout/enclosure-assembly.facts.json').read_text())
interface = doc['box']['tee_carrier']
state = interface['assembly_state']
offset = doc['box']['collet_plate']['carrier_states'][state]['offset_y']
assert state == 'connected' and abs(offset-interface['connected_offset_y']) < 1e-9
assert sha(host) == sha(before)
assert _mesh_payload.read_source(host) == sha(step)
held = flute_payload.read_payload(host)
surfaces = flute_payload.surfaces(flute_payload.ENCLOSURE_DIRS)
names = ('enclosure-tee-carrier-left', 'enclosure-tee-carrier-right')
changes = []
for name in names:
    entries = [e for e in held if e['name'] == name]
    assert len(entries) == 1
    surface = flute_payload.carried(surfaces[name], (np.eye(3), np.array([0.,offset,0.])))
    pos = np.asarray(surface['pos']).reshape(-1,3)
    bounds = np.concatenate([pos.min(0),pos.max(0)])
    native_bounds = np.asarray(doc['bodies'][name])
    error = float(np.abs(bounds-native_bounds).max())
    piece = ROOT/'hardware/printed-parts/enclosure/tee-carrier'/f'{name}.step.mesh'
    budget = _mesh_payload.read_header(piece)['cut']['bound']
    assert error <= budget + 1e-5, (name, error, budget, bounds, native_bounds)
    entries[0].update({key:surface[key] for key in ('pos','nrm','idx','fac')})
    changes.append({'name':name,'state':state,'translation_mm':[0.,offset,0.],
                    'maximum_native_bbox_error_mm':error,'declared_viewer_deflection_bound_mm':budget})
tmp = host.with_name(host.name+'.pose-repair.tmp')
_mesh_payload.write(held, str(tmp), src=sha(step))
tmp.replace(host)
report = {'status':'two_viewer_entries_restored_to_current_native_working_pose',
          'before_payload':str(before),'before_sha256':sha(before),
          'after_payload':str(host),'after_sha256':sha(host),
          'source_step_sha256':sha(step), 'changes':changes,
          'repair_script_sha256':sha(__file__),
          'facts_sha256':sha(ROOT/'hardware/manifold-layout/enclosure-assembly.facts.json'),
          'scope':'Viewer payload only. No STEP, STL, model source, scorecard or print input changed. Exact whole-payload comparison is recorded separately.'}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
