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
into its face near the top — NOT through the ceiling. The channel is one
constant width the whole way (the rod diameter plus a little clearance): a
horizontal run open at the +X (back / doorway) edge that the rod slides
along, then a curve down — both walls of the bend are rounded arcs — into a
rounded cradle at center X that holds the round rod. A bridge of wall
material spans above the channel, so the ceiling stays attached. The user
threads the rod through both bag loops and connects the spouts outside the
box, slides the rod in from the +X back through the three aligned channels
(carrying the bags in with it), and at center the rod rolls down into the
cradle; the hanging bags' weight seats it there and resists sliding back
out. The rod ends run 6 mm past each outer wall into a boss that wraps them
in 2 mm of floor, ceiling, and an end wall — those end walls capture the rod
along Y so it cannot slide out the front or back. To remove, lift the rod up
out of the cradle and slide it back out the +X side.

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
# A constant-width channel — rod diameter plus a little clearance, the same
# width along its whole length — cut as a profile in the X-Z plane and swept
# along Y through the front wall, the divider, and the back wall (the empty
# pockets between them carry no material). The channel runs horizontally in
# from the +X (back / doorway) edge, then curves down through a rounded bend
# (BOTH walls of the bend are arcs: outer radius bend_radius + channel_hw,
# inner radius bend_radius - channel_hw) into a rounded cradle at center X
# that holds the round rod. Its highest point stays at channel_top_z (below
# the ceiling), leaving a bridge of wall material above it
# (channel_top_z .. 287) so the ceiling stays attached. Nothing extends past
# the cradle in -X, so that solid wall is the end stop.
#
# A 1/8 in stainless rod carries two full 1 L bags easily: the divider acts as
# a midspan support, so each ~72 mm span sees ~10 N (~57 MPa bending; 304 SS
# yields ~215 MPa) and under 0.1 mm sag. The channel is derived from
# rod_diameter, so a 1/4 in rod is a one-line change. Heights are placeholders
# pending the real bag loop / hung-bag height; they set how high the bag hangs.
rod_diameter = 3.175             # 1/8 in stainless rod
rod_radius = rod_diameter / 2.0
channel_clearance = 0.3          # gap per side around the rod — entry and cradle alike
channel_hw = rod_radius + channel_clearance   # channel half-width (constant along its length)

channel_top_z = 283.0            # highest point of the channel; bridge spans channel_top_z .. 287
rod_run_z = channel_top_z - channel_hw        # rod centerline along the horizontal entry run
rod_rest_z = 272.0               # rod centerline at the cradle (its resting point)
bend_radius = 6.0                # centerline radius of the curve-down (must exceed channel_hw)

rod_entry_x_open = 79.0          # entry runs out past the +X face at x=77 (open end, trimmed)

# The rod ends extend y_stub past each outer (XZ-plane) wall and are captured
# by a boss: the y_stub of rod is wrapped in 2 mm of floor/ceiling, then a
# y_endcap of solid wall caps the tip so the rod cannot slide out along Y. The
# channel sweeps the full rod length (tip to tip); the bosses supply the
# material it carves through past the original walls, and the y_endcap beyond
# each tip stays solid. The +X side stays open the whole way for insertion.
y_stub = 6.0                     # exposed rod past each outer wall
y_endcap = wall_thickness        # 2 mm end wall capping the rod tip
rod_tip_y = outer_y_range[1] + y_stub        # 79: where each rod end stops
boss_outer_y = rod_tip_y + y_endcap          # 81: outer face of the end cap

# Boss footprint in X-Z: the channel region plus 2 mm of floor (below the
# cradle), ceiling (above the channel top), and -X end-stop wall; left open on
# the +X side (the rod entry) out to the +X face.
boss_x_range = (-channel_hw - wall_thickness, outer_x_range[1])
boss_z_range = (rod_rest_z - channel_hw - wall_thickness, channel_top_z + wall_thickness)

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
    """The rod hang channel: a constant-width profile cut in the X-Z plane and
    swept along Y through the front wall, divider, and back wall. A horizontal
    entry run, open at the +X edge, curves down through a rounded bend (both
    walls arcs) into a rounded cradle at center X. The channel is the same
    width — rod diameter plus clearance — all the way along. Its top stays at
    channel_top_z, leaving a bridge to the ceiling so the top stays closed."""
    hw = channel_hw
    # Centerline of the curve-down: a quarter bend of radius bend_radius from
    # the horizontal run (at rod_run_z) to a vertical drop at center X, then
    # straight down into the cradle. Bend center:
    bend_cx = bend_radius
    bend_cz = rod_run_z - bend_radius

    def arc_pt(r, deg):
        return (
            bend_cx + r * math.cos(math.radians(deg)),
            bend_cz + r * math.sin(math.radians(deg)),
        )

    # Walls of the bend are concentric arcs about the bend center: the outer
    # wall at radius bend_radius + hw, the inner wall at bend_radius - hw, so
    # the gap between them stays the constant channel width (2*hw).
    outer_r = bend_radius + hw
    outer_top = arc_pt(outer_r, 90)     # tangent to the top of the entry run
    outer_mid = arc_pt(outer_r, 135)
    outer_left = arc_pt(outer_r, 180)   # tangent to the outer wall of the drop
    inner_r = bend_radius - hw
    inner_top = arc_pt(inner_r, 90)     # tangent to the bottom of the entry run
    inner_mid = arc_pt(inner_r, 135)
    inner_left = arc_pt(inner_r, 180)   # tangent to the inner wall of the drop

    half_depth = rod_tip_y   # sweep tip to tip (the end caps past the tips stay solid)
    profile = (
        cq.Workplane("XZ")
        .moveTo(rod_entry_x_open, rod_run_z + hw)            # entry top-outer, open +X end
        .lineTo(outer_top[0], rod_run_z + hw)                # top wall of the entry run, in
        .threePointArc(outer_mid, outer_left)               # outer wall of the bend (rounded)
        .lineTo(outer_left[0], rod_rest_z)                   # outer wall of the drop, down
        .threePointArc((0.0, rod_rest_z - hw), (hw, rod_rest_z))  # rounded cradle bottom
        .lineTo(inner_left[0], bend_cz)                      # inner wall of the drop, up
        .threePointArc(inner_mid, inner_top)                # inner wall of the bend (rounded)
        .lineTo(rod_entry_x_open, rod_run_z - hw)            # bottom wall of the entry run, out
        .close()                                             # entry end cap, past the +X face
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
    # Front wall is at -Y, back wall at +Y; a boss protrudes from each.
    front_boss = make_box(boss_x_range, (-boss_outer_y, -outer_y_range[1]), boss_z_range)
    back_boss = make_box(boss_x_range, (outer_y_range[1], boss_outer_y), boss_z_range)
    rod_channel = make_rod_channel()
    return (
        outer
        .cut(front_pocket)
        .cut(back_pocket)
        .cut(front_doorway)
        .cut(back_doorway)
        .cut(front_tube_hole)
        .cut(back_tube_hole)
        .union(front_boss)
        .union(back_boss)
        .cut(rod_channel)
    )


def main():
    model = build_reservoir_pockets()
    export_step(model, str(_here.parent / "reservoir-pockets.step"))
    print("-> reservoir-pockets.step")


if __name__ == "__main__":
    main()
