"""Verify front-bottom's emitted layer bands, support contacts and plate bounds."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString,shape
from shapely.affinity import translate

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
BASE=ROOT/'.cache/prints/2026-09-24-enclosure-front-bottom-h2c-v6'
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/faucet')]
from verify_round_layer_band import wall_layers,check_span
from enclosure_support_audit import audit
from prepare_display_print import extrusion_segments
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prep=json.loads((JOB/'preparation.json').read_text())
new=next((JOB/'ready').glob('*.gcode.3mf'))
old=next((BASE/'ready').glob('*.gcode.3mf'))
staged=next(JOB.glob('*-input.3mf'))
tag=lambda n:'{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'+n
with zipfile.ZipFile(old) as a,zipfile.ZipFile(new) as b,zipfile.ZipFile(staged) as inp,zipfile.ZipFile(next(BASE.glob('*-input.3mf'))) as ref:
    assert b.testzip() is None
    settings=json.loads(b.read('Metadata/project_settings.config'))
    assert settings==json.loads(a.read('Metadata/project_settings.config'))
    gc=b.read('Metadata/plate_1.gcode')
    assert hashlib.md5(gc).hexdigest()==b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    (JOB/'ready/plate_1.gcode').write_bytes(gc)
    (JOB/'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
    ranges=ET.fromstring(b.read('Metadata/layer_config_ranges.xml'))
    native_ranges=[{'min_z':float(r.get('min_z')),'max_z':float(r.get('max_z')),'options':{o.get('opt_key'):o.text for o in r.findall('option')}} for r in ranges.findall('./object/range')]
    assert native_ranges==[{'min_z':29.15,'max_z':41.3,'options':{'layer_height':'0.08','wall_loops':'6'}},{'min_z':41.3,'max_z':44.3,'options':{'layer_height':'0.08'}}],native_ranges
    changed=[n for n in ref.namelist() if ref.read(n)!=inp.read(n)]
    assert set(changed)=={'3D/Objects/object_1.model','Metadata/layer_config_ranges.xml'}
    for member in ['3D/Objects/object_1.model']:
        before=ET.fromstring(ref.read(member));after=ET.fromstring(inp.read(member))
        assert [v.attrib for v in before.iter(tag('vertex'))]==[v.attrib for v in after.iter(tag('vertex'))]
        bare=lambda tree:[{k:v for k,v in t.attrib.items() if k!='paint_supports'} for t in tree.iter(tag('triangle'))]
        assert bare(before)==bare(after)
    plate=ET.fromstring(b.read('Metadata/slice_info.config')).find('plate')
    meta={e.get('key'):e.get('value') for e in plate.findall('metadata')}
    objects={int(e.get('identify_id')):e.get('name') for e in plate.findall('object')}
    assert objects=={1901:'enclosure-front-bottom'},objects
    assert meta['outside']=='false'
    assert [f.get('color') for f in plate.findall('filament')]==['#000000']
    assert [n.get('id') for n in plate.findall('nozzle')]==['0']
for p,h in prep['source_geometry_sha256'].items():assert sha(ROOT/p)==h,p
text=gc.decode()
# This single-object export uses OBJECT_ID rather than the multi-object
# cancellation label expected by extrusion_segments. Normalize comments in an
# analysis copy only; the reviewed native archive and its G-code stay intact.
analysis_gcode=JOB/'analysis-object-labels.gcode'
analysis_gcode.write_text(re.sub(r'^; OBJECT_ID: (\d+)$',r'; start printing object, unique label id: \1',text,flags=re.M))
trims=list(map(float,re.findall(r'^\s*G29\.1 Z([-+\d.]+)',text,re.M)))
assert trims==[0,.16],trims
layers=wall_layers(new,1901);reference=wall_layers(old,1901)
assert len(layers)==len(reference),(len(layers),len(reference))
assert np.allclose(np.array(layers),np.array(reference),atol=.00001,rtol=0)
rounds=[check_span(layers,'complete-downward-handhold-rounds',29.25,41.25,.08,.001),check_span(layers,'visible-flute-run-outs',41.25,44.25,.08,.001)]
assert all(r['pass'] for r in rounds),rounds
result=json.loads((JOB/'ready/result.json').read_text())
assert result['return_code']==0 and len(result['sliced_plates'])==1
assert result['sliced_plates'][0]['warning_message']==''
reading=audit(JOB/'ready/plate_1.gcode','enclosure-front-bottom',ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-bottom.stl',staged,include_unlabelled_support=True)
(JOB/'support-audit.json').write_text(json.dumps(reading,indent=2)+'\n')
print('SUPPORT',json.dumps({'summary':reading['summary'],'interfaces':reading['interfaces']}),flush=True)
bounds=np.array([[np.inf,np.inf],[-np.inf,-np.inf]])
features=defaultdict(int);crossings=defaultdict(list);support=[];outside=[]
flat=translate(shape(prep['flat_ceiling_geometry']),162.5,51.2249984741211)
section_y=241.2249984741211
for s in extrusion_segments(analysis_gcode):
    if s['feature'] in ['', 'Custom']:continue
    assert s['object']==1901,s['object']
    assert s['width']>0
    p=np.array([s['a'][:2],s['b'][:2]]);pad=s['width']/2+.1
    bounds[0]=np.minimum(bounds[0],p.min(axis=0)-pad)
    bounds[1]=np.maximum(bounds[1],p.max(axis=0)+pad)
    features[s['feature']]+=1
    if s['feature'] in {'Inner wall','Outer wall','Overhang wall'}:
        x1,y1=s['a'][:2];x2,y2=s['b'][:2]
        if min(y1,y2)<=section_y<max(y1,y2):
            x=x1+(section_y-y1)*(x2-x1)/(y2-y1)
            if x<73:crossings[round(s['layer'],5)].append({'x_mm':round(x,5),'feature':s['feature']})
    if s['feature'].startswith('Support') and 28.5<=s['layer']<=44.3:
        support.append(s)
        if s['feature']=='Support interface' and not flat.buffer(.001).covers(LineString(p).buffer(s['width']/2)):
            outside.append(s)
(JOB/'round-band-support-segments.json').write_text(json.dumps(support,separators=(',',':')))
(JOB/'wall-crossings.json').write_text(json.dumps({str(z):sorted(v,key=lambda q:q['x_mm']) for z,v in crossings.items()},indent=2)+'\n')
(JOB/'flat-ceiling-interface-check.json').write_text(json.dumps({'interface_road_segments_outside_flat_ceiling':len(outside),'outside':outside,'pass':not outside},indent=2)+'\n')
assert not outside,outside[:2]
assert features['Outer wall']>0 and features['Support']>0 and support
assert np.isfinite(bounds).all()
margin=float(min(*bounds[0],325-bounds[1,0],320-bounds[1,1]));assert margin>0,bounds
report={'native_archive':str(new.relative_to(ROOT)),'native_archive_sha256':sha(new),'gcode_sha256':hashlib.sha256(gc).hexdigest(),'staged_input_sha256':sha(staged),
 'source_geometry_sha256':prep['source_geometry_sha256'],'geometry_and_placement_identical':True,'native_global_settings_identical':True,'native_layer_ranges':native_ranges,
 'emitted_model_wall_layers_identical_within_mm':.00001,'rounds':rounds,'initial_layer_mm':.2,'nozzle':'left 0.4 mm','filament':'black PET-GF labelled PET-CF, external254',
 'emitted_z_trim_commands_mm':trims,'slicer_return_code':0,'slicer_warning_message':'','layer_count':len(re.findall(r'^; CHANGE_LAYER',text,re.M)),
 'estimated_seconds':int(meta['prediction']),'estimated_grams_profile_density':float(meta['weight']),'support_summary':reading['summary'],
 'path_bounds_xy_mm':bounds.tolist(),'minimum_plate_clearance_mm':margin,'feature_counts':dict(features),'flat_ceiling_interface_road_segments_outside_flat_projection':len(outside),'pass':True}
(JOB/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
