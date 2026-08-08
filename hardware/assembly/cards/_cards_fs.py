"""PV / CA / FC / AB / FS / GT — the vessel the bench builds by hand, and the
five benches that prove, commission, accept and ship the finished machine.

One subsystem function, registered in `_cards_sync.SUBSYSTEMS`. The rules it
follows are that file's: read the figure off the built appliance, prefer a
structural reading to a coordinate, and assert the structure the sentence around
it stands on.

These six prefixes are one subsystem because they are one arc seen at six
benches, and the same handful of things carry through all of it. The vessel PV
welds is the vessel AB fills; the port the vessel is gassed through is the bore
FS caps; the row of unions FS inspects is the row IP lands the risers on. A
figure stated at two of those benches is one fact, and the deck's one namespace
is what stops them disagreeing.

WHAT THESE CARDS STAND ON, and is therefore asserted rather than measured:

- THE MACHINE IS ENTERED FROM THE BACK. Nothing at all is cut in the front
  wall, so the bench rig AB-01 connects and the caps FS-03 fits are all on one
  face: water into the JG union's outboard collet, CO2 into the DERPIPE's bore,
  mains into the C14. "Both inlets are on the rear wall" holds no number, so
  only `_rear_entry` can put those cards back.
- NEITHER INLET IS A THREAD. Both are push-to-connect — the water a collet on
  the union's own barrel, the CO2 the DERPIPE's 5/16" collar — which is why
  FS-03's caps are press-on and why GT-02's three-beat is the technique both
  take. A fitting is a body in the pack, not a number, so it is asserted.
- THE UMBILICAL BULKHEADS STAND IN A ROW, not a cluster: one line, one pitch,
  the blue ring at one END of it. FS-01 sends the eye down that line and FS-03
  draws it. `UMBILICAL_PITCH` / `CARB_END` are the enclosure's own facts and are
  reused rather than re-derived, so a card here cannot state the row's shape and
  disagree with the card that seats it.
- EVERY LEVEL ROD IS CUT TO A SEAT-TO-SEAT SPAN MINUS ONE MILLIMETRE. That is
  the whole clearance budget, and it is the same rule in the carbonator (welded
  base, registered tip) and in both reservoirs (boss-captured both ends), so
  PV-05 states one clearance for three rods and `_rod_clearances` holds it.
"""

import os
import sys
from fractions import Fraction
from pathlib import Path

# This subsystem's own subjects, found on this file's own path setup rather than
# the driver's: the end-cap cut file, the reservoir, the PRV shroud, and the
# benches' own constant-owning drivers. All of them are constants and small
# helpers — a module that finds its own subject cannot be broken by the order
# somebody else's imports run in.
_hw = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
for _p in ("printed-parts/cadlib", "printed-parts/cold-core",
           "printed-parts/cold-core/reservoir", "printed-parts/cold-core/prv-shroud",
           "printed-parts/enclosure/front-panel",
           "cut-parts/carbonation/endcaps-circular", "assembly"):
    _dir = str(_hw / _p.replace("/", os.sep))
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import endcap_circular_dxf as _cap                                    # noqa: E402
import prv_shroud as _prv                                             # noqa: E402
import reservoir as _rsv                                              # noqa: E402
from _front_panel_dimensions import secondary_regulator_pressure_psi  # noqa: E402

# The benches' own constants, taken from the driver that owns them rather than
# retyped here — the same borrow `_acceptance_and_burn_in_sync` makes of
# `_firmware_and_commissioning_sync` for a pin it does not own.
import _acceptance_and_burn_in_sync as _ab                            # noqa: E402
import _cable_assemblies_sync as _ca                                  # noqa: E402
import _finish_pack_ship_sync as _fs                                  # noqa: E402
import _firmware_and_commissioning_sync as _fc                        # noqa: E402
import _pressure_vessel_sync as _pv                                   # noqa: E402

X = "&#215;"        # ×
DIA = "&#8960;"     # ⌀
NDASH = "&ndash;"   # –
PRIME = "&Prime;"   # ″
DEG = "&#176;"      # °
MM_PER_IN = 25.4


