"""The enclosure assembly's tube runs — every line between two placed bodies, authored port to port.

The manifold's own 21 segments are drawn by `manifold_layout.py`, which knows its butt joints
and its hairpins. This module is for the runs BETWEEN sub-assemblies: a mouth on one placed body
to a mouth on another, through whatever the pack leaves between them.

Each run is one `R.bent(...)` — the source port, hand-placed interior waypoints, the destination
port — swept at the port's own bore. `_routing` seats the largest arc each corner's two legs
allow and records the shortfall of any that cannot: a run drawn past its stock's floor is still
drawn, and `BLOCKED` says by how much.

A RUN ARRIVES WITH THE BODIES IT JOINS. Both of its mouths have to be placed before it can be
authored, so the set here grows as `enclosure_assembly.build_pack` grows, and a run with one end in
the pack and the other nowhere is not written down as a guess. `build_seated_runs` is the same rule
one step later: the box is sized on the pack, so a body seated in one of its WALLS is placed after
it, and the lines reaching those bodies are drawn once the box exists.

Frames come off the placed pack, so a run rides a move of its parts: change a pose in
`enclosure_assembly.py` and every waypoint measured off that body's ports moves with it.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
# EVERY MODULE IMPORTED BELOW IS ON THIS LIST, this module's own directory among them. A module
# that leans on its importer's path is one only that importer can import: the doc-sync drivers
# reach this file without going through `enclosure_assembly`, and they set up their own path.
for _p in (_hw / "scripts", _here.parent,
           _hw / "printed-parts" / "cold-core",
           _hw / "printed-parts" / "cold-core" / "copper-plugs",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "reference" / "compressor",
           _hw / "reference" / "condenser-block",
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
import enclosure as _enc                               # noqa: E402
import _cold_core_interface as _cc                     # noqa: E402
import asse1022_assembly as _asse                      # noqa: E402
import hopper_funnel as _funnel                        # noqa: E402
import seaflo_22_pump as _pump                         # noqa: E402
import seaflo_suction_chain as _suct                   # noqa: E402
import seaflo_discharge_chain as _dis                  # noqa: E402
import beduan_solenoid as _beduan                      # noqa: E402
import jg_bulkhead_union as _jg                        # noqa: E402
import neofit_flow_control as _flowreg                 # noqa: E402
import water_split as _split                           # noqa: E402
import manifold_layout as _ml                           # noqa: E402
import compressor as _comp                             # noqa: E402
import condenser_block as _cond                        # noqa: E402
import copper_plugs as _plugs                          # noqa: E402
import gasher_check_valve as _gasher                    # noqa: E402
import wr1110_regulator as _wr1110                      # noqa: E402
import digiten_flow_sensor as _digiten                  # noqa: E402

BLOCKED = R.BLOCKED


def _ea_cap(name):
    """The core's cap conduit stations, read off `enclosure_assembly` at call time — importing it
    here at module scope would close a cycle, since it imports this one."""
    import enclosure_assembly
    return enclosure_assembly.cap_conduit(name)

# The 3/8" reinforced PVC's own floor, and the coarsest stock on the machine: a corner it cannot
# hold is a corner nothing drawn here can.
HOSE_BEND = R.stock_min("water", _suct.HOSE_OD)
# The 1/4" LLDPE's, which every fitting on the water side hands over on.
TUBE_BEND = R.stock_min("water", _split.TUBE_D)
# How far off its own axis a hose may leave a BARB and still run unbent. A barb is a taper the
# hose stretches over and a clamp closes on, not a collet gripping a tube all round, so it takes
# a good deal more than `R.COLLET_SKEW`. Seeded, not ratified.
BARB_SKEW = 14.0
# 1/4" soft ACR copper, the stock the sealed loop is cut from.
CU_OD = 6.35
# The straight each copper mouth takes before its first corner, so the arcs seat in the middle
# of the run and neither brazed stub is asked to bend where it is made up.
CU_BEND = R.stock_min("refrigerant", CU_OD)
CU_LEAD = 20.0
# How far off its own axis a line may enter a CAP CONDUIT. The lid's hole is countersunk to this
# angle (`_cold_core_interface.cap_conduit_entry_skew`), so the lip a leaning line crosses lies
# along it and what the tube bears on there is a face.
CAP_BORE_SKEW = _cc.cap_conduit_entry_skew

# Which reference module states each placed body's stations, and the bore each one carries. The
# module gives `(position, outward axis)` in the body's own frame; `enclosure_assembly`'s `carry`
# takes that through the placement, so a port table is written once and rides every later move.
STATIONS = {
    # The cold core's cap conduits — bores up the cap's own columns, each opening on the lid's
    # outer face. A line reaching one arrives at the deck, not at a body face.
    "foam-assembly": {"water-in": (lambda: _ea_cap("water-in"), _split.TUBE_D),
                      "carb-water-out": (lambda: _ea_cap("carb-water-out"), _split.TUBE_D),
                      "reservoir-a": (lambda: _ea_cap("reservoir-a"), _split.TUBE_D),
                      "reservoir-b": (lambda: _ea_cap("reservoir-b"), _split.TUBE_D),
                      "reservoir-a-fill": (lambda: _ea_cap("reservoir-a-fill"), _split.TUBE_D),
                      "reservoir-b-fill": (lambda: _ea_cap("reservoir-b-fill"), _split.TUBE_D),
                      "co2-in": (lambda: _ea_cap("co2-in"), _split.TUBE_D),
                      # The evaporator's two ends are copper, not LLDPE, and they open on
                      # the core's own flanks rather than up its cap columns.
                      "evap-outlet": (lambda: _plugs.slot_station("evap-outlet"), CU_OD),
                      "evap-inlet": (lambda: _plugs.slot_station("evap-inlet"), CU_OD)},
    "compressor": {"refrig-suction": (lambda: _comp.stations()["refrig-suction"], CU_OD)},
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
    # The basin's gravity drain — the spout's exit annulus, on the collar centre, facing the
    # floor. `hopper_funnel.drain_local` is in the part's own frame, so it rides the funnel
    # wherever the top wall carries it.
    "hopper-funnel": {"drain": ((lambda: (_funnel.drain_local, (0.0, 0.0, -1.0))),
                                _funnel.spout_id)},
}

# The three unions the machine dispenses through, all on one row of the back wall. Each carries
# the same two mouths the tap-water union does, under the names the topology gives them: the
# INBOARD collet is what a run inside the box pushes into, the outboard one is what the
# above-counter umbilical lands on.
for _b in ("bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb"):
    STATIONS[_b] = {"tube-in": (lambda: _jg.port(-1.0), _jg.PORT_D),
                    "tube-out": (lambda: _jg.port(1.0), _jg.PORT_D)}


# The flavour manifold's ten solenoid valves. Each stands coil-up with its flow along the pack's
# own ±Y, and the fold names its two collets `front` and `back`.
# `enclosure_assembly.manifold_carry` takes both through the pose and the lift the pack is stood
# at, so a run anchors on where the collet ends up.
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
    if {"compressor", "foam-assembly"} <= set(F):
        runs.append(_refrig_3(F))
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
    if {"wr1110", "foam-assembly"} <= set(F):
        runs.append(_co2_2(F))
    if {"flow-regulator", "valve-v-a"} <= set(F) and "coil-v-a" in placed:
        runs.append(_fluid_2(F, placed))
    if {"foam-assembly", "digiten-flow"} <= set(F):
        runs.append(_carb_1(F))
    if {"digiten-flow", "bulkhead-carb"} <= set(F):
        runs.append(_carb_2(F))
    if {"valve-v-j", "bulkhead-flavor-b"} <= set(F) and "valve-v-i" in F:
        runs.append(_fluid_28(F, placed))
    if {"valve-v-g", "bulkhead-flavor-a"} <= set(F) and "valve-v-f" in F:
        runs.append(_fluid_18(F, placed))
    if {"valve-v-i", "foam-assembly"} <= set(F):
        runs.append(_fluid_24(F))
    if {"valve-v-h", "foam-assembly"} <= set(F):
        runs.append(_fluid_26(F))
    if {"valve-v-f", "foam-assembly"} <= set(F):
        runs.append(_fluid_14(F, placed))
    if {"valve-v-e", "foam-assembly"} <= set(F):
        runs.append(_fluid_16(F))
    return runs


def build_seated_runs(placed, carries):
    """The runs with a mouth on a body the BOX seats rather than the pack.

    The box is sized on the pack, so a body seated in one of its walls is placed after it — and a
    run reaching that body can only be authored once it is.
    `enclosure_assembly.build_enclosure_assembly` calls this with the pack's own bodies and the
    seated one added to them, so a run drawn here anchors on exactly the frames the pack's own runs
    do."""
    F = frames(placed, carries)
    runs = []
    if {"hopper-funnel", "valve-v-a", "valve-v-b", "seaflo-pump"} <= set(F):
        runs.append(_fluid_4(F, placed))
    return runs


def _co2_1(F):
    """co2-1 — the check's stub tip to the regulator's inlet socket, one straight hop.

    The two mouths face each other down the chain's own axis with `enclosure_assembly.CO2_HOP`
    between them, so this is a PP450822E on the check's male stub, a PP010822E in the regulator's
    female one, and the length of tube the two collets both take hold of."""
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
    the assembly that crosses the whole machine.

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

    The tube between two mouths and nothing about it turns: the split's flavour collet fires
    forward and the regulator's inlet faces it on that collet's own line, both on the storey the
    hopper's bowl leaves the lane."""
    return R.bent(
        "fluid-1", "water-split.to-flavor", "flow-regulator.inlet",
        kind="fluid", note="flavor tap: split run → flow regulator, straight down the lane")


