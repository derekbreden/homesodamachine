"""Opaque third-party objects for compiled Rust document and recipe callbacks.

The Rust caller owns its arithmetic, branching and iteration. This registry
passes values to an imported provider or library primitive and carries objects
such as ReportLab canvases by identity across the JSON transport.
"""

import importlib
import operator
import threading
from pathlib import Path

_objects = {}
_identities = {}
_lock = threading.RLock()


def _service(named=None):
    if named is not None:
        return tuple(named)
    from _rust_data import current_service
    return current_service()


def encode(value, service=None):
    """JSON primitives and containers by value; library objects by opaque handle."""
    if isinstance(value, NativeProxy):
        return value._tag if _service(service) == value._service else reference(value)
    if type(value).__module__.startswith("pypdf."):
        return reference(value)
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if isinstance(value, slice):
        return {"$slice": [value.start, value.stop, value.step]}
    if isinstance(value, frozenset):
        return {"$frozenset": [encode(item, service) for item in value]}
    if isinstance(value, set):
        return {"$set": [encode(item, service) for item in value]}
    if type(value) is tuple:
        return {"$tuple": [encode(item, service) for item in value]}
    if isinstance(value, list):
        return [encode(item, service) for item in value]
    if isinstance(value, dict):
        return {"$dict": [[encode(key, service), encode(item, service)] for key, item in value.items()]}
    return reference(value)


def reference(value):
    """Carry a library object or mutable object field by its identity."""
    with _lock:
        identity = id(value)
        if identity not in _identities:
            handle = len(_objects) + 1
            _identities[identity] = handle
            _objects[handle] = value
        return {"$ref": _identities[identity]}


def decode(value, service=None):
    if isinstance(value, list):
        return [decode(item, service) for item in value]
    if isinstance(value, dict):
        if set(value) == {"$path"}:
            return Path(value["$path"])
        if set(value) == {"$frozenset"}:
            return frozenset(decode(item, service) for item in value["$frozenset"])
        if set(value) == {"$set"}:
            return {decode(item, service) for item in value["$set"]}
        if set(value) == {"$native"}:
            owner = _service(service)
            if owner is None:
                raise ValueError("A compiled object needs the Rust service that returned it")
            return NativeProxy(owner, value)
        if set(value) == {"$slice"}:
            return slice(*value["$slice"])
        if set(value) == {"$bytes"}:
            return bytes.fromhex(value["$bytes"])
        if set(value) == {"$ref"}:
            return _objects[value["$ref"]]
        if set(value) == {"$tuple"}:
            return tuple(decode(item, service) for item in value["$tuple"])
        if set(value) == {"$dict"}:
            return {decode(key, service): decode(item, service) for key, item in value["$dict"]}
        return {key: decode(item, service) for key, item in value.items()}
    return value


def snapshot(value):
    """Copy JSON-compatible container structure while retaining opaque leaves."""
    if type(value).__module__.startswith("pypdf."):
        return reference(value)
    if isinstance(value, NativeProxy) and value._tag["$native"]["kind"] in (
            "dict", "list", "tuple", "set", "frozenset"):
        return snapshot(value._invoke("snapshot"))
    if isinstance(value, tuple):
        return {"$tuple": [snapshot(item) for item in value]}
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    if isinstance(value, dict):
        return {"$dict": [[snapshot(key), snapshot(item)]
                           for key, item in value.items()]}
    if isinstance(value, frozenset):
        return {"$frozenset": [snapshot(item) for item in value]}
    if isinstance(value, set):
        return {"$set": [snapshot(item) for item in value]}
    return encode(value)


