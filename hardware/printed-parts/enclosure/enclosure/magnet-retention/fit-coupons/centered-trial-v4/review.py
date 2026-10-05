"""Stream the exact centered coupon archive and bind its launch constraints."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in HERE.parents if (path / 'tools/publish_now.py').is_file())
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/enclosure/support-bottom-gap'))
from read_roads import layers, MODEL, WALL

sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review(directory):
    prep = json.loads((directory / 'preparation.json').read_text())
    native = json.loads((directory / 'native-slice.json').read_text())
    archive, project = ROOT / native['archive'], ROOT / native['project']
    assert sha(archive) == native['archive_sha256'] and sha(project) == native['project_sha256']
    assert len(prep['parts']) == 12 and prep['frame_quantity'] == prep['full_enclosure_quantity'] == 0
    expected = {f'rc62-pocket-{label.lower()}' for label in prep['selected_labels']['magnets']}
    expected.update(f'beduan-socket-{label.lower()}' for label in prep['selected_labels']['valves'])
    assert {part['name'] for part in prep['parts']} == expected
    assert prep['pause'] is None and not prep['layer_ranges_mm'] and not prep['support_painted_facets']
    for source, digest in prep['source_sha256'].items():
        assert sha(ROOT / source) == digest, source
    for part in prep['parts']:
        assert not part['supports_enabled'] and part['rotation_x_degrees'] == 0.
        assert abs(part['plate_bounds_mm'][0][2]) < 1e-6
        assert sha(ROOT / part['source']) == part['stl_sha256']
    with zipfile.ZipFile(project) as z:
        config = ET.fromstring(z.read('Metadata/model_settings.config'))
        objects = config.findall('object')
        assert len(objects) == 12
        for obj in objects:
            assert obj.find("metadata[@key='enable_support']").get('value') == '0'
            assert all(part.get('subtype') == 'normal_part' for part in obj.findall('part'))
        assert len(ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))) == 0
        assert 'Metadata/custom_gcode_per_layer.xml' not in z.namelist()
        assert not any(b'paint_supports' in z.read(part['member']) for part in prep['parts'])
    measurements = {part['identify_id']: dict(name=part['name'], tools=set(), layer_heights=[],
                    low=np.array([float('inf'),float('inf')]), high=np.array([-float('inf'),-float('inf')]),
                    model_roads=0) for part in prep['parts']}
    support_count = 0; trims = []; pauses = []; declared_mass = None
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        digest = hashlib.md5()
        with z.open('Metadata/plate_1.gcode') as stream:
            for raw in stream:
                digest.update(raw)
                text = raw.decode(errors='replace').strip()
                trim = re.match(r'G29\.1\s+Z([-+.\d]+)', text)
                if trim: trims.append(float(trim[1]))
                if re.match(r'(?:M400\s+U|M0(?:\s|$)|M1(?:\s|$))', text): pauses.append(text)
                mass = re.match(r'; total filament weight \[g\]\s*=\s*([\d.]+)', text)
                if mass: declared_mass = float(mass[1])
        assert digest.hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert trims == [0., round(prep['expected_textured_trim_mm'], 2)] and not pauses
        settings = json.loads(z.read('Metadata/project_settings.config'))
        for key, expected_value in dict(initial_layer_print_height='0.2', layer_height='0.24',
                wall_loops='2', sparse_infill_density='15%', enable_support='0',
                xy_contour_compensation='0', xy_hole_compensation='0', elefant_foot_compensation='0',
                brim_type='no_brim', brim_width='0', enable_arc_fitting='0',
                filament_map=['1'], filament_nozzle_map=['0']).items():
            assert settings[key] == expected_value, (key, settings[key])
        assert settings['filament_colour'] == (['#161616'] if prep['printer'] == 'Mark2' else ['#000000'])
        assert settings['filament_flow_ratio'][0] == '0.9555'
        with z.open('Metadata/plate_1.gcode') as stream:
            for z_height, _, roads, _ in layers(stream):
                for road in roads:
                    if road[7].startswith('Support'):
                        support_count += 1
                    if road[7] not in MODEL:
                        continue
                    assert road[6] in measurements, (road[-1], road[6])
                    item = measurements[road[6]]; item['tools'].add(road[5]); item['model_roads'] += 1
                    half = road[4]/2
                    item['low'] = np.minimum(item['low'], [min(road[0],road[2])-half,min(road[1],road[3])-half])
                    item['high'] = np.maximum(item['high'], [max(road[0],road[2])+half,max(road[1],road[3])+half])
                    pair = (round(z_height,6),round(road[10],6))
                    if road[7] in WALL and (not item['layer_heights'] or item['layer_heights'][-1][0] != pair[0]):
                        item['layer_heights'].append(pair)
    assert support_count == 0
    bed = np.array(prep['shared_printable_area_mm']); rows = []
    for ident, item in measurements.items():
        assert item['model_roads'] and item['tools'] == {0}
        assert item['layer_heights'][:2] == [(.2,.2),(.44,.24)]
        assert all(abs(pair[1]-.24) < 3e-6 for pair in item['layer_heights'][1:])
        assert all(abs(second[0]-first[0]-.24) < 1e-6
                   for first,second in zip(item['layer_heights'],item['layer_heights'][1:]))
        margins = np.concatenate((item['low']-bed[0],bed[1]-item['high']))
        assert min(margins) >= 60., (item['name'], margins)
        rows.append(dict(name=item['name'], identify_id=ident, model_road_count=item['model_roads'],
                         model_layer_count=len(item['layer_heights']), model_tools=[0],
                         full_bead_xy_bounds_mm=[item['low'].tolist(),item['high'].tolist()],
                         edge_margins_left_front_right_back_mm=margins.tolist(),
                         minimum_full_bead_edge_margin_mm=float(min(margins)),
                         first_two_model_layers_z_and_height_mm=item['layer_heights'][:2]))
    separations = []
    for index, first in enumerate(rows):
        for second in rows[:index]:
            a,b=np.array(first['full_bead_xy_bounds_mm']),np.array(second['full_bead_xy_bounds_mm'])
            axis_gap=np.maximum(np.maximum(a[0]-b[1],b[0]-a[1]),0.)
            gap=float(np.linalg.norm(axis_gap))
            assert gap >= 8., (first['name'],second['name'],gap)
            separations.append(dict(parts=[first['name'],second['name']],full_bead_box_gap_mm=gap))
    record=dict(checks_pass=True, status='centered_coupon_constraints_pass', printer=prep['printer'],
                archive=native['archive'],archive_sha256=native['archive_sha256'],
                gcode_sha256=native['gcode_sha256'],project_sha256=native['project_sha256'],
                preparation_sha256=sha(directory/'preparation.json'), reviewer_sha256=sha(Path(__file__)),
                selected_labels=prep['selected_labels'],fit_object_count=12,frame_count=0,full_enclosure_count=0,
                support_road_count=0,pause_count=0,local_modifier_count=0,
                emitted_z_trim_commands_mm=trims,estimated_seconds=native['estimated_seconds'],
                estimated_mass_g=declared_mass,
                minimum_full_bead_edge_margin_mm=min(row['minimum_full_bead_edge_margin_mm'] for row in rows),
                minimum_full_bead_box_gap_mm=min(row['full_bead_box_gap_mm'] for row in separations),
                shared_fit_settings={key:settings[key] for key in ('wall_loops','sparse_infill_density',
                    'filament_flow_ratio','xy_contour_compensation','xy_hole_compensation','filament_colour')},
                objects=rows,object_separations=separations,submitted=False,
                physical_fit_and_visual_adhesion_qualified=False)
    output=directory/'native-constraints-review.json';assert not output.exists()
    output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:record[key] for key in ('checks_pass','printer','archive_sha256',
                    'minimum_full_bead_edge_margin_mm','minimum_full_bead_box_gap_mm','estimated_seconds','estimated_mass_g')},indent=2))
    return record


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    review(parser.parse_args().directory)
