"""The front half's requirements as a single pass/fail scorecard — the one place the
arrangement's rules are enumerated as executable checks, computed from the placed geometry the
pack already builds. Printed at the tail of every `front_half.py` run and written beside the
STEP as `front-half.scorecard.json`, which the 3D viewer's bottom bar reads
([`web/contracts/scorecard-sidecar.js`](/web/contracts/scorecard-sidecar.js)).

Two kinds of check:

  - GATE — a requirement that must hold for the machine as it stands to be built.
  - GOAL — the work this effort is converting, reported as a `score` (0..100) rather than a
           gate, so the pack still builds while it converts.

THE FOCUS IS `bend-radius`, AND THE AXIS BEHIND IT IS `routed`. A run arrives with the bodies
it joins, so the two read together: `routed` says how much of the machine's tube inventory is
drawn at all, and `bend-radius` says whether what is drawn turns at a radius its stock takes.
A corner short of that minimum is a tube nobody can build, and most corners are bound by where
their two ends STAND — so driving the gate is usually moving a body, not raising a number.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/front_half.py
"""
# The leading underscore is what `_lines.py` has: a private module of this pack, and the name
# `scorecard` on the import path already belongs to the retired enclosure assembly.

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = _hw.parent
for _p in (_hw / "scripts", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import _boxes                                          # noqa: E402
import _clearing                                       # noqa: E402
import _overlap                                        # noqa: E402
import _routing as R                                   # noqa: E402

_TOPOLOGY = _hw / "topology" / "fluid-topology.md"

# Grade bands on `radius ÷ the stock's minimum`. B is the requirement — a run AT its stock's
# floor is buildable and nothing more; A is the room that survives a part moving a millimetre.
GRADE_BANDS = ((1.5, "A"), (1.0, "B"), (0.75, "C"), (0.5, "D"), (0.0, "F"))
BEND_GRADE_PASS = "B"       # the worst grade a run may carry and still clear the gate
FOCUS_IDS = ("bend-radius", "routed")
DETAIL_MAX = 8
FOCUS_DETAIL_MAX = 24

# How close two bodies the machine does not seat against each other may stand.
CLEARANCE_FLOOR = 1.0
# Only pairs nearer than this are ranked, so the clearance detail reads as the tight end of the
# pack rather than as every pair in it.
REPORT_NEAR = 6.0
# The straight a run leaves a fitting on, as a multiple of the line's own bend radius: one reach
# for the stub and one for the tangent its first corner is seated on — `_routing.route`'s own
# two, and the shortest straight any turn off a port can be built in.
PORT_LEAD_BENDS = 2.0


def grade_of(ratio: float) -> str:
    return next(g for lo, g in GRADE_BANDS if ratio >= lo)


# The names a length of TUBE goes into the assembly under. `_lines.tubes` names each authored run
# `tube-<connection>`, and `manifold_layout` names the pack's own segments and the placeholder
# stubs off its free mouths the same way. Everything else the assembly carries is a body.
TUBE_PREFIXES = ("tube-", "turn-", "step-", "stub-")


def _placed(a) -> dict:
    """The assembly's children as world solids, by name."""
    import cadquery as cq
    return {c.name: (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation())) for c in a.children}


def _split_placed(a) -> tuple:
    """The placed world in the three populations the checks read it in: `(bodies, tubes,
    pieces)` — the machine's parts, the tube drawn between them, and the printed box."""
    bodies, tubes, pieces = {}, {}, {}
    for name, solid in _placed(a).items():
        target = (pieces if name.startswith("enclosure-")
                  else tubes if name.startswith(TUBE_PREFIXES) else bodies)
        target[name] = solid
    return bodies, tubes, pieces


# --- what the machine owes -------------------------------------------------
#
# The FLAVOR MANIFOLD's segments are `fluid-1` … `fluid-28` and they live in
# [`fluid-topology.md`](/hardware/topology/fluid-topology.md)'s own tables, read below.
# Everything upstream of the carbonator lives in no segment table — that doc starts at "Tap
# water source", which is the far end of the paths here — so the four below are declared,
# each against the procedure that builds it.

