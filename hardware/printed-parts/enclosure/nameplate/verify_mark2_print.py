"""Verify the native two-hotend nameplate job, colour paths and support access."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
JOB=ROOT/'.cache/prints/2026-09-20-nameplate-001-black-white-z004-mark2-v1'
DIRECTORY=JOB/'slice-2'
ARCHIVE=DIRECTORY/'nameplate-001-black-white-z004-mark2-v1.gcode.3mf'
PROJECT=HERE/'nameplate-001-petgf.3mf'
sys.path.insert(0,str(ROOT/'hardware/scripts'))
from enclosure_support_audit import audit,_WORD


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def segments(path):
    x=y=z=e=0.;tool=0;obj=None;feature='';layer=None;width=0.;absolute=True;relative_e=True
    for raw in path.read_text().splitlines():
        line=raw.strip()
        m=re.match(r'; start printing object, unique label id: (\d+)',line)
        if m:obj=int(m[1])
        elif line.startswith('; stop printing object'):obj=None
        elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        elif line.startswith('; Z_HEIGHT:'):layer=float(line.split(':',1)[1])
        elif line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
        code=line.split(';',1)[0].strip()
        if not code:continue
        m=re.match(r'^T([01])(?:\s|$)',code)
        if m:tool=int(m[1])
        command=code.split()[0];v={k:float(n) for k,n in _WORD.findall(code)}
        if command in ('G90','G91'):absolute=command=='G90'
        elif command in ('M82','M83'):relative_e=command=='M83'
        elif command=='G92':x,y,z,e=(v.get(k,old) for k,old in zip('XYZE',(x,y,z,e)))
        elif command in ('G0','G1','G2','G3'):
            nx,ny,nz=(v.get(k,old) if absolute else old+v.get(k,0) for k,old in zip('XYZ',(x,y,z)))
            de=v.get('E',0) if relative_e else v.get('E',e)-e
            if obj is not None and layer is not None and de>1e-9 and (nx!=x or ny!=y):
                assert command in ('G0','G1'),'Arc fitting must remain disabled'
                yield {'object':obj,'tool':tool,'layer':layer,'feature':feature,'width':width,'a':(x,y),'b':(nx,ny),'extrusion_mm':de}
            x,y,z=nx,ny,nz
            if 'E' in v:e=e+v['E'] if relative_e else v['E']


def main():
    report=json.loads(PROJECT.with_suffix('.print.json').read_text())
    assert sha(PROJECT)==report['project_sha256']
    assert sha(HERE/'nameplate-001.step')==report['source_step_sha256']
    assert sha(HERE/'nameplate-receiver.step')==report['receiver_step_sha256']
    result=json.loads((DIRECTORY/'result.json').read_text());assert result['return_code']==0
    plate,=result['sliced_plates'];assert not plate['warning_message'] and len(plate['objects'])==2
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        effective=json.loads(z.read('Metadata/project_settings.config'))
        gcode=z.read('Metadata/plate_1.gcode');assert z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()==hashlib.md5(gcode).hexdigest()
    for k,v in {'filament_map':['1','2'],'filament_nozzle_map':['0','1'],'filament_printable':['3','3'],'nozzle_diameter':['0.4','0.4'],'layer_height':'0.24','initial_layer_print_height':'0.2','support_top_z_distance':'0.24','enable_arc_fitting':'0'}.items():assert effective[k]==v,(k,effective[k])
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gcode,re.M)];assert trims==[0.,.02]
    config=dict(re.findall(rb'^; ([a-z0-9_]+) = ([^\n]*)',gcode,re.M))
    assert config[b'nozzle_temperature']==b'280,280' and config[b'nozzle_temperature_initial_layer']==b'265,265'
    path=DIRECTORY/'plate_1.gcode';path.write_bytes(gcode)
    roads=list(segments(path));model=[r for r in roads if not r['feature'].startswith('Support') and r['feature'] not in ('Brim','Custom','Prime tower')]
    nameplate=[r for r in model if r['object']==2303];receiver=[r for r in model if r['object']==2305]
    white_layers=sorted({r['layer'] for r in nameplate if r['tool']==1});assert white_layers==[.2,.44,.68],white_layers
    assert {r['tool'] for r in receiver}=={0}
    samples=[]
    for height in (5.,9.8,11.,11.24,11.48,11.72,11.96,12.2):
        chosen=[r for r in nameplate if abs(r['layer']-height)<.001]
        shape=unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in chosen])
        for x in (120.,210.):
            cut=shape.intersection(LineString(((x-5,122.5),(x+5,122.5))))
            pieces=[cut] if cut.geom_type=='LineString' else list(cut.geoms)
            bands=[g.bounds for g in pieces if not g.is_empty]
            band=next(b for b in bands if b[0]<=x<=b[2]);width=band[2]-band[0]
            assert width >= (1.2 if height<11.2 else 3.0),(height,x,width)
            samples.append({'z_mm':height,'tab':'left' if x<165 else 'right','toolpath_width_mm':width})
    support=audit(path,'nameplate-and-receiver',profile=PROJECT,include_unlabelled_support=True)
    for tree in support['trees']:
        is_plate=tree['bbox_xy_mm'][1]<170
        tree['part']='nameplate' if is_plate else 'receiver coupon'
        tree['removal_access']='Open beside the tab' if is_plate else 'Open from receiver front and rear before assembly'
    assert sum(t['part']=='nameplate' for t in support['trees'])==2
    support['physical_removal_tested']=False
    (HERE/'nameplate-001-petgf.support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    first=[r for r in nameplate if r['layer']==.2]
    scale=20;lo=np.array([110.,103.]);hi=np.array([220.,147.]);size=tuple(((hi-lo)*scale).astype(int))
    im=Image.new('RGB',size,'#777777');draw=ImageDraw.Draw(im)
    def point(p):return tuple(((np.array(p)-lo)*scale).round().astype(int))
    for r in first:
        color='white' if r['tool'] else 'black';width=max(1,round(r['width']*scale))
        a,b=point(r['a']),point(r['b']);draw.line((a,b),fill=color,width=width)
        # Extruded road ends are round, including at short infill segments.
        radius=width/2
        for x,y in (a,b):draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
    # The artwork is read from the underside of the printed bed face.
    im=ImageOps.flip(ImageOps.mirror(im));im.save(HERE/'mark2-first-layer.png')
    bounds={}
    for obj in (2303,2305):
        pts=np.array([p for r in roads if r['object']==obj for p in (r['a'],r['b'])]);low=pts.min(axis=0)-.5;high=pts.max(axis=0)+.5
        margin=float(min(*(low-np.array([25,0])),*(np.array([325,320])-high)));assert margin>=15
        bounds[str(obj)]={'bounds_xy_mm':[low.tolist(),high.tolist()],'shared_bed_margin_mm':margin}
    a,b=[np.array(bounds[str(obj)]['bounds_xy_mm']) for obj in (2303,2305)]
    gap=float(np.linalg.norm(np.maximum(0,np.maximum(a[0]-b[1],b[0]-a[1]))));assert gap>=10
    diagnostics=[line.split('[error]',1)[1].strip() for line in (DIRECTORY/'bambu-cli.log').read_text().splitlines() if '[error]' in line]
    allowed={'ZFiller: encounter idx from clip: 4','Invalid T command (T1001).','Invalid T command (T65535).','Invalid T command (T65279).'}
    assert not (set(diagnostics)-allowed),diagnostics
    record={'status':'native_geometry_and_toolpaths_pass_qr_and_live_mapping_pending','submitted':False,'printer':'Mark2','native_archive':str(ARCHIVE.relative_to(ROOT)),'native_archive_sha256':sha(ARCHIVE),'gcode_sha256':hashlib.sha256(gcode).hexdigest(),'project':str(PROJECT.relative_to(ROOT)),'project_sha256':sha(PROJECT),'source_step_sha256':report['source_step_sha256'],'receiver_step_sha256':report['receiver_step_sha256'],'source_profile':report['profile_source'],'source_profile_sha256':report['profile_sha256'],'physical_filament_mapping':report['physical_filament_mapping'],'hotend_compatibility_evidence':str((HERE/'petgf-hotend-compatibility.json').relative_to(ROOT)),'requested_z_trim_mm':.04,'actual_z_trim_commands_mm':trims,'estimated_seconds':plate['total_predication'],'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in plate['filaments']),'layers':int(re.search(rb'; total layer number: (\d+)',gcode)[1]),'white_artwork_layers_z_mm':white_layers,'black_receiver_verified':True,'tab_toolpath_sections':samples,'support_audit_sha256':sha(HERE/'nameplate-001-petgf.support-audit.json'),'toolpath_bounds':bounds,'object_separation_mm':gap,'native_log_diagnostics':diagnostics,'physical_fit_tested':False,'part_scope':'Unit 0001 production nameplate with matching receiver coupon for retention testing.'}
    record_path=HERE/'mark2-print-readiness.json'
    if record_path.exists():
        previous=json.loads(record_path.read_text())
        if previous.get('native_archive_sha256')==record['native_archive_sha256']:
            for key in ('status','submitted','qr_verification','live_preflight','printer_acknowledgement','print_progress','physical_fit_tested','physical_result'):
                if key in previous:record[key]=previous[key]
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('status','estimated_seconds','estimated_grams_saved_profile_density','layers','white_artwork_layers_z_mm','object_separation_mm')},indent=2))

if __name__=='__main__':main()
