"""Prepare the explicitly authorized base-and-tip seam evaluation; never send."""
from pathlib import Path
import hashlib, json, os, subprocess, sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
INDUSTRIAL = HERE.parents[1]
SOURCE = INDUSTRIAL / 'seam-placement/rear-center-v2/2026-10-13-industrial-faucet-full-rear-seam-petgf-left04-z004-mark2.3mf'
STEM = '2026-10-13-industrial-base-tip-full-rear-seam-petgf-left04-z004-mark2'
PROJECT = HERE / (STEM + '.3mf')
NATIVE = ROOT / '.cache/printer-control/faucet-rear-seam-full-review/evaluation-slice'
SHIFTS = {'industrial-shell-base': (50., 0.), 'faucet-shell-tip': (26., -45.)}
AUTHORIZATION = "Well, Mark 2 bed is clear, and I'd like to get the next print started if that next print is just the same faucet base again. But I'm worried because you said you're checking the whole base, that you didn't actually check the seam across the rest of our faucet. So could you please also check the tip and the mounting plate? And if they're good and they line up with this seam on the base, great, then start another print of base on Mark 2. Otherwise, print me everything that's got a problem that we need to verify is fixed here. Thanks."
sys.path.insert(0, str(INDUSTRIAL.parent))
import refresh_print_project as writer


def main():
    source_report = json.loads(SOURCE.with_suffix('.print.json').read_text())
    parts = [p for p in source_report['parts'] if p['name'] in SHIFTS]
    ids = {p['object_id'] for p in parts}
    by_id = {p['object_id']: p for p in parts}
    with ZipFile(SOURCE) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    model = ET.fromstring(members['3D/3dmodel.model'])
    resources, build = model.find(writer.qn('resources')), model.find(writer.qn('build'))
    for obj in list(resources):
        if obj.get('id') not in ids: resources.remove(obj)
    transforms = {}
    for item in list(build):
        oid = item.get('objectid')
        if oid not in ids: build.remove(item); continue
        values = [float(v) for v in item.get('transform').split()]
        dx, dy = SHIFTS[by_id[oid]['name']]
        values[9] += dx; values[10] += dy
        item.set('transform', ' '.join(f'{v:.9f}' for v in values))
        transforms[oid] = item.get('transform')
    model.find(f"{writer.qn('metadata')}[@name='Title']").text = 'Industrial base and tip - rear seam evaluation'
    keep = {c.get('{' + writer.PROD + '}path').lstrip('/') for c in resources.findall(
        f"{writer.qn('object')}/{writer.qn('components')}/{writer.qn('component')}")}
    members['3D/3dmodel.model'] = writer.xml(model)
    for name in list(members):
        if name.startswith('3D/Objects/') and name not in keep: del members[name]
    rels = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    for relation in list(rels):
        if relation.get('Target').lstrip('/') not in keep: rels.remove(relation)
    ET.register_namespace('', writer.REL)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rels)
    ET.register_namespace('', writer.CORE)
    config = ET.fromstring(members['Metadata/model_settings.config'])
    for obj in config.findall('object'):
        if obj.get('id') not in ids: config.remove(obj)
    plate = config.find('plate')
    plate.find("metadata[@key='plater_name']").set('value', 'Base and tip rear seam evaluation')
    for instance in plate.findall('model_instance'):
        if instance.find("metadata[@key='object_id']").get('value') not in ids: plate.remove(instance)
    for entry in list(config.find('assemble')):
        oid = entry.get('object_id')
        if oid not in ids: config.find('assemble').remove(entry)
        elif entry.get('instance_id') is not None: entry.set('transform', transforms[oid])
    members['Metadata/model_settings.config'] = writer.xml(config)
    writer.archive_write(PROJECT, members)
    rows = []
    for p in parts:
        row = json.loads(json.dumps(p))
        dx, dy = SHIFTS[row['name']]
        row['build_transform'][9] += dx; row['build_transform'][10] += dy
        row['plate_translation_mm'][0] += dx; row['plate_translation_mm'][1] += dy
        for bound in row['plate_bounds_mm']: bound[0] += dx; bound[1] += dy
        rows.append(row)
    report = {
        'evaluation_only': True, 'one_time_exception': True, 'authorization_quote': AUTHORIZATION,
        'normal_complete_recipe_changed': False,
        'source_complete_project': str(SOURCE.relative_to(ROOT)),
        'source_complete_project_sha256': writer.digest(SOURCE.read_bytes()),
        'project': str(PROJECT.relative_to(ROOT)), 'project_sha256': writer.digest(PROJECT.read_bytes()),
        'settings_payload_unchanged': True,
        'settings_sha256': writer.digest(members[writer.SETTINGS_MEMBER]),
        'retained_mesh_members_sha256': {n: writer.digest(members[n]) for n in sorted(keep)},
        'rear_seam_enforcement': source_report['rear_seam_enforcement'],
        'tip_rear_seam_enforcement': source_report['tip_rear_seam_enforcement'],
        'parts': rows, 'printer': 'Mark2', 'material': 'PET-GF',
        'nozzle_mapping': 'Left fixed 0.4 mm; external spool 254', 'requested_z_trim_mm': .04,
        'submitted': False,
    }
    PROJECT.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    NATIVE.mkdir(parents=True, exist_ok=True)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
               '--arrange', '0', '--orient', '0', '--export-3mf', STEM + '.gcode.3mf',
               '--outputdir', str(NATIVE), str(PROJECT)]
    with (NATIVE / 'slice.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True,
                       cwd=NATIVE, env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
    result = json.loads((NATIVE / 'result.json').read_text())
    if result.get('return_code') != 0: raise ValueError(result.get('error_string'))
    archive = NATIVE / (STEM + '.gcode.3mf')
    (HERE / archive.name).write_bytes(archive.read_bytes())
    plate, = result['sliced_plates']
    print(json.dumps({'project': PROJECT.name, 'native_archive': archive.name,
                     'estimated_seconds': plate['total_predication'],
                     'warning': plate['warning_message']}))


if __name__ == '__main__': main()
