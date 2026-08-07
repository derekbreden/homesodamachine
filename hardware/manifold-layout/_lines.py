"""The front half's tube runs — every line between two placed bodies, authored port to port.

The manifold's own 21 segments are drawn by `manifold_layout.py`, which knows its butt joints
and its hairpins. This module is for the runs BETWEEN sub-assemblies: a mouth on one placed body
to a mouth on another, through whatever the pack leaves between them.

Each run is one `R.bent(...)` — the source port, hand-placed interior waypoints, the destination
port — swept at the port's own bore. `_routing` seats the largest arc each corner's two legs
allow and records the shortfall of any that cannot: a run drawn past its stock's floor is still
drawn, and `BLOCKED` says by how much.

A RUN ARRIVES WITH THE BODIES IT JOINS. Both of its mouths have to be placed before it can be
authored, so the set here grows as `front_half.build_pack` grows, and a run with one end in the
pack and the other nowhere is not written down as a guess.

Frames come off the placed pack, so a run rides a move of its parts: change a pose in
`front_half.py` and every waypoint measured off that body's ports moves with it.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/front_half.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cold-core",
           _hw / "reference" / "seaflo-22-pump",
           _hw / "reference" / "seaflo-suction-chain",
           _hw / "reference" / "seaflo-discharge-chain",
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "beduan-solenoid",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "gasher-check-valve",
           _hw / "reference" / "wr1110-regulator",
           _hw / "reference" / "digiten-flow-sensor"):
    sys.path.insert(0, str(_p))
import _routing as R                                   # noqa: E402
import _cold_core_interface as _cc                     # noqa: E402
import asse1022_assembly as _asse                      # noqa: E402
import seaflo_22_pump as _pump                         # noqa: E402
import seaflo_suction_chain as _suct                   # noqa: E402
import seaflo_discharge_chain as _dis                  # noqa: E402
import beduan_solenoid as _beduan                      # noqa: E402
import jg_bulkhead_union as _jg                        # noqa: E402
import neofit_flow_control as _flowreg                 # noqa: E402
import water_split as _split                           # noqa: E402
import manifold_layout as _ml                           # noqa: E402
import gasher_check_valve as _gasher                    # noqa: E402
import wr1110_regulator as _wr1110                      # noqa: E402
import digiten_flow_sensor as _digiten                  # noqa: E402

BLOCKED = R.BLOCKED


def _fh_cap(name):
    """The core's cap conduit stations, read off `front_half` at call time — importing it here
    at module scope would close a cycle, since it imports this one."""
    import front_half
    return front_half.cap_conduit(name)

# The 3/8" reinforced PVC's own floor, and the coarsest stock on the machine: a corner it cannot
# hold is a corner nothing drawn here can.
HOSE_BEND = R.stock_min("water", _suct.HOSE_OD)
# The 1/4" LLDPE's, which every fitting on the water side hands over on.
TUBE_BEND = R.stock_min("water", _split.TUBE_D)
# How far off its own axis a hose may leave a BARB and still run unbent. A barb is a taper the
# hose stretches over and a clamp closes on, not a collet gripping a tube all round, so it takes
# a good deal more than `R.COLLET_SKEW`. Seeded, not ratified.
BARB_SKEW = 14.0
# How far off its own axis a line may enter a CAP CONDUIT. The lid's hole is countersunk to this
# angle (`_cold_core_interface.cap_conduit_entry_skew`), so the lip a leaning line crosses lies
# along it and what the tube bears on there is a face.
CAP_BORE_SKEW = _cc.cap_conduit_entry_skew

# Which reference module states each placed body's stations, and the bore each one carries. The
# module gives `(position, outward axis)` in the body's own frame; `front_half`'s `carry` takes
# that through the placement, so a port table is written once and rides every later move.
STATIONS = {
    # The cold core's cap conduits — bores up the cap's own columns, each opening on the lid's
    # outer face. A line reaching one arrives at the deck, not at a body face.
    "foam-assembly": {"water-in": (lambda: _fh_cap("water-in"), _split.TUBE_D),
                      "carb-water-out": (lambda: _fh_cap("carb-water-out"), _split.TUBE_D),
                      "reservoir-a": (lambda: _fh_cap("reservoir-a"), _split.TUBE_D),
                      "reservoir-b": (lambda: _fh_cap("reservoir-b"), _split.TUBE_D),
                      "reservoir-b-fill": (lambda: _fh_cap("reservoir-b-fill"), _split.TUBE_D),
                      "co2-in": (lambda: _fh_cap("co2-in"), _split.TUBE_D)},
    "seaflo-pump": {"suction": (_pump.suction, _suct.HOSE_OD),
                    "discharge": (_pump.discharge, _suct.HOSE_OD)},
    "suction-chain": {"barb-tip": (_suct.barb_tip, _suct.HOSE_OD),
                      "tube-port": (_suct.tube_port, _suct.TUBE_D)},
    "discharge-chain": {"barb-tip": (_dis.barb_tip, _dis.HOSE_OD),
                        "tube-port": (_dis.tube_port, _dis.TUBE_D)},
    "asse1022-assembly": {"tube-in": (lambda: _asse.port("tube-in"), _split.TUBE_D),
                          "tube-out": (lambda: _asse.port("tube-out"), _split.TUBE_D),
                          "vent-tip": (lambda: _asse.port("vent-tip"), _asse.VENT_STUB_OD)},
    "vk-solenoid": {"inlet": (_beduan.inlet, _split.TUBE_D),
                    "outlet": (_beduan.outlet, _split.TUBE_D)},
    "flow-regulator": {"inlet": (_flowreg.inlet, _flowreg.TUBE_D),
                       "outlet": (_flowreg.outlet, _flowreg.TUBE_D)},
    "bulkhead-water": {"inboard": (lambda: _jg.port(-1.0), _jg.PORT_D),
                       "outboard": (lambda: _jg.port(1.0), _jg.PORT_D)},
    "gasher-co2": {"inlet": (_gasher.inlet, _split.TUBE_D),
                   "outlet": (_gasher.outlet, _split.TUBE_D)},
    "wr1110": {"inlet": (_wr1110.inlet, _split.TUBE_D),
               "outlet": (_wr1110.outlet, _split.TUBE_D)},
    "water-split": {"supply": (_split.supply, _split.TUBE_D),
                    "to-vk": (_split.to_vk, _split.TUBE_D),
                    "to-flavor": (_split.to_flavor, _split.TUBE_D)},
    # The meter inline on the carb riser. Its two collets are coaxial on its own flow axis and
    # the machine lays that axis fore and aft, so `inlet` faces forward and `outlet` aft. The
    # bore is the TUBE'S, not the barrel's: `digiten_flow_sensor.port_dia` is the Ø12 collet
    # moulding, and what pushes into it is the same 1/4" LLDPE the rest of the water side runs.
    "digiten-flow": {"inlet": (_digiten.inlet, _split.TUBE_D),
                     "outlet": (_digiten.outlet, _split.TUBE_D)},
}

# The one reservoir junction. Y-E is a Tee whose run joins reservoir A's fill and draw valves and
# whose third port is left open for the line that reaches the reservoir itself —
# `manifold_layout.MOUTHS` names it Y-E-2, and the fold calls that collet `back`. It faces AFT,
# at the outboard column over the nozzle-A gate. Channel B has no junction to match it: reservoir
# B carries two mouths of its own and its pair reaches them directly.
for _t in ("Y-E",):
    STATIONS[f"tee-{_t.lower()}"] = {
        f"{_t}-2": ((lambda t=_t: (_ml.port(t, "back"), _ml.port_axis(t, "back"))),
                    _split.TUBE_D)}

# The three unions the machine dispenses through, all on one row of the back wall. Each carries
# the same two mouths the tap-water union does, under the names the topology gives them: the
# INBOARD collet is what a run inside the box pushes into, the outboard one is what the
# above-counter umbilical lands on.
for _b in ("bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb"):
    STATIONS[_b] = {"tube-in": (lambda: _jg.port(-1.0), _jg.PORT_D),
                    "tube-out": (lambda: _jg.port(1.0), _jg.PORT_D)}


# The flavour manifold's ten solenoid valves. Each stands coil-up with its flow along the pack's
# own ±Y, and the fold names its two collets `front` and `back`. `front_half.manifold_carry`
# takes both through the pose and the lift the pack is stood at, so a run anchors on where the
# collet ends up.
#
# Which collet is the INLET is the valve's own turn. `manifold_layout` stands each body on
# `valve_dirs(P[v]["arg"])`, and that argument is which way round it faces — the flow runs the
# way the moulded arrow points, so the two turns present opposite ends. Six valves take +1 and
# four take −1, and the manifold's own `MOUTHS` names the `front` collet of V-G and V-J
# V-x-**O**.
VALVES = ("V-A", "V-B", "V-C", "V-D", "V-E", "V-F", "V-G", "V-H", "V-I", "V-J")


def valve_ends(v: str) -> tuple:
    """A valve's two collets as `(inlet, outlet)` in the fold's own `front`/`back` names, read
    off the turn `manifold_layout` stood the body at."""
    return ("front", "back") if _ml.P[v]["arg"] > 0 else ("back", "front")


for _v in VALVES:
    _in, _out = valve_ends(_v)
    STATIONS[f"valve-{_v.lower()}"] = {
        "inlet": ((lambda v=_v, e=_in: (_ml.port(v, e), _ml.port_axis(v, e))),
                  _split.TUBE_D),
        "outlet": ((lambda v=_v, e=_out: (_ml.port(v, e), _ml.port_axis(v, e))),
                   _split.TUBE_D),
    }


def frames(placed, carries):
    """Register one `_routing.Frame` per body that states stations, so a run may anchor on
    `"seaflo-pump.suction"`. `placed` is the pack's solids by name; `carries` is the carry each
    was placed by."""
    out = {}
    for name, ports in STATIONS.items():
        if name not in placed or name not in carries:
            continue
        carry = carries[name]
        table = {}
        for port, (station, diam) in ports.items():
            pos, axis = carry(station())
            table[port] = (pos, tuple(axis), diam)
        out[name] = R.frame(name, placed[name], table)
    return out


def build_runs(placed, carries):
    """Every authored run, in the order they read.

    Each one names what it carries and what it turns on. A run's waypoints are world points, so
    the numbers in them are struck off the frames above — move a body and they move with it."""
    F = frames(placed, carries)
    runs = []
    if {"seaflo-pump", "suction-chain"} <= set(F):
        runs.append(_water_7(F))
    if {"seaflo-pump", "discharge-chain"} <= set(F):
        runs.append(_water_6(F))
    if {"discharge-chain", "foam-assembly"} <= set(F):
        runs.append(_water_5(F))
    if {"asse1022-assembly", "water-split"} <= set(F):
        runs.append(_water_2(F))
    if {"water-split", "flow-regulator"} <= set(F):
        runs.append(_fluid_1(F))
    if {"vk-solenoid", "suction-chain"} <= set(F):
        runs.append(_water_4(F))
    if {"water-split", "vk-solenoid"} <= set(F):
        runs.append(_water_3(F))
    if {"gasher-co2", "wr1110"} <= set(F):
        runs.append(_co2_1(F))
    if {"wr1110", "foam-assembly", "seaflo-pump"} <= set(F):
        runs.append(_co2_2(F))
    if {"flow-regulator", "valve-v-a"} <= set(F) and "coil-v-a" in placed:
        runs.append(_fluid_2(F, placed))
    if {"foam-assembly", "digiten-flow"} <= set(F):
        runs.append(_carb_1(F))
    if {"digiten-flow", "bulkhead-carb"} <= set(F):
        runs.append(_carb_2(F))
    if {"valve-v-j", "bulkhead-flavor-b"} <= set(F) and "valve-v-i" in F:
        runs.append(_fluid_28(F, placed))
    if {"valve-v-g", "bulkhead-flavor-a"} <= set(F) and "stub-fluid-15" in placed:
        runs.append(_fluid_18(F, placed))
    if {"valve-v-i", "foam-assembly"} <= set(F):
        runs.append(_fluid_24(F))
    if {"valve-v-h", "foam-assembly"} <= set(F):
        runs.append(_fluid_26(F))
    if {"tee-y-e", "foam-assembly"} <= set(F):
        runs.append(_fluid_15(F))
    return runs


def _co2_1(F):
    """co2-1 — the check's stub tip to the regulator's inlet socket, one straight hop.

    The two mouths face each other down the chain's own axis with `front_half.CO2_HOP` between
    them, so this is a PP450822E on the check's male stub, a PP010822E in the regulator's female
    one, and the length of tube the two collets both take hold of."""
    return R.bent(
        "co2-1", "gasher-co2.outlet", "wr1110.inlet",
        kind="co2", note="CO2: check outlet → WR1110 inlet, one straight hop on the chain's axis")


# The rear bulkhead's inboard collet and the ASSE 1022's inlet collet meet face to face, so the
# first tube in the machine — everything the customer's supply line reaches passes through it —
# is a length of stock cut to the two grips and swallowed whole. There is no free tube to sweep,
# and no `water-1` in this table.


# Where the machine is CROSSABLE at V-K's inlet height. The valve manifold fills this storey
# from wall to wall, and a 1/4" line cast east off the split's own column reaches the east wall
# through one window in it: the junction tee `tee-y-b` closes that window forward, the source
# column's `step-fluid-5` closes it aft. Re-measure it by sweeping the cast in y —
#
#     w.cast((-74.0, y, w.at("vk-solenoid", "inlet")[2]), (1, 0, 0), dia=6.35)
#
# `CROSS_Y` sits inside the window's forward lip rather than on its centre. That is the aft
# leg's doing: the corner at V-K's column seats its arc out of that leg, and whatever is left
# over is the tube that enters the collet straight — so a crossing further aft is a shorter
# grip, and the window's centre is not where the run wants to be.
CROSS_Y = 157.0


def _water_3(F):
    """water-3 — the split's DOWNWARD branch to V-K's forward-facing inlet, and the one run in
    the front half that crosses the whole machine.

    It has to. The split stands in the WEST lane and V-K stands on the EAST, and V-K's inlet
    faces FORWARD — so the water leaves the split going down, and has to arrive at V-K from in
    front of it. There is no shorter way round: the valve manifold occupies the storey between
    the two columns and `CROSS_Y` is the one window through it.

    Three corners, each on a plane the run is already on. The branch drops onto the INLET'S OWN
    plane and stays there — every leg after the first is at that height, so the run reaches the
    collet without a fourth corner to climb. Then forward down the split's own column into the
    window, east through it, and aft into the mouth."""
    split, vk = F["water-split"], F["vk-solenoid"]
    src, dst = split.at("to-vk"), vk.at("inlet")
    z = dst[2]
    return R.bent(
        "water-3", "water-split.to-vk",
        (src[0], src[1], z),                # down the branch onto the inlet's plane
        (src[0], CROSS_Y, z),               # forward down the west column into the window
        (dst[0], CROSS_Y, z),               # east through it, onto V-K's column
        "vk-solenoid.inlet",
        kind="water",
        note="tap water: split branch → V-K inlet, down the west column, across the one window "
             "in the valve manifold, and aft into the mouth")


def _water_4(F):
    """water-4 — V-K's outlet to the suction chain's collet, and the last link in the pump's
    supply: V-K, this, the chain, `water-7`, the barb.

    BOTH MOUTHS FACE ALONG Y ON ONE COLUMN AND ONE PLANE. The valve discharges aft and the
    chain lying forward of the pump opens forward at it, so the run leaves and enters on one
    axis with nothing to turn around. The plane is `beduan_solenoid.port_center_z`, which is
    what the chain's own Z is struck from — the two mouths cannot fall out of line, because one
    of them is measured off the other."""
    return R.bent(
        "water-4", "vk-solenoid.outlet", "suction-chain.tube-port",
        kind="water", note="tap water: V-K outlet → suction chain's collet, one straight")


def _fluid_1(F):
    """fluid-1 — the flavour tap off the split, into the regulator that throttles it.

    The same straight `water-2` is, one fitting further down the lane: the split's flavour
    collet fires forward and the regulator's inlet faces it on that collet's own line, so the
    run is the tube between two mouths and nothing about it turns."""
    return R.bent(
        "fluid-1", "water-split.to-flavor", "flow-regulator.inlet",
        kind="fluid", note="flavor tap: split run → flow regulator, straight down the lane")


def _water_2(F):
    """water-2 — the ASSE 1022's outlet to the split's supply, and it is ONE LENGTH OF TUBE.

    The chain hands the water over facing forward down the west lane and the split's own run
    axis IS that lane, so the two collets face each other on one line with nothing between them
    to turn around. `front_half.WATER_2` is the gap, and a gap between two collets facing down
    one axis seats no arc — what it has to be is enough tube for both to take hold of."""
    return R.bent(
        "water-2", "asse1022-assembly.tube-out", "water-split.supply",
        kind="water", note="tap water: ASSE outlet → split supply, one straight down the lane")


def _water_7(F):
    """water-7 — the 3/8" braided stub off the moulded suction barb, from the pump to the chain
    that steps its inlet down to 1/4".

    THE TWO MOUTHS ARE A QUARTER APART IN PLAN AND A CHAIN'S RADIUS APART IN HEIGHT, and the run
    is those two turns and nothing else. `SEAFLO_YAW` puts the suction barb on the head's EAST
    face pointing east; the chain lies in the lane that barb points into, forward of it, with its
    own barb facing AFT back at the pump — so the hose leaves across the machine and turns along
    it. The chain lies on the crown the pump's feet stand on, so its axis is one half-section off
    that crown while the barb is `seaflo_22_pump.PORT_Z` up the head, and the run falls that
    difference on the same leg it turns on.

    Both corners want the stock's whole `HOSE_BEND` as tangent in each leg they touch, and
    the placement is what buys those legs: `SUCT_PUMP_GAP` sets the reach east and
    `SUCT_CORNER_ROOM` the reach aft. Neither is in `BLOCKED`, so both seat it.

    `lead` plants a waypoint on each port's own axis, so the hose leaves the barb and enters the
    chain dead straight and a clamp closes on a straight length at either end."""
    return R.bent(
        "water-7", "seaflo-pump.suction", "suction-chain.barb-tip",
        kind="water", bend=HOSE_BEND, skew=BARB_SKEW, lead=HOSE_BEND,
        note="carb water: SeaFlo suction barb → suction chain, east off the barb, one quarter forward "
             "and down onto the chain's own axis (3/8\" braided PVC, two clamps)")


def _water_6(F):
    """water-6 — the 3/8" braided stub off the moulded discharge barb, from the pump to the
    chain that carries its outlet onto 1/4" tube.

    ONE CORNER IN PLAN AND NOTHING ELSE. `SEAFLO_YAW` puts the discharge barb on the head's
    WEST face pointing west, and the chain lies in that lane forward of it with its own barb
    facing AFT — so the hose leaves across the machine, turns once, and arrives square on. The
    chain's axis is struck from this same mouth's Z (`front_half.build_discharge_chain`), so
    the two ends lie on one plane and the corner is flat.

    The waypoint is the corner itself: the chain's own column at the barb's own Y. What buys
    its arc is `DISCH_SPLIT_CLEAR` down one leg and `DISCH_CORNER_ROOM` down the other."""
    pump, chain = F["seaflo-pump"], F["discharge-chain"]
    src, dst = pump.at("discharge"), chain.at("barb-tip")
    return R.bent(
        "water-6", "seaflo-pump.discharge",
        (dst[0], src[1], src[2]),
        "discharge-chain.barb-tip",
        kind="water", bend=HOSE_BEND, skew=BARB_SKEW,
        note="carb water: SeaFlo discharge barb → discharge chain, west off the barb and one "
             "quarter forward onto the chain's own axis (3/8\" braided PVC, two clamps)")


def _water_5(F):
    """water-5 — the discharge chain's collet to the cold core's water-in conduit, and the
    tap-water path's only descent.

    ONE SLANT ACROSS THE FALL. The collet looks forward off the far end of the laid-down chain
    and the bore opens up out of the cap's lid on that chain's own column, ahead of it and
    below it — so the tube leaves the collet straight on its own axis, crosses the fall at a
    slant, and enters the bore dead on the vertical it is drilled at. Two gentle turns rather
    than one square one; its height only ever descends.

    `lead` is what plants the two straights: one stock bend radius off each mouth, so the
    corners live in the middle of the run and both mouths take the tube unbent."""
    return R.bent(
        "water-5", "discharge-chain.tube-port", "foam-assembly.water-in",
        kind="water", lead=TUBE_BEND, skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="carb water: discharge chain's collet → the core's water-in cap conduit, one "
             "slant across the fall")


# The storey `co2-2` crosses the deck on. `water-7` lies across the lane between the regulator
# and the core's cap and the suction chain lies forward of it, so the run climbs over the pair
# and travels at a height neither reaches — one clearance over the taller of the two, which is
# the hose.
CO2_DECK_CLEAR = 10.0
# The straight off the regulator's outlet before it starts that climb, and the reach the climb
# itself takes down the lane. Both are the gap the corner at each end of the lean seats its arc
# in; the lean is one leg and its two corners share it.
CO2_OUT_LEAD = 10.0
CO2_CLIMB_REACH = 15.0


def _co2_2(F):
    """co2-2 — the regulator's outlet to the cold core's CO2 conduit, and the whole gas path
    inside the machine.

    THE PAIR IT HAS TO CLEAR IS THE PUMP'S OWN. `water-7` crosses this lane at the pump's
    suction and the suction chain lies forward of it, both between the regulator and the bore,
    so the run leaves the outlet, leans up over the hose in one leg, and travels forward at that
    storey with nothing under it. Then east onto the port lane's own column and straight down
    into the bore.

    The bore is the one window the +X flank leaves: the power block's column stands on the lid
    from the cap to the ceiling aft of it, and V-K's plate forward of it.

    The storey it travels at is read off the hose it clears — the pump's own suction mouth plus
    half the 3/8" section over it — so a move of the pump carries this run with it."""
    out = F["wr1110"].at("outlet")
    bore = F["foam-assembly"].at("co2-in")
    deck = (F["seaflo-pump"].at("suction")[2] + _suct.HOSE_OD / 2.0 + CO2_DECK_CLEAR)
    return R.bent(
        "co2-2", "wr1110.outlet",
        (out[0], out[1] - CO2_OUT_LEAD - CO2_CLIMB_REACH, deck),   # the lean's far end
        (out[0], bore[1], deck),                                   # forward over the hose
        (bore[0], bore[1], deck),                                  # east onto the bore's column
        "foam-assembly.co2-in",
        kind="co2", lead=(CO2_OUT_LEAD, TUBE_BEND), skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="CO2: WR1110 outlet → the core's CO2 cap conduit, one lean up over the pump's "
             "suction hose, forward at that storey, east onto the port lane's column and down")


