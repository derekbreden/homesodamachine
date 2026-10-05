"""Bind the fresh front-top's retention, picked roots and holder support paths."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString, box

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path[:0] = [str(ENC / 'magnet-retention'), str(ROOT / 'hardware/scripts')]
from audit_prints import read_job
from enclosure_support_audit import audit
from check_picked_roots import check
from read_roads import layers, MODEL, WALL
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review(directory, reuse_readings=False):
    prep = json.loads((directory / 'preparation.json').read_text())
    native = json.loads((directory / 'native-slice.json').read_text())
    part, = prep['parts']
    offset = np.array(part['build_transform'][9:])-part['source_center_mm']
    archive, project = ROOT / native['archive'], ROOT / native['project']
    assert sha(archive) == native['archive_sha256'] and sha(project) == native['project_sha256']
    for source, expected in prep['source_sha256'].items():
        assert sha(ROOT / source) == expected, source
    job = dict(part='front-top', native_archive=native['archive'], native_archive_sha256=native['archive_sha256'],
               project=native['project'], project_sha256=native['project_sha256'], gcode_sha256=native['gcode_sha256'],
               source_stl_sha256=part['stl_sha256'], native_object_name='enclosure-front-top',
               machine_to_bed_translation_mm=offset.tolist(), solid_host_regions=prep['solid_host_regions'])
    geom = json.loads((ENC / 'magnet-retention/geometry-check.json').read_text())['pieces']['front-top']
    retention_path = directory / 'retention-native-check.json'
    if reuse_readings and retention_path.exists():
        retention = json.loads(retention_path.read_text())
        assert retention['native_archive_sha256'] == native['archive_sha256']
        assert retention['gcode_sha256'] == native['gcode_sha256']
        assert retention['project_sha256'] == native['project_sha256']
        assert retention['source_stl_sha256'] == part['stl_sha256']
    else:
        retention = read_job(job, geom)
        retention_path.write_text(json.dumps(retention, indent=2)+'\n')
    print('Retention checks:', retention['native_checks_pass'], flush=True)
    roots_path = directory / 'picked-roots.json'
    if reuse_readings and roots_path.exists():
        roots = json.loads(roots_path.read_text())
        assert roots['gcode_sha256'] == native['gcode_sha256']
        assert roots['source_stl_sha256'] == part['stl_sha256']
        assert np.allclose(roots['machine_to_bed_translation_mm'], offset)
    else:
        roots = check(directory / 'ready/plate_1.gcode', ROOT / part['source'], offset.tolist())
        roots_path.write_text(json.dumps(roots, indent=2)+'\n')
    topology_path = directory / 'support-audit.json'
    if reuse_readings and topology_path.exists():
        topology = json.loads(topology_path.read_text())
        assert topology['inputs']['gcode_sha256'] == native['gcode_sha256']
        assert topology['inputs']['model_sha256'] == part['stl_sha256']
        assert topology['inputs']['profile_sha256'] == native['project_sha256']
    else:
        topology = audit(directory / 'ready/plate_1.gcode', 'enclosure-front-top', model=ROOT / part['source'],
                         profile=project, include_unlabelled_support=True)
        topology_path.write_text(json.dumps(topology, indent=2)+'\n')
    # Declared tee-carrier window-cover posts, on both native flanks. The
    # three-millimetre top-half slots open upward and along both Y ends.
    post_y = (129.186, 141.186)
    post_z = (180.8, 224.796)
    slot_z = (202.798, 224.796)
    slot_x = ((-98.5, -95.5), (95.5, 98.5))
    slot_windows = [box(x0+offset[0], post_y[0]+offset[1], x1+offset[0], post_y[1]+offset[1]) for x0, x1 in slot_x]
    post_windows = [box(x0+offset[0], post_y[0]+offset[1], x1+offset[0], post_y[1]+offset[1])
                    for x0, x1 in ((-98.5, -92.5), (92.5, 98.5))]
    # The removable frame owns the front surround from the display roof arris
    # to a running slip before the Y200 seam. This interior window excludes
    # retained shell flank stock and its separate functional rail ends.
    opening = box(-98.2+offset[0], 95.8+offset[1], 98.2+offset[0], 199.5+offset[1])
    roof_roads = []; slot_roads = []; post_support = []; post_model = Counter()
    bead_min = [float('inf'), float('inf')]; bead_max = [-float('inf'), -float('inf')]
    model_heights = []; metadata_support_overrides = []
    with zipfile.ZipFile(archive) as az:
        settings = json.loads(az.read('Metadata/project_settings.config'))
        assert float(settings['support_bottom_z_distance']) == .3
        assert float(settings['support_object_xy_distance']) == .5
        assert float(settings['support_top_z_distance']) == .45
        assert settings['support_type'] == 'tree(auto)' and settings['support_style'] == 'default'
        assert settings['filament_colour'] == ['#000000'] and settings['filament_nozzle_map'] == ['0']
        config = ET.fromstring(az.read('Metadata/model_settings.config'))
        for parent in config.findall('object') + config.findall('object/part'):
            values = {m.get('key'): m.get('value') for m in parent.findall('metadata') if m.get('key')}
            support = {k: v for k, v in values.items() if k.startswith('support_') or k == 'enable_support'}
            if support:
                metadata_support_overrides.append(dict(name=values.get('name'), settings=support))
        assert not metadata_support_overrides, metadata_support_overrides
        with az.open('Metadata/plate_1.gcode') as data:
            for z, _, roads, _ in layers(data):
                model = [r for r in roads if r[6] == 1901 and r[7] in MODEL]
                walls = [r for r in model if r[7] in WALL]
                if model:
                    height = walls[0][10] if walls else model[0][10]
                    model_heights.append(dict(z_mm=z, height_mm=height))
                for road in roads:
                    if road[6] != 1901 or not (road[7] in MODEL or road[7].startswith('Support')):
                        continue
                    half = road[4]/2
                    road_box = (min(road[0], road[2])-half, min(road[1], road[3])-half,
                                max(road[0], road[2])+half, max(road[1], road[3])+half)
                    bead_min[0] = min(bead_min[0], road_box[0]); bead_min[1] = min(bead_min[1], road_box[1])
                    bead_max[0] = max(bead_max[0], road_box[2]); bead_max[1] = max(bead_max[1], road_box[3])
                    cad_top = z-offset[2]; cad_bottom = cad_top-road[10]
                    is_support = road[7].startswith('Support')
                    def near(window):
                        x0,y0,x1,y1 = window.bounds
                        return road_box[2] >= x0 and road_box[0] <= x1 and road_box[3] >= y0 and road_box[1] <= y1
                    roof_candidate = is_support and cad_top >= 334. and cad_bottom <= 355. and near(opening)
                    post_candidates = [(side, window) for side, window in zip(('west', 'east'), post_windows)
                                       if cad_top >= post_z[0] and cad_bottom <= post_z[1] and near(window)]
                    slot_candidates = [(side, window) for side, window in zip(('west', 'east'), slot_windows)
                                       if is_support and cad_top >= slot_z[0] and cad_bottom <= slot_z[1] and near(window)]
                    if not roof_candidate and not post_candidates and not slot_candidates:
                        continue
                    footprint = LineString(((road[0], road[1]), (road[2], road[3]))).buffer(half)
                    if roof_candidate and footprint.intersection(opening).area > 1e-5:
                        roof_roads.append(dict(line=road[-1], feature=road[7], machine_top_z_mm=cad_top,
                                               machine_bottom_z_mm=cad_bottom, width_mm=road[4],
                                               start_machine_xy_mm=[road[0]-offset[0], road[1]-offset[1]],
                                               end_machine_xy_mm=[road[2]-offset[0], road[3]-offset[1]]))
                    for side, window in post_candidates:
                        if footprint.intersection(window).area > 1e-5:
                            if is_support:
                                post_support.append(dict(side=side, line=road[-1], machine_top_z_mm=cad_top,
                                                         machine_bottom_z_mm=cad_bottom, feature=road[7], width_mm=road[4]))
                            else:
                                post_model[(side, round(z, 6))] += 1
                    for side, window in slot_candidates:
                        overlap = footprint.intersection(window).area
                        if overlap > 1e-5:
                            slot_roads.append(dict(side=side, line=road[-1], machine_top_z_mm=cad_top,
                                                   machine_bottom_z_mm=cad_bottom, overlap_slot_mm2=overlap))
    bed = np.array(prep['shared_printable_area_mm'])
    margins = np.concatenate((np.array(bead_min)-bed[0], bed[1]-np.array(bead_max)))
    assert min(margins) >= 10., margins
    assert post_model and all(any(side == key[0] for key in post_model) for side in ('west', 'east'))
    support = dict(schema=1, archive_sha256=native['archive_sha256'], gcode_sha256=native['gcode_sha256'],
                   source_stl_sha256=part['stl_sha256'], support_topology=topology['summary'],
                   support_style=settings['support_style'], support_type=settings['support_type'],
                   per_object_support_overrides=metadata_support_overrides,
                   removed_front_roof_window_support_roads=roof_roads,
                   tee_window_cover_slot_support_roads=slot_roads, tee_window_cover_post_support_roads=post_support,
                   post_model_layer_counts={side: sum(key[0] == side for key in post_model) for side in ('west', 'east')},
                   post_y_mm=post_y, post_z_mm=post_z, slot_z_mm=slot_z, slot_x_mm=slot_x,
                   minimum_full_bead_bed_margin_mm=float(min(margins)),
                   all_model_heights=model_heights,
                   removal_route='Use the open funnel/frame bay and empty cartridge bay before hardware installation; release functional contacts and cut sacrificial branch junctions. Keep leverage off the tee-window cover posts. The cover slots open upward and at both Y ends.',
                   physical_cleanup_qualified=False,
                   scope='Actual native support roads in the removed roof opening and both cover-post/slot windows, including unlabelled short bodies. Counts and open routes do not establish physical detachment effort or cover-holder strength.')
    (directory / 'roof-holder-support-review.json').write_text(json.dumps(support, indent=2)+'\n')
    result = dict(native_checks_pass=retention['native_checks_pass'] and not roof_roads and not slot_roads,
                  archive=native['archive'], archive_sha256=native['archive_sha256'], project=native['project'],
                  project_sha256=native['project_sha256'], gcode_sha256=native['gcode_sha256'],
                  estimated_seconds=native['estimated_seconds'], support_summary=topology['summary'],
                  picked_seam_contact_mm2=[p['touching_support_emitted_model_overlap_mm2'] for p in roots['picks']],
                  front_roof_support_roads=len(roof_roads), tee_cover_slot_support_roads=len(slot_roads),
                  submitted=False, physical_fit_retention_cleanup_and_finish_qualified=False)
    (directory / 'verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--reuse-readings', action='store_true', help='Reuse exact digest-bound read-only component checks.')
    args = parser.parse_args()
    review(args.directory, args.reuse_readings)
