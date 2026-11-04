"""Compatibility transport for the Rust cold-core scalar recipes."""

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _rust_data import _LOCK, request as _request
from _rust_objects import NativeProxy as _NativeProxy

_SERVICE = ("cold-core-data", "cold-core-data")


def read(op, **inputs):
    return _request("cold-core-data", "cold-core-data", {"op": op, **inputs})


def _arguments(args, kwargs):
    import _rust_objects
    def argument(value):
        if isinstance(value, (dict, list, set)):
            return _rust_objects.reference(value)
        return _rust_objects.encode(value, _SERVICE)
    return {"args": {"$tuple": [argument(value) for value in args]},
            "kwargs": {"$dict": [[name, argument(value)]
                                  for name, value in kwargs.items()]}}


def _response(payload):
    import _rust_objects
    with _LOCK:
        result = _request(*_SERVICE, payload, callback=_rust_objects.handler)
        return _rust_objects.decode(result, _SERVICE)


class _Function(_NativeProxy):
    """Preserve a compiled function's identity and return public data by value."""

    def __call__(self, *args, **kwargs):
        with _LOCK:
            return _response({"op": "compiled-invoke", "target": self._tag,
                              **_arguments(args, kwargs)})


def member(module, name):
    with _LOCK:
        value = compiled(module, action="get", path=(name,))
        if isinstance(value, _NativeProxy) and value._tag["$native"]["kind"] == "callable":
            return _Function(value._service, value._tag)
        return value


def compiled(module, action="call", path=(), args=(), kwargs=None):
    """Marshal a compiled recipe call and its explicit library objects."""
    import _rust_part
    with _LOCK:
        return _response({
            "op": "compiled", "root": str(_rust_part.ROOT), "module": module,
            "action": action, "path": list(path),
            **_arguments(args, kwargs or {}),
        })
