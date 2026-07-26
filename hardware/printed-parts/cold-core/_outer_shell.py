"""Outer rectangular cup (floor + four perimeter walls) with 6 cylindrical
corner/mid-side bosses and their heat-set insert pockets. Exterior corners
rounded; each corner boss seated in the corner with its ⌀ tangent to the
exterior wall arc, two short webs filling to the flanking flat walls — the
cylinder + corner-fill teardrop idiom of the reservoir pocket-corner
supports."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
    attachment_xy_positions,
    screw_boss_size,
    corner_round_radius,
    insert_pocket_radius,
    insert_pocket_depth,
    make_box,
)


def _rounded_footprint(height):
    """The outer footprint with rounded corners, extruded to `height`."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_round_radius)
    )


def build_attachment_bosses(height, oversize=0.0):
    """The ⌀screw_boss_size cylindrical boss + teardrop corner-fill webs at
    each of the 6 attachment positions, extruded to `height` and trimmed
    flush to the rounded footprint. Shared by the outer shell and the
    foam-cap stack — every mating part's boss cross-section is identical.

    `oversize` grows the section in the plane by that much on every free side.
    A cap's mouth-end relief is the lid pad it receives, one slip oversize; the
    footprint trim is common to both, so the two stay flush where they reach
    the outer skin and clear each other everywhere they do not.

    The webs are the cylinder + corner-fill idiom of the reservoir
    pocket-corner supports: each is one boss radius wide off the boss center
    (tangent to the boss circle) and runs out past the wall, filling the
    crescent where the circle pulls off the flat wall. A corner boss sits
    against two walls (a far ±X and an end ±Y wall) and gets a web toward
    each, diagonal-inboard quadrant left open for foam; a mid-side boss sits
    against one wall and gets a single web toward it (a D: flat to the wall,
    round toward the foam)."""
    r = screw_boss_size / 2 + oversize
    corner_x = outer_shell_x_length / 2
    corner_y = outer_shell_y_length / 2
    corner_positions = attachment_xy_positions[:4]
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(attachment_xy_positions)
        .circle(r)
        .extrude(height)
    )
    for cx, cy in attachment_xy_positions:
        x_sign = 1 if cx > 0 else -1
        y_sign = 1 if cy > 0 else -1
        # The web toward this boss's ±Y wall — every boss sits against one.
        boss_webs = make_box((cx - r, cx + r), (cy, y_sign * corner_y), (0.0, height))
        # A corner boss also sits against a far ±X wall, so it gets a second web.
        if (cx, cy) in corner_positions:
            boss_webs = boss_webs.union(
                make_box((cx, x_sign * corner_x), (cy - r, cy + r), (0.0, height))
            )
        bosses = bosses.union(boss_webs)
    return bosses.intersect(_rounded_footprint(height).unwrap())


def build_outer_shell():
    # Rounded corners with both wall faces concentric arcs, each wrapping an
    # inward-nested corner boss.
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
    return shell.union(build_attachment_bosses(foam_shell_outer_height)).unwrap()


def cut_insert_pockets(foam_shell):
    """Heat-set insert pockets in the corner/mid bosses on both faces — each
    cap's M3 SHCS threads into an insert pressed from its own face, so every
    boss carries a pocket at z=0 and another at z=foam_shell_outer_height."""
    def insert_pockets_at(z_floor):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=z_floor)
            .pushPoints(attachment_xy_positions)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth)
        )
    bottom_pockets = insert_pockets_at(0).unwrap()
    top_pockets = insert_pockets_at(foam_shell_outer_height - insert_pocket_depth).unwrap()
    return foam_shell.cut(bottom_pockets).cut(top_pockets)
