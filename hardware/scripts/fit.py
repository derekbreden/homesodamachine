"""Candidate poses — carry a part to where it is not yet, and ask whether it fits.

`probe` answers questions about the world as it stands. This answers them about a body
that is not in it: a part carried to a pose, its ports carried by the same transform,
measured against the placed world.

    import fit

    p = fit.part("beduan-solenoid")             # module, builder and ports, discovered
    pose = p.pose(at=(x, y, z), yaw=90)
    print(fit.check(pose, skip=("vk-solenoid",)))
    print(pose.port("inlet"))                   # world position and axis

A FITTING GOES WHERE THE MOUTH IT JOINS IS, and that is a pose too — `mate` gives a port
the position and normal of the mouth it seats into and the body follows, so a chain hung
off the thing before it is placed by naming the joint rather than by solving for a corner:

    w = probe.world()
    elbow = fit.part("jg-pp061208w").mate(
        "tube_port", at=w.at("vk-solenoid", "outlet"),
        axis=tuple(-c for c in w.normal("vk-solenoid", "outlet")))
    print(elbow.port("stem_tip"))               # where the far end lands, for the next link

EVERY BODY IN THE MACHINE IS NAMEABLE HERE, printed ones included. `fit.part` takes a
`hardware/reference/` directory name, the path of a `.step`, or a `builder=` of its own —
whichever the caller states, in that order:

    fit.part("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.step")
    fit.part("pcba-assembly", builder=lambda: pcba_tray.build_assembly())

A LIST of candidates is an arrangement, and `check` takes one: every body against the
world, and every pair of them against each other, which is what "does this arrangement
fit" asks. Nothing in the world holds one candidate off another.

    print(fit.check([tray, psu, board], clearance=1.0))      # …  pairs  CLEAR nearest: …

The world is `probe.world()`, which holds the four printed enclosure pieces alongside the
interior pack — so a pose this reports CLEAR is a pose the enclosure's pack-closes gate
also calls clear, walls, seam lips, cross-pin pods and boss chains included. `skip=`
takes them out one query at a time (`skip=probe.world().pieces`) and both scans say when
they were held out.

The body and its ports move under one `cq.Location`, so a port cannot drift from the face
it names. A pose reports the transform it used; two poses of the same part with the same
arguments are the same solid.

Clearance is a threshold on an exact measured distance, never an inflation of the
obstacles: a pose free at 3 mm is a pose free at 0 mm, always. So is every distance a
verdict reports — a body far enough out to settle the verdict by its bounding box alone
is measured before its number is read off, because a box gap is a floor and a part that
is mostly air stands far behind its box. `search` ranks the free poses by how much room
they leave, on the same measured distances.

    fit.search(p, x=(xlo, xhi, step), y=(ylo, yhi, step), z=deck,
               yaw=(0, 90, 180, 270), clearance=2.0, skip=("vk-solenoid",))

    fit.slab(z=(deck, ceiling), size=(width, depth), exact=("seaflo-pump",))

`slab` maps what is free in a Z band rather than testing one part: the largest rectangles
a footprint could stand in, each with the floor it stands on — a rectangle with nothing
under it is a hole in the deck and not a place to put a part. Obstacles count by their
bounding box unless named in `exact`, which measures against the solid, and every body
reports the fill fraction that decides which it should be: a body 11% full blacks out
nine times its material by box, and hands back its own cavity as free space when measured
exactly. A printed piece is always exact and never boxed: its box is the whole machine.

Both scans state their own bounds before their answer, and what they measured them
against. A search reports the `Box` it ranged over — every range, every axis pinned to one
value, every body held out, the world the poses were measured in, and the width of free
window its own step falls over — and names the ends the best pose sits on. A slab reports
its field, where the field came from, which bodies were measured by box and which exactly,
which printed pieces reach into the band, how far below it looked for a floor, and whether
its largest rectangle runs to the edge of a field the caller supplied.

AN END OF A SCAN IS A FACT ABOUT THE GRID and not about the geometry, and so is a count of
free poses: a grid answers where it stands and nowhere else, and the record's free window
was 0.2 mm wide under a 2.5 mm step. So `search` does not stop at the grid — wherever two
adjacent points are blocked by two different bodies it splits the interval between them
and reports any pose standing there, off the grid. `probe.free(holds=…)` asks the same
question with no grid at all.

From the shell, without writing a file:

    tools/cad-venv/bin/python hardware/scripts/fit.py parts
    tools/cad-venv/bin/python hardware/scripts/fit.py try beduan-solenoid --at 222,322,274 --yaw 90
    tools/cad-venv/bin/python hardware/scripts/fit.py try \
        hardware/printed-parts/electronics/pcba-tray/pcba-assembly.step \
        --bbmin 2,202,258.4 --pitch 90 --clearance 6 --near 60
    tools/cad-venv/bin/python hardware/scripts/fit.py mate jg-pp061208w \
        --port tube_port --onto vk-solenoid.outlet --clearance 1
    tools/cad-venv/bin/python hardware/scripts/fit.py search meanwell-irm90 \
        --x 0,90,10 --y 200,340,10 --z 268 --yaw 0,90 --clearance 2
    tools/cad-venv/bin/python hardware/scripts/fit.py slab --z 267,331 --size 74,52
    tools/cad-venv/bin/python hardware/scripts/fit.py selftest

`selftest` checks the instrument against known-answer geometry — that a port lands on the
body it belongs to at arbitrary angles, that clearance only ever removes poses, that a
known fit fits and a known clash clashes, that a body whose bounding box reaches nearer
than its material is reported at its material, that a pose clear of every interior body
but standing in a printed piece comes back CLASH, that a free window narrower than the
grid is found between two of its points, that two candidates clear of the world but inside
each other are caught, that a hollow body reports its own fill, and that a rectangle over
a hole says it stands in air. Run it when an answer looks wrong before trusting the answer.
"""

import inspect
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq

import _overlap

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import probe                                                        # noqa: E402
from _seating import _carry_axis, _carry_point                      # noqa: E402  — one carry,
# shared with the seats the placed bodies read through

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_REF = _HW / "reference"

VOL_TOL = probe.VOL_TOL         # mm³ below which an intersection is contact, not overlap
TOUCH = 1e-7                    # mm below which an exact distance is contact, not a gap

# One default each, read by the API and by the shell's verb that calls it.
NEAR = 25.0                     # mm: how far out a body is still considered at all
LIMIT = 20000                   # poses a search tests before it asks whether the wait is wanted
RESOLVE = 0.1                   # mm: how fine a search splits the interval between two points
FLOOR = 40.0                    # mm: how far under a slab's band to look for a floor

# Names that are builders or entry points rather than ports.
_NOT_PORTS = ("build", "main", "export", "render", "show", "test")


# --- reference parts ------------------------------------------------------

def _solid(obj, label: str):
    """The bare solid behind whatever a builder returned. `cq.Assembly` flattens to its
    compound; everything else normalizes through `probe.shape`."""
    if isinstance(obj, cq.Assembly):
        return obj.toCompound()
    return probe.shape(obj, label)


def _dir_for(name: str) -> Path:
    d = _REF / name
    if not d.is_dir():
        have = sorted(p.name for p in _REF.iterdir() if p.is_dir())
        raise KeyError(f"no reference part {name!r} — have: {', '.join(have)}")
    return d


def _step_path(name: str):
    """`name` read as the path of a STEP file, or `None` when it is a part's name.

    Most of the machine's bodies are printed, and a printed part has no directory under
    `hardware/reference/` — it has a `.step` beside the script that generates it. That path
    is a name this takes."""
    p = Path(name)
    if p.suffix.lower() not in (".step", ".stp"):
        return None
    if not p.is_file():
        raise FileNotFoundError(f"{name}: no STEP file there")
    return p.resolve()


def _module_or_none(name: str):
    """The reference module of that name, or `None` when nothing under
    `hardware/reference/` is called that — which is the ordinary case for a part whose
    builder the caller is supplying."""
    try:
        return _module_for(name)
    except KeyError:
        return None


def _module_for(name: str):
    """Import a reference part's module by its directory name, or `None` when the part
    is carried as a STEP with no generator beside it."""
    d = _dir_for(name)
    stem = name.replace("-", "_")
    cands = [d / f"{stem}.py"]
    cands += sorted(p for p in d.glob("*.py") if not p.name.startswith("_"))
    src = next((p for p in cands if p.is_file()), None)
    if src is None:
        return None
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))
    probe._ensure_paths()
    import importlib
    return importlib.import_module(src.stem)


def _step_for(name: str):
    """The part's exported STEP, when it has one."""
    d = _dir_for(name)
    for cand in (d / f"{name}.step", d / f"{name.replace('-', '_')}.step"):
        if cand.is_file():
            return cand
    return next(iter(sorted(d.glob("*.step"))), None)


def _takes_no_args(fn) -> bool:
    """Callable with nothing passed — a parameter carrying a default does not count
    against it."""
    try:
        params = inspect.signature(fn).parameters.values()
    except (TypeError, ValueError):
        return False
    return all(p.default is not inspect.Parameter.empty
               or p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD) for p in params)


def _builder(mod, name: str):
    """The module's builder: `build()`, `build_<module>()` or `build_assembly()`, else
    raise naming what it does have — a guessed builder is a different part."""
    for attr in ("build", f"build_{mod.__name__}", "build_assembly"):
        fn = getattr(mod, attr, None)
        if callable(fn) and _takes_no_args(fn):
            return fn
    builds = sorted(n for n in dir(mod) if n.startswith("build") and callable(getattr(mod, n)))
    raise AttributeError(
        f"{name}: no zero-argument build(), build_{mod.__name__}() or build_assembly() — "
        f"has {', '.join(builds) if builds else 'no build* function'}; "
        f"pass builder= with the one that makes the whole part")


def _discover_ports(mod) -> dict:
    """Every zero-argument function returning `(point, axis)` — the reference parts'
    port convention. A function that raises is not a port."""
    out = {}
    for attr in sorted(dir(mod)):
        if attr.startswith("_") or attr.startswith(_NOT_PORTS):
            continue
        fn = getattr(mod, attr, None)
        if not callable(fn) or inspect.isclass(fn) or getattr(fn, "__module__", None) != mod.__name__:
            continue
        if not _takes_no_args(fn):
            continue
        try:
            val = fn()
        except Exception:
            continue
        if (isinstance(val, tuple) and len(val) == 2
                and all(isinstance(v, (tuple, list)) and len(v) == 3 for v in val)
                and all(isinstance(c, (int, float)) for v in val for c in v)):
            out[attr] = (tuple(float(c) for c in val[0]), tuple(float(c) for c in val[1]))
    return out


