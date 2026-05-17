"""Port-hole and slot cuts through the foam shell — water outlet, two
reservoir bulkhead pass-throughs, CO2 inlet doorway, and the shared
copper/water inlet slot."""

import cadquery as cq

from _cold_core_interface import (
    xy_plane_z_up,
    wall_and_floor_thickness,
    hole_shift_from_edge,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    reservoir_bulkhead_port_z,
    build_a_hole_punch,
    build_a_slot_punch,
)

# Y at which every port that exits through the bag-pocket front (+Y)
# face sits — water outlet, CO2 inlet, and the shared copper/water
# inlet slot's bottom anchor. hole_shift_from_edge from the +Y outer
# face, plus the wall thickness it passes through.
front_face_port_y = hole_shift_from_edge + wall_and_floor_thickness

# Z of the water outlet and the copper/water inlet slot — both pass
# through the bag-pocket +Z wall, 20 mm inboard of its outer face.
plus_z_wall_plug_port_z = pocket_centerward_arc_outer_radius - 20

# Z-axis ⌀6.5 × 40 mm cylindrical cuts through the foam shell, each
# starting at its anchor and extending in +Z. The CO2 inlet is cut
# separately by `cut_co2_inlet()`: its bore is ⌀16 to house an
# in-cavity 90° push-to-connect elbow, so it doesn't share this radius.
water_outlet_xyz = (0, front_face_port_y, plus_z_wall_plug_port_z)
reservoir_bulkhead_plus_x_xyz = (+reservoir_bulkhead_port_x, reservoir_bulkhead_port_y, reservoir_bulkhead_port_z)
reservoir_bulkhead_minus_x_xyz = (-reservoir_bulkhead_port_x, reservoir_bulkhead_port_y, reservoir_bulkhead_port_z)


def cut_circular_port_holes(foam_shell):
    for anchor in (water_outlet_xyz, reservoir_bulkhead_plus_x_xyz, reservoir_bulkhead_minus_x_xyz):
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=anchor))
    return foam_shell


def cut_co2_inlet(foam_shell):
    """CO2 inlet — a doorway-shaped cut at x = 0, z = −70.5: a ⌀16
    round bore at y = 17 (where the JG PP0308E elbow's ⌀15 body
    seats for its in-cavity 90° turn) with a rectangular slot below
    it down to the floor's top face at y = 2. The slot exists for
    angled insertion from above — the elbow's perpendicular legs
    can't enter along the bore axis. The cut clears a passage from
    just outside the support ring (at z = −70.5) inward; the foam-
    shell floor below y = 2 stays intact."""
    co2_inlet_z_start = -(pocket_centerward_arc_outer_radius - wall_and_floor_thickness)
    co2_inlet_y_center = front_face_port_y
    bore_radius = 8.0
    round_bore = build_a_hole_punch(
        origin=(0, co2_inlet_y_center, co2_inlet_z_start),
        hole_punch_radius=bore_radius,
    )
    slot_width = 2 * bore_radius
    slot_y_top = co2_inlet_y_center
    slot_y_bottom = wall_and_floor_thickness
    slot_y_center = (slot_y_top + slot_y_bottom) / 2.0
    slot_extrude_z = 40
    slot_punch = (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(0, slot_y_center, co2_inlet_z_start), offset=co2_inlet_z_start)
        .rect(slot_width, slot_y_top - slot_y_bottom)
        .extrude(slot_extrude_z)
    )
    return foam_shell.cut(round_bore).cut(slot_punch)


def cut_slot_for_copper_and_water_inlet(foam_shell):
    """Y-elongated slot through the outer-shell +Z wall, shared by the
    two copper-line plugs and the water-inlet plug — plugs are slid
    down in from above. slot_y_top is pushed slot_diameter/2 past the
    wall's top edge so the rounded top tapers ABOVE the wall — the
    straight portion reaches the wall's top exactly, no sliver left."""
    slot_diameter = 6.5
    slot_y_bottom = 42.0
    slot_y_top = foam_shell_outer_height + slot_diameter / 2
    slot_length = slot_y_top - slot_y_bottom
    slot_y_center = (slot_y_top + slot_y_bottom) / 2.0
    slot_z_offset = plus_z_wall_plug_port_z
    slot_x_offset = 0
    slot_punch = build_a_slot_punch(
        origin=(slot_x_offset, slot_y_center, slot_z_offset),
        slot_length=slot_length,
        slot_diameter=slot_diameter,
    )
    return foam_shell.cut(slot_punch)
