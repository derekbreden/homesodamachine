"""Compatibility transport for the Rust cold-core scalar recipes."""

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _rust_data import request as _request


def read(op, **inputs):
    return _request("cold-core-data", "cold-core-data", {"op": op, **inputs})
