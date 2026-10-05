"""Prepare two centered, support-free upright RC62 and valve fit plates.

Each immutable revision preserves the corresponding left-nozzle PET-GF profile,
colour and trim. This script prepares and slices; it does not control printers.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in HERE.parents if (path / 'tools/publish_now.py').is_file())
SUPPORT = ROOT / 'hardware/printed-parts/enclosure/enclosure/support-bottom-gap'
sys.path.insert(0, str(SUPPORT))
import prepare_prints as common

MAGNETS = HERE.parent
VALVES = ROOT / 'hardware/printed-parts/fixtures/valve-socket-fit/tighter-trial-v2'
PROFILE = ROOT / 'hardware/printed-parts/petgf.3mf'
SPLITS = {
    'Mark2': dict(magnets=[f'{row}{col}' for row in 'AB' for col in range(1, 5)]+['C0'],
                  valves=['V72', 'V71', 'V70'], trim=.04, colour='#161616'),
    'H2C': dict(magnets=[f'{row}{col}' for row in 'CD' for col in range(1, 5)]+['C0'],
                valves=['V70', 'V69', 'V68'], trim=.18, colour='#000000'),
}
sha = common.sha


def prepare(printer, revision):
    selected = SPLITS[printer]
    magnet_manifest = json.loads((MAGNETS / 'geometry.json').read_text())
    valve_manifest = json.loads((VALVES / 'geometry.json').read_text())
    magnet_samples = {sample['label']: sample for sample in magnet_manifest['samples']}
    valve_samples = {sample['label']: sample for sample in valve_manifest['samples']}
    assert not magnet_manifest['pause'] and not valve_manifest['insertion_pause']
    stem = f'2026-10-04-centered-rc62-valve-{printer.lower()}-v{revision}'
    directory = ROOT / '.cache/prints' / stem
    assert not directory.exists(), f'Preserve every existing revision: {directory}'
    directory.mkdir()
    project = directory / (stem+'-input.3mf')
    parts = []; offsets = []; sources = [PROFILE, Path(__file__), SUPPORT / 'prepare_prints.py',
                                       MAGNETS / 'geometry.json', MAGNETS / 'generate.py',
                                       VALVES / 'geometry.json', VALVES / 'generate.py']
    for index, label in enumerate(selected['magnets']):
        sample = magnet_samples[label]; source = MAGNETS / sample['stl']
        assert sha(source) == sample['stl_sha256'], source
        row, column = divmod(index, 3)
        parts.append((sample['name'], source, 0.))
        offsets.append(((column-1)*34., -15.+row*25.))
        sources.extend((source, source.with_suffix('.step')))
    for index, label in enumerate(selected['valves']):
        sample = valve_samples[label]; source = VALVES / sample['stl']
        assert sha(source) == sample['stl_sha256'], source
        parts.append((sample['name'], source, 0.))
        offsets.append(((index-1)*54., -45.))
        sources.extend((source, source.with_suffix('.step')))
    # Center the complete model rectangle, including the label feet, on the
    # usable left-nozzle area. Reserve additional room for finite bead widths.
    bounds = []
    for (_, source, _), offset in zip(parts, offsets):
        size = np.ptp(trimesh.load_mesh(source, process=True).bounds, axis=0)[:2]
        bounds.append(np.array((np.array(offset)-size/2, np.array(offset)+size/2)))
    combined = np.array((np.min([bound[0] for bound in bounds], axis=0),
                         np.max([bound[1] for bound in bounds], axis=0)))
    shift = combined.mean(axis=0)
    offsets = tuple(tuple(np.array(offset)-shift) for offset in offsets)
    frozen = directory / 'inputs'; frozen.mkdir()
    source_hashes = {str(source.relative_to(ROOT)): sha(source) for source in sources}
    for index, source in enumerate(sources):
        shutil.copyfile(source, frozen / f'{index:02d}-{source.name}')
    report = common.writer.refresh(
        PROFILE, project, parts=tuple(parts), offsets=offsets,
        title=f'Centered upright RC62 and valve fit samples; {printer}',
        z_trim=selected['trim'], plate_border=62.)
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[common.writer.SETTINGS_MEMBER])
    overrides = dict(enable_support='0', support_filament='1', support_interface_filament='1',
                     extruder_ams_count=['1#0|4#0', '1#0|4#0'], flush_into_support='0',
                     filament_colour=[selected['colour']], elefant_foot_compensation='0',
                     brim_type='no_brim', brim_width='0')
    for key, expected in dict(initial_layer_print_height='0.2', layer_height='0.24',
                              wall_loops='2', sparse_infill_density='15%',
                              xy_contour_compensation='0', xy_hole_compensation='0',
                              filament_map=['1'], filament_nozzle_map=['0'],
                              enable_arc_fitting='0').items():
        assert settings[key] == expected, (key, settings[key])
    assert settings['filament_flow_ratio'][0] == '0.9555'
    report['intentional_overrides'] = {key: dict(from_value=settings.get(key), to_value=value)
                                       for key, value in overrides.items()}
    settings.update(overrides)
    members[common.writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    config = ET.fromstring(members['Metadata/model_settings.config'])
    for element, part in zip(config.findall('object'), report['parts']):
        common.writer.metadata(element, 'enable_support', '0')
        part['supports_enabled'] = False
    members['Metadata/model_settings.config'] = common.writer.xml(config)
    members['Metadata/layer_config_ranges.xml'] = common.writer.xml(ET.Element('objects'))
    assert 'Metadata/custom_gcode_per_layer.xml' not in members
    separations = []
    for index, first in enumerate(report['parts']):
        for second in report['parts'][:index]:
            a, b = np.array(first['plate_bounds_mm']), np.array(second['plate_bounds_mm'])
            axis_gap = np.maximum(np.maximum(a[0, :2]-b[1, :2], b[0, :2]-a[1, :2]), 0.)
            gap = float(np.linalg.norm(axis_gap))
            assert gap >= 8., (first['name'], second['name'], gap)
            separations.append(dict(parts=[first['name'], second['name']], bounding_box_gap_mm=gap))
    common.writer.archive_write(project, members)
    for source, digest in source_hashes.items():
        assert sha(ROOT / source) == digest, source
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  printer=printer, revision=revision, requested_z_trim_mm=selected['trim'],
                  expected_textured_trim_mm=selected['trim']-.02,
                  source_sha256=source_hashes, source_profile_sha256=sha(PROFILE),
                  settings_sha256=hashlib.sha256(members[common.writer.SETTINGS_MEMBER]).hexdigest(),
                  selected_labels=dict(magnets=selected['magnets'], valves=selected['valves']),
                  layout='Nine upright RC62 pockets in three centered rows; three upright valve panels in one centered row.',
                  minimum_required_full_bead_edge_margin_mm=60., object_separations=separations,
                  support_policy='All fit samples have support disabled globally and per object.',
                  layer_ranges_mm=[], support_painted_facets={}, pause=None,
                  production_print_pose_retained=True, fit_sample_quantity=12,
                  frame_quantity=0, full_enclosure_quantity=0, submitted=False,
                  physical_fit_and_first_layer_adhesion_qualified=False)
    (directory / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    return directory, project, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('printer', choices=SPLITS)
    parser.add_argument('--revision', type=int, default=4)
    parser.add_argument('--slice', action='store_true')
    args = parser.parse_args()
    directory, project, report = prepare(args.printer, args.revision)
    if args.slice:
        common.slice_prepared(directory, project, report)
    else:
        print(str(project.relative_to(ROOT)), flush=True)
