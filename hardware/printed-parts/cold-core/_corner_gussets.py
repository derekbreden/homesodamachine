"""Corner anti-warp gussets — four short diagonal ribs, one per pocket
far-corner, bridging the foam gap to the outer-shell corner.

The outer shell's flat floor is wide (283 × 181 mm) and its four corners
are the classic warp-initiation site: as the part cools they peel off the
plate over the first few cm of height. Each corner is otherwise a nearly
free cantilever — the outer wall ties to the rest of the shell only
through the 2 mm floor. A short diagonal rib triangulates that free corner
to the stiff, closed reservoir pocket, stiffening the floor diaphragm in
the band where the curl happens so the corner can't lift.

The rib lives entirely in the corner foam-pour zone (the ~16 mm gap
between each pocket's outboard walls and the outer shell), runs from the
pocket's far-outer corner to the outer-shell corner boss, sits on top of
the floor, and is left open at the top — the top-down foam pour falls in
around it, so it traps no air. It is short (warp settles low; a full-height
beam would be wasted above ~40 mm) and thin (a 1 % volume add)."""

import math

from _cold_core_interface import (
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    bag_pocket_outermost_x,
    pocket_centerward_arc_outer_radius,
    wall_and_floor_thickness,
    bag_pocket_corner_inner_radius,
    bag_pocket_floor_top_z,
    foam_cap_attachment_xy_positions,
    make_box,
)
from _reservoir_pocket_walls import build_plus_x_cavity

# Rib cross-section + reach. Thickness ~ one nozzle-pair of wall; height
# covers the low band where the floor corner curls (warp settles low, so a
# full-height beam would be wasted). The ends are extended past both
# anchors and trimmed by the real solids, so the rib reliably lands on the
# pocket outer corner and the relocated shell corner boss.
gusset_thickness = 2.4
gusset_height = 40.0
gusset_end_overlap = 3.0

# Endpoints in the +X/+Y quadrant (signed per corner below):
#   pocket far-outer corner — the convex outside corner where the pocket's
#   far-±X wall meets its ±Y wall (outboard of the cavity fillet).
pocket_corner_xy = (bag_pocket_outermost_x, pocket_centerward_arc_outer_radius)
#   outer-shell corner boss — the +X/+Y corner boss center (first entry of
#   the shared attachment list); the rib fuses into the boss + its teardrop
#   webs. Taken from the shared source so it tracks the boss automatically.
shell_corner_xy = tuple(abs(c) for c in foam_cap_attachment_xy_positions[0])


def _corner_gusset(x_sign, y_sign):
    """One rib spanning the (x_sign, y_sign) pocket outer corner to the
    matching shell corner boss. Built axis-aligned, rotated to the corner
    diagonal, translated to the diagonal midpoint; ends extended past both
    anchors by gusset_end_overlap so the rib buries into the pocket wall at
    one end and the boss at the other (real solids trim the overlap)."""
    px, py = x_sign * pocket_corner_xy[0], y_sign * pocket_corner_xy[1]
    sx, sy = x_sign * shell_corner_xy[0], y_sign * shell_corner_xy[1]
    midpoint = ((px + sx) / 2, (py + sy) / 2)
    length = math.hypot(sx - px, sy - py) + 2 * gusset_end_overlap
    angle = math.degrees(math.atan2(sy - py, sx - px))
    z_range = (bag_pocket_floor_top_z, bag_pocket_floor_top_z + gusset_height)
    rib = make_box((-length / 2, length / 2), (-gusset_thickness / 2, gusset_thickness / 2), z_range)
    return rib.rotate((0, 0, 0), (0, 0, 1), angle).translate((midpoint[0], midpoint[1], 0))


def _rounded_interior_footprint():
    """The shell's rounded interior floor footprint, full height — the
    volume the ribs must stay within. The pocket-side overlap is removed
    instead by the cavity cut below; this only trims the shell-side end to
    the rounded inner wall so nothing pokes past the envelope."""
    interior_x = outer_shell_x_length - 2 * wall_and_floor_thickness
    interior_y = outer_shell_y_length - 2 * wall_and_floor_thickness
    inner_round = corner_round_radius - wall_and_floor_thickness
    return (
        make_box(
            (-interior_x / 2, interior_x / 2),
            (-interior_y / 2, interior_y / 2),
            (bag_pocket_floor_top_z, bag_pocket_floor_top_z + gusset_height),
        )
        .edges("|Z")
        .fillet(inner_round)
    )


def build_corner_gussets():
    """All four corner ribs (both pockets, both ±Y far-corners each),
    clipped to the rounded shell interior (no outward poke). The pocket-side
    end is trimmed by the pocket cavity so the rib butts the pocket outer
    wall rather than intruding into the reservoir space."""
    gussets = _corner_gusset(+1, +1)
    for x_sign, y_sign in ((+1, -1), (-1, +1), (-1, -1)):
        gussets = gussets.union(_corner_gusset(x_sign, y_sign))
    cavity_z = bag_pocket_floor_top_z + gusset_height
    plus_x_cavity = build_plus_x_cavity(cavity_z).unwrap()
    return (
        gussets
        .intersect(_rounded_interior_footprint())
        .cut(plus_x_cavity)
        .cut(plus_x_cavity.mirror("YZ"))
    )
