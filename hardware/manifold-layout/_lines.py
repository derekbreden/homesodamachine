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
           _hw / "reference" / "seaflo-22-pump",
           _hw / "reference" / "seaflo-suction-chain",
           _hw / "reference" / "asse1022-assembly",
           _hw / "reference" / "water-split",
           _hw / "reference" / "neofit-flow-control",
           _hw / "reference" / "beduan-solenoid"):
    sys.path.insert(0, str(_p))
import _routing as R                                   # noqa: E402
import asse1022_assembly as _asse                      # noqa: E402
import seaflo_22_pump as _pump                         # noqa: E402
import seaflo_suction_chain as _suct                   # noqa: E402
import beduan_solenoid as _beduan                      # noqa: E402
import neofit_flow_control as _flowreg                 # noqa: E402
import water_split as _split                           # noqa: E402

BLOCKED = R.BLOCKED

# The 3/8" reinforced PVC's own floor, and the coarsest stock on the machine: a corner it cannot
# hold is a corner nothing drawn here can.
HOSE_BEND = R.stock_min("water", _suct.HOSE_OD)
# How far off its own axis a hose may leave a BARB and still run unbent. A barb is a taper the
# hose stretches over and a clamp closes on, not a collet gripping a tube all round, so it takes
# a good deal more than `R.COLLET_SKEW`. Seeded, not ratified.
BARB_SKEW = 14.0

# Which reference module states each placed body's stations, and the bore each one carries. The
# module gives `(position, outward axis)` in the body's own frame; `front_half`'s `carry` takes
# that through the placement, so a port table is written once and rides every later move.
STATIONS = {
    "seaflo-pump": {"suction": (_pump.suction, _suct.HOSE_OD),
                    "discharge": (_pump.discharge, _suct.HOSE_OD)},
    "suction-chain": {"barb-tip": (_suct.barb_tip, _suct.HOSE_OD),
                      "tube-port": (_suct.tube_port, _suct.TUBE_D)},
    "asse1022-assembly": {"tube-in": (lambda: _asse.port("tube-in"), _split.TUBE_D),
                          "tube-out": (lambda: _asse.port("tube-out"), _split.TUBE_D),
                          "vent-tip": (lambda: _asse.port("vent-tip"), _asse.VENT_STUB_OD)},
    "vk-solenoid": {"inlet": (_beduan.inlet, _split.TUBE_D),
                    "outlet": (_beduan.outlet, _split.TUBE_D)},
    "flow-regulator": {"inlet": (_flowreg.inlet, _flowreg.TUBE_D),
                       "outlet": (_flowreg.outlet, _flowreg.TUBE_D)},
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
    if {"asse1022-assembly", "water-split"} <= set(F):
        runs.append(_water_2(F))
    if {"water-split", "flow-regulator"} <= set(F):
        runs.append(_fluid_1(F))
    if {"vk-solenoid", "suction-chain"} <= set(F):
        runs.append(_water_4(F))
    if {"water-split", "vk-solenoid"} <= set(F):
        runs.append(_water_3(F))
    return runs


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