# What each collet on the step gets straight off its own axis before `water-2` starts to lean —
# the stub a push-to-connect grips, taken out of the reach `enclosure_assembly.WATER_2` gives.
WATER_2_LEAD = 6.0


def _water_2(F):
    """water-2 — the ASSE 1022's outlet to the split's supply, and the tap's whole step off the
    panel deck.

    ONE LEAN IN THE OPEN ROOM AFT OF THE HOPPER. The chain hands the water over facing forward
    down the west lane and the split's own run axis IS that lane, a storey lower — so the two
    collets face each other down the lane with `enclosure_assembly.FLAVOR_STEP` between them.
    The run leaves and enters on-axis off its own `WATER_2_LEAD` stubs and takes the whole fall
    in the leg between, which lies in the room the bowl stops short of.

    THE TWO ARE NOT ON ONE COLUMN. The chain's is the rear wall's `PORT_WEST_COLUMN` and the
    split's is `enclosure_assembly.SPLIT_COLUMN`, so the lean crosses as well as falls.

    THE WAYPOINT IS THE MIDDLE OF ALL THREE, which is the whole of what makes this one lean and
    not two. Halfway along each of the run's own coordinates, the two legs it splits the lean
    into are collinear and the waypoint is a point on a straight rather than a corner — so the
    lean turns twice, once out of each stub, and each of those two turns the same angle. Take
    the middle of any two of the three and the offset in the third is spent entirely in one
    half: the legs come out at different angles, the waypoint becomes a kink, and the run pays
    a corner tighter than either stub asked for."""
    src = F["asse1022-assembly"].at("tube-out")
    dst = F["water-split"].at("supply")
    return R.bent(
        "water-2", "asse1022-assembly.tube-out",
        tuple((src[i] + dst[i]) / 2.0 for i in range(3)),
        "water-split.supply",
        kind="water", bend=TUBE_BEND, lead=WATER_2_LEAD,
        note="tap water: ASSE outlet → split supply, one lean off the deck onto the lane the "
             "hopper's bowl leaves")


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
    the placement is what buys those legs: the rib's own column sets the reach east and
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

    ONE CORNER IN PLAN AND NOTHING ELSE. `SEAFLO_YAW` puts the discharge barb on the head's WEST
    face pointing west, and the chain lies in that lane forward of it with its own barb facing AFT
    — so the hose leaves across the machine and turns along it. The chain lies in a rib printed on
    the core's cap, one seat's height off that face, while the barb is `seaflo_22_pump.PORT_Z` up
    the head — so the run falls that difference on the same leg it turns on, which is `water-7`'s
    own shape read across the machine.

    Both corners want the stock's whole `HOSE_BEND` as tangent in each leg they touch, and the
    placement is what buys those legs: the anchor's own column sets the reach west and
    `DISCH_CORNER_ROOM` the reach forward.

    `lead` plants a waypoint on each port's own axis, so the hose leaves the barb and enters the
    chain dead straight and a clamp closes on a straight length at either end."""
    return R.bent(
        "water-6", "seaflo-pump.discharge", "discharge-chain.barb-tip",
        kind="water", bend=HOSE_BEND, skew=BARB_SKEW, lead=HOSE_BEND,
        note="carb water: SeaFlo discharge barb → discharge chain, west off the barb, one quarter "
             "forward and down onto the chain's own axis (3/8\" braided PVC, two clamps)")


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


def _co2_2(F):
    """co2-2 — the regulator's outlet to the cold core's CO2 conduit, and the whole gas path
    inside the machine.

    IT NEVER CHANGES HEIGHT UNTIL IT DROPS. The regulator lies on the panel deck, so the run
    leaves its outlet on that storey, comes forward onto the bore's own Y, crosses east onto the
    bore's own column and falls the whole way down the port lane in one leg. Three legs, two
    corners, and the only descent is the last of them.

    IT IS `carb-1` ON THE SAME DECK, ONE CAP CONDUIT AFT. That run climbs this same lane off the
    lid's other bore and crosses the deck the other way, to the meter. The two conduits stand
    side by side on the lid and their two runs stand side by side over it.

    The lane is the one window the +X flank leaves: the power block's column stands on the lid
    from the cap to the ceiling aft of it, and V-K's plate forward of it. Both ends of this run
    are on the deck, so a move of the deck carries the whole of it."""
    out = F["wr1110"].at("outlet")
    bore = F["foam-assembly"].at("co2-in")
    return R.bent(
        "co2-2", "wr1110.outlet",
        (out[0], bore[1], out[2]),           # forward down the chain's own column onto the bore's Y
        (bore[0], bore[1], out[2]),          # east along the deck onto the bore's column
        "foam-assembly.co2-in",              # and straight down the port lane into it
        kind="co2", lead=(TUBE_BEND, TUBE_BEND), skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="CO2: WR1110 outlet → the core's CO2 cap conduit, forward along the panel deck, "
             "east onto the port lane's column and down it")


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
    is what makes that stub a real line, so `enclosure_assembly.build_pack` stops adding the
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


# --- the hopper's gravity drain ---------------------------------------------
#
# `fluid-4` carries HEAD and not pressure, and it is the basin's air-purge path as well as its
# drain, so NO LEG OF IT MAY RISE — a hump anywhere in it holds the air the basin has to push
# out. Every leg below either falls or is level.


def _fluid_4_lane_z(solids) -> float:
    """The storey the drain crosses the source pair on.

    THE PAIR IS A WALL FROM THE PORT PLANE UP TO ITS COIL CROWNS, AND THE MIRROR LINE IS THE ONE
    WAY THROUGH IT. V-A and V-B stand a valve's half-width either side of x 0 with their coils
    over them, and what the two leave between them on the machine's own centreline is a slot a
    quarter-inch line fits with under a millimetre either side — the manifold's own inner-limb
    gap, and the tightest lane in the machine. This is that slot's floor: the run hangs its
    underside on the plane the coils stand on — the highest the pair reaches anywhere inboard of
    them — and what it actually clears is the valves' crown hardware under that plane.

    It is also as low as the drop can afford to cross. What stands between the spout and that
    plane is where the first corner's stock arc and the tube's own half-section come out of, and
    the straight the line leaves the spout with is whatever is left of it."""
    return solids["valve-v-a"].BoundingBox().zmax + _split.TUBE_D / 2.0


def _fluid_4_turn_y(F, solids) -> float:
    """The plane the drain comes about in — where it leaves the slot and leans onto V-B's column.

    IT HAS TO COME ABOUT AFT OF THE PAIR, because V-B's inlet is the AFT collet: the line runs
    the valve's whole length past its own mouth and turns back into it. What it turns in is the
    band between the source pair and the water pump, and `fluid-2` crosses that band on V-A's own
    stub plane — so this stands midway between that crossing's skin and the pump's front face,
    which is the widest either gap can be made."""
    cross = F["valve-v-a"].at("inlet")[1] + _ml.STUB + _split.TUBE_D / 2.0
    return (cross + solids["seaflo-pump"].BoundingBox().ymin) / 2.0


def _fluid_4(F, solids):
    """fluid-4 — the hopper basin's spout to V-B's inlet, and the machine's only gravity feed.

    FOUR LEGS, TWO FALLING AND TWO LEVEL. It drops the spout's own column onto the slot the
    source pair leaves on the mirror line, runs aft down that slot, comes about behind the pair
    and takes the rest of the fall in ONE LEAN west onto V-B's column and port plane, then runs
    forward into the aft-facing collet.

    THE LEAN IS ONE LEG AND NOT TWO CORNERS. V-B's column stands one inner limb off the mirror
    line and its collet faces the way the run arrives from, so slot to collet is a full 180° —
    and a 180° built of two stock arcs wants 2 × R14 between its straights where those columns
    leave 20. Spending the fall in the same leg is what makes it: the lean is 30 mm long because
    it descends while it steps across, so both of its corners seat R14 where a flat dogleg would
    seat R10."""
    drain = F["hopper-funnel"].at("drain")
    inlet = F["valve-v-b"].at("inlet")
    lane = _fluid_4_lane_z(solids)
    turn = _fluid_4_turn_y(F, solids)
    return R.bent(
        "fluid-4", "hopper-funnel.drain",
        (drain[0], drain[1], lane),          # down the spout's own column onto the slot
        (drain[0], turn, lane),              # aft down the mirror line, between the two valves
        (inlet[0], turn, inlet[2]),          # one lean west and down onto the collet's column
        "valve-v-b.inlet",                   # and forward into the mouth
        kind="fluid", bend=TUBE_BEND,
        note="hopper: the basin's drain → V-B inlet, down the spout's column, aft down the "
             "mirror line between the source valves and one lean west onto the collet — every "
             "leg falls or is level")


# --- the carb-water riser, and the two nozzle gates' lines to the panel -----
#
# All three end on the panel deck (`enclosure_assembly.PANEL_X`), which is the band over the water
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

    `enclosure_assembly.build_digiten` seats the meter ON THIS RUN: its outlet is placed one
    `CARB_2` forward of the union's collet and on that collet's own column and plane, so the two
    mouths face each other down one line with nothing between them to turn around."""
    return R.bent(
        "carb-2", "digiten-flow.outlet", "bulkhead-carb.tube-in",
        kind="water", note="carb water: DIGITEN outlet → rear union, one straight down the deck")