# The straight `fluid-2` runs forward off the regulator's outlet before it turns. It is longer
# than the arc's own tangent so a length of tube still leaves the collet straight.
FLUID_2_LEAD = 20.0
# The column the run goes aft in: the strip between the WEST source valve and the tap-water lane,
# struck off that valve's own outboard face, so the run rides the valve wherever the valve goes.
FLUID_2_LANE_CLEAR = 7.5
# The storey that strip carries. The regulator lies over the strip — its needle stem reaches east
# across the lane — and the strip is open below it, so the run hangs its centreline this far under
# the regulator's own underside.
FLUID_2_DECK_CLEAR = 6.5


def _fluid_2(F, solids):
    """fluid-2 — the flow regulator's outlet to V-A's inlet, and the tap water's last leg
    before the flavour manifold.

    THE TWO MOUTHS FACE THE SAME WAY AND THE VALVE IS BEHIND THE REGULATOR. The regulator lies
    in the west lane with its flow running forward, so its outlet fires FORWARD; V-A stands
    coil-up on the deck with its inlet on the AFT end, so the run has to come at that collet from
    behind. It goes forward off the regulator, leans east and down into the strip west of V-B,
    runs aft down that strip beside the two source valves, crosses the machine east on the storey
    BEHIND their coils, and comes down V-A's own column into the collet.

    The last leg is `manifold_layout.STUB` — the straight that pack draws on every mouth that
    leaves it, which is what its first corner needs before it can turn at all. Drawing this run
    is what makes that stub a real line, so `front_half.build_pack` stops adding the
    placeholder once the run exists."""
    reg, vk_a = F["flow-regulator"], F["valve-v-a"]
    out, inlet = reg.at("outlet"), vk_a.at("inlet")
    lane = out[1] - FLUID_2_LEAD
    lane_x = solids["coil-v-b"].BoundingBox().xmin - FLUID_2_LANE_CLEAR
    deck = solids["flow-regulator"].BoundingBox().zmin - FLUID_2_DECK_CLEAR
    cross = inlet[1] + _ml.STUB
    return R.bent(
        "fluid-2", "flow-regulator.outlet",
        (lane_x, lane, deck),                         # east and down into the strip in one lean
        (lane_x, cross, deck),                        # aft down the strip, beside the valves
        (inlet[0], cross, inlet[2]),                  # east behind both coils and down in one lean
        "valve-v-a.inlet",
        kind="fluid", lead=(FLUID_2_LEAD, _ml.STUB),
        note="tap water: flow regulator outlet → V-A inlet, forward off the regulator, east and "
             "down into the strip west of V-B, aft past the source valves and east behind them")


