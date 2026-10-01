"""Verify the float geometry, sourced material settings and emitted assembly jobs."""

import argparse
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import trimesh
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
import magnetic_float as m

HERE = Path(__file__).resolve().parent
FEATURES = {'Outer wall', 'Inner wall', 'Overhang wall', 'Sparse infill', 'Floating vertical shell',
            'Internal solid infill', 'Top surface', 'Bottom surface', 'Bridge',
            'Internal Bridge', 'Gap infill', 'Ironing'}
MATERIAL_KEYS = (
    'nozzle_temperature', 'nozzle_temperature_initial_layer', 'filament_flow_ratio',
    'filament_density', 'filament_max_volumetric_speed', 'chamber_temperatures',
    'eng_plate_temp', 'eng_plate_temp_initial_layer',
    'textured_plate_temp', 'textured_plate_temp_initial_layer',
    'fan_min_speed', 'fan_max_speed', 'additional_cooling_fan_speed',
    'overhang_fan_speed', 'close_fan_the_first_x_layers',
    'filament_retraction_length', 'filament_wipe_distance', 'filament_z_hop',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry():
    parts = m.build()
    meshes = {}
    for name, shape in parts.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name
        if name != 'magnet':
            mesh = trimesh.load(HERE / f'{name}.stl', force='mesh', process=True)
            assert mesh.is_watertight and mesh.is_winding_consistent, name
            assert abs(mesh.bounds[0, 2]) < 1e-6, ('print bottom', name)
            error = abs(mesh.volume - shape.Volume()) / shape.Volume()
            assert error < 0.002, name
            meshes[name] = {'volume_relative_error': error, 'bottom_z_mm': float(mesh.bounds[0, 2])}
    envelope = m.annulus(m.outer_radius, m.bore_radius, 0, m.height)
    interior = m.annulus(m.core_outer_radius, m.core_inner_radius, m.floor, m.roof_bottom)
    fill = parts['body-aero'].fuse(parts['insert-aero'], parts['magnet'])
    allowed_voids = m.magnet_pocket().cut(parts['magnet'])
    for bottom, top in ((m.floor, m.insert_bottom), (m.insert_bottom, m.insert_top)):
        blank = m.annulus(m.core_outer_radius, m.core_inner_radius, bottom, top)
        allowed_voids = allowed_voids.fuse(blank.cut(m.lead_in(blank)))
    voids = interior.cut(fill)
    assert voids.cut(allowed_voids).Volume() < 1e-6
    assert allowed_voids.cut(voids).Volume() < 1e-6
    assert fill.cut(interior).Volume() < 1e-6
    assert envelope.cut(interior).cut(parts['body-petg']).Volume() < 1e-6
    for i, first in enumerate(parts.values()):
        for second in list(parts.values())[i + 1:]:
            assert first.intersect(second).Volume() < 1e-6
    roof_cut = m.box(m.diameter + 2, m.diameter + 2, m.roof_bottom, m.height + 1)
    open_skin = parts['body-petg'].cut(roof_cut)
    for name in ('body-aero', 'insert-aero', 'magnet'):
        for lift in (0, 0.2, 1, 5, 10, 20, 40, 60):
            assert parts[name].translate((0, 0, lift)).intersect(open_skin).Volume() < 1e-6, name
    maximum_magnet = m.annulus((m.magnet_od + m.magnet_tolerance) / 2,
                              (m.magnet_id - m.magnet_tolerance) / 2,
                              m.magnet_seat, m.magnet_seat + m.magnet_height + m.magnet_tolerance)
    assert maximum_magnet.intersect(open_skin).Volume() < 1e-6
    assert maximum_magnet.intersect(parts['body-aero']).Volume() < 1e-6
    assert maximum_magnet.intersect(parts['insert-aero']).Volume() < 1e-6
    roof_support = m.annulus(m.core_outer_radius, m.core_inner_radius,
                            m.roof_bottom - 0.02, m.roof_bottom)
    assert roof_support.cut(parts['insert-aero']).Volume() < 1e-6
    measurements = m.measurements(parts)
    assert measurements['magnet_pocket_minimum_compensated_radial_clearance_mm'] >= 0.05 - 1e-6
    assert measurements['magnet_pocket_minimum_depth_clearance_mm'] >= 0.125 - 1e-6
    return {'valid_solids': 4, 'meshes': meshes,
            'petg_thickness_mm': {'outer_wall': m.outer_wall, 'bore_wall': m.bore_wall,
                                  'floor': m.floor, 'roof': m.roof},
            'nominal_unfilled_volume_cc': voids.Volume() / 1000,
            'unfilled_volume_scope': 'Lower insertion chamfers and RC62 pocket clearance only.',
            'nominal_material_overlap_cc': 0.0,
            'separate_core_insertion_clear': True, 'magnet_tolerance_clear_of_petg': True,
            'magnet_tolerance_clear_of_aero': True,
            'magnet_pocket_minimum_compensated_radial_clearance_mm': measurements['magnet_pocket_minimum_compensated_radial_clearance_mm'],
            'magnet_pocket_minimum_depth_clearance_mm': measurements['magnet_pocket_minimum_depth_clearance_mm'],
            'insert_top_meets_roof_underside': m.insert_top == m.roof_bottom,
            'insert_supports_full_roof_annulus': True,
            'aero_lower_lead_in_mm': m.insertion_lead,
            'fit_allowances_radial_mm': {'body-aero': m.core_fit_allowance,
                                         'insert-aero': m.insert_fit_allowance}}


def radial_bounds(x0, y0, x1, y1):
    ax, ay, bx, by = x0 - 150, y0 - 145, x1 - 150, y1 - 145
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    t = max(0, min(1, -(ax * dx + ay * dy) / length2)) if length2 else 0
    return math.hypot(ax + t * dx, ay + t * dy), max(math.hypot(ax, ay), math.hypot(bx, by))


def wall_coverage(segments, layer_z):
    footprint = unary_union([LineString([a, b]).buffer(width / 2, resolution=8)
                             for a, b, width in segments])
    samples = []
    for degrees in range(0, 360, 30):
        angle = math.radians(degrees)
        ray = LineString([(r * math.cos(angle), r * math.sin(angle)) for r in (0, m.outer_radius + 1)])
        hit = ray.intersection(footprint)
        lines = list(hit.geoms) if hasattr(hit, 'geoms') else [hit]
        intervals = sorted(sorted([math.hypot(*line.coords[0]), math.hypot(*line.coords[-1])])
                           for line in lines if line.geom_type == 'LineString')
        assert len(intervals) == 2, ('Gap in nominal wall bead coverage', degrees, intervals)
        bore, outer = intervals
        assert bore[1] - bore[0] >= m.bore_wall - 0.05
        assert outer[1] - outer[0] >= m.outer_wall - 0.05
        samples.append({'azimuth_deg': degrees, 'radial_intervals_mm': intervals})
    return {'layer_z_mm': layer_z, 'samples': samples,
            'basis': 'Nominal bead footprints from emitted LINE_WIDTH, not measured printed porosity.'}


def pocket_clearance(segments, layer_z):
    footprint = unary_union([LineString([a, b]).buffer(width / 2, resolution=8)
                             for a, b, width in segments])
    maximum_magnet = Point(0, 0).buffer((m.magnet_od + m.magnet_tolerance) / 2, resolution=180).difference(
        Point(0, 0).buffer((m.magnet_id - m.magnet_tolerance) / 2, resolution=180))
    assert segments and not footprint.intersects(maximum_magnet), 'Aero paths obstruct the RC62 pocket'
    distance = footprint.distance(maximum_magnet)
    assert distance > 0.02, ('RC62 nominal path clearance', distance)
    return {'layer_z_mm': layer_z,
            'minimum_maximum_size_magnet_clearance_mm': distance,
            'basis': 'Nominal emitted LINE_WIDTH footprints and RC62 maximum dimensional tolerance; not measured printed fit.'}


def read_paths(gcode, part, layer, first_layer, filament_density, side):
    x = y = z = layer_z = e_position = 0.0
    feature = ''
    relative_e = True
    material_tool = None
    object_mass = 0.0
    layers, roof_layers, walls = set(), set(), {}
    pauses, tools, thermal = [], set(), []
    bounds = [float('inf'), 0.0]
    min_bore_path = float('inf')
    object_started = False
    deposited_before_pause = None
    remaining_minutes = None
    width = 0.0
    wall_segments = []
    pocket_segments = []
    sample_z = round(first_layer + layer * round((m.height / 2 - first_layer) / layer), 4)
    pocket_sample_z = round(layer * round(((m.magnet_seat + m.insert_bottom) / 2 - m.floor) / layer), 4)
    for raw in gcode.splitlines():
        if raw.startswith('; Z_HEIGHT:'):
            layer_z = round(float(raw.split(':')[1]), 4)
        if raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        if raw.startswith('; LINE_WIDTH:'):
            width = float(raw.split(':', 1)[1])
        command = raw.split(';', 1)[0].strip()
        if command.startswith('M73 '):
            remaining = re.search(r'\bR(\d+)\b', command)
            if remaining:
                remaining_minutes = int(remaining[1])
        if command == 'M83':
            relative_e = True
        if command == 'M82':
            relative_e = False
        if command.startswith(('M104 ', 'M109 ', 'M140 ', 'M190 ', 'M141 ', 'M191 ')):
            thermal.append(command)
        selection = re.match(r'^T(\d+)\s+H(-?\d+)', command)
        if selection and int(selection[1]) < 100:
            assert selection[1] == '0', ('unexpected material', command)
            material_tool = int(selection[1])
        if command == 'M400 U1':
            assert object_started
            deposited_before_pause = max(layers)
            pauses.append({'before_layer_z_mm': layer_z, 'last_deposited_layer_z_mm': deposited_before_pause,
                           'slicer_remaining_minutes_at_pause': remaining_minutes})
        if command.startswith('G92 '):
            found = re.search(r'\bE(-?[\d.]+)', command)
            if found:
                e_position = float(found[1])
        if not re.match(r'^G(?:0|1) ', command):
            continue
        values = {key: float(value) for key, value in re.findall(r'\b([XYZE])(-?[\d.]+)', command)}
        old_x, old_y = x, y
        x, y, z = values.get('X', x), values.get('Y', y), values.get('Z', z)
        e = values.get('E')
        extrusion = (e if relative_e else e - e_position) if e is not None else 0
        if e is not None:
            e_position = e_position + e if relative_e else e
        if extrusion <= 0 or feature not in FEATURES or math.hypot(x - old_x, y - old_y) < 1e-5:
            continue
        rmin, rmax = radial_bounds(old_x, old_y, x, y)
        if rmax > m.outer_radius + 0.5:
            continue
        object_started = True
        assert material_tool == 0, ('unexpected model material tool', material_tool)
        tools.add(material_tool)
        layers.add(layer_z)
        object_mass += extrusion * math.pi * (1.75 / 2) ** 2 / 1000 * filament_density
        if part == 'body-aero' and layer_z == pocket_sample_z:
            pocket_segments.append(((old_x - 150, old_y - 145), (x - 150, y - 145), width))
        if part == 'body-petg':
            if layer_z == sample_z and feature in ('Outer wall', 'Inner wall'):
                wall_segments.append(((old_x - 150, old_y - 145), (x - 150, y - 145), width))
            min_bore_path = min(min_bore_path, rmin)
            assert rmin >= m.bore_radius - 0.02, ('extrusion crosses the open guide bore', layer_z, rmin)
            if m.floor + 1e-4 < layer_z <= m.roof_bottom + 1e-4:
                assert rmax <= m.core_inner_radius + 0.04 or rmin >= m.core_outer_radius - 0.04, (
                    'extrusion obstructs separate core', layer_z, feature, rmin, rmax)
            rings = walls.setdefault(layer_z, set())
            if feature in ('Outer wall', 'Inner wall'):
                if rmax < m.core_inner_radius + 0.1:
                    rings.add('bore')
                if rmin > m.core_outer_radius - 0.1:
                    rings.add('outer')
            if layer_z > m.roof_bottom + 1e-4:
                assert len(pauses) == 1, 'Roof deposited before assembly pause'
                roof_layers.add(layer_z)
        elif feature == 'Outer wall' and m.insertion_lead + 0.2 <= layer_z <= 5:
            bounds[0] = min(bounds[0], rmin)
            bounds[1] = max(bounds[1], rmax)
    expected_height = {'body-aero': m.insert_bottom - m.floor,
                       'insert-aero': m.insert_height, 'body-petg': m.height}[part]
    expected_layers = {round(first_layer + layer * i, 4)
                       for i in range(1 + round((expected_height - first_layer) / layer))}
    assert layers == expected_layers, (part, len(layers), len(expected_layers), sorted(layers ^ expected_layers))
    if part == 'body-petg':
        assert len(pauses) == 1
        assert math.isclose(pauses[0]['before_layer_z_mm'], m.roof_bottom + layer)
        assert math.isclose(deposited_before_pause, m.roof_bottom)
        assert all(rings == {'bore', 'outer'} for rings in walls.values()), 'Missing sealing wall'
        assert len(roof_layers) == round(m.roof / layer)
    else:
        assert not pauses
        # A 0.48 mm nominal perimeter centers half a line inside each compensated face.
        assert math.isclose(bounds[1], m.core_outer_radius + 0.05 - 0.24, abs_tol=0.06), bounds
        assert math.isclose(bounds[0], m.core_inner_radius - 0.05 + 0.24, abs_tol=0.06), bounds
    return {'part': part, 'object_extrusion_mass_g': object_mass, 'material_tools': sorted(tools),
            'mapped_extruder': side,
            'layers': len(layers), 'print_height_mm': max(layers), 'insertion_pauses': pauses,
            'roof_layers_mm': sorted(roof_layers),
            'aero_perimeter_centerline_radii_mm': bounds if part != 'body-petg' else None,
            'minimum_guide_bore_centerline_radius_mm': min_bore_path if part == 'body-petg' else None,
            'wall_coverage': wall_coverage(wall_segments, sample_z) if part == 'body-petg' else None,
            'magnet_pocket_clearance': pocket_clearance(pocket_segments, pocket_sample_z) if part == 'body-aero' else None,
            'thermal_commands': sorted(set(thermal))}


def print_project(path, key, provenance):
    from prepare_print import JOBS, PRESETS, system_preset
    job = JOBS[key]
    stock, _, ids = system_preset(PRESETS, 'filament', job['filament'], {})
    expected_material = {**stock, **provenance['filament_changes']}
    with zipfile.ZipFile(path) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        effective = {}
        for name in MATERIAL_KEYS:
            if name not in expected_material:
                continue
            value = expected_material[name]
            expected = [value[0]] if isinstance(value, list) else value
            assert settings[name] == expected, (key, name, settings[name], expected)
            effective[name] = settings[name]
        assert settings['filament_ids'] == [ids['filament_id']]
        assert settings['filament_colour'] == [job['colour']]
        assert settings['filament_map'] == [str(job['side'])]
        assert settings['enable_support'] == '0'
        assert settings['enable_prime_tower'] == '0'
        assert settings['sparse_infill_density'] == '100%'
        assert settings['nozzle_diameter'] == ['0.6', '0.4']
        assert float(settings['layer_height']) == provenance['layer_height_mm']
        assert float(settings['initial_layer_print_height']) == provenance['first_layer_height_mm']
        if key == 'aero':
            assert settings['filament_flow_ratio'] == ['0.52']
            assert settings['nozzle_temperature'] == ['270']
            assert settings['filament_density'] == ['0.99']
            assert all(float(v) == 5000 for v in settings['default_acceleration'])
            assert all(float(v) == 3000 for v in settings['outer_wall_acceleration'])
        else:
            assert ids['filament_id'] == 'GFG01'
            assert settings['filament_max_volumetric_speed'] == ['16']
            assert float(settings['filament_density'][0]) == m.petg_density
            assert settings['filament_flow_ratio'] == ['1.02']
            assert settings['nozzle_temperature'] == ['260']
            assert settings['nozzle_temperature_initial_layer'] == ['255']
            assert settings['seam_position'] == 'random'
            assert settings['seam_gap'] == '0%'
            assert settings['seam_slope_type'] == 'all'
            assert settings['seam_slope_conditional'] == '0'
            assert settings['ironing_type'] == 'top'
        config = ET.fromstring(archive.read('Metadata/model_settings.config'))
        parts = []
        for obj in config.findall('object'):
            meta = {n.get('key'): n.get('value') for n in obj.findall('metadata')}
            if key == 'aero':
                assert float(meta['xy_contour_compensation']) == 0.05
                assert float(meta['xy_hole_compensation']) == -0.05
            for part in obj.findall('part'):
                pm = {n.get('key'): n.get('value') for n in part.findall('metadata')}
                assert pm.get('extruder', meta.get('extruder')) == '1'
                parts.append(pm['name'])
        assert sorted(parts) == sorted(job['parts'])
        info = ET.fromstring(archive.read('Metadata/slice_info.config'))
        plates = []
        assert len(info.findall('plate')) == len(job['parts'])
        for number, part in enumerate(job['parts'], 1):
            node = info.findall('plate')[number - 1]
            meta = {n.get('key'): n.get('value') for n in node.findall('metadata')}
            filaments = [n.attrib for n in node.findall('filament')]
            nozzles = [n.attrib for n in node.findall('nozzle')]
            assert len(filaments) == 1 and filaments[0]['tray_info_idx'] == ids['filament_id']
            assert len(nozzles) == 1 and int(nozzles[0]['extruder_id']) == job['side']
            assert math.isclose(float(nozzles[0]['nozzle_diameter']), job['nozzle'])
            assert meta['support_used'] == 'false'
            paths = read_paths(archive.read(f'Metadata/plate_{number}.gcode').decode(),
                               part, provenance['layer_height_mm'], provenance['first_layer_height_mm'],
                               float(expected_material['filament_density'][0]), job['side'])
            plate_data = json.loads(archive.read(f'Metadata/plate_{number}.json'))
            assert len(plate_data['bbox_objects']) == 1
            target_bed = 'eng_plate_temp' if key == 'aero' else 'textured_plate_temp'
            bed_temp = expected_material[target_bed][0]
            assert any(re.match(rf'M(?:140|190) S{bed_temp}(?:\s|$)', cmd)
                       for cmd in paths['thermal_commands']), ('bed target', key)
            initial_temp = expected_material['nozzle_temperature_initial_layer'][0]
            assert f'M104 S{initial_temp} T{2 - job["side"]}' in paths['thermal_commands']
            plates.append({'plate': number, 'estimated_seconds': int(meta['prediction']),
                           'total_material_g': float(filaments[0]['used_g']), **paths})
        return {'filename': job['filename'], 'project_sha256': sha(path),
                'material': job['filament'], 'material_settings_match_recipe': True,
                'material_settings_match_stock': key == 'aero',
                'effective_material_settings': effective, 'plates': plates}


def verify_directory(directory):
    from prepare_print import JOBS
    result = {'geometry': geometry(), 'jobs': {}, 'assemblies': {},
              'mass_scope': 'Object extrusion only, nominal filament diameter/density; excludes brim and startup purge.',
              'physical_prints': 'No physical float print recorded.',
              'pressure_rating': 'No hydrostatic endurance result recorded.'}
    profile = {'jobs': {}}
    for key, job in JOBS.items():
        provenance = json.loads((directory / f'{key}-provenance.json').read_text())
        assert provenance['geometry_sha256'] == sha(HERE / 'design.json')
        for name, digest in provenance['meshes_sha256'].items():
            assert digest == sha(HERE / f'{name}.stl'), name
        if key == 'petg':
            assert provenance['petg_recipe_sha256'] == sha(HERE / 'petg-water-recipe.json')
        report = print_project(directory / key / job['filename'], key, provenance)
        result['jobs'][key] = report
        profile['jobs'][key] = {**provenance, 'project_sha256': report['project_sha256'],
                               'effective_material_settings': report['effective_material_settings'],
                               'plates': [{k: p[k] for k in ('plate', 'part', 'estimated_seconds',
                                                            'total_material_g', 'object_extrusion_mass_g')}
                                          for p in report['plates']]}
    aero_mass = sum(p['object_extrusion_mass_g'] for p in result['jobs']['aero']['plates'])
    displacement = json.loads((HERE / 'design.json').read_text())['water_displacement_g']
    for key in ('petg',):
        petg_mass = result['jobs'][key]['plates'][0]['object_extrusion_mass_g']
        total = aero_mass + petg_mass + m.magnet_mass
        reserve = displacement - total
        assert reserve > 3, ('sliced buoyancy reserve', key, reserve)
        result['assemblies'][key] = {'aero_g': aero_mass, 'petg_g': petg_mass,
                                     'magnet_g': m.magnet_mass, 'assembled_mass_g': total,
                                     'reserve_lift_g': reserve,
                                     'upright_freeboard_mm': m.height * reserve / displacement}
    return result, profile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    report, _ = verify_directory(args.directory)
    print(json.dumps(report, indent=2))