# How high a gate's line climbs on its own column before it steps outboard. Each gate has its own
# channel's reservoir line standing over it, so the column is a bay and not a shaft, and this is
# the air left under whatever that is.
#
# WHAT CROSSES A GATE'S COLUMN IS ITS OWN CHANNEL'S FILL LINE. West that is `fluid-24`, which
# runs aft up the outboard lane on `RESERVOIR_CRUISE` and passes directly over V-J. East,
# `fluid-14` climbs a storey higher to cross V-K, so nothing fences V-G at all — and the two
# gates still take ONE plane, because they are twins and a pair that reads the same on both
# flanks is worth more than the few millimetres the east one could have.
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
# aft — and the riser is what actually sets it. `carb-1` climbs the cap's `carb-water-out`
# conduit on one column that runs the machine's whole height, so it crosses this storey whatever
# storey this is; the only room between them is Y, and this is the plane that leaves it. Struck
# off the riser rather than stated, so a conduit that moves takes the crossing with it.
GATE_A_RISER_CLEAR = 2.0


def _gate_a_deck_y(F) -> float:
    """Where the east gate's lean tops out — one clear section forward of the carb riser.

    The lean and the crossing SHARE THIS CORNER, so the arc that joins them leans back toward
    the riser and the two are nearest on the arc rather than on either straight. That is what
    `GATE_A_RISER_CLEAR` is over and above the two half-sections."""
    return F["foam-assembly"].at("carb-water-out")[1] - _split.TUBE_D - GATE_A_RISER_CLEAR
