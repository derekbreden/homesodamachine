"""Reservoir corner supports — four 45°-cut cylinder stubs per pocket
that hold each rigid reservoir up by its four floor corners.

The reservoir's raised V floor (see ../reservoir/coating.md) leaves open
air below it in the bag-pocket cavity. These supports span that air at
the four corners: a cylinder stub fused to the pocket walls, its top
matching the reservoir's exterior V underside at the corner so the corner
seats on it, its free (cavity-side) underside sliced by a 45° plane
anchored at the wall — the exact technique the reservoir uses for its
heat-set insert bosses (../reservoir/reservoir.py, build_reservoir_body),
so the otherwise-unprintable overhang self-supports when the foam shell
prints floor-down. Minus the insert pocket: these are solid and
load-bearing.

The +X pocket's supports are built explicitly from the reservoir's
side=+1 corner geometry; the −X pocket's are the YZ mirror — matching how
build_reservoir_pocket_walls mirrors the pocket itself."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
# reservoir.py lives in the sibling reservoir/ dir. Import it so the
# support positions + heights track the reservoir's own corner bosses and
# V-floor geometry with no duplicated constants (it self-configures its
# sys.path at import and runs no side effects outside __main__).
sys.path.insert(0, str(_here / "reservoir"))

import reservoir as _R
from _cold_core_interface import bag_pocket_corner_inner_radius

# Cylinder radius. One wall-thickness past the pocket corner-fillet radius
# so the stub bites into the pocket walls (fuses solidly) instead of just
# touching them, at every corner.
support_radius = bag_pocket_corner_inner_radius + 1.0

# How deep the stub reaches at the wall (its 45°-cut low point), below the
# reservoir-underside height at the corner. Open air continues below that
# down to the bag-pocket floor — the stub does not reach the floor, same as
# the reservoir bosses don't reach the reservoir floor.
support_wall_drop = 8.0

# Reservoir exterior V underside, as a function of |y| (the dry face of the
# 4 mm V floor): flat at floor_underside_z for |y| ≤ trough half-width,
# sloping up at floor_slope_rate beyond. The support top is cut to this
# plane so the reservoir corner seats flush on it.
_floor_underside_z = _R.floor_trough_z - _R.reservoir_wall_thickness


def _underside_z(y_abs):
    return _floor_underside_z + _R.floor_slope_rate * max(
        0.0, y_abs - _R.floor_trough_half_width_y
    )


# The four corner positions (reservoir insert positions 1, 2, 4, 5 — the
# +X×±Y corners and the centerward-arc×±Y corners; positions 3 and 6 are
# wall midpoints, not corners) and their boss cut directions, taken
# straight from the reservoir so a support sits under each corner boss.
_CORNER_POSITIONS = [
    _R.insert_positions_for_side_plus_1[i] for i in (0, 1, 3, 4)
]


def _build_one_support(cx, cy):
    """One corner support for the side=+1 pocket, centered at the
    reservoir corner-boss (cx, cy)."""
    pivot_x, pivot_y, dir_x, dir_y = _R.body_boss_cut_info_for_side_plus_1[(cx, cy)]
    sign_y = 1.0 if cy >= 0 else -1.0

    # Top of the stub at the corner center, and the 45°-cut low point one
    # support_wall_drop below it.
    top_center_z = _underside_z(abs(cy))
    boss_bottom_z = top_center_z - support_wall_drop

    # Cylinder built past both cut planes (extra below the 45° low point,
    # and up past the sloped top), then trimmed by the two planes.
    cyl = _R._z_cylinder(
        (cx, cy),
        (boss_bottom_z - 5.0, top_center_z + _R.floor_slope_rise + 2.0),
        2 * support_radius,
    )

    # Top: cut away everything ABOVE the reservoir's exterior V underside
    # plane (z = floor_underside_z + rate·(|y|−half)), so the stub top is
    # coincident with the underside and the corner seats flush. Anchored on
    # the corner's ±Y half; normal (0, −sign·rate, +1), keep below.
    top_plane = cq.Plane(
        origin=(0, sign_y * _R.floor_trough_half_width_y, _floor_underside_z),
        xDir=(1, 0, 0),
        normal=(0, -sign_y * _R.floor_slope_rate, 1),
    )
    cyl = cyl.cut(cq.Workplane(top_plane).rect(2000, 2000).extrude(2000))

    # Bottom: the reservoir boss's 45° cut — plane through the wall pivot at
    # boss_bottom_z, normal (dir_x, dir_y, 1), keep the up-and-toward-wall
    # side, slice the cavity-side underside into a self-supporting 45° ramp.
    cut_plane = cq.Plane(
        origin=(pivot_x, pivot_y, boss_bottom_z),
        xDir=(-dir_y, dir_x, 0),
        normal=(dir_x, dir_y, 1),
    )
    cyl = cyl.cut(cq.Workplane(cut_plane).rect(500, 500).extrude(-500))

    return cyl


def build_reservoir_supports():
    """Four corner supports for each of the two pockets. The +X pocket's
    are built from the side=+1 corner geometry; the −X pocket's are the YZ
    mirror."""
    plus_x = _build_one_support(*_CORNER_POSITIONS[0])
    for pos in _CORNER_POSITIONS[1:]:
        plus_x = plus_x.union(_build_one_support(*pos))
    return plus_x.union(plus_x.mirror("YZ")).unwrap()
