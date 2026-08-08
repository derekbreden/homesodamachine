"""Lanes and arrangements — every corridor a run could take, and every pose its ends could
stand in, ranked against each other.

`probe` asks about the world as it stands. `fit` asks about a body that is not in it yet. Both
hold everything else frozen, so both answer one pose at a time, and a question about how a SET
of parts goes together comes back as a column of clearances that never adds up to a design.
This is the third instrument, and it varies two things at once:

  * THE LANE. A run's ends fix its span; what it costs is the corridor it is drawn through, and
    the card only ever reads the corridor the run is in. `fluid-4` runs 152.6 mm for ends 88.6
    apart and passes both source coils at 0.770 mm — the card names the pins of that lane and
    never asks whether the run belongs in it. `lanes()` asks: it searches every orthogonal
    corridor between the two mouths that keeps a stated floor off every body, and ranks them.
  * THE POSE. A fitting hung off another fitting's mouth has a roll about that joint and a
    reach along it, and a chain of them has one per link. `rank()` varies those together, moves
    every mouth downstream of the one it turned, and re-costs the lanes the new mouths oblige.

    import arrange

    print(arrange.lanes("fluid-4")[0].report())      # the cheapest corridor for that run
    sp = arrange.west_lane()                         # the space: every choice and its values
    print(sp.report())                               # what it varies, what it holds, how many
    print(arrange.rank(sp, top=10)[0].report())

What a lane costs is the TUBE and the CORNERS, on the machine's own terms. A corner backs a
tangent arc `r·tan(θ/2)` down each of its legs and a leg between two corners pays it at both
ends, so a leg shorter than `2r` is a corner drawn square — which is what `bend-radius` grades.
The search will not emit one: every interior leg it draws is at least two stock radii long, and
every lead off a port is at least one. So a lane it returns is a lane that turns at spec, and
its length is the developed length of stock, arcs taken out, directly comparable with the card's
`need.path`.

The lane search is ORTHOGONAL and the authored runs LEAN — `_routing.bent` draws a leg that
steps two coordinates at once, and two of `fluid-4`'s do. A leaned version of a corridor is
shorter than the square one, so a corridor's orthogonal cost is an UPPER BOUND on what that
corridor can be drawn at. That is the safe direction: a lane that beats the authored run
squarely beats it leaning too.

Everything is measured against BOXES, and the direction that runs matters. Here the boxes are
the OBSTACLES, not the candidate — so a segment clear of a body's box is clear of the body, and
that is proven, while a segment its box overlaps has proven nothing and may still be free. The
filter can therefore only ever DELETE lanes, never admit a bad one. Two categories cannot be
boxed at all and are not:

  * the routed tubes, whose boxes are mostly air — each is carried as its own centreline
    polyline, segment by segment, which for a swept cylinder is the body itself;
  * the printed pieces, whose boxes are the whole machine — the interior `cavity` stands in for
    them, and `verify` is what measures a lane against the walls exactly.

So a rank is a SHORTLIST. `verify` carries one lane into `probe`'s exact world — printed walls,
seam lips, ribs and all — and that is the answer.

From the shell:

    tools/cad-venv/bin/python hardware/scripts/arrange.py snapshot
    tools/cad-venv/bin/python hardware/scripts/arrange.py lanes fluid-4 --top 8
    tools/cad-venv/bin/python hardware/scripts/arrange.py lanes fluid-2 --floor 2.0
    tools/cad-venv/bin/python hardware/scripts/arrange.py space
    tools/cad-venv/bin/python hardware/scripts/arrange.py rank --top 12
    tools/cad-venv/bin/python hardware/scripts/arrange.py verify fluid-4 --lane 1
    tools/cad-venv/bin/python hardware/scripts/arrange.py selftest

`selftest` runs the solver against known-answer geometry — an empty room, a room with one slab
across the line, a floor that closes the only gap, the leg rule that keeps a corner at spec, the
lattice's own bounds — then puts the machine that EXISTS through the same filter, which is the
control the whole thing stands on: an instrument that rejects the built machine is rejecting
reality. Run it before trusting a ranking.
"""

import argparse
import heapq
import itertools
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_ML = _HW / "manifold-layout"
sys.path.insert(0, str(_HW / "scripts"))

# The env a read-only run wants, set BEFORE the build modules are imported. This scans and
# exports nothing, so it must not take the global build lock: holding it makes every later
# build follow this process instead of running.
os.environ.setdefault("HSM_SKIP_THUMBNAILS", "1")
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")


# --- the weights ----------------------------------------------------------

# The gate's own floor. `_scorecard`'s `clearance-floor` reads a millimetre between two things
# the machine does not seat together, and a lane drawn under it is a lane that fails the card.
FLOOR = 1.0

# What a corner is worth against a millimetre of tube. A bend is not free — it is a fixture, a
# spring-back and a place the bore necks — and this is the exchange rate the ranking uses. It is
# a WEIGHT, not a measurement: change it and the ranking re-orders, which is why every lane
# reports its tube and its corners separately as well as its cost.
BEND_MM = 25.0

# The shortest step the search will take sideways while it runs. It is NOT a bend rule — a step
# this short is drawn as one lean and not two corners, and `_smooth` is where that happens. It is
# the lattice's own grain: two coordinates nearer than this are one coordinate as far as a tube
# is concerned, and letting the search stop between them only makes the state space bigger.
LEAN_STEP = 4.0

# How far outside the box of a run's two mouths a lane may wander, and the region the lattice is
# cut from. A lane is not searched beyond it — which is a bound on the QUERY and not a claim
# that nothing out there would serve.
REGION = 90.0

# The most coordinates the lattice carries per axis. The search is over (cell × heading), so
# this is the knob that decides whether a query takes a second or a minute; the coordinates kept
# are the ones a shortest orthogonal path can turn on — an obstacle's own faces, stood off by
# the tube's half-section and the floor — thinned until they fit.
LATTICE_CAP = 22


# --- the snapshot ---------------------------------------------------------
#
# One `build_front_half()` is a minute and a half, and a scan wants the same world thousands of
# times. So the world is taken ONCE and written down flat: every body's box, every routed run's
# centreline, every port's position and axis, and the interior the printed pieces leave. The
# cache is keyed on the SOURCE — the size and mtime of every module the pose of anything
# depends on — so a tree that has moved rebuilds rather than answering from a stale world.