class Part:
    """A part in its own coordinates, with the ports it declares.

    What builds it is settled in the order the caller stated it: a `builder=` IS the part,
    then a `name` that is the path of a `.step`, and only then `hardware/reference/<name>/`.
    So every body in the machine is nameable here — the printed ones, which have a `.step`
    and a generator that is not a reference module, as much as the bought ones.

        fit.part("hardware/printed-parts/electronics/pcba-tray/pcba-assembly.step")
        fit.part("pcba-assembly", builder=lambda: pcba_tray.build_assembly())"""

    def __init__(self, name: str, builder=None):
        self.step = _step_path(str(name))
        self.name = self.step.stem if self.step is not None else str(name)
        self.module = None
        if builder is not None:
            self._builder = builder
            self.module = _module_or_none(self.name)
        elif self.step is not None:
            self._builder = lambda: cq.importers.importStep(str(self.step))
        else:
            self.module = _module_for(self.name)
            if self.module is not None:
                self._builder = _builder(self.module, self.name)
            else:
                self.step = _step_for(self.name)
                if self.step is None:
                    raise FileNotFoundError(
                        f"{self.name}: neither a module nor a .step in "
                        f"{_dir_for(self.name)} — nothing here builds this part; pass "
                        f"builder= or the path of a .step")
                self._builder = lambda: cq.importers.importStep(str(self.step))
        self._local = None
        self.local_ports = _discover_ports(self.module) if self.module else {}

    @property
    def solid(self):
        """The part at its own origin, built once."""
        if self._local is None:
            self._local = _solid(self._builder(), self.name)
        return self._local

    @property
    def ports(self) -> list:
        return sorted(self.local_ports)

    @property
    def bb(self):
        return self.solid.BoundingBox()

    def local_port(self, port: str):
        if port not in self.local_ports:
            raise KeyError(
                f"{self.name} has no port {port!r} — "
                f"has: {', '.join(self.ports) if self.ports else 'none declared'}")
        return self.local_ports[port]

    def pose(self, at=None, bbmin=None, yaw=0.0, pitch=0.0, roll=0.0):
        """This part carried to a pose.

        Rotations are about the part's own origin and compose roll (X), then pitch (Y),
        then yaw (Z). Exactly one of `at` — where the part's origin lands — or `bbmin`,
        where the rotated bounding box's low corner lands, which is how
        `enclosure_assembly.seat_body` seats a body in the pack."""
        if (at is None) == (bbmin is None):
            raise ValueError("pose needs exactly one of at= (the part's origin) "
                             "or bbmin= (its bounding-box low corner)")
        rot = _rotation(yaw, pitch, roll)
        if bbmin is not None:
            b = self.solid.moved(rot).BoundingBox()
            at = (bbmin[0] - b.xmin, bbmin[1] - b.ymin, bbmin[2] - b.zmin)
        loc = cq.Location(cq.Vector(*(float(c) for c in at))) * rot
        return Pose(self, loc, (yaw, pitch, roll))

    def mate(self, port: str, at, axis, spin: float = 0.0):
        """This part carried so that `port` sits at `at` and points along `axis`.

        The pose a fitting takes when it is put on the thing it connects to: give the port
        the position and normal of the mouth it joins and the rest of the body follows.
        `spin` turns the part about that axis, which the joint leaves free.

        A port's axis points out of the part, so two ports that join face opposite ways —
        mating onto `w.normal(component, port)` seats the two mouths back to back. Pass the
        negated normal to have this part's port point the same way as its neighbour's."""
        p, a = self.local_port(port)
        rot = _align(a, axis)
        if spin:
            rot = cq.Location(cq.Vector(0, 0, 0), cq.Vector(*probe.unit(axis)), float(spin)) * rot
        landed = _carry_point(rot, p)
        move = cq.Location(cq.Vector(*(float(at[i]) - landed[i] for i in range(3))))
        return Pose(self, move * rot)

    def __repr__(self) -> str:
        b = self.bb
        return (f"<Part {self.name} {b.xlen:.1f}×{b.ylen:.1f}×{b.zlen:.1f} "
                f"ports={','.join(self.ports) or 'none'}>")


def part(name: str, builder=None) -> Part:
    """A part by its `hardware/reference/` directory name, by the path of a `.step`, or
    under a `builder=` that names its own — see `Part`."""
    return Part(name, builder=builder)


def _align(a, b) -> cq.Location:
    """The rotation about the origin taking unit direction `a` onto `b`.

    Turns about their common perpendicular. When they are already opposed there is no such
    perpendicular, and any axis square to `a` reverses it — the half-turn is chosen rather
    than left to a cross product that has collapsed to zero."""
    u, v = probe.unit(a), probe.unit(b)
    dot = max(-1.0, min(1.0, sum(u[i] * v[i] for i in range(3))))
    if dot > 1.0 - 1e-12:
        return cq.Location()
    cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    if math.sqrt(sum(c * c for c in cross)) < 1e-9:
        seed = (1.0, 0.0, 0.0) if abs(u[0]) < 0.9 else (0.0, 1.0, 0.0)
        cross = (u[1] * seed[2] - u[2] * seed[1],
                 u[2] * seed[0] - u[0] * seed[2],
                 u[0] * seed[1] - u[1] * seed[0])
    return cq.Location(cq.Vector(0, 0, 0), cq.Vector(*probe.unit(cross)),
                       math.degrees(math.acos(dot)))


def _rotation(yaw: float, pitch: float, roll: float) -> cq.Location:
    """Roll about X, then pitch about Y, then yaw about Z, all through the origin."""
    loc = cq.Location()
    for angle, axis in ((roll, (1, 0, 0)), (pitch, (0, 1, 0)), (yaw, (0, 0, 1))):
        if angle:
            loc = cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), float(angle)) * loc
    return loc


# --- a posed part ---------------------------------------------------------

class Pose:
    """A part under one `cq.Location`. The body and every port read through the same
    transform, so a port is always on the face it names."""

    def __init__(self, part: Part, loc: cq.Location, angles=(0.0, 0.0, 0.0)):
        self.part = part
        self.loc = loc
        self.angles = angles
        self._solid = None

    @property
    def solid(self):
        if self._solid is None:
            self._solid = self.part.solid.moved(self.loc)
        return self._solid

    @property
    def bb(self):
        return self.solid.BoundingBox()

    def port(self, name: str) -> tuple:
        """`(position, axis)` in world coordinates."""
        p, a = self.part.local_port(name)
        return _carry_point(self.loc, p), _carry_axis(self.loc, a)

    def ports(self) -> dict:
        return {n: self.port(n) for n in self.part.ports}

    def moved(self, dx=0.0, dy=0.0, dz=0.0):
        """The same pose translated — for stepping a candidate without re-deriving it."""
        return Pose(self.part, cq.Location(cq.Vector(dx, dy, dz)) * self.loc, self.angles)

    @property
    def origin(self) -> tuple:
        return _carry_point(self.loc, (0.0, 0.0, 0.0))

    def __str__(self) -> str:
        b, o = self.bb, self.origin
        yaw, pitch, roll = self.angles
        spin = f" yaw {yaw:g}" if yaw else ""
        spin += f" pitch {pitch:g}" if pitch else ""
        spin += f" roll {roll:g}" if roll else ""
        return (f"{self.part.name} at ({o[0]:.1f}, {o[1]:.1f}, {o[2]:.1f}){spin}  "
                f"x[{b.xmin:.1f},{b.xmax:.1f}] y[{b.ymin:.1f},{b.ymax:.1f}] "
                f"z[{b.zmin:.1f},{b.zmax:.1f}]")


# --- fit ------------------------------------------------------------------

@dataclass(order=True)
class Gap:
    """How far a body stands, and whether that is the distance or a floor under it.

    A body already outside the threshold by its bounding box alone settles the verdict
    without an exact query, and carries its box gap — which is never more than the
    distance between the solids inside the boxes, and often far less. Until `Verdict`
    measures it, the number renders with the `≥` it has earned."""

    mm: float
    name: str
    exact: bool = True
    seated: bool = False        # measured touching with nothing shared — a seat, not a clash

    def __str__(self) -> str:
        return (f"{self.name} {'' if self.exact else '≥'}{self.mm:.2f}"
                + (" seated" if self.seated else ""))


@dataclass
class Verdict:
    """What a candidate ran into and how much room it left.

    Every distance that reaches a reader is measured against the solid: `nearest`, `room`
    and the rendered line resolve what they report. `gaps` is the working order, nearest
    first, and its tail may still hold the floor a bounding box put under a body — each
    entry says which it is."""

    clashes: list = field(default_factory=list)         # probe.Hit, worst first
    gaps: list = field(default_factory=list)            # Gap, nearest first
    clearance: float = 0.0
    measure: object = None                              # name -> exact distance to the body

    @property
    def clear(self) -> bool:
        """No overlap and nothing closer than `clearance`."""
        return not self.clashes and not self.tight

    @property
    def tight(self) -> list:
        """Bodies inside the clearance threshold without overlapping.

        Every one was measured: a floor is only ever taken for a body whose box already
        stood outside the threshold, so no floor can decide a verdict. A SEAT is not one of
        them — a body the candidate rests on stands at zero however much clearance is asked
        for, and it is what the pose is for."""
        return [g for g in self.gaps if g.mm < self.clearance and not g.seated]

    def resolve(self, depth: int = 1) -> list:
        """The `depth` nearest bodies, each measured against the solid.

        A floor can only stand a body earlier in the order than it belongs, never later,
        so the nearest are found by measuring the smallest floor and re-sorting until none
        stands among them. Measuring can only raise a value, so this ends, and a body it
        reaches can never turn out to be a clash. Without a `measure` the order is left as
        it is and the floors in it say so."""
        while self.measure is not None:
            head = self.gaps[:depth]
            loose = next((i for i, g in enumerate(head) if not g.exact), None)
            if loose is None:
                return head
            g = self.gaps[loose]
            self.gaps[loose] = Gap(self.measure(g.name), g.name)
            self.gaps.sort()
        return self.gaps[:depth]

    @property
    def nearest(self) -> Gap:
        """The closest body, measured."""
        if not self.gaps:
            raise ValueError("nearest: nothing was measured — every body was skipped")
        return self.resolve(1)[0]

    @property
    def room(self) -> float:
        """Distance to the closest body — the margin a free pose leaves. Infinite when
        nothing was near enough to measure."""
        if self.clashes:
            return 0.0
        return self.resolve(1)[0].mm if self.gaps else math.inf

    def __str__(self) -> str:
        if self.clashes:
            return "CLASH " + ", ".join(f"{h.name} {h.volume:.1f} mm³" for h in self.clashes[:4])
        if self.tight:
            return "TIGHT " + ", ".join(str(g) for g in self.tight[:4])
        near = ", ".join(str(g) for g in self.resolve(4)) or "nothing within reach"
        seats = [g.name for g in self.gaps if g.seated]
        return (f"CLEAR  nearest: {near}"
                + (f"   seated on {', '.join(seats)}" if seats else ""))


@dataclass
class Arrangement:
    """What a whole placement runs into — every candidate against the world, and every
    candidate against every other one.

    An arrangement is not its bodies checked one at a time. Nothing in the world holds a
    candidate off another candidate, so two of them can occupy the same millimetre while
    both come back CLEAR; `pairs` is that missing half, measured the same way `check`
    measures the world — exact, and a seat is a seat."""

    verdicts: dict = field(default_factory=dict)        # label -> Verdict against the world
    pairs: Verdict = None                               # candidate against candidate
    clearance: float = 0.0

    @property
    def clear(self) -> bool:
        return all(v.clear for v in self.verdicts.values()) and self.pairs.clear

    @property
    def tightest(self) -> Gap:
        """The nearest two candidates, measured. Infinite room is no pair within reach."""
        return self.pairs.nearest if self.pairs.gaps else Gap(math.inf, "no pair within reach")

    def __str__(self) -> str:
        bad = [n for n, v in self.verdicts.items() if not v.clear]
        head = (f"ARRANGEMENT  {len(self.verdicts)} bod"
                f"{'y' if len(self.verdicts) == 1 else 'ies'}, "
                + ("all clear of the world" if not bad
                   else f"{len(bad)} not clear of the world: {', '.join(bad[:4])}"))
        return "\n".join([head, f"  pairs  {self.pairs}"]
                         + [f"  {n:24s} {v}" for n, v in self.verdicts.items()])


def _labels(candidates) -> list:
    """One name per candidate, a repeated part taking a number so a pair can be read."""
    out, seen = [], {}
    for i, c in enumerate(candidates):
        base = c.part.name if isinstance(c, Pose) else f"candidate-{i + 1}"
        seen[base] = seen.get(base, 0) + 1
        out.append(base if seen[base] == 1 else f"{base}#{seen[base]}")
    return out


def _pack_entry(x) -> bool:
    """A `(solid, color)` entry out of the assembly's pack, which is a 2-tuple and not a
    list of candidates."""
    return isinstance(x, tuple) and len(x) == 2 and isinstance(x[1], str)


def arrangement(candidates, skip=(), clearance: float = 0.0, world=None,
                near: float = NEAR, labels=None) -> Arrangement:
    """Every candidate against the world, and every pair of them against each other.

    The pair distances are measured exactly and read the same way `check` reads the world:
    a pair held apart by their bounding boxes alone carries a floor, occupancy decides
    wherever two boxes meet, and two candidates measured touching with nothing shared are
    seated — one is the other's mount."""
    w = world or probe.world()
    cands = list(candidates)
    names = list(labels) if labels else _labels(cands)
    solids = [c.solid if isinstance(c, Pose) else probe.shape(c, "candidate") for c in cands]
    verdicts = {n: check(c, skip=skip, clearance=clearance, world=w, near=near)
                for n, c in zip(names, cands)}

    pw = probe.World(dict(zip(names, solids)), {n: "candidate" for n in names})
    ends, clashes, gaps = {}, [], []
    reach = max(float(near), float(clearance))
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            label = f"{names[i]} ↔ {names[j]}"
            ends[label] = (names[i], names[j])
            sep = _bb_gap(solids[i].BoundingBox(), solids[j].BoundingBox())
            if sep > reach:
                continue
            if sep > clearance and sep > TOUCH:
                gaps.append(Gap(sep, label, False))
                continue
            d = pw.gap(names[i], names[j])
            if d > TOUCH and sep > 0.0:
                gaps.append(Gap(d, label))
                continue
            try:
                inter, overlap = _overlap.common(solids[i], solids[j])
            except Exception as exc:
                raise RuntimeError(
                    f"intersection of {label} failed ({exc}) — this pair's occupancy is "
                    f"unknown, not empty") from exc
            if overlap > VOL_TOL:
                clashes.append(probe.Hit(label, overlap, probe._meshes.box(inter)))
            else:
                gaps.append(Gap(d, label, seated=d <= TOUCH))
    clashes.sort(key=lambda h: -h.volume)
    gaps.sort()
    pairs = Verdict(clashes, gaps, float(clearance), lambda lbl: pw.gap(*ends[lbl]))
    return Arrangement(verdicts, pairs, float(clearance))


