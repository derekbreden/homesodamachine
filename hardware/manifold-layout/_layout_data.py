"""Compatibility transport for the Rust appliance frame and tube recipes."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import _rust_part
from _rust_data import request


def data(op, **values):
    return request('layout-data', 'layout-data', {'op': op, **values})


def read_json(path):
    path = Path(path).resolve()
    try:
        _rust_part._READ_TARGETS.add(path.relative_to(_rust_part.ROOT).as_posix())
    except ValueError:
        pass
    return json.loads(data('specification', path=str(path)))
