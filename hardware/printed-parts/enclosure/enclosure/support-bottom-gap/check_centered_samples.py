"""Independently read centered fit-sample placement and first-layer overlap."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile

import numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(HERE))
from read_roads import layers, MODEL, WALL

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def footprint(road):
    return LineString(((road[0], road[1]), (road[2], road[3]))).buffer(road[4]/2)


def review(directory, output):
    prep_path, native_path = directory / 'preparation.json', directory / 'native-slice.json'
    prep, native = json.loads(prep_path.read_text()), json.loads(native_path.read_text())
    archive = ROOT / native['archive']
    assert sha(archive) == native['archive_sha256']
    project = ROOT / native['project']
    assert sha(project) == native['project_sha256'] == prep['project_sha256']
    parts = {int(p['identify_id']): p for p in prep['parts']}
    assert len(parts) == 12 and all('frame' not in p['name'] for p in parts.values())
    assert all(sha(ROOT / p['source']) == p['stl_sha256'] for p in parts.values())
    area = np.array(prep['shared_printable_area_mm'])
    assert area.shape == (2, 2) and np.all(area[1] > area[0])
    counts = Counter(); tools = Counter(); support = Counter(); invalid = []
    bead_bounds = defaultdict(list); first = {}; seconds = {}; heights = defaultdict(list)
    first_components = {}; first_raw_components = {}; layers_per_owner = Counter()
    with zipfile.ZipFile(archive) as az:
        assert az.testzip() is None
        raw = az.read('Metadata/plate_1.gcode')
        assert hashlib.sha256(raw).hexdigest() == native['gcode_sha256']
        assert hashlib.md5(raw).hexdigest() == az.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        with az.open('Metadata/plate_1.gcode') as source:
            for z, _, roads, _ in layers(source):
                by_owner = defaultdict(list)
                for road in roads:
                    owner, feature = road[6], road[7]
                    if not (feature in MODEL or feature.startswith('Support')):
                        continue
                    if owner not in parts:
                        invalid.append(dict(line=road[-1], owner=owner, feature=feature,
                                            reason='unexpected object owner'))
                        continue
                    counts[(owner, feature)] += 1; tools[road[5]] += 1
                    if road[5] != 0 or road[4] <= 0 or road[10] <= 0 or road[8] not in ('G0', 'G1'):
                        invalid.append(dict(line=road[-1], owner=owner, feature=feature))
                    if feature.startswith('Support'):
                        support[owner] += 1
                    else:
                        by_owner[owner].append(road)
                    half = road[4]/2
                    for x, y in ((road[0], road[1]), (road[2], road[3])):
                        bead_bounds[owner].extend(((x-half, y-half), (x+half, y+half)))
                for owner, model in by_owner.items():
                    layers_per_owner[owner] += 1
                    walls = [r for r in model if r[7] in WALL]
                    height = walls[0][10] if walls else model[0][10]
                    if len(heights[owner]) < 2:
                        heights[owner].append(dict(top_z_mm=z, height_mm=height))
                    if owner not in first:
                        base = unary_union([footprint(r) for r in model])
                        first[owner] = base
                        # 2 microns admits coordinate rounding, not a physical
                        # extrusion gap or disconnected sample root.
                        raw_parts = list(base.geoms) if hasattr(base, 'geoms') else [base]
                        tidy = base.buffer(.002)
                        tidy_parts = list(tidy.geoms) if hasattr(tidy, 'geoms') else [tidy]
                        first_raw_components[owner] = len(raw_parts)
                        first_components[owner] = len(tidy_parts)
                    elif owner not in seconds:
                        values = []
                        for road in model:
                            bead = footprint(road)
                            values.append(dict(line=road[-1], feature=road[7],
                                               overlap_fraction=bead.intersection(first[owner]).area/bead.area))
                        seconds[owner] = values
    assert set(first) == set(parts) == set(seconds) == set(bead_bounds)
    rows = []; rectangles = {}
    for owner, part in parts.items():
        xy = np.array(bead_bounds[owner]); lo, hi = xy.min(0), xy.max(0)
        edge = dict(left_mm=float(lo[0]-area[0, 0]), right_mm=float(area[1, 0]-hi[0]),
                    front_mm=float(lo[1]-area[0, 1]), rear_mm=float(area[1, 1]-hi[1]))
        weakest = min(seconds[owner], key=lambda r: r['overlap_fraction'])
        outer = min((r['overlap_fraction'] for r in seconds[owner] if r['feature'] == 'Outer wall'), default=0.)
        bed_layers = heights[owner]
        layer_ok = (len(bed_layers) == 2 and abs(bed_layers[0]['top_z_mm']-.2) < .0005
                    and abs(bed_layers[0]['height_mm']-.2) < .0005
                    and abs(bed_layers[1]['top_z_mm']-.44) < .0005
                    and abs(bed_layers[1]['height_mm']-.24) < .0005)
        row = dict(name=part['name'], identify_id=owner, source=part['source'],
                   source_stl_sha256=part['stl_sha256'], full_bead_bounds_xy_mm=[lo.tolist(), hi.tolist()],
                   edge_margins_mm=edge, minimum_edge_margin_mm=min(edge.values()),
                   first_two_layers=bed_layers, first_layer_raw_components=first_raw_components[owner],
                   first_layer_components_at_2um_roundoff=first_components[owner],
                   first_layer_printed_area_mm2=first[owner].area,
                   min_second_layer_overlap_fraction=weakest['overlap_fraction'],
                   min_second_layer_outer_wall_overlap_fraction=outer,
                   weakest_second_layer_road=weakest, model_layers=layers_per_owner[owner],
                   support_roads=support[owner])
        row['pass'] = (layer_ok and row['minimum_edge_margin_mm'] >= 60.
                       and first_components[owner] == 1 and weakest['overlap_fraction'] > .5
                       and outer > .5 and support[owner] == 0)
        rows.append(row); rectangles[owner] = box(*lo, *hi)
    pairs = []
    for i, owner in enumerate(parts):
        for other in list(parts)[i+1:]:
            pairs.append(dict(a=parts[owner]['name'], b=parts[other]['name'],
                              full_bead_envelope_gap_mm=rectangles[owner].distance(rectangles[other])))
    min_pair = min(pairs, key=lambda p: p['full_bead_envelope_gap_mm'])
    all_xy = np.array([p for values in bead_bounds.values() for p in values])
    lo, hi = all_xy.min(0), all_xy.max(0)
    record = dict(schema=1, printer=prep['printer'], object_count=len(parts),
                  preparation_sha256=sha(prep_path), native_record_sha256=sha(native_path),
                  archive=native['archive'], archive_sha256=native['archive_sha256'],
                  project=native['project'], project_sha256=native['project_sha256'],
                  gcode_sha256=native['gcode_sha256'], shared_printable_area_mm=area.tolist(),
                  required_minimum_bead_edge_margin_mm=60., full_plate_bead_bounds_xy_mm=[lo.tolist(), hi.tolist()],
                  full_plate_envelope_center_mm=((lo+hi)/2).tolist(), usable_bed_center_mm=area.mean(0).tolist(),
                  minimum_bead_edge_margin_mm=min(r['minimum_edge_margin_mm'] for r in rows),
                  closest_full_bead_envelopes=min_pair, fixed_left_extrusion_tool_counts=dict(tools),
                  invalid_paths=invalid, parts=rows, pair_envelope_gaps=pairs,
                  reviewer='flush_funnel_frame', source_sha256=sha(__file__),
                  scope='Independent reading of actual object extrusion envelopes, connected first-layer roots and every second-layer model bead. Native paths do not establish physical adhesion, friction fit, dimensional accuracy or strength.')
    record['pass'] = all(r['pass'] for r in rows) and min_pair['full_bead_envelope_gap_mm'] >= 2. and not invalid
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(printer=record['printer'], objects=len(rows),
                          margin_mm=record['minimum_bead_edge_margin_mm'],
                          min_overlap=min(r['min_second_layer_overlap_fraction'] for r in rows),
                          min_outer_overlap=min(r['min_second_layer_outer_wall_overlap_fraction'] for r in rows),
                          closest_pair_gap_mm=min_pair['full_bead_envelope_gap_mm'],
                          failed_parts=[r['name'] for r in rows if not r['pass']],
                          passed=record['pass'], record=str(output)), indent=2))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = review(args.directory, args.output)
    if not result['pass']:
        raise SystemExit(1)
