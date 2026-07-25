"""Geometry probe — ask the placed solids a question instead of reasoning about them.

The enclosure pack, its panel bodies, the hopper funnel and the routed tubes,
loaded as one flat `{name: shape}` world, with the queries that answer where a
part is, how close two parts come, what a candidate volume runs into, and how
far a line can travel before it hits something.

Every query is exact and every query is loud. A body that cannot be normalized
raises instead of being skipped; a boolean that fails raises with the body's
name; a cast that never contacts anything says so rather than reporting its own
limit as a clearance. Nothing here returns 0.0 for "I could not measure".

Use from anywhere in the repo:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"),
    )
    import probe

    w = probe.world()
    print(w.table(sort="ymin"))                       # every body's box
    w.gap("foam-assembly", "compressor-shroud")       # exact mm between two solids
    w.hits(probe.box(x=(100, 120), y=(160, 200), z=(30, 275)))   # what a lane runs into
    w.cast((110.1, 98.4, 273.1), (0, 0, -1), dia=6.35)           # how far a tube can drop

    probe.sweep(range(0, 360, 10), lambda a: w.cast(tip(a), aim(a)).free)

From the shell, without writing a file:

    tools/cad-venv/bin/python hardware/scripts/probe.py boxes --sort ymin
    tools/cad-venv/bin/python hardware/scripts/probe.py gap foam-assembly compressor-shroud
    tools/cad-venv/bin/python hardware/scripts/probe.py at bag-circuit-assembly.Y-H-2
    tools/cad-venv/bin/python hardware/scripts/probe.py cast 110.14,98.36,273.1 0,0,-1 --dia 6.35
    tools/cad-venv/bin/python hardware/scripts/probe.py hits --x 100,120 --y 160,200 --z 30,275
    tools/cad-venv/bin/python hardware/scripts/probe.py selftest

`selftest` runs the instrument against known-answer geometry — a known hit, a
known miss, a known distance — and then normalizes every body in the real world.
Run it when a number looks wrong before trusting the number.
"""

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_ENCLOSURE = _HW / "printed-parts" / "enclosure" / "enclosure-assembly"
_BOX = _HW / "printed-parts" / "enclosure" / "enclosure"        # `enclosure` — the box itself

VOL_TOL = 1e-6          # mm³ below which an intersection is contact noise, not overlap
TUBE_OD = 6.35          # 1/4" LLDPE, the default probe diameter
CAST_LIMIT = 250.0      # default cast length: longer than the box's largest span


# --- normalizing what the pack hands back ---------------------------------

def shape(obj, label: str = "?"):
    """The bare `cq.Shape` behind a pack entry: `(solid, color)` tuples and
    `Workplane`s unwrap, a `Shape` passes through, anything else raises naming
    its type. `_contents.build()` yields tuples and `placed_funnel()` yields a
    solid, so a caller that unwraps by hand gets one of them wrong."""
    obj = obj[0] if isinstance(obj, tuple) else obj
    obj = obj.val() if hasattr(obj, "val") else obj
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


# --- the world ------------------------------------------------------------

class World:
    """The placed solids, flat and normalized: `{name: cq.Shape}`."""

    def __init__(self, solids: dict, sources: dict):
        self.solids = solids
        self.sources = sources          # name → "component" | "panel" | "funnel" | "run"
        self._frames = None
        self._boxes = {}                # name → (solid, box), see bb()

    # -- what is here --

    @property
    def names(self) -> list:
        return sorted(self.solids)

    def solid(self, name: str):
        if name not in self.solids:
            raise KeyError(f"no body {name!r} — have: {', '.join(self.names)}")
        return self.solids[name]

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
        """`{component: Frame}` from the routing module — `.at(port)`,
        `.normal(port)`, `.diam(port)`, `.bb`."""
        if self._frames is None:
            import _lines
            self._frames = _lines._frames()
        return self._frames

    def at(self, component: str, port: str) -> tuple:
        return self.frames()[component].at(port)

    def normal(self, component: str, port: str) -> tuple:
        return self.frames()[component].normal(port)

    def ports(self, component: str) -> list:
        return sorted(self.frames()[component].ports)

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
                inter = v.intersect(self.solids[name])
                overlap = inter.Volume()
            except Exception as exc:
                raise RuntimeError(
                    f"intersection with {name} failed ({exc}) — this body's "
                    f"occupancy is unknown, not empty") from exc
            if overlap > tol:
                out.append(Hit(name, overlap, inter.BoundingBox()))
        return sorted(out, key=lambda h: -h.volume)

    def clear(self, vol, skip=()) -> bool:
        return not self.hits(vol, skip=skip)

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
                inter = probe_rod.intersect(self.solids[name])
                if inter.Volume() <= tol:
                    continue
            except Exception as exc:
                raise RuntimeError(
                    f"cast against {name} failed ({exc}) — the free run past this "
                    f"body is unknown, not clear") from exc
            t = _axis_min(inter, origin, d)
            if t < best:
                best, who = max(0.0, t), name
        return Contact(best, who, tuple(origin), d, limit, dia)


