"""Front-bottom handhold support paint and scoped six-wall band."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon,mapping
from shapely import polygons,union_all

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
BASE=ROOT/'.cache/prints/2026-09-24-enclosure-front-bottom-h2c-v6'
STEM='enclosure-front-bottom-black-z018-h2c-v7-six-wall-handhold-rounds'
source=next(BASE.glob('*-input.3mf'));target=JOB/(STEM+'-input.3mf')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='88d61b33aec4e0b9175ddeb526cffa452958dee78f39deb3d804f88e6dc49b46'
assert not target.exists()
baseprep=json.loads((BASE/'preparation.json').read_text())
hashes={k:v for k,v in baseprep['input_sha256'].items() if k.endswith(('.stl','.step'))}
for p,h in hashes.items():assert sha(ROOT/p)==h,p
with zipfile.ZipFile(source) as z:members={n:z.read(n) for n in z.namelist()}
original=dict(members)
settings=json.loads(members['Metadata/project_settings.config'])
assert settings['wall_loops']=='2' and settings['is_infill_first']=='0'
assert settings['wall_sequence']=='inner wall/outer wall' and settings['infill_wall_overlap']=='15%'
assert settings['enable_support']=='1' and settings['initial_layer_print_height']=='0.2'
ranges=ET.fromstring(members['Metadata/layer_config_ranges.xml'])
obj=ranges.find('object');bands=obj.findall('range')
assert len(bands)==1 and bands[0].get('min_z')=='29.1500' and bands[0].get('max_z')=='44.3000'
bands[0].set('max_z','41.3000')
ET.SubElement(bands[0],'option',opt_key='wall_loops').text='6'
upper=ET.SubElement(obj,'range',min_z='41.3000',max_z='44.3000')
ET.SubElement(upper,'option',opt_key='layer_height').text='0.08'
members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
tag=lambda n:'{'+NS+'}'+n
member='3D/Objects/object_1.model';tree=ET.fromstring(members[member])
vertices=np.array([[float(v.get(a)) for a in ['x','y','z']] for v in tree.iter(tag('vertex'))])
triangles=list(tree.iter(tag('triangle')))
indices=np.array([[int(t.get(a)) for a in ['v1','v2','v3']] for t in triangles])
cad=vertices+[0,108.7750015258789,84.4000015258789]
pts=cad[indices]
normals=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);lengths=np.linalg.norm(normals,axis=1)
nz=normals[:,2]/np.maximum(lengths,1e-30)
flat=((np.abs(pts[:,:,2]-29.25)<.0001).all(axis=1)&(nz<-.99)
      &(np.abs(pts[:,:,0])>=90.4999).all(axis=1)&(pts[:,:,1]>=179.9999).all(axis=1))
assert flat.sum()==12
rounds=((np.abs(pts[:,:,0])>=93.4999).all(axis=1)&(pts[:,:,1]>=167.9).all(axis=1)
        &(pts[:,:,1]<=200.0001).all(axis=1)&(pts[:,:,2]>=23.2499).all(axis=1)
        &(pts[:,:,2]<=38.3).all(axis=1)&(nz<-.00001)&~flat)
assert int(rounds.sum())==15984
assert not any(t.get('paint_supports') for t in triangles)
flat_area=union_all(polygons(pts[flat][:,:,:2]))
inset_area=flat_area.buffer(-.8)
leaves=[]
def encode(p,depth=0):
    poly=Polygon(p[:,:2])
    if inset_area.covers(poly):leaves.append((p,0));return '0'
    if not inset_area.intersects(poly) or depth==8:leaves.append((p,8));return '8'
    a,b,c=p;ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
    children=[np.array([a,ab,ca]),np.array([ab,b,bc]),np.array([bc,c,ca]),np.array([ab,bc,ca])]
    return ''.join(encode(q,depth+1) for q in children)+'3'
flat_codes=[]
for i,t in enumerate(triangles):
    if rounds[i]:t.set('paint_supports','8')
    elif flat[i]:
        code=encode(pts[i]);t.set('paint_supports',code)
        flat_codes.append({'triangle':i,'paint_nibbles':len(code)})
members[member]=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for n,p in members.items():z.writestr(n,p)
changed=[n for n in original if members[n]!=original[n]]
assert set(changed)=={member,'Metadata/layer_config_ranges.xml'}
config=json.loads((BASE/'job-config.json').read_text())
config.update(status='prepared',archive_stem=STEM,title='Front-bottom; complete fine handhold rounds; six walls through downward curves; rounded faces unsupported; H2C')
config['layer_ranges_mm']['enclosure-front-bottom']=[
 {'min_z':29.15,'max_z':41.3,'layer_height':.08,'settings_overrides':{'wall_loops':'6'},'reason':'Complete downward R6 handhold rounds span print Z29.25–41.25.'},
 {'min_z':41.3,'max_z':44.3,'layer_height':.08,'reason':'Visible flute run-outs above the R6 rounds end at print Z44.25; normal two-wall setting.'}]
config['support_policy']='Block all downward handhold rounds; inset flat-ceiling support contact 0.8 mm; retain functional ceilings and seam catches.'
(JOB/'job-config.json').write_text(json.dumps(config,indent=2)+'\n')
paint={}
for label,side in [('west',-1),('east',1)]:
    mask=rounds&(pts[:,:,0].mean(axis=1)*side>0);p=pts[mask].reshape(-1,3)
    paint[label]={'triangles':int(mask.sum()),'cad_bounds_mm':[p.min(axis=0).tolist(),p.max(axis=0).tolist()]}
prep={'reference_input':str(source.relative_to(ROOT)),'reference_input_sha256':sha(source),'staged_input':str(target.relative_to(ROOT)),'staged_input_sha256':sha(target),
      'source_geometry_sha256':hashes,'changed_archive_members':changed,'geometry_vertices_triangle_indices_and_placement_identical':True,
      'global_settings_identical_including_speed_acceleration_temperatures_and_fans':True,'normal_wall_loops':2,'downward_round_wall_loops':6,'six_wall_band_mm':[29.15,41.3],
      'fine_layer_band_mm':[29.15,44.3],'layer_height_profile_identical':True,'blocked_rounds':paint,'blocked_round_triangle_indices':np.flatnonzero(rounds).tolist(),
      'flat_ceiling_cad_z_mm':29.25,'flat_ceiling_support_inset_mm':.8,'flat_ceiling_geometry':mapping(flat_area),'ceiling_painted_source_facets':flat_codes,
      'native_painting_example':'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-pump-cartridge-cap-mark2-v8/prepare.py',
      'printer':'H2C','requested_z_trim_mm':.18,'expected_textured_plate_trim_mm':.16}
(JOB/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
print(json.dumps({'staged_input_sha256':sha(target),'blocked_round_triangles':int(rounds.sum()),'ceiling_facets':len(flat_codes)}),flush=True)
with (JOB/'ready/bambu-cli.log').open('w') as log:
    rc=subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(JOB/'ready'),'--export-3mf',STEM+'.gcode.3mf',str(target)],cwd=JOB/'ready',stdout=log,stderr=subprocess.STDOUT).returncode
print('SLICE_EXIT',rc,flush=True)
raise SystemExit(rc)
