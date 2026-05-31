"""Shared interface for the cold-core's geometry modules — dimensional
constants and hole-punch helpers that every sibling part (foam shell,
foam cap stack, reservoir, copper plugs, coil mandrel) needs to stay
in sync against."""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
# Sibling generator scripts set these sys.path entries before importing
# us, so they're redundant in the normal case — but running this file
# directly (for the substitute_py_comments pass below) needs them too.
# sys.path.insert is idempotent.
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

import cadquery as cq

from world_workplane import xy_plane_z_up, xz_plane_y_up, xz_plane_y_down, WorldWorkplane


# All structural walls and floors are [2 mm](WALL_AND_FLOOR_THICKNESS) PETG.
wall_and_floor_thickness = 2.0
hole_shift_from_edge = 15.0


# Reservoir-pocket centerward arc. Each pocket's centerward wall (the
# one facing the cold-core axis) is curved; the wall's cavity-side face
# rides on a cylinder of this radius (centered on the cold-core axis).
# The wall's tank-side face sits one wall-thickness inboard at radius
# (pocket_centerward_arc_outer_radius − wall_and_floor_thickness), giving
# [7 mm](COIL_RADIAL_CLEARANCE) of radial clearance between the tank and the wall — room for the
# 1/4" ACR copper coil + thermal tape + slack.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
pocket_centerward_arc_outer_radius = (
    tank_outer_radius + coil_radial_clearance + wall_and_floor_thickness
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
# (water outlet, reservoir bulkheads, reed cable holes, CO2 tube
# clearance). Used as the explicit radius arg for the punch builders.
port_hole_radius = 3.25

# Bag pocket. Width tracks pocket_centerward_arc_outer_radius so the
# pocket's ±Y outboard faces are tangent to the cylinder the centerward
# arc rides on. Depth sized so each reservoir's usable window (Reed 1
# low warning → Reed 4 full, 135 mm of float travel) holds 2 × Soda-
# Stream 0.44 L bottles per refill cycle = 0.88 L usable. Total
# geometric wet volume ≈ 1.18 L. Earlier baselines: 33 mm = 791 mL
# total; 42 mm = ~1.02 L total but only ~0.76 L usable; 49 mm hits
# the 0.88 L usable target. ~17.8 mL per mm of X interior in the
# usable Y range.
bag_pocket_width = pocket_centerward_arc_outer_radius * 2
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
# elbow + its dry-side flange + the below-side TPU washer hang below the
# reservoir's flat exterior floor bottom (the nut is on the wet/cavity side,
# above). The reservoir's weight rides on the corner support posts, so the
# elbow hangs as low as it can: its lowest point clears the bag-pocket floor
# by bulkhead_floor_clearance and never bears load. The flavor-line wall holes
# and the reed cable holes both pin their Z to bulkhead_elbow_exit_z (the
# elbow's lateral-port center), so the tube and the cable run level out of the
# open pocket.
#
# How far the floor is raised to clear that below-floor hardware (dry washer +
# elbow; the seal boss sits flush in the flat bottom) is DERIVED in
# reservoir.py (floor_trough_lift / bulkhead_below_floor_stack) from the
# seal-boss geometry — itself keyed off reservoir_wall_thickness — plus the
# measured elbow standoff. There is no hand-tuned stack constant here, so
# adjusting the wall thickness propagates through the boss, the floor height,
# and the foam-shell support posts.
bulkhead_floor_clearance = 1.0  # gap from the lowest bulkhead hardware down to the bag-pocket floor — non-load-bearing
bulkhead_elbow_bottom_z = bag_pocket_floor_top_z + bulkhead_floor_clearance
bulkhead_elbow_exit_z = bulkhead_elbow_bottom_z + 3.0  # lateral-PTC-port Z center, 3 mm above the elbow bottom
reservoir_bulkhead_port_x = (bag_pocket_far_inner_x + pocket_centerward_arc_outer_radius) / 2
# Y of the bulkhead pass-through (and the cable hole that shares its y so
# the reed cable runs straight from channel to outside). 10 mm inboard
# of the bag-pocket +Y wall outer face.
reservoir_bulkhead_port_y = bag_pocket_width / 2 - 10

# Outer footprint shared by the outer shell, the foam cap, and the
# foam cap lid — must be coplanar at the corners so the screw bosses
# line up at each attachment position.
outer_shell_foam_gap = 16.0
bag_pocket_outermost_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - wall_and_floor_thickness
)
outer_shell_x_length = 2 * (
    bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness
)
outer_shell_y_length = 2 * (
    pocket_centerward_arc_outer_radius + outer_shell_foam_gap + wall_and_floor_thickness
)


