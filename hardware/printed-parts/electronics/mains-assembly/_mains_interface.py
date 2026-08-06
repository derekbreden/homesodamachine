"""Mains block interface — what the carrier prints, and where every wire lands.

The block is the appliance's whole mains side: the AC hub that splices H/N/G, the
Mean Well brick that ends the AC side and begins the DC one, the relay that
switches the compressor's hot leg, and the chassis-ground stud every green bond
clamps to. The four of them are one electrical zone — the Class I earthed node
and everything at mains potential. Nothing at logic level is in it.

The block has no part of its own. All four bodies land on ONE printed piece of
the enclosure — `enclosure_back_top`, since every station is aft of the Y joint,
above the back Z seam, and one rib inset off the +X wall — so the wall carries
the joints directly: a boss under each of the nine holes and the hub's three
wells grown into its own face.

Frame: +X aft, +Y up, +Z off the carrier into the cabinet. Origin at the block's
forward-bottom corner on the CARRIER'S OWN FACE, so z = 0 is the plane the bosses
and the wells grow from.

`stations` is the boss pattern the carrier owes, `hub_wells` the well solid it
grows in, `seat` each body's pose, `terminals` every wire landing, and `envelope`
the box to place.
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

clearance_floor = 1.0          # = scorecard.CLEARANCE_FLOOR
carrier_t = 3.0                # = enclosure.wall, the section the bosses stand on

# --- The joint ------------------------------------------------------------
insert_pocket_depth = _cc.insert_pocket_depth
insert_pocket_radius = _cc.insert_pocket_radius
boss_d = _cc.screw_boss_size

# Material the carrier owes under every station: an insert's full pocket, and
# enough beyond it that the bore does not open on the wall's outer face.
insert_backing = 1.5
station_depth = insert_pocket_depth + insert_backing

# The one plane every body seats on, off the carrier's face. Two things reach for
# it: the relay's pins hang under its board, and a boss standing on the carrier's
# own section has to hold a whole pocket.
seat_z = max(_relay.pin_drop + clearance_floor, station_depth - carrier_t)

# --- What each body claims in plan ----------------------------------------
psu_span_x = _psu.length
psu_span_y = _psu.width

hub_span_x = 2.0 * _hub.margin + len(_hub.poles) * _hub.wago_pitch
hub_span_y = 2.0 * _hub.margin + 2.0 * _hub.wago_slot_half_y

relay_span_x = _relay.length
relay_span_y = _relay.width

# The tongues fan the whole way round the stud, so what it claims in plan is a
# disc: an eye's radius plus the crimp barrel standing off it.
gnd_fan_radius = _gnd.eye_od / 2.0 + _gnd.barrel_len

# --- Rows ------------------------------------------------------------------
# Three rows, a clearance floor apart, and the middle one is the splice: the hub
# between the brick it feeds below and the relay it feeds above, with the ground
# stud in the band aft of the hub, nearest the inlet whose earth is the bond it
# exists for. The stud shares the hub's row, so the block is one row shorter than
# the four bodies standing one on another.
psu_y0 = 0.0
psu_y1 = psu_y0 + psu_span_y

splice_y0 = psu_y1 + clearance_floor
splice_y1 = splice_y0 + hub_span_y

relay_y0 = splice_y1 + clearance_floor
relay_y1 = relay_y0 + relay_span_y

# The brick is the longest body in the block, and the row it lies in is the
# block's own length. Nothing stands outboard of any body.
block_x = psu_span_x
block_y = relay_y1

# --- Seats, in the block's own frame ---------------------------------------
# The brick's AC end and the relay's contacts face AFT, toward the inlet and the
# hub; the brick's DC end and the relay's logic header face FORWARD, toward the
# controller. Mains lands at the aft end of the block.
psu_rot = -90.0
relay_rot = 0.0

psu_c = (block_x / 2.0, psu_y0 + psu_span_y / 2.0)
relay_c = (block_x - relay_span_x / 2.0, relay_y0 + relay_span_y / 2.0)

# The hub is placed by its CORNER, and its own floor is buried in the carrier:
# the wells stand out of the wall's face and the lugs bottom on it.
hub_corner = (0.0, splice_y0)
hub_z = -_hub.floor_t

_gnd_band_x0 = hub_corner[0] + hub_span_x + clearance_floor
gnd_c = ((_gnd_band_x0 + block_x) / 2.0, splice_y0 + hub_span_y / 2.0)


def seat(body):
    """One body's pose in the block frame: `(centre, rot_deg, z)`.

    `centre` is a footprint centre for the two bolted boards and the stud, the
    plate corner for the hub, which is authored from one."""
    if body == "psu":
        return psu_c, psu_rot, seat_z
    if body == "relay-1":
        return relay_c, relay_rot, seat_z
    if body == "ground-stack":
        return gnd_c, 0.0, seat_z
    if body == "ac-hub":
        return hub_corner, 0.0, hub_z
    raise KeyError(body)


def _rot(dx, dy, deg):
    import math
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (dx * c - dy * s, dx * s + dy * c)


def _at(body, station):
    """A station authored in a body's own frame, read in the block's."""
    (cx, cy), rot, z0 = seat(body)
    (sx, sy, sz), axis = station
    rx, ry = _rot(sx, sy, rot)
    return (cx + rx, cy + ry, z0 + sz), _rot(axis[0], axis[1], rot) + (axis[2],)


def stations():
    """Every boss the carrier owes, as `(body, [(x, y), ...], hole_dia)` in the
    block frame. Each is a boss `seat_z` tall, bored `insert_pocket_depth` from
    its top for a ruthex M3 short, taking an M3 driven from the open face.

    The stud is here too: its screw lands in a boss like a board's, and the ring
    tongues clamp under the head instead of a PCB."""
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


def hub_wells():
    """The AC hub's solid, posed in the block frame with its own floor buried in
    the carrier's section. The carrier fuses this: the floors are one plane at
    one thickness, so what stands out of the wall's face is the three wells."""
    hub_x, hub_y = hub_corner
    return _hub.build_ac_hub().translate((hub_x, hub_y, hub_z))


