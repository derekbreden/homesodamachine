"""Prepare matched actual-faucet sections; manual experiment, no printer control."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
FAUCET = HERE.parents[1]
INDUSTRIAL = FAUCET/'industrial'
sys.path[:0] = [str(FAUCET), str(INDUSTRIAL)]
import refresh_print_project as writer
import prepare_print_project as industrial

loader = importlib.util.spec_from_file_location('coarse_start_helpers', HERE.parent/'coarse-start-v1/prepare.py')
helpers = importlib.util.module_from_spec(loader)
loader.loader.exec_module(helpers)
SOURCE = INDUSTRIAL/'faucet-industrial-petgf.3mf'
APPROVAL = INDUSTRIAL/'prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json'
WORK = ROOT/'.cache/printer-control/faucet-bridge-transfer-20261014'


def save(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n')


def section(kind, angle, top):
    stem = INDUSTRIAL/'industrial-shell-base' if kind == 'foot' else FAUCET/'faucet-shell/faucet-shell-tip'
    source = stem.with_suffix('.stl')
    approved = json.loads(APPROVAL.read_text())
    if writer.digest(source.read_bytes()) != approved['source_geometry_hashes'][str(source.relative_to(ROOT))]:
        raise ValueError('Current source differs from the identified production geometry')
    mesh = trimesh.load(source, force='mesh')
    rotation = trimesh.transformations.rotation_matrix(math.radians(angle), [1, 0, 0])
    rotated = trimesh.transform_points(mesh.vertices, rotation)
    lift = -float(rotated[:, 2].min())
    original = cq.importers.importStep(str(stem.with_suffix('.step'))).val()
    posed = original.rotate((0, 0, 0), (1, 0, 0), angle).translate((0, 0, lift))
    clipped = posed.intersect(cq.Solid.makeBox(400, 500, top+0.001,
                                             cq.Vector(-200, -200, -0.001)), tol=1e-6)
    if not clipped.isValid() or len(clipped.Solids()) != 1:
        raise ValueError('Section must remain one valid model body')
    # Store in assembly coordinates so the production rear-seam reader remains applicable.
    clipped = clipped.translate((0, 0, -lift)).rotate((0, 0, 0), (1, 0, 0), -angle)
    out = HERE/f'{kind}-section.stl'
    cq.exporters.export(clipped, str(out), tolerance=0.012, angularTolerance=0.07)
    return out, dict(source=str(source.relative_to(ROOT)), source_sha256=writer.digest(source.read_bytes()),
                     source_step_sha256=writer.digest(stem.with_suffix('.step').read_bytes()),
                     original_rotation_x_degrees=angle, original_lift_mm=lift,
                     crop_max_original_print_z_mm=top, full_circumference_retained=True,
                     tessellation_tolerance_mm=0.012)


def prepare(printer, kind, angle, top):
    folder = HERE/printer.lower()
    folder.mkdir(parents=True, exist_ok=True)
    if (folder/'launch.json').exists():
        raise ValueError('Preserve the submitted experiment; use a new directory for another print')
    trim = 0.18 if printer == 'Mark1' else 0.04
    stem = f'2026-10-14-faucet-{kind}-bridge-transfer-petgf-left04-z{round(trim*100):03d}-{printer.lower()}'
    geometry, origin = section(kind, angle, top)
    project = folder/f'{stem}.3mf'
    parts = tuple((f'{letter} {kind} {name}', geometry, angle)
                  for letter, name in [('A', 'production reference'), ('B', '125 bridge 70 cooling')])
    report = writer.refresh(SOURCE, project, parts=parts, offsets=((-39, 0), (39, 0)),
                            title=f'Faucet {kind}: A reference, B bridge treatment',
                            z_trim=trim, plate_border=80)
    with ZipFile(project) as z, ZipFile(SOURCE) as parent:
        members = {n:z.read(n) for n in z.namelist()}
        source_config = ET.fromstring(parent.read('Metadata/model_settings.config'))
        source_name = 'industrial-shell-base' if kind == 'foot' else 'faucet-shell-tip'
        original_config = next(o for o in source_config.findall('object')
                               if o.find("metadata[@key='name']").get('value') == source_name)
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings['filament_colour'] = ['#000000' if printer == 'Mark1' else '#161616']
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    config = ET.fromstring(members['Metadata/model_settings.config'])
    model = ET.fromstring(members['3D/3dmodel.model'])
    relationships = ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    ranges = ET.Element('objects')
    specimens = []
    for index, row in enumerate(report['parts']):
        obj = config.find(f"object[@id='{row['object_id']}']")
        for setting in original_config.findall('metadata'):
            key = setting.get('key')
            if key and key not in ('name', 'extruder'):
                writer.metadata(obj, key, setting.get('value'))
        writer.metadata(obj, 'bridge_flow', '1' if index == 0 else '1.25')
        if kind == 'foot':
            group = ET.SubElement(ranges, 'object', id=str(index+1))
            for low, high in json.loads((INDUSTRIAL/'finish-selection.json').read_text())['base_fine_bands_print_z_mm']:
                if low < top:
                    r = ET.SubElement(group, 'range', min_z=f'{low:.4f}', max_z=f'{min(high, top):.4f}')
                    ET.SubElement(r, 'option', opt_key='layer_height').text = '0.12'
            region = trimesh.creation.box(extents=[61, 61, 14.02])
            region.apply_translation([0, 0, 7.0])
            helpers.add_foot_modifier(members, model, config, relationships, row, region, index)
        specimens.append(dict(id='AB'[index], **row, treatment=index == 1,
                              native_bridge_flow=1.0 if index == 0 else 1.25,
                              model_fan_after_first_three_layers_percent=None if index == 0 else 70,
                              bridge_speed_mm_s=None if index == 0 else 15))
    members['Metadata/model_settings.config'] = writer.xml(config)
    members['3D/3dmodel.model'] = writer.xml(model)
    members['3D/_rels/3dmodel.model.rels'] = writer.xml(relationships).replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    if kind == 'foot':
        members['Metadata/layer_config_ranges.xml'] = writer.xml(ranges)
    paint = []
    for row in report['parts']:
        paint.append(industrial.enforce_rear_seam(members, report,
            dict(part=row['name'], half_width_mm=0.25 if kind == 'foot' else 0.0,
                 **({} if kind == 'foot' else {'surface':'curved_outer_arc'}))))
    writer.archive_write(project, members)
    report.update(printer=printer, kind=kind, project=str(project.relative_to(ROOT)),
                  project_sha256=writer.digest(project.read_bytes()), specimens=specimens,
                  source_geometry=origin, rear_seam_paint=paint, requested_z_trim_mm=trim,
                  production_project_sha256=writer.digest(SOURCE.read_bytes()),
                  candidate_scope='Native per-object bridge flow; local model cooling and Bridge feed treatment applied by finish.py. XYZ and native E remain unchanged.',
                  authorization_quote='Please take a look at what your peer Tine failure learned with me and see if we can apply some of that to these faucet defects.\n\nBoth printers are available.')
    save(folder/'preparation.json', report)
    save(project.with_suffix('.print.json'), report)
    native = WORK/printer.lower()
    native.mkdir(parents=True, exist_ok=True)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
               '--arrange', '0', '--orient', '0', '--outputdir', str(native),
               '--export-3mf', 'native.gcode.3mf', str(project)]
    save(folder/'slice-command.json', {'argv':command})
    print(json.dumps({'printer':printer, 'project':str(project.relative_to(ROOT)), 'native':str(native)}), flush=True)
    with (native/'slice.log').open('w') as log:
        subprocess.run(command, cwd=native, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'))
    result = json.loads((native/'result.json').read_text())
    if result.get('return_code') != 0:
        raise ValueError(result.get('error_string'))
    (folder/'native.gcode.3mf').write_bytes((native/'native.gcode.3mf').read_bytes())
    save(folder/'slice-result.json', result)
    print(json.dumps({'printer':printer, 'plates':result['sliced_plates']}), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'Mark1':
        prepare('Mark1', 'tip', -105, 40.0)
    elif sys.argv[1] == 'Mark2':
        prepare('Mark2', 'foot', -15, 33.8)
    else:
        raise ValueError('Choose Mark1 or Mark2')
