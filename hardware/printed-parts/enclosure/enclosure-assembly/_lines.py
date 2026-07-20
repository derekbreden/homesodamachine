"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the sealed refrigerant loop (`scorecard.REFRIGERANT_SEGMENTS`) — the discharge and
liquid legs authored, the suction leg unauthored — and the manifold's junction column, fully
joined: both trays' west collets into the union tees hanging between them. Three corridors
carry the authored legs, each measured off the faces that bound it:

  * the machine corridor — 49 mm, compressor back face to cold-core front face — with the
    valve-manifold tray stack in its upper band (z 164.8–296.1). The stack's tall walls back
    on the foam face at the valve rows, but its central span stops at y 155.3, so a window
    stands open off the cold-core face at the evaporator ports; below the stack's floor the
    corridor is open across its whole width. refrig-2 crosses at the floor.
  * the condenser channel — 21 mm, compressor +X face to condenser −X face, one lane wide.
    refrig-1 crosses at the discharge's height and climbs the tipped block's flank to the
    back-top inlet; refrig-2 leaves the front-bottom outlet along the channel floor — the two
    share the lane plane 69 mm apart in z.
  * the junction column — the open air off the trays' west ends, outboard of the west valve
    banks: the source tray's pair pointing up from below, the inverted bag tray's pointing
    down from above, ~60 mm apart, and the pump-inlet union tees (`tee-y-c`, `tee-y-f`)
    hanging between them on the line the collets make. Each elbow is rolled off its port
    axis to aim along that line (bag_circuit_tray `_junction_aim`), which leans ~11.6° off
    Z, so all four legs — fluid-9/19 down from the source, fluid-10/20 up from the bag —
    are straight tube, ~10 mm each, no bends. Segments 11/21 leave the branch collets east
    for the pump row, unauthored.

Precedent: `pcba.tsx`'s `route(...)` call sites.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parent))

import _contents as contents
import _routing as R
from _routing import route

# 1/4" ACR copper, drawn as the metal it is.
COPPER = cq.Color(0.72, 0.45, 0.20)

# Connections the pack does not carry as it stands, each with the measurement that blocks it.
# They stay counted against the `routed` axis.
BLOCKED: dict = {
    "fluid-23": "dropped bag-B elbow → Y-G-2: the elbow's −Z-tilted free port and the ~3 mm "
                "x-offset to the outlet need two sub-bend-radius legs at once; waits on the "
                "y-g divider pose (nudge east clears the x-offset but crowds the gate tray).",
}


def _frames():
    """A frame per placed component: its body box from the pack, its ports from the scorecard's
    port table."""
    import scorecard                                   # deferred: scorecard reads this module back

    placed = contents.build()
    by_comp: dict = {}
    for p in scorecard.PORTS:
        if p.pos is not None and p.face and p.component in placed:
            by_comp.setdefault(p.component, {})[p.name] = (p.pos, p.face, p.diam)
    return {n: R.frame(n, placed[n][0], by_comp.get(n, {})) for n in placed}