# The sealed loop the whole cold core exists to run, verified by disassembly in
# `reference/ice-maker/README.md` and built in `assembly/refrigerant-loop.md`. The drier and
# the capillary tube ride the condenser → evaporator leg.
REFRIGERANT_SEGMENTS = (
    ("refrig-1", "compressor-shroud discharge", "condenser+fan inlet"),
    ("refrig-2", "condenser+fan outlet (drier + cap tube)", "foam-assembly evaporator inlet"),
    ("refrig-3", "foam-assembly evaporator outlet", "compressor-shroud suction"),
)

# The tap water, from the rear-panel bulkhead through the backflow preventer, the split and the
# V-K fill/shutoff to the carbonator's own water inlet — `assembly/internal-plumbing.md` §2. All
# 1/4" LLDPE, stepping back up to 3/8" only at the SeaFlo's two moulded barbs. The ASSE 1022's
# vent is not here: it terminates to atmosphere over the drip pan.
#
# THERE IS NO `water-1`. The rear bulkhead's inboard collet and the ASSE chain's inlet collet
# meet face to face, so the first tube in the machine is a length of stock cut to the two grips
# and swallowed whole by them (`front_half.py`, the bulkhead block).
WATER_SEGMENTS = (
    ("water-2", "asse1022-assembly tube-out", "water-split supply"),
    ("water-3", "water-split to-vk", "vk-solenoid inlet"),
    ("water-4", "vk-solenoid outlet", "suction-chain tube-port"),
    ("water-5", "discharge-chain tube-port", "foam-assembly water-in"),
    ("water-6", "seaflo-pump discharge (3/8\" barb, moulded)", "discharge-chain barb-tip"),
    ("water-7", "seaflo-pump suction (3/8\" barb, moulded)", "suction-chain barb-tip"),
)

# The gas, from the back-panel DERPIPE through the GASHER check and the WR1110 secondary
# regulator to the carbonator's bottom-plate CO2 port — `assembly/internal-plumbing.md` §1. The
# DERPIPE → GASHER joint is a made-up 1/4" NPT thread and carries no line.
CO2_SEGMENTS = (
    ("co2-1", "gasher-co2 outlet", "wr1110 inlet"),
    ("co2-2", "wr1110 outlet", "foam-assembly co2-in"),
)

# The dispense leg — `P3 --> Faucet` in `fluid-topology-carbonator.mmd`, built in
# `assembly/internal-plumbing.md` §4. The DIGITEN turbine meter is a placed body with a collet
# at each end, so it splits the riser in two rather than being drawn on one run.
CARB_SEGMENTS = (
    ("carb-1", "foam-assembly carb-water-out", "digiten-flow inlet"),
    ("carb-2", "digiten-flow outlet", "bulkhead-carb tube-in"),
)


# --- what fastens each body ------------------------------------------------
#
# One row per body `front_half` seats, as `(component, by, held)`.
#
#   `by`   — the part whose PRINTED FEATURE fastens it. A boss a screw goes into, a socket a
#            thread makes up in. `None` is a joint still to design, and every `None` here is
#            one unit of the `mounted` axis's gap.
#   `held` — what holds it today, which is a different question. A body captured in a wall's
#            bore, resting on a crown, riding on rails or hanging off its own two collets is
#            HELD and is not MOUNTED: nothing about any of those survives the machine being
#            picked up by one corner.
#
# The manifold pack's own bodies are not here. `manifold_layout` arranges them on its own
# trays and hairpins, and this module seats that pack as one thing.
MOUNTS = (
    ("compressor-shroud", None, "floor"),
    ("condenser+fan", None, "floor"),
    ("foam-assembly", None, "floor"),
    ("seaflo-pump", None, "cap"),
    ("hopper-funnel", None, "wall-capture"),
    ("display", None, "wall-capture"),
    ("suction-chain", None, "none"),
    ("discharge-chain", None, "none"),
    ("psu", None, "cap"),
    ("pcba", None, "cap"),
    ("relay-1", None, "stack"),
    ("ac-hub", None, "stack"),
    ("ground-stack", None, "stack"),
    ("asse1022-assembly", None, "none"),
    ("drip-pan", None, "rails"),
    ("water-split", None, "tube-hung"),
    ("flow-regulator", None, "tube-hung"),
    ("vk-solenoid", None, "cap"),
    ("bulkhead-water", None, "wall-capture"),
    ("c14-inlet", "enclosure-back-top", "bosses"),
    ("co2-inlet", None, "wall-capture"),
    ("gasher-co2", None, "wall-capture"),
    ("wr1110", None, "none"),
    ("bulkhead-flavor-a", None, "wall-capture"),
    ("bulkhead-flavor-b", None, "wall-capture"),
    ("bulkhead-carb", None, "wall-capture"),
    ("digiten-flow", None, "none"),
)


