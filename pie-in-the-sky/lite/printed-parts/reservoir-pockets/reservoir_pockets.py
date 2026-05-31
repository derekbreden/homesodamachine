"""Reservoir pockets — a rectangular box holding two collapsible 1 L
Platypus water bags hanging vertically, separated by a divider.

Two bag pockets sit front-to-back along the depth (Y) axis with a 2 mm
divider between them. Each pocket is sized to one 1 L Platypus bag —
285 mm tall, 150 mm wide, 70 mm deep when depth-restricted. Walls, floor,
and divider are 2 mm. The outer envelope is 154 mm wide (X) × 146 mm deep
(Y) × 289 mm tall (Z). The top is open (no ceiling) so each bag hangs from
the rod below.

Each pocket opens through its right (+X) wall as a doorway the full size of
the pocket side face — 70 mm deep (Y) × 285 mm tall (Z) — leaving the floor,
front wall, divider, and back wall as a 2 mm frame. The opposite, left (-X)
wall carries one ⌀6.5 mm (~1/4") tubing exit hole per pocket, centered in
the pocket's depth (Y) and low in the wall — its bottom 6.5 mm above the
floor — for each bag's spout line. Transparent PETG.

Hang channel: one SS rod runs front-to-back (along Y) through both bags'
centered top loops, crossing the front wall, the divider, and the back
wall. Each of those three walls carries a rod channel cut into its open
top — a horizontal entry slot open at the +X (back / doorway) edge that
runs inward to center, then drops into a detent notch. The user threads
the rod through both bag loops outside the box, lays it into the open
channel at the back, slides it in -X to center, and it drops into the
detent; the hanging bags' weight seats it there (closet-rod style). To
remove, lift the rod out of the detent and slide it back out the +X side.

World frame: Z+ up, Y- front (front face points in -Y), X left(-)/
right(+). The floor sits on Z=0, centered in X and Y."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware"))
from _cadq_export import export_step

# Wall, floor, and divider thickness.
wall_thickness = 2.0

# Outer shell extents (world coordinates, centered in X and Y, floor on Z=0).
outer_x_range = (-77, 77)
outer_y_range = (-73, 73)
outer_z_range = (0, 289)

# The two bag pockets, cut from the shell. Front pocket is in -Y, back in
# +Y; the 2 mm divider is the stock between them across Y=0. The pockets run
# to the full outer height (no ceiling) so the top is open for the bags.
front_pocket_x_range = (-75, 75)
front_pocket_y_range = (-71, -1)
front_pocket_z_range = (2, 289)

back_pocket_x_range = (-75, 75)
back_pocket_y_range = (1, 71)
back_pocket_z_range = (2, 289)

# Each pocket opens through the right (+X) wall as a doorway the full size of
# the pocket side face: 70 mm deep (Y) x 285 mm tall (Z). The cut spans the
# 2 mm wall over each pocket's Y/Z footprint, leaving the floor, front wall,
# divider, and back wall as a frame.
doorway_wall_x_range = (75, 77)
doorway_z_range = (2, 287)

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

# --- Rod hang channel (broadside slide-in + drop-into-detent) ---
# The rod lies along Y and is laid into the open top of the front wall,
# divider, and back wall. A single channel cut spanning the full Y range
# carves it through all three at once (the open pocket gaps between them are
# already empty). rod_diameter is a placeholder pending the real bag loop.
rod_diameter = 8.0
rod_slot_clearance = 1.0
rod_slot_width = rod_diameter + rod_slot_clearance  # X width of the detent notch
# Entry slot: rod rests on this floor while sliding in from the +X back edge.
# Its center sits ~rod radius above, near the open top.
rod_entry_floor_z = 281.0
rod_entry_x_near = 0.0                      # inboard end of the slide (over center)
rod_entry_x_far = outer_x_range[1] + 2.0    # open past the +X back face
# Detent: at center X, the floor drops by rod_detent_drop so the seated rod
# nestles below the entry floor; bag weight keeps it from climbing back up
# and sliding out. Bounded on -X by solid wall (end stop).
rod_detent_x = 0.0
rod_detent_drop = 8.0
rod_detent_floor_z = rod_entry_floor_z - rod_detent_drop
rod_slot_top_z = outer_z_range[1] + 2.0     # open above the wall top
rod_slot_y_range = (outer_y_range[0] - 1.0, outer_y_range[1] + 1.0)  # full Y, all 3 walls


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
    """The rod hang channel, cut through the front wall, divider, and back
    wall in one Y-spanning pass (the open pocket gaps between them carry no
    material). Profile in X-Z: a horizontal entry slot open at the +X back
    edge and at the top, plus a deeper detent notch at center X."""
    entry = make_box(
        (rod_entry_x_near, rod_entry_x_far),
        rod_slot_y_range,
        (rod_entry_floor_z, rod_slot_top_z),
    )
    detent = make_box(
        (rod_detent_x - rod_slot_width / 2, rod_detent_x + rod_slot_width / 2),
        rod_slot_y_range,
        (rod_detent_floor_z, rod_slot_top_z),
    )
    return entry.union(detent)


def build_reservoir_pockets():
    outer = make_box(outer_x_range, outer_y_range, outer_z_range)
    front_pocket = make_box(front_pocket_x_range, front_pocket_y_range, front_pocket_z_range)
    back_pocket = make_box(back_pocket_x_range, back_pocket_y_range, back_pocket_z_range)
    front_doorway = make_box(doorway_wall_x_range, front_pocket_y_range, doorway_z_range)
    back_doorway = make_box(doorway_wall_x_range, back_pocket_y_range, doorway_z_range)
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
