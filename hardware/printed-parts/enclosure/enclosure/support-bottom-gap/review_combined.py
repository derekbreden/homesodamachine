"""Read every frame layer and the complete native multi-object fit plate."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import shapely
import trimesh
from shapely.geometry import LineString, Point
from shapely.ops import polygonize, unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from enclosure_support_audit import audit
from read_roads import layers, MODEL, WALL
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
TAG = lambda n: f'{{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}}{n}'


def polygons_from_edges(edges):
    """Fill the actual section's odd/even material, retaining all interior holes."""
    if not len(edges):
        return []
    edges = np.round(edges[:, :, :2], 6)
    a, b = edges[:, 0], edges[:, 1]
    output = []
    for poly in polygonize(unary_union([LineString(e) for e in edges])):
        q = poly.representative_point()
        crossing = (a[:, 1] > q.y) != (b[:, 1] > q.y)
        st, en = a[crossing], b[crossing]
        at_x = st[:, 0] + (q.y-st[:, 1])*(en[:, 0]-st[:, 0])/(en[:, 1]-st[:, 1])
        if np.count_nonzero(at_x > q.x) % 2:
            output.append(poly)
    return output


def review(directory):
    prep = json.loads((directory / 'preparation.json').read_text())
    native = json.loads((directory / 'native-slice.json').read_text())
    archive = ROOT / native['archive']
    project = ROOT / native['project']
    assert sha(archive) == native['archive_sha256'] and sha(project) == native['project_sha256']
    assert len(prep['parts']) == 23 and prep['pause'] is None
    for source, expected in prep['source_sha256'].items():
        assert sha(ROOT / source) == expected, source
    expected_names = {p['name'] for p in prep['parts']}
    frame = prep['parts'][0]
    assert frame['name'] == 'funnel-frame' and frame['identify_id'] == 1901
    mesh = trimesh.load_mesh(ROOT / frame['source'], process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    offset = np.array(frame['build_transform'][9:]) - frame['source_center_mm']
    mesh.apply_translation(offset)
    tri_z = mesh.triangles[:, :, 2]
    low, high = tri_z.min(1), tri_z.max(1)

    def stock_section(z):
        ids = np.flatnonzero((low < z) & (high > z))
        return polygons_from_edges(trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z], local_faces=ids))

    counts = Counter(); tools = Counter(); object_layers = defaultdict(list)
    support_counts = Counter(); invalid = []; layer_rows = []; missed = []; flags = []
    first = {}; second = defaultdict(list); bounds = defaultdict(list)
    support_sweeps = []; support_sweep_flags = []; expansion_contacts = []
    six_wall_stations = []; coupon_wall_stations = {}
    parts_by_id = {p['identify_id']: p for p in prep['parts']}
    with zipfile.ZipFile(archive) as az:
        assert az.testzip() is None
        raw = az.read('Metadata/plate_1.gcode')
        assert hashlib.sha256(raw).hexdigest() == native['gcode_sha256']
        assert hashlib.md5(raw).hexdigest() == az.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert not re.search(rb'^\s*M400 U1\s*$', raw, re.M)
        settings = json.loads(az.read('Metadata/project_settings.config'))
        assert settings['filament_colour'] == ['#161616']
        assert settings['filament_nozzle_map'] == ['0']
        assert settings['wall_loops'] == '2' and settings['sparse_infill_density'] == '15%'
        assert float(settings['filament_flow_ratio'][0]) == .9555
        assert float(settings['xy_contour_compensation']) == 0. and float(settings['xy_hole_compensation']) == 0.
        assert settings['enable_support'] == '1' and settings['support_type'] == 'tree(auto)'
        assert settings['brim_type'] == 'no_brim' and settings['elefant_foot_compensation'] == '0'
        trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', raw, re.M)]
        assert trims == [0., .02], trims
        slice_plate = ET.fromstring(az.read('Metadata/slice_info.config')).find('plate')
        assert {n.get('id') for n in slice_plate.findall('nozzle')} == {'0'}
        plate_values = {m.get('key'): m.get('value') for m in slice_plate.findall('metadata')}
        assert plate_values['outside'] == 'false'
        config = ET.fromstring(az.read('Metadata/model_settings.config'))
        native_objects = {}
        for obj in config.findall('object'):
            values = {m.get('key'): m.get('value') for m in obj.findall('metadata')}
            name = values['name']; native_objects[name] = values
            if name != 'funnel-frame':
                assert values.get('enable_support') == '0', values
        assert set(native_objects) == expected_names
        ranges = ET.fromstring(az.read('Metadata/layer_config_ranges.xml'))
        span, = ranges.findall('object/range')
        assert float(span.get('min_z')) == 34. and float(span.get('max_z')) == 46.3
        assert {o.get('opt_key'): o.text for o in span} == {'layer_height': '0.24', 'wall_loops': '6'}
        with az.open('Metadata/plate_1.gcode') as data:
            for z, _, roads, _ in layers(data):
                models = defaultdict(list); supports = []
                for road in roads:
                    owner, feature = road[6], road[7]
                    if owner not in parts_by_id:
                        assert owner is None or owner < 0, (owner, road[-1])
                        continue
                    if feature in MODEL:
                        models[owner].append(road); counts[(owner, feature)] += 1
                    elif feature.startswith('Support'):
                        supports.append(road); support_counts[owner] += 1
                    else:
                        continue
                    tools[road[5]] += 1
                    if road[5] != 0 or road[8] not in ('G0', 'G1') or road[4] <= 0:
                        invalid.append(dict(line=road[-1], z_mm=z, road=road))
                    for x, y in ((road[0], road[1]), (road[2], road[3])):
                        bounds[owner].extend(((x-road[4]/2, y-road[4]/2), (x+road[4]/2, y+road[4]/2)))
                for owner, model in models.items():
                    walls = [r for r in model if r[7] in WALL]
                    height = walls[0][10] if walls else model[0][10]
                    object_layers[owner].append(dict(z_mm=z, height_mm=height, wall_roads=len(walls), model_roads=len(model)))
                    if not walls:
                        invalid.append(dict(owner=owner, z_mm=z, reason='Model layer has no walls.'))
                    part = parts_by_id[owner]
                    if part['name'].startswith('beduan-socket') and 39. < z < 40. and owner not in coupon_wall_stations:
                        translation = np.array(part['build_transform'][9:])-part['source_center_mm']
                        witness_y = translation[1]
                        crossings = []
                        for road in walls:
                            if (road[1] < witness_y) != (road[3] < witness_y):
                                x = road[0]+(witness_y-road[1])*(road[2]-road[0])/(road[3]-road[1])
                                if x > translation[0]+18.:
                                    crossings.append(dict(source_x_mm=x-translation[0], width_mm=road[4], feature=road[7]))
                        assert len(crossings) == 2, (part['name'], z, crossings)
                        coupon_wall_stations[owner] = dict(name=part['name'], print_z_mm=z, source_y_mm=0., crossings=crossings)
                    if abs(z-.2) < 1e-6:
                        first[owner] = unary_union([LineString(((r[0], r[1]), (r[2], r[3]))).buffer(r[4]/2) for r in model])
                    elif abs(z-.44) < 1e-6:
                        assert owner in first
                        for road in model:
                            bead = LineString(((road[0], road[1]), (road[2], road[3]))).buffer(road[4]/2)
                            second[owner].append((bead.intersection(first[owner]).area/bead.area, road[7]))
                if supports:
                    assert all(r[6] == 1901 for r in supports), 'Support was emitted for a fit sample.'
                    per_height = defaultdict(list)
                    for road in supports:
                        per_height[round(z-road[10]/2, 8)].append(road)
                    for cut, rr in per_height.items():
                        stock = unary_union(stock_section(cut))
                        motions = []; centre_crossings = []
                        for road in rr:
                            ax, bx = road[0]-offset[0], road[2]-offset[0]
                            if ax*bx < 0:
                                centre_crossings.append(road[-1])
                            sign = 1 if (ax+bx)/2 >= 0 else -1
                            outside = mesh.bounds[1 if sign > 0 else 0, 0]+sign*30.
                            motion = shapely.MultiPoint([(road[0], road[1]), (road[2], road[3]),
                                                        (outside, road[1]), (outside, road[3])]).convex_hull.buffer(road[4]/2)
                            motions.append(motion)
                            if 34.1 <= cut <= 46.1:
                                footprint = LineString(((road[0], road[1]), (road[2], road[3]))).buffer(road[4]/2)
                                outside_side = shapely.box(mesh.bounds[0, 0]-2, mesh.bounds[0, 1]-2, offset[0]-98.249, mesh.bounds[1, 1]+2).union(
                                    shapely.box(offset[0]+98.249, mesh.bounds[0, 1]-2, mesh.bounds[1, 0]+2, mesh.bounds[1, 1]+2))
                                if footprint.intersection(stock.intersection(outside_side)).area > 1e-5:
                                    expansion_contacts.append(dict(line=road[-1], cut_z_mm=cut))
                        overlap = unary_union(motions).intersection(stock).area
                        row = dict(print_z_mm=z, section_z_mm=cut, roads=len(rr), swept_native_stock_overlap_mm2=overlap,
                                   centre_crossing_roads=centre_crossings)
                        support_sweeps.append(row)
                        if overlap > 1e-5 or centre_crossings:
                            support_sweep_flags.append(row)
                model = models.get(1901)
                if not model:
                    continue
                walls = [r for r in model if r[7] in WALL]
                height = walls[0][10] if walls else model[0][10]
                cut = z-height/2
                polygons = stock_section(cut)
                lines = np.array([LineString(((r[0], r[1]), (r[2], r[3]))) for r in walls], dtype=object)
                widths = np.array([r[4] for r in walls]); tree = shapely.STRtree(lines)
                all_lines = np.array([LineString(((r[0], r[1]), (r[2], r[3]))) for r in model], dtype=object)
                all_widths = np.array([r[4] for r in model]); model_tree = shapely.STRtree(all_lines)
                components = []
                for poly in polygons:
                    hit = len(tree.query(poly, predicate='dwithin', distance=.5)) > 0
                    if not hit:
                        missed.append(dict(z_mm=z, area_mm2=poly.area, bounds_xy_mm=list(poly.bounds)))
                    points = []
                    for ring in [poly.exterior, *poly.interiors]:
                        count = max(5, int(np.ceil(ring.length)))
                        points.extend(ring.interpolate(i/count, normalized=True) for i in range(count))
                    points = np.array(points, dtype=object)
                    qi, wi = tree.query_nearest(points, all_matches=False)
                    air = shapely.distance(points[qi], lines[wi])-widths[wi]/2
                    max_air = float(air.max(initial=0.))
                    if max_air > .3:
                        i = int(air.argmax()); point = points[qi[i]]
                        _, mi = model_tree.query_nearest(np.array([point], dtype=object), all_matches=False)
                        cover_air = float(point.distance(all_lines[mi[0]])-all_widths[mi[0]]/2)
                        flags.append(dict(print_z_mm=z, native_section_z_mm=cut,
                                          witness_source_xyz_mm=[point.x-offset[0], point.y-offset[1], cut],
                                          wall_boundary_air_mm=max_air, nearest_all_model_bead_air_mm=cover_air))
                    components.append(dict(area_mm2=poly.area, receives_model_walls=hit, max_boundary_air_mm=max_air))
                layer_rows.append(dict(print_z_mm=z, height_mm=height, components=components))
                if 38. < cut < 42. and not six_wall_stations:
                    witness_y = offset[1]
                    crossings = []
                    for road in walls:
                        if (road[1] < witness_y) != (road[3] < witness_y):
                            x = road[0]+(witness_y-road[1])*(road[2]-road[0])/(road[3]-road[1])
                            if x > offset[0]+94:
                                crossings.append(dict(source_x_mm=x-offset[0], width_mm=road[4], feature=road[7]))
                    six_wall_stations.append(dict(print_z_mm=z, y_source_mm=0., crossings=crossings))
                if len(layer_rows) % 100 == 0:
                    print(f'Frame native layers reviewed: {len(layer_rows)}', flush=True)
    assert set(object_layers) == {p['identify_id'] for p in prep['parts']}
    assert len(coupon_wall_stations) == 5
    overlap_rows = []
    extent_rows = []
    bed = np.array(prep['shared_printable_area_mm'])
    for part in prep['parts']:
        owner = part['identify_id']
        rr = object_layers[owner]
        assert rr[0]['z_mm'] == .2 and rr[0]['height_mm'] == .2 and rr[1]['z_mm'] == .44
        values = second[owner]
        minimum = min(v for v, _ in values)
        outer = min(v for v, feature in values if feature == 'Outer wall')
        assert minimum > .5 and outer > .5, (part['name'], minimum, outer)
        overlap_rows.append(dict(name=part['name'], layers=len(rr), min_second_bead_overlap_fraction=minimum,
                                 min_second_outer_wall_overlap_fraction=outer))
        ext = np.array(bounds[owner]); bb = [ext.min(0).tolist(), ext.max(0).tolist()]
        margin = min(*list(ext.min(0)-bed[0]), *list(bed[1]-ext.max(0)))
        assert margin >= 10., (part['name'], margin)
        extent_rows.append(dict(name=part['name'], full_bead_bounds_xy_mm=bb, minimum_bed_margin_mm=margin))
    gaps = []
    for index, a in enumerate(extent_rows):
        for b in extent_rows[:index]:
            aa, bb = np.array(a['full_bead_bounds_xy_mm']), np.array(b['full_bead_bounds_xy_mm'])
            gap = float(np.linalg.norm(np.maximum(np.maximum(aa[0]-bb[1], bb[0]-aa[1]), 0.)))
            assert gap >= 8., (a['name'], b['name'], gap)
            gaps.append(dict(parts=[a['name'], b['name']], full_bead_bounding_box_gap_mm=gap))
    topology = audit(directory / 'ready/plate_1.gcode', 'funnel-frame', model=ROOT / frame['source'], profile=project,
                     include_unlabelled_support=True)
    (directory / 'support-audit.json').write_text(json.dumps(topology, indent=2)+'\n')
    result = dict(schema=1, native_checks_pass=not invalid and not missed and not expansion_contacts and not support_sweep_flags,
                  archive_sha256=native['archive_sha256'], gcode_sha256=native['gcode_sha256'],
                  fixed_left_model_and_support_tools=dict(tools), emitted_trim_mm=trims,
                  no_insertion_pause=True, object_count=23, support_roads_by_owner=dict(support_counts),
                  native_frame_layer_count=len(layer_rows), native_frame_components_missing_walls=missed,
                  invalid_emitted_paths=invalid, perimeter_diagnostics=flags, all_frame_layers=layer_rows,
                  object_layer_and_first_overlap=overlap_rows, full_bead_extents=extent_rows, full_bead_gaps=gaps,
                  six_wall_native_crossing_stations=six_wall_stations,
                  coupon_two_wall_crossing_stations=list(coupon_wall_stations.values()),
                  frame_only_layer_range_index=1,
                  expanding_roof_transition_support_contacts=expansion_contacts,
                  all_support_layer_sweeps=support_sweeps, support_sweep_flags=support_sweep_flags,
                  support_topology=topology['summary'], submitted=False,
                  scope='Native source geometry, emitted paths, full-width support footprints and mid-slab outward removal lanes. Geometric overlap does not establish adhesion, physical surface quality, hand fit, load or retention.')
    (directory / 'emitted-path-review.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('native_checks_pass', 'native_frame_layer_count', 'object_count',
                                            'support_topology', 'perimeter_diagnostics', 'support_sweep_flags')}, indent=2), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    review(args.directory)