# --- the carb-water riser, and the two nozzle gates' lines to the panel -----
#
# All three end on the panel deck (`front_half.PANEL_X`), which is the band over the water
# pump's crown, and all three reach it by a column that runs the machine's whole height.

def _carb_1(F):
    """carb-1 — the cold core's carbonated-water conduit to the meter's inlet.

    UP THE PORT LANE AND WEST ALONG THE DECK. The bore opens out of the cap's lid facing the
    ceiling and the meter lies fore and aft on the panel deck with its inlet facing forward, so
    the run climbs the lane's own column to that deck, crosses west onto the meter's column, and
    runs aft down it into the collet.

    The closing leg is THE COLLET'S OWN AXIS, so there is no closing corner: the column the run
    turns onto is the meter's own X and the deck is its own Z, and what is left between them is
    one straight length of tube."""
    bore = F["foam-assembly"].at("carb-water-out")
    inlet = F["digiten-flow"].at("inlet")
    return R.bent(
        "carb-1", "foam-assembly.carb-water-out",
        (bore[0], bore[1], inlet[2]),        # up the lane's own column onto the deck
        (inlet[0], bore[1], inlet[2]),       # west along the deck onto the meter's column
        "digiten-flow.inlet",                # and aft down it into the collet
        kind="water", lead=(TUBE_BEND, TUBE_BEND), skew=(CAP_BORE_SKEW, R.COLLET_SKEW),
        note="carb water: the core's carb-water cap conduit → DIGITEN inlet, up the port lane "
             "and west along the panel deck onto the meter's own column")


