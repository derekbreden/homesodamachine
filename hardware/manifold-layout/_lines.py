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
           _hw / "reference" / "wr1110-regulator"):
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
import gasher_check_valve as _gasher                    # noqa: E402
import wr1110_regulator as _wr1110                      # noqa: E402

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
