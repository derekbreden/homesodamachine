"""Python object interfaces for the compiled native build plan."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _rust_data import request, _LOCK
from _rust_objects import NativeProxy, decode, encode, handler

SERVICE = ("build-plan", "build-plan")


class _Function(NativeProxy):
    def __init__(self, native, name):
        super().__init__(native._service, native._tag)
        object.__setattr__(self, "_function_name", name)

    def __call__(self, *args, **kwargs):
        with _LOCK:
            result = request(*SERVICE, dict(root=str(ROOT), module="gen_build", path=[], action="invoke",
                             function=self._tag, args=encode(args, SERVICE), kwargs=encode(kwargs, SERVICE)), callback=handler)
            return decode(result, SERVICE)


def get(name):
    with _LOCK:
        result = request(*SERVICE, dict(root=str(ROOT), module="gen_build", path=[name], action="get"), callback=handler)
        value = decode(result, SERVICE)
        return _Function(value, name) if isinstance(value, NativeProxy) and value._tag["$native"]["kind"] == "callable" else value


def call(name, *args, **kwargs):
    with _LOCK:
        result = request(*SERVICE, dict(root=str(ROOT), module="gen_build", path=[name], action="call",
                                   args=encode(args, SERVICE), kwargs=encode(kwargs, SERVICE)), callback=handler)
        return decode(result, SERVICE)