def seated_build(body):
    """One seated body's solid, in its own frame, on the plane `seat` gives it."""
    return {"psu": _psu.build,
            "relay-1": _relay.build,
            "ground-stack": _gnd.build}[body]()


def wago_places():
    """Each Wago's well centre in the block frame. A lug bottoms on the carrier's
    own face and stands its wire half proud."""
    hub_x, hub_y = hub_corner
    return [(hub_x + cx, hub_y + cy) for cx, cy in _hub.LAYOUT.wago_places]


def wago_stand():
    """A lug's standing dimensions in the block frame: `(width, depth, height)`."""
    return (_hub.stand_w, _hub.stand_d, _hub.stand_h)


press = _hub.press


def well_reach():
    """How far a well wraps a lug off the carrier's face — the butt half, with the
    wire half standing proud above it."""
    return _hub.wago_engage


def terminals():
    """Every wire landing in the block, as `(name, position, outward axis)` in the
    block frame.

    All of them look +Z, off the open face. Nothing in this block is entered from
    behind, from an end, or from under a neighbour."""
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


def pin_clearance():
    """What the relay's pins leave over the carrier's face."""
    return seat_z - _relay.pin_drop


def reach():
    """How far off the carrier's face the tallest body stands."""
    return seat_z + _psu.height


def envelope():
    """The box the block claims off the carrier's face: `(x, y, z)`."""
    return (block_x, block_y, reach())


def rows():
    """Each row as `(name, y0, y1, reach)` — its band up the carrier and how far
    off the face it actually stands.

    The envelope is the deepest row's, and it is the brick's alone. What stands
    over the other two is free to whatever the placement puts there."""
    def top(*solids):
        return max(s.BoundingBox().zmax for s in solids)
    psu = seated_build("psu").val().translate((0.0, 0.0, seat_z))
    relay = seated_build("relay-1").val().translate((0.0, 0.0, seat_z))
    stud = seated_build("ground-stack").val().translate((0.0, 0.0, seat_z))
    lug_top = hub_z + _hub.floor_t + _hub.stand_h
    return [("brick", psu_y0, psu_y1, top(psu)),
            ("splice", splice_y0, splice_y1, max(top(stud), lug_top)),
            ("relay", relay_y0, relay_y1, top(relay))]
