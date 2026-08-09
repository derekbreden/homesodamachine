"""Port openings and slot cuts through the foam shell — the two reservoir draws, the
CO2 inlet bore, and the front wall's two lane slots.

EVERY FLUID LINE LEAVES BY THE TOP, and every opening one of them takes on the way is
that line's own CORRIDOR: the run swept at the project's ⌀[6.5](PORT_HOLE_DIAMETER)
standard where it crosses shell material, rather than a circle the line has to hold a
straight through (`cut_line_corridors`). The tight 1/4" fit is the same either way —
it is radial to the tube's own path — and what a corner costs stops being the hole's
shape. Reservoir A's opening is in its pocket's −Y wall, onto the port lane; reservoir
B's is in its +Y wall, onto the west lane; and the CO2's is the port lane run the other
way, its line coming DOWN from the cap into a bore that runs the whole reach in.

The carbonated-water outlet has no opening here at all. It crosses the tank support
ring at one of the ring's own slots, on the column its cap conduit stands over —
`water_outlet_ring_crossing_x` is that column, and the assertion under it is what
holds the crossing inside the slot.

Only the two lane slots open on the shell's −X FACE. The two reed cables take the
front port field on the port lane below its slot (`_reed_channels`), and they are the whole
of what crosses that wall besides the slots: it is mated face to face with the refrigeration
base, and what the slots carry is made up on that base's own picks.
"""

import math

