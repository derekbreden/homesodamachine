"""Lane search — every corridor a run could take between its two mouths, and what each one costs
the hand that has to lay it.

A run's ends are fixed by the two fittings it joins. What is not fixed is the corridor between
them, and the card only ever reads the corridor the run is in: `carb-1` spends 289.1 mm of stock
on ends 176.3 mm apart and passes the suction chain at 0.775 mm, and every gate grades that lane
without asking whether the run belongs in it. `lanes()` asks. It enumerates every orthogonal
corridor between the two mouths that keeps a stated floor off every body, redraws each one the
way the bender would, and hands back the ones a tube can be made to.

NOT A POSE SWEEP — read this next to [`calibration/Chain.md`](/calibration/Chain.md). Every body
in the machine stands exactly where the tree puts it, in every candidate, including the two
fittings this run's own mouths are cut into. Nothing here moves a coordinate other coordinates
read, so no row of it is a half-move and there is no chain to print: what varies is which way a
length of tube goes between two points that do not move. The gates cannot answer this. They are
exact and they are the oracle, and what they grade is the corridor already drawn — `bend-radius`
prices the corners of the lane the run is in, `lines-clear` asks what its tube shares with the
machine, and neither has any way to say that the corridor one strip over is shorter, holds a
bigger radius, or can be reached without lifting the pack out. That question has to be enumerated
before there is anything for a gate to grade.

What a lane costs is not one number. Tube, corners, the tightest clearance it holds, the lowest Z
it reaches down to, and which sub-assembly each of its legs lies on — those are five different
questions and a route is chosen on whichever of them is binding that day. The one real routing
decision in this repo's record turned on hand reach and assembly order, and the route that won
had two more corners and the same length as the one it beat. So nothing here is ranked: every
candidate reports all five and the caller orders them (`sort=`, `--sort`).

Use from anywhere in the repo:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"),
    )
    import lanes

    snap = lanes.snapshot()                       # the world, flat — off disk, not rebuilt
    print(lanes.measured(snap))                   # what this reading is about

    got = lanes.lanes("fluid-4", floor=0.7)       # every corridor between that run's two mouths
    print(lanes.table("fluid-4", got))            # all five columns, one row per candidate
    print(got[0].report())                        # the winner leg by leg, corner by corner
    print(lanes.authored("fluid-4").report())     # the run AS DRAWN, through the same reader

    lanes.lanes("fluid-4", sort="margin")         # ordered by the column the caller cares about
    lanes.lanes("fluid-4", nonrising=True)        # a lane a gravity drain can take
    print(lanes.verify(got[0]))                   # one lane in probe's EXACT world

WHAT A LANE IS. The two mouths and their leads are not negotiable: a line leaves a collet along
the collet's own axis and arrives at one against it, and neither may turn inside a stock radius of
the face. So the search runs between the two LEAD ENDS, and every interior leg it draws is at
least two stock radii long, because a corner backs a tangent arc `r·tan(θ/2)` down each of its
legs and a leg between two corners pays it at both ends. A lane that comes back is a lane that
turns at spec, and its `path` is the developed length of stock with the arcs taken out — directly
comparable with the card's `need.path`.

THE SEARCH IS ORTHOGONAL AND THE AUTHORED RUNS LEAN. `_routing.bent` draws a leg that steps two
coordinates at once and two of `fluid-4`'s do, so the search steps square and `_smooth` redraws
each staircase as the lean the machine would bend, checking the diagonal against the same room. A
leaned corridor is shorter than the square one, so an orthogonal `path` is an UPPER BOUND on what
that corridor can be drawn at: a lane that beats the authored run squarely beats it leaning too.

EVERYTHING IS MEASURED AGAINST BOXES, and the direction that runs matters. Here the boxes are the
OBSTACLES and not the candidate — so a segment clear of a body's box is clear of the body, and
that is proven, while a segment its box overlaps has proven nothing. The filter can therefore only
ever DELETE lanes, never admit a bad one. Two categories cannot be boxed at all and are not: the
routed tubes, each carried as its own centreline chopped into chords, which for a swept cylinder
is the body itself; and the printed pieces, whose boxes are the whole machine, for which the
interior `cavity` stands in.

From the shell, without writing a file:

    tools/cad-venv/bin/python hardware/scripts/lanes.py snapshot
    tools/cad-venv/bin/python hardware/scripts/lanes.py snapshot --reload
    tools/cad-venv/bin/python hardware/scripts/lanes.py runs
    tools/cad-venv/bin/python hardware/scripts/lanes.py lanes fluid-4 --floor 0.7 --full
    tools/cad-venv/bin/python hardware/scripts/lanes.py lanes fluid-4 --sort margin
    tools/cad-venv/bin/python hardware/scripts/lanes.py lanes fluid-4 --sweep
    tools/cad-venv/bin/python hardware/scripts/lanes.py verify fluid-4 --lane 1 --floor 0.7
    tools/cad-venv/bin/python hardware/scripts/lanes.py selftest

BUILDING THE WORLD IS TWO MINUTES AND NO QUERY PAYS IT. `snapshot` pays it once and writes the
world down flat; every other call reads what that left, and says on its way past which snapshot it
read and whether the tree has moved since. A stale reading is a reading about the machine in that
snapshot — legible, and stated on every result — and `snapshot --reload` is what re-takes it.

`selftest` runs the solver against known-answer geometry — an empty room, a slab across the only
line, a slot a 0.5 mm floor fits through and a 2 mm floor does not, a sidestep small enough that
it has to be drawn as a lean, a block standing in the corner a shortcut would cut — then the
reader's own arithmetic against the arc it stands for, and then the machine that EXISTS through
the same filter. Run it before trusting a reading.

WHAT THESE ANSWERS DO NOT COVER:

  * A LANE IS A SHORTLIST, NOT A CLEARANCE. `margin` is box-bounded against the bodies and exact
    only against the tube centrelines, and the printed walls, seam lips, ribs and boss chains are
    not in the room at all. `verify` carries one lane into `probe`'s exact world, and that is the
    answer.
  * A BOX READING GOING NEGATIVE IS NOT A CLASH. It is the box failing to certify, and the reading
    saturates at `−Ø/2` the moment a centreline enters a box. Some of the machine's own authored
    runs read negative and every one of them is clear in the exact world — the cap lid the flavour
    lines lie in ribs on at 0.200 mm, and the compressor's cuboid round a can. `selftest` counts
    them and names each one's blocker.
  * AN EMPTY ANSWER IS NOT A PROOF. Smoothing can only redraw a corridor the square search
    REACHED, and a lane that exists on the diagonal and nowhere square is never seen — `fluid-2`
    crosses the machine on a leg that descends while it goes, and nothing comes back for it even
    at the floor its own drawn line holds. The lattice, what it was thinned at, the region it was
    cut to and whether the walk ran out of patience are printed with every result.
  * NOTHING HERE MOVES A BODY. Every candidate is a corridor in the machine as it stands, and a
    run whose two mouths are in the wrong place has no lane worth having. That is the gates' table
    and Chain.md's shape, not this.
"""

import argparse
import heapq
import itertools
import json
import math
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_ML = _HW / "manifold-layout"
sys.path.insert(0, str(_HW / "scripts"))

# The env a read-only run wants, set BEFORE the build modules are imported. This scans and
# exports nothing, so it must not take the global build lock: holding it makes every later
# build follow this process instead of running.
os.environ.setdefault("HSM_SKIP_THUMBNAILS", "1")
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")


# --- the floor and the walk's own weights ---------------------------------

# The gate's own floor. `_scorecard`'s `clearance-floor` reads a millimetre between two things
# the machine does not seat together, and a lane drawn under it is a lane that fails the card.
FLOOR = 1.0

# WHAT THE WALK PAYS FOR A CORNER, AND NOTHING ELSE PAYS IT. A Dijkstra needs a scalar to settle
# states in, and this is the exchange rate that one uses — high enough that the walk reaches an
# arrival in a few thousand states instead of a million, low enough that it still finds the
# corridors the machine's own runs are drawn on. It orders the WALK. It does not order the
# answers: what comes back reports its tube, its corners, its clearance, its depth and its
# sub-assemblies separately, because those are five questions and no exchange rate between them
# is a fact about the machine.
WALK_BEND = 25.0

# The shortest step the search will take sideways while it runs. It is NOT a bend rule — a step
# this short is drawn as one lean and not two corners, and `_smooth` is where that happens. It is
# the lattice's own grain: two coordinates nearer than this are one coordinate as far as a tube
# is concerned, and letting the search stop between them only makes the state space bigger.
LEAN_STEP = 4.0

# How far outside the box of a run's two mouths a lane may wander, and the region the lattice is
# cut from. A lane is not searched beyond it — which is a bound on the QUERY and not a claim
# that nothing out there would serve.
REGION = 90.0

# The most coordinates the lattice carries per axis. The search is over (cell × heading), so this
# is the knob that decides whether a query takes a second or a minute; the coordinates kept are
# the ones a shortest orthogonal path can turn on — an obstacle's own faces, stood off by the
# tube's half-section and the floor — thinned until they fit.
#
# A THINNED LATTICE COSTS THE CORRIDOR ITS TURNS, which is why every reading says what it was
# thinned at. At 34 the machine's runs thin at 10.5 mm; at 22 they thin at 16.8 mm and the same
# corridors come back six millimetres longer, because the coordinate a leg would have turned on
# is no longer carried. Thin far enough and a lane stops coming back at all.
LATTICE_CAP = 34

# The most states a lane search will settle before it gives up and reports what it has. A bound
# on the QUERY and not on the machine: a search that reaches it has run out of patience, not out
# of corridors, and `lanes()` says so rather than letting an empty answer read as a proof.
POP_BUDGET = 400_000

# How many times one (cell, heading) may be settled. One is a shortest-path search and answers
# only the first question; more is what makes a SECOND corridor reachable at all. Every extra
# settlement multiplies the walk, so this is small and `_search` de-duplicates on the corridor's
# own shape rather than leaning on it.
VISITS = 4

# What a corridor pays, in corners, for a turning leg too short to seat two square ones. See
# `_search`. 0 turns the search loose on staircases; it is here so the shortlist fills with
# corridors that can be bent as they are found.
SHORT_LEG = 1.0


# --- the snapshot ---------------------------------------------------------
#
# One `build_enclosure_assembly()` is two minutes, and a scan wants the same world thousands of
# times. So the world is taken ONCE and written down flat: every body's box, every routed run's
# centreline, every port's position and axis, and the interior the printed pieces leave.
#
# THE SNAPSHOT IS THE DEFAULT PATH AND A QUERY NEVER BUILDS. `snapshot --reload` is what pays the
# two minutes; everything else reads the newest one on disk and states, on its way past, which
# sources have moved under it. A reading off a moved tree is a reading about the machine in that
# snapshot, which is legible; a query that silently spends two minutes rebuilding is a query
# nobody runs twice.

