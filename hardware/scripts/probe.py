"""Geometry probe — ask the placed solids a question instead of reasoning about them.

The whole placed machine as one flat `{name: shape}` world — `enclosure_assembly`'s pack
bodies, the display and hopper funnel seated in the walls, the four printed
enclosure pieces and the routed tubes — with the queries that answer where a part
is, how close two parts come, what a candidate volume runs into, how far a
line can travel before it hits something, and where a piece of a routed line can stand.

The world is one `enclosure_assembly.build_enclosure_assembly()`, body for body: `w.parts` are the
bodies, `w.pieces` are the box's four printable pieces, and both are in the one
dict every query iterates. That is the point. The pieces are the walls, seam lips,
cross-pin pods, boss chains and ribs, they are what bounds a placement in a
machine this full, and a query that could not see them would answer CLEAR
exactly where the clash check answers clash. The two groups keep
their names so a query can ask for the interior pack alone — `skip=w.pieces` —
but nothing has to remember to ask for the walls.

Every query is bounded and every query is loud. A body that cannot be normalized
raises instead of being skipped; a body whose mesh will not close raises with its
name; a cast that never contacts anything says so rather than reporting its own
limit as a clearance. Nothing here returns 0.0 for "I could not measure".

That last promise is why every overlap goes through `_overlap.common` rather
than one `intersect`: an exact `intersect` succeeds and hands back nothing for
two bodies whose surfaces are tangent where they cross. Two swept tubes of one Ø
on one stratum are exactly that, and the pack authors them on purpose.

Use from anywhere in the repo:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"),
    )
    import probe

    w = probe.world()
    print(w.table(sort="ymin"))                       # every body's box, tagged by role
    w.gap("foam-assembly", "compressor")              # exact mm between two solids
    w.hits(probe.box(x=(100, 120), y=(160, 200), z=(30, 275)))   # what a lane runs into
    w.cast((110.1, 98.4, 273.1), (0, 0, -1), dia=6.35)           # how far a tube can drop
    w.travel("psu", (1, 0, 0))                        # how far a BODY moves, and past what
    w.hits(vol, skip=w.pieces)                        # the interior pack alone

    print(w.route("fluid-14"))                        # an authored run's waypoints, numbered
    w.reroute("fluid-14", (3, 4), "-y", probe.steps(0, 80, 2.5))   # move a bend, collisions only
    w.drawn("fluid-14", pts)                          # one candidate centreline, waypoints and all

    probe.sweep(range(0, 360, 10), lambda a: w.cast(tip(a), aim(a)).free)

MOVING A PIECE OF A DRAWN LINE is `reroute`. It translates named waypoints of an authored run
over a range of offsets, REDRAWS the whole run at each one, and reports what that run collides
with there — one row per position, the contiguous bands of positions that are clear, and the
radius each row's tightest corner seats. A bend, a corner, a fall, a crossing, a whole leg:
whatever the piece is called, it is some waypoints of the route, and those indices are the
handle. `w.route(id)` prints them numbered and takes `near=` a pick off the STEP to say which
index a set of coordinates is.

`w.drawn(run, pts)` is the same reading for ONE candidate centreline given whole, so a waypoint
can be dropped as well as moved. Both hold every BODY where it stands. A run's waypoints are
expressions over the bodies its author measured them off — `fluid-14`'s read `valve-v-f`,
`foam-assembly`, `vk-solenoid` and `seaflo-pump` — so a body moved in `enclosure_assembly.py`
takes its runs with it and is built, not swept.

The centreline is what moves. `w.chain(id)` is the rest of the build that reads the run and
does not — the ribs struck on it, the cap's seat for it, the stretch it is graded on, the
sleeve that closes on it — and every sweep prints it. The whole move is
[`calibration/Chain.md`](/calibration/Chain.md).

From the shell, without writing a file:

    tools/cad-venv/bin/python hardware/scripts/probe.py boxes --sort ymin
    tools/cad-venv/bin/python hardware/scripts/probe.py gap foam-assembly compressor
    tools/cad-venv/bin/python hardware/scripts/probe.py at foam-assembly.evap-outlet
    tools/cad-venv/bin/python hardware/scripts/probe.py cast 110.14,98.36,273.1 0,0,-1 --dia 6.35
    tools/cad-venv/bin/python hardware/scripts/probe.py hits --x 100,120 --y 160,200 --z 30,275
    tools/cad-venv/bin/python hardware/scripts/probe.py travel psu +x
    tools/cad-venv/bin/python hardware/scripts/probe.py route fluid-14 --near 43.5,244.7,289
    tools/cad-venv/bin/python hardware/scripts/probe.py reroute fluid-14 3-4 y- -20:80:2.5
    tools/cad-venv/bin/python hardware/scripts/probe.py selftest

`selftest` runs the instrument against known-answer geometry — a known hit, a
known miss, a known distance, a volume buried in a printed wall that every
interior body clears — and then normalizes every body in the real world. Run it
when a number looks wrong before trusting the number.
"""

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

from OCP.BRepExtrema import BRepExtrema_DistShapeShape

import _clearing
import _meshes
import _overlap
import _routing

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_ML = _HW / "manifold-layout"                              # `enclosure_assembly` — the machine
_BOX = _HW / "printed-parts" / "enclosure" / "enclosure"   # `enclosure` — the box itself

VOL_TOL = 1e-6          # mm³ below which an intersection is contact noise, not overlap
TUBE_OD = 6.35          # 1/4" LLDPE, the default probe diameter
CAST_LIMIT = 250.0      # default cast length: longer than the box's largest span
CONTACT_EPS = 1e-7      # a gap under this is bodies touching, not bodies near each other
TRAVEL_LIMIT = 60.0     # default body travel: past any move this pack has wanted, and short
                        # enough that a sweep of a real body stays quick. It is a bound on the
                        # QUERY — a travel that reaches it has found no obstacle, not room.
BED_TOL = 1.0           # slack on a piece's own extents against the bed, per axis

PIECE = "piece"         # the source tag a printed enclosure piece carries
SKIP_PIECES = "HSM_SKIP_PIECES"     # env flag that leaves the printed pieces out


# --- the overlap boolean --------------------------------------------------
# Every occupancy question here — what a volume runs into, how far a body slides, what a cast
# hits — goes through `_overlap.common`. An exact `intersect` returns no solid at all — IsDone,
# no error — for two bodies whose surfaces are tangent where they cross, which is what two swept
# tubes of one Ø on one stratum are. It answers CLEAR there, in a file whose own docstring
# promises that nothing returns 0.0 for "I could not measure".


def _common(a, b) -> tuple:
    """The solid two bodies share and its volume, as (shape, mm³). Raises on a body that will
    not close, so an unmeasured pair is never counted as a clear one."""
    return _overlap.common(a, b)


def _common_volume(a, b) -> float:
    """Just the mm³ of `_common`, for the queries that only threshold on it."""
    return _overlap.volume(a, b)


# --- normalizing what the pack hands back ---------------------------------

def shape(obj, label: str = "?"):
    """The bare `cq.Shape` behind a pack entry: `(solid, color)` tuples and
    `Workplane`s unwrap, a `Shape` passes through, anything else raises naming
    its type. `enclosure_assembly._solids()` yields `(solid, color)` tuples and
    `enclosure.build_pieces()` yields `Workplane`s, so a caller that unwraps by
    hand gets one of them wrong."""
    obj = obj[0] if isinstance(obj, tuple) else obj
    obj = obj.val() if hasattr(obj, "val") else obj
    if hasattr(obj, "bounding_box"):        # already a mesh — `common` hands these back
        return obj
    if not hasattr(obj, "wrapped"):
        raise TypeError(
            f"{label}: cannot read a solid out of {type(obj).__name__} — "
            f"probe.shape() unwraps (solid, color) tuples and Workplanes; this is neither.")
    return obj


# --- probe volumes --------------------------------------------------------

def box(x: tuple, y: tuple, z: tuple):
    """An axis-aligned box from three (lo, hi) world ranges."""
    for axis, (lo, hi) in (("x", x), ("y", y), ("z", z)):
        if hi <= lo:
            raise ValueError(f"box {axis}=({lo}, {hi}): hi must exceed lo")
    return (cq.Workplane("XY")
            .box(x[1] - x[0], y[1] - y[0], z[1] - z[0], centered=False)
            .translate((x[0], y[0], z[0]))
            .val())


def rod(origin, direction, length: float, dia: float = TUBE_OD):
    """A cylinder of `dia` running `length` from `origin` along `direction`."""
    d = unit(direction)
    if dia <= 0:
        raise ValueError(f"rod dia={dia}: a probe volume needs a real diameter")
    return cq.Solid.makeCylinder(
        dia / 2.0, length, cq.Vector(*origin), cq.Vector(*d))


def corridor(pts, dia: float = TUBE_OD):
    """The swept volume of a tube of `dia` along a polyline — rods joined by
    spheres at the interior points, so a bend is covered without a mitre."""
    pts = [tuple(float(c) for c in p) for p in pts]
    if len(pts) < 2:
        raise ValueError("corridor needs at least two points")
    out = None
    for a, b in zip(pts, pts[1:]):
        seg = [b[i] - a[i] for i in range(3)]
        ln = math.sqrt(sum(c * c for c in seg))
        if ln < 1e-9:
            continue
        piece = rod(a, seg, ln, dia)
        out = piece if out is None else out.fuse(piece)
    for p in pts[1:-1]:
        ball = cq.Solid.makeSphere(dia / 2.0, cq.Vector(*p), angleDegrees1=-90)
        out = ball if out is None else out.fuse(ball)
    if out is None:
        raise ValueError("corridor collapsed to a point")
    return out