# --- the joints that carry no line -----------------------------------------
#
# Two mouths meeting with nothing between them are still joined, and `port-leads` has to read
# them as joined or it asks each end for a straight it will never turn in.
MADE_UP = (
    # The rear bulkhead's inboard collet and the ASSE chain's inlet collet meet face to face —
    # `front_half.build_asse` seats the chain on `bulkhead_mouth_y`, "the inlet collet butts the
    # union's inboard collet". The first tube in the machine is a length of stock cut to the two
    # grips and swallowed whole by them, which is why there is no `water-1`.
    ("bulkhead-water.inboard", "asse1022-assembly.tube-in"),
    # A made-up 1/4" NPT thread: `front_half.build_gasher_co2` stations the check valve's inlet
    # on the DERPIPE's own stub tip. `co2-inlet` states no port table, so the pair is named on
    # the end that has one.
    ("gasher-co2.inlet", "co2-inlet"),
)

# Ports that open to ATMOSPHERE rather than onto a line. Nothing is ever bent onto one, so a
# bend radius is the wrong thing to ask of it — what the vent owes is that its drip falls on the
# basin's flat floor, and `front_half.check_vent_lands` raises unless it does.
TERMINI = ("asse1022-assembly.vent-tip",)


@dataclass
class Connection:
    id: str
    kind: str
    frm: str
    to: str
    routed: bool = False
    blocked: str = ""


def load_connections(runs) -> list[Connection]:
    """Every TUBE connection the machine owes, and whether a real 3-D path exists for it.

    The flavour manifold's own segments come out of `fluid-topology.md`'s tables so the
    inventory cannot drift from the topology; the four paths upstream of the carbonator are
    declared above. A connection counts as routed once `_lines.py` authors it, and a run that
    `_routing` could not draw as asked carries the shortfall with it.

    The wiring schedule is not here. It is a separate axis and nothing in this pack routes a
    conductor yet, so counting it would only bury the tube reading this card is for."""
    conns: list[Connection] = []
    if _TOPOLOGY.is_file():
        row = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
        for line in _TOPOLOGY.read_text().splitlines():
            m = row.match(line)
            if m:
                conns.append(Connection(f"fluid-{m.group(1)}", "fluid",
                                        m.group(2).strip(), m.group(3).strip()))
    for table, kind in ((REFRIGERANT_SEGMENTS, "refrigerant"), (WATER_SEGMENTS, "water"),
                        (CO2_SEGMENTS, "co2"), (CARB_SEGMENTS, "water")):
        for cid, frm, to in table:
            conns.append(Connection(cid, kind, frm, to))
    drawn = {r.id for r in runs}
    for c in conns:
        c.routed = c.id in drawn
        c.blocked = R.BLOCKED.get(c.id, "")
    return conns


# --- the bend grading ------------------------------------------------------

