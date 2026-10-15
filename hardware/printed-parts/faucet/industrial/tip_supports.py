"""Retain the accepted tip fins, local lip support paint and hidden-root anchor."""
from copy import deepcopy
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import refresh_print_project as writer


def add_selected_tip_supports(members, report, selected):
    source = writer.ROOT / selected['source_project']
    prep = json.loads((writer.ROOT / selected['source_preparation']).read_text())
    origin = prep['parts'][0]
    target = next(p for p in report['parts'] if p['name'] == selected['part'])
    center = np.array(target['source_center_mm'])
    shift = np.array(origin['source_center_mm']) - center
    model = ET.fromstring(members['3D/3dmodel.model'])
    config = ET.fromstring(members['Metadata/model_settings.config'])
    rels = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    owner = model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{target['object_id']}']")
    target_config = config.find(f"object[@id='{target['object_id']}']")
    copied = []
    with ZipFile(source) as z:
        source_model = ET.fromstring(z.read('3D/3dmodel.model'))
        source_owner = source_model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{origin['object_id']}']")
        source_config = ET.fromstring(z.read('Metadata/model_settings.config')).find(f"object[@id='{origin['object_id']}']")
        for old_id, new_id, name in ((selected['fin_component_id'], 8000, 'tip-eight-fin-walls'),
                                    (selected['root_anchor_component_id'], 8400, 'tip-hidden-root-disc')):
            component = deepcopy(source_owner.find(f"{writer.qn('components')}/{writer.qn('component')}[@objectid='{old_id}']"))
            source_member = component.get(f'{{{writer.PROD}}}path').lstrip('/')
            raw = z.read(source_member)
            child = ET.fromstring(raw)
            child.find(f"{writer.qn('resources')}/{writer.qn('object')}").set('id', str(new_id))
            for vertex in child.findall('.//' + writer.qn('vertex')):
                for axis, delta in zip('xyz', shift):
                    vertex.set(axis, f'{float(vertex.get(axis))+delta:.9f}')
            member = f'3D/Objects/{name}.model'
            members[member] = writer.xml(child)
            component.set('objectid', str(new_id))
            component.set(f'{{{writer.PROD}}}path', '/' + member)
            component.set(f'{{{writer.PROD}}}UUID', writer.identifier(name + '/component'))
            owner.find(writer.qn('components')).append(component)
            part = deepcopy(source_config.find(f"part[@id='{old_id}']"))
            part.set('id', str(new_id))
            part.set('uuid', writer.identifier(name + '/part'))
            writer.metadata(part, 'name', name)
            target_config.append(part)
            ET.SubElement(rels, f'{{{writer.REL}}}Relationship', Target='/' + member, Id=name,
                Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
            copied.append(dict(source_component_id=old_id, component_id=new_id, source_member=source_member,
                member=member, source_member_sha256=writer.digest(raw), member_sha256=writer.digest(members[member])))
    # The full tip has a different tessellation from the short section. Use the
    # accepted geometric selection on its downward joint-plane facets; retain seams.
    child = ET.fromstring(members[target['member']])
    mesh = child.find('.//' + writer.qn('mesh'))
    vertices = np.array([[float(v.get(k)) for k in 'xyz'] for v in mesh.find(writer.qn('vertices'))]) + center
    triangles = list(mesh.find(writer.qn('triangles')))
    indices = np.array([[int(t.get(k)) for k in ('v1', 'v2', 'v3')] for t in triangles])
    points = vertices[indices]
    cross = np.cross(points[:,1]-points[:,0], points[:,2]-points[:,0])
    lengths = np.linalg.norm(cross, axis=1)
    normals = cross / np.maximum(lengths[:,None], 1e-20)
    point = np.array(selected['joint_plane']['point'])
    normal = np.array(selected['joint_plane']['normal'])
    plane = (np.max(abs((points-point)@normal), axis=1) < .02) & (normals@(-normal) > .999)
    t = np.array(target['build_transform'])
    centers = points.mean(axis=1)
    placed = (centers-center)@t[:9].reshape(3,3) + t[9:]
    selection = selected['lip_enforcer_selection']
    enforced = plane & (placed[:,2] < selection['maximum_build_z_mm']) & (abs(centers[:,0]) < selection['maximum_abs_cad_x_mm'])
    for index in np.flatnonzero(plane):
        triangles[index].set('paint_supports', '4' if enforced[index] else '8')
    members[target['member']] = writer.xml(child)
    members['3D/3dmodel.model'] = writer.xml(model)
    members['Metadata/model_settings.config'] = writer.xml(config)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rels).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    return dict(part=target['name'], source_project=selected['source_project'],
        source_project_sha256=writer.digest(source.read_bytes()), source_preparation=selected['source_preparation'],
        physical_result=selected['physical_result'], components=copied, fin_count=selected['fin_count'],
        source_local_to_target_local_translation_mm=shift.tolist(), joint_plane=selected['joint_plane'],
        joint_plane_faces=int(plane.sum()), joint_plane_area_mm2=float((lengths[plane]/2).sum()),
        enforced_lip_faces=int(enforced.sum()), enforced_lip_area_mm2=float((lengths[enforced]/2).sum()),
        lip_enforcer_selection=selection, vertices_and_triangle_indices_unchanged=True, seam_paint_preserved=True,
        root_contact_scope=selected['root_contact_scope'],
        scope='Exact accepted fin and hidden-root-disc meshes; accepted lip support-selection geometry on the full tip tessellation. Tree(auto)/Default elsewhere. Bonded disc contact stays on the hidden male insertion end.')
