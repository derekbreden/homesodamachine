"""Shared cold-core datums and construction interfaces.

Rust owns the casing stock, cavity envelope, clamp stack and port-lane
dimensions. The remaining cap mount and passage recipes expose their
source-frame values to the sibling parts.

The constants carry claims about each other — a screw long enough for its insert, a band wide
enough for its bore, two columns far enough apart for foam to reach between them — and those are
settled here, as this file is read, with no solid yet to measure. `_stated_bounds` is the ledger
they record into; `enclosure_assembly.carry_stated_bounds` drains it onto the machine's card, where
an open one is a red row a reader can see beside the geometry it describes. The siblings that
import this module take `bound` and `state` from here rather than reaching for the ledger
themselves, because this is already the path they read every other shared name off."""

import itertools
import math
import sys
from collections import namedtuple
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent / "enclosure" / "enclosure"))
sys.path.insert(0, str(_here.parent / "valve-seat"))
sys.path.insert(0, str(_here.parents[1] / "reference" / "g-ganen-pump" / "installation"))
sys.path.insert(0, str(_here.parents[1] / "cold-core-layout"))

import fits
import valve_seat as _valve_seat
import _above_core_mounts as _above_mounts
from _stated_bounds import bound, state
from _enclosure_interface import (manifold_rise, inner_limb_drop,
                                  rear_plane_y, rear_seam_clear)
import _anchor_cap_interface as _anchor_cap


from _carbonator_stock import carbonator_outer_radius, carbonator_height
from _cold_core_data import read as _read

# The Rust recipe derives the casing stock, cavity envelope, port lanes and
# clamp stack from the shared printed-face allowances and carbonator stock.
_interface_fits = {name: getattr(fits, name) for name in
                   ("running", "slip", "m5_thread_pass_dia", "supported_surface")}
_base_recipe = _read("interface-base", fits=_interface_fits)
_base_states = _base_recipe.pop("_states")
globals().update(_base_recipe)
for _name in ("reservoir_fill_port", "reservoir_draw_port"):
    globals()[_name] = {int(side): tuple(xy) for side, xy in globals()[_name].items()}
for _name in ("reservoir_fill_sides", "top_lid_pour_xy", "carbonator_sensor_axis"):
    globals()[_name] = tuple(globals()[_name])
bottom_pour_positions = tuple(tuple(xy) for xy in bottom_pour_positions)
for _name in ("attachment_stations", "lid_attachment_stations"):
    globals()[_name] = tuple((tuple(xy), wall) for xy, wall in globals()[_name])
for _name in ("attachment_xy_positions", "lid_attachment_xy_positions"):
    globals()[_name] = [tuple(xy) for xy in globals()[_name]]
for _row in _base_states:
    state(*_row)


def reservoir_fill_conduit_xy(side):
    """Fill conduit in the cap frame over the reservoir's fill bore."""
    return tuple(_read("interface-reservoir-conduit", fits=_interface_fits,
                       kind="fill", side=side))


def reservoir_draw_conduit_xy(side):
    """Draw conduit in the cap frame over the reservoir's draw bore."""
    return tuple(_read("interface-reservoir-conduit", fits=_interface_fits,
                       kind="draw", side=side))


# Deck mounts pass through the equipment lid and carry the above-core PCB.
DeckMount = namedtuple("DeckMount", "points standoff seat screw seat_min")
deck_mounts = {name: DeckMount(*row) for name, row in _above_mounts.deck_mounts().items()}


def deck_mount_xy(name):
    """Explicit selected boss centres in the cap's own frame."""
    return tuple(sorted(set(deck_mounts[name].points)))


def deck_mount_standoff(name):
    """How far proud of the lid's outer face this mount's column tops stand."""
    return deck_mounts[name].standoff


def deck_mount_proud():
    """The tallest standoff in the pack — the foam assembly's own top over its lid's face.
    PCB columns pass through the lid."""
    return max((deck_mount_standoff(name) for name in deck_mounts), default=0.0)


def deck_mount_reach(name):
    """How far a seated screw runs past this mount's column top. A flush station's screw
    crosses the WHOLE lid on its way down — the top lid is solid to `foam_cap_lid_height`,
    and that is what a station under it spends before it reaches the column. A standing one
    meets its column at the head and crosses nothing. `seat` is what the head bears on before
    either — a board's own thickness, a hub's floor, or the fan of ring terminals that is the
    ground bus."""
    m = deck_mounts[name]
    over = m.seat
    if m.standoff == 0.0:
        over += foam_cap_lid_height + cap_lid_clearance
    return m.screw - over


deck_mount_bore_depth = max(deck_mount_insert_length + deck_mount_bore_relief,
    max(
    (m.screw - m.seat_min - (foam_cap_lid_height + cap_lid_clearance
                           if m.standoff == 0.0 else 0.0)
     for m in deck_mounts.values()), default=0.0) + deck_mount_bore_relief)
_mount_reach = bound(
    "deck-mount-reach", "Every deck mount's screw reaches the whole of its insert",
    f"{deck_mount_insert_length:g} mm into the column")
for _name in deck_mounts:
    _mount_reach(
        deck_mount_reach(_name) >= deck_mount_insert_length,
        f"deck mount {_name}: an M3 × {deck_mounts[_name].screw:g} through "
        f"{deck_mounts[_name].seat:g} mm of seat reaches {deck_mount_reach(_name):g} mm "
        f"into the column, short of its {deck_mount_insert_length:g} mm insert")


def deck_lid_hole_radius(name):
    """The lid's opening at a deck-mount station: a slip fit around a column standing
    through it, a screw clearance over one that stops beneath it."""
    if deck_mount_standoff(name) == 0.0:
        return screw_clearance_radius
    return deck_mount_boss_radius + deck_mount_lid_slip


# --- Horizontal valve cradles -----------------------------------------------
#
# The lid carries V-B's upright valve wall, supplied by `_above_core_mounts`.
# Horizontal plinth stations use this table; the current cap has none.
Cradle = namedtuple("Cradle", "centre yaw seat")
cap_cradles = {}

# Where a boss stands off the valve's centre, and how wide it is: a socket with a wall around it.
cap_cradle_corner_inset_x = _valve_seat.corner_inset_x
cap_cradle_corner_inset_y = _valve_seat.corner_inset_y
cap_cradle_socket_radius = _valve_seat.socket_radius
cap_cradle_wall = _valve_seat.wall
cap_cradle_boss_radius = _valve_seat.boss_radius
cap_cradle_half_x = _valve_seat.seat_half_x
cap_cradle_half_y = _valve_seat.seat_half_y
cap_cradle_corner_radius = _valve_seat.seat_corner_radius

# What a cradle holds off every other thing cut in the lid's outer face. Nothing is poured
# between them — this face is the machine's room, not the cup's — so the fence is the
# machine's own clearance floor rather than the pour gap the cavity keeps.
cap_cradle_room_gap = 1.0