# WEST the union stands 8 mm off the lane, which is not two stock arcs — so the lean runs on aft
# past the ASSE chain and the step inboard is taken as one plan DIAGONAL, with the reach aft in it
# to make the leg.
GATE_B_DECK_Y = 340.0
GATE_B_CROSS_Y = 380.0
# EAST the line has the machine to cross, because its union stands in the WEST pair. The crossing
# is taken fore of the pump, on the one strip that is clear wall to wall there: under it the
# manifold's own crossings fill the band — `fluid-2` and `fluid-4` reach z 294 across the middle
# — and over it `fluid-14` and `co2-2` take the room. Re-read it by sweeping the strip:
#
#     w.hits(probe.box(x=(-50, 90), y=(258, 270), z=(z, z + 6)))
GATE_A_CROSS_Z = 303.0
# Where the line has come down onto its union's own storey: forward of the drip tray, whose
# channel takes that column from y 346 aft.
GATE_A_FALL_Y = 340.0


def gate_cruise(v_i_outlet_z: float) -> float:
    """The storey the two nozzle gates cruise their outboard lanes at, off the collet of the
    valve whose own channel crosses the west gate's column.

    The same figure struck on `RESERVOIR_CRUISE` instead of on a stub — what the west gate
    climbs to under `fluid-24`. A run's own underside is one half-section below its axis, exactly
    as a stub's box is, so the two flanks come out on one plane while the two reservoir lines
    cross on one.

    Takes the Z rather than the frames, so a body may be STOOD on this plane before any run is
    drawn — `enclosure_assembly.panel_z` puts the nozzle-B union on it."""
    return v_i_outlet_z + RESERVOIR_CRUISE - _split.TUBE_D - GATE_STUB_CLEAR


