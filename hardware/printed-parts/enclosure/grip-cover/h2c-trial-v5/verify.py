"""Read-only verification of the frozen grip test package before its UI send."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
PART = ROOT / 'hardware/printed-parts/enclosure/grip-cover'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    job = ROOT / '.cache/prints/grip-receivers-h2c-v5'
    preparation = json.loads((job / 'preparation.json').read_text())
    geometry = json.loads((PART / 'geometry-check.json').read_text())
    archive = job / 'ready/grip-receivers-h2c-v5.gcode.3mf'
    assert archive.parent == job / 'ready'
    assert geometry['status'] == 'pass' and all(geometry['checks'].values())
    for path, digest in preparation['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
    for name, digest in geometry['artifacts_sha256'].items():
        assert sha(PART / name) == digest, name
    assert sha(job / preparation['project']) == preparation['project_sha256']
    with zipfile.ZipFile(ROOT / preparation['settings_source']) as z:
        baseline = json.loads(z.read('Metadata/project_settings.config'))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        settings = json.loads(z.read('Metadata/project_settings.config'))
        gcode = z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gcode).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    with zipfile.ZipFile(job / preparation['project']) as z:
        ranges = ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))
    scoped_walls = []
    for obj in ranges:
        for band in obj:
            options = {o.attrib['opt_key']: o.text for o in band}
            if 'wall_loops' in options:
                scoped_walls.append({'object': obj.attrib['id'], **band.attrib, **options})
    assert len(scoped_walls) == 2 and all(b['wall_loops'] == '6' and b['min_z'] == '35.0' and b['max_z'] == '41.5' for b in scoped_walls)
    (job / 'ready/plate_1.gcode').write_bytes(gcode)
    sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet'))
    import refresh_print_project as writer
    support = writer.slice_review(job / preparation['project'], preparation, job / 'ready')
    (HERE / 'support-audit.json').write_text(json.dumps(support, indent=2) + '\n')
    contact_envelope = max(tree['bbox_cad_xyz_mm'][5] for part in support['parts']
                           for tree in part['trees']) + float(settings['support_top_z_distance'])
    assert contact_envelope < 29.25, contact_envelope
    with zipfile.ZipFile(archive) as z:
        (HERE / 'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    expected = {
        'initial_layer_print_height': '0.2', 'layer_height': '0.24',
        'enable_support': '1', 'support_type': 'tree(auto)',
        'support_object_xy_distance': '0.4', 'support_top_z_distance': '0.45',
        'support_bottom_z_distance': '0.3', 'support_filament': '1',
        'support_interface_filament': '1', 'flush_into_support': '0',
        'wall_sequence': 'inner wall/outer wall', 'is_infill_first': '0',
        'infill_wall_overlap': '15%', 'elefant_foot_compensation': '0',
        'brim_type': 'no_brim', 'brim_width': '0',
        'filament_colour': ['#000000'], 'filament_nozzle_map': ['0'],
        'nozzle_diameter': ['0.4', '0.4'], 'curr_bed_type': 'Textured PEI Plate',
    }
    for key, value in expected.items():
        assert settings[key] == value, (key, settings[key], value)
    speed_keys = [k for k in baseline if 'speed' in k]
    assert all(settings[k] == baseline[k] for k in speed_keys)
    trims = [float(s) for s in re.findall(rb'^\s*G29\.1 Z([-+\d.]+)', gcode, re.M)]
    assert trims == [0., .16], trims
    assert len(preparation['parts']) == 2
    assert all(p['rotation_x_degrees'] == 0 and p['watertight'] and p['body_count'] == 1 for p in preparation['parts'])
    assert {p['name'] for p in preparation['parts']} == {'grip-receiver-front', 'grip-receiver-back'}
    sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/nameplate'))
    from verify_mark2_print import segments
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union
    roads = list(segments(job / 'ready/plate_1.gcode'))
    first_layers = {}
    for part in preparation['parts']:
        part_roads = [r for r in roads if r['object'] == part['identify_id'] and not r['feature'].startswith('Support')]
        z1, z2 = sorted({r['layer'] for r in part_roads})[:2]
        assert abs(z1 - .20) < .001 and abs(z2 - .44) < .001
        first = unary_union([LineString((r['a'], r['b'])).buffer(r['width']/2) for r in part_roads if r['layer'] == z1])
        second_roads = [r for r in part_roads if r['layer'] == z2]
        second = [LineString((r['a'], r['b'])).buffer(r['width']/2) for r in second_roads]
        overlap = min(road.intersection(first).area / road.area for road in second)
        wall_overlap = min(bead.intersection(first).area / bead.area for road, bead in zip(second_roads, second) if 'wall' in road['feature'].lower())
        assert wall_overlap > .5, (part['name'], wall_overlap)
        assert first.geom_type == 'Polygon'
        footprint = Polygon(first.exterior)
        upper = unary_union(second)
        assert footprint.buffer(.12).covers(upper)
        low, high = 0., .12
        for _ in range(16):
            mid = (low + high)/2
            if footprint.buffer(mid).covers(upper): high = mid
            else: low = mid
        first_layers[part['name']] = {'first_z_mm': z1, 'second_z_mm': z2, 'minimum_second_layer_bead_overlap_fraction': overlap,
            'minimum_second_layer_wall_bead_overlap_fraction': wall_overlap,
            'maximum_second_layer_outward_advance_mm': high,
            'criterion': 'Walls have at least half bead-area support and no second-layer path advances more than 0.12 mm outside the first-layer perimeter. Short internal infill crossings may bridge gaps between first-layer roads.'}
    result = json.loads((job / 'ready/result.json').read_text())
    plate, = result['sliced_plates']
    assert result['return_code'] == 0 and not plate['warning_message']
    evidence = {
        'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'status': 'pass',
        'archive': str(archive.relative_to(ROOT)), 'archive_sha256': sha(archive),
        'gcode_sha256': hashlib.sha256(gcode).hexdigest(), 'project_sha256': preparation['project_sha256'],
        'source_sha256': preparation['source_sha256'],
        'geometry_check_sha256': sha(PART / 'geometry-check.json'),
        'support_audit_sha256': sha(HERE / 'support-audit.json'),
        'highest_support_contact_envelope_cad_z_mm': contact_envelope,
        'exterior_transition_starts_cad_z_mm': 29.25,
        'settings_verified': expected, 'shared_profile_speeds_preserved': True,
        'scoped_six_wall_bands': scoped_walls, 'first_layers': first_layers,
        'requested_h2c_trim_mm': .18, 'emitted_g29_1_z_mm': trims,
        'parts': [p['name'] for p in preparation['parts']],
        'estimate_seconds': plate['total_predication'], 'filaments': plate['filaments'],
        'launch_options': {'timelapse': 'On', 'bed_leveling': 'On', 'flow_calibration': 'Auto', 'nozzle_offset_calibration': 'Auto'},
        'submitted': False,
    }
    (HERE / 'preflight.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))

if __name__ == '__main__':
    main()
