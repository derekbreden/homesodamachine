"""Bind a front-top successor to its predecessor and original native path inputs."""
from pathlib import Path
import argparse
import json

import refine_review as refinement
import review as r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--original', type=Path,
                        default=Path('/tmp/pump-mount-before-lint-fix/enclosure-front-top.step'))
    parser.add_argument('--reading', type=Path, default=r.HERE / 'native-review.json')
    parser.add_argument('--delta-directory', type=Path,
                        help='retain native added/removed bodies for a separate manual reading')
    args = parser.parse_args()
    prior_sha = r.sha(args.reading)
    reading = json.loads(args.reading.read_text())
    old, old_id = refinement.read_native(args.baseline)
    matched = [entry for entry in reading['printed_stock_refinements']
               if any(part['part'] == 'enclosure-front-top' and
                      part['refined_native']['sha256'] == old_id['sha256']
                      for part in entry['parts'])]
    if not matched:
        raise RuntimeError('Baseline is not a recorded front-top stock refinement')
    new, new_id = refinement.read_native(r.ENC / 'enclosure-front-top.step')
    added, removed = refinement.delta(old, new)
    delta_cache = None
    if args.delta_directory is not None:
        args.delta_directory.mkdir(parents=True, exist_ok=True)
        delta_cache = dict(predecessor_native=old_id, refined_native=new_id, bodies={})
        for label, shape in (('added', added), ('removed', removed)):
            path = args.delta_directory / (label + '.brep')
            shape.exportBrep(str(path))
            delta_cache['bodies'][label] = dict(path=str(path.resolve()), sha256=r.sha(path),
                volume_mm3=r.volume(shape), bounds_mm=refinement.solid_bounds(shape))
        (args.delta_directory / 'index.json').write_text(json.dumps(delta_cache, indent=2) + '\n')
    guard_z = max(part['bearing_and_screw_guard_top_z_mm'] for entry in matched
                  for part in entry['parts'] if part['part'] == 'enclosure-front-top')
    guard = r.enc._ybox(-150., 150., 0., 230., 100., guard_z)
    protected_change = refinement.common_volume(removed, guard)
    result = dict(part='enclosure-front-top', original_native=old_id, refined_native=new_id,
        valid=new.isValid(), solids=len(new.Solids()), added_volume_mm3=r.volume(added),
        removed_volume_mm3=r.volume(removed), removed_bounds_mm=refinement.solid_bounds(removed),
        bearing_and_screw_guard_top_z_mm=guard_z,
        changed_volume_in_bearing_and_screw_guard_mm3=protected_change,
        native_delta_cache=delta_cache,
        scope='The current front-top is a native material subset of the recorded intermediate '
            'stock refinement. All original and added-stock rigid-clearance path bounds remain '
            'conservative. This comparison makes no wire/Faston fit or physical retention claim.')
    if not result['valid'] or result['solids'] != 1 or protected_change > r.VOLUME_FLOOR:
        raise RuntimeError(f'Successor changes the protected bearing/screw stock: {result}')
    if result['added_volume_mm3'] > r.VOLUME_FLOOR:
        result['scope'] = ('Native immediate-predecessor comparison. The added material '
            'requires direct final-stock path queries instead of a subset inference.')
        predecessor_comparison = result
        result = refinement.front_reading(reading, args.original,
            r.ENC / 'enclosure-front-top.step', r.ENC / 'enclosure-pump-retainer.step')
        result['immediate_predecessor_comparison'] = predecessor_comparison
        role = 'direct_added_stock_successor'
    else:
        role = 'removal_only_successor'
    for entry in matched:
        entry['role'] = 'intermediate_rigid_stock_refinement'
    reading['printed_stock_refinements'].append(dict(role=role,
        verification_source_sha256=r.sha(Path(__file__).resolve()),
        comparison_source_sha256=r.sha(Path(refinement.__file__).resolve()),
        prior_reading_sha256=prior_sha, status='native_refinement_clear', parts=[result]))
    temporary = args.reading.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(reading, indent=2) + '\n')
    temporary.replace(args.reading)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