def _swept_tube(*pts, diam: float = TUBE_OD, bend: float = 25.4):
    """A tube built the way the ROUTED RUNS are — `_routing.tube`, a circle carried along
    the waypoints with a tangent arc at each interior corner.

    `corridor` above answers a different question and cannot stand in for this one. It fuses
    rods and spheres, and a fused primitive resolves cleanly against anything; the overlap a
    single boolean goes blind to is a property of two SWEPT surfaces meeting tangentially.
    Only a body made the way `world()`'s tubes are made puts that question, which is why the
    selftest's tangent-crossing control is built here and not out of `corridor`."""
    import types

    n = len(pts)
    return _routing.tube(types.SimpleNamespace(
        pts=list(pts), diam=diam,
        radii={i: bend for i in range(1, n - 1)},
        bends=[(i, 90.0, 0.0, 0.0) for i in range(1, n - 1)]))


# --- results --------------------------------------------------------------

@dataclass
class Hit:
    name: str
    volume: float       # mm³ of overlap
    bb: object          # bounding box of the overlap itself, not of the body

    def __str__(self) -> str:
        b = self.bb
        return (f"{self.name:28s} {self.volume:10.1f} mm³  "
                f"x[{b.xmin:8.2f},{b.xmax:8.2f}] y[{b.ymin:8.2f},{b.ymax:8.2f}] "
                f"z[{b.zmin:8.2f},{b.zmax:8.2f}]")


@dataclass
class Contact:
    """How far a cast ran. `free` is only a clearance when `blocker` is set —
    when nothing was hit, `free` is the cast limit, which is a fact about the
    probe and not about the geometry."""

    free: float
    blocker: str | None
    origin: tuple
    direction: tuple
    limit: float
    dia: float

    @property
    def blocked(self) -> bool:
        return self.blocker is not None

    @property
    def end(self) -> tuple:
        return tuple(self.origin[i] + self.free * self.direction[i] for i in range(3))

    def __str__(self) -> str:
        e = self.end
        where = f"  end ({e[0]:.2f}, {e[1]:.2f}, {e[2]:.2f})"
        if self.blocked:
            return f"Ø{self.dia:g} runs {self.free:.2f} mm, stopped by {self.blocker}{where}"
        return (f"Ø{self.dia:g} reached the {self.limit:g} mm cast limit with no contact — "
                f"raise limit= to find one{where}")


@dataclass
class Stop:
    """One body's stop under a translation: how far the mover goes before it touches this
    body. `seated` marks a body the mover is already touching at rest — a seat it slides
    over rather than a gap it closes, so `at` is where a FEATURE of that body first stands
    in the way (a cap column under a module lying on the lid). `exact` is false only on a
    seated row, where the distance is bracketed rather than stepped."""

    at: float
    name: str
    seated: bool = False
    exact: bool = True

    def __str__(self) -> str:
        how = "" if self.exact else "  (bracketed)"
        seat = "  seated" if self.seated else ""
        return f"{self.at:9.3f}  {self.name}{seat}{how}"


@dataclass
class Travel:
    """Every body that stops a translation, nearest first — the whole stop list rather than
    the first stop, so the cascade behind the binder is priced in the same reading.

    Bodies the mover never reaches within `limit` are absent, and `limit` is a fact about
    this query and not about the machine. `sliding` names the bodies the mover rests on and
    stays resting on: never blockers, listed because a body nobody measured is not a body
    that is not there."""

    mover: str
    direction: tuple
    stops: list
    limit: float
    clearance: float
    sliding: tuple = ()
    skipped: tuple = ()

    @property
    def free(self) -> float:
        """Travel before the first contact — `limit` when nothing is in the way."""
        return self.stops[0].at if self.stops else self.limit

    def __str__(self) -> str:
        d = self.direction
        head = (f"{self.mover} along ({d[0]:g}, {d[1]:g}, {d[2]:g}) at clearance "
                f"{self.clearance:g} mm")
        out = [head]
        if self.skipped:
            out.append(f"  holding out: {', '.join(self.skipped)}")
        if self.sliding:
            out.append(f"  sliding on (never a blocker): {', '.join(self.sliding)}")
        if not self.stops:
            out.append(f"  reached the {self.limit:g} mm travel limit with no contact — "
                       f"raise limit= to find one")
            return "\n".join(out)
        out.append(f"  {'travel':>9}  body")
        out += [f"  {s}" for s in self.stops]
        return "\n".join(out)


@dataclass
class Offset:
    """One offset of a `reroute`: what the redrawn run runs into there, and the radius its
    tightest corner seats.

    `hits` is the bodies the run interpenetrates at this offset, empty when it interpenetrates
    none. `seats` is what the corners have left: a reroute lengthens one leg and shortens
    another, and the corners either side of a leg share what is left of it
    (`_routing.seat_radii`), so an offset stands clear of every body in the machine at one
    figure and is a corner the stock will not take at another. `clear` is both."""

    at: float               # mm along the reroute's direction
    hits: tuple             # the bodies interpenetrated, worst overlap first
    seats: float            # the smallest radius any corner seats at this offset
    corner: int | None      # which corner that is, indexed in the REDRAWN centreline
    floor: float            # the stock's minimum bend radius, what `seats` answers to
    corners: int            # how many corners the redraw has — a reroute can straighten one out

    @property
    def tight(self) -> bool:
        """A corner under its stock's floor: drawable on paper, not bendable on the bench."""
        return self.corner is not None and self.seats < self.floor - 1e-9

    @property
    def clear(self) -> bool:
        return not self.hits and not self.tight

    @property
    def why(self) -> str:
        """Why this offset is no good, in one phrase — the bodies, or the corner."""
        if self.hits:
            return ", ".join(self.hits)
        if self.tight:
            return f"corner {self.corner} seats R{self.seats:.3f}"
        return ""

    def __str__(self) -> str:
        what = ", ".join(self.hits) if self.hits else "CLEAR"
        if not self.tight:
            return f"{self.at:9.3f}  {what}"
        return (f"{self.at:9.3f}  {what:40s} · corner {self.corner} seats R{self.seats:.3f}, "
                f"under the stock's {self.floor:g}")


@dataclass
class Link:
    """One derivation that reads a run: what it reads it for, where it is stated, whether a
    redraw of the run's centreline carries it, and the gate that prices it in a build."""

    reads: str
    where: str
    carries: bool
    gates: str

    def __str__(self) -> str:
        return (f"{'rides ' if self.carries else 'STANDS'}  {self.reads}\n"
                f"            {self.where} — graded by {self.gates}")


def _chain_of(a, rid: str) -> tuple:
    """The derivations in the built assembly that name this run, read off the structures that
    key on a run id — a row added to one of them appears here without this being rewritten."""
    import enclosure_assembly as ea

    out = [Link("the longest stretch of it nothing holds, walked off the run and its anchors",
                "enclosure_assembly.unsupported_spans", True, "tube-anchored")]
    for row_id, leg, _root, piece in ea.TUBE_ANCHOR_SITES:
        if row_id == rid:
            out.append(Link(
                f"the rib {piece} stands for it, centred on leg {leg} — the leg INDEX is "
                f"stated, and a redraw that straightens a corner out renumbers the legs",
                "enclosure_assembly.TUBE_ANCHOR_SITES", True, "tube-seated, anchor-lands"))
    seat = ea._cci.cap_anchors.get(rid)
    if seat is not None:
        out.append(Link(
            f"the rib the cold core's cap stands for it, at {seat.centre} in the CAP's own "
            f"frame, reaching {seat.over_face:g} over that face",
            f"_cold_core_interface.cap_anchors[{rid!r}]", False, "run-seated, anchor-room"))
    for sleeve, line in ea.SLEEVE_LINES.items():
        if line == rid:
            out.append(Link(f"{sleeve}, closed on a length of it, with the MPR121's leads read "
                            f"off where it sits", "enclosure_assembly.SLEEVE_LINES", False,
                            "sleeve-grips"))
    return tuple(out)


@dataclass
class Band:
    """A contiguous stretch of the sample the run can be drawn in, and what ends it either side.

    `under` and `over` name what the first BLOCKED offset outside the band ran into — the thing
    to move if the band has to be wider. Either is None where the band runs off the end of the
    sweep, which is a fact about the range that was asked for and not about the machine."""

    lo: float
    hi: float
    under: str | None
    over: str | None

    def __str__(self) -> str:
        end = "the sweep ended here, not the machine"
        return (f"{self.lo:+.3f} … {self.hi:+.3f}   (under: {self.under or end}"
                f" · over: {self.over or end})")


