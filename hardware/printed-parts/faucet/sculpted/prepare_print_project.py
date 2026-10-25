"""Prepare a complete Sculpted faucet with the selected Industrial print process.

Run by hand. Native slicing and printer submission are separate operations.
"""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
import argparse
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
sys.path[:0] = [str(FAUCET), str(FAUCET / 'industrial')]
import refresh_print_project as writer
from rim_supports import add_selected_base_rim
from tip_supports import add_selected_tip_supports

spec = importlib.util.spec_from_file_location('industrial_recipe', FAUCET / 'industrial/prepare_print_project.py')
industrial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(industrial)

PARENT = FAUCET / 'industrial/faucet-industrial-petgf.3mf'
PROFILE = FAUCET / 'industrial/prints/2026-10-15-all-learnings/mark2/2026-10-15-complete-faucet-all-learnings-mark2-base-arcs-z004.3mf'
FINISH = HERE / 'finish-selection.json'
PART_NAMES = {
    'faucet-shell-base': 'industrial-shell-base',
    'faucet-shell-tip': 'faucet-shell-tip',
    'faucet-display-cover': 'sculpted-display-cover',
    'above-counter-plate': 'industrial-above-counter-plate',
    'lever-replica': 'lever-replica',
}
OFFSETS = ((-77., 0.), (20., 47.), (89., 76.), (43., -52.), (-17.5, -60.))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def relative(path):
    return str(path.relative_to(ROOT))


