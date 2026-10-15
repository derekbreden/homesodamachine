"""Carry the physically accepted base-edge print aids into the complete project."""
from copy import deepcopy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import refresh_print_project as writer


def add_selected_base_rim(members: dict, report: dict, selected: dict) -> dict:
    source = writer.ROOT / selected['source_project']
    preparation = json.loads((writer.ROOT / selected['source_preparation']).read_text())
    origin = preparation['parts'][0]
    target = next(p for p in report['parts'] if p['name'] == selected['part'])
    shift = np.array(origin['source_center_mm']) - np.array(target['source_center_mm'])
    model = ET.fromstring(members['3D/3dmodel.model'])
    config = ET.fromstring(members['Metadata/model_settings.config'])
    rels = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    owner = model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{target['object_id']}']")
    target_config = config.find(f"object[@id='{target['object_id']}']")
    transferred = []
    with ZipFile(source) as z:
        source_model = ET.fromstring(z.read('3D/3dmodel.model'))
        source_owner = source_model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{origin['object_id']}']")
        source_config = ET.fromstring(z.read('Metadata/model_settings.config')).find(f"object[@id='{origin['object_id']}']")
        for arc in preparation['rim_arcs']:
            for key, kind in (('component_id', 'arc'), ('blocker_component_id', 'contact-blocker')):
                original_id = arc[key]
                new_id = original_id + 3800
                name = f'base-rim-{kind}-{original_id}'
                member = f'3D/Objects/{name}.model'
                component = deepcopy(source_owner.find(f"{writer.qn('components')}/{writer.qn('component')}[@objectid='{original_id}']"))
                source_member = component.get(f'{{{writer.PROD}}}path').lstrip('/')
                raw = z.read(source_member)
                child = ET.fromstring(raw)
                child.find(f"{writer.qn('resources')}/{writer.qn('object')}").set('id', str(new_id))
                for vertex in child.findall('.//' + writer.qn('vertex')):
                    for axis, delta in zip('xyz', shift):
                        vertex.set(axis, f'{float(vertex.get(axis))+delta:.9f}')
                members[member] = writer.xml(child)
                component.set('objectid', str(new_id))
                component.set(f'{{{writer.PROD}}}path', '/' + member)
                component.set(f'{{{writer.PROD}}}UUID', writer.identifier(name + '/component'))
                owner.find(writer.qn('components')).append(component)
                part = deepcopy(source_config.find(f"part[@id='{original_id}']"))
                part.set('id', str(new_id))
                part.set('uuid', writer.identifier(name + '/part'))
                writer.metadata(part, 'name', name)
                target_config.append(part)
                ET.SubElement(rels, f'{{{writer.REL}}}Relationship', Target='/' + member, Id=name,
                    Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
                transferred.append(dict(kind=kind, source_component_id=original_id, component_id=new_id,
                    source_member=source_member, member=member, source_member_sha256=writer.digest(raw),
                    member_sha256=writer.digest(members[member]), subtype=part.get('subtype')))
    members['3D/3dmodel.model'] = writer.xml(model)
    members['Metadata/model_settings.config'] = writer.xml(config)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(rels).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    return dict(part=target['name'], source_project=selected['source_project'],
        source_project_sha256=writer.digest(source.read_bytes()), source_preparation=selected['source_preparation'],
        physical_result=selected['physical_result'], source_local_to_target_local_translation_mm=shift.tolist(),
        arc_count=len(preparation['rim_arcs']), components=transferred,
        scope='Exact accepted curved rim walls and their narrow blocker strips on the base only. Tree(auto)/Default remains elsewhere. The part meshes, poses, seams and layer bands are retained.')