@dataclass
class Reroute:
    """A range of positions for one piece of a run, and what the run hits at each of them.

    EVERY ROW IS A HALF-MOVE. The centreline is redrawn and `chain` — the ribs struck on the
    run, the cap's own seat for it, the span it is graded on, the sleeve that closes on it —
    stands where it stood. The whole move is [`calibration/Chain.md`](/calibration/Chain.md).

    `held_out` is the other half of every CLEAR: the run's own tube is out of the measurement,
    being the body this centreline was swept into. Every row is exact at its own offset and
    says nothing about the millimetre either side of it, so a band reaches as far as the step
    that drew it."""

    run: str
    moving: tuple           # the waypoint indices that translated
    along: tuple
    poses: list
    held_out: tuple
    chain: tuple = ()       # the derivations reading this run, see `World.chain`
    measured: str = ""

    @property
    def clear(self) -> list:
        """Every offset the run can actually be drawn at — nothing in the way, corners at
        spec."""
        return [p for p in self.poses if p.clear]

    @property
    def bands(self) -> list:
        """The clear offsets gathered into contiguous stretches of the sample, each carrying
        what stops it either side."""
        out, run_ = [], []
        for i, p in enumerate(self.poses):
            if p.clear:
                run_.append((i, p))
                continue
            if run_:
                out.append(self._band(run_))
                run_ = []
        if run_:
            out.append(self._band(run_))
        return out

    def _band(self, gathered: list) -> Band:
        first, last = gathered[0][0], gathered[-1][0]
        under = self.poses[first - 1].why if first > 0 else None
        over = self.poses[last + 1].why if last + 1 < len(self.poses) else None
        return Band(gathered[0][1].at, gathered[-1][1].at, under, over)

    def __str__(self) -> str:
        d = self.along
        moving = ", ".join(str(i) for i in self.moving)
        out = [f"{self.run}, waypoint{'s' if len(self.moving) > 1 else ''} {moving} along "
               f"({d[0]:g}, {d[1]:g}, {d[2]:g})"]
        if self.measured:
            out.append(f"  measured against {self.measured}")
        out.append(f"  holding out: {', '.join(self.held_out)}")
        out.append(f"  the rest of the build that reads {self.run}, none of which any row "
                   f"below moves (calibration/Chain.md):")
        out += [f"    {link}" for link in self.chain] or [
            "    nothing recorded — this world was not built from the assembly"]
        out.append(f"  {'offset':>9}  runs into")
        out += [f"  {p}" for p in self.poses]
        bands = self.bands
        if not bands:
            out.append(f"  nothing clear anywhere in the {len(self.poses)} offsets swept")
        else:
            out.append(f"  clear at {len(self.clear)} of {len(self.poses)} offsets:")
            out += [f"    {b}" for b in bands]
        return "\n".join(out)


# --- the world ------------------------------------------------------------

