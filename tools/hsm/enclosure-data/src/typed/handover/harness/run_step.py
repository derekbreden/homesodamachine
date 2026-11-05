"""Run one staged generator with pinned Rust data workers.

usage (cwd = the step's work dir): python run_step.py <script> [args...]
HSM_PIN_SPEC names a JSON file: {"workers": {name: program}, "pinned_dir": dir}.
A worker named in "workers" uses that program; any other data worker uses the copy of its
program in "pinned_dir" when one is there, so concurrent rebuilds elsewhere move nothing.

With HSM_TRACE_DIR set, every request into the compiled enclosure modules is logged with its
origin: py:<file>:<function> for Python code, worker:<crate> for a Rust worker's callback.
"""
import json
import os
import runpy
import sys

script = sys.argv[1]
sys.argv = [script, *sys.argv[2:]]
sys.path.insert(0, os.path.abspath('hardware/scripts'))
import _rust_data  # noqa: E402
import _rust_part  # noqa: E402

sys.path.pop(0)
sys.path[0] = os.path.dirname(os.path.abspath(script))

# HEAD's enclosure-checks program has no `nameplate-stock` / `nameplate-cuts` ops (bab473406
# added them to the back-top recipe only), so the enclosure step stops at its checks. Every
# variant asks the checks with those nodes emptied, so the code after the checks runs too.
_UNSUPPORTED = {'nameplate-stock', 'nameplate-cuts'}
_check = _rust_part.check


def _patched_check(crate, name, numbers):
    if name == 'enclosure-checks' and isinstance(numbers, dict) and isinstance(numbers.get('nodes'), list):
        nodes = numbers['nodes']
        if any(isinstance(n, dict) and n.get('op') in _UNSUPPORTED for n in nodes):
            numbers = dict(numbers, nodes=[dict(n, op='empty', inputs=[])
                                           if isinstance(n, dict) and n.get('op') in _UNSUPPORTED else n
                                           for n in nodes])
    return _check(crate, name, numbers)


_rust_part.check = _patched_check

spec = json.load(open(os.environ['HSM_PIN_SPEC']))
workers = spec.get('workers', {})
pinned = spec.get('pinned_dir')
_init = _rust_data._Worker.__init__


def _pinned_init(self, crate, name, program=None):
    if program is None:
        if name in workers:
            program = workers[name]
        elif pinned and os.path.exists(os.path.join(pinned, name)):
            program = os.path.join(pinned, name)
    _init(self, crate, name, program)


_rust_data._Worker.__init__ = _pinned_init

if os.environ.get('HSM_TRACE_DIR'):
    work = os.getcwd()
    stubs = set(spec.get('stubs', ()))
    infra = {'_enclosure_compiled.py', '_rust_data.py'}
    out = open(os.path.join(os.environ['HSM_TRACE_DIR'],
                            f"{os.environ.get('HSM_TRACE_STEP', 'step')}-{os.getpid()}.py.log"), 'a')
    seen = set()
    labels = {}

    def origin():
        f = sys._getframe(2)
        while f is not None:
            name = os.path.basename(f.f_code.co_filename)
            path = os.path.relpath(os.path.abspath(f.f_code.co_filename), work)
            if name in infra or path in stubs:
                f = f.f_back
                continue
            if name == '_rust_objects.py':
                if f.f_code.co_name == 'handler':
                    service = _rust_data.current_service()
                    return 'worker:' + (service[0] if service else '?')
                f = f.f_back
                continue
            return f'py:{path}:{f.f_code.co_name}'
        return 'none'

    def note(*row):
        if row not in seen:
            seen.add(row)
            out.write('\t'.join(map(str, row)) + '\n')
            out.flush()

    def tag_id(value):
        tag = getattr(value, '_native_tag', None) if hasattr(type(value), '_tag') else None
        try:
            return tag['$native']['id'], tag['$native']['kind']
        except Exception:
            return None

    enc = os.path.abspath('hardware/printed-parts/enclosure/enclosure')
    _ec = None
    if os.path.exists(os.path.join(enc, '_enclosure_compiled.py')):
        sys.path.insert(0, enc)
        import _enclosure_compiled as _ec  # noqa: E402
        sys.path.remove(enc)

    def _traced_send(fields):
        where = origin()
        action = fields.get('action', 'call')
        if action == 'invoke':
            ident = fields['callable']['$native']['id']
            label = labels.get(ident, f'?{ident}')
            module, path = 'invoke', label
        else:
            module, path = fields.get('module'), '.'.join(fields.get('path', ()))
        result = _send(fields)
        kind = None
        found = tag_id(result)
        if found:
            labels[found[0]] = f'{module}:{path}' if action != 'invoke' else f'{path}()'
            kind = found[1]
        note('send', where, action, module, path, kind or type(result).__name__)
        return result

    if _ec is not None:
        _send = _ec._send
        _ec._send = _traced_send
    _request = _rust_data.request

    def _traced_request(crate, name, payload, callback=None):
        if crate == 'enclosure-data' and isinstance(payload, dict) and '_hsm_native' in payload:
            native = payload['_hsm_native']
            label = labels.get(native.get('id'), f"?{native.get('id')}")
            note('native', origin(), native.get('op'), label, native.get('name', ''))
        elif crate == 'enclosure-data' and isinstance(payload, dict) and payload.get('op') != 'compiled':
            note('op', origin(), payload.get('op'))
        return _request(crate, name, payload, callback)

    _rust_data.request = _traced_request

    import atexit

    def _cad_state():
        cq = sys.modules.get('cadquery')
        note('cadquery', type(cq).__name__ if cq is not None else 'absent',
             'OCP' in sys.modules, 'OCP.OCP' in sys.modules)

    atexit.register(_cad_state)

runpy.run_path(script, run_name='__main__')
