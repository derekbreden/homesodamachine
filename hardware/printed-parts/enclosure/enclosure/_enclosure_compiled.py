"""Import, type and third-party object transport for compiled enclosure recipes."""
from pathlib import Path
from types import ModuleType
import sys

_hardware = next(path for path in Path(__file__).resolve().parents if path.name == 'hardware')
sys.path.insert(0, str(_hardware / 'scripts'))
from _rust_data import request as _request
import _rust_objects

_SERVICE = ('enclosure-data', 'enclosure-data')


def _transport(value):
    if isinstance(value, ModuleType) and '_rust_enclosure_module' in vars(value):
        return compiled(vars(value)['_rust_enclosure_module'], action='get')
    return value


def _argument(value):
    value = _transport(value)
    if type(value) in (dict, list, set):
        return _rust_objects.reference(value)
    return _rust_objects.encode(value, _SERVICE)


def _call_fields(args, kwargs):
    return {
        'args': {'$tuple': [_argument(value) for value in args]},
        'kwargs': {'$dict': [[key, _argument(value)] for key, value in (kwargs or {}).items()]},
    }


def _value(value):
    if isinstance(value, _rust_objects.NativeProxy) and value._service == _SERVICE:
        kind = value._tag['$native']['kind']
        if kind == 'callable':
            return _Callable(_SERVICE, value._tag)
        if kind == 'namespace':
            return _Namespace(_SERVICE, value._tag)
    return value


def _send(fields):
    import _rust_part
    result = _request(*_SERVICE, {
        'op': 'compiled', 'root': str(_rust_part.ROOT), **fields,
    }, callback=_rust_objects.handler)
    return _value(_rust_objects.decode(result, _SERVICE))


def compiled(module, action='call', path=(), args=(), kwargs=None):
    return _send({'module': module, 'action': action, 'path': list(path),
                  **_call_fields(args, kwargs)})


class _Callable(_rust_objects.NativeProxy):
    def __call__(self, *args, **kwargs):
        from _rust_data import _LOCK
        with _LOCK:
            return _send({'action': 'invoke', 'callable': self._tag,
                          **_call_fields(args, kwargs)})


class _Namespace(_rust_objects.NativeProxy):
    def __getattr__(self, name):
        return _value(super().__getattr__(name))


class _Module(ModuleType):
    def __setattr__(self, name, value):
        if name.startswith('__'):
            return super().__setattr__(name, value)
        module = ModuleType.__getattribute__(self, '_rust_enclosure_module')
        compiled(module, action='set', path=(name,), args=(value,))


def install(module):
    module.__class__ = _Module
