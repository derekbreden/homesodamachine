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

Where a piece of a run can stand is read by sweeping it —
[`probe.World.reroute`](/hardware/scripts/probe.py) slides named waypoints across a range of
offsets, redraws the run at each one, and reports what it collides with there, the bands that
are clear, and the radius each corner has left:

    tools/cad-venv/bin/python hardware/scripts/probe.py route fluid-14
    tools/cad-venv/bin/python hardware/scripts/probe.py reroute fluid-14 3-4 y- 0:80:2.5

A bend, a fall, a crossing, a leg — whatever the piece is called it is some waypoints of the
route, and those indices are the handle (`route` numbers them, `--near x,y,z` says which index
a pick off the STEP is). The centreline is what moves; the ribs struck on the run, the cap's
seat for it and the stretch it is graded on stand where they stand, and each sweep prints them.

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
           _hw / "reference" / "jg-pp0408w",
           _hw / "reference" / "neofit-bulkhead",
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
import jg_pp0408w as _pp0408w                          # noqa: E402
import neofit_bulkhead as _neofit                      # noqa: E402
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
# The lane the compressor's suction turns in, off the −X wall's inner face: the straight the leg
# leaves on and the radius its first corner carries past that straight.
CU_SUCTION_LANE = 2.0 * CU_BEND
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
    "compressor": {"refrig-suction": (lambda: _comp.stations()["refrig-suction"], CU_OD),
                   "refrig-discharge": (lambda: _comp.stations()["refrig-discharge"], CU_OD)},
    "condenser+fan": {"refrig-outlet": (lambda: _cond.stations()["refrig-outlet"], CU_OD),
                      "refrig-inlet": (lambda: _cond.stations()["refrig-inlet"], CU_OD)},
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
    # The other inlet on that wall, and the same two mouths under the same names: the customer's
    # red tether lands on the outboard collet and the gas chain leaves by the inboard one.
    "co2-inlet": {"inboard": (lambda: _neofit.port(-1.0), _neofit.TUBE_OD),
                  "outboard": (lambda: _neofit.port(1.0), _neofit.TUBE_OD)},
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
    # The disconnect under that drain. Its upper collet takes the stub the basin carries and
    # its lower one starts `fluid-4`, so the two are named for the joint rather than for flow:
    # `stub` is the mouth a hand works and `outlet` is the mouth a run leaves by.
    "hopper-drain-union": {"stub": (lambda: _pp0408w.port(1.0), _pp0408w.PORT_D),
                           "outlet": (lambda: _pp0408w.port(-1.0), _pp0408w.PORT_D)},
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
    if {"compressor", "condenser+fan"} <= set(F):
        runs.append(_refrig_1(F))
    if {"condenser+fan", "foam-assembly"} <= set(F):
        runs.append(_refrig_2(F))
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
    if {"co2-inlet", "gasher-co2"} <= set(F):
        runs.append(_co2_0(F))
    if {"gasher-co2", "wr1110"} <= set(F):
        runs.append(_co2_1(F))
    if {"wr1110", "foam-assembly"} <= set(F):
        runs.append(_co2_2(F))
    if ({"flow-regulator", "valve-v-a", "bulkhead-flavor-a"} <= set(F)
            and "coil-v-a" in placed):
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
    if {"hopper-drain-union", "valve-v-a", "valve-v-b", "seaflo-pump"} <= set(F):
        runs.append(_fluid_4(F, placed))
    return runs


def _co2_0(F):
    """co2-0 — the wall bulkhead's inboard collet to the check's inlet socket, one straight hop.

    The two mouths face each other down the chain's own axis with
    `enclosure_assembly.CO2_INLET_HOP` between them, so this is a PI010822S in the check's female
    inlet and the length of tube the bulkhead's collet and the adapter's collet both grip."""
    return R.bent(
        "co2-0", "co2-inlet.inboard", "gasher-co2.inlet",
        kind="co2", note="CO2: rear-wall bulkhead → check inlet, one straight hop on the "
                         "chain's axis")


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


