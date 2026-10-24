"""Prepare the requested Industrial set with a lowered Sculpted cover.

Manual local preparation; slicing and printer submission are separate actions.
"""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
INDUSTRIAL = HERE.parents[1]
FAUCET = INDUSTRIAL.parent
REVIEW = INDUSTRIAL / 'display-seat-review/2026-10-24'
PREVIOUS = INDUSTRIAL / 'prints/2026-10-24-lowered-display-complete-mark2'
STEM = '2026-10-24-industrial-sculpted-cover-low45-uniform024-black-left04-z004-mark2'
sys.path.insert(0, str(INDUSTRIAL))
import prepare_print_project as industrial
writer = industrial.writer
shell = writer.shell


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    if (HERE / 'launch.json').exists():
        raise ValueError('Preserve submitted artifacts; prepare a new print directory.')
    review = json.loads((REVIEW / 'geometry-review.json').read_text())
    tip = REVIEW / 'candidate-tip.stl'
    accepted = json.loads((PREVIOUS / '2026-10-24-industrial-complete-display-low45-petgf-left04-z004-mark2.print.json').read_text())
    expected = next(p['stl_sha256'] for p in accepted['parts'] if p['name'] == 'faucet-shell-tip')
    assert writer.digest(tip.read_bytes()) == expected
    cover_source = FAUCET / 'faucet-display-cover/faucet_display_cover.py'
    drop = review['total_display_and_bezel_drop_mm']
    changed = {'display_feet_n': review['new_recess_floor_n_mm'],
               'display_floor_n': review['new_recess_floor_n_mm'],
               'display_face_n': shell.display_face_n - drop,
               'display_cover_top_n': shell.display_cover_top_n - drop}
    with ExitStack() as stack:
        for key, value in changed.items():
            stack.enter_context(patch.object(shell, key, value))
        spec = importlib.util.spec_from_file_location('lowered_sculpted_cover', cover_source)
        cover = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cover)
        printable = cover.build_display_cover().val()
        seated = cover.build_seated_display_cover().val()
        native_tip = cq.importers.importStep(str(REVIEW / 'candidate-tip.step')).val()
        intersection = seated.intersect(native_tip).Volume()
        geometry = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
                    'cover_style': 'Sculpted', 'display_drop_mm': drop,
                    'display_foot_bearing_n_mm': shell.display_feet_n,
                    'cover_top_n_mm': cover.plate_n_top,
                    'bezel_bottom_n_mm': cover.bezel_n_bottom,
                    'bezel_thickness_mm': cover.bezel_thickness,
                    'glass_to_bezel_gap_mm': cover.bezel_n_bottom - shell.display_face_n,
                    'snap_bottom_top_n_mm': [shell.display_clip_bottom_n, shell.display_clip_top_n],
                    'seated_cover_to_accepted_tip_intersection_mm3': intersection,
                    'native_valid_single_solid': printable.isValid() and len(printable.Solids()) == 1,
                    'source_sha256': {str(cover_source.relative_to(ROOT)): writer.digest(cover_source.read_bytes()),
                                      str(Path(shell.__file__).relative_to(ROOT)): writer.digest(Path(shell.__file__).read_bytes()),
                                      str(tip.relative_to(ROOT)): expected},
                    'physical_fit_scope': 'The lowered Industrial head has reported tight but working fit. This Sculpted cover retains its own broad-wing design and fixed snap datums; its lowered geometry requires this requested print.'}
        assert geometry['native_valid_single_solid']
        assert intersection < 1e-5, geometry
        assert abs(cover.bezel_thickness - 1.3) < 1e-6
        cq.exporters.export(printable, str(HERE / 'sculpted-display-cover-low45.step'))
        cover_stl = HERE / 'sculpted-display-cover-low45.stl'
        cq.exporters.export(printable, str(cover_stl), tolerance=.005, angularTolerance=.1)
    geometry['print_stl_sha256'] = writer.digest(cover_stl.read_bytes())
    save(HERE / 'cover-geometry.json', geometry)
    parts = tuple((name, tip if name == 'faucet-shell-tip' else cover_stl, rotation)
                  if name in ('faucet-shell-tip', 'industrial-display-cover') else (name, source, rotation)
                  for name, source, rotation in industrial.industrial_parts())
    profile = PREVIOUS / '2026-10-24-industrial-complete-display-low45-petgf-left04-z004-mark2.3mf'
    project = HERE / (STEM + '.3mf')
    with patch.object(industrial, 'industrial_parts', lambda: parts):
        report = industrial.refresh(profile, project, 'Mark2', '#161616')
    with ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    old, new = 'industrial-display-cover', 'sculpted-display-cover'
    cover_row = next(p for p in report['parts'] if p['name'] == old)
    for name in ('Metadata/model_settings.config', '3D/3dmodel.model', cover_row['member']):
        tree = ET.fromstring(members[name])
        for node in tree.iter():
            if node.get('key') == 'name' and node.get('value') == old:
                node.set('value', new)
            if node.get('name') == old:
                node.set('name', new)
        members[name] = writer.xml(tree)
    cover_row['name'] = new
    writer.archive_write(project, members)
    report.update(project_sha256=writer.digest(project.read_bytes()),
                  display_drop_mm=drop, display_foot_recess_depth_mm=1.0,
                  cover_style='Sculpted', uniform_layer_height_mm=.24,
                  lowered_display_fit_record=str((PREVIOUS / 'physical-result/physical-result.json').relative_to(ROOT)),
                  cover_geometry_record=str((HERE / 'cover-geometry.json').relative_to(ROOT)),
                  authorization_quote="So start a new print on Mark II, which is clear and ready for you, and make it an industrial faucet, complete faucet, without the finer layers.",
                  launch_authorized=True)
    for source in (Path(__file__), cover_source, Path(shell.__file__)):
        report['source_sha256'][str(source.relative_to(ROOT))] = writer.digest(source.read_bytes())
    save(project.with_suffix('.print.json'), report)
    industrial.write_readiness(project, report)
    print(json.dumps({'project': str(project.relative_to(ROOT)), 'cover': geometry,
                      'parts': [p['name'] for p in report['parts']],
                      'first_layer_mm': report['first_bed_layer_height_mm'],
                      'normal_layer_mm': report['layer_height_mm']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
