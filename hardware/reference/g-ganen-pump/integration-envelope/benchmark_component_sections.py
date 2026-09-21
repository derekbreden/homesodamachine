"""Compare component clipping with the identical full-compound room probe."""
from pathlib import Path
import hashlib
import json
import time

import cadquery as cq
import numpy as np

from native_queries import intersect_components, occupied_bounds

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    native = HERE/'g-ganen-integration-envelope.step'
    input_hashes = {name: digest(HERE/name) for name in
                   (native.name, 'native-query-cost.json', 'native_queries.py', Path(__file__).name)}
    standard = json.loads((HERE/'native-query-cost.json').read_text())
    section = next(row for row in standard['operations'] if row['operation'] == 'section')
    if section['status'] != 'completed':
        raise ValueError('The standard native room query did not complete')
    expected = next(json.loads(line) for line in section['stdout'].splitlines()
                    if json.loads(line)['stage'] == 'operation_complete')['result']['bounds_mm']
    started = time.perf_counter()
    shape = cq.importers.importStep(str(native)).val()
    imported = time.perf_counter()
    slab = cq.Solid.makeBox(130., 110., 38., cq.Vector(-60., -55., 20.))
    clipped = intersect_components(shape, slab)
    query_seconds = time.perf_counter()-imported
    actual = occupied_bounds(clipped)
    if not np.allclose(actual, expected, atol=1e-5, rtol=0):
        raise ValueError('Component section occupied bounds differ from the standard native query')
    valid = all(s.isValid() for s in clipped.Solids())
    if not valid:
        raise ValueError('Invalid native section fragment')
    empty = intersect_components(shape, cq.Solid.makeBox(1, 1, 1, cq.Vector(1000, 1000, 1000)))
    if occupied_bounds(empty) is not None:
        raise ValueError('Empty native section did not remain empty')
    for name, expected_hash in input_hashes.items():
        if digest(HERE/name) != expected_hash:
            raise ValueError('Input changed while measuring: '+name)
    result = {'schema': 1, 'status': 'same_native_occupied_bounds_pass',
              'input_sha256': input_hashes,
              'import_seconds': imported-started, 'query_seconds': query_seconds,
              'native_fragments': len(clipped.Solids()), 'all_fragments_valid': valid,
              'bounds_mm': actual, 'standard_compound_bounds_mm': expected,
              'maximum_bound_difference_mm': float(np.max(np.abs(np.asarray(actual)-expected))),
              'empty_case_pass': True,
              'geometry_identity': 'Union over components of (component intersect cutter) equals (union over components) intersect cutter. The output preserves overlaps; summed component volume is not union volume.',
              'scope': 'Identical room box and exact native solid components. Indicative host timing during shared local work, with a single cold import.'}
    (HERE/'component-section-cost.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('import_seconds', 'query_seconds', 'native_fragments',
                                          'maximum_bound_difference_mm', 'empty_case_pass')}), flush=True)


if __name__ == '__main__':
    run()
