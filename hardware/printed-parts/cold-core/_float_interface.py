"""Shared ASA Aero float and guide datums from the Rust cold-core recipe.

These dimensions place the trial article in the carbonator and reservoirs.
Reed reach is bench evidence; liquid switching levels still need calibration.
"""

import sys
from pathlib import Path

_layout = Path(__file__).resolve().parents[2] / "cold-core-layout"
if str(_layout) not in sys.path:
    sys.path.insert(0, str(_layout))
from _cold_core_data import read as _read

globals().update(_read("float"))


def magnet_above_waterline(mass_g=design_mass_g, liquid_density=water_density):
    """Magnet centre minus surface height for a guided dry upright article."""
    return _read("float-waterline", mass_g=mass_g, liquid_density=liquid_density)


def reed_edge_distance(rod_axis, reed_axis):
    """Conservative collinear horizontal reed-centre to nearest RC62 edge."""
    return _read("float-edge", rod_axis=rod_axis, reed_axis=reed_axis)


def reed_float_edge_distance(rod_axis, reed_axis):
    """Greatest collinear float-perimeter to reed-center distance with bore play."""
    return _read("float-edge", rod_axis=rod_axis, reed_axis=reed_axis, float_edge=True)