_SOURCES = ("manifold-layout/front_half.py", "manifold-layout/_lines.py",
            "manifold-layout/manifold_layout.py", "scripts/_routing.py",
            "printed-parts/enclosure/enclosure/enclosure.py")

_SNAP: dict = {}


def _source_key() -> str:
    bits = []
    for rel in _SOURCES:
        p = _HW / rel
        st = p.stat()
        bits.append(f"{rel}:{st.st_size}:{int(st.st_mtime)}")
    return str(abs(hash(tuple(bits))))


def _cache_path() -> Path:
    return Path(tempfile.gettempdir()) / f"hsm-arrange-{_source_key()}.json"


def take() -> dict:
    """Build the machine and write down what a lane search needs of it.

    Bodies as boxes, runs as centrelines, ports as (position, axis, bore), and the cavity the
    box's four pieces leave. Nothing here is a summary of a measurement — every number is the
    placed geometry's own, read off the same assembly the build exports."""
    sys.path.insert(0, str(_ML))
    import front_half as fh                                  # noqa: E402
    a = fh.build_front_half()
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
        bodies[name] = {"tag": tag,
                        "box": [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]}
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
            "source": _source_key()}


def _tag(name: str) -> str:
    """The role a body's name carries — `probe._source`'s own split, restated here so a
    snapshot can be read back without building anything."""
    if name.startswith("enclosure-"):
        return "piece"
    if name.startswith("tube-") or name.startswith("turn-") or name.startswith("step-"):
        return "run"
    return {"display": "display", "hopper-funnel": "funnel"}.get(name, "component")


def pinned() -> tuple:
    """Every snapshot on disk, newest first — what a pinned read may fall back to."""
    d = Path(tempfile.gettempdir())
    return tuple(sorted(d.glob("hsm-arrange-*.json"), key=lambda p: p.stat().st_mtime,
                        reverse=True))


def snapshot(reload: bool = False, pin: bool = None) -> dict:
    """The world as a flat table, from the cache when the tree has not moved.

    `pin` reads the newest snapshot on disk WHATEVER the tree now says, and says so on the way
    past. It is for a reading taken while the machine is being edited under it: the alternative
    is that every query rebuilds and a scan never finishes. A pinned answer is an answer about
    the world the snapshot holds, and the caller has to mean it — `HSM_ARRANGE_PIN=1` is the
    same switch from the shell."""
    pin = bool(os.environ.get("HSM_ARRANGE_PIN")) if pin is None else pin
    if _SNAP and not reload:
        return _SNAP
    cache = _cache_path()
    if cache.exists() and not reload:
        _SNAP.update(json.loads(cache.read_text()))
        return _SNAP
    if pin and not reload:
        have = pinned()
        if have:
            print(f"arrange: PINNED to {have[0].name} — the tree has moved since it was taken, "
                  f"and this reading is about the machine in it", file=sys.stderr)
            _SNAP.update(json.loads(have[0].read_text()))
            return _SNAP
    snap = take()
    cache.write_text(json.dumps(snap))
    _SNAP.clear()
    _SNAP.update(snap)
    return _SNAP


# --- the room a lane has to miss ------------------------------------------

def _boxes_of(snap: dict, hold: tuple) -> tuple:
    """Every obstacle as an axis-aligned box, with the held bodies out.

    A ROUTED RUN IS NOT ITS BOX. `fluid-18` crosses the machine and climbs, and its box is a
    slab of mostly air through half the cabinet — held as one box it would delete every lane
    that goes anywhere near it. So each run comes in as its own centreline SEGMENTS, each boxed
    on its own two ends and grown by its own half-section, which for a swept cylinder is the
    tube itself wherever the leg is axis-aligned and a shade fat wherever it leans.

    The printed PIECES are not here at all, for the opposite reason: a piece's box is the whole
    machine. `cavity` stands in for them and `verify` measures against them exactly."""
    out = []
    for name, b in snap["bodies"].items():
        if name in hold or b["tag"] in ("piece", "run"):
            continue
        out.append((name, tuple(b["box"])))
    for rid, r in snap["runs"].items():
        if rid in hold or f"tube-{rid}" in hold:
            continue
        rad = r["diam"] / 2.0
        for i, (p, q) in enumerate(zip(r["pts"], r["pts"][1:])):
            out.append((f"{rid}[{i}]",
                        (min(p[0], q[0]) - rad, max(p[0], q[0]) + rad,
                         min(p[1], q[1]) - rad, max(p[1], q[1]) + rad,
                         min(p[2], q[2]) - rad, max(p[2], q[2]) + rad)))
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
    """One corridor: the polyline it turns on, what it costs, and what it clears.

    `path` is the DEVELOPED length — the stock the run would cut, arcs taken out — so it is the
    same number the card's `need.path` reports. `margin` is the tightest the lane comes to
    anything in the room, exact against the tube centrelines and box-bounded against the bodies.
    `seated` is the smallest radius any of its corners can actually turn at, off `_routing`'s own
    solver: a lane whose corners cannot reach the stock's minimum is a lane the bender cannot
    make, and it is said here rather than left in the ranking."""
    run: str
    pts: tuple
    od: float
    radius: float
    floor: float
    margin: float
    span: float
    legs: tuple
    square: tuple = ()          # the orthogonal lane it was smoothed from

    def __post_init__(self):
        self._run = _graded(self.run, self.pts, self.od, self.radius)

    @property
    def bends(self) -> int:
        return len(self._run.bends)

    @property
    def path(self) -> float:
        return self._run.length

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
    def cost(self) -> float:
        return self.path + BEND_MM * self.bends

    @property
    def leans(self) -> int:
        """How many of its legs step more than one coordinate — what `_routing.bent` draws and
        `_routing.route` cannot."""
        n = 0
        for a, b in zip(self.pts, self.pts[1:]):
            if sum(1 for i in range(3) if abs(b[i] - a[i]) > 1e-6) > 1:
                n += 1
        return n

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
               f"{'' if self.bends == 1 else 's'} ({self.leans} leaning), cost {self.cost:.0f}",
               f"  ends {self.span:.1f} mm apart, detour {self.detour:.3f}×, "
               f"margin {self.margin:.3f} mm (floor {self.floor:.2f}), "
               f"corners seat R{self.seated:.2f} of R{self.radius:g}"
               f"{'' if self.at_spec else '  — UNDER SPEC'}", ""]
        for n, (a, b) in enumerate(zip(self.pts, self.pts[1:])):
            i = max(range(3), key=lambda k: abs(b[k] - a[k]))
            lean = "~" if sum(1 for k in range(3) if abs(b[k] - a[k]) > 1e-6) > 1 else " "
            out.append(f"  leg {n + 1} {lean} {'xyz'[i]} {_dist(a, b):7.2f} mm   "
                       f"({a[0]:7.2f}, {a[1]:7.2f}, {a[2]:7.2f}) → "
                       f"({b[0]:7.2f}, {b[1]:7.2f}, {b[2]:7.2f})")
        for i, turn, la, lb in self._run.bends:
            out.append(f"  corner at {i}  {turn:5.1f}°  seats R{self._run.radii[i]:5.2f}  "
                       f"legs {la:.1f} / {lb:.1f}")
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