def bend_radii(runs) -> list[dict]:
    """Every authored run graded on the radius it turns at, worst first.

    Two grades, because two different things are wrong when a bend is too tight:

      `drawn` — the radius the run is authored at over its stock's minimum. This is the
                buildable/not question, and the gate reads it.
      `reach` — the largest radius the run's own INTERIOR legs could seat, over the same
                minimum (`_routing.leg_caps`). This is the ceiling the PACK imposes: how gentle
                the run could be made if only its `bend=` were raised.

    The pair is the diagnostic. `drawn` F with `reach` A is an authoring number — one edit in
    `_lines.py` and the run is legal. `drawn` F with `reach` F is a placement: the lane the run
    passes through is too short to turn in at any legal radius, and something on either side of
    it has to move. The leads are held out of `reach` on purpose: a run's exit and approach
    stubs are reaches the author picks, so counting them would blame the pack for a number it
    does not own.

    HOLDING THE LEADS OUT CUTS BOTH WAYS. A high `reach` on a run whose worst corner sits on an
    END leg says the interior is roomy and says nothing about whether that end leg can grow —
    which is read at the call in `_lines.py`, not off this row.

    `reach` bounds the CENTRELINE and nothing else. A run redrawn at its reach sweeps a wider
    tube through different air, so `pack-closes` is what answers that, after the edit.

    A run with no corner carries no bend to grade: `grade` is None and it is out of the gate's
    population. The radius on a straight run is the one it would turn at if it turned."""
    rows = []
    for r in runs:
        st = R.stock_of(r.kind, r.diam)
        caps = R.leg_caps(r)
        inner = [c for c in caps if c[4] == "interior"]
        seat = min((c[0] for c in caps), default=float("inf"))
        hold = min((c[0] for c in inner), default=float("inf"))
        binding = min(inner, key=lambda c: c[0]) if inner else None
        turns = [t for _i, t, _a, _b in r.bends]
        # Each CORNER is graded on the radius IT turns at, and the run reports its worst. A run
        # holds as many radii as it has corners (`_routing.seat_radii`), so one number for the
        # whole run is the tightest of them and says nothing about the rest.
        corners = [{"at": i, "turn": round(t, 1), "radius": round(r.radii[i], 3),
                    "ratio": round(r.radii[i] / st.min_bend, 4),
                    "grade": grade_of(r.radii[i] / st.min_bend),
                    "legs": [round(a, 2), round(b, 2)]}
                   for i, t, a, b in r.bends]
        tightest = min((c["radius"] for c in corners), default=r.bend)
        ratio = tightest / st.min_bend
        rows.append({
            "id": r.id, "kind": r.kind, "frm": r.frm, "to": r.to,
            "stock": st.name, "od": r.diam, "length": round(r.length, 2),
            "radius": round(tightest, 3), "cap": round(r.bend, 3), "minBend": st.min_bend,
            "ratio": round(ratio, 4),
            "grade": grade_of(ratio) if turns else None,
            "corners": corners,
            "atSpec": sum(1 for c in corners if c["radius"] >= st.min_bend - 1e-9),
            "bends": len(turns), "worstTurn": round(max(turns), 1) if turns else None,
            "seat": None if seat == float("inf") else round(seat, 3),
            "reach": None if hold == float("inf") else round(hold, 3),
            "reachRatio": None if hold == float("inf") else round(hold / st.min_bend, 4),
            "reachGrade": None if not turns else ("A" if hold == float("inf")
                                                  else grade_of(hold / st.min_bend)),
            "binding": None if binding is None else {
                "leg": binding[1], "length": round(binding[2], 3),
                "demand": round(binding[3], 4),
                "from": [round(v, 2) for v in r.pts[binding[1]]],
                "to": [round(v, 2) for v in r.pts[binding[1] + 1]],
            },
        })
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    # Worst first, and within a grade the run with the least room to improve — which is the
    # order the work wants: a run whose lanes cannot hold a legal bend is a part to move, one
    # whose lanes can is a number to raise. The ungraded straights sort last.
    rows.sort(key=lambda d: (0 if d["grade"] else 1,
                             -order.get(d["grade"], 0), -order.get(d["reachGrade"], 0),
                             d["reachRatio"] if d["reachRatio"] is not None else 1e9))
    return rows


# --- the checks ------------------------------------------------------------

@dataclass
class Check:
    id: str
    label: str
    kind: str            # "gate" | "goal"
    status: str          # "pass" | "fail" | "warn"
    value: str
    target: str
    detail: list = field(default_factory=list)
    active: bool = True


def _verdict(ok: bool) -> str:
    return "pass" if ok else "fail"


def _pack_closes(a) -> Check:
    import manifold_layout as ml
    bad, unanswered = ml.clashes(a)
    detail = [f"{c.a} ∩ {c.b}   {c.volume:.1f} mm³, {c.where}" for c in bad]
    detail += [f"{ni} ? {nj}   {why}" for ni, nj, why in unanswered]
    return Check("pack-closes", "No two solids overlap (pack closes)", "gate",
                 _verdict(not detail), f"{len(bad)} clash, {len(unanswered)} unanswered",
                 "0 clash, 0 unanswered", detail)


def _bed_fit(a) -> Check:
    import enclosure as _enc
    bed = (_enc.H2C_X, _enc.H2C_Y, _enc.H2C_Z)
    rows, short = [], []
    for c in a.children:
        if not c.name.startswith("enclosure-"):
            continue
        b = (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
            __import__("cadquery").Location(c.loc.wrapped.Transformation())).BoundingBox()
        fits = b.xlen <= bed[0] and b.ylen <= bed[1] and b.zlen <= bed[2]
        rows.append(fits)
        if not fits:
            short.append(f"{c.name}: {b.xlen:.1f} × {b.ylen:.1f} × {b.zlen:.1f} over "
                         f"{bed[0]:g} × {bed[1]:g} × {bed[2]:g}")
    return Check("bed-fit", "Every printed piece fits the bed", "gate",
                 _verdict(not short), f"{sum(rows) - 0}/{len(rows)} on the bed",
                 "every piece on the bed", short)


