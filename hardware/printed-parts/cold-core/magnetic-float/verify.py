"""Read the float's sealing envelope, assembly motions and emitted print commands."""

import argparse
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import trimesh
import magnetic_float as m

HERE = Path(__file__).resolve().parent


def geometry():
    parts = m.build()
    for name, shape in parts.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name
        if name != 'magnet':
            mesh = trimesh.load(HERE / f'{name}.stl', force='mesh', process=True)
            assert mesh.is_watertight and mesh.is_winding_consistent, name
            boundary_volumes = [component.volume for component in mesh.split()]
            assert sum(volume > 0 for volume in boundary_volumes) == 1, name
            assert sum(volume < 0 for volume in boundary_volumes) == (1 if name == 'body-petg' else 0), name
            assert abs(mesh.volume - shape.Volume()) / shape.Volume() < 0.002, name
    envelope = m.annulus(m.outer_radius, m.bore_radius, 0, m.height)
    interior = m.annulus(m.core_outer_radius, m.core_inner_radius, m.skin, m.roof_bottom)
    sealing_skin = envelope.cut(interior)
    assert sealing_skin.cut(parts['body-petg']).Volume() < 1e-6
    assert parts['body-petg'].cut(envelope).Volume() < 1e-6
    assert parts['body-petg'].intersect(parts['body-aero']).Volume() < 1e-6
    roof_cut = m.box(m.diameter + m.skin * 2, m.diameter + m.skin * 2,
                     m.roof_bottom, m.height + m.skin)
    paused_body = parts['body-petg'].cut(roof_cut).fuse(parts['body-aero'])
    maximum_magnet = m.annulus((m.magnet_od + m.magnet_tolerance) / 2,
                              (m.magnet_id - m.magnet_tolerance) / 2,
                              m.magnet_seat, m.magnet_seat + m.magnet_height + m.magnet_tolerance)
    for lift in range(0, 21, 2):
        assert maximum_magnet.translate((0, 0, lift)).intersect(paused_body).Volume() < 1e-6
    motion = {}
    for stem in ('insert', 'insert-loose'):
        collar, aero = parts[stem + '-petg'], parts[stem + '-aero']
        assert collar.intersect(aero).Volume() < 1e-6
        cap = collar.fuse(aero)
        for lift in range(0, 17):
            assert cap.translate((0, 0, lift)).intersect(paused_body).Volume() < 1e-6, (stem, lift)
        for angle in range(0, 91, 3):
            rotated = cap.rotate((0, 0, 0), (0, 0, 1), angle)
            assert rotated.intersect(paused_body).Volume() < 1e-6, (stem, angle)
        locked = cap.rotate((0, 0, 0), (0, 0, 1), m.lock_angle)
        assert locked.intersect(maximum_magnet).Volume() < 1e-6
        assert locked.translate((0, 0, m.lug_axial_clearance)).intersect(paused_body).Volume() < 1e-6
        blocking = locked.translate((0, 0, m.lug_axial_clearance + 0.2)).intersect(paused_body).Volume()
        assert blocking > 0.5, stem
        assert aero.translate((0, 0, 0.2)).intersect(collar).Volume() > 1
        key = (parts['turning-key'].rotate((0, 0, 0), (1, 0, 0), 180)
               .rotate((0, 0, 0), (0, 0, 1), 45)
               .translate((0, 0, m.insert_top + m.key_bar_height)))
        assert key.intersect(cap).Volume() < 1e-6, (stem, 'key socket')
        motion[stem] = {'insertion_and_rotation_clear': True,
                       'lift_stopped_before_roof': True, 'blocking_overlap_cc': blocking / 1000,
                       'aero_mechanically_captive': True, 'turning_key_fits': True}
    return {'valid_solids': len(parts), 'closed_print_meshes': len(parts) - 1,
            'continuous_petg_skin_mm': m.skin, 'maximum_tolerance_magnet_insertion_clear': True,
            'motions': motion}


FEATURES = {'Outer wall', 'Inner wall', 'Overhang wall', 'Sparse infill',
            'Internal solid infill', 'Top surface', 'Bottom surface', 'Bridge',
            'Internal Bridge', 'Gap infill'}


