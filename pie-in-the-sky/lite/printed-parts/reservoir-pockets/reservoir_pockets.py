"""Reservoir pockets — a rectangular box holding two collapsible 1 L
Platypus water bags hanging vertically, separated by a divider.

Two bag pockets sit front-to-back along the depth (Y) axis with a 2 mm
divider between them. Each pocket is sized to one 1 L Platypus bag —
285 mm tall, 150 mm wide, 70 mm deep when depth-restricted. Walls, floor,
ceiling, and divider are all 2 mm. The outer envelope is 154 mm wide
(X) × 146 mm deep (Y) × 289 mm tall (Z). The box is closed on top — the
ceiling stays.

Each pocket opens through its right (+X) wall as a doorway the full size of
the pocket side face — 70 mm deep (Y) × 285 mm tall (Z) — leaving the floor,
ceiling, front wall, divider, and back wall as a 2 mm frame. The opposite,
left (-X) wall carries one ⌀6.5 mm (~1/4") tubing exit hole per pocket,
centered in the pocket's depth (Y) and low in the wall — its bottom 6.5 mm
above the floor — for each bag's spout line. Transparent PETG.

Rod hang channel: one 1/8 in stainless rod runs front-to-back (along Y)
through both bags' centered top loops, passing through the front wall, the
divider, and the back wall. Each of those three walls carries a channel cut
into its face near the top — NOT through the ceiling: a flat entry slot open
at the +X (back / doorway) edge that the rod slides along, then the channel
curves down — rounding the corner — into a rounded cradle at center X that
holds the round rod. A bridge of wall material spans above the channel, so
the ceiling stays attached. The user threads the rod through both bag loops
and connects the spouts outside the box, slides the rod in from the +X back
through the three aligned slots (carrying the bags in with it), and at
center the rod rolls down into the cradle; the hanging bags' weight seats it
there and resists sliding back out. To remove, lift the rod up out of the
cradle and slide it back out the +X side.

World frame: Z+ up, Y- front (front face points in -Y), X left(-)/
right(+). The floor sits on Z=0, centered in X and Y."""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware"))
from _cadq_export import export_step

# Wall, floor, ceiling, and divider thickness.
wall_thickness = 2.0

# Outer shell extents (world coordinates, centered in X and Y, floor on Z=0).
outer_x_range = (-77, 77)
outer_y_range = (-73, 73)
outer_z_range = (0, 289)

# The two bag pockets, cut from the shell. Front pocket is in -Y, back in
# +Y; the 2 mm divider is the stock between them across Y=0.
front_pocket_x_range = (-75, 75)
front_pocket_y_range = (-71, -1)
front_pocket_z_range = (2, 287)

back_pocket_x_range = (-75, 75)
back_pocket_y_range = (1, 71)
back_pocket_z_range = (2, 287)

# Each pocket opens through the right (+X) wall as a doorway the full size of
# the pocket side face: 70 mm deep (Y) x 285 mm tall (Z). The cut spans the
# 2 mm wall over each pocket's Y/Z footprint, leaving the floor, ceiling,
# front wall, divider, and back wall as a frame.
doorway_wall_x_range = (75, 77)

# Tubing exit holes — one per pocket, through the LEFT (-X) wall (the
# no-doorway side), for each bag's spout line to leave the enclosure.
# Diameter matches the foam shell's project-wide port-hole standard
# (port_hole_radius = 3.25, ⌀6.5 ≈ 1/4"; see
# hardware/printed-parts/cold-core/_cold_core_interface.py). Each hole is
# centered in its pocket's depth (Y) and low in the wall: tube_hole_floor_gap
# leaves a band of solid wall between the 2 mm floor and the bottom of the
# hole, where a spout-down bag's line exits. tube_hole_wall_x is the mid-plane
# of the 2 mm left wall.
port_hole_radius = 3.25
tube_hole_floor_gap = 6.5  # solid wall between the floor top and the hole bottom
tube_hole_wall_x = (outer_x_range[0] + front_pocket_x_range[0]) / 2
tube_hole_z = front_pocket_z_range[0] + tube_hole_floor_gap + port_hole_radius
front_tube_hole_y = sum(front_pocket_y_range) / 2
back_tube_hole_y = sum(back_pocket_y_range) / 2

# --- Rod hang channel (slide in from the +X back, curve down to a rounded rest) ---
# A profile cut in the X-Z plane and swept along Y through the front wall, the
# divider, and the back wall (the empty pockets between them carry no
# material). In X-Z: a flat entry slot, open at the +X edge, that the rod
# rides in along; the channel then curves down over a rounded crest and ends
# in a rounded cradle at center X that holds the round rod. The profile top
# stays at z_top (below the ceiling), leaving a bridge of wall material above
# it (z_top .. 287) so the ceiling stays attached.
#
# A 1/8 in stainless rod carries two full 1 L bags easily: the divider acts as
# a midspan support, so each ~72 mm span sees ~10 N (~57 MPa bending; 304 SS
# yields ~215 MPa) and under 0.1 mm sag. Channel features are derived from
# rod_diameter, so a 1/4 in rod is a one-line change. Heights are placeholders
# pending the real bag loop / hung-bag height; they set how high the bag hangs.
rod_diameter = 3.175             # 1/8 in stainless rod
rod_radius = rod_diameter / 2.0