def _lines_clear(a, runs) -> Check:
    """The tube-interpenetration gate, asked with the boolean that resolves a tangency.

    `pack-closes` reads every pair in the assembly, tubes included, through one `intersect`. That
    is the ask `_overlap` was written because of: two tubes of one Ø crossing on ONE STRATUM are
    exactly tangent along the section, OCCT hands back an empty result with no error, and a whole
    Steinmetz solid of interpenetration reports as zero. A port row fixing two runs to a single z
    is how a pack builds that arrangement on purpose, so the case a single ask is blind to is the
    case this machine is most likely to have.

    So the runs are asked again, with `_overlap.common`'s fuzz retry — tube against tube, and
    tube against every body, piece and manifold segment it does not TERMINATE on. The two bodies
    a run ends on are held out because a tube seats into their collets by design, which is the
    one overlap here that is not a defect.

    The swept solids come off the assembly rather than being swept again: `_lines.tubes` already
    built each run's tube and `front_half` added it under `tube-<connection>`, and a second sweep
    of the same eighteen runs costs more than every boolean below."""
    bodies, drawn, pieces = _split_placed(a)
    tubes = {r.id: drawn[f"tube-{r.id}"] for r in runs if f"tube-{r.id}" in drawn}
    ends = {r.id: {r.frm.partition(".")[0], r.to.partition(".")[0]} for r in runs}
    # What is left in `drawn` is `manifold_layout`'s own segments and the placeholder stubs off
    # its free mouths. No authored run terminates on one, so they stand as bodies here.
    rest = {**bodies, **pieces,
            **{n: s for n, s in drawn.items() if n not in {f"tube-{i}" for i in tubes}}}
    tbb = {i: _boxes.boxed(t) for i, t in tubes.items()}
    rbb = {n: _boxes.boxed(s) for n, s in rest.items()}
    detail = []
    ids = list(tubes)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            if _clearing.box_gap(tbb[x], tbb[y]) > 0:
                continue
            v = _overlap.volume(tubes[x], tubes[y])
            if v > _clearing.HIT_VOL:
                detail.append(f"{x} ∩ {y}: {v:.1f} mm³")
    for i in ids:
        for name, solid in rest.items():
            if name in ends[i] or _clearing.box_gap(tbb[i], rbb[name]) > 0:
                continue
            v = _overlap.volume(tubes[i], solid)
            if v > _clearing.HIT_VOL:
                detail.append(f"{i} ∩ {name}: {v:.1f} mm³")
    return Check("lines-clear", "No routed tube intersects a body, a piece or another tube",
                 "gate", _verdict(not detail), f"{len(detail)} clash", "0 clash", detail)