# WHERE THE MACHINE IS CROSSABLE, and it is the cold core's own front step. The lid's outer face
# runs forward at z 253.4 from the deck the valve cradles stand on, and the band over that face —
# between the core's front and the hopper union's ring — is clear from wall to wall. The crossing
# lies in it, one lane off the core it is assembled onto, and the core's cap prints the rib that
# holds it there. Re-measure it by sweeping the cast in y —
#
#     w.cast((-78.0, y, z), (1, 0, 0), dia=6.35)
#
# WHAT MOVES IT IS THE DISPLAY. The band's forward bound is the hopper union's ring, the union
# hangs on the funnel's drain, and the top wall sites the funnel as far forward as the display
# facet's back plane allows — so growing the facet walks this crossing aft by the same figure.
# The run is authored in `build_runs`, which draws the pack's own runs before the box seats the
# funnel, so the union is not there to measure against and this is a Y rather than a standoff.
# `clearance-floor` is what holds the two apart, and it is what caught the facet growing.
CROSS_Y = 176.5
# And how far UNDER V-K's own inlet plane it runs. The hopper's disconnect hangs on the spout's
# column and its ring stands in the storey this run used to cross on, so the crossing drops
# beneath the union's foot — and what it drops ONTO is the height the cap's rib holds it at over
# the lid's face, which is what `_cold_core_interface.cap_anchors` states.
CROSS_DROP = 7.1
# THE CHANNEL THE BRANCH FALLS INTO, and it is the strip the box already leaves west of the core.
# `enclosure.side_band_inset` is the band between the shell's own face and the wall's inner one,
# and NOTHING UNDER IT IS THE CORE'S — which is what this run comes here for: a belly in the strip
# is floored by the cabinet rather than by the cap lid the shell's own x-band stands over.
#   TWO THINGS STAND IN IT. The Y SEAM, where the front piece laps the back one, puts a second
# wall's thickness proud of the inner face on that plane, and this run crosses the seam on its way
# forward — so the lap is what fences it across, and the run stands midway between the lap and the
# shell. And `fluid-28`'s anchor rib crosses the band bodily at tube height, on the slice of Y its
# own `GATE_B_STEP_Y` places it in. This run is forward of that rib and does not meet it; a run
# taken up the band aft of it would. Re-measure across at the seam's own plane, and along it for
# the rib —
#
#     w.cast((-90.0, 213.1, z), (-1, 0, 0), dia=6.35)
#     tools/cad-venv/bin/python hardware/scripts/probe.py hits --x -101.5,-90.5 --y 265,290 --z 260,280
#
CHANNEL_X = -97.2
# HOW FAR UNDER THE CROSSING'S LANE THE FALL BOTTOMS OUT. The branch's corner turns through more
# than a right angle: the leg leaving it leans west into the channel and rises onto the lane over
# the run forward, so the fall ends beneath the storey it hands the water to.
#
# THE TEE ABOVE STANDS ONE TANGENT OVER THAT CORNER, which is what the fall costs it. The arc's
# own belly is the deepest the run gets, one `port_lead` under the branch collet, and it holds its
# lane over the lid's outer face.
#
# THE BELLY IS ARITHMETIC OFF THE ROUTE AND NOT A SOLID DISTANCE. This run is SEATED on the cap —
# the side post grips it on the crossing — so `clearance-floor` holds the pair exempt, and the
# distance between tube and shell reads the post's own grip whatever this figure is. What the
# belly keeps over the lid is `_water_3`'s vertex plus corner 0's tangent, less one `port_lead`.
# Re-read it by standing a box under the arc —
#
#     tools/cad-venv/bin/python hardware/scripts/probe.py hits --x -96.1,-89.7 --y 223,229 --z 250,256
#
CROSS_RISE = 8.0
# Where it starts leaning off the core again. The crossing hugs the core as far east as the
# hopper union's ring, then leans forward and up in ONE leg onto V-K's column and inlet plane:
# the collet needs its own straight, and a crossing that stayed against the core to the end would
# leave a closing leg too short to turn a stock arc in.
# WHERE THE RUN REACHES THE CHANNEL'S OWN COLUMN, and it is what carries the fall's belly out of
# the lid's shadow. The branch collet fires down on `enclosure_assembly.SPLIT_COLUMN`, whose tube
# stands its east face inside the shell's x-band — so a corner whose outgoing leg is mostly
# FORWARD keeps its arc on that column and bellies over the cap. Struck aft of the crossing, the
# leg out of that corner heads WEST instead, the arc swings with it, and the belly comes down in
# the strip where the lid is not underneath. What the fall may then spend is `CROSS_RISE`, and
# what that is worth is the tee's own height.
#   IT IS FENCED BOTH WAYS. The leg into it has to seat corner 0's whole quarter-turn as tangent,
# so it cannot be struck so near the branch that the fall has no room to turn; and the leg out of
# it runs the channel to the crossing, which is what the run is in the strip FOR.
CHANNEL_ENTRY_Y = 224.0
CROSS_LIFT_X = 20.0
CROSS_APPROACH_Y = 164.0




def _water_3(F):
    """water-3 — the split's DOWNWARD branch to V-K's forward-facing inlet, and the one run in
    the assembly that crosses the whole machine.

    It has to. The split stands in the WEST lane and V-K stands on the EAST, and V-K's inlet
    faces FORWARD — so the water leaves the split going down, and has to arrive at V-K from in
    front of it. There is no shorter way round: the valve manifold occupies the storey between
    the two columns and the band behind the union's ring is the one window through it.

    IT FALLS INTO THE CHANNEL AND RUNS IT. The branch drops on the split's own column, and its
    corner turns WEST off that column into `CHANNEL_X` — the strip between the shell's face and
    the wall's — reaching that column at `CHANNEL_ENTRY_Y`, aft of the crossing. What follows is
    a leg down the channel itself, rising `CROSS_RISE` onto the crossing's storey as it goes.

    THE TEE ABOVE STANDS ONE TANGENT OVER THAT CORNER, which is what the fall costs it, so where
    the corner's arc bellies is what sets the tap's height. `SPLIT_COLUMN` stands the branch's own
    tube with its east face inside the shell's x-band, so an arc that leaves mostly FORWARD stays
    on that column and bellies over the cap lid. Leaving WEST swings the arc into the strip, where
    what is under the belly is the cabinet floor rather than the lid.

    IT CROSSES UNDER THE HOPPER'S DISCONNECT. The union hangs on the basin's spout in the middle
    of that window, so the crossing runs `CROSS_DROP` under the inlet's own plane, the whole width
    of the machine beneath the union's foot and against the cold core's front, and climbs back
    onto the inlet's plane on V-K'S OWN COLUMN — where the climb costs nothing, because the aft
    leg into the collet is there anyway and the lean shares it. The cap's own side post grips the
    run on that lane (`_cold_core_interface.cap_side_anchors`), which is what fixes its height.

    The closing straight is planted on the collet's axis (`lead`), so the mouth is entered square
    however the lean arrives at it."""
    split, vk = F["water-split"], F["vk-solenoid"]
    src, dst = split.at("to-vk"), vk.at("inlet")
    z = dst[2] - CROSS_DROP
    return R.bent(
        "water-3", "water-split.to-vk",
        (src[0], src[1], z - CROSS_RISE),   # the whole fall, on the branch's column, past the lane
        (CHANNEL_X, CHANNEL_ENTRY_Y, z - CROSS_RISE),  # west OUT of the lid's shadow, still low
        (CHANNEL_X, CROSS_Y, z),              # forward down the channel, rising onto the lane
        (CROSS_LIFT_X, CROSS_Y, z),           # east along that lane, beneath the union's foot
        (dst[0], CROSS_APPROACH_Y, dst[2]),  # one lean off the core, onto V-K's column and plane
        "vk-solenoid.inlet",
        kind="water", lead=(None, _ml.STUB),
        note="tap water: split branch → V-K inlet, down into the west channel, across the window "
             "under the hopper's union, and up V-K's own column into the mouth")


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

    A HAIRPIN. The regulator stands over the split on one column with its inlet facing the way
    the split's flavour collet faces, so the run leaves one mouth going forward, turns through
    180° in the open room ahead of the pair, and comes back into the other.

    THE TWO WAYPOINTS ARE THE TURN'S OWN CORNERS, one radius forward of the FURTHER mouth and one
    over the other. A square U is what the router is given and two quarter-arcs are what it
    returns: the rise is `enclosure_assembly.FLUID_1_RISE`, each arc spends a radius of it, and
    nothing is left over. Both mouths are on one X, so the turn lies in the lane's own vertical
    plane; the two stand one reach apart along it, because the pair is stacked on its BODIES'
    centres and their two collets look the same way off that column. So the apex is struck on
    whichever mouth reaches further forward, and the other's leg is the reach longer."""
    split, reg = F["water-split"], F["flow-regulator"]
    src, dst = split.at("to-flavor"), reg.at("inlet")
    apex = min(src[1], dst[1]) - TUBE_BEND
    return R.bent(
        "fluid-1", "water-split.to-flavor",
        (src[0], apex, src[2]),             # forward off the split's collet, and turn up
        (src[0], apex, dst[2]),             # up the turn's own column, and turn back aft
        "flow-regulator.inlet",
        kind="fluid", bend=TUBE_BEND,
        note="flavor tap: split run -> flow regulator, a 180 degree hairpin forward of the pair")


