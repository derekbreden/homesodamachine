"""Port-hole and slot cuts through the foam shell — water outlet, two
reservoir bulkhead pass-throughs, CO2 inlet doorway, and the shared
copper/water inlet slot."""

import cadquery as cq

from _cold_core_interface import (
    xy_plane_z_up,
    wall_and_floor_thickness,
    hole_shift_from_edge,
    tank_copper_shell_radius,
    tank_copper_shell_height,
    bag_pocket_width,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    build_a_hole_punch,
    build_a_slot_punch,
)

# All circular port holes through the foam shell: Z-axis ⌀6.5 × 40 mm
# cylindrical cuts, starting at the given z and extending in +Z.
#   - water_outlet:            outer +Z wall
#   - reservoir_bulkhead_±X:   bag-pocket +Z wall (and outer +Z wall;
#     the bulkhead body sits in the bag-pocket wall, the dry-side tube
#     exits through the outer wall along the same axis)
#
# The CO2 inlet through the −Z support arch is cut separately by
# `cut_co2_inlet()` — its bore is ⌀16 (vs ⌀6.5 here) to house an
# in-cavity 90° push-to-connect elbow, so it doesn't fit this list's
# default radius.
CIRCULAR_PORT_HOLES = [
    # (x, y, z)
    (0,                          hole_shift_from_edge + wall_and_floor_thickness,    tank_copper_shell_radius - 20),
    (+reservoir_bulkhead_port_x, reservoir_bulkhead_port_y,                          bag_pocket_width / 2 - 10),
    (-reservoir_bulkhead_port_x, reservoir_bulkhead_port_y,                          bag_pocket_width / 2 - 10),
]


def cut_circular_port_holes(foam_shell):
    for (x, y, z) in CIRCULAR_PORT_HOLES:
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=(x, y, z)))
    return foam_shell


def cut_co2_inlet(foam_shell):
    """CO2 inlet through the −Z support arch: a doorway-shaped cut —
    ⌀16 round bore on top, rectangular slot below it down to the
    support arch's bottom face. The bore seats a JG PP0308E elbow
    (⌀15 body) for the in-cavity 90° turn; the slot exists for
    angled insertion from above (the elbow's perpendicular legs
    can't enter along the bore axis and the back wall is solid).
    The slot's bottom is flush with the floor's top face — the
    foam-shell floor below stays intact."""
    co2_inlet_z_start = -(tank_copper_shell_radius - wall_and_floor_thickness)
    co2_inlet_y_center = hole_shift_from_edge + wall_and_floor_thickness
    bore_radius = 8.0
    round_bore = build_a_hole_punch(
        origin=(0, co2_inlet_y_center, co2_inlet_z_start),
        hole_punch_radius=bore_radius,
    )
    slot_width    = 2 * bore_radius
    slot_y_top    = co2_inlet_y_center
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
    slot_y_top    = tank_copper_shell_height + slot_diameter / 2
    slot_length   = slot_y_top - slot_y_bottom
    slot_y_center = (slot_y_top + slot_y_bottom) / 2.0
    slot_z_offset = tank_copper_shell_radius - 20
    slot_x_offset = 0
    slot_punch = build_a_slot_punch(
        origin=(slot_x_offset, slot_y_center, slot_z_offset),
        slot_length=slot_length,
        slot_diameter=slot_diameter,
    )
    return foam_shell.cut(slot_punch)
