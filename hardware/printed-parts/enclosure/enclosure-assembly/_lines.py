"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the sealed refrigerant loop (`scorecard.REFRIGERANT_SEGMENTS`), binding the three placed
components — compressor, condenser, cold-core evaporator. Two corridors carry it, each measured
off the faces that bound it:

  * the machine corridor — 22 mm, compressor back face to cold-core front face.
  * the condenser channel — 21 mm, compressor +X face to condenser −X face.

A 1/4" line runs one bend radius of straight (12.7 mm) off a fitting before it turns, so each
corridor carries one lane and the legs sharing it are separated by height.

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
BLOCKED = {
    "refrig-2": (
        "condenser+fan.refrig-outlet → foam-assembly.evap-inlet needs a lateral jog in y. The "
        "outlet sits at y 145.5. The last corner before the evaporator inlet sits at y ≤ 142.30 "
        "(one bend radius off the cold core's front face) and y ≥ 137.18 (clear of the "
        "compressor's back face), putting the jog at 3.2–8.3 mm. A leg between two 90° corners "
        "is 2R = 25.4 mm; the jog closes at R ≤ 1.60 mm, or R ≤ 2.73 mm as a 45° offset pair. "
        "The condenser is a placeholder box and this outlet is a viewer pick on it; the outlet "
        "at y ≤ 111.8 clears the corridor lane by 2R."),
    "refrig-3": (
        "foam-assembly.evap-outlet → compressor-shroud.refrig-suction. The SeaFlo's back face "
        "(y 147) and the cold core's front face (y 155) leave an 8.0 mm strip; the evaporator "
        "outlet opens into it at z 191. A 1/4\" line turns 12.7 mm off the port, and the SeaFlo "
        "stands 8.0 mm off it. A Ø6.35 line centred in the strip clears each face by 0.83 mm, "
        "against a 1.0 mm floor."),
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
    comp, cond, foam = f["compressor-shroud"], f["condenser+fan"], f["foam-assembly"]
    bend = R.BEND_RATIO * 6.35                              # 1/4" ACR copper, the loop's line

    # Each lane sits one bend radius off the face its ports turn away from.
    lane = comp.bb.ymax + bend
    slot = cond.bb.xmin - bend

    runs = []

    # refrig-1 — hot gas off the compressor's back face onto the corridor lane, across to the
    # condenser channel, forward the length of the machine, up the channel into the inlet at the
    # condenser's top-front.
    runs.append(route(
        "refrig-1", "compressor-shroud.refrig-discharge",
        {"x": slot},                                        # across into the condenser channel
        cond.y("refrig-inlet"),                             # forward to the inlet's station
        cond.z("refrig-inlet"),                             # up the channel to its height
        "condenser+fan.refrig-inlet",
        note="hot gas: compressor → condenser"))

    # refrig-2, refrig-3 — see BLOCKED.

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)}."""
    return {r.id: (R.tube(r), COPPER) for r in build_runs()}


def routed_ids() -> set:
    """The connection ids with a built path — what the scorecard's `routed` axis counts."""
    return {r.id for r in build_runs()}


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
