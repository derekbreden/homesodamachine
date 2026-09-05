"""The placement-derived enclosure description shared by its two CAD producers.

The box is a named tuple of plain numbers, lists, tuples and dictionaries.  The placement pass
writes it once; the enclosure and ceiling actions read that exact output before either cuts
geometry.  Direct design runs deliberately do not read this artifact: they derive the live
placement so an edited checkout cannot use yesterday's stations.
"""

import json
import os
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "hardware" / "scripts").is_dir())
ARTIFACT = _ROOT / "hardware" / "manifold-layout" / "enclosure-box.json"
SCHEMA = 4
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


def _tupled(value, named_types):
    """Restore tuples and explicitly named records; dictionaries keep their names."""
    if isinstance(value, list):
        return tuple(_tupled(item, named_types) for item in value)
    if isinstance(value, dict):
        if _RECORD in value:
            if set(value) != {_RECORD, "fields", "values"}:
                raise ValueError("enclosure-box has a malformed tagged record")
            name = value.get(_RECORD)
            record_type = named_types.get(name)
            if record_type is None:
                raise ValueError(f"enclosure-box names unknown record type {name!r}")
            if not isinstance(value["fields"], list) or not isinstance(value["values"], list):
                raise ValueError(f"enclosure-box {name} fields and values must be arrays")
            fields = tuple(value["fields"])
            if fields != tuple(record_type._fields):
                raise ValueError(
                    f"enclosure-box {name} fields {fields!r}, expected {record_type._fields!r}")
            values = value["values"]
            if len(values) != len(fields):
                raise ValueError(f"enclosure-box {name} has {len(values)} values for {len(fields)} fields")
            return record_type(*(_tupled(item, named_types) for item in values))
        if _LIST in value:
            if set(value) != {_LIST} or not isinstance(value[_LIST], list):
                raise ValueError("enclosure-box has a malformed tagged list")
            return [_tupled(item, named_types) for item in value[_LIST]]
        if _DICT in value:
            if set(value) != {_DICT} or not isinstance(value[_DICT], list):
                raise ValueError("enclosure-box has a malformed tagged dictionary")
            out = {}
            for i, pair in enumerate(value[_DICT]):
                if not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str):
                    raise ValueError(f"enclosure-box dictionary pair {i} is malformed")
                if pair[0] in out:
                    raise ValueError(f"enclosure-box dictionary repeats key {pair[0]!r}")
                out[pair[0]] = _tupled(pair[1], named_types)
            return out
        keys = set(value)
        for record_type in named_types.values():
            if set(record_type._fields).issubset(keys):
                raise ValueError(
                    f"enclosure-box carries untagged {record_type.__name__} fields")
        raise ValueError("enclosure-box carries an untagged dictionary")
    return value


def document(box, bounds=()) -> dict:
    fields = tuple(getattr(box, "_fields", ()))
    if not fields:
        raise TypeError("the enclosure description is not a named tuple")
    return {
        "schema": SCHEMA,
        "box_fields": list(fields),
        "box": {name: _plain(getattr(box, name)) for name in fields},
        "bounds": [
            {name: _plain(getattr(bound, name)) for name in bound._fields}
            for bound in bounds
        ],
    }


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
        raise FileNotFoundError(
            f"{shown} is absent; build the enclosure-box producer")
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema", "box_fields", "box", "bounds"}:
        raise ValueError(f"{target.name} does not have the exact enclosure-box document shape")
    if data.get("schema") != SCHEMA:
        raise ValueError(
            f"{target.name} schema {data.get('schema')!r}, expected {SCHEMA}")
    fields = tuple(getattr(box_type, "_fields", ()))
    if not isinstance(data["box_fields"], list):
        raise ValueError(f"{target.name} box_fields is not an array")
    if tuple(data.get("box_fields", ())) != fields:
        raise ValueError(
            f"{target.name} names fields {tuple(data.get('box_fields', ()))!r}, "
            f"but this source expects {fields!r}")
    raw = data.get("box")
    if not isinstance(raw, dict) or set(raw) != set(fields):
        raise ValueError(f"{target.name} does not carry exactly one value for every Box field")
    records = tuple(named_types)
    types = {record.__name__: record for record in records}
    if len(types) != len(records):
        raise ValueError("enclosure-box record type names must be unique")
    box = box_type(*(_tupled(raw[name], types) for name in fields))
    if not isinstance(data["bounds"], list):
        raise ValueError(f"{target.name} bounds is not an array")
    if bound_type is None:
        return box, ()
    bound_fields = tuple(getattr(bound_type, "_fields", ()))
    bounds = []
    for i, row in enumerate(data["bounds"]):
        if not isinstance(row, dict) or set(row) != set(bound_fields):
            raise ValueError(f"{target.name} bound {i} does not match {bound_fields!r}")
        bounds.append(bound_type(*(_tupled(row[name], types) for name in bound_fields)))
    return box, tuple(bounds)


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
        assert type(got.options) is Options
        assert got.options.holes == ((5.0, 6.0),)
        assert got.stations[0][0] == "port"
        assert got.cuts["add"][0][1] == 10.0

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
