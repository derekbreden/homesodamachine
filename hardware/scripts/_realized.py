"""A solid drawn once and kept, keyed on everything that decides its shape.

    import _realized
    shape = _realized.realized(_realized.key(__name__, description), lambda: draw(description))

A part is redrawn on every build, and most builds change nothing about it — an agent moving one
body rebuilds the four printed pieces, whose shape is decided by the box description and the
code that cuts it, neither of which moved. `realized` reads such a part back off disk instead.

WHAT THE KEY MUST COVER IS EVERYTHING THAT DECIDES THE SHAPE, and a key that misses one is a
build that ships last run's geometry. Two things decide it, and the key takes both:

  - THE CODE. Not one file: the module that draws, and every module of this repo it imports,
    transitively. `enclosure` cuts its throat at `hopper_funnel.collar_w` and its wells at
    `wago_221`'s body, so an edit to either is an edit to the wall — and neither shows in
    `enclosure.py`. `sources` walks that graph off the IMPORT STATEMENTS, which is the one
    reading that holds however a name was bound: `from _seating import seat_body` puts no
    module in the namespace, and the file behind `seat_body` decides a seat all the same.
    The whole text of each file found goes in, so an edit anywhere in any of them misses.

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

import ast
import hashlib
import importlib.util
import io
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DIR = _ROOT / ".cache" / "realized"

# A build that must not read a kept solid — the one that proves the cache is honest — sets this.
DISABLED = bool(os.environ.get("HSM_NO_REALIZED_CACHE"))

_SOURCES: dict = {}


def _repo_file(name: str):
    """The path a module name stands for, when it is a file of this repo.

    FOUND ON THE PATH AND NOT IN `sys.modules`. A module imported inside the function that needs
    it — `enclosure_assembly.main` takes `_scorecard` that way — is in `sys.modules` only once
    that function has run, so a walk that asks `sys.modules` gets a different graph depending on
    who is walking. `find_spec` locates the file without importing it, which is the same answer
    from every caller."""
    f = getattr(sys.modules.get(name), "__file__", None)
    if not f:
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, AttributeError, ValueError):
            return None
        f = getattr(spec, "origin", None) if spec else None
    if not f or not f.endswith(".py"):
        return None
    path = Path(f).resolve()
    return None if _ROOT not in path.parents or "site-packages" in path.parts else path


def _imported(path: Path) -> set:
    """The module names a file imports, read off its own import statements.

    THE STATEMENT AND NOT THE NAMESPACE. `from _seating import seat_body` leaves `_seating`
    nowhere in the importing module's namespace, so a namespace walk cannot see the file that
    decides what `seat_body` does — and a key that cannot see a file is a key that holds still
    while that file moves. The text says what was imported however the name was bound."""
    try:
        tree = ast.parse(path.read_bytes())
    except (OSError, SyntaxError):
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.add(node.module)
            # `from pkg import mod` names a module too; `_repo_file` says which names are files.
            out.update(f"{node.module}.{a.name}" for a in node.names)
    return out


def source_files(start) -> list:
    """Every file of this repo whose text can decide what `start` draws: its own, and each repo
    module it imports, transitively. `start` is a path, so it does not matter whether the file
    was run as a script or imported under its own name. Sorted, so the walk order never reaches
    the key."""
    seen, queue = set(), [Path(start).resolve()]
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        for name in _imported(path):
            inner = _repo_file(name)
            if inner is not None:
                queue.append(inner)
    return sorted(seen)


def sources(module_name: str) -> list:
    """`source_files` for a module already imported under `module_name`."""
    hit = _SOURCES.get(module_name)
    if hit is not None:
        return hit
    start = _repo_file(module_name)
    _SOURCES[module_name] = out = [] if start is None else source_files(start)
    return out


def digest(paths) -> str:
    """One name for the whole text of `paths`, in the order given."""
    h = hashlib.blake2b(digest_size=16)
    for path in paths:
        h.update(Path(path).read_bytes())
    return h.hexdigest()


def key(module_name: str, *inputs) -> str:
    """A name for the shape `module_name` draws from `inputs`."""
    h = hashlib.blake2b(digest_size=16)
    h.update(digest(sources(module_name)).encode())
    for i in inputs:
        h.update(repr(i).encode())
    return h.hexdigest()


def realized(name: str, build):
    """The shape `build()` draws, read back from disk when `name` already stands for one.

    A SHAPE OFF BREP IS NOT LAID OUT LIKE THE ONE THAT WAS DRAWN. Its faces and edges are the
    same faces and edges standing in a different order, which no reading can tell apart and the
    STEP writer can: the file it emits follows the order it walks. So EVERY shape leaves here
    through BREP, drawn or kept, and a 20 MB artifact does not churn on whether a local
    directory happened to be populated. `DISABLED` skips the disk, not the round trip, so the
    run that proves the kept work honest is comparing the one thing that differs."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    import cadquery as cq

    def off_brep(text):
        text.seek(0)
        shape, builder = TopoDS_Shape(), BRep_Builder()
        BRepTools.Read_s(shape, text, builder)
        return cq.Workplane(obj=cq.Shape.cast(shape))

    path = _DIR / f"{name}.brep"
    if not DISABLED and path.is_file():
        try:
            return off_brep(io.BytesIO(path.read_bytes()))
        except Exception:
            pass                                 # an entry that cannot be read is a miss
    made = build()
    solid = made.val() if hasattr(made, "val") else made
    text = io.BytesIO()
    BRepTools.Write_s(solid.wrapped, text)
    if not DISABLED:
        try:
            _DIR.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_bytes(text.getvalue())
            os.replace(tmp, path)                # a reader never sees a half-written entry
        except Exception:
            pass                                 # a cache that cannot be written is not an error
    return off_brep(text)


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
        straight = draw(3.0).val().Volume()
        for label, got in (("kept", b), ("drawn and handed back", a)):
            if abs(got - straight) > 1e-9:
                raise AssertionError(f"a {label} solid measures {got:.6f} where the shape as "
                                     f"drawn measures {straight:.6f} — the round trip is not "
                                     f"the shape")
        yield f"a kept solid is the drawn one, to {abs(a - straight):.1e} mm³"

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
            # THE BINDING THAT LEAVES NO MODULE BEHIND. The drawer reads the constant and the
            # name `held_constant` appears nowhere in what it ends up holding, which is the
            # shape a walk over the namespace cannot follow.
            Path(drawer.__file__).write_text("from held_constant import radius\n")
            drawer.radius = 3.0
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
            yield "an edit to a module the drawer reads a constant FROM moves the key"
        finally:
            for n in ("held_constant", "held_drawer"):
                sys.modules.pop(n, None)
            _SOURCES.pop("held_drawer", None)
            for f in dep_dir.iterdir():
                f.unlink()
            dep_dir.rmdir()
    finally:
        # The entries this run wrote go with the directory it wrote them to: a selftest cache is
        # one run's, and a machine that runs this often keeps one per run otherwise.
        for f in _DIR.iterdir() if _DIR.is_dir() else ():
            f.unlink()
        if _DIR.is_dir():
            _DIR.rmdir()
        _DIR = held


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_realized selftest OK")