def _frac(inches: float) -> str:
    """An inch dimension as the shop fraction it is bought and called by.

    The stock is imperial and the bench reads "7/16", not "0.438" — but the
    number in the file is decimal, so the fraction is DERIVED from it rather
    than typed beside it. A drill that changes size changes both."""
    f = Fraction(inches).limit_denominator(64)
    return f"{f.numerator}/{f.denominator}{PRIME}"


def _dec(inches: float, places: int = 3) -> str:
    """An inch dimension at bench precision, trailing zeros kept — `0.150` is a
    depth held to a thou and `0.15` is not."""
    return f"{inches:.{places}f}{PRIME}"


def bench(m):
    """The carbonator's own geometry, the harness the board's connectors size,
    and the figures the commissioning, acceptance and finish benches work to.

    Structure first, then the figures. NONE of these figures needs the pack
    built — a carbonator plate is cut before anything is placed and a board's
    pin count is the board's — so `_figures` stands on its own and what the
    assembly is read for here is the structure the cards' sentences rest on."""
    pack, box = m.pack, m.box

    # ── the machine is entered from the back (AB-01, AB-02, FS-03) ─────────
    # AB-01 stands the bench rig behind the machine and FS-03 caps two inlets on
    # one face. A station appearing in the front wall makes both cards wrong and
    # has no number in it to drift, so this is the only thing that can say so.
    assert not pack.front_ports and not box.front_ports, (
        f"{len(box.front_ports)} station(s) are cut in the front wall — AB-01 brings water, "
        f"CO2 and mains to the BACK, and FS-03 caps both inlets on that one face")
    # The three the bench rig plugs into, each on the back wall: the water
    # union's bore, the DERPIPE's bore, the C14's opening. FS-03 fits a cap to
    # the first two and AB-01 lands a cord on the third.
    assert len(box.back_ports) >= 3 and box.c14, (
        f"the back wall stands {len(box.back_ports)} station(s) and {len(box.c14)} C14 boss(es) "
        f"— AB-01 connects water, CO2 and mains there and FS-03 caps the two fluid ones")

    # ── neither inlet is a thread (FS-03, GT-02) ──────────────────────────
    # Both are push-to-connect, which is why FS-03's caps press on over a collar
    # and why GT-02's cut-click-tug is the technique the bench uses at both. The
    # water union carries a collet at each end and the CO2 inlet is the DERPIPE.
    water = m.a.frames["bulkhead-water"].ports
    assert {"outboard", "inboard"} <= set(water), (
        f"the water union presents {sorted(water)} — FS-03 caps its OUTBOARD collet, the one "
        f"the customer's supply pushes into, and IP-02 butts the inboard one onto the ASSE chain")
    assert "co2-inlet" in m.a.pack_solids, (
        "the DERPIPE is no longer a body in the pack — AB-01 pushes 5/16\" beer line into its "
        "collar and FS-03 presses a rubber plug over the same collar")

    return _figures()