def check(candidate, skip=(), clearance: float = 0.0, world=None, near: float = NEAR):
    """What `candidate` — a `Pose`, a shape, or a `(solid, color)` pack entry — runs into.

    A LIST of candidates is an arrangement, and comes back as one: every body against the
    world and every pair against each other, which is the question a placement actually
    asks. See `arrangement`.

    Overlaps are exact intersections, and so is every distance the `Verdict` reports: a
    body held off by its bounding box alone settles the verdict unmeasured and carries a
    floor under its distance, and `Verdict.resolve` measures whatever the ordering brings
    to the front before a number is read off it. `near` bounds which bodies are considered
    at all: a body whose bounding box is further than that cannot be the nearest and is not
    queried. Raise it when a pose sits alone in a large void."""
    if isinstance(candidate, (list, tuple)) and not _pack_entry(candidate):
        return arrangement(candidate, skip=skip, clearance=clearance, world=world, near=near)
    w = world or probe.world()
    sh = candidate.solid if isinstance(candidate, Pose) else probe.shape(candidate, "candidate")
    cb = sh.BoundingBox()
    reach = max(float(near), float(clearance))

    clashes, gaps = [], []
    for name in w.names:
        if name in skip:
            continue
        ob = w.bb(name)
        sep = _bb_gap(cb, ob)
        if sep > reach:                     # a box gap under-states the solid gap: safe to skip
            continue
        if sep > clearance and sep > TOUCH:
            gaps.append(Gap(sep, name, False))   # outside the threshold by its box alone
            continue
        d = w.gap(name, sh)
        # A DISTANCE IS BETWEEN SURFACES, and a candidate standing wholly inside a body has
        # a healthy one to every face of it — the wall it is buried in is the furthest thing
        # from it that its own box reaches. So a gap only settles a body whose box stands
        # clear too; where the boxes meet, occupancy is asked.
        if d > TOUCH and sep > 0.0:
            gaps.append(Gap(d, name))
            continue
        try:
            inter, overlap = _overlap.common(sh, w.solid(name))
        except Exception as exc:
            raise RuntimeError(
                f"intersection with {name} failed ({exc}) — this body's occupancy is "
                f"unknown, not empty") from exc
        if overlap > VOL_TOL:
            clashes.append(probe.Hit(name, overlap, probe._meshes.box(inter)))
        elif d > TOUCH:
            gaps.append(Gap(d, name))       # boxes met, solids did not
        else:
            # Measured touching and sharing nothing: the candidate RESTS on this body. A
            # part is designed to meet its mount, so counting the seat as a clearance
            # violation rejects the pose the design asks for — `probe.Travel` names the
            # same bodies `sliding` and never lets one stop a move.
            gaps.append(Gap(d, name, seated=True))
    clashes.sort(key=lambda h: -h.volume)
    gaps.sort()
    return Verdict(clashes, gaps, float(clearance), lambda n: w.gap(n, sh))


def _conflict(sh, w, skip=(), clearance: float = 0.0):
    """The first body `sh` overlaps or comes within `clearance` of, or `None`.

    The same test `check` makes, stopping at the first answer instead of measuring every
    neighbour — a rejected pose costs one exact query rather than twenty. Only bodies whose
    bounding box is already inside the threshold can be a conflict, and the nearest box is
    tried first — then the smallest, because a printed piece's box spans the whole machine
    and is 0 mm from every candidate while its material is almost always elsewhere. Order
    only decides which exact query is paid first; the verdict is the same either way."""
    cb = sh.BoundingBox()
    near = []
    for name in w.names:
        if name in skip:
            continue
        ob = w.bb(name)
        sep = _bb_gap(cb, ob)
        if sep > clearance:                 # a box gap under-states the solid gap
            continue
        near.append((sep, ob.xlen * ob.ylen * ob.zlen, name))
    for _sep, _vol, name in sorted(near):
        d = w.gap(name, sh)
        if d > TOUCH:
            if d < clearance:
                return name                 # near without touching: a real violation
            # Boxes that meet may be one body inside the other, whose surfaces never do —
            # see `check`. Only a box standing clear lets a distance settle the question.
            if _sep > 0.0:
                continue
        try:
            if _overlap.volume(sh, w.solid(name)) > VOL_TOL:
                return name
        except Exception as exc:
            raise RuntimeError(
                f"intersection with {name} failed ({exc}) — this body's occupancy is "
                f"unknown, not empty") from exc
        # Touching and sharing nothing: the candidate RESTS on this body, which is what a
        # mount is. `check` files the same body as a seated gap and does not call it tight.
    return None


