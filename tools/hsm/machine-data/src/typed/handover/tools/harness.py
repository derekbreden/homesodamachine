"""Run one staged script with every Rust data worker taken from pinned binaries.

usage (cwd = a staged work dir): python harness.py <bindir> <machine-data program> <script> [args...]
Workers whose binary is in <bindir> run that copy; machine-data runs the named program.
The script runs as `python <script>` would: its own directory first on sys.path, an
absolute __file__ and argv[0] naming it.
CALLBACK_STATS=<path> appends one JSON line of provider-callback counts and seconds at exit.
UNPINNED_LOG=<path> appends `crate name` for each worker taken from the live checkout.
"""
import os, runpy, sys
from pathlib import Path

bindir, machine, script = Path(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3])
sys.argv = [sys.argv[3], *sys.argv[4:]]
sys.path[0] = os.path.abspath('hardware/scripts')
import _rust_part  # noqa: E402

if os.environ.get('CALLBACK_STATS'):
    import atexit, collections, json, time
    import _rust_objects
    _handler = _rust_objects.handler
    _counts = collections.Counter()
    _seconds = collections.Counter()

    def handler(query):
        op = query.get('op')
        key = op + ':' + str(query.get('module') or query.get('name') or '')
        t = time.perf_counter()
        try:
            return _handler(query)
        finally:
            _counts[key] += 1
            _seconds[key] += time.perf_counter() - t

    _rust_objects.handler = handler

    @atexit.register
    def _stats():
        with open(os.environ['CALLBACK_STATS'], 'a') as out:
            out.write(json.dumps({'script': script, 'total': sum(_counts.values()),
                                  'seconds': round(sum(_seconds.values()), 3),
                                  'top': _counts.most_common(40),
                                  'slow': [(k, round(v, 3)) for k, v in _seconds.most_common(20)]}) + '\n')

sys.path[0] = os.path.dirname(script)
_original = _rust_part.program


def program(crate, name):
    if (crate, name) == ('machine-data', 'machine-data'):
        return Path(machine)
    pinned = bindir / name
    if pinned.is_file():
        return pinned
    if os.environ.get('UNPINNED_LOG'):
        with open(os.environ['UNPINNED_LOG'], 'a') as log:
            log.write(f'{crate} {name}\n')
    return _original(crate, name)


_rust_part.program = program
runpy.run_path(script, run_name='__main__')
