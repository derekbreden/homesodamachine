"""Prepare the two mold plates with six walls and 15% gyroid.

The frozen straight-rod project supplies the printer, filament, supports and
placements. Current STL meshes replace the template meshes; only the specified
process fields and preset label change in the printer recipe.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
HERE = ROOT/'.cache/funnel-gyroid-2026-10-05'
MODELS = ROOT/'hardware/printed-parts/zone-c/funnel-mold'
BASE = '4d584d29f'
REL = 'hardware/printed-parts/zone-c/funnel-mold/funnel-mold.3mf'
CHANGES = {
    'wall_loops': '6',
    'sparse_infill_density': '15%',
    'sparse_infill_pattern': 'gyroid',
    'top_shell_layers': '6',
    'bottom_shell_layers': '6',
    'top_one_wall_type': 'not apply',
    'print_settings_id': 'Funnel mold - six walls - 15% gyroid - PETG088',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    baseline = HERE/'baseline-funnel-mold.3mf'
    baseline.write_bytes(subprocess.check_output(['git', 'show', BASE+':'+REL], cwd=ROOT))
    with zipfile.ZipFile(baseline) as z:
        payloads = {n: z.read(n) for n in z.namelist()}
    old = json.loads(payloads['Metadata/project_settings.config'])
    settings = {**old, **CHANGES}
    payloads['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
    sys.path.insert(0, str(ROOT/'tools/funnel-mold-print'))
    from profiles import mesh_object, metadata, qn
    from scipy.spatial import cKDTree
    model = ET.fromstring(payloads['3D/3dmodel.model'])
    config = ET.fromstring(payloads['Metadata/model_settings.config'])
    prepared = []
    for index,name in enumerate(('cavity','core'),1):
        path = MODELS/(name+'.stl')
        mesh = trimesh.load(path, force='mesh', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        center = mesh.bounds.mean(axis=0)
        part_id, object_id = str(index*2-1), str(index*2)
        member = f'3D/Objects/object_{index}.model'
        old_obj = next(ET.fromstring(payloads[member]).iter(qn('object')))
        sub = ET.Element(qn('model'), unit='millimeter')
        resources = ET.SubElement(sub,qn('resources'))
        mesh_object(resources,part_id,mesh,center)
        obj = resources.find(qn('object'))
        obj.attrib.update(old_obj.attrib)
        payloads[member] = ET.tostring(sub,xml_declaration=True,encoding='UTF-8')
        item = model.find(qn('build')).find(f"{qn('item')}[@objectid='{object_id}']")
        transform = [float(v) for v in item.attrib['transform'].split()]
        rotation = np.array(transform[:9]).reshape(3,3)
        local_points = mesh.vertices-center
        transform[11] = -float((local_points@rotation)[:,2].min())
        item.set('transform',' '.join(f'{v:.12g}' for v in transform))
        object_settings = config.find(f"object[@id='{object_id}']")
        part = object_settings.find('part')
        for key,value in zip(('source_offset_x','source_offset_y','source_offset_z'),center):
            metadata(part,key,f'{value:.12g}')
        for node in (object_settings.find('metadata[@face_count]'),part.find('mesh_stat')):
            node.set('face_count',str(len(mesh.faces)))
        for a in config.findall(f"assemble/assemble_item[@object_id='{object_id}'][@instance_id]"):
            t=[float(v) for v in a.attrib['transform'].split()]
            t[11]=transform[11]
            a.set('transform',' '.join(f'{v:.12g}' for v in t))
        plate_points=local_points@rotation+np.array(transform[9:12])
        plate_bounds=np.vstack((plate_points.min(axis=0),plate_points.max(axis=0)))
        bed_bounds = plate_bounds.copy()
        bed_bounds[:,0] -= 396*(index-1)
        inside = np.all(bed_bounds[0]>=np.array([0,0,-1e-6])) and np.all(bed_bounds[1]<=np.array([299,320,325])+1e-6)
        assert inside,bed_bounds
        vertices=np.array([[float(v.attrib[k]) for k in ('x','y','z')]
                           for v in resources.iter(qn('vertex'))])+center
        distance=float(cKDTree(mesh.vertices).query(vertices)[0].max())
        assert distance<1e-6
        prepared.append({'part':name,'plate':index,'stl_sha256':sha(path),
           'mesh_watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
           'mesh_bodies':int(mesh.body_count),'triangles':int(len(mesh.faces)),
           'embedded_maximum_vertex_distance_mm':distance,'transform':transform,
           'source_center_mm':center.tolist(),'local_bed_bounds_mm':bed_bounds.tolist(),
           'model_within_bed':bool(inside),'orientation':'upright' if name=='cavity' else 'inverted'})
    payloads['3D/3dmodel.model']=ET.tostring(model,xml_declaration=True,encoding='UTF-8')
    payloads['Metadata/model_settings.config']=ET.tostring(config,xml_declaration=True,encoding='UTF-8')
    destination = HERE/'current-funnel-mould-petg088.3mf'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for n, data in payloads.items():
            out.writestr(n, data)
    sys.path.insert(0, str(ROOT/'tools/funnel-mold-print'))
    from verify_print import embedded_mesh
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        meshes = {name: embedded_mesh(z, str(i*2), MODELS/(name+'.stl'))
                  for i, name in enumerate(('cavity', 'core'), 1)}
        with zipfile.ZipFile(baseline) as base:
            assert all(z.read(n) == base.read(n) for n in z.namelist()
                       if n not in ('Metadata/project_settings.config', 'Metadata/model_settings.config',
                                    '3D/3dmodel.model', '3D/Objects/object_1.model',
                                    '3D/Objects/object_2.model'))
    native = json.loads(subprocess.check_output([
        'git', 'show', BASE+':hardware/printed-parts/zone-c/funnel-mold/current-slice-review.json'], cwd=ROOT))
    selected_keys = tuple(native['selected_recipe'])
    native = {'checked_date': '2026-10-05', 'selected_recipe': dict.fromkeys(selected_keys)}
    info = json.loads((MODELS/'design.json').read_text())
    containment = json.loads((MODELS/'containment-review.json').read_text())
    assert containment['contained']
    assert all(sha(MODELS/n) == digest for n, digest in containment['sha256'].items())
    native['containment_pass'] = True
    native['containment_review_sha256'] = sha(MODELS/'containment-review.json')
    native['design_sha256'] = sha(MODELS/'design.json')
    native['prepared_plates'] = prepared
    native['complete_tooling'] = True
    native['tooling'] = 'Two solid mold bodies and one stock straight 6 x 25 mm stainless steel rod.'
    native['minimum_cavity_backing_mm'] = info['minimum_cavity_backing_mm']
    native['minimum_core_backing_mm'] = info['minimum_core_backing_mm']
    native.update({
        'method': 'Current native STL meshes, current containment binding and frozen printer/filament/support recipe; explicit sparse-process changes.',
        'baseline_recipe_commit': BASE,
        'baseline_project_sha256': sha(baseline),
        'current_project': str(destination.relative_to(ROOT)),
        'current_project_sha256': sha(destination),
        'settings_byte_identical_to_frozen_template': False,
        'settings_changes': {k: {'baseline': old[k], 'current': settings[k]} for k in CHANGES},
        'selected_recipe': {k: settings[k] for k in (
            *native['selected_recipe'], 'sparse_infill_pattern', 'top_shell_layers',
            'bottom_shell_layers', 'top_one_wall_type')},
        'all_other_recipe_and_nonmodel_payloads_identical': True,
        'embedded_meshes': meshes,
        'native_slice_pending': True,
        'native_slice_success': False,
        'physical_scope': 'September 16 records a successful 15% infill Snug-support mold and a failed subsequent solid-infill print. September 18 supports the retained PETG flow/nozzle recipe. Six walls with 15% gyroid are the current mold process; those reports do not measure its stiffness or cast behavior.',
    })
    (HERE/'preparation-review.json').write_text(json.dumps(native, indent=2)+'\n')
    physical = json.loads(subprocess.check_output([
        'git', 'show', BASE+':hardware/printed-parts/zone-c/funnel-mold/current-slice-review.json'], cwd=ROOT))['physical_recipe_binding']
    physical['process_changes'] = native['settings_changes']
    physical['physical_result_scope'] = 'The September 18 print supports the retained nozzle, filament and flow recipe; its solid-infill process is separately identified. The September 16 report supports sparse mold printing with Snug normal supports.'
    (HERE/'physical-recipe-binding.json').write_text(json.dumps(physical, indent=2)+'\n')
    print(destination)


if __name__ == '__main__':
    main()