def _bb_gap(a, b) -> float:
    """Separation between two axis-aligned boxes — 0 if they overlap. Never more than the
    distance between the solids inside them."""
    dx = max(0.0, a.xmin - b.xmax, b.xmin - a.xmax)
    dy = max(0.0, a.ymin - b.ymax, b.ymin - a.ymax)
    dz = max(0.0, a.zmin - b.zmax, b.zmin - a.zmax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# --- searching a pose grid ------------------------------------------------

AXES = ("x", "y", "z", "yaw", "pitch", "roll")
_SPIN = ("yaw", "pitch", "roll")


@dataclass
class Candidate:
    pose: Pose
    verdict: Verdict
    point: dict = field(default_factory=dict)       # the grid point that produced the pose
    between: tuple = None                           # (axis, lo, hi) when found off the grid

    @property
    def room(self) -> float:
        return self.verdict.room

    def __str__(self) -> str:
        off = (f"  between {self.between[0]}={self.between[1]:g} and {self.between[2]:g}, "
               f"off the grid" if self.between else "")
        return f"{self.pose}  {self.verdict}{off}"


@dataclass
class Box:
    """The grid a search ranged over, in the caller's own numbers — every range and every
    axis held to one value. An end of this box is a fact about the grid and not about the
    geometry, so a pose sitting on one is reported alongside the pose.

    A rotation whose values tile the circle at their own spacing has no end to sit on.

    `measured` is the other half of the same disclosure: a grid says where the scan looked,
    and that says what it looked at. A free pose in a world whose printed pieces were held
    out is free of the interior pack and nothing more.

    AND A COUNT IS NOT A PROOF. A grid answers where it stands and nowhere else, so its
    step is the width of free window it steps over — the record's window was 0.2 mm wide
    under a 2.5 mm step, and 33,900 poses reported zero. `blind` is that step and `spans`,
    `found` and `exhausted` say what was done about it: how many intervals between two
    blocked points were split down to `resolve`, how many free poses stood in one, and
    whether the splitting ran out of budget before the intervals ran out."""

    specs: dict                                     # label -> the spec as given
    values: dict                                    # label -> what it expanded to
    anchor: str = "at"
    skip: tuple = ()                                # bodies held out of the measurement
    measured: str = ""                              # the world it was measured in
    resolve: float = 0.0                            # how fine the intervals were split
    spans: int = 0                                  # intervals between two blocked points
    found: int = 0                                  # free poses that stood in one of them
    exhausted: bool = False                         # the splitting budget ran out first

    @property
    def swept(self) -> list:
        return [n for n in AXES if len(self.values.get(n, ())) > 1]

    @property
    def blind(self) -> float:
        """The coarsest step on a swept linear axis — the width of free window this grid
        steps over. Zero when nothing linear was swept, the grid then being the poses it
        lists and no others."""
        steps = []
        for name in self.swept:
            if name in _SPIN:
                continue
            v = sorted(self.values[name])
            steps.append(max(b - a for a, b in zip(v, v[1:])))
        return max(steps) if steps else 0.0

    @property
    def proof(self) -> str:
        """What this grid could not have seen, in one line."""
        blind = self.blind
        head = ("a count is not a proof — this grid tested the poses it lists and no others"
                if blind <= 0 else
                f"a count is not a proof — this grid steps {blind:g} mm and a free window "
                f"narrower than that falls between its points")
        if self.resolve <= 0:
            return head + "; the intervals between its points were not split (resolve=0)"
        if not self.spans:
            return head + "; no interval between two of its points had both ends blocked"
        tail = (f"; {self.spans} interval(s) between two blocked points, resolved to "
                f"{self.resolve:g} mm — {self.found} free pose(s) stood in one")
        return head + tail + (" — THE SPLITTING RAN OUT OF BUDGET" if self.exhausted else "")

    @property
    def fixed(self) -> list:
        return [n for n in AXES if len(self.values.get(n, ())) == 1]

    def wraps(self, label: str) -> bool:
        """Whether a rotation's values close the circle, leaving no end to widen."""
        v = sorted(self.values[label])
        if label not in _SPIN or len(v) < 2:
            return False
        gaps = [b - a for a, b in zip(v, v[1:])]
        return (max(gaps) - min(gaps) < 1e-9
                and (v[-1] - v[0]) + gaps[0] >= 360.0 - 1e-9)

    def edges(self, point: dict) -> list:
        """The swept axes `point` sits at the low or high end of."""
        out = []
        for name in self.swept:
            if self.wraps(name):
                continue
            v = self.values[name]
            if abs(point[name] - min(v)) < 1e-9:
                out.append(f"{name} low")
            elif abs(point[name] - max(v)) < 1e-9:
                out.append(f"{name} high")
        return out

    def _axis(self, label: str) -> str:
        spec, v = self.specs[label], self.values[label]
        if _is_triple(spec):
            return f"{label}[{spec[0]:g},{spec[1]:g}] step {spec[2]:g} ({len(v)})"
        if len(v) > 6:
            return f"{label}[{min(v):g},{max(v):g}] ({len(v)} given)"
        return f"{label}{{" + ",".join(f"{u:g}" for u in v) + "}"

    def __str__(self) -> str:
        swept = "  ".join(self._axis(n) for n in self.swept)
        held = " ".join(f"{n}={self.values[n][0]:g}" if isinstance(self.specs[n], (int, float))
                        else self._axis(n) for n in self.fixed)
        return ("box  " + (swept or "nothing swept")
                + (f"  fixed: {held}" if held else "")
                + (f"  anchor={self.anchor}" if self.anchor != "at" else "")
                + (f"  holding out: {', '.join(self.skip)}" if self.skip else "")
                + (f"\n  against  {self.measured}" if self.measured else "")
                + f"\n  {self.proof}")


class Candidates(list):
    """The free poses, best room first, carrying the `Box` they were found in."""

    def __init__(self, items=(), box: Box = None):
        super().__init__(items)
        self.box = box


def _is_triple(spec) -> bool:
    return (isinstance(spec, tuple) and len(spec) == 3
            and all(isinstance(v, (int, float)) for v in spec))


def _axis_values(spec, label: str) -> list:
    """A scalar, a `(lo, hi, step)` triple, or any iterable of values."""
    if spec is None:
        raise ValueError(f"search needs {label}=")
    if isinstance(spec, (int, float)):
        return [float(spec)]
    if _is_triple(spec):
        lo, hi, step = (float(v) for v in spec)
        if step <= 0:
            raise ValueError(f"{label}=({lo}, {hi}, {step}): step must be positive")
        n = int(math.floor((hi - lo) / step + 1e-9))
        return [lo + i * step for i in range(n + 1)]
    return [float(v) for v in spec]


def _split(fn, lo, blo, hi, bhi, resolve: float, out: list, budget: list) -> None:
    """Every free value hiding in `[lo, hi]`, both ends blocked, split until one turns up.

    A stretch one body holds at both ends and at the midpoint is that body's, and the half
    it holds is not split again — so an interval buried in a wall costs ONE query and only
    an interval where the binding body changes is followed down. That change is the whole
    signal: two obstacles blocking the two ends is what a free window between them looks
    like from a grid too coarse to stand in it."""
    if hi - lo <= resolve or budget[0] <= 0:
        return
    mid = 0.5 * (lo + hi)
    budget[0] -= 1
    pose, by = fn(mid)
    if by is None:
        out.append((mid, pose))
        return
    if by != blo:
        _split(fn, lo, blo, mid, by, resolve, out, budget)
    if by != bhi:
        _split(fn, mid, by, hi, bhi, resolve, out, budget)


def _between(state: dict, values: dict, axis: str, resolve: float, poser, budget: list) -> list:
    """Every free pose standing between two adjacent, both-blocked grid points on `axis`.

    A pair with a free end is skipped: that pose is already in hand and splitting the
    interval only sharpens the edge of a window the grid already found."""
    others = [a for a in AXES if a != axis]
    vals = sorted(values[axis])
    lines = sorted({tuple(dict(zip(AXES, k))[a] for a in others) for k in state})
    out = []
    for line in lines:
        base = dict(zip(others, line))
        for lo, hi in zip(vals, vals[1:]):
            blo = state[tuple({**base, axis: lo}[a] for a in AXES)]
            bhi = state[tuple({**base, axis: hi}[a] for a in AXES)]
            if blo is None or bhi is None:
                continue
            hits = []
            _split(lambda v: poser({**base, axis: v}), lo, blo, hi, bhi, resolve, hits, budget)
            out.append((lo, hi, [({**base, axis: v}, p) for v, p in hits]))
    return out


def search(part: Part, x, y, z, yaw=(0.0,), pitch=(0.0,), roll=(0.0,), anchor: str = "at",
           clearance: float = 0.0, skip=(), world=None, limit: int = LIMIT, top: int = 12,
           near: float = NEAR, resolve: float = RESOLVE, quiet: bool = False) -> Candidates:
    """Every free pose on a grid, best room first, carrying the grid it searched.

    Each axis takes a scalar, a `(lo, hi, step)` triple or a list — `pitch` and `roll` are
    axes like the rest, and a part on its side is a pose like any other. `anchor` is `"at"`
    (the part's origin lands on the grid point) or `"bbmin"` (its rotated box's low corner
    does). `skip` must name the body being re-placed — a part already in the world clashes
    with itself.

    Raising `clearance` can only remove poses: it is a threshold on a measured distance and
    the distances do not depend on it.

    A GRID ANSWERS WHERE IT STANDS AND NOWHERE ELSE, so the answer does not stop at the
    grid. Wherever two adjacent points are blocked by two different bodies, a free window
    may lie between them — the interval is split down to `resolve` mm and any pose found
    there comes back with the rest, marked as standing off the grid. `resolve=0` turns that
    off and the `Box` says so; `probe.free(holds=…)` answers the same question exactly and
    without a grid at all. `limit` bounds the whole scan, grid and splitting together — the
    splitting spends what the grid leaves, and the `Box` says when it ran out first.

    The report states the `Box` before the answer — the grid, the world the grid was
    measured in, and what the grid could not have seen — and names the ends the best pose
    sits on; a pose on an end is the grid reporting where it stopped."""
    if anchor not in ("at", "bbmin"):
        raise ValueError(f"anchor={anchor!r}: expected 'at' or 'bbmin'")
    w = world or probe.world()
    specs = dict(x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll)
    values = {n: _axis_values(specs[n], n) for n in AXES}
    box = Box(specs, values, anchor, tuple(skip), w.measured, float(resolve))
    grid = [dict(zip(AXES, (gx, gy, gz, ya, pi, ro)))
            for gx in values["x"]
            for gy in values["y"]
            for gz in values["z"]
            for ya in values["yaw"]
            for pi in values["pitch"]
            for ro in values["roll"]]
    if limit is not None and len(grid) > limit:
        raise ValueError(
            f"search would test {len(grid)} poses, over limit={limit} — coarsen a step "
            f"or narrow a range, or raise limit if the wait is wanted")

    def poser(point):
        """The pose at a point and the body blocking it, or `None` when it is free."""
        kw = {anchor: (point["x"], point["y"], point["z"])}
        p = part.pose(yaw=point["yaw"], pitch=point["pitch"], roll=point["roll"], **kw)
        return p, _conflict(p.solid, w, skip=skip, clearance=clearance)

    def keep(point, pose, between=None):
        return Candidate(pose, check(pose, skip=skip, clearance=clearance, world=w, near=near),
                         dict(point), between)

    out, state = [], {}
    for point in grid:
        p, by = poser(point)
        state[tuple(point[a] for a in AXES)] = by
        if by is None:
            out.append(keep(point, p))

    # The grid is where the scan looked; between its points is where it did not. Splitting
    # tests poses like everything else, so it spends what `limit` has left over.
    budget = [0 if resolve <= 0 else
              math.inf if limit is None else max(0, int(limit) - len(grid))]
    for axis in (a for a in box.swept if a not in _SPIN):
        for lo, hi, hits in _between(state, values, axis, resolve, poser, budget):
            box.spans += 1
            for point, pose in hits:
                box.found += 1
                out.append(keep(point, pose, (axis, lo, hi)))
    box.exhausted = resolve > 0 and budget[0] <= 0

    out.sort(key=lambda c: -c.room)
    found = Candidates(out, box)
    if not quiet:
        print(f"{len(out)} free of {len(grid)} poses at clearance {clearance:g} mm"
              + (f", best room {out[0].room:.2f} mm" if out else ""))
        print(f"  {box}")
        if not out:
            print("  nothing outside this box was tested")
        else:
            ends = box.edges(out[0].point)
            if ends:
                print(f"  best pose sits on {', '.join(ends)} — widen and re-run")
        for c in out[:top]:
            print(f"  {c}")
        if len(out) > top:
            print(f"  … {len(out) - top} more free pose(s) not shown")
    return found


# --- free space in a slab -------------------------------------------------

@dataclass
class Floor:
    """What a free rectangle stands on.

    A rectangle is a footprint, not a shelf: the space above a body's top and the space
    over a hole in the deck are the same free cells, and only one of them is somewhere to
    put a part. `fraction` is how much of the rectangle has material under it, `x` and `y`
    are how far that part of it reaches, and `on` names what holds it up with the top of
    each — so the drop from the band is `z[0] - top`."""

    fraction: float
    x: tuple
    y: tuple
    on: list                    # [(name, top z), …] highest first
    reach: float                # how far below the band this looked

    def __str__(self) -> str:
        if self.fraction <= 0:
            return f"floor  NOTHING within {self.reach:g} mm under it — it stands in air"
        who = ", ".join(f"{n} top z {t:.1f}" for n, t in self.on[:3])
        where = ("all of it" if self.fraction >= 1 - 1e-9 else
                 f"{self.fraction:.0%} of it — x[{self.x[0]:.1f},{self.x[1]:.1f}] "
                 f"y[{self.y[0]:.1f},{self.y[1]:.1f}], the rest stands in air")
        return f"floor  under {where}: {who}"


@dataclass
class Rect:
    """A free footprint in a Z band, and what stands under it."""

    x: tuple
    y: tuple
    z: tuple
    floor: Floor = None

    @property
    def w(self) -> float:
        return self.x[1] - self.x[0]

    @property
    def d(self) -> float:
        return self.y[1] - self.y[0]

    @property
    def area(self) -> float:
        return self.w * self.d

    def __str__(self) -> str:
        head = (f"{self.w:6.1f} × {self.d:6.1f} mm  ({self.area:8.0f} mm²)  "
                f"x[{self.x[0]:7.1f},{self.x[1]:7.1f}] y[{self.y[0]:7.1f},{self.y[1]:7.1f}] "
                f"z[{self.z[0]:.1f},{self.z[1]:.1f}]")
        return head + (f"\n{' ' * 8}{self.floor}" if self.floor is not None else "")


def slab(z: tuple, x: tuple = None, y: tuple = None, step: float = 4.0, skip=(),
         exact=(), size: tuple = None, world=None, top: int = 8, floor: float = FLOOR,
         quiet: bool = False) -> list:
    """The largest free rectangles in the Z band `z`, biggest area first.

    A cell is occupied when a body reaches into the band above it. Bodies count by their
    bounding box, which over-states them — every rectangle returned is genuinely free, and
    a part that is mostly air hides space behind its box. Name those in `exact` (or pass
    `exact=True`) to intersect the band against the solid instead.

    EVERY BODY REPORTS ITS FILL FRACTION, its material over its own box, because that one
    number is both failure directions of the choice: a body 11% full counted by box blacks
    out nine times the space it holds, and the same body counted exactly hands back every
    void inside it — a vessel's contents come back as room to put something.

    A printed enclosure piece is always exact and can never be boxed: its box is the whole
    machine, so counting one by box would black out the field and report a full cavity. Its
    material — the walls, and the seam lips, cross-pin pods, boss chains and ribs standing
    inboard of them — is measured cell by cell like any other exact body.

    `size=(w, d)` keeps only rectangles that hold that footprint in either orientation.
    `floor=` is how far below the band to look for something to stand on, and every
    rectangle reports what it found there; `floor=0` skips that scan.

    The report states the field, where the field came from, the world it measured against,
    and which bodies were taken by box against which were taken exactly — a field the
    caller supplied is a bound on the scan and not on the machine, so a rectangle reaching
    the edge of one is reported as reaching it."""
    w = world or probe.world()
    zlo, zhi = float(z[0]), float(z[1])
    if zhi <= zlo:
        raise ValueError(f"slab z=({zlo}, {zhi}): hi must exceed lo")

    live = [n for n in w.names if n not in skip and w.bb(n).zmax > zlo and w.bb(n).zmin < zhi]
    given = (x is not None, y is not None)
    source = "as given"
    if not all(given):
        bounds = _interior(w, skip)
        x = x if given[0] else bounds[0]
        y = y if given[1] else bounds[1]
        source = ("x as given, y from " if given[0] else
                  "y as given, x from " if given[1] else "from ") + bounds[2]
    x0, x1, y0, y1 = float(x[0]), float(x[1]), float(y[0]), float(y[1])
    nx, ny = max(1, int(round((x1 - x0) / step))), max(1, int(round((y1 - y0) / step)))
    sx, sy = (x1 - x0) / nx, (y1 - y0) / ny

    in_band = tuple(n for n in live if w.sources[n] == probe.PIECE)
    want_exact = set(live) if exact is True else {n for n in exact if n in live}
    want_exact |= set(in_band)
    grid = [[False] * ny for _ in range(nx)]

    # Boxes first, solids second. An exact body only has to answer for the cells the boxed
    # bodies left free, and in a machine this full that is most of the booleans gone. The
    # order changes nothing: a cell marked by a box is occupied whoever marks it.
    for name in (n for n in live if n not in want_exact):
        b = w.bb(name)
        i0, i1 = _span(b.xmin, b.xmax, x0, sx, nx)
        j0, j1 = _span(b.ymin, b.ymax, y0, sy, ny)
        for i in range(i0, i1):
            for j in range(j0, j1):
                grid[i][j] = True

    fill = {n: _fill(w.solid(n), w.bb(n)) for n in live if n not in want_exact}
    band = probe.box(x=(x0, x1), y=(y0, y1), z=(zlo, zhi))
    for name in sorted(want_exact):
        clipped, boxes = _in_band(w.solid(name), band, name)
        if clipped is None:                 # nothing of this body stands in the field's band
            continue
        cb = clipped.BoundingBox()
        fill[name] = _fill(clipped, cb)
        i0, i1 = _span(cb.xmin, cb.xmax, x0, sx, nx)
        j0, j1 = _span(cb.ymin, cb.ymax, y0, sy, ny)
        for i in range(i0, i1):
            cx0, cx1 = x0 + i * sx, x0 + (i + 1) * sx
            reach = [b for b in boxes if b.xmax > cx0 and b.xmin < cx1]
            if not reach:
                continue
            for j in range(j0, j1):
                if grid[i][j]:
                    continue
                cy0, cy1 = y0 + j * sy, y0 + (j + 1) * sy
                if not any(b.ymax > cy0 and b.ymin < cy1 for b in reach):
                    continue                # no material's box reaches this cell
                cell = probe.box(x=(cx0, cx1), y=(cy0, cy1), z=(zlo, zhi))
                try:
                    if _overlap.volume(cell, clipped) > VOL_TOL:
                        grid[i][j] = True
                except Exception as exc:
                    raise RuntimeError(
                        f"exact occupancy for {name} failed ({exc}) — this cell's state is "
                        f"unknown, not free") from exc

    rects = _maximal_rects(grid, x0, y0, sx, sy, (zlo, zhi))
    if size:
        wmin, dmin = float(size[0]), float(size[1])
        rects = [r for r in rects
                 if (r.w >= wmin and r.d >= dmin) or (r.w >= dmin and r.d >= wmin)]
    rects.sort(key=lambda r: -r.area)
    if floor > 0 and rects:
        under = _floors(w, zlo, float(floor), x0, y0, sx, sy, nx, ny, skip)
        for r in rects:
            r.floor = _floor_of(r, under, x0, y0, sx, sy, float(floor))
    if not quiet:
        print(f"free in z[{zlo:.1f},{zhi:.1f}] on a {sx:.1f}×{sy:.1f} mm grid — "
              f"{len(rects)} rectangle(s)"
              + (f" holding {size[0]:g}×{size[1]:g}" if size else ""))
        print(f"  field  x[{x0:.1f},{x1:.1f}] y[{y0:.1f},{y1:.1f}] {source}")
        print(f"  against  {w.measured}")
        named = sorted(n for n in want_exact if n not in in_band)
        print(f"  bodies  {len(live) - len(want_exact)} by bounding box"
              + (f", {len(named)} exact" if named else ", none exact")
              + (f"  holding out: {', '.join(skip)}" if skip else ""))
        if named:
            print(f"  exact   {_fills(fill, named)} — measured exactly, so every void inside "
                  f"one of them comes back as free space, its own cavity included")
        empty = sorted((n for n in live if n not in want_exact), key=lambda n: fill[n])[:3]
        if empty:
            print(f"  boxed   emptiest {_fills(fill, empty)} — a box counts a body's air as "
                  f"material; name one in exact= to measure it")
        held = [n for n in w.pieces if n in skip]
        print("  pieces  " + (
            f"{len(in_band)} reach this band, measured exactly — a piece's box is the whole "
            f"machine: {', '.join(in_band)}" if in_band else
            f"held out: {', '.join(held)}" if held else
            "none reach this band" if w.pieces else "none in this world"))
        print("  floor   " + (
            f"looked {floor:g} mm below the band; a piece by its material, every other body "
            f"by its box" if floor > 0 else "not looked for (floor=0)"))
        if rects:
            ends = _field_ends(rects[0], (x0, x1), (y0, y1), given)
            if ends:
                print(f"  largest reaches {', '.join(ends)} of the field you gave — "
                      f"widen and re-run")
        for r in rects[:top]:
            print(f"  {r}")
        if len(rects) > top:
            print(f"  … {len(rects) - top} more rectangle(s) not shown")
    return rects


def _in_band(solid, band, name: str):
    """`solid` clipped to the scan's own band, and one box per body the clip leaves.

    Every cell of the grid lies inside the band, so `cell ∩ solid` and `cell ∩ (solid ∩
    band)` enclose the same volume: the clip decides what a cell costs, never what it
    answers. It is what makes a printed piece affordable — the boolean runs against the
    material standing in this band rather than against the whole shell — and the boxes it
    hands back reject most cells before a boolean is built at all, since a cell no
    material's box reaches cannot hold material. `(None, [])` when nothing of the body
    stands in the band."""
    try:
        # WHETHER THIS BODY IS IN THE BAND AT ALL is a measurement and asks `_overlap`: an
        # exact boolean answers empty for two surfaces tangent where they meet, and a body
        # dropped here is a body every cell in the band then reads as free.
        if _overlap.volume(solid, band) <= VOL_TOL:
            return None, []
        # The CLIP itself is a construction — it decides what a cell COSTS and never what a
        # cell answers, since every cell is measured against `_overlap` either way. Exact,
        # for the solids and boxes it hands back; the whole body when the clip comes back
        # empty against a measurement that says it should not have.
        clipped = solid.intersect(band)
        if clipped.Volume() <= VOL_TOL:
            clipped = solid
    except Exception as exc:
        raise RuntimeError(
            f"clipping {name} to the scan band failed ({exc}) — its occupancy in the band "
            f"is unknown, not empty") from exc
    return clipped, [s.BoundingBox() for s in clipped.Solids()]


def _fill(solid, bb) -> float:
    """A body's material over its own bounding box. 1.0 is a brick; a swept tube on a
    diagonal runs under 0.01, and a vessel reads its walls and calls its contents air."""
    span = bb.xlen * bb.ylen * bb.zlen
    if span <= 0:
        return 1.0
    try:
        return max(0.0, min(1.0, solid.Volume() / span))
    except Exception:
        return 1.0


def _fills(fill: dict, names) -> str:
    return ", ".join(f"{n} {fill.get(n, 1.0):.1%} full" for n in names)


def _floors(w, zlo: float, reach: float, x0, y0, sx, sy, nx, ny, skip=()) -> list:
    """What stands under each cell of the field, within `reach` mm below the band.

    Every body marks by its bounding box, which OVER-states a floor — the direction that
    invents somewhere to stand — except a printed piece, whose box is the whole machine and
    would floor the field, and which is measured cell by cell like the band scan measures
    it. A cell keeps the highest material found under it."""
    lo = zlo - reach
    below = sorted(n for n in w.names
                   if n not in skip and w.bb(n).zmin < zlo - 1e-9 and w.bb(n).zmax > lo + 1e-9)
    cells = [[None] * ny for _ in range(nx)]
    band = probe.box(x=(x0, x0 + nx * sx), y=(y0, y0 + ny * sy), z=(lo, zlo))
    for name in below:
        piece = w.sources[name] == probe.PIECE
        clipped, boxes = ((None, [w.bb(name)]) if not piece
                          else _in_band(w.solid(name), band, name))
        if piece and clipped is None:
            continue
        for b in boxes:
            top = min(zlo, b.zmax)
            i0, i1 = _span(b.xmin, b.xmax, x0, sx, nx)
            j0, j1 = _span(b.ymin, b.ymax, y0, sy, ny)
            for i in range(i0, i1):
                cx0, cx1 = x0 + i * sx, x0 + (i + 1) * sx
                if not (b.xmax > cx0 and b.xmin < cx1):
                    continue
                for j in range(j0, j1):
                    if cells[i][j] is not None and cells[i][j][0] >= top:
                        continue
                    cy0, cy1 = y0 + j * sy, y0 + (j + 1) * sy
                    if not (b.ymax > cy0 and b.ymin < cy1):
                        continue
                    if piece:
                        cell = probe.box(x=(cx0, cx1), y=(cy0, cy1), z=(lo, zlo))
                        try:
                            if _overlap.volume(cell, clipped) <= VOL_TOL:
                                continue
                        except Exception as exc:
                            raise RuntimeError(
                                f"floor under {name} failed ({exc}) — what holds this cell "
                                f"up is unknown, not nothing") from exc
                    cells[i][j] = (top, name)
    return cells


def _floor_of(r: Rect, cells: list, x0, y0, sx, sy, reach: float) -> Floor:
    """The part of `r` with material under it, and what that material is."""
    i0, i1 = int(round((r.x[0] - x0) / sx)), int(round((r.x[1] - x0) / sx))
    j0, j1 = int(round((r.y[0] - y0) / sy)), int(round((r.y[1] - y0) / sy))
    on, xs, ys, held = {}, [], [], 0
    for i in range(i0, i1):
        for j in range(j0, j1):
            c = cells[i][j]
            if c is None:
                continue
            held += 1
            xs += [x0 + i * sx, x0 + (i + 1) * sx]
            ys += [y0 + j * sy, y0 + (j + 1) * sy]
            on[c[1]] = max(on.get(c[1], -math.inf), c[0])
    total = max(1, (i1 - i0) * (j1 - j0))
    return Floor(held / total,
                 (min(xs), max(xs)) if xs else r.x, (min(ys), max(ys)) if ys else r.y,
                 sorted(on.items(), key=lambda kv: -kv[1]), reach)


_CAVITY = None                          # the enclosure's own dimensions, read once


def _cavity() -> tuple:
    """The enclosure's inner extent, built once. `machine_of()` rebuilds the shell to
    measure it and costs seconds, while what it returns is a property of the source and not
    of the world being scanned — so a second slab reads it rather than paying for it
    again."""
    global _CAVITY
    if _CAVITY is None:
        probe._ensure_paths()
        import enclosure
        _CAVITY = tuple(enclosure.machine_of()[1].inner)
    return _CAVITY


def _interior(w, skip=()) -> tuple:
    """The enclosure's inner cavity as `((xlo, xhi), (ylo, yhi), source)` — the default field
    for a slab, so a scan reports room inside the machine rather than the air around it.
    `source` names where the field came from, which the slab reports with its answer."""
    try:
        inner = _cavity()
        return ((inner[0], inner[1]), (inner[2], inner[3]), "the enclosure cavity")
    except Exception:
        boxes = [w.bb(n) for n in w.names if n not in skip]
        if not boxes:
            raise ValueError("slab: no enclosure to bound the field and every body was "
                             "skipped — pass x= and y=")
        return ((min(b.xmin for b in boxes), max(b.xmax for b in boxes)),
                (min(b.ymin for b in boxes), max(b.ymax for b in boxes)),
                "the placed bodies' extent, the enclosure being unavailable")


def _field_ends(r: Rect, x: tuple, y: tuple, given: tuple) -> list:
    """The edges of a caller-supplied field that `r` reaches. An edge the caller did not
    supply is the cavity wall, which is the machine's and not the scan's."""
    return [e for e, reached in (
        ("x low", given[0] and r.x[0] <= x[0] + 1e-6),
        ("x high", given[0] and r.x[1] >= x[1] - 1e-6),
        ("y low", given[1] and r.y[0] <= y[0] + 1e-6),
        ("y high", given[1] and r.y[1] >= y[1] - 1e-6)) if reached]


def _span(lo, hi, origin, cell, n) -> tuple:
    """Half-open cell range a body covers, clipped to the grid."""
    i0 = max(0, int(math.floor((lo - origin) / cell + 1e-9)))
    i1 = min(n, int(math.ceil((hi - origin) / cell - 1e-9)))
    return i0, max(i0, i1)


def _maximal_rects(grid, x0, y0, sx, sy, z) -> list:
    """Every maximal free rectangle, by the histogram scan — for each row, the widest
    all-free span at each height. A rectangle that fits inside another is dropped, so
    what comes back is the free space itself and not every sub-rectangle of it."""
    nx, ny = len(grid), len(grid[0])
    heights = [0] * ny
    boxes = set()
    for i in range(nx):
        for j in range(ny):
            heights[j] = 0 if grid[i][j] else heights[j] + 1
        for j in range(ny):
            if heights[j] == 0:
                continue
            h = heights[j]
            lo = j
            while lo > 0 and heights[lo - 1] >= h:
                lo -= 1
            hi = j
            while hi + 1 < ny and heights[hi + 1] >= h:
                hi += 1
            boxes.add((i - h + 1, i + 1, lo, hi + 1))

    keep = [b for b in boxes
            if not any(o != b and o[0] <= b[0] and o[1] >= b[1] and o[2] <= b[2] and o[3] >= b[3]
                       for o in boxes)]
    return [Rect(x=(x0 + a * sx, x0 + b * sx), y=(y0 + c * sy, y0 + d * sy), z=z)
            for a, b, c, d in keep]


# --- instrument check -----------------------------------------------------

def selftest() -> int:
    """Known-answer controls: a port that must stay on its body under rotation, a
    clearance that must only ever remove poses, a known fit and a known clash."""
    fails = []

    def ok(label, passed, got="", want=""):
        tail = f"  want {want}" if want != "" else ""
        print(f"  {'ok  ' if passed else 'FAIL'}  {label:52s} {got}{tail}")
        if not passed:
            fails.append(label)

    def _line(box: Box) -> str:
        """A `Box` renders over two lines; a control row wants the grid on one."""
        return str(box).splitlines()[0]

    # A cube centred on its origin in X and Y, with a port on the centre of its +X face,
    # in a module of its own so port discovery sees it exactly as it sees a real part.
    import types
    side = 20.0
    fake = types.ModuleType("_fake")

    def _build():
        return cq.Workplane("XY").box(side, side, side, centered=(True, True, False)).val()

    def spout():
        return (side / 2, 0.0, side / 2), (1.0, 0.0, 0.0)

    def _imported_elsewhere():
        return (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)

    _imported_elsewhere.__module__ = "somewhere_else"
    for fn, name in ((_build, "build"), (spout, "spout"),
                     (_imported_elsewhere, "borrowed")):
        fn.__module__ = fn.__module__ if fn is _imported_elsewhere else "_fake"
        setattr(fake, name, fn)

    p = Part.__new__(Part)
    p.name, p.module, p._builder, p._local = "_fake", fake, fake.build, None
    p.local_ports = _discover_ports(fake)

    print("controls — discovery:")
    ok("a (point, axis) function is found as a port", p.ports == ["spout"], p.ports, "['spout']")
    ok("a function imported from elsewhere is not a port", "borrowed" not in p.local_ports)

    print("controls — the port rides the body:")
    for yaw, pitch, roll in ((0, 0, 0), (90, 0, 0), (37, 0, 0), (0, 45, 0), (0, 0, 30), (23, 41, 67)):
        pose = p.pose(at=(100, 200, 300), yaw=yaw, pitch=pitch, roll=roll)
        pos, axis = pose.port("spout")
        d = probe.World({"b": pose.solid}, {"b": "test"}).gap(
            "b", cq.Solid.makeSphere(0.05, cq.Vector(*pos), angleDegrees1=-90))
        ok(f"port on the body at yaw/pitch/roll {yaw}/{pitch}/{roll}", d <= 1e-6, f"gap {d:.9f}")
        ok(f"axis stays a unit vector at {yaw}/{pitch}/{roll}",
           abs(math.sqrt(sum(c * c for c in axis)) - 1.0) < 1e-9)

    print("controls — anchors:")
    b = p.pose(bbmin=(0, 0, 0), yaw=90).bb
    ok("bbmin= lands the rotated box's low corner",
       abs(b.xmin) < 1e-9 and abs(b.ymin) < 1e-9 and abs(b.zmin) < 1e-9,
       f"({b.xmin:.3f}, {b.ymin:.3f}, {b.zmin:.3f})", "(0, 0, 0)")
    o = p.pose(at=(5, 6, 7)).origin
    ok("at= lands the part's own origin", all(abs(o[i] - v) < 1e-9 for i, v in enumerate((5, 6, 7))),
       f"{tuple(round(v, 3) for v in o)}", "(5, 6, 7)")

    print("controls — what builds a part:")
    # `builder=` names its own part. Nothing under `hardware/reference/` is called this, and
    # nothing has to be: every printed body in the machine is in the same position.
    made = part("no-directory-of-this-name", builder=_build)
    ok("builder= reaches a part with no reference directory", abs(made.bb.xlen - side) < 1e-9,
       f"{made.bb.xlen:.3f}", f"{side:g}")
    ok("and keeps the name it was given", made.name == "no-directory-of-this-name", made.name)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "carried-part.step"
        cq.exporters.export(_build(), str(f))
        sp = part(str(f))
        ok("the path of a .step is a part name", abs(sp.bb.xlen - side) < 1e-6,
           f"{sp.bb.xlen:.3f}", f"{side:g}")
        ok("and the file's stem is what it is called", sp.name == "carried-part", sp.name)

    print("controls — mating a port onto a mouth:")
    targets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, -1), (0.3, -0.7, 0.65), (0, 0, 1))
    for axis in targets:
        want_at = (12.0, -34.0, 56.0)
        pose = p.mate("spout", at=want_at, axis=axis)
        got_at, got_axis = pose.port("spout")
        u = probe.unit(axis)
        ok(f"port lands where asked, axis {tuple(round(c, 2) for c in u)}",
           max(abs(got_at[i] - want_at[i]) for i in range(3)) < 1e-9,
           f"off by {max(abs(got_at[i] - want_at[i]) for i in range(3)):.2e}")
        ok(f"port points where asked, axis {tuple(round(c, 2) for c in u)}",
           max(abs(got_axis[i] - u[i]) for i in range(3)) < 1e-9,
           f"off by {max(abs(got_axis[i] - u[i]) for i in range(3)):.2e}")
    # Spin is free about the joint: the port holds while the body turns.
    a, b = p.mate("spout", at=(0, 0, 0), axis=(0, 1, 0)), p.mate("spout", at=(0, 0, 0),
                                                                 axis=(0, 1, 0), spin=90)
    pa, pb = a.port("spout"), b.port("spout")
    ok("spin holds the port and turns the body",
       max(abs(pa[0][i] - pb[0][i]) for i in range(3)) < 1e-9
       and max(abs(pa[1][i] - pb[1][i]) for i in range(3)) < 1e-9
       and abs(a.bb.xlen - b.bb.xlen) + abs(a.bb.zlen - b.bb.zlen) >= 0.0)

    print("controls — fit:")
    # A wall whose face stands one cube-width east of the origin.
    face = 2.5 * side
    wall = probe.box(x=(face, face + side / 2), y=(-5 * side, 5 * side), z=(0, 5 * side))
    w = probe.World({"wall": wall}, {"wall": "test"})
    v = check(p.pose(at=(0, 0, 0)), world=w, near=4 * side)
    ok("a known miss is clear", v.clear and not v.clashes)
    ok("its gap is exact", abs(v.nearest.mm - (face - side / 2)) < 1e-6,
       f"{v.nearest.mm:.6f}", f"{face - side / 2}")
    v = check(p.pose(at=(face + 1.0, 0, 0)), world=w)
    ok("a known overlap clashes", bool(v.clashes) and not v.clear,
       f"{[h.name for h in v.clashes]}", "['wall']")
    v = check(p.pose(at=(face - side / 2, 0, 0)), world=w)
    ok("touching is not overlapping", v.clear and not v.clashes, f"clashes {len(v.clashes)}")

    print("controls — an arrangement is not its bodies one at a time:")
    # Two candidates half a cube apart, so they share half their volume. Nothing in the
    # world is anywhere near either, and every one-at-a-time verdict is CLEAR.
    over = check([p.pose(at=(0, 0, 0)), p.pose(at=(side / 2, 0, 0))], world=w, near=4 * side)
    ok("both bodies are clear of the world", all(vv.clear for vv in over.verdicts.values()),
       f"{[str(vv)[:5] for vv in over.verdicts.values()]}")
    ok("and the arrangement is not", not over.clear and bool(over.pairs.clashes),
       f"{[h.name for h in over.pairs.clashes]}")
    ok("a repeated part is numbered so a pair can be read",
       list(over.verdicts) == ["_fake", "_fake#2"], f"{list(over.verdicts)}")
    apart = check([p.pose(at=(0, 0, 0)), p.pose(at=(1.5 * side, 0, 0))], world=w, near=4 * side)
    ok("a placement with room between its bodies is clear", apart.clear, str(apart).splitlines()[0])
    ok("the tightest pair is the measured gap between them",
       abs(apart.tightest.mm - side / 2) < 1e-6, f"{apart.tightest.mm:.6f}", f"{side / 2:g}")
    ok("a clearance the pair breaks is the arrangement's too",
       not check([p.pose(at=(0, 0, 0)), p.pose(at=(1.5 * side, 0, 0))],
                 world=w, clearance=side, near=4 * side).clear)
    # A DISTANCE IS BETWEEN SURFACES here too: one candidate wholly inside another has a
    # healthy one to every face of it, and only occupancy settles the pair.
    buried_pair = check([p.pose(at=(0, 0, 0)),
                         probe.box(x=(-2, 2), y=(-2, 2), z=(2, 6))], world=w, near=4 * side)
    ok("a candidate buried in another candidate is a clash, not a gap",
       bool(buried_pair.pairs.clashes) and not buried_pair.clear,
       f"{[h.name for h in buried_pair.pairs.clashes]}")
    # And a body resting on another is what a mount is — the same seat `check` allows.
    stacked = check([p.pose(at=(0, 0, 0)), p.pose(at=(0, 0, side))],
                    world=w, clearance=side, near=4 * side)
    ok("a candidate seated on another is not a violation", stacked.clear,
       f"{stacked.pairs}")

    print("controls — a reported distance is measured, not read off a box:")
    # `wall` is a box, so its box gap happens to be its distance and it could not catch a
    # box gap standing in for one. `bracket` can: an L whose bounding box reaches within
    # `side` of the cube while its material — the wing, out at the diagonal — stands
    # side·√2 away. `post` is a plain box at 1.25·side, nearer than the bracket's material
    # and further than the bracket's box, so a report taken off boxes gets the order wrong
    # as well as the number. `far` sits behind both, where no report reaches.
    wing = probe.box(x=(1.5 * side, 3.5 * side), y=(1.5 * side, 2.5 * side), z=(0, side))
    back = probe.box(x=(3.5 * side, 4.5 * side), y=(-2.5 * side, 2.5 * side), z=(0, side))
    wa = probe.World({"bracket": wing.fuse(back),
                      "post": probe.box(x=(1.75 * side, 2.25 * side),
                                        y=(-side / 2, side / 2), z=(0, side)),
                      "far": probe.box(x=(2.5 * side, 3 * side),
                                       y=(-side / 2, side / 2), z=(0, side))},
                     {"bracket": "test", "post": "test", "far": "test"})
    cube = p.pose(at=(0, 0, 0))
    ok("the bracket's box stands nearer than its material",
       abs(_bb_gap(cube.bb, wa.bb("bracket")) - side) < 1e-6,
       f"{_bb_gap(cube.bb, wa.bb('bracket')):.6f}", f"{side:g}")
    v = check(cube, world=wa, near=4 * side)
    ok("the nearest is the nearest body, not the nearest box",
       v.nearest.name == "post", v.nearest.name, "post")
    ok("its gap is exact", abs(v.nearest.mm - 1.25 * side) < 1e-6,
       f"{v.nearest.mm:.6f}", f"{1.25 * side:g}")
    # Measuring goes as deep as the report and no deeper, so the rest keeps its floor —
    # and says so rather than passing it off as a distance.
    ok("a body no report reaches keeps the floor its box gave it",
       [g.name for g in v.gaps if not g.exact] == ["far"],
       f"{[g.name for g in v.gaps if not g.exact]}", "['far']")
    ok("a floor renders as one", str(Gap(2.03, "far", False)) == "far ≥2.03",
       str(Gap(2.03, "far", False)))
    floors = {g.name: g.mm for g in v.gaps if not g.exact}
    line = str(v)
    ok("the reported line carries the measured distances",
       line == f"CLEAR  nearest: post {1.25 * side:.2f}, bracket {side * math.sqrt(2):.2f}, "
               f"far {2 * side:.2f}", line)
    ok("measuring a floor never lowered it",
       all(g.mm >= floors[g.name] - 1e-9 for g in v.gaps if g.name in floors))
    # And the ranking a search hands back rides on the same numbers.
    ok("room is the measured distance", abs(check(cube, world=wa, near=4 * side).room
                                            - 1.25 * side) < 1e-6)

    print("controls — a printed piece is a body the pose has to clear:")
    # The defect in miniature. `shell` is shaped like what it stands for: a box whose
    # bounding box is the whole field and whose material is only the rim, so a world that
    # took it by its box would call everything occupied and one that left it out would call
    # everything free. The candidate stands in the rim, 140 mm from the only interior body.
    rim = (probe.box(x=(-3 * side, 3 * side), y=(-3 * side, 3 * side), z=(0, 2 * side))
           .cut(probe.box(x=(-2 * side, 2 * side), y=(-2 * side, 2 * side),
                          z=(-1.0, 2 * side + 1.0))))
    walled = probe.World(
        {"far-part": probe.box(x=(10 * side, 11 * side), y=(0, side), z=(0, side)), "shell": rim},
        {"far-part": "component", "shell": probe.PIECE})
    buried = p.pose(at=(2.5 * side, 0, side / 4))
    v = check(buried, world=walled, near=4 * side)
    ok("a pose inside a printed piece is not clear", bool(v.clashes) and not v.clear,
       f"{[h.name for h in v.clashes]}", "['shell']")
    ok("holding the pieces out is what makes it read clear",
       check(buried, world=walled, skip=walled.pieces, near=4 * side).clear,
       f"skip={list(walled.pieces)}")
    ok("the fast reject calls it a conflict too", _conflict(buried.solid, walled) == "shell",
       f"{_conflict(buried.solid, walled)}", "shell")
    # And the same thing one level up: the pose the search would have offered is gone.
    lane = dict(x=(0.0, 2.5 * side, side / 2), y=0.0, z=side / 4)
    with_pieces = search(p, world=walled, quiet=True, **lane)
    without = search(p, world=walled, skip=walled.pieces, quiet=True, **lane)
    ok("a search offers no pose the pack-closes gate would fail",
       len(with_pieces) < len(without) and all(check(c.pose, world=walled, near=4 * side).clear
                                               for c in with_pieces),
       f"{len(with_pieces)} free of {len(without)} with the pieces held out")
    ok("the search says which world it ranged in",
       "printed enclosure piece" in str(with_pieces.box), str(with_pieces.box).splitlines()[-1])

    print("controls — the fast reject agrees with the full check:")
    disagreed = []
    for c in (0.0, 0.1 * side, 0.5 * side):
        for gx in [i * side / 5 for i in range(int(5 * face / side) + 1)]:
            pose = p.pose(at=(gx, 0, 0))
            fast = _conflict(pose.solid, w, clearance=c) is None
            full = check(pose, clearance=c, world=w, near=4 * side).clear
            if fast != full:
                disagreed.append((c, gx, fast, full))
    ok("every pose gets the same verdict either way", not disagreed,
       f"{len(disagreed)} disagreed" if disagreed else "")

    print("controls — clearance only removes:")
    grid = dict(x=(0.0, face - side / 2, side / 5), y=0.0, z=0.0)
    counts = [len(search(p, clearance=c, world=w, quiet=True, **grid))
              for c in (0.0, 0.1 * side, 0.25 * side, 0.5 * side)]
    ok("free poses never grow with clearance",
       all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1)), f"{counts}")
    ok("clearance 0 admits the touching pose", counts[0] > counts[-1], f"{counts}")

    print("controls — a search states the box it searched:")
    found = search(p, x=(0.0, face - side / 2, side / 5), y=0.0, z=0.0,
                   skip=("nothing-here",), world=w, quiet=True)
    b = found.box
    ok("every axis is in the box", sorted(b.values) == sorted(AXES),
       f"{sorted(b.values)}", f"{sorted(AXES)}")
    ok("the swept axis is named swept", b.swept == ["x"], f"{b.swept}", "['x']")
    ok("the pinned axes are named fixed", b.fixed == ["y", "z", "yaw", "pitch", "roll"],
       f"{b.fixed}")
    ok("the rendered box carries the range", "x[0,40] step 4" in str(b), _line(b))
    ok("the rendered box carries the held-out body", "nothing-here" in str(b), _line(b))
    ok("the rendered box carries the world it measured in",
       str(b).splitlines()[-2].strip().startswith("against"), str(b).splitlines()[-2].strip())
    ok("and ends saying a count is not a proof",
       str(b).splitlines()[-1].strip().startswith("a count is not a proof"),
       str(b).splitlines()[-1].strip())
    ok("the best pose is at the low end and says so", b.edges(found[0].point) == ["x low"],
       f"{b.edges(found[0].point)}", "['x low']")
    ok("a fixed axis is never an end", not any(e.startswith(("y ", "z ")) for e in
                                               b.edges(found[0].point)))
    blocked = search(p, x=face + 1.0, y=0.0, z=0.0, world=w, quiet=True)
    ok("a search that finds nothing still carries its box",
       blocked == [] and blocked.box is not None and "x=51" in str(blocked.box),
       _line(blocked.box))

    print("controls — an end is an end only where widening reaches:")
    for label, values, at, want in (
        ("a full circle of yaw has no end", [0.0, 90.0, 180.0, 270.0], 0.0, []),
        ("half a circle of yaw has ends", [0.0, 90.0], 90.0, ["yaw high"]),
        ("a linear axis always has ends", [0.0, 90.0], 0.0, ["x low"]),
        ("an uneven rotation keeps its ends", [0.0, 90.0, 200.0], 200.0, ["yaw high"]),
    ):
        name = "x" if label.startswith("a linear") else "yaw"
        got = Box({name: tuple(values)}, {name: values}).edges({name: at})
        ok(label, got == want, f"{got}", f"{want}")

    print("controls — a count is a fact about the grid:")
    # The recorded failure in miniature. Two walls leave the cube's origin a window
    # x ∈ [10.2, 10.6] — 0.4 mm wide, and every point of a 5 mm grid misses it. West holds
    # the low end of the straddling interval and east holds the high one, which is what a
    # free window looks like from a grid too coarse to stand in it.
    slot = probe.World({"west": probe.box(x=(-3 * side, 0.2), y=(-side, side), z=(0, side)),
                        "east": probe.box(x=(20.6, 3 * side), y=(-side, side), z=(0, side))},
                       {"west": "test", "east": "test"})
    lane = dict(x=(0.0, 30.0, 5.0), y=0.0, z=0.0)
    gridded = search(p, world=slot, resolve=0.0, quiet=True, **lane)
    ok("a grid coarser than the free window reports none", gridded == [],
       f"{len(gridded)} free", "0 free")
    ok("and discloses the width it steps over", abs(gridded.box.blind - 5.0) < 1e-9
       and "a count is not a proof" in gridded.box.proof, gridded.box.proof)
    keen = search(p, world=slot, resolve=0.05, quiet=True, **lane)
    ok("splitting the intervals between its points finds it", len(keen) > 0,
       f"{len(keen)} free", "at least 1")
    ok("the pose it found stands in the 0.4 mm window", bool(keen)
       and 10.2 - 1e-9 <= keen[0].point["x"] <= 10.6 + 1e-9,
       f"x={keen[0].point['x']:.4f}" if keen else "nothing", "x in [10.2, 10.6]")
    ok("and it is really free", bool(keen) and check(keen[0].pose, world=slot,
                                                     near=4 * side).clear)
    ok("a pose off the grid says which interval it stood in",
       bool(keen) and keen[0].between is not None and keen[0].between[0] == "x",
       f"{keen[0].between}" if keen else "nothing")
    ok("the box counts the intervals it split and what stood in them",
       keen.box.spans > 0 and keen.box.found > 0 and str(keen.box.spans) in keen.box.proof,
       f"{keen.box.spans} split, {keen.box.found} found")
    # A stretch one body holds all the way across costs one query and finds nothing —
    # otherwise every interval in a full machine would be followed to the resolution.
    solidly = probe.World({"west": probe.box(x=(-3 * side, 3 * side), y=(-side, side),
                                             z=(0, side))}, {"west": "test"})
    walled_run = search(p, world=solidly, resolve=0.05, quiet=True, **lane)
    ok("one body blocking both ends is not split down", walled_run == []
       and walled_run.box.found == 0, f"{walled_run.box.spans} split, "
       f"{walled_run.box.found} found")
    # Splitting tests poses like everything else, so it spends what the grid leaves of
    # `limit` — and a scan that stopped short of its own intervals says so out loud.
    starved = search(p, world=slot, resolve=0.05, limit=8, quiet=True, **lane)
    ok("the splitting spends what the grid leaves of limit",
       starved == [] and starved.box.exhausted and "RAN OUT" in starved.box.proof,
       starved.box.proof)

    print("controls — slab:")
    # One bar across the middle of a square field: two free strips, the north one wider.
    span, lo, hi = 5 * side, 2 * side, 3 * side
    bar = probe.box(x=(0, span), y=(lo, hi), z=(0, side / 2))
    ws = probe.World({"bar": bar}, {"bar": "test"})
    rects = slab(z=(0, side / 2), x=(0, span), y=(0, span), step=side / 4, world=ws, quiet=True)
    widest = max(rects, key=lambda r: r.area)
    ok("slab finds the larger free strip", abs(widest.area - span * (span - hi)) < 1e-6,
       f"{widest.area:.0f} mm²", f"{span * (span - hi):.0f} mm²")
    ok("slab excludes the occupied band",
       all(not (r.y[0] < hi and r.y[1] > lo) for r in rects), f"{len(rects)} rects")

    print("controls — a slab never counts a printed piece by its box:")
    # `rim`'s box is the whole field and its material is only the edge of it. Counted by
    # box it fills the machine; counted exactly it is what it is. A piece is always the
    # second, which is why nothing about it is left to the caller to remember.
    field, hole = (-3 * side, 3 * side), 2 * side
    wr = probe.World({"shell": rim}, {"shell": probe.PIECE})
    rects = slab(z=(0, 2 * side), x=field, y=field, step=side / 2, world=wr, quiet=True)
    inside = max(rects, key=lambda r: r.area) if rects else None
    ok("the space inside a piece is free", inside is not None
       and abs(inside.area - (2 * hole) ** 2) < 1e-6,
       f"{inside.area:.0f} mm²" if inside else "no rectangle", f"{(2 * hole) ** 2:.0f} mm²")
    # The same body under any other tag still counts by its box — the rule is about pieces,
    # not about this shape.
    wb = probe.World({"shell": rim}, {"shell": "component"})
    ok("the same body under another tag still counts by its box",
       slab(z=(0, 2 * side), x=field, y=field, step=side / 2, world=wb, quiet=True) == [],
       "no free rectangle")
    # The band clip is what makes a piece affordable, so it has to be free of consequence:
    # every cell must land the same way against the clipped body as against the whole one.
    band = probe.box(x=field, y=field, z=(0, 2 * side))
    clipped, boxes = _in_band(rim, band, "shell")
    ok("the clip leaves one box per body it leaves", len(boxes) == len(clipped.Solids()),
       f"{len(boxes)} for {len(clipped.Solids())}")
    disagreed = []
    for gx in [field[0] + k * side for k in range(6)]:
        for gy in [field[0] + k * side for k in range(6)]:
            cell = probe.box(x=(gx, gx + side), y=(gy, gy + side), z=(0, 2 * side))
            if (_overlap.volume(cell, clipped) > VOL_TOL) != (
                    _overlap.volume(cell, rim) > VOL_TOL):
                disagreed.append((gx, gy))
    ok("a clipped body answers every cell the way the whole one does", not disagreed,
       f"{len(disagreed)} disagreed" if disagreed else "36 cells")

    print("controls — a body says how much of its own box it is:")
    # The number that decides `exact=`, and both directions of it: `rim` counted by box
    # blacks out nearly twice the space it holds, and counted exactly hands its own
    # interior back as room — 6400 mm² of it, which the control above just measured.
    brick = probe.box(x=(0, side), y=(0, side), z=(0, side))
    ok("a brick is full", abs(_fill(brick, brick.BoundingBox()) - 1.0) < 1e-9,
       f"{_fill(brick, brick.BoundingBox()):.1%}", "100.0%")
    rbb = rim.BoundingBox()
    want = rim.Volume() / (rbb.xlen * rbb.ylen * rbb.zlen)
    ok("a vessel reports its walls and not its contents",
       abs(_fill(rim, rbb) - want) < 1e-12 and want < 0.6, f"{_fill(rim, rbb):.1%}",
       f"{want:.1%}")
    flat = types.SimpleNamespace(xlen=0.0, ylen=0.0, zlen=0.0)
    ok("a body with no box to speak of is not divided by zero", _fill(brick, flat) == 1.0)

    print("controls — a rectangle stands on something or it stands in air:")
    # A deck under the near half of the field and nothing at all under the far half. The
    # whole field is free in the band either way; only half of it is somewhere to stand.
    wf = probe.World({"deck": probe.box(x=(0, span), y=(0, 2.5 * side), z=(-side, 0))},
                     {"deck": "test"})
    stood = slab(z=(0, side), x=(0, span), y=(0, span), step=side / 4, world=wf,
                 floor=side, quiet=True)
    r = max(stood, key=lambda t: t.area)
    ok("the rectangle is the whole field", abs(r.area - span * span) < 1e-6,
       f"{r.area:.0f} mm²", f"{span * span:.0f} mm²")
    ok("and reports what holds it up",
       r.floor is not None and [n for n, _t in r.floor.on] == ["deck"],
       f"{[n for n, _t in r.floor.on] if r.floor else None}", "['deck']")
    ok("over the half that has a floor", abs(r.floor.fraction - 0.5) < 1e-9,
       f"{r.floor.fraction:.0%}", "50%")
    ok("naming how far that half reaches", abs(r.floor.y[1] - 2.5 * side) < 1e-9,
       f"y[{r.floor.y[0]:.1f},{r.floor.y[1]:.1f}]", f"y[0.0,{2.5 * side:.1f}]")
    ok("and where its top surface is", abs(r.floor.on[0][1] - 0.0) < 1e-9,
       f"{r.floor.on[0][1]:.2f}", "0.00")
    hollow = slab(z=(0, side), x=(0, span), y=(0, span), step=side / 4, world=wf,
                  skip=("deck",), floor=side, quiet=True)
    ok("a rectangle with nothing under it says it stands in air",
       hollow[0].floor.fraction == 0.0 and "air" in str(hollow[0].floor), str(hollow[0].floor))
    low = probe.World({"deck": probe.box(x=(0, span), y=(0, 2.5 * side),
                                         z=(-3 * side, -2 * side))}, {"deck": "test"})
    deep = max(slab(z=(0, side), x=(0, span), y=(0, span), step=side / 4, world=low,
                    floor=side, quiet=True), key=lambda t: t.area)
    ok("a floor further down than the scan looked is not a floor", deep.floor.fraction == 0.0,
       f"{deep.floor.fraction:.0%}", "0%")
    deeper = max(slab(z=(0, side), x=(0, span), y=(0, span), step=side / 4, world=low,
                      floor=3 * side, quiet=True), key=lambda t: t.area)
    ok("and looking far enough down finds it", abs(deeper.floor.fraction - 0.5) < 1e-9
       and abs(deeper.floor.on[0][1] + 2 * side) < 1e-9,
       f"{deeper.floor.fraction:.0%} top z {deeper.floor.on[0][1]:.1f}", f"50% top z {-2 * side:.1f}")
    ok("floor=0 leaves the question unasked",
       slab(z=(0, side), x=(0, span), y=(0, span), step=side / 4, world=wf,
            floor=0, quiet=True)[0].floor is None)

    print("controls — a slab states the field it scanned:")
    ends = _field_ends(widest, (0, span), (0, span), (True, True))
    ok("a rectangle on a given field's edge says so", ends == ["x low", "x high", "y high"],
       f"{ends}", "['x low', 'x high', 'y high']")
    ok("an edge of a field nobody supplied is the machine's",
       _field_ends(widest, (0, span), (0, span), (False, False)) == [])
    ok("the derived field names where it came from",
       isinstance(_interior(ws)[2], str) and _interior(ws)[2] != "", _interior(ws)[2])

    print("controls — the shell reaches what the API does:")
    verbs = _parser()._subparsers._group_actions[0].choices
    import re
    shown = set(re.findall(r"fit\.py (\w+)", __doc__ or ""))
    ok("every verb the docstring shows is a verb", shown <= set(verbs),
       f"{sorted(shown - set(verbs))}", "nothing left over")
    ok("every verb is in the docstring", set(verbs) <= shown,
       f"{sorted(set(verbs) - shown)}", "nothing unnamed")
    for verb in ("try", "mate", "search"):
        opts = {s for act in verbs[verb]._actions for s in act.option_strings}
        ok(f"{verb} reaches --near", "--near" in opts, f"{sorted(opts)}")
    ok("the shell's pose limit is the API's",
       verbs["search"].get_default("limit")
       == inspect.signature(search).parameters["limit"].default,
       f"shell {verbs['search'].get_default('limit')}, "
       f"API {inspect.signature(search).parameters['limit'].default}")
    ok("and so is how fine it splits between them",
       verbs["search"].get_default("resolve")
       == inspect.signature(search).parameters["resolve"].default,
       f"shell {verbs['search'].get_default('resolve')}, "
       f"API {inspect.signature(search).parameters['resolve'].default}")
    ok("and how far below a slab looks for a floor",
       verbs["slab"].get_default("floor")
       == inspect.signature(slab).parameters["floor"].default,
       f"shell {verbs['slab'].get_default('floor')}, "
       f"API {inspect.signature(slab).parameters['floor'].default}")

    print("controls — refusals:")
    for label, thunk in (
        ("unknown part name raises", lambda: part("no-such-part")),
        ("a .step path that is not there raises", lambda: part("nowhere/nothing.step")),
        ("unknown port name raises", lambda: p.pose(at=(0, 0, 0)).port("nope")),
        ("giving both at= and bbmin= raises", lambda: p.pose(at=(0, 0, 0), bbmin=(0, 0, 0))),
        ("giving neither at= nor bbmin= raises", lambda: p.pose()),
        ("a bad anchor raises",
         lambda: search(p, x=0, y=0, z=0, anchor="middle", world=w, quiet=True)),
        ("an oversized grid raises",
         lambda: search(p, x=(0, 100, 1), y=(0, 100, 1), z=0, limit=100, world=w, quiet=True)),
        ("a zero step raises", lambda: _axis_values((0.0, 10.0, 0.0), "x")),
        ("an inverted slab band raises", lambda: slab(z=(10, 0), world=w, quiet=True)),
    ):
        try:
            thunk()
        except Exception:
            print(f"  ok    {label}")
        else:
            print(f"  FAIL  {label} — returned instead of raising")
            fails.append(label)

    print("\nreal world:")
    real = probe.world()
    print(f"  ok    {real.measured}")
    if real.pieces:
        # The synthetic control above proves the rule; this one proves the wiring. A volume
        # cut out of a real printed wall must come back CLASH, and must come back clear the
        # moment the walls are the thing held out.
        ok("the printed pieces are in the world it measures against", len(real.pieces) == 4,
           f"{len(real.pieces)}", "4")
        sample = probe.wall_sample(real)
        v = check(sample, world=real)
        ok("a volume inside a real printed wall clashes",
           bool(v.clashes) and all(real.sources[h.name] == probe.PIECE for h in v.clashes),
           f"{[h.name for h in v.clashes]}")
        ok("and clears every interior body once they are held out",
           check(sample, world=real, skip=real.pieces).clear)
    elif real.pieces_held_out:
        # Switched off on purpose: the walls have nothing to answer for here. Said out
        # loud, because a green run against a world with no walls is not the same claim.
        print(f"  --    the printed-piece controls did not run — {real.measured}")
    else:
        ok("the printed pieces are in the world it measures against", False, "0", "4")

    print("\nreal parts:")
    named = sorted(d.name for d in _REF.iterdir() if d.is_dir())
    built, ported, broken = 0, 0, []
    for name in named:
        try:
            rp = part(name)
            rp.solid.BoundingBox()
            built += 1
            ported += 1 if rp.ports else 0
        except Exception as exc:
            broken.append(f"{name} ({type(exc).__name__})")
    print(f"  ok    {built}/{len(named)} reference parts build, {ported} declare ports")
    if broken:
        print("  --    needs an explicit builder=: " + ", ".join(broken))

    print(f"\n{'PASS' if not fails else 'FAIL: ' + ', '.join(fails)}")
    return 0 if not fails else 1


