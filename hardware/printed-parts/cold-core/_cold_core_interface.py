"""Shared interface for the cold-core's geometry modules — workplane
conventions, hole-punch helpers, and the dimensional constants that
every sibling part (foam shell, foam cap stack, reservoir, copper
plugs, coil mandrel) needs to stay in sync against."""

import cadquery as cq

xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
xy_plane_z_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))


def flip_z(world_xz):
    """World (x, z) → (x, -z) for xz_plane_y_up workplane calls. Its 2D
    point args (moveTo, lineTo, polyline, radiusArc, threePointArc, ...)
    interpret their second component as -world Z."""
    x, z = world_xz
    return (x, -z)


# All structural walls and floors are 2 mm PETG.
wall_and_floor_thickness = 2.0
hole_shift_from_edge = 15.0


# Reservoir-pocket centerward arc. Each pocket's centerward wall (the
# one facing the cold-core axis) is curved; the wall's cavity-side face
# rides on a cylinder of this radius (centered on the cold-core axis).
# The wall's tank-side face sits one wall-thickness inboard at radius
# (pocket_centerward_arc_outer_radius − wall_and_floor_thickness), giving
# 7 mm of radial clearance between the tank and the wall — room for the
# 1/4" ACR copper coil + thermal tape + slack.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
pocket_centerward_arc_outer_radius = (
    tank_outer_radius + coil_radial_clearance + wall_and_floor_thickness
)

# Foam-shell outer height. Tank height + 30 mm above for top-side elbow
# fittings + 30 mm below for bottom-side elbow fittings + 1 mm
# wall-thickness compensation.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
foam_shell_outer_height = (
    tank_height + below_tank_elbows_height + above_tank_elbows_height + 1.0
)

tank_support_ring_height = 30.0

# Bag pocket. Width tracks pocket_centerward_arc_outer_radius so the
# pocket's ±Z outboard faces are tangent to the cylinder the centerward
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
bag_pocket_z_inner_max = bag_pocket_width / 2 - wall_and_floor_thickness
bag_pocket_floor_top_y = wall_and_floor_thickness
bag_pocket_walls_top_y = foam_shell_outer_height

# Matches the reservoir's outer +X × ±Z fillet (R=6) with reservoir_clearance
# on top, so the reservoir's outer arc slides into a snugly-mated arc on
# the pocket's inner corner with uniform clearance.
bag_pocket_corner_inner_radius = 6.5

reservoir_clearance = 0.5
reservoir_floor_thickness = 4.0
bulkhead_pocket_diameter = 23.0

# Y of the bulkhead NUT cavity center — anchored to the floor's low point.
# Computed so the nut cavity's lowest reach (washer counterbore at
# ⌀22.3) sits right at the reservoir floor's wet surface, leaving the
# full reservoir_floor_thickness (4 mm) of PETG below it as the fluid
# barrier. The nut (washer + hex piece) is the deepest feature in this
# area and the floor MUST stay 4 mm at this low point.
reservoir_bulkhead_nut_y = (
    bag_pocket_floor_top_y
    + reservoir_clearance
    + reservoir_floor_thickness
    + bulkhead_pocket_diameter / 2
)

# 2026-05-16 print test: the bulkhead body itself needs to sit 1 mm
# above the nut. Achieved by lifting the bulkhead axis 1 mm above the
# nut cavity center; the bulkhead's threading section then engages the
# nut at a 1 mm offset, well within the ⌀17 panel hole's clearance
# around the ⌀~13 threaded section. The nut cavity stays at
# reservoir_bulkhead_nut_y (the floor low point); everything anchored
# to the bulkhead axis (chamber, panel hole, TPU seals, foam-shell
# pass-through, wet/dry slopes, dry slab, rod body boss) lifts with it.
bulkhead_axis_lift_above_nut = 1.0
reservoir_bulkhead_port_y = reservoir_bulkhead_nut_y + bulkhead_axis_lift_above_nut
reservoir_bulkhead_port_x = (bag_pocket_far_inner_x + pocket_centerward_arc_outer_radius) / 2

# Outer footprint shared by the outer shell, the foam cap, and the
# foam cap lid (must be coplanar at the corners so the pin bosses
# line up).
outer_shell_foam_gap = 16.0
bag_pocket_outermost_x = (
    pocket_centerward_arc_outer_radius + bag_pocket_depth - wall_and_floor_thickness
)
outer_shell_x_length = 2 * (
    bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness
)
outer_shell_z_length = 2 * (
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
screw_clearance_radius = 1.95   # ⌀3.9 clearance for M3 SHCS shank
insert_pocket_radius   = 2.0    # ⌀4.0 for ruthex M3 short heat-set
insert_pocket_depth    = 8.0    # 4 mm insert engagement + 4 mm relief
screw_boss_size        = 8.0    # 8 × 8 mm square pillar at each attachment

# Mid-long-side bosses offset in X to clear the copper/water-outlet
# slot at x=0; opposite signs at ±Z preserve 180° rotational symmetry
# around the Y axis (balanced gasket compression).
mid_screw_x_offset = 15.0
foam_cap_attachment_xz_positions = (
    [(x_sign * (outer_shell_x_length / 2 - screw_boss_size / 2),
      z_sign * (outer_shell_z_length / 2 - screw_boss_size / 2))
     for x_sign in (1, -1) for z_sign in (1, -1)]
    + [(z_sign * mid_screw_x_offset,
        z_sign * (outer_shell_z_length / 2 - screw_boss_size / 2))
       for z_sign in (1, -1)]
)
gasket_thickness   = 2.0
gasket_strip_width = 5.0


def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    # Default height (40 mm) is intentionally larger than every call
    # site's exact wall-reach distance.  Don't reduce it to the
    # per-hole exact reach — looks like an obvious refactor, but the
    # co2_inlet's hole is tangent to the support ring's inner curved
    # cylinder (r = 61.5).  At the hole's outer radius |x| = 3.25 the
    # ring extends to z ≈ -61.41, so an exact-reach height of 9 mm
    # (ending at z = -61.5) leaves a ~1.86 mm³ sliver of ring material
    # in the tube's actual path.  The 40 mm overshoot reliably clears
    # that.  (Flat-wall holes — water_outlet, reservoir bulkheads —
    # do tolerate exact-reach face coincidence, but mixing exact-reach
    # for some and overshoot for others adds nothing here; the 40 mm
    # extrude just cuts air past the wall in those cases.)
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )


def build_a_slot_punch(
    origin=(0, 0, 0),
    slot_length=1.0,
    slot_diameter=6.5,
    slot_punch_height=40,
):
    """Y-elongated, Z-extruded rounded slot (circle-rect-circle), centered
    at `origin`. Long axis runs along world Y. The rounded ends each
    contribute slot_diameter/2 of additional Y reach beyond `slot_length`."""
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .slot2D(slot_length, slot_diameter, angle=90)
        .extrude(slot_punch_height)
    )


def build_a_y_axis_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    """Y-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Z and
    starting at `origin`'s Y, extruded in +Y. Mirror of
    `build_a_hole_punch` along the Y axis instead of Z."""
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=origin, offset=origin[1])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )
