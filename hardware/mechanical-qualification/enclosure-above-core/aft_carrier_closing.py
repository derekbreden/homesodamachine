"""Manual continuous +Y closing bound for the aft meter carrier and strap.

Run through the CAD queue. This reader loads the exported appliance only to
resolve the exact stationary inventory in wall-closing-loose-stage-review.json.
It substitutes the separate canonical lid at its selected frame. It constructs
two conservative swept boxes, then reads native intersections only for targets
whose bounds survive. It builds no appliance and runs on no generator or hook.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HW = ROOT / 'hardware'
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'manifold-layout'),
               str(HW / 'printed-parts/cold-core'),
               str(HW / 'printed-parts/enclosure/enclosure')]

import cadquery as cq
from _cadq_export import import_assembly, import_step
import above_core as layout
import _back_top_meter as meter
import _above_core_mounts as mounts


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def bounds(shape):
    box = shape.BoundingBox()
    return [[box.xmin, box.ymin, box.zmin],
            [box.xmax, box.ymax, box.zmax]]


def signature(shape):
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
            'faces': len(shape.Faces()), 'volume_mm3': shape.Volume(),
            'center_mm': list(shape.Center().toTuple()), 'bounds_mm': bounds(shape)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly', type=Path,
                        default=HW / 'manifold-layout/enclosure-assembly.step')
    parser.add_argument('--lid', type=Path,
                        default=HW / 'printed-parts/cold-core/foam-cap/foam-cap-lid-top.step')
    parser.add_argument('--stage-record', type=Path,
                        default=HERE / 'wall-closing-loose-stage-review.json')
    parser.add_argument('--output', type=Path, default=HERE / 'aft-carrier-closing-review.json')
    args = parser.parse_args()
    stage = json.loads(args.stage_record.read_text())
    assembly_hash = sha(args.assembly)
    imported = import_assembly(args.assembly)
    by_tail = {}
    for name, (shape, _color) in imported.items():
        by_tail.setdefault(name.rsplit('/', 1)[-1], []).append((name, shape))
    targets = {}
    resolved = {}
    for name in stage['stationary_components']:
        tail = name.rsplit('/', 1)[-1]
        matches = by_tail.get(tail, [])
        if len(matches) != 1:
            raise ValueError(f'{name}: expected one actual native body, found {len(matches)}')
        actual, shape = matches[0]
        targets[name] = shape
        resolved[name] = actual
    targets['cold-core/foam-cap-lid-top'] = import_step(args.lid).val().moved(
        layout.frame_location(layout.cap_lid_pose()))
    if sha(args.assembly) != assembly_hash:
        raise ValueError('The appliance artifact changed while being read')

    moving = {'aft-meter-carrier': meter.meter_supports()[1],
              'aft-meter-nominal-strip': mounts.nominal_tie_strips()['meter-aft']}
    readings = []
    for name, body in moving.items():
        lo, hi = bounds(body)
        swept_hi = [hi[0], hi[1] + 300., hi[2]]
        prism = cq.Solid.makeBox(*(b-a for a, b in zip(lo, swept_hi)), cq.Vector(*lo))
        rows = []
        for target, obstacle in targets.items():
            low, high = bounds(obstacle)
            separated = [axis for axis, i in zip('XYZ', range(3))
                         if hi[i] + (300. if i == 1 else 0.) < low[i] or high[i] < lo[i]]
            row = {'stationary': target, 'actual_name': resolved[target],
                   'bounds_mm': [low, high], 'separated_axes': separated}
            if not separated:
                common = prism.intersect(obstacle, tol=1.e-7)
                volume = 0. if common.isNull() else abs(common.Volume())
                row.update({'native_swept_box_common_mm3': volume,
                            'native_common_bounds_mm': bounds(common) if volume > 1.e-6 else None,
                            'native_swept_box_air_mm': prism.distance(obstacle)})
            row['passed'] = bool(separated) or row['native_swept_box_common_mm3'] <= 1.e-6
            rows.append(row)
        readings.append({'moving': name, 'component_signature': signature(body),
                         'swept_box_bounds_mm': [lo, swept_hi],
                         'target_count': len(rows),
                         'native_candidate_count': sum(not r['separated_axes'] for r in rows),
                         'targets': rows, 'passed': all(r['passed'] for r in rows)})
    sources = [Path(__file__), Path(meter.__file__), Path(mounts.__file__),
               Path(layout.__file__), HW / 'manifold-layout/above-core.json']
    result = {
        'schema': 1, 'units': 'mm', 'frame': 'Production enclosure XYZ; Z up',
        'scope': 'Only the aft meter carrier and its complete nominal flat-section strip '
                 'over the retained stationary core set in the named loose-stage record.',
        'method': 'For each moving body, its complete native bounding box is extended '
                  '300 mm in +Y. This box contains every intermediate translated body. '
                  'Native box/body intersections are read only after exact native bounds '
                  'survive. A zero common establishes a continuous rigid noncontact bound '
                  'for 0 <= Y offset <= 300 mm; no sampled scene motion is replayed.',
        'offset_range_mm': [[0., 0., 0.], [0., 300., 0.]],
        'native_volume_tolerance_mm3': 1.e-6,
        'stage_record': {'path': relative(args.stage_record), 'sha256': sha(args.stage_record),
                         'removed_moving_components': stage['removed_moving_components'],
                         'removed_stationary_component': stage['removed_stationary_component']},
        'artifacts': {relative(args.assembly): assembly_hash, relative(args.lid): sha(args.lid)},
        'canonical_lid_override': 'The separately exported top lid replaces only that '
                                  'appliance leaf at above_core.cap_lid_pose().',
        'stationary_components': stage['stationary_components'],
        'readings': readings,
        'source_sha256': {relative(path): sha(path) for path in sources},
        'passed': all(row['passed'] for row in readings),
        'limits': ['No other moving equipment, shell, front rail or handoff path is requalified.',
                   'The low V-A chain and lower pump elbow retain the named loose-stage prerequisites.',
                   'The strip is a nominal compound clearance witness, not a measured purchased tie '
                   'or a threading, retention, hand-access or force qualification.',
                   'A positive conservative box reading would be inconclusive about actual collision.'],
    }
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': relative(args.output), 'passed': result['passed'],
                      'moving': [{k: row[k] for k in ('moving', 'target_count',
                                 'native_candidate_count', 'passed')} for row in readings]}), flush=True)


if __name__ == '__main__':
    main()
