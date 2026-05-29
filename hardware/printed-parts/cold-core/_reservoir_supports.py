"""Reservoir corner supports — teardrop posts at the far-+X pocket corners.

Each support is a vertical post rising from the bag-pocket floor (z=0,
fusing with the outer-shell floor) up to the reservoir's exterior V-floor
underside at a far-+X pocket corner. The post is a cylinder sized to the
bag-pocket inner-corner fillet (radius bag_pocket_corner_inner_radius),
seated on the pocket corner's fillet center so its arc is coincident with
the rounded corner and tangent to both pocket inner faces, then webbed to
the two flanking pocket walls by filling the two square-corner regions
beside the pocket corner (the "teardrop"). The diagonal region faces open
pocket interior and is left clear.

Built for the +X pocket: both far-+X corners (±Y) and the centerward −Y
corner. The centerward wall is a curved tank-wrapping arc with no fillet to
nest, so that post seats under the reservoir's curve-corner and webs only to
the flat ±Y wall (its curved side faces the open cavity). The −X-pocket
mirror, the centerward +Y corner, and the 45° print cut / sloped top to
match the floor are still pending."""

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

# Far-+X corner X, shared by both ±Y corners: the fillet center is
# support_radius in from the +X inner face.
_cx = _I.bag_pocket_far_inner_x - support_radius


def _corner_teardrop(y_sign):
    """Teardrop post at the far-+X × (y_sign·Y) pocket corner: the corner
    cylinder plus the two webs filling the square-corner regions against the
    +X wall and the ±Y wall, rising to the reservoir floor underside. The
    cylinder is tangent to both pocket inner faces; the pocket corner itself
    is filled by the wall fillet and the diagonal square corner is left
    open."""
    cy = y_sign * (_I.bag_pocket_y_inner_max - support_radius)
    floor_underside_z = _R.floor_trough_z - _R.reservoir_wall_thickness
    top_z = floor_underside_z + _R.floor_slope_rate * (abs(cy) - _R.floor_trough_half_width_y)

    post = _R._z_cylinder((_cx, cy), (0.0, top_z), 2 * support_radius).unwrap()
    # Web against the +X wall (right edge at the +X inner face), below the
    # pocket corner.
    post = post.union(
        _I.make_box((_cx, _cx + support_radius), (cy, cy - y_sign * support_radius), (0.0, top_z))
    )
    # Web against the ±Y wall (outer edge at the ±Y inner face), inboard of
    # the pocket corner.
    post = post.union(
        _I.make_box((_cx - support_radius, _cx), (cy, cy + y_sign * support_radius), (0.0, top_z))
    )
    return post


def _centerward_teardrop(y_sign):
    """Post under the reservoir's centerward (curve × y_sign·Y) corner.

    The centerward pocket wall is a curved tank-wrapping arc — there is no
    filleted corner to nest a cylinder into. So the post is seated under the
    reservoir's curve-corner boss (where the reservoir actually bears down),
    tangent to the flat ±Y wall, and webbed to that wall on the +X side —
    toward the far wall, clear of the curve. The cylinder's curved-wall side
    faces the open cavity."""
    # insert_positions index 3 = curve × +Y, index 4 = curve × −Y.
    cx, cy = _R.insert_positions_for_side_plus_1[3 if y_sign > 0 else 4]
    floor_underside_z = _R.floor_trough_z - _R.reservoir_wall_thickness
    top_z = floor_underside_z + _R.floor_slope_rate * (abs(cy) - _R.floor_trough_half_width_y)

    post = _R._z_cylinder((cx, cy), (0.0, top_z), 2 * support_radius).unwrap()
    # Web to the ±Y wall on the +X side (outer edge at the ±Y inner face).
    post = post.union(
        _I.make_box((cx, cx + support_radius), (cy, cy + y_sign * support_radius), (0.0, top_z))
    )
    return post


def build_reservoir_supports():
    """Posts at both far-+X pocket corners (±Y) plus the centerward −Y
    corner."""
    support = _corner_teardrop(-1).union(_corner_teardrop(+1))
    return support.union(_centerward_teardrop(-1))
