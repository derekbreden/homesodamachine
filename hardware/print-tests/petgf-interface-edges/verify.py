"""Verify the machine file, inherited profile, gaps and edge-treatment scope."""
import io
import json
import hashlib
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'petgf-support-interface'))
from audit_gcode import audit


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    exp = json.loads((HERE/'experiment.json').read_text())
    project = ROOT/exp['project']
    out = project.parent
    bundle = out/'petgf-interface-edges-mark2.gcode.3mf'
    edge = json.loads((out/'edge-verification.json').read_text())
    slices = json.loads((out/'result.json').read_text())
    assert slices['return_code'] == 0
    plate = slices['sliced_plates'][0]
    assert not plate['warning_message'], plate['warning_message']
    assert 8*3600 < plate['total_predication'] < 16*3600
    with zipfile.ZipFile(ROOT/exp['profile']) as z:
        baseline = json.loads(z.read('Metadata/project_settings.config'))
        filament = z.read('Metadata/filament_settings_1.config')
    assert sha(ROOT/exp['profile']) == exp['profile_sha256']
    with zipfile.ZipFile(project) as z:
        prepared = json.loads(z.read('Metadata/project_settings.config'))
        objects = ET.fromstring(z.read('Metadata/model_settings.config')).findall('object')
    overrides = {k:[baseline.get(k), prepared.get(k)] for k in set(baseline)|set(prepared) if baseline.get(k)!=prepared.get(k)}
    assert overrides == {'extruder_ams_count': [['1#0|4#1','1#0|4#0'], ['1#0|4#0','1#0|4#0']]}, overrides
    for o, spec in zip(objects, exp['specimens']):
        metadata = {m.attrib['key']:m.attrib['value'] for m in o.findall('metadata') if 'key' in m.attrib}
        assert float(metadata['support_top_z_distance']) == spec['gap_mm']
    with zipfile.ZipFile(bundle) as z:
        sliced = json.loads(z.read('Metadata/project_settings.config'))
        assert json.loads(z.read('Metadata/filament_settings_1.config')) == json.loads(filament)
        raw = z.read('Metadata/plate_1.gcode')
        assert z.read('Metadata/plate_1.gcode.md5').decode().lower() == hashlib.md5(raw).hexdigest()
        slice_info = ET.fromstring(z.read('Metadata/slice_info.config'))
        nozzles = [x.attrib for x in slice_info.findall('.//nozzle')]
        assert nozzles == [{'id':'0','extruder_id':'1','nozzle_diameter':'0.4','volume_type':'Standard'}], nozzles
        assert len(slice_info.findall('.//object')) == 16
        assert len(slice_info.findall('.//filament')) == 1
    normalizations = {k:[prepared.get(k),sliced.get(k)] for k in set(prepared)|set(sliced) if prepared.get(k)!=sliced.get(k)}
    assert normalizations == {'filament_map_2':[None,['1']], 'filament_prime_volume':[['30'],['45']]}, normalizations
    text = raw.decode()
    trims = [l.strip() for l in text.splitlines() if l.lstrip().startswith('G29.1')]
    assert trims == ['G29.1 Z0 ; clear z-trim value first','G29.1 Z0.02 ; for Textured PEI Plate'], trims
    assert hashlib.sha256(raw).hexdigest() == edge['gcode_sha256']
    assert sha(bundle) == edge['bundle_sha256']
    regions = json.loads((out/'regions.json').read_text())
    measurements = audit(io.StringIO(text), regions)
    with zipfile.ZipFile(out/'native.gcode.3mf') as z:
        native = audit(io.StringIO(z.read('Metadata/plate_1.gcode').decode()), regions)
    for measured, unmodified, spec in zip(measurements, native, exp['specimens']):
        expected = {0.3:0.24, 0.45:0.48}[spec['gap_mm']]
        assert measured['planned_deposition_gap_mm'] == expected
        assert measured['observed_interface_layers'] == 2
        # Central sheet, model and tree paths are unchanged within every ROI.
        assert measured == unmodified, (spec['id'], measured, unmodified)
    treatments = {}
    for s in exp['specimens']:
        k = (s['gap_mm'],s['wall_setback_mm'],s['free_edge_setback_mm'])
        treatments.setdefault(k,[]).append(s['id'])
    assert len(treatments)==8 and all(len(v)==2 for v in treatments.values())
    report = dict(slicer='BambuStudio 02.08.02.61',sliced_file=str(bundle.relative_to(ROOT)),
        sliced_file_sha256=sha(bundle),gcode_sha256=hashlib.sha256(raw).hexdigest(),
        source_profile_sha256=exp['profile_sha256'],input_project_sha256=sha(project),
        settings_overrides=overrides,settings_normalizations=normalizations,nozzles=nozzles,
        active_z_trim_commands=trims,estimated_seconds_upper_bound=plate['total_predication'],
        filament_grams_upper_bound=plate['filaments'][0]['total_used_g'],layers=120,
        specimen_count=16,slicer_warnings=plate['warning_message'],
        all_central_interface_model_and_tree_paths_match_native=True,
        support_path_audit=measurements,edge_verification=edge)
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    (HERE/'regions.json').write_text(json.dumps(regions,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('support_path_audit','edge_verification')},indent=2))
    fractions=[r['retained_interface_path_fraction'] for r in edge['layers']]
    print('Minimum retained contact path:', min(fractions))


if __name__ == '__main__': main()
