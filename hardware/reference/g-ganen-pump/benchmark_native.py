"""Bounded indicative timings for the detailed reference's integration queries.

Each operation uses a fresh native STEP import. This records query cost without
running or changing the shared assembly. An operation is limited to 90 seconds,
including import; printed progress retains its last measured stage on timeout.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
NATIVE = HERE/'g-ganen-pump.step'


def operation(name):
    import cadquery as cq
    started = time.perf_counter()
    shape = cq.importers.importStep(str(NATIVE)).val()
    imported = time.perf_counter()
    print(json.dumps({'stage': 'imported', 'seconds': imported-started,
                      'solids': len(shape.Solids()), 'faces': len(shape.Faces())}), flush=True)
    if name == 'distance':
        obstacle = cq.Solid.makeBox(5., 5., 5., cq.Vector(-15., 34.5, 30.))
        started = time.perf_counter()
        result = {'distance_mm': shape.distance(obstacle)}
        description = '5 mm box beside the measured +Y head lug, lower corner (-15, 34.5, 30).'
    elif name == 'section':
        slab = cq.Solid.makeBox(130., 110., 38., cq.Vector(-60., -55., 20.))
        started = time.perf_counter()
        clipped = shape.intersect(slab)
        b = clipped.BoundingBox()
        result = {'bounds_mm': [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]],
                  'solids': len(clipped.Solids())}
        description = 'Native room section: X -60..70, full Y, Z 20..58; analogous to pump_west_face.'
    else:
        raise ValueError(name)
    print(json.dumps({'stage': 'operation_complete', 'operation': name,
                      'query_seconds': time.perf_counter()-started,
                      'description': description, 'result': result}), flush=True)


def run():
    before = hashlib.sha256(NATIVE.read_bytes()).hexdigest()
    rows = []
    for name in ('distance', 'section'):
        started = time.perf_counter()
        try:
            result = subprocess.run([sys.executable, __file__, '--operation', name],
                                    capture_output=True, text=True, timeout=90)
            rows.append({'operation': name, 'exit_code': result.returncode,
                         'wall_seconds': time.perf_counter()-started,
                         'stdout': result.stdout, 'stderr': result.stderr,
                         'status': 'completed' if result.returncode == 0 else 'failed'})
        except subprocess.TimeoutExpired as failure:
            output = failure.stdout or b''
            rows.append({'operation': name, 'status': 'timeout', 'wall_seconds': time.perf_counter()-started,
                         'timeout_including_import_seconds': 90,
                         'stdout': output.decode() if isinstance(output, bytes) else output})
        print(name, rows[-1]['status'], round(rows[-1]['wall_seconds'], 3), flush=True)
    if hashlib.sha256(NATIVE.read_bytes()).hexdigest() != before:
        raise ValueError('Native input changed during benchmark')
    return {'status': 'indicative_query_costs', 'native_sha256': before,
            'tool_sha256': {'benchmark_native.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'operations': rows,
            'scope': 'Fresh STEP imports and specified queries on this host during shared local work. These timings are not a performance guarantee or a full-assembly benchmark.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operation', choices=['distance', 'section'])
    args = parser.parse_args()
    if args.operation:
        operation(args.operation)
    else:
        (HERE/'native-query-cost.json').write_text(json.dumps(run(), indent=2)+'\n')