_SOURCES = ("manifold-layout/enclosure_assembly.py", "manifold-layout/_lines.py",
            "manifold-layout/manifold_layout.py", "scripts/_routing.py",
            "printed-parts/enclosure/enclosure/enclosure.py")

_SNAP: dict = {}


def _stamps() -> dict:
    """Each source's size and mtime — what decides whether a snapshot is still the tree's."""
    out = {}
    for rel in _SOURCES:
        st = (_HW / rel).stat()
        out[rel] = f"{st.st_size}:{int(st.st_mtime)}"
    return out


def _source_key(stamps: dict = None) -> str:
    stamps = _stamps() if stamps is None else stamps
    return str(abs(hash(tuple(f"{k}:{v}" for k, v in sorted(stamps.items())))))


def _cache_path() -> Path:
    return Path(tempfile.gettempdir()) / f"hsm-lanes-{_source_key()}.json"


def held() -> tuple:
    """Every snapshot on disk, newest first."""
    d = Path(tempfile.gettempdir())
    return tuple(sorted(d.glob("hsm-lanes-*.json"), key=lambda p: p.stat().st_mtime,
                        reverse=True))


def moved(snap: dict) -> tuple:
    """Which of the sources have moved since this snapshot was taken, by name."""
    now, was = _stamps(), snap.get("sources") or {}
    return tuple(rel for rel in _SOURCES if now.get(rel) != was.get(rel))


def measured(snap: dict) -> str:
    """What a reading off this snapshot is about, in one line — printed with every result.

    A scan that reports its bounds and not this is reporting half of where its answer came from:
    the same query against a snapshot taken before `_lines.py` moved answers about a different
    machine, and neither answer is wrong about the world it was taken in."""
    head = (f"{len(snap['bodies'])} bodies, {len(snap['runs'])} routed runs, "
            f"{len(snap['ports'])} ports, taken "
            f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(snap.get('taken', 0)))}")
    gone = moved(snap)
    if not gone:
        return f"{head} — the tree has not moved under it"
    return (f"{head}\nTAKEN BEFORE {', '.join(Path(g).name for g in gone)} MOVED — this reading "
            f"is about the machine in that snapshot,\nnot the one in the tree. Re-take it with "
            f"`lanes.py snapshot --reload`.")


def take() -> dict:
    """Build the machine and write down what a lane search needs of it.

    Bodies as boxes, runs as centrelines, ports as (position, axis, bore), and the cavity the
    box's four pieces leave. Nothing here is a summary of a measurement — every number is the
    placed geometry's own, read off the same assembly the build exports."""
    sys.path.insert(0, str(_ML))
    import enclosure_assembly as fh                                  # noqa: E402
    a = fh.build_enclosure_assembly()
    placed = fh._solids(a)
    bodies = {}
    for name, (solid, _colour) in placed.items():
        tag = _tag(name)
        # NEITHER A PIECE NOR A RUN IS BOXED, and neither is boxed here. `cq.Shape.BoundingBox`
        # is `AddOptimal` — a mesh — and on a printed piece that is minutes, not the 0.2 s
        # `_boxes` quotes for a pack solid. Both are held by something else anyway: the pieces
        # by `cavity`, the runs by their own centrelines. So the box is never taken.
        if tag in ("piece", "run"):
            bodies[name] = {"tag": tag, "box": None}
            continue
        b = solid.BoundingBox()
        box = [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]
        span = [box[1] - box[0], box[3] - box[2], box[5] - box[4]]
        room = span[0] * span[1] * span[2]
        fill = (solid.Volume() / room) if room > 1e-9 else 1.0
        bodies[name] = {"tag": tag, "box": box, "fill": round(fill, 4)}
        # A BODY THAT DOES NOT FILL ITS BOX IS NOT ITS BOX. The hopper basin is a cone under a
        # brim and fills a fifth of the cuboid round it; a lane running under that brim reads
        # blocked against the box and clear against the basin. Sliced across its own longest
        # axis, the staircase of slabs hugs it, and every one of them is still an
        # over-approximation — so the filter still only ever deletes lanes, never admits one.
        if fill < FILL_FLOOR:
            bodies[name]["slabs"] = _slabs(solid, box)
    runs = {}
    for r in a.runs:
        runs[r.id] = {"frm": r.frm, "to": r.to, "kind": r.kind, "diam": r.diam,
                      "bend": r.bend, "length": r.length,
                      "pts": [list(p) for p in r.pts]}
    import _routing as R                                      # noqa: E402
    ports = {}
    for comp, frame in a.frames.items():
        for port in frame.ports:
            ports[f"{comp}.{port}"] = {"pos": list(frame.at(port)),
                                       "axis": list(R.normal_of(frame.ports[port][1])),
                                       "diam": frame.diam(port)}
    inner = list(a.box.inner)
    return {"bodies": bodies, "runs": runs, "ports": ports,
            "cavity": [inner[0], inner[1], inner[2], inner[3], inner[4], inner[5]],
            "sources": _stamps(), "taken": time.time()}


# How much of its own box a body has to fill before the box is taken as a fair stand-in for it,
# and how many slabs an unfair one is cut into. Under the floor the body is sliced instead: a
# cone, a shell or a bracket that reads as a solid block deletes lanes that are really there.
FILL_FLOOR = 0.5
SLABS = 10


def _slabs(solid, box) -> list:
    """A body cut into slices, each boxed on what is actually in it — on whichever of the three
    axes the slicing gains most.

    WHICH AXIS IS NOT THE LONGEST ONE. The hopper basin is 173 mm across and 53 mm tall, and
    slicing its width leaves ten tall slabs each still holding the air under the brim; sliced
    across its own short axis the slabs follow the cone down. So all three are cut and the one
    whose slabs hold the least is kept — measured, not guessed, because which way a body tapers
    is a fact about the body.

    Every slab is still an over-approximation of the slice it holds, so this can only ever make
    the filter LOOSER — the lanes it admits are lanes the single box was wrong to delete. A slice
    the boolean will not resolve keeps the whole box, which is the direction that cannot invent
    room."""
    import cadquery as cq
    span = [box[1] - box[0], box[3] - box[2], box[5] - box[4]]
    best = None
    for axis in range(3):
        if span[axis] < 1e-6:
            continue
        step = span[axis] / SLABS
        out = []
        for n in range(SLABS):
            origin = [box[0], box[2], box[4]]
            size = list(span)
            origin[axis], size[axis] = box[2 * axis] + n * step, step
            try:
                part = solid.intersect(cq.Solid.makeBox(
                    size[0] + 2e-6, size[1] + 2e-6, size[2] + 2e-6,
                    cq.Vector(origin[0] - 1e-6, origin[1] - 1e-6, origin[2] - 1e-6)))
            except Exception:
                out = None
                break
            if part is None or not part.Solids():
                continue
            sb = part.BoundingBox()
            out.append([sb.xmin, sb.xmax, sb.ymin, sb.ymax, sb.zmin, sb.zmax])
        if not out:
            continue
        held_ = sum((s[1] - s[0]) * (s[3] - s[2]) * (s[5] - s[4]) for s in out)
        if best is None or held_ < best[0]:
            best = (held_, out)
    return best[1] if best else [list(box)]


def _tag(name: str) -> str:
    """The role a body's name carries — `probe._source`'s own split, restated here so a
    snapshot can be read back without building anything."""
    if name.startswith("enclosure-"):
        return "piece"
    if name.startswith("tube-") or name.startswith("turn-") or name.startswith("step-"):
        return "run"
    return {"display": "display", "hopper-funnel": "funnel"}.get(name, "component")


def snapshot(reload: bool = False, build: bool = None) -> dict:
    """The world as a flat table, read off disk.

    A QUERY DOES NOT BUILD. The exact snapshot for this tree is taken if it is there; otherwise
    the newest one on disk is read and `measured` says which sources moved under it. Only
    `reload=True` — `snapshot --reload` — pays the two minutes, and only a machine with no
    snapshot at all builds without being asked.

    `build=True` restores the other bargain: rebuild whenever the tree has moved. It is for a
    caller who would rather wait than read a stale world, and it is never the default, because
    the default is what somebody runs at the top of a session to see whether the instrument says
    anything at all."""
    if _SNAP and not reload:
        return _SNAP
    cache = _cache_path()
    if cache.exists() and not reload:
        _SNAP.update(json.loads(cache.read_text()))
        return _SNAP
    on_disk = held()
    if on_disk and not reload and not build:
        _SNAP.update(json.loads(on_disk[0].read_text()))
        return _SNAP
    if not reload and not on_disk:
        print("lanes: no snapshot on disk — building the world once, about two minutes. "
              "`lanes.py snapshot --reload` is what re-takes it.", file=sys.stderr)
    snap = take()
    cache.write_text(json.dumps(snap))
    _SNAP.clear()
    _SNAP.update(snap)
    return _SNAP


# --- what fastens what ----------------------------------------------------

_MOUNTS: dict = {}


def sub_assemblies() -> dict:
    """`{body: the sub-assembly it is part of}` — `_scorecard.MOUNTS`, which is one row per body
    the machine seats, naming the part whose printed feature fastens it.

    THIS IS THE ASSEMBLY-ORDER READING. A leg lying on `enclosure-back-top` is a leg laid against
    a wall that is in the operator's hand; a leg lying on `foam-assembly` is one that cannot be
    laid until the cold core is down and cannot be reached afterwards without lifting it. That is
    the axis the one real routing decision in this repo's record turned on, and no clearance
    figure carries it.

    A body `MOUNTS` gives no fastener — one that stands on the floor or is captured in a wall —
    names itself with its joint, because that is what it is a part of. A body the table does not
    hold at all says so rather than being quietly assigned somewhere."""
    if _MOUNTS:
        return _MOUNTS
    sys.path.insert(0, str(_ML))
    import _scorecard                                            # noqa: E402
    for name, by, joint in _scorecard.mounts():
        _MOUNTS[name] = by or f"{name} ({joint})"
    return _MOUNTS


def _rides(name: str) -> str:
    """The sub-assembly one obstacle belongs to. A chopped tube chord carries its run's id."""
    if "[" in name:
        return f"run {name.split('[')[0]}"
    got = sub_assemblies().get(name)
    return got if got is not None else f"{name} (no row in _scorecard.MOUNTS)"


# --- the room a lane has to miss ------------------------------------------

# The longest chord a tube is chopped into before it is boxed. A box round a leaning length of
# tube holds the tube and a wedge of air either side of it, and the wedge is what would delete a
# lane running beside it — `fluid-2` leans across the strip `fluid-4` runs down, and one box round
# that whole leg swallows the mirror line. Chopped this fine, the wedge is under a tenth of a
# millimetre on the steepest lean in the machine.
TUBE_CHORD = 6.0

