"""Shared interface for the cold-core's geometry modules — dimensional
constants and hole-punch helpers that every sibling part (foam shell,
foam cap stack, reservoir, copper plugs, coil mandrel) needs to stay
in sync against."""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

import cadquery as cq

from world_workplane import xy_plane_z_up, xz_plane_y_up, xz_plane_y_down, WorldWorkplane


# All structural walls and floors are [2 mm](WALL_AND_FLOOR_THICKNESS) PETG.
wall_and_floor_thickness = 2.0
hole_shift_from_edge = 15.0


# The cold cylinder + its evaporator coil. [7 mm](COIL_RADIAL_CLEARANCE) of
# radial clearance out from the cylinder OD holds the 1/4" ACR copper coil +
# thermal tape; the tank support ring cradles the tank rim at this envelope.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
tank_coil_envelope_radius = tank_outer_radius + coil_radial_clearance

# Foam blanket around the cylinder — the pour-foam standoff measured from the
# cylinder OD out to the reservoir's tank-facing wall, uniform around the wrapped
# arc (that wall is a concentric arc), with the coil embedded in its inner slice
# (so it must be >= coil_radial_clearance). This VALUE is not a thermal target:
# it is set so the reservoir, shifted out by it, keeps the 283 mm outer width
# (outer_shell_x_length below) with its reed channel butted against the outer
# wall — i.e. the foam that used to sit outboard of the reed moved to the
# cylinder side. The reservoir-facing (cavity) face is one wall further out.
foam_thickness_around_cylinder = 15.0
pocket_centerward_arc_outer_radius = (
    tank_outer_radius + foam_thickness_around_cylinder + wall_and_floor_thickness
)

# Foam-shell outer height. Tank height + [30 mm](ABOVE_TANK_ELBOWS_HEIGHT) above for top-side elbow
# fittings + [30 mm](BELOW_TANK_ELBOWS_HEIGHT) below for bottom-side elbow fittings + 1 mm
# wall-thickness compensation.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
foam_shell_outer_height = (
    tank_height + below_tank_elbows_height + above_tank_elbows_height + 1.0
)

tank_support_ring_height = 30.0
support_ring_radial_width = 9.0

# ⌀[6.5](PORT_HOLE_DIAMETER) — the project-wide standard for small through-shell features
# (water outlet, reservoir bulkheads, reed cable holes, CO2 tube clearance).
port_hole_radius = 3.25

# Reed-channel cavity depth (radial, out from the bag-pocket far wall). The reed
# column drops into this cavity; the outer_shell X width is sized so the cavity +
# its wall butt the outer shell wall (see outer_shell_x_length). Consumed by
# _reed_channels.py too.
reed_x_depth = 6.0

# Bag pocket. Width and depth are the reservoir's own dimensions — sized to the
# flavor charge it carries (each usable window, Reed 1 low → Reed 4 full over
# 135 mm of float travel, holds 2 × SodaStream 0.44 L bottles). They are NOT tied
# to the tank geometry: the ±Y width stands on its own so growing the cylinder's
# foam blanket slides the pocket outward without resizing the reservoir.
bag_pocket_width = 145.0
bag_pocket_depth = 49 + 2 * wall_and_floor_thickness
bag_pocket_far_inner_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - 2 * wall_and_floor_thickness
)
bag_pocket_y_inner_max = bag_pocket_width / 2 - wall_and_floor_thickness
bag_pocket_floor_top_z = wall_and_floor_thickness
bag_pocket_walls_top_z = foam_shell_outer_height

# Matches the reservoir's outer +X × ±Y fillet (R=6) with reservoir_clearance
# on top, so the reservoir's outer arc slides into a snugly-mated arc on
# the pocket's inner corner with uniform clearance.
bag_pocket_corner_inner_radius = 6.5

reservoir_clearance = 0.5
reservoir_floor_thickness = 3.0
# Bulkhead vertical scheme. The PureSec mounts elbow-DOWN: the integral 90°
# elbow + its dry-side flange + the below-side printed-TPU washer hang below
# the reservoir's flat exterior floor bottom (the wet-side primary seal is a
# purchased silicone flat washer in a wet/cavity-side counterbore, compressed
# by the nut on the wet/cavity side, above; the dry-side TPU washer is the
# secondary seal under the elbow flange). The reservoir's weight rides on the
# corner support posts; the
# elbow's lowest point clears the bag-pocket floor by bulkhead_floor_clearance
# and bears no load. The flavor-line wall holes and the reed cable holes both
# pin their Z to bulkhead_elbow_exit_z (the elbow's lateral-port center), so
# the tube and the cable run level out of the open pocket.
bulkhead_floor_clearance = 1.0  # gap from the lowest bulkhead hardware down to the bag-pocket floor — non-load-bearing
bulkhead_elbow_bottom_z = bag_pocket_floor_top_z + bulkhead_floor_clearance
bulkhead_elbow_exit_z = bulkhead_elbow_bottom_z + 3.0  # elbow's lateral-PTC-port Z center
reservoir_bulkhead_port_x = (bag_pocket_far_inner_x + pocket_centerward_arc_outer_radius) / 2
# Y of the bulkhead pass-through (and the cable hole that shares its y so
# the reed cable runs straight from channel to outside). 10 mm inboard
# of the bag-pocket −Y (front, toward the user) wall outer face.
reservoir_bulkhead_port_y = -(bag_pocket_width / 2 - 10)

