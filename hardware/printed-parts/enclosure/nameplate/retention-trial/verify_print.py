"""Verify both hotends, precise hook height, supports and nameplate artwork paths."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageOps
import prepare_print as prep

ROOT,JOB,HERE=prep.ROOT,prep.JOB,prep.HERE
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from enclosure_support_audit import audit

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    staged=next(JOB.glob('*-input.3mf'));native=next((JOB/'ready').glob('*.gcode.3mf'))
    report=json.loads((JOB/'preparation.json').read_text())
    for p,d in report['source_geometry_and_settings_sha256'].items():assert sha(ROOT/p)==d,p
    with zipfile.ZipFile(staged) as a,zipfile.ZipFile(native) as b:
        assert b.testzip() is None
        expected=json.loads(a.read('Metadata/project_settings.config'));actual=json.loads(b.read('Metadata/project_settings.config'))
        differences={k:[expected.get(k),actual.get(k)] for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)}
        assert set(differences)<={'inherits_group','different_settings_to_system'},differences
        assert all(actual[k]==expected[k][:4] for k in differences)
        for k,v in {'filament_nozzle_map':['0','1'],'filament_colour':['#000000','#FFFFFF'],'filament_printable':['3','3'],
                    'nozzle_diameter':['0.4','0.4'],'layer_height':'0.24','initial_layer_print_height':'0.2',
                    'support_top_z_distance':'0.24','enable_arc_fitting':'0'}.items():assert actual[k]==v,(k,actual[k])
        gc=b.read('Metadata/plate_1.gcode');assert hashlib.md5(gc).hexdigest()==b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'ready/plate_1.gcode').write_bytes(gc);(JOB/'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
        plate=ET.fromstring(b.read('Metadata/slice_info.config')).find('plate')
        assert {o.get('identify_id'):o.get('name') for o in plate.findall('object')}==report['identify_ids']
        assert all(o.get('skipped')=='false' for o in plate.findall('object'))
        assert {n.get('id') for n in plate.findall('nozzle')}=={'0','1'}
        assert {e.get('key'):e.get('value') for e in plate.findall('metadata')}['outside']=='false'
    trims=[float(z) for z in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.02]
    roads=list(segments(JOB/'ready/plate_1.gcode'))
    model=[s for s in roads if not s['feature'].startswith('Support') and s['feature'] not in ('Brim','Custom','Prime tower')]
    nameplate=[s for s in model if s['object']==2303];receiver=[s for s in model if s['object']==2305]
    white=sorted({s['layer'] for s in nameplate if s['tool']==1});assert white==[.2,.44,.68]
    assert {s['tool'] for s in receiver}=={0}
    walls=wall_layers(native,2303)
    fine=[(z,h) for z,h in walls if abs(h-.24)>.001];assert fine==[(.2,.2),(5.17,.17)]
    hooks=[s['layer'] for s in nameplate if s['layer']>5 and s['feature'] in ('Inner wall','Outer wall','Overhang wall')
           and max(abs(p[0]-165) for p in (s['a'],s['b']))>43]
    first=min(hooks);bearing=first-dict(walls)[first];assert abs(bearing-11.65)<.001
    supports=[s for s in roads if s['feature'].startswith('Support')]
    contacts=[]
    for side in (-1,1):
        points=[]
        for s in supports:
            if s['object']!=2303 or not 0<=bearing-s['layer']<=.6:continue
            for point in (s['a'],s['b']):
                x=side*(point[0]-165);y=point[1]-125
                if x+s['width']/2>=41.65 and x-s['width']/2<=45.25 and abs(y)<=16:
                    points.append((y,bearing-s['layer']))
        assert len(points)>10
        low,high=min(p[0] for p in points),max(p[0] for p in points)
        gap=min(p[1] for p in points)
        assert high-low>29 and abs(gap-.24)<.001,(side,low,high,gap)
        contacts.append({'side':side,'span_mm':[low,high],'support_top_gap_mm':gap})
    support=audit(JOB/'ready/plate_1.gcode','nameplate-broad-leaf-and-receiver',profile=staged,include_unlabelled_support=True)
    for tree in support['trees']:
        is_plate=tree['bbox_xy_mm'][1]<170
        tree['part']='Nameplate' if is_plate else 'Receiver'
        tree['removal_lane']='Outward from the fully exposed hook face.' if is_plate else 'Open receiver face, back and outer ends before inserting the nameplate.'
    assert sum(t['part']=='Nameplate' for t in support['trees'])==2
    (JOB/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    bounds={}
    for oid in (2303,2305):
        pts=np.array([p for r in roads if r['object']==oid for p in (r['a'],r['b'])])
        low=pts.min(axis=0)-.6;high=pts.max(axis=0)+.6
        margin=float(min(*(low-[25,0]),*([325,320]-high)));assert margin>=15
        bounds[str(oid)]=[low.tolist(),high.tolist()]
    a,b=[np.array(bounds[str(oid)]) for oid in (2303,2305)]
    gap=float(np.linalg.norm(np.maximum(0,np.maximum(a[0]-b[1],b[0]-a[1]))));assert gap>10
    # Read the first layer from the visible, plate-facing side.
    scale=20;lo=np.array([110.,103.]);hi=np.array([220.,147.])
    im=Image.new('RGB',tuple(((hi-lo)*scale).astype(int)),'#777777');draw=ImageDraw.Draw(im)
    for r in nameplate:
        if r['layer']!=.2:continue
        a,b=[tuple(((np.array(p)-lo)*scale).round().astype(int)) for p in (r['a'],r['b'])]
        color='white' if r['tool'] else 'black';width=max(1,round(r['width']*scale))
        draw.line((a,b),fill=color,width=width)
        for x,y in (a,b):draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=color)
    ImageOps.flip(ImageOps.mirror(im)).save(JOB/'first-layer.png')
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    proof={'pass':True,'native_archive':str(native.relative_to(ROOT)),'native_archive_sha256':sha(native),
           'gcode_sha256':hashlib.sha256(gc).hexdigest(),'source_hashes_current':True,
           'native_export_metadata_normalizations':differences,'other_settings_match_input':True,
           'first_hook_layer_print_z_mm':first,'emitted_hook_bearing_bottom_z_mm':bearing,
           'white_artwork_layers_mm':white,'receiver_uses_black_left':True,'hook_support_contacts':contacts,
           'support_summary':support['summary'],'model_and_support_bounds_xy_mm':bounds,'object_gap_mm':gap,
           'emitted_z_trim_mm':trims,'estimated_seconds':sliced['total_predication'],
           'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
           'layer_count':int(re.search(rb'; total layer number: (\d+)',gc)[1]),'printer':'Mark2','submitted':False}
    (JOB/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('pass','emitted_hook_bearing_bottom_z_mm','estimated_seconds','layer_count')},indent=2))


if __name__=='__main__':main()