def station(body: str, port: str):
    """One body's station in its own frame, as a carry takes it."""
    return STATIONS[body][port][0]()


def _gate_climb_under_cruise(F) -> float:
    """`gate_cruise` read off the placed valve."""
    return gate_cruise(F["valve-v-i"].at("outlet")[2])


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

    THE SAME FOUR MOVES AS ITS TWIN AND TWO MORE, because its union stands in the WEST pair and
    this gate is on the east flank. V-G-O faces up under the same bowl behind the same kind of
    stub, and the outboard lane is the same strip; but where `fluid-28` closes on a column three
    fittings away, this one has the machine to cross.

    IT CROSSES FORE OF THE PUMP AND FALLS BEHIND IT. The lean carries it past the manifold's own
    crossings to `GATE_A_CROSS_Z`, it takes the strip west onto its union's column, and then it
    comes down that column to the union's storey — forward of the drip tray, which takes the same
    column from its own front rim aft."""
    gate = F["valve-v-g"].at("outlet")
    tin = F["bulkhead-flavor-a"].at("tube-in")
    climb = _gate_climb_under_cruise(F)
    deck_y = _gate_a_deck_y(F)
    return R.bent(
        "fluid-18", "valve-v-g.outlet",
        (gate[0], gate[1], climb),                        # up what the reservoir stub leaves
        (GATE_LANE_X, GATE_LANE_Y, climb),                # one diagonal east and aft into the lane
        (GATE_LANE_X, deck_y, GATE_A_CROSS_Z),            # one lean aft and up onto the crossing
        (tin[0], deck_y, GATE_A_CROSS_Z),                 # west across the machine, fore of the pump
        (tin[0], GATE_A_FALL_Y, tin[2]),                  # down the column onto the union's storey
        "bulkhead-flavor-a.tube-in",                      # and straight aft into the collet
        kind="fluid", bend=TUBE_BEND,
        note="nozzle A: V-G-O → rear union, up the gate's own bay, out into the east outboard "
             "lane, one lean onto the crossing strip, west across the machine fore of the pump "
             "and down its union's own column")


# --- the four reservoir lines, gate to vessel and vessel to gate --------------
#
# Neither reservoir has a junction: each carries two mouths of its own — the draw on the bulkhead
# at the bottom of its wet V, the fill on a bore in its own cap — so each pair's two valves reach
# one directly. The fill arrives ABOVE THE LIQUID, which is the whole point of the second mouth:
# everything entering has to cross the cavity to leave by the trough, so a purge displaces what
# is in there rather than short-circuiting back out the drain it came in by.
#
# BOTH ENDS OF EVERY ONE OF THESE FACE UP. A gate's collet on the lower deck opens +Z and a cap
# conduit opens +Z, so each is a U over the crown rather than a fall: it leaves on its own axis,
# crosses on one plane, and comes down on the far one's.
#
# THREE OF THE FOUR CROSS ON `RESERVOIR_CRUISE`, which is not typed — it is the least a collet
# facing up can rise and still turn, one stock radius, and every one of those ends sits on the
# same port plane so one figure serves them. `fluid-14` is the exception and says why.
RESERVOIR_CRUISE = TUBE_BEND
# The two ends of `fluid-24`'s crossing from the outboard lane to the bore's own column.
#
# THE WEST HALF IS OPEN AT THIS PLANE ONLY FORWARD OF `water-5`. Swept east from x −80 at the
# cruise, the strip runs clear across the machine at every station up to y 185 and then shuts:
# `water-5` crosses this plane at x[−60.1, −53.2] over y[185.7, 203.2] on its way down to the
# `water-in` bore, and the discharge chain takes x[−64.5, −49] from y 223 aft. So the crossing
# is taken forward of both, and what the run does aft of it is hold the bore's column, which is
# clear the machine's whole depth.
#   THAT BAND IS THE PUMP'S. `water-5` leaves the discharge chain's collet on the barb's own
# storey (`seaflo_22_pump.PORT_Z` up the head) and slants down to a bore on the cap, so where it
# stands in this plane is where that slant happens to be — a barb higher up the head is a
# steeper slant standing further forward, and this crossing moves ahead of it.
#   `FILL_B_JOIN_Y` is then fenced from the other side: `fluid-26` rises off the draw bore at
# y 184 on this same column, so the join stands clear of that climb by more than the two lines'
# own sections. `FILL_B_LEAN_Y` holds the gate's column long enough to make the crossing steep,
# which is what buys that clearance.
FILL_B_LEAN_Y = 170.0
FILL_B_JOIN_Y = 192.0
# What a line holds off a body it passes in a lane, where the lane is the whole of its room.
LANE_CLEAR = 4.0
# THE LANE `fluid-14` CROSSES THE MACHINE IN: the daylight between V-K standing on the cap and
# channel A's own V-A beside it, which runs from the manifold to the back of the core. Both
# bodies are round where the lane is narrowest and their boxes stand well inside their own metal,
# so the lane is swept —
#
#     w.cast((43.5, 432.0, 289.0), (0, -1, 0), dia=6.35)
#
# — which runs the machine's whole depth without contact, and stops on V-K or on V-A's coil at
# every column either side of it.
#
# V-A's crown stands under this plane; over it the tap-water riser crosses to the pump's suction
# on `water-7`, at z 293.85 across x[32.5, 63.5] over y[323.4, 338.5]. The tightest on the sweep
# is 1.4 mm.
FILL_A_LANE_Z = 289.0


def _fill_a_lane_y(solids) -> float:
    """Where the run comes about onto the lane — one clear section forward of V-K's own face,
    so the diagonal off the gate is on the lane's column before it reaches the valve it passes."""
    return solids["vk-solenoid"].BoundingBox().ymin - _split.TUBE_D - LANE_CLEAR


