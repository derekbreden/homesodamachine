"""Manual review of a complete Sculpted native slice; never starts a printer."""
from pathlib import Path
from zipfile import ZipFile
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
# Read stored meshes and G-code; importing the project writer does not build CAD.
os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tools/gcode'),
               str(HERE.parent), str(HERE.parent / 'industrial')]
import refresh_print_project as writer
import toolpaths as tp
import seams
from review_rim_supports import material_review, segments
from bambu_print_archive import package


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def front_rim_contacts(early, report):
    """Read lower-bead bearing at the two last-starting front-rim courses."""
    import shapely
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    base = report['parts'][0]
    label = base['identify_id']
    transform = np.array(base['build_transform'])
    translation = transform[9:] + report['native_right_tool_offset_mm']
    center = np.array(base['source_center_mm'])
    paths = [p for p in segments(early) if p['object'] == label]
    traces, active = [], None
    for p in paths:
        cad = ((p['a'] + p['b']) / 2 - translation) @ transform[:9].reshape(3, 3).T + center
        keep = (round(p['z'], 2) in (15.32, 15.56) and cad[1] < -24
                and .02 <= cad[2] <= .70 and p['feature'] in ('Outer wall', 'Overhang wall', 'Bridge'))
        if not keep:
            active = None
            continue
        if active is None or active['z'] != p['z'] or np.linalg.norm(active['points'][-1] - p['a'][:2]) > .005:
            active = {'z': p['z'], 'line': p['line'], 'points': [p['a'][:2]], 'width': p['width']}
            traces.append(active)
        active['points'].append(p['b'][:2])
    bearing_cache = {}
    result = []
    for trace in traces:
        line = LineString(trace['points'])
        if line.length < .1:
            continue
        z = trace['z']
        if z not in bearing_cache:
            bearing_cache[z] = unary_union([LineString([p['a'][:2], p['b'][:2]]).buffer(p['width']/2, quad_segs=4)
                for p in paths if .001 < z - p['z'] <= .80001])
        count = max(2, int(np.ceil(line.length / .1)) + 1)
        samples = shapely.line_interpolate_point(line, np.linspace(0, line.length, count))
        missing = ~shapely.intersects(bearing_cache[z].buffer(trace['width']/2), samples)
        longest = run = 0
        for v in missing:
            run = run + 1 if v else 0
            longest = max(longest, run)
        result.append({'print_z_mm': z, 'gcode_line': trace['line'], 'length_mm': line.length,
            'longest_run_without_lower_bead_xy_overlap_mm': max(0, (longest-1)*line.length/(count-1))})
    return {'scope': 'Front rim near CAD Y<-24 at the first two last-starting courses. Bearing includes model and support beads within the preceding 0.80 mm in Z; it is an XY envelope reading, not an adhesion measurement.',
            'traces': result}