class NativeProxy:
    """Identity-preserving access to a callable or mutable compiled Rust value."""

    def __init__(self, service, tag):
        from _rust_data import service_generation
        owner = tuple(service)
        object.__setattr__(self, "_native_service", owner)
        object.__setattr__(self, "_native_tag", tag)
        object.__setattr__(self, "_native_generation", service_generation(owner))

    def _check_generation(self):
        from _rust_data import service_generation
        owner = object.__getattribute__(self, "_native_service")
        generation = object.__getattribute__(self, "_native_generation")
        if generation is None or service_generation(owner) != generation:
            raise RuntimeError(
                "Compiled value belongs to a closed or restarted service: " + owner[1]
            )

    @property
    def _service(self):
        self._check_generation()
        return object.__getattribute__(self, "_native_service")

    @property
    def _tag(self):
        self._check_generation()
        return object.__getattribute__(self, "_native_tag")

    def _invoke(self, operation, **fields):
        from _rust_data import _LOCK, request
        with _LOCK:
            self._check_generation()
            payload = {"_hsm_native": {"id": self._tag["$native"]["id"],
                                       "op": operation, **fields}}
            result = request(*self._service, payload, callback=handler)
            return decode(result, self._service)

    def __call__(self, *args, **kwargs):
        return self._invoke("call", args=encode(args, self._service),
                            kwargs=encode(kwargs, self._service))

    def __getattr__(self, name):
        try:
            return self._invoke("attr", name=name)
        except ValueError as error:
            raise AttributeError(name) from error

    def __setattr__(self, name, value):
        self._invoke("setattr", name=name, value=encode(value, self._service))

    def __getitem__(self, key):
        return self._invoke("get", key=encode(key, self._service))

    def __setitem__(self, key, value):
        self._invoke("set", key=encode(key, self._service),
                     value=encode(value, self._service))

    def __delitem__(self, key):
        self._invoke("delete", key=encode(key, self._service))

    def __iter__(self):
        return iter(self._invoke("iter"))

    def __len__(self):
        return self._invoke("len")

    def __bool__(self):
        return self._invoke("bool")

    def __str__(self):
        return self._invoke("str")

    def __repr__(self):
        return self._invoke("repr")

    def __contains__(self, item):
        return self._invoke("contains", item=encode(item, self._service))

    def __enter__(self):
        return self._invoke("enter")

    def __exit__(self, kind, value, traceback):
        from _rust_data import _LOCK
        with _LOCK:
            return self._invoke("exit", args=encode((kind, value, traceback), self._service))

    def _binary(self, operation, other):
        return self._invoke("binary", operator=operation,
                            other=encode(other, self._service))

    def __add__(self, other):
        return self._binary("add", other)

    def __sub__(self, other):
        return self._binary("sub", other)

    def __mul__(self, other):
        return self._binary("mul", other)

    def __truediv__(self, other):
        return self._binary("truediv", other)

    def __neg__(self):
        return self._invoke("unary", operator="neg")

    def __eq__(self, other):
        return self._binary("eq", other)

    def __ne__(self, other):
        return self._binary("ne", other)


def handler(query):
    """Execute one explicit provider/library operation and encode its result.

    Commands use ``op`` plus ``object`` for a previously encoded object:
    import(module), getattr(name), call(args, kwargs), setattr(name, value),
    getitem(key), setitem(key, value), iter, len, bool, str, repr, contains(item),
    binary(operator, other), unary(operator), next, enter and exit.
    """
    operation = query["op"]
    if operation == "import":
        return encode(importlib.import_module(query["module"]))
    obj = decode(query["object"])
    if operation == "snapshot":
        return snapshot(obj)
    if operation == "getattr":
        value = getattr(obj, query["name"])
        return reference(value) if isinstance(value, (list, dict, set)) else encode(value)
    if operation == "call":
        value = obj(*decode(query.get("args", [])),
                    **decode(query.get("kwargs", {})))
        return reference(value) if isinstance(value, (list, dict, set)) else encode(value)
    if operation == "setattr":
        setattr(obj, query["name"], decode(query["value"]))
        return None
    if operation == "getitem":
        value = obj[decode(query["key"])]
        return reference(value) if isinstance(value, (list, dict, set)) else encode(value)
    if operation == "setitem":
        obj[decode(query["key"])] = decode(query["value"])
        return None
    if operation == "iter":
        return [reference(value) if isinstance(value, (list, dict, set)) else encode(value)
                for value in obj]
    if operation == "len":
        return len(obj)
    if operation == "bool":
        return bool(obj)
    if operation == "str":
        return str(obj)
    if operation == "repr":
        return repr(obj)
    if operation == "contains":
        return decode(query["item"]) in obj
    if operation == "binary":
        return encode(getattr(operator, query["operator"])(obj, decode(query["other"])))
    if operation == "unary":
        return encode(getattr(operator, query["operator"])(obj))
    if operation == "next":
        return encode(next(obj))
    if operation == "enter":
        return encode(obj.__enter__())
    if operation == "exit":
        return encode(obj.__exit__(*decode(query.get("args", {"$tuple": [None, None, None]}))))
    raise ValueError("Unknown Rust object operation: " + operation)
