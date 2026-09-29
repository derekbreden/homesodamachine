"""Check bed-connected wings and all raised artwork in the native face-up slice."""
import hashlib,json,re,sys,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from shapely.geometry import LineString,Point
from shapely.ops import unary_union
import prepare_print as prep

ROOT,JOB,HERE=prep.ROOT,prep.JOB,prep.HERE
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers

def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    prepared=json.loads((JOB/'preparation.json').read_text())
    staged=next(JOB.glob('*-input.3mf'));native=next((JOB/'ready').glob('*.gcode.3mf'))
    assert sha(staged)==prepared['project_sha256']
    for path,digest in prepared['source_geometry_and_settings_sha256'].items():assert sha(ROOT/path)==digest,path
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings=json.loads(z.read('Metadata/project_settings.config'));gc=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    for k,v in {'enable_support':'0','brim_type':'no_brim','initial_layer_print_height':'0.2',
                'layer_height':'0.24','filament_nozzle_map':['0','1'],'nozzle_diameter':['0.4','0.4'],
                'wall_sequence':'inner wall/outer wall','is_infill_first':'0','infill_wall_overlap':'15%'}.items():
        assert settings[k]==v,(k,settings[k])
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path));assert {r['object'] for r in roads}=={2303}
    assert not any(r['feature'].startswith('Support') for r in roads)
    layers=wall_layers(native,2303)
    assert len(layers)==12 and np.allclose([z for z,h in layers],[.2,.48,.72,.96,1.2,1.44,1.68,1.92,2.16,2.4,2.64,2.88])
    assert sorted({r['layer'] for r in roads if r['tool']==1})==[1.92,2.16,2.4,2.64,2.88]
    assert max(r['layer'] for r in roads if r['tool']==0)==2.4
    wing_checks=[]
    for z in (.2,1.2,1.44):
        shape=unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in roads if r['layer']==z])
        covered=[shape.covers(Point(x,125)) for x in (111.235,218.765)]
        assert covered==([True,True] if z<=1.2 else [False,False]),(z,covered)
        wing_checks.append({'print_z_mm':z,'both_wing_midpoints_covered':covered})
    checks=[]
    for z in (2.64,2.88):
        raised=[r for r in roads if r['layer']==z];assert {r['tool'] for r in raised}=={1}
        counts={name:sum(all(lo<p[0]<hi for p in (r['a'],r['b'])) for r in raised)
                for name,(lo,hi) in {'logo_and_drop':(117,143),'lettering':(145,187),'qr':(188,214)}.items()}
        assert all(n>10 for n in counts.values()) and sum(counts.values())==len(raised)
        checks.append({'print_z_mm':z,'white_paths_by_region':counts})
    scale=20;lo=np.array([109.,103.]);hi=np.array([221.,147.])
    im=Image.new('RGB',tuple(((hi-lo)*scale).astype(int)),'#777777');draw=ImageDraw.Draw(im)
    for layer in (2.4,2.64,2.88):
        for r in roads:
            if r['layer']!=layer:continue
            pts=[tuple(((np.array(p)-lo)*scale).round().astype(int)) for p in (r['a'],r['b'])]
            draw.line(pts,fill='white' if r['tool'] else 'black',width=max(1,round(r['width']*scale)))
    ImageOps.flip(im).save(JOB/'show-face-paths.png')
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    record={'pass':True,'printer':'Mark2','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'source_hashes_current':True,'layers':layers,'support_paths':0,'wing_checks':wing_checks,
            'raised_artwork_checks':checks,'artwork_rise_mm':.48,
            'estimated_seconds':sliced['total_predication'],'submitted':False,
            'launch_hold':'Await the Mark2 registration coupon result; this uncorrected slice is a geometry review.',
            'physical_qualification':'Insertion, shake retention, flatness, colour registration and QR scanning pending.'}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','support_paths','estimated_seconds','raised_artwork_checks')}))

if __name__=='__main__':main()