def _carb_2(F):
    """carb-2 — the meter's outlet to the carb union's inboard collet, and it is ONE LENGTH OF
    TUBE.

    `front_half.build_digiten` seats the meter ON THIS RUN: its outlet is placed one `CARB_2`
    forward of the union's collet and on that collet's own column and plane, so the two mouths
    face each other down one line with nothing between them to turn around."""
    return R.bent(
        "carb-2", "digiten-flow.outlet", "bulkhead-carb.tube-in",
        kind="water", note="carb water: DIGITEN outlet → rear union, one straight down the deck")


# How high a gate's line climbs on its own column before it steps outboard. Each gate has its own
# channel's reservoir line standing over it, so the column is a bay and not a shaft, and this is
# the air left under whatever that is.
#
# THE TWO GATES ARE OVERFLOWN BY DIFFERENT THINGS, because the two channels reach their
# reservoirs differently. East it is `stub-fluid-15`, the mouth of the junction reservoir A still
# meets its pair at, and the figure is read off that stub's own underside. West there is no
# junction: what crosses V-J's column is `fluid-24` itself, running aft up the outboard lane on
# `RESERVOIR_CRUISE`, and the figure is struck on that plane.
GATE_STUB_CLEAR = 4.0
# The outboard lane the two gate lines run aft in. It is the strip between the hopper's bowl and
# the ±X boss chain, and it is the one column on either flank that carries a line from the valve
# deck to the back wall. Re-measure it by sweeping the lane —
#
#     w.cast((x, 160.0, z), (0, 1, 0), dia=6.35)
#
# — which reads clear at ±88 and stops on the machine's own bodies at every station inboard of it.
GATE_LANE_X = 88.0
# How far aft the line has run by the time it reaches that lane. The step outboard is taken as one
# DIAGONAL with this reach in it, so the leg is 34.7 mm rather than the 10.9 mm between the gate's
# column and the lane — a square corner spends its whole radius as tangent in each leg it touches,
# and the two this leg carries want more than that step is long.
#
# It also stands FORWARD OF V-K, whose body reaches into the east flank at this height: the
# diagonal is on the lane before it reaches the valve's own face.
GATE_LANE_Y = 175.0
# Where each line comes about onto the panel deck — the far end of the lean it climbs its whole
# storey in — and where it then crosses to its union's own column.
#
# THE HOPPER IS WHAT BOUNDS THE CROSSING. At the deck's own height the bowl is near its full
# width, reaching x ±79.5 until its aft face; a crossing is a leg wall to wall, so it is taken
# behind that face and nowhere else. Re-read it by sweeping the deck —
#
#     w.cast((100.0, y, deck), (-1, 0, 0), dia=6.35)
#
# EAST the crossing is the far end of the lean itself: the lean is steep, tops out one board's
# depth behind the hopper, and turns straight into the crossing, so the two share a corner. It
# also stands AHEAD of the carb riser's own crossing, which reaches this line's column further
# aft.
GATE_A_DECK_Y = 264.0
# WEST the union stands 8 mm off the lane, which is not two stock arcs — so the lean runs on aft
# past the ASSE chain and the step inboard is taken as one plan DIAGONAL, with the reach aft in it
# to make the leg.
GATE_B_DECK_Y = 340.0
GATE_B_CROSS_Y = 380.0