class World:
    """The placed solids, flat and normalized: `{name: cq.Shape}`.

    One dict, every body, so no query can be written that quietly leaves a wall out.
    The roles stay legible through `sources`, and `pieces` / `parts` split the world
    the way `scorecard.pack_clashes` splits its arguments."""

    def __init__(self, solids: dict, sources: dict, pieces_held_out: bool = False,
                 frames: dict = None, box=None, runs: dict = None,
                 runs_held_out: bool = False, chains: dict = None):
        self.solids = solids
        # name → "component" | "display" | "funnel" | "run" | PIECE
        self.sources = sources
        self.pieces_held_out = pieces_held_out      # asked for without pieces, see measured
        self.runs_held_out = runs_held_out          # asked for without tubes, see measured
        # The frames the tubes were swept along and the box the pieces were cut from, as the
        # assembly carries them.
        self._frames = frames
        self.box = box
        # The AUTHORED runs behind the `tube-*` bodies — `{id: _routing.Run}`, the centrelines
        # themselves rather than the swept solids. `reroute` moves a piece of one.
        self._runs = runs
        # `{id: (Link, …)}` — what else in the build reads each run, taken off the assembly
        # that drew them, see `chain`.
        self._chains = chains or {}
        self._boxes = {}                # name → (solid, box), see bb()

    # -- what is here --

    @property
    def names(self) -> list:
        return sorted(self.solids)

    def solid(self, name: str):
        if name not in self.solids:
            raise KeyError(f"no body {name!r} — have: {', '.join(self.names)}")
        return self.solids[name]

    def tagged(self, *sources) -> tuple:
        """Every body carrying one of these source tags."""
        return tuple(n for n in self.names if self.sources[n] in sources)

    @property
    def pieces(self) -> tuple:
        """The printed enclosure pieces — what `scorecard.pack_clashes` takes as its
        `pieces`. `skip=w.pieces` is how a query asks about the interior pack alone."""
        return self.tagged(PIECE)

    @property
    def parts(self) -> tuple:
        """Every body that is not a printed piece — what the same gate takes as `solids`."""
        return tuple(n for n in self.names if self.sources[n] != PIECE)

    @property
    def measured(self) -> str:
        """What a query against this world was measured against, in one line. A scan that
        reports its bounds and not this is reporting half of where its answer came from:
        the pieces are what a placement in a full machine runs into first."""
        head = f"{len(self.solids)} bod{'y' if len(self.solids) == 1 else 'ies'}"
        if self.runs_held_out:
            head += ", NO routed tubes (runs=False) — every line on the machine is missing"
        if self.pieces:
            return f"{head}, {len(self.pieces)} of them printed enclosure pieces"
        if self.pieces_held_out:
            return (f"{head}, NO printed enclosure pieces ({SKIP_PIECES}) — a free answer "
                    f"here is not one the pack-closes gate agrees with")
        return f"{head}, no printed enclosure pieces"

    def bb(self, name: str):
        """A body's bounding box, held once per solid. Taking one costs real time on a
        compound, and a scan over the world takes every one of them. The cached box is
        kept against the solid it was measured from, so a body swapped into `solids`
        after loading is re-measured rather than read from the previous one."""
        s = self.solid(name)
        held = self._boxes.get(name)
        if held is not None and held[0] is s:
            return held[1]
        b = s.BoundingBox()
        self._boxes[name] = (s, b)
        return b

    def table(self, sort: str = "name", only=None) -> str:
        """Every body's box, one per line, sorted by `name` or any box
        attribute (`ymin`, `zmax`, …)."""
        names = list(only) if only else self.names
        if sort != "name":
            names.sort(key=lambda n: getattr(self.bb(n), sort))
        out = []
        for n in names:
            b = self.bb(n)
            out.append(f"{n:28s} {self.sources[n]:9s} "
                       f"x[{b.xmin:8.2f},{b.xmax:8.2f}] y[{b.ymin:8.2f},{b.ymax:8.2f}] "
                       f"z[{b.zmin:8.2f},{b.zmax:8.2f}]")
        return "\n".join(out)

    # -- ports --

    def frames(self) -> dict:
        """`{component: Frame}` as the assembly was built with them — `.at(port)`,
        `.normal(port)`, `.diam(port)`, `.bb`.

        Holds one entry per body whose reference module states a port table."""
        if self._frames is None:
            raise ValueError("this world carries no port frames — it was built from an "
                             "assembly without them")
        return self._frames

    def at(self, component: str, port: str) -> tuple:
        return self.frames()[component].at(port)

    def normal(self, component: str, port: str) -> tuple:
        return self.frames()[component].normal(port)

    def ports(self, component: str) -> list:
        return sorted(self.frames()[component].ports)

    # -- the authored runs --

    @property
    def runs(self) -> dict:
        """`{id: _routing.Run}` — the CENTRELINES the `tube-*` bodies were swept along, as
        `_lines` authored them. The body `tube-fluid-14` is what that run runs into; the run
        `fluid-14` is the waypoints it was drawn through, and the thing `reroute` moves."""
        if self._runs is None:
            raise ValueError("this world carries no authored runs — it was built from an "
                             "assembly without them")
        return self._runs

    def run(self, name: str):
        """One authored run by id (`fluid-14`, not `tube-fluid-14`)."""
        name = name[5:] if name.startswith("tube-") else name
        if name not in self.runs:
            raise KeyError(f"no run {name!r} — have: {', '.join(sorted(self.runs))}")
        return self.runs[name]

    def chain(self, run) -> tuple:
        """Everything else in the build that reads this run, and whether a redraw of its
        centreline carries them.

        Ribs are struck on its legs, the cold core's cap stands a seat for it at a station in
        the cap's own frame, the stretch between held points is graded, a cap-sense sleeve
        closes on the line it grips. `reroute` moves the centreline and none of these; this is
        the list of what it leaves standing. [`calibration/Chain.md`](/calibration/Chain.md)."""
        r = run if hasattr(run, "pts") else self.run(run)
        return self._chains.get(r.id, ())

    def route(self, run, near=None) -> str:
        """One run's centreline written out waypoint by waypoint — the table an INDEX is read
        off before `reroute` moves one.

        Each interior waypoint is a corner and carries the two figures that decide whether it
        can move: the angle it turns and the radius it seats there, against its stock's floor.
        `near=(x, y, z)` marks the waypoint closest to a point, which is how a pick off the
        STEP — the coordinates of an arc, a face, an edge — becomes an index."""
        r = run if hasattr(run, "pts") else self.run(run)
        floor = _routing.stock_min(r.kind, r.diam)
        head = (f"{r.id}  {r.frm} → {r.to}  {r.kind} Ø{r.diam:g}  {r.length:.2f} mm  "
                f"{len(r.bends)} corner{'s' if len(r.bends) != 1 else ''}, stock min R{floor:g}")
        pick = None
        if near is not None:
            pick = min(range(len(r.pts)), key=lambda i: math.dist(r.pts[i], near))
        turns = {i: t for i, t, _a, _b in r.bends}
        out = [head]
        for i, p in enumerate(r.pts):
            row = f"  {i:2d}  ({p[0]:9.3f}, {p[1]:9.3f}, {p[2]:9.3f})"
            if i in turns:
                seat = r.radii[i]
                row += (f"   turns {turns[i]:5.1f}°  seats R{seat:6.3f}"
                        f"{'' if seat >= floor - 1e-9 else '  UNDER STOCK'}")
            if i == pick:
                row += f"   ← nearest the pick, {math.dist(p, near):.3f} mm off"
            out.append(row)
        return "\n".join(out)

    # -- distance --

    def gap(self, a, b) -> float:
        """Exact minimum distance between two bodies (0 if they touch or
        overlap). Names or shapes. Raises rather than falling back to a box
        approximation — a box gap is not a clearance."""
        sa = self.solid(a) if isinstance(a, str) else shape(a, "a")
        sb = self.solid(b) if isinstance(b, str) else shape(b, "b")
        dss = BRepExtrema_DistShapeShape(sa.wrapped, sb.wrapped)
        if not dss.IsDone():
            raise RuntimeError(
                f"exact distance failed between {a if isinstance(a, str) else 'a'} and "
                f"{b if isinstance(b, str) else 'b'} — the result is unknown, not large")
        return dss.Value()

    def nearest(self, target, skip=()) -> tuple:
        """The closest body to `target` as `(gap_mm, name)`, skipping `skip`."""
        gaps = [(self.gap(name, target), name)
                for name in self.names if name not in skip]
        if not gaps:
            raise ValueError("nearest: every body was skipped")
        return min(gaps)

    # -- what a volume runs into --

    def hits(self, vol, skip=(), tol: float = VOL_TOL) -> list:
        """Every body `vol` interpenetrates, worst first, each with its overlap
        volume and the overlap's own extents. A boolean that fails raises with
        the body named — it is never counted as a miss."""
        v = shape(vol, "probe volume")
        out = []
        for name in self.names:
            if name in skip:
                continue
            try:
                inter, overlap = _common(v, self.solids[name])
            except Exception as exc:
                raise RuntimeError(
                    f"intersection with {name} failed ({exc}) — this body's "
                    f"occupancy is unknown, not empty") from exc
            if overlap > tol:
                out.append(Hit(name, overlap, _meshes.box(inter)))
        return sorted(out, key=lambda h: -h.volume)

    def clear(self, vol, skip=()) -> bool:
        return not self.hits(vol, skip=skip)

    # -- how far a body can move --

    def travel(self, mover: str, direction, limit: float = TRAVEL_LIMIT, skip=(),
               clearance: float = 0.0, coarse: float = 1.0, tol: float = VOL_TOL) -> Travel:
        """How far `mover` translates along `direction` before each body stops it, nearest
        first. The answer to "can this move, and what does it cost" — one reading, no grid.

        A body standing clear is measured by advancing the mover by its own exact gap, which
        cannot step over a contact (`gap` is 1-Lipschitz under translation), so that distance
        is exact rather than sampled. A body the mover already RESTS on cannot be measured that
        way — its gap stays 0 down the whole slide — so it is tested against the mover's swept
        box, which contains every place the mover reaches: a body outside it exactly never
        blocks, and one inside is bracketed on `coarse` and bisected to 1e-4. The error runs
        one way — a body reported as no obstacle is exactly that, and a `seated` row's distance
        is the bracketed figure rather than a stepped one."""
        d = unit(direction)
        solid = self.solid(mover)
        skipped = tuple(sorted(set(skip) | {mover}))
        stops, sliding = [], []

        def moved(t):
            return solid.translate((d[0] * t, d[1] * t, d[2] * t))

        for name in self.names:
            if name in skipped:
                continue
            other = self.solids[name]
            # A resting face contact measures as a gap of ~1e-16 rather than a clean 0, and
            # read as a gap it closes on the first stride and reports the seat as the stop.
            if self.gap(mover, name) > max(clearance, CONTACT_EPS):
                # Clear at rest: close the gap in exact strides.
                t, hit = 0.0, None
                while t <= limit:
                    g = self.gap(moved(t), other) - clearance
                    if g <= 1e-9:
                        hit = t
                        break
                    t += g
                if hit is not None:
                    stops.append(Stop(round(hit, 4), name))
                continue

            # Touching at rest. Everywhere the mover can reach lies inside its swept box, so a
            # body outside that box is exactly one this slide never meets.
            try:
                if _common_volume(_swept_box(solid, d, limit), other) <= tol:
                    sliding.append(name)
                    continue
            except Exception as exc:
                raise RuntimeError(
                    f"sweeping {mover} against {name} failed ({exc}) — the travel past this "
                    f"body is unknown, not clear") from exc

            def blocked(t):
                return _common_volume(moved(t), other) > tol

            if blocked(0.0):
                stops.append(Stop(0.0, name, seated=True))
                continue
            lo = 0.0
            hi = None
            t = coarse
            while t <= limit:
                if blocked(t):
                    hi = t
                    break
                lo, t = t, t + coarse
            if hi is None:
                # The sweep found material this stepping did not reach: report the bracket's
                # own floor rather than a clear, since the sweep is the exact witness.
                stops.append(Stop(round(lo, 4), name, seated=True, exact=False))
                continue
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if blocked(mid):
                    hi = mid
                else:
                    lo = mid
                if hi - lo < 1e-4:
                    break
            stops.append(Stop(round(hi, 4), name, seated=True, exact=False))

        stops.sort(key=lambda s: s.at)
        return Travel(mover, d, stops, limit, clearance, tuple(sorted(sliding)), skipped)

    # -- how far a line can run --

    def cast(self, origin, direction, dia: float = TUBE_OD,
             limit: float = CAST_LIMIT, skip=(), tol: float = VOL_TOL) -> Contact:
        """First contact of a tube of `dia` launched from `origin` along
        `direction`. Exact: the intersection solid is projected onto the cast
        axis and its minimum taken, so the answer does not depend on a vertex
        happening to sit at the nearest point."""
        d = unit(direction)
        probe_rod = rod(origin, d, limit, dia)
        best, who = limit, None
        for name in self.names:
            if name in skip:
                continue
            try:
                inter, overlap = _common(probe_rod, self.solids[name])
                if overlap <= tol:
                    continue
            except Exception as exc:
                raise RuntimeError(
                    f"cast against {name} failed ({exc}) — the free run past this "
                    f"body is unknown, not clear") from exc
            t = _clearing.axis_min(inter, origin, d)
            if t < best:
                best, who = max(0.0, t), name
        return Contact(best, who, tuple(origin), d, limit, dia)

    # -- where a piece of a routed line can stand --

    def drawn(self, run, pts, at: float = 0.0, skip=(), tol: float = VOL_TOL) -> Offset:
        """What a run runs into when drawn through `pts` instead of its own waypoints — one
        candidate centreline, redrawn at its own bore and measured against everything but the
        body it already has in the world.

        Takes the whole point list, so a waypoint can be DROPPED as well as moved: a cluster
        authored around a body that has gone somewhere else comes out by handing back the list
        without it.

            r = w.run("fluid-14")
            w.drawn(r, [p for i, p in enumerate(r.pts) if i not in (3, 4)])

        `reroute` is this over a range of translations. `at` labels the row. The two ends must
        stay on their ports, and `chain` is what this leaves standing either way."""
        r = run if hasattr(run, "pts") else self.run(run)
        pts = [tuple(float(c) for c in p) for p in pts]
        for end, (i, j) in (("first", (0, 0)), ("last", (-1, -1))):
            off = math.dist(pts[i], r.pts[j])
            if off > 1e-6:
                raise ValueError(
                    f"{r.id}: the {end} point is {off:.3f} mm off the port it closes on "
                    f"({r.frm if end == 'first' else r.to}). A run's ends are mouths on placed "
                    f"bodies — move the body in `enclosure_assembly.py` and every waypoint "
                    f"measured off it follows, this list included.")
        redrawn = _routing.redrawn(r, pts)
        try:
            tube = _routing.tube(redrawn)
        except Exception as exc:
            raise RuntimeError(
                f"{r.id} will not sweep down this centreline ({exc}) — what it runs into is "
                f"unknown, not nothing.") from exc
        own = f"tube-{r.id}"
        held = tuple(sorted(set(skip) | ({own} if own in self.solids else set())))
        seats, corner = min(((redrawn.radii[i], i) for i, _t, _a, _b in redrawn.bends),
                            default=(math.inf, None))
        return Offset(at, tuple(h.name for h in self.hits(tube, skip=held, tol=tol)),
                      seats, corner, _routing.stock_min(r.kind, r.diam), len(redrawn.bends))

    def reroute(self, run, moving, along, values, skip=(), tol: float = VOL_TOL) -> Reroute:
        """Slide named waypoints of an authored run along a direction, and say what the run
        RUNS INTO at each offset. Collisions, one row per position.

        `moving` is which waypoints translate — one index, or any iterable of them; a bend is
        two, a corner one, a crossing however many carry it. `w.route(id)` prints them
        numbered and takes a pick off the STEP to say which index that is. `values` are offsets
        in mm along `along`, either sign; `steps()` makes the float range.

            w.reroute("fluid-14", (3, 4), "-y", probe.steps(0, 80, 2.5))

        THE CENTRELINE IS REDRAWN, not translated. A moved waypoint stretches one of its legs
        and shortens the other, and both corners on a shortened leg lose the tangent they seat
        their arcs in, so the whole run goes through `_routing.redrawn` at every offset and is
        swept again at its own bore. The radius that leaves is `Offset.seats`.

        MEASURED AGAINST every body in this world but the run's own tube, which is out of it —
        that body is what this centreline was swept into. `skip=` takes anything else moving
        with it. The pack, the other lines and the printed walls are in, and `Reroute.__str__`
        prints what they were.

        WHAT DOES NOT MOVE is `Reroute.chain`, printed with the sweep: the ribs struck on this
        run, the cap's own seat for it, the stretch it is graded on, the sleeve that closes on
        it. Its two END waypoints do not move either — they are mouths on placed bodies, and a
        run drawn off one reaches no fitting."""
        r = run if hasattr(run, "pts") else self.run(run)
        idx = _moving(moving, len(r.pts), r.id)
        d = unit(along)
        own = f"tube-{r.id}"
        held = tuple(sorted(set(skip) | ({own} if own in self.solids else set())))
        values = [float(v) for v in values]
        if not values:
            raise ValueError(f"{r.id}: a reroute over no offsets answers nothing — give it a "
                             f"range (`probe.steps(lo, hi, step)`), 0.0 among them to read "
                             f"the run where it stands")
        rows = [self.drawn(r, [p if i not in idx else tuple(p[k] + d[k] * v for k in range(3))
                               for i, p in enumerate(r.pts)], v, skip=skip, tol=tol)
                for v in values]
        return Reroute(r.id, idx, d, rows, held, self.chain(r), self.measured)


