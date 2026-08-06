"""Mains block interface — every number a reader of this module is allowed to know.

The block is the appliance's whole mains side on one printed carrier: the AC hub
that splices H/N/G, the Mean Well brick that ends the AC side and begins the DC
one, the relay that switches the compressor's hot leg, and the chassis-ground
stud every green bond clamps to. The four of them are one electrical zone — the
Class I earthed node and everything at mains potential. Nothing at logic level is
in it.

It is assembled and wired on the bench and installed as one body. The carrier
owns every joint inside it; what the module owes the machine is four screws.

Frame: +X aft, +Y up, +Z off the carrier into the cabinet — the module's own
frame, in the pose it installs in. Origin at the plate's forward-bottom corner on
its LANDING FACE, so z = 0 is the plane the four stations bear on and the plate's
open face is at `floor_t`.

Nothing outside the module reads a body's own frame. `seat` gives each body its
pose here, `terminals` gives every wire landing, `stations` gives the four joints
the module owes whatever carries it, and `envelope` gives the box it claims.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "printed-parts" / "cold-core",
    _hw / "printed-parts" / "electronics" / "ac-hub",
    _hw / "reference" / "wago-221-413",
    _hw / "reference" / "meanwell-irm90",
    _hw / "reference" / "teyleten-relay",
    _hw / "reference" / "ground-ring-stack",
):
    sys.path.insert(0, str(_p))
import _cold_core_interface as _cc
import ac_hub as _hub
import ground_ring_stack as _gnd
import meanwell_irm90 as _psu
import teyleten_relay as _relay

# --- The carrier -----------------------------------------------------------
# The plate IS the hub's own floor plane: the hub carries no hold-down, and its
# wells stand off a floor of this thickness.
floor_t = _hub.floor_t

# The insert's pocket runs its full depth and stops short of the landing face,
# which the plate bears on at its four stations.
insert_backing = 1.5
insert_pocket_depth = _cc.insert_pocket_depth
insert_pocket_radius = _cc.insert_pocket_radius
board_standoff = insert_pocket_depth + insert_backing - floor_t
boss_d = _cc.screw_boss_size

# One plane for every seated body. All the bosses print at one height, and every
# body in the block stands its own hole pattern on it.
seat_z = floor_t + board_standoff

# Material outboard of a station's clearance hole, and the band the bodies leave
# for the stations to stand in. At twice the inset a station's head bears fully
# on plate — the screw is `station_inset` clear of the nearest footprint, against
# a head that reaches `_gnd.head_d / 2`.
edge_wall = 3.0
station_inset = _cc.screw_clearance_radius + edge_wall
margin = 2.0 * station_inset

# The row gap is what a terminated lead takes leaving its landing before the wire
# itself begins: a crimp barrel's own length, with no wire past it.
lead_gap = _gnd.barrel_len

# --- What each body claims in plan -----------------------------------------
# The brick lies with its length aft-forward, so the plate's length is the
# brick's and every other body stands in the band it opens.
psu_span_x = _psu.length
psu_span_y = _psu.width

# The hub's plate is authored from its own corner, and its three wells with a
# margin either way are the whole of it.
hub_span_x = 2.0 * _hub.margin + len(_hub.poles) * _hub.wago_pitch
hub_span_y = 2.0 * _hub.margin + 2.0 * _hub.wago_slot_half_y

relay_span_x = _relay.length
relay_span_y = _relay.width

# The tongues fan the whole way round the stud, so what it claims in plan is a
# disc: an eye's radius plus the crimp barrel standing off it.
gnd_fan_radius = _gnd.eye_od / 2.0 + _gnd.barrel_len

# --- Rows ------------------------------------------------------------------
# Three rows up the plate, and the middle one is the splice: the hub sits between
# the brick it feeds below and the relay it feeds above, so the star's centre is
# a lead's length from both of its loads. The ground stud takes the band aft of
# the hub, nearest the inlet whose earth is the bond it exists for.
psu_y0 = margin
psu_y1 = psu_y0 + psu_span_y

splice_y0 = psu_y1 + lead_gap
splice_y1 = splice_y0 + hub_span_y

relay_y0 = splice_y1 + lead_gap
relay_y1 = relay_y0 + relay_span_y

plate_x = psu_span_x + 2.0 * margin
plate_y = relay_y1 + margin

# --- Seats, in the module's own frame --------------------------------------
# The brick's AC end and the relay's contacts both face AFT, toward the inlet and
# the hub; the brick's DC end and the relay's logic header both face FORWARD,
# toward the controller. Mains lands at the aft end of the block.
psu_rot = -90.0
relay_rot = 0.0

psu_c = (margin + psu_span_x / 2.0, psu_y0 + psu_span_y / 2.0)
relay_c = (plate_x - margin - relay_span_x / 2.0, relay_y0 + relay_span_y / 2.0)

# The hub is placed by its CORNER — its own frame starts there, not at a centre.
hub_corner = (margin, splice_y0)

# The stud stands centred in the band the hub leaves aft of it.
_gnd_band_x0 = hub_corner[0] + hub_span_x + lead_gap
_gnd_band_x1 = plate_x - margin
gnd_c = ((_gnd_band_x0 + _gnd_band_x1) / 2.0, splice_y0 + hub_span_y / 2.0)


def seat(body):
    """One body's pose in the module frame: `(centre, rot_deg, seat_z)`.

    `centre` is the body's own origin in plan — a footprint centre for the two
    bolted boards and the stud, the plate corner for the hub, which is authored
    from one. Every one of them stands on `seat_z` except the hub, whose wells
    rise out of the carrier itself."""
    if body == "psu":
        return psu_c, psu_rot, seat_z
    if body == "relay-1":
        return relay_c, relay_rot, seat_z
    if body == "ground-stack":
        return gnd_c, 0.0, seat_z
    if body == "ac-hub":
        return hub_corner, 0.0, floor_t
    raise KeyError(body)


def _rot(dx, dy, deg):
    import math
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (dx * c - dy * s, dx * s + dy * c)


def _at(body, station):
    """A station authored in a body's own frame, read in the module's."""
    (cx, cy), rot, z0 = seat(body)
    (sx, sy, sz), axis = station
    rx, ry = _rot(sx, sy, rot)
    return (cx + rx, cy + ry, z0 + sz), _rot(axis[0], axis[1], rot) + (axis[2],)


def bolted():
    """Every hole pattern the carrier answers with a boss, as
    `(body, [(x, y), ...], hole_dia)` in the module frame.

    The stud is here too: its screw lands in a boss like a board's, and the six
    ring tongues clamp under the head instead of a PCB."""
    out = []
    for body, ref in (("psu", _psu), ("relay-1", _relay)):
        (cx, cy), rot, _z = seat(body)
        holes = getattr(ref, "holes", None)
        if holes is None:
            holes = [(sx * ref.hole_dx, sy * ref.hole_dy)
                     for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
        out.append((body, [tuple(c + d for c, d in zip((cx, cy), _rot(hx, hy, rot)))
                           for hx, hy in holes], ref.hole_dia))
    out.append(("ground-stack", [gnd_c], _gnd.hole_d))
    return out


def stations():
    """The four joints the module owes its carrier: `(x, y)` in the module frame,
    each a clearance hole through the plate for an M3 into a boss on the carrier.

    They stand in the margin band, with open plate over each one when the block
    is fully assembled."""
    return [(x, y)
            for x in (station_inset, plate_x - station_inset)
            for y in (station_inset, plate_y - station_inset)]


def station_clearance_r():
    """Half the clearance hole a station's screw passes through."""
    return _cc.screw_clearance_radius


