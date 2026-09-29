"""Check the native face-up nameplate paths, supports, colours and print planes."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from shapely.geometry import LineString, box
from shapely.ops import unary_union, nearest_points

import prepare_print as prep

ROOT, JOB, HERE = prep.ROOT, prep.JOB, prep.HERE
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from enclosure_support_audit import audit


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def road_shape(roads):
    return unary_union([LineString((r['a'], r['b'])).buffer(r['width']/2) for r in roads])


def main():
    staged = next(JOB.glob('*-input.3mf'))
    native = next((JOB/'ready').glob('*.gcode.3mf'))
    preparation = json.loads((JOB/'preparation.json').read_text())
    assert sha(staged) == preparation['project_sha256']
    for path, digest in preparation['source_geometry_and_settings_sha256'].items():
        assert sha(ROOT/path) == digest, path
    with zipfile.ZipFile(staged) as source, zipfile.ZipFile(native) as output:
        assert output.testzip() is None
        expected = json.loads(source.read('Metadata/project_settings.config'))
        actual = json.loads(output.read('Metadata/project_settings.config'))
        differences = {k: [expected.get(k), actual.get(k)] for k in set(expected)|set(actual)
                       if expected.get(k) != actual.get(k)}
        assert set(differences) <= {'inherits_group', 'different_settings_to_system'}, differences
        assert all(actual[k] == expected[k][:4] for k in differences)
        settings = {
            'filament_nozzle_map': ['0', '1'], 'filament_colour': ['#000000', '#FFFFFF'],
            'filament_printable': ['3', '3'], 'nozzle_diameter': ['0.4', '0.4'],
            'layer_height': '0.24', 'initial_layer_print_height': '0.2',
            'enable_arc_fitting': '0', 'support_type': 'normal(auto)', 'support_style': 'snug',
            'support_base_pattern': 'rectilinear', 'support_interface_top_layers': '2',
            'support_interface_spacing': '0.5', 'support_top_z_distance': '0.45',
            'support_bottom_z_distance': '0.45',
            'support_object_xy_distance': '0.8', 'support_object_first_layer_gap': '0.5',
            'support_filament': '1', 'support_interface_filament': '1', 'flush_into_support': '0',
        }
        for key, value in settings.items():
            assert actual[key] == value, (key, actual[key])
        gc = output.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest() == output.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'ready/plate_1.gcode').write_bytes(gc)
        (JOB/'preview.png').write_bytes(output.read('Metadata/plate_1.png'))
        plate = ET.fromstring(output.read('Metadata/slice_info.config')).find('plate')
        assert {o.get('identify_id'): o.get('name') for o in plate.findall('object')} == preparation['identify_ids']
        assert all(o.get('skipped') == 'false' for o in plate.findall('object'))
        assert {n.get('id') for n in plate.findall('nozzle')} == {'0', '1'}
        assert {m.get('key'): m.get('value') for m in plate.findall('metadata')}['outside'] == 'false'
    trims = [float(z) for z in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gc, re.M)]
    assert trims == [0., .02]
    roads = list(segments(JOB/'ready/plate_1.gcode'))
    assert {r['object'] for r in roads} == {2303}
    supports = [r for r in roads if r['feature'].startswith('Support')]
    model = [r for r in roads if not r['feature'].startswith('Support')
             and r['feature'] not in ('Brim', 'Custom', 'Prime tower')]
    assert supports and {r['tool'] for r in supports} == {0}
    layers = wall_layers(native, 2303)
    assert [(z, h) for z, h in layers if abs(h-.24) > .001] == [(.2, .2), (3.2, .12), (8.13, .13)]
    assert all(z in dict(layers) for z in (4.4, 13.65, 15.33, 16.05, 16.29, 16.53))
    white = sorted({r['layer'] for r in model if r['tool'] == 1})
    assert white == [15.57, 15.81, 16.05, 16.29, 16.53]
    assert max(r['layer'] for r in model if r['tool'] == 0) == 16.05
    raised_checks = []
    for z in (16.29, 16.53):
        raised = [r for r in model if r['layer'] == z]
        assert raised and {r['tool'] for r in raised} == {1}
        # Installed artwork bounds transformed to the checked print placement,
        # expanded into the clear gaps between the three groups.
        regions = {'logo_and_drop': (117, 143), 'lettering': (145, 187), 'qr': (188, 214)}
        counts = {name: sum(all(low < p[0] < high for p in (r['a'], r['b'])) for r in raised)
                  for name, (low, high) in regions.items()}
        assert all(count > 10 for count in counts.values()), (z, counts)
        assert sum(counts.values()) == len(raised), 'Raised paths outside artwork regions'
        raised_checks.append({'print_z_mm': z, 'height_mm': dict(layers)[z], 'white_paths_by_region': counts})
    first_gap = road_shape([r for r in supports if r['layer'] == .2]).distance(
        road_shape([r for r in model if r['layer'] == .2]))
    assert first_gap >= .45, first_gap
    # Inspect emitted bead edges on every shared leaf/support layer. A nominal
    # XY setting alone does not establish the narrowest removable clearance.
    leaf_clearances = []
    for z in sorted({r['layer'] for r in model} & {r['layer'] for r in supports}):
        if z >= 13.65:
            continue
        leaf = road_shape([r for r in model if r['layer'] == z])
        scaffold = road_shape([r for r in supports if r['layer'] == z])
        gap = leaf.distance(scaffold)
        assert gap >= .50, (z, gap)
        leaf_clearances.append({'print_z_mm': z, 'bead_edge_gap_mm': gap,
                                'closest_points_xy_mm': [list(p.coords[0]) for p in nearest_points(leaf, scaffold)]})
    hook_support_gaps = []
    for side in (-1, 1):
        x0, x1 = sorted((165+side*42.1, 165+side*44.8))
        bearing = box(x0, 109.5, x1, 140.5)
        above = [r for r in supports if r['layer'] > 4.4
                 and LineString((r['a'], r['b'])).buffer(r['width']/2).intersects(bearing)]
        bottom = min(r['layer']-dict(layers)[r['layer']] for r in above)
        assert bottom-4.4 >= .45, (side, bottom)
        hook_support_gaps.append({'side': side, 'bearing_z_mm': 4.4,
                                  'support_bottom_z_mm': bottom, 'vertical_gap_mm': bottom-4.4})
    # Both catches retain their full width and exact bearing height, then become stems.
    hook_bands = []
    for z in (3.44, 4.4, 4.64):
        shape = road_shape([r for r in model if r['layer'] == z])
        for side in (-1, 1):
            cut = shape.intersection(LineString(((165+side*39, 125), (165+side*47, 125))))
            low, _, high, _ = cut.bounds
            span = high-low
            assert span > 4.6 if z <= 4.4 else 1.2 < span < 1.4, (side, z, span)
            hook_bands.append({'side': side, 'print_z_mm': z, 'section_width_mm': span})
    centre = box(150, 110, 180, 140)
    central = [r for r in supports if r['feature'] == 'Support interface'
               and LineString((r['a'], r['b'])).intersects(centre)]
    support_top = max(r['layer'] for r in central)
    first_back_layer = min(r['layer'] for r in model
                           if LineString((r['a'], r['b'])).intersects(centre))
    plate_bottom = first_back_layer-dict(layers)[first_back_layer]
    support_gap = plate_bottom-support_top
    assert abs(plate_bottom-13.65) < .001 and abs(support_gap-.48) < .001
    assert sorted({r['layer'] for r in central}) == [12.93, 13.17]
    support = audit(JOB/'ready/plate_1.gcode', 'nameplate-face-up-raised', profile=staged,
                    include_unlabelled_support=True)
    assert support['summary']['model_rooted_bodies'] == 0
    assert support['summary']['bodies_without_interface_labels'] == 0
    support['removal_access'] = (
        'Rear-face support is exposed around all plate edges. Separate the connected support mat; '
        'the central region exits along the 38 mm plate axis between the two leaves, '
        'and each outer strip exits toward its nearest short end. No receiver is installed during removal.')
    support['physical_removal_tested'] = False
    (JOB/'support-audit.json').write_text(json.dumps(support, indent=2)+'\n')
    points = np.array([p for r in model+supports for p in (r['a'], r['b'])])
    low, high = points.min(axis=0)-.6, points.max(axis=0)+.6
    assert float(min(*(low-[25, 0]), *([325, 320]-high))) > 15
    # Reconstruct the final face directly from extrusion paths, viewed from above.
    scale = 20
    lo, hi = np.array([110., 103.]), np.array([220., 147.])
    im = Image.new('RGB', tuple(((hi-lo)*scale).astype(int)), '#777777')
    draw = ImageDraw.Draw(im)
    for z in (16.05, 16.29, 16.53):
        for r in model:
            if r['layer'] != z:
                continue
            a, b = [tuple(((np.array(p)-lo)*scale).round().astype(int)) for p in (r['a'], r['b'])]
            color, width = ('white' if r['tool'] else 'black'), max(1, round(r['width']*scale))
            draw.line((a, b), fill=color, width=width)
            for x, y in (a, b):
                draw.ellipse((x-width/2, y-width/2, x+width/2, y+width/2), fill=color)
    ImageOps.flip(im).save(JOB/'show-face-paths.png')
    result = json.loads((JOB/'ready/result.json').read_text())
    assert result['return_code'] == 0
    sliced, = result['sliced_plates']
    assert not sliced['warning_message']
    proof = {
        'pass': True, 'native_archive': str(native.relative_to(ROOT)), 'native_archive_sha256': sha(native),
        'gcode_sha256': hashlib.sha256(gc).hexdigest(), 'source_hashes_current': True,
        'native_export_metadata_normalizations': differences, 'other_settings_match_input': True,
        'receiver_reused': True, 'white_artwork_layers_mm': white, 'raised_artwork_layers_mm': [16.29, 16.53],
        'raised_artwork_checks': raised_checks,
        'show_face_print_z_mm': 16.05, 'artwork_rise_mm': .48, 'emitted_model_layers_z_height_mm': layers,
        'hook_sections': hook_bands, 'all_supports_black_left': True,
        'support_first_layer_emitted_gap_mm': first_gap, 'plate_back_print_z_mm': plate_bottom,
        'leaf_support_xy_clearances': leaf_clearances,
        'minimum_leaf_support_xy_gap_mm': min(row['bead_edge_gap_mm'] for row in leaf_clearances),
        'support_above_hook_gaps': hook_support_gaps,
        'support_top_print_z_mm': support_top, 'emitted_plate_back_support_gap_mm': support_gap,
        'support_summary': support['summary'], 'model_and_support_bounds_xy_mm': [low.tolist(), high.tolist()],
        'emitted_z_trim_mm': trims, 'estimated_seconds': sliced['total_predication'],
        'estimated_grams_saved_profile_density': sum(f['total_used_g'] for f in sliced['filaments']),
        'layer_count': int(re.search(rb'; total layer number: (\d+)', gc)[1]),
        'printer': 'Mark2', 'submitted': False,
    }
    (JOB/'verification.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k: proof[k] for k in ('pass', 'artwork_rise_mm', 'raised_artwork_checks', 'emitted_plate_back_support_gap_mm',
                                         'estimated_seconds', 'layer_count')}, indent=2))


if __name__ == '__main__':
    main()