_TUBES: dict = {}


def _tube_boxes(rid: str, r: dict) -> tuple:
    """One routed run as a string of tight boxes along the tube the machine actually contains.

    Two things a run's own `pts` are not. They are SQUARE, and the sweep rounds every corner off
    them — so the tube stands inside the vertex and outside the arc, and a box on the polyline is
    a box on a shape that was never built. And they are LONG, so a leaning leg's box is mostly
    air. `_rounded` fixes the first and the chord fixes the second."""
    hit = _TUBES.get(rid)
    if hit is not None:
        return hit
    pts = _rounded(_graded(rid, tuple(tuple(p) for p in r["pts"]), r["diam"], r["bend"]))
    rad = r["diam"] / 2.0
    out = []
    for p, q in zip(pts, pts[1:]):
        n = max(1, int(math.ceil(_dist(p, q) / TUBE_CHORD)))
        for s in range(n):
            a = tuple(p[i] + (q[i] - p[i]) * s / n for i in range(3))
            b = tuple(p[i] + (q[i] - p[i]) * (s + 1) / n for i in range(3))
            out.append((f"{rid}[{len(out)}]",
                        (min(a[0], b[0]) - rad, max(a[0], b[0]) + rad,
                         min(a[1], b[1]) - rad, max(a[1], b[1]) + rad,
                         min(a[2], b[2]) - rad, max(a[2], b[2]) + rad)))
    _TUBES[rid] = tuple(out)
    return _TUBES[rid]


def _boxes_of(snap: dict, hold: tuple) -> tuple:
    """Every obstacle as an axis-aligned box, with the held bodies out.

    A ROUTED RUN IS NOT ITS BOX. `fluid-18` crosses the machine and climbs, and its box is a slab
    of mostly air through half the cabinet — held as one box it would delete every lane that goes
    anywhere near it. So each run comes in as `_tube_boxes`: the tube it really is, chopped fine
    enough that the boxes hug it.

    The printed PIECES are not here at all, for the opposite reason: a piece's box is the whole
    machine. `cavity` stands in for them and `verify` measures against them exactly."""
    out = []
    for name, b in snap["bodies"].items():
        if name in hold or b["tag"] in ("piece", "run"):
            continue
        for s in b.get("slabs") or [b["box"]]:
            out.append((name, tuple(s)))
    for rid, r in snap["runs"].items():
        if rid in hold or f"tube-{rid}" in hold:
            continue
        out.extend(_tube_boxes(rid, r))
    return tuple(out)


@dataclass
class Room:
    """What a lane has to miss, and what it is allowed to ignore.

    `hold` is the whole of the second half: a run being re-laned is measured against the machine
    and not against the tube it is replacing, and neither against the two bodies its own mouths
    are cut into. Leaving those in reports a clash at exactly the joints the search exists to
    move, which is a tautology and not a finding."""
    boxes: tuple
    cavity: tuple
    hold: tuple

    @classmethod
    def of(cls, snap: dict, hold=()) -> "Room":
        hold = tuple(sorted(set(hold)))
        return cls(_boxes_of(snap, hold), tuple(snap["cavity"]), hold)

    def near(self, region: tuple, pad: float = 0.0) -> tuple:
        """The obstacles whose boxes reach into a region — the only ones a lane inside it can
        run into, which is what keeps the free-interval scan short."""
        return tuple((n, b) for n, b in self.boxes
                     if all(b[2 * i] - pad < region[2 * i + 1]
                            and b[2 * i + 1] + pad > region[2 * i] for i in range(3)))


# --- the lane -------------------------------------------------------------

def _dist(a, b) -> float:
    return math.dist(a, b)


def _graded(cid: str, pts: tuple, od: float, radius: float):
    """A polyline through `_routing`'s OWN corner solver, as the `Run` it would be.

    Nothing here re-derives what a corner costs or what radius it seats. `_routing._bends` reads
    the turns, `_routing.seat_radii` shares each leg's tangent between the two corners that pay
    for it, and `Run.length` takes the arcs back out of the square length — the same three the
    card grades every authored run with. So a lane's `path` and the card's `need.path` are one
    number computed one way, and may be read against each other."""
    import _routing as R
    pts = list(pts)
    bends = R._bends(pts, cid)
    radii = R.seat_radii(pts, bends, R._caps(bends, radius, cid, od), cid, od)
    return R.Run(cid, "fluid", "", "", pts, od, radius, "", bends, radii)


@dataclass
class Lane:
    """One corridor: the polyline it turns on, and the five things a route is chosen on.

    `path` is the DEVELOPED length — the stock the run would cut, arcs taken out — so it is the
    same number the card's `need.path` reports. `bends` is the corners. `margin` is the tightest
    the lane comes to anything in the room, exact against the tube centrelines and box-bounded
    against the bodies. `lowest` is how far down into the machine the tube reaches, which is what
    an arm has to get to. `rides` names the sub-assembly each leg lies on, which is what decides
    whether the leg can be laid before the cold core goes in or only after.

    `seated` is the smallest radius any of its corners can actually turn at, off `_routing`'s own
    solver: a lane whose corners cannot reach the stock's minimum is a lane the bender cannot
    make, and it is said here rather than left in a table.

    NOTHING ORDERS THESE. Five columns and no scalar over them — see the module docstring."""
    run: str
    pts: tuple
    od: float
    radius: float
    floor: float
    margin: float
    span: float
    legs: tuple
    square: tuple = ()          # the orthogonal lane it was smoothed from
    near: tuple = ()            # the bodies it comes nearest to, tightest first
    rides: tuple = ()           # one (leg, gap, body, sub-assembly) per leg
    lattice: object = None      # the lattice it was searched on, when it was searched
    drawn: float = 0.0          # the authored length, on the run AS DRAWN

    def __post_init__(self):
        self._run = _graded(self.run, self.pts, self.od, self.radius)

    @property
    def bends(self) -> int:
        return len(self._run.bends)

    @property
    def path(self) -> float:
        return self._run.length

    @property
    def lowest(self) -> float:
        """The lowest Z the TUBE holds — arcs drawn in, not the polyline's vertices.

        A lane that stays high is one an arm reaches over the pack; a lane that dips is one
        somebody has to get a hand under something to lay."""
        return min(p[2] for p in self.centreline)

    @property
    def seated(self) -> float:
        return self._run.tightest

    @property
    def worst_turn(self) -> float:
        return max((t for _i, t, _a, _b in self._run.bends), default=0.0)

    @property
    def at_spec(self) -> bool:
        return self.seated >= self.radius - 1e-6 and self.worst_turn <= MAX_TURN + 1e-6

    @property
    def centreline(self) -> tuple:
        """The tube's own path — the polyline with every corner's arc drawn in."""
        return _rounded(self._run)

    @property
    def detour(self) -> float:
        return self.path / self.span if self.span > 1e-9 else math.inf

    @property
    def leans(self) -> int:
        """How many of its legs step more than one coordinate — what `_routing.bent` draws and
        `_routing.route` cannot."""
        n = 0
        for a, b in zip(self.pts, self.pts[1:]):
            if sum(1 for i in range(3) if abs(b[i] - a[i]) > 1e-6) > 1:
                n += 1
        return n

    @property
    def on(self) -> tuple:
        """The distinct sub-assemblies this lane lies on, in the order its legs meet them."""
        out = []
        for _leg, _gap, _body, sub in self.rides:
            if sub not in out:
                out.append(sub)
        return tuple(out)

    def vector(self) -> str:
        """The lane's own shape in one line — the axis each leg mostly runs on and how far, with
        a leaning leg marked."""
        bits = []
        for a, b in zip(self.pts, self.pts[1:]):
            i = max(range(3), key=lambda k: abs(b[k] - a[k]))
            d = b[i] - a[i]
            lean = "~" if sum(1 for k in range(3) if abs(b[k] - a[k]) > 1e-6) > 1 else ""
            bits.append(f"{lean}{'xyz'[i]}{'+' if d > 0 else '-'}{abs(d):.0f}")
        return " ".join(bits)

    def report(self) -> str:
        out = [f"{self.run}: {self.path:.1f} mm of stock, {self.bends} bend"
               f"{'' if self.bends == 1 else 's'} ({self.leans} leaning), "
               f"lowest z {self.lowest:.1f}",
               f"  ends {self.span:.1f} mm apart, detour {self.detour:.3f}×, "
               f"margin {self.margin:.3f} mm (floor {self.floor:.2f}), "
               f"corners seat R{self.seated:.2f} of R{self.radius:g}"
               f"{'' if self.at_spec else '  — UNDER SPEC'}", ""]
        rides = {leg: (gap, body, sub) for leg, gap, body, sub in self.rides}
        for n, (a, b) in enumerate(zip(self.pts, self.pts[1:])):
            i = max(range(3), key=lambda k: abs(b[k] - a[k]))
            lean = "~" if sum(1 for k in range(3) if abs(b[k] - a[k]) > 1e-6) > 1 else " "
            out.append(f"  leg {n + 1} {lean} {'xyz'[i]} {_dist(a, b):7.2f} mm   "
                       f"({a[0]:7.2f}, {a[1]:7.2f}, {a[2]:7.2f}) → "
                       f"({b[0]:7.2f}, {b[1]:7.2f}, {b[2]:7.2f})")
            if n in rides:
                gap, body, sub = rides[n]
                out.append(f"          lies on {sub}  ({body} at {gap:.3f} mm)")
        for i, turn, la, lb in self._run.bends:
            out.append(f"  corner at {i}  {turn:5.1f}°  seats R{self._run.radii[i]:5.2f}  "
                       f"legs {la:.1f} / {lb:.1f}")
        if self.near:
            out.append("  nearest: " + ", ".join(f"{n} {g:.3f}" for g, n in self.near))
        return "\n".join(out)


# --- how a caller orders them ---------------------------------------------

# The columns a candidate carries, each with the sign that puts its own better end first: less
# tube, fewer corners, more clearance, less depth reached, less detour.
COLUMNS = {"path": 1, "bends": 1, "margin": -1, "lowest": -1, "detour": 1}


def order(made: list, by: str = None) -> list:
    """The candidates ordered on ONE named column, or left in the order the walk found them.

    There is no ordering over all of them, so there is none here. `by` is the caller saying
    which question is binding today."""
    if by is None:
        return list(made)
    if by not in COLUMNS:
        raise KeyError(f"no column {by!r} — have: {', '.join(sorted(COLUMNS))}")
    return sorted(made, key=lambda l: COLUMNS[by] * getattr(l, by))


