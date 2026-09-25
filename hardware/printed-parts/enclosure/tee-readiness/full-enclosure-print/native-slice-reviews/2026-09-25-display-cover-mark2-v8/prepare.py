"""Slice the complete machine display cover, visible face down, for a fit trial."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
STEM='display-cover-black-z004-mark2-v8-inset-snaps-09'
PROFILE=ROOT/'hardware/printed-parts/petgf.3mf'
SOURCE=ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.stl'
STAGED=JOB/(STEM+'-input.3mf')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not STAGED.exists()
assert sha(PROFILE)=='3864deceaa295d0fffded05e445b77ee926e2706d8765fdc8bbf81a23fe98697'
sources=[SOURCE,SOURCE.with_suffix('.step'),SOURCE.with_name('display_cover.py'),
         ROOT/'hardware/printed-parts/enclosure/enclosure/_display_retention.py',
         ROOT/'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
         ROOT/'hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py']
hashes={str(p.relative_to(ROOT)):sha(p) for p in sources}
report=writer.refresh(PROFILE,STAGED,parts=(('display-cover',SOURCE,180.),),offsets=((0.,0.),),
                      title='Machine display cover; original perimeter; snaps inset 0.9 mm each; Mark2',z_trim=.04,plate_border=15.)
with zipfile.ZipFile(STAGED) as z:members={n:z.read(n) for n in z.namelist()}
settings=json.loads(members[writer.SETTINGS_MEMBER])
overrides={'extruder_ams_count':['1#0|4#0','1#0|4#0'],
           'support_remove_small_overhang':'0','support_top_z_distance':'0.24'}
settings.update(overrides)
assert settings['layer_height']=='0.24' and settings['initial_layer_print_height']=='0.2'
assert settings['wall_loops']=='2' and settings['wall_sequence']=='inner wall/outer wall' and settings['is_infill_first']=='0'
assert settings['infill_wall_overlap']=='15%' and settings['brim_type']=='auto_brim'
assert settings['filament_nozzle_map']==['0'] and settings['filament_colour']==['#000000']
members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
writer.archive_write(STAGED,members)
report.update({'project_sha256':sha(STAGED),'settings_sha256':hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
               'intentional_process_and_mapping_overrides':overrides,'source_geometry_and_settings_sha256':hashes,
               'orientation':'X180: visible face on plate, skirts up','printer':'Mark2','requested_z_trim_mm':.04,
               'geometry_change':'Both complete retaining skirts translated 0.9 mm toward center. Original bezel, window and housing receivers unchanged.',
               'support_policy':'Retain removable bed-rooted supports under the two square lip catch faces. Bezel corners are rounded in XY only; no fine print-Z round band.'})
(JOB/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
ready=JOB/'ready';ready.mkdir(exist_ok=True)
command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(ready),'--export-3mf',STEM+'.gcode.3mf',str(STAGED)]
(JOB/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
with (ready/'bambu-cli.log').open('w') as log:
    rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
print('SLICE_EXIT',rc,flush=True)
raise SystemExit(rc)
