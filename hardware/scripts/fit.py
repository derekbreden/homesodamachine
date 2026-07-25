"""Candidate poses — carry a part to where it is not yet, and ask whether it fits.

`probe` answers questions about the world as it stands. This answers them about a body
that is not in it: a reference part carried to a pose, its ports carried by the same
transform, measured against the placed world.

    import fit

    p = fit.part("beduan-solenoid")             # module, builder and ports, discovered
    pose = p.pose(at=(x, y, z), yaw=90)
    print(fit.check(pose, skip=("vk-fill-valve",)))
    print(pose.port("inlet"))                   # world position and axis

The body and its ports move under one `cq.Location`, so a port cannot drift from the face
it names. A pose reports the transform it used; two poses of the same part with the same
arguments are the same solid.

Clearance is a threshold on an exact measured distance, never an inflation of the
obstacles: a pose free at 3 mm is a pose free at 0 mm, always. `search` ranks the free
poses by how much room they leave.

    fit.search(p, x=(xlo, xhi, step), y=(ylo, yhi, step), z=deck,
               yaw=(0, 90, 180, 270), clearance=2.0, skip=("vk-fill-valve",))

    fit.slab(z=(deck, ceiling), size=(width, depth), exact=("seaflo-pump",))

`slab` maps what is free in a Z band rather than testing one part: the largest rectangles
a footprint could stand in. Obstacles count by their bounding box unless named in `exact`,
which measures against the solid — a part that is mostly air reads as mostly air.

From the shell, without writing a file:

    tools/cad-venv/bin/python hardware/scripts/fit.py parts
    tools/cad-venv/bin/python hardware/scripts/fit.py ports beduan-solenoid
    tools/cad-venv/bin/python hardware/scripts/fit.py try beduan-solenoid --at 222,322,274 --yaw 90
    tools/cad-venv/bin/python hardware/scripts/fit.py search meanwell-irm90 \
        --x 0,90,10 --y 200,340,10 --z 268 --yaw 0,90 --clearance 2
    tools/cad-venv/bin/python hardware/scripts/fit.py slab --z 267,331 --size 74,52
    tools/cad-venv/bin/python hardware/scripts/fit.py selftest

`selftest` checks the instrument against known-answer geometry — that a port lands on the
body it belongs to at arbitrary angles, that clearance only ever removes poses, that a
known fit fits and a known clash clashes. Run it when an answer looks wrong before
trusting the answer.
"""

import inspect
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq

from OCP.gp import gp_Pnt, gp_Vec

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import probe                                                        # noqa: E402

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_REF = _HW / "reference"

