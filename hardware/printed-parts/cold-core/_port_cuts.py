"""Port-hole and slot cuts through the foam shell — the two reservoir draws, the
CO2 inlet bore, and the shared copper/PRV-vent slot.

EVERY FLUID LINE LEAVES BY THE TOP. Each is an inner bore — the project's
⌀[6.5](PORT_HOLE_DIAMETER) standard, sized for a tight 1/4" OD tube fit — where the
fitting inside points, then a band, then a conduit in the cap (`cap_conduits`) at the
far end of it, the band a climb rather than a reach. Reservoir A's is the −Y band (the port lane),
reservoir B's the +Y band, and the CO2's is the port lane run the other way: its
line comes DOWN from the cap and this bore is where it arrives.

The carbonated-water outlet has no bore here at all. It crosses the tank support
ring at one of the ring's own slots, on the column its cap conduit stands over —
`water_outlet_ring_crossing_x` is that column, and the assertion under it is what
holds the crossing inside the slot.

Only the copper/PRV slot opens on the shell's −X FACE. The two reed cables take the
front port field beside it (`_reed_channels`), and they are the whole of what crosses
that wall besides the slot: it is mated face to face with the refrigeration base.
"""

import math

import cadquery as cq

from world_workplane import xz_plane_y_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    hole_shift_from_edge,
    foam_shell_outer_height,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    cap_conduit_shell_xy,
    co2_inlet_y,
    lldpe_tube_od,
    port_hole_radius,
    port_lane_mid_y,
    support_ring_radial_width,
    tank_coil_envelope_radius,
    west_lane_mid_y,
    build_hole_punch,
    build_slot_punch,
    port_to_shell,
)
from _support_ring import slot_angular_width, slot_count

# [17](FRONT_FACE_PORT_Z) — Z of the vessel's two bottom-plate lines where they
# leave their own fittings: the carbonated-water outlet and the CO2 inlet, both
# hole_shift_from_edge in from the +Z outer face of the shell's floor. One band of the
# shell's height carries both, one either side of the plate's own axis in Y, and both
# have to cross the tank support ring to get out of it. THEY CROSS IT IN DIFFERENT
# PLACES: the CO2 takes a bore on the shell's centreline (below), the water outlet
# takes a slot. Two lines on one crossing would be two tubes in one ⌀6.5 hole.
front_face_port_z = hole_shift_from_edge + wall_and_floor_thickness

# WHERE THE CARBONATED-WATER OUTLET LEAVES THE RING, and the one thing this module says
# about that line: it crosses at a SLOT, on the column its own cap conduit stands over,
# so the line turns once under the tank and then climbs on one X the whole way up. The
# ring is already slotted at four azimuths (`_support_ring`) to let the pour reach the
# under-tank floor, and one of them lies where a line heading for that column wants to
# go — so this crossing costs no bore, notches no bearing segment, and the ⌀6.5
# standard does not apply to it. The assertion is what keeps it inside the slot when
# either the column or the ring moves.
water_outlet_ring_crossing_x = cap_conduit_shell_xy("carb-water-out")[0]
support_ring_outer_radius = tank_coil_envelope_radius
support_ring_inner_radius = support_ring_outer_radius - support_ring_radial_width


def ring_crossing_azimuths(x, tube_radius):
    """The azimuth band a −Y line at `x` sweeps while it is inside the ring's annulus.

    `(low, high)` in degrees about +X, or None if the line passes clear outboard of the
    ring and never crosses it. The extremes are corners: the tube's two edges against the
    annulus's two radii, because azimuth runs monotonically in each."""
    band = []
    for edge in (x - tube_radius, x + tube_radius):
        for radius in (support_ring_inner_radius, support_ring_outer_radius):
            if abs(edge) >= radius:
                continue
            band.append(math.degrees(math.atan2(-math.sqrt(radius ** 2 - edge ** 2), edge)) % 360.0)
    return (min(band), max(band)) if band else None


def ring_slot_spans():
    """Each ring slot as `(low, high)` degrees — `_support_ring`'s own construction."""
    step = 360.0 / slot_count
    return [(step * (i + 0.5) - slot_angular_width / 2.0,
             step * (i + 0.5) + slot_angular_width / 2.0) for i in range(slot_count)]


