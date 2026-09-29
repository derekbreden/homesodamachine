"""Check the carrier's emitted round bands, wall schedule, settings and support exclusion."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from shapely.ops import unary_union
import prepare_print as prep

ROOT,JOB=prep.ROOT,prep.JOB
sys.path.insert(0,str(ROOT/'hardware/scripts'))
from verify_round_layer_band import wall_layers,check_span
from enclosure_support_audit import audit
sys.path.insert(0,str(ROOT/'hardware/printed-parts/enclosure/nameplate'))
from verify_mark2_print import segments

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    native=next((JOB/'ready').glob('*.gcode.3mf'));staged=next(JOB.glob('*-input.3mf'))
    report=json.loads((JOB/'preparation.json').read_text())
    for p,d in report['source_geometry_and_settings_sha256'].items():assert sha(ROOT/p)==d,p
    with zipfile.ZipFile(staged) as a,zipfile.ZipFile(native) as b:
        assert b.testzip() is None
        expected=json.loads(a.read('Metadata/project_settings.config'));actual=json.loads(b.read('Metadata/project_settings.config'))
        differences={k:[expected.get(k),actual.get(k)] for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)}
        allowed={'filament_map_2':[None,['1']],'filament_prime_volume':[['30'],['45']]}
        assert all(allowed.get(k)==v for k,v in differences.items()),differences
        for k,v in {'enable_support':'0','wall_loops':'2','is_infill_first':'0','infill_wall_overlap':'15%',
                    'wall_sequence':'inner wall/outer wall','filament_nozzle_map':['0'],'filament_colour':['#000000'],
                    'initial_layer_print_height':'0.2','layer_height':'0.24',
                    'brim_type':'outer_only','brim_width':'1','brim_object_gap':'0',
                    'elefant_foot_compensation':'0'}.items():assert actual[k]==v,(k,actual[k])
        gc=b.read('Metadata/plate_1.gcode');assert hashlib.md5(gc).hexdigest()==b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'ready/plate_1.gcode').write_bytes(gc);(JOB/'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
        def schedule(payload):
            return [(round(float(r.get('min_z')),6),round(float(r.get('max_z')),6),
                     {o.get('opt_key'):o.text for o in r.findall('option')})
                    for r in ET.fromstring(payload).findall('./object/range')]
        assert schedule(a.read('Metadata/layer_config_ranges.xml'))==schedule(b.read('Metadata/layer_config_ranges.xml'))
        ranges=ET.fromstring(b.read('Metadata/layer_config_ranges.xml')).findall('./object/range')
        assert ranges[0].find("option[@opt_key='wall_loops']").text=='6'
        assert ranges[1].find("option[@opt_key='wall_loops']") is None
        plate=ET.fromstring(b.read('Metadata/slice_info.config')).find('plate')
        objects=plate.findall('object');assert len(objects)==1 and objects[0].get('skipped')=='false'
        assert objects[0].get('name')==prep.trial.NAME
        metadata={e.get('key'):e.get('value') for e in plate.findall('metadata')}
        assert metadata['outside']=='false' and metadata['support_used']=='false'
    text=gc.decode();trims=[float(z) for z in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',text,re.M)]
    assert trims==[0.,.16]
    assert not any('support' in f.lower() for f in re.findall(r'^; FEATURE: (.*)',text,re.M))
    # The slicer can repeat a Z with heights differing only in round-off digits.
    # Count physical Z levels once while still rejecting conflicting heights.
    by_z={}
    for z,h in wall_layers(native,1901):
        assert z not in by_z or abs(by_z[z]-h)<.001,(z,by_z.get(z),h)
        by_z[z]=round(h,3)
    layers=sorted(by_z.items())
    assert len(layers)==int(re.search(r'; total layer number: (\d+)',text)[1])
    assert layers[0]==(.2,.2),layers[:2]
    rounds=[check_span(layers,'aft-R6-above-bed-layer',.2,6,.08,.001),check_span(layers,'fore-R6',15.054,21.054,.08,.001)]
    assert all(r['pass'] for r in rounds)
    runs=[]
    for z,h in layers:
        if not runs or abs(h-runs[-1]['height'])>.001:runs.append({'height':h,'bottom':z-h,'last_z':z,'count':1})
        else:runs[-1].update(last_z=z,count=runs[-1]['count']+1)
    assert [round(r['height'],2) for r in runs]==[.2,.08,.24,.08]
    roads=[r for r in segments(JOB/'ready/plate_1.gcode') if r['layer']<.4]
    shape=lambda rr:unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in rr])
    zs=[.2,.28,.36]
    model={z:[r for r in roads if r['layer']==z and r['feature']!='Brim'] for z in zs}
    shapes={z:shape(model[z]) for z in zs}
    brim=shape([r for r in roads if r['feature']=='Brim'])
    base=shape([r for r in roads if r['layer']==.2])
    overlap={'model_bounds':{str(z):list(s.bounds) for z,s in shapes.items()},
             'brim_bounds':list(brim.bounds),'first_layer_with_brim_bounds':list(base.bounds),
             'brim_to_model_gap_mm':brim.distance(shapes[.2]),'transitions':[]}
    for previous,z in zip(zs,zs[1:]):
        under=base if previous==.2 else shapes[previous]
        rr=[r for r in model[z] if r['feature'] in ('Outer wall','Overhang wall')]
        footprint=shape(rr)
        points=[LineString((r['a'],r['b'])).interpolate(i/10,normalized=True) for r in rr for i in range(11)]
        overlap['transitions'].append({'from_z':previous,'to_z':z,
            'max_sampled_outer_centerline_unsupported_mm':max(p.distance(under) for p in points),
            'outer_wall_area_fraction_supported':footprint.intersection(under).area/footprint.area})
    a,b=overlap['transitions']
    assert overlap['brim_to_model_gap_mm']<.02
    assert a['max_sampled_outer_centerline_unsupported_mm']<=b['max_sampled_outer_centerline_unsupported_mm']+.005
    assert a['outer_wall_area_fraction_supported']>.999
    overlap['pass']=True
    (JOB/'first-layer-overlap.json').write_text(json.dumps(overlap,indent=2)+'\n')
    support=audit(JOB/'ready/plate_1.gcode',prep.trial.NAME,profile=staged,include_unlabelled_support=True)
    assert support['summary']['support_bodies']==0
    (JOB/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert sliced['warning_message']==''
    proof={'pass':True,'native_archive':str(native.relative_to(ROOT)),'native_archive_sha256':sha(native),
           'gcode_sha256':hashlib.sha256(gc).hexdigest(),'source_hashes_current':True,
           'native_export_normalizations':differences,'other_settings_match_input':True,
           'rounds':rounds,'model_layer_runs':runs,'lower_wall_count':6,'global_wall_count':2,
           'supports':support['summary'],'emitted_z_trim_mm':trims,'initial_layer_height_mm':.2,
           'first_layer_overlap':overlap,'layer_count':len(layers),'estimated_seconds':sliced['total_predication'],
           'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
           'printer':'H2C','left_external_black_petgf':True,'submitted':False}
    (JOB/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('pass','layer_count','estimated_seconds','estimated_grams_saved_profile_density')},indent=2))


if __name__=='__main__':main()