foam_cap_interior_height = outer_shell_foam_gap
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness

foam_cap_lid_pour_radius = 5.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0

# Cap-to-outer-shell joinery: ruthex M3 heat-set inserts + M3 SHCS,
# 6 attachment points per face × 2 faces = 12 inserts / 12 screws.
# Gasket compresses between each cap's mating edge and the outer shell
# (foam-cap-gasket.step). See bom.md for hardware SKUs.
screw_clearance_radius = 1.95  # ⌀[3.9](SCREW_CLEARANCE_DIAMETER) clearance for M3 SHCS shank
insert_pocket_radius = 2.0  # ⌀[4](INSERT_POCKET_DIAMETER) for ruthex M3 short heat-set
insert_pocket_depth = 8.0  # 4 mm insert engagement + 4 mm relief
screw_boss_size = 8.0  # ⌀[8 mm](SCREW_BOSS_SIZE) cylindrical boss at each attachment

# Rounded outer-shell corners. Each corner's exterior wall is a true arc:
# the outer face is a quarter-round of [12 mm](CORNER_ROUND_R) radius, the
# inner face concentric one wall-thickness inboard. The corner boss is
# seated deep IN the corner so its cylinder's outer edge is tangent to the
# EXTERIOR wall arc — the boss fuses right into the outer skin at the corner
# (one wall-thickness of PETG over the insert), the stiffest tie into the
# warp-prone corner. (The reservoir teardrops can make boss radius == fillet
# radius so the boss arc IS the wall; here boss radius ≠ corner radius, so
# the boss can only touch the arc at a point — tangent.)
corner_round_radius = 12.0
# Corner-arc center (corner_round_radius in from each outer face), then the
# boss center steps out along the +diagonal by (exterior-wall-arc radius −
# boss radius) so the boss's outer edge is tangent to the exterior wall arc.
_corner_arc_x = outer_shell_x_length / 2 - corner_round_radius
_corner_arc_y = outer_shell_y_length / 2 - corner_round_radius
_corner_boss_diag_offset = (corner_round_radius - screw_boss_size / 2) / math.sqrt(2)
_corner_boss_x = _corner_arc_x + _corner_boss_diag_offset
_corner_boss_y = _corner_arc_y + _corner_boss_diag_offset

# Mid-long-side bosses offset in X to clear the copper/water-outlet
# slot at x=0; opposite signs at ±Y preserve 180° rotational symmetry
# around the Z axis (balanced gasket compression).
mid_screw_x_offset = 15.0
foam_cap_attachment_xy_positions = (
    [(x_sign * _corner_boss_x, y_sign * _corner_boss_y)
     for x_sign in (1, -1) for y_sign in (1, -1)]
    + [(y_sign * mid_screw_x_offset,
        y_sign * (outer_shell_y_length / 2 - screw_boss_size / 2))
       for y_sign in (1, -1)]
)
gasket_thickness = 2.0
gasket_strip_width = 5.0


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
):
    """Y-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Z and
    starting at `origin`'s Y, extruded in +Y.

    Default height (40 mm) is intentionally larger than every call site's
    exact wall-reach distance. Don't reduce it to the per-hole exact reach
    — looks like an obvious refactor, but the co2_inlet's hole is tangent
    to the support ring's inner curved cylinder (r = 61.5). At the hole's
    outer radius |x| = 3.25 the ring extends to y ≈ -61.41, so an
    exact-reach height of 9 mm (ending at y = -61.5) leaves a ~1.86 mm³
    sliver of ring material in the tube's actual path. The 40 mm overshoot
    reliably clears that. (Flat-wall holes — water_outlet, reservoir
    bulkheads — do tolerate exact-reach face coincidence, but mixing
    exact-reach for some and overshoot for others adds nothing here; the
    40 mm extrude just cuts air past the wall in those cases.)"""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )


def build_slot_punch(
    origin=(0, 0, 0),
    slot_length=1.0,
    slot_diameter=6.5,
    slot_punch_height=40,
):
    """Z-elongated, Y-extruded rounded slot (circle-rect-circle), centered
    at `origin`'s X/Z and starting at `origin`'s Y. Long axis runs along
    world Z. The rounded ends each contribute slot_diameter/2 of additional
    Z reach beyond `slot_length`."""
    x, y, z = origin
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(x, 0, z), offset=y)
        .slot2D(slot_length, slot_diameter, angle=90)
        .extrude(slot_punch_height)
    )


def build_z_axis_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
):
    """Z-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Y and
    starting at `origin`'s Z, extruded in +Z. Same shape as
    `build_hole_punch` but aimed along +Z instead of +Y."""
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
