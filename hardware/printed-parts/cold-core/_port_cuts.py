"""Port-hole and slot cuts through the foam shell — water outlet, two
flavor-line pass-throughs, CO2 inlet doorway, and the shared
copper/water inlet slot."""

import cadquery as cq

from world_workplane import xz_plane_y_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    hole_shift_from_edge,
    pocket_centerward_arc_outer_radius,
    tank_support_ring_height,
    foam_shell_outer_height,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    port_hole_radius,
    build_hole_punch,
    build_slot_punch,
    cut_pour_band_pass_through,
)

# Z of the through-foam ports — water outlet and CO2 inlet notch, both
# through the foam shell, hole_shift_from_edge in from the +Z outer face.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# CO2 inlet notch — clears the JG PP0308E elbow's ⌀15 body for its in-cavity
# 90° turn. Open to the ring's top plateau: the elbow is made up on the
# vessel's bottom-plate elbow at the bench and descends through the notch as
# the vessel seats, so no shell material may arch over it.
co2_inlet_notch_half_width = 9.0
co2_inlet_notch_z_top = wall_and_floor_thickness + tank_support_ring_height

# CO2 inlet doorway — pocket-side face of the bag-pocket +Y (rear, toward
# the rear panel) centerward wall; the cut runs inward toward the cavity (−Y).
co2_doorway_y = pocket_centerward_arc_outer_radius - wall_and_floor_thickness

# −Y (front, toward the user) start of the water-outlet and copper/water-inlet
# cuts — 20 mm inboard of the bag-pocket −Y wall outer face.
minus_y_wall_plug_port_y = -(pocket_centerward_arc_outer_radius - 20)

# The three circular port holes are the project's ⌀[6.5](PORT_HOLE_DIAMETER) standard.
water_outlet_xyz = (0, minus_y_wall_plug_port_y, front_face_port_z)

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
    """CO2 inlet — a [18](CO2_NOTCH_W)-wide notch at x = 0, cut inward (−Y) from
    y = [78.5](CO2_DOORWAY_Y) through the tank support ring, running from the floor's
    top face at z = [2](FLOOR_TOP_Z) clear through the ring's top plateau at
    z = [32](CO2_NOTCH_Z_TOP). Nothing arches over it: the JG PP0308E elbow is made up
    on the vessel's bottom-plate elbow before the vessel is lowered, and rides down
    the notch with it. The foam-shell floor below z = [2](FLOOR_TOP_Z) stays intact."""
    # Pocket-side face of the bag-pocket +Y (rear) wall; the cut runs inward (−Y).
    notch_z_bottom = wall_and_floor_thickness
    notch_z_top = co2_inlet_notch_z_top
    notch_z_center = (notch_z_top + notch_z_bottom) / 2.0
    notch_punch = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, notch_z_center), offset=co2_doorway_y)
        .rect(2 * co2_inlet_notch_half_width, notch_z_top - notch_z_bottom)
        .extrude(-40)
    )
    return foam_shell.cut(notch_punch)


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
