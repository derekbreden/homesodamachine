"""CC + RL — the cold core, and the refrigerant loop that is brazed into it.

One subsystem function per `_cards_sync.py`'s contract, registered there in
`SUBSYSTEMS`. Everything here is read off the cold core's own modules, which are
what the printer and the bench get.

WHAT THE CC CARDS STAND ON, and therefore what is asserted rather than measured:

- The core is reached THROUGH ITS LID. Seven conduits stand on the top cap and
  every fluid line takes one; the −X face is mated flat against the refrigeration
  base, so what crosses it is the two reed cables and the two lane slots above
  them and nothing else. No number in that sentence, so `_front_wall_census` is
  what puts it back.
- EVERY VESSEL IS FILLED HIGH AND DRAWN LOW — the carbonator at its top plate and
  its bottom, each reservoir at its cap and at its floor bulkhead. That is what
  the air-purge and clean-flush service modes run on, and it is a pairing of
  conduits rather than a figure, so it is an assertion too.
- The evaporator's two coppers leave by OPPOSITE LANES, because the refrigeration
  base the wall is mated to is two bodies. CC-03, CC-10 and CC-12 all send the
  bench to a different lane per tail; one column carrying both would make all
  three wrong at once.
- The carbonated-water outlet crosses the tank support ring at one of the RING'S
  OWN SLOTS and the CO2's reach crosses the same one, so no bearing segment is
  notched. `_port_cuts` asserts the water outlet's crossing at import; the CO2's
  lean is measured here, because CC-10 and CC-12 both say "both lines, one slot".
- THE CAP IS CLOCKED BY WHAT ITS INSTALL TURN MOVES. It goes on spun a half turn
  (`foam_assembly._spin`), and CC-15 tells the bench the six clamp bosses bolt
  either way while the deck columns and the lid's valve cradles do not. Three
  patterns against one turn and no figure in any of it, so all three readings are
  assertions.

The RL cards state no figure the machine owns. The two legs they braze are routed
runs (`_lines.py` refrig-2, refrig-3) cut in situ off the coil's own tails, so
their length is the bench's; what the loop owes the deck is the pair of coil stubs
the cold core hands it, and `refrigerant_loop` holds that the two stations still
stand on the front wall's two lanes.
"""

import math
import os
import sys
from pathlib import Path

# The cold core's own modules, on this file's own path setup rather than the
# driver's: these are constants, hole-punch helpers and the stack's own placement
# arithmetic, and a module that finds its own subject cannot be broken by the
# order somebody else's imports run in.
_hw = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
for _p in ("printed-parts/cadlib", "printed-parts/cold-core",
           "printed-parts/cold-core/copper-plugs",
           "printed-parts/cold-core/foam-assembly"):
    _dir = str(_hw / _p.replace("/", os.sep))
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import _cold_core_interface as cci  # noqa: E402
import _port_cuts as pcuts  # noqa: E402
import _reed_channels as reed  # noqa: E402
import copper_plugs as plugs  # noqa: E402
import foam_assembly as stack  # noqa: E402

X = "&#215;"        # ×
DIA = "&#8960;"     # ⌀
DEG = "&#176;"      # °
PM = "&#177;"       # ±


def _front_wall_census():
    """Everything that crosses the shell's −X face, by name.

    The field's two stations plus every lane slot's. CC-12 draws this face and
    CC-13 fills it, so the census is the one reading both stand on."""
    return sorted(set(cci.front_port_order) | set(plugs.slot_stations()))


