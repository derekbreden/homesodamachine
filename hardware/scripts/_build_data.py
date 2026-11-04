"""Python paths and object types for Rust build/surface data operations."""
from pathlib import Path

from _rust_data import request as _request
import _rust_part


def request(op, *, callback=None, **fields):
    return _request("build-data", "build-data", {"op": op, **fields}, callback=callback)


def read(op, path, **fields):
    path = Path(path).resolve()
    try:
        _rust_part._READ_TARGETS.add(_rust_part._relative(path))
    except ValueError:
        pass
    return request(op, path=str(path), **fields)


def write(op, path, **fields):
    path = Path(path).resolve()
    try:
        _rust_part._WRITE_TARGETS.add(_rust_part._relative(path))
    except ValueError:
        pass
    return request(op, path=str(path), **fields)
