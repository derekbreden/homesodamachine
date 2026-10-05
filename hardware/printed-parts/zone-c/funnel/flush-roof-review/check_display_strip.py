"""Read actual bead backing beneath the retained front display roof strip.

This is a read-only native G-code review. A Bridge/Overhang label alone is not
a verdict: prior model and support footprints determine the available backing.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from shapely.geometry import LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
SUPPORT = ROOT / 'hardware/printed-parts/enclosure/enclosure/support-bottom-gap'
sys.path.insert(0, str(SUPPORT))
from read_roads import layers, MODEL

FROZEN_STL_SHA = 'cc2cfd8a490b52439d957aa082b0e4369c5602076740494298b3a954f0ba36ba'
FACE_BOUNDS = (-96.878444663164, 93.158492076719,
                96.878444663167, 95.208492076719)
FACE_Z = 349.25
CURRENT_Z, PREVIOUS_Z = 349.32, 349.24
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def segments(geometry):
    return list(geometry.geoms) if hasattr(geometry, 'geoms') else [geometry]


def backing(line, footprint, below, offset):
    contact = footprint.intersection(below)
    free = line.difference(below)
    spans = sorted([p.bounds[0]-offset[0], p.bounds[2]-offset[0]]
                   for p in segments(contact) if not p.is_empty)
    merged = []
    for start, stop in spans:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], stop)
        else:
            merged.append([start, stop])
    free_lines = [p for p in segments(free)
                  if not p.is_empty and p.geom_type == 'LineString']
    return dict(centerline_backed_mm=line.intersection(below).length,
                longest_unbacked_centerline_mm=max((p.length for p in free_lines), default=0.),
                full_bead_contact_area_mm2=contact.area,
                full_bead_area_mm2=footprint.area,
                full_bead_contact_fraction=contact.area / footprint.area,
                any_bead_contact_projected_x_intervals_mm=merged,
                free_centerline_segments_machine_xy_mm=[
                    [[x-offset[0], y-offset[1]] for x, y in p.coords]
                    for p in free_lines])


def review(directory, output):
    prep = json.loads((directory / 'preparation.json').read_text())
    native = json.loads((directory / 'native-slice.json').read_text())
    part, = prep['parts']
    assert part['stl_sha256'] == FROZEN_STL_SHA
    assert sha(ROOT / part['source']) == FROZEN_STL_SHA
    archive = ROOT / native['archive']
    gcode = archive.parent / 'plate_1.gcode'
    assert sha(archive) == native['archive_sha256']
    assert sha(gcode) == native['gcode_sha256']
    offset = np.array(part['build_transform'][9:]) - part['source_center_mm']
    region = box(-110+offset[0], 85+offset[1], 110+offset[0], 101+offset[1])
    strip = box(FACE_BOUNDS[0]+offset[0], FACE_BOUNDS[1]+offset[1],
                FACE_BOUNDS[2]+offset[0], FACE_BOUNDS[3]+offset[1])
    prior, current, support = [], [], []
    with gcode.open('rb') as source:
        for z, _, roads, _ in layers(source):
            cad_z = z-offset[2]
            if cad_z > CURRENT_Z+.0001:
                break
            if cad_z < FACE_Z-1.0:
                continue
            for road in roads:
                if road[6] != 1901 or not (road[7] in MODEL or road[7].startswith('Support')):
                    continue
                half = road[4]/2
                if max(road[1], road[3])+half < region.bounds[1] or min(road[1], road[3])-half > region.bounds[3]:
                    continue
                line = LineString(((road[0], road[1]), (road[2], road[3])))
                footprint = line.buffer(half)
                if not footprint.intersects(region):
                    continue
                if abs(cad_z-PREVIOUS_Z) < .0001:
                    prior.append(footprint)
                if road[7].startswith('Support') and footprint.intersects(strip) and cad_z <= FACE_Z+.001:
                    support.append((cad_z, road, footprint))
                if abs(cad_z-CURRENT_Z) < .0001 and road[7] in MODEL and abs(road[2]-road[0]) > 180:
                    if footprint.intersection(strip).area > 1e-5:
                        current.append(road)
    assert prior and current, 'The frozen strip layers were not found.'
    previous = unary_union(prior)
    highest = max((z for z, _, _ in support), default=None)
    near_support = [(z, r, p) for z, r, p in support
                    if highest is not None and z >= highest-.001]
    support_tip = unary_union([p for _, _, p in near_support])
    rows = []
    for road in current:
        line = LineString(((road[0], road[1]), (road[2], road[3])))
        footprint = line.buffer(road[4]/2)
        row = dict(line=road[-1], feature=road[7], road_length_mm=line.length,
                   start_machine_xy_mm=[road[0]-offset[0], road[1]-offset[1]],
                   end_machine_xy_mm=[road[2]-offset[0], road[3]-offset[1]],
                   width_mm=road[4], height_mm=road[10],
                   machine_top_z_mm=CURRENT_Z,
                   machine_bottom_z_mm=CURRENT_Z-road[10],
                   support_tip_vertical_gap_mm=(CURRENT_Z-road[10]-highest
                                                if highest is not None else None),
                   previous_layer=backing(line, footprint, previous, offset),
                   support_tip=backing(line, footprint, support_tip, offset))
        rows.append(row)
    record = dict(schema=1, source_stl_sha256=FROZEN_STL_SHA,
                  native_project_sha256=native['project_sha256'],
                  archive_sha256=native['archive_sha256'], gcode_sha256=native['gcode_sha256'],
                  strip_bounds_machine_xy_mm=list(FACE_BOUNDS), native_face_z_mm=FACE_Z,
                  current_machine_z_mm=CURRENT_Z, previous_machine_z_mm=PREVIOUS_Z,
                  previous_printed_footprint_count=len(prior),
                  highest_local_support_top_machine_z_mm=highest,
                  local_support_tip_roads=[dict(line=r[-1], feature=r[7], machine_z_mm=z,
                                              width_mm=r[4], height_mm=r[10])
                                           for z, r, _ in near_support],
                  roads=rows,
                  scope='Full-width emitted model beads versus previous-layer model/support material and the highest local support-tip footprints. A projected support tip is separated by the recorded Z gap; it is not direct previous-layer bead overlap. Physical underside finish and removal effort remain unqualified.',
                  source_sha256=sha(__file__))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(record=str(output), roads=len(rows),
                          highest_local_support_top_machine_z_mm=highest,
                          free_previous_layer_spans_mm=[r['previous_layer']['longest_unbacked_centerline_mm'] for r in rows],
                          free_support_tip_spans_mm=[r['support_tip']['longest_unbacked_centerline_mm'] for r in rows]), indent=2))
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    review(args.directory, args.output)
