"""Prepare the current left/right PETG lids, exterior down, with supports off."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/cad-venv').is_dir())
RESERVOIR = HERE.parents[1]
CACHE = ROOT / '.cache/reservoir-lids-clear-ports-20261026'
sys.path.insert(0, str(RESERVOIR))
from prepare_print import write_archive, xml, qn, metadata, CORE, PROD


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    source = RESERVOIR / 'reservoir.3mf'
    with zipfile.ZipFile(source) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    model = ET.fromstring(members['3D/3dmodel.model'])
    config = ET.fromstring(members['Metadata/model_settings.config'])
    baseline = json.loads((HERE.parent / '2026-10-26-mark1-right-engineering-flow105-overlap50-temp260-left08-z000/settings.json').read_text())
    settings = baseline.copy()
    settings['enable_support'] = '0'
    settings['print_settings_id'] = 'Reservoir lids 0.8 - flush grips no supports'
    settings['filament_map_mode'] = 'Manual'
    settings['filament_map'] = ['1']
    settings['filament_nozzle_map'] = ['0']
    report = json.loads((RESERVOIR / 'reservoir.print.json').read_text())
    geometry = {p['name']: p for p in report['parts']}
    kept = {}
    for obj in config.findall('object'):
        values = {m.get('key'): m.get('value') for m in obj.findall('metadata')}
        if values.get('name') in ('reservoir-cap-left', 'reservoir-cap-right'):
            kept[obj.get('id')] = values['name']
        else:
            config.remove(obj)
    for tag in ('plate', 'assemble'):
        for child in config.findall(tag):
            config.remove(child)
    plate = ET.SubElement(config, 'plate')
    for key, value in {'plater_id': 1, 'plater_name': 'Left and right lids - open air ports',
                       'locked': 'false', 'bed_type': 'Engineering Plate',
                       'filament_map_mode': 'Manual', 'filament_maps': '1',
                       'filament_volume_maps': '0'}.items():
        metadata(plate, key, value)
    assembled = ET.SubElement(config, 'assemble')
    resources = model.find(qn('resources'))
    for obj in list(resources):
        if obj.get('id') not in kept:
            resources.remove(obj)
    build = model.find(qn('build'))
    for item in list(build):
        if item.get('objectid') not in kept:
            build.remove(item)
    part_records = []
    for i, item in enumerate(build):
        oid = item.get('objectid')
        name = kept[oid]
        transform = '1 0 0 0 -1 0 0 0 -1 ' + ('119' if name.endswith('left') else '206') + ' 160 5.5'
        item.set('transform', transform)
        instance = ET.SubElement(plate, 'model_instance')
        for key, value in {'object_id': oid, 'instance_id': 0, 'identify_id': 2601 + i}.items():
            metadata(instance, key, value)
        ET.SubElement(assembled, 'assemble_item', object_id=oid, instance_id='0', transform=transform, offset='0 0 0')
        ET.SubElement(assembled, 'assemble_item', object_id=oid, volume_id='0', transform='1 0 0 0 1 0 0 0 1 0 0 0')
        original = geometry[name]
        digest = sha((ROOT / original['source']).read_bytes())
        if digest != original['step_sha256']:
            raise ValueError(name + ' STEP differs from the current project record')
        part_records.append({'name': name, 'source_step': original['source'], 'step_sha256': digest,
                             'source_mesh_triangles': original['triangles'], 'transform': transform,
                             'print_orientation': 'exterior face down',
                             'ports': 'two 9/11 mm liquid seats and one 6/8 mm air seat; matched 45-degree countersinks'})
    for m in model.findall(qn('metadata')):
        if m.get('name') == 'Title':
            m.text = 'Reservoir lids - open air ports and TPU seats'
    members['3D/3dmodel.model'] = xml(model)
    members['Metadata/model_settings.config'] = xml(config)
    members['Metadata/project_settings.config'] = (json.dumps(settings, indent=2) + '\n').encode()
    for name in list(members):
        if name.endswith('.png') or name.startswith('Metadata/plate_'):
            del members[name]
    candidate = CACHE / 'reservoir-lids-open-airport-nosupport.3mf'
    write_archive(candidate, members)
    (HERE / 'settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    changes = {k: {'from': baseline.get(k), 'to': v} for k, v in settings.items() if v != baseline.get(k)}
    record = {'source_project': str(source.relative_to(ROOT)), 'source_project_sha256': sha(source.read_bytes()),
              'candidate': str(candidate.relative_to(ROOT)), 'candidate_sha256': sha(candidate.read_bytes()),
              'parts': part_records, 'settings_changes_from_right_overlap50_recipe': changes,
              'supports': 'Off for this lid pair. The 45-degree grommet seats grow without supports; the screw seats bridge their small clearance bores. All three tube ports are open, without a baffle.',
              'scope': 'Current lid geometry and editable project. Native slice, open-port toolpaths and launch are recorded separately.'}
    (HERE / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'candidate': str(candidate), 'parts': [p['name'] for p in part_records], 'changes': changes}, indent=2))


if __name__ == '__main__':
    main()