def table(run: str, made: list, drawn: "Lane" = None) -> str:
    """The candidates as the caller reads them: five columns and no ranking, with the run AS
    DRAWN on the bottom row so every figure has the thing it is being read against beside it."""
    out = [f"{'#':>3}  {'path':>6}  {'bend':>4}  {'detour':>6}  {'margin':>7}  {'low z':>6}"
           f"   lane"]
    for n, l in enumerate(made, 1):
        out.append(f"{n:>3}  {l.path:6.1f}  {l.bends:4d}  {l.detour:6.3f}  {l.margin:7.3f}  "
                   f"{l.lowest:6.1f}   {l.vector()}")
        if l.on:
            out.append(f"{'':>3}  lies on {' · '.join(l.on)}")
    if drawn is not None:
        out.append(f"{'now':>3}  {drawn.drawn:6.1f}  {drawn.bends:4d}  "
                   f"{drawn.drawn / drawn.span:6.3f}  {drawn.margin:7.3f}  {drawn.lowest:6.1f}"
                   f"   {drawn.vector()}")
        if drawn.on:
            out.append(f"{'':>3}  lies on {' · '.join(drawn.on)}")
    out.append("no column here ranks another. Order on the one that is binding: "
               "`--sort " + "|".join(sorted(COLUMNS)) + "`.")
    return "\n".join(out)


# --- the lattice ----------------------------------------------------------

def _thin(values, keep, cap: int) -> tuple:
    """A sorted axis of coordinates no longer than `cap`, with `keep` never dropped.

    Thinned by SPACING and not by count: the step is walked up until what survives fits, so what
    goes is a coordinate that stands a hair off another one rather than a whole region of the
    machine. A lattice that has been thinned is a search that can miss a lane, and `Lattice`
    carries the step it was thinned at so a reading says so."""
    keep = sorted(set(round(v, 6) for v in keep))
    rest = sorted(set(round(v, 6) for v in values) - set(keep))
    step = 0.0
    while True:
        out, last = [], None
        for v in sorted(keep + rest):
            if last is None or v - last > step - 1e-9 or v in keep:
                out.append(v)
                last = v
        if len(out) <= cap or step > 400.0:
            return tuple(out), step
        step = max(1.0, step * 1.6)


@dataclass
class Lattice:
    """The coordinates a lane may turn on, and how they were chosen.

    A shortest orthogonal path among boxes turns where an obstacle's own face is, stood off by
    the tube's half-section and the floor — so those planes, the two mouths' own coordinates and
    the region's bounds are the whole candidate set. The step is what the thinning cost: 0 is
    every candidate kept."""
    coords: tuple
    step: tuple
    region: tuple

    def index(self, axis: int, value: float) -> int:
        c = self.coords[axis]
        for n, v in enumerate(c):
            if abs(v - value) < 1e-6:
                return n
        raise ValueError(f"{value} is not on the lattice's {'xyz'[axis]} axis — "
                         f"{len(c)} coordinates from {c[0]:.2f} to {c[-1]:.2f}")

    @property
    def size(self) -> int:
        return len(self.coords[0]) * len(self.coords[1]) * len(self.coords[2])


def lattice(room: Room, ends: tuple, rad: float, radius: float, region_pad: float = REGION,
            cap: int = LATTICE_CAP) -> Lattice:
    """The lattice a lane between these two points is searched on.

    TWO STANDOFFS PER OBSTACLE FACE, not one. A leg that runs PAST a body wants the tube's own
    half-section and the floor; a leg that TURNS beside it wants that and the bulge its corner
    arc makes, which at 90° reaches `r·(sec 45° − 1)` off the vertex the lane was searched on.
    Both are candidate planes because a lane does both, and a lattice carrying only the first
    finds hugging corridors that vanish the moment their corners are rounded.

    And two more per mouth, at two radii either side: a lane that has to COME ABOUT to enter a
    collet turns about that far from it, and with no body nearby to plant a coordinate there,
    nothing else would."""
    lo = [min(e[i] for e in ends) - region_pad for i in range(3)]
    hi = [max(e[i] for e in ends) + region_pad for i in range(3)]
    cav = room.cavity
    for i in range(3):
        lo[i] = max(lo[i], cav[2 * i] + rad)
        hi[i] = min(hi[i], cav[2 * i + 1] - rad)
        # A mouth in a wall stands outside the interior; the region has to hold it anyway.
        lo[i] = min(lo[i], min(e[i] for e in ends))
        hi[i] = max(hi[i], max(e[i] for e in ends))
    region = tuple(v for i in range(3) for v in (lo[i], hi[i]))
    near = room.near(region)
    bulge = radius * (math.sqrt(2.0) - 1.0)
    coords, steps = [], []
    for i in range(3):
        keep = [e[i] for e in ends] + [lo[i], hi[i]]
        cand = list(keep)
        for e in ends:
            cand += [e[i] - 2.0 * radius, e[i] + 2.0 * radius]
        for _n, b in near:
            for v in (b[2 * i] - rad, b[2 * i + 1] + rad,
                      b[2 * i] - rad - bulge, b[2 * i + 1] + rad + bulge):
                cand.append(v)
        cand = [v for v in cand if lo[i] - 1e-9 <= v <= hi[i] + 1e-9]
        c, step = _thin(cand, keep, cap)
        coords.append(c)
        steps.append(step)
    return Lattice(tuple(coords), tuple(steps), region)


def _spans(near: tuple, axis: int, c1: float, c2: float, rad: float,
           bound: tuple) -> tuple:
    """The free intervals along one line of the lattice.

    Every obstacle whose grown box straddles the line's other two coordinates blocks a closed
    interval on it; what is left inside the bound is where a leg on that line may run. Taken
    once per line and reused by every edge on it, which is what makes an edge check a bisection
    instead of a sweep of the machine."""
    j, k = [n for n in range(3) if n != axis]
    blocked = []
    for _n, b in near:
        if (b[2 * j] - rad < c1 < b[2 * j + 1] + rad
                and b[2 * k] - rad < c2 < b[2 * k + 1] + rad):
            blocked.append((b[2 * axis] - rad, b[2 * axis + 1] + rad))
    blocked.sort()
    free, at = [], bound[0]
    for lo, hi in blocked:
        if lo > at:
            free.append((at, min(lo, bound[1])))
        at = max(at, hi)
        if at >= bound[1]:
            break
    if at < bound[1]:
        free.append((at, bound[1]))
    return tuple((a, b) for a, b in free if b - a > 1e-9)


class _Free:
    """The free intervals of every line the lattice carries, taken on demand and kept."""

    def __init__(self, lat: Lattice, near: tuple, rad: float):
        self.lat, self.near, self.rad = lat, near, rad
        self._held: dict = {}
        self._legs: dict = {}

    def spans(self, axis: int, cell: tuple) -> tuple:
        j, k = [n for n in range(3) if n != axis]
        key = (axis, cell[j], cell[k])
        hit = self._held.get(key)
        if hit is None:
            c = self.lat.coords
            hit = _spans(self.near, axis, c[j][cell[j]], c[k][cell[k]], self.rad,
                         (self.lat.region[2 * axis], self.lat.region[2 * axis + 1]))
            self._held[key] = hit
        return hit

    def clear(self, axis: int, cell: tuple, a: float, b: float) -> bool:
        lo, hi = (a, b) if a <= b else (b, a)
        return any(s <= lo + 1e-6 and hi <= e + 1e-6 for s, e in self.spans(axis, cell))

    def legs(self, cell: tuple, axis: int, sign: int, turn: int, lead: float,
             goal: tuple, into: tuple) -> tuple:
        """Every cell a leg from here along this heading may end on, held once per line.

        A leg that starts at a CORNER is at least `LEAN_STEP` long; one that carries the previous
        leg further owes nothing, because a leg only gets longer that way.

        THE ONE THAT ARRIVES OWES NOTHING EITHER, and that is not a relaxation. The search runs
        between the two LEAD ENDS, and the lead end already stands one stock radius off the
        mouth on the mouth's own line — so the leg that arrives there is only the far part of a
        final leg that is already `radius` long before it starts. Asking it for a radius of its
        own asks the approach for two, and the band a mouth stands in is often not that deep.

        Past the first obstruction on the line nothing is reachable at all, which is where the
        walk stops.

        Held on (line, heading, whether it turns): the search asks the same question from the
        same cell once per settlement, and the answer cannot have changed."""
        key = (cell, axis, sign, turn)
        hit = self._legs.get(key)
        if hit is not None:
            return hit
        c = self.lat.coords[axis]
        here = c[cell[axis]]
        minleg = LEAN_STEP if turn else 0.0
        out = []
        rng = range(cell[axis] + 1, len(c)) if sign > 0 else range(cell[axis] - 1, -1, -1)
        for n in rng:
            if not self.clear(axis, cell, here, c[n]):
                break
            span = abs(c[n] - here)
            end = tuple(n if i == axis else cell[i] for i in range(3))
            arrives = end == goal and (axis, sign) == into
            if span < minleg - 1e-6 and not arrives:
                continue
            out.append((end, span))
        self._legs[key] = tuple(out)
        return self._legs[key]


# --- the search -----------------------------------------------------------

