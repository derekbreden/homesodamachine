"""Prepare the complete requested faucet with switch relief and a Sculpted cover."""
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
import json
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
INDUSTRIAL = HERE.parents[1]
FAUCET = INDUSTRIAL.parent
ROOT = FAUCET.parents[2]
REVIEW = FAUCET / 'faucet-display-cover/fit-review/2026-10-24'
PREVIOUS = INDUSTRIAL / 'prints/2026-10-24-sculpted-cover-uniform024-mark2'
STEM = '2026-10-24-industrial-sculpted-buttons-bands020v2-black-left04-z004-mark2'
sys.path.insert(0, str(INDUSTRIAL))
import prepare_print_project as industrial
writer = industrial.writer


def main():
    if (HERE / 'launch.json').exists():
        raise ValueError('Preserve submitted artifacts; prepare a new directory.')
    parts = tuple((name, REVIEW / ('corrected-tip.stl' if name == 'faucet-shell-tip'
                                  else 'corrected-sculpted-cover.stl'), rotation)
                  if name in ('faucet-shell-tip', 'industrial-display-cover') else (name, source, rotation)
                  for name, source, rotation in industrial.industrial_parts())
    profile = PREVIOUS / '2026-10-24-industrial-sculpted-cover-low45-uniform024-black-left04-z004-mark2.3mf'
    project = HERE / (STEM + '.3mf')
    with patch.object(industrial, 'industrial_parts', lambda: parts):
        report = industrial.refresh(profile, project, 'Mark2', '#161616')
    with ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    old, new = 'industrial-display-cover', 'sculpted-display-cover'
    cover = next(p for p in report['parts'] if p['name'] == old)
    for name in ('Metadata/model_settings.config', '3D/3dmodel.model', cover['member']):
        tree = ET.fromstring(members[name])
        for node in tree.iter():
            if node.get('key') == 'name' and node.get('value') == old:
                node.set('value', new)
            if node.get('name') == old:
                node.set('name', new)
        members[name] = writer.xml(tree)
    cover['name'] = new
    writer.archive_write(project, members)
    report.update(project_sha256=writer.digest(project.read_bytes()),
                  display_drop_mm=4.5, display_foot_recess_depth_mm=1.,
                  button_recess_depth_mm=1., button_nominal_floor_clearance_mm=.6,
                  cover_style='Sculpted', cover_reach_extension_mm=.5,
                  cover_nominal_glass_clearance_mm=.6, cover_nominal_arch_clearance_mm=.65,
                  authorization_quote='Mark2 bed is clear, start your next print when you’re ready.',
                  launch_authorized=True, physical_fit_validated=False)
    for source in (Path(__file__), REVIEW / 'measure.py', REVIEW / 'button_relief.py',
                   REVIEW / 'native-review.json', REVIEW / 'button-review.json'):
        report['source_sha256'][str(source.relative_to(ROOT))] = writer.digest(source.read_bytes())
    project.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    industrial.write_readiness(project, report)
    print(project, flush=True)


if __name__ == '__main__':
    main()