# --- vector helpers -------------------------------------------------------

_AXIS = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


def unit(v) -> tuple:
    """A unit direction from a 3-vector, or from a NAMED axis: `"+x"`, `"x+"`, `"-y"`, `"y-"`,
    `"z"`, `"0,-1,0"`.

    The sign is taken on either end because a bare `-y` in a shell positional is read as a flag
    by argparse and never reaches here — `y-` is the form that always arrives, and the two mean
    the same thing wherever a direction is asked for."""
    if isinstance(v, str):
        t = v.strip()
        for sign, axis in ((t[:1], t[1:]), (t[-1:], t[:-1])):
            if sign in "+-" and axis in _AXIS:
                a = _AXIS[axis]
                return a if sign == "+" else tuple(-c for c in a)
        if t in _AXIS:
            return _AXIS[t]
        if "," not in t:
            raise ValueError(f"direction {v!r} names no axis — write y-, +z, or x,y,z (the sign "
                             f"goes LAST from a shell, where a leading -y reads as a flag)")
        v = t.split(",")
    n = math.sqrt(sum(float(c) * float(c) for c in v))
    if n < 1e-12:
        raise ValueError(f"direction {tuple(v)} has no length")
    return tuple(float(c) / n for c in v)


def _swept_box(sh, d, length: float):
    """A box holding everywhere `sh` reaches while translating `length` along `d`. It contains
    the true swept volume and is generally larger than it, so a body it does not touch is one
    the mover exactly cannot reach, while a body it does touch has still to be measured."""
    b = sh.BoundingBox()
    lo = [b.xmin, b.ymin, b.zmin]
    hi = [b.xmax, b.ymax, b.zmax]
    for i in range(3):
        step = d[i] * length
        lo[i] += min(0.0, step)
        hi[i] += max(0.0, step)
    return box(x=(lo[0], hi[0]), y=(lo[1], hi[1]), z=(lo[2], hi[2]))


def _moving(moving, n: int, cid: str) -> tuple:
    """Which waypoints a `reroute` translates: one index, or any iterable of them.

    The first and last are the run's PORTS and are refused. They are mouths on placed bodies
    and they move when those bodies move — a run drawn off one does not reach its fitting, so
    the sweep would be over positions that are not connections."""
    idx = (moving,) if isinstance(moving, int) else tuple(moving)
    if not idx:
        raise ValueError(f"{cid}: a reroute has to move at least one waypoint")
    bad = [i for i in idx if not isinstance(i, int) or not -n <= i < n]
    if bad:
        raise ValueError(f"{cid}: {', '.join(str(i) for i in bad)} "
                         f"{'name' if len(bad) > 1 else 'names'} no waypoint of a run that has "
                         f"{n} of them (0…{n - 1}) — `w.route({cid!r})` prints them numbered")
    idx = tuple(sorted({i % n for i in idx}))
    ends = [i for i in idx if i in (0, n - 1)]
    if ends:
        raise ValueError(
            f"{cid}: waypoint{'s' if len(ends) > 1 else ''} "
            f"{', '.join(str(i) for i in ends)} "
            f"{'are' if len(ends) > 1 else 'is'} the run's PORT — a mouth on a placed body, "
            f"which moves when that body moves and not before. "
            + (f"This run is one straight between two of them and has no interior waypoint "
               f"to reroute. " if n == 2 else f"Reroute the interior waypoints (1…{n - 2}). ")
            + f"To stand a fitting somewhere else, move its body in `enclosure_assembly.py`, "
              f"and every waypoint measured off it follows.")
    return idx


# --- sweeping a continuous parameter --------------------------------------

def steps(lo: float, hi: float, step: float) -> list:
    """`lo` to `hi` INCLUSIVE in `step` mm — the float range `range()` will not give, and what
    a sweep of positions is asked over. Ends given the other way round come back ascending."""
    if step <= 0:
        raise ValueError(f"steps({lo}, {hi}, {step}): the step has to be positive — the range "
                         f"runs from the smaller end whichever order it is given in")
    lo, hi = (lo, hi) if hi >= lo else (hi, lo)
    n = int(math.floor((hi - lo) / step + 1e-9))
    return [round(lo + i * step, 9) for i in range(n + 1)]


def sweep(values, fn, label: str = "value", fmt: str = "{}") -> list:
    """Run `fn` across `values` and print one row each — the answer to "which
    setting is best" when the parameter is continuous and the helper that
    consumes it only exposes a few poses. Returns the `(value, result)` pairs."""
    rows = []
    for v in values:
        r = fn(v)
        rows.append((v, r))
        print(f"{label} {fmt.format(v):>10}  {r}")
    return rows


def best(rows, key=None):
    """The `(value, result)` row maximizing `key`. A Contact that never made
    contact scores infinite rather than its limit — its `free` is the length of
    the cast, and ranking that against real clearances compares a measurement
    with a setting. Ties are common at infinity; `unblocked()` lists them all."""
    def default(r):
        if isinstance(r, Contact):
            return math.inf if not r.blocked else r.free
        return r
    return max(rows, key=lambda vr: (key or default)(vr[1]))


def unblocked(rows) -> list:
    """Every `(value, Contact)` row whose cast reached its limit untouched."""
    return [(v, r) for v, r in rows if isinstance(r, Contact) and not r.blocked]


# --- sweeping a design constant -------------------------------------------

@dataclass
class Rebuild:
    """One value of a swept constant and what building at it produced."""

    value: object
    result: object = None
    error: str | None = None

    @property
    def built(self) -> bool:
        return self.error is None

    def __str__(self) -> str:
        return f"{self.value}: {self.error if self.error else 'built'}"


def rebuild_sweep(module, attr: str, values, build, label: str = None) -> list:
    """Set `module.attr` to each value, call `build()`, and collect what it returns.

    `sweep` asks a question of one placed world; this one rebuilds the world per value —
    the parameter is a constant the geometry is generated from, not an argument to a query.
    The attribute is restored however the sweep ends, and a value whose build raises is kept
    as its error rather than stopping the run.

    Reads a constant the pack is built from (rather than the box around it) and this module's
    own memoized `world()` will hand back the pack from before the change — call
    `world(reload=True)` after, or sweep in a fresh process."""
    label = label or f"{module.__name__}.{attr}"
    original = getattr(module, attr)
    out = []
    try:
        for v in values:
            setattr(module, attr, v)
            try:
                row = Rebuild(v, build())
            except Exception as exc:                    # a value that will not build is a result
                row = Rebuild(v, None, f"{type(exc).__name__}: {exc}")
            out.append(row)
            print(f"{label} = {v!r:>10}  {'built' if row.built else row.error}")
    finally:
        setattr(module, attr, original)
    return out


def bed_fit(pieces: dict = None, bed=None) -> list:
    """Each printed piece against the H2C's bed: `(name, xlen, ylen, zlen, fits)` per piece,
    on `BED_TOL`. With no `pieces`, the world's own. Values normalize through `shape()`, so a
    `build_pieces()` Workplane is accepted. The pieces are stored in print orientation, so the
    test is per-axis."""
    _ensure_paths()
    import enclosure

    if pieces is None:
        w = world()
        pieces = {n: w.solid(n) for n in w.pieces}
    if bed is None:
        bed = (enclosure.H2C_X, enclosure.H2C_Y, enclosure.H2C_Z)
    bx, by, bz = bed
    out = []
    for n, p in pieces.items():
        b = shape(p, n).BoundingBox()
        out.append((n, b.xlen, b.ylen, b.zlen,
                    b.xlen <= bx + BED_TOL and b.ylen <= by + BED_TOL and b.zlen <= bz + BED_TOL))
    return out


# --- loading --------------------------------------------------------------

_WORLDS: dict = {}              # (runs, pieces) → World, see world()


def _ensure_paths() -> None:
    """The machine's modules on sys.path, and the env a read-only run wants."""
    os.environ.setdefault("HSM_SKIP_THUMBNAILS", "1")
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    for d in (_ML, _BOX):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))


def _assembly():
    """`enclosure_assembly` — the module that states which bodies are placed, where each one is
    turned to, what is seated in the walls and how the box is cut."""
    _ensure_paths()
    import enclosure_assembly
    return enclosure_assembly


# How a child of the enclosure assembly is tagged. The names carry the role: the box's four
# printable pieces come in under `enclosure-`, the swept runs under `tube-`, and the two
# bodies seated in walls rather than standing in the pack are named outright.
def _source(name: str) -> str:
    if name.startswith("enclosure-"):
        return PIECE
    if name.startswith("tube-"):
        return "run"
    return {"display": "display", "hopper-funnel": "funnel"}.get(name, "component")


