"""Reservoir corner support — ITERATION 1: a cylinder webbed to two walls.

One vertical cylinder rising from the bag-pocket floor up to the height of
the reservoir's floor underside at one corner (the +X−Y corner), so we can
get placement + height right before adding anything else — no 45° print
cut, no sloped top to match the floor, no mirror, no other three corners.
Built for the +X pocket only.

The cylinder is sized and centered to the BAG-POCKET inner corner (radius
bag_pocket_corner_inner_radius, centered on the pocket corner's fillet
center), so its arc is coincident with the pocket's rounded inner corner
and tangent to both pocket inner faces — the support abuts the pocket wall
rather than floating the reservoir_clearance gap inside it.

Of the four square-corner regions between the cylinder and a square tangent
to it, the +X−Y region is already solid (the pocket corner). Two more are
filled in here — the +X+Y region (against the +X wall) and the −X−Y region
(against the −Y wall) — webbing the post to both flanking pocket walls over
its full height. The diagonal −X+Y region faces open pocket interior and is
left clear."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
# reservoir.py is in the sibling reservoir/ dir; import it for the
# floor-underside height. _cold_core_interface owns the pocket geometry.
sys.path.insert(0, str(_here / "reservoir"))

import reservoir as _R
import _cold_core_interface as _I

# Cylinder radius = the pocket inner-corner fillet radius, so the cylinder
# arc coincides with the pocket's rounded corner.
support_radius = _I.bag_pocket_corner_inner_radius

# +X−Y bag-pocket inner corner: the fillet center is support_radius in from
# the +X inner face and from the −Y inner face. Sitting the cylinder there
# at support_radius makes its arc coincident with the pocket corner and
# tangent to both pocket inner faces. The +X−Y corner is chosen for this
# first iteration because it is clear of far-+X-wall features; the +X+Y
# corner overlaps both the reed cable channel (which runs the +Y half of
# the far-+X wall) and the reservoir-line port hole (y≈62.5), so a support
# there gets sliced.
_cx = _I.bag_pocket_far_inner_x - support_radius
_cy = -(_I.bag_pocket_y_inner_max - support_radius)

# Reservoir exterior V-floor underside height at this corner — the height
# the corner needs to rest at.
_floor_underside_z = _R.floor_trough_z - _R.reservoir_wall_thickness
_top_z = _floor_underside_z + _R.floor_slope_rate * (abs(_cy) - _R.floor_trough_half_width_y)


def build_reservoir_supports():
    """A cylinder from the bag-pocket floor (z=0, fusing with the
    outer-shell floor) up to the reservoir-corner underside height at the
    +X−Y pocket corner, webbed to the +X and −Y pocket walls by filling
    the +X+Y and −X−Y square-corner regions over the same height."""
    support = _R._z_cylinder((_cx, _cy), (0.0, _top_z), 2 * support_radius).unwrap()
    # +X+Y corner web — against the +X wall (right edge at the +X inner face).
    support = support.union(
        _I.make_box((_cx, _cx + support_radius), (_cy, _cy + support_radius), (0.0, _top_z))
    )
    # −X−Y corner web — against the −Y wall (bottom edge at the −Y inner face).
    support = support.union(
        _I.make_box((_cx - support_radius, _cx), (_cy - support_radius, _cy), (0.0, _top_z))
    )
    return support
