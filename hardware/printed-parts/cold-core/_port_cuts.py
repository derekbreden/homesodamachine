"""Port-hole and slot cuts through the foam shell — water outlet, two
flavor-line pass-throughs, CO2 inlet bore, and the shared
copper/PRV-vent slot.

All but two open on the shell's −X FACE, on the port lane
(`_cold_core_interface`, §"The front face, and the lane that reaches it"). None of
them reaches that face head-on: each is two features — an inner bore where the
fitting inside points, and a station on the front field — with the line turning
through the lane between them, west to the wall and up it to the station.

The two are reservoir B's flavor line and the vessel's carbonated-water outlet, both of
which leave by the TOP. They are the same shape — an inner bore, a band, a second feature
— with the second feature in the cap (`cap_conduits`) rather than in this wall, and the
band a climb rather than a reach: B's is the +Y band and the carb water's is the port lane
itself, which every front-field line crosses and only this one goes up.
"""

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
    co2_inlet_y,
    port_hole_radius,
    port_lane_mid_y,
    west_lane_mid_y,
    front_port_z,
    build_hole_punch,
    build_slot_punch,
    cut_front_exit,
    cut_pour_band_pass_through,
    port_to_shell,
)

# [17](FRONT_FACE_PORT_Z) — Z of the vessel's two bottom-plate lines where they
# leave their own fittings: the water outlet and the CO2 inlet, both
# hole_shift_from_edge in from the +Z outer face of the shell's floor. One band of
# the shell's height carries both, one either side of the plate's own axis in Y. Both land
# on the lane here and neither crosses the wall here: the CO2 climbs a little way to its
# front-field station (`front_port_z`) and turns west, the water outlet climbs the whole
# shell to the cap. So the lane holds them apart from the point they share.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# −Y (front, toward the user) start of the water-outlet and copper/PRV-vent
# cuts — 20 mm inboard of the bag-pocket −Y wall outer face.
minus_y_wall_plug_port_y = -(pocket_centerward_arc_outer_radius - 20)

# The three circular port holes are the project's ⌀[6.5](PORT_HOLE_DIAMETER) standard.
water_outlet_xyz = (0, minus_y_wall_plug_port_y, front_face_port_z)

# CO2 inlet — the inner bore starts at the bottom plate's own lane-side port and runs
# −Y down the shell's centreline, so it is stated where the port it serves is rather than
# at some clearance inboard of the ring. It crosses the tank support ring and stops on the
# lane; the line turns there and runs west to its own front-field station.
co2_inlet_xyz = (0.0, co2_inlet_y, front_face_port_z)

# Flavor-line pass-throughs — each reservoir's 1/4" LLDPE outlet line out of the
# pocket at bulkhead_elbow_exit_z (level out of the elbow's lateral port). The two
# leave by OPPOSITE ±Y bands, because the fittings they feed stand at opposite ends
# of the machine: A crosses its pocket's −Y wall onto the port lane and out the front
# field, B crosses its pocket's +Y wall onto the west lane and climbs to the cap.
#
# A's bore sits inboard of the bulkhead axis, opposite the outboard reed cable hole
# — the two ⌀[6.5](PORT_HOLE_DIAMETER) holes [12](FLAVOR_REED_PITCH) mm apart
# center-to-center with PETG between them. That step is the reed cable's price, and
# B's bore does not pay it: nothing else crosses the +Y wall, so B's stands on the
# BULKHEAD'S OWN AXIS and its elbow, the wall bore and the tube are one straight line
# across the void — the same reading the CO2 inlet's bore has.
flavor_line_hole_offset_from_bulkhead_x = 8.0
flavor_line_hole_x = reservoir_bulkhead_port_x - flavor_line_hole_offset_from_bulkhead_x

flavor_line_plus_x_xyz = (+flavor_line_hole_x, reservoir_bulkhead_port_y, bulkhead_elbow_exit_z)
flavor_line_minus_x_xyz = (-reservoir_bulkhead_port_x, -reservoir_bulkhead_port_y,
                           bulkhead_elbow_exit_z)


