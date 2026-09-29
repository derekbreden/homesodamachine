"""Measure the emitted candidate shifts, not just the requested CAD positions."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from shapely.geometry import LineString,box
from shapely.ops import unary_union
import prepare_print as prep

ROOT,JOB,HERE=prep.ROOT,prep.JOB,prep.HERE
sys.path[:0]=[str(ROOT/'hardware/printed-parts/enclosure/nameplate'),str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers

def roads_shape(roads):
    return unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in roads])

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
    for key,value in {'filament_nozzle_map':['0','1'],'nozzle_diameter':['0.4','0.4'],
                      'enable_support':'0','enable_arc_fitting':'0','initial_layer_print_height':'0.2',
                      'layer_height':'0.24','brim_type':'no_brim','extruder_offset':['0x0','0x0']}.items():
        assert settings[key]==value,(key,settings[key])
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.02]
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path))
    assert not any(r['feature'].startswith('Support') for r in roads)
    assert {r['object'] for r in roads}=={2303}
    layers=wall_layers(native,2303)
    assert np.allclose(layers,[(.2,.2),(.48,.28),(.72,.24),(.96,.24),(1.2,.24),(1.44,.24)]),layers
    assert sorted({r['layer'] for r in roads if r['tool']==1})==[1.2,1.44]
    checks=[]
    for z in (1.2,1.44):
        for i in range(15):
            x=165+(i-7)*7
            dx,dy=(prep.trial.OFFSETS[a][i] for a in ('X','Y'))
            for axis,regions in [('X',((x-.7,135.8,x+.7,139.2),(x+dx-.7,131.4,x+dx+.7,134.8))),
                                 ('Y',((x-3,119.3,x-.4,120.7),(x+.4,120+dy-.7,x+3,120+dy+.7)))]:
                d=prep.trial.OFFSETS[axis][i]
                shapes=[]
                for tool,region in enumerate(regions):
                    shape=roads_shape([r for r in roads if r['layer']==z and r['tool']==tool
                                       and box(*region).contains(LineString((r['a'],r['b'])).centroid)])
                    assert not shape.is_empty,(z,i,axis,tool)
                    shapes.append(shape)
                k=0 if axis=='X' else 1
                centres=[(s.bounds[k]+s.bounds[k+2])/2 for s in shapes]
                emitted=centres[1]-centres[0]
                assert abs(emitted-d)<.006,(z,i,axis,d,emitted)
                checks.append({'print_z_mm':z,'index':i,'axis':axis,'requested_mm':d,'emitted_mm':emitted})
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    scale=15;lo=np.array([109.,105.]);hi=np.array([221.,146.])
    image=Image.new('RGB',tuple(((hi-lo)*scale).astype(int)),'#777777');draw=ImageDraw.Draw(image)
    for layer in (.96,1.44):
        for r in roads:
            if r['layer']!=layer:continue
            pts=[tuple(((np.array(p)-lo)*scale).round().astype(int)) for p in (r['a'],r['b'])]
            draw.line(pts,fill='white' if r['tool'] else 'black',width=max(1,round(r['width']*scale)))
    ImageOps.flip(image).save(JOB/'coplanar-paths.png')
    record={'pass':True,'printer':'Mark2','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'layer_planes_mm':layers,'emitted_candidate_checks':checks,
            'maximum_candidate_error_mm':max(abs(c['emitted_mm']-c['requested_mm']) for c in checks),
            'source_hashes_current':True,'supports':0,'emitted_z_trim_mm':trims,
            'estimated_seconds':sliced['total_predication'],
            'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
            'launch_options':prepared['launch_options'],'submitted':False}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','estimated_seconds','maximum_candidate_error_mm')}))

if __name__=='__main__':main()
