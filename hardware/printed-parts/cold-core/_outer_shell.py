"""Outer rectangular cup (floor + four perimeter walls) with 6 cylindrical
corner/mid-side bosses and their heat-set insert pockets. Exterior corners
rounded; each corner boss seated in the corner with its ⌀ tangent to the
exterior wall arc, two short webs filling to the flanking flat walls — the
cylinder + corner-fill teardrop idiom of the reservoir pocket-corner
supports."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    outer_shell_wall,
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


def cavity_plan(z0, z1, wall=None):
    """The cup's cavity in plan between two heights — the footprint inset by `wall`, on the
    concentric inner round a shell of that thickness leaves."""
    w = outer_shell_wall if wall is None else wall
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z0)
        .rect(outer_shell_x_length - 2 * w, outer_shell_y_length - 2 * w)
        .extrude(z1 - z0)
        .edges("|Z")
        .fillet(corner_round_radius - w)
    )


#: How much of a shelled cup's floor is the show skin's stock rather than the floor's own.
floor_skin_stock = outer_shell_wall - wall_and_floor_thickness


def take_skin_off_the_floor(cup, z0, z1):
    """`cup`, with the show skin's stock given back on the one face that is not show face —
    `z0`..`z1` being the `floor_skin_stock`-thick slab of cavity the shell left behind.

    A SHELL THICKENS EVERY FACE IT LEAVES, and a cup's closed end is one of them. But that end
    lies FLAT: it carries no flutes, so it has no reason to stand a groove's depth deeper, and
    it cannot afford to either. Every height in the core is measured off the shell floor's top
    face (`bag_pocket_floor_top_z`, `front_face_port_z`, the support ring's own seat) and
    `foam_cap_height` is a pour depth plus one floor, so a floor that moved would carry the
    whole stack with it. The four standing walls keep their own section; only this is given
    back."""
    return cup.cut(cavity_plan(z0, z1))


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
        # THE WALL IS ONE FLUTE DEEPER THAN THE STRUCTURE NEEDS (`outer_shell_wall`), and the
        # depth is found on the inside. The footprint this is shelled out of is untouched, so
        # the groove floor lands on the surface the cabinet was measured against.
        .shell(-outer_shell_wall)
    )
    shell = take_skin_off_the_floor(shell, wall_and_floor_thickness, outer_shell_wall)
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
