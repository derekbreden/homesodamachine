"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the sealed refrigerant loop (`scorecard.REFRIGERANT_SEGMENTS`) — the discharge and
liquid legs authored, the suction leg BLOCKED by the tray stack pressed to the cold core (see
BLOCKED) — and the manifold's first tray-to-tray line, channel A's pump-inlet run. Three
corridors carry the authored legs, each measured off the faces that bound it:

  * the machine corridor — 49 mm, compressor back face to cold-core front face — but the
    valve-manifold tray stack stands in its upper band (z 157.8–283.8, to 9.2 off the foam
    face); the corridor is open below the stack's floor. refrig-2 crosses it there, at the
    floor.
  * the condenser channel — 21 mm, compressor +X face to condenser −X face, one lane wide.
    refrig-1 crosses at the discharge's height and climbs the tipped block's flank to the
    back-top inlet; refrig-2 leaves the front-bottom outlet along the channel floor — the two
    share the lane plane 69 mm apart in z.
  * the west manifold column — the open slot off the source-select tray's west end, outboard
    of its west valve bank. Both trays turn their channel-A pump-inlet collets up into it
    (V-E-O below, V-C-O above), and it is the only lane that climbs past the source-select
    tray's floor: straight above V-E-O the tray's own west bank closes to under a millimetre.
    fluid-9+10 rides it.

A 1/4" line runs one bend radius of straight (12.7 mm) off a fitting before it turns. The two
trays' port rows sit at different Y offsets from the shared stack centre (source ±36.73, bag
±17.125), so a run between them closes across 19.6 mm of Y — less than the 2R a leg between two
90° corners seats. Such a run parks its climb one bend diameter clear of the near row and takes
the offset on the long reach at the top.

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
        "Tee branch to 172.7) across z 157.8–220.8, leaving 9.2 mm of free corridor off the "
        "cold-core face — less than the 12.7 mm exit stub — and every drop/cross window inside "
        "the band is occupied (valve bodies x 67.9–126.9 and 167.1–226.1, the Y-E branch at "
        "x 140.1–153.9 z 162–176, the bridge floor below). The leg waits on a chimney through "
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
    src, bag = f["source-select-assembly"], f["bag-circuit-assembly"]
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

    # fluid-9+10 — channel A's pump-inlet run, the manifold's first line between the trays.
    # Both ends are up-facing collets on the west end of the stack: V-E-O on the bag tray
    # (bag A back to the pump) and V-C-O on the source-select tray above it (the shared
    # source). The Y-C union tee butts into this run in-line — its RUN ports are these two
    # segments' far ends, so the pair is one continuous 1/4" path and one authored line; the
    # tee's station along it, and its branch to P-A-I, are Tray 3's to pin.
    #
    # V-E-O turns up into a 29 mm pocket (the source-select tray's floor is its ceiling), so
    # the run crosses west under that floor to the open column outboard of the west valve
    # bank, and only climbs there. The turn parks one bend diameter aft of V-E-O's row: the
    # two rows are 19.6 mm apart in Y, under the 2R a leg between two corners seats, so the
    # Y offset is spent on the long reach forward at the top instead.
    park = 2.0 * bend + 2.0                                 # tangents, plus margin off the guard
    runs.append(route(
        "fluid-9+10", "bag-circuit-assembly.V-E-O",
        src.x("V-C-O"),                                     # west along the pocket to the column
        bag.y("V-E-O", park),                               # aft to the climb's station
        src.z("V-C-O", bend),                               # up the column, one bend over V-C-O
        "source-select-assembly.V-C-O",
        kind="fluid", note="channel A pump inlet: bag A + shared source → Y-C → P-A"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)}."""
    return {r.id: (R.tube(r), COPPER) for r in build_runs()}


# A run whose id is not itself a connection, because an in-line fitting splits it: a union
# tee's RUN ports face each other down one straight path, so the two segments butted into them
# are one piece of authored geometry. The run answers for both on the routed axis.
CARRIES: dict = {
    "fluid-9+10": ("fluid-9", "fluid-10"),                  # Y-C's run — V-C-O ↔ V-E-O
}


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
