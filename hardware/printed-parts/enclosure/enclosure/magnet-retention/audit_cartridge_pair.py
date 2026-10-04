"""Read the combined native cartridge/cap archive without printer communication."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

import numpy as np
import trimesh
from shapely import union_all
from shapely.geometry import LineString, box

from prepare_prints import TAG, PROD, HERE, ENC, ROOT, SETTING, members, sha
from audit_prints import read_job, dense_road_check, NUMBER

sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet'))
from refresh_print_project import slice_review


def native_components(payload, job):
    """Bind each native normal volume and modifier to its own source and placement."""
    config = ET.fromstring(payload['Metadata/model_settings.config'])
    model = ET.fromstring(payload['3D/3dmodel.model'])
    rows, support_parts = [], []
    for source in job['components']:
        name = source['part']
        obj = next(o for o in config.findall('object') if
                   o.find("metadata[@key='name']").get('value') == source['native_object_name'])
        root_id = obj.get('id')
        native_root = next(o for o in model.iter(TAG('object')) if o.get('id') == root_id)
        build = next(i for i in model.iter(TAG('item')) if i.get('objectid') == root_id)
        transform = np.array([float(v) for v in build.get('transform').split()])
        rotation = np.array(source['machine_to_bed_rotation_matrix'])
        translation = np.array(source['machine_to_bed_translation_mm'])
        mesh = trimesh.load_mesh(ENC / f'enclosure-{name}.stl', process=True)
        parts = {p.get('id'): p for p in obj.findall('part')}
        modifier_rows = []
        vertex_error = None
        normal_count = 0
        for component in native_root.iter(TAG('component')):
            part = parts[component.get('objectid')]
            values = {m.get('key'): m.get('value') for m in part.findall('metadata')}
            path = component.get(f'{{{PROD}}}path').lstrip('/')
            document = ET.fromstring(payload[path])
            native = next(o for o in document.iter(TAG('object')) if o.get('id') == component.get('objectid'))
            vertices = np.array([[float(v.get(axis)) for axis in 'xyz'] for v in native.iter(TAG('vertex'))])
            ct = np.array([float(v) for v in component.get('transform').split()])
            bed = (vertices @ ct[:9].reshape(3, 3) + ct[9:]) @ transform[:9].reshape(3, 3) + transform[9:]
            machine = (bed - translation) @ rotation.T
            if part.get('subtype') == 'normal_part':
                normal_count += 1
                faces = np.array([[int(t.get(key)) for key in ('v1', 'v2', 'v3')]
                                  for t in native.iter(TAG('triangle'))])
                assert faces.shape == mesh.faces.shape and np.array_equal(faces, mesh.faces)
                assert machine.shape == mesh.vertices.shape
                vertex_error = float(np.max(np.abs(machine - mesh.vertices)))
            else:
                region = next(r for r in source['solid_host_regions'] if r['name'] == values['name'])
                bounds = np.column_stack((machine.min(0), machine.max(0))).flatten()
                modifier_rows.append(dict(name=values['name'], machine_bounds_mm=bounds.tolist(),
                    density=values.get('sparse_infill_density'), pattern=values.get('sparse_infill_pattern'),
                    pass_check=values.get('sparse_infill_density') == '100%' and
                    values.get('sparse_infill_pattern') == 'zig-zag' and
                    np.allclose(bounds, region['applied_machine_bounds_mm'], atol=0.002, rtol=0)))
        assert sha(ENC / f'enclosure-{name}.stl') == source['source_stl_sha256']
        assert sha(ENC / f'enclosure-{name}.step') == source['source_step_sha256']
        rows.append(dict(part=name, normal_volumes=normal_count, embedded_vertex_error_mm=vertex_error,
                         source_stl_sha256=source['source_stl_sha256'], modifiers=modifier_rows,
                         pass_check=normal_count == 1 and vertex_error < 0.00003 and
                         len(modifier_rows) == len(source['solid_host_regions']) and
                         all(r['pass_check'] for r in modifier_rows)))
        instance = next(i for i in config.findall('plate/model_instance') if
                        i.find("metadata[@key='object_id']").get('value') == root_id)
        support_parts.append(dict(name=f'enclosure-{name}', source=str((ENC / f'enclosure-{name}.stl').relative_to(ROOT)),
            stl_sha256=source['source_stl_sha256'], plate=1, object_id=root_id,
            build_transform=transform.tolist(), plate_translation_mm=transform[9:].tolist(),
            identify_id=int(instance.find("metadata[@key='identify_id']").get('value')),
            rotation_x_degrees=180 if name == 'pump-cap' else 0))
    return rows, support_parts


def cap_roads(data, source, identify_id):
    """Read the cap's own model roads back into its crown-down machine frame."""
    rotation = np.array(source['machine_to_bed_rotation_matrix'])
    translation = np.array(source['machine_to_bed_translation_mm'])
    feature, width, height, z, owner = '', 0.45, 0.24, 0., None
    actual = dict(X=0., Y=0., Z=0., E=0.)
    relative_e = False
    layers = {}
    first, second = [], []
    features = Counter()
    for raw in data.splitlines():
        line = raw.decode()
        if line.startswith('; FEATURE: '):
            feature = line.split(': ', 1)[1]; continue
        if line.startswith('; LINE_WIDTH: '):
            width = float(line.split(': ', 1)[1]); continue
        if line.startswith('; LAYER_HEIGHT: '):
            height = float(line.split(': ', 1)[1]); continue
        if line.startswith('; Z_HEIGHT: '):
            z = float(line.split(': ', 1)[1]); continue
        if line.startswith('; OBJECT_ID:'):
            owner = int(line.split(':', 1)[1])
        if line.startswith('; start printing object, unique label id:'):
            owner = int(line.rsplit(':', 1)[1])
        if line.startswith('; stop printing object'):
            owner = None
        if line.startswith('M83'):
            relative_e = True; continue
        if line.startswith('M82'):
            relative_e = False; continue
        cmd = line.split(';', 1)[0].strip()
        if not cmd:
            continue
        command = cmd.split()[0]
        if command not in ('G0', 'G1', 'G2', 'G3', 'G92'):
            continue
        values = {k: float(v) for k, v in NUMBER.findall(cmd)}
        if command == 'G92':
            actual.update({k: v for k, v in values.items() if k in actual}); continue
        start = actual.copy()
        actual.update({k: values[k] for k in 'XYZ' if k in values})
        extrusion = values.get('E', 0.) if relative_e else values.get('E', actual['E']) - actual['E']
        if 'E' in values:
            actual['E'] = actual['E'] + values['E'] if relative_e else values['E']
        if owner != identify_id or extrusion <= 0 or not ('X' in values or 'Y' in values) or feature.startswith('Support'):
            continue
        features[feature] += 1
        if feature in ('Inner wall', 'Outer wall', 'Overhang wall'):
            row = [start['X'], start['Y'], actual['X'], actual['Y'], width]
            if abs(z - 0.2) < 0.002:
                first.append(row)
            elif abs(z - 0.44) < 0.002:
                second.append(row)
        # Inverted cap: its physical slab center is ABOVE the machine-frame
        # coordinate of the print-Z top. The same native material query applies.
        pts = (np.array([[start['X'], start['Y'], z], [actual['X'], actual['Y'], z]]) - translation) @ rotation.T
        center_z = float(((np.array([0., 0., z-height/2]) - translation) @ rotation.T)[2])
        for region in source['solid_host_regions']:
            x0, x1, y0, y1, z0, z1 = region['applied_machine_bounds_mm']
            if not z0 < center_z < z1:
                continue
            segment = LineString(pts[:, :2]).intersection(box(x0+0.25, y0+0.25, x1-0.25, y1-0.25))
            if segment.length > 0.005:
                assert command not in ('G2', 'G3'), (region['name'], cmd)
                layers.setdefault((region['name'], round(center_z, 6)), []).append(
                    dict(xy=list(segment.coords), width=width, feature=feature))
    first_footprint = union_all([LineString(((a, b), (c, d))).buffer(w/2) for a, b, c, d, w in first])
    unsupported = sum(not LineString(((a, b), (c, d))).buffer(w/2).intersects(first_footprint)
                      for a, b, c, d, w in second)
    density = dense_road_check('pump-cap', layers)
    return dict(part='pump-cap', native_checks_pass=bool(first) and bool(second) and not unsupported and
                density['pass_check'] and len(density['regions']) == len(source['solid_host_regions']),
                first_layer_wall_roads=len(first), second_layer_wall_roads=len(second),
                second_layer_roads_without_overlap=unsupported, model_feature_road_counts=dict(features),
                solid_host_deposition=density)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, default=4)
    args = parser.parse_args()
    destination = HERE / f'v{args.revision}'
    job, = json.loads((destination / 'preparation.json').read_text())['jobs']
    project, archive = ROOT / job['project'], ROOT / job['native_archive']
    assert sha(project) == job['project_sha256'] and sha(archive) == job['native_archive_sha256']
    payload = members(archive)
    data = payload['Metadata/plate_1.gcode']
    assert hashlib.sha256(data).hexdigest() == job['gcode_sha256']
    assert hashlib.md5(data).hexdigest() == payload['Metadata/plate_1.gcode.md5'].decode().strip().lower()
    bindings, native_parts = native_components(payload, job)
    cartridge = next(s for s in job['components'] if s['part'] == 'pump-cartridge')
    geom = json.loads((HERE / 'geometry-check.json').read_text())['pieces']['pump-cartridge']
    cartridge_check = read_job({**job, **cartridge}, geom)
    cap = next(s for s in job['components'] if s['part'] == 'pump-cap')
    cap_id = next(p['identify_id'] for p in native_parts if p['name'] == 'enclosure-pump-cap')
    cap_check = cap_roads(data, cap, cap_id)
    source = members(project)
    # A normal two-object native support audit retains short unlabelled trees.
    _, input_parts = native_components(source, job)
    output = archive.parent
    (output / 'plate_1.gcode').write_bytes(data)
    settings = json.loads(source[SETTING])
    support = slice_review(project, dict(project_sha256=job['project_sha256'],
        settings_sha256=hashlib.sha256(source[SETTING]).hexdigest(), parts=input_parts,
        saved_profile_filament_density_g_cm3=settings['filament_density'],
        shared_printable_area_mm=[[0., 0.], [325., 320.]]), output)
    (destination / 'support-topology.json').write_text(json.dumps(support, indent=2) + '\n')
    metadata = ET.fromstring(payload['Metadata/slice_info.config']).find('plate')
    values = {m.get('key'): m.get('value') for m in metadata.findall('metadata')}
    pauses = metadata.findall('pause_list/pause')
    assert len(pauses) == 1
    result = json.loads((output / 'result.json').read_text())
    plate, = result['sliced_plates']
    total = plate['total_predication']
    remaining = int(pauses[0].get('remaining_time'))
    pause_index = next(i for i, line in enumerate(data.splitlines()) if re.fullmatch(rb'M400 U1(?:\s*;.*)?', line))
    commands = [line.decode() for line in data.splitlines()[:pause_index] if line.startswith(b'M73 C')]
    baseline = members(ROOT / job['baseline_project'])
    checks = dict(two_current_source_bindings=all(r['pass_check'] for r in bindings),
        cartridge_pause_and_paths=cartridge_check['native_checks_pass'],
        cap_first_layers_and_dense_pogo_hosts=cap_check['native_checks_pass'],
        original_mark2_settings_and_pause_unchanged=source[SETTING] == baseline[SETTING] and
        source['Metadata/custom_gcode_per_layer.xml'] == baseline['Metadata/custom_gcode_per_layer.xml'],
        native_success_without_warning=result['return_code'] == 0 and not plate['warning_message'],
        both_objects_emitted=len(plate['objects']) == 2 and values['outside'] == 'false',
        one_pause=len(pauses) == 1)
    report = dict(submitted=False, native_checks_pass=all(checks.values()), checks=checks,
        source_bindings=bindings, parts=[cartridge_check, cap_check],
        plate_fit=support['fit'], native_archive=job['native_archive'],
        native_archive_sha256=job['native_archive_sha256'], gcode_sha256=job['gcode_sha256'],
        project_sha256=job['project_sha256'], audit_script_sha256=sha(Path(__file__)),
        pocket_audit_script_sha256=sha(HERE / 'audit_prints.py'),
        timing=dict(total_estimated_seconds=total, pause_layer=int(pauses[0].get('layer')),
            pause_percent=int(pauses[0].get('percent')), remaining_at_pause_minutes=remaining,
            estimated_start_to_pause_seconds=total-remaining*60,
            initial_pause_countdown=commands[0], last_pause_countdown=commands[-1],
            estimate_resolution='Remaining time and countdown are rounded to minutes; elapsed estimate includes native startup overhead and excludes the operator pause duration.'),
        physical_fit_retention_thermal_and_strength_accepted=False)
    (destination / 'native-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('native_checks_pass', 'checks', 'timing', 'plate_fit')}, indent=2))
    if not report['native_checks_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