def _figures():
    """Every figure these six benches state, and which card carries it.

    All of it is upstream of the pack: the end-cap cut file, the two rods'
    seat-to-seat spans, the PRV shroud, the board's connector list, and the
    setpoints the commissioning and acceptance benches load. `bench` holds the
    structure; this holds the numbers."""
    # ── the vessel's two plates are one part (PV-01…PV-04, PV-09) ─────────
    # Every PV card up to closure says "both plates, identically": one cut file,
    # one register drill, interchangeable top and bottom. Two plate variants
    # would make PV-03's "drill both plates identically" a different step.
    assert len(_cap.hole_positions) == 2, (
        f"the end-cap cut carries {len(_cap.hole_positions)} holes — PV-01 breaks two per face "
        f"and PV-02 taps two per plate, and the vessel's four ports are those two twice")
    ports_per_plate = len(_cap.hole_positions)
    plates = 2
    # The register is BLIND and must stay blind: PV-03's one critical is the
    # plate left under it, and that plate is the pressure boundary the vessel is
    # hydro-tested to. A register drilled to the plate's own thickness is a hole.
    assert _cap.register_depth < _cap.disc_thickness, (
        f"the rod register is {_cap.register_depth}\" deep in a {_cap.disc_thickness}\" plate — "
        f"PV-03's critical is that it must not break through, and the remainder is the boundary")
    # The register sits on the cap's own −Y axis, clear of the port line, which
    # is what PV-03's "the −Y cap axis, clear of both ports" means and what puts
    # the donut off the inlet jet and out of the outlet's draw.
    assert _cap.register_position[0] == 0.0 and _cap.register_position[1] < 0, (
        f"the rod register stands at {_cap.register_position} — PV-03 drills it on the −Y axis "
        f"at x 0, the one azimuth carrying no port")

    # The plate is a plug in the tube's bore, and the slip is what PV-04's
    # inside-face chamfer is a lead-in for and what PV-07's deburr is to protect.
    plate_slip = (_cap.tube_id - _cap.disc_diameter) / 2.0

    # ── one clearance, three rods (PV-05, PV-06, PV-09) ───────────────────
    # Each rod is cut under its own seat-to-seat span by the same millimetre, in
    # the carbonator and in both reservoirs. PV-05 cuts all three at one bench
    # and states ONE clearance for them; two clearances would make that sentence
    # a table instead.
    assert _pv.rod_clearance == _rsv.reservoir_rod_clearance, (
        f"the carbonator's rod is cut {_pv.rod_clearance} mm under its span and a reservoir's "
        f"{_rsv.reservoir_rod_clearance} mm under its — PV-05 states one clearance for all three")
    rod_clearance = _pv.rod_clearance
    # PV-05's nesting note is arithmetic on the two cuts against a nominal stick,
    # and the whole point of it is whether they fit. Both halves move.
    stick_len = 12.0 * MM_PER_IN
    rod_pair = _pv.carbonator_rod_len + _rsv.reservoir_rod_len
    assert rod_pair > stick_len, (
        f"one carbonator rod and one reservoir rod now come to {rod_pair:.4g} mm against a "
        f"{stick_len:.4g} mm stick — PV-05's note is that they DO NOT nest; they do now")

    # ── the PRV rides in a cup, not in the foam (PV-13) ───────────────────
    # PV-13's whole page is the shroud keeping the discharge port and the bonnet
    # windows in air. A cup shorter than its cavity is not enclosing them.
    assert _prv.cavity_length < _prv.total_length, (
        f"the PRV shroud is {_prv.total_length} mm long over a {_prv.cavity_length} mm cavity — "
        f"PV-13 slips it past the hex and the discharge port to a seat, and caps the far end")

    # ── the harness is the board's own connectors (CA-01, CA-02) ──────────
    # Every conductor count in CA-02's schedule is a pin count on `pcba.tsx`, so
    # the board is read rather than the schedule retyped. CA-02's own critical
    # rests on two housings being the same size, which is a comparison, not a
    # number.
    pins = _ca.connector_pins()
    assert pins["J4"] == pins["J7"], (
        f"J4 is {pins['J4']}P and J7 is {pins['J7']}P — CA-02's critical and GT-04's last step "
        f"are both that they share a shell, which is why the label is the guard")
    assert "J12" not in pins, (
        "the board has grown a J12 — CA-02's note says there is none, and the schedule is the "
        "board's connector list")
    looms = len(pins) + 1  # every connector's loom, plus the AC mains set
    assert looms == 13, (
        f"the board's connectors come to {looms - 1} looms and CA-02 counts {looms} assemblies "
        f"with the AC set — recount the schedule, not this line")

    # ── what the acceptance bench proves (AB-03, AB-05, FC-03, FC-04) ─────
    # The reed census and the valve census are the machine's, and four cards
    # walk them. A reed added anywhere changes AB-05's audit and FC-03's table
    # at once, so both read the same total.
    assert _fc.reeds_total == _fc.reeds_carbonator + _fc.reservoir_count * _fc.reeds_per_reservoir, (
        f"the reed total {_fc.reeds_total} is not the carbonator's {_fc.reeds_carbonator} plus "
        f"{_fc.reservoir_count} reservoirs of {_fc.reeds_per_reservoir} — AB-05 audits it as that sum")
    # AB-01 sets the primary anywhere in a band and the appliance holds one
    # pressure regardless; the band is the bench's and the pressure is the
    # WR1110's, and AB-01's caption is about exactly that difference.
    assert _ab.co2_primary_min_psi <= secondary_regulator_pressure_psi <= _ab.co2_primary_max_psi, (
        f"the WR1110 holds {secondary_regulator_pressure_psi:g} PSI outside the bench's "
        f"{_ab.co2_primary_min_psi}–{_ab.co2_primary_max_psi} PSI primary band — AB-01 sets the "
        f"primary to the appliance's own pressure as its centreline")

    facts = {
        # ── PV — the end plates (PV-01, PV-02, PV-03, PV-04) ──────────────
        "TAP_DRILL": _frac(_cap.hole_diameter),
        "TAP_DRILL_D": f"{DIA}{_dec(_cap.hole_diameter)}",
        "PLATE_THK": _frac(_cap.disc_thickness),
        "DISC_D": f"{DIA}{_dec(_cap.disc_diameter)}",
        "PORT_SPACING": _dec(_cap.hole_spacing),
        "PORTS_PER_PLATE": f"{ports_per_plate}",
        "VESSEL_PORTS": f"{ports_per_plate * plates}",
        # Both faces of every hole, both plates — the count PV-01 flips for.
        "CHAMFER_PASSES": f"{ports_per_plate * 2 * plates}",
        "REGISTER_D": _frac(_cap.register_drill_diameter),
        "REGISTER_Y": f"{abs(_cap.register_position[1]):.3f}",
        "REGISTER_DEPTH": _dec(_cap.register_depth),
        "REGISTER_REMAINING": _dec(_cap.disc_thickness - _cap.register_depth),
        "PLATE_SLIP": f"~{_dec(plate_slip)}",
        # ── PV — the rods (PV-05, PV-06) ─────────────────────────────────
        "LEVEL_RODS": f"{1 + _fc.reservoir_count}",
        "CARB_ROD_QTY": "1",
        "RSVR_ROD_QTY": f"{_fc.reservoir_count}",
        "CARB_ROD_LEN": f"{_pv.carbonator_rod_len:.4g} mm "
                        f"({_pv.carbonator_rod_len / MM_PER_IN:.3g} in)",
        "CARB_ROD_MM": f"{_pv.carbonator_rod_len:.4g} mm",
        "RSVR_ROD_LEN": f"{_rsv.reservoir_rod_len:.4g} mm "
                        f"({_rsv.reservoir_rod_len / MM_PER_IN:.3g} in)",
        "RSVR_ROD_MM": f"{_rsv.reservoir_rod_len:.4g} mm",
        "ROD_CLEARANCE": f"{rod_clearance:.4g} mm",
        "ROD_PAIR_SUM": f"{rod_pair:.4g}",
        "ROD_STICK": f"{stick_len:.4g}",
        # ── PV — closure (PV-06, PV-09) ──────────────────────────────────
        "TANK_H": f"{_pv.tank_height:.4g}",
        "PLATE_RECESS": _frac(_pv.plate_recess / MM_PER_IN),
        # ── PV — the PRV shroud (PV-13) ──────────────────────────────────
        "PRV_SHROUD_SIZE": f"{_prv.inner_diameter:.4g} ID {X} {_prv.outer_diameter:.4g} OD "
                           f"{X} {_prv.total_length:.4g} mm",
        "PRV_SHROUD_WALL": f"{_prv.wall_thickness:.4g} &#183; {_prv.cap_thickness:.4g} "
                           f"&#183; {DIA}{_prv.vent_hole_diameter:.4g} mm",
        "PRV_SEAT_SLIP": f"{_prv.overcut:.4g} mm",
        # ── the pressures (PV-03, PV-11, PV-14, AB-01, AB-02, GT-02) ─────
        # One regulator setting, stated at six benches. The vessel is proved to
        # twice it, so PV-11's "~2× working" is arithmetic on this number and
        # not a second figure to keep in step.
        "REG_PSI": f"{secondary_regulator_pressure_psi:.4g} PSI",
        "CO2_PRIMARY_BAND": f"{_ab.co2_primary_min_psi:.4g}{NDASH}"
                            f"{_ab.co2_primary_max_psi:.4g} PSI",
        "PRV_HOLD": f"{_ab.prv_hold_min:.4g} min",
        # ── CA — the board's connectors (CA-02) ──────────────────────────
        "ASSEMBLY_COUNT": f"{looms}",
        **{f"{j}_PINS": f"{n}" for j, n in pins.items()},
        # ── FC / AB — the census every bench walks ───────────────────────
        "REEDS_TOTAL": f"{_fc.reeds_total}",
        "REEDS_CARB": f"{_fc.reeds_carbonator}",
        "REEDS_RSVR_ALL": f"{_fc.reservoir_count * _fc.reeds_per_reservoir}",
        "REEDS_PER_RSVR": f"{_fc.reeds_per_reservoir}",
        "PROBE_COUNT": f"{_fc.ds18b20_count}",
        "SOLENOID_COUNT": f"{_fc.valve_count}",
        "RAIL_12V": f"{_fc.rail_12v_nominal:.4g} V",
        "RAIL_5V": f"{_fc.rail_5v_nominal:.4g} V",
        "RAIL_33V": f"{_fc.rail_33v_nominal:.4g} V",
        "FREEZE_CUTOUT": f"&minus;{abs(_fc.freeze_cutoff_c):.4g} {DEG}C",
        "MIN_OFF": f"{_fc.min_off_time_min:.4g} min",
        "COMP_ON_OFF": f"{_fc.comp_on_temp_c:.4g} / {_fc.comp_off_temp_c:.4g} {DEG}C",
        "TANK_TARGET": f"{_fc.tank_target_c:.4g} {DEG}C",
        "HYSTERESIS": f"&plusmn;{_fc.hysteresis_c:.4g} {DEG}C",
        # ── FS — the carton and the gate it has to clear ─────────────────
        "TILT_ANGLE": f"~{_fs.splash_check_tilt_deg:.4g}{DEG}",
        "SCALE_PRECISION": f"{_fs.scale_precision_kg:.4g} kg",
        "CARTON_W_BAND": f"{_fs.carton_gross_weight_low_kg:.4g}{NDASH}"
                         f"{_fs.carton_gross_weight_high_kg:.4g} kg",
        "CARTON_DIMS": f"{_fs.carton_length_cm:.4g}{X}{_fs.carton_width_cm:.4g}"
                       f"{X}{_fs.carton_height_cm:.4g} cm",
        "CARRIER_LIMIT_LB": f"{_fs.carrier_ground_limit_lb:.4g} lb",
        "CARRIER_LIMIT_KG": f"~{_fs.carrier_ground_limit_kg:.4g} kg",
        "DECLARED_VALUE": f"${_fs.founder_edition_price_usd:,}",
        "WATER_DRAINED": f"~{_fs.water_drained_kg:.4g}",
        "FLAVOR_DRAINED": f"~{_fs.flavor_drained_kg:.4g} kg",
    }

    cards = {
        # PV — the plates.
        "pv-01-chamfer-port-holes": {
            "TAP_DRILL", "TAP_DRILL_D", "PLATE_THK", "PORTS_PER_PLATE",
            "CHAMFER_PASSES", "VESSEL_PORTS"},
        "pv-02-tap-npt-ports": {"PORTS_PER_PLATE", "VESSEL_PORTS", "TAP_DRILL"},
        "pv-03-rod-register": {
            "DISC_D", "PLATE_THK", "TAP_DRILL", "PORT_SPACING", "PORTS_PER_PLATE",
            "REGISTER_D", "REGISTER_Y", "REGISTER_DEPTH", "REGISTER_REMAINING",
            "REG_PSI"},
        "pv-04-break-plate-edges": {"PLATE_SLIP"},
        # PV — the rods and the closure.
        "pv-05-cut-level-rods": {
            "LEVEL_RODS", "CARB_ROD_LEN", "RSVR_ROD_LEN", "CARB_ROD_QTY",
            "RSVR_ROD_QTY", "CARB_ROD_MM", "RSVR_ROD_MM", "ROD_CLEARANCE",
            "ROD_PAIR_SUM", "ROD_STICK"},
        "pv-06-tack-float-rod": {
            "REGISTER_D", "CARB_ROD_LEN", "CARB_ROD_MM", "ROD_CLEARANCE",
            "TANK_H", "PLATE_RECESS", "PLATE_THK", "REGISTER_DEPTH"},
        "pv-07-deburr-and-prep": {"PLATE_SLIP", "PLATE_THK"},
        "pv-09-close-the-vessel": {"PLATE_RECESS"},
        "pv-11-hydro-test": {"REG_PSI"},
        "pv-13-prv-shroud-subassembly": {
            "PRV_SHROUD_SIZE", "PRV_SHROUD_WALL", "PRV_SEAT_SLIP"},
        "pv-14-port-fittings": {"VESSEL_PORTS", "REG_PSI"},
        # CA — the schedule is the board's connector list.
        "ca-02-harness-schedule": {
            "ASSEMBLY_COUNT", "J1_PINS", "J2_PINS", "J3_PINS", "J4_PINS", "J5_PINS",
            "J6_PINS", "J7_PINS", "J8_PINS", "J9_PINS", "J10_PINS", "J11_PINS",
            "J13_PINS"},
        # FC — first power, then every input and every actuator.
        "fc-01-first-dc-power-on": {"RAIL_12V", "RAIL_5V", "RAIL_33V", "WALL_BOSSES"},
        "fc-03-sensor-health": {
            "PROBE_COUNT", "REEDS_TOTAL", "REEDS_CARB", "REEDS_PER_RSVR"},
        "fc-04-valve-pump-self-test": {"SOLENOID_COUNT", "MANIFOLD_VALVES"},
        "fc-05-compressor-smoke-test": {
            "TANK_TARGET", "HYSTERESIS", "COMP_ON_OFF", "FREEZE_CUTOUT", "MIN_OFF"},
        # AB — the bench rig stands behind the machine.
        "ab-01-inspect-connect-power": {
            "REG_PSI", "CO2_PRIMARY_BAND", "CO2_HOLE_D", "UMBILICAL_UNIONS",
            "UMBILICAL_PITCH", "CARB_END"},
        "ab-02-water-fill-co2": {"REG_PSI", "PRV_HOLD", "CAP_CONDUITS"},
        "ab-05-level-transitions": {
            "REEDS_TOTAL", "REEDS_CARB", "REEDS_RSVR_ALL", "REEDS_PER_RSVR"},
        "ab-06-burn-in-log": {"FREEZE_CUTOUT"},
        # FS — the row, the two capped bores, and the carton.
        "fs-01-wipe-down-inspect": {"UMBILICAL_UNIONS", "CARB_END"},
        "fs-02-drain-dry-nameplate": {
            "TILT_ANGLE", "WATER_DRAINED", "FLAVOR_DRAINED"},
        "fs-03-cap-photograph": {"UMBILICAL_UNIONS", "CARB_END"},
        "fs-05-weigh-label-handoff": {
            "SCALE_PRECISION", "CARTON_W_BAND", "CARTON_DIMS", "CARRIER_LIMIT_LB",
            "CARRIER_LIMIT_KG", "DECLARED_VALUE"},
        # GT — the technique the joints in this machine actually take.
        "gt-02-push-to-connect": {"REG_PSI"},
    }
    return facts, cards
