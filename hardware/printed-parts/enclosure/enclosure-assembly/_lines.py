"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the sealed refrigerant loop (`scorecard.REFRIGERANT_SEGMENTS`) — the discharge and
liquid legs authored, the suction leg BLOCKED by the tray stack pressed to the cold core (see
BLOCKED) — and the manifold's junction column, fully joined: the source drops and the bag
returns into the hanging pump-inlet tees. Three corridors carry the authored legs, each
measured off the faces that bound it:

  * the machine corridor — 49 mm, compressor back face to cold-core front face — but the
    valve-manifold tray stack stands in its upper band (z 164.8–290.8, to 9.2 off the foam
    face); the corridor is open below the stack's floor. refrig-2 crosses it there, at the
    floor.
  * the condenser channel — 21 mm, compressor +X face to condenser −X face, one lane wide.
    refrig-1 crosses at the discharge's height and climbs the tipped block's flank to the
    back-top inlet; refrig-2 leaves the front-bottom outlet along the channel floor — the two
    share the lane plane 69 mm apart in z.
  * the junction column — the open air off the trays' west ends, outboard of the west valve
    banks at x 18.67, where both trays' west outlet collets align (the bag tray rides 29.7
    west of the stack centre for exactly this): the inverted source tray's pair hanging
    down above, the bag pair up below, 58.3 mm apart, and the pump-inlet union tees
    (`tee-y-c`, `tee-y-f`) hanging in-line between them, connected at both run ports.
    fluid-9/19 drop the source collets into the run-up ports, one coaxial stub each;
    fluid-10/20 rise from the bag collets into the run-down ports through a two-bend jog —
    the trays' port rows sit 19.6 mm apart in Y (source ±36.73, bag ±17.125 off the stack
    centre), closed inside the 16.1 mm rise, which is why these two legs run a tighter
    former (R7.9, ~1.24×OD — soft LLDPE, the jog the row offset demands) with 8 mm stubs.
    Segments 11/21 leave the branch collets east for the pump row, unauthored.

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
    "refrig-3": (
        "foam-assembly.evap-outlet → compressor-shroud.refrig-suction: the evap-outlet exits "
        "−Y at (141.5, 182, 191), inside the tray stack's band. The bag-circuit assembly, "
        "pressed with the stack to the cold core, reaches y 172.8 (aft walls; valves to 169.8, "
        "Tee branch to 172.7) across z 164.8–227.8, leaving 9.2 mm of free corridor off the "
        "cold-core face — less than the 12.7 mm exit stub — and every drop/cross window inside "
        "the band is occupied (valve port rows x 38.2–97.2 and 137.4–196.4, the Y-E branch at "
        "x 110.4–124.2 z 169–183, the bridge floor below). The leg waits on a chimney through "
        "the stack, a stack move, or an evap-outlet port move."),
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

    # refrig-3 — see BLOCKED: the tray stack pressed to the cold core owns the
    # evap-outlet's exit space.

    # fluid-9 / fluid-19 — the source drops: V-C-O and V-D-O hang down out of the inverted
    # west bank and butt the union tees' run-up collets, one tube stub each. Anchored
    # port-to-port with no constraints: each pair is coaxial by construction (_contents
    # hangs each tee on its collet's own x, y), so the path is the straight the stubs meet
    # in.
    for cid, frm, to, ch in (
        ("fluid-9",  "source-select-assembly.V-C-O", "tee-y-c.Y-C-1", "A"),
        ("fluid-19", "source-select-assembly.V-D-O", "tee-y-f.Y-F-1", "B"),
    ):
        runs.append(route(cid, frm, to, kind="fluid", stub=(1.0, 1.0),
                          note=f"channel {ch} source drop: down collet into the hanging tee"))

    # fluid-10 / fluid-20 — the bag returns: V-E-O and V-H-O rise into the tees' run-down
    # collets. The trays' port rows are 19.6 mm apart in Y, closed inside the 16.1 mm rise
    # as a two-bend jog: up one stub, across the offset, up into the port. The 8 mm stubs
    # and the R7.9 former (~1.24×OD, soft LLDPE) are what seat both bends in that rise —
    # the one place the row offset is absorbed.
    tees = {"fluid-10": f["tee-y-c"], "fluid-20": f["tee-y-f"]}
    for cid, frm, to, port, ch in (
        ("fluid-10", "bag-circuit-assembly.V-E-O", "tee-y-c.Y-C-2", "Y-C-2", "A"),
        ("fluid-20", "bag-circuit-assembly.V-H-O", "tee-y-f.Y-F-2", "Y-F-2", "B"),
    ):
        runs.append(route(
            cid, frm,
            tees[cid].y(port),                              # across the row offset
            to,
            kind="fluid", bend=7.9, stub=(8.0, 8.0),
            note=f"channel {ch} bag return: up collet into the hanging tee's run-down"))

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