def lattice(room: Room, ends: tuple, rad: float, region_pad: float = REGION,
            cap: int = LATTICE_CAP) -> Lattice:
    """The lattice a lane between these two points is searched on."""
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
    coords, steps = [], []
    for i in range(3):
        keep = [e[i] for e in ends] + [lo[i], hi[i]]
        cand = list(keep)
        for _n, b in near:
            for v in (b[2 * i] - rad, b[2 * i + 1] + rad):
                if lo[i] - 1e-9 <= v <= hi[i] + 1e-9:
                    cand.append(v)
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


# --- the search -----------------------------------------------------------

def lanes(run: str, top: int = 6, floor: float = FLOOR, hold=(), snap: dict = None,
          nonrising: bool = None, cap: int = LATTICE_CAP, region: float = REGION,
          ends: tuple = None, radius: float = None, od: float = None) -> list:
    """Every orthogonal corridor between a run's two mouths that keeps `floor` off the machine,
    cheapest first.

    The two mouths and their leads are not negotiable: a line leaves a collet along the collet's
    own axis and arrives at one against it, and neither may turn inside a stock radius of the
    face. So the search runs between the two LEAD ENDS, and each interior leg is at least two
    radii long because a corner backs a tangent that far down each of its legs. That is the
    whole difference between a lane and a polyline: what comes back can be bent.

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
    if ends is None:
        a, b = spec["frm"], spec["to"]
        pa, pb = snap["ports"][a], snap["ports"][b]
        ends = ((tuple(pa["pos"]), tuple(pa["axis"])), (tuple(pb["pos"]), tuple(pb["axis"])))
        od = spec["diam"] if od is None else od
        radius = spec["bend"] if radius is None else radius
        hold = tuple(hold) + (run, f"tube-{run}", a.split(".")[0], b.split(".")[0])
    if nonrising is None:
        nonrising = bool(spec) and spec["frm"].startswith("hopper-funnel")
    od = 6.35 if od is None else od
    radius = 14.0 if radius is None else radius

    rad = od / 2.0 + floor
    (p0, n0), (p1, n1) = ends
    # A lane leaves along the port's own axis and enters against the other's. Both leads are a
    # full stock radius, which is what the first corner needs before it can turn at all.
    q0 = tuple(p0[i] + n0[i] * radius for i in range(3))
    q1 = tuple(p1[i] + n1[i] * radius for i in range(3))
    room = Room.of(snap, hold)
    lat = lattice(room, (q0, q1), rad, region_pad=region, cap=cap)
    near = room.near(lat.region)
    free = _Free(lat, near, rad)

    start = tuple(lat.index(i, _nearest(lat.coords[i], q0[i])) for i in range(3))
    goal = tuple(lat.index(i, _nearest(lat.coords[i], q1[i])) for i in range(3))
    # The heading a lane must leave on and the one it must arrive on, as (axis, sign).
    out = _heading(n0)
    into = _heading(tuple(-c for c in n1))
    found = _search(lat, free, start, goal, out, into, radius, max(top, 4) * 3, nonrising)

    made, seen = [], set()
    for pts in found:
        square = _straighten((tuple(p0),) + tuple(_at(lat, c) for c in pts) + (tuple(p1),))
        whole = _straighten(_smooth(square, near, od, floor, radius, ends))
        key = tuple(tuple(round(v, 4) for v in p) for p in whole)
        if key in seen:
            continue                    # two settlements that smooth to one corridor
        seen.add(key)
        lane = Lane(run, whole, od, radius, floor, math.inf, _dist(p0, p1),
                    tuple(_dist(x, y) for x, y in zip(whole, whole[1:])), square)
        if not lane.at_spec:
            continue                    # a corner the bender cannot make is not a lane
        # MEASURED ON THE TUBE AND NOT ON THE POLYLINE. The search worked on straight lattice
        # legs; the thing that gets built rounds every corner off them, and the arc stands where
        # the vertex did not. A lane that only clears square is not a lane.
        lane.margin = _margin(lane.centreline, od, near)
        if lane.margin < floor - 1e-6:
            continue
        made.append(lane)
    made.sort(key=lambda l: (round(l.cost, 4), -round(l.margin, 4)))
    for l in made:
        l.lattice = lat                                          # noqa: B010 — carried, not set
    return made[:top]


def _nearest(coords, v: float) -> float:
    return min(coords, key=lambda c: abs(c - v))


def _at(lat: Lattice, cell: tuple) -> tuple:
    return tuple(lat.coords[i][cell[i]] for i in range(3))


def _heading(axis) -> tuple:
    """A unit vector as (axis index, sign). Raises on anything off the world axes — this
    instrument costs axis-aligned mouths only, and one that is not is one it cannot lay a lane
    off."""
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
        u = [b[k] - a[k] for k in range(3)]
        v = [c[k] - b[k] for k in range(3)]
        cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
                 u[0] * v[1] - u[1] * v[0])
        if max(abs(c_) for c_ in cross) > 1e-6:
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

    Returns up to `top` arrivals, cheapest first. Each state is allowed `top` settlements rather
    than one, which is what makes the second-cheapest corridor reachable at all — a single
    settlement per state is a shortest-path search and answers only the first question."""
    minleg = LEAN_STEP
    lead = radius
    # (cost, tie, cell, heading, path). The tie-break keeps the heap total-ordered without
    # comparing tuples of floats.
    seen: dict = {}
    tie = itertools.count()
    heap = [(0.0, next(tie), start, out, (start,))]
    done = []
    while heap:
        cost, _t, cell, head, path = heapq.heappop(heap)
        key = (cell, head)
        if seen.get(key, 0) >= top:
            continue
        seen[key] = seen.get(key, 0) + 1
        if cell == goal and head == into:
            done.append(path)
            if len(done) >= top:
                return done
            continue
        for axis in range(3):
            for sign in (-1, 1):
                if axis == head[0] and sign != head[1]:
                    continue              # a tube does not turn back through itself
                if nonrising and axis == 2 and sign > 0:
                    continue
                turn = 0 if (axis, sign) == head else 1
                floor_ = 0.0 if not turn else minleg
                for cn, run_len in _legs(lat, free, cell, axis, sign, floor_, lead,
                                         goal, into):
                    heapq.heappush(heap, (cost + run_len + BEND_MM * turn, next(tie),
                                          cn, (axis, sign), path + (cn,)))
    return done