_crossing = ring_crossing_azimuths(water_outlet_ring_crossing_x, lldpe_tube_od / 2.0)
assert _crossing is not None and any(lo <= _crossing[0] and _crossing[1] <= hi
                                     for lo, hi in ring_slot_spans()), (
    f"the carbonated-water outlet crosses the tank support ring at x "
    f"{water_outlet_ring_crossing_x:g} over azimuths {_crossing[0]:.1f}°..{_crossing[1]:.1f}°, "
    f"which no slot of {ring_slot_spans()} holds — the line would have to be bored through a "
    f"bearing segment")

# CO2 inlet — the one bore through the tank support ring, and the ONLY one: the water
# outlet takes a slot. It runs from the bottom plate's own lane-side port out to the
# PORT LANE, and it lands on the lane UNDER THE `co2-in` CONDUIT rather than on the
# shell's centreline. That is the whole of why it leans.
#   The line falls the shell's height down the lane and has to turn into this bore at the
# bottom. A bore struck on the shell's centreline puts its lane mouth `co2_bore_to_ring`
# from the ring's own face, which is a fraction of what that corner takes, so the tube
# would have to finish bending inside the hole. Struck on the conduit's column instead,
# the fall lands on the bore's own axis: one corner out in the open lane, then straight
# in. The port, its TAISHER elbow — clocked to this line — the collet on it and the bore
# are one line, which is what the ⌀6.5 fit through the ring asks for.
co2_inlet_xyz = (0.0, co2_inlet_y, front_face_port_z)
co2_inlet_lane_xyz = cap_conduit_shell_xy("co2-in") + (front_face_port_z,)
co2_bore_to_ring = abs(port_lane_mid_y) - support_ring_outer_radius
assert abs(co2_inlet_lane_xyz[1] - port_lane_mid_y) < 1e-9, (
    f"the co2-in conduit stands at y {co2_inlet_lane_xyz[1]:g}, off the port lane "
    f"({port_lane_mid_y:g}) its line falls down — the bore is struck to meet that fall")

# Reservoir DRAW pass-throughs — each reservoir's 1/4" LLDPE line off its floor bulkhead,
# out of the pocket at bulkhead_elbow_exit_z (level out of the elbow's lateral port, in the
# open space under the reservoir's raised floor). The two leave by OPPOSITE ±Y bands,
# because that is the wall each one's elbow is turned at: A crosses its pocket's −Y wall
# onto the port lane, B its +Y wall onto the west lane. Both then come about and climb the
# forward band to their own cap conduits — neither crosses the −X wall.
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
    # Reservoir A pierces its pocket's −Y wall where its bulkhead elbow points and stops on the
    # PORT LANE — reservoir B's own cut read across the shell. It has no second bore: the band
    # it lands in runs clear to the shell's open top, and the feature at the far end of it is
    # the cap's `reservoir-a` conduit. A's pocket is the far one from that conduit, so its run
    # takes the lane's own floor, under everything else standing in it.
    foam_shell = foam_shell.cut(
        build_hole_punch(
            origin=flavor_line_plus_x_xyz,
            hole_punch_radius=port_hole_radius,
            hole_punch_height=flavor_line_plus_x_xyz[1] - port_lane_mid_y,
            direction=-1,
        )
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
    """CO2 inlet — a ⌀[6.5](PORT_HOLE_DIAMETER) bore from the bottom plate's lane-side port
    at y = [-19.05](CO2_INLET_Y) out through the tank support ring to the PORT LANE, LEANING
    across the shell's floor rather than running its centreline: it ends under the `co2-in`
    conduit, because that is where the line arrives.

    It crosses the ring with open cavity inboard of it, which is where the vessel's TAISHER
    elbow and its PP010822E adapter hang; the line bottoms in that collet, so nothing is made
    up in-cavity. Between the ring and the lane it crosses nothing at all — the pockets stop
    well outboard of this run.

    THE LANE END IS FED FROM ABOVE. The line falls the shell's whole height down the port lane
    from the cap's `co2-in` conduit and turns once, in the open, onto this axis — so it is laid
    before the top cap goes on, not pushed in from outside. Nothing crosses the −X wall on this
    line's account."""
    start = cq.Vector(*co2_inlet_lane_xyz)
    reach = cq.Vector(*co2_inlet_xyz) - start
    return foam_shell.cut(
        cq.Solid.makeCylinder(port_hole_radius, reach.Length, start, reach.normalized()))


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