# What each collet on the step gets straight off its own axis before `water-2` starts to lean.
# NOT A GRIP — a collet grips inside the fitting, behind the face, and a line starts curving at
# that face. What this holds is the TANGENT its own corner seats on, R·tan(θ/2) for the lean the
# step takes, so it is priced against the corner rather than against the push-fit. Taken out of
# the reach `enclosure_assembly.WATER_2` gives.
#   IT ALSO CARRIES THE LEAN OUT OF THE TAP'S OWN STOREY. The split's supply mouth faces aft and
# this straight runs aft on its axis, level, a storey under the regulator — so every millimetre
# here is a millimetre the climb does not spend in the band `fluid-2` leaves the regulator
# through. The lean starts where this ends.
#   AND IT IS SELF-OPPOSING, which is what keeps it honest: the lead is taken out of the step's Y
# and the fall is not, so a longer straight leaves the lean less run for the same drop and steepens
# it. The corner's own demand rises with it — slower than the lead does, which is why there is a
# figure that satisfies both, but the two move together and neither may be read alone.
WATER_2_LEAD = 12.0
# THE SPLIT END'S HORIZONTAL SECTION, stated as a leg rather than reached for as a lead. A lead
# plants its point along the port's own axis and the climb's corner then backs its tangent into
# that same straight, so what stands off the tee is the lead less that tangent. A waypoint is a
# place the run passes through: the leg is the length, and the corner takes its tangent out of the
# LEAN instead. What the eye reads standing off the collet is this figure less `R·tan(θ/2)`.
#   IT IS FENCED AT BOTH ENDS. Aft, `wago-reeds-b`'s well opens at y 294.60 on that wall, and this
# leg's far end has to stop short of it. Forward, the lean it hands the run to crosses the lane
# `fluid-2` leaves the regulator on, and a leg that ends too early puts that crossing in the same
# band. Between them, `WATER_2_LEAD` and this share one leg — the lean — and each of the two
# corners backs its tangent down it, so neither figure may be read alone. `bend-radius` reads the
# pair back and `clearance-floor` reads the crossing.
WATER_2_RUN = 23.25