def _legs(lat: Lattice, free: _Free, cell: tuple, axis: int, sign: int, minleg: float,
          lead: float, goal: tuple, into: tuple) -> list:
    """Every cell a leg from here along this heading may end on.

    A leg that starts at a corner is at least `minleg` long, because both of its ends may be
    corners — except the one that ARRIVES at the far mouth on the heading the collet is entered
    on, which is the approach lead and pays for one corner only. The line's free interval is
    what bounds it, and past the first obstruction on that line nothing is reachable at all."""
    c = lat.coords[axis]
    here = c[cell[axis]]
    out = []
    rng = range(cell[axis] + 1, len(c)) if sign > 0 else range(cell[axis] - 1, -1, -1)
    for n in rng:
        span = abs(c[n] - here)
        end = tuple(n if i == axis else cell[i] for i in range(3))
        if not free.clear(axis, cell, here, c[n]):
            break                     # past the first obstruction the line is shut
        arrives = end == goal and (axis, sign) == into
        if span < minleg - 1e-6 and not (arrives and span > lead - 1e-6):
            continue
        out.append((end, span))
    return out


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
        run = _graded("smooth", tuple(pts), od, radius)
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


def _margin(pts: tuple, od: float, near: tuple) -> float:
    """The tightest the lane comes to anything in the room.

    Segment against box, exactly for the axis-aligned legs an orthogonal lane is made of: the
    box is grown by the tube's half-section and the distance taken from the segment to it. A
    body it clears by this much is a body it clears — the box is the over-approximation, so the
    reading is a floor on the truth and never a ceiling."""
    best = math.inf
    for a, b in zip(pts, pts[1:]):
        for _n, box in near:
            best = min(best, _seg_box(a, b, box) - od / 2.0)
    return best


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


# --- what the card says about the lane a run is in now --------------------

def authored(run: str, floor: float = FLOOR, snap: dict = None) -> Lane:
    """The run AS DRAWN, put through the same reader as a searched lane, so a ranking has the
    thing it is ranking against in it.

    Its `path` is its own developed length off `_routing.Run.length` rather than this module's
    square-corner arithmetic — the authored run leans, and the arithmetic here is orthogonal."""
    snap = snapshot() if snap is None else snap
    spec = snap["runs"][run]
    hold = (run, f"tube-{run}", spec["frm"].split(".")[0], spec["to"].split(".")[0])
    room = Room.of(snap, hold)
    pts = tuple(tuple(p) for p in spec["pts"])
    region = tuple(v for i in range(3)
                   for v in (min(p[i] for p in pts) - 20.0, max(p[i] for p in pts) + 20.0))
    lane = Lane(run, pts, spec["diam"], spec["bend"], floor, math.inf,
                _dist(pts[0], pts[-1]),
                tuple(_dist(a, b) for a, b in zip(pts, pts[1:])))
    lane.margin = _margin(lane.centreline, spec["diam"], room.near(region))
    lane.drawn = spec["length"]                                  # noqa: B010 — carried
    return lane


# --- the exact world ------------------------------------------------------

def verify(lane: Lane, clearance: float = 0.0, skip=()) -> str:
    """A searched lane in the exact world — printed walls, seam lips, ribs and boss chains — as
    the solid it would be swept into.

    The rank is a claim about boxes and centrelines. This is the claim about the machine, and
    they are not the same answer: a box-clear lane standing in a seam lip clashes here, and this
    is the one that counts. It holds out exactly what the search held out, and for the same
    reason."""
    import cadquery as cq
    import probe
    import _clearing
    w = probe.world()
    wire = cq.Wire.assembleEdges(
        [cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b))
         for a, b in zip(lane.pts, lane.pts[1:])])
    solid = (cq.Workplane("XY").center(lane.pts[0][0], lane.pts[0][1])
             .workplane(offset=lane.pts[0][2])
             .circle(lane.od / 2.0).sweep(cq.Workplane(wire), isFrenet=True).val())
    held = set(skip) | {n for n in w.names
                        if n.replace("tube-", "") == lane.run or n == lane.run}
    spec = snapshot()["runs"].get(lane.run)
    if spec:
        held |= {spec["frm"].split(".")[0], spec["to"].split(".")[0]}
    worst, hits = math.inf, []
    for name in w.names:
        if name in held:
            continue
        g = _clearing.gap(solid, w.solid(name))
        if g < worst:
            worst = g
        if g <= clearance + 1e-9:
            hits.append(f"{name} {g:.3f}")
    out = [f"{lane.run}: {w.measured}, holding out {', '.join(sorted(held))}",
           f"  tightest exact clearance {worst:.3f} mm"]
    out.append("  " + ("CLASH: " + "; ".join(hits) if hits else "clear of every body"))
    return "\n".join(out)


# --- the poses a mouth may stand in ---------------------------------------
#
# A fitting in this machine is hung off another fitting's mouth: it takes one of its own mouths
# to that one, stands a stated reach off it, and is free to ROLL about the joint. A chain of
# them — the bulkhead, the ASSE, the split, the regulator — is one such link per fitting, and
# turning any link carries everything downstream of it.
#
# So a body's pose here is a RIGID TRANSFORM of the body the snapshot holds, and the transform
# is what the space varies. Quarter turns only: the rotation that takes one axis-aligned mouth
# onto another is one of the cube's own 24, which is exactly the set that carries an
# axis-aligned box onto an axis-aligned box. Anything else and the boxes this scans on would
# stop being the bodies' boxes.

QUARTERS = (0, 1, 2, 3)


def _rot_axis(axis: int, quarters: int) -> tuple:
    """The 3×3 of a quarter turn about a world axis, as a tuple of rows."""
    c, s = int(round(math.cos(quarters * math.pi / 2))), int(round(math.sin(quarters * math.pi / 2)))
    m = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    j, k = [i for i in range(3) if i != axis]
    m[j][j], m[j][k] = c, -s
    m[k][j], m[k][k] = s, c
    return tuple(tuple(r) for r in m)