def _ring_azimuths(a, b, tube_radius):
    """The azimuth band a straight line from plan `a` to plan `b` sweeps while it is
    inside the tank support ring's annulus — `(low, high)` degrees about +X.

    `_port_cuts.ring_crossing_azimuths` answers this for a line running square out
    of the shell, where the extremes are corners. The CO2's reach LEANS, so its
    band is read off the swept tube instead: both edges of the tube, sampled along
    the run, wherever the radius is between the ring's two faces."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    span = math.hypot(dx, dy)
    nx, ny = -dy / span, dx / span            # unit normal, the tube's own width
    band = []
    for edge in (-tube_radius, +tube_radius):
        for i in range(2001):
            t = i / 2000.0
            x = ax + dx * t + nx * edge
            y = ay + dy * t + ny * edge
            r = math.hypot(x, y)
            if pcuts.support_ring_inner_radius <= r <= pcuts.support_ring_outer_radius:
                band.append(math.degrees(math.atan2(y, x)) % 360.0)
    return (min(band), max(band)) if band else None


def _ring_slot_holding(band):
    """The ring slot that holds an azimuth band whole — `(low, high)` — or None."""
    for lo, hi in pcuts.ring_slot_spans():
        if band is not None and lo <= band[0] and band[1] <= hi:
            return (lo, hi)
    return None


def _turned(pattern):
    """A pattern of cap-frame `(x, y)` at the top cap's INSTALL ORIENTATION, as a set.

    The turn is the metal's own — `foam_assembly.spin_xy`, the coordinate half of the half
    turn `_spin` gives the part — so a pattern compared against this cannot drift off the
    orientation the stack is actually built at."""
    return {stack.spin_xy(p) for p in pattern}


# ═══ CC — Cold core ════════════════════════════════════════════════════════

def cold_core(m):
    """`cold-core.md`'s seven steps: the shell's inserts, the cap's columns, what
    crosses the boundary and where, and the plug stacks that close the two lanes."""
    # ── the core is reached through its lid ───────────────────────────────
    # CC-12's whole page. A fluid station appearing on the front wall — or a reed
    # cable leaving it — makes the card's first sentence false, and there is no
    # number in "and nothing else" for the value to drift on.
    assert _front_wall_census() == ["evap-inlet", "evap-outlet", "prv-vent",
                                    "reed-cable-a", "reed-cable-b"], (
        f"the shell's −X face carries {_front_wall_census()} — CC-12 sends every fluid "
        f"line out the top and leaves that face the two reed cables and the two lane "
        f"slots, and CC-13 stacks plugs for exactly those slots")
    # Filled high, drawn low. Each of the three vessels is entered once and drawn
    # once, and the pairs are named: two ends per vessel, never two of a kind.
    entries = {"water-in", "co2-in", "reservoir-a-fill", "reservoir-b-fill"}
    draws = {"carb-water-out", "reservoir-a", "reservoir-b"}
    assert set(cci.cap_conduits) == entries | draws, (
        f"the cap carries {sorted(cci.cap_conduits)} — CC-12 walks three vessels, each "
        f"entered above its liquid and drawn at its lowest point, and every conduit on "
        f"the cap is one end of one of those")
    assert cci.water_inlet_port_y == +cci.vessel_port_offset \
        and cci.co2_inlet_y == -cci.vessel_port_offset, (
        "the carbonator's water inlet is on the TOP plate and its CO2 on the bottom — "
        "CC-12 says the vessel is filled above the liquid and gassed below it")
    # The evaporator's two coppers leave by opposite lanes (CC-03, CC-10, CC-12).
    tails = {name: plugs.columns[spec.column].lane_y
             for name, spec in ((s.station, s) for s in plugs.plug_specs.values())}
    assert tails["evap-inlet"] == cci.port_lane_mid_y \
        and tails["evap-outlet"] == cci.west_lane_mid_y, (
        f"the evaporator's tails cross at {tails} — CC-03 clocks one tail to each lane "
        f"and CC-10's last check is that they lie there")
    # Both bottom-plate lines cross the tank support ring at ONE of its own slots,
    # so all four bearing segments stay whole (CC-10's table, CC-12's step).
    water_band = pcuts.ring_crossing_azimuths(
        pcuts.water_outlet_ring_crossing_x, cci.lldpe_tube_od / 2.0)
    co2_band = _ring_azimuths(pcuts.co2_inlet_lane_xyz[:2], pcuts.co2_inlet_xyz[:2],
                              cci.lldpe_tube_od / 2.0)
    slot = _ring_slot_holding(water_band)
    assert slot is not None and slot == _ring_slot_holding(co2_band), (
        f"the carbonated water crosses the support ring over {water_band} and the CO2 over "
        f"{co2_band}, which is not one slot of {pcuts.ring_slot_spans()} — CC-10 and CC-12 "
        f"both say both lines take the same slot and the ring is bored nowhere")
    ring_slot_deg = (slot[0] + slot[1]) / 2.0
    # The top cap is the only one with anything standing in it, which is what makes
    # CC-06's "label them" step a step and CC-15's rotation the column pattern's.
    # An EMPTY table is the case a count cannot report: CC-06 would tell the bench to
    # press an insert into each of nought columns and CC-15 would clock the cap by a
    # pattern that is not there, and both would read as sentences about a real part.
    assert cci.deck_mounts, (
        "the top cap carries no deck mount — CC-06 presses a ruthex into every deck "
        "column before the pour and CC-15 clocks the cap by the pattern they make, so "
        "with an empty table both steps describe a feature the part does not have")
    assert cci.cap_cradles, (
        "the top lid stands no valve cradle — CC-06 tells the bench to trim around them "
        "and CC-15 reads the cap's clocking off them beside the deck columns, so with an "
        "empty table both steps describe a feature the part does not have")
    assert cci.deck_mount_proud() == 0.0, (
        "a deck mount now stands proud of the lid — CC-06 sets a ruthex flush in every "
        "column UNDER the lid, and CC-15 closes the cap on a lid whose outer face is the "
        "one plane the valve cradles stand on")
    # Three patterns against one turn. CC-15 bolts the top cap on spun a half turn and says
    # the six clamp bosses go either way while the deck columns and the lid's cradles do not
    # — which is true only if the turn carries the first onto itself and neither of the
    # others, and there is no number in any of that for a value to drift on.
    clamp = set(cci.attachment_xy_positions)
    assert _turned(clamp) == clamp, (
        "the clamp bosses are not carried onto themselves by the cap's install turn — CC-15 "
        "says the screw pattern bolts either way, and a cap that only goes on one way has "
        "nothing left for the deck columns to clock")
    for what, pattern in (("deck-column",
                           {p for n in cci.deck_mounts for p in cci.deck_mount_xy(n)}),
                          ("valve-cradle",
                           {c.centre for c in cci.cap_cradles.values()})):
        assert _turned(pattern) != pattern, (
            f"the {what} pattern is carried onto itself by the cap's install turn — CC-15 "
            f"reads which way the cup goes on off it, and a pattern that looks the same "
            f"both ways tells the bench nothing")

    # The vessel's own bottom rim, where it lands on the support ring's plateau —
    # what CC-03 measures the coil's bare band up from.
    band_floor_z = cci.wall_and_floor_thickness + cci.tank_support_ring_height
    plug_count = len(plugs.plug_specs)
    deck_columns = sum(len(cci.deck_mount_xy(n)) for n in cci.deck_mounts)
    face_bosses = len(cci.attachment_xy_positions)
    capped_h = (cci.foam_shell_outer_height
                + 2.0 * (cci.foam_cap_height + cci.gasket_thickness))

    def span(plug):
        lo, hi = plugs.plug_specs[plug].z_range
        return f"{lo:.4g} &#8594; {hi:.4g}"

    facts = {
        # The shell (CC-05, CC-14, CC-15).
        "CORE_FOOTPRINT": f"{cci.outer_shell_x_length:.4g} {X} "
                          f"{cci.outer_shell_y_length:.4g} mm",
        "SHELL_H": f"{cci.foam_shell_outer_height:.4g}",
        "CORE_CAPPED": f"{cci.outer_shell_x_length:.4g} {X} "
                       f"{cci.outer_shell_y_length:.4g} {X} {capped_h:.4g} mm",
        "SHELL_INSERTS": f"{2 * face_bosses}",
        # The wind band on the vessel (CC-03) — bare steel under the coil's low
        # tail, and over its high one, read off the tails the mandrel is wound to.
        "WIND_LENGTH": f"{cci.evap_tail_high_z - cci.evap_tail_low_z:.4g}",
        "WIND_BAND_LOW": f"{cci.evap_tail_low_z - band_floor_z:.4g}",
        "WIND_BAND_HIGH": f"{cci.tank_top_plate_z - cci.evap_tail_high_z:.4g}",
        "FACE_BOSSES": f"{face_bosses}",
        "INSERT_POCKET": f"{DIA}{2 * cci.insert_pocket_radius:.4g} mm {X} "
                         f"{cci.insert_length:.4g} mm",
        "INSERT_RELIEF": f"{cci.insert_pocket_depth - cci.insert_length:.4g} mm",
        "MID_BOSS_X": f"{PM}{cci.mid_screw_x_offset:.4g} mm",
        "CAP_SCREW": f"M3 {X} {cci.cap_screw_length:.4g}",
        # The top cap (CC-06, CC-15).
        "CAP_CONDUITS": f"{len(cci.cap_conduits)}",
        "DECK_STATIONS": f"{len(cci.deck_mounts)}",
        "DECK_COLUMNS": f"{deck_columns}",
        "CAP_CRADLES": f"{len(cci.cap_cradles)}",
        "CAP_CAVITY": f"{cci.foam_cap_interior_height:.4g}",
        "POUR_HOLE_D": f"{DIA}{2 * cci.foam_cap_lid_pour_radius:.4g}",
        "LID_VENT_D": f"{DIA}{2 * cci.foam_cap_lid_vent_radius:.4g}",
        # What crosses the boundary (CC-11, CC-12).
        "TUBE_HOLE_D": f"{DIA}{2 * cci.port_hole_radius:.4g}",
        "FORWARD_BAND": f"{cci.forward_band_width:.4g} mm",
        "TOP_BAND": f"{cci.top_band_to_cap:.4g} mm",
        "FLAVOR_HOLE_X": f"{PM}{pcuts.flavor_line_hole_x:.4g}",
        "CABLE_HOLE_X": f"{PM}{reed.reed_cable_pocket_x(+1):.4g}",
        "RESERVOIR_GAP": f"{cci.reservoir_clearance:.4g} mm",
        "POCKET_FILLET": f"{cci.bag_pocket_corner_inner_radius:.4g} mm",
        "BULKHEAD_CLEARANCE": f"{cci.bulkhead_floor_clearance:.4g} mm",
        # The tank support ring (CC-10, CC-12).
        "RING_H": f"{cci.tank_support_ring_height:.4g} mm",
        "RING_SLOTS": f"{len(pcuts.ring_slot_spans())} {X} "
                      f"{pcuts.slot_angular_width:.4g}{DEG} at "
                      + "/".join(f"{(lo + hi) / 2:.4g}" for lo, hi in pcuts.ring_slot_spans())
                      + DEG,
        "RING_SLOT_DEG": f"{ring_slot_deg:.4g}{DEG}",
        # The front wall's two lanes (CC-12, CC-13).
        "CORE_FRONT_PORTS": f"{len(cci.front_port_order)}",
        "FIELD_PITCH": f"{cci.front_port_pitch:.4g}",
        "REED_A_Z": f"{cci.front_port_z('reed-cable-a'):.4g}",
        "REED_B_Z": f"{cci.front_port_z('reed-cable-b'):.4g}",
        "EVAP_IN_Z": f"{plugs.slot_station('evap-inlet')[0][2]:.4g}",
        "EVAP_OUT_Z": f"{plugs.slot_station('evap-outlet')[0][2]:.4g}",
        "PRV_VENT_Z": f"{plugs.slot_station('prv-vent')[0][2]:.4g}",
        "SLOT_W": f"{DIA}{plugs.slot_width_x:.4g}",
        # The plug stacks (CC-13).
        "PLUG_COUNT": f"{plug_count}",
        "PLUG_LOWER": span("lower"),
        "PLUG_MIDDLE": span("middle"),
        "PLUG_TOP": span("top"),
    }

    cards = {
        "cc-03-transfer-the-coil": {
            "WIND_LENGTH", "WIND_BAND_LOW", "WIND_BAND_HIGH"},
        "cc-05-press-shell-inserts": {
            "SHELL_INSERTS", "FACE_BOSSES", "INSERT_POCKET", "INSERT_RELIEF",
            "MID_BOSS_X", "CORE_FOOTPRINT"},
        "cc-06-pour-cap-foam": {
            "CAP_CONDUITS", "DECK_STATIONS", "DECK_COLUMNS", "CAP_CAVITY",
            "POUR_HOLE_D", "LID_VENT_D", "FACE_BOSSES", "CAP_SCREW"},
        "cc-10-lower-the-vessel": {
            "RING_H", "RING_SLOTS", "RING_SLOT_DEG", "TUBE_HOLE_D"},
        "cc-11-seat-reservoirs": {
            "RESERVOIR_GAP", "POCKET_FILLET", "BULKHEAD_CLEARANCE", "FLAVOR_HOLE_X"},
        "cc-12-route-penetrations": {
            "CAP_CONDUITS", "CORE_FRONT_PORTS", "TUBE_HOLE_D", "FORWARD_BAND",
            "TOP_BAND", "FLAVOR_HOLE_X", "CABLE_HOLE_X", "RING_SLOT_DEG",
            "FIELD_PITCH", "REED_A_Z", "REED_B_Z", "EVAP_IN_Z", "EVAP_OUT_Z",
            "PRV_VENT_Z"},
        "cc-13-stack-copper-plugs": {
            "PLUG_COUNT", "PLUG_LOWER", "PLUG_MIDDLE", "PLUG_TOP", "SLOT_W",
            "SHELL_H", "FIELD_PITCH", "EVAP_IN_Z", "EVAP_OUT_Z", "PRV_VENT_Z"},
        "cc-14-pour-body-foam": {"CORE_FOOTPRINT", "RESERVOIR_GAP"},
        "cc-15-columns-gaskets-caps": {
            "CORE_CAPPED", "SHELL_INSERTS", "FACE_BOSSES", "CAP_SCREW",
            "DECK_COLUMNS", "CAP_CRADLES", "CABLE_HOLE_X"},
    }
    return facts, cards


# ═══ RL — Refrigerant loop ═════════════════════════════════════════════════

def refrigerant_loop(m):
    """`refrigerant-loop.md`: the donor's loop opened, and the cold core's two coil
    stubs brazed into it.

    THE BENCH WORK IS DONOR COPPER AT DONOR LENGTHS — cap-tube length, charge mass
    and vacuum target are the donor's and the refrigerant's, not this machine's, so
    almost nothing on these cards is a figure the appliance owns. The two legs these
    cards braze are routed runs (`_lines.py` refrig-2, refrig-3) cut and fitted in
    situ off the coil's own tails, so the length of either is the bench's and not a
    dimension a card states.
    WHAT IS THE MACHINE'S is WHICH SIDE each coil stub comes out of. The two leave
    by opposite lanes, because the base the front wall is mated to is two bodies —
    RL-04 reaches the outlet on one flank and RL-05 the inlet on the other, and a
    card sending the bench to the wrong flank sends it to a wall."""
    stations = plugs.slot_stations()
    assert set(stations) >= {"evap-inlet", "evap-outlet"}, (
        f"the cold core presents {sorted(stations)} — RL-04 brazes the coil OUTLET to the "
        f"donor's suction line and RL-05 pinch-swages the coil INLET onto the cap tube, and "
        f"each stub is the one that leaves at its own station")

    def lane(station):
        y = stations[station][0][1]
        assert y in (cci.port_lane_mid_y, cci.west_lane_mid_y), (
            f"the {station} stub leaves at y {y:g}, on neither lane of the front wall")
        return "port" if y == cci.port_lane_mid_y else "west"

    assert lane("evap-inlet") != lane("evap-outlet"), (
        "the two coil stubs leave the shell on one lane — RL-04 and RL-05 reach them from "
        "opposite flanks of the refrigeration base, and a card sending the bench to the "
        "wrong flank sends it to a wall")

    facts = {"STUB_IN_LANE": lane("evap-inlet"), "STUB_OUT_LANE": lane("evap-outlet")}
    cards = {"rl-04-suction-tie-in": {"STUB_OUT_LANE"},
             "rl-05-pinch-swage": {"STUB_IN_LANE"}}
    return facts, cards