def build_runs() -> list:
    """The authored runs. Each waypoint is a port offset, a body face, or a bend-radius reach."""
    f = _frames()
    cond, foam = f["condenser+fan"], f["foam-assembly"]
    bend = R.BEND_RATIO * 6.35                              # 1/4" ACR copper, the loop's line

    # Each lane sits one bend radius off the face its ports turn away from.
    slot = cond.bb.xmin - bend

    runs = []

    # refrig-1 — hot gas off the compressor's back face onto the corridor lane, across to the
    # condenser channel, aft along the tipped block's flank, up into the inlet at the
    # condenser's back-top.
    runs.append(route(
        "refrig-1", "compressor-shroud.refrig-discharge",
        {"x": slot},                                        # across into the condenser channel
        cond.y("refrig-inlet"),                             # aft to the inlet's station
        cond.z("refrig-inlet"),                             # up the channel to its height
        "condenser+fan.refrig-inlet",
        note="hot gas: compressor → condenser"))

    # refrig-2 — liquid line off the tipped condenser's front-bottom outlet (the donor drier +
    # cap tube ride this leg, inside the harvested block): along the channel floor, aft to the
    # corridor's approach lane, across the machine at the floor — 70 mm under refrig-1's channel
    # crossing — then up the cold-core face into the evaporator inlet at its station.
    runs.append(route(
        "refrig-2", "condenser+fan.refrig-outlet",
        foam.y("evap-inlet", -bend),                        # aft: one bend off the cold-core face
        foam.x("evap-inlet"),                               # across the machine at the floor
        foam.z("evap-inlet"),                               # up the cold-core face to the inlet
        "foam-assembly.evap-inlet",
        note="liquid: condenser (drier + cap tube) → evaporator"))

    # refrig-3 — the suction leg, unauthored. Its corridor stands open: the source-select
    # tray's central span stops at y 155.3 over the outlet's x, leaving ~27 mm off the
    # cold-core face at the outlet's own height, and the drop from there to the floor lane is
    # clear the whole way down past the stack. The floor lane is refrig-2's, so the two want
    # separating in y before this one is drawn.

    # The junction column's four legs — fluid-9/19 down from the source bank, fluid-10/20 up
    # from the bag bank — are one shape. Each elbow is rolled to aim along the column and the
    # tee stands on the line its two collets make (_contents `junction`), so the leg is the
    # straight between them: no constraint, no stub, no bend, ~1.8° of collet skew at each
    # end.
    for cid, frm, to, ch in (
        ("fluid-9",  "source-select-assembly.V-C-O", "tee-y-c.Y-C-1", "A source"),
        ("fluid-19", "source-select-assembly.V-D-O", "tee-y-f.Y-F-1", "B source"),
        ("fluid-10", "bag-circuit-assembly.V-E-O",   "tee-y-c.Y-C-2", "A bag return"),
        ("fluid-20", "bag-circuit-assembly.V-H-O",   "tee-y-f.Y-F-2", "B bag return"),
    ):
        runs.append(route(cid, frm, to, kind="fluid", stub=0.0,
                          note=f"channel {ch}: collet to tee, straight down the junction column"))

    # The pump-discharge runs — each turn-elbow's free collet down into its divider outlet. A
    # flavor's bag and nozzle legs meet at its divider (diagonal netlist): a short near leg and a
    # longer cross-row leg over the pump. The x/z constraints set the lane; each run closes in y
    # into the +Y-facing outlet. Tight radii (R4) — these are short jumpers in the open air over
    # the pumps, a starting point that relaxes as the divider spots settle. The stems to the pumps
    # (segments 12/22) stay unauthored. fluid-23 (dropped bag-B elbow → Y-G-2) is deferred: its
    # −Z-tilted exit plus the small x-offset need two sub-radius legs the orthogonal router can't
    # place at this spacing — it waits on the divider pose (see BLOCKED).
    for cid, elb, div, port in (
        ("fluid-13", "elbow-bag-y-d", f["y-d"], "Y-D-2"),
        ("fluid-17", "elbow-y-g",     f["y-d"], "Y-D-3"),
        ("fluid-27", "elbow-y-d",     f["y-g"], "Y-G-3"),
    ):
        runs.append(route(cid, f"{elb}.free", div.x(port), div.z(port), f"{div.name}.{port}",
                          kind="fluid", bend=4.0, stub=4.0,
                          note=f"discharge {port}: {elb} free → divider outlet"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)}."""
    return {r.id: (R.tube(r), COPPER) for r in build_runs()}


# A run whose id is not itself a connection, because an in-line fitting splits it: a union
# tee's RUN ports face each other down one straight path, so two segments butted into them
# can be one piece of authored geometry answering for both on the routed axis. Empty — every
# authored run is one connection; the union tees are placed components whose collets anchor
# their segments separately.
CARRIES: dict = {}


def routed_ids() -> set:
    """The connection ids with a built path — what the scorecard's `routed` axis counts."""
    return {c for r in build_runs() for c in CARRIES.get(r.id, (r.id,))}


def clearances(solids: dict) -> list:
    """Each run's tightest gap to a part it does not terminate on. The two components a run
    joins are skipped. Reported, not gated."""
    import scorecard

    out = []
    for r in build_runs():
        t = R.tube(r)
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        gaps = sorted((scorecard._solid_gap(t, s), n) for n, s in solids.items() if n not in ends)
        out.append((r, gaps[0] if gaps else None))
    return out