def cap_cradle_xy(name):
    """A cradle's four socket centres, in the cap's own frame."""
    (cx, cy) = cap_cradles[name].centre
    th = math.radians(cap_cradles[name].yaw + 90.0)
    c, s = math.cos(th), math.sin(th)
    return tuple((cx + c * sx * cap_cradle_corner_inset_x - s * sy * cap_cradle_corner_inset_y,
                  cy + s * sx * cap_cradle_corner_inset_x + c * sy * cap_cradle_corner_inset_y)
                 for sx in (-1, 1) for sy in (-1, 1))


def cap_cradle_half_extents(name):
    """Axis-aligned half extents of the plinth in the cap's frame."""
    th = math.radians(cap_cradles[name].yaw + 90.0)
    c, s = abs(math.cos(th)), abs(math.sin(th))
    return (c * cap_cradle_half_x + s * cap_cradle_half_y,
            s * cap_cradle_half_x + c * cap_cradle_half_y)


def cap_cradle_circle_gap(name, x, y, radius):
    """Plan clearance from a circular opening to the rounded plinth outline."""
    (cx, cy), yaw, _seat = cap_cradles[name]
    th = math.radians(yaw + 90.0)
    dx, dy = x - cx, y - cy
    px = abs(math.cos(th) * dx + math.sin(th) * dy)
    py = abs(-math.sin(th) * dx + math.cos(th) * dy)
    qx = px - (cap_cradle_half_x - cap_cradle_corner_radius)
    qy = py - (cap_cradle_half_y - cap_cradle_corner_radius)
    return (math.hypot(max(qx, 0.0), max(qy, 0.0))
            + min(max(qx, qy), 0.0) - cap_cradle_corner_radius - radius)


def cap_cradle_rectangle_gap(name, x0, x1, y0, y1):
    """Plan clearance to an axis-aligned rectangle at these cap stations."""
    (cx, cy), yaw, _seat = cap_cradles[name]
    assert math.isclose(yaw % 90.0, 0.0), "plinth rectangle reading needs an axial station"
    hx, hy = cap_cradle_half_extents(name)
    core_x, core_y = hx - cap_cradle_corner_radius, hy - cap_cradle_corner_radius
    dx = max(x0 - (cx + core_x), (cx - core_x) - x1, 0.0)
    dy = max(y0 - (cy + core_y), (cy - core_y) - y1, 0.0)
    return math.hypot(dx, dy) - cap_cradle_corner_radius


