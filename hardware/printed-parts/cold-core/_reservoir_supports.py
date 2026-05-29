"""Reservoir corner support — ITERATION 1: a single plain cylinder.

One vertical cylinder rising from the bag-pocket floor up to the height of
the reservoir's floor underside at one corner (the +X+Y corner), so we can
get placement + height right before adding anything else — no 45° print
cut, no sloped top to match the floor, no mirror, no other three corners.
Built for the +X pocket only."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
# reservoir.py is in the sibling reservoir/ dir; import it so the corner
# position + underside height track the reservoir directly.
sys.path.insert(0, str(_here / "reservoir"))

import reservoir as _R

# Plain cylinder radius — kept simple for this iteration.
support_radius = 6.0

# +X−Y reservoir corner (insert boss position 2) and the reservoir's
# exterior V-floor underside height there — the height the corner needs to
# rest at. The +X−Y corner is chosen for this first iteration because it is
# clear of far-+X-wall features; the +X+Y corner overlaps both the reed
# cable channel (which runs the +Y half of the far-+X wall) and the
# reservoir-line port hole (y≈62.5), so a support there gets sliced.
_cx, _cy = _R.insert_positions_for_side_plus_1[1]
_floor_underside_z = _R.floor_trough_z - _R.reservoir_wall_thickness
_top_z = _floor_underside_z + _R.floor_slope_rate * (abs(_cy) - _R.floor_trough_half_width_y)


def build_reservoir_supports():
    """A single cylinder from the bag-pocket floor (z=0, fusing with the
    outer-shell floor) up to the reservoir-corner underside height, at the
    +X+Y corner."""
    return _R._z_cylinder((_cx, _cy), (0.0, _top_z), 2 * support_radius).unwrap()
