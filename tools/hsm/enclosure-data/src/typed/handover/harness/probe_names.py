"""Print one enclosure module's names in order and what each holds (run through run_step.py).

usage: run_step.py probe_names.py <module>[,<module>...] <out.json>
"""
import json
import os
import sys

modules, out = sys.argv[1].split(','), sys.argv[2]
sys.path.insert(0, os.path.abspath('hardware/scripts'))
sys.path.insert(0, os.path.abspath('hardware/printed-parts/enclosure/enclosure'))
import _rust_objects  # noqa: E402
from _enclosure_compiled import compiled  # noqa: E402
import _enclosure_datums  # noqa: E402

_enclosure_datums.install()


def describe(v):
    if isinstance(v, _rust_objects.NativeProxy):
        kind = v._tag['$native']['kind']
        if kind in ('dict', 'list', 'tuple', 'set', 'frozenset'):
            return {'native': kind, 'value': _rust_objects.snapshot(v)}
        return {'native': kind}
    if type(v).__name__ == 'module':
        return {'module': v.__name__}
    if isinstance(v, type):
        return {'type': v.__module__ + '.' + v.__qualname__}
    if callable(v):
        return {'callable': type(v).__name__ + ':' + getattr(v, '__module__', '?') + '.' + getattr(v, '__qualname__', '')}
    try:
        return {'value': _rust_objects.snapshot(v), 'type': type(v).__name__}
    except Exception as e:  # noqa: BLE001
        return {'opaque': type(v).__name__, 'error': repr(e)[:300]}


result = {}
for m in modules:
    try:
        names = list(compiled(m, action='names'))
    except Exception as e:  # noqa: BLE001
        result[m] = {'error': repr(e)[:3000]}
        continue
    values = {}
    for n in names:
        try:
            values[n] = describe(compiled(m, action='get', path=(n,)))
        except Exception as e:  # noqa: BLE001
            values[n] = {'error': repr(e)[:500]}
    result[m] = {'names': names, 'values': values}
json.dump(result, open(out, 'w'), indent=1, default=repr)
