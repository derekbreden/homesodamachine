"""Shared faucet stack dimensions supplied by the Rust scalar program.

Coordinates are +Z up, +X lateral and +Y toward the appliance back.
The shared fit allowance remains the printed-parts fit source's value.
"""

import sys
from pathlib import Path

_HARDWARE = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
sys.path.insert(0, str(_HARDWARE / "scripts"))
sys.path.insert(0, str(_HARDWARE / "printed-parts/cadlib"))
import fits
from _rust_data import request


globals().update(request("faucet-data", "faucet-data", {"op": "interface", "args": [fits.slip]}))
