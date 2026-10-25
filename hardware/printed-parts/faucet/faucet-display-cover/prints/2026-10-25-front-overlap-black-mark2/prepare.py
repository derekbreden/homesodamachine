"""Prepare one front-overlap cover with the physically accepted print recipe."""
from pathlib import Path
from zipfile import ZipFile
import json
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
FAUCET = ROOT / 'hardware/printed-parts/faucet'
REVIEW = FAUCET / 'faucet-display-cover/corner-overlap-review/2026-10-25'
SOURCE = FAUCET / 'industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/2026-10-24-industrial-sculpted-buttons-bands020v2-black-left04-z004-mark2.3mf'
STEM = '2026-10-25-sculpted-cover-front-overlap-black-left04-z004-mark2'
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer


def main():
    if (HERE / 'launch.json').exists():
        raise ValueError('Preserve submitted print artifacts.')
    stl = REVIEW / 'proposed-cover.stl'
    native = json.loads((REVIEW / 'native-review.json').read_text())
    assert writer.digest(stl.read_bytes()) == native['candidate_sha256'][stl.name]
    project = HERE / (STEM + '.3mf')
    report = writer.refresh(SOURCE, project,
        parts=(('sculpted-display-cover', stl, -50.),), offsets=((0., 0.),),
        title=STEM, plate_border=80.)
    with ZipFile(project) as archive, ZipFile(SOURCE) as source:
        members = {n: archive.read(n) for n in archive.namelist()}
        source_config = ET.fromstring(source.read('Metadata/model_settings.config'))
        source_cover = next(o for o in source_config.findall('object')
            if o.find("metadata[@key='name']").get('value') == 'sculpted-display-cover')
        config = ET.fromstring(members['Metadata/model_settings.config'])
        target = config.find('object')
        for setting in source_cover.findall('metadata'):
            key = setting.get('key')
            if key and key not in ('name', 'extruder'):
                writer.metadata(target, key, setting.get('value'))
        members['Metadata/model_settings.config'] = writer.xml(config)
        members['Metadata/layer_config_ranges.xml'] = writer.xml(ET.Element('objects'))
        assert members[writer.SETTINGS_MEMBER] == source.read(writer.SETTINGS_MEMBER)
        assert all(members[n] == source.read(n) for n in members if n.startswith('Metadata/filament_settings_'))
    writer.archive_write(project, members)
    report.update(project_sha256=writer.digest(project.read_bytes()),
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        printer='Mark2', requested_z_trim_mm=.04, active_nozzle=0,
        first_bed_layer_height_mm=.24, layer_height_mm=.24, layer_ranges=[],
        complete_project_settings_preserved_byte_for_byte=True,
        cover_object_overrides_preserved=True,
        authorization_quote='Please print your recommended faucet display cover on mark2, the bed is clear and ready.',
        launch_authorized=True, submitted=False,
        geometric_review=str((REVIEW / 'native-review.json').relative_to(ROOT)),
        source_sha256={str(p.relative_to(ROOT)): writer.digest(p.read_bytes())
            for p in [Path(__file__), REVIEW / 'review.py', REVIEW / 'native-review.json', stl]})
    project.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    print(project, flush=True)


if __name__ == '__main__':
    main()