def lanes(run: str, top: int = 6, floor: float = FLOOR, hold=(), snap: dict = None,
          nonrising: bool = None, cap: int = LATTICE_CAP, region: float = REGION,
          ends: tuple = None, radius: float = None, od: float = None,
          sort: str = None) -> list:
    """Every orthogonal corridor between a run's two mouths that keeps `floor` off the machine.

    The two mouths and their leads are not negotiable: a line leaves a collet along the collet's
    own axis and arrives at one against it, and neither may turn inside a stock radius of the
    face. So the search runs between the two LEAD ENDS, and each interior leg is at least two
    radii long because a corner backs a tangent that far down each of its legs. That is the
    whole difference between a lane and a polyline: what comes back can be bent.

    THE ORDER IS THE WALK'S OWN AND IS NOT A RANKING. The Dijkstra settles states on `WALK_BEND`
    because a shortest-path search needs a scalar to settle on; the candidates come back in the
    order it reached them. `sort=` orders them on one named column — `path`, `bends`, `margin`,
    `lowest`, `detour` — which is the caller saying which question is binding. `top` is a bound
    on the QUERY, how many distinct corridors the walk is asked for, and not a shortlist off a
    ranking.

    `nonrising` bans a leg that climbs, which is what a gravity drain needs — `fluid-4` is the
    basin's air-purge path as well as its drain, so a hump anywhere in it holds the air the
    basin has to push out. Left unset it is read off the run: the hopper's drain takes it.

    RAISES when the mouths are not axis-aligned, and returns EMPTY when nothing on the lattice
    joins them at that floor. Empty is a statement about the lattice and the floor, not a proof
    that no corridor exists — a thinned lattice can miss one, and the report says so."""
    snap = snapshot() if snap is None else snap
    spec = snap["runs"].get(run)
    if spec is None and ends is None:
        raise KeyError(f"no run {run!r} — have: {', '.join(sorted(snap['runs']))}")
    own = ()
    if ends is None:
        a, b = spec["frm"], spec["to"]
        pa, pb = snap["ports"][a], snap["ports"][b]
        ends = ((tuple(pa["pos"]), tuple(pa["axis"])), (tuple(pb["pos"]), tuple(pb["axis"])))
        od = spec["diam"] if od is None else od
        radius = spec["bend"] if radius is None else radius
        own = (a.split(".")[0], b.split(".")[0])
        hold = tuple(hold) + (run, f"tube-{run}")
    if nonrising is None:
        nonrising = bool(spec) and spec["frm"].startswith("hopper-funnel")
    od = 6.35 if od is None else od
    radius = 14.0 if radius is None else radius

    (p0, n0), (p1, n1) = ends
    # A lane leaves along the port's own axis and enters against the other's. Both leads are a
    # full stock radius, which is what the first corner needs before it can turn at all.
    q0 = tuple(p0[i] + n0[i] * radius for i in range(3))
    q1 = tuple(p1[i] + n1[i] * radius for i in range(3))

    # A BODY A RUN LEAVES IS STILL A BODY THE RUN HAS TO MISS. The two the mouths are cut into
    # are held out only where holding them out is the only way to ask the question: if the lead
    # end still stands inside the body's own box — the hopper basin is a cone and its box holds
    # the whole spout — then every line off that mouth reads blocked and there is nothing to
    # search. Where the lead end stands clear of it, as it does at a valve whose collet is on the
    # face of its own box, the body stays IN, because a search that may tunnel through the
    # fitting it is plumbing will find its cheapest lane straight down the middle of it.
    swallowed = tuple(n for n, q in zip(own, (q0, q1))
                      if n in snap["bodies"] and snap["bodies"][n]["box"]
                      and _pt_box(q, tuple(snap["bodies"][n]["box"])) <= od / 2.0 + floor)
    room = Room.of(snap, tuple(hold) + swallowed)
    out = _heading(n0)                          # the heading a lane must leave on,
    into = _heading(tuple(-c for c in n1))      # and the one it must arrive on

    # TWO PASSES, AND THE SECOND IS NOT A LOOSER ONE. The search works on straight legs and the
    # tube rounds every corner off them, so a corridor that hugs a body down a straight and then
    # turns beside it is found at the floor and then fails once its arcs are drawn. Searching
    # again with the corner's own bulge paid up front is what finds the lane one standoff wider —
    # the one that survives. Both passes are then filtered on the TUBE, so nothing is admitted by
    # the second that the first would have rejected.
    bulge = radius * (math.sqrt(2.0) - 1.0)
    # What the two mouths are allowed to touch: their own fittings, and only within the lead and
    # the arc its first corner turns in.
    mouths = tuple((p, radius + od) for p in (p0, p1))
    made, seen, lat = [], set(), None
    for extra in (0.0, bulge):
        rad = od / 2.0 + floor + extra
        lat = lattice(room, (q0, q1), rad, radius, region_pad=region, cap=cap)
        near = room.near(lat.region)
        free = _Free(lat, near, rad)
        start = tuple(lat.index(i, _nearest(lat.coords[i], q0[i])) for i in range(3))
        goal = tuple(lat.index(i, _nearest(lat.coords[i], q1[i])) for i in range(3))
        shapes = set()
        for pts in _search(lat, free, start, goal, out, into, radius, top * 3 + 4,
                           nonrising):
            # The two lead ends go in EXACTLY and not as the lattice rounded them. A
            # coordinate a ten-millionth off its port turns the last leg into a corner that
            # turns nothing, and the grader then tries to seat a stock radius in it.
            walk = [_at(lat, c) for c in pts]
            walk[0], walk[-1] = q0, q1
            square = _straighten((tuple(p0),) + tuple(walk) + (tuple(p1),))
            skey = tuple(tuple(round(v, 4) for v in p) for p in square)
            if skey in shapes:
                continue                # the same corridor settled twice
            shapes.add(skey)
            whole = _straighten(_smooth(square, near, od, floor, radius, ends))
            key = tuple(tuple(round(v, 4) for v in p) for p in whole)
            if key in seen:
                continue                # two settlements that smooth to one corridor
            seen.add(key)
            lane = Lane(run, whole, od, radius, floor, math.inf, _dist(p0, p1),
                        tuple(_dist(x, y) for x, y in zip(whole, whole[1:])), square)
            if not lane.at_spec:
                continue                # a corner the bender cannot make is not a lane
            # MEASURED ON THE TUBE AND NOT ON THE POLYLINE. The thing that gets built rounds
            # every corner, and the arc stands where the vertex did not. A lane that only clears
            # square is not a lane.
            lane.near = tuple(_nearest_bodies(lane.centreline, od, near, 6, mouths))
            lane.margin = lane.near[0][0]
            if lane.margin < floor - 1e-6:
                continue
            lane.rides = _leg_rides(lane.pts, od, near, mouths)
            lane.lattice = lat
            made.append(lane)
    return order(made, sort)[:top]


def _nearest(coords, v: float) -> float:
    return min(coords, key=lambda c: abs(c - v))


def _at(lat: Lattice, cell: tuple) -> tuple:
    return tuple(lat.coords[i][cell[i]] for i in range(3))


def _heading(axis) -> tuple:
    """A unit vector as (axis index, sign). Raises on anything off the world axes — this
    instrument lays a lane off an axis-aligned mouth only, and one that is not is one it cannot
    lay a lane off."""
    off = [i for i in range(3) if abs(axis[i]) > 1e-6]
    if len(off) != 1 or abs(abs(axis[off[0]]) - 1.0) > 1e-6:
        raise ValueError(f"the mouth faces {tuple(round(c, 4) for c in axis)}, off the world "
                         f"axes — a lane leaves along its collet and this one has no axis to "
                         f"leave along")
    return (off[0], 1 if axis[off[0]] > 0 else -1)


def _straighten(pts: tuple) -> tuple:
    """Drop a waypoint that turns nothing — a lead that carries straight on into the first leg
    is one leg, and counting it as two would price a corner the tube does not have."""
    out = [pts[0]]
    for p in pts[1:]:
        if _dist(out[-1], p) < 1e-9:
            continue
        out.append(p)
    kept = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = kept[-1], out[i], out[i + 1]
        # ON THE UNIT DIRECTIONS, not on the legs. A cross product of two long legs is long even
        # when they are parallel to a part in ten million, so a fixed tolerance on it reads a
        # straight as a corner — and a corner that turns nothing is a corner the grader then
        # tries to seat a radius in.
        u, v = _unit(a, b), _unit(b, c)
        cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
                 u[0] * v[1] - u[1] * v[0])
        if math.sqrt(sum(c_ * c_ for c_ in cross)) > 1e-6:
            kept.append(b)
    kept.append(out[-1])
    return tuple(kept)


def _search(lat: Lattice, free: _Free, start: tuple, goal: tuple, out: tuple, into: tuple,
            radius: float, top: int, nonrising: bool) -> list:
    """Dijkstra over (cell, heading), where a TURNING EDGE IS A WHOLE LEG.

    A step-at-a-time lattice cannot state the rule that matters — a corner backs `r` down each
    of its legs, so a leg between two corners is at least `2r` — because the rule is about the
    leg and not about the step. So an edge that turns runs from a corner to the next corner: it
    picks a heading square to the one it arrived on, and it may stop at any lattice coordinate
    that far along which the line's own free interval reaches. An edge that does NOT turn is the
    same leg carried further and owes nothing, since a leg only ever gets longer that way. So
    every lane that comes back turns at its stock radius, and one that would have to turn
    tighter is never drawn.

    A tube does not turn back through itself, so the reverse of the heading is not a move.

    THE MINIMUM IS NOT TWO RADII, and it is not two radii because the lane is smoothed after.
    A square corner backs a full radius down each leg, so two square corners cannot stand closer
    than `2r` — but two corners `LEAN_STEP` apart are not two square corners, they are one lean,
    and a lean's own corners turn through a shallow angle and want `r·tan(θ/2)` apiece. Barring
    the short step here would delete every corridor that steps sideways while it runs, which is
    most of the machine's. What the search may not do is decide the step is drawable: `_smooth`
    draws it and `_seats` grades it, and a lane whose corners cannot reach the stock radius is
    thrown away there.

    WHAT `WALK_BEND` DOES HERE IS SETTLE STATES, and that is the whole of what it does. Returns
    up to `top` arrivals in the order it reached them. Each state is allowed `VISITS`
    settlements rather than one, which is what makes the second corridor reachable at all — a
    single settlement per state is a shortest-path search and answers only the first question."""
    lead = radius
    coords = lat.coords
    goal_at = tuple(coords[i][goal[i]] for i in range(3))

    def rest(cell, head) -> float:
        """A lower bound on what is left to pay from a cell on a heading.

        The coordinate differences, which no lane can beat because every move costs its own
        length. And the CORNERS it still owes: every axis it is off the goal on, other than the
        one it is running down, takes at least one turn to close, and arriving on a heading it is
        not already on takes at least one more. Admissible — it never over-states — so the search
        still settles in the walk's own cost order and reaches the corridors it can pay for
        first. Without the corner half a lane across this machine explores a million states to
        find its first arrival; with it, a few thousand."""
        far = sum(abs(coords[i][cell[i]] - goal_at[i]) for i in range(3))
        turns = sum(1 for i in range(3)
                    if i != head[0] and cell[i] != goal[i])
        if head != into:
            turns = max(turns, 1)
        return far + WALK_BEND * turns

    # (bound, tie, cost, cell, heading, path). The bound is what orders the heap and the cost is
    # what is paid; the tie-break keeps it total-ordered without comparing tuples of floats.
    minleg = 2.0 * lead
    seen: dict = {}
    tie = itertools.count()
    heap = [(rest(start, out), next(tie), 0.0, start, out, (start,))]
    done, shapes, pops = [], set(), 0
    _search.spent = 0
    while heap and pops < POP_BUDGET:
        _f, _t, cost, cell, head, path = heapq.heappop(heap)
        pops += 1
        key = (cell, head)
        if seen.get(key, 0) >= VISITS:
            continue
        seen[key] = seen.get(key, 0) + 1
        if cell == goal and head == into:
            # DISTINCT CORRIDORS, not distinct settlements. A k-shortest walk over
            # (cell × heading) reaches one corridor a dozen ways — a coordinate stopped at and
            # carried through is the same straight line — and twelve readings of one lane answer
            # nothing. The shape it straightens to is what counts as an answer.
            shape = _straighten(tuple(_at(lat, c) for c in path))
            if shape in shapes:
                continue
            shapes.add(shape)
            done.append(path)
            if len(done) >= top:
                _search.spent = pops
                return done
            continue
        for axis in range(3):
            for sign in (-1, 1):
                if axis == head[0] and sign != head[1]:
                    continue              # a tube does not turn back through itself
                if nonrising and axis == 2 and sign > 0:
                    continue
                turn = 0 if (axis, sign) == head else 1
                for cn, run_len in free.legs(cell, axis, sign, turn, lead, goal, into):
                    # A TURNING LEG UNDER TWO RADII IS NOT FREE. It is a leg no pair of square
                    # corners fits in, so it is a lean or it is nothing — and whether the lean
                    # can be drawn is a question about a diagonal the search never checks.
                    # `SHORT_LEG` is what a corridor pays for depending on one. It is a WEIGHT
                    # and not a measurement: at 0 the search returns staircases `_smooth` then
                    # throws away, and high enough it stops finding the lanes the machine's own
                    # runs are drawn on.
                    short = max(0.0, minleg - run_len) / minleg if turn else 0.0
                    g = cost + run_len + WALK_BEND * (turn + SHORT_LEG * short)
                    heapq.heappush(heap, (g + rest(cn, (axis, sign)), next(tie), g, cn,
                                          (axis, sign), path + (cn,)))
    _search.spent = pops
    return done