def cut_circular_port_holes(foam_shell):
    # The water outlet leaves the vessel's bottom plate on the tank's own centre
    # line and turns onto the lane: no pocket stands behind it, so its inner bore
    # is one reach from the fitting out to the lane. It has no second bore in the
    # shell either — the lane it lands in runs clear to the shell's open top at every
    # height, and the feature at the far end of it is the cap's `carb-water-out`
    # conduit. Every other line on this lane turns west here; this one turns up.
    foam_shell = foam_shell.cut(
        build_hole_punch(
            origin=water_outlet_xyz,
            hole_punch_radius=port_hole_radius,
            hole_punch_height=water_outlet_xyz[1] - port_lane_mid_y,
            direction=-1,
        )
    )
    # Reservoir A pierces its pocket's −Y wall where its bulkhead elbow points, and the
    # −X wall at its own station; the port lane joins the two.
    foam_shell = cut_pour_band_pass_through(
        foam_shell,
        pocket_hole_x=flavor_line_plus_x_xyz[0],
        y=flavor_line_plus_x_xyz[1],
        z=flavor_line_plus_x_xyz[2],
        exit_z=front_port_z("reservoir-a"),
        hole_punch_radius=port_hole_radius,
    )
    # Reservoir B pierces its pocket's +Y wall and stops on the WEST LANE. It has no
    # second bore in the shell: the band it lands in runs clear to the shell's open top,
    # and the feature at the far end of it is the cap's `reservoir-b` conduit. Same two
    # features and a band between them; the second one is printed in the next part up.
    return foam_shell.cut(
        build_hole_punch(
            origin=flavor_line_minus_x_xyz,
            hole_punch_radius=port_hole_radius,
            hole_punch_height=west_lane_mid_y - flavor_line_minus_x_xyz[1],
            direction=+1,
        )
    )


def cut_co2_inlet(foam_shell):
    """CO2 inlet — a ⌀[6.5](PORT_HOLE_DIAMETER) bore on the shell's centreline,
    run from the bottom plate's lane-side port at y = [-19.05](CO2_INLET_Y) out through
    the tank support ring to the port lane, plus its own station on the front field.
    The port, its elbow, the ring bore and the wall bore stand on one line. It crosses the ring with open
    cavity inboard of it, which is where the vessel's TAISHER elbow and its PP010822E
    adapter hang. The line is pushed in from outside once the vessel is seated, along
    the lane and in through the ring, and bottoms in that collet — so nothing is made
    up in-cavity and nothing arrives from above."""
    foam_shell = foam_shell.cut(
        build_hole_punch(
            origin=co2_inlet_xyz,
            hole_punch_radius=port_hole_radius,
            hole_punch_height=co2_inlet_xyz[1] - port_lane_mid_y,
            direction=-1,
        )
    )
    return cut_front_exit(foam_shell, z=front_port_z("co2-in"),
                          hole_punch_radius=port_hole_radius)


def cut_slot_for_copper_and_prv_vent(foam_shell):
    """Z-elongated slot through the outer-shell −X wall, shared by the
    two copper lines and the PRV vent, plugged by a stack slid down in from
    above. Built in the PORT FRAME — where the wall it crosses is a −Y wall and the
    slot runs lateral in x, which is the frame the copper plugs themselves are
    authored in — then carried onto the lane by `port_to_shell`, so the slot and the
    stack that fills it are one reading. The rounded top tapers above the foam-shell
    top edge, so the straight portion reaches the edge exactly with no sliver left.

    Its bottom stands clear of the front port field below it: the three lines this
    slot carries all cross the wall above every circular station, and
    `copper_plugs.lowest_copper_z` is derived from that."""
    from copper_plugs import slot_z_bottom, slot_width_x, outer_wall_inner_y

    slot_z_top = foam_shell_outer_height + slot_width_x / 2
    slot_z_center = (slot_z_top + slot_z_bottom) / 2.0
    overshoot = 1.0                                    # a through-cut, both faces cleared
    slot_punch = build_slot_punch(
        origin=(0, outer_wall_inner_y + overshoot, slot_z_center),
        slot_length=slot_z_top - slot_z_bottom,
        slot_diameter=slot_width_x,
        slot_punch_height=wall_and_floor_thickness + 2.0 * overshoot,
        direction=-1,
    )
    return foam_shell.cut(port_to_shell(slot_punch.val()))