def _fill_a_turn_y(F) -> float:
    """Where it leaves the lane for the bore's own column — aft of the tap-water riser.

    `water-7` crosses this lane on the pump's suction barb in 3/8" braided, the fattest stock the
    machine carries. The run holds the lane past that hose and leans east only behind it."""
    return F["seaflo-pump"].at("suction")[1] + (_suct.HOSE_OD + _split.TUBE_D) / 2.0 + LANE_CLEAR


def _fluid_14(F, solids):
    """fluid-14 — the channel-A fill gate to the bore in reservoir A's own cap.

    RESERVOIR A IS THE AFT POCKET AND THE PUMP STANDS ON IT. The SeaFlo takes the middle of A's
    cap and the power brick the far side, and what they leave is the strip between them — which
    is where the bore is. So this run has the machine's whole depth to cross, and it crosses on
    the CAP'S OWN STOREY: up off the gate onto `FILL_A_LANE_Z`, one diagonal aft and inboard into
    the lane V-K and V-A leave between them, aft down that lane the length of the core, one lean
    east onto the bore's column behind the tap-water riser, and straight down the strip into it.

    ITS COLUMN IS THE DRAW BORE'S OWN. `fluid-16` rises off `reservoir-a` and leans away forward;
    the fill runs aft on that same column and crosses over its own channel's draw where it stands.

    THE RIB IT LIES IN IS THE CAP'S. The lane passes over the stretch of lid between V-K's aft
    face and the pump's front one, and `_cold_core_interface.cap_anchors["fluid-14"]` stands
    there."""
    gate = F["valve-v-f"].at("outlet")
    bore = F["foam-assembly"].at("reservoir-a-fill")
    lane_x = F["foam-assembly"].at("reservoir-a")[0]
    return R.bent(
        "fluid-14", "valve-v-f.outlet",
        (gate[0], gate[1], FILL_A_LANE_Z),          # up onto the cap's own storey
        (lane_x, _fill_a_lane_y(solids), FILL_A_LANE_Z),   # one diagonal aft and inboard, onto the lane
        (lane_x, _fill_a_turn_y(F), FILL_A_LANE_Z),        # aft down the lane, west of the riser
        (bore[0], bore[1], FILL_A_LANE_Z),          # one lean east onto the bore's own column
        "foam-assembly.reservoir-a-fill",           # and straight down the strip into it
        kind="fluid", bend=TUBE_BEND, skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="reservoir A fill: V-F-O → the fill bore in its own cap, up onto the cap's storey, "
             "aft down the lane V-K and V-A leave between them and one lean east onto the bore's "
             "column behind the tap-water riser")


