"""Typed Python access to the machine's statically compiled Rust recipes."""
from pathlib import Path
from types import ModuleType

from _rust_data import request
from _rust_objects import NativeProxy, decode, encode, handler, reference

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ('machine-data', 'machine-data')


def _argument(value):
    return reference(value) if isinstance(value, (dict, list, set)) else encode(value, SERVICE)


def _arguments(args, kwargs):
    return {'args': {'$tuple': [_argument(value) for value in args]},
            'kwargs': {'$dict': [[key, _argument(value)] for key, value in kwargs.items()]}}


def _response(service, payload):
    try:
        value = request(*service, payload, callback=handler)
    except ValueError as error:
        message = str(error)
        for kind in (AttributeError, KeyError, TypeError, FileNotFoundError,
                     AssertionError, RuntimeError, NotImplementedError):
            marker = kind.__name__ + ': '
            if marker in message:
                raise kind(message.split(marker, 1)[1]) from None
        raise
    return decode(value, service)


class Function(NativeProxy):
    """Retain a function's identity while hydrating its returned data containers."""

    def __call__(self, *args, **kwargs):
        from _rust_data import _LOCK
        with _LOCK:
            return _response(self._service, {'op': 'compiled_invoke', 'target': self._tag,
                **_arguments(args, kwargs)})


class Surface(ModuleType):
    """Forward temporary provider substitutions to the same Rust module state."""

    def __getattribute__(self, name):
        fields = ModuleType.__getattribute__(self, '__dict__')
        if name in fields.get('_rust_functions', ()):
            value = fields['_compiled'].get(name)
            if isinstance(value, NativeProxy) and value._tag['$native']['kind'] == 'callable':
                return Function(value._service, value._tag)
            return value
        return ModuleType.__getattribute__(self, name)

    def __setattr__(self, name, value):
        fields = ModuleType.__getattribute__(self, '__dict__')
        if name in fields.get('_rust_exports', ()):
            fields['_compiled'].set(name, value)
        ModuleType.__setattr__(self, name, value)


class Module:
    """Keep source-language types at the boundary; Rust owns each callable body."""

    def __init__(self, name):
        self.name = name

    def _read(self, action, path=(), args=(), kwargs=None):
        return _response(SERVICE, {'op': 'compiled', 'root': str(ROOT),
            'module': self.name, 'action': action, 'path': list(path),
            **_arguments(args, kwargs or {})})

    def get(self, name):
        if name.startswith('__') and name not in ('__all__',):
            raise AttributeError(name)
        try:
            return self._read('get', (name,))
        except ValueError as error:
            raise AttributeError(name) from error

    def call(self, name, *args, **kwargs):
        return self._read('call', (name,), args, kwargs)

    def set(self, name, value):
        return self._read('set', (name,), (value,))

    def names(self):
        return self._read('names')

    def main(self):
        return self._read('main')
