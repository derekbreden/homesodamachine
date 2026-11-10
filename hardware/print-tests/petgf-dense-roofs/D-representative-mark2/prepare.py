"""prepare.py slices the production support crops with D contact treatment and Mark2's own trim."""
import importlib.util
import io
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
source = ROOT/'hardware/print-tests/enclosure-support-scenarios/prepare.py'
spec = importlib.util.spec_from_file_location('D_representative_plate',source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.HERE = HERE
module.RUN = ROOT/'.cache/runs/D-representative-mark2-2026-11-09'
module.TITLE = '2026-11-09-D-faucet-arch-pad-left04-z004-mark2'
module.EXAMPLE = 'D-representative-mark2'
native_package = module.package


def mark2_package():
    project, cli = native_package()
    spec = json.loads((HERE/'samples.json').read_text())
    for path in (project,cli):
        with zipfile.ZipFile(path) as archive:
            members = {name:archive.read(name) for name in archive.namelist()}
        settings = json.loads(members['Metadata/project_settings.config'])
        start = settings['machine_start_gcode']
        if start.count('Z{0.18') != 4:
            raise ValueError('Expected the retained Mark1 trim expressions in the D source profile')
        settings['machine_start_gcode'] = start.replace('Z{0.18','Z{0.04')
        settings.update(spec['machine_overrides'])
        members['Metadata/project_settings.config'] = (json.dumps(settings,indent=2)+'\n').encode()
        for name,data in list(members.items()):
            if name.startswith('Metadata/filament_settings_'):
                filament = json.loads(data)
                if 'filament_colour' in filament:
                    filament['filament_colour'] = spec['machine_overrides']['filament_colour']
                    members[name] = (json.dumps(filament,indent=2)+'\n').encode()
        out = io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in members.items():
                archive.writestr(name,data)
        path.write_bytes(out.getvalue())
    record = json.loads((HERE/'preparation.json').read_text())
    record.update(project_sha256=module.digest(project),machine_overrides=spec['machine_overrides'],
                  requested_z_trim_mm=spec['requested_z_trim_mm'])
    (HERE/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    return project,cli


module.package = mark2_package

if __name__=='__main__':
    module.main()
