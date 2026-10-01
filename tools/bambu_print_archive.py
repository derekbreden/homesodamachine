#!/usr/bin/env python3
"""Create a Bambu Studio print-only copy without changing any sliced toolpaths.

    python3 tools/bambu_print_archive.py input.gcode.3mf output.gcode.3mf

Studio opens an archive with editable models as a project. An empty model with
the existing plate metadata opens its stored G-code in Preview instead.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def package(source: Path, destination: Path):
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError("Use a new destination; preserve the reviewed source archive")
    with zipfile.ZipFile(source) as archive:
        if archive.testzip():
            raise ValueError("Source ZIP checksum failed")
        data = {name: archive.read(name) for name in archive.namelist()}
    gcodes = {name: body for name, body in data.items() if name.endswith('.gcode')}
    if not gcodes:
        raise ValueError("The source contains no sliced G-code")
    for name, body in gcodes.items():
        if hashlib.md5(body).hexdigest() != data[name + '.md5'].decode().strip().lower():
            raise ValueError(f"G-code checksum failed: {name}")

    core = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    ET.register_namespace('', core)
    ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
    ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
    model = ET.fromstring(data['3D/3dmodel.model'])
    for tag in ('resources', 'build'):
        model.find('{' + core + '}' + tag).clear()
    model.attrib.pop('requiredextensions', None)
    changed = {'3D/3dmodel.model': ET.tostring(model, encoding='utf-8', xml_declaration=True)}
    config = ET.fromstring(data['Metadata/model_settings.config'])
    for child in list(config):
        if child.tag in ('object', 'assemble'):
            config.remove(child)
        elif child.tag == 'plate':
            for instance in child.findall('model_instance'):
                child.remove(instance)
    changed['Metadata/model_settings.config'] = ET.tostring(config, encoding='utf-8', xml_declaration=True)
    omitted = {name for name in data if name.startswith(('3D/Objects/', '3D/_rels/'))}
    omitted.update(name for name in ('Metadata/layer_config_ranges.xml', 'Metadata/cut_information.xml')
                   if name in data)
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, body in data.items():
            if name not in omitted:
                archive.writestr(name, changed.get(name, body))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip():
            raise ValueError("Output ZIP checksum failed")
        for name in archive.namelist():
            if name not in changed and archive.read(name) != data[name]:
                raise ValueError(f"Unexpected change to {name}")
    return {
        'source_archive': str(source),
        'source_archive_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'print_only_archive': str(destination),
        'print_only_archive_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'gcode_sha256': {name: hashlib.sha256(body).hexdigest() for name, body in gcodes.items()},
        'gcode_byte_identical': True,
        'changed_container_entries': list(changed),
        'omitted_editable_geometry_entries': sorted(omitted),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(package(args.source, args.destination), indent=2))
