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


def _rounded_footprint(height):
    """The outer footprint with rounded corners, extruded to `height` — the
    mask the boss webs are trimmed to, so each web is flush with the rounded
    wall and nothing pokes past the envelope. Shared at every part's height."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_round_radius)
    )


def build_attachment_bosses(height):
    """The ⌀screw_boss_size cylindrical boss + teardrop corner-fill webs at
    each of the 6 attachment positions, extruded to `height` and trimmed
    flush to the rounded footprint. Shared by the outer shell AND the
    foam-cap stack so every mating part's boss cross-section is identical —
    a single source of truth for the boss shape.

    The webs are the cylinder + corner-fill idiom of the reservoir
    pocket-corner supports: each is one boss radius wide off the boss center
    (tangent to the boss circle) and runs out past the wall, so the mask
    trims it flush and the thin crescent where the circle pulls off the flat
    wall is filled — the boss blends into the wall instead of meeting it on a
    knife-edge seam. A corner boss sits against two walls (a far ±X and an
    end ±Y wall) and gets a web toward each, diagonal-inboard quadrant left
    open for foam; a mid-side boss sits against one wall and gets a single
    web toward it (a D: flat to the wall, round toward the foam)."""
    r = screw_boss_size / 2
    corner_x = outer_shell_x_length / 2
    corner_y = outer_shell_y_length / 2
    corner_positions = foam_cap_attachment_xy_positions[:4]
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .circle(r)
        .extrude(height)
    )
    for cx, cy in foam_cap_attachment_xy_positions:
        x_sign = 1 if cx > 0 else -1
        y_sign = 1 if cy > 0 else -1
        # The web toward this boss's ±Y wall — every boss sits against one.
        boss_webs = make_box((cx - r, cx + r), (cy, y_sign * corner_y), (0.0, height))
        # Corner bosses also sit against a far ±X wall — add the web to it.
        if (cx, cy) in corner_positions:
            boss_webs = boss_webs.union(
                make_box((cx, x_sign * corner_x), (cy - r, cy + r), (0.0, height))
            )
        bosses = bosses.union(boss_webs)
    return bosses.intersect(_rounded_footprint(height).unwrap())


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
    # NB: the heat-set insert pockets are NOT cut here — they are cut at the
    # full-shell level (cut_insert_pockets, applied after every union) so
    # that nothing unioned later (the corner gussets fuse into these bosses)
    # can back-fill an insert pocket.
    return shell.union(build_attachment_bosses(foam_shell_outer_height)).unwrap()


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
