"""Build four compact interface-pattern specimens for Mark2."""

import hashlib
import json
from pathlib import Path
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools/funnel-mold-print'))
from profiles import PROD, REL, qn, mesh_object, metadata

WIDTH = 36.0
DEPTH = 36.0
WALL = 3.0
CEILING = 12.2
ROOF = 3.84
LABEL_HEIGHT = 0.64
PITCH = 60.0
FIRST_CENTER = (130.0, 120.0)
VARIANTS = [("A", "auto", 2), ("B", "rectilinear", 1), ("C", "rectilinear", 1), ("D", "auto", 0)]
OUT = ROOT / '.cache/prints/2026-09-15-interface-patterns-mark2'
TITLE = 'petgf-interface-patterns-mark2'


def block(x, y, z, origin):
    return cq.Workplane('XY').box(x, y, z, centered=False).translate(origin)


def specimen(number):
    roof = block(WIDTH, DEPTH, ROOF, (0, 0, CEILING))
    back = block(WIDTH, WALL, CEILING, (0, DEPTH-WALL, 0))
    left = block(WALL, DEPTH-WALL, CEILING, (0, 0, 0))
    right = block(WALL, DEPTH-WALL, CEILING, (WIDTH-WALL, 0, 0))
    body = roof.union(back).union(left).union(right)
    witness = (cq.Workplane('XZ')
        .polyline([(-0.01, CEILING-0.36), (0.40, CEILING),
                   (-0.01, CEILING+0.36), (-0.01, CEILING-0.36)])
        .close().extrude(-8))
    body = body.cut(witness).cut(witness.mirror('YZ').translate((WIDTH, 0, 0)))
    label = (cq.Workplane('XY').text(str(number), 10, LABEL_HEIGHT,
             font='Arial', kind='bold', combine=False)
             .translate((WIDTH/2, DEPTH*0.66, CEILING+ROOF)))
    return body.union(label).clean()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    profile = ROOT / 'hardware/printed-parts/petgf.3mf'
    with zipfile.ZipFile(profile) as source:
        settings = json.loads(source.read('Metadata/project_settings.config'))
        data = {name: source.read(name) for name in
                ('Metadata/filament_settings_1.config', '[Content_Types].xml')}
    settings['extruder_ams_count'] = ['1#0|4#0', '1#0|4#0']
    assert settings['independent_support_layer_height'] == '1'
    assert settings['support_type'] == 'tree(auto)'
    assert settings['layer_height'] == '0.24'
    data['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
        **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    for name, text in [('Application', 'BambuStudio-02.08.02.61'),
                       ('BambuStudio:3mfVersion', '1'), ('Title', TITLE)]:
        ET.SubElement(model, qn('metadata'), name=name).text = text
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
    config = ET.Element('config')
    rels = ET.Element(f'{{{REL}}}Relationships')
    plate = ET.SubElement(config, 'plate')
    for key, value in {'plater_id': 1, 'plater_name': TITLE, 'locked': 'false',
            'filament_map_mode': 'Manual', 'filament_maps': '1',
            'filament_volume_maps': '0', 'bed_type': 'Textured PEI Plate'}.items():
        metadata(plate, key, value)
    records, regions = [], []
    for index in range(4):
        row, col = divmod(index, 2)
        label, pattern, layers = VARIANTS[index]
        gap, spacing = 0.30, 0.50
        number = index+1
        shape = specimen(label)
        assert shape.val().isValid() and len(shape.solids().vals()) == 1
        mesh_path = OUT / f'specimen-{number:02}.stl'
        cq.exporters.export(shape, str(mesh_path), tolerance=0.025, angularTolerance=0.15)
        mesh = trimesh.load(mesh_path, force='mesh', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        center = mesh.bounds.mean(axis=0)
        cx, cy = FIRST_CENTER[0]+col*PITCH, FIRST_CENTER[1]+row*PITCH
        pid, oid = str(2*number-1), str(2*number)
        subpath = f'/3D/Objects/object_{number}.model'
        sub = ET.Element(qn('model'), unit='millimeter')
        mesh_object(ET.SubElement(sub, qn('resources')), pid, mesh, center)
        data[subpath.lstrip('/')] = ET.tostring(sub, encoding='UTF-8', xml_declaration=True)
        obj = ET.SubElement(resources, qn('object'), id=oid, type='model',
                            **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
        ET.SubElement(ET.SubElement(obj, qn('components')), qn('component'), objectid=pid,
            transform='1 0 0 0 1 0 0 0 1 0 0 0',
            **{f'{{{PROD}}}path': subpath, f'{{{PROD}}}UUID': str(uuid.uuid4())})
        ET.SubElement(build, qn('item'), objectid=oid, printable='1',
                      transform=f'1 0 0 0 1 0 0 0 1 {cx} {cy} {center[2]:.9f}')
        ET.SubElement(rels, f'{{{REL}}}Relationship', Target=subpath, Id=f'rel-{number}',
                      Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        obj = ET.SubElement(config, 'object', id=oid)
        overrides = {'support_top_z_distance': str(gap), 'support_interface_top_layers': str(layers),
                     'support_interface_pattern': pattern}
        for key, value in {'name': f'{label} {pattern} {layers} interface layers',
                           'extruder': '1', **overrides}.items():
            metadata(obj, key, value)
        ET.SubElement(obj, 'metadata', face_count=str(len(mesh.faces)))
        part = ET.SubElement(obj, 'part', id=pid, subtype='normal_part')
        for key, value in {'name': mesh_path.name,
                'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                'source_file': mesh_path.name, 'source_object_id': 0, 'source_volume_id': 0,
                'source_offset_x': center[0], 'source_offset_y': center[1],
                'source_offset_z': center[2]}.items():
            metadata(part, key, value)
        instance = ET.SubElement(plate, 'model_instance')
        for key, value in {'object_id': oid, 'instance_id': 0, 'identify_id': 2000+number}.items():
            metadata(instance, key, value)
        record = {'id': label, 'identify_id': 2000+number, 'row': row+1, 'column': col+1,
            'baseline_control': label == 'A', 'pattern': pattern,
            'remove_interface_connectors': label == 'C',
            'gap_mm': gap, 'spacing_mm': spacing, 'interface_layers': layers,
            'plate_center_xy': [cx, cy], 'object_id': int(oid), 'overrides': overrides,
            'mesh': str(mesh_path.relative_to(ROOT)),
            'mesh_sha256': hashlib.sha256(mesh_path.read_bytes()).hexdigest(),
            'triangles': len(mesh.faces)}
        records.append(record)
        regions.append({'id': record['id'], 'x_min': cx-WIDTH/2+6, 'x_max': cx+WIDTH/2-6,
            'y_min': cy-DEPTH/2+6, 'y_max': cy+DEPTH/2-6,
            'ceiling_z': CEILING, 'model_layer_height': 0.24,
            'expected_top_gap': gap, 'expected_interface_layers': layers})
    package = ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package, f'{{{REL}}}Relationship', Target='/3D/3dmodel.model', Id='rel-1',
                  Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    for path, element in [('3D/3dmodel.model', model), ('Metadata/model_settings.config', config),
            ('3D/_rels/3dmodel.model.rels', rels), ('_rels/.rels', package)]:
        data[path] = ET.tostring(element, encoding='UTF-8', xml_declaration=True).replace(
            b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    project = OUT / (TITLE+'-input.3mf')
    with zipfile.ZipFile(project, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, payload in data.items():
            archive.writestr(name, payload)
    editable = HERE / 'interface-patterns.3mf'
    editable.write_bytes(project.read_bytes())
    info = {'editable_project': str(editable.relative_to(ROOT)), 'profile': str(profile.relative_to(ROOT)),
        'profile_sha256': hashlib.sha256(profile.read_bytes()).hexdigest(),
        'project': str(project.relative_to(ROOT)),
        'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
        'printer': 'Mark2', 'z_offset_mm': 0.04, 'effective_textured_plate_trim_mm': 0.02,
        'pattern_method': 'For C, remove commanded extrusion only from horizontal end connections in its single Y-oriented interface layer. D has zero interface layers.',
        'geometry': {'width': WIDTH, 'depth': DEPTH, 'wall': WALL, 'ceiling_z': CEILING,
                     'roof_thickness': ROOF, 'label_height': LABEL_HEIGHT},
        'specimens': records}
    (HERE / 'experiment.json').write_text(json.dumps(info, indent=2)+'\n')
    (OUT / 'regions.json').write_text(json.dumps(regions, indent=2)+'\n')
    print(project)


if __name__ == '__main__':
    main()
