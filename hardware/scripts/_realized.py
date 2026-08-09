"""A solid drawn once and kept, keyed on everything that decides its shape.

    import _realized
    shape = _realized.realized(_realized.key(__name__, description), lambda: draw(description))

A part is redrawn on every build, and most builds change nothing about it — an agent moving one
body rebuilds the four printed pieces, whose shape is decided by the box description and the
code that cuts it, neither of which moved. `realized` reads such a part back off disk instead.

WHAT THE KEY MUST COVER IS EVERYTHING THAT DECIDES THE SHAPE, and a key that misses one is a
build that ships last run's geometry. Two things decide it, and the key takes both:

  - THE CODE. Not one file: the module that draws, and every module of this repo it can reach
    through its own namespace. `enclosure` cuts its throat at `hopper_funnel.collar_w` and its
    wells at `wago_221`'s body, so an edit to either is an edit to the wall — and neither shows
    in `enclosure.py`. `sources` walks that graph and the whole text of each file goes in, so an
    edit anywhere in any of them misses.

  - THE DESCRIPTION, by `repr`. A description that does not repr completely is a key that
    cannot see part of its own input: `enclosure.Box` is a namedtuple of numbers and station
    tuples and repr's whole, which is what makes it usable here.

WHAT THE KEY CANNOT COVER IS A READING TAKEN WHILE DRAWING. A part that records into a ledger as
it cuts is a part whose second call does something its first call did — hand back the kept solid
and the ledger goes unfilled, with no row saying so. `enclosure.build_pieces` draws a piece and
takes no reading; `enclosure.with_funnel` states the throat's bounds where the centre is seated.

The entries are not committed and carry no meaning between machines: `.gitignore` holds
`.cache/`, a miss costs exactly what the build always cost, and deleting the directory is
always safe.
"""

import hashlib
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DIR = _ROOT / ".cache" / "realized"

# A build that must not read a kept solid — the one that proves the cache is honest — sets this.
DISABLED = bool(os.environ.get("HSM_NO_REALIZED_CACHE"))

_SOURCES: dict = {}


def sources(module_name: str) -> list:
    """Every file of this repo whose text can decide what `module_name` draws: its own, and
    each repo module reachable from its namespace, transitively. Sorted, so the walk order
    never reaches the key."""
    hit = _SOURCES.get(module_name)
    if hit is not None:
        return hit
    seen, found, queue = set(), set(), [module_name]
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        mod = sys.modules.get(name)
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        path = Path(f).resolve()
        if _ROOT not in path.parents or "site-packages" in path.parts:
            continue
        found.add(path)
        for value in vars(mod).values():
            inner = getattr(value, "__name__", None)
            if inner and inner in sys.modules and hasattr(value, "__file__"):
                queue.append(inner)
    _SOURCES[module_name] = out = sorted(found)
    return out


def key(module_name: str, *inputs) -> str:
    """A name for the shape `module_name` draws from `inputs`."""
    h = hashlib.blake2b(digest_size=16)
    for path in sources(module_name):
        h.update(path.read_bytes())
    for i in inputs:
        h.update(repr(i).encode())
    return h.hexdigest()


def realized(name: str, build):
    """The shape `build()` draws, read back from disk when `name` already stands for one."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    import cadquery as cq

    if DISABLED:
        return build()
    path = _DIR / f"{name}.brep"
    if path.is_file():
        shape, builder = TopoDS_Shape(), BRep_Builder()
        if BRepTools.Read_s(shape, str(path), builder) and not shape.IsNull():
            return cq.Workplane(obj=cq.Shape.cast(shape))
    made = build()
    solid = made.val() if hasattr(made, "val") else made
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        BRepTools.Write_s(solid.wrapped, str(tmp))
        os.replace(tmp, path)                    # a reader never sees a half-written entry
    except Exception:
        pass                                     # a cache that cannot be written is not an error
    return made


def selftest():
    """A kept solid is the drawn one; a key that cannot see its input is caught; and an edit to
    a module the drawing one reads through is an edit the key feels."""
    import tempfile
    import types
    import cadquery as cq

    drawn = [0]

    def draw(r):
        drawn[0] += 1
        return cq.Workplane(obj=cq.Solid.makeCylinder(r, 10.0))

    global _DIR
    held, _DIR = _DIR, Path(tempfile.mkdtemp(prefix="hsm-realized-"))
    try:
        k = key(__name__, ("selftest", 3.0))
        first = realized(k, lambda: draw(3.0))
        second = realized(k, lambda: draw(3.0))
        if drawn[0] != 1:
            raise AssertionError(f"one shape was drawn {drawn[0]} times — the key does not stand "
                                 f"for it, so nothing is ever read back")
        a, b = first.val().Volume(), second.val().Volume()
        if abs(a - b) > 1e-9:
            raise AssertionError(f"a kept solid measures {b:.6f} where the drawn one measures "
                                 f"{a:.6f} — the round trip is not the shape")
        yield f"a kept solid is the drawn one, to {abs(a-b):.1e} mm³"

        if key(__name__, ("selftest", 3.0)) == key(__name__, ("selftest", 4.0)):
            raise AssertionError("two descriptions share a key — a change to one would be "
                                 "served the other's geometry")
        yield "two descriptions do not share a key"

        # A module this one reads a constant through, and an edit to that constant's file.
        dep_dir = Path(tempfile.mkdtemp(prefix="hsm-realized-dep-", dir=_ROOT))
        try:
            dep = dep_dir / "held_constant.py"
            dep.write_text("radius = 3.0\n")
            mod = types.ModuleType("held_constant")
            mod.__file__ = str(dep)
            sys.modules["held_constant"] = mod
            drawer = types.ModuleType("held_drawer")
            drawer.__file__ = str(dep_dir / "held_drawer.py")
            Path(drawer.__file__).write_text("import held_constant\n")
            drawer.held_constant = mod
            sys.modules["held_drawer"] = drawer

            if dep.resolve() not in sources("held_drawer"):
                raise AssertionError("a module the drawer reads through is not in its sources — "
                                     "an edit to it would not move the key")
            before = key("held_drawer", ("selftest",))
            dep.write_text("radius = 4.0\n")
            _SOURCES.pop("held_drawer", None)
            if key("held_drawer", ("selftest",)) == before:
                raise AssertionError("a constant moved and the key did not — the next build "
                                     "would be served geometry cut to the old one")
            yield "an edit to a module the drawer reads through moves the key"
        finally:
            for n in ("held_constant", "held_drawer"):
                sys.modules.pop(n, None)
            _SOURCES.pop("held_drawer", None)
            for f in dep_dir.iterdir():
                f.unlink()
            dep_dir.rmdir()
    finally:
        _DIR = held


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_realized selftest OK")
