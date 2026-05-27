"""Port-hole and slot cuts through the foam shell — water outlet, two
reservoir bulkhead pass-throughs, CO2 inlet doorway, and the shared
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
    reservoir_bulkhead_port_z,
    port_hole_radius,
    build_hole_punch,
    build_slot_punch,
)

# Z at which the through-foam ports sit — water outlet and CO2 inlet
# bore both pass through the foam shell at this Z. hole_shift_from_edge
# from the +Z outer face, plus the wall thickness they pass through.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# Y at which the water outlet and the copper/water inlet slot start
# their +Y extrusion — 20 mm inboard of the bag-pocket +Y wall outer
# face. Each cut tool extrudes far enough past the outer-shell +Y
# wall to clear it.
plus_y_wall_plug_port_y = pocket_centerward_arc_outer_radius - 20

# The three circular port holes are the project's ⌀6.5 standard. The
# CO2 inlet is separate (`cut_co2_inlet`) because its bore is ⌀16
# (in-cavity 90° push-to-connect elbow), not ⌀6.5.
water_outlet_xyz = (0, plus_y_wall_plug_port_y, front_face_port_z)
reservoir_bulkhead_plus_x_xyz = (+reservoir_bulkhead_port_x, reservoir_bulkhead_port_y, reservoir_bulkhead_port_z)
reservoir_bulkhead_minus_x_xyz = (-reservoir_bulkhead_port_x, reservoir_bulkhead_port_y, reservoir_bulkhead_port_z)


def cut_circular_port_holes(foam_shell):
    for anchor in (water_outlet_xyz, reservoir_bulkhead_plus_x_xyz, reservoir_bulkhead_minus_x_xyz):
        foam_shell = foam_shell.cut(build_hole_punch(origin=anchor, hole_punch_radius=port_hole_radius))
    return foam_shell


def cut_co2_inlet(foam_shell):
    """CO2 inlet — a doorway-shaped cut at x = 0, y = −70.5: a ⌀16
    round bore at z = 17 (where the JG PP0308E elbow's ⌀15 body
    seats for its in-cavity 90° turn) with a rectangular slot below
    it down to the floor's top face at z = 2. The slot exists for
    angled insertion from above — the elbow's perpendicular legs
    can't enter along the bore axis. The cut clears a passage from
    just outside the support ring (at y = −70.5) inward; the foam-
    shell floor below z = 2 stays intact."""
    # Y at which the doorway starts cutting — the pocket-side face of
    # the bag-pocket −Y wall. Bore and slot extrude in +Y from here.
    doorway_y = -(pocket_centerward_arc_outer_radius - wall_and_floor_thickness)
    bore_radius = 9.0
    bore_z = front_face_port_z - 1.0
    round_bore = build_hole_punch(
        origin=(0, doorway_y, bore_z),
        hole_punch_radius=bore_radius,
    )
    # Slot below the bore: same X-width as the bore (diameter), running
    # from the foam-shell floor's top face up to the bore center.
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
    two copper-line plugs and the water-inlet plug — plugs are slid
    down in from above. slot_z_top is pushed slot_diameter/2 past the
    foam-shell top edge so the rounded top tapers ABOVE the wall — the
    straight portion reaches the top exactly, no sliver left."""
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
