"""Prepare and inspect one local B-fill cup/lid comparison plate."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
OUT = ROOT/'.cache/prints/2026-10-28-b-fill-round-fore-20560'
sys.path[:0] = [str(ROOT/'hardware/printed-parts/faucet'),
               str(ROOT/'hardware/printed-parts/enclosure/trial-preparation'),
               str(ROOT/'hardware/scripts')]
import refresh_print_project as writer
from review import layers
from enclosure_support_audit import audit


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(variant, printer, review_only=False):
    geometry = json.loads((HERE/'geometry.json').read_text())
    row = geometry['variants'][variant]
    directory = OUT/variant/printer.lower()
    directory.mkdir(parents=True, exist_ok=True)
    job_name = f'bfill-{variant}-cup-lid-{printer.lower()}-20261028'
    project = directory/(job_name+'-input.3mf')
    trim, colour = (.18, '#000000') if printer == 'Mark1' else (.04, '#161616')
    if review_only:
        report = json.loads((directory/'preparation.json').read_text())
    else:
        if project.exists():
            raise FileExistsError('Keep the reviewed project immutable; use a new trial directory.')
        trim, colour = (.18, '#000000') if printer == 'Mark1' else (.04, '#161616')
        names = ('B-fill '+variant+' cup', 'B-fill '+variant+' lid')
        parts = tuple((name, ROOT/row['pieces'][kind]['stl'], 0.)
                      for name, kind in zip(names, ('cup', 'lid')))
        for (_, stl, _), kind in zip(parts, ('cup', 'lid')):
            assert sha(stl) == row['pieces'][kind]['stl_sha256']
        report = writer.refresh(ROOT/'hardware/printed-parts/petgf.3mf', project,
            parts=parts, offsets=((-38., 0.), (38., 0.)), z_trim=trim,
            title=job_name, plate_border=80.)
        with zipfile.ZipFile(project) as archive:
            members = {n: archive.read(n) for n in archive.namelist()}
        settings = json.loads(members[writer.SETTINGS_MEMBER])
        overrides = {
            'initial_layer_print_height': '0.2', 'layer_height': '0.24',
            'wall_loops': '3', 'wall_generator': 'classic',
            'sparse_infill_pattern': 'gyroid',
            'support_filament': '1', 'support_interface_filament': '1',
            'flush_into_support': '0',
            'extruder_ams_count': ['1#0|4#0', '1#0|4#0'],
            'filament_colour': [colour], 'raft_first_layer_expansion': '0.5',
        }
        report['coupon_settings_changes'] = {
            key: {'from': settings.get(key), 'to': value}
            for key, value in overrides.items() if settings.get(key) != value}
        settings.update(overrides)
        assert settings['filament_nozzle_map'] == ['0']
        assert settings['enable_arc_fitting'] == '0'
        assert settings['enable_support'] == '1' and settings['support_type'] == 'tree(auto)'
        assert settings['support_style'] == 'default'
        members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
        for name in members:
            if name.startswith('Metadata/filament_settings_') and name.endswith('.config'):
                config = json.loads(members[name])
                config['filament_colour'] = [colour]
                members[name] = json.dumps(config, indent=2).encode()
        config = ET.fromstring(members['Metadata/model_settings.config'])
        cup = config.find("object[@id='2']")
        writer.metadata(cup, 'enable_support', '0')
        members['Metadata/model_settings.config'] = writer.xml(config)
        writer.archive_write(project, members)
        report.update(printer=printer, variant=variant,
            project=str(project.relative_to(ROOT)), project_sha256=sha(project),
            geometry_record_sha256=sha(HERE/'geometry.json'),
            requested_z_trim_mm=trim, expected_emitted_trim_mm=trim-.02,
            fore_screw_y_mm=row['fore_screw_y_mm'],
            cup_support='Off, retaining the production cup recipe',
            lid_support='Tree(auto)/Default, retaining the production lid recipe',
            support_access='Remove lid-channel support through the open split groove and its ends before clamping.')
        (directory/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
        command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
            '--slice', '0', '--arrange', '0', '--orient', '0', '--outputdir', str(directory),
            '--export-3mf', job_name+'.gcode.3mf', str(project)]
        with (directory/'slice.log').open('w') as log:
            subprocess.run(command, cwd=directory, stdout=log, stderr=subprocess.STDOUT, check=True)
    archive = directory/(job_name+'.gcode.3mf')
    result = json.loads((directory/'result.json').read_text())
    assert result['return_code'] == 0
    plate, = result['sliced_plates']
    assert len(plate['objects']) == 2 and not plate['warning_message'], plate
    with zipfile.ZipFile(archive) as native:
        assert native.testzip() is None
        gcode = native.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gcode).hexdigest() == native.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        effective = json.loads(native.read(writer.SETTINGS_MEMBER))
        (HERE/(variant+'-preview.png')).write_bytes(native.read('Metadata/plate_1.png'))
    text = gcode.decode()
    trims = [float(n) for n in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', text, re.M)]
    assert np.allclose(trims, [0., trim-.02])
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    counts, support, first_layers = {}, {}, {}
    for z, height, roads in layers(text.splitlines()):
        for x0, y0, x1, y1, width, feature, owner in roads:
            if owner not in (1901, 1902) and not feature.startswith('Support') and feature not in ('Brim', 'Skirt'):
                continue
            low = np.minimum(low, np.minimum((x0, y0), (x1, y1))-width/2)
            high = np.maximum(high, np.maximum((x0, y0), (x1, y1))+width/2)
            if owner is not None:
                counts[owner] = counts.get(owner, 0)+1
                first_layers.setdefault(owner, set()).add(z)
            if feature.startswith('Support'):
                support[owner] = support.get(owner, 0)+1
    area_low, area_high = np.asarray(report['shared_printable_area_mm'])
    margins = [*(low-area_low), *(area_high-high)]
    assert min(margins) >= 80., margins
    assert {1901, 1902} <= set(counts), counts
    assert support.get(1901, 0) == 0, support
    assert all(np.allclose(sorted(first_layers[i])[:2], [.2, .44]) for i in (1901, 1902))
    path = directory/'plate_1.gcode'
    path.write_bytes(gcode)
    support_reading = audit(path, 'B-fill local cup and lid', include_unlabelled_support=True)
    (HERE/(variant+'-support.json')).write_text(json.dumps(support_reading, indent=2)+'\n')
    record = {
        'printer': printer, 'variant': variant, 'pieces': ['cup', 'lid'],
        'archive': str(archive.relative_to(ROOT)), 'archive_sha256': sha(archive),
        'project': str(project.relative_to(ROOT)), 'project_sha256': sha(project),
        'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
        'geometry_record_sha256': sha(HERE/'geometry.json'),
        'fore_screw_y_mm': row['fore_screw_y_mm'],
        'source_stl_sha256': {kind: p['stl_sha256'] for kind, p in row['pieces'].items()},
        'production_orientations_retained': True,
        'nozzle': {'side': 'left', 'diameter_mm': .4},
        'material': 'PET-GF, reported as PET-CF', 'filament_colour': colour,
        'emitted_z_trim_mm': trims, 'requested_z_trim_mm': trim,
        'layer_height_mm': .24, 'first_layer_mm': .2,
        'complete_bead_bounds_mm': [low.tolist(), high.tolist()],
        'minimum_bed_margin_mm': min(margins),
        'support_roads_by_object': support,
        'support_summary': support_reading['summary'],
        'embedded_vertex_max_error_mm': max(p['embedded_vertex_error_mm'] for p in report['parts']),
        'estimated_seconds': plate['total_predication'],
        'warnings': plate['warning_message'],
        'settings': {k: effective.get(k) for k in (
            'support_type', 'support_style', 'wall_loops', 'wall_generator',
            'sparse_infill_density', 'sparse_infill_pattern', 'fan_min_speed',
            'fan_max_speed', 'overhang_fan_speed', 'overhang_fan_threshold',
            'filament_nozzle_map', 'nozzle_diameter')},
        'submitted': False,
    }
    (HERE/(variant+'-preflight.json')).write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k: record[k] for k in (
        'printer', 'variant', 'archive', 'estimated_seconds',
        'minimum_bed_margin_mm', 'support_summary', 'emitted_z_trim_mm')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=('round20560',))
    parser.add_argument('printer', choices=('Mark1', 'Mark2'))
    parser.add_argument('--review-only', action='store_true')
    args = parser.parse_args()
    main(args.variant, args.printer, args.review_only)
