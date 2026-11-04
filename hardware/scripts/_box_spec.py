"""The placement-derived enclosure description the enclosure producer reads.

The box is a named tuple of plain numbers, lists, tuples and dictionaries.  The placement pass
writes it once; the enclosure action reads that exact output before it cuts geometry.  Direct design runs deliberately do not read this artifact: they derive the live
placement so an edited checkout cannot use yesterday's stations.
"""

import json
import os
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "hardware" / "scripts").is_dir())
ARTIFACT = _ROOT / "hardware" / "manifold-layout" / "enclosure-box.json"
SCHEMA = 5
_RECORD = "__hsm_namedtuple__"
_LIST = "__hsm_list__"
_DICT = "__hsm_dict__"


def in_action() -> bool:
    """Whether this process must consume declared producer outputs."""
    return bool(os.environ.get("HSM_INPUT_DIGEST")
                or os.environ.get("HSM_BUILD_SOURCE") == "trace")


def _plain(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "_asdict"):
        return {
            _RECORD: type(value).__name__,
            "fields": list(value._fields),
            "values": [_plain(item) for item in value],
        }
    if isinstance(value, dict):
        if any(not isinstance(name, str) for name in value):
            raise TypeError("an enclosure-box dictionary key is not a string")
        return {_DICT: [[name, _plain(item)] for name, item in value.items()]}
    if isinstance(value, list):
        return {_LIST: [_plain(item) for item in value]}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    raise TypeError(f"{type(value).__name__} has no enclosure-box JSON form")


def _request(op, **values):
    from _rust_data import request
    return request('machine-data', 'machine-data', {'op': op, **values})


def _restore(value, named_types):
    """Hydrate Python container and namedtuple objects after Rust validates their wire form."""
    if isinstance(value, list):
        return tuple(_restore(item, named_types) for item in value)
    if isinstance(value, dict):
        if _RECORD in value:
            return named_types[value[_RECORD]](*(_restore(item, named_types) for item in value['values']))
        if _LIST in value:
            return [_restore(item, named_types) for item in value[_LIST]]
        return {name: _restore(item, named_types) for name, item in value[_DICT]}
    return value


def _tupled(value, named_types):
    """Restore a Rust-validated tagged scalar value as the caller's Python record types."""
    _request('box_validate', mode='value', value=value,
             types={name: list(record._fields) for name, record in named_types.items()})
    return _restore(value, named_types)


def document(box, bounds=()) -> dict:
    fields = tuple(getattr(box, "_fields", ()))
    if not fields:
        raise TypeError("the enclosure description is not a named tuple")
    return _request('box_document', box_fields=list(fields),
                    box={name: _plain(getattr(box, name)) for name in fields},
                    bounds=[{name: _plain(getattr(bound, name)) for name in bound._fields}
                            for bound in bounds])


def same_document(left, right) -> bool:
    """Compare placement descriptions at 1 nm, below the CAD mesh tolerance.

    Re-reading an OCCT solid can shift derived bounds by about 0.1 nm. Keep
    record structure and nonnumeric values exact while comparing float stations
    with an absolute 0.000001 mm allowance.
    """
    return _request('same_document', left=left, right=right)


def write(box, bounds=(), path=ARTIFACT) -> Path:
    """Write one deterministic description, atomically."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(document(box, bounds), indent=1, sort_keys=True) + "\n"
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, target)
    return target


def read(box_type, bound_type=None, named_types=(), path=ARTIFACT):
    """Read the declared description or fail before any geometry is cut."""
    target = Path(path)
    if not target.is_file():
        try:
            shown = target.relative_to(_ROOT)
        except ValueError:
            shown = target
        raise FileNotFoundError(f"{shown} is absent; build the enclosure-box producer")
    from _cadq_export import note_read
    note_read(target)
    records = tuple(named_types)
    types = {record.__name__: record for record in records}
    if len(types) != len(records):
        raise ValueError("enclosure-box record type names must be unique")
    fields = tuple(getattr(box_type, '_fields', ()))
    data = _request('box_validate', path=str(target.resolve()), box_fields=list(fields),
                    bound_fields=list(bound_type._fields) if bound_type else None,
                    types={name: list(record._fields) for name, record in types.items()})
    box = box_type(*(_restore(data['box'][name], types) for name in fields))
    bounds = (() if bound_type is None else tuple(
        bound_type(*(_restore(row[name], types) for name in bound_type._fields))
        for row in data['bounds']))
    return box, bounds


def selftest() -> int:
    import tempfile
    from collections import namedtuple

    Options = namedtuple("Options", "holes enabled")
    Box = namedtuple("Box", "inner stations options cuts")
    Bound = namedtuple("Bound", "id ok detail")
    box = Box((1.0, 2.0), [("port", (3.0, 4.0)), ["nested", {"cuts": [7, 8]}]],
              Options(((5.0, 6.0),), True), {"add": [(9.0, 10.0)], "cut": []})
    bounds = (Bound("fits", True, ["whole", ("typed",)]),)

    def same(want, got, where="root"):
        assert type(got) is type(want), f"{where}: {type(got).__name__} != {type(want).__name__}"
        if isinstance(want, dict):
            assert got.keys() == want.keys(), f"{where}: dictionary keys moved"
            for key in want:
                same(want[key], got[key], f"{where}[{key!r}]")
        elif isinstance(want, (list, tuple)):
            assert len(got) == len(want), f"{where}: sequence length moved"
            for i, (left, right) in enumerate(zip(want, got)):
                same(left, right, f"{where}[{i}]")
        else:
            assert got == want, f"{where}: {got!r} != {want!r}"

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "box.json"
        write(box, bounds, path)
        got, got_bounds = read(Box, Bound, (Options,), path=path)
        same(box, got, "box")
        same(bounds, got_bounds, "bounds")
        assert repr(got) == repr(box)

        malformed = document(box, bounds)
        malformed["extra"] = True
        path.write_text(json.dumps(malformed))
        try:
            read(Box, Bound, (Options,), path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("an extra top-level key was accepted")

        malformed = document(box, bounds)
        malformed["bounds"] = None
        path.write_text(json.dumps(malformed))
        try:
            read(Box, Bound, (Options,), path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("non-array bounds were accepted")

        malformed = document(box, bounds)
        malformed["box"]["options"] = {"holes": [], "enabled": True}
        path.write_text(json.dumps(malformed))
        try:
            read(Box, Bound, (Options,), path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("an untagged known record was accepted")

        malformed = document(box, bounds)
        malformed["box"]["options"]["extra"] = True
        path.write_text(json.dumps(malformed))
        try:
            read(Box, Bound, (Options,), path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("an extra tagged-record key was accepted")

        try:
            document(box._replace(cuts={1: "number", "1": "string"}), bounds)
        except TypeError:
            pass
        else:
            raise AssertionError("a non-string dictionary key was coerced")

        moved = document(box, bounds)
        moved["box_fields"].append("stale")
        path.write_text(json.dumps(moved))
        try:
            read(Box, Bound, (Options,), path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("a stale field list was accepted")
    print("_box_spec selftest OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(selftest())
