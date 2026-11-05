"""Build-support requests to the native build-data service."""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "hardware/scripts"))
from _build_data import request as _request


def request(op, **fields):
    return _request(op, **fields)