def _gate_climb_z(solids, stub: str) -> float:
    """The Z a gate's line climbs to on its own column: one `GATE_STUB_CLEAR` and its own
    half-section under the reservoir stub standing over that gate."""
    return solids[stub].BoundingBox().zmin - _split.TUBE_D / 2.0 - GATE_STUB_CLEAR


def _gate_climb_under_cruise(F) -> float:
    """The same figure struck on `RESERVOIR_CRUISE` instead of on a stub — what the west gate
    climbs to under `fluid-24`, which is the body crossing ITS column.

    A run's own underside is one half-section below its axis, exactly as a stub's box is, so the
    two flanks come out on one plane while the two reservoir lines cross on one."""
    return (F["valve-v-i"].at("outlet")[2] + RESERVOIR_CRUISE
            - _split.TUBE_D - GATE_STUB_CLEAR)


def _fluid_28(F, solids):
    """fluid-28 — the nozzle-B gate to its rear union, and the line the manifold sends out of the
    machine on the WEST side.

    V-J-O faces UP off the west outboard valve, under the hopper's bowl and behind the reservoir
    stub that shares its column. So the run climbs what that stub leaves, steps out into the
    outboard lane, and takes the whole storey to the deck in ONE LEAN — which carries it back
    inboard onto the union's own column and aft past the bowl at the same time. Then it runs the
    deck to the collet on that collet's own axis.

    THE OUTBOARD LANE IS WHAT THE LEAN IS TAKEN IN. The tap-water lane stands in the column
    between this gate and its union — the flow regulator reaches x −81 across it and the split
    stands over that — and the lane runs outboard of both."""
    gate = F["valve-v-j"].at("outlet")
    tin = F["bulkhead-flavor-b"].at("tube-in")
    climb = _gate_climb_under_cruise(F)
    return R.bent(
        "fluid-28", "valve-v-j.outlet",
        (gate[0], gate[1], climb),                  # up what the reservoir stub leaves
        (-GATE_LANE_X, GATE_LANE_Y, climb),         # one diagonal west and aft into the lane
        (-GATE_LANE_X, GATE_B_DECK_Y, tin[2]),      # one lean aft and up the lane onto the deck
        (tin[0], GATE_B_CROSS_Y, tin[2]),           # one diagonal east onto the union's column
        "bulkhead-flavor-b.tube-in",                # and straight aft into the collet
        kind="fluid", bend=TUBE_BEND,
        note="nozzle B: V-J-O → rear union, up the gate's own bay, out into the west outboard "
             "lane and one lean onto the panel deck")