def cap_cradle_room(name):
    """Least plan clearance around the plinth and its conduit edge passages."""
    room = []
    for cname, (x, y) in cap_conduits.items():
        gap = cap_cradle_circle_gap(name, x, y, cap_conduit_entry_relief_radius)
        # The plinth opens a full-height passage with this radial clearance.
        room.append((max(gap, cap_cradle_room_gap), f"the {cname} conduit passage"))
    for x, y in attachment_xy_positions:
        room.append((cap_cradle_circle_gap(name, x, y, head_cbore_radius),
                     "a clamp screw's counterbore"))
    for dname in deck_mounts:
        for x, y in deck_mount_xy(dname):
            room.append((cap_cradle_circle_gap(name, x, y, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    cx, cy = cap_cradles[name].centre
    hx, hy = cap_cradle_half_extents(name)
    room.append((min(outer_shell_x_length / 2.0 - abs(cx) - hx,
                     outer_shell_y_length / 2.0 - abs(cy) - hy),
                 "the lid's own edge"))
    for other, station in cap_cradles.items():
        if other == name:
            continue
        ox, oy = station.centre
        ohx, ohy = cap_cradle_half_extents(other)
        # The rectangle includes the other plinth's rounded corners.
        room.append((cap_cradle_rectangle_gap(name, ox-ohx, ox+ohx, oy-ohy, oy+ohy),
                     f"the {other} plinth"))
    return min(room)


# --- Cap conduits ------------------------------------------------------------
#
# A conduit is one of the cup's own full-height columns carrying a THROUGH bore: liquid
# foam pours around its shank the way it pours around a deck mount's, the lid passes it,
# and a line runs up it from the shell's open top out onto the lid's outer face. The
# service bay stands on that face.
lldpe_tube_od = 6.35                         # the 1/4" line every fluid port on the core takes
cap_conduit_bore_radius = port_hole_radius   # the ⌀[7.5](PORT_HOLE_DIAMETER) every shell penetration takes
# The A-fill tube completes its offset below the lid's outer face. Its
# larger straight through-hole clears that bend without a blind cavity.
cap_conduit_bore_radii = {"reservoir-a-fill": 5.5}
cap_conduit_wall = wall_thickness
cap_conduit_boss_radius = cap_conduit_bore_radius + cap_conduit_wall
cap_conduit_lid_slip = deck_mount_lid_slip   # per side, a standing column to the lid's clearance hole

# How far off its own bore axis a line leaves a conduit — a bore's `manifold_layout.FLAVOR_SKEW`.
# The LID'S HOLE IS COUNTERSUNK to this angle: the lip a leaning line crosses lies along it, and
# what the tube bears on there is a face. Everything under that countersink carries the bore on
# its own axis — the rest of the lid's plate and the column beneath it, one straight run.
# `_lines.CAP_BORE_SKEW` is bound to this name.
cap_conduit_entry_skew = 38.0
# The countersink's mouth on the lid's outer face — the bore opened at that angle through the
# one wall of plate the cone is sunk into: ⌀[10.63](ENTRY_RELIEF_D).
cap_conduit_entry_relief_radius = (
    cap_conduit_bore_radius
    + wall_and_floor_thickness * math.tan(math.radians(cap_conduit_entry_skew)))
# The relief stands inside the boss its own column carries, so `cap_conduit_wall_neck` and
# `cap_conduit_pair_neck` fence the cone where they fence the column. A wall of boss over a cone
# one wall deep puts that ceiling at [49.96°](ENTRY_SKEW_CEILING).
cap_conduit_entry_skew_ceiling = math.degrees(
    math.atan2(cap_conduit_wall, wall_and_floor_thickness))
# The mouth passes the tube's SECTION and not just its centreline: a ⌀[6.35](LLDPE_TUBE_OD) line
# crossing the outer face at that lean reads `r / cos(skew)` wide in the face's own plane.
state(
    "entry-passes-section", "The countersink's mouth passes the leaning tube's whole section",
    f"⌀{lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)):.2f} across the face",
    cap_conduit_entry_relief_radius >= (
        0.5 * lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)) - 1e-9),
    f"cap conduit entry: a ⌀{lldpe_tube_od:g} line leaning {cap_conduit_entry_skew:g}° reads "
    f"{lldpe_tube_od / math.cos(math.radians(cap_conduit_entry_skew)):.2f} mm across the lid's "
    f"face, over the ⌀{2.0 * cap_conduit_entry_relief_radius:.2f} the relief opens to")

# Per conduit: its centre in the CAP'S OWN frame. The cap installs spun a half turn about
# Z (`foam_assembly.spin_xy`), and a half turn is its own inverse — so a conduit that
# stands over a carbonator port at (x, y) in the shell's frame is authored at (−x, −y) here,
# and `foam_assembly.cap_conduit_station` turns it back.
#   A CONDUIT IS ONE END OF A LINE, and what the line does at the far end is what this table
# is for; `_internal_routes` draws every one of them and measures it against the shell. Seven
# stand here, and they answer to the carbonator and the two reservoirs. TWO ENTER THE
# CARBONATOR (water at the top plate, CO2 at the bottom) and one draws it; each reservoir is
# entered once at its cap and drawn once from its floor, by a dip tube down through that same
# cap. Every line that ENTERS one of the three arrives above that one's liquid and every line
# that LEAVES takes its lowest point, so nothing can enter and leave without crossing it. That
# is what the air-purge and clean-flush service modes run on.
#
#   water-in retains the carbonator's TOP-plate elbow and push-connect adapter.
# Its tube leaves on the fixed lateral clocking line and turns upward in
# the open body before the cup floor. The aligned cup and lid guide is straight.
# An accessible R18 arch above the lid joins the upward check elbow. The
# plain guide adds no socket or tube break; its cylindrical wall is 3 mm.
#   reservoir-a-fill and reservoir-b-fill, the two FILLS, stand over their own reservoirs rather
# than over a band, and have no run inside the shell at all: each is the column between a valve
# on the deck and the bore in the cap of the reservoir it fills, and that cap's own outer face is
# the last thing under this one, so the two features meet across the pour clearance over the
# reservoir and nothing else (`_internal_routes` draws and measures the stub). The bore it lands
# on opens into the reservoir's HEADSPACE, above the liquid and clear of the vent boss, the rod
# register and every screw boss — so what arrives falls into the cavity and can only leave by the
# draw. `reservoir_fill_conduit_xy` is the station, and `reservoir_fill_sides` is which
# reservoirs have one.
#   reservoir-a and reservoir-b, the two DRAWS, stand over their own reservoirs the same way, and
# the line that comes down one does not stop at the cap: it is its own dip tube, down the cap's
# draw bore to the reservoir's floor, so the column over it is the top of one straight drop and
# the internal route is that drop (`_internal_routes`). `reservoir_draw_conduit_xy` is the station.
#   carb-water-out — the carbonator's BOTTOM-PLATE +Y port, under the liquid, which is the
# carbonator's own drain and the dispense line's source. The elbow turns it laterally, it crosses
# under the carbonator inboard of the support ring, leaves the ring through the ring's OWN SLOT on
# this bore's column (`_port_cuts.water_outlet_ring_crossing_x` — no bore, and the four bearing
# segments stay whole), and climbs beside the coil clear of the port lane until the carbonator's top
# plate is under it. Only there does it step out onto the lane and into this bore. That climb is
# inboard because the CO2 owns the lane's own strip at the bottom of the shell.
#   Its X answers to THE COIL'S OWN TAIL: the climb runs
# in the annulus between the wrapped coil and a reservoir pocket's centreward arc, which is
# where the evaporator's inlet tail turns off its helix, and one bore of that annulus holds one
# run. The column stands clear of the tail's own, and far enough round that the ring crossing
# under it still falls inside one ring slot (`_port_cuts.water-outlet-slot`) — those two fences
# leave a 2.5 mm band and this is in it.
#   co2-in stands over the PORT LANE and its line runs DOWN it, the one conduit here that feeds
# rather than drains. It falls the shell's whole height, turns along the lane's floor and leans
# in to `_port_cuts.co2_inlet_xyz` through one of the support ring's slots, to land on the
# collet made up under the bottom plate's lane-side port. That port opens directly into the
# water column; gas rises to the headspace. Because the line arrives from above, it is laid
# down the lane before the top cap goes on.
#   ITS FALL IS THE ONLY RISER THE LANE CARRIES. A lane is one bore wide, so a riser in it is a
# wall to everything crossing that column, and the lane's other traffic all runs WEST at one
# storey each: the evaporator's inlet copper drops onto the lane beside the carbonator and takes it to
# its exit station (`_copper_ports.stations()`), and the carbonated water joins only once it is over
# the carbonator.
# The PRV shroud lies on the west lane and its vent leaves through the +Y flank.
#   WHERE THE LEAN CROSSES is the Carbonator SUPPORT RING's business, not this file's. The reach in
# from the lane to the bottom plate's port crosses the ring, and the ring is four bearing
# segments with four slots between them (`_support_ring`); a reach that misses a slot would have
# to be bored through a segment that carries the carbonator. `_port_cuts.co2-inlet-slot` is that
# fence, and `co2_lane_x` is the column whose lean lands inside slot four. Reservoir A stands on
# its pocket's floor, so the lean also keeps out of that pocket: struck from here it passes
# outboard of the pocket's centreward corner, and the ring's slots are clocked to meet it
# (`_support_ring.slot_clock`).
co2_lane_x = 48.0
# The cap guide follows the above-core gas chain. Its descent stays in the
# existing port lane and reaches the independently fixed support-ring approach
# below it; the carbonator port and its fitting retain their own stations.
co2_cap_x = _above_mounts.gas_guide_xy()[0]
# THE CARBONATED WATER IS SPLIT THE SAME WAY, at the other end of its line. Its CLIMB is
# pinned: it crosses the carbonator support ring at one of the ring's own four slots, so the column
# it rises on may not wander without notching a bearing segment, and the slot leaves it under
# 8 mm of travel — all of it under the same deck body its bore has to dodge. Its cap bore has
# no such tie: the run is already on the lane by then, and a jog ALONG a lane costs it nothing.
# So the ring reads this column and the appliance reads the bore's, and neither is the other's.
water_outlet_climb_x = -48.5
# The lower climb clears the inlet copper tail. Once over the tail's lead — it runs at
# `evap_tail_low_z`, and both lines are 1/4" OD, so one OD and a 2 mm foam hug clear it —
# the tube drifts along the coil standoff to the column where its climb and its lean out to
# the lane stand clear of reservoir B's −Y centerward pocket corner, so that pocket's wall is
# never opened. Every turn keeps the stock bend radius.
water_outlet_upper_climb_x = -35.0
water_outlet_drift_z = (evap_tail_low_z + lldpe_tube_od + 2.0, 140.0)
# Reservoir A's ribbon leaves through the cap. B's ribbon leaves the shell
# rim through `_reed_b_outlet`; its dry channel and sensing axis stay fixed.
reed_cable_conduit_x = reed_column_axis_x
reed_cable_conduit_y = level_rod_y


def reed_cable_conduit_xy(side):
    """One side's reed-cable conduit in the CAP's frame — the cap installs spun a half turn,
    so a bore over the shell-frame station `(x, y)` is authored at `(−x, −y)` here."""
    return (-side * reed_cable_conduit_x, -reed_cable_conduit_y)


cap_fluid_conduits = {
    "water-in": _above_mounts.cap_guide_xy("water-in", (86.2532889963965, 32.80179966121266)),
    "reservoir-a": reservoir_draw_conduit_xy(+1),
    "reservoir-b": _above_mounts.cap_guide_xy("B-draw", reservoir_draw_conduit_xy(-1)),
    "reservoir-a-fill": _above_mounts.cap_guide_xy("A-fill", reservoir_fill_conduit_xy(+1)),
    "reservoir-b-fill": reservoir_fill_conduit_xy(-1),
    "carb-water-out": _above_mounts.cap_guide_xy("carb-water-out", (52.2, -port_lane_mid_y)),
    "co2-in": _above_mounts.gas_guide_xy(),
}
# Cable passages use the same column and bore construction as fluid conduits.
# The reservoir passages open over their reed channels; the shared sensor
# passage opens into the main foam cavity.
cap_cable_floor_conduits = {
    "reed-cable-a": reed_cable_conduit_xy(+1),
    # Temperature 3P, carbonator reeds 3P and the dedicated PE lead
    # gather above the vessel and rise straight through the cap.
    "sensor-cable": (-23.2, -48.0),
}
cap_cable_conduits = {name: _above_mounts.cap_guide_xy(name, xy)
                      for name, xy in cap_cable_floor_conduits.items()}
cap_conduits = {**cap_fluid_conduits, **cap_cable_conduits}
# Water, soda, both draws and gas have aligned straight cap entries. A-fill
# uses a straight 11 mm lid opening above its tangent below-lid offset.
# B-fill enters the cap's front face and turns to its retained lower reservoir seat.
# Both cable guides stand directly above their floor entries.
cap_conduit_floor_xy = {
    **cap_conduits,
    **cap_cable_floor_conduits,
    "water-in": _above_mounts.water_in_floor_xy(),
    "reservoir-b": reservoir_draw_conduit_xy(-1),
    "reservoir-a-fill": reservoir_fill_conduit_xy(+1),
    "reservoir-b-fill": reservoir_fill_conduit_xy(-1),
    "carb-water-out": cap_conduits["carb-water-out"],
}
cap_passive_guides = ("reservoir-a-fill",)
cap_cable_guides = tuple(cap_cable_conduits)
# A full-height web closes a foam gap between two columns too narrow to pour; the bore axes and
# their 7.5 mm clear passages are independent of that stock. Every pair here stands the pour gap
# apart, so none is linked.
cap_conduit_links = ()
cap_conduit_link_width = 5.0

# Names pair the core's fill connections with their reservoir bores. Their
# upper guides can differ from the lower entries while the cap joins them.
_fill_conduits = {n for n in cap_conduits if n.endswith("-fill")}
_fill_wanted = {f"reservoir-{'ab'[s < 0]}-fill" for s in reservoir_fill_sides}
state(
    "fill-conduits-paired", "Every fill bore has a conduit over it and every conduit a bore",
    f"the cap's fills naming {sorted(_fill_wanted)}",
    _fill_conduits == _fill_wanted,
    f"reservoir fills: {sorted(_fill_conduits)} stand on the cap, but "
    f"`reservoir_fill_sides` cuts {reservoir_fill_sides} — a conduit with no bore under it "
    f"is a hole into a sealed pocket, and a bore with no conduit over it is a blind one")
# What a line arriving off-axis turns in: the band from a top-plate elbow's own lateral
# axis up to the cap's floor, against the rise a corner of 1/4" LLDPE takes.
carbonator_top_plate_z = wall_and_floor_thickness + carbonator_support_ring_height + carbonator_height
top_band_to_cap = foam_shell_outer_height - (carbonator_top_plate_z + hole_shift_from_edge)
# [25.4 mm](LLDPE_BEND_R) — the cold core's 4 × OD routing allowance. Actual drawn corner
# radii follow `_routing.stock_min`; the cured foam retains the internal routes.
# A bend radius alone does not specify the unloaded shape of an exposed tube.
lldpe_bend_radius = 4.0 * lldpe_tube_od


def cap_conduit_wall_neck(x, y):
    """What a conduit standing near the cup's PERIMETER leaves: `(mm, what)`.

    The same two states a pair of conduits has (`cap_conduit_pair_neck`), read against the
    wall instead of against another column. APART, with the pour gap between the column and
    the wall's inner face, so foam reaches down behind it. Or MERGED into the wall, and then
    what carries the joint is the material left OUTBOARD of the bore, which must be a wall
    thick — the column is no longer a post in the pour, it is a local thickening of the wall
    the bore runs up.
    A column that neither clears the wall nor reaches it stands tangent, which closes the
    same knife edge a tangent pair does."""
    to_outer = min(outer_shell_x_length / 2.0 - abs(x), outer_shell_y_length / 2.0 - abs(y))
    if to_outer - outer_shell_wall >= cap_conduit_boss_radius:
        return (to_outer - outer_shell_wall - cap_conduit_boss_radius,
                "the pour gap behind a standing column")
    return (to_outer - cap_conduit_bore_radius, "the wall left outboard of a merged bore")


_conduit_wall = bound(
    "cap-conduit-wall", "Every conduit column stands the pour gap off the wall or merges in",
    f"the pour gap apart or a {cap_conduit_wall:g} mm neck")
for _name in cap_conduits:
    _neck, _what = cap_conduit_wall_neck(*cap_conduits[_name])
    _want = deck_mount_cap_gap if _what.startswith("the pour") else cap_conduit_wall
    _conduit_wall(
        _neck >= _want - 1e-9,
        f"cap conduit {_name}: {_what} is {_neck:.3f} mm, under the {_want:g} mm it takes "
        f"— a column either stands the pour gap off the wall or merges into it")


def foam_cap_lid_pour_xy(top=False):
    """The top lid's fore-west pour station, or the bottom lid's: nearest the cap centreline
    with room beside mounts and plinths."""
    if top:
        return top_lid_pour_xy
    x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    bands = []

    def fence(sx, sy, need):
        reach = need ** 2 - (x - sx) ** 2
        if reach > 0.0:
            half = math.sqrt(reach)
            bands.append((sy - half, sy + half))

    for name in deck_mounts:
        for sx, sy in deck_mount_xy(name):
            fence(sx, sy, foam_cap_lid_pour_radius + screw_clearance_radius
                  + deck_mount_cap_gap)
    for name, station in cap_cradles.items():
        assert math.isclose(station.yaw % 90.0, 0.0)
        cx, cy = station.centre
        hx, hy = cap_cradle_half_extents(name)
        core_x, core_y = hx - cap_cradle_corner_radius, hy - cap_cradle_corner_radius
        reach = foam_cap_lid_pour_radius + deck_mount_cap_gap + cap_cradle_corner_radius
        dx = max(abs(x - cx) - core_x, 0.0)
        if dx < reach:
            half = core_y + math.sqrt(reach * reach - dx * dx)
            bands.append((cy - half, cy + half))
    # MERGE FIRST, THEN STEP. Two stations near each other throw overlapping bands, and a
    # hole stepped off one lands inside the next — so the bands are run together into the
    # spans they actually close before the offset is read, and the answer is the nearer edge
    # of the one span that holds the centreline.
    merged: list = []
    for lo, hi in sorted(bands):
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    y = 0.0
    for lo, hi in merged:
        if lo < y < hi:
            y = lo if (y - lo) <= (hi - y) else hi
            break
    return (x, y)


def foam_cap_lid_vent_xy(top=False):
    """Both vent holes' centres in the lid — the −X corners, mirrored across y, where the
    pour hole is not and nothing stands. Air leaves by whichever is uppermost."""
    x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset
          + (top_lid_vent_setback if top else 0.0))
    y = outer_shell_y_length / 2 - foam_cap_lid_hole_inset
    return ((x, y), (x, -y))