def port_leads(a, runs) -> list[dict]:
    """Every port's clear lead, worst first: what it meets along its own axis, how far it got,
    and how much straight a run leaving it needs.

    `pack-closes` says two bodies do not overlap and `located` says a port is carried into world.
    Neither asks the question a connector exists to answer — whether a line can LEAVE it. A port
    is a bore with a direction, and a bore with a body parked in front of it is a bore nothing
    can be plugged into: two fittings a clean millimetre apart with their collets facing each
    other clear every other gate on this card and clear nothing a tube can be built through.

    So the port's own bore is cast along its own axis, at its own Ø, for `PORT_LEAD_BENDS` of the
    line's bend radius, and the cast has to reach. The radius is the LINE's and not the port's:
    the run that mates the port says what stock is drawn there, and a port with no run yet is
    read against the coarsest stock its own bore takes — 1/4" LLDPE asks 28 mm of straight where
    3/8" braided PVC asks 31.8.

    WHAT THE CAST MAY END ON is the body the port is JOINED to, read off the authored runs rather
    than from prose, plus the `MADE_UP` joints that have no run to read. A port whose connection
    is still un-authored is held to the full lead against everything, which is the useful
    direction — that is the state every undrawn segment's two ends are in.

    Tube is out of the population. A port's own line lies on its axis by construction, and a
    foreign one crossing there is `lines-clear`'s question, not this one."""
    bodies, _drawn, pieces = _split_placed(a)
    solids = {**bodies, **pieces}
    mates, mating = {}, {}
    for r in runs:
        for anchor, other in ((r.frm, r.to), (r.to, r.frm)):
            mates.setdefault(anchor, set()).add(other.partition(".")[0])
            mating.setdefault(anchor, []).append(r)
    for x, y in MADE_UP:
        mates.setdefault(x, set()).add(y.partition(".")[0])
        mates.setdefault(y, set()).add(x.partition(".")[0])
    rows = []
    for name, fr in sorted((getattr(a, "frames", {}) or {}).items()):
        for port in sorted(fr.ports):
            pos, face, diam = fr.ports[port]
            if pos is None or diam is None:
                continue
            anchor = f"{name}.{port}"
            drawn = mating.get(anchor)
            if drawn:
                bend = max(R.stock_of(r.kind, r.diam).min_bend for r in drawn)
            else:
                takes = [s.min_bend for s in R.STOCKS if abs(s.od - diam) < 0.05]
                bend = max(takes) if takes else R.BEND_RATIO * diam
            need = PORT_LEAD_BENDS * bend
            who, free = _clearing.cast(pos, R.normal_of(face), diam, need, solids,
                                       skip={name} | mates.get(anchor, set()))
            rows.append({"component": name, "port": port, "meets": who,
                         "free": round(free, 3), "need": round(need, 3),
                         "ok": who is None, "gated": anchor not in TERMINI,
                         "routed": bool(drawn)})
    rows.sort(key=lambda d: (d["ok"], d["free"]))
    return rows


def _port_leads(rows) -> Check:
    gated = [d for d in rows if d["gated"]]
    short = [d for d in gated if not d["ok"]]
    detail = [f"a port needs {PORT_LEAD_BENDS:g} bend radii of its own bore along its own axis, "
              f"clear of every body but the one its own line joins it to"]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to {d['meets']}, needs "
               f"{d['need']:.2f}" + ("" if d["routed"] else " — no run authored on it yet")
               for d in short]
    detail += [f"{d['component']}.{d['port']}: {d['free']:.2f} mm to "
               f"{d['meets'] or 'nothing'} — opens to atmosphere, not gated"
               for d in rows if not d["gated"]]
    return Check("port-leads", "Every tube port has the straight a run off it needs", "gate",
                 _verdict(not short), f"{len(gated) - len(short)}/{len(gated)} clear",
                 "all clear", detail)


def _runs_drawn(runs) -> Check:
    short = [f"{cid}: {why}" for cid, why in sorted(R.BLOCKED.items())]
    return Check("runs-drawn", "Every authored run is drawn as its author asked", "gate",
                 _verdict(not short), f"{len(runs) - len(short)}/{len(runs)} as drawn",
                 "0 short", short)


def _bend_radius(bends) -> Check:
    order = {g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}
    limit = order[BEND_GRADE_PASS]
    graded = [d for d in bends if d["grade"]]
    corners = sum(len(d["corners"]) for d in graded)
    at_spec = sum(d["atSpec"] for d in graded)
    worst = min((order[d["grade"]] for d in graded), default=limit)
    hist = {g: sum(1 for d in graded if d["grade"] == g) for _lo, g in GRADE_BANDS}
    tally = " ".join(f"{g}:{hist[g]}" for _lo, g in GRADE_BANDS if hist[g])
    detail = [
        "grade = radius ÷ the stock's minimum — "
        + "; ".join(f"{s.name} R{s.min_bend:g}" for s in R.STOCKS),
        f"runs by grade: {tally or 'none with a corner'}",
    ]
    for d in bends:
        if not d["grade"] or order[d["grade"]] <= limit:
            continue
        b = d["binding"]
        where = ("" if b is None
                 else f", bound by leg {b['leg']} at {b['length']:.1f} mm")
        detail.append(f"{d['grade']}/{d['reachGrade']} {d['id']} ({d['frm']} → {d['to']}): "
                      f"R{d['radius']:.1f} against R{d['minBend']:g}{where}")
    return Check("bend-radius", "Every routed tube turns at or above its stock's minimum radius",
                 "gate", _verdict(worst <= limit),
                 f"{[g for _lo, g in GRADE_BANDS][worst]} — {at_spec}/{corners} corners at spec",
                 f"every corner ≥ its stock's minimum ({BEND_GRADE_PASS})", detail)