def world(runs: bool = True, pieces: bool = True, reload: bool = False) -> World:
    """The placed world — the same bodies `scorecard.pack_clashes` measures: the pack's
    components, the bodies seated through the walls, the display in its facet
    housing, the hopper funnel, the four printed enclosure pieces, and (unless
    `runs=False`) the routed tubes.

    The pieces are IN by default, and the default is the whole point. Left out, every
    query still answers, and the one it gets wrong is the dangerous direction: a pose clear
    of every interior body reads CLEAR while standing in a wall, a seam lip or a boss chain
    — and the pack-closes gate, which does compare the interior solids against the pieces,
    then reds on the pose the answer was chosen for. In by default, that answer is one you
    have to ask for; out by default, it is the one you get by forgetting.

    `pieces=False` (or `HSM_SKIP_PIECES=1`) leaves them out, for a tree whose
    `enclosure-*.step` have not been exported. It costs the answer the walls, and it is not
    a speed setting: the pieces are four STEP imports (~0.3 s) on a world that takes
    seconds, ~0.04 s of exact distance per body compared against them, and a `slab` band
    they reach into. `w.measured` says which way a world was built, and both scans print
    it.

    Memoized per (runs, pieces) — building one places every body in the machine."""
    want_pieces = bool(pieces) and not os.environ.get(SKIP_PIECES)
    key = (bool(runs), want_pieces)
    if reload:
        _WORLDS.clear()
    elif key in _WORLDS:
        return _WORLDS[key]

    # The whole machine in one assembly — pack bodies, the funnel and display seated in the
    # walls, the four printed pieces, the swept runs — carrying the frames and the box it was
    # built from. The same object the build exports and reports on.
    a = _assembly().build_enclosure_assembly()

    solids, sources = {}, {}

    def add(name, obj, source):
        if name in solids:
            raise ValueError(f"two bodies named {name!r} ({sources[name]} and {source})")
        solids[name] = shape(obj, name)
        sources[name] = source

    for name, (solid, _color) in _assembly()._solids(a).items():
        src = _source(name)
        if src == PIECE and not want_pieces:
            continue
        if src == "run" and not runs:
            continue
        add(name, solid, src)

    # The AUTHORED runs come across whether or not their tubes did: they are the centrelines
    # `_lines` drew, and `reroute` asks what a piece of one could do. A world built `runs=False`
    # says so in `measured`, which is what a reroute there has to be read against. Each one
    # arrives with the rest of the build that reads it (`chain`), taken off the same assembly.
    drawn = {r.id: r for r in getattr(a, "runs", ())}
    _WORLDS[key] = World(solids, sources, pieces_held_out=not want_pieces,
                         frames=getattr(a, "frames", None), box=getattr(a, "box", None),
                         runs=drawn, runs_held_out=not runs,
                         chains={rid: _chain_of(a, rid) for rid in drawn})
    return _WORLDS[key]


def wall_sample(w: World = None, side: float = 10.0):
    """A volume buried in a printed piece that every interior body clears — the one case an
    instrument gets wrong when the pieces are not in its world, handed back as a solid so a
    control can put the question to `hits`, to `cast` or to `fit.check`.

    Cut from the floor slab, between the cavity floor and the outer skin, where the material
    is a piece's by construction and no interior body can reach: the pack stands ON the
    floor. Derived from the box's own dimensions and confirmed against the world rather than
    written down, so it survives the box being redrawn. Raises when no such volume can be
    found, because a control that quietly tests nothing passes for the wrong reason."""
    w = w or world()
    if not w.pieces:
        raise ValueError(
            "wall_sample: this world holds no printed pieces to sample — "
            f"it was built with pieces=False or under {SKIP_PIECES}")
    if w.box is None:
        raise ValueError("wall_sample: this world carries no box to cut a sample from")
    inner, outer = w.box.inner, w.box.outer
    if outer[4] >= inner[4] - 1.0:
        raise ValueError(
            f"wall_sample: the floor slab is {inner[4] - outer[4]:.2f} mm thick, too thin to "
            f"cut a sample out of — pick another wall")
    z = (outer[4] + 0.5, inner[4] - 0.5)
    tried = []
    for fy in (0.2, 0.8, 0.5, 0.35, 0.65):
        for fx in (0.5, 0.25, 0.75):
            cx = inner[0] + fx * (inner[1] - inner[0])
            cy = inner[2] + fy * (inner[3] - inner[2])
            cut = box(x=(cx - side / 2, cx + side / 2), y=(cy - side / 2, cy + side / 2), z=z)
            buried = [h for h in w.hits(cut) if w.sources[h.name] == PIECE]
            if not buried:
                tried.append(f"({cx:.0f}, {cy:.0f}) is not in a piece")
                continue
            sample, _vol = _common(cut, w.solid(buried[0].name))
            loose = w.hits(sample, skip=w.pieces)
            if loose:
                tried.append(f"({cx:.0f}, {cy:.0f}) shares the slab with {loose[0].name}")
                continue
            return sample
    raise ValueError("wall_sample: no floor-slab volume is both inside a piece and clear of "
                     "every interior body — " + "; ".join(tried))


# --- instrument check -----------------------------------------------------

