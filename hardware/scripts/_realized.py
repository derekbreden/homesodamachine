"""A solid drawn once and kept, keyed on everything that decides its shape.

    import _realized
    shape = _realized.realized(_realized.key(__name__, description), lambda: draw(description))

A part is redrawn on every build, and most builds change nothing about it — an agent moving one
body rebuilds the four printed pieces, whose shape is decided by the box description and the
code that cuts it, neither of which moved. `realized` reads such a part back off disk instead.

WHAT THE KEY MUST COVER IS EVERYTHING THAT DECIDES THE SHAPE, and a key that misses one is a
build that ships last run's geometry. Three things decide it, and the key takes all three:

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

  - THE KERNEL. The code says `cut` and `fuse`; OCCT is what performs them, so the same source
    and the same description hand back a different solid under a different kernel. This key
    needs naming it because it stands for an INSTRUCTION: `_boxes` and `_meshes` key on the
    serialized shape an entry came off, so a kernel computing a different shape moves their
    keys without being named in them. A description does not move at all. Nothing in
    this repo's text moves when `cadquery-ocp` does, and a key taken from the text alone stands
    for a shape the installed kernel no longer draws. `toolchain` reads the versions out of the
    running interpreter rather than off a file recording them, so there is no second step that
    can be skipped and leave the name unchanged while the kernel underneath it moved.

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
import re
import shutil
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DIR = _ROOT / ".cache" / "realized"

# A build that must not read a kept solid — the one that proves the cache is honest — sets this.
DISABLED = bool(os.environ.get("HSM_NO_REALIZED_CACHE"))

_SOURCES: dict = {}
_TOOLCHAIN: str | None = None


def generation() -> Path:
    """Where this kernel's entries live: one directory per toolchain under the store.

    AN ENTRY OUTLIVES THE KERNEL THAT WROTE IT AND CANNOT BE READ AGAIN. `key` names the
    toolchain, so every entry here is unreachable the moment a version moves — not replaced,
    stranded, because the new key is a new name and nothing collides with the old one. A flat
    store cannot tell a live entry from a stranded one: the name is a hash and holds nothing
    to sort by. A directory per toolchain is what makes the dead generation nameable, and
    `sweep` is what removes it.

    The cost of not doing this is a copy of the whole store per kernel: 793 MB across 1,682
    entries as it stands, beside `.cache/meshes`, which forks only for the shapes a kernel
    actually draws differently while this one forks for all of them."""
    return _DIR / re.sub(r"[^A-Za-z0-9._-]+", "-", toolchain())


def sweep() -> tuple[int, int]:
    """Drop every generation but this kernel's; answer what went, in entries and bytes.

    SAFE AT ANY MOMENT AND FROM ANYWHERE. What it removes is unreadable by construction — a
    key naming another toolchain is a key nothing running will ask for — and a miss costs
    exactly what the build always cost. A run reading the current generation while this walks
    the others touches nothing it holds."""
    gone = held = 0
    keep = generation()
    for child in _DIR.iterdir() if _DIR.is_dir() else ():
        if child == keep:
            continue
        for f in child.rglob("*") if child.is_dir() else (child,):
            if f.is_file():
                gone += 1
                held += f.stat().st_size
        shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()
    return gone, held


def toolchain() -> str:
    """The kernel this process draws with, named by the versions installed under it.

    READ ONCE PER PROCESS AND ONLY WHEN A KEY IS TAKEN. `importlib.metadata` costs 80 ms on this
    tree, which is a price per generator and not per shape. A distribution that is not installed
    is named as absent rather than skipped, so a kernel going missing moves the name it is part
    of instead of leaving it where the present one put it.

    IT NAMES VERSIONS, SO IT HOLDS EXACTLY AS WELL AS A VERSION STRING DOES. A `cadquery-ocp`
    rebuilt from source under the version it already carried is a different kernel wearing the
    same name, and every key here stands still across it.

    WHAT IT DELIBERATELY DOES NOT READ IS site-packages. `tools/cad-venv-site` keeps VTK out of
    the interpreter, which changes what a process IMPORTS and not what it COMPUTES — the solids
    are byte-identical with the shim and without it. Reaching for the installed set here would
    put that difference in every key and buy a whole-graph invalidation for a change no solid
    can see."""
    global _TOOLCHAIN
    if _TOOLCHAIN is None:
        from importlib.metadata import PackageNotFoundError, version

        held = []
        for dist in ("cadquery", "cadquery-ocp"):
            try:
                held.append(f"{dist}=={version(dist)}")
            except PackageNotFoundError:
                held.append(f"{dist}==absent")
        _TOOLCHAIN = " ".join(held)
    return _TOOLCHAIN


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


#: The module-level functions a script runs from, and nothing a module draws is reached through
#: them. `main` orchestrates a run — it exports, renders, re-checks — `selftest` exercises one,
#: and `machine_of` obtains an action's already-derived placement description or orchestrates the
#: direct design run that derives it. What they import is what the RUN needs, so it is read as the
#: run's and not the shape's. The start module itself is always read, including these functions.
ENTRY_POINTS = ("main", "selftest", "machine_of")


def _imported(path: Path) -> set:
    """The module names a file imports, read off its own import statements.

    THE STATEMENT AND NOT THE NAMESPACE. `from _seating import seat_body` leaves `_seating`
    nowhere in the importing module's namespace, so a namespace walk cannot see the file that
    decides what `seat_body` does — and a key that cannot see a file is a key that holds still
    while that file moves. The text says what was imported however the name was bound.

    THE BODY AND THE FUNCTIONS, NOT THE ENTRY POINTS. `enclosure_assembly.main` imports the
    scene renderer, the facts writer and the scene check, because one run writes all four
    artifacts; none of them can move a millimetre of what the module draws. Reading them as
    the shape's puts every renderer in the closure of every wall, so `ENTRY_POINTS` is where
    the walk stops. A sandboxed action holding what it declared reports any
    module the build imports that the walk did not name."""
    try:
        tree = ast.parse(path.read_bytes())
    except (OSError, SyntaxError):
        return set()
    skip = {id(fn) for fn in tree.body
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name in ENTRY_POINTS}
    out = set()
    for top in ast.iter_child_nodes(tree):
        if id(top) in skip:
            continue
        for node in ast.walk(top):
            if isinstance(node, ast.Import):
                out.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                out.add(node.module)
                # `from pkg import mod` names a module too; `_repo_file` says which are files.
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


_CODE: dict = {}


def code_digest(path) -> str | None:
    """A name for what a file COMPUTES, or None when it is not there.

    THE PARSED CODE AND NOT THE TEXT. A comment is invisible to Python, so a file whose comments
    moved draws the same walls, writes the same figures and takes the same picture — and a name
    taken over its bytes says otherwise, which is a rebuild of the whole tree to arrive back
    where it started. Two files that parse alike are named alike here.

    Docstrings stay in the name: they are values the code carries, and a doc that prints one has
    moved when it moves. Anything that will not parse is named by its bytes, which is what a
    `.json` table and a file mid-edit both want."""
    p = Path(path)
    try:
        st = p.stat()
    except OSError:
        return None
    stamp = (st.st_mtime_ns, st.st_size)
    hit = _CODE.get(path)
    if hit is not None and hit[0] == stamp:
        return hit[1]
    try:
        raw = p.read_bytes()
    except OSError:
        return None
    try:
        form = ast.dump(ast.parse(raw)).encode()
    except (SyntaxError, ValueError):
        form = raw
    out = hashlib.blake2b(form, digest_size=16).hexdigest()
    _CODE[path] = (stamp, out)
    return out


def digest(paths) -> str:
    """One name for what the whole of `paths` computes, in the order given."""
    h = hashlib.blake2b(digest_size=16)
    for path in paths:
        h.update((code_digest(path) or "").encode())
    return h.hexdigest()


def key(module_name: str, *inputs) -> str:
    """A name for the shape `module_name` draws from `inputs`.

    `HSM_INPUT_DIGEST` NAMES EVERYTHING THE RUN WAS GIVEN, and a build that sets it holds
    every file it declared and nothing else. The walk below reaches what `module_name`
    imports; a solid loaded off disk is not an import, and `enclosure.py` makes no
    `import_step` call while the run it happens in reaches 28 of them. So a key taken from
    the walk alone stands for a shape after a solid it was cut against has moved."""
    h = hashlib.blake2b(digest_size=16)
    h.update(os.environ.get("HSM_INPUT_DIGEST", "").encode())
    h.update(toolchain().encode())
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

    path = generation() / f"{name}.brep"
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
            path.parent.mkdir(parents=True, exist_ok=True)
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

        # THE KERNEL MOVES WITHOUT ANY FILE OF THIS REPO MOVING, which is the one input the
        # source walk cannot reach. Named here rather than upgraded here: the reading is what
        # `toolchain` returns, so standing a different answer in its place is the whole test.
        global _TOOLCHAIN
        under = _TOOLCHAIN
        try:
            _TOOLCHAIN = "cadquery==0 cadquery-ocp==0"
            other = key(__name__, ("selftest", 3.0))
        finally:
            _TOOLCHAIN = under
        if other == key(__name__, ("selftest", 3.0)):
            raise AssertionError("one description keeps its key across two kernels — an OCCT "
                                 "upgrade would be served the old kernel's geometry")
        yield f"a kernel this tree does not run does not share its key ({toolchain()})"

        # A GENERATION NOTHING CAN READ IS ONE `sweep` REMOVES, and the live one is what it
        # must not. Both halves, because a sweep that takes everything passes the first.
        stranded = _DIR / "cadquery-0-cadquery-ocp-0"
        stranded.mkdir(parents=True, exist_ok=True)
        (stranded / "old.brep").write_bytes(b"x" * 64)
        live = generation() / f"{k}.brep"
        if not live.exists():
            raise AssertionError("the kept entry is not under this kernel's generation — "
                                 "`realized` and `generation` disagree about where entries go")
        gone, freed = sweep()
        if stranded.exists():
            raise AssertionError("a generation this kernel cannot read survived the sweep")
        if not live.exists():
            raise AssertionError("the sweep took the generation this kernel is reading")
        yield f"a sweep drops the stranded generation and keeps the live one ({gone} entry, {freed} B)"

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
        shutil.rmtree(_DIR, ignore_errors=True)
        _DIR = held


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        n, b = sweep()
        print(f"dropped {n} entr{'y' if n == 1 else 'ies'}, {b / 1e6:.1f} MB — "
              f"kept {generation().name}")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_realized selftest OK")