def _smooth(pts: tuple, near: tuple, od: float, floor: float, radius: float,
            ends: tuple) -> tuple:
    """The orthogonal lane redrawn the way `_routing.bent` would draw it: a staircase of square
    steps replaced by the single leaning leg that takes them all at once.

    THE LEAN IS ONE LEG AND NOT TWO CORNERS — `_lines._fluid_4` says it about the run this
    instrument was pointed at, and an orthogonal lattice cannot say it at all: a lattice steps
    one world coordinate at a time, so a 20 mm sidestep down a 100 mm fall becomes two right
    angles where the machine draws one gentle move. Searching on the lattice and smoothing after
    is how the search keeps a corridor's shape while the drawing keeps the machine's.

    Greedy and CHECKED: a shortcut is taken only when the straight it replaces two legs with is
    itself clear at the same floor. So smoothing cannot walk a lane through a body — the worst
    it can do is decline, and the square lane stands.

    THE TWO MOUTHS ARE NEVER MOVED and the legs that reach them are held to their collets. A
    line leaves a collet along the collet's own axis and arrives at one against it, within the
    few degrees a push-fit takes (`_routing.COLLET_SKEW`) — so a shortcut that swings either end
    leg past that is declined, however much tube it would save. That is the one thing smoothing
    could otherwise get wrong: a run that reads shorter and will not go in."""
    pts = list(pts)
    changed = True
    while changed and len(pts) > 2:
        changed = False
        for i in range(0, len(pts) - 2):
            for j in range(len(pts) - 1, i + 1, -1):
                a, b = pts[i], pts[j]
                if not _clear(a, b, near, od, floor):
                    continue
                trial = pts[:i + 1] + pts[j:]
                if len(trial) < 2 or not _mouths_hold(trial, ends, radius):
                    continue
                if _seats(trial, od, radius):
                    pts, changed = trial, True
                    break
            if changed:
                break
    return tuple(pts)


def _mouths_hold(pts, ends: tuple, radius: float) -> bool:
    """Does the polyline still leave and enter its two collets the way a tube can?

    Each end leg has to run within `_routing.COLLET_SKEW` of its port's own axis and reach at
    least one stock radius, which is what the first corner needs before it can turn at all. The
    same two conditions `_routing.route` records in `BLOCKED` when an authored run misses them,
    asked here before a lane is offered rather than after it is drawn."""
    import _routing as R
    (p0, n0), (p1, n1) = ends
    if _dist(pts[0], p0) > 1e-6 or _dist(pts[-1], p1) > 1e-6:
        return False
    if _dist(pts[0], pts[1]) < radius - 1e-6 or _dist(pts[-2], pts[-1]) < radius - 1e-6:
        return False
    return (R.leg_skew(pts[0], pts[1], n0) <= R.COLLET_SKEW + 1e-9
            and R.leg_skew(pts[-2], pts[-1], tuple(-c for c in n1)) <= R.COLLET_SKEW + 1e-9)


def _clear(a, b, near: tuple, od: float, floor: float) -> bool:
    """Is the straight from `a` to `b` clear of everything in the room at this floor?

    Against a box the reading is a LOWER bound for a leaning segment, so a straight this calls
    clear is clear and one it calls blocked may not be. That is the direction that cannot invent
    room: smoothing declines a shortcut it cannot prove."""
    want = od / 2.0 + floor
    return all(_seg_box(a, b, box) >= want - 1e-9 for _n, box in near)


def _seats(pts, od: float, radius: float) -> bool:
    """Does every corner of this polyline still turn at its stock radius, and turn no further
    than `MAX_TURN`?

    A shortcut that shortens a leg takes tangent away from the two corners that share it, so it
    is not free: this is the check that stops smoothing where the bender would run out."""
    try:
        run = _graded("smooth", _straighten(tuple(pts)), od, radius)
    except Exception:
        return False
    if any(t > MAX_TURN + 1e-6 for _i, t, _a, _b in run.bends):
        return False
    return run.tightest >= radius - 1e-6


# The sharpest turn a lane may make. Every authored run in this machine turns 90° or less, and
# past 90° an arc's tangent length runs away from it — `r·tan(θ/2)` is `r` at 90° and seven times
# `r` at 164° — so the tube leaves the polyline it was searched on by more than the floor it was
# searched at. `_rounded` is what measures the tube and not the polyline; this is what keeps the
# two from parting company in the first place.
MAX_TURN = 90.0

# How many chords an arc is sampled into when the tube is measured rather than the polyline. Six
# leaves a 90° arc's chord 0.24 mm inside its own curve at R14 — under a tenth of the floor.
ARC_STEPS = 6


def _rounded(run) -> tuple:
    """The polyline redrawn as the TUBE — each corner's square vertex replaced by the tangent arc
    the bender actually puts there, sampled into chords.

    A clearance taken on the polyline is a clearance taken on a shape the machine does not
    contain: the arc cuts the vertex off, so the tube stands where the polyline does not and the
    polyline stands where the tube does not. This is the centreline `_routing.tube` sweeps, which
    is the one `lines-clear` measures.

    The chords lie INSIDE the arc, so a clearance read off them is a hair optimistic on the
    convex side and a hair pessimistic on the concave one. `ARC_STEPS` is what bounds that."""
    pts = [tuple(p) for p in run.pts]
    radii, turns = run.radii, {i: t for i, t, _a, _b in run.bends}
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        if i not in turns:
            out.append(pts[i])
            continue
        r, th = radii[i], math.radians(turns[i])
        u, v = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        t = r * math.tan(th / 2.0)
        a = tuple(pts[i][k] - t * u[k] for k in range(3))
        b = tuple(pts[i][k] + t * v[k] for k in range(3))
        perp = [v[k] - sum(v[m] * u[m] for m in range(3)) * u[k] for k in range(3)]
        nrm = math.sqrt(sum(c * c for c in perp))
        if nrm < 1e-9 or th < 1e-9:
            out.append(pts[i])
            continue
        n = [c / nrm for c in perp]
        c = tuple(a[k] + r * n[k] for k in range(3))
        ra = [a[k] - c[k] for k in range(3)]
        rb = [b[k] - c[k] for k in range(3)]
        out.append(a)
        for s in range(1, ARC_STEPS):
            f = s / ARC_STEPS
            w = [(math.sin((1 - f) * th) * ra[k] + math.sin(f * th) * rb[k]) / math.sin(th)
                 for k in range(3)]
            out.append(tuple(c[k] + w[k] for k in range(3)))
        out.append(b)
    out.append(pts[-1])
    return tuple(out)


def _unit(a, b) -> tuple:
    d = _dist(a, b)
    return tuple((b[i] - a[i]) / d for i in range(3))


def _exempt(near: tuple, od: float, mouths: tuple) -> list:
    """Which body is exempt where. A body is only ever exempt AT a mouth, and only if it is a
    body that mouth is IN or ON — its box within a bore of the point. That is what a fitting the
    run plugs into looks like, and what a fitting seated hard against that one looks like;
    anything standing merely near the mouth is measured like the rest of the machine."""
    out = []
    for p, r in mouths:
        p = tuple(p)
        out.append((p, r, {n.split("[")[0] for n, box in near if _pt_box(p, box) <= od}))
    return out


def _nearest_bodies(pts: tuple, od: float, near: tuple, count: int = 6, mouths=()) -> list:
    """The `count` things the lane comes nearest to, as `(clearance, name)`, tightest first —
    with a run's own chopped tube reported under the run's name and not under a chord's.

    A BOX BOUNDS THE TRUTH FROM BELOW. `_seg_box` is the distance to a body's BOX and cannot go
    negative, so the figure saturates at `−Ø/2` the moment the centreline enters one: a negative
    reading here is the box failing to certify the segment and is never a measured overlap. Some
    of the machine's own authored runs read negative and every one is clear in the exact world —
    `selftest` names them, and `verify` is what settles any of them.

    A MOUTH IS NOT A CLASH. A lane ends ON the face of the fitting it plugs into, so the last
    stretch of it reads zero against that fitting's own box and would swamp every other reading —
    and not only against that fitting: the machine seats fittings hard against each other
    (`co2-inlet` bears on `gasher-co2`, the ASSE chain on its union), so what a mouth sits in is
    a cluster and a reading inside it is a seating and not a clearance. `mouths` is each mouth's
    point and the reach the exemption covers — the lead and the arc its first corner turns in,
    and nothing past that. Everything beyond is measured like any other body, which is what stops
    a lane running back through the fitting it just left."""
    skip = _exempt(near, od, mouths)
    best: dict = {}
    for a, b in zip(pts, pts[1:]):
        at = set()
        for p, r, who_at in skip:
            if _dist(a, p) <= r or _dist(b, p) <= r:
                at |= who_at
        for n, box in near:
            who = n.split("[")[0]
            if who in at:
                continue
            g = _seg_box(a, b, box) - od / 2.0
            if g < best.get(who, math.inf):
                best[who] = g
    if not best:
        return [(math.inf, "nothing in the room")]
    return sorted(((g, n) for n, g in best.items()))[:count]


