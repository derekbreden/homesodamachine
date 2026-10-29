"""Outer rectangular cup (floor + four perimeter walls) with a cylindrical boss at
every `attachment_stations` station and their heat-set insert pockets. Exterior
corners rounded; each corner boss seated in the corner with its ⌀ tangent to the
exterior wall arc, two short webs filling to the flanking flat walls — the
cylinder + corner-fill teardrop idiom of the reservoir pocket-corner supports."""

import cadquery as cq
from world_workplane import WorldWorkplane, xy_plane_z_up, yz_plane_x_up
import fits
from _cold_core_interface import (
    attachment_stations,
    casing_foil_land,
    seam_channel_depth,
    seam_channel_width,
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


def trim_cup_floor(cup, z0, z1, wall=None):
    """Remove surplus closed-end stock while retaining the cup's vertical walls."""
    return cup.cut(cavity_plan(z0, z1, wall=wall))


def build_attachment_bosses(height, oversize=0.0):
    """The ⌀screw_boss_size cylindrical boss + teardrop corner-fill webs at each station in
    `attachment_stations`, extruded to `height` and trimmed flush to the rounded footprint.
    Shared by the outer shell and the foam-cap stack; lid pads and their
    receiving pockets apply their own growth to this base section.

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
    round toward the foam).

    WHICH WALL A BOSS LEANS ON IS THE STATION'S OWN, read off `attachment_stations` and never
    off the sign of its coordinates. A station centred on a ±X wall stands at y = 0, where
    that sign is neither — and a web run to a wall picked by it would sweep the whole half of
    the shell between the boss and that wall, which unions in silently and reads only as a
    part that came out heavy."""
    r = screw_boss_size / 2 + oversize
    corner_x = outer_shell_x_length / 2
    corner_y = outer_shell_y_length / 2
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(attachment_xy_positions)
        .circle(r)
        .extrude(height)
    )
    for (cx, cy), wall in attachment_stations:
        boss_webs = None
        # The web toward this boss's ±Y wall — every boss but a ±X wall's own sits against one.
        if wall in ("corner", "y"):
            y_sign = 1 if cy > 0 else -1
            boss_webs = make_box((cx - r, cx + r), (cy, y_sign * corner_y), (0.0, height))
        # A corner boss also sits against a far ±X wall, and a ±X station sits against one alone.
        if wall in ("corner", "x"):
            x_sign = 1 if cx > 0 else -1
            web = make_box((cx, x_sign * corner_x), (cy - r, cy + r), (0.0, height))
            boss_webs = web if boss_webs is None else boss_webs.union(web)
        bosses = bosses.union(boss_webs)
    return bosses.intersect(_rounded_footprint(height).unwrap())


def _ramped_slab(half_width, face_y, depth, z0, z1):
    """A slab |x| <= `half_width` reaching `depth` toward -Y off the plane y = `face_y`, from
    z0 to z1. Its depth runs out at 45 degrees at both ends, so its upper end is no ledge and
    its lower end grows out of the face; the back runs 1 mm past the plane for the boolean."""
    over = 1.0
    return (
        WorldWorkplane(yz_plane_x_up)
        .workplane(offset=-half_width)
        .polyline([(face_y + over, z0 - over), (face_y - depth, z0 + depth),
                   (face_y - depth, z1 - depth), (face_y + over, z1 + over)])
        .close()
        .extrude(2.0 * half_width)
        .unwrap()
    )


def fold_seam_channel(shell):
    """The seam channel down the +Y flank's centre line, between the two foil lands.

    The flank gives up the channel and the wall's inner face takes the same depth back over
    the channel's width plus one section either side, so every horizontal section through the
    fold is still `outer_shell_wall` thick. The fold reaches one depth past each end of the
    channel, where it runs out on the same 45 degrees."""
    face_y = outer_shell_y_length / 2.0
    z0, z1 = casing_foil_land, foam_shell_outer_height - casing_foil_land
    d = seam_channel_depth
    channel = _ramped_slab(seam_channel_width / 2.0, face_y, d, z0, z1)
    fold = _ramped_slab(seam_channel_width / 2.0 + outer_shell_wall, face_y - outer_shell_wall,
                        d, z0 - d, z1 + d)
    return shell.cut(channel).union(fold)


def build_outer_shell():
    """Continuous standing walls, fixed floor, cap attachment bosses and the seam channel."""
    h = foam_shell_outer_height
    shell = _rounded_footprint(h).cut(cavity_plan(wall_and_floor_thickness, h))

    return fold_seam_channel(shell.union(build_attachment_bosses(h))).unwrap()


def cut_insert_pockets(foam_shell):
    """Heat-set insert pockets in every boss on both faces — each
    cap's M3 SHCS threads into an insert pressed from its own face, so every
    boss carries a pocket at z=0 and another at z=foam_shell_outer_height."""
    def insert_pockets_at(z_floor, depth=insert_pocket_depth):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=z_floor)
            .pushPoints(attachment_xy_positions)
            .circle(insert_pocket_radius)
            .extrude(depth)
        )
    # The shell prints floor-down: only the bottom blind ends bridge over an
    # opening. Their extra depth budgets the retained bridge skin without moving
    # the insert mouths or the upper, upward-opening pockets.
    bottom_pockets = insert_pockets_at(0, insert_pocket_depth + fits.supported_surface).unwrap()
    top_pockets = insert_pockets_at(foam_shell_outer_height - insert_pocket_depth).unwrap()
    return foam_shell.cut(bottom_pockets).cut(top_pockets)