def review(project, native_directory):
    folder = project.parent
    report_path = project.with_suffix('.print.json')
    report = json.loads(report_path.read_text())
    result = json.loads((native_directory / 'result.json').read_text())
    plate, = result['sliced_plates']
    assert result['return_code'] == 0 and not plate['warning_message']
    assert len(plate['objects']) == 5
    native = project.with_suffix('.gcode.3mf')
    shutil.copyfile(native_directory / 'native.gcode.3mf', native)
    with ZipFile(project) as prepared, ZipFile(native) as sliced:
        settings = json.loads(prepared.read(writer.SETTINGS_MEMBER))
        effective = json.loads(sliced.read(writer.SETTINGS_MEMBER))
        normalization = {k: {'prepared': settings.get(k), 'native': effective.get(k)}
            for k in settings.keys() | effective.keys() if settings.get(k) != effective.get(k)}
        data = sliced.read('Metadata/plate_1.gcode')
        assert hashlib.md5(data).hexdigest() == sliced.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert data == (native_directory / 'plate_1.gcode').read_bytes()
        assert 'Metadata/layer_config_ranges.xml' not in prepared.namelist()
        assert settings['filament_map'] == effective['filament_map'] == ['2']
        assert settings['filament_map_mode'] == effective['filament_map_mode'] == 'Manual'
        assert effective['filament_printable'] == ['3']
        assert settings['filament_nozzle_map'] == effective['filament_nozzle_map'] == ['1']
        assert effective['filament_colour'] == ['#FFFFFF']
        assert effective['nozzle_diameter'] == ['0.4', '0.4']
        assert effective['extruder_offset'] == ['0x0', '0.5x-0.7']
        assert settings['layer_height'] == effective['layer_height'] == '0.24'
        assert settings['initial_layer_print_height'] == effective['initial_layer_print_height'] == '0.2'
        for k in ('fan_min_speed', 'fan_max_speed', 'overhang_fan_speed', 'bridge_flow',
                  'bridge_speed', 'filament_bridge_speed', 'filament_wipe', 'filament_wipe_distance',
                  'nozzle_temperature', 'nozzle_temperature_initial_layer', 'support_type', 'support_style'):
            assert effective[k] == settings[k], k
        config = ET.fromstring(prepared.read('Metadata/model_settings.config'))
        modifier_overrides = []
        for part in config.findall('.//part'):
            if part.get('subtype') == 'modifier_part':
                modifier_overrides.extend(m.get('key') for m in part.findall('metadata')
                    if m.get('key', '').startswith(('wall_', 'inner_wall_', 'outer_wall_')))
        assert not modifier_overrides
        for row in report['parts']:
            assert sha(ROOT / row['source']) == row['stl_sha256']
        if 'Metadata/plate_1.png' in sliced.namelist():
            (folder / 'preview.png').write_bytes(sliced.read('Metadata/plate_1.png'))
    text = data.decode()
    assert re.search(r'^; filament_map = 2$', text, re.M)
    assert re.search(r'^; filament_nozzle_map = 1$', text, re.M)
    assert [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', text, re.M)] == [0., .02]
    layer_z = [float(v) for v in re.findall(r'^; Z_HEIGHT: ([-+.\d]+)', text, re.M)]
    # LAYER_HEIGHT also describes bridge/overhang bead cross-sections, which
    # can be taller than the nominal course. Measure courses from their Zs.
    nominal_heights = sorted({round(b-a, 5) for a, b in zip([0.] + layer_z, layer_z)})
    assert nominal_heights == [.20, .24]
    assert not re.search(r'^; (?:WIPE_START|WIPE_END)', text, re.M)
    material, early = material_review(native_directory / 'plate_1.gcode', report, early_max_z=16)
    save(folder / 'material-commands.json', {'parts': material})
    contacts = front_rim_contacts(early, report)
    save(folder / 'front-rim-contacts.json', contacts)
    print('Native process, material mapping and layer heights verified.', flush=True)
    # Full emitted bead envelope, including automatic and custom supports.
    sys.path.insert(0, str(ROOT / 'hardware/scripts'))
    envelopes = []
    for row in report['parts']:
        output = native_directory / ('bounds-' + row['name'] + '.gcode')
        bounds = writer.object_toolpaths(native_directory / 'plate_1.gcode', output, row['identify_id'])
        envelopes.append({'part': row['name'], **bounds})
    low = np.min([p['extrusion_bounds_xy_mm'][0] for p in envelopes], axis=0)
    high = np.max([p['extrusion_bounds_xy_mm'][1] for p in envelopes], axis=0)
    usable_low, usable_high = np.array(report['shared_printable_area_mm'])
    margin = float(min(*(low - usable_low), *(usable_high - high)))
    assert margin >= 20
    # Every exterior loop across every height, in nominal CAD coordinates after
    # undoing the right nozzle's registered native tool-coordinate correction.
    runs = tp.read_runs(text)
    seam_summary = {}
    import runpy
    geometry = runpy.run_path(str(HERE.parent / 'faucet_paths.py'))
    center = np.array([geometry['WATER_Y'] - geometry['WATER_RADIUS'], geometry['ARC_START_Z']])
    radius = geometry['WATER_RADIUS'] + geometry['SHELL_CENTER_N'] + geometry['SHELL_RADIUS']
    for name in ('faucet-shell-base', 'faucet-shell-tip', 'above-counter-plate', 'faucet-display-cover', 'lever-replica'):
        placement = tp.Placement(report_path, name)
        placement.t += np.array(report['native_right_tool_offset_mm'])
        selected = [r for r in runs if r['object'] == placement.identify_id]
        toward = (0, 0, 1) if name == 'faucet-shell-tip' else (0, 1, 0)
        rows = seams.measure(native, placement, toward=toward, runs=selected)
        if name == 'faucet-shell-tip':
            main = [r for r in rows if abs(np.linalg.norm(r['target_cad'][1:] - center) - radius) <= .4
                    and np.degrees(geometry['JOINT_ANGLE']) <= np.degrees(np.arctan2(*(r['target_cad'][1:] - center)[::-1]))
                    <= np.degrees(geometry['TOTAL_ANGLE'])]
        elif name == 'above-counter-plate':
            main = [r for r in rows if r['perimeter_mm'] > 150]
        elif name == 'faucet-shell-base':
            main = [r for r in rows if r['target_cad'][2] >= -.02 and r['closed']]
        else:
            main = rows
        summary = {'all_exterior_loop_layers': len(rows), 'goal_layers': len(main),
            'maximum_lateral_mm': float(max((abs(r['lateral_mm']) for r in main), default=0)),
            'profile': seams.profile(rows), 'zones_past_0_6_mm': seams.zones(main, .6)}
        seam_summary[name] = summary
        with (folder / (name + '-seams.csv')).open('w', newline='') as stream:
            out = csv.writer(stream, lineterminator="\n")
            out.writerow(['layer', 'print_z', 'layer_h', 'gcode_line', 'closed', 'lateral_mm',
                          'start_cad_x', 'start_cad_y', 'start_cad_z', 'target_cad_y', 'target_cad_z'])
            for r in rows:
                out.writerow([r['layer'], r['print_z'], r['layer_h'], r['gcode_line'], int(r['closed']),
                              r['lateral_mm'], *r['start_cad'], *r['target_cad'][1:]])
        print(name, json.dumps({k: summary[k] for k in ('all_exterior_loop_layers', 'goal_layers', 'maximum_lateral_mm')}), flush=True)
    print_only = native.with_name(native.name.replace('.gcode.3mf', '-print-only.gcode.3mf'))
    packaging = package(native, print_only)
    for key in ('source_archive', 'print_only_archive'):
        packaging[key] = str(Path(packaging[key]).relative_to(ROOT))
    save(folder / 'packaging.json', packaging)
    output = {'status': 'Complete Sculpted native slice reviewed; physical result pending',
        'project': str(project.relative_to(ROOT)), 'project_sha256': sha(project),
        'archive': str(native.relative_to(ROOT)), 'archive_sha256': sha(native),
        'submitted_archive': str(print_only.relative_to(ROOT)), 'submitted_archive_sha256': sha(print_only),
        'gcode_sha256': hashlib.sha256(data).hexdigest(),
        'printer': 'Mark2', 'active_nozzle': 1, 'external_spool': 255, 'filament_colour': '#FFFFFF',
        'right_tool_offset_mm': report['native_right_tool_offset_mm'],
        'first_bed_layer_mm': .2, 'subsequent_layer_mm': .24, 'industrial_fine_bands': [],
        'native_layer_heights_mm': nominal_heights, 'modifier_wall_setting_overrides': modifier_overrides,
        'nominal_layer_count': len(layer_z),
        'native_settings_normalizations': normalization, 'part_envelopes': envelopes,
        'all_bead_envelope_xy_mm': [low.tolist(), high.tolist()],
        'right_nozzle_usable_area_mm': report['shared_printable_area_mm'],
        'minimum_bead_edge_margin_mm': margin, 'seams': seam_summary,
        'estimated_seconds': plate['total_predication'],
        'estimated_grams_saved_profile_density': sum(f['total_used_g'] for f in plate['filaments']),
        'gcode_bytes_unchanged_by_packaging': True}
    save(folder / 'native-review.json', output)
    print(json.dumps({k: output[k] for k in ('minimum_bead_edge_margin_mm', 'estimated_seconds')}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('native_directory', type=Path)
    args = parser.parse_args()
    review(args.project.resolve(), args.native_directory.resolve())