def _fluid_18(F, solids):
    """fluid-18 — the nozzle-A gate to its rear union, and the line the manifold sends out of the
    machine on the EAST side.

    THE SAME FOUR MOVES AS ITS TWIN AND ONE MORE, because the east flank is deeper. V-G-O faces
    up under the same bowl behind the same kind of stub, and the outboard lane is the same strip;
    but the union it ends on stands west of centre — the +X end of the wall is the C14's — so
    where `fluid-28` closes on its own column this one crosses the deck first.

    The deck it crosses is the room over the pump's crown: the hopper stops short of it forward,
    the power block stands below it aft, and between the two there is nothing in it at all."""
    gate = F["valve-v-g"].at("outlet")
    tin = F["bulkhead-flavor-a"].at("tube-in")
    climb = _gate_climb_z(solids, "stub-fluid-15")
    return R.bent(
        "fluid-18", "valve-v-g.outlet",
        (gate[0], gate[1], climb),                  # up what the reservoir stub leaves
        (GATE_LANE_X, GATE_LANE_Y, climb),          # one diagonal east and aft into the lane
        (GATE_LANE_X, GATE_A_DECK_Y, tin[2]),       # one lean aft and up the lane onto the deck
        (tin[0], GATE_A_DECK_Y, tin[2]),            # west across the deck onto the union's column
        "bulkhead-flavor-a.tube-in",                # and straight aft into the collet
        kind="fluid", bend=TUBE_BEND,
        note="nozzle A: V-G-O → rear union, up the gate's own bay, out into the east outboard "
             "lane, one lean onto the panel deck and west across it")


