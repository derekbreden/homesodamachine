"""Run one staged generator with every Rust program pinned.

usage (cwd = the step's work dir): python inner.py <pins.json> <script>
pins.json maps a program name to its binary. A program missing from it is an error.
HSM_TRACE_COLD=<file> appends one JSON line per cold-core-data member access and call.
"""
import json, os, runpy, sys

pins_path, script = sys.argv[1], sys.argv[2]
sys.argv = [script]
# As `python <script>` would: the script's own directory first. The pinned-program hook
# imports `_rust_part` from hardware/scripts without leaving that directory on the path.
sys.path[0] = os.path.dirname(os.path.abspath(script))
_helper = os.path.abspath('hardware/scripts')
sys.path.insert(1, _helper)
import _rust_part  # noqa: E402
sys.path.remove(_helper)

PINS = json.load(open(pins_path))


def program(crate, name):
    if name not in PINS:
        raise SystemExit(f'no pinned program {crate}/{name}')
    from pathlib import Path
    return Path(PINS[name])


_rust_part.program = program

trace = os.environ.get('HSM_TRACE_COLD')
if trace:
    _layout = os.path.abspath('hardware/cold-core-layout')
    sys.path.insert(1, _layout)
    import _cold_core_data  # noqa: E402
    sys.path.remove(_layout)
    log = open(trace, 'a')
    original_member, original_call = _cold_core_data.member, _cold_core_data._Function.__call__
    names = {}

    def kind(v):
        t = type(v).__name__
        if isinstance(v, (list, tuple)) and v:
            return f'{t}[{kind(v[0])}]'
        return t

    def member(module, name):
        value = original_member(module, name)
        if isinstance(value, _cold_core_data._Function):
            names[id(value)] = f'{module}.{name}'
        log.write(json.dumps({'get': f'{module}.{name}', 'type': type(value).__name__}) + '\n')
        log.flush()
        return value

    def call(self, *args, **kwargs):
        log.write(json.dumps({'call': names.get(id(self), str(self._tag)),
                              'args': [kind(a) for a in args],
                              'kwargs': {k: kind(v) for k, v in kwargs.items()}}) + '\n')
        return original_call(self, *args, **kwargs)

    original_compiled = _cold_core_data.compiled

    def compiled(module, action="call", path=(), args=(), kwargs=None):
        log.write(json.dumps({'compiled': module, 'action': action, 'path': list(path)}) + '\n')
        log.flush()
        return original_compiled(module, action, path, args, kwargs)

    _cold_core_data.member = member
    _cold_core_data.compiled = compiled
    _cold_core_data._Function.__call__ = call

runpy.run_path(script, run_name='__main__')
