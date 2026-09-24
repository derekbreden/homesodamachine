"""Read the native plate's layers, supports, geometry and extrusion bounds."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString, box
from shapely import polygons,union_all

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
BASE=ROOT/'.cache/prints/2026-09-23-pump-cartridge-cap-mark2-v6'
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/faucet')]
from verify_round_layer_band import wall_layers,check_span
from enclosure_support_audit import audit
from prepare_display_print import extrusion_segments
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
new=next((JOB/'ready').glob('*.gcode.3mf'))
old=next((BASE/'ready').glob('*.gcode.3mf'))
staged=next(JOB.glob('*-input.3mf'))
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
tag=lambda n:'{'+NS+'}'+n
with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b,zipfile.ZipFile(staged) as inp:
    assert b.testzip() is None
    settings=json.loads(b.read('Metadata/project_settings.config'))
    assert settings==json.loads(a.read('Metadata/project_settings.config'))
    gc=b.read('Metadata/plate_1.gcode')
    assert hashlib.md5(gc).hexdigest()==b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    (JOB/'ready/plate_1.gcode').write_bytes(gc)
    (JOB/'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
    members={n:inp.read(n) for n in inp.namelist()}
    ranges=ET.fromstring(b.read('Metadata/layer_config_ranges.xml'))
    native_ranges=[{'min_z':float(r.get('min_z')),'max_z':float(r.get('max_z')),'options':{o.get('opt_key'):o.text for o in r.findall('option')}} for r in ranges.findall('./object/range')]
    assert native_ranges==[{'min_z':6.,'max_z':18.4,'options':{'layer_height':'0.08'}},{'min_z':100.3,'max_z':113.2,'options':{'layer_height':'0.08','wall_loops':'6'}}],native_ranges
    assert b.read('3D/Objects/object_1.model').count(b'paint_supports="8"')>=31562
    plate=ET.fromstring(b.read('Metadata/slice_info.config')).find('plate')
    meta={e.get('key'):e.get('value') for e in plate.findall('metadata')}
    objects={int(e.get('identify_id')):e.get('name') for e in plate.findall('object')}
    assert objects=={1901:'enclosure-pump-cartridge',1902:'enclosure-pump-cap'}
    assert meta['outside']=='false'
    assert [f.get('color') for f in plate.findall('filament')]==['#000000']
    assert [n.get('id') for n in plate.findall('nozzle')]==['0']
text=gc.decode()
trims=list(map(float,re.findall(r'^\s*G29\.1 Z([-+\d.]+)',text,re.M)))
assert trims==[0,.02],trims
layers={}
for oid in objects:
    layers[oid]=wall_layers(new,oid)
    reference=wall_layers(old,oid)
    assert len(layers[oid])==len(reference)
    assert np.allclose(np.array(layers[oid]),np.array(reference),atol=.00001,rtol=0),oid
rounds=[check_span(layers[1901],'complete-grip-floor-rounds',6.23,18.23,.08,.001),check_span(layers[1901],'complete-grip-ceiling-rounds',100.999,112.999,.08,.001)]
assert all(r['pass'] for r in rounds),rounds
assert all(abs(h-(.2 if i==0 else .24))<.001 for i,(z,h) in enumerate(layers[1902]))
result=json.loads((JOB/'ready/result.json').read_text())
assert result['return_code']==0 and len(result['sliced_plates'])==1
assert result['sliced_plates'][0]['warning_message']==''
parts=[]
for oid,name in objects.items():
    source_id='2' if oid==1901 else '4'
    one=dict(members)
    model=ET.fromstring(one['3D/3dmodel.model'])
    resources,build=model.find(tag('resources')),model.find(tag('build'))
    for item in list(resources):
        if item.get('id')!=source_id: resources.remove(item)
    for item in list(build):
        if item.get('objectid')!=source_id: build.remove(item)
    config=ET.fromstring(one['Metadata/model_settings.config'])
    for item in list(config):
        if item.tag!='object' or item.get('id')!=source_id: config.remove(item)
    one['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    one['Metadata/model_settings.config']=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    coordinates=JOB/('coordinates-'+name+'.3mf')
    with zipfile.ZipFile(coordinates,'w',zipfile.ZIP_DEFLATED) as z:
        for n,p in one.items():z.writestr(n,p)
    filtered=JOB/('support-labels-'+name+'.gcode')
    current=None
    with filtered.open('w') as f:
        for raw in text.splitlines(True):
            if m:=re.match(r'; start printing object, unique label id: (\d+)',raw):
                current=int(m[1]); f.write('; FEATURE: Other object\n')
            elif raw.startswith('; stop printing object'):
                current=None; f.write('; FEATURE: Other object\n')
            if raw.startswith('; FEATURE:') and current!=oid:f.write('; FEATURE: Other object\n')
            else:f.write(raw)
    reading=audit(filtered,name,ROOT/f'hardware/printed-parts/enclosure/enclosure/{name}.stl',staged,coordinates,include_unlabelled_support=True)
    (JOB/('support-audit-'+name+'.json')).write_text(json.dumps(reading,indent=2)+'\n')
    parts.append(reading)
    print(name,json.dumps({'summary':reading['summary'],'interfaces':reading['interfaces']}),flush=True)

bounds={oid:np.array([[np.inf,np.inf],[-np.inf,-np.inf]]) for oid in objects}
feature_counts={oid:defaultdict(int) for oid in objects}
crossings=defaultdict(list)
support_high=[]
interfaces=[]
# The flat ceilings in plate coordinates. Complete round projections lie outside
# these rectangles; inspect all support paths separately from labelled interfaces.
flat_roofs=union_all([box(61,202.203,70.75,218.203),box(254.25,202.203,264,218.203)])
interface_road_outside_flat=[]
for s in extrusion_segments(JOB/'ready/plate_1.gcode'):
    if s['feature'] in ['', 'Custom']: continue
    oid=s['object']; assert oid in objects,oid
    assert s['width']>0
    p=np.array([s['a'][:2],s['b'][:2]])
    pad=s['width']/2+.1
    bounds[oid][0]=np.minimum(bounds[oid][0],p.min(axis=0)-pad)
    bounds[oid][1]=np.maximum(bounds[oid][1],p.max(axis=0)+pad)
    feature_counts[oid][s['feature']]+=1
    if oid!=1901:continue
    if s['feature'] in {'Inner wall','Outer wall','Overhang wall'}:
        x1,y1=s['a'][:2];x2,y2=s['b'][:2]
        if min(y1,y2)<=210.2<max(y1,y2):
            x=x1+(210.2-y1)*(x2-x1)/(y2-y1)
            if x<62: crossings[round(s['layer'],5)].append({'x_mm':round(x,5),'feature':s['feature']})
    if s['feature'].startswith('Support') and s['layer']>=100:
        support_high.append(s)
        if s['feature']=='Support interface':
            interfaces.append(s)
            line=LineString(p)
            if not flat_roofs.buffer(.001).covers(line.buffer(s['width']/2)):
                interface_road_outside_flat.append(s)
print('SUPPORT_HIGH',len(support_high),'INTERFACE_ROADS_OUTSIDE_FLAT',len(interface_road_outside_flat),flush=True)
assert not interface_road_outside_flat,interface_road_outside_flat[:2]
(JOB/'upper-support-segments.json').write_text(json.dumps(support_high,separators=(',',':')))
(JOB/'wall-crossings.json').write_text(json.dumps({str(z):sorted(v,key=lambda c:c['x_mm']) for z,v in crossings.items()},indent=2)+'\n')
bound_report={}
for oid,b in bounds.items():
    margin=float(min(*b[0],325-b[1,0],320-b[1,1]))
    assert margin>0,(oid,b)
    bound_report[objects[oid]]={'bounds_xy_mm':b.tolist(),'minimum_plate_clearance_mm':margin,'feature_counts':dict(feature_counts[oid])}
gap=float(np.linalg.norm(np.maximum(0,np.maximum(bounds[1901][0]-bounds[1902][1],bounds[1902][0]-bounds[1901][1]))))
assert gap>0
report={'native_archive':str(new.relative_to(ROOT)),'native_archive_sha256':sha(new),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
 'staged_input_sha256':sha(staged),'source_hashes':json.loads((JOB/'preparation.json').read_text())['source_input_sha256'],
 'native_settings_identical':True,'native_layer_ranges':native_ranges,'emitted_model_wall_layers_identical_within_mm':.00001,'rounds':rounds,
 'cap_layers_mm':.24,'initial_layer_mm':.2,'nozzle':'left 0.4 mm','filament':'black PET-GF labelled PET-CF, external254',
 'emitted_z_trim_commands_mm':trims,'slicer_return_code':0,'slicer_warning_message':'','layer_count':len(re.findall(r'^; CHANGE_LAYER',text,re.M)),
 'estimated_seconds':int(meta['prediction']),'estimated_grams_profile_density':float(meta['weight']),
 'support_summaries':{p['piece']:p['summary'] for p in parts},'path_bounds':bound_report,'projected_object_path_gap_mm':gap,
 'cartridge_interface_road_segments_outside_flat_roof_projection':len(interface_road_outside_flat),'pass':True}
(JOB/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