# --- the two reservoir lines, off the junctions and down onto the cap ------
#
# Each leaves its junction's open mouth facing aft over its own nozzle gate, and each ends on a
# bore up a column of the cold core's cap. ONE LEAN AND NO TYPED COORDINATE: the run leaves on
# the mouth's own axis, leans aft and inboard onto the bore's column together, and drops. The one
# waypoint is a component of the two mouths, so the pair rides a move of either.
#
# THE LEAN IS WHAT SEATS THE ARCS. Both corners draw their tangent out of the leg between them,
# and a corner spends `R·tan(θ/2)` of it — so carrying the reach aft and the step inboard on one
# diagonal gives that shared leg its full length and halves the angle each end turns through.

def _reservoir_line(F, cid: str, tee: str, mouth_port: str, bore_port: str, note: str):
    """One junction's open mouth to the cap conduit its reservoir is reached through."""
    mouth = F[tee].at(mouth_port)
    bore = F["foam-assembly"].at(bore_port)
    return R.bent(
        cid, f"{tee}.{mouth_port}",
        (bore[0], bore[1], mouth[2]),       # one lean aft and inboard, onto the bore's column
        f"foam-assembly.{bore_port}",       # and straight down into it
        kind="fluid", lead=(TUBE_BEND, TUBE_BEND),
        skew=(R.COLLET_SKEW, CAP_BORE_SKEW), note=note)


# --- channel B's pair, which has no junction between it and the reservoir ----
#
# Reservoir B carries TWO MOUTHS of its own — the draw on the bulkhead at the bottom of its wet
# V, out of the `reservoir-b` conduit at the head of the +Y band; the fill on a bore in its own
# cap, under the `reservoir-b-fill` conduit standing over it. So each of its pair's valves
# reaches one directly and nothing stands between them.
#
# BOTH ENDS OF BOTH RUNS FACE UP. A gate's collet on the lower deck opens +Z and a cap conduit
# opens +Z, so each of these is a U over the crown rather than a fall: it leaves on its own axis,
# crosses on one plane, and comes down on the far one's. `RESERVOIR_CRUISE` is that plane, and it
# is not typed — it is the least a collet facing up can rise and still turn, which is one stock
# radius. Both ends of both runs sit on the same port plane, so one figure serves all four.
RESERVOIR_CRUISE = TUBE_BEND
# The two ends of `fluid-24`'s crossing from the outboard lane to the bore's own column.
#
# THE WEST HALF IS OPEN AT THIS PLANE ONLY FORWARD OF `water-5`. Swept east from x −80 at the
# cruise, the strip runs clear across the machine at every station up to y 190 and then shuts:
# `water-5` stands at x −60.6 from y 195 to 220 on its way to the `water-in` bore, and the
# discharge chain takes x[−64.5, −49] from y 223 aft. So the crossing is taken forward of both,
# and what the run does aft of it is hold the bore's column, which is clear the machine's whole
# depth.
#   `FILL_B_JOIN_Y` is then fenced from the other side: `fluid-26` rises off the draw bore at
# y 184 on this same column, so the join stands clear of that climb by more than the two lines'
# own sections. `FILL_B_LEAN_Y` holds the gate's column long enough to make the crossing steep,
# which is what buys that clearance.
FILL_B_LEAN_Y = 170.0
FILL_B_JOIN_Y = 194.0


