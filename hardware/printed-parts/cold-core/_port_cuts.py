"""Openings through the foam shell — the PRV vent's port through the +Y flank and the front
wall's two copper feed-throughs — and the two lines that cross the carbonator support ring.

EVERY FLUID LINE LEAVES BY THE TOP, and no line crosses a bag pocket's wall: both reservoirs
are filled and drawn through their own caps. The two lines that run under the carbonator —
the CO2 in and the carbonated water out — cross the support ring at its own slots, on the
columns `co2_lane_x` and `water_outlet_climb_x`, and the assertions here are what hold each
crossing inside one slot.

Only the two copper feed-throughs open on the shell's −X FACE. The two reed cables take the
reed channels' own cavities, open to the cap (`_reed_channels`), and they are the whole
of what crosses that wall besides the copper: it is mated face to face with the refrigeration
base, and the copper meets that base's own entries.
"""

import math
import cadquery as cq
import fits

from _cold_core_interface import (
    wall_and_floor_thickness,
    carbonator_support_ring_height,
    outer_shell_wall,
    foam_shell_outer_height,
    water_outlet_climb_x,
    co2_inlet_y,
    co2_lane_x,
    lldpe_tube_od,
    port_lane_mid_y,
    support_ring_radial_width,
    carbonator_coil_envelope_radius,
    make_box,
    state,
)
from _support_ring import slot_angular_width, slot_clock, slot_count

# [20.8](FRONT_FACE_PORT_Z) — Z of the carbonator's two bottom-plate lines where they
# leave their own fittings: the carbonated-water outlet and the CO2 inlet. Each bottom port
# carries a one-piece push-fit male elbow (neoFit AME4-N2-E), and this is the socket axis it
# turns its line onto, `bottom_port_drop` below the carbonator tube's bottom end. One band of
# the shell's height carries both, one either side of the plate's own axis in Y, and both
# have to cross the carbonator support ring to get out of it. THEY CROSS IT IN DIFFERENT
# SLOTS: two lines on one crossing would be two tubes in one ⌀[7.5](PORT_HOLE_DIAMETER) passage.
#   The drop is the elbow's reach off the plate less the plate's one-thickness recess into the
# tube. Off neoFit's Male Elbow NPTF drawing, AME4-N2 row (thread A 0.520 in, overall E
# 1.256 in, body ⌀P 0.610 in), the socket axis stands E − A − P/2 = 0.431 in over the thread's
# shoulder. Threaded into the tapped plate as deep as the street elbow's model takes — the
# small end 0.26 in past the outer face — the shoulder stands 0.260 in off it: the axis is
# 0.691 in (17.55 mm) off the plate, 11.2 mm below the tube's end. The installed engagement is
# unmeasured; `cold-core-layout/_carbonator.py` prints this storey against the catalog reach.
bottom_port_drop = 11.2
front_face_port_z = wall_and_floor_thickness + carbonator_support_ring_height - bottom_port_drop

# WHERE THE CARBONATED-WATER OUTLET LEAVES THE RING, and the one thing this module says
# about that line: it crosses at a SLOT, on the column it CLIMBS, so the line turns once
# under the carbonator and holds one X the whole way up to the lane. What it does once it is ON
# the lane is the lane's business and not this module's. The
# ring is already slotted at four azimuths (`_support_ring`) to let the pour reach the
# under-carbonator floor, and one of them lies where a line heading for that column wants to
# go — so this crossing costs no bore, notches no bearing segment, and the ⌀[7.5](PORT_HOLE_DIAMETER)
# standard does not apply to it. The assertion is what keeps it inside the slot when
# either the column or the ring moves.
water_outlet_ring_crossing_x = water_outlet_climb_x
support_ring_outer_radius = carbonator_coil_envelope_radius
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
    return [(step * (i + 0.5) + slot_clock - slot_angular_width / 2.0,
             step * (i + 0.5) + slot_clock + slot_angular_width / 2.0) for i in range(slot_count)]


