"""Reservoir pockets — a rectangular box holding two collapsible 1 L
Platypus water bags hanging vertically, separated by a divider.

Two bag pockets sit front-to-back along the depth (Y) axis with a 2 mm
divider between them. Each pocket is sized to one 1 L Platypus bag —
285 mm tall, 150 mm wide, 70 mm deep when depth-restricted. Walls, floor,
ceiling, and divider are all 2 mm. The outer envelope is 154 mm wide
(X) × 146 mm deep (Y) × 289 mm tall (Z).

Each pocket opens through its right (+X) wall as a doorway the full size of
the pocket side face — 70 mm deep (Y) × 285 mm tall (Z) — leaving the floor,
ceiling, front wall, divider, and back wall as a 2 mm frame. Transparent PETG.

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


def build_reservoir_pockets():
    outer = make_box(outer_x_range, outer_y_range, outer_z_range)
    front_pocket = make_box(front_pocket_x_range, front_pocket_y_range, front_pocket_z_range)
    back_pocket = make_box(back_pocket_x_range, back_pocket_y_range, back_pocket_z_range)
    front_doorway = make_box(doorway_wall_x_range, front_pocket_y_range, front_pocket_z_range)
    back_doorway = make_box(doorway_wall_x_range, back_pocket_y_range, back_pocket_z_range)
    return (
        outer
        .cut(front_pocket)
        .cut(back_pocket)
        .cut(front_doorway)
        .cut(back_doorway)
    )


def main():
    model = build_reservoir_pockets()
    export_step(model, str(_here.parent / "reservoir-pockets.step"))
    print("-> reservoir-pockets.step")


if __name__ == "__main__":
    main()