# --- CLI ------------------------------------------------------------------

def _triple(s: str):
    parts = [float(v) for v in s.split(",")]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 3:
        return (parts[0], parts[1], parts[2])
    raise SystemExit(f"expected a value or lo,hi,step — got {s!r}")


def _list(s: str) -> list:
    return [float(v) for v in s.split(",") if v != ""]


def _parser():
    """The shell's verbs and their defaults, built where the selftest can read them —
    every default here is the API's own, and every verb is one the docstring names."""
    import argparse

    ap = argparse.ArgumentParser(prog="fit", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("parts", help="every reference part, its size and its ports")

    p = sub.add_parser("try", help="one pose against the placed world")
    p.add_argument("part", help="a reference part's name, or the path of a .step")
    p.add_argument("--at", help="x,y,z the part's origin lands on")
    p.add_argument("--bbmin", help="x,y,z its bounding box's low corner lands on")
    for a in ("yaw", "pitch", "roll"):
        p.add_argument(f"--{a}", type=float, default=0.0)
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")
    p.add_argument("--near", type=float, default=NEAR,
                   help="how far out a body is still considered — raise it in a large void")

    p = sub.add_parser("mate", help="seat a part's port into a placed component's mouth")
    p.add_argument("part", help="a reference part's name, or the path of a .step")
    p.add_argument("--port", required=True, help="the part's own port to seat")
    p.add_argument("--onto", required=True, help="component.port to seat it into")
    p.add_argument("--spin", type=float, default=0.0, help="turn about the joint axis")
    p.add_argument("--along", action="store_true",
                   help="point the port the same way as the mouth's normal rather than into it")
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")
    p.add_argument("--near", type=float, default=NEAR,
                   help="how far out a body is still considered — raise it in a large void")

    p = sub.add_parser("search", help="every free pose on a grid, best room first")
    p.add_argument("part", help="a reference part's name, or the path of a .step")
    for a in ("x", "y", "z"):
        p.add_argument(f"--{a}", required=True, help="value or lo,hi,step")
    for a in ("yaw", "pitch", "roll"):
        p.add_argument(f"--{a}", default="0", help="comma-separated angles")
    p.add_argument("--anchor", default="at", choices=("at", "bbmin"))
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")
    p.add_argument("--limit", type=int, default=LIMIT,
                   help="poses the whole scan may test, grid and splitting together")
    p.add_argument("--top", type=int, default=12, help="how many poses to print")
    p.add_argument("--near", type=float, default=NEAR,
                   help="how far out a body is still considered — raise it in a large void")
    p.add_argument("--resolve", type=float, default=RESOLVE,
                   help="how fine to split the intervals between grid points; 0 leaves them")

    p = sub.add_parser("slab", help="the largest free rectangles in a Z band")
    p.add_argument("--z", required=True, help="lo,hi")
    p.add_argument("--x", help="lo,hi")
    p.add_argument("--y", help="lo,hi")
    p.add_argument("--step", type=float, default=4.0)
    p.add_argument("--size", help="w,d a footprint to hold")
    p.add_argument("--skip", default="")
    p.add_argument("--exact", default="", help="bodies to measure as solids, or 'all'")
    p.add_argument("--top", type=int, default=8, help="how many rectangles to print")
    p.add_argument("--floor", type=float, default=FLOOR,
                   help="how far below the band to look for something to stand on; 0 skips")

    sub.add_parser("selftest", help="known-answer controls, then load every reference part")
    return ap


def main(argv: list) -> int:
    a = _parser().parse_args(argv)
    if a.cmd == "selftest":
        return selftest()

    skip = tuple(s for s in getattr(a, "skip", "").split(",") if s)

    if a.cmd == "parts":
        for name in sorted(d.name for d in _REF.iterdir() if d.is_dir()):
            try:
                rp = part(name)
                b = rp.bb
                print(f"{name:28s} {b.xlen:7.1f} × {b.ylen:7.1f} × {b.zlen:7.1f}   "
                      f"{', '.join(rp.ports) or '—'}")
            except Exception as exc:
                print(f"{name:28s} {type(exc).__name__}: {str(exc).splitlines()[0][:60]}")
        return 0

    if a.cmd == "try":
        rp = part(a.part)
        if (a.at is None) == (a.bbmin is None):
            raise SystemExit("try needs exactly one of --at or --bbmin")
        where = {"at": _list(a.at)} if a.at else {"bbmin": _list(a.bbmin)}
        pose = rp.pose(yaw=a.yaw, pitch=a.pitch, roll=a.roll, **where)
        print(pose)
        print("  " + str(check(pose, skip=skip, clearance=a.clearance, near=a.near)))
        for n in rp.ports:
            pos, ax = pose.port(n)
            print(f"  {n:16s} ({pos[0]:8.2f}, {pos[1]:8.2f}, {pos[2]:8.2f})  "
                  f"axis ({ax[0]:.3g}, {ax[1]:.3g}, {ax[2]:.3g})")
        return 0

    if a.cmd == "mate":
        rp = part(a.part)
        comp, _, mouth = a.onto.partition(".")
        if not mouth:
            raise SystemExit(f"--onto {a.onto!r}: expected component.port")
        w = probe.world()
        tip, nrm = w.at(comp, mouth), w.normal(comp, mouth)
        axis = nrm if a.along else tuple(-c for c in nrm)
        pose = rp.mate(a.port, at=tip, axis=axis, spin=a.spin)
        print(f"{a.part}.{a.port} onto {a.onto} at "
              f"({tip[0]:.2f}, {tip[1]:.2f}, {tip[2]:.2f})")
        print(f"  {pose}")
        print("  " + str(check(pose, skip=skip or (comp,), clearance=a.clearance, near=a.near)))
        for n in rp.ports:
            if n == a.port:
                continue
            pos, ax = pose.port(n)
            print(f"  far end {n:14s} ({pos[0]:8.2f}, {pos[1]:8.2f}, {pos[2]:8.2f})  "
                  f"axis ({ax[0]:.3g}, {ax[1]:.3g}, {ax[2]:.3g})")
        return 0

    if a.cmd == "search":
        search(part(a.part), x=_triple(a.x), y=_triple(a.y), z=_triple(a.z),
               yaw=_list(a.yaw), pitch=_list(a.pitch), roll=_list(a.roll),
               anchor=a.anchor, clearance=a.clearance, skip=skip, limit=a.limit, top=a.top,
               near=a.near, resolve=a.resolve)
        return 0

    if a.cmd == "slab":
        exact = True if a.exact == "all" else tuple(s for s in a.exact.split(",") if s)
        slab(z=tuple(_list(a.z)), x=tuple(_list(a.x)) if a.x else None,
             y=tuple(_list(a.y)) if a.y else None, step=a.step,
             size=tuple(_list(a.size)) if a.size else None, skip=skip, exact=exact,
             top=a.top, floor=a.floor)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