z_top = 283.0                    # profile top; bridge spans z_top .. 287 below the ceiling
entry_gap = 5.0                  # entry-slot height the rod slides in along
entry_floor_z = z_top - entry_gap

rest_center_z = 272.0            # rod center at its resting point
cradle_clearance = 0.3
cradle_radius = rod_radius + cradle_clearance   # rounded rest cradle, just over the rod
cradle_bottom_z = rest_center_z - cradle_radius

crest_radius = 3.0               # rounds the corner where the channel curves down
dip_wall_x = cradle_radius       # the dip's right wall, where the curve-down meets the cradle

rod_entry_x_open = 79.0          # entry slot open past the +X face at x=77
rod_channel_y_range = (-74.0, 74.0)   # spans front wall, divider, and back wall


def make_box(x_range, y_range, z_range):
    """Axis-aligned box spanning the given world-coordinate ranges."""
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane("XY")
        .box(x_max - x_min, y_max - y_min, z_max - z_min, centered=True)
        .translate(
            (
                (x_min + x_max) / 2,
                (y_min + y_max) / 2,
                (z_min + z_max) / 2,
            )
        )
    )


def make_tube_hole(y):
    """Cylindrical hole of radius port_hole_radius along X, centered at world
    (y, tube_hole_z), punched through the left (-X) wall. Overshoots the wall
    on both faces so the cut is clean."""
    return (
        cq.Workplane("YZ")
        .circle(port_hole_radius)
        .extrude(20, both=True)
        .translate((tube_hole_wall_x, y, tube_hole_z))
    )


def make_rod_channel():
    """The rod hang channel: a profile cut in the X-Z plane and swept along Y
    through the front wall, divider, and back wall. A flat entry slot open at
    the +X edge curves down over a rounded crest into a rounded cradle at
    center X. The profile top stays at z_top, leaving a bridge to the ceiling
    so the top stays closed."""
    # Crest fillet: rounds the inside corner at (dip_wall_x, entry_floor_z)
    # where the flat entry floor meets the curve down. It is tangent to the
    # floor at x = dip_wall_x + crest_radius and to the vertical at
    # z = entry_floor_z - crest_radius; its arc midpoint is at 135 deg on the
    # fillet circle.
    crest_cx = dip_wall_x + crest_radius
    crest_cz = entry_floor_z - crest_radius
    crest_mid = (
        crest_cx + crest_radius * math.cos(math.radians(135)),
        crest_cz + crest_radius * math.sin(math.radians(135)),
    )
    half_depth = (rod_channel_y_range[1] - rod_channel_y_range[0]) / 2.0
    profile = (
        cq.Workplane("XZ")
        .moveTo(rod_entry_x_open, z_top)
        .lineTo(rod_entry_x_open, entry_floor_z)             # open +X edge, down
        .lineTo(crest_cx, entry_floor_z)                     # flat entry floor, in
        .threePointArc(crest_mid, (dip_wall_x, crest_cz))    # crest: curve down
        .lineTo(dip_wall_x, rest_center_z)                   # short drop to the cradle
        .threePointArc((0.0, cradle_bottom_z), (-cradle_radius, rest_center_z))  # rounded cradle
        .lineTo(-cradle_radius, z_top)                       # left end-stop wall, up
        .close()                                             # bridge-line top, back to start
    )
    return profile.extrude(half_depth, both=True)


def build_reservoir_pockets():
    outer = make_box(outer_x_range, outer_y_range, outer_z_range)
    front_pocket = make_box(front_pocket_x_range, front_pocket_y_range, front_pocket_z_range)
    back_pocket = make_box(back_pocket_x_range, back_pocket_y_range, back_pocket_z_range)
    front_doorway = make_box(doorway_wall_x_range, front_pocket_y_range, front_pocket_z_range)
    back_doorway = make_box(doorway_wall_x_range, back_pocket_y_range, back_pocket_z_range)
    front_tube_hole = make_tube_hole(front_tube_hole_y)
    back_tube_hole = make_tube_hole(back_tube_hole_y)
    rod_channel = make_rod_channel()
    return (
        outer
        .cut(front_pocket)
        .cut(back_pocket)
        .cut(front_doorway)
        .cut(back_doorway)
        .cut(front_tube_hole)
        .cut(back_tube_hole)
        .cut(rod_channel)
    )


def main():
    model = build_reservoir_pockets()
    export_step(model, str(_here.parent / "reservoir-pockets.step"))
    print("-> reservoir-pockets.step")


if __name__ == "__main__":
    main()
