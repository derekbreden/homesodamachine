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

import cadquery as cq
from world_workplane import xy_plane_z_up
from _cold_core_interface import (
    outer_shell_x_length,
    outer_shell_y_length,
    foam_shell_outer_height,
    bag_pocket_outermost_x,
    pocket_centerward_arc_outer_radius,
    wall_and_floor_thickness,
    bag_pocket_floor_top_z,
    make_box,
)
from _reservoir_pocket_walls import build_plus_x_cavity

# Rib cross-section + reach. Thickness ~ one nozzle-pair of wall; height
# covers the low band where the floor corner curls; end overlap buries each
# end into the pocket wall and the corner boss so the rib fuses to both.
gusset_thickness = 2.4
gusset_height = 40.0
gusset_end_overlap = 2.5

# Endpoints in the +X/+Y quadrant (signed per corner below):
#   pocket far-outer corner — where the pocket's far-±X wall meets its ±Y wall
pocket_corner_xy = (bag_pocket_outermost_x, pocket_centerward_arc_outer_radius)
#   outer-shell inner corner — inside the solid 8×8 corner boss
shell_corner_xy = (
    outer_shell_x_length / 2 - wall_and_floor_thickness,
    outer_shell_y_length / 2 - wall_and_floor_thickness,
)


def _corner_gusset(x_sign, y_sign):
    """One rib, from the (x_sign, y_sign) pocket far-corner to the matching
    outer-shell corner. Built axis-aligned at the origin, rotated to the
    corner's diagonal, then translated to the diagonal's midpoint — so the
    same construction serves all four corners regardless of diagonal sense."""
    px, py = x_sign * pocket_corner_xy[0], y_sign * pocket_corner_xy[1]
    sx, sy = x_sign * shell_corner_xy[0], y_sign * shell_corner_xy[1]
    midpoint = ((px + sx) / 2, (py + sy) / 2)
    length = math.hypot(sx - px, sy - py) + 2 * gusset_end_overlap
    angle = math.degrees(math.atan2(sy - py, sx - px))
    z_range = (bag_pocket_floor_top_z, bag_pocket_floor_top_z + gusset_height)
    rib = make_box((-length / 2, length / 2), (-gusset_thickness / 2, gusset_thickness / 2), z_range)
    return rib.rotate((0, 0, 0), (0, 0, 1), angle).translate((midpoint[0], midpoint[1], 0))


def _shell_interior_footprint():
    """The outer shell's interior floor footprint, extruded full height —
    the volume the ribs must stay within. Clipping to it trims the
    diagonal rib's splayed corner flush with the outer wall's inner face
    so nothing pokes past the envelope."""
    interior_x = outer_shell_x_length - 2 * wall_and_floor_thickness
    interior_y = outer_shell_y_length - 2 * wall_and_floor_thickness
    return make_box(
        (-interior_x / 2, interior_x / 2),
        (-interior_y / 2, interior_y / 2),
        (bag_pocket_floor_top_z, foam_shell_outer_height),
    )


def build_corner_gussets():
    """All four corner ribs (both pockets, both ±Y far-corners each),
    clipped to the shell interior (no outward poke) and cut by both pocket
    cavities (never intrude on the reservoir space)."""
    gussets = _corner_gusset(+1, +1)
    for x_sign, y_sign in ((+1, -1), (-1, +1), (-1, -1)):
        gussets = gussets.union(_corner_gusset(x_sign, y_sign))
    plus_x_cavity = build_plus_x_cavity().unwrap()
    return (
        gussets
        .intersect(_shell_interior_footprint())
        .cut(plus_x_cavity)
        .cut(plus_x_cavity.mirror("YZ"))
    )