def terminals():
    """Every wire landing in the block, as `(name, position, outward axis)` in the
    module frame.

    All of them look +Z, off the open face. Nothing in this module is entered
    from behind, from an end, or from under a neighbour."""
    out = [("psu-ac", ) + _at("psu", _psu.ac_in()),
           ("psu-dc", ) + _at("psu", _psu.dc_out()),
           ("relay-contacts", ) + _at("relay-1", _relay.contacts()),
           ("relay-logic", ) + _at("relay-1", _relay.logic())]
    for pole in _hub.poles:
        out.append(("hub-%s" % pole, ) + _at("ac-hub", _hub.lug(pole)))
    (gx, gy), _rotation, gz = seat("ground-stack")
    (_sx, _sy, sz), axis = _gnd.landing()
    out.append(("ground-landing", (gx, gy, gz + sz), axis))
    return out


def hub_build():
    """The AC hub's own solid, in its own frame — its floor on z = 0, its wells
    above it. The carrier fuses this at the plate's own floor plane."""
    return _hub.build_ac_hub()


def seated_build(body):
    """One seated body's solid, in its own frame, on the plane `seat` gives it."""
    return {"psu": _psu.build,
            "relay-1": _relay.build,
            "ground-stack": _gnd.build}[body]()


def wago_places():
    """Each Wago's well centre in the module frame, with the lug's own standing
    dimensions — the assembly stands one in each."""
    hub_x, hub_y = hub_corner
    return [(hub_x + cx, hub_y + cy) for cx, cy in _hub.LAYOUT.wago_places]


def reach():
    """How far off the plate's open face the tallest body stands."""
    return board_standoff + _psu.height


def envelope():
    """The box the module claims, from its landing face: `(x, y, z)`."""
    return (plate_x, plate_y, floor_t + reach())
