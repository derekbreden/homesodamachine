"""Type and library-object transport for compiled owner-guide programs."""
import sys

import _rust_part
import _rust_objects
from _rust_data import _LOCK, request

sys.path.insert(0, str(_rust_part.ROOT / "tools"))

_SERVICE = ('guides', 'guides')


def compiled(module, action='call', path=(), args=(), kwargs=None, mutable=()):
    with _LOCK:
        _rust_part.start()
        encoded_args = _rust_objects.encode(tuple(args), _SERVICE)
        encoded_kwargs = _rust_objects.encode(kwargs or {}, _SERVICE)
        for index, name in mutable:
            if index < len(args):
                encoded_args['$tuple'][index] = _rust_objects.reference(args[index])
            else:
                for item in encoded_kwargs['$dict']:
                    if item[0] == name:
                        item[1] = _rust_objects.reference(kwargs[name])
        result = request(*_SERVICE, {
            'op': 'compiled', 'root': str(_rust_part.ROOT), 'module': module,
            'action': action, 'path': list(path),
            'args': encoded_args,
            'kwargs': encoded_kwargs,
        }, callback=_rust_objects.handler)
        return _rust_objects.decode(result, _SERVICE)


def call(module, name, *args, **kwargs):
    return compiled(module, path=(name,), args=args, kwargs=kwargs)


def bind(module, namespace):
    def lookup(name):
        if name.startswith('__'):
            raise AttributeError(name)
        return compiled(module, 'get', (name,))
    namespace['__getattr__'] = lookup
    namespace['__dir__'] = lambda: compiled(module, 'names')


def python_type_module(module, path):
    import importlib.util
    import sys
    registered = sys.modules.get(module)
    if registered is not None:
        return registered
    spec = importlib.util.spec_from_file_location(module, path)
    registered = importlib.util.module_from_spec(spec)
    sys.modules[module] = registered
    spec.loader.exec_module(registered)
    return registered


def main(module):
    return compiled(module, 'main')
