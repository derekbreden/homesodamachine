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
           _hw / "reference" / "seaflo-suction-chain"):
    sys.path.insert(0, str(_p))
import _routing as R                                   # noqa: E402
import seaflo_22_pump as _pump                         # noqa: E402
import seaflo_suction_chain as _suct                   # noqa: E402

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
    return runs


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