def _routed(conns) -> Check:
    done = [c for c in conns if c.routed]
    missing = [c for c in conns if not c.routed]
    by_kind = {}
    for c in conns:
        d, t = by_kind.setdefault(c.kind, [0, 0])
        by_kind[c.kind] = [d + (1 if c.routed else 0), t + 1]
    detail = [f"{k}: {d}/{t}" for k, (d, t) in sorted(by_kind.items())]
    detail += [f"{c.id} ({c.kind}): {c.frm} → {c.to}" for c in missing]
    return Check("routed", "Every tube connection the machine owes, drawn as a real 3-D path",
                 "goal", _verdict(not missing), f"{len(done)}/{len(conns)} drawn",
                 "every connection drawn", detail)


def _located(a) -> Check:
    """Every port a placed body declares, carried to a world position with its bore."""
    frames = getattr(a, "frames", {}) or {}
    rows, bad = [], []
    for name, fr in sorted(frames.items()):
        for port in sorted(fr.ports):
            pos, _face, diam = fr.ports[port]
            ok = pos is not None and diam is not None
            rows.append(ok)
            if not ok:
                bad.append(f"{name}.{port}")
    return Check("located", "Every port a placed body declares is carried into world",
                 "goal", _verdict(not bad), f"{sum(rows)}/{len(rows)} located",
                 "every declared port positioned and sized", bad)


def _coverage(a) -> Check:
    """Every body this module seats has a row in `MOUNTS`. A body added without one is a body
    whose fastening nobody has been asked about."""
    import front_half as fh
    placed = {c.name for c in a.children
              if c.name in fh.STANDALONE or c.name in ("hopper-funnel", "display")}
    declared = {name for name, _by, _held in MOUNTS}
    missing = sorted(placed - declared)
    stray = sorted(declared - placed)
    detail = [f"placed, undeclared: {n}" for n in missing] + [f"declared, unplaced: {n}"
                                                             for n in stray]
    return Check("coverage", "Every body this module seats is declared in the fastening table",
                 "gate", _verdict(not detail),
                 f"{len(placed & declared)}/{len(placed)} declared", "all declared", detail)


def _mounted() -> Check:
    open_joints = [(n, held) for n, by, held in MOUNTS if by is None]
    # A body already held by something looser sorts last — that joint is a conversion, and one
    # nothing holds at all is a joint to invent.
    open_joints.sort(key=lambda r: (r[1] != "none", r[0]))
    detail = [f"{n}: held by {held}" for n, held in open_joints]
    done = len(MOUNTS) - len(open_joints)
    return Check("mounted",
                 "A printed feature of another placed part fastens every body", "goal",
                 _verdict(not open_joints), f"{done}/{len(MOUNTS)} mounted",
                 "a printed joint per body", detail)


def _score(check: Check) -> int:
    lo, hi = check.value.split("/")[0], check.value.split("/")[-1]
    try:
        done = int(re.findall(r"(\d+)", lo)[-1])
        total = int(re.findall(r"(\d+)", hi)[0])
    except (IndexError, ValueError):
        return 0
    return 0 if not total else round(100.0 * done / total)


# --- the card --------------------------------------------------------------

@dataclass
class Scorecard:
    checks: list
    bends: list
    conns: list
    ports: list

    @property
    def gates_pass(self) -> bool:
        return all(c.status == "pass" for c in self.checks if c.kind == "gate")


def build(a) -> Scorecard:
    runs = list(getattr(a, "runs", []))
    bends = bend_radii(runs)
    conns = load_connections(runs)
    leads = port_leads(a, runs)
    ports = []
    for name, fr in sorted((getattr(a, "frames", {}) or {}).items()):
        for port in sorted(fr.ports):
            pos, face, diam = fr.ports[port]
            ports.append({
                "component": name, "name": port, "kind": "fluid",
                "pos": None if pos is None else [round(v, 3) for v in pos],
                # The FACE ITSELF and not a rendering of it: a body-face name where the port
                # declares one, the outward normal where it is clocked off the world axes.
                # `web/contracts/port-format.js` reads a direction out of this.
                "face": face if isinstance(face, str) else [round(v, 6) for v in face],
                "diam": diam,
                "mates": ", ".join(sorted(r.id for r in runs
                                          if f"{name}.{port}" in (r.frm, r.to))) or "—",
                "status": "ok" if pos is not None and diam is not None else "no-pos",
                "note": "",
            })
    checks = [_coverage(a), _pack_closes(a), _lines_clear(a, runs), _port_leads(leads),
              _bed_fit(a), _runs_drawn(runs), _bend_radius(bends),
              _mounted(), _routed(conns), _located(a)]
    return Scorecard(checks, bends, conns, ports)


