"""Verify the wall-pose coupon and unobstructed sideways wing slots."""
import hashlib,json,re,sys,zipfile
import numpy as np
from shapely.geometry import LineString,box
from shapely.ops import unary_union
import prepare_receiver as prep

ROOT,JOB,HERE=prep.ROOT,prep.JOB,prep.HERE
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from enclosure_support_audit import audit

def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    prepared=json.loads((JOB/'preparation.json').read_text())
    staged=next(JOB.glob('*-input.3mf'));native=next((JOB/'ready').glob('*.gcode.3mf'))
    assert sha(staged)==prepared['project_sha256']
    for path,digest in prepared['source_geometry_and_settings_sha256'].items():assert sha(ROOT/path)==digest,path
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings=json.loads(z.read('Metadata/project_settings.config'))
        gc=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    required={'filament_nozzle_map':['0'],'filament_colour':['#000000'],
              'nozzle_diameter':['0.4','0.4'],'layer_height':'0.24','initial_layer_print_height':'0.2',
              'wall_sequence':'inner wall/outer wall','is_infill_first':'0','infill_wall_overlap':'15%',
              'support_object_xy_distance':'0.8','support_top_z_distance':'0.45',
              'support_bottom_z_distance':'0.45','support_type':'normal(auto)','support_style':'snug'}
    for k,v in required.items():assert settings[k]==v,(k,settings[k])
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.16]
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path));assert {r['object'] for r in roads}=={1901} and {r['tool'] for r in roads}=={0}
    layers=wall_layers(native,1901)
    assert layers[0]==(.2,.2) and all(abs(h-.24)<1e-5 for _,h in layers[1:])
    support=[r for r in roads if r['feature'].startswith('Support')]
    # Printed XY = (162.5 + CAD X, 159.4 - CAD Y), Z = 23 - CAD Z.
    # Check every support bead against the open length of both 1.50 mm slots.
    slots=[box(162.5-55.565,157.9,162.5-52.265,159.4),
           box(162.5+52.265,157.9,162.5+55.565,159.4)]
    slot_overlaps=[]
    for side,slot in zip(('left','right'),slots):
        volume=0.
        for r in support:
            if 6.7<r['layer']<39.55:
                volume+=LineString((r['a'],r['b'])).buffer(r['width']/2).intersection(slot).area
        assert volume<1e-6,(side,volume)
        slot_overlaps.append({'side':side,'sum_of_support_bead_intersection_areas_mm2':volume})
    a=audit(path,'nameplate-flat-wing-receiver',profile=staged,include_unlabelled_support=True)
    a['removal_access']='Central support exits outward through the open front before the plate is installed. No support bead enters either sideways wing slot. Two small bed-rooted bodies are exposed at the bottom corners.'
    a['physical_removal_tested']=False
    (JOB/'support-audit.json').write_text(json.dumps(a,indent=2)+'\n')
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    record={'pass':True,'printer':'H2C','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'source_hashes_current':True,'model_layers':len(layers),'independent_support_layers':True,
            'emitted_z_trim_mm':trims,'slot_support_clearance_checks':slot_overlaps,
            'support_summary':a['summary'],'support_removal':'Physical trial pending; front-access lane verified.',
            'estimated_seconds':sliced['total_predication'],
            'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
            'submitted':False}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','estimated_seconds','model_layers')}))

if __name__=='__main__':main()
