"""Prepare the two authorized complete-faucet plates from the selected full project.

Run manually after refreshing industrial/prepare_print_project.py. Geometry,
component contacts, seam paint, object settings and build Z stay unchanged.
"""
from copy import deepcopy
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
INDUSTRIAL = HERE.parents[1]
sys.path.insert(0, str(INDUSTRIAL.parent))
import refresh_print_project as writer

ROOT = writer.ROOT
PARENT = INDUSTRIAL / 'faucet-industrial-petgf.3mf'
AUTHORIZATION = "Please start me a complete faucet with ***EVERYTHING*** we've learned. Both beds are free."
LAYOUTS = {
    'Mark2': {'industrial-shell-base': (162.5, 160.)},
    'Mark1': {'faucet-shell-tip': (136., 202.),
              'industrial-display-cover': (198., 202.),
              'industrial-above-counter-plate': (130., 120.),
              'lever-replica': (198., 120.)},
}


def set_meta(parent, key, value):
    found = parent.find(f"metadata[@key='{key}']")
    if found is None:
        writer.metadata(parent, key, value)
    else:
        found.set('value', str(value))


def prepare(printer):
    folder = HERE / printer.lower()
    folder.mkdir(exist_ok=True)
    if (folder / 'launch.json').exists():
        raise ValueError('Preserve submitted archives; use a new print directory.')
    title = f'2026-10-15-complete-faucet-all-learnings-{printer.lower()}'
    stem = title + ('-base-arcs-z004' if printer == 'Mark2' else '-tip-disc-cover-plate-lever-z018')
    project = folder / (stem + '.3mf')
    with ZipFile(PARENT) as z:
        members = {n:z.read(n) for n in z.namelist()}
    report = json.loads(PARENT.with_suffix('.print.json').read_text())
    original = deepcopy(report)
    rows = [p for p in report['parts'] if p['name'] in LAYOUTS[printer]]
    ids = {p['object_id'] for p in rows}
    model = ET.fromstring(members['3D/3dmodel.model'])
    resources, build = model.find(writer.qn('resources')), model.find(writer.qn('build'))
    for obj in list(resources):
        if obj.get('id') not in ids:
            resources.remove(obj)
    for item in list(build):
        if item.get('objectid') not in ids:
            build.remove(item)
    model.find(f"{writer.qn('metadata')}[@name='Title']").text = title
    config = ET.fromstring(members['Metadata/model_settings.config'])
    for obj in list(config.findall('object')):
        if obj.get('id') not in ids:
            config.remove(obj)
    plate = config.find('plate')
    set_meta(plate, 'plater_name', title)
    for item in list(plate.findall('model_instance')):
        if item.find("metadata[@key='object_id']").get('value') not in ids:
            plate.remove(item)
    assemble = config.find('assemble')
    for item in list(assemble):
        if item.get('object_id') not in ids:
            assemble.remove(item)
    shifts = []
    for row in rows:
        old = [(a+b)/2 for a,b in zip(*row['plate_bounds_mm'])][:2]
        delta = [a-b for a,b in zip(LAYOUTS[printer][row['name']], old)]
        for axis in range(2):
            row['build_transform'][9+axis] += delta[axis]
            row['plate_translation_mm'][axis] += delta[axis]
            for bound in row['plate_bounds_mm']:
                bound[axis] += delta[axis]
        transform = ' '.join(f'{v:.9f}' for v in row['build_transform'])
        build.find(f"{writer.qn('item')}[@objectid='{row['object_id']}']").set('transform', transform)
        assemble.find(f"assemble_item[@object_id='{row['object_id']}'][@instance_id='0']").set('transform', transform)
        shifts.append(dict(part=row['name'], translation_xy_mm=delta, rotation_and_build_z_preserved=True))
    members['3D/3dmodel.model'] = writer.xml(model)
    members['Metadata/model_settings.config'] = writer.xml(config)
    used = {c.get(f'{{{writer.PROD}}}path').lstrip('/') for c in model.findall('.//' + writer.qn('component'))}
    for name in list(members):
        if name.startswith('3D/Objects/') and name not in used:
            del members[name]
    rels = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    for rel in list(rels):
        if rel.get('Target').lstrip('/') not in used:
            rels.remove(rel)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rels).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    if printer == 'Mark1':
        members.pop('Metadata/layer_config_ranges.xml', None)
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {}
    if printer == 'Mark2':
        selected = json.loads((INDUSTRIAL / 'finish-selection.json').read_text())['base_rim_supports']
        with ZipFile(ROOT / selected['source_project']) as z:
            machine = json.loads(z.read(writer.SETTINGS_MEMBER))
        for key in ('machine_start_gcode', 'printer_settings_id', 'filament_colour'):
            changes[key] = dict(from_sha256=writer.digest(json.dumps(settings[key]).encode()),
                                to_sha256=writer.digest(json.dumps(machine[key]).encode()))
            settings[key] = machine[key]
        members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + '\n').encode()
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=writer.digest(project.read_bytes()),
        printer=printer, requested_z_trim_mm=.04 if printer == 'Mark2' else .18,
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        native_settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
        parts=rows, plate_border_mm=80., project_title=title,
        parent_project=str(PARENT.relative_to(ROOT)), parent_project_sha256=original['project_sha256'],
        authorization_quote=AUTHORIZATION, layout_translations=shifts,
        machine_and_spool_changes=changes, rigid_part_count=len(rows), repeat_control=False,
        complete_faucet_scope='One of each of the five rigid PET-GF parts, distributed over two printers.',
        submitted=False, send_attempted=False, launch_authorized=True, preparation_only=True)
    if printer == 'Mark1':
        for key in ('base_rim_supports','rear_seam_enforcement','selected_faces','local_solid_regions'):
            report.pop(key, None)
    else:
        for key in ('tip_supports','tip_rear_seam_enforcement'):
            report.pop(key, None)
    report['source_sha256'][str(Path(__file__).relative_to(ROOT))] = writer.digest(Path(__file__).read_bytes())
    for name in report['profile_member_sha256']:
        report['profile_member_sha256'][name] = writer.digest(members[name])
    project.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    (folder / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(project, flush=True)


if __name__ == '__main__':
    for name in LAYOUTS:
        prepare(name)