def _water_2(F):
    """water-2 — the ASSE 1022's outlet to the split's supply, and the tap's whole step off the
    panel deck.

    ONE LEAN IN THE OPEN ROOM AFT OF THE HOPPER. The chain hands the water over facing forward
    down the west lane and the split's own run axis IS that lane, a storey lower — so the two
    collets face each other down the lane with `enclosure_assembly.FLAVOR_STEP` between them.
    The run leaves the chain on-axis off its own `WATER_2_LEAD` stub and arrives at the tee along
    `WATER_2_RUN`, the level leg stated aft of it; the whole fall is taken in the lean between,
    which lies in the room the bowl stops short of.

    THE TWO ARE NOT ON ONE COLUMN. The chain's is the rear wall's `PORT_WEST_COLUMN` and the
    split's is `enclosure_assembly.SPLIT_COLUMN`, so the lean crosses as well as falls.

    ONE END IS A STUB AND THE OTHER IS A PLACE, and that is the whole shape of it. At the chain,
    `lead=` plants a point one reach along the collet's axis and the lean starts wherever the
    corner off it leaves off — a standoff, spent by its own turn. At the tee, `WATER_2_RUN` is a
    waypoint the run must pass through, so the level leg is the length it says and the lean starts
    at its far end. The tee's stub is therefore 0, not open: `None` there would ask the router for
    one bend radius along the same axis the waypoint already stands on.
      The lean is the single leg between those two, and it turns twice — once out of the chain's
    stub, once onto the tee's leg — at whatever angle the step's fall and crossing make of it."""
    _S2 = F["water-split"].at("supply")
    return R.bent(
        "water-2", "asse1022-assembly.tube-out",
        # A STATED HORIZONTAL SECTION off the tee, on the tee's own storey. `lead=` cannot carry
        # this: it plants its point along the port axis and the climb's own corner then reaches
        # back into it, so a longer lead is largely eaten before it is seen. A waypoint is a place
        # the run must pass through, so this length is the length.
        (_S2[0], _S2[1] + WATER_2_RUN, _S2[2]),
        "water-split.supply",
        kind="water", bend=TUBE_BEND, lead=(WATER_2_LEAD, 0.0),
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


# The straight `fluid-2` runs aft off the regulator's outlet before it turns. It is longer than
# the arc's own tangent so a length of tube still leaves the collet straight, and no longer:
# `water-2` comes down this same lane from the chain overhead, and the further aft this run turns
# the nearer it turns to that descent.
FLUID_2_LEAD = 15.0
# THE CROSSING THREADS THE DRAIN, which fences it from both sides. `fluid-4` comes aft down the
# mirror line on `_fluid_4_lane_z`'s storey and then turns DOWN onto V-B's column, so the band this
# run crosses has the drain's lane over it and the drain's own turn into that valve under it. The
# storey is struck up off V-A's inlet plane rather than down off the lane, because the turn is the
# nearer of the two: the lean spends this rise getting down the column and passes over the turn's
# arc on the way.
FLUID_2_CROSS_RISE = 18.5
# How far past the pack's own stub this run turns onto V-A's column. A square corner spends its
# whole radius as tangent in each leg it touches, so a turn planted ON the stub's far end has
# exactly the stub to seat in and no more — this is what the leg carries over that.
FLUID_2_CROSS_SET = 1.0
# The column the run goes forward and down in: the strip WEST of the flavour-A line's own aft
# lane. `fluid-18` holds that lane over the whole depth this run crosses it in, so the strip is
# struck off the union that line falls onto and rides it wherever the union goes. Both are 1/4",
# and the figure is axis to axis — one tube's diameter of it is the two skins.
FLUID_2_LANE_CLEAR = 10.35


def _fluid_2(F, solids):
    """fluid-2 — the flow regulator's outlet to V-A's inlet, and the tap water's last leg
    before the flavour manifold.

    THE TWO MOUTHS FACE THE SAME WAY AND THE VALVE IS BEHIND THE REGULATOR. The regulator stands
    over the split with its flow running aft, so its outlet fires AFT; V-A stands coil-up on the
    deck with its inlet on the AFT end, so the run has to come at that collet from behind. It goes
    aft off the regulator, turns east across the lane, comes forward and down the strip in one
    leg, and leans east behind both coils onto V-A's column.

    IT CROSSES THE LANE LEVEL, ON THE OUTLET'S OWN STOREY, AND SPENDS NO HEIGHT DOING IT. `water-2`
    comes down this same lane from the chain overhead and passes under this run on its way to the
    split, so what the two have between them is whatever this one has not yet given away — and the
    crossing stands where the descent has barely begun. Every millimetre of the fall is taken in
    the strip instead, east of the lane and clear of that line altogether.

    THE STRIP'S DESCENT AND ITS RUN FORWARD ARE ONE LEG. Taken as two they are two SQUARE corners
    sharing the strip's own depth, and a square corner spends its whole radius as tangent in each
    leg it touches — so the pair would want two stock radii of a strip that has 22. Leaning the
    descent forward instead makes both corners shallower than square AND lengthens the leg they
    share, and the two spend under two thirds of what they then stand in.

    THE CROSSING THREADS THE DRAIN. `fluid-4` holds the mirror line on `_fluid_4_lane_z`'s
    storey and then turns down onto V-B's column, so this run crosses that line square with the
    drain's lane over it and the drain's own turn under it. `FLUID_2_CROSS_RISE` is the window it
    goes through, and the lean spends that rise getting down V-A's own column.

    The last leg is `manifold_layout.STUB` and `FLUID_2_CROSS_SET` over it — the straight that
    pack draws on every mouth that leaves it, which is what its first corner needs before it can
    turn at all. Drawing this run is what makes that stub a real line, so
    `enclosure_assembly.build_pack` stops adding the placeholder once the run exists."""
    reg, vk_a = F["flow-regulator"], F["valve-v-a"]
    out, inlet = reg.at("outlet"), vk_a.at("inlet")
    lane = out[1] + FLUID_2_LEAD
    lane_x = F["bulkhead-flavor-a"].at("tube-in")[0] - FLUID_2_LANE_CLEAR
    under = inlet[2] + FLUID_2_CROSS_RISE
    cross = inlet[1] + _ml.STUB + FLUID_2_CROSS_SET
    return R.bent(
        "fluid-2", "flow-regulator.outlet",
        (lane_x, lane, out[2]),                       # east across the lane, level on its own storey
        (lane_x, cross, under),                       # forward and down that strip in one leg
        (inlet[0], cross, inlet[2]),                  # east under the drain, onto V-A's column
        "valve-v-a.inlet",
        kind="fluid", lead=(FLUID_2_LEAD, _ml.STUB),
        note="tap water: flow regulator outlet → V-A inlet, aft off the regulator, level east "
             "across the lane into the strip west of the nozzle-A line, forward and down that "
             "strip, and east through the window the drain leaves")


# --- the hopper's gravity drain ---------------------------------------------
#
# `fluid-4` carries HEAD and not pressure. The basin's own column is what moves it: the brim
# stands at the machine's ceiling and V-B's inlet is 88 mm under it, so the line runs full and
# climbs whatever it is given on the way. What it may not do is END high — the last leg into the
# collet falls, and the basin empties to the collet's own plane.
#
# THE LOW POINT IS A TRAP AND IT IS PUMPED DRY. The disconnect hangs the union's whole length
# below the spout and `fluid-4` starts under it, so the run's first leg is the deepest point on
# the line and everything after it climbs back to the lane. Concentrate stands in that dip when
# the basin runs out; what clears it is the same suction the machine already uses on the clean
# cycle — V-B opens onto the pump's own draw, and `assembly/acceptance-and-burn-in.md`'s dry
# purge pulls air through the whole run until the nozzle sputters.


# Where the drain climbs back out of the disconnect. The union stands Ø15.10 on the spout's own
# column and fills the lane the run used to drop into, so the line has to come up somewhere else
# and lean back. The bay it comes up in is the open one west of the basin's neck, forward of V-B
# and under the collar — the step across to it is what gives both of its corners their arc, so it
# is measured from the union rather than chosen: two stock radii is the least a 90° in and a 90°
# out can be built from, and the column stands one of those past the union's own ring.
FLUID_4_FLOOR_Z = 248.0  # the plane the step west runs on, under the union's own foot
FLUID_4_RISER_X = -28.0  # the bay's column, clear of the union's ring and of `fluid-26`'s step
FLUID_4_REJOIN_Y = 183.0  # where the lean back lands on the mirror line — aft of the union,
                          # forward of where the source coils close the slot


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
    """fluid-4 — the hopper's disconnect to V-B's inlet, and the machine's only gravity feed.

    IT GOES ROUND THE UNION IT LEAVES. The disconnect hangs Ø15.10 on the spout's own column and
    fills the lane the run used to drop into, so the line leaves the lower collet still falling,
    steps west under the union's own foot, climbs the open bay in front of the cold core back to
    the lane, and leans east onto the mirror line in the band between the union and the source
    coils. From there it is the run it always was: aft down the slot, about behind the pair, and
    one lean west onto the collet.

    THE DIP IS THE LINE'S LOW POINT AND IT IS PUMPED, NOT DRAINED. See the note above this
    section: V-B opens onto the pump's own draw and the dry purge pulls the whole run through.

    THE LEAN INTO V-B IS ONE LEG AND NOT TWO CORNERS. V-B's column stands one inner limb off the
    mirror line and its collet faces the way the run arrives from, so slot to collet is a full
    180° — and a 180° built of two stock arcs wants 2 × R14 between its straights where those
    columns leave 20. Spending the fall in the same leg is what makes it: the lean descends while
    it steps across, so both of its corners seat R14 where a flat dogleg would seat R10.

    THE FIRST LEG IS THE FALL OFF THE UNION, and it is what the disconnect is paid for out of —
    `enclosure_assembly.build_enclosure_assembly` records it against the basin's own seat, and
    `room-holds` is where it reads."""
    drain = F["hopper-drain-union"].at("outlet")
    inlet = F["valve-v-b"].at("inlet")
    lane = _fluid_4_lane_z(solids)
    turn = _fluid_4_turn_y(F, solids)
    return R.bent(
        "fluid-4", "hopper-drain-union.outlet",
        (drain[0], drain[1], FLUID_4_FLOOR_Z),                # down off the collet, under the union's foot
        (FLUID_4_RISER_X, drain[1], FLUID_4_FLOOR_Z),         # west across that floor, clear of the ring
        (FLUID_4_RISER_X, drain[1], lane),                    # up the bay's own column onto the lane
        (drain[0], FLUID_4_REJOIN_Y, lane),                   # one lean east and aft, round the union
        (drain[0], turn, lane),                               # aft down the slot, between the two valves
        (inlet[0], turn, inlet[2]),                           # one lean west and down onto the collet's column
        "valve-v-b.inlet",                                    # and forward into the mouth
        kind="fluid", bend=TUBE_BEND,
        note="hopper: the basin's disconnect → V-B inlet, down off the union and west under its "
             "foot, up the bay in front of the cold core, one lean east and aft onto the mirror "
             "line, then aft down the slot between the source valves")


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


# How high the WEST gate's line climbs on its own column before it steps outboard. That gate has
# its own channel's reservoir line standing over it, so the column is a bay and not a shaft, and
# this is the air left under whatever that is.
#
# WHAT CROSSES A GATE'S COLUMN IS ITS OWN CHANNEL'S FILL LINE. West that is `fluid-24`, which
# runs aft up the outboard lane on `RESERVOIR_CRUISE` and passes directly over V-J and fixes this
# plane. East, `fluid-14` climbs a storey higher to cross V-K, so NOTHING FENCES V-G AT ALL —
# and `fluid-18` climbs its own bay through this plane to the crown lane. This figure is the
# west line's.
GATE_STUB_CLEAR = 4.0
# WHERE THE WEST GATE'S LINE RUNS AFT IS ITS OWN UNION'S COLUMN, and it takes that column at the
# first corner it can and holds it to the wall. The gate stands on `LIMB_OUT_XW` and the union on
# `PORT_WEST_COLUMN`, which are ONE MILLIMETRE apart — so the whole crossing between them is that
# millimetre, and a line that spends it once has nothing left to spend. Everything aft of the jog
# is one column: the cold core's whole length, the panel deck and the collet.
#
# WHAT THAT LEAVES IS THE WEST FLANK ITSELF. A run out in the outboard strip stands its section in
# the one band the −X wall's own furniture wants — the tap-water split's cap reaches x −85.1
# inboard and the three cluster lever nuts sit in that wall's wells — and it fences that band for
# the whole height it crosses at. On the union's column the tube spans x[−81.2, −74.9] and the
# strip outboard of it is the wall's.
#
# THE EAST FLANK IS NOT ITS TWIN. The board and its relay hang on the +X wall's own seat and take
# that column from y 232 aft for the whole of the height a gate line would climb it in — so
# `fluid-18` cannot come down its own flank at all and takes the crown lane over the core instead.
# What follows is the west line's.
#
# HOW FAR AFT THE JOG IS TAKEN, and it is fenced from both sides. The leg has to hold the climb's
# whole quarter-turn as tangent — a square corner spends its whole radius in each leg it touches,
# so `TUBE_BEND` of this leg is spoken for before the jog's own corner asks for any — and the jog
# turns only `atan(1 / reach)`, which `_routing._straighten` DROPS under 2°: past 28.6 mm of reach
# there is no corner here at all and the run is drawn as one straight into the collet, off its
# axis. This stands between the two, at 19.9 mm of leg and 2.87° of turn.
GATE_B_JOG_Y = 162.0
# Where the line comes off the cruise plane onto its union's own storey. The rise is 2.9 mm and
# the run holds the plane it climbed to for everything before it, so what this figure places is
# THE ANCHOR: the rib rides the middle of the leg it names, and the middle of this one stands in
# the daylight between the tap-water split's barrel (which ends at y 260) and the wall's own
# cluster wells (which begin at y 295). It is the one stretch of that wall a rib can cross without
# standing in something else's band, and it leaves 12 mm either side.
GATE_B_STEP_Y = 393.0
# What the rise takes fore and aft. Both its corners turn 8.1° and spend a millimetre of tangent
# apiece, so nearly all of this is straight — the reach is here to keep the corner well over the
# 2° a lean needs to be a lean, not because the arcs want it.
GATE_B_RISE_RUN = 20.0
# How far aft the EAST line has run by the time it reaches the crown lane. The step inboard is
# taken as one DIAGONAL with this reach in it, so the leg is 45.2 mm rather than the 33.6 mm
# between the gate's column and the lane — a square corner spends its whole radius as tangent in
# each leg it touches, and the two this leg carries want more than that step is long.
#
# It also stands FORWARD OF V-K, whose body reaches into the east flank at this height: the
# diagonal is on the lane before it reaches the valve's own face.
GATE_LANE_Y = 175.0
# Where the EAST line comes about to cross to its union's own column — it has the machine to
# cross, because its union stands in the WEST pair. A crossing is a leg wall to wall, so what
# bounds it is whatever fills the strip it is taken on. Re-read it by sweeping that strip —
#
#     w.cast((100.0, y, z), (-1, 0, 0), dia=6.35)
#
# The run comes about on ITS OWN STOREY and not on a deck, so this is a plan corner and nothing
# more. What stands at the aft end of the crown lane is the PUMP, whose barrel fills that storey
# from its front face back, so the lane runs until that face and the corner is taken at the last
# station forward of it. Struck off the pump rather than stated, so a pump that shifts fore takes
# the crossing with it.
#
# THE WEST LINE HAS NO CROSSING. Its union stands on the column it is already running, one
# millimetre off its own gate's, so what the east line spends a whole leg on the west line spent
# at `GATE_B_JOG_Y` before the cold core began.
def _gate_a_deck_y(solids) -> float:
    """Where the east line comes about to cross — the last station forward of the pump's face."""
    return solids["seaflo-pump"].BoundingBox().ymin - _split.TUBE_D / 2.0 - LANE_CLEAR
# EAST the line has the machine to cross, because its union stands in the WEST pair — and it
# takes ONE STOREY from the bay it climbs out of to the column it falls down: the strip that
# carries it aft over the core's crown and the strip that carries it west are one daylight, so
# nothing between them is a lean.
#
# WHAT THAT DAYLIGHT IS BETWEEN. Under it the manifold's own crossings fill the band — `fluid-2`
# and `fluid-4` reach 294.0 across the middle — and over it the hopper's bowl closes the ceiling
# at its own underside, 304.4. Both are hard and neither governs, so this stands in the MIDDLE of
# the two rather than held off either: a run stood one clearance off one wall is the run that
# starves when the other moves. That leaves a section and a half of daylight each way. Re-read
# the band by sweeping the strip:
#
#     w.hits(probe.box(x=(-50, 90), y=(258, 270), z=(z, z + 6)))
#
# `fluid-14` SHARES THAT COLUMN A STOREY UNDER THIS. The fill line holds `FILL_A_LANE_Z` across
# the core's front and falls onto the cap behind it, so the tallest of it stands a full section
# below, and the crown lane passes over it the whole way aft.
GATE_A_CROSS_Z = 299.2
# Where the line has come down onto its union's own storey: forward of the drip tray, whose
# channel takes that column from y 346 aft.
GATE_A_FALL_Y = 340.0


def gate_cruise(v_i_outlet_z: float) -> float:
    """The storey the WEST nozzle gate cruises aft at, off the collet of the valve whose own
    channel crosses that gate's column.

    The same figure struck on `RESERVOIR_CRUISE` instead of on a stub — what the west gate climbs
    to under `fluid-24`. A run's own underside is one half-section below its axis, exactly as a
    stub's box is, so the lane and the reservoir line crossing it come out on one plane.

    IT IS WHAT BOTH UNIONS ARE STOOD ON, or the least of it: the west line cruises this plane the
    whole way aft and the east line comes down its union's column onto it, so neither has a storey
    to find at the end. What the unions actually take is `enclosure_assembly.nozzle_storey`, which
    carries this plane up to whatever passes their barrels over the pump's bracket.

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
    stub that shares its column. So the run climbs what that stub leaves, comes about onto its
    UNION'S OWN COLUMN in one jog, and holds that column the rest of the way — the cold core's
    whole length, the panel deck, and into the collet on the collet's own axis.

    IT CROSSES ONCE AND THE CROSSING IS A MILLIMETRE. Gate and union stand one millimetre apart
    across the machine, so there is no lane to take and nothing to come back from: the run is on
    its final column before the cold core's front face, and every station aft of `GATE_B_JOG_Y`
    reads the same X.

    WHAT IT LEAVES BEHIND IS THE WEST FLANK. The tap-water lane stands outboard of this column —
    the split's cap reaches x −85.1 and the wall's own cluster wells are outboard of that — and
    none of it is under this tube. The one thing this run puts in that strip is the rib that
    holds it, and `GATE_B_STEP_Y` stands that rib in the daylight between the two.

    THE STEP UP IS TAKEN LAST. The union stands a storey over the plane the gate climbs to,
    because `enclosure_assembly.nozzle_storey` carries both barrels over the pump's bracket — so
    the run cruises the gate's own plane the whole way aft and spends the rise in one short lean
    behind the drip tray, where nothing is over it."""
    gate = F["valve-v-j"].at("outlet")
    tin = F["bulkhead-flavor-b"].at("tube-in")
    climb = _gate_climb_under_cruise(F)
    return R.bent(
        "fluid-28", "valve-v-j.outlet",
        (gate[0], gate[1], climb),                          # up what the reservoir stub leaves
        (tin[0], GATE_B_JOG_Y, climb),                      # the one jog, onto the union's column
        (tin[0], GATE_B_STEP_Y, climb),                     # the cold core's whole length, one column
        (tin[0], GATE_B_STEP_Y + GATE_B_RISE_RUN, tin[2]),  # one lean onto the union's own storey
        "bulkhead-flavor-b.tube-in",                        # and straight aft into the collet
        kind="fluid", bend=TUBE_BEND,
        note="nozzle B: V-J-O → rear union, up the gate's own bay and one jog onto the union's "
             "own column, held to the wall")


def _fluid_18(F, solids):
    """fluid-18 — the nozzle-A gate to its rear union, and the line the manifold sends out of the
    machine on the EAST side.

    IT CLIMBS ITS OWN BAY. Its union stands in the WEST pair, so where `fluid-28` closes on a
    column three fittings away this one has the machine to cross, and the column it crosses from is
    V-G's own: `fluid-14` crosses that column a storey higher than the stub and nothing else fences
    it, so the bay stands open the whole way to the crown. The east outboard strip is the board's —
    `pcba` and `relay-1` hang on the +X wall's seat and take it from y 232 aft.

    THEN IT IS ON ONE STOREY THE WHOLE WAY. One diagonal west and aft puts it on `fluid-14`'s own
    column over the cold core's crown, and the plane it arrives on is the plane it crosses on —
    the strip that carries it aft under the bowl and the strip that carries it west over the
    manifold's own crossings are the same daylight, so nothing between them is a lean.

    IT PASSES OVER `fluid-14` FOR THE WHOLE OF THAT LANE. The fill line holds its own high lane
    across the core's front and falls onto the cap behind it, so the tallest of it stands a
    section and more below this run, and the two share the column with a storey between them.

    IT CROSSES FORE OF THE PUMP AND FALLS BEHIND IT — west onto its union's column, and then down
    that column to the union's storey, forward of the drip tray, which takes the same column from
    its own front rim aft."""
    gate = F["valve-v-g"].at("outlet")
    tin = F["bulkhead-flavor-a"].at("tube-in")
    lane_x = F["foam-assembly"].at("reservoir-a")[0]
    deck_y = _gate_a_deck_y(solids)
    return R.bent(
        "fluid-18", "valve-v-g.outlet",
        (gate[0], gate[1], GATE_A_CROSS_Z),               # up the bay nothing fences, to the storey
        (lane_x, GATE_LANE_Y, GATE_A_CROSS_Z),            # one diagonal west and aft onto the crown lane
        (lane_x, deck_y, GATE_A_CROSS_Z),                 # aft over `fluid-14`, under the bowl
        (tin[0], deck_y, GATE_A_CROSS_Z),                 # west across the machine, fore of the pump
        (tin[0], GATE_A_FALL_Y, tin[2]),                  # down the column onto the union's storey
        "bulkhead-flavor-a.tube-in",                      # and straight aft into the collet
        kind="fluid", bend=TUBE_BEND,
        note="nozzle A: V-G-O → rear union, up the gate's own bay onto the crown lane over "
             "`fluid-14`, and west across the machine fore of the pump on that same storey and "
             "down its union's own column")


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
# THE LANE `fluid-14` CROSSES THE VALVE DECK IN: the daylight between V-K standing on the cap and
# channel A's own V-A beside it. Both bodies are round where the lane is narrowest and their boxes
# stand well inside their own metal, so the lane is swept —
#
#     w.cast((43.5, 244.0, 268.575), (0, -1, 0), dia=6.35)
#
# — which runs from V-K's aft face forward to `fluid-16`'s own riser, and stops on V-K or on V-A
# at every column either side of it. It reads 1.71 mm to V-A and 2.25 to V-K, against 1.38 and
# 1.53 for the same lane one storey up.
#
# `FILL_A_LANE_Z` is the storey the run ENTERS on and nearly all it uses it for is `fluid-16`:
# that line leans away from the draw bore at z 281.315 across this column, and the crossing is
# held over it. What the run comes down through is V-A's forward end.
FILL_A_LANE_Z = 289.0
# How long the run holds that storey before it falls — one stock radius, of which the corner off
# the diagonal and the corner into the fall take 11.2 between them. What is left is the only
# straight between those two bends. Re-read the fall's room by sweeping the two waypoints that
# carry it —
#
#     tools/cad-venv/bin/python hardware/scripts/probe.py reroute fluid-14 3-4 y- 0:6:0.5
#
# — clear to 2.5 mm forward of here, then that corner starves and `fluid-16` arrives a few
# millimetres behind it. The rib holding this run stands in the cap's own frame and does not
# follow the fall: `_cold_core_interface.cap_anchors["fluid-14"]`.
FILL_A_LANE_RUN = TUBE_BEND
# How much depth the fall onto the cap takes. Both its corners spend `TUBE_BEND` as tangent, so
# what reaches the cap's plane is the fall plus those two arcs.
FILL_A_FALL_RUN = 10.0


def _fill_a_lane_y(solids) -> float:
    """Where the run comes about onto the lane — one clear section forward of V-K's own face,
    so the diagonal off the gate is on the lane's column before it reaches the valve it passes."""
    return solids["vk-solenoid"].BoundingBox().ymin - _split.TUBE_D - LANE_CLEAR


def _fill_a_cap_z(solids) -> float:
    """The plane the run holds over the cap: one `LANE_CLEAR` over the pump's own foot pad.

    THE LANE IS THE PUMP'S BRACKET AND NOT THE LID. West of the SeaFlo's barrel its foot pad is
    what the run passes over, `seaflo_22_pump.FOOT_T` up from the face both of them stand on, and
    the pad reaches further west than anything else the pocket carries."""
    return (solids["seaflo-pump"].BoundingBox().zmin + _pump.FOOT_T
            + _split.TUBE_D / 2.0 + LANE_CLEAR)


def _fill_a_turn_y(F) -> float:
    """Where it leaves the cap's plane for the bore's own column — aft of the tap-water riser.

    `water-7` crosses this lane on the pump's suction barb in 3/8" braided, the fattest stock the
    machine carries. The run holds the lane past that hose and leans east only behind it."""
    return F["seaflo-pump"].at("suction")[1] + (_suct.HOSE_OD + _split.TUBE_D) / 2.0 + LANE_CLEAR


def _fluid_14(F, solids):
    """fluid-14 — the channel-A fill gate to the bore in reservoir A's own cap.

    RESERVOIR A IS THE AFT POCKET AND THE PUMP STANDS ON IT. The SeaFlo takes the middle of A's
    cap and the power brick the far side, and what they leave is the strip between them — which
    is where the bore is. So this run has the machine's whole depth to cross, and it crosses ON
    THE CAP: up off the gate onto `FILL_A_LANE_Z`, one diagonal aft and inboard into the lane V-K
    and V-A leave between them, one stock radius of that storey to clear `fluid-16`, one fall
    onto `_fill_a_cap_z` at V-A's forward end, aft down the lane and over the pump's own bracket,
    one lean east onto the bore's column behind the tap-water riser, and down the strip into it.

    IT IS ON THE CAP'S PLANE FOR EVERYTHING PAST V-A'S FIRST 20 MM. The storey it enters on is
    `fluid-16`'s: that line leans away from the draw bore across this column and the crossing is
    held over it. Past that lean the lane between the two valves is open right down to the
    bracket, and reads wider there than it does one storey up.

    ITS COLUMN IS THE DRAW BORE'S OWN. `fluid-16` rises off `reservoir-a` and leans away forward;
    the fill runs aft on that same column and crosses over its own channel's draw where it stands.

    THE RIB IT LIES IN IS THE CAP'S, and it stands where the low leg begins — behind the valve
    cradles, on the station that splits the run's two spans evenly."""
    gate = F["valve-v-f"].at("outlet")
    bore = F["foam-assembly"].at("reservoir-a-fill")
    lane_x = F["foam-assembly"].at("reservoir-a")[0]
    fall = _fill_a_lane_y(solids) + FILL_A_LANE_RUN
    cap = _fill_a_cap_z(solids)
    return R.bent(
        "fluid-14", "valve-v-f.outlet",
        (gate[0], gate[1], FILL_A_LANE_Z),                  # up onto the storey `fluid-16` sets
        (lane_x, _fill_a_lane_y(solids), FILL_A_LANE_Z),    # one diagonal aft and inboard, onto the lane
        (lane_x, fall, FILL_A_LANE_Z),                      # one stock radius of it, over that lean
        (lane_x, fall + FILL_A_FALL_RUN, cap),              # one fall onto the cap's own plane
        (lane_x, _fill_a_turn_y(F), cap),                   # aft down the lane and over the bracket
        (bore[0], bore[1], cap),                            # one lean east onto the bore's column
        "foam-assembly.reservoir-a-fill",                   # and straight down the strip into it
        kind="fluid", bend=TUBE_BEND, skew=(R.COLLET_SKEW, CAP_BORE_SKEW),
        note="reservoir A fill: V-F-O → the fill bore in its own cap, over `fluid-16`'s lean and "
             "straight down onto the cap, then the whole way aft in the lane V-K and V-A leave "
             "and over the pump's bracket to the bore's own column")


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
    and draw no tube. This one cannot be: the suction stands on the shell's WEST tangent, which
    looks at the side wall and at no neighbour at all, and the core stands a lane behind the can
    besides. So this leg is cut and brazed like any other run — out into the west lane, then one
    long diagonal aft and back inboard, past the shell's own shoulder and down into the core's
    outlet slot."""
    return R.bent(
        "refrig-3", "compressor.refrig-suction", "foam-assembly.evap-outlet",
        kind="refrigerant", bend=CU_BEND, lead=CU_LEAD,
        note="sealed loop: evaporator outlet → compressor suction, the one leg of the three "
             "that is drawn rather than made across a shared plane")


def _refrig_1(F):
    """refrig-1 — the compressor's discharge into the condenser's intake, in copper.

    BOTH MOUTHS FACE EACH OTHER ON ONE LINE. The can's discharge stub stands on its own +X
    tangent and the block's header is re-dressed to that stub's column and plane, so what
    crosses the lane the block's slide east opens is one length of tube."""
    return R.bent(
        "refrig-1", "compressor.refrig-discharge", "condenser+fan.refrig-inlet",
        kind="refrigerant",
        note="sealed loop: compressor discharge → condenser inlet, one straight across the lane")


def _refrig_2(F):
    """refrig-2 — the condenser's liquid line into the evaporator's inlet, in copper.

    BOTH MOUTHS FACE EACH OTHER ON ONE LINE. The block's own header is re-dressed to the core's
    evaporator-inlet station — same column, same plane — so what crosses the lane between them is
    one length of tube with nothing to turn around. The drier stands inside the block's own
    envelope, and what leaves it is this."""
    return R.bent(
        "refrig-2", "condenser+fan.refrig-outlet", "foam-assembly.evap-inlet",
        kind="refrigerant",
        note="sealed loop: condenser outlet → evaporator inlet, one straight across the lane")


def authored() -> frozenset:
    """The connection ids this module draws a run for, without building one. `enclosure_assembly`
    reads it before the pack is assembled, to know which of the manifold's placeholder mouth stubs
    a real line has replaced."""
    return frozenset(_AUTHORED)


# The ids `build_runs` can produce. One name per `_*` author below, and the guard each is behind
# only decides whether the bodies to draw it are placed yet.
_AUTHORED = ("water-7", "water-6", "water-5", "water-2", "fluid-1", "water-4", "water-3",
             "co2-0", "co2-1", "co2-2", "fluid-2", "fluid-4", "carb-1", "carb-2", "fluid-28",
             "fluid-18", "fluid-24", "fluid-26", "fluid-14", "fluid-16", "refrig-3",
             "refrig-2", "refrig-1")


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