# Outer footprint. The ±Y (front/back) gap is the tank's foam blanket out to the
# shell wall. The ±X width is set by the reservoir + its reed channel butted
# against the shell wall — no outboard foam there; it moved to the cylinder side.
outer_shell_foam_gap = 16.0  # ±Y front/back foam-pour gap
bag_pocket_outermost_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - wall_and_floor_thickness
)
# ±X: reservoir far wall + reed cavity + reed wall + shell wall (reed butted).
outer_shell_x_length = 2 * (
    bag_pocket_outermost_x + reed_x_depth + 2 * wall_and_floor_thickness
)
# ±Y: reservoir side wall (its own half-width) + front/back foam + shell wall.
outer_shell_y_length = 2 * (
    bag_pocket_width / 2 + outer_shell_foam_gap + wall_and_floor_thickness
)


# Foam-cap stack — the pour trays that close both ends of the shell (one
# mouth-up on top, one mouth-down underneath), each with a thin pour lid.
# The interior height is the cap's foam depth; the printed cup adds one
# floor.
foam_cap_interior_height = outer_shell_foam_gap
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness
foam_cap_lid_pour_radius = 10.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0

# CO2 inlet tube pass-through (through the top cap + its lid): the 1/4" OD
# LLDPE CO2 line enters from above at x=0, its Y midway between the
# centerward-wall band and the support-ring band, then routes down through
# the body foam to the internal ⌀18 elbow doorway (the doorway itself is cut
# in _port_cuts, not here). Only the tube traverses the cap stack. The cap
# is authored with its bore on −Y and installed rotated 180° about Z, so the
# bore lands at +co2_inlet_y — the doorway's side (see foam-assembly).
co2_inlet_tube_radius = port_hole_radius
_co2_centerward_mid_r = pocket_centerward_arc_outer_radius - wall_and_floor_thickness / 2
_co2_support_ring_outer_r = tank_coil_envelope_radius  # the ring sits on the tank+coil envelope
_co2_support_ring_mid_r = _co2_support_ring_outer_r - support_ring_radial_width / 2
co2_inlet_y = -(_co2_centerward_mid_r + _co2_support_ring_mid_r) / 2

# Cap-to-outer-shell joinery: 6 attachment points per face × 2 faces =
# 12 inserts / 12 M3×25 SHCS, each screw passing lid + cap into an insert
# pressed from the shell face it mates. TPU gasket per cap
# (foam-cap-gasket.step). See bom.md for hardware SKUs.
screw_clearance_radius = 1.95  # ⌀[3.9](SCREW_CLEARANCE_DIAMETER) clearance for M3 SHCS shank
insert_pocket_radius = 2.0  # ⌀[4](INSERT_POCKET_DIAMETER) for ruthex M3 short heat-set
insert_pocket_depth = 8.0  # 4 mm insert engagement + 4 mm relief
screw_boss_size = 8.0  # ⌀[8 × 8 mm](SCREW_BOSS_SIZE) cylindrical boss at each attachment

# Rounded outer-shell corners. Each corner's exterior wall is a true arc:
# the outer face is a quarter-round of [12 mm](CORNER_ROUND_R) radius, the
# inner face concentric one wall-thickness inboard. The corner boss is
# seated deep IN the corner so its cylinder's outer edge is tangent to the
# EXTERIOR wall arc, fusing into the outer skin with one wall-thickness of
# PETG over the insert.
corner_round_radius = 12.0
_corner_arc_x = outer_shell_x_length / 2 - corner_round_radius
_corner_arc_y = outer_shell_y_length / 2 - corner_round_radius
_corner_boss_diag_offset = (corner_round_radius - screw_boss_size / 2) / math.sqrt(2)
_corner_boss_x = _corner_arc_x + _corner_boss_diag_offset
_corner_boss_y = _corner_arc_y + _corner_boss_diag_offset

# Mid-long-side bosses offset in X to clear the copper/water-outlet
# slot at x=0; opposite signs at ±Y preserve 180° rotational symmetry
# around the Z axis (balanced gasket compression).
mid_screw_x_offset = 15.0
attachment_xy_positions = (
    [(x_sign * _corner_boss_x, y_sign * _corner_boss_y)
     for x_sign in (1, -1) for y_sign in (1, -1)]
    + [(y_sign * mid_screw_x_offset,
        y_sign * (outer_shell_y_length / 2 - screw_boss_size / 2))
       for y_sign in (1, -1)]
)
gasket_thickness = 2.0
gasket_strip_width = 5.0