def _mul(a, b) -> tuple:
    return tuple(tuple(sum(a[i][t] * b[t][j] for t in range(3)) for j in range(3))
                 for i in range(3))


def _apply(m, v) -> tuple:
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _align(frm, to) -> tuple:
    """A quarter-turn rotation carrying one axis-aligned unit vector onto another.

    There are many; this takes the one that turns about the axis square to both, which for
    opposite vectors is a half turn about either of the other two. The ROLL is the caller's
    choice and is applied after, so which one this picks decides only what roll 0 means."""
    fi, fs = _heading(frm)
    ti, ts = _heading(to)
    if fi == ti:
        return _rot_axis((fi + 1) % 3, 0 if fs == ts else 2)
    about = [i for i in range(3) if i != fi and i != ti][0]
    for q in QUARTERS:
        m = _rot_axis(about, q)
        if all(abs(x - y) < 1e-9 for x, y in zip(_apply(m, frm), to)):
            return m
    raise ValueError(f"no quarter turn carries {frm} onto {to}")


@dataclass(frozen=True)
class Seat:
    """One body hung off another's mouth: which of its own mouths meets it, how far off, and
    how it is rolled about the joint.

    This is the machine's own seating rule read back as a transform — `front_half.build_split`
    stands the split one `WATER_2` off the chain's outlet on that collet's own line, and that is
    a `Seat` with `gap=WATER_2` and a roll. What the space varies is the roll and the gap; what
    it holds is that the joint is a joint at all.

    A seat with no parent is a STATION: the mouth is put at a stated point facing a stated way,
    which is how a body clamped through a wall is placed — `front_half.build_panel_bulkhead`
    seats a union on its inboard collet at `(x, bulkhead_mouth_y, z)`. What the space varies
    there is the station, and `stations()` is where the ones that clear the machine come from."""
    body: str
    mouth: str                  # this body's port that meets the parent's
    on: str = ""                # "parent.port", or empty for a station
    gap: float = 0.0
    roll: int = 0
    at: tuple = None            # a station's own point, when there is no parent
    axis: tuple = None          # and the way the mouth faces there

    @property
    def parent(self) -> str:
        return self.on.split(".")[0] if self.on else ""


def _pose(snap: dict, seat: Seat, ports: dict) -> tuple:
    """The rigid transform a seat puts its body through, as `(rotation, translation)`.

    The body's own mouth has to land on the parent's, one `gap` off it, facing back at it — or,
    for a station, on the point the station names facing the way it names. Either fixes
    everything but the roll about that axis, and the roll is the seat's."""
    if seat.on:
        p, axis = ports[seat.on]["pos"], ports[seat.on]["axis"]
        target = tuple(p[i] + axis[i] * seat.gap for i in range(3))
        face = tuple(-c for c in axis)
    else:
        target, face = tuple(seat.at), tuple(seat.axis)
        axis = face
    mine = snap["ports"][f"{seat.body}.{seat.mouth}"]
    m = _align(tuple(mine["axis"]), face)
    m = _mul(_rot_axis(_heading(axis)[0], seat.roll), m)
    origin = tuple(mine["pos"])
    t = tuple(target[i] - _apply(m, origin)[i] for i in range(3))
    return m, t


