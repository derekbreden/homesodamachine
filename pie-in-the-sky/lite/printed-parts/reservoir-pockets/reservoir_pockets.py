"""Reservoir pockets — a rectangular box holding two collapsible 1 L
Platypus water bags hanging vertically, separated by a divider.

Two bag pockets sit front-to-back along the depth (Y) axis with a 2 mm
divider between them. Each pocket is sized to one 1 L Platypus bag —
285 mm tall, 150 mm wide, 70 mm deep when depth-restricted. Walls, floor,
ceiling, and divider are all 2 mm. The outer envelope is 154 mm wide
(X) × 146 mm deep (Y) × 289 mm tall (Z).

Each pocket opens through its right (+X) wall as a doorway the full size of
the pocket side face — 70 mm deep (Y) × 285 mm tall (Z) — leaving the floor,
ceiling, front wall, divider, and back wall as a 2 mm frame. The opposite,
left (-X) wall carries one ⌀6.5 mm (~1/4") tubing exit hole per pocket,
centered in the pocket's depth (Y) and low at the floor, for each bag's
spout line. Transparent PETG.

World frame: Z+ up, Y- front (front face points in -Y), X left(-)/
right(+). The floor sits on Z=0, centered in X and Y."""

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
# centered in its pocket's depth (Y) and placed as low as the pocket allows:
# its bottom sits at the pocket floor (Z=2), where a spout-down bag's outlet
# is. tube_hole_wall_x is the mid-plane of the 2 mm left wall.
port_hole_radius = 3.25
tube_hole_wall_x = (outer_x_range[0] + front_pocket_x_range[0]) / 2
tube_hole_z = front_pocket_z_range[0] + port_hole_radius
front_tube_hole_y = sum(front_pocket_y_range) / 2
back_tube_hole_y = sum(back_pocket_y_range) / 2


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


def build_reservoir_pockets():
    outer = make_box(outer_x_range, outer_y_range, outer_z_range)
    front_pocket = make_box(front_pocket_x_range, front_pocket_y_range, front_pocket_z_range)
    back_pocket = make_box(back_pocket_x_range, back_pocket_y_range, back_pocket_z_range)
    front_doorway = make_box(doorway_wall_x_range, front_pocket_y_range, front_pocket_z_range)
    back_doorway = make_box(doorway_wall_x_range, back_pocket_y_range, back_pocket_z_range)
    front_tube_hole = make_tube_hole(front_tube_hole_y)
    back_tube_hole = make_tube_hole(back_tube_hole_y)
    return (
        outer
        .cut(front_pocket)
        .cut(back_pocket)
        .cut(front_doorway)
        .cut(back_doorway)
        .cut(front_tube_hole)
        .cut(back_tube_hole)
    )


def main():
    model = build_reservoir_pockets()
    export_step(model, str(_here.parent / "reservoir-pockets.step"))
    print("-> reservoir-pockets.step")


if __name__ == "__main__":
    main()