def _fluid_16(F):
    """fluid-16 — the draw conduit on reservoir A's cap to the channel-A draw gate.

    A's draw conduit stands at the head of its band on the same forward strip B's does, so this
    and `fluid-26` are the same shape on opposite flanks — up off the bore, one lean forward and
    inboard, and down onto the gate's own column."""
    bore = F["foam-assembly"].at("reservoir-a")
    gate = F["valve-v-e"].at("inlet")
    cruise = gate[2] + RESERVOIR_CRUISE
    return R.bent(
        "fluid-16", "foam-assembly.reservoir-a",
        (bore[0], bore[1], cruise),             # up off the bore onto the cruise plane
        (gate[0], gate[1], cruise),             # one lean forward and inboard onto the gate
        "valve-v-e.inlet",                      # and straight down into the collet
        kind="fluid", bend=TUBE_BEND, skew=(CAP_BORE_SKEW, R.COLLET_SKEW),
        note="reservoir A draw: the cap's draw conduit → V-E-I, up off the bore and one lean "
             "forward and inboard onto the gate's own column")


def _fluid_24(F):
    """fluid-24 — the channel-B fill gate to the bore in reservoir B's own cap.

    V-I-O opens up off the west outboard limb, on the same column the nozzle-B gate climbs and
    one storey under it. The run rises what a corner needs, holds that column aft the length of
    the manifold — the outboard lane is clear of everything the west flank stands — and leans
    inboard onto the bore only at `FILL_B_JOIN_Y`, behind the tap water's own descent."""
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
    head of the +Y band on the FORWARD strip rather than over the pocket. The lean crosses between
    two descents on the same strip — `water-5` into `water-in` one column west, `fluid-2` a
    storey above — and holds the cruise plane between them."""
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


def _refrig_3(F):
    """refrig-3 — the evaporator's outlet back to the compressor's suction, in copper.

    The other two joints of the sealed loop are made across a plane their bodies already share
    and draw no tube. This one cannot be: the compressor's shell is a pressed oblong, so it
    meets a neighbour along a tangent line, and that tangent stands short of the cold core's
    front. So this leg is cut and brazed like any other run — up out of the shell's suction and
    back into the core's own outlet slot."""
    return R.bent(
        "refrig-3", "compressor.refrig-suction", "foam-assembly.evap-outlet",
        kind="refrigerant", bend=CU_BEND, lead=CU_LEAD,
        note="sealed loop: evaporator outlet → compressor suction, the one leg of the three "
             "that is drawn rather than made across a shared plane")


def authored() -> frozenset:
    """The connection ids this module draws a run for, without building one. `enclosure_assembly`
    reads it before the pack is assembled, to know which of the manifold's placeholder mouth stubs
    a real line has replaced."""
    return frozenset(_AUTHORED)


# The ids `build_runs` can produce. One name per `_*` author below, and the guard each is behind
# only decides whether the bodies to draw it are placed yet.
_AUTHORED = ("water-7", "water-6", "water-5", "water-2", "fluid-1", "water-4", "water-3",
             "co2-1", "co2-2", "fluid-2", "fluid-4", "carb-1", "carb-2", "fluid-28", "fluid-18",
             "fluid-24", "fluid-26", "fluid-14", "fluid-16", "refrig-3")


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
