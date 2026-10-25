"""Prepare one approved Sculpted faucet cover; never contacts a printer."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import json
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer


def prepare(project, printer='Mark2', colour=None):
    selection_path = FAUCET / 'industrial/production-selection.json'
    selection = json.loads(selection_path.read_text())
    row = next(p for p in selection['parts'] if p['name'] == 'sculpted-display-cover')
    source = ROOT / selection['settings_source']
    trim = {'Mark1': .18, 'Mark2': .04}[printer]
    report = writer.refresh(source, project,
        parts=((row['name'], ROOT / row['source'], row['rotation_x_degrees']),),
        offsets=((0., 0.),), title='Approved Sculpted faucet display cover',
        z_trim=trim, plate_border=80.)
    with ZipFile(project) as archive, ZipFile(source) as baseline:
        members = {n: archive.read(n) for n in archive.namelist()}
        reference = ET.fromstring(baseline.read('Metadata/model_settings.config')).find('object')
        config = ET.fromstring(members['Metadata/model_settings.config'])
        obj = config.find('object')
        for setting in reference.findall('metadata'):
            key = setting.get('key')
            if key and key not in ('name', 'extruder'):
                writer.metadata(obj, key, setting.get('value'))
        members['Metadata/model_settings.config'] = writer.xml(config)
        members['Metadata/layer_config_ranges.xml'] = writer.xml(ET.Element('objects'))
        settings = json.loads(members[writer.SETTINGS_MEMBER])
        settings['filament_colour'] = [colour or selection['recipe']['filament_colour']]
        members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + '\n').encode()
    writer.archive_write(project, members)
    report.update(project_sha256=writer.digest(project.read_bytes()),
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        printer=printer, requested_z_trim_mm=trim, active_nozzle=0,
        first_bed_layer_height_mm=.24, layer_height_mm=.24, layer_ranges=[],
        production_selection=str(selection_path.relative_to(ROOT)),
        physical_approval=selection['physical_result'],
        accepted_remaining_corner_gap=True, launch_authorized=False, submitted=False)
    project.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=HERE / 'faucet-display-cover-petgf.3mf')
    parser.add_argument('--printer', choices=('Mark1', 'Mark2'), default='Mark2')
    parser.add_argument('--filament-colour')
    args = parser.parse_args()
    result = prepare(args.project.resolve(), args.printer, args.filament_colour)
    print(f'{args.project}: approved cover; uniform 0.24 mm layers; {result["printer"]}')
