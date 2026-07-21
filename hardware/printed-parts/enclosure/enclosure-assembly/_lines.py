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
    are straight tube, ~10 mm each, no bends. Each tee's branch is then rolled about the
    run (`JUNCTION_ROLL`) to aim at its pump inlet, and fluid-11/21 carry the suction from
    the branch collets east to the pump row.

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
# 1/4" LLDPE, drawn as the soft tube it is.
LLDPE = cq.Color(0.90, 0.90, 0.94)
# How far off a divider/elbow collet's axis a pump-discharge run may enter as one straight length
# of soft LLDPE — the flex a push-to-connect collet takes, past the copper loop's COLLET_SKEW.
# The aimed poses (_contents `_solve_discharge`) leave a few degrees of residual the tube absorbs;
# y-g, boxed in over pump-b, is the tightest at ~9°.
DISCHARGE_SKEW = 22.0

# Connections the pack does not carry as it stands, each with the measurement that blocks it.
# They stay counted against the `routed` axis.
BLOCKED: dict = {}


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

    # The pump-discharge runs — each flavor's bag + nozzle legs meet at its two-way divider. The
    # netlist is DIAGONAL (a flavor's two valves sit on opposite tray rows), so the two long legs
    # cross the row. Each turn-elbow aims its free leg at the outlet it feeds (_contents
    # `elbow_free_dir`), so a run leaves nearly along its collet: fluid-27 is one straight tube into
    # its outlet; fluid-13 bends once into y-d's yawed outlet; the two long crossing legs (17, 23)
    # leave climbing (the elbow's lift) and are carried OVER the near flavor's fitting by one
    # hand-placed apex, then down — a gentle arc, authored point-to-point with `bent`. Each takes a
    # `lead=` stub, so it leaves and enters straight along its collet (skew ~0 by construction) and
    # only the apex is hand-placed, then rounds at the DBEND radius. The divider stems to the pumps
    # (segments 12/22) leave below, from each divider's own stem port.
    LEAD = 8.0                              # exit/approach stub: straight lead-out/-in along each collet
    DBEND = 12.0                            # 1/4" LLDPE, clean-sweeping radius (as the copper loop uses)
    for cid, elb, div, port, apex, lead in (
        ("fluid-13", "elbow-bag-y-d", "y-d", "Y-D-2", None,                   (0.0, 4.0)),  # one bend into the yawed outlet
        ("fluid-17", "elbow-y-g",     "y-d", "Y-D-3", (202.0, 111.0, 259.0),  LEAD),        # over elbow-y-d (top z254)
        ("fluid-23", "elbow-bag-y-g", "y-g", "Y-G-2", (200.0, 112.0, 289.0),  LEAD),        # over elbow-bag-y-d (top z286)
        ("fluid-27", "elbow-y-d",     "y-g", "Y-G-3", None,                   None),         # rises straight to the raised outlet
    ):
        mids = [apex] if apex is not None else []
        runs.append(R.bent(cid, f"{elb}.free", *mids, f"{div}.{port}",
                            kind="fluid", bend=DBEND, skew=DISCHARGE_SKEW, lead=lead,
                            note=f"discharge {port}: {elb} → {div} {port}, bent over the row"))

    # The pump-discharge stems (segments 12/22) — each divider's stem back to a pump outlet.
    # pump-b's outlet elbow and y-d's yawed stem face each other, so fluid-12 is a single bend where
    # their collet axes meet. fluid-22 leaves pump A's east-facing outlet, crosses the open band over
    # the pumps, and turns into y-g's stem; the two sit in separate bays.
    op, od = contents.pump_outlet_pose("pump-b")
    sp, sd = contents.divider_port("y-d", 1)
    runs.append(R.bent("fluid-12", "pump-b.P-B-O", R.meet(op, od, sp, sd, 0.85), "y-d.Y-D-1",
                        kind="fluid", bend=6.0, skew=DISCHARGE_SKEW,
                        note="discharge stem P-B-O → y-d Y-D-1, where the two collets meet"))
    runs.append(R.bent("fluid-22", "pump-a.P-A-O", (165.0, 25.0, 278.0), "y-g.Y-G-1",
                        kind="fluid", bend=12.0, skew=DISCHARGE_SKEW, lead=14.0,
                        note="discharge stem P-A-O → y-g Y-G-1, across the pump row"))

    # The pump-suction stems (segments 11/21) — each pump's inlet back to its channel's junction
    # tee. The tees hang in the manifold seam between the source and bag trays; each branch is
    # rolled forward, off the pump row (_contents `JUNCTION_ROLL`), so each run leaves its collet
    # heading −Y and picks up its `lead=` stub there. fluid-11 climbs out of tee-y-c behind pump
    # A's west motor barrel, drapes east over the pump bodies — below the row's elbows, ahead of
    # the bag tray — and drops into pump B's far inlet, rolled northwest to meet it
    # (`PUMP_INLET_AIM`). fluid-21 comes forward-low under the bag tray out of the buried tee-y-f,
    # then rises up pump A's aft into its near inlet, which keeps its west face. tee-y-f is
    # sandwiched in the source/bag tray seam, so this leg grazes the trays at the exit (reported).
    SLEAD = 12.0                        # exit/approach stub: straight lead off each suction collet
    runs.append(R.bent(
        "fluid-11", "tee-y-c.Y-C-3",
        (12.0, 83.0, 260.0), (50.0, 60.0, 271.0), (98.0, 57.0, 278.0), (146.0, 70.0, 279.0), (186.0, 84.0, 280.0), (213.0, 87.0, 278.0),
        "pump-b.P-B-I",
        kind="fluid", bend=9.0, skew=DISCHARGE_SKEW, lead=SLEAD,
        note="suction stem tee-y-c Y-C-3 → pump-b P-B-I, forward off the tee then over the pump row"))
    runs.append(R.bent(
        "fluid-21", "tee-y-f.Y-F-3",
        (52.0, 96.0, 224.0), (82.0, 92.0, 261.0),
        "pump-a.P-A-I",
        kind="fluid", bend=10.0, skew=DISCHARGE_SKEW, lead=SLEAD,
        note="suction stem tee-y-f Y-F-3 → pump-a P-A-I, forward-low then up the aft"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)} — copper for the refrigerant loop,
    white LLDPE for the fluid (flavor) runs."""
    return {r.id: (R.tube(r), LLDPE if r.kind == "fluid" else COPPER) for r in build_runs()}


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
    """Each run's tightest gap to a part it does not terminate on, or to another run. The two
    components a run joins are skipped. Reported, not gated."""
    import scorecard

    tubes = {r.id: R.tube(r) for r in build_runs()}
    out = []
    for r in build_runs():
        t = tubes[r.id]
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        gaps = [(scorecard._solid_gap(t, s), n) for n, s in solids.items() if n not in ends]
        gaps += [(scorecard._solid_gap(t, tubes[o]), o) for o in tubes if o != r.id]
        out.append((r, min(gaps) if gaps else None))
    return out