from _cold_core_interface import (
    wall_and_floor_thickness,
    hole_shift_from_edge,
    foam_shell_outer_height,
    bag_pocket_width,
    bag_pocket_y_inner_max,
    outer_shell_x_length,
    reservoir_bulkhead_port_x,
    cap_conduit_shell_xy,
    co2_inlet_y,
    lldpe_tube_od,
    port_lane_mid_y,
    support_ring_radial_width,
    tank_coil_envelope_radius,
    make_box,
    build_slot_punch,
    port_to_shell,
    state,
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


def segment_ring_azimuths(a, b, tube_radius):
    """The azimuth band a straight run from `a` to `b` sweeps while it is inside the ring's
    annulus — the general form of the one above, for a run that LEANS instead of crossing the
    ring square.

    Both edges of the tube are solved against both radii, and what comes back is every azimuth
    at which the run has ring material beside it. A band inside one slot is a crossing that
    notches no bearing segment."""
    (ax, ay), (bx, by) = a[:2], b[:2]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return None
    nx, ny = -dy / length, dx / length
    band = []
    for side in (-1.0, 1.0):
        ox, oy = ax + nx * side * tube_radius, ay + ny * side * tube_radius
        for radius in (support_ring_inner_radius - tube_radius,
                       support_ring_outer_radius + tube_radius):
            qa = dx * dx + dy * dy
            qb = 2.0 * (ox * dx + oy * dy)
            qc = ox * ox + oy * oy - radius * radius
            disc = qb * qb - 4.0 * qa * qc
            if disc < 0.0:
                continue
            for t in ((-qb - math.sqrt(disc)) / (2.0 * qa),
                      (-qb + math.sqrt(disc)) / (2.0 * qa)):
                if 0.0 <= t <= 1.0:
                    band.append(math.degrees(
                        math.atan2(oy + t * dy, ox + t * dx)) % 360.0)
    return (min(band), max(band)) if band else None


def ring_slot_spans():
    """Each ring slot as `(low, high)` degrees — `_support_ring`'s own construction."""
    step = 360.0 / slot_count
    return [(step * (i + 0.5) - slot_angular_width / 2.0,
             step * (i + 0.5) + slot_angular_width / 2.0) for i in range(slot_count)]


_crossing = ring_crossing_azimuths(water_outlet_ring_crossing_x, lldpe_tube_od / 2.0)
# The line missing the ring entirely is one of the two ways this opens, and it has no azimuths
# to name — so the note is written for both rather than reaching into a reading that is None.
state(
    "water-outlet-slot", "The carbonated-water outlet crosses the support ring in one slot",
    "one slot holding the whole crossing",
    _crossing is not None and any(lo <= _crossing[0] and _crossing[1] <= hi
                                  for lo, hi in ring_slot_spans()),
    (f"the carbonated-water outlet at x {water_outlet_ring_crossing_x:g} passes clear "
     f"outboard of the tank support ring and crosses no azimuth of it — the slot it is "
     f"struck against is not the ring this line meets" if _crossing is None else
     f"the carbonated-water outlet crosses the tank support ring at x "
     f"{water_outlet_ring_crossing_x:g} over azimuths "
     f"{_crossing[0]:.1f}°..{_crossing[1]:.1f}°, "
     f"which no slot of {ring_slot_spans()} holds — the line would have to be bored through a "
     f"bearing segment"))

# CO2 inlet — the ⌀[6.5](PORT_HOLE_DIAMETER) reach in to the bottom plate's own lane-side
# port at y = [-19.05](CO2_INLET_Y), from the PORT LANE, landing UNDER THE `co2-in` CONDUIT
# rather than on the shell's centreline. That is the whole of why it leans.
#   The line falls the shell's height down the lane and has to turn onto this axis at the
# bottom. An axis struck on the shell's centreline puts its lane end `co2_bore_to_ring`
# from the ring's own face, which is a fraction of what that corner takes, so the tube
# would have to finish bending inside the reach. Struck on the conduit's column instead,
# the fall lands on the axis itself: one corner out in the open lane, then straight in.
# The port, its TAISHER elbow — clocked to this line — the collet on it and the reach are
# one line, which is what the collet asks for: a tube still bending never bottoms in it.
# `foam_assembly` probes that last leg straight at every build.
co2_inlet_xyz = (0.0, co2_inlet_y, front_face_port_z)
co2_inlet_lane_xyz = cap_conduit_shell_xy("co2-in") + (front_face_port_z,)
co2_bore_to_ring = abs(port_lane_mid_y) - support_ring_outer_radius

# AND IT CROSSES THE RING IN A SLOT, like the water outlet does. The ring is four bearing
# segments carrying the vessel with four pour slots between them, and the reach in leans
# across it; struck on a column whose lean lands inside one slot, the crossing costs no bore
# and notches no segment. That column is `_cold_core_interface.co2_lane_x`, and this is what
# holds it there when either the column or the ring moves.
_co2_crossing = segment_ring_azimuths(co2_inlet_lane_xyz, co2_inlet_xyz, lldpe_tube_od / 2.0)
state(
    "co2-inlet-slot", "The CO2 reach in crosses the support ring in one slot",
    "one slot holding the whole crossing",
    _co2_crossing is not None and any(lo <= _co2_crossing[0] and _co2_crossing[1] <= hi
                                      for lo, hi in ring_slot_spans()),
    (f"the CO2 reach in from x {co2_inlet_lane_xyz[0]:g} passes clear of the ring this is "
     f"struck against" if _co2_crossing is None else
     f"the CO2 reach in from x {co2_inlet_lane_xyz[0]:g} crosses the tank support ring over "
     f"azimuths {_co2_crossing[0]:.1f}°..{_co2_crossing[1]:.1f}°, which no slot of "
     f"{ring_slot_spans()} holds — the line would have to be bored through a bearing "
     f"segment that carries the vessel"))
state(
    "co2-bore-meets-fall", "The CO2 bore is struck where its line falls down the lane",
    f"the co2-in conduit on the port lane ({port_lane_mid_y:g})",
    abs(co2_inlet_lane_xyz[1] - port_lane_mid_y) < 1e-9,
    f"the co2-in conduit stands at y {co2_inlet_lane_xyz[1]:g}, off the port lane "
    f"({port_lane_mid_y:g}) its line falls down — the bore is struck to meet that fall")

# Reservoir DRAW pass-throughs — each reservoir's 1/4" LLDPE line off its floor bulkhead,
# out of the pocket at bulkhead_elbow_exit_z (level out of the elbow's lateral port, in the
# open space under the reservoir's raised floor). The two leave by OPPOSITE ±Y bands,
# because that is the wall each one's elbow is turned at: A crosses its pocket's −Y wall
# onto the port lane, B its +Y wall onto the west lane. Both then come about and climb the
# forward band to their own cap conduits — neither crosses the −X wall.
#
# A's crossing sits inboard of the bulkhead axis, opposite the outboard reed cable hole
# — the two openings [12](FLAVOR_REED_PITCH) mm apart center-to-center with PETG between
# them. That step is the reed cable's price, and B's crossing does not pay it: nothing else
# crosses the +Y wall, so B's stands on the BULKHEAD'S OWN AXIS.
flavor_line_hole_offset_from_bulkhead_x = 8.0
flavor_line_hole_x = reservoir_bulkhead_port_x - flavor_line_hole_offset_from_bulkhead_x


def pocket_wall_slab(y_sign):
    """One bag pocket's ±Y wall as a slab, an overshoot proud of both faces.

    Not a cut — a place. Two openings are neighbours when they land in the same wall, and a
    run half a metre long passes plenty of things it never shares a wall with, so anything
    pricing one opening against another meets both with this first."""
    overshoot = 1.0
    return make_box(
        (-outer_shell_x_length, outer_shell_x_length),
        (y_sign * (bag_pocket_width / 2.0 + overshoot),
         y_sign * (bag_pocket_y_inner_max - overshoot)),
        (-overshoot, foam_shell_outer_height + overshoot),
    ).val()


def cut_line_corridors(foam_shell, gives_way):
    """Every internal line's opening through the shell, cut as that line's own CORRIDOR
    (`_internal_routes.route_corridor`) and not as a straight bore.

    A wall here is two millimetres of PETG. A circular bore in one makes the line hold a
    straight a bore's length past it before it may begin to turn, and every one of these
    lines turns the moment it is through: both reservoir draws come out of a pocket and
    come about onto a lane, and the CO2 arrives down the port lane and turns in under the
    pockets. What they turn in is `outer_shell_foam_gap` with the attachment bosses standing
    in its outboard half, so a bore's shape rather than the band would be what set the
    corner. Cut as the corridor, what a corner costs is what the band leaves — and the tube
    crosses on the same tight fit either way, the shell's ⌀[6.5](PORT_HOLE_DIAMETER) round a
    `lldpe_tube_od` line, which is what keeps the body pour out of a pocket.

    `gives_way` IS THE WHOLE FENCE ON THIS, and it is a list of bodies rather than a region:
    each corridor is met with them and the shell is cut by what comes back, so a line opens
    those bodies where it crosses them and nothing anywhere else on a run that may be half a
    metre long. What gives way is stated by `_foam_shell`, which is where the bodies are.
    Everything left out of it — the outer shell, the tank support ring, the tank, the
    reservoirs, the other six lines — still stops a line dead, and `_internal_routes.
    report_routes` is where that shows as the arc a corner comes back at.

    Which line crosses which body is not named anywhere: this reads every line in the pack,
    and a corridor that never reaches a body leaves nothing when it is met with it."""
    from _internal_routes import routes as internal_routes, route_corridor

    for name in sorted(internal_routes):
        corridor = route_corridor(name)
        box = corridor.BoundingBox()
        for body in gives_way:
            solid = body.val() if hasattr(body, "val") else body
            b = solid.BoundingBox()
            if (box.xmax < b.xmin or box.xmin > b.xmax or box.ymax < b.ymin
                    or box.ymin > b.ymax or box.zmax < b.zmin or box.zmin > b.zmax):
                continue                      # a box is enough to prove it never gets there
            foam_shell = foam_shell.cut(corridor.intersect(solid))
    return foam_shell


def cut_lane_slots(foam_shell):
    """One Z-elongated slot through the outer-shell −X wall per LANE, each plugged by a stack
    slid down in from above.

    THERE ARE TWO because the evaporator's two coppers leave by opposite lanes — the
    condenser stands against the port lane's face and the compressor just short of the
    west lane's, and each copper is made up on the pick of the body behind it
    (`copper_plugs.columns`). A tail formed off a coil that is lowered into the cavity
    travels DOWN the wall to its station rather than through it, so each of them takes an
    opening running out through the shell's top; everything else on the same lane then
    crosses inside that one opening.

    Built in the PORT FRAME — where the wall it crosses is a −Y wall and the
    slot runs lateral in x, which is the frame the copper plugs themselves are
    authored in — then carried onto its own lane by `port_to_shell`, so a slot and the
    stack that fills it are one reading. The rounded top tapers above the foam-shell
    top edge, so the straight portion reaches the edge exactly with no sliver left.

    A slot's bottom stands clear of whatever the lane carries below it: on the port lane
    that is the front port field, and `copper_plugs.evap_cross_z` is derived from it."""
    from copper_plugs import columns, slot_width_x, outer_wall_inner_y

    slot_z_top = foam_shell_outer_height + slot_width_x / 2
    overshoot = 1.0                                    # a through-cut, both faces cleared
    for column in columns.values():
        slot_punch = build_slot_punch(
            origin=(0, outer_wall_inner_y + overshoot,
                    (slot_z_top + column.slot_z_bottom) / 2.0),
            slot_length=slot_z_top - column.slot_z_bottom,
            slot_diameter=slot_width_x,
            slot_punch_height=wall_and_floor_thickness + 2.0 * overshoot,
            direction=-1,
        )
        foam_shell = foam_shell.cut(port_to_shell(slot_punch.val(), column.lane_y))
    return foam_shell