def _moved_box(m, t, box) -> tuple:
    """A quarter-turned box is a box — the corners are carried through and re-bounded, which for
    a cube rotation loses nothing."""
    corners = [(box[i], box[2 + j], box[4 + k])
               for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    moved = [tuple(_apply(m, c)[a] + t[a] for a in range(3)) for c in corners]
    return tuple(v for a in range(3)
                 for v in (min(c[a] for c in moved), max(c[a] for c in moved)))


# --- the space ------------------------------------------------------------

@dataclass(frozen=True)
class Choice:
    """One axis of the space: a body, what about it is free, and every value it may take."""
    body: str
    what: str
    values: tuple


@dataclass
class Space:
    """The arrangements, the runs they are scored on, and what is held while they vary.

    A space states itself before it states an answer. A ranking read without its space is a
    ranking of a search."""
    chain: tuple                # the seats, parent before child
    choices: tuple
    runs: tuple                 # the runs re-costed for every arrangement
    label: str
    floor: float = FLOOR

    @property
    def bodies(self) -> tuple:
        return tuple(s.body for s in self.chain)

    @property
    def size(self) -> int:
        n = 1
        for c in self.choices:
            n *= len(c.values)
        return n

    def report(self) -> str:
        snap = snapshot()
        out = [f"{self.label} — {self.size:,} arrangements over {len(self.choices)} choices"]
        for c in self.choices:
            vals = ", ".join(f"{v:g}" if isinstance(v, float) else str(v) for v in c.values)
            out.append(f"  {c.body:<22} {c.what:<6} {len(c.values):>3}  [{vals}]")
        out.append(f"  chain   {' → '.join(s.body for s in self.chain)}")
        out.append(f"  runs    {len(self.runs)}: {', '.join(self.runs)}")
        held = sorted(set(snap['bodies']) - set(self.bodies))
        out.append(f"  holds   {len(held)} bodies still, "
                   f"{len(snap['runs'])} runs, the cavity and the four printed pieces")
        out.append(f"  floor   {self.floor:g} mm, bend {BEND_MM:g} mm of tube")
        return "\n".join(out)


def west_lane() -> Space:
    """The tap-water chain in the west lane, and the two runs that leave it.

    `front_half` seats these four one off the next: the union's collet fixes the ASSE chain, the
    chain's outlet fixes the split one `WATER_2` along it, the split's flavour collet fixes the
    regulator one `FLUID_1` along that. Each of those joints has a ROLL nobody has costed — the
    split's branch may look down, up or either way across, and the regulator may lie any of four
    ways about its own flow axis — and each has a REACH the author picked as a round number.

    What the space holds is the joints themselves. The union is in the back wall and the chain's
    inlet butts it, so the chain's own yaw is not free: the three quarter turns that are not
    `ASSE1022_YAW` put its inlet on a face the back wall is not. That is a finding and not an
    omission — the lane has one turn in it, and it is spent."""
    snap = snapshot()
    chain = (
        Seat("water-split", "supply", "asse1022-assembly.tube-out",
             _dist(snap["ports"]["asse1022-assembly.tube-out"]["pos"],
                   snap["ports"]["water-split.supply"]["pos"]), 0),
        Seat("flow-regulator", "inlet", "water-split.to-flavor",
             _dist(snap["ports"]["water-split.to-flavor"]["pos"],
                   snap["ports"]["flow-regulator.inlet"]["pos"]), 0),
    )
    gaps = (18.0, 24.0, 30.0, 36.0)
    choices = (
        Choice("water-split", "roll", QUARTERS),
        Choice("water-split", "gap", gaps),
        Choice("flow-regulator", "roll", QUARTERS),
        Choice("flow-regulator", "gap", gaps),
    )
    return Space(chain, choices, ("fluid-2",), "west lane")


# --- one arrangement ------------------------------------------------------

@dataclass
class Arrangement:
    """One value for every choice, the mouths it puts where, and what the runs then cost."""
    space: Space
    values: dict
    ports: dict
    boxes: dict
    lanes: dict
    clash: tuple

    @property
    def cost(self) -> float:
        return sum(l.cost for l in self.lanes.values()) if self.lanes else math.inf

    @property
    def path(self) -> float:
        return sum(l.path for l in self.lanes.values()) if self.lanes else math.inf

    @property
    def bends(self) -> int:
        return sum(l.bends for l in self.lanes.values()) if self.lanes else 0

    @property
    def margin(self) -> float:
        return min((l.margin for l in self.lanes.values()), default=math.inf)

    def vector(self) -> str:
        return " ".join(f"{c.body.split('-')[-1]}:{c.what[0]}"
                        f"{self.values[(c.body, c.what)]:g}" for c in self.space.choices)

    def report(self) -> str:
        out = [("CLASH: " + "; ".join(self.clash)) if self.clash else "box-clear",
               f"  cost {self.cost:.0f}   path {self.path:.1f} mm   bends {self.bends}   "
               f"margin {self.margin:.3f} mm", ""]
        for name, lane in self.lanes.items():
            out.append(f"  {name:<10} {lane.path:7.1f} mm  {lane.bends} bends  "
                       f"detour {lane.detour:.3f}×  margin {lane.margin:.3f}   {lane.vector()}")
        out.append("")
        for c in self.space.choices:
            out.append(f"  {c.body:<22} {c.what:<6} {self.values[(c.body, c.what)]}")
        return "\n".join(out)


def _overlaps(a, b, slack=1e-6) -> bool:
    return all(a[2 * i] < b[2 * i + 1] - slack and b[2 * i] < a[2 * i + 1] - slack
               for i in range(3))


def build(space: Space, values: dict, top: int = 1) -> Arrangement:
    """One arrangement: the chain re-posed, its mouths carried, and the runs re-laned.

    The chain is walked PARENT FIRST, so a link's seat reads a mouth its parent has already
    moved — which is what makes a roll at the top of the chain carry everything under it."""
    snap = snapshot()
    ports = dict((k, dict(v)) for k, v in snap["ports"].items())
    boxes = {n: tuple(b["box"]) for n, b in snap["bodies"].items()}
    moved = {}
    for seat in space.chain:
        s = Seat(seat.body, seat.mouth, seat.on,
                 values.get((seat.body, "gap"), seat.gap),
                 values.get((seat.body, "roll"), seat.roll))
        m, t = _pose(snap, s, ports)
        for key, p in list(ports.items()):
            if key.split(".")[0] != s.body:
                continue
            base = snap["ports"][key]
            ports[key] = {"pos": [ _apply(m, tuple(base["pos"]))[i] + t[i] for i in range(3)],
                          "axis": list(_apply(m, tuple(base["axis"]))),
                          "diam": base["diam"]}
        boxes[s.body] = _moved_box(m, t, tuple(snap["bodies"][s.body]["box"]))
        moved[s.body] = boxes[s.body]

    clash = []
    for name, b in moved.items():
        for other, ob in boxes.items():
            if other == name or other in moved and other < name:
                continue
            if snap["bodies"][other]["tag"] in ("piece", "run"):
                continue
            if _overlaps(b, ob):
                clash.append(f"{name}/{other}")
        cav = snap["cavity"]
        for i in range(3):
            if b[2 * i] < cav[2 * i] - 1e-6 or b[2 * i + 1] > cav[2 * i + 1] + 1e-6:
                clash.append(f"{name} out of the cavity on {'xyz'[i]}")

    scored = {}
    if not clash:
        live = dict(snap)
        live["ports"] = ports
        live["bodies"] = {n: {"tag": snap["bodies"][n]["tag"], "box": list(boxes[n])}
                          for n in snap["bodies"]}
        # A RUN THAT TOUCHES A MOVED BODY IS NOT WHERE THE SNAPSHOT LEFT IT. Its tube was swept
        # to mouths this arrangement has taken somewhere else, so holding it in would measure
        # every candidate against the plumbing of the one it replaces — the same tautology
        # holding the moved bodies themselves in would be.
        stale = tuple(rid for rid, r in snap["runs"].items()
                      if r["frm"].split(".")[0] in moved or r["to"].split(".")[0] in moved)
        for rid in space.runs:
            got = lanes(rid, top=1, floor=space.floor, snap=live,
                        hold=stale + tuple(f"tube-{s}" for s in stale))
            if not got:
                clash.append(f"{rid} has no lane at a {space.floor:g} mm floor")
                scored = {}
                break
            scored[rid] = got[0]
    return Arrangement(space, values, ports, boxes, scored, tuple(clash))


def current(space: Space) -> dict:
    """The arrangement the tree builds today, read off the snapshot rather than restated — so a
    value changed in `front_half` moves this, and the ranking that scores it stays honest.

    The ROLL is solved and not assumed. Which quarter turn `_align` calls zero is this module's
    convention and not the machine's, so the tree's own roll is whichever of the four puts every
    one of the body's mouths back where the snapshot has it. A body no quarter reproduces is a
    body seated off the world axes, and that RAISES — a scan that silently called it zero would
    be ranking a pose the machine does not have."""
    snap = snapshot()
    out = {}
    for seat in space.chain:
        parent = snap["ports"][seat.on]
        mine = snap["ports"][f"{seat.body}.{seat.mouth}"]
        gap = round(_dist(parent["pos"], mine["pos"]), 6)
        out[(seat.body, "gap")] = gap
        keys = [k for k in snap["ports"] if k.split(".")[0] == seat.body]
        best = None
        for roll in QUARTERS:
            m, t = _pose(snap, Seat(seat.body, seat.mouth, seat.on, gap, roll), snap["ports"])
            off = max(_dist(tuple(_apply(m, tuple(snap["ports"][k]["pos"]))[i] + t[i]
                                  for i in range(3)), snap["ports"][k]["pos"]) for k in keys)
            if best is None or off < best[1]:
                best = (roll, off)
        if best[1] > 1e-6:
            raise ValueError(
                f"{seat.body} is not reproduced by any quarter roll about "
                f"{seat.on} — the nearest is roll {best[0]} at {best[1]:.4f} mm. It is seated "
                f"off the world axes, and this instrument cannot state its pose.")
        out[(seat.body, "roll")] = best[0]
    for c in space.choices:
        out.setdefault((c.body, c.what), c.values[0])
    return out


def rank(space: Space, top: int = 10, keep_clashing: bool = False) -> list:
    """Every arrangement in the space, scored, cheapest first.

    A body standing in another body is not a worse arrangement, it is not an arrangement — those
    are dropped unless asked for. So are the ones whose runs have no lane at the floor: an
    arrangement that cannot be plumbed is not one either."""
    axes = [(c.body, c.what, c.values) for c in space.choices]
    out = []
    for combo in itertools.product(*(v for _b, _w, v in axes)):
        values = {(b, w): v for (b, w, _vals), v in zip(axes, combo)}
        a = build(space, values)
        if a.clash and not keep_clashing:
            continue
        out.append(a)
    out.sort(key=lambda a: (round(a.cost, 3), -round(a.margin, 3)))
    return out[:top]


# --- selftest -------------------------------------------------------------

def _room(boxes, cavity) -> Room:
    return Room(tuple(boxes), tuple(cavity), ())


def selftest() -> int:
    """Known-answer controls on the solver, then the machine that exists through the filter."""
    fails = []

    def check(name, got, want, tol=1e-6):
        ok = abs(got - want) <= tol if isinstance(want, float) else got == want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got} (want {want})")
        if not ok:
            fails.append(name)

    print("the lane solver — known answers")
    big = (-500.0, 500.0, -500.0, 500.0, -500.0, 500.0)
    ends = (((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((0.0, -200.0, 0.0), (0.0, 1.0, 0.0)))
    got = lanes("probe", ends=ends, od=6.35, radius=14.0, top=3,
                snap={"bodies": {}, "runs": {}, "ports": {}, "cavity": list(big)})
    check("two mouths down one empty line: bends", got[0].bends, 0)
    check("two mouths down one empty line: path", got[0].path, 200.0)
    check("and nothing else in an empty room beats a straight line",
          all(l.cost > got[0].cost - 1e-9 for l in got[1:]), True)

    # One slab across that line, narrower than the room: the lane has to go round it, which is
    # two corners and the width of the detour.
    slab = {"slab": {"tag": "component", "box": [-40.0, 40.0, -120.0, -80.0, -40.0, 40.0]}}
    got = lanes("probe", ends=ends, od=6.35, radius=14.0, top=4,
                snap={"bodies": slab, "runs": {}, "ports": {}, "cavity": list(big)})
    check("a slab across it: bends", got[0].bends, 2)
    check("a slab across it: it clears the slab",
          got[0].margin >= FLOOR - 1e-6, True)
    check("a slab across it: it steps at least as far as the slab is wide",
          max(abs(p[0]) for p in got[0].pts) >= 40.0 + 6.35 / 2 + FLOOR - 1e-6, True)

    # A gap that a 1 mm floor fits through and a 6 mm floor does not. This is `fluid-4`'s own
    # case in miniature — the source pair's limbs leave 7.890 mm for a Ø6.35 line — and it is
    # the control on the floor being a real parameter and not a decoration.
    slot = {"west": {"tag": "component", "box": [-60.0, -5.0, -120.0, -80.0, -40.0, 40.0]},
            "east": {"tag": "component", "box": [5.0, 60.0, -120.0, -80.0, -40.0, 40.0]}}
    thin = {"bodies": slot, "runs": {}, "ports": {}, "cavity": list(big)}
    got = lanes("probe", ends=ends, od=6.35, radius=14.0, top=1, floor=0.5, snap=thin)
    check("a 10 mm slot at a 0.5 mm floor: straight through", got[0].bends, 0)
    got = lanes("probe", ends=ends, od=6.35, radius=14.0, top=1, floor=2.0, snap=thin)
    check("the same slot at a 2.0 mm floor: goes around", got[0].bends > 0, True)

    # The leg rule. A corner backs `r` down each leg, so two corners cannot stand closer than
    # `2r`: an offset under that is taken in one wide step and not two tight ones.
    off = (((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), ((10.0, -200.0, 0.0), (0.0, 1.0, 0.0)))
    got = lanes("probe", ends=off, od=6.35, radius=14.0, top=1,
                snap={"bodies": {}, "runs": {}, "ports": {}, "cavity": list(big)})
    check("a 10 mm offset: two corners", got[0].bends, 2)
    check("a 10 mm offset: no leg under two radii",
          min(l for l in got[0].legs[1:-1]) >= 2 * 14.0 - 1e-6, True)

    print("the reader — a lane's own arithmetic")
    l = Lane("probe", ((0.0, 0.0, 0.0), (0.0, -100.0, 0.0), (50.0, -100.0, 0.0)),
             6.35, 14.0, 1.0, 9.9, 111.8, (100.0, 50.0))
    check("square length", l.square, 150.0)
    check("developed length takes the arc back out",
          l.path, 150.0 - 14.0 * (2.0 - math.pi / 2.0))
    check("one corner", l.bends, 1)

    print("the pose — a seat's own transform")
    # A quarter turn carries a box onto a box, and the mouth it is seated on lands where the
    # seat says. Both are what the arrangement scan's boxes and ports stand on.
    m = _align((0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
    check("a quarter turn carries the mouth", _apply(m, (0.0, 1.0, 0.0)), (1.0, 0.0, 0.0))
    box = _moved_box(_rot_axis(2, 1), (0.0, 0.0, 0.0), (0.0, 10.0, 0.0, 4.0, 0.0, 2.0))
    check("a turned box is a box", box, (-4.0, 0.0, 0.0, 10.0, 0.0, 2.0))

    print("the world — the machine that exists, through the same filter")
    snap = snapshot()
    check("the snapshot holds every body", len(snap["bodies"]) >= 86, True)
    check("and every routed run", len(snap["runs"]), 19)
    # The control the whole instrument stands on. These runs are DRAWN, the pack closes and
    # `lines-clear` passes — so a reader that says one of them clashes is rejecting reality.
    worst = []
    for rid in sorted(snap["runs"]):
        a = authored(rid, floor=0.0)
        worst.append((a.margin, rid))
    worst.sort()
    check("every authored run clears the machine it is in",
          worst[0][0] > -1e-6, True)
    print(f"       tightest authored run: {worst[0][1]} at {worst[0][0]:.3f} mm")
    # And the reader agrees with the card about the two runs this instrument was pointed at.
    for rid, want in (("fluid-4", 152.63), ("fluid-2", 212.33)):
        check(f"{rid}: the drawn length is the card's", round(authored(rid).drawn, 2), want,
              tol=0.02)

    print("the space — the tree's own arrangement is in it")
    sp = west_lane()
    cur = current(sp)
    for c in sp.choices:
        if cur[(c.body, c.what)] not in c.values:
            fails.append(f"{c.body}.{c.what} not in the space")
            print(f"  FAIL {c.body}.{c.what} = {cur[(c.body, c.what)]} is not a value")
        else:
            print(f"  ok   {c.body}.{c.what} = {cur[(c.body, c.what)]} is a value")
    # Rebuilding the machine's own arrangement has to put every mouth back where the snapshot
    # has it. A seat model that cannot reproduce the tree is a seat model that is scoring
    # something else.
    a = build(sp, cur)
    off = max(_dist(a.ports[k]["pos"], snap["ports"][k]["pos"])
              for k in snap["ports"] if k.split(".")[0] in sp.bodies)
    check("re-seating the chain puts every mouth back", off, 0.0, tol=1e-6)

    print(f"\n{'PASS' if not fails else 'FAIL: ' + ', '.join(sorted(set(fails)))}")
    return 1 if fails else 0


# --- CLI ------------------------------------------------------------------

def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("snapshot", help="the world a scan reads, and where it is cached")
    p.add_argument("--reload", action="store_true")
    p = sub.add_parser("lanes", help="every corridor between a run's two mouths, ranked")
    p.add_argument("run")
    p.add_argument("--top", type=int, default=6)
    p.add_argument("--floor", type=float, default=FLOOR)
    p.add_argument("--cap", type=int, default=LATTICE_CAP)
    p.add_argument("--region", type=float, default=REGION)
    p.add_argument("--full", action="store_true", help="the winner leg by leg")
    sub.add_parser("space", help="the choices, the runs, and what is held")
    p = sub.add_parser("rank", help="every arrangement, scored, best first")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--full", action="store_true")
    p = sub.add_parser("verify", help="a searched lane in the exact world")
    p.add_argument("run")
    p.add_argument("--lane", type=int, default=1)
    p.add_argument("--floor", type=float, default=FLOOR)
    p.add_argument("--clearance", type=float, default=0.0)
    sub.add_parser("selftest", help="known-answer controls, then the real machine")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "snapshot":
        snap = snapshot(reload=args.reload)
        print(f"{len(snap['bodies'])} bodies, {len(snap['runs'])} routed runs, "
              f"{len(snap['ports'])} ports")
        c = snap["cavity"]
        print(f"cavity x[{c[0]:.1f}, {c[1]:.1f}] y[{c[2]:.1f}, {c[3]:.1f}] "
              f"z[{c[4]:.1f}, {c[5]:.1f}]")
        print(f"cached at {_cache_path()}")
        return 0
    if args.cmd == "lanes":
        drawn = authored(args.run, floor=args.floor)
        got = lanes(args.run, top=args.top, floor=args.floor, cap=args.cap,
                    region=args.region)
        lat = getattr(got[0], "lattice", None) if got else None
        print(f"{args.run}: ends {drawn.span:.1f} mm apart, floor {args.floor:g} mm, "
              f"bend R{drawn.radius:g}, Ø{drawn.od:g}")
        if lat:
            print(f"lattice {'×'.join(str(len(c)) for c in lat.coords)} = {lat.size:,} cells, "
                  f"thinned at {max(lat.step):.1f} mm, region "
                  + " ".join(f"{'xyz'[i]}[{lat.region[2*i]:.0f}, {lat.region[2*i+1]:.0f}]"
                             for i in range(3)))
        print()
        print(f"{'#':>3}  {'cost':>6}  {'path':>6}  {'bend':>4}  {'detour':>6}  "
              f"{'margin':>7}   lane")
        for n, l in enumerate(got, 1):
            print(f"{n:>3}  {l.cost:6.0f}  {l.path:6.1f}  {l.bends:4d}  {l.detour:6.3f}  "
                  f"{l.margin:7.3f}   {l.vector()}")
        print(f"{'now':>3}  {drawn.cost:6.0f}  {drawn.drawn:6.1f}  {drawn.bends:4d}  "
              f"{drawn.drawn / drawn.span:6.3f}  {drawn.margin:7.3f}   {drawn.vector()}")
        print("\nan orthogonal lane is an UPPER bound on its corridor — the authored run leans, "
              "and a leaning\nversion of any lane here is shorter than the square one shown.")
        if args.full and got:
            print()
            print(got[0].report())
        return 0
    sp = west_lane()
    if args.cmd == "space":
        print(sp.report())
        return 0
    if args.cmd == "rank":
        print(sp.report())
        print()
        best = rank(sp, top=args.top)
        cur = build(sp, current(sp))
        print(f"{'#':>3}  {'cost':>6}  {'path':>6}  {'bend':>4}  {'margin':>7}   arrangement")
        for n, a in enumerate(best, 1):
            print(f"{n:>3}  {a.cost:6.0f}  {a.path:6.1f}  {a.bends:4d}  {a.margin:7.3f}   "
                  f"{a.vector()}")
        print(f"{'now':>3}  {cur.cost:6.0f}  {cur.path:6.1f}  {cur.bends:4d}  "
              f"{cur.margin:7.3f}   {cur.vector()}"
              + ("   " + "; ".join(cur.clash) if cur.clash else ""))
        if args.full and best:
            print()
            print(best[0].report())
        return 0
    if args.cmd == "verify":
        got = lanes(args.run, top=args.lane, floor=args.floor)
        if len(got) < args.lane:
            print(f"{args.run}: only {len(got)} lane(s) at a {args.floor:g} mm floor")
            return 1
        print(verify(got[args.lane - 1], clearance=args.clearance))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
