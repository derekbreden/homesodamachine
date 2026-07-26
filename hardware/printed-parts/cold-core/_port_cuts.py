"""Port-hole and slot cuts through the foam shell — water outlet, two
flavor-line pass-throughs, CO2 inlet bore, and the shared
copper/water inlet slot."""

import cadquery as cq

from world_workplane import xz_plane_y_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    hole_shift_from_edge,
    pocket_centerward_arc_outer_radius,
    outer_shell_y_length,
    foam_shell_outer_height,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    co2_inlet_x,
    port_hole_radius,
    build_hole_punch,
    build_slot_punch,
    cut_pour_band_pass_through,
)

# Z of the through-foam ports — water outlet and CO2 inlet, both bottom-plate
# lines leaving through the −Y wall, hole_shift_from_edge in from the +Z outer
# face. One band of the shell's height carries both, side by side in X.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# −Y (front, toward the user) start of the water-outlet and copper/water-inlet
# cuts — 20 mm inboard of the bag-pocket −Y wall outer face.
minus_y_wall_plug_port_y = -(pocket_centerward_arc_outer_radius - 20)

# The three circular port holes are the project's ⌀[6.5](PORT_HOLE_DIAMETER) standard.
water_outlet_xyz = (0, minus_y_wall_plug_port_y, front_face_port_z)

# CO2 inlet — the bore starts on the bottom plate's own centre line and runs
# −Y, so it is stated where the port it serves is rather than at some clearance
# inboard of the ring. Long enough to leave the outer wall.
co2_inlet_xyz = (co2_inlet_x, 0.0, front_face_port_z)
co2_inlet_bore_length = outer_shell_y_length / 2 + wall_and_floor_thickness

# Flavor-line pass-throughs — each reservoir's 1/4" LLDPE outlet line out
# of the pocket, across the pour band and through the −Y outer-shell wall,
# at bulkhead_elbow_exit_z (level out of the elbow's lateral port). The
# pocket-wall bore sits inboard of the bulkhead axis, opposite the outboard
# reed cable hole — the two ⌀[6.5](PORT_HOLE_DIAMETER) holes
# [12](FLAVOR_REED_PITCH) mm apart center-to-center with PETG between them.
flavor_line_hole_offset_from_bulkhead_x = 8.0
flavor_line_hole_x = reservoir_bulkhead_port_x - flavor_line_hole_offset_from_bulkhead_x

# Where the line leaves the shell. Far enough inboard that it emerges clear
# of the condenser+fan block standing against the cabinet's +X wall, and
# under the one window in the manifold tray stack above, so the line falls
# straight down the core's front face rather than traversing beneath the
# stack. Inside the shell it reaches this X along the pour band.
flavor_line_shell_hole_x = 47.0

flavor_line_plus_x_xyz = (+flavor_line_hole_x, reservoir_bulkhead_port_y, bulkhead_elbow_exit_z)
flavor_line_minus_x_xyz = (-flavor_line_hole_x, reservoir_bulkhead_port_y, bulkhead_elbow_exit_z)


def cut_circular_port_holes(foam_shell):
    # The water outlet crosses the −Y wall in a single bore: no pocket
    # stands behind it, so only the outer shell is in its way.
    foam_shell = foam_shell.cut(
        build_hole_punch(origin=water_outlet_xyz, hole_punch_radius=port_hole_radius, direction=-1)
    )
    # Each flavor line pierces two walls at two different X, joined by its
    # own run along the pour band.
    for side in (+1, -1):
        foam_shell = cut_pour_band_pass_through(
            foam_shell,
            pocket_hole_x=side * flavor_line_hole_x,
            shell_hole_x=side * flavor_line_shell_hole_x,
            y=reservoir_bulkhead_port_y,
            z=bulkhead_elbow_exit_z,
            hole_punch_radius=port_hole_radius,
        )
    return foam_shell


def cut_co2_inlet(foam_shell):
    """CO2 inlet — one ⌀[6.5](PORT_HOLE_DIAMETER) bore at x = [19.05](CO2_INLET_X),
    run from the bottom plate's centre line straight out through the tank support
    ring and the −Y outer wall, level with the water outlet at
    z = [17](FRONT_FACE_PORT_Z). It crosses two bands of material — the ring, and
    the wall — with open cavity inboard of them and between them, which is where
    the vessel's TAISHER elbow and its PP010822E adapter hang. The line is pushed
    in from outside once the vessel is seated and bottoms in that collet, so
    nothing is made up in-cavity and nothing arrives from above."""
    return foam_shell.cut(
        build_hole_punch(
            origin=co2_inlet_xyz,
            hole_punch_radius=port_hole_radius,
            hole_punch_height=co2_inlet_bore_length,
            direction=-1,
        )
    )


def cut_slot_for_copper_and_water_inlet(foam_shell):
    """Z-elongated slot through the outer-shell −Y wall, shared by the
    two copper-line plugs and the water-inlet plug, slid down in from
    above. The rounded top tapers above the foam-shell top edge, so the
    straight portion reaches the edge exactly with no sliver left."""
    slot_diameter = 6.5
    slot_z_bottom = 42.0
    slot_z_top = foam_shell_outer_height + slot_diameter / 2
    slot_z_center = (slot_z_top + slot_z_bottom) / 2.0
    slot_punch = build_slot_punch(
        origin=(0, minus_y_wall_plug_port_y, slot_z_center),
        slot_length=slot_z_top - slot_z_bottom,
        slot_diameter=slot_diameter,
        direction=-1,
    )
    return foam_shell.cut(slot_punch)
