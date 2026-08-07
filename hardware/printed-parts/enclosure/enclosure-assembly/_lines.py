"""The tube between the placed bodies — every connection `fluid-topology.md`, the wiring
schedule and the four declared segment tables name, drawn port to port in the pack's own
coordinates.

Two kinds of line meet here.

The MANIFOLD'S OWN twenty-one segments are drawn by
[`manifold_layout`](/hardware/manifold-layout/manifold_layout.py), in the study's frame, and
carried into the machine on `_contents.manifold_seat()` — the same seat the valves and tees
ride. Fifteen of them are BUTTS: two collet faces meeting, tube in both quick-connects and none
between them, so no solid is drawn. The other six are the fold's four spine turns and the pair
of reservoir crossings, plus the six quarter turns and two steps the study's own mouths leave on.

Everything else is AUTHORED here, against the stations `_contents` publishes — the tap-water
sequence down the west lane, the carb riser, the refrigerant loop, and the two nozzle outlets.
[`_routing.py`](_routing.py) is the vocabulary: `route` for an orthogonal path through
one-dimensional constraints, `bent` for hand-placed waypoints, and the lean solvers below for
two mouths that have to meet off-axis.

Lines, not components: outside the component registry and its gates. They are drawn to the
pack's own stations, so a dragged body's runs follow it.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "manifold-layout"):
    sys.path.insert(0, str(_p))
import _boxes                                          # noqa: E402
import _contents as contents                           # noqa: E402
import _routing as R                                   # noqa: E402
from _routing import route, bent                       # noqa: E402

# 1/4" ACR copper, drawn as the metal it is.
COPPER = cq.Color(0.72, 0.45, 0.20)
# 1/4" LLDPE, drawn as the soft tube it is.
LLDPE = cq.Color(0.90, 0.90, 0.94)
# 3/8" braided PVC, the two hoses between the pump's barbs and its chains.
HOSE = cq.Color(0.86, 0.86, 0.80)

# Connections the pack does not carry as it stands, each with the measurement that blocks it —
# `_routing.BLOCKED` itself, filled as the runs below are drawn. They stay counted against the
# `routed` axis.
BLOCKED = R.BLOCKED

# The radius a 1/4" LLDPE run turns at when nothing else is said. DEFINED in `_contents`
# because a POSE depends on it and not only a path.
WBEND = contents.LLDPE_BEND
FLAVOR_SKEW = contents.FLAVOR_SKEW
CAP_BORE_SKEW = contents.CAP_BORE_SKEW
CLIMB_HUG = contents.LINE_HUG
LINE_PITCH = contents.LINE_PITCH
LINE_STEP = contents.LINE_STEP


def _ml():
    import manifold_layout
    return manifold_layout


def _frames():
    """A frame per placed component, per through-wall panel body, and the hopper funnel: its body
    box from the pack, its ports from the scorecard's port table."""
    import scorecard                                   # deferred: scorecard reads this module back

    placed = {**contents.build(), **contents.panel_bodies(),
              "hopper-funnel": (contents.placed_funnel(), None)}
    by_comp: dict = {}
    for p in scorecard.PORTS:
        if p.pos is not None and p.face and p.component in placed:
            by_comp.setdefault(p.component, {})[p.name] = (p.pos, p.face, p.diam)
    return {n: R.frame(n, placed[n][0], by_comp.get(n, {})) for n in placed}


# --- The manifold's own twenty-one ------------------------------------------
# `manifold_layout.SEGMENTS` says how each is made. A BUTT carries no tube outside its two
# collets and so no solid; the rest come over as the study drew them.

def manifold_segments() -> dict:
    """`{connection id: how it is made}` for every segment inside the manifold."""
    return {f"fluid-{cid}": how for cid, _f, _t, how in _ml().SEGMENTS}


def manifold_tubes() -> dict:
    """The study's own tube in the machine's coordinates: `{name: (solid, colour)}`.

    Named as the study names them — `tube-fluid-9`, `turn-fluid-3`, `step-fluid-5`,
    `stub-fluid-18` — so a segment drawn in more than one piece reads as the pieces it is."""
    seat = contents.manifold_seat()
    return {n: (own.then(seat).solid(s), LLDPE)
            for n, (s, own, _c) in _ml().posed_tubes().items()}


# --- The authored runs ------------------------------------------------------

_RUNS: list | None = None


def build_runs() -> list:
    """The authored runs. Memoized for the life of the process."""
    global _RUNS
    if _RUNS is None:
        _RUNS = _authored_runs()
    return _RUNS


def _mouth(f, anchor):
    """An anchor string as `(frame, port)`, so a run states its ends once."""
    return R._anchor(anchor)


def _authored_runs() -> list:
    F = _frames()
    runs: list = []

    # --- The refrigerant loop. Three joints, and every one of them crosses a plane two bodies
    # already share, so each is a made-up union rather than a length of tube: the shroud's
    # discharge on the condenser's inlet, the condenser's liquid line on the evaporator's inlet,
    # the evaporator's outlet on the shroud's suction. Nothing is drawn between them.

    return runs


# --- What the pack carries ---------------------------------------------------

# A run whose id is not itself a connection, because an in-line fitting splits it.
CARRIES: dict = {}


def build() -> dict:
    """Every line in the machine: `{name: (solid, colour)}`."""
    out = dict(manifold_tubes())
    for r in build_runs():
        out[r.id] = (R.tube(r), COPPER if r.kind == "refrigerant" else LLDPE)
    return out


def routed_ids() -> set:
    """The connection ids with a built path — what the scorecard's `routed` axis counts."""
    ids = {c for c in manifold_segments() if c not in BLOCKED}
    ids |= {c for r in build_runs() if r.id not in BLOCKED
            for c in CARRIES.get(r.id, (r.id,))}
    return ids


def blocked_ids() -> dict:
    """Connection id → the measurement that blocks it."""
    out = {c: why for c in manifold_segments() if (why := BLOCKED.get(c))}
    out.update({c: why for r in build_runs() if (why := BLOCKED.get(r.id))
                for c in CARRIES.get(r.id, (r.id,))})
    return out


def clearances(solids: dict) -> list:
    """Each run's tightest gap to a part it does not terminate on, or to another run."""
    import scorecard

    PRUNE_SLOP = 1e-6                                   # mm; a box gap this much past best still queries
    runs = build_runs()
    tubes = {r.id: R.tube(r) for r in runs}
    boxes = {n: _boxes.boxed(s) for n, s in solids.items()}
    tube_boxes = {rid: _boxes.boxed(t) for rid, t in tubes.items()}

    out = []
    for r in runs:
        t, tb = tubes[r.id], tube_boxes[r.id]
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        cand = [(scorecard._bbox_gap(tb, boxes[n]), n, solids[n]) for n in solids if n not in ends]
        cand += [(scorecard._bbox_gap(tb, tube_boxes[o]), o, tubes[o]) for o in tubes if o != r.id]
        cand.sort(key=lambda c: c[0])
        best = None                                    # (exact gap, name) of the nearest so far
        for bgap, n, s in cand:
            if best is not None and bgap > best[0] + PRUNE_SLOP:
                break                                  # lower bound past best: no farther body can win
            g = scorecard._solid_gap(t, s)
            if best is None or (g, n) < best:
                best = (g, n)
        out.append((r, best))
    return out


def lane_stations() -> dict:
    """The figures the runs were built along, for the prose that describes them. Empty while the
    deck's runs are unauthored."""
    return {}