def read_paths(gcode, plate):
    x = y = z = layer_z = 0.0
    tool = 0
    feature = ''
    masses = {}
    pauses = []
    roof_layers = set()
    body_layer_tools = {}
    for raw in gcode.splitlines():
        if raw.startswith('; Z_HEIGHT:'):
            layer_z = float(raw.split(':')[1])
        if raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        command = raw.split(';', 1)[0].strip()
        if command == 'M400 U1':
            pauses.append({'before_layer_z_mm': layer_z, 'commanded_z_before_pause_mm': z})
        if command in ('T0', 'T1'):
            tool = int(command[1:])
        if not re.match(r'^G(?:0|1|2|3) ', command):
            continue
        values = {key: float(value) for key, value in re.findall(r'\b([XYZE])(-?[\d.]+)', command)}
        old_x, old_y = x, y
        x, y, z = values.get('X', x), values.get('Y', y), values.get('Z', z)
        extrusion = values.get('E', 0)
        if extrusion <= 0 or feature not in FEATURES or math.hypot(x - old_x, y - old_y) < 1e-5:
            continue
        if plate == 2:
            name = 'body' if math.hypot(x - 150, y - 145) < m.outer_radius + 0.01 else None
        else:
            name = next((name for name, cx, cy, radius in
                [('insert', 115, 145, 13), ('insert-loose', 155, 145, 13), ('key', 135, 180, 16)]
                if math.hypot(x - cx, y - cy) < radius), None)
        if name is None:
            continue
        masses.setdefault(name, [0.0, 0.0])[tool] += extrusion * math.pi * (1.75 / 2) ** 2 / 1000 * (1.25, 1.21)[tool]
        if name == 'body':
            body_layer_tools.setdefault(round(layer_z, 3), set()).add(tool)
            if layer_z > m.roof_bottom:
                roof_layers.add(round(layer_z, 3))
                assert tool == 0, 'Aero in the sealing roof'
                assert len(pauses) == 1, 'Roof extrusion precedes insertion pause'
    if plate == 2:
        assert len(pauses) == 1 and math.isclose(pauses[0]['before_layer_z_mm'], m.roof_bottom + 0.2)
        assert sorted(roof_layers) == [round(m.roof_bottom + 0.2 * i, 3) for i in range(1, round(m.skin / 0.2) + 1)]
        assert len(body_layer_tools) == round(m.height / 0.2)
        assert all(0 in tools for tools in body_layer_tools.values()), 'PETG wall omitted on a layer'
        assert all(1 not in tools for h, tools in body_layer_tools.items() if h > m.insert_bottom + 0.001)
    else:
        assert not pauses
    return {'object_material_mass_g': masses, 'insertion_pauses': pauses,
            'roof_layers_mm': sorted(roof_layers), 'body_petg_layers': len(body_layer_tools)}


def print_project(path):
    with zipfile.ZipFile(path) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        expected = {'filament_flow_ratio': ['0.97', '0.38'], 'filament_map': ['1', '2'],
            'nozzle_temperature': ['250', '250'], 'textured_plate_temp': ['65', '65'],
            'layer_height': '0.2', 'sparse_infill_density': '100%', 'enable_support': '0',
            'nozzle_diameter': ['0.4', '0.4']}
        for key, value in expected.items():
            assert settings[key] == value, (key, settings[key], value)
        config = ET.fromstring(archive.read('Metadata/model_settings.config'))
        material_parts = []
        for obj in config.findall('object'):
            parent = {node.get('key'): node.get('value') for node in obj.findall('metadata')}
            for part in obj.findall('part'):
                meta = {node.get('key'): node.get('value') for node in part.findall('metadata')}
                expected_slot = '2' if meta['name'].endswith('aero') else '1'
                assert meta.get('extruder', parent.get('extruder', '1')) == expected_slot
                assert 'magnet' not in meta['name']
                material_parts.append(meta['name'])
        assert len(material_parts) == 7
        plates = [read_paths(archive.read(f'Metadata/plate_{i}.gcode').decode(), i) for i in (1, 2)]
        mass = sum(plates[0]['object_material_mass_g']['insert']) + sum(plates[1]['object_material_mass_g']['body']) + m.magnet_mass
        info = json.loads((HERE / 'design.json').read_text())
        reserve = info['water_displacement_g'] - mass
        assert reserve > 4, ('insufficient sliced reserve', reserve)
        return {'project_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'verified_settings': expected, 'material_parts': material_parts,
                'plates': plates, 'assembled_mass_from_model_extrusion_g': mass,
                'reserve_from_model_extrusion_g': reserve,
                'mass_scope': 'Positive extrusion on object toolpaths; excludes purge, brim, spare insert and key. Nominal filament diameter/density.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE / 'verification.json')
    args = parser.parse_args()
    report = {'geometry': geometry(), 'print': print_project(args.project),
              'physical_prints': 'No physical float print recorded.'}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
