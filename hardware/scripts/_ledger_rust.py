"""Compatibility transport and trace registration for Rust ledger programs."""
from decimal import Decimal
from pathlib import Path
import datetime
import sys

import _rust_data
import _rust_part

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))


def _json(value):
    if isinstance(value, (Path, Decimal)):
        return str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json(v) for v in value]
    return value


def call(op, **payload):
    response = _rust_data.request("ledger", "ledger-data", _json({"root": ROOT, "op": op, **payload}))
    for name in response.get("reads", ()):
        try:
            _rust_part._READ_TARGETS.add(Path(name).resolve().relative_to(ROOT).as_posix())
        except ValueError:
            pass
    for name in response.get("rewritten", ()):
        try:
            _rust_part._WRITE_TARGETS.add(Path(name).resolve().relative_to(ROOT).as_posix())
        except ValueError:
            pass
        from docgen import note_rewritten
        note_rewritten(name)
    return response["result"]


def main(op, **payload):
    result = call(op, **payload)
    print(result["output"], end="")
    return result["status"]
