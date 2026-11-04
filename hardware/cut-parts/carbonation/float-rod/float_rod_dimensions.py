"""Finished carbonator guide rod and axial fit requirements, in inches.

The Rust cold-core data recipe owns the dimensions and independent-extreme
stack calculation, including drill point and rod-end form.
"""

import sys
from pathlib import Path

_hardware = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_layout = _hardware / "cold-core-layout"
if str(_layout) not in sys.path:
    sys.path.insert(0, str(_layout))
from _cold_core_data import read as _read

globals().update(_read("rod"))


def fit_envelope(*, rod_diameter, register_depth):
    """Conservative independent-extreme axial stack, including rod-end form."""
    return _read("rod-fit", rod_diameter=rod_diameter, register_depth=register_depth)