def prepare(project):
    selection = json.loads(FINISH.read_text())
    parts = (*writer.PARTS, ('lever-replica', FAUCET / 'lever-replica/lever-replica-side-down.stl', 0.))
    report = writer.refresh(PROFILE, project, parts=parts, offsets=OFFSETS,
        title='Complete Sculpted white faucet PET-GF right Mark2', z_trim=.04, plate_border=40.)
    parent_report = json.loads(PARENT.with_suffix('.print.json').read_text())
    regions = tuple({**r, 'part': 'faucet-shell-base', 'clip_to_part_bounds': False}
        for r in parent_report['local_solid_regions'])
    writer.add_local_solid_regions(project, report, regions)
    with ZipFile(project) as z, ZipFile(PARENT) as parent:
        members = {n: z.read(n) for n in z.namelist()}
        parent_config = ET.fromstring(parent.read('Metadata/model_settings.config'))
    config = ET.fromstring(members['Metadata/model_settings.config'])
    parent_objects = {o.find("metadata[@key='name']").get('value'): o
                      for o in parent_config.findall('object')}
    for obj in config.findall('object'):
        name = obj.find("metadata[@key='name']").get('value')
        for setting in parent_objects[PART_NAMES[name]].findall('metadata'):
            if setting.get('key') not in ('name', 'extruder'):
                obj.append(deepcopy(setting))
    members['Metadata/model_settings.config'] = writer.xml(config)
    members.pop('Metadata/layer_config_ranges.xml', None)
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    original = deepcopy(settings)
    industrial.apply_overhang_recipe(settings, selection['overhang_recipe'])
    settings['filament_map'] = ['2']
    settings['filament_nozzle_map'] = ['1']
    settings['filament_map_mode'] = 'Manual'
    # Both installed Mark2 hotends are hardened 0.4 mm; this PET-GF preset's
    # saved bitmask advertises only the left one. Retain its process values.
    settings['filament_printable'] = ['3']
    settings['filament_colour'] = ['#FFFFFF']
    if 'filament_multi_colour' in settings:
        settings['filament_multi_colour'] = ['#FFFFFF']
    registration = ROOT / 'hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json'
    settings['extruder_offset'] = json.loads(registration.read_text())['native_extruder_offset']
    # Refresh started from the black left-nozzle profile. Center the complete
    # layout in the right nozzle's own reachable rectangle before adding aids.
    area = np.array([[float(v) for v in p.split('x')]
                     for p in settings['extruder_printable_area'][1].split(',')])
    low, high = area.min(axis=0), area.max(axis=0)
    delta = (low + high) / 2 - np.mean(report['shared_printable_area_mm'], axis=0)
    model = ET.fromstring(members['3D/3dmodel.model'])
    for row in report['parts']:
        for axis in range(2):
            row['build_transform'][9 + axis] += delta[axis]
            row['plate_translation_mm'][axis] += delta[axis]
            for bound in row['plate_bounds_mm']:
                bound[axis] += delta[axis]
        transform = ' '.join(f'{v:.9f}' for v in row['build_transform'])
        model.find(f"{writer.qn('build')}/{writer.qn('item')}[@objectid='{row['object_id']}']").set('transform', transform)
        config.find(f"assemble/assemble_item[@object_id='{row['object_id']}'][@instance_id='0']").set('transform', transform)
    report['shared_printable_area_mm'] = [low.tolist(), high.tolist()]
    report['printable_area_extruders'] = [1]
    report['right_nozzle_layout_translation_xy_mm'] = delta.tolist()
    members['3D/3dmodel.model'] = writer.xml(model)
    config.find("plate/metadata[@key='filament_maps']").set('value', '2')
    config.find("plate/metadata[@key='filament_map_mode']").set('value', 'Manual')
    members['Metadata/model_settings.config'] = writer.xml(config)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + '\n').encode()
    for key in ('rear_seam_enforcement', 'tip_rear_seam_enforcement'):
        target = deepcopy(selection[key])
        report[key] = industrial.enforce_rear_seam(members, report, target)
    rim = add_selected_base_rim(members, report, selection['base_rim_supports'])
    # The Sculpted foot is 58 x 59 mm; the accepted Industrial rim is diameter
    # 59 mm. Fit the same contact/release arrangement to the actual ellipse.
    scale_x = 58. / 59.
    center = np.array(report['parts'][0]['source_center_mm'])
    for component in rim['components']:
        child = ET.fromstring(members[component['member']])
        for vertex in child.findall('.//' + writer.qn('vertex')):
            vertex.set('x', f'{(float(vertex.get("x")) + center[0]) * scale_x - center[0]:.9f}')
        members[component['member']] = writer.xml(child)
        component['member_sha256'] = writer.digest(members[component['member']])
    rim.update(cad_scale=[scale_x, 1., 1.], target_foot_xy_mm=[58., 59.],
        scope='Accepted seven segmented rim arcs and local contact blockers fitted to the Sculpted elliptical rim. Build Z, release angles and requested gap are retained; Tree(auto)/Default elsewhere.')
    report['base_rim_supports'] = rim
    report['tip_supports'] = add_selected_tip_supports(members, report, selection['tip_supports'])
    writer.archive_write(project, members)
    report.update(project=relative(project), project_sha256=writer.digest(project.read_bytes()),
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        native_settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        printer='Mark2', active_nozzle=1, external_spool=255, requested_z_trim_mm=.04,
        filament_colour='#FFFFFF', parent_project=relative(PARENT),
        parent_project_sha256=writer.digest(PARENT.read_bytes()),
        profile_source=relative(PROFILE), profile_source_sha256=writer.digest(PROFILE.read_bytes()),
        finish_selection=relative(FINISH), finish_selection_sha256=writer.digest(FINISH.read_bytes()),
        selected_finish=selection, layer_config_ranges=[],
        layer_scope='0.20 mm first bed layer; 0.24 mm thereafter on all five parts. No Industrial shoulder bands or separate eight-layer override.',
        settings_changes={k: {'from': original.get(k), 'to': v}
            for k, v in settings.items() if original.get(k) != v},
        native_right_tool_offset_mm=[-.5, .7, 0.],
        rigid_part_count=5, preparation_only=True, submitted=False, send_attempted=False,
        authorization_quote=selection['authorization_quote'])
    report['source_sha256'] = {relative(p): writer.digest(p.read_bytes())
        for p in (Path(__file__), FINISH, PARENT, PROFILE, registration, *[p for _, p, _ in parts])}
    save(project.with_suffix('.print.json'), report)
    print(project, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    prepare(args.project.resolve())