# Deck mounts — the service bay's electronics, carried on columns of the TOP CAP.
# The cap is already a foam-poured cup with six screw-boss columns spanning its full
# height; a deck mount is that same column at four more stations, carried on through
# the lid so its top stands `deck_mount_standoff` proud of the lid's outer face — the
# plane the bay's deck sits on. Foam pours around them, the lid's clearance holes drop
# over them, and the module bolts down into a heat-set insert. Nothing is bonded and no
# tray floor stands between the module and the cap.
#   The stations live here, in the cap's own frame, because the mount belongs to the
# part it is printed in. The enclosure reads its world poses off them
# (`_contents.deck_mount`) rather than the cap being told where a board went, so one
# edit here moves the column, the module and its connector map together.
deck_mount_boss_radius = 3.5     # column radius — one wall over the insert
deck_mount_bore_radius = 2.0     # ruthex M3 short heat-set
deck_mount_bore_depth = 5.5
deck_mount_lid_slip = 0.4        # per side, column to the lid's clearance hole
deck_mount_standoff = 5.0        # boss top above the lid — clears the boards' THT tails

# Per module: the mount rectangle's centre in the cap's frame, and the module's own
# hole pitch across X and Y — the controller board's MH1–MH4 rectangle turned a
# quarter so its long axis runs down the bay, and the IRM-90's own pattern laid
# across the aft strip, its long span needing more than the column forward of the
# board has left in Y.
deck_mounts = {
    "pcba": ((92.85, 44.50), 66.30, 78.00),
    "psu":  ((85.00, -37.50), 98.00, 33.00),
}


def deck_mount_xy(name):
    """The four boss centres of a deck mount, in the cap's own frame."""
    (cx, cy), pitch_x, pitch_y = deck_mounts[name]
    return tuple((cx + sx * pitch_x / 2.0, cy + sy * pitch_y / 2.0)
                 for sx in (-1, 1) for sy in (-1, 1))


def make_box(x_range, y_range, z_range):
    """Axis-aligned box from world-coordinate ranges in each axis."""
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(((x_min + x_max) / 2, (y_min + y_max) / 2))
        .rect(x_max - x_min, y_max - y_min)
        .extrude(z_max - z_min)
        .unwrap()
    )


def build_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
    direction=1,
):
    """Y-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Z and
    starting at `origin`'s Y, extruded in `direction`·Y (+1 = +Y, −1 = −Y —
    so a port on the −Y wall punches outward toward −Y)."""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .circle(hole_punch_radius)
        .extrude(direction * hole_punch_height)
    )


def build_slot_punch(
    origin=(0, 0, 0),
    slot_length=1.0,
    slot_diameter=6.5,
    slot_punch_height=40,
    direction=1,
):
    """Z-elongated, Y-extruded rounded slot (circle-rect-circle), centered
    at `origin`'s X/Z and starting at `origin`'s Y, extruded in `direction`·Y
    (+1 = +Y, −1 = −Y). Long axis runs along world Z. The rounded ends each
    contribute slot_diameter/2 of additional Z reach beyond `slot_length`."""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .slot2D(slot_length, slot_diameter, angle=90)
        .extrude(direction * slot_punch_height)
    )


def build_z_axis_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
):
    """Z-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Y and
    starting at `origin`'s Z, extruded in +Z."""
    x, y, z = origin
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(x, y, 0), offset=z)
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )


if __name__ == "__main__":
    sys.path.insert(
        0,
        str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
    )
    from docgen import substitute_py_comments

    variables = {
        "WALL_AND_FLOOR_THICKNESS": f"{wall_and_floor_thickness:.4g} mm",
        "COIL_RADIAL_CLEARANCE": f"{coil_radial_clearance:.4g} mm",
        "ABOVE_TANK_ELBOWS_HEIGHT": f"{above_tank_elbows_height:.4g} mm",
        "BELOW_TANK_ELBOWS_HEIGHT": f"{below_tank_elbows_height:.4g} mm",
        "PORT_HOLE_DIAMETER": f"{port_hole_radius * 2:.4g}",
        "SCREW_CLEARANCE_DIAMETER": f"{screw_clearance_radius * 2:.4g}",
        "INSERT_POCKET_DIAMETER": f"{insert_pocket_radius * 2:.4g}",
        "SCREW_BOSS_SIZE": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "WALL_AND_FLOOR_THICKNESS": 1,
            "COIL_RADIAL_CLEARANCE": 1,
            "ABOVE_TANK_ELBOWS_HEIGHT": 1,
            "BELOW_TANK_ELBOWS_HEIGHT": 1,
            "PORT_HOLE_DIAMETER": 1,
            "SCREW_CLEARANCE_DIAMETER": 1,
            "INSERT_POCKET_DIAMETER": 1,
            "SCREW_BOSS_SIZE": 1,
        },
    )
    print("-> _cold_core_interface.py (self)")