def _source() -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(_repo),
                                capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        commit = ""
    return {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": commit or None, "inputs": {}}


def to_dict(sc: Scorecard) -> dict:
    """The sidecar the 3D viewer reads — `web/contracts/scorecard-sidecar.js` is the contract.

    `mounted` is the live goal axis and every other goal is deferred, which the viewer renders
    gray. `routed`, `located` and `held` still carry their measured scores while deferred, so
    the bar reads what they are rather than a zero.

    `placed` and `shaped` read 0: nothing in this pack declares a placement rule the card can
    check, or an authorship the card can distinguish from real geometry."""
    by_id = {c.id: c for c in sc.checks}
    held = sum(1 for _n, _by, h in MOUNTS if h != "none")
    return {
        "gatesPass": sc.gates_pass,
        "placed": 0,
        "located": _score(by_id["located"]),
        "shaped": 0,
        "routed": _score(by_id["routed"]),
        "held": round(100.0 * held / len(MOUNTS)) if MOUNTS else 0,
        "mounted": _score(by_id["mounted"]),
        "checks": [
            {"id": c.id, "label": c.label, "kind": c.kind, "status": c.status,
             "value": c.value, "target": c.target, "detail": list(c.detail),
             # `mounted` is the axis the work is on; every other goal is a reading the card
             # takes but is not converting yet.
             "active": c.active and c.id == "mounted" if c.kind == "goal" else c.active}
            for c in sc.checks
        ] + [
            {"id": i, "label": lbl, "kind": "goal", "status": "warn", "value": "not opened",
             "target": want, "detail": [], "active": False}
            for i, lbl, want in (
                ("placed", "Every placement stated as a measured rule the card checks",
                 "a placement rule per body"),
                ("shaped", "Every body real geometry rather than a placeholder",
                 "no placeholder solids"),
                ("held", "Something holds every body", "a holder per body"))
        ],
        "ports": sc.ports,
        "shapes": [],
        "bends": sc.bends,
        "mounts": [{"component": n, "by": by, "held": h, "kind": "real"}
                   for n, by, h in MOUNTS],
        "source": _source(),
    }


def write(a, step: Path) -> Path:
    sc = build(a)
    out = step.with_suffix("").with_suffix(".scorecard.json") if step.suffix else step
    out = step.parent / (step.stem + ".scorecard.json")
    out.write_text(json.dumps(to_dict(sc), indent=1) + "\n")
    return out


def report(a) -> Scorecard:
    """The card, printed. One line per check, then the bend table — every run and every corner
    in it, because a run holds one radius per corner and its worst says nothing about the
    rest."""
    sc = build(a)
    print("\nscorecard")
    for c in sc.checks:
        mark = {"pass": "OK  ", "fail": "FAIL", "warn": "    "}[c.status]
        print(f"  {mark} {c.id:14} {c.value:34} {c.label}")
        limit = FOCUS_DETAIL_MAX if c.id in FOCUS_IDS else DETAIL_MAX
        for line in c.detail[:limit]:
            print(f"         {line}")
        if len(c.detail) > limit:
            print(f"         … {len(c.detail) - limit} more")
    if sc.bends:
        print("\nbend radii")
        print(f"  {'run':12} {'grade':7} {'stock':18} {'R drawn':>9} {'min':>6} "
              f"{'reach':>7} corners")
        for d in sc.bends:
            reach = "—" if d["reach"] is None else f"{d['reach']:.1f}"
            grade = f"{d['grade']}/{d['reachGrade']}" if d["grade"] else "straight"
            per = " ".join(f"{c['grade']}{c['radius']:.1f}" for c in d["corners"]) or "—"
            print(f"  {d['id']:12} {grade:7} {d['stock']:18} {d['radius']:9.1f} "
                  f"{d['minBend']:6.1f} {reach:>7} {per}")
    return sc
