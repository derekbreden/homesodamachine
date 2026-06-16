"""Reservoir pockets — a rectangular box holding two collapsible 1 L
Platypus water bags hanging vertically, separated by a divider.

Two bag pockets sit front-to-back along the depth (Y) axis with a [2 mm](WALL_THICKNESS)
divider between them. Each pocket is sized to one 1 L Platypus bag —
285 mm tall, 150 mm wide, 70 mm deep when depth-restricted. Walls, floor,
ceiling, and divider are all [2 mm](WALL_THICKNESS). The outer envelope is [154 mm](OUTER_WIDTH) wide
(X) × [146 mm](OUTER_DEPTH) deep (Y) × [289 mm](OUTER_HEIGHT) tall (Z). The box is closed on top — the
ceiling stays.

Each pocket opens through its right (+X) wall as a doorway the full size of
the pocket side face — [70 mm](POCKET_DEPTH) deep (Y) × [285 mm](POCKET_HEIGHT) tall (Z) — leaving the floor,
ceiling, front wall, divider, and back wall as a [2 mm](WALL_THICKNESS) frame. The opposite,
left (-X) wall carries one [⌀6.5 mm](PORT_HOLE_DIAMETER) (~1/4") tubing exit hole per pocket,
centered in the pocket's depth (Y) and low in the wall — its bottom [6.5 mm](TUBE_HOLE_FLOOR_GAP)
above the floor — for each bag's spout line. Transparent PETG.

Rod hang channel: one 1/8 in stainless rod runs front-to-back (along Y)
through both bags' centered top loops, passing through the front wall, the
divider, and the back wall. Each of those three walls carries a channel cut
into its face near the top — NOT through the ceiling. The channel is the rod diameter plus a little clearance over its secure
length: a horizontal run open at the +X (back / doorway) edge that the rod
slides along — flared wider at the mouth (downward only, since the top stays
at the ceiling) so the rod is easy to start, ramping back to the secure
width partway in — then an all-straight drop at center X into a rest pocket: a
45 deg ramp down, a flat floor, and a vertical back wall (the -X end stop), no
arcs, so it prints clean on the -X face. The channel top sits one wall thickness
below the box top, so the ceiling closes solid over it. The user
threads the rod through both bag loops and connects the spouts outside the
box, slides the rod in from the +X back through the three aligned channels
(carrying the bags in with it), and at center the rod rolls down the ramp and
seats in the pocket, wedged between the ramp and the back wall; the hanging
bags' weight holds it there and resists sliding back out. The rod ends run [6 mm](Y_STUB)
past each outer wall into a boss whose outer surface is the channel
cross-section grown by one wall thickness — a uniform [2 mm](WALL_THICKNESS) shell hugging the
channel, open at the +X mouth — with a [2 mm](Y_ENDCAP) plug past each tip that captures the
rod along Y so it cannot slide out the front or back. To remove, lift the rod up
out of the pocket and slide it back out the +X side.

World frame: Z+ up, Y- front (front face points in -Y), X left(-)/
right(+). The floor sits on Z=0, centered in X and Y."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_step
from docgen import substitute_py_comments, substitute_md

# Wall, floor, ceiling, and divider thickness.
wall_thickness = 2.0

# Outer shell extents (world coordinates, centered in X and Y, floor on Z=0).
outer_x_range = (-77, 77)
outer_y_range = (-73, 73)
outer_z_range = (0, 289)

# The two bag pockets, cut from the shell. Front pocket is in -Y, back in
# +Y; the [2 mm](WALL_THICKNESS) divider is the stock between them across Y=0.
front_pocket_x_range = (-75, 75)
front_pocket_y_range = (-71, -1)
front_pocket_z_range = (2, 287)

back_pocket_x_range = (-75, 75)
back_pocket_y_range = (1, 71)
back_pocket_z_range = (2, 287)

# Each pocket opens through the right (+X) wall as a doorway the full size of
# the pocket side face: [70 mm](POCKET_DEPTH) deep (Y) x [285 mm](POCKET_HEIGHT) tall (Z). The cut spans the
# [2 mm](WALL_THICKNESS) wall over each pocket's Y/Z footprint, leaving the floor, ceiling,
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

# --- Rod hang channel (slide in from the +X back, ramp down to a rest pocket) ---
# A channel — rod diameter plus a little clearance over its secure length,
# flared wider at the +X mouth for easy insertion — cut as a profile in the
# X-Z plane and swept
# along Y through the front wall, the divider, and the back wall (the empty
# pockets between them carry no material). The channel runs horizontally in
# from the +X (back / doorway) edge, then drops at center X into an all-straight
# rest pocket: a 45 deg ramp down from the secure run, a flat floor, and a
# vertical back wall (the -X end stop). Every wall is a straight line — no arcs —
# so the part prints clean lying on its -X face (build direction +X): the ramp is
# the lone overhang and sits right at the 45 deg self-supporting limit; the back
# wall, floor, top, and secure run are all vertical or horizontal in that
# orientation. Its highest point is channel_top_z, one wall thickness below the
# box top, so the ceiling closes solid over it. The rod rolls down the ramp and
# seats in the pocket, wedged between the ramp and the vertical back wall.
#
# A 1/8 in stainless rod carries two full 1 L bags easily: the divider acts as
# a midspan support, so each ~72 mm span sees ~10 N (~57 MPa bending; 304 SS
# yields ~215 MPa) and under 0.1 mm sag. The channel is derived from
# rod_diameter, so a 1/4 in rod is a one-line change. Heights are placeholders
# pending the real bag loop / hung-bag height; they set how high the bag hangs.
rod_diameter = 3.175             # 1/8 in stainless rod
rod_radius = rod_diameter / 2.0
channel_clearance = 0.3          # gap per side around the rod — entry and rest alike
channel_hw = rod_radius + channel_clearance   # secure channel half-width (the mouth flares wider)

# Raised as high as the closed top allows: the channel top sits one wall
# thickness below the box top, so the [2 mm](WALL_THICKNESS) ceiling closes over it and the
# ceiling's top face stays at the box top (outer_z_range[1]). The envelope
# does not grow in Z.
channel_top_z = outer_z_range[1] - wall_thickness   # 287
rod_run_z = channel_top_z - channel_hw        # rod centerline along the horizontal entry run
rod_rest_z = 272.0               # rod centerline at the rest pocket (its resting point)

rod_entry_x_open = 79.0          # entry runs out past the +X face at x=77 (open end, trimmed)

# Funnel mouth: the entry opening flares wider toward the +X mouth so the rod
# is easy to start, then ramps back to the secure width partway in. The flare
# is downward ONLY — the top wall stays at the run top (just under the [2 mm](WALL_THICKNESS)
# ceiling) the whole way, since flaring upward would breach the ceiling. From
# the secure run out to funnel_ramp_x the bottom is at its normal height; from
# there it ramps down to funnel_mouth_floor_z, reaching it AT the +X face (then
# held flat through the [2 mm](WALL_THICKNESS) overshoot). The mouth floor drops clear to the
# resting depth — the same z as the pocket floor — so the mouth is its largest at the
# face (~4.5x the secure height) and tapers back to the secure slot by
# funnel_ramp_x.
funnel_ramp_x = 40.0             # where the bottom returns to the secure channel
funnel_mouth_floor_z = rod_rest_z - channel_hw   # mouth floor at the rest-pocket floor (resting depth)

# The rod ends extend y_stub past each outer (XZ-plane) wall, captured by a
# boss whose outer surface is the channel cross-section grown by one
# wall_thickness: a uniform [2 mm](WALL_THICKNESS) shell hugging the channel, open at the +X
# mouth just like the channel. Over the stub the shell wraps the rod; past the
# tip a y_endcap-thick plug caps it, so the rod cannot slide out along Y. The
# channel sweeps the full rod length (tip to tip); the plugs past the tips stay
# solid.
y_stub = 6.0                     # exposed rod past each outer wall
y_endcap = wall_thickness        # [2 mm](Y_ENDCAP) plug capping the rod tip
rod_tip_y = outer_y_range[1] + y_stub        # [79 mm](ROD_TIP_Y): where each rod end stops
boss_outer_y = rod_tip_y + y_endcap          # [81 mm](BOSS_OUTER_Y): outer face of the end plug
rod_length = 2 * rod_tip_y                   # [158 mm](ROD_LENGTH) — cut length of the 1/8" SS bag-hanger rod, tip to tip

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


def _channel_profile():
    """The rod hang channel cross-section: a closed profile in the X-Z plane —
    a horizontal entry run open at the +X edge (flared wider at the mouth,
    downward only, then ramping back to the secure width), then an all-straight
    drop at center X into the rest pocket: a 45 deg ramp down, a flat floor, and
    a vertical back wall (the -X end stop). No arcs — every wall is a straight
    line, so the part prints clean on its -X face (the ramp is the lone overhang
    and sits at the 45 deg self-supporting limit; floor, back wall, top, and
    secure run are all horizontal or vertical in that orientation). Width over
    the secure run is the rod diameter plus clearance. Reused two ways: extruded
    along Y as the channel void, and offset outward by one wall for the rod-end
    boss shell. Returns the pending wire."""
    hw = channel_hw
    secure_floor_z = rod_run_z - hw          # floor of the horizontal secure run
    floor_z = funnel_mouth_floor_z           # flat pocket floor, level with the mouth floor
    # The 45 deg ramp drops from the secure-run floor to the pocket floor; at
    # 45 deg its horizontal run equals that drop, and it is laid out to land at
    # center X (x=0), so the ramp top sits at x = the drop.
    ramp_top_x = secure_floor_z - floor_z    # == rod_run_z - rod_rest_z
    back_x = -hw                             # vertical back wall, hw to -X of center
    return (
        cq.Workplane("XZ")
        .moveTo(rod_entry_x_open, rod_run_z + hw)            # entry top-outer, open +X end
        .lineTo(back_x, rod_run_z + hw)                      # top wall, all the way back to the vertical wall
        .lineTo(back_x, floor_z)                             # vertical back wall — the -X end stop (line in Z)
        .lineTo(0.0, floor_z)                                # flat pocket floor, out to center X (line in X)
        .lineTo(ramp_top_x, secure_floor_z)                  # 45 deg ramp up to the secure-run floor
        .lineTo(funnel_ramp_x, secure_floor_z)               # secure bottom wall, out to the mouth ramp
        .lineTo(outer_x_range[1], funnel_mouth_floor_z)      # mouth ramp down, reaching the mouth floor AT the +X face
        .lineTo(rod_entry_x_open, funnel_mouth_floor_z)      # hold at resting depth through the overshoot past the face
        .close()                                             # mouth end cap, past the +X face
    )


def make_rod_channel():
    """The channel void: the cross-section swept along Y the full rod length,
    tip to tip. The plugs past the tips stay solid (the sweep stops at the
    tips)."""
    return _channel_profile().extrude(rod_tip_y, both=True)


def make_boss_shell():
    """Both rod-end bosses. The outer surface is the channel cross-section grown
    by one wall_thickness (offset2D) — a uniform 2 mm shell — clipped at the +X
    face so the mouth stays open, then kept only over the two boss Y-slabs
    beyond the front and back walls. The caller cuts the channel through it,
    leaving a 2 mm shell over each stub and a solid plug past each tip."""
    fat = _channel_profile().offset2D(wall_thickness).extrude(boss_outer_y, both=True)
    fat = fat.intersect(make_box((-200, outer_x_range[1]), (-boss_outer_y, boss_outer_y), (-100, 400)))
    back = fat.intersect(make_box((-200, 200), (outer_y_range[1], boss_outer_y), (-100, 400)))
    front = fat.intersect(make_box((-200, 200), (-boss_outer_y, -outer_y_range[1]), (-100, 400)))
    return back.union(front)


def build_reservoir_pockets():
    outer = make_box(outer_x_range, outer_y_range, outer_z_range)
    front_pocket = make_box(front_pocket_x_range, front_pocket_y_range, front_pocket_z_range)
    back_pocket = make_box(back_pocket_x_range, back_pocket_y_range, back_pocket_z_range)
    front_doorway = make_box(doorway_wall_x_range, front_pocket_y_range, front_pocket_z_range)
    back_doorway = make_box(doorway_wall_x_range, back_pocket_y_range, back_pocket_z_range)
    front_tube_hole = make_tube_hole(front_tube_hole_y)
    back_tube_hole = make_tube_hole(back_tube_hole_y)
    boss = make_boss_shell()
    rod_channel = make_rod_channel()
    return (
        outer
        .cut(front_pocket)
        .cut(back_pocket)
        .cut(front_doorway)
        .cut(back_doorway)
        .cut(front_tube_hole)
        .cut(back_tube_hole)
        .union(boss)
        .cut(rod_channel)
    )


def main():
    model = build_reservoir_pockets()
    export_step(model, str(_here.parent / "reservoir-pockets.step"))
    print("-> reservoir-pockets.step")

    # Pinned computed numbers — the rod's geometry, fed from the source
    # constants so the docs/comments can never drift from the model.
    variables = {
        "ROD_LENGTH": f"{rod_length:.4g} mm",
        "ROD_TIP_Y": f"{rod_tip_y:.4g} mm",
        "BOSS_OUTER_Y": f"{boss_outer_y:.4g} mm",
        "WALL_THICKNESS": f"{wall_thickness:.4g} mm",
        "OUTER_WIDTH": f"{outer_x_range[1] - outer_x_range[0]:.4g} mm",
        "OUTER_DEPTH": f"{outer_y_range[1] - outer_y_range[0]:.4g} mm",
        "OUTER_HEIGHT": f"{outer_z_range[1] - outer_z_range[0]:.4g} mm",
        "POCKET_DEPTH": f"{front_pocket_y_range[1] - front_pocket_y_range[0]:.4g} mm",
        "POCKET_HEIGHT": f"{front_pocket_z_range[1] - front_pocket_z_range[0]:.4g} mm",
        "PORT_HOLE_DIAMETER": f"⌀{port_hole_radius * 2:.4g} mm",
        "TUBE_HOLE_FLOOR_GAP": f"{tube_hole_floor_gap:.4g} mm",
        "Y_STUB": f"{y_stub:.4g} mm",
        "Y_ENDCAP": f"{y_endcap:.4g} mm",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={"ROD_LENGTH": 1},
    )
    print("-> README.md")
    substitute_py_comments(
        _here,
        variables=variables,
        expected_counts={
            "ROD_LENGTH": 1,
            "ROD_TIP_Y": 1,
            "BOSS_OUTER_Y": 1,
            "WALL_THICKNESS": 10,
            "OUTER_WIDTH": 1,
            "OUTER_DEPTH": 1,
            "OUTER_HEIGHT": 1,
            "POCKET_DEPTH": 2,
            "POCKET_HEIGHT": 2,
            "PORT_HOLE_DIAMETER": 1,
            "TUBE_HOLE_FLOOR_GAP": 1,
            "Y_STUB": 1,
            "Y_ENDCAP": 2,
        },
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    main()
