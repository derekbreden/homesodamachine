"""Keep the grip rounds unsupported and reinforce only the upper rounded band."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB = Path(__file__).resolve().parent
BASE = ROOT/'.cache/prints/2026-09-23-pump-cartridge-cap-mark2-v6'
STEM = 'pump-cartridge-cap-black-z004-mark2-v7-six-wall-grip-rounds'
source = BASE/'pump-cartridge-cap-black-z004-mark2-v6-input.3mf'
target = JOB/(STEM+'-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source) == '8123110feda4b94099972923448ce51e9c2139b05fdb6240ef646bb4ae805201'
assert not target.exists()
config = json.loads((BASE/'job-config.json').read_text())
expected = {
 'enclosure-pump-cartridge.stl': 'a8bec3fc0b63d15aafdcf6edb2c73e4e4802099c9b6d67cb515a04f4b53b57d2',
 'enclosure-pump-cartridge.step': '052433c3907fc2ae4cc99fe876994b3697d82b1de93acdee506aed71d0531186',
 'enclosure-pump-cap.stl': 'f5f98bf2942457b74e223a087b180717b3614fae5a89b04ffb5d24c7e8c9e063',
 'enclosure-pump-cap.step': 'fc0bf27eff36d906f8f83d744ab5a1d7d0fef11b7caa770afc81c5467241b4f4',
}
source_hashes = {}
for part in config['parts']:
    for kind in ['stl','step']:
        p = ROOT/part[kind]
        assert sha(p) == expected[p.name], str(p)
        source_hashes[part[kind]] = sha(p)
with zipfile.ZipFile(source) as z:
    members = {n:z.read(n) for n in z.namelist()}
original = dict(members)
settings = json.loads(members['Metadata/project_settings.config'])
assert settings['wall_loops'] == '2'
assert settings['wall_sequence'] == 'inner wall/outer wall'
assert settings['is_infill_first'] == '0'
assert settings['infill_wall_overlap'] == '15%'
assert settings['enable_support'] == '1'
assert settings['nozzle_temperature'][0] == '280'
ranges = ET.fromstring(members['Metadata/layer_config_ranges.xml'])
bands = ranges.findall('./object/range')
assert [(float(r.get('min_z')),float(r.get('max_z'))) for r in bands] == [(6.0,18.4),(100.3,113.2)]
ET.SubElement(bands[1], 'option', opt_key='wall_loops').text = '6'
members['Metadata/layer_config_ranges.xml'] = ET.tostring(ranges, encoding='utf-8', xml_declaration=True)

NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
tag = lambda n: '{'+NS+'}'+n
mesh_member = '3D/Objects/object_1.model'
tree = ET.fromstring(members[mesh_member])
vertices = np.array([[float(v.get(a)) for a in ['x','y','z']] for v in tree.iter(tag('vertex'))])
triangles = list(tree.iter(tag('triangle')))
indices = np.array([[int(t.get(a)) for a in ['v1','v2','v3']] for t in triangles])
cad = vertices + np.array([0,42.134498596191406,224.68450927734375])
pts = cad[indices]
normals = np.cross(pts[:,1]-pts[:,0], pts[:,2]-pts[:,0])
lengths = np.linalg.norm(normals,axis=1)
nz = normals[:,2]/np.maximum(lengths,1e-30)
# These bounds are the STEP's complete ten downward R6 grip faces. Keep the
# two planar hand-bearing roofs at Z272.194, X91.75..101.5, Y34.1325..50.1325.
in_round_box = ((np.abs(pts[:,:,0]) >= 91.7499).all(axis=1)
                & (pts[:,:,1] >= 22.1324).all(axis=1)
                & (pts[:,:,1] <= 62.1326).all(axis=1)
                & (pts[:,:,2] >= 266.1939).all(axis=1)
                & (pts[:,:,2] <= 278.1941).all(axis=1))
flat_roof = (np.abs(pts[:,:,2]-272.1940001) < .0001).all(axis=1)
selected = in_round_box & (nz < -0.00001) & ~flat_roof
assert selected.sum() > 1000
assert (flat_roof & (nz < -.99)).sum() >= 4
assert not any(t.get('paint_supports') for t in triangles)
for t, use in zip(triangles,selected):
    if use:
        t.set('paint_supports','8')
members[mesh_member] = ET.tostring(tree,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for name,payload in members.items(): z.writestr(name,payload)
changed = [n for n in members if members[n] != original[n]]
assert set(changed) == {mesh_member,'Metadata/layer_config_ranges.xml'}
rounds = {}
for label,side in [('west',-1),('east',1)]:
    mask = selected & ((pts[:,:,0].mean(axis=1)*side)>0)
    p=pts[mask].reshape(-1,3)
    rounds[label]={'triangles':int(mask.sum()),'cad_bounds_mm':[p.min(axis=0).tolist(),p.max(axis=0).tolist()], 'surface_area_mm2':float(lengths[mask].sum()/2)}
config.update(status='prepared', archive_stem=STEM,
    title='Pump cartridge and cap; unsupported 0.08 mm grip rounds; six walls only in upper grip band; original order and speeds; Mark2')
config['layer_ranges_mm']['enclosure-pump-cartridge'][1]['settings_overrides']={'wall_loops':'6'}
config['support_policy']='Painted blockers on both complete downward grip rounds; support retained for flat grip ceilings and cap seats.'
(JOB/'job-config.json').write_text(json.dumps(config,indent=2)+'\n')
prep={'reference_input':str(source.relative_to(ROOT)), 'reference_input_sha256':sha(source),
      'staged_input':str(target.relative_to(ROOT)), 'staged_input_sha256':sha(target),
      'source_input_sha256':source_hashes, 'changed_archive_members':changed,
      'global_settings_identical':True, 'geometry_vertices_and_triangles_identical':True,
      'placement_identical':True, 'layer_heights_identical':True,
      'upper_grip_band_mm':[100.3,113.2], 'upper_grip_band_wall_loops':6, 'normal_wall_loops':2,
      'wall_sequence':'inner wall/outer wall', 'is_infill_first':False,'infill_wall_overlap':'15%',
      'speed_acceleration_temperature_and_cooling_settings_identical':True,
      'triangle_annotation':'paint_supports="8"', 'blocked_rounds':rounds,
      'retained_flat_ceiling_cad_z_mm':272.1940001, 'printer':'Mark2','requested_z_trim_mm':.04}
(JOB/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
print(json.dumps(prep,indent=2),flush=True)
ready=JOB/'ready'
with (ready/'bambu-cli.log').open('w') as log:
    result=subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(ready),'--export-3mf',STEM+'.gcode.3mf',str(target)],cwd=ready,stdout=log,stderr=subprocess.STDOUT)
print('SLICE_EXIT',result.returncode,flush=True)
raise SystemExit(result.returncode)
