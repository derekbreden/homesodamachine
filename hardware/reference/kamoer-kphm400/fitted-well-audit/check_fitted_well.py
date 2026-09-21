#!/usr/bin/env python3
"""Compare the production Kamoer well with retained print and raw scan evidence.

Builds only a bounded native fixture in memory. The earlier 3MF supplies its actual
printed surfaces; the current holder datums are deliberately replaced with that
print's datums to isolate local fit from assembly placement. No CAD is exported.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh
from shapely import contains_xy


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/cad-venv').is_dir())
REFERENCE = HERE.parent
ENCLOSURE = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path.insert(0, str(REFERENCE))
sys.path.insert(0, str(ENCLOSURE))
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import enclosure as enclosure  # noqa: E402
import analyze_scan as scan  # noqa: E402
import _box_spec  # noqa: E402


PRINT_INPUT = ROOT / '.cache/prints/2026-09-13-enclosure/enclosure-pump-cartridge-mark2-input.3mf'
PROVENANCE = PRINT_INPUT.with_name('enclosure-pump-cartridge-mark2.provenance.json')
PRINT_SHA256 = '9f84eb4edb3faba30243680036600c45f6a700ee7e884a7f0237940f153df372'
HOLDER_DATUMS = ((49.945, 46.009, 213.745), (-49.945, 46.009, 213.745))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def input_name(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def snapshot(paths):
    return {input_name(p): digest(p) for p in sorted(set(paths))}


def print_mesh(index, provenance):
    """Recover authored coordinates from the centered mesh, not print-bed transforms."""
    with zipfile.ZipFile(PRINT_INPUT) as archive:
        root = ET.fromstring(archive.read(f'3D/Objects/object_{index + 1}.model'))
    vertices = np.array([[float(node.attrib[k]) for k in ('x', 'y', 'z')]
                         for node in root.iter() if node.tag.endswith('}vertex')])
    triangles = np.array([[int(node.attrib[k]) for k in ('v1', 'v2', 'v3')]
                          for node in root.iter() if node.tag.endswith('}triangle')])
    declared_bounds = np.array(provenance['parts'][index]['model_bounds_mm'])
    vertices += declared_bounds.mean(axis=0)
    mesh = trimesh.Trimesh(vertices, triangles, process=False)
    if np.max(abs(mesh.bounds - declared_bounds)) > 1e-5:
        raise ValueError('Recovered 3MF bounds disagree with retained provenance')
    if len(triangles) != provenance['parts'][index]['triangles']:
        raise ValueError('3MF triangle count disagrees with retained provenance')
    return mesh


def symmetric_difference(a, b):
    return float(a.cut(b).Volume() + b.cut(a).Volume())


def fixture():
    """Earlier print stations with enough aft room for its full support band."""
    return SimpleNamespace(
        pack=SimpleNamespace(pump_trays=HOLDER_DATUMS, collet_plate={'fore_y': 79.669}),
        inner=(-104.5, 104.5, 14.0, 464.0, 0.0, 352.0),
        pump_bay=(-104.5, 104.5, 282.745),
    )


def surface_comparison(cradle, native_well):
    local = cradle.triangles_center - np.array(HOLDER_DATUMS[0])
    inward = np.sum(cradle.face_normals[:, :2] * local[:, :2], axis=1) < -5
    selected = ((abs(local[:, 0]) < 36) & (local[:, 1] > -34) & (local[:, 1] < 33)
                & (local[:, 2] < -.01) & (local[:, 2] > -48.2) & inward)
    indices = np.flatnonzero(selected)
    if len(indices) != 208:
        raise ValueError('The retained print does not expose the expected 208 well triangles')
    vertices, faces = native_well.tessellate(.004, .1)
    mesh = trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=False)
    _, distance, _ = trimesh.proximity.closest_point(mesh, cradle.triangles_center[indices])
    categories = {}
    for name, mask in [
        ('all', np.ones(len(indices), dtype=bool)),
        ('vertical', abs(cradle.face_normals[indices, 2]) < .001),
        ('lower_ramp', (local[indices, 2] < -32) & (abs(cradle.face_normals[indices, 2]) > .5)),
    ]:
        values = distance[mask]
        categories[name] = {
            'triangles': len(values),
            'triangle_area_mm2': float(cradle.area_faces[indices[mask]].sum()),
            'median_mm': float(np.median(values)),
            'p95_mm': float(np.quantile(values, .95)),
            'max_mm': float(values.max()),
        }
    return {
        'method': 'Actual inward-facing print triangle centroids to current native well surface tessellated at 0.004 mm / 0.1 rad.',
        'scope': 'Positive pump lower-well faces. This is a sampled local surface comparison, not a full assembly Hausdorff bound.',
        'triangle_indices': indices.tolist(),
        'native_valid': native_well.isValid(),
        'native_solids': len(native_well.Solids()),
        'surface_distances': categories,
        'pass': bool(native_well.isValid() and len(native_well.Solids()) == 1
                     and categories['all']['max_mm'] < .0041
                     and categories['vertical']['max_mm'] < 1e-5),
    }


def retained_box_station(path):
    box, _bounds = _box_spec.read(
        enclosure.Box, enclosure.Bound,
        (enclosure.Pack, enclosure.PortField, enclosure.Nameplate), path=str(path))
    trays, plate = box.pack.pump_trays, box.pack.collet_plate
    band_y = enclosure.pump_skirt_band_aft_y(trays)
    minimum_air = enclosure.cap_kiss - enclosure.cap_kiss_station_allowance
    gap = plate['fore_y'] - band_y
    try:
        aft_y = enclosure.pump_cartridge_aft_y(trays, plate)
        guard = {'pass': True, 'cartridge_aft_y_mm': aft_y}
    except ValueError as exc:
        guard = {'pass': False, 'error': str(exc)}
    return {
        'scope': 'Retained serialized Box input only; this audit does not regenerate or qualify current assembly placement.',
        'pump_trays_mm': trays,
        'plate_fore_y_mm': plate['fore_y'],
        'full_skirt_band_aft_y_mm': band_y,
        'available_air_mm': gap,
        'required_air_mm': minimum_air,
        'minimum_fore_movement_mm': max(0.0, minimum_air - gap),
        'station_guard': guard,
    }


def run(box_path):
    started = time.monotonic()
    files = [Path(__file__), PRINT_INPUT, PROVENANCE, box_path]
    files += [REFERENCE / name for name in (
        'physical-fit.json', 'scan-evidence.json', 'scan-registration.json',
        'scan-measurements.json', 'analyze_scan.py', 'register_scan.py')]
    # No dependency graph is written. Record the project Python modules actually imported.
    files += [Path(module.__file__).resolve() for module in tuple(sys.modules.values())
              if getattr(module, '__file__', None)
              and Path(module.__file__).resolve().is_relative_to(ROOT / 'hardware')
              and Path(module.__file__).suffix == '.py']
    inputs = snapshot(files)
    provenance = json.loads(PROVENANCE.read_text())
    if digest(PRINT_INPUT) != PRINT_SHA256 or provenance['input_sha256'] != PRINT_SHA256:
        raise ValueError('The retained September 13 print input changed')
    cradle, cap = print_mesh(0, provenance), print_mesh(1, provenance)
    box = fixture()
    old_floor = float(cradle.bounds[0, 2])
    land = enclosure.pump_skirt_support_z(HOLDER_DATUMS)
    floor = enclosure.bay_floor_z(HOLDER_DATUMS)
    print('Checking local fitted well against retained print...', flush=True)
    native_well = enclosure._pump_drop_voids(box)[0]
    comparison = surface_comparison(cradle, native_well)
    print('Checking floor-only native invariance...', flush=True)
    native_cap = enclosure.build_pump_cap(box).val()
    relief = enclosure.pump_bay_floor_relief
    try:
        enclosure.pump_bay_floor_relief = 1.0
        alternate_well = enclosure._pump_drop_voids(box)[0]
        alternate_cap = enclosure.build_pump_cap(box).val()
    finally:
        enclosure.pump_bay_floor_relief = relief
    well_delta = symmetric_difference(native_well, alternate_well)
    cap_delta = symmetric_difference(native_cap, alternate_cap)
    floor_invariance = {
        'relief_values_mm': [relief, 1.0],
        'scope': 'Only pump_bay_floor_relief changes; all holder and cap datums are held fixed.',
        'lower_well_symmetric_difference_mm3': well_delta,
        'cap_symmetric_difference_mm3': cap_delta,
        'pass': well_delta < 1e-7 and cap_delta < 1e-7,
    }
    up_faces = cradle.face_normals[:, 2] > .99999
    horizontal_areas = {}
    for z, area in zip(cradle.triangles_center[up_faces, 2], cradle.area_faces[up_faces]):
        key = str(round(float(z), 4))
        horizontal_areas[key] = horizontal_areas.get(key, 0.0) + float(area)
    land_footprint = scan.face_footprint(cradle, land, 1)
    bottom_material = scan.face_footprint(cradle, old_floor, -1)
    print('Checking independent raw front-rim observations...', flush=True)
    evidence = json.loads((REFERENCE / 'scan-evidence.json').read_text())
    registration = json.loads((REFERENCE / 'scan-registration.json').read_text())
    observations, normals, pass_ids = scan.scan_observations(
        evidence, registration, Path(evidence['capture_archive']))
    measured = json.loads((REFERENCE / 'scan-measurements.json').read_text())
    bearing_frame = measured['skirt_bearing_plane']
    rotation = np.array(bearing_frame['common_to_bearing_rotation'])
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-7):
        raise ValueError('Bearing frame is not rigid')
    bearing = (observations - np.array(bearing_frame['origin_common'])) @ rotation.T
    bearing_normals = normals @ rotation.T
    world_origin = np.array([HOLDER_DATUMS[0][0],
                             HOLDER_DATUMS[0][1] + enclosure.clamp_pump_y_shift, land])
    world = bearing + world_origin
    front = ((abs(observations[:, 0]) < 32) & (observations[:, 1] > -31)
             & (observations[:, 1] < 33) & (observations[:, 2] > -50)
             & (observations[:, 2] < -45) & (abs(bearing_normals[:, 2]) > .9))
    over_material = contains_xy(bottom_material, world[:, 0], world[:, 1])
    rows = []
    for current_pass in (1, 2):
        selected = front & (pass_ids == current_pass)
        points = world[selected]
        over = over_material[selected]
        if len(points) < 1000:
            raise ValueError('Too few observed front-rim points')
        rows.append({
            'pass': current_pass,
            'front_observations': len(points),
            'projected_over_printed_cradle_bottom_material': int(over.sum()),
            'below_printed_bottom': int((points[:, 2] < old_floor).sum()),
            'below_current_fixed_floor': int((points[:, 2] < floor[1]).sum()),
            'rim_to_printed_bottom_mm': scan.stats(points[:, 2] - old_floor),
            'rim_to_current_fixed_floor_mm': scan.stats(points[:, 2] - floor[1]),
            'over_material_gaps_mm': scan.stats(points[over, 2] - old_floor) if over.any() else None,
        })
    station = retained_box_station(box_path)
    after = snapshot(files)
    if inputs != after:
        changed = [name for name, value in inputs.items() if after[name] != value]
        raise RuntimeError(f'Inputs changed while audit ran: {changed}')
    result = {
        'schema': 1,
        'status': 'local_fitted_profile_verified' if comparison['pass'] and floor_invariance['pass'] else 'failed',
        'production_assembly_current': False,
        'inputs_sha256': inputs,
        'raw_clouds': [{'path': registration[role]['path'],
                       'sha256': registration[role]['sha256']}
                      for role in ('fixed', 'moving')],
        'current_source_parameters_mm': {
            'cap_pump_air': enclosure.cap_pump_air,
            'skirt_y_plus_air': enclosure._tray.skirt_y_plus_air,
            'skirt_open_y_max': enclosure._tray.skirt_open_y_max,
            'skirt_upper_band': enclosure._tray.skirt_upper_band,
            'pump_bay_floor_relief': relief,
            'outlet_axis_z_local': enclosure._tray.outlet_axis_z,
        },
        'print_frame': {
            'holder_datums_mm': HOLDER_DATUMS,
            'motor_axis_y_mm': world_origin[1],
            'fixture_collet_fore_y_mm': box.pack.collet_plate['fore_y'],
            'cradle_bounds_mm': cradle.bounds.tolist(),
            'cap_bounds_mm': cap.bounds.tolist(),
            'upward_planar_face_areas_mm2_by_z': horizontal_areas,
            'skirt_land_z_mm': land,
            'actual_skirt_land_projected_area_mm2': land_footprint.area,
            'broad_cap_base_z_mm': enclosure.cap_base_z(HOLDER_DATUMS),
        },
        'fitted_surface_comparison': comparison,
        'floor': {
            'actual_print_bottom_z_mm': old_floor,
            'current_fixed_floor_z_mm': floor,
            'floor_top_difference_mm': floor[1] - old_floor,
            'actual_print_bottom_material_area_mm2': bottom_material.area,
            'parameter_only_native_invariance': floor_invariance,
            'scan_pose': {
                'common_to_bearing_rotation': rotation.tolist(),
                'origin_common_mm': bearing_frame['origin_common'],
                'bearing_origin_world_mm': world_origin.tolist(),
                'scale': 1.0,
            },
            'scan_front_rim': rows,
        },
        'retained_box_station': station,
        'limits': [
            'Derek confirms firm fit and no vertical play in his existing assembled pair, but has not bound it to a print date. September 13 is the retained earlier printable comparison.',
            'The raw-scan front rim is evaluated in an underside-strip seated analysis pose. Actual assembled contact faces and load sharing remain unobserved; no flange-only load path is inferred.',
            'The floor result concerns fixed-sill clearance and the matching cartridge bottom. Reusing the older cartridge on the lower sill changes its whole seated height.',
            'Current cap crown geometry is not matched to the old cap. The cap is used only for floor-parameter invariance; its accepted contact geometry is checked separately.',
            'The current assembly needs a fresh Box and native generation. This bounded fixture does not establish full-machine placement, tube clearance, support removal or physical clamp force.',
        ],
        'runtime_seconds': time.monotonic() - started,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--box', type=Path, default=ROOT / 'hardware/manifold-layout/enclosure-box.json')
    parser.add_argument('--output', type=Path, default=HERE / 'fitted-well-check.json')
    args = parser.parse_args()
    result = run(args.box.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({
        'output': str(args.output), 'status': result['status'],
        'well_surface_max_mm': result['fitted_surface_comparison']['surface_distances']['all']['max_mm'],
        'floor_invariance': result['floor']['parameter_only_native_invariance'],
        'retained_box_guard': result['retained_box_station']['station_guard'],
        'runtime_seconds': result['runtime_seconds'],
    }, indent=2))
    return 0 if result['status'] == 'local_fitted_profile_verified' else 1


if __name__ == '__main__':
    raise SystemExit(main())