def _leg_rides(pts: tuple, od: float, near: tuple, mouths=()) -> tuple:
    """WHICH SUB-ASSEMBLY EACH LEG LIES ON — one row per leg, as
    `(leg index, gap, nearest body, sub-assembly)`.

    A leg is laid against whatever it runs closest to, and what that body is BOLTED TO is what
    decides when in the build the leg can be laid and whether a hand still reaches it afterwards.
    `_scorecard.MOUNTS` is the table that carries it. A leg with nothing in reach names none."""
    skip = _exempt(near, od, mouths)
    out = []
    for n, (a, b) in enumerate(zip(pts, pts[1:])):
        at = set()
        for p, r, who_at in skip:
            if _dist(a, p) <= r or _dist(b, p) <= r:
                at |= who_at
        best = None
        for name, box in near:
            if name.split("[")[0] in at:
                continue
            g = _seg_box(a, b, box) - od / 2.0
            if best is None or g < best[0]:
                best = (g, name)
        if best is None:
            out.append((n, math.inf, "", "nothing in reach"))
        else:
            out.append((n, best[0], best[1].split("[")[0], _rides(best[1])))
    return tuple(out)


def _seg_box(a, b, box) -> float:
    """Least distance from a segment to an axis-aligned box. Exact when the segment is axis
    aligned, and a lower bound otherwise — the direction that cannot invent clearance."""
    if all(abs(b[i] - a[i]) < 1e-9 for i in range(3)):
        return _pt_box(a, box)
    # Walk the segment at the box's own face planes plus the ends: for an axis-aligned segment
    # the distance is monotone between them, so the sampled minimum is the true one.
    ts = {0.0, 1.0}
    for i in range(3):
        d = b[i] - a[i]
        if abs(d) > 1e-9:
            for v in (box[2 * i], box[2 * i + 1]):
                t = (v - a[i]) / d
                if 0.0 < t < 1.0:
                    ts.add(t)
    return min(_pt_box(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)), box)
               for t in sorted(ts))


def _pt_box(p, box) -> float:
    d = [max(box[2 * i] - p[i], 0.0, p[i] - box[2 * i + 1]) for i in range(3)]
    return math.sqrt(sum(x * x for x in d))


# --- the lane a run is in now ---------------------------------------------

def authored(run: str, floor: float = FLOOR, snap: dict = None) -> Lane:
    """The run AS DRAWN, put through the same reader as a searched lane, so a table has the thing
    it is being read against in it.

    Its `path` is its own developed length off `_routing.Run.length` rather than this module's
    square-corner arithmetic — the authored run leans, and the arithmetic here is orthogonal."""
    snap = snapshot() if snap is None else snap
    spec = snap["runs"][run]
    room = Room.of(snap, (run, f"tube-{run}"))
    pts = tuple(tuple(p) for p in spec["pts"])
    mouths = tuple((p, spec["bend"] + spec["diam"]) for p in (pts[0], pts[-1]))
    region = tuple(v for i in range(3)
                   for v in (min(p[i] for p in pts) - 20.0, max(p[i] for p in pts) + 20.0))
    lane = Lane(run, pts, spec["diam"], spec["bend"], floor, math.inf,
                _dist(pts[0], pts[-1]),
                tuple(_dist(a, b) for a, b in zip(pts, pts[1:])))
    near = room.near(region)
    lane.near = tuple(_nearest_bodies(lane.centreline, spec["diam"], near, 6, mouths))
    lane.margin = lane.near[0][0]
    lane.rides = _leg_rides(lane.pts, spec["diam"], near, mouths)
    lane.drawn = spec["length"]
    return lane


# --- the exact world ------------------------------------------------------

def verify(lane: Lane, clearance: float = 0.0, skip=()) -> str:
    """A searched lane in the exact world — printed walls, seam lips, ribs and boss chains — as
    the solid it would be swept into.

    Everything above is a claim about boxes and centrelines. This is the claim about the machine,
    and they are not the same answer: a box-clear lane standing in a seam lip clashes here, and a
    box-blocked lane standing 0.2 mm off the rib it lies in is clear here. This is the one that
    counts. It holds out exactly what the search held out, and for the same reason.

    It builds `probe`'s world, which is the two minutes the snapshot exists to avoid — so it is
    asked of ONE lane, after the enumeration has chosen which one is worth asking about."""
    import probe
    import _clearing
    import _routing as R
    w = probe.world()
    # SWEPT BY THE PACK'S OWN SWEEPER. `_routing.tube` is what drew every tube in the world this
    # is measured against — same arcs off `seat_radii`, same bore off the port — so a lane and
    # the runs it is compared with are the same kind of solid. A sweeper written here would be a
    # second opinion about what a bent tube is, and the clash it reported would be about that.
    # A HAIR UNDER THE SEATED RADIUS. A lane's leads are the minimum a corner can turn on — the
    # search takes exactly one radius and no more — so a corner can seat its whole tangent in a
    # leg and leave no straight at all, and a sweep along an edge of no length is not a sweep.
    # Turning every corner a thousandth tighter leaves each one its sliver. The solid is that
    # much slimmer at its corners than the lane it stands for, which is the direction that
    # reports a clash rather than hiding one.
    solid = R.tube(_graded(lane.run, lane.pts, lane.od, lane.radius * (1.0 - 1e-3)))
    holding = set(skip) | {n for n in w.names
                           if n.replace("tube-", "") == lane.run or n == lane.run}
    spec = snapshot()["runs"].get(lane.run)
    if spec:
        holding |= {spec["frm"].split(".")[0], spec["to"].split(".")[0]}
    # A body standing further off than the tube is wide is not part of this lane's story, so
    # that is how far each gap is read.
    horizon = clearance + lane.od
    worst, hits = math.inf, []
    for name in w.names:
        if name in holding:
            continue
        g = _clearing.gap(solid, w.solid(name), horizon)
        if g < worst:
            worst = g
        if g <= clearance + 1e-9:
            hits.append(f"{name} {g:.3f}")
    out = [f"{lane.run}: {w.measured}, holding out {', '.join(sorted(holding))}",
           f"  tightest clearance {worst:.3f} mm" if worst < horizon
           else f"  nothing stands within {horizon:.3f} mm"]
    out.append("  " + ("CLASH: " + "; ".join(hits) if hits else "clear of every body"))
    return "\n".join(out)


# --- selftest -------------------------------------------------------------

