"""Port-hole and slot cuts through the foam shell — water outlet, two
flavor-line pass-throughs, CO2 inlet doorway, and the shared
copper/water inlet slot."""

import cadquery as cq

from world_workplane import xz_plane_y_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    hole_shift_from_edge,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    port_hole_radius,
    build_hole_punch,
    build_slot_punch,
)

# Z of the through-foam ports — water outlet and CO2 inlet bore, both
# through the foam shell, hole_shift_from_edge in from the +Z outer face.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# CO2 inlet round bore — seats the JG PP0308E elbow's ⌀15 body for its
# in-cavity 90° turn, dropped one mm below front_face_port_z.
co2_inlet_bore_radius = 9.0
co2_inlet_bore_z = front_face_port_z - 1.0

# +Y start of the water-outlet and copper/water-inlet cuts — 20 mm
# inboard of the bag-pocket +Y wall outer face.
plus_y_wall_plug_port_y = pocket_centerward_arc_outer_radius - 20

# The three circular port holes are the project's ⌀[6.5](PORT_HOLE_DIAMETER) standard.
water_outlet_xyz = (0, plus_y_wall_plug_port_y, front_face_port_z)

# Flavor-line pass-throughs — each reservoir's 1/4" LLDPE outlet line
# through the +Y bag-pocket wall and the +Y outer-shell wall, at
# bulkhead_elbow_exit_z (level out of the elbow's lateral port). Inboard
# of the bulkhead axis, opposite the outboard reed cable hole — the two
# ⌀[6.5](PORT_HOLE_DIAMETER) holes 16 mm apart center-to-center with PETG between them.
flavor_line_hole_offset_from_bulkhead_x = 8.0
flavor_line_hole_x = reservoir_bulkhead_port_x - flavor_line_hole_offset_from_bulkhead_x
flavor_line_plus_x_xyz = (+flavor_line_hole_x, reservoir_bulkhead_port_y, bulkhead_elbow_exit_z)
flavor_line_minus_x_xyz = (-flavor_line_hole_x, reservoir_bulkhead_port_y, bulkhead_elbow_exit_z)


def cut_circular_port_holes(foam_shell):
    for anchor in (water_outlet_xyz, flavor_line_plus_x_xyz, flavor_line_minus_x_xyz):
        foam_shell = foam_shell.cut(build_hole_punch(origin=anchor, hole_punch_radius=port_hole_radius))
    return foam_shell


def cut_co2_inlet(foam_shell):
    """CO2 inlet — a doorway-shaped cut at x = 0, y = [−70.5](CO2_DOORWAY_Y): a [⌀18](CO2_INLET_BORE_D)
    round bore at z = [16](CO2_INLET_BORE_Z) (seating the JG PP0308E elbow's ⌀15 body for
    its in-cavity 90° turn) over a rectangular slot down to the floor's
    top face at z = [2](FLOOR_TOP_Z), the elbow entered at an angle from above. The
    foam-shell floor below z = [2](FLOOR_TOP_Z) stays intact."""
    # Pocket-side face of the bag-pocket −Y wall.
    doorway_y = -(pocket_centerward_arc_outer_radius - wall_and_floor_thickness)
    bore_radius = co2_inlet_bore_radius
    bore_z = co2_inlet_bore_z
    round_bore = build_hole_punch(
        origin=(0, doorway_y, bore_z),
        hole_punch_radius=bore_radius,
    )
    slot_z_bottom = wall_and_floor_thickness
    slot_z_top = bore_z
    slot_z_center = (slot_z_top + slot_z_bottom) / 2.0
    slot_punch = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, slot_z_center), offset=doorway_y)
        .rect(2 * bore_radius, slot_z_top - slot_z_bottom)
        .extrude(40)
    )
    return foam_shell.cut(round_bore).cut(slot_punch)


def cut_slot_for_copper_and_water_inlet(foam_shell):
    """Z-elongated slot through the outer-shell +Y wall, shared by the
    two copper-line plugs and the water-inlet plug, slid down in from
    above. The rounded top tapers above the foam-shell top edge, so the
    straight portion reaches the edge exactly with no sliver left."""
    slot_diameter = 6.5
    slot_z_bottom = 42.0
    slot_z_top = foam_shell_outer_height + slot_diameter / 2
    slot_z_center = (slot_z_top + slot_z_bottom) / 2.0
    slot_punch = build_slot_punch(
        origin=(0, plus_y_wall_plug_port_y, slot_z_center),
        slot_length=slot_z_top - slot_z_bottom,
        slot_diameter=slot_diameter,
    )
    return foam_shell.cut(slot_punch)