_crossing = ring_crossing_azimuths(water_outlet_ring_crossing_x, lldpe_tube_od / 2.0)
# The line missing the ring entirely is one of the two ways this opens, and it has no azimuths
# to name — so the note is written for both rather than reaching into a reading that is None.
state(
    "water-outlet-slot", "The carbonated-water outlet crosses the support ring in one slot",
    "one slot holding the whole crossing",
    _crossing is not None and any(lo <= _crossing[0] and _crossing[1] <= hi
                                  for lo, hi in ring_slot_spans()),
    (f"the carbonated-water outlet at x {water_outlet_ring_crossing_x:g} passes clear "
     f"outboard of the carbonator support ring and crosses no azimuth of it — the slot it is "
     f"struck against is not the ring this line meets" if _crossing is None else
     f"the carbonated-water outlet crosses the carbonator support ring at x "
     f"{water_outlet_ring_crossing_x:g} over azimuths "
     f"{_crossing[0]:.1f}°..{_crossing[1]:.1f}°, "
     f"which no slot of {ring_slot_spans()} holds — the line would have to be bored through a "
     f"bearing segment"))

# CO2 inlet — the ⌀[7.5](PORT_HOLE_DIAMETER) reach in to the bottom plate's own lane-side
# port at y = [-19.05](CO2_INLET_Y), from the PORT LANE, landing UNDER THE `co2-in` CONDUIT
# rather than on the shell's centreline. That is the whole of why it leans.
#   The line falls the shell's height down the lane and has to turn onto this axis at the
# bottom. An axis struck on the shell's centreline puts its lane end `co2_bore_to_ring`
# from the ring's own face, which is a fraction of what that corner takes, so the tube
# would have to finish bending inside the reach. Struck on the conduit's column instead,
# the fall lands on the axis itself: one corner out in the open lane, then straight in.
# The port, its neoFit push-fit male elbow — aimed along this line — and the reach are
# one line, so the tube is straight where it enters the elbow's socket and bottoms in it.
# `foam_assembly` probes that last leg straight at every build.
co2_inlet_xyz = (0.0, co2_inlet_y, front_face_port_z)
# WHERE THE LEAN STARTS, which is not where the fall lands. The line falls the lane on the cap
# conduit's own column and runs along the lane's floor to this one before it turns in, so this
# is the column the ring reads and the conduit above is free of it.
co2_inlet_lane_xyz = (co2_lane_x, port_lane_mid_y, front_face_port_z)
co2_bore_to_ring = abs(port_lane_mid_y) - support_ring_outer_radius

# AND IT CROSSES THE RING IN A SLOT, like the water outlet does. The ring is four bearing
# segments carrying the carbonator with four pour slots between them, and the reach in leans
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
     f"the CO2 reach in from x {co2_inlet_lane_xyz[0]:g} crosses the carbonator support ring over "
     f"azimuths {_co2_crossing[0]:.1f}°..{_co2_crossing[1]:.1f}°, which no slot of "
     f"{ring_slot_spans()} holds — the line would have to be bored through a bearing "
     f"segment that carries the carbonator"))


def cut_prv_vent_port(foam_shell):
    """The PRV vent's opening through the +Y OUTER wall — the one place a line is let out
    through this shell's skin, cut for that line by name.

    THE OUTER SHELL YIELDS TO NO OTHER LINE. What keeps six lines climbing to the lid instead
    of punching out wherever they happen to touch the skin is that a run meeting it reads
    blocked, and `report_routes` says so. Opening it for one line is a decision about that
    line, so it is written as one line's own cut with that line's own name on it.

    WHY THIS LINE. The core is reached through its lid because nothing potted in it can be
    reached again, so every run the machine has to make up is brought to the one face the
    service bay stands on. A relief vent is made up on nothing — it ends open — and what it
    owes instead is the shortest path to air outside the cabinet, because tube length on a
    relief path is discharge taken off the valve's rating. The opening is the line's own
    ⌀[7.5](PORT_HOLE_DIAMETER) clearance corridor, masked around the tube during the pour, and the tube runs on through it into the socket the appliance's own west
    wall holds across the band."""
    from _internal_routes import route_corridor

    corridor = route_corridor("prv-vent")
    return (foam_shell.cut(corridor)
            .cut(corridor.translate((0, 0, fits.supported_surface))))


def cut_copper_ports(foam_shell):
    """Two round copper passages through the continuous front wall."""
    from _copper_ports import hole_radius, stations
    for (x, y, z), _axis in stations().values():
        bore = cq.Solid.makeCylinder(
            hole_radius, outer_shell_wall + 4.0,
            cq.Vector(x - 2.0, y, z), cq.Vector(1., 0., 0.))
        foam_shell = foam_shell.cut(bore)
    return foam_shell
