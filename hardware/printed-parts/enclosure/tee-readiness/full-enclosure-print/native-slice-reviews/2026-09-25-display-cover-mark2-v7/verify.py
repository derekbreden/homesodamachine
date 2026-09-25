"""Validate native plate integrity, settings, model paths and every support body."""
from pathlib import Path
from collections import defaultdict
import hashlib, itertools, json, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/faucet')]
from enclosure_support_audit import audit
from prepare_display_print import extrusion_segments, emitted_config
from verify_round_layer_band import wall_layers
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
native = next((JOB/'ready').glob('*.gcode.3mf'))
staged = next(JOB.glob('*-input.3mf'))
preparation = json.loads((JOB/'preparation.json').read_text())
for name, digest in preparation['source_geometry_and_settings_sha256'].items():
    assert sha(ROOT/name) == digest, name
for part in preparation['parts']:
    assert sha(ROOT/part['source']) == part['stl_sha256'], part['name']
with zipfile.ZipFile(staged) as inp, zipfile.ZipFile(native) as z:
    assert z.testzip() is None
    members = {n:inp.read(n) for n in inp.namelist()}
    expected = json.loads(members['Metadata/project_settings.config'])
    actual = json.loads(z.read('Metadata/project_settings.config'))
    differences = {k:[expected.get(k),actual.get(k)] for k in set(expected)|set(actual)
                   if expected.get(k)!=actual.get(k)}
    allowed = {'filament_prime_volume':[['30'],['45']], 'filament_map_2':[None,['1']]}
    assert all(allowed.get(k)==v for k,v in differences.items()), differences
    gc = z.read('Metadata/plate_1.gcode')
    assert hashlib.md5(gc).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    (JOB/'ready/plate_1.gcode').write_bytes(gc)
    (JOB/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    plates = ET.fromstring(z.read('Metadata/slice_info.config')).findall('plate')
    assert len(plates) == 1
    plate = plates[0]
    meta = {e.get('key'):e.get('value') for e in plate.findall('metadata')}
    objects = {int(e.get('identify_id')):e.get('name') for e in plate.findall('object')}
    assert objects == {p['identify_id']:p['name'] for p in preparation['parts']}
    assert all(o.get('skipped')=='false' for o in plate.findall('object')) and meta['outside']=='false'
    assert [f.get('color') for f in plate.findall('filament')] == ['#000000']
    assert [f.get('type') for f in plate.findall('filament')] == ['PET-CF']
    assert [n.get('id') for n in plate.findall('nozzle')] == ['0']
    config,trims,total_layers = emitted_config(z)
assert trims == [0,.02], trims
assert config['wall_loops']=='2' and config['layer_height']=='0.24'
assert config['infill_wall_overlap']=='15%' and config['is_infill_first']=='0'
text = gc.decode()
# Single-object exports omit start/stop labels. Normalize comments in an audit copy only.
normalized = text if '; start printing object' in text else re.sub(
    r'^; OBJECT_ID: (\d+)$',r'; start printing object, unique label id: \1',text,flags=re.M)
analysis_gcode = JOB/'audit-object-labels.gcode'
analysis_gcode.write_text(normalized)
assert re.sub(r'^;.*$', '', normalized,flags=re.M) == re.sub(r'^;.*$', '', text,flags=re.M)
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
tag = lambda n:'{'+NS+'}'+n
support_readings = []
layer_readings = {}
for part in preparation['parts']:
    oid,name = part['identify_id'],part['name']
    layers = wall_layers(native,oid)
    assert layers and all(abs(h-(.2 if i==0 else .24))<.001 for i,(z,h) in enumerate(layers)), (name,layers)
    layer_readings[name] = {'wall_layer_count':len(layers),'first':layers[0],'last':layers[-1],
                            'layer_height_mm':.24,'first_layer_height_mm':.2}
    # Keep only this object's placement for the support audit's CAD coordinate mapping.
    one = dict(members)
    model = ET.fromstring(one['3D/3dmodel.model'])
    for parent_name,key in (('resources','id'),('build','objectid')):
        parent = model.find(tag(parent_name))
        for item in list(parent):
            if item.get(key)!=part['object_id']: parent.remove(item)
    cfg = ET.fromstring(one['Metadata/model_settings.config'])
    for item in list(cfg):
        if item.tag!='object' or item.get('id')!=part['object_id']: cfg.remove(item)
    one['3D/3dmodel.model'] = ET.tostring(model,encoding='utf-8',xml_declaration=True)
    one['Metadata/model_settings.config'] = ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
    coords = JOB/('coordinates-'+name+'.3mf')
    with zipfile.ZipFile(coords,'w',zipfile.ZIP_DEFLATED) as z:
        for n,payload in one.items(): z.writestr(n,payload)
    filtered = JOB/('support-labels-'+name+'.gcode')
    current = None
    with filtered.open('w') as f:
        for raw in normalized.splitlines(True):
            if m:=re.match(r'; start printing object, unique label id: (\d+)',raw):
                current = int(m[1]); f.write('; FEATURE: Other object\n')
            elif raw.startswith('; stop printing object'):
                current = None; f.write('; FEATURE: Other object\n')
            f.write('; FEATURE: Other object\n' if raw.startswith('; FEATURE:') and current!=oid else raw)
    reading = audit(filtered,name,ROOT/part['source'],staged,coords,include_unlabelled_support=True)
    (JOB/('support-audit-'+name+'.json')).write_text(json.dumps(reading,indent=2)+'\n')
    support_readings.append(reading)
    print(name, json.dumps({'summary':reading['summary'],'interfaces':reading['interfaces']}), flush=True)
    if name.startswith('enclosure-window-cover'):
        assert reading['summary']['support_bodies']==0,reading

bounds = {oid:np.array([[np.inf,np.inf],[-np.inf,-np.inf]]) for oid in objects}
counts = {oid:defaultdict(int) for oid in objects}
support_segments = []
for s in extrusion_segments(analysis_gcode):
    if s['feature'] in ('','Custom'): continue
    oid = s['object']
    assert oid in objects and s['width']>0, s
    points = np.array([s['a'][:2],s['b'][:2]])
    pad = s['width']/2+.1
    bounds[oid][0] = np.minimum(bounds[oid][0],points.min(axis=0)-pad)
    bounds[oid][1] = np.maximum(bounds[oid][1],points.max(axis=0)+pad)
    counts[oid][s['feature']] += 1
    if s['feature'].startswith('Support'): support_segments.append(s)
path_bounds = {}
for oid,b in bounds.items():
    assert np.all(np.isfinite(b)) and counts[oid]['Outer wall']>0, oid
    margin = float(min(*b[0],325-b[1,0],320-b[1,1]))
    assert margin>15, (oid,b,margin)
    path_bounds[objects[oid]] = {'bounds_xy_mm':b.tolist(),'minimum_plate_clearance_mm':margin,
                                 'feature_segment_counts':dict(counts[oid])}
gaps = []
for a,b in itertools.combinations(objects,2):
    gap = float(np.linalg.norm(np.maximum(0,np.maximum(bounds[a][0]-bounds[b][1],bounds[b][0]-bounds[a][1]))))
    assert gap>5, (a,b,gap)
    gaps.append({'parts':[objects[a],objects[b]],'path_bounds_clearance_mm':gap})
assert all(s['object']==1901 for s in support_segments)
assert any(s['feature']=='Support interface' for s in support_segments)
(JOB/'support-segments.json').write_text(json.dumps(support_segments,separators=(',',':')))
result = json.loads((JOB/'ready/result.json').read_text())
assert result['return_code']==0 and len(result['sliced_plates'])==1
slice_plate = result['sliced_plates'][0]
assert slice_plate['warning_message']==''
assert slice_plate['triangle_count']==sum(p['triangles'] for p in preparation['parts'])
report = {'pass':True,'native_archive':str(native.relative_to(ROOT)),
          'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
          'staged_input_sha256':sha(staged),'source_hashes_current':True,
          'native_export_settings_normalizations':differences,
          'all_other_native_settings_match_staged':True,'model_layers':layer_readings,
          'layer_count':total_layers,'emitted_z_trim_commands_mm':trims,
          'slicer_return_code':0,'slicer_warning_message':'','object_count':len(objects),
          'triangles':slice_plate['triangle_count'],
          'estimated_seconds':slice_plate['total_predication'],
          'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in slice_plate['filaments']),
          'path_bounds':path_bounds,'path_gaps':gaps,
          'support_summaries':{r['piece']:r['summary'] for r in support_readings},
          'support_only_on_display_cover':True,'submitted':False}
(JOB/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
