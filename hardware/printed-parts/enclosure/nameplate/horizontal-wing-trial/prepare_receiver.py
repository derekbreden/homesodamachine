"""Slice the receiver in back-top's build direction with the shared tree profile."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB=ROOT/'.cache/prints/2026-09-29-nameplate-tip025-receiver-mark2-v6'
STEM='nameplate-tip025-receiver-tree-z004-mark2-v6'
NAME='nameplate-horizontal-wings-receiver'
PROFILE=ROOT/'hardware/printed-parts/petgf.3mf'
ENCLOSURE=HERE.parent.parent/'enclosure/enclosure.py'

def support_settings(settings):
    """All tree and interface settings, including clearance and support speeds."""
    return {k:v for k,v in settings.items()
            if k.startswith(('support_', 'tree_support_'))
            or k in ('enable_support', 'independent_support_layer_height')}

def main():
    staged=JOB/(STEM+'-input.3mf')
    assert not staged.exists(),'Keep reviewed jobs immutable.'
    source=HERE/(NAME+'.stl')
    declarations=ast.parse(ENCLOSURE.read_text())
    up=next(ast.literal_eval(n.value)['back-top'] for n in declarations.body
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and
               t.id=='PIECE_PRINT_UP' for t in n.targets))
    assert up==-1.,'Receiver build direction must follow its back-top enclosure wall.'
    report=writer.refresh(PROFILE,staged,parts=((NAME,source,180.),),
                          offsets=((0.,0.),),title='Nameplate receiver, 0.25 mm wing-tip clearance; Mark2',
                          z_trim=.04,plate_border=15.)
    with zipfile.ZipFile(staged) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    overrides={'extruder_ams_count':['1#0|4#0','1#0|4#0'],
               'support_filament':'1',
               'support_interface_filament':'1','flush_into_support':'0'}
    settings.update(overrides)
    with zipfile.ZipFile(PROFILE) as z: profile=json.loads(z.read(writer.SETTINGS_MEMBER))
    support_diff={k:{'profile':profile[k],'receiver':v}
                  for k,v in support_settings(settings).items() if profile[k]!=v}
    assert set(support_diff)=={'support_filament','support_interface_filament'}
    assert settings['support_type']=='tree(auto)' and settings['support_style']=='default'
    assert settings['layer_height']=='0.24' and settings['initial_layer_print_height']=='0.2'
    assert settings['filament_nozzle_map']==['0'] and settings['filament_colour']==['#000000']
    members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
    writer.archive_write(staged,members)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    sources=[source,source.with_suffix('.step'),HERE/'geometry-check.json',HERE/'wing_interface.py',Path(__file__),PROFILE,ENCLOSURE]
    report.update(project_sha256=sha(staged),printer='Mark2',
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  intentional_overrides=overrides,requested_z_trim_mm=.04,expected_textured_plate_trim_mm=.02,
                  wing_tip_clearance_mm=.25,
                  orientation='CAD -Z up (X180), matching back-top roof-down orientation; slots open to the face.',
                  enclosure_build_direction=up,
                  inherited_support_settings=support_settings(settings),
                  support_profile_differences=support_diff,
                  support_policy='Shared petgf.3mf tree supports and clearances; support and interface explicitly black. Verify emitted slot access.',
                  qualification='Insertion flex, retention and removal remain physical tests.')
    (JOB/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    ready=JOB/'ready';ready.mkdir()
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
             '--outputdir',str(ready),'--export-3mf',STEM+'.gcode.3mf',str(staged)]
    (JOB/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT',rc,flush=True)
    return rc

if __name__=='__main__':raise SystemExit(main())
