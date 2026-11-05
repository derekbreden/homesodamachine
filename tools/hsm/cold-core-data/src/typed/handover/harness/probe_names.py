"""Every compiled module's names and the value each name holds.

usage (cwd = a work dir holding every input): python probe_names.py <pins.json> <out.json>
"""
import json, os, sys

pins_path, out = sys.argv[1], sys.argv[2]
sys.argv = ['probe']
_helper = os.path.abspath('hardware/scripts')
sys.path.insert(0, _helper)
import _rust_part  # noqa: E402

PINS = json.load(open(pins_path))


def program(crate, name):
    from pathlib import Path
    return Path(PINS[name])


_rust_part.program = program
sys.path.insert(0, os.path.abspath('hardware/cold-core-layout'))
import _cold_core_data as d  # noqa: E402
import _rust_objects  # noqa: E402

modules = [line.strip() for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules.txt')) if line.strip()]
modules = list(dict.fromkeys(modules))
if os.environ.get('PROBE_MODULES'):
    modules = os.environ['PROBE_MODULES'].split(',')


def describe(v):
    if isinstance(v, _rust_objects.NativeProxy):
        kind = v._tag['$native']['kind']
        if kind in ('dict', 'list', 'tuple', 'set', 'frozenset'):
            return {'native': kind, 'value': _rust_objects.snapshot(v)}
        return {'native': kind}
    if type(v).__name__ == 'module':
        return {'module': v.__name__}
    if callable(v) and not isinstance(v, type):
        return {'python': getattr(v, '__module__', '?') + '.' + getattr(v, '__qualname__', type(v).__name__)}
    if isinstance(v, type):
        return {'type': v.__module__ + '.' + v.__qualname__}
    try:
        return {'value': _rust_objects.snapshot(v)}
    except Exception as e:  # noqa: BLE001
        return {'opaque': type(v).__name__, 'error': repr(e)}


result = {}
for m in modules:
    try:
        names = list(d.compiled(m, action='names'))
    except Exception as e:  # noqa: BLE001
        result[m] = {'error': repr(e)[:2000]}
        continue
    entry = {}
    for n in names:
        try:
            entry[n] = describe(d.compiled(m, action='get', path=(n,)))
        except Exception as e:  # noqa: BLE001
            entry[n] = {'error': repr(e)[:500]}
    result[m] = {'names': names, 'values': entry}
json.dump(result, open(out, 'w'), indent=0, sort_keys=False, default=repr)
print(len(result), 'modules', sum(len(v.get('names', [])) for v in result.values()), 'names')