BIG = (-500.0, 500.0, -500.0, 500.0, -500.0, 500.0)
DOWN_ONE_LINE = (((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((0.0, -200.0, 0.0), (0.0, 1.0, 0.0)))


def _room_of(**bodies) -> dict:
    return {"bodies": {n: {"tag": "component", "box": list(b)} for n, b in bodies.items()},
            "runs": {}, "ports": {}, "cavity": list(BIG), "sources": {}, "taken": 0}


def selftest() -> int:
    """Known-answer controls on the solver, then the machine that exists through the filter."""
    fails = []

    def check(name, got, want, tol=1e-6):
        ok = abs(got - want) <= tol if isinstance(want, float) else got == want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got} (want {want})")
        if not ok:
            fails.append(name)

    def one(ends, top=3, floor=FLOOR, **bodies):
        return lanes("probe", ends=ends, od=6.35, radius=14.0, top=top, floor=floor,
                     snap=_room_of(**bodies))

    print("the lane solver — known answers")
    got = one(DOWN_ONE_LINE)
    check("two mouths down one empty line: bends", got[0].bends, 0)
    check("two mouths down one empty line: path", got[0].path, 200.0)
    check("and nothing in an empty room is shorter than the straight line",
          all(l.path > got[0].path - 1e-9 for l in got[1:]), True)

    # THE LEAN. A 10 mm sidestep down a 200 mm run is one gentle move, not two right angles —
    # `_lines._fluid_4` says so about the run this instrument was pointed at, and an orthogonal
    # lattice cannot say it at all. The search steps it square and `_smooth` draws it.
    off10 = (((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((10.0, -200.0, 0.0), (0.0, 1.0, 0.0)))
    got = one(off10, top=1)
    check("a 10 mm offset is one leaning leg: bends", got[0].bends, 0)
    check("a 10 mm offset is one leaning leg: leans", got[0].leans, 1)
    check("and it costs barely more than the straight",
          round(got[0].path, 2), round(math.dist((0, 0, 0), (10, -200, 0)), 2), tol=0.01)

    # A step wide enough for two square corners is drawn as two square corners: `2r` of tangent
    # is exactly what a 90° pair needs, and 40 mm has it.
    got = one((((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((40.0, -200.0, 0.0), (0.0, 1.0, 0.0))),
              top=1)
    check("a 40 mm offset is two square corners", (got[0].bends, got[0].leans), (2, 0))
    check("and no leg of it is under two radii",
          min(got[0].legs[1:-1]) >= 2 * 14.0 - 1e-6, True)

    # One slab across the line between two facing collinear mouths. Out and back is FOUR corners
    # — there is no offset to spend them on — and the lane has to clear the slab by the floor.
    got = one(DOWN_ONE_LINE, slab=(-40.0, 40.0, -120.0, -80.0, -40.0, 40.0))
    check("a slab across it: bends", got[0].bends, 4)
    check("a slab across it: clears the slab", got[0].margin >= FLOOR - 1e-6, True)
    check("a slab across it: steps past the slab's own width",
          max(abs(p[0]) for p in got[0].pts) >= 40.0 + 6.35 / 2 + FLOOR - 1e-6, True)
    check("a slab across it: turns no further than the cap",
          got[0].worst_turn <= MAX_TURN + 1e-6, True)

    # A 10 mm slot a 0.5 mm floor fits through and a 2 mm floor does not. `fluid-4`'s own case in
    # miniature — the source pair's limbs leave 7.890 mm for a Ø6.35 line — and the control on
    # the floor being a real parameter rather than a decoration.
    slot = dict(west=(-60.0, -5.0, -120.0, -80.0, -40.0, 40.0),
                east=(5.0, 60.0, -120.0, -80.0, -40.0, 40.0))
    got = one(DOWN_ONE_LINE, top=1, floor=0.5, **slot)
    check("a 10 mm slot at a 0.5 mm floor: straight through", got[0].bends, 0)
    got = one(DOWN_ONE_LINE, top=1, floor=2.0, **slot)
    check("the same slot at a 2.0 mm floor: goes around", got[0].bends > 0, True)

    # SMOOTHING MAY NOT WALK A LANE THROUGH A BODY. A block standing in the corner a shortcut
    # would cut is a shortcut the lane does not get: it stays square, and stays clear.
    got = one((((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((80.0, -200.0, 0.0), (0.0, 1.0, 0.0))),
              top=1, corner=(20.0, 70.0, -170.0, -40.0, -40.0, 40.0))
    check("a block in the corner: the lane stays square", got[0].leans, 0)
    check("a block in the corner: and stays clear", got[0].margin >= FLOOR - 1e-6, True)

    # THE COLUMNS DISAGREE, WHICH IS WHY THERE IS NO RANKING. Round a slab, the four-corner lane
    # that hugs it is the shortest and the one that swings wide holds the most room; ordering on
    # one puts the other last.
    got = one(DOWN_ONE_LINE, top=6, slab=(-40.0, 40.0, -120.0, -80.0, -40.0, 40.0))
    by_path = order(got, "path")
    by_margin = order(got, "margin")
    check("ordering on tube and ordering on clearance are different orders",
          len(got) > 1 and by_path[0] is not by_margin[0], True)

    print("the reader — a lane's own arithmetic, and the tube it stands for")
    l = Lane("probe", ((0.0, 0.0, 0.0), (0.0, -100.0, 0.0), (50.0, -100.0, 0.0)),
             6.35, 14.0, 1.0, 9.9, 111.8, (100.0, 50.0))
    check("one corner", l.bends, 1)
    check("developed length takes the arc back out",
          l.path, 150.0 - 14.0 * (2.0 - math.pi / 2.0))
    # The arc's own geometry: a 90° corner at R14 passes `r(√2 − 1)` inside its vertex, which is
    # the whole reason a clearance is taken on `_rounded` and not on the polyline.
    arc = l.centreline
    check("the tube passes inside the vertex by r(√2 − 1)",
          round(min(_dist(p, (0.0, -100.0, 0.0)) for p in arc), 4),
          round(14.0 * (math.sqrt(2.0) - 1.0), 4), tol=0.02)
    check("lowest z is read off the tube", l.lowest, 0.0)

    print("the world — the machine that exists, through the same filter")
    snap = snapshot()
    print(f"       {measured(snap)}")
    check("the snapshot holds the whole machine", len(snap["bodies"]) >= 80, True)
    check("and every routed run", len(snap["runs"]) >= 19, True)
    unfair = sorted(n for n, b in snap["bodies"].items() if b.get("slabs"))
    print(f"       sliced rather than boxed ({len(unfair)}): {', '.join(unfair) or 'none'}")

    # WHAT THE BOX READER CAN CERTIFY, AND WHAT IT CANNOT. A box bounds the truth from below, so
    # a run reading clear here is clear and a run reading blocked has proven nothing — the figure
    # saturates at −Ø/2 the moment a centreline enters a box. The runs it cannot certify are
    # named with the body whose box swallowed them, because a blind spot printed is a blind spot
    # a reader can work around and a blind spot asserted as a clash is an instrument nobody
    # trusts. Every one of these is clear in `probe`'s exact world; `verify` is what settles one.
    read = sorted((authored(rid, floor=0.0).margin, rid) for rid in snap["runs"])
    blind = [(m, rid) for m, rid in read if m < -1e-6]
    print(f"       the box reader certifies {len(read) - len(blind)} of {len(read)} authored "
          f"runs clear")
    for m, rid in blind:
        a = authored(rid, floor=0.0)
        who = a.near[0][1]
        fill = snap["bodies"].get(who, {}).get("fill")
        print(f"       uncertifiable: {rid:<10} {m:8.3f} against {who}"
              + (f", which fills {fill:.2f} of its box" if fill is not None else ""))

    # AND THE ONE CLASS WHERE THE BOX IS THE BODY. A routed run is carried as its own centreline
    # chopped into chords, so a chord's box hugs the tube to a hair — which makes a negative
    # reading between two runs a real overlap and not a blind spot. There are none.
    worst_pair = (math.inf, "", "")
    for rid in snap["runs"]:
        spec = snap["runs"][rid]
        pts = tuple(tuple(p) for p in spec["pts"])
        region = tuple(v for i in range(3)
                       for v in (min(p[i] for p in pts) - 20.0, max(p[i] for p in pts) + 20.0))
        tubes = [(n, b) for n, b in Room.of(snap, (rid, f"tube-{rid}")).near(region) if "[" in n]
        if not tubes:
            continue
        g, who = _nearest_bodies(
            authored(rid, floor=0.0).centreline, spec["diam"], tubes, 1,
            tuple((p, spec["bend"] + spec["diam"]) for p in (pts[0], pts[-1])))[0]
        if g < worst_pair[0]:
            worst_pair = (g, rid, who)
    check("no authored run reads blocked against another authored run", worst_pair[0] > -1e-6,
          True)
    print(f"       tightest run against run: {worst_pair[1]} / {worst_pair[2]} at "
          f"{worst_pair[0]:.3f} mm")

    # AND THE SEARCH FINDS THE MACHINE'S OWN LANE. `carb-1` crosses the machine at 0.775 mm,
    # the tightest corridor in it this reader can see all of; searched at that floor, what comes
    # back is that corridor — same stock, same corners, same clearance. An instrument that
    # cannot re-find the lane the machine is built to has not been pointed at the machine.
    got = lanes("carb-1", top=4, floor=0.73, cap=34)
    drawn = authored("carb-1")
    check("carb-1: the search re-finds the lane the machine is built to",
          bool(got) and abs(got[0].path - drawn.drawn) < 0.1
          and abs(got[0].margin - drawn.margin) < 0.01
          and got[0].bends == drawn.bends, True)
    if got:
        print(f"       found {got[0].path:.1f} mm / {got[0].bends} bends / "
              f"{got[0].margin:.3f} mm / low z {got[0].lowest:.1f}    "
              f"drawn {drawn.drawn:.1f} mm / {drawn.bends} / {drawn.margin:.3f} / "
              f"low z {drawn.lowest:.1f}")
        print(f"       and it lies on {' · '.join(got[0].on)}")
    # And the gate's own floor is where it stops being a lane at all.
    check("carb-1: and no lane at all at the gate's own floor",
          lanes("carb-1", top=1, floor=FLOOR, cap=34), [])

    print(f"\n{'PASS' if not fails else 'FAIL: ' + ', '.join(sorted(set(fails)))}")
    return 1 if fails else 0


# --- CLI ------------------------------------------------------------------

def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fresh", action="store_true",
                    help="rebuild the world if the tree has moved, instead of reading the "
                         "newest snapshot and saying so")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("snapshot", help="take the world a query reads, and say where it is")
    p.add_argument("--reload", action="store_true", help="re-take it even if nothing moved")
    sub.add_parser("runs", help="every authored run through the reader, tightest first")
    p = sub.add_parser("lanes", help="every corridor between a run's two mouths")
    p.add_argument("run")
    p.add_argument("--sweep", action="store_true",
                   help="walk the floor down until a lane appears — the room the corridor has")
    p.add_argument("--top", type=int, default=6)
    p.add_argument("--floor", type=float, default=FLOOR)
    p.add_argument("--cap", type=int, default=LATTICE_CAP)
    p.add_argument("--region", type=float, default=REGION)
    p.add_argument("--sort", choices=sorted(COLUMNS), default=None,
                   help="order the candidates on ONE column; without it the order is the "
                        "walk's own and is not a ranking")
    p.add_argument("--full", action="store_true", help="the first candidate leg by leg")
    p = sub.add_parser("verify", help="one lane in probe's exact world")
    p.add_argument("run")
    p.add_argument("--lane", type=int, default=1)
    p.add_argument("--floor", type=float, default=FLOOR)
    p.add_argument("--sort", choices=sorted(COLUMNS), default=None)
    p.add_argument("--clearance", type=float, default=0.0)
    sub.add_parser("selftest", help="known-answer controls, then the real machine")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "snapshot":
        snap = snapshot(reload=args.reload, build=True)
        print(measured(snap))
        c = snap["cavity"]
        print(f"cavity x[{c[0]:.1f}, {c[1]:.1f}] y[{c[2]:.1f}, {c[3]:.1f}] "
              f"z[{c[4]:.1f}, {c[5]:.1f}]")
        print(f"cached at {_cache_path()}")
        return 0

    snap = snapshot(build=args.fresh)
    print(measured(snap))
    print()
    if args.cmd == "runs":
        print(f"{'run':<10} {'ends':>6} {'path':>7} {'bend':>4} {'detour':>6} {'margin':>7} "
              f"{'low z':>6}   nearest")
        for margin, rid in sorted((authored(r).margin, r) for r in snap["runs"]):
            a = authored(rid)
            print(f"{rid:<10} {a.span:6.1f} {a.drawn:7.1f} {a.bends:4d} "
                  f"{a.drawn / a.span:6.3f} {margin:7.3f} {a.lowest:6.1f}   "
                  + ", ".join(f"{n} {g:.2f}" for g, n in a.near[:3]))
        print("\na negative margin is the BOX failing to certify the run, never a measured "
              "overlap — see `selftest`.")
        return 0
    if args.cmd == "lanes":
        drawn = authored(args.run, floor=args.floor)
        if args.sweep:
            print(f"{args.run}: ends {drawn.span:.1f} mm apart, drawn {drawn.drawn:.1f} mm at "
                  f"{drawn.margin:.3f} mm — the floors a lane is found at")
            for f in (4.0, 3.0, 2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.2):
                got = lanes(args.run, top=1, floor=f, cap=args.cap, region=args.region)
                print(f"  floor {f:4.2f}  " + (f"{len(got)} lane: {got[0].path:7.1f} mm, "
                                               f"{got[0].bends} bends, margin "
                                               f"{got[0].margin:.3f}, low z "
                                               f"{got[0].lowest:.1f}   {got[0].vector()}"
                                               if got else "none"))
            return 0
        got = lanes(args.run, top=args.top, floor=args.floor, cap=args.cap,
                    region=args.region, sort=args.sort)
        lat = got[0].lattice if got else None
        print(f"{args.run}: ends {drawn.span:.1f} mm apart, floor {args.floor:g} mm, "
              f"bend R{drawn.radius:g}, Ø{drawn.od:g}")
        if lat:
            print(f"lattice {'×'.join(str(len(c)) for c in lat.coords)} = {lat.size:,} cells, "
                  f"thinned at {max(lat.step):.1f} mm, region "
                  + " ".join(f"{'xyz'[i]}[{lat.region[2*i]:.0f}, {lat.region[2*i+1]:.0f}]"
                             for i in range(3)))
        spent = getattr(_search, "spent", 0)
        if spent >= POP_BUDGET:
            print(f"THE WALK RAN OUT OF PATIENCE at {spent:,} states — what is below is what it "
                  f"had reached,\nnot what the machine holds. Raise POP_BUDGET or narrow "
                  f"--region.")
        print(f"order: {args.sort or 'the walk’s own, which is not a ranking'}")
        print()
        print(table(args.run, got, drawn))
        print("\nan orthogonal lane is an UPPER bound on its corridor — the authored run leans, "
              "and a leaning\nversion of any lane here is shorter than the square one shown. "
              "`verify` is the exact answer.")
        if args.full and got:
            print()
            print(got[0].report())
        return 0
    if args.cmd == "verify":
        got = lanes(args.run, top=max(args.lane, 6), floor=args.floor, sort=args.sort)
        if len(got) < args.lane:
            print(f"{args.run}: only {len(got)} lane(s) at a {args.floor:g} mm floor")
            return 1
        print(verify(got[args.lane - 1], clearance=args.clearance))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