def selftest() -> int:
    """Known-answer controls, then a normalization pass over the real world.
    The controls exist because a probe that silently measures nothing reports
    the same shape of number as one that works."""
    fails = []

    def check(label, got, want, tol=1e-6):
        ok = abs(got - want) <= tol
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:44s} got {got:.6f}  want {want:.6f}")
        if not ok:
            fails.append(label)

    plate = box(x=(-50, 50), y=(-200, 200), z=(100, 110))
    near = box(x=(-5, 5), y=(-5, 5), z=(0, 10))
    overlapping = box(x=(0, 10), y=(0, 10), z=(5, 15))
    w = World({"plate": plate, "near": near, "overlapping": overlapping},
              {"plate": "test", "near": "test", "overlapping": "test"})

    print("controls — distance:")
    check("known gap, plate to near", w.gap("plate", "near"), 90.0)
    check("known gap, overlapping pair", w.gap("near", "overlapping"), 0.0)

    print("controls — overlap:")
    hits = w.hits(box(x=(0, 10), y=(0, 10), z=(6, 16)), skip=("plate",))
    names = {h.name for h in hits}
    print(f"  {'ok  ' if names == {'near', 'overlapping'} else 'FAIL'}  "
          f"known hit set{'':31s} got {sorted(names)}  want ['near', 'overlapping']")
    if names != {"near", "overlapping"}:
        fails.append("known hit set")
    # the probe box spans x,y (0,10) and near spans (-5,5): they share 5 × 5, over z 6..10
    check("known overlap volume, into near", next(h.volume for h in hits if h.name == "near"),
          5 * 5 * 4, tol=1e-3)
    miss = w.hits(box(x=(200, 210), y=(200, 210), z=(200, 210)))
    print(f"  {'ok  ' if not miss else 'FAIL'}  known miss returns nothing"
          f"{'':19s} got {[h.name for h in miss]}  want []")
    if miss:
        fails.append("known miss")

    print("controls — cast:")
    up = w.cast((0, 0, 20), (0, 0, 1), dia=1.0, limit=300.0, skip=("near", "overlapping"))
    check("cast up to the plate", up.free, 80.0, tol=1e-3)
    print(f"  {'ok  ' if up.blocker == 'plate' else 'FAIL'}  cast names its blocker"
          f"{'':18s} got {up.blocker}  want plate")
    if up.blocker != "plate":
        fails.append("cast blocker")
    # A rod tilted θ off the plate normal touches early by its own radius: the
    # surface point nearest the plate sits r·sinθ above the axis.
    tilted = w.cast((0, 0, 20), (0, 1, 1), dia=1.0, limit=300.0, skip=("near", "overlapping"))
    cos_t = sin_t = 1.0 / math.sqrt(2.0)
    check("cast at 45° to the plate", tilted.free, (100.0 - 20.0 - 0.5 * sin_t) / cos_t, tol=1e-3)
    away = w.cast((0, 0, 20), (0, 0, -1), dia=1.0, limit=40.0, skip=("near", "overlapping"))
    print(f"  {'ok  ' if not away.blocked else 'FAIL'}  cast with no contact reports none"
          f"{'':11s} got {away.blocker}  want None")
    if away.blocked:
        fails.append("cast no-contact")

    print("controls — travel:")
    # A block on a long rail, a post standing 3 mm east of it, and a second post 12 mm on.
    # The rail runs under the block the whole way: a seat it slides over, never a blocker.
    rail = box(x=(-100, 100), y=(-20, 20), z=(-5, 0))
    mover = box(x=(0, 10), y=(-5, 5), z=(0, 10))
    post = box(x=(13, 18), y=(-5, 5), z=(0, 10))
    far = box(x=(30, 35), y=(-5, 5), z=(0, 10))
    tw = World({"rail": rail, "mover": mover, "post": post, "far": far},
               {n: "test" for n in ("rail", "mover", "post", "far")})
    tr = tw.travel("mover", (1, 0, 0), limit=60.0)
    check("travel to the first post", tr.free, 3.0, tol=1e-3)
    order = [s.name for s in tr.stops]
    print(f"  {'ok  ' if order == ['post', 'far'] else 'FAIL'}  the whole stop list, nearest "
          f"first{'':7s} got {order}  want ['post', 'far']")
    if order != ["post", "far"]:
        fails.append("travel stop order")
    check("the stop behind the binder is priced too",
          next(s.at for s in tr.stops if s.name == "far"), 20.0, tol=1e-3)
    print(f"  {'ok  ' if tr.sliding == ('rail',) else 'FAIL'}  a seat is named, never a "
          f"blocker{'':13s} got {tr.sliding}  want ('rail',)")
    if tr.sliding != ("rail",):
        fails.append("travel seat")
    # A body that runs out of query before it runs out of room says so: the limit is a fact
    # about the probe, and `free` reporting it is not a clearance.
    short = tw.travel("mover", (1, 0, 0), limit=2.0)
    print(f"  {'ok  ' if not short.stops else 'FAIL'}  travel under the first contact finds "
          f"none{'':5s} got {[s.name for s in short.stops]}  want []")
    if short.stops:
        fails.append("travel limit")
    # A feature of the very body it rests on: the rail grows a lip 6 mm east, and sliding on
    # the rail must not hide it. This is the shape that reads +0.000 to a gap alone.
    lipped = rail.fuse(box(x=(16, 20), y=(-20, 20), z=(0, 20)))
    lw = World({"rail": lipped, "mover": mover}, {"rail": "test", "mover": "test"})
    lt = lw.travel("mover", (1, 0, 0), limit=60.0)
    check("a lip on the seat still stops the slide",
          lt.stops[0].at if lt.stops else -1.0, 6.0, tol=1e-3)

    print("controls — ranking:")
    # `up` is stopped at 80; `away` never touched anything. The untouched cast
    # wins on having no contact, not on its limit outranking 80.
    ranked = [("stopped", up), ("untouched", away)]
    picked = best(ranked)[0]
    print(f"  {'ok  ' if picked == 'untouched' else 'FAIL'}  best prefers a no-contact cast"
          f"{'':13s} got {picked}  want untouched")
    if picked != "untouched":
        fails.append("best ranking")
    free_rows = [v for v, _ in unblocked(ranked)]
    print(f"  {'ok  ' if free_rows == ['untouched'] else 'FAIL'}  unblocked lists only the "
          f"untouched{'':6s} got {free_rows}  want ['untouched']")
    if free_rows != ["untouched"]:
        fails.append("unblocked filter")

    print("controls — the held bounding box:")
    wc = World({"body": box(x=(0, 10), y=(0, 10), z=(0, 10))}, {"body": "test"})
    first = wc.bb("body")
    check("a repeat read gives the same box", wc.bb("body").xmax, first.xmax)
    print(f"  {'ok  ' if wc.bb('body') is first else 'FAIL'}  a repeat read is the held box")
    if wc.bb("body") is not first:
        fails.append("bb caching")
    # An agent that injects a body into `solids` must not read the box of the one it replaced.
    wc.solids["body"] = box(x=(0, 99), y=(0, 10), z=(0, 10))
    check("a swapped body is re-measured", wc.bb("body").xmax, 99.0)

    print("controls — a piece is a body like any other, and says which it is:")
    # The shape of the defect, in miniature: a candidate clear of every interior body,
    # standing inside a printed wall. A world that answers CLEAR here answers CLEAR in the
    # machine, and the pack-closes gate then reds on the pose the answer was chosen for.
    wp = World({"part": box(x=(0, 10), y=(0, 10), z=(0, 10)),
                "wall": box(x=(50, 60), y=(0, 100), z=(0, 100))},
               {"part": "component", "wall": PIECE})
    inside = box(x=(52, 58), y=(20, 30), z=(20, 30))
    named = [h.name for h in wp.hits(inside)]
    print(f"  {'ok  ' if named == ['wall'] else 'FAIL'}  a volume in a piece is not clear"
          f"{'':17s} got {named}  want ['wall']")
    if named != ["wall"]:
        fails.append("piece occupancy")
    print(f"  {'ok  ' if wp.clear(inside, skip=wp.pieces) else 'FAIL'}  and is clear of the "
          f"interior pack alone{'':6s} got skip={list(wp.pieces)}")
    if not wp.clear(inside, skip=wp.pieces):
        fails.append("skip=pieces")
    print(f"  {'ok  ' if wp.pieces == ('wall',) and wp.parts == ('part',) else 'FAIL'}  "
          f"pieces and parts split the way the gate does  got {wp.pieces} / {wp.parts}")
    if wp.pieces != ("wall",) or wp.parts != ("part",):
        fails.append("piece/part split")
    held = World(dict(wp.solids), dict(wp.sources), pieces_held_out=True)
    del held.solids["wall"], held.sources["wall"]
    print(f"  {'ok  ' if 'NO printed' in held.measured else 'FAIL'}  a world without pieces "
          f"says so out loud{'':7s} got {held.measured!r}")
    if "NO printed" not in held.measured:
        fails.append("held-out world is loud")

    print("controls — the overlap a single boolean cannot see:")
    # The defect this instrument's whole promise rests on. Two swept tubes of one Ø crossing
    # at right angles ON ONE STRATUM, out where the pack stands: their surfaces are tangent
    # at the two poles of the crossing, and one exact `intersect` returns an empty solid for
    # the whole Steinmetz region. Boxes, rods and `corridor()` all resolve cleanly at the
    # same crossing, so only a fixture built through `_routing.tube` — the sweep the routed
    # tubes in `world()` are made of — puts the question. A world that answers CLEAR here
    # answers CLEAR for a pair `lines-clear` reds on.
    tx, ty, tz = 105.0, 417.0, 358.0
    t1 = _swept_tube((tx, ty - 60, tz - 60), (tx, ty - 60, tz), (tx, ty + 33, tz))
    t2 = _swept_tube((tx + 20, ty + 51, tz), (tx + 20, ty, tz), (tx - 60, ty, tz))
    tw2 = World({"tube-a": t1}, {"tube-a": "run"})
    tangent = tw2.hits(t2)
    print(f"  {'ok  ' if tangent else 'FAIL'}  a tube crossing tangent on one stratum is a "
          f"hit{'':6s} got {[h.name for h in tangent]}  want ['tube-a']")
    if [h.name for h in tangent] != ["tube-a"]:
        fails.append("tangent crossing")
    else:
        # A Steinmetz solid of two Ø6.35 cylinders is 16r³/3; the arcs either side of the
        # crossing carry a little more. Reported as a real volume, not a token one.
        steinmetz = 16.0 * (TUBE_OD / 2.0) ** 3 / 3.0
        print(f"  {'ok  ' if tangent[0].volume > steinmetz else 'FAIL'}  and carries the "
              f"whole overlap, not a sliver{'':4s} got {tangent[0].volume:.1f}  "
              f"want > {steinmetz:.1f} mm³")
        if tangent[0].volume <= steinmetz:
            fails.append("tangent crossing volume")
    # The control: the same pair with one lifted a tube's width and a clearance floor off
    # that stratum. The move that parts them must read clear.
    lift = TUBE_OD + 1.0
    t2_up = _swept_tube((tx + 20, ty + 51, tz + lift), (tx + 20, ty, tz + lift),
                        (tx - 60, ty, tz + lift))
    print(f"  {'ok  ' if tw2.clear(t2_up) else 'FAIL'}  the same pair one stratum apart is "
          f"clear{'':6s} got {[h.name for h in tw2.hits(t2_up)]}  want []")
    if not tw2.clear(t2_up):
        fails.append("tangent crossing control")

    print("controls — rerouting a piece of a run:")
    # A U lying in the XY plane whose crossbar is two waypoints, a post standing in the middle
    # of the band that crossbar sweeps through, and the run's OWN swept tube in the world
    # beside it. The last is the control that matters most: at offset 0 the redrawn run is
    # exactly the body already standing there, so a reroute that did not hold the run out would
    # report a total overlap with itself at every offset and never find anything else.
    u_pts = [(0.0, 0.0, 0.0), (0.0, 40.0, 0.0), (60.0, 40.0, 0.0), (60.0, 0.0, 0.0)]
    u_run = _routing.redrawn(
        _routing.Run("u", "fluid", "a.out", "b.in", list(u_pts), TUBE_OD, 14.0), u_pts)
    sw = World({"tube-u": _routing.tube(u_run), "post": box(x=(20, 30), y=(66, 74), z=(-5, 5))},
               {"tube-u": "run", "post": "test"}, runs={"u": u_run})
    moved = sw.reroute("u", (1, 2), "+y", steps(0.0, 60.0, 10.0))
    at = {p.at: p for p in moved.poses}
    print(f"  {'ok  ' if not at[0.0].hits else 'FAIL'}  the run's own tube is never its "
          f"obstacle{'':10s} got {list(at[0.0].hits)}  want []")
    if at[0.0].hits:
        fails.append("reroute holds the run out")
    print(f"  {'ok  ' if at[30.0].hits == ('post',) else 'FAIL'}  the crossbar driven onto the "
          f"post names it{'':4s} got {list(at[30.0].hits)}  want ['post']")
    if at[30.0].hits != ("post",):
        fails.append("reroute finds the obstacle")
    print(f"  {'ok  ' if not at[40.0].hits else 'FAIL'}  and past it is clear again"
          f"{'':21s} got {list(at[40.0].hits)}  want []")
    if at[40.0].hits:
        fails.append("reroute past the obstacle")
    edges = [(b.lo, b.hi, b.under, b.over) for b in moved.bands]
    want_edges = [(0.0, 20.0, None, "post"), (40.0, 60.0, "post", None)]
    print(f"  {'ok  ' if edges == want_edges else 'FAIL'}  two bands, each naming what ends it"
          f"{'':9s} got {edges}")
    if edges != want_edges:
        fails.append("reroute bands")
    # The reading a sweep of clearances would have missed: pulled back, the crossbar clears
    # every body in the world and its two corners are left seating 10 mm of the 14 the stock
    # wants — the same shape as two bends run into each other with no straight between them.
    short = sw.reroute("u", (1, 2), "-y", [30.0]).poses[0]
    ok_tight = not short.hits and short.tight and abs(short.seats - 10.0) < 1e-3
    print(f"  {'ok  ' if ok_tight else 'FAIL'}  a corner starved of tangent is not clear"
          f"{'':11s} got hits {list(short.hits)}, seats R{short.seats:.3f} vs "
          f"{short.floor:g}  want [] and R10 under spec")
    if not ok_tight:
        fails.append("reroute grades the corner")
    print(f"  {'ok  ' if not short.clear else 'FAIL'}  so the offset is not one the run can "
          f"take{'':7s} got clear={short.clear}  want False")
    if short.clear:
        fails.append("reroute clear folds both in")
    # A waypoint DROPPED rather than moved: the U's crossbar taken out entirely leaves one leg
    # straight down the far side of the post, which is a centreline `reroute` cannot express
    # and `drawn` takes whole.
    cut = sw.drawn("u", [u_run.pts[0], (60.0, 40.0, 0.0), u_run.pts[-1]])
    print(f"  {'ok  ' if not cut.hits and cut.corners == 1 else 'FAIL'}  a waypoint dropped "
          f"redraws the whole run{'':6s} got hits {list(cut.hits)}, {cut.corners} corner(s)  "
          f"want [] and 1")
    if cut.hits or cut.corners != 1:
        fails.append("drawn drops a waypoint")
    # And the redraw is a hypothetical: it must not put the authored run on the machine's own
    # list of shortfalls, which is keyed by run id and read out as `_lines.BLOCKED`.
    print(f"  {'ok  ' if 'u' not in _routing.BLOCKED else 'FAIL'}  a swept position never marks "
          f"the real run{'':6s} got BLOCKED={ {k: v for k, v in _routing.BLOCKED.items() if k == 'u'} }")
    if "u" in _routing.BLOCKED:
        fails.append("reroute leaks into BLOCKED")

    print("controls — refusals:")
    for label, thunk in (
        ("unnormalizable body raises", lambda: shape("not a solid", "x")),
        ("unknown body name raises", lambda: w.solid("nope")),
        ("zero-length direction raises", lambda: unit((0, 0, 0))),
        ("sampling a wall of a world with no pieces raises", lambda: wall_sample(held)),
        ("rerouting a run's port waypoint raises", lambda: sw.reroute("u", 0, "+y", [1.0])),
        ("a candidate centreline off its port raises",
         lambda: sw.drawn("u", [(0.0, 9.0, 0.0), (60.0, 40.0, 0.0), u_run.pts[-1]])),
        ("rerouting a waypoint the run has not got raises",
         lambda: sw.reroute("u", 9, "+y", [1.0])),
        ("rerouting an unknown run raises", lambda: sw.reroute("nope", 1, "+y", [1.0])),
        ("a world with no runs raises rather than answering", lambda: w.runs),
        ("a step of zero raises", lambda: steps(0.0, 10.0, 0.0)),
    ):
        try:
            thunk()
        except Exception:
            print(f"  ok    {label}")
        else:
            print(f"  FAIL  {label} — returned instead of raising")
            fails.append(label)

    print("\nreal world:")
    real = world()
    print(f"  ok    {len(real.solids)} bodies normalized "
          f"({sum(1 for s in real.sources.values() if s == 'run')} routed runs) — {real.measured}")
    got = len(real.tagged("display"))
    print(f"  {'ok  ' if got == 1 else 'FAIL'}  {'the display placed':44s} got {got}  want 1")
    if got != 1:
        fails.append("the display placed")
    if real.pieces:
        got = len(real.pieces)
        print(f"  {'ok  ' if got == 4 else 'FAIL'}  {'the printed pieces placed':44s} "
              f"got {got}  want 4")
        if got != 4:
            fails.append("the printed pieces placed")
        sample = wall_sample(real)
        buried = [h.name for h in real.hits(sample)]
        loose = [h.name for h in real.hits(sample, skip=real.pieces)]
        ok_real = buried and all(real.sources[n] == PIECE for n in buried) and not loose
        print(f"  {'ok  ' if ok_real else 'FAIL'}  a volume in a real printed wall is not "
              f"clear{'':4s} got in {buried}, interior {loose}")
        if not ok_real:
            fails.append("real piece occupancy")
    elif real.pieces_held_out:
        # The walls were switched off on purpose, so their controls have nothing to run
        # against. Not a pass: the instrument is sound and this world is not the one the
        # pack-closes gate agrees with, and both facts belong on the page.
        print(f"  --    the printed-piece controls did not run — {real.measured}")
    else:
        print("  FAIL  the printed pieces are missing from a world that asked for them")
        fails.append("pieces present")

    print(f"\n{'PASS' if not fails else 'FAIL: ' + ', '.join(fails)}")
    return 0 if not fails else 1


