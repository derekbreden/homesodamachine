"""Verify the native slice's roof support exclusions and retained functional contacts."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys
import zipfile

import numpy as np
from shapely import polygons, union_all
from shapely.geometry import LineString

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/printed-parts/petgf.3mf').is_file())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from verify_round_layer_band import wall_layers, check_span
from enclosure_support_audit import _WORD, _arc_points, audit

BASE = ROOT / '.cache/prints/2026-09-24-enclosure-back-top-h2c-v6'
JOB = ROOT / '.cache/prints/2026-09-24-enclosure-back-top-h2c-v7'
MEMBER = '3D/Objects/object_1.model'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def roof_projection(staged):
    with zipfile.ZipFile(staged) as archive:
        payload = archive.read(MEMBER)
    vertices = np.fromiter((float(v) for m in re.finditer(
        rb'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"\s*/>', payload)
        for v in m.groups()), float).reshape(-1, 3) + [162.5, 168, 97.5]
    faces = np.fromiter((int(v) for m in re.finditer(
        rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"\s+paint_supports="8"\s*/>', payload)
        for v in m.groups()), np.int64).reshape(-1, 3)
    assert len(faces) == 7024
    return union_all(polygons(vertices[faces][:, :, :2])).buffer(0)


def support_in_projection(gcode, region):
    # Check support centerlines, including unlabelled Support bodies. Projection
    # is conservative: it also includes bed feet of trees serving higher faces.
    x = y = e = 0.0
    z = feature = None
    absolute_xy = relative_e = True
    counts = Counter()
    lengths = Counter()
    for raw in gcode.splitlines():
        if raw.startswith('; Z_HEIGHT:'):
            z = float(raw.split(':', 1)[1])
            feature = None
            if z > 9.31:
                break
        elif raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        code = raw.split(';', 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {key: float(value) for key, value in _WORD.findall(code)}
        if command in ('G90', 'G91'):
            absolute_xy = command == 'G90'
        elif command in ('M82', 'M83'):
            relative_e = command == 'M83'
        elif command == 'G92':
            x, y, e = words.get('X', x), words.get('Y', y), words.get('E', e)
        if command not in ('G0', 'G1', 'G2', 'G3'):
            continue
        nx = words.get('X', x) if absolute_xy else x + words.get('X', 0)
        ny = words.get('Y', y) if absolute_xy else y + words.get('Y', 0)
        de = words.get('E', 0) if relative_e else words.get('E', e) - e
        if (z is not None and feature in {'Support', 'Support transition', 'Support interface'}
                and de > 1e-9 and (x != nx or y != ny)):
            points = ([(nx, ny)] if command in ('G0', 'G1')
                      else _arc_points((x, y), (nx, ny), words, command == 'G2'))
            line = LineString([(x, y), *points])
            if region.intersects(line):
                counts[z] += 1
                lengths[z] += line.intersection(region).length
        x, y = nx, ny
        if 'E' in words:
            e = e + words['E'] if relative_e else words['E']
    return [{'z_mm': z, 'moves': counts[z], 'centerline_length_mm': round(lengths[z], 6)}
            for z in sorted(counts)]


def main():
    old = next((BASE / 'ready').glob('*.gcode.3mf'))
    new = next((JOB / 'ready').glob('*.gcode.3mf'))
    staged = next(JOB.glob('*-input.3mf'))
    region = roof_projection(staged)
    with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b:
        assert b.testzip() is None
        settings_a = json.loads(a.read('Metadata/project_settings.config'))
        settings_b = json.loads(b.read('Metadata/project_settings.config'))
        assert settings_a == settings_b
        assert b.read(MEMBER).count(b'paint_supports="8"') == 7024
        gc = b.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest() == b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB / 'ready/plate_1.gcode').write_bytes(gc)
        (JOB / 'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
        previous_projection = support_in_projection(a.read('Metadata/plate_1.gcode').decode(), region)
        current_projection = support_in_projection(gc.decode(), region)
    layers = wall_layers(new, 1901)
    assert layers == wall_layers(old, 1901)
    round_check = check_span(layers, 'roof-rounds-and-flute-runouts', 0, 9.25, .08, .001)
    assert round_check['pass']
    old_audit = json.loads((BASE / 'support-audit.json').read_text())
    new_audit = audit(JOB / 'ready/plate_1.gcode', 'enclosure-back-top',
                      BASE / 'oriented-meshes/enclosure-back-top.stl', staged,
                      include_unlabelled_support=True)
    assert len(new_audit['interfaces']) == len(old_audit['interfaces']) == 40
    for before, after in zip(old_audit['interfaces'], new_audit['interfaces']):
        assert before['id'] == after['id']
        assert before['bbox_xy_mm'] == after['bbox_xy_mm']
        assert before['last_z_mm'] == after['last_z_mm']
        assert abs(before['first_z_mm'] - after['first_z_mm']) <= .01
    # The independent east-roof sliver is absent. The other unlabelled body is
    # the retained interior support, starting above the complete roof band.
    unlabelled = [t for t in new_audit['trees'] if t['interface_reading'] == 'unlabelled']
    assert len(unlabelled) == 1 and unlabelled[0]['base_z_mm'] > 9.31
    result = json.loads((JOB / 'ready/result.json').read_text())
    assert result['return_code'] == 0 and len(result['sliced_plates']) == 1
    assert not result['sliced_plates'][0]['warning_message']
    proof = {
        'reference_native_archive_sha256': sha(old), 'native_archive_sha256': sha(new),
        'staged_input_sha256': sha(staged), 'gcode_sha256': hashlib.sha256(gc).hexdigest(),
        'native_settings_identical': True, 'emitted_model_wall_layers_identical': True,
        'native_blocked_roof_triangles': 7024, 'complete_fine_roof_band': round_check,
        'retained_functional_interface_islands': 40,
        'functional_interface_xy_bounds_and_last_z_identical': True,
        'maximum_interface_start_z_difference_mm': max(abs(x['first_z_mm'] - y['first_z_mm'])
            for x, y in zip(old_audit['interfaces'], new_audit['interfaces'])),
        'previous_support_summary': old_audit['summary'], 'support_summary': new_audit['summary'],
        'east_roof_sliver_absent': True,
        'roof_projection_support_centerlines_before': previous_projection,
        'roof_projection_support_centerlines_after': current_projection,
        'roof_projection_note': 'Projection alone also includes feet of trees serving higher functional faces; it is not a contact count.',
        'slicer': 'BambuStudio 02.08.02.61', 'slicer_return_code': 0,
        'slicer_warning_message': '', 'printer_submission': False,
        'scope': 'Visible roof support exclusions, complete fine layers and retained functional contacts; not a print release or full support-removal review.',
        'pass': True,
    }
    (JOB / 'support-audit.json').write_text(json.dumps(new_audit, indent=2, sort_keys=True) + '\n')
    (JOB / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