# Clearances are read on the complete plinth outline. Its conduit passages are
# cut separately; each socket keeps its complete surrounding wall beside them.
_cradle_room = bound(
    "cradle-room", "Every plinth clears the other openings on the lid",
    f"{cap_cradle_room_gap:g} mm off the nearest")
for _name in cap_cradles:
    _room, _what = cap_cradle_room(_name)
    _cradle_room(_room >= cap_cradle_room_gap - 1e-9,
                 f"valve plinth {_name}: {_room:.3f} mm off {_what}")
    for _sx, _sy in cap_cradle_xy(_name):
        for _hx, _hy in cap_conduits.values():
            _room = (math.hypot(_sx - _hx, _sy - _hy)
                     - cap_cradle_boss_radius - cap_conduit_entry_relief_radius)
            _cradle_room(_room >= cap_cradle_room_gap - 1e-9,
                         f"valve plinth {_name}: conduit passage preserves each socket wall")


# --- Body and tube cradles on the lid's outer face ---------------------------
#
# The single water check's fixed barrel rests in a round cradle. A tie through
# the channel beneath it prevents lift-out and leaves both collets accessible.
# The pump and check share this lid; their tube spans no enclosure joint.
# Tube cradles use the existing removable anchor caps.
#
# Centres and bore radii are in the cap frame. A stated `over_face` holds the
# installed axis at its required height; otherwise the floor and channel stock
# determine it. `anchor_rows` compares the bore and the sections under its span.
CapAnchor = namedtuple("CapAnchor", "centre seat_r over_face along closure")
CapAnchor.__new__.__defaults__ = (None, "x", "tie")
cap_anchors = {}

