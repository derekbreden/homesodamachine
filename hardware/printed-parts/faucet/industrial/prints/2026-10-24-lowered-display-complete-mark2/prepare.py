"""Prepare the authorized complete Industrial faucet with the reviewed low head.

Manual preparation only. This imports the reviewed tip and printable cover,
retains the three other production parts and selected support/finish recipe,
and never connects to a printer.
"""
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
INDUSTRIAL = HERE.parents[1]
REVIEW = INDUSTRIAL / 'display-seat-review/2026-10-24'
STEM = '2026-10-24-industrial-complete-display-low45-petgf-left04-z004-mark2'
sys.path.insert(0, str(INDUSTRIAL))
import prepare_print_project as industrial
writer = industrial.writer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plate', choices=('textured', 'engineering'), required=True)
    args = parser.parse_args()
    project = HERE / (STEM + '.3mf')
    if (HERE / 'launch.json').exists():
        raise ValueError('Preserve submitted artifacts; use a new print directory.')
    review = json.loads((REVIEW / 'geometry-review.json').read_text())
    cache = ROOT / '.cache/printer-control/2026-10-24-industrial-low-display-mark2'
    cache.mkdir(parents=True, exist_ok=True)
    with ZipFile(industrial.RECIPE) as source:
        members = {n: source.read(n) for n in source.namelist()
                   if n == writer.SETTINGS_MEMBER
                   or n.startswith('Metadata/filament_settings_') and n.endswith('.config')}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings['curr_bed_type'] = {'textured': 'Textured PEI Plate',
                                 'engineering': 'Engineering Plate'}[args.plate]
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + '\n').encode()
    profile = cache / 'source-profile.3mf'
    writer.archive_write(profile, members)
    parts = industrial.industrial_parts()
    selected = tuple((name, REVIEW / ('candidate-tip.stl' if name == 'faucet-shell-tip'
                                    else 'candidate-cover.stl'), rotation)
                     if name in ('faucet-shell-tip', 'industrial-display-cover')
                     else (name, source, rotation) for name, source, rotation in parts)
    with patch.object(industrial, 'industrial_parts', lambda: selected):
        report = industrial.refresh(profile, project, 'Mark2', '#161616')
    report.update({
        'authorization_quote': 'Alright, mark2 is available, please give me a new complete industrial faucet print',
        'launch_authorized': True,
        'complete_faucet_scope': 'One of each of the five rigid PET-GF parts on Mark2.',
        'reviewed_geometry': str(REVIEW.relative_to(ROOT)),
        'review_geometry_sha256': writer.digest((REVIEW / 'geometry-review.json').read_bytes()),
        'display_drop_mm': review['total_display_and_bezel_drop_mm'],
        'display_foot_recess_depth_mm': review['recess_depth_below_former_support_base_mm'],
        'display_foot_recess_diameter_mm': review['recess_diameter_mm'],
        'selected_plate': settings['curr_bed_type'],
        'physical_fit_scope': 'First complete fit print of the reviewed 4.5 mm lower display head. The conservative component/tube and component/tip overlaps in the review remain modeled evidence; physical fit is unmeasured.',
    })
    report['source_sha256'][str(Path(__file__).relative_to(ROOT))] = writer.digest(Path(__file__).read_bytes())
    project.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'project': str(project.relative_to(ROOT)), 'bed': settings['curr_bed_type'],
                      'parts': [{'name': p['name'], 'source': p['source'],
                                 'sha256': p['stl_sha256']} for p in report['parts']]}, indent=2), flush=True)


if __name__ == '__main__':
    main()
