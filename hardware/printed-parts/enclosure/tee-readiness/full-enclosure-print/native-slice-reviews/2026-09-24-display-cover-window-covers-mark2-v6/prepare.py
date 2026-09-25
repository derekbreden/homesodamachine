"""Prepare one machine display cover and both front-top window covers; never sends."""
from pathlib import Path
import hashlib, json, subprocess, sys, zipfile
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

STEM = 'display-cover-window-covers-black-z004-mark2-v6'
PROFILE = ROOT/'hardware/printed-parts/petgf.3mf'
STAGED = JOB/(STEM+'-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not STAGED.exists()
assert sha(PROFILE) == '3864deceaa295d0fffded05e445b77ee926e2706d8765fdc8bbf81a23fe98697'

cover = ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.stl'
parts = [('display-cover', cover, 180.)]
hashes = {str(p.relative_to(ROOT)): sha(p) for p in (
    cover, cover.with_suffix('.step'), cover.with_name('display_cover.py'),
    ROOT/'hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py',
    ROOT/'hardware/printed-parts/enclosure/enclosure/_display_retention.py',
    ROOT/'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
    ROOT/'hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py',
    ROOT/'hardware/manifold-layout/enclosure-box.json')}
orientation = []
oriented_dir = JOB/'oriented-meshes'
oriented_dir.mkdir(exist_ok=True)
for side, rotation in (
    ('east', np.array([[0,0,1],[0,1,0],[-1,0,0]], dtype=float)),
    ('west', np.array([[0,0,-1],[0,1,0],[1,0,0]], dtype=float))):
    name = 'enclosure-window-cover-'+side
    source = ROOT/'hardware/printed-parts/enclosure/tee-carrier'/f'{name}.stl'
    for p in (source, source.with_suffix('.step')):
        hashes[str(p.relative_to(ROOT))] = sha(p)
    mesh = trimesh.load_mesh(source)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    initial = mesh.vertices.copy()
    mesh.vertices = initial @ rotation.T
    assert np.array_equal(mesh.vertices @ rotation, initial)
    oriented = oriented_dir/source.name
    mesh.export(oriented)
    reread = trimesh.load_mesh(oriented)
    assert np.array_equal(np.sort(reread.vertices, axis=0), np.sort(mesh.vertices, axis=0))
    orientation.append({'name': name, 'source': str(source.relative_to(ROOT)),
                        'source_sha256': sha(source), 'rotation_matrix': rotation.tolist(),
                        'oriented_source': str(oriented.relative_to(ROOT)),
                        'oriented_sha256': sha(oriented),
                        'rigid_transform_vertex_recovery_exact': True,
                        'orientation': 'Outboard face down; tongue and both slabs on bed'})
    parts.append((name, oriented, 0.))

report = writer.refresh(PROFILE, STAGED, parts=tuple(parts),
    offsets=((0.,-30.),(42.,45.),(-42.,45.)),
    title='Display cover inset snaps and both window covers; Mark2', z_trim=.04, plate_border=15.)
with zipfile.ZipFile(STAGED) as z:
    members = {n:z.read(n) for n in z.namelist()}
settings = json.loads(members[writer.SETTINGS_MEMBER])
overrides = {'extruder_ams_count':['1#0|4#0','1#0|4#0'],
             'support_remove_small_overhang':'0','support_top_z_distance':'0.24'}
settings.update(overrides)
assert settings['layer_height'] == '0.24' and settings['initial_layer_print_height'] == '0.2'
assert settings['wall_loops'] == '2' and settings['wall_sequence'] == 'inner wall/outer wall'
assert settings['is_infill_first'] == '0' and settings['infill_wall_overlap'] == '15%'
assert settings['brim_type'] == 'auto_brim'
assert settings['filament_nozzle_map'] == ['0'] and settings['filament_colour'] == ['#000000']
members[writer.SETTINGS_MEMBER] = (json.dumps(settings,indent=2)+'\n').encode()
writer.archive_write(STAGED,members)
report.update({'project_sha256':sha(STAGED),
    'settings_sha256':hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
    'intentional_process_and_mapping_overrides':overrides,
    'source_geometry_and_settings_sha256':hashes,
    'window_cover_orientation':orientation,
    'printer':'Mark2','requested_z_trim_mm':.04,
    'geometry_change':'Display-cover retaining skirts inset 0.3 mm each; original bezel and fixed housing unchanged. Both window covers use existing geometry.',
    'support_policy':'Display-cover square catch faces retain removable external supports. Both window covers lie on their outboard faces and need no supports. No model has show rounds varying in print Z.',
    'submitted':False})
(JOB/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
ready = JOB/'ready'
ready.mkdir(exist_ok=True)
command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
           '--slice','0','--arrange','0','--orient','0','--outputdir',str(ready),
           '--export-3mf',STEM+'.gcode.3mf',str(STAGED)]
(JOB/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
with (ready/'bambu-cli.log').open('w') as log:
    rc = subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
print('SLICE_EXIT',rc,flush=True)
raise SystemExit(rc)