# What a zip tie is, wherever one is cut for on this cap. `enclosure.tie_w` is the same
# fastener stated for the other box; `enclosure_assembly.check_tie_vocabulary` holds the two
# against each other.
# `cap_anchor_tie_loop` gives the nominal water-check/body loop recorded in
# foam-cap/above-core-native-review.json.
# Its 2.5 mm band crosses only the fixed barrel, clear of both moving collets.
cap_anchor_tie_w = 2.5              # the 18 lb zip tie, across its width — 0.1"
cap_anchor_cav_buffer = 2.0 * fits.slip
cap_anchor_cav_w = cap_anchor_tie_w + cap_anchor_cav_buffer
# Solid either side of the channel, ALONG the run: what the rib keeps of itself at each end.
cap_anchor_cav_wall = 3.0
# ITS LENGTH ALONG THE BODY IS ITS CHANNEL'S. One zip tie crosses one anchor, so the rib is that
# zip tie's cavity with `cap_anchor_cav_wall` of itself at each end of it.
cap_anchor_len = cap_anchor_cav_w + 2.0 * cap_anchor_cav_wall
# One wall of material under the bore's floor, and one more from there down to the lid's face —
# the height the rib's two ends stand, and the zip tie's channel between them. `valve_seat`'s is
# the wall this face already carries.
cap_anchor_wall = cap_cradle_wall
# Leave the supported-surface allowance at the roof, above the flat lid floor.
cap_anchor_channel_height = cap_anchor_wall + fits.supported_surface


def cap_anchor_axis_over_face(name):
    """How far the seated body's AXIS stands over the lid's outer face.

    Three layers of the rib, read from the face up: the channel the zip tie is pushed through, one
    `cap_anchor_channel_height`; the material under the bore, one `cap_anchor_wall`; then the bore's own radius. A body
    seated lower than that sits on its own zip tie. A capped rib has no channel, so its two
    layers are the material under the bore and the bore.

    A row that STATES its own height is one whose body cannot move to meet the rib, so the rib is
    built up to it. What it must not do is come out under its layers, which is the same floor a
    seated body has."""
    row = cap_anchors[name]
    stated = row.over_face
    least = row.seat_r + cap_anchor_wall + (0.0 if row.closure == "cap" else cap_anchor_channel_height)
    if stated is None:
        return least
    if stated < least - 1e-9:
        raise ValueError(
            f"cap_anchor_axis_over_face: {name} states {stated:.3f} mm over the lid's face and "
            f"the rib's own layers come to {least:.3f}. A seat lower than that stands the body on "
            f"the lid or on its own zip tie.")
    return stated


def cap_anchor_tie_loop(name):
    """The shortest zip tie that closes round the seated body and the rib together.

    A zip tie turns INSIDE the channel, so what it reaches round is the body with the rib's own
    back behind it — the convex perimeter of that pair, and not of the lid the rib stands on.
    Read on the bore rather than on the body, which is the section this part knows.

    The hull uses the rib's actual height beneath the stated axis, with the bore above it: its floor, its two flanks,
    a tangent from each top corner onto the bore, and the arc between the two tangent points."""
    r = cap_anchors[name].seat_r
    if name == 'discharge-chain':
        data = _above_mounts.check_support_datums()
        w = data['half_width_mm']
        h = data['centre_world_mm'][2]-data['tie_route_z_mm']
        # Convex loop around the circle and the lower-east rectangular
        # quarter bearing: bottom, east face, two tangents and retained arc.
        return (w+h+math.sqrt(w*w-r*r)+math.sqrt(h*h-r*r)
                +r*(1.5*math.pi-math.acos(r/w)-math.acos(r/h)))
    else:
        w = r + cap_anchor_wall
        h = cap_anchor_axis_over_face(name) - cap_anchor_channel_height
    return 2.0 * w + 2.0 * h + 2.0 * math.sqrt(w * w - r * r) + r * (math.pi - 2.0 * math.acos(r / w))