VOL_TOL = probe.VOL_TOL         # mm³ below which an intersection is contact, not overlap
TOUCH = 1e-7                    # mm below which an exact distance is contact, not a gap

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
    """A reference part in its own coordinates, with the ports it declares."""

    def __init__(self, name: str, builder=None):
        self.name = name
        self.module = _module_for(name)
        self.step = None
        if builder is not None:
            self._builder = builder
        elif self.module is not None:
            self._builder = _builder(self.module, name)
        else:
            self.step = _step_for(name)
            if self.step is None:
                raise FileNotFoundError(
                    f"{name}: neither a module nor a .step in {_dir_for(name)} — "
                    f"nothing here builds this part")
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
        where the rotated bounding box's low corner lands, which is how `_contents._at`
        seats a body in the pack."""
        if (at is None) == (bbmin is None):
            raise ValueError("pose needs exactly one of at= (the part's origin) "
                             "or bbmin= (its bounding-box low corner)")
        rot = _rotation(yaw, pitch, roll)
        if bbmin is not None:
            b = self.solid.moved(rot).BoundingBox()
            at = (bbmin[0] - b.xmin, bbmin[1] - b.ymin, bbmin[2] - b.zmin)
        loc = cq.Location(cq.Vector(*(float(c) for c in at))) * rot
        return Pose(self, loc, (yaw, pitch, roll))

    def __repr__(self) -> str:
        b = self.bb
        return (f"<Part {self.name} {b.xlen:.1f}×{b.ylen:.1f}×{b.zlen:.1f} "
                f"ports={','.join(self.ports) or 'none'}>")


def part(name: str, builder=None) -> Part:
    """A reference part by its `hardware/reference/` directory name."""
    return Part(name, builder=builder)


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


def _carry_point(loc: cq.Location, p) -> tuple:
    q = gp_Pnt(float(p[0]), float(p[1]), float(p[2]))
    q.Transform(loc.wrapped.Transformation())
    return (q.X(), q.Y(), q.Z())


def _carry_axis(loc: cq.Location, a) -> tuple:
    """An axis takes the rotation and not the translation — `gp_Vec` is the direction
    half of the same transform that moved the body."""
    v = gp_Vec(float(a[0]), float(a[1]), float(a[2]))
    v.Transform(loc.wrapped.Transformation())
    return (v.X(), v.Y(), v.Z())


# --- fit ------------------------------------------------------------------

@dataclass
class Verdict:
    """What a candidate ran into and how much room it left."""

    clashes: list = field(default_factory=list)         # probe.Hit, worst first
    gaps: list = field(default_factory=list)            # (mm, name), nearest first
    clearance: float = 0.0

    @property
    def clear(self) -> bool:
        """No overlap and nothing closer than `clearance`."""
        return not self.clashes and not self.tight

    @property
    def tight(self) -> list:
        """Bodies inside the clearance threshold without overlapping."""
        return [(g, n) for g, n in self.gaps if g < self.clearance]

    @property
    def nearest(self) -> tuple:
        if not self.gaps:
            raise ValueError("nearest: nothing was measured — every body was skipped")
        return self.gaps[0]

    @property
    def room(self) -> float:
        """Distance to the closest body — the margin a free pose leaves. Infinite when
        nothing was near enough to measure."""
        if self.clashes:
            return 0.0
        return self.gaps[0][0] if self.gaps else math.inf

    def __str__(self) -> str:
        if self.clashes:
            return "CLASH " + ", ".join(f"{h.name} {h.volume:.1f} mm³" for h in self.clashes[:4])
        if self.tight:
            return "TIGHT " + ", ".join(f"{n} {g:.2f}" for g, n in self.tight[:4])
        near = ", ".join(f"{n} {g:.2f}" for g, n in self.gaps[:4]) or "nothing within reach"
        return f"CLEAR  nearest: {near}"


def check(candidate, skip=(), clearance: float = 0.0, world=None, near: float = 25.0) -> Verdict:
    """What `candidate` — a `Pose`, a shape, or a `(solid, color)` pack entry — runs into.

    Overlaps are exact intersections; distances are exact minimum distances. `near` bounds
    which bodies get measured: a body whose bounding box is further than that cannot be the
    nearest and is not queried. Raise it when a pose sits alone in a large void."""
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
            gaps.append((sep, name))        # already outside the threshold by its box alone
            continue
        d = w.gap(name, sh)
        if d > TOUCH:
            gaps.append((d, name))
            continue
        try:
            inter = sh.intersect(w.solid(name))
            overlap = inter.Volume()
        except Exception as exc:
            raise RuntimeError(
                f"intersection with {name} failed ({exc}) — this body's occupancy is "
                f"unknown, not empty") from exc
        if overlap > VOL_TOL:
            clashes.append(probe.Hit(name, overlap, inter.BoundingBox()))
        else:
            gaps.append((d, name))          # touching, not overlapping
    clashes.sort(key=lambda h: -h.volume)
    gaps.sort()
    return Verdict(clashes, gaps, float(clearance))


def _conflict(sh, w, skip=(), clearance: float = 0.0):
    """The first body `sh` overlaps or comes within `clearance` of, or `None`.

    The same test `check` makes, stopping at the first answer instead of measuring every
    neighbour — a rejected pose costs one exact query rather than twenty. Only bodies whose
    bounding box is already inside the threshold can be a conflict, and the nearest box is
    tried first."""
    cb = sh.BoundingBox()
    near = []
    for name in w.names:
        if name in skip:
            continue
        sep = _bb_gap(cb, w.bb(name))
        if sep > clearance:                 # a box gap under-states the solid gap
            continue
        near.append((sep, name))
    for _, name in sorted(near):
        d = w.gap(name, sh)
        if d >= clearance and d > TOUCH:
            continue
        if d < clearance:
            return name
        try:
            if sh.intersect(w.solid(name)).Volume() > VOL_TOL:
                return name
        except Exception as exc:
            raise RuntimeError(
                f"intersection with {name} failed ({exc}) — this body's occupancy is "
                f"unknown, not empty") from exc
    return None


def _bb_gap(a, b) -> float:
    """Separation between two axis-aligned boxes — 0 if they overlap. Never more than the
    distance between the solids inside them."""
    dx = max(0.0, a.xmin - b.xmax, b.xmin - a.xmax)
    dy = max(0.0, a.ymin - b.ymax, b.ymin - a.ymax)
    dz = max(0.0, a.zmin - b.zmax, b.zmin - a.zmax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# --- searching a pose grid ------------------------------------------------

@dataclass
class Candidate:
    pose: Pose
    verdict: Verdict

    @property
    def room(self) -> float:
        return self.verdict.room

    def __str__(self) -> str:
        return f"{self.pose}  {self.verdict}"


def _axis_values(spec, label: str) -> list:
    """A scalar, a `(lo, hi, step)` triple, or any iterable of values."""
    if spec is None:
        raise ValueError(f"search needs {label}=")
    if isinstance(spec, (int, float)):
        return [float(spec)]
    if isinstance(spec, tuple) and len(spec) == 3 and all(isinstance(v, (int, float)) for v in spec):
        lo, hi, step = (float(v) for v in spec)
        if step <= 0:
            raise ValueError(f"{label}=({lo}, {hi}, {step}): step must be positive")
        n = int(math.floor((hi - lo) / step + 1e-9))
        return [lo + i * step for i in range(n + 1)]
    return [float(v) for v in spec]


def search(part: Part, x, y, z, yaw=(0.0,), pitch=(0.0,), roll=(0.0,), anchor: str = "at",
           clearance: float = 0.0, skip=(), world=None, limit=None, quiet: bool = False) -> list:
    """Every free pose on a grid, best room first.

    Each axis takes a scalar, a `(lo, hi, step)` triple or a list. `anchor` is `"at"` (the
    part's origin lands on the grid point) or `"bbmin"` (its rotated box's low corner does).
    `skip` must name the body being re-placed — a part already in the world clashes with
    itself.

    Raising `clearance` can only remove poses: it is a threshold on a measured distance and
    the distances do not depend on it."""
    if anchor not in ("at", "bbmin"):
        raise ValueError(f"anchor={anchor!r}: expected 'at' or 'bbmin'")
    w = world or probe.world()
    grid = [(gx, gy, gz, ya, pi, ro)
            for gx in _axis_values(x, "x")
            for gy in _axis_values(y, "y")
            for gz in _axis_values(z, "z")
            for ya in _axis_values(yaw, "yaw")
            for pi in _axis_values(pitch, "pitch")
            for ro in _axis_values(roll, "roll")]
    if limit is not None and len(grid) > limit:
        raise ValueError(
            f"search would test {len(grid)} poses, over limit={limit} — coarsen a step "
            f"or narrow a range, or raise limit if the wait is wanted")

    out = []
    for gx, gy, gz, ya, pi, ro in grid:
        kw = {anchor: (gx, gy, gz)}
        p = part.pose(yaw=ya, pitch=pi, roll=ro, **kw)
        if _conflict(p.solid, w, skip=skip, clearance=clearance) is not None:
            continue
        out.append(Candidate(p, check(p, skip=skip, clearance=clearance, world=w)))
    out.sort(key=lambda c: -c.room)
    if not quiet:
        print(f"{len(out)} free of {len(grid)} poses at clearance {clearance:g} mm"
              + (f", best room {out[0].room:.2f} mm" if out else ""))
        for c in out[:12]:
            print(f"  {c}")
    return out


# --- free space in a slab -------------------------------------------------

@dataclass
class Rect:
    """A free footprint in a Z band."""

    x: tuple
    y: tuple
    z: tuple

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
        return (f"{self.w:6.1f} × {self.d:6.1f} mm  ({self.area:8.0f} mm²)  "
                f"x[{self.x[0]:7.1f},{self.x[1]:7.1f}] y[{self.y[0]:7.1f},{self.y[1]:7.1f}] "
                f"z[{self.z[0]:.1f},{self.z[1]:.1f}]")


def slab(z: tuple, x: tuple = None, y: tuple = None, step: float = 4.0, skip=(),
         exact=(), size: tuple = None, world=None, top: int = 8, quiet: bool = False) -> list:
    """The largest free rectangles in the Z band `z`, biggest area first.

    A cell is occupied when a body reaches into the band above it. Bodies count by their
    bounding box, which over-states them — every rectangle returned is genuinely free, and
    a part that is mostly air hides space behind its box. Name those in `exact` (or pass
    `exact=True`) to intersect the band against the solid instead.

    `size=(w, d)` keeps only rectangles that hold that footprint in either orientation."""
    w = world or probe.world()
    zlo, zhi = float(z[0]), float(z[1])
    if zhi <= zlo:
        raise ValueError(f"slab z=({zlo}, {zhi}): hi must exceed lo")

    live = [n for n in w.names if n not in skip and w.bb(n).zmax > zlo and w.bb(n).zmin < zhi]
    if x is None or y is None:
        bounds = _interior(w, skip)
        x = x or bounds[0]
        y = y or bounds[1]
    x0, x1, y0, y1 = float(x[0]), float(x[1]), float(y[0]), float(y[1])
    nx, ny = max(1, int(round((x1 - x0) / step))), max(1, int(round((y1 - y0) / step)))
    sx, sy = (x1 - x0) / nx, (y1 - y0) / ny

    want_exact = set(live) if exact is True else {n for n in exact if n in live}
    grid = [[False] * ny for _ in range(nx)]

    for name in live:
        b = w.bb(name)
        i0, i1 = _span(b.xmin, b.xmax, x0, sx, nx)
        j0, j1 = _span(b.ymin, b.ymax, y0, sy, ny)
        if i0 >= i1 or j0 >= j1:
            continue
        if name not in want_exact:
            for i in range(i0, i1):
                for j in range(j0, j1):
                    grid[i][j] = True
            continue
        solid = w.solid(name)
        for i in range(i0, i1):
            for j in range(j0, j1):
                if grid[i][j]:
                    continue
                cell = probe.box(x=(x0 + i * sx, x0 + (i + 1) * sx),
                                 y=(y0 + j * sy, y0 + (j + 1) * sy), z=(zlo, zhi))
                try:
                    if cell.intersect(solid).Volume() > VOL_TOL:
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
    if not quiet:
        print(f"free in z[{zlo:.1f},{zhi:.1f}] on a {sx:.1f}×{sy:.1f} mm grid — "
              f"{len(rects)} rectangle(s)"
              + (f" holding {size[0]:g}×{size[1]:g}" if size else ""))
        for r in rects[:top]:
            print(f"  {r}")
    return rects


def _interior(w, skip=()) -> tuple:
    """The enclosure's inner cavity as `((xlo, xhi), (ylo, yhi))` — the default field for a
    slab, so a scan reports room inside the machine rather than the air around it."""
    try:
        probe._ensure_paths()
        import enclosure
        inner = enclosure._dims().inner
        return ((inner[0], inner[1]), (inner[2], inner[3]))
    except Exception:
        boxes = [w.bb(n) for n in w.names if n not in skip]
        if not boxes:
            raise ValueError("slab: no enclosure to bound the field and every body was "
                             "skipped — pass x= and y=")
        return ((min(b.xmin for b in boxes), max(b.xmax for b in boxes)),
                (min(b.ymin for b in boxes), max(b.ymax for b in boxes)))


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

    print("controls — fit:")
    # A wall whose face stands one cube-width east of the origin.
    face = 2.5 * side
    wall = probe.box(x=(face, face + side / 2), y=(-5 * side, 5 * side), z=(0, 5 * side))
    w = probe.World({"wall": wall}, {"wall": "test"})
    v = check(p.pose(at=(0, 0, 0)), world=w, near=4 * side)
    ok("a known miss is clear", v.clear and not v.clashes)
    ok("its gap is exact", abs(v.nearest[0] - (face - side / 2)) < 1e-6,
       f"{v.nearest[0]:.6f}", f"{face - side / 2}")
    v = check(p.pose(at=(face + 1.0, 0, 0)), world=w)
    ok("a known overlap clashes", bool(v.clashes) and not v.clear,
       f"{[h.name for h in v.clashes]}", "['wall']")
    v = check(p.pose(at=(face - side / 2, 0, 0)), world=w)
    ok("touching is not overlapping", v.clear and not v.clashes, f"clashes {len(v.clashes)}")

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

    print("controls — refusals:")
    for label, thunk in (
        ("unknown part name raises", lambda: part("no-such-part")),
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


def main(argv: list) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="fit", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("parts", help="every reference part, its size and its ports")

    p = sub.add_parser("ports", help="one part's ports in its own coordinates")
    p.add_argument("part")

    p = sub.add_parser("try", help="one pose against the placed world")
    p.add_argument("part")
    p.add_argument("--at", help="x,y,z the part's origin lands on")
    p.add_argument("--bbmin", help="x,y,z its bounding box's low corner lands on")
    for a in ("yaw", "pitch", "roll"):
        p.add_argument(f"--{a}", type=float, default=0.0)
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")

    p = sub.add_parser("search", help="every free pose on a grid, best room first")
    p.add_argument("part")
    for a in ("x", "y", "z"):
        p.add_argument(f"--{a}", required=True, help="value or lo,hi,step")
    for a in ("yaw", "pitch", "roll"):
        p.add_argument(f"--{a}", default="0", help="comma-separated angles")
    p.add_argument("--anchor", default="at", choices=("at", "bbmin"))
    p.add_argument("--clearance", type=float, default=0.0)
    p.add_argument("--skip", default="")
    p.add_argument("--limit", type=int, default=20000)

    p = sub.add_parser("slab", help="the largest free rectangles in a Z band")
    p.add_argument("--z", required=True, help="lo,hi")
    p.add_argument("--x", help="lo,hi")
    p.add_argument("--y", help="lo,hi")
    p.add_argument("--step", type=float, default=4.0)
    p.add_argument("--size", help="w,d a footprint to hold")
    p.add_argument("--skip", default="")
    p.add_argument("--exact", default="", help="bodies to measure as solids, or 'all'")
    p.add_argument("--top", type=int, default=8, help="how many rectangles to print")

    sub.add_parser("selftest", help="known-answer controls, then load every reference part")

    a = ap.parse_args(argv)
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

    if a.cmd == "ports":
        rp = part(a.part)
        print(rp)
        for n in rp.ports:
            pos, ax = rp.local_port(n)
            print(f"  {n:16s} ({pos[0]:8.2f}, {pos[1]:8.2f}, {pos[2]:8.2f})  "
                  f"axis ({ax[0]:g}, {ax[1]:g}, {ax[2]:g})")
        return 0

    if a.cmd == "try":
        rp = part(a.part)
        if (a.at is None) == (a.bbmin is None):
            raise SystemExit("try needs exactly one of --at or --bbmin")
        where = {"at": _list(a.at)} if a.at else {"bbmin": _list(a.bbmin)}
        pose = rp.pose(yaw=a.yaw, pitch=a.pitch, roll=a.roll, **where)
        print(pose)
        print("  " + str(check(pose, skip=skip, clearance=a.clearance)))
        for n in rp.ports:
            pos, ax = pose.port(n)
            print(f"  {n:16s} ({pos[0]:8.2f}, {pos[1]:8.2f}, {pos[2]:8.2f})  "
                  f"axis ({ax[0]:.3g}, {ax[1]:.3g}, {ax[2]:.3g})")
        return 0

    if a.cmd == "search":
        search(part(a.part), x=_triple(a.x), y=_triple(a.y), z=_triple(a.z),
               yaw=_list(a.yaw), pitch=_list(a.pitch), roll=_list(a.roll),
               anchor=a.anchor, clearance=a.clearance, skip=skip, limit=a.limit)
        return 0

    if a.cmd == "slab":
        exact = True if a.exact == "all" else tuple(s for s in a.exact.split(",") if s)
        slab(z=tuple(_list(a.z)), x=tuple(_list(a.x)) if a.x else None,
             y=tuple(_list(a.y)) if a.y else None, step=a.step,
             size=tuple(_list(a.size)) if a.size else None, skip=skip, exact=exact, top=a.top)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
