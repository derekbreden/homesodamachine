"""Verify the carrier obstacle-box memo change without rebuilding the appliance."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
SOURCE = 'hardware/manifold-layout/enclosure_assembly.py'
CACHE_SOURCE = 'hardware/scripts/_boxes.py'
OLD_REVISION = '987f5d91b303bcc19dd523bb719863db824b2a70'
OLD_SHA = 'fd28eef61a1a92b6c5ef3b5c7fd87d1ac055e07a24a34d00d4344fe54e9c4c30'
NEW_SHA = '999ec78472f9b2c4028733e41d8c379c284b4eb89b3879af8cfcd07c1577a029'
CACHE_SHA = 'b4ef9757879de112561a56d294a7705075a9006e2826e534cb1779781eaebc23'
OLD_LINE = b'            bb = blocker.BoundingBox()\n'
NEW_LINE = b'            bb = _boxes.boxed(blocker)\n'
COORDS = ('xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def label(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache', type=Path,
                        default=Path('/tmp/scanner-review/full-enclosure-current/route-pack'))
    parser.add_argument('--output', type=Path, default=HERE / 'carrier-box-cache-equivalence.json')
    args = parser.parse_args()
    before = subprocess.check_output(['git', 'show', OLD_REVISION + ':' + SOURCE], cwd=ROOT)
    after = (ROOT / SOURCE).read_bytes()
    assert sha(before) == OLD_SHA and sha(after) == NEW_SHA, 'Named source pair changed'
    assert sha((ROOT / CACHE_SOURCE).read_bytes()) == CACHE_SHA, 'Box cache changed'
    assert before.count(OLD_LINE) == 1
    assert before.replace(OLD_LINE, NEW_LINE) == after, 'A second source edit is present'
    old_tree, new_tree = ast.parse(before), ast.parse(after)
    target = next(n for n in old_tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == '_carrier_front_top_motion_bound')
    read = next(n for n in target.body if isinstance(n, ast.FunctionDef) and n.name == 'read')
    assignments = [n for n in ast.walk(read) if isinstance(n, ast.Assign)
                   and ast.unparse(n) == 'bb = blocker.BoundingBox()']
    assert len(assignments) == 1
    assignments[0].value = ast.parse('_boxes.boxed(blocker)', mode='eval').body
    assert ast.dump(old_tree, include_attributes=False) == ast.dump(new_tree, include_attributes=False)

    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path.insert(0, str(ROOT / 'hardware/scripts'))
    import cadquery as cq
    import _boxes
    frames_path = args.pack_cache / 'frames.json'
    frames = json.loads(frames_path.read_text())
    paths = [(name, args.pack_cache / row['brep']) for name, row in frames.items()
             if name.startswith(('valve-', 'coil-'))]
    enclosure = ROOT / 'hardware/printed-parts/enclosure/enclosure'
    paths += [('enclosure-' + name, enclosure / ('enclosure-' + name + '.step'))
              for name in ('front-top', 'front-bottom', 'back-top', 'back-bottom',
                           'pump-cap', 'pump-cartridge')]
    inputs = {label(p): sha(p.read_bytes()) for p in [frames_path, *(p for _, p in paths)]}
    _boxes._CACHE.clear()
    rows = []
    started = time.perf_counter()
    last_shape = None
    for name, path in paths:
        shape = (cq.Shape.importBrep(str(path)) if path.suffix == '.brep'
                 else cq.importers.importStep(str(path)).val())
        cached_start = time.perf_counter()
        cached = _boxes.boxed(shape)
        cached_seconds = time.perf_counter() - cached_start
        exact_start = time.perf_counter()
        direct = shape.BoundingBox()
        exact_seconds = time.perf_counter() - exact_start
        expected = [getattr(direct, c) for c in COORDS]
        actual = [getattr(cached, c) for c in COORDS]
        assert actual == expected, (name, actual, expected)
        wrapped_again = cq.Shape.cast(shape.wrapped)
        assert wrapped_again.wrapped.IsSame(shape.wrapped)
        repeats = [_boxes.boxed(wrapped_again) for _ in range(20)]
        assert all(b is cached for b in repeats), 'Repeated immutable obstacle did not reuse its exact box'
        row = {'name': name, 'native_path': label(path), 'coordinates_mm': actual,
               'direct_equals_cached_exactly': True, 'maximum_coordinate_delta_mm': 0.0,
               'same_native_shape_new_python_wrapper': True, 'cache_identity_hits': len(repeats),
               'initial_cached_seconds': cached_seconds, 'direct_optimal_seconds': exact_seconds}
        rows.append(row)
        print(f'PASS {name}: exact box equality and {len(repeats)} native-identity hits', flush=True)
        last_shape = shape

    # A moved wrapper must not reuse the original obstacle's position.
    original = _boxes.boxed(last_shape)
    moved = last_shape.translate((0.125, 0.25, 0.375))
    moved_cached, moved_direct = _boxes.boxed(moved), moved.BoundingBox()
    assert moved_cached is not original
    assert all(getattr(moved_cached, c) == getattr(moved_direct, c) for c in COORDS)
    assert not moved.wrapped.IsSame(last_shape.wrapped)
    for path, digest in inputs.items():
        assert sha((ROOT / path).read_bytes() if not Path(path).is_absolute() else Path(path).read_bytes()) == digest
    assert sha((ROOT / SOURCE).read_bytes()) == NEW_SHA
    assert sha((ROOT / CACHE_SOURCE).read_bytes()) == CACHE_SHA
    record = {
        'status': 'geometry_and_guard_equivalent',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_path': SOURCE, 'old_revision': OLD_REVISION,
        'old_sha256': OLD_SHA, 'new_sha256': NEW_SHA,
        'cache_source_path': CACHE_SOURCE, 'cache_source_sha256': CACHE_SHA,
        'reproducer_sha256': sha(Path(__file__).read_bytes()), 'command': sys.argv,
        'scope': 'One carrier clearance-loop obstacle-box query. No appliance or part geometry is constructed or exported; existing native obstacles and one translated identity witness are inspected.',
        'ast': {'only_named_assignment_changed': True, 'all_geometry_constructors_identical': True,
                'box_disjoint_condition_identical': True, 'exact_overlap_call_identical': True,
                'overlap_failure_threshold_and_reporting_identical': True,
                'returned_bound_identical': True},
        'cache_contract': 'The existing cache computes the same Shape.BoundingBox result, keys the placed native shape, verifies IsSame, pins it, and includes placement in its persistent BREP key.',
        'input_sha256': inputs, 'immutable_obstacles': rows,
        'different_location_probe': {'translation_mm': [0.125, 0.25, 0.375],
            'original_cache_not_reused': True, 'direct_equals_cached_exactly': True},
        'input_drift': [], 'elapsed_seconds': time.perf_counter() - started,
        'geometry_outputs_written': False, 'full_assembly_regenerated': False,
        'current_geometry_receipt_modified': False, 'print_released': False,
    }
    args.output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'obstacles': len(rows),
                      'identity_hits': sum(r['cache_identity_hits'] for r in rows),
                      'output': str(args.output)}, indent=2), flush=True)


if __name__ == '__main__':
    main()
