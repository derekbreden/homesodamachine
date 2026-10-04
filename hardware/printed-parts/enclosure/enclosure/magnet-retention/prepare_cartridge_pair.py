"""Prepare the current cartridge and cap together, with one RC62 pause.

The reviewed v3 cartridge source supplies the Mark2 process, facet exclusions,
grip layer bands and whole clamp-root modifiers. Geometry is not regenerated.
The current cap is added crown-down with its own whole pogo-host modifier.
--slice exports a fresh local native archive; this never communicates with a printer.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

from prepare_prints import CORE, PROD, TAG, HERE, ENC, ROOT, SETTING, STUDIO, members, sha


def xml_mesh(mesh, ident):
    document = ET.Element(TAG('model'), unit='millimeter')
    resources = ET.SubElement(document, TAG('resources'))
    obj = ET.SubElement(resources, TAG('object'), id=str(ident), type='model')
    shaped = ET.SubElement(obj, TAG('mesh'))
    vertices = ET.SubElement(shaped, TAG('vertices'))
    for point in mesh.vertices:
        ET.SubElement(vertices, TAG('vertex'), **dict(zip('xyz', (f'{v:.9f}' for v in point))))
    triangles = ET.SubElement(shaped, TAG('triangles'))
    for face in mesh.faces:
        ET.SubElement(triangles, TAG('triangle'),
                      **dict(zip(('v1', 'v2', 'v3'), (str(int(v)) for v in face))))
    ET.SubElement(document, TAG('build'))
    return ET.tostring(document, encoding='UTF-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, default=4)
    parser.add_argument('--slice', action='store_true')
    args = parser.parse_args()
    destination = HERE / f'v{args.revision}'
    project = destination / 'pump-cartridge-cap-pause.3mf'
    record_path = destination / 'preparation.json'
    if project.exists() or record_path.exists():
        raise FileExistsError(f'Use an unused revision: {destination}')
    baseline = json.loads((HERE / 'v3/preparation.json').read_text())
    cartridge = copy.deepcopy(next(j for j in baseline['jobs'] if j['part'] == 'pump-cartridge'))
    reviewed = json.loads((HERE / 'v3/native-check.json').read_text())
    assert next(j for j in reviewed['jobs'] if j['part'] == 'pump-cartridge')['native_checks_pass']
    original = ROOT / cartridge['project']
    assert sha(original) == cartridge['project_sha256']
    for extension in ('stl', 'step'):
        assert sha(ENC / f'enclosure-pump-cartridge.{extension}') == cartridge[f'source_{extension}_sha256']
    region_path = ENC / 'heat-set-review/print-regions.json'
    regions = json.loads(region_path.read_text())
    assert sha(region_path) == cartridge['solid_host_region_record_sha256']
    cap_source = ENC / 'enclosure-pump-cap.stl'
    cap = trimesh.load_mesh(cap_source, process=True)
    assert cap.is_watertight
    for extension in ('stl', 'step'):
        assert sha(cap_source.with_suffix('.' + extension)) == regions['native_artifact_sha256']['pump-cap']['.' + extension]
    center = cap.bounds.mean(axis=0)
    height = float(np.ptp(cap.bounds[:, 2]))
    revised = members(original)
    model = ET.fromstring(revised['3D/3dmodel.model'])
    config = ET.fromstring(revised['Metadata/model_settings.config'])
    # Same production layout: cartridge aft, cap fore. Both model envelopes
    # have over 15 mm border in the shared 325 x 320 mm usable plate.
    item = model.find(f'.//{TAG("item")}')
    pump_transform = item.get('transform').split()
    pump_transform[10] = '210'
    item.set('transform', ' '.join(pump_transform))
    cartridge['machine_to_bed_translation_mm'][1] += 50
    for entry in config.findall('assemble/assemble_item'):
        if entry.get('instance_id') is not None:
            entry.set('transform', item.get('transform'))
    cap_transform = f'1 0 0 0 -1 0 0 0 -1 162.5 110 {height/2:.9f}'
    cap_uid = str(uuid.uuid5(uuid.NAMESPACE_URL, sha(cap_source)))
    resources = model.find(TAG('resources'))
    cap_root = ET.SubElement(resources, TAG('object'), id='6', type='model',
                             **{f'{{{PROD}}}UUID': cap_uid})
    components = ET.SubElement(cap_root, TAG('components'))
    cap_member = '3D/Objects/pump-cap.model'
    centered = cap.copy()
    centered.apply_translation(-center)
    revised[cap_member] = xml_mesh(centered, 5)
    ET.SubElement(components, TAG('component'), objectid='5', transform='1 0 0 0 1 0 0 0 1 0 0 0',
                  **{f'{{{PROD}}}path': '/' + cap_member, f'{{{PROD}}}UUID': cap_uid})
    ET.SubElement(model.find(TAG('build')), TAG('item'), objectid='6', transform=cap_transform,
                  printable='1', **{f'{{{PROD}}}UUID': cap_uid})
    cap_config = ET.SubElement(config, 'object', id='6')
    ET.SubElement(cap_config, 'metadata', key='name', value='enclosure-pump-cap')
    ET.SubElement(cap_config, 'metadata', key='extruder', value='1')
    face_count = ET.SubElement(cap_config, 'metadata', face_count=str(len(cap.faces)))
    normal = ET.SubElement(cap_config, 'part', id='5', subtype='normal_part', uuid=cap_uid)
    values = dict(name='enclosure-pump-cap', matrix='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                  source_file='enclosure-pump-cap.stl', source_object_id='0', source_volume_id='0',
                  **{f'source_offset_{axis}': str(v) for axis, v in zip('xyz', center)})
    for key, value in values.items():
        ET.SubElement(normal, 'metadata', key=key, value=value)
    ET.SubElement(normal, 'mesh_stat', face_count=str(len(cap.faces)), edges_fixed='0',
                  degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
    relationships_path = '3D/_rels/3dmodel.model.rels'
    relationships = ET.fromstring(revised[relationships_path])
    rel_type = next(iter(relationships)).get('Type')
    rel_tag = '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'
    ET.SubElement(relationships, rel_tag, Target='/' + cap_member, Type=rel_type, Id='pump-cap')
    modifiers = []
    for index, source in enumerate(regions['pieces']['pump-cap'], 7):
        region = copy.deepcopy(source)
        bounds = np.array(region['machine_bounds_mm']).reshape(3, 2)
        bounds[:, 0] = np.maximum(bounds[:, 0], cap.bounds[0] + 0.001)
        bounds[:, 1] = np.minimum(bounds[:, 1], cap.bounds[1] - 0.001)
        assert (bounds[:, 1] > bounds[:, 0]).all()
        region['applied_machine_bounds_mm'] = bounds.flatten().tolist()
        modifiers.append(region)
        box = trimesh.creation.box(extents=bounds[:, 1] - bounds[:, 0])
        box.apply_translation(bounds.mean(axis=1) - center)
        path = f'3D/Objects/cap-solid-host-{index}.model'
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, f'{sha(region_path)}:pump-cap:{index}'))
        revised[path] = xml_mesh(box, index)
        ET.SubElement(components, TAG('component'), objectid=str(index),
                      transform='1 0 0 0 1 0 0 0 1 0 0 0',
                      **{f'{{{PROD}}}path': '/' + path, f'{{{PROD}}}UUID': uid})
        part = ET.SubElement(cap_config, 'part', id=str(index), subtype='modifier_part', uuid=uid)
        for key, value in dict(name=region['name'], matrix='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                               sparse_infill_density=region['sparse_infill_density'],
                               sparse_infill_pattern=region['sparse_infill_pattern']).items():
            ET.SubElement(part, 'metadata', key=key, value=value)
        ET.SubElement(part, 'mesh_stat', face_count='12', edges_fixed='0', degenerate_facets='0',
                      facets_removed='0', facets_reversed='0', backwards_edges='0')
        ET.SubElement(relationships, rel_tag, Target='/' + path, Type=rel_type, Id=f'cap-host-{index}')
    face_count.set('face_count', str(len(cap.faces) + 12 * len(modifiers)))
    plate = config.find('plate')
    plate.find("metadata[@key='plater_name']").set('value', 'Cartridge and cap: insert one RC62 in cartridge')
    instance = ET.SubElement(plate, 'model_instance')
    for key, value in dict(object_id='6', instance_id='0', identify_id='1902').items():
        ET.SubElement(instance, 'metadata', key=key, value=value)
    assemble = config.find('assemble')
    ET.SubElement(assemble, 'assemble_item', object_id='6', instance_id='0', transform=cap_transform, offset='0 0 0')
    ET.SubElement(assemble, 'assemble_item', object_id='6', volume_id='0', transform='1 0 0 0 1 0 0 0 1 0 0 0')
    model.find(f"{TAG('metadata')}[@name='Title']").text = 'Current pump cartridge and cap; RC62 pause; Mark2'
    ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
    revised[relationships_path] = ET.tostring(relationships, encoding='UTF-8', xml_declaration=True)
    ET.register_namespace('', CORE)
    for path, document in [('3D/3dmodel.model', model), ('Metadata/model_settings.config', config)]:
        revised[path] = ET.tostring(document, encoding='UTF-8', xml_declaration=True)
    assert revised[SETTING] == members(original)[SETTING]
    assert revised['Metadata/custom_gcode_per_layer.xml'] == members(original)['Metadata/custom_gcode_per_layer.xml']
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(project, 'w', zipfile.ZIP_DEFLATED) as z:
        for path, data in revised.items():
            z.writestr(path, data)
    components_record = [
        {**cartridge, 'native_object_name': 'enclosure-pump-cartridge-RC62',
         'machine_to_bed_rotation_matrix': np.eye(3).astype(int).tolist()},
        dict(part='pump-cap', native_object_name='enclosure-pump-cap',
             source_stl_sha256=sha(cap_source), source_step_sha256=sha(cap_source.with_suffix('.step')),
             machine_to_bed_rotation_matrix=np.diag([1, -1, -1]).tolist(),
             machine_to_bed_translation_mm=[162.5, 110 + center[1], cap.bounds[1, 2]],
             solid_host_regions=modifiers),
    ]
    job = dict(part='pump-cartridge-cap', included_parts=['pump-cartridge', 'pump-cap'], printer='Mark2',
               project=str(project.relative_to(ROOT)), project_sha256=sha(project), components=components_record,
               baseline_project=str(original.relative_to(ROOT)), baseline_project_sha256=sha(original),
               solid_host_region_record_sha256=sha(region_path),
               requested_pause_height_mm=cartridge['requested_pause_height_mm'],
               magnet_count_to_insert=1, magnet_model='K&J RC62', submitted=False,
               preparation_script_sha256=sha(HERE / 'prepare_cartridge_pair.py'))
    if args.slice:
        output = ROOT / f'.cache/prints/cartridge-rc62-retention-v{args.revision}/pump-cartridge-cap'
        output.mkdir(parents=True, exist_ok=True)
        filename = f'enclosure-pump-cartridge-cap-rc62-mark2-v{args.revision}.gcode.3mf'
        if (output / filename).exists():
            raise FileExistsError(f'Native archive exists: {output / filename}')
        command = [str(STUDIO), '--slice', '0', '--arrange', '0', '--orient', '0',
                   '--outputdir', str(output), '--export-3mf', filename, str(project)]
        print('Slicing cartridge and cap together', flush=True)
        with (output / 'slice.log').open('w') as log:
            subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
        job['native_archive'] = str((output / filename).relative_to(ROOT))
        job['native_archive_sha256'] = sha(output / filename)
        job['gcode_sha256'] = hashlib.sha256(members(output / filename)['Metadata/plate_1.gcode']).hexdigest()
    for component in components_record:
        for key in ('project', 'project_sha256', 'native_archive', 'native_archive_sha256', 'gcode_sha256',
                    'baseline_project', 'baseline_project_sha256', 'printer'):
            component.pop(key, None)
    record_path.write_text(json.dumps(dict(submitted=False, revision=args.revision, jobs=[job]), indent=2) + '\n')
    print(json.dumps({k: job.get(k) for k in ('part', 'project', 'native_archive', 'submitted')}, indent=2))


if __name__ == '__main__':
    main()
