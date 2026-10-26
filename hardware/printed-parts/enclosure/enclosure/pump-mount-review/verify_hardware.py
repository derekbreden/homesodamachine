"""Explicitly compare a final native subset with its identified native references.

This preserves the path reading's actual input hashes. It appends the final
subset agreement only after every named native body agrees geometrically.
"""
from pathlib import Path
import argparse
import io
import json

import review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reading', type=Path)
    parser.add_argument('final_subset', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--front-bottom-reference', type=Path,
                        help='current native front-bottom, separately compared with its old path input')
    args = parser.parse_args()
    reading = json.loads(args.reading.read_text())
    record = reading['native_hardware_cache']
    cache = review.ROOT / record['cache_directory']
    index_path = cache / 'index.json'
    if review.sha(index_path) != record['index_sha256']:
        raise RuntimeError('The path-reading cache index changed')
    subset_sha = review.sha(args.final_subset)
    final = {name: shape for name, (shape, _colour)
             in review.import_assembly(args.final_subset).items()}
    if review.sha(args.final_subset) != subset_sha:
        raise RuntimeError('Final native subset changed during read')
    if set(final) != set(record['bodies']):
        raise RuntimeError('The final subset names differ from the path-reading inputs')
    rows = []
    front_bottom = None
    front_bottom_identity = None
    if args.front_bottom_reference is not None:
        front_bottom_identity = dict(path=review.path_label(args.front_bottom_reference),
                                    sha256=review.sha(args.front_bottom_reference))
        front_bottom = review.import_step(args.front_bottom_reference).val()
        if review.sha(args.front_bottom_reference) != front_bottom_identity['sha256']:
            raise RuntimeError('Current front-bottom changed during its read')
        if not any(part.get('current_front_bottom',{}).get('sha256') == front_bottom_identity['sha256']
                   for entry in reading['printed_stock_refinements'] for part in entry['parts']):
            raise RuntimeError('Current front-bottom has no recorded old/new stock scope')
    for name, row in record['bodies'].items():
        source_path = cache / row['file']
        if review.sha(source_path) != row['sha256']:
            raise RuntimeError(f'Cached native body changed: {name}')
        original = review.cq.Shape.importBrep(str(source_path))
        reference = front_bottom if name == 'enclosure-front-bottom' and front_bottom is not None else original
        candidate = final[name]
        serialized = io.BytesIO()
        candidate.exportBrep(serialized)
        candidate_sha = review.hashlib.sha256(serialized.getvalue()).hexdigest()
        same_serialization = candidate_sha == row['sha256'] and reference is original
        removed = 0. if same_serialization else review.volume(reference.cut(candidate))
        added = 0. if same_serialization else review.volume(candidate.cut(reference))
        bounds_delta = max(abs(a - b) for a, b in zip(
            review.shape_bounds(reference), review.shape_bounds(candidate)))
        rows.append(dict(name=name, original_brep_sha256=row['sha256'],
            current_native_reference=front_bottom_identity if reference is front_bottom else None,
            final_brep_sha256=candidate_sha, identical_native_serialization=same_serialization,
            removed_volume_mm3=removed, added_volume_mm3=added,
            maximum_bound_delta_mm=bounds_delta))
        print(f'{name}: removed {removed:.6g}, added {added:.6g} mm3', flush=True)
        if removed > review.VOLUME_FLOOR or added > review.VOLUME_FLOOR or bounds_delta > 1e-6:
            raise RuntimeError(f'Final hardware differs from the path-reading body: {name}')
    agreement = dict(
        scope='The final native subset was emitted from the same in-memory appliance '
              'as the final production aggregate. The original path-input hashes above '
              'are retained. Bodies compare with their original path inputs except an '
              'explicitly identified current front-bottom reference, whose old/new '
              'material and complete-path separation keep their separate native receipt.',
        verification_source_sha256=review.sha(Path(__file__).resolve()),
        original_reading_sha256=review.sha(args.reading),
        final_subset_sha256=subset_sha, status='all_named_native_bodies_agree', bodies=rows)
    if front_bottom is not None:
        agreement['status'] = '32_original_bodies_and_current_front_bottom_agree'
        reading.setdefault('current_hardware_agreements', []).append(agreement)
    else:
        reading['final_hardware_agreement'] = agreement
    args.out.write_text(json.dumps(reading, indent=2) + '\n')
    print(args.out, flush=True)


if __name__ == '__main__':
    main()