# --- CLI ------------------------------------------------------------------

def _pt(s: str) -> tuple:
    parts = s.split(",")
    if len(parts) != 3:
        raise SystemExit(f"expected x,y,z — got {s!r}")
    return tuple(float(p) for p in parts)


def _range(s: str) -> tuple:
    parts = s.split(",")
    if len(parts) != 2:
        raise SystemExit(f"expected lo,hi — got {s!r}")
    return (float(parts[0]), float(parts[1]))


def _axis(s: str) -> tuple:
    """`unit` on a shell argument, with its refusal reported as usage rather than a traceback."""
    try:
        return unit(s)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


def _moving_arg(s: str) -> tuple:
    """Which waypoints move: `3`, the inclusive span `3-4`, or the set `3,5,6`."""
    try:
        if "," in s:
            return tuple(int(p) for p in s.split(","))
        if "-" in s:
            lo, _, hi = s.partition("-")
            return tuple(range(int(lo), int(hi) + 1))
        return (int(s),)
    except ValueError:
        raise SystemExit(f"expected a waypoint index, the span 3-4, or the set 3,5 — "
                         f"got {s!r}") from None


def _values(s: str) -> list:
    """The offsets to sweep: `lo:hi:step`, or a comma list of them."""
    try:
        if ":" in s:
            lo, hi, step = (float(p) for p in s.split(":"))
            return steps(lo, hi, step)
        return [float(p) for p in s.split(",")]
    except ValueError as exc:
        raise SystemExit(f"expected offsets — lo:hi:step, or a comma list — got {s!r} "
                         f"({exc})") from None


def main(argv: list) -> int:
    import argparse
    import re

    ap = argparse.ArgumentParser(prog="probe", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("boxes", help="every body's bounding box")
    p.add_argument("--sort", default="name", help="name, ymin, zmax, …")

    p = sub.add_parser("gap", help="exact distance between two bodies")
    p.add_argument("a")
    p.add_argument("b")

    p = sub.add_parser("nearest", help="closest body to the named one")
    p.add_argument("name")

    p = sub.add_parser("at", help="a port's position and normal (component.port)")
    p.add_argument("port")

    p = sub.add_parser("cast", help="how far a tube runs before contact")
    p.add_argument("origin")
    p.add_argument("direction")
    p.add_argument("--dia", type=float, default=TUBE_OD)
    p.add_argument("--limit", type=float, default=CAST_LIMIT)
    p.add_argument("--skip", default="")

    p = sub.add_parser("travel", help="how far a body moves before each thing stops it")
    p.add_argument("mover")
    p.add_argument("direction", help="+x, -y, or x,y,z")
    p.add_argument("--limit", type=float, default=TRAVEL_LIMIT)
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")

    p = sub.add_parser("hits", help="what a box runs into")
    for axis in "xyz":
        p.add_argument(f"--{axis}", required=True, help="lo,hi")
    p.add_argument("--skip", default="")

    p = sub.add_parser("route", help="one run's waypoints, numbered — the index `reroute` moves")
    p.add_argument("run", nargs="?", help="a run id (fluid-14); omit to list every run")
    p.add_argument("--near", default="", metavar="x,y,z",
                   help="mark the waypoint closest to a pick off the STEP")

    p = sub.add_parser("reroute", help="sweep a piece of a run over a range of positions and "
                                     "report what it collides with at each one")
    p.add_argument("run", help="a run id (fluid-14), not its tube body")
    p.add_argument("moving", help="which waypoints move: 3, the span 3-4, or the set 3,5")
    p.add_argument("direction", help="y-, +z, or x,y,z — sign LAST (a leading -y reads as a flag)")
    p.add_argument("values", help="offsets in mm: lo:hi:step, or a comma list")
    p.add_argument("--skip", default="", help="other bodies to hold out, comma separated")

    sub.add_parser("selftest", help="known-answer controls, then load the world")

    # A cast runs `0,0,-1` and a reroute sweeps `-20:80:5`. Argparse reads a token starting with
    # `-` as a flag unless it matches this, which it excepts on the condition that the parser
    # carries no option looking like a negative number — none of these do. `-y` is not a
    # number and stays a flag, so `unit` takes the sign last, as `y-`.
    signed = re.compile(r"^-[\d.]")
    for parser in (ap, *sub.choices.values()):
        parser._negative_number_matcher = signed

    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()

    w = world()
    skip = tuple(s for s in getattr(a, "skip", "").split(",") if s)

    if a.cmd == "boxes":
        print(w.measured)
        print(w.table(sort=a.sort))
    elif a.cmd == "gap":
        print(f"{w.gap(a.a, a.b):.4f} mm")
    elif a.cmd == "nearest":
        g, n = w.nearest(a.name, skip=(a.name,))
        print(f"{g:.4f} mm to {n}")
    elif a.cmd == "at":
        comp, _, port = a.port.partition(".")
        if not port:
            print(f"{comp} ports: {', '.join(w.ports(comp))}")
        else:
            pos, nrm = w.at(comp, port), w.normal(comp, port)
            print(f"{a.port} at ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}) "
                  f"normal ({nrm[0]:g}, {nrm[1]:g}, {nrm[2]:g})")
    elif a.cmd == "travel":
        print(w.travel(a.mover, _axis(a.direction), limit=a.limit, clearance=a.clearance,
                       skip=skip))
    elif a.cmd == "route":
        if not a.run:
            for rid, r in sorted(w.runs.items()):
                print(f"  {rid:12s} {len(r.pts):2d} waypoints  {len(r.bends)} corner(s)  "
                      f"{r.frm} → {r.to}")
        else:
            print(w.route(a.run, near=_pt(a.near) if a.near else None))
    elif a.cmd == "reroute":
        print(w.reroute(a.run, _moving_arg(a.moving), _axis(a.direction), _values(a.values),
                      skip=skip))
    elif a.cmd in ("cast", "hits"):
        # A held-out body is part of the answer: "CLEAR" over a list of bodies nobody
        # measured is the same word as "CLEAR" over the whole machine.
        if skip:
            print(f"holding out: {', '.join(skip)}")
        if a.cmd == "cast":
            print(w.cast(_pt(a.origin), _pt(a.direction), dia=a.dia, limit=a.limit, skip=skip))
        else:
            found = w.hits(box(x=_range(a.x), y=_range(a.y), z=_range(a.z)), skip=skip)
            print("\n".join(str(h) for h in found) if found else "CLEAR")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