# --- vector helpers -------------------------------------------------------

def unit(v) -> tuple:
    n = math.sqrt(sum(float(c) * float(c) for c in v))
    if n < 1e-12:
        raise ValueError(f"direction {tuple(v)} has no length")
    return tuple(float(c) / n for c in v)


def _axis_min(sh, origin, d) -> float:
    """Smallest distance along `d` from `origin` of any point of `sh` — the
    shape is moved to the origin and rotated until `d` lies on +Z, where the
    bounding box's zmin is exactly that distance."""
    loc = sh.translate((-origin[0], -origin[1], -origin[2]))
    dot = d[2]
    if dot < 1.0 - 1e-12:
        if dot <= -1.0 + 1e-12:
            loc = loc.rotate((0, 0, 0), (1, 0, 0), 180.0)
        else:
            axis = (d[1], -d[0], 0.0)       # d × ẑ
            angle = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
            loc = loc.rotate((0, 0, 0), axis, angle)
    return loc.BoundingBox().zmin


# --- sweeping a continuous parameter --------------------------------------

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

    Reads a constant the pack is built from (rather than the box around it) and the memoized
    `_contents.build()` will hand back the pack from before the change — call
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


def bed_fit(pieces: dict, bed=None) -> list:
    """Each printed piece against the print bed, through the scorecard's own check:
    `(name, xlen, ylen, zlen, fits)` per piece, on the scorecard's own tolerance. `pieces`
    values normalize through `shape()`, so a `build_pieces()` Workplane is accepted."""
    _ensure_paths()
    import enclosure
    import scorecard

    if bed is None:
        bed = (enclosure.H2C_X, enclosure.H2C_Y, enclosure.H2C_Z)
    return scorecard.fit_bed({n: shape(p, n) for n, p in pieces.items()}, bed)


# --- loading --------------------------------------------------------------

_WORLD = None


def _ensure_paths() -> None:
    """The enclosure modules on sys.path, and the env a read-only run wants."""
    os.environ.setdefault("HSM_SKIP_THUMBNAILS", "1")
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    for d in (_ENCLOSURE, _BOX):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))


def world(runs: bool = True, reload: bool = False) -> World:
    """The placed world: the enclosure pack's components, the panel bodies
    seated through the walls, the hopper funnel, and (unless `runs=False`) the
    routed tubes. Memoized — building it imports and places every STEP."""
    global _WORLD
    if _WORLD is not None and not reload:
        return _WORLD

    _ensure_paths()

    import _contents as contents

    solids, sources = {}, {}

    def add(name, obj, source):
        if name in solids:
            raise ValueError(f"two bodies named {name!r} ({sources[name]} and {source})")
        solids[name] = shape(obj, name)
        sources[name] = source

    for name, entry in contents.build().items():
        add(name, entry, "component")
    for name, entry in contents.panel_bodies().items():
        add(name, entry, "panel")
    add("hopper-funnel", contents.placed_funnel(), "funnel")
    if runs:
        import _lines
        for name, entry in _lines.build().items():
            add(name, entry, "run")

    _WORLD = World(solids, sources)
    return _WORLD


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

    print("controls — refusals:")
    for label, thunk in (
        ("unnormalizable body raises", lambda: shape("not a solid", "x")),
        ("unknown body name raises", lambda: w.solid("nope")),
        ("zero-length direction raises", lambda: unit((0, 0, 0))),
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
          f"({sum(1 for s in real.sources.values() if s == 'run')} routed runs)")

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


def main(argv: list) -> int:
    import argparse

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

    p = sub.add_parser("hits", help="what a box runs into")
    for axis in "xyz":
        p.add_argument(f"--{axis}", required=True, help="lo,hi")
    p.add_argument("--skip", default="")

    sub.add_parser("selftest", help="known-answer controls, then load the world")

    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()

    w = world()
    skip = tuple(s for s in getattr(a, "skip", "").split(",") if s)

    if a.cmd == "boxes":
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
    elif a.cmd == "cast":
        print(w.cast(_pt(a.origin), _pt(a.direction), dia=a.dia, limit=a.limit, skip=skip))
    elif a.cmd == "hits":
        found = w.hits(box(x=_range(a.x), y=_range(a.y), z=_range(a.z)), skip=skip)
        print("\n".join(str(h) for h in found) if found else "CLEAR")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
