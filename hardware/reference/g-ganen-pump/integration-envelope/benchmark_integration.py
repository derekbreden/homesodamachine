"""Run the frozen detailed reference's identical distance/room-section probes."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
NATIVE = HERE/'g-ganen-integration-envelope.step'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operation(name):
    sys.path.insert(0, str(REFERENCE))
    import benchmark_native
    benchmark_native.NATIVE = NATIVE
    benchmark_native.operation(name)


def run():
    before = digest(NATIVE)
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
    if digest(NATIVE) != before:
        raise ValueError('Native envelope changed during benchmark')
    return {'status': 'indicative_query_costs', 'native_sha256': before,
            'tool_sha256': {'benchmark_integration.py': digest(Path(__file__)),
                           '../benchmark_native.py': digest(REFERENCE/'benchmark_native.py')},
            'detailed_reference_costs_sha256': digest(REFERENCE/'native-query-cost.json'),
            'operations': rows,
            'scope': 'Identical frozen benchmark implementation and fresh STEP imports, on this host during shared local work. These are indicative timings, not a full-assembly benchmark.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operation', choices=['distance', 'section'])
    args = parser.parse_args()
    if args.operation:
        operation(args.operation)
    else:
        (HERE/'native-query-cost.json').write_text(json.dumps(run(), indent=2)+'\n')