def _fluid_24(F):
    """fluid-24 — the channel-B fill gate to the bore in reservoir B's own cap.

    V-I-O opens UP off the west outboard limb, on the same column the nozzle-B gate climbs and
    one storey under it. The run rises what a corner needs, holds that column aft the length of
    the manifold — the outboard lane is clear of everything the west flank stands — and leans
    inboard onto the bore only at `FILL_B_LEAN_Y`, behind the tap water's own descent.

    THE FILL ARRIVES ABOVE THE LIQUID, which is the whole of why the reservoir has two mouths:
    everything entering has to cross the cavity to leave by the trough, so a purge displaces
    what is in there rather than short-circuiting back out the drain it came in by."""
    mouth = F["valve-v-i"].at("outlet")
    bore = F["foam-assembly"].at("reservoir-b-fill")
    cruise = mouth[2] + RESERVOIR_CRUISE
    return R.bent(
        "fluid-24", "valve-v-i.outlet",
        (mouth[0], mouth[1], cruise),           # up off the collet, what a corner needs
        (mouth[0], FILL_B_LEAN_Y, cruise),      # aft on the gate's own column, up the lane
        (bore[0], FILL_B_JOIN_Y, cruise),       # one lean inboard onto the bore's column
        (bore[0], bore[1], cruise),             # aft on it, past what shuts the strip west
        "foam-assembly.reservoir-b-fill",       # and straight down into the bore
        kind="fluid", bend=TUBE_BEND, skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="reservoir B fill: V-I-O → the fill bore in its own cap, up the west outboard "
             "lane and one lean inboard onto the bore")


def _fluid_26(F):
    """fluid-26 — the draw conduit on reservoir B's cap to the channel-B draw gate.

    The reverse journey of `fluid-24` and a shorter one, because the draw's conduit stands at the
    head of the +Y band on the FORWARD strip rather than over the pocket. It rises off that bore,
    takes one lean forward and inboard across the strip the source valves stand in, and drops
    onto V-H-I's own column.

    The lean crosses between two descents on the same strip — `water-5` into `water-in` one
    column west, `fluid-2` a storey above — and holds the cruise plane between them."""
    bore = F["foam-assembly"].at("reservoir-b")
    gate = F["valve-v-h"].at("inlet")
    cruise = gate[2] + RESERVOIR_CRUISE
    return R.bent(
        "fluid-26", "foam-assembly.reservoir-b",
        (bore[0], bore[1], cruise),             # up off the bore onto the cruise plane
        (gate[0], gate[1], cruise),             # one lean forward and inboard onto the gate
        "valve-v-h.inlet",                      # and straight down into the collet
        kind="fluid", bend=TUBE_BEND, skew=(CAP_BORE_SKEW, R.COLLET_SKEW),
        note="reservoir B draw: the cap's draw conduit → V-H-I, up off the bore and one lean "
             "forward and inboard onto the gate's own column")


def _fluid_15(F):
    """fluid-15 — reservoir A's junction to its conduit on the cold core's cap.

    `fluid-25` read across the machine. Where reservoir B carries two mouths and reaches each
    of its pair's valves directly, reservoir A's fill and draw meet at Y-E before the shell —
    so ONE line leaves this junction and one bore carries it, and the cap column it climbs is
    reservoir B's own read across the mirror plane.

    The slot it drops through is the one the source valves and V-K leave between them, and it is
    the bore's own column — the lean holds the mouth's plane until it is over that slot, and the
    descent is what V-K's face fences."""
    return _reservoir_line(
        F, "fluid-15", "tee-y-e", "Y-E-2", "reservoir-a",
        "reservoir A: Y-E-2 → its conduit on the cap, one lean aft and west on the "
        "mouth's own plane onto the bore's column, and down")


def authored() -> frozenset:
    """The connection ids this module draws a run for, without building one. `front_half` reads
    it before the pack is assembled, to know which of the manifold's placeholder mouth stubs a
    real line has replaced."""
    return frozenset(_AUTHORED)


# The ids `build_runs` can produce. One name per `_*` author below, and the guard each is behind
# only decides whether the bodies to draw it are placed yet.
_AUTHORED = ("water-7", "water-6", "water-5", "water-2", "fluid-1", "water-4", "water-3",
             "co2-1", "co2-2", "fluid-2", "carb-1", "carb-2", "fluid-28", "fluid-18",
             "fluid-24", "fluid-26", "fluid-15")


def tubes(runs):
    """Each run swept at its own bore, as `(name, solid)` — what the assembly carries."""
    return [(f"tube-{r.id}", R.tube(r)) for r in runs]


def report(runs):
    """One line per run: what it joins, the stock it cuts, and the roundest corner it turns."""
    if not runs:
        return
    print("\nruns")
    for r in runs:
        print(f"  {r.id:12} {r.frm:28} → {r.to:28} {r.length:7.1f} mm  "
              f"{len(r.bends)} corner(s) at R{r.tightest:.1f} "
              f"(stock floor R{R.stock_min(r.kind, r.diam):.1f})")
    for cid, why in sorted(BLOCKED.items()):
        print(f"  BLOCKED {cid}: {why}")