def cap_anchor_slotted(name):
    """Whether a capped rib's lid gives the cap's wings their slots: its face standing inside the
    wings' reach (`_anchor_cap_interface.wing_room`)."""
    return (cap_anchors[name].closure == "cap"
            and cap_anchor_axis_over_face(name) < _anchor_cap.SLOT_TOP - _anchor_cap.HEADROOM / 2.0)


def cap_anchor_room(name):
    """The least room this rib leaves to anything else opening on the lid's outer face:
    `(mm, what)` — a conduit's entry countersink, a clamp screw's counterbore, a deck mount's
    lid hole, a cradle boss, the pour hole, a vent, the lid's own edge.

    Read on the rib's own rectangle, which is the whole of it: its length down the row's own
    axis and one `reach` either side of the centre across it — a tied rib's `cap_anchor_len`, a
    capped rib's `_anchor_cap_interface.RIB_LEN` and, where the lid gives the cap's wings their
    slots, the slots' outer walls."""
    row = cap_anchors[name]
    (cx, cy) = row.centre
    if row.closure == "cap":
        length = _anchor_cap.RIB_LEN
        reach = _anchor_cap.RIB_R + (_anchor_cap.SLOT_W if cap_anchor_slotted(name) else 0.0)
    else:
        length, reach = cap_anchor_len, row.seat_r + cap_anchor_wall
    along, across = (length / 2.0, reach) if row.along == "x" else (reach, length / 2.0)
    x0, x1 = cx - along, cx + along
    y0, y1 = cy - across, cy + across

    def off(px, py, r):
        """How far a disc of radius `r` at (px, py) stands off the rib's rectangle."""
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        return math.hypot(dx, dy) - r

    room = []
    for cname, (bx, by) in cap_conduits.items():
        room.append((off(bx, by, cap_conduit_entry_relief_radius),
                     f"the {cname} conduit's entry"))
    for bx, by in lid_attachment_xy_positions:
        room.append((off(bx, by, head_cbore_radius), "a clamp screw's counterbore"))
    for dname in deck_mounts:
        for dx, dy in deck_mount_xy(dname):
            room.append((off(dx, dy, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    for vname in cap_cradles:
        room.append((cap_cradle_rectangle_gap(vname, x0, x1, y0, y1),
                     f"the {vname} plinth"))
    room.append((min(outer_shell_x_length / 2.0 - abs(x0),
                     outer_shell_x_length / 2.0 - abs(x1),
                     outer_shell_y_length / 2.0 - abs(y0),
                     outer_shell_y_length / 2.0 - abs(y1)), "the lid's own edge"))
    return min(room)


# The rib stands on a plate it only touches, so everything the face opens has to be somewhere
# else: a rib over a hole is a channel with no floor and a zip tie that falls into the cup.
_anchor_room = bound(
    "anchor-room", "Every chain anchor stands its room off everything else the face opens",
    f"{cap_cradle_room_gap:g} mm off the nearest")
for _name in cap_anchors:
    _room, _what = cap_anchor_room(_name)
    _anchor_room(
        _room >= cap_cradle_room_gap - 1e-9,
        f"chain anchor {_name}: the rib stands {_room:.3f} mm off {_what}, inside the "
        f"{cap_cradle_room_gap:g} mm this face keeps between two things it opens")


# --- the anchors that grip SIDEWAYS -----------------------------------------
#
# The ribs above open at the sky: a run is laid down into the trough and the zip tie comes up round
# it. A run laid ACROSS this lid cannot be held that way. `water-3` crosses the machine along the
# cap's own Y, one lane off the core's front face, and an upward trough on that line would open
# its mouth at the funnel — a tube dropped into it would come down through the storey the
# source valves fill.
#
# SO THIS ONE STANDS ON THE STEP AND GRIPS THE RUN FROM BEHIND. A post, its FORWARD face the run's
# own axis plane, a half pipe cut into that face, and the tube pushed in horizontally.
#
# THE POST GROWS ALONG THE CAP'S OWN −X, which the machine lays on world +Y: the pipe's axis
# plane is its forward face and everything behind it is between the run and the core the run is
# assembled onto. `centre` is that axis plane, so the post is on the far side of it from the room.
#
# THE TIE'S TUNNEL IS A WINDOW CUT THROUGH THE POST, front to back, hung one wall under the pipe.
# The tie goes through the window, out the front, round the tube and back over the post's crown,
# and buckles in the channel down its back — so the loop closes on the tube, and every millimetre
# the window stands off the pipe is a millimetre added to that loop and taken out of the post.
# Each station's `depth` runs aft from its front face along the cap's −X.
SideAnchor = namedtuple("SideAnchor", "centre over_face seat_r axis_off depth")

cap_side_wall = cap_anchor_wall           # every solid section in the post
cap_side_len = cap_anchor_len             # along the run, one tie's tunnel and its two flanks
cap_side_cav_w = cap_anchor_cav_w         # the tunnel's width, on the zip tie and its slip
cap_side_flank = (cap_side_len - cap_side_cav_w) / 2.0
# The 18 lb zip tie through its thickness — `enclosure.tie_t`, and the one figure the window
# has to leave standing.
cap_side_tie_t = 1.0
# WHAT THE WINDOW IS NOT IS THE WHOLE COLUMN UNDER THE PIPE. The up-opening ribs take their
# channel as the remainder between two feet, and a post that did the same would give the whole of
# its height to one: this post stands as tall as the run it grips, so on a high crossing the
# remainder is two `cap_side_flank` blades running the post's length with nothing but the roof
# joining them — a pair of towers to print where the section wants to be one block.
#   So the window is a STATED height and the rest of that column is the post's own stock, which
# is `enclosure.tube_anchor_cavity_depth`'s bargain read on this face: a 1 mm zip tie needs its
# own thickness and routing air, not every millimetre between a low run and a tall post.
cap_side_cav_h = cap_side_wall
# And a post whose pipe runs low keeps all the air it has. Capping a window that is already
# compact buys a fraction of channel back as a floor thinner than the room the cavity is cut
# with — `enclosure.tube_anchor_backing_min` again, and the same figure.
cap_side_cav_backing_min = 1.0  # printable stock, independent of tie clearance
# The tie's own channel down the post's back face, so the buckle seats and the zip tie cannot walk
# along the run.
cap_side_back_relief = 1.2
# The bore and the rear tie channel retain one nominal wall between them. The
# zip tie pulls the tube into that section; this geometric floor does not qualify
# its retention load or endurance.
cap_side_web = cap_side_wall

cap_side_anchors = {}


def cap_side_axis_y(name) -> float:
    """The pipe's axis in the cap's own X — the post's front face, stood `axis_off` forward of
    it. The cap's +X is the world's forward, so the axis is at the greater figure."""
    a = cap_side_anchors[name]
    return a.centre[0] + a.axis_off


def cap_side_wrap_deg(name) -> float:
    """How much of the tube's own circle the seat closes on, in degrees. A pipe on the face
    itself takes half; one stood proud of it takes less, and what makes up the difference is the
    tie."""
    a = cap_side_anchors[name]
    return 2.0 * math.degrees(math.acos(a.axis_off / a.seat_r))


def cap_side_tunnel_roof(name) -> float:
    """The tunnel's roof over the lid's outer face — one wall under the pipe, which is the whole
    of the column the post has to hand the zip tie."""
    a = cap_side_anchors[name]
    return a.over_face - a.seat_r - cap_side_wall


def cap_side_tunnel_h(name) -> float:
    """The tunnel's own height, hung under that roof.

    A post with the column to spend gives the window `cap_side_cav_h` of it and stands its own
    stock under the rest, so what prints below the pipe is one block and not two blades. A post
    whose pipe runs low keeps all the air it has, since a window capped there would trade the
    channel for a floor thinner than `cap_side_cav_backing_min`."""
    roof = cap_side_tunnel_roof(name)
    if roof - cap_side_cav_h >= cap_side_cav_backing_min - 1e-9:
        return cap_side_cav_h
    return roof


def cap_side_anchor_height(name) -> float:
    """How tall the post stands over the lid's outer face — the axis, the pipe's own radius over
    it, and one wall over that."""
    a = cap_side_anchors[name]
    return a.over_face + a.seat_r + fits.supported_surface + cap_side_wall


def cap_side_anchor_holds(name) -> None:
    """The post's own stack, against what the run's height gives it.

    A run laid closer to the lid's face than the pipe, one wall and the zip tie together is a run
    with no tie path under it, and the post would stand on its own zip tie."""
    a = cap_side_anchors[name]
    roof = cap_side_tunnel_roof(name)
    if roof < cap_side_tie_t - 1e-9:
        raise ValueError(
            f"cap_side_anchor_holds: {name} runs {a.over_face:.3f} mm over the lid's face; the "
            f"pipe takes {a.seat_r:.3f} of that and one wall {cap_side_wall:.3f} more, leaving "
            f"{roof:.3f} mm under it where the zip tie is {cap_side_tie_t:g} thick. What gives "
            f"way here is the run's own lane, not the lid: route it further off that face.")
    # The bore eats forward from the front face and the tie's channel eats back from the rear one,
    # and they meet over the pipe: what is left between them is the whole of the web, so the
    # relief comes off the reading the same way the seat does.
    web = a.depth + a.axis_off - a.seat_r - cap_side_back_relief
    if web < cap_side_web - 1e-9:
        raise ValueError(
            f"cap_side_anchor_holds: the post runs {a.depth:.3f} mm back from its face; "
            f"the pipe takes {a.seat_r - a.axis_off:.3f} of that and the tie's channel "
            f"{cap_side_back_relief:g} more, leaving a web of {web:.3f} where this face wants "
            f"{cap_side_web:g}. What caps the depth is the body behind the post, so what gives "
            f"is the pipe or the lane — not the web.")


def cap_side_anchor_tie_loop(name) -> float:
    """The shortest tie that closes round the tube and the post's own back together.

    A tie turns INSIDE the window, so what it reaches round is everything ABOVE the window: the
    tube, and the block of post between the window's roof and the post's own crown. That crown
    is one wall PROUD OF THE TUBE'S TOP, so the loop clears the post there and not the pipe, and
    the figure is not the up-opening ribs' — theirs stops on the axis plane.
      The hull is that block's rectangle with the pipe bulging out of one face: the window's own
    floor, the crown, the back face between them, a tangent from each front corner onto the pipe,
    and the arc the two tangent points leave. Read on the post's own faces, so the back channel's
    relief is slack the tie does not have to reach round.
      IT IS THE WINDOW'S HEIGHT THAT SETS IT, which is why the window is stated rather than left:
    a window taken as the remainder under the pipe carries the loop up with the post."""
    a = cap_side_anchors[name]
    w = a.seat_r + cap_side_wall
    tun_h = cap_side_tunnel_h(name)
    axis = tun_h + w                              # the pipe's axis over the window's floor
    crown = tun_h + 2.0 * w                       # and the post's crown over that same floor
    d_lo = math.hypot(a.axis_off, axis)           # the two front corners' reach to the axis
    d_hi = math.hypot(a.axis_off, crown - axis)
    sweep = (math.atan2(crown - axis, -a.axis_off)
             - math.atan2(-axis, -a.axis_off)) % (2.0 * math.pi)
    return (2.0 * a.depth + crown
            + math.sqrt(d_lo * d_lo - a.seat_r * a.seat_r)
            + math.sqrt(d_hi * d_hi - a.seat_r * a.seat_r)
            + a.seat_r * (sweep - math.acos(a.seat_r / d_lo) - math.acos(a.seat_r / d_hi)))


def cap_side_anchor_room(name):
    """The least room this post leaves to anything else opening on the lid's outer face:
    `(mm, what)` — a clamp screw's counterbore, a conduit's entry countersink, a deck mount's
    lid hole, a cradle boss, the pour hole, a vent, the up-opening ribs.

    A POST IS THE ONE THING ON THIS FACE THAT STANDS ON IT WITHOUT BEING CUT INTO IT, and that
    is why it needs saying. Every other body here opens THROUGH the plate, so two of them
    fouling shows up as a hole in the wrong shape; a post fouling one shows up as nothing at
    all — the lid comes off the plate correct and the screw under the post cannot be driven.
    `cap_anchor_room` reads the up-opening ribs the same way and this is its twin, on the
    family that stands on the cap's side instead.

    Read on the post's own rectangle, which is the whole of its footing. `centre` is NOT the
    middle of it in both axes: in the cap's X it is the post's FRONT FACE, the plane
    `axis_off` stands the pipe forward of, and the block runs the station's `depth` aft of that.
    In the cap's Y it is the middle, and the block is `cap_side_len` long about it."""
    a = cap_side_anchors[name]
    (cx, cy) = a.centre
    x0, x1 = cx - a.depth, cx
    y0, y1 = cy - cap_side_len / 2.0, cy + cap_side_len / 2.0

    def off(px, py, r):
        """How far a disc of radius `r` at (px, py) stands off the post's rectangle."""
        dx = max(x0 - px, 0.0, px - x1)
        dy = max(y0 - py, 0.0, py - y1)
        return math.hypot(dx, dy) - r

    room = []
    for bx, by in lid_attachment_xy_positions:
        room.append((off(bx, by, head_cbore_radius), "a clamp screw's counterbore"))
    for cname, (bx, by) in cap_conduits.items():
        room.append((off(bx, by, cap_conduit_entry_relief_radius),
                     f"the {cname} conduit's entry"))
    for dname in deck_mounts:
        for dx, dy in deck_mount_xy(dname):
            room.append((off(dx, dy, deck_lid_hole_radius(dname)),
                         f"the {dname} mount's lid hole"))
    for vname in cap_cradles:
        room.append((cap_cradle_rectangle_gap(vname, x0, x1, y0, y1),
                     f"the {vname} plinth"))
    for aname in cap_anchors:
        room.append((off(*cap_anchors[aname].centre,
                         cap_anchors[aname].seat_r + cap_anchor_wall),
                     f"the {aname} rib"))
    return min(room)


_side_anchor_room = bound(
    "cap-side-anchor-room", "Every side post stands clear of what the lid's face opens",
    f"{cap_cradle_room_gap:g} mm off the nearest")
for _name in cap_side_anchors:
    _room, _what = cap_side_anchor_room(_name)
    _side_anchor_room(
        _room >= cap_cradle_room_gap - 1e-9,
        f"cap side anchor {_name}: its post stands {_room:.3f} mm off {_what}, inside the "
        f"{cap_cradle_room_gap:g} mm this face keeps between two things it opens — a post over "
        f"one of them is a body no plate reads as fouled")


def cap_conduit_pair_neck(a, b):
    """What a PAIR of conduits leaves between them: `(mm, what)`.

    A pair is one of two things and never a third. APART, with at least the pour gap
    between the two columns, so foam reaches down between them. Or MERGED, the two bores
    standing nearer than a boss diameter and their columns fusing into one post — and then
    what matters is the NECK the lens leaves, which carries the joint and must be a wall
    thick. What neither may be is tangent: two circles meeting near a point close a knife
    edge that prints as a void and holds no load."""
    pair = frozenset((tuple(a), tuple(b)))
    for first, second in cap_conduit_links:
        if pair == frozenset((cap_conduits[first], cap_conduits[second])):
            return (cap_conduit_link_width, "the connecting web")
    r = cap_conduit_boss_radius
    d = math.hypot(a[0] - b[0], a[1] - b[1])
    if d >= 2.0 * r:
        return (d - 2.0 * r, "the pour gap between two standing columns")
    return (2.0 * math.sqrt(max(r * r - (d / 2.0) ** 2, 0.0)), "the neck their lens leaves")


_pair_neck = bound(
    "cap-conduit-pair", "Every pair of conduits stands apart or merges on a neck, never tangent",
    f"the pour gap apart or a {cap_conduit_wall:g} mm neck")
for _a, _b in itertools.combinations(sorted(cap_conduits), 2):
    _neck, _what = cap_conduit_pair_neck(cap_conduits[_a], cap_conduits[_b])
    _want = (deck_mount_cap_gap
             if _what.startswith("the pour") else cap_conduit_wall)
    _pair_neck(
        _neck >= _want - 1e-9,
        f"cap conduits {_a} and {_b}: {_what} is {_neck:.3f} mm, under the "
        f"{_want:g} mm it takes — a pair either stands the pour gap apart or merges on a "
        f"neck a wall thick")


def cap_conduit_shell_xy(name):
    """One cap conduit's station in the SHELL's own frame — where the line coming down it
    lands in the shell, which is the frame every band and lane in this file is stated in.

    The cap installs spun a half turn about Z (`foam_assembly.spin_xy`) and a half turn is
    its own inverse, so this is the authored pair negated. Everything that has to meet a
    conduit from BELOW reads it here."""
    x, y = cap_conduits[name]
    return (-x, -y)


# The face a cap conduit opens on, as a direction: the TOP cap's own +Z.
cap_conduit_axis = (0.0, 0.0, 1.0)


def cap_conduit_station(name):
    """One cap conduit's mouth in the CAP'S OWN frame: `(position, outward axis)`, with Z
    left at the lid's outer face for whoever seats the stack to carry."""
    x, y = cap_conduits[name]
    return ((x, y, 0.0), cap_conduit_axis)



def make_box(x_range, y_range, z_range):
    """Axis-aligned box from world-coordinate ranges in each axis."""
    from world_workplane import xy_plane_z_up, WorldWorkplane
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(((x_min + x_max) / 2, (y_min + y_max) / 2))
        .rect(x_max - x_min, y_max - y_min)
        .extrude(z_max - z_min)
        .unwrap()
    )


def build_z_axis_hole_punch(
    *,
    origin=(0, 0, 0),
    hole_punch_radius,
    hole_punch_height=40,
):
    """Z-axis ⌀ × height cylindrical cut, centered at `origin`'s X/Y and
    starting at `origin`'s Z, extruded in +Z."""
    import cadquery as cq
    from world_workplane import xy_plane_z_up
    x, y, z = origin
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(x, y, 0), offset=z)
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )


if __name__ == "__main__":
    sys.path.insert(
        0,
        str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
    )
    from docgen import substitute_py_comments

    variables = {
        "WALL_AND_FLOOR_THICKNESS": f"{wall_and_floor_thickness:.4g} mm",
        "COIL_RADIAL_CLEARANCE": f"{coil_radial_clearance:.4g} mm",
        "ABOVE_TANK_ELBOWS_HEIGHT": f"{above_carbonator_elbows_height:.4g} mm",
        "BELOW_TANK_ELBOWS_HEIGHT": f"{below_carbonator_elbows_height:.4g} mm",
        "PORT_HOLE_DIAMETER": f"{port_hole_radius * 2:.4g}",
        "SCREW_CLEARANCE_DIAMETER": f"{screw_clearance_radius * 2:.4g}",
        "INSERT_POCKET_DIAMETER": f"{insert_pocket_radius * 2:.4g}",
        "SCREW_BOSS_SIZE": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
        "SCREW_HEAD_H": f"{screw_head_height:.4g} mm",
        "HEAD_PAD_H": f"{head_pad_height:.4g} mm",
        "FOAM_CAP_LID_H": f"{foam_cap_lid_height:.4g} mm",
        "HEAD_CBORE_D": f"{head_cbore_radius * 2:.4g} mm",
        "CAP_SCREW_L": f"{cap_screw_length:.4g}",
        "DECK_MOUNT_CAP_GAP": f"{deck_mount_cap_gap:.4g} mm",
        "CARBONATOR_PORT_PITCH": f"{2 * carbonator_port_offset / 25.4:.4g}\"",
        "CARBONATOR_PORT_OFFSET": f"{carbonator_port_offset:.4g} mm",
        "LLDPE_BEND_R": f"{lldpe_bend_radius:.4g} mm",
        "FORWARD_BAND": f"{forward_band_width:.4g} mm",
        "LLDPE_TUBE_OD": f"{lldpe_tube_od:.4g}",
        "ENTRY_RELIEF_D": f"{2.0 * cap_conduit_entry_relief_radius:.4g}",
        "ENTRY_SKEW_CEILING": f"{cap_conduit_entry_skew_ceiling:.4g}°",
        "ANCHOR_LOOP": "none",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print("-> _cold_core_interface.py (self)")


def __getattr__(name):
    if name == "cq":
        import cadquery
        return cadquery
    if name in {"xy_plane_z_up", "xz_plane_y_up", "xz_plane_y_down", "WorldWorkplane"}:
        import world_workplane
        return getattr(world_workplane, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
