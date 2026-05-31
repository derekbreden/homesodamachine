"""Outer rectangular cup (floor + four perimeter walls) with the
6 cylindrical corner/mid-side bosses and their heat-set insert pockets.
The exterior corners are rounded; each corner boss is seated deep in the
corner — its ⌀ tangent to the EXTERIOR wall arc, so the boss fuses into the
outer skin — with two short webs filling to the flanking flat walls, the
cylinder + corner-fill teardrop idiom the reservoir pocket-corner supports
use."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
    foam_cap_attachment_xy_positions,
    screw_boss_size,
    corner_round_radius,
    insert_pocket_radius,
    insert_pocket_depth,
    make_box,
)


def _rounded_outer_footprint():
    """The shell's outer footprint with rounded corners, full height — the
    mask each corner web is intersected with, so the web is trimmed to the
    rounded wall's outer face and never pokes past the envelope."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_shell_outer_height)
        .edges("|Z")
        .fillet(corner_round_radius)
    )


def _corner_webs():
    """The teardrop's two corner-fill squares per corner boss, exactly as
    the reservoir pocket-corner supports do it: a boss-radius square is
    tangent to the boss circle in each quadrant; the two squares on the
    corner side (toward the +/-X far wall and toward the +/-Y end wall) are
    kept, the diagonal-facing square is left open for foam. Each square
    spans one boss radius in x and one in y from the boss center, toward the
    corner. Trimmed to the rounded wall by the footprint mask; the insert
    pockets are cut later at the full-shell level (cut_insert_pockets)."""
    r = screw_boss_size / 2
    webs = None
    for cx, cy in foam_cap_attachment_xy_positions[:4]:  # first 4 entries are the corners
        x_sign = 1 if cx > 0 else -1
        y_sign = 1 if cy > 0 else -1
        # Square reaching toward the far X wall (corner-ward in X, centered in Y).
        toward_x_wall = make_box(
            (cx, cx + x_sign * r),
            (cy - r, cy + r),
            (0.0, foam_shell_outer_height),
        )
        # Square reaching toward the end Y wall (corner-ward in Y, centered in X).
        toward_y_wall = make_box(
            (cx - r, cx + r),
            (cy, cy + y_sign * r),
            (0.0, foam_shell_outer_height),
        )
        pair = toward_x_wall.union(toward_y_wall)
        webs = pair if webs is None else webs.union(pair)
    return webs.intersect(_rounded_outer_footprint().unwrap())


def build_outer_shell():
    # Round the four vertical corner edges before shelling, so the shell
    # offsets uniformly inward and both wall faces come out as concentric
    # arcs — a rounded corner that wraps each (inward-nested) corner boss.
    shell = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_shell_outer_height)
        .edges("|Z")
        .fillet(corner_round_radius)
        .faces(">Z")
        .shell(-wall_and_floor_thickness)
    )
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .circle(screw_boss_size / 2)
        .extrude(foam_shell_outer_height)
    )
    # NB: the heat-set insert pockets are NOT cut here — they are cut at the
    # full-shell level (cut_insert_pockets, applied after every union) so
    # that nothing unioned later (the corner gussets fuse into these bosses)
    # can back-fill an insert pocket.
    return shell.union(bosses).union(_corner_webs()).unwrap()


def cut_insert_pockets(foam_shell):
    """Cut the heat-set insert pockets into the corner/mid bosses on both
    faces — each cap's M3 SHCS threads into an insert pressed from its own
    face, so every boss carries a pocket at z=0 and another at
    z=foam_shell_outer_height. Applied at the full-shell level, after all
    unions, so a later union (e.g. the corner gussets fusing into a boss)
    can never plug a pocket."""
    def insert_pockets_at(z_floor):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=z_floor)
            .pushPoints(foam_cap_attachment_xy_positions)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth)
        )
    bottom_pockets = insert_pockets_at(0).unwrap()
    top_pockets = insert_pockets_at(foam_shell_outer_height - insert_pocket_depth).unwrap()
    return foam_shell.cut(bottom_pockets).cut(top_pockets)
