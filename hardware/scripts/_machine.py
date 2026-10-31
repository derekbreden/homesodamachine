"""The machine as `enclosure_assembly` last built it, read off its scene file.

Building the machine stands every body, draws every run and cuts the box. On the mesh kernel
the build leaves what it stood in `hardware/manifold-layout/enclosure-assembly.scene.npz`
(`meshcad.scene`): every body in world coordinates under its name, with its colour and face
records, and a document of what the bodies alone do not say. That is the authored runs, each
component's ports, the box, the anchor stations, the stamp of every source the build read, and
what the build's checks read off these bodies: the scorecard and the ASSE drain check.
`load()` hands it back as mesh solids a study can cut, measure and select faces on.

    import _machine
    m = _machine.machine()            # the scene, or the machine built and its scene written
    back_top = m.bodies["enclosure-back-top"]
    m.runs["fluid-14"].pts            # an authored run's waypoints
    m.frames["g-ganen-pump"].at("suction")
    m.card["gatesPass"]               # what its scorecard read

`machine()` reads the scene when no source has moved since it was taken, and otherwise builds
the machine on the mesh kernel, which runs its checks and writes the scene for the next reader.
`load()` reads whatever scene is on disk, and `measured()` says which machine that is.

A scene holds meshes, so it is read on the mesh kernel: a process reads one only when it has
taken the kernel before anything imported CadQuery (`meshcad.activate()`).
"""

import dataclasses
import json
import os
import sys
import time
import types
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
_ML = _ROOT / "hardware" / "manifold-layout"
PATH = _ML / "enclosure-assembly.scene.npz"
#: Moves when the document's layout does.
SCHEMA = 1

#: WHAT DECIDES THE MACHINE IS WHAT ITS BUILD WAS WATCHED READING: `graph.json`'s record of
#: `enclosure_assembly.py`, the one `gen_build.py` fills an action's sandbox from.
_GRAPH = _ROOT / "tools" / "bazel" / "graph.json"
_WORLD = "hardware/manifold-layout/enclosure_assembly.py"
_FALLBACK_SOURCES = ("manifold-layout/enclosure_assembly.py", "manifold-layout/_lines.py",
                     "manifold-layout/manifold_layout.py", "scripts/_routing.py",
                     "printed-parts/enclosure/enclosure/enclosure.py")


def sources() -> tuple:
    """Every Python file of this repo whose text can decide the machine, repo-relative: what the
    build was watched reading, and the mesh kernel, which cut every body a scene holds and which
    OCCT's build does not read. A tree with no `graph.json` names the five files that are
    certainly among the first."""
    kernel = {str(p.relative_to(_ROOT)) for p in (_HERE.parent / "meshcad").glob("*.py")}
    try:
        entry = json.loads(_GRAPH.read_text())[_WORLD]
    except (OSError, ValueError, KeyError):
        return tuple(sorted(kernel | {f"hardware/{rel}" for rel in _FALLBACK_SOURCES}))
    return tuple(sorted(kernel | {p for p in entry.get("reads", ()) if p.endswith(".py")}))


def stamps() -> dict:
    """Each source's size and mtime: what decides whether a scene is still the tree's."""
    out = {}
    for rel in sources():
        try:
            st = (_ROOT / rel).stat()
        except OSError:
            out[rel] = "gone"
            continue
        out[rel] = f"{st.st_size}:{int(st.st_mtime)}"
    return out


@dataclasses.dataclass
class Machine:
    """One built machine. `bodies` holds every body the build measures (`solids`, the pack and
    the box's pieces with the cold core as one envelope) and the cold core's own bodies
    (`core`), each `{name: shape}` in world coordinates."""

    bodies: dict
    colors: dict                 # name → linear rgb, or None
    solids: tuple                # the names `enclosure_assembly._solids` reads
    core: tuple                  # the names `enclosure_assembly._core_solids` reads
    runs: dict                   # id → `_routing.Run`
    frames: dict                 # component → `_routing.Frame`
    box: object                  # the enclosure Box, its pack's placed bodies left out
    anchors: dict                # what prints it → ((mid, along, root, seat_r), …)
    sources: dict                # the stamps the build read, see `stamps`
    taken: float
    path: Path = None
    # What the build's checks read, as `_scorecard.to_dict` and `check_asse_drain.write` hand
    # them back.
    card: dict = None
    drain: dict = None

    @property
    def moved(self) -> tuple:
        """Which sources have moved since this machine was built, by name."""
        now, was = stamps(), self.sources
        return tuple(rel for rel in sorted(set(now) | set(was)) if now.get(rel) != was.get(rel))

    def measured(self) -> str:
        """Which machine this is, in one line, and what moved under it since."""
        head = (f"{len(self.solids)} bodies, {len(self.runs)} runs, built "
                f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(self.taken))}")
        gone = self.moved
        if not gone:
            return f"{head}, off this tree"
        named = ", ".join(Path(g).name for g in gone[:4])
        if len(gone) > 4:
            named += f" and {len(gone) - 4} more"
        return f"{head}, BEFORE {named} MOVED: this is the machine in that scene, not the tree's"


# --- writing -----------------------------------------------------------------


def _plain(value):
    """`value` as JSON: tuples and arrays as lists, numpy scalars as floats."""
    import numpy as np
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_plain(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if hasattr(value, "toTuple"):                   # a cq.Vector
        return list(value.toTuple())
    return value


def _rgb(colour):
    if colour is None:
        return None
    from OCP.Quantity import Quantity_TypeOfColor
    return list(colour.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))


def document(a, taken=None, card=None, drain=None) -> dict:
    """What a reader of the built assembly `a` needs that its bodies do not say, and what its
    checks read off them."""
    import _box_spec
    import enclosure_assembly as ea
    frames = {name: {"ports": {port: _plain(row) for port, row in fr.ports.items()},
                     "bb": [fr.bb.xmin, fr.bb.xmax, fr.bb.ymin, fr.bb.ymax, fr.bb.zmin, fr.bb.zmax]}
              for name, fr in (getattr(a, "frames", None) or {}).items()}
    box = getattr(a, "box", None)
    return {
        "schema": SCHEMA,
        "taken": time.time() if taken is None else taken,
        "sources": stamps(),
        "solids": list(ea._solids(a)),
        "core": list(ea._core_solids(a)),
        "runs": [_plain(dataclasses.asdict(r)) for r in getattr(a, "runs", ())],
        "frames": frames,
        "box": None if box is None else _box_spec.document(ea._enc.documented(box)),
        "anchors": {k: _plain(getattr(a, k, ()) or ())
                    for k in ("tube_anchors", "cap_tube_anchors", "body_anchors")},
        "card": _plain(card),
        "drain": _plain(drain),
    }


def write(a, path=PATH, *, card=None, drain=None) -> Path:
    """The built assembly `a` as its scene: the bodies `_solids` and `_core_solids` read, and its
    document with the readings its checks took (`card`, `drain`). Written whole and then put in
    place, so a reader never meets half of one."""
    import enclosure_assembly as ea
    from meshcad import scene
    taken = time.time()
    bodies = [(name, shape, _rgb(colour))
              for name, (shape, colour) in {**ea._solids(a), **ea._core_solids(a)}.items()]
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    scene.write(bodies, tmp, document(a, taken, card, drain))
    os.replace(tmp, path)
    return path


# --- reading -----------------------------------------------------------------


def _tupled(value):
    """Lists back to the tuples they were written from."""
    if isinstance(value, list):
        return tuple(_tupled(v) for v in value)
    if isinstance(value, dict):
        return {k: _tupled(v) for k, v in value.items()}
    return value


def _run(row):
    import _routing as R
    row = dict(row)
    row["pts"] = [tuple(p) for p in row["pts"]]
    row["bends"] = [tuple(b) for b in row.get("bends", ())]
    for k in ("radii", "caps"):
        row[k] = {int(i): v for i, v in row.get(k, {}).items()}
    return R.Run(**row)


def _box(doc):
    """The Box the document names, its records restored as the named tuples they were written
    as, without importing the module that defines them."""
    import collections
    import _box_spec
    if doc is None:
        return None
    records = {}

    def collect(value):
        if isinstance(value, list):
            for v in value:
                collect(v)
        elif isinstance(value, dict):
            if _box_spec._RECORD in value:
                name = value[_box_spec._RECORD]
                records.setdefault(name, collections.namedtuple(name, value["fields"]))
            for v in value.values():
                collect(v)

    collect(doc["box"])
    Box = collections.namedtuple("Box", doc["box_fields"])
    return Box(*(_box_spec._tupled(doc["box"][f], records) for f in doc["box_fields"]))


def load(path=PATH):
    """The machine in the scene at `path`, or None when there is none."""
    import meshcad
    if not meshcad.mesh_mode():
        raise RuntimeError("_machine: a scene holds meshes, and this process's CadQuery is "
                           "OCCT's — take the mesh kernel (`meshcad.activate()`) before "
                           "anything imports cadquery")
    path = Path(path)
    if not path.is_file():
        return None
    from meshcad import scene
    import _routing as R
    doc = scene.document(path)
    if doc is None or doc.get("schema") != SCHEMA:
        return None
    held = scene.load(path)
    bodies = {name: shape for name, (shape, _rgb) in held.items()}
    frames = {}
    for name, f in doc["frames"].items():
        table = {port: (tuple(pos), tuple(axis) if isinstance(axis, list) else axis, diam)
                 for port, (pos, axis, diam) in f["ports"].items()}
        bb = types.SimpleNamespace(**dict(zip(("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"),
                                              f["bb"])))
        frames[name] = R.frame(name, None, table, bb=bb)
    return Machine(bodies=bodies, colors={name: rgb for name, (_s, rgb) in held.items()},
                   solids=tuple(doc["solids"]), core=tuple(doc["core"]),
                   runs={row["id"]: _run(row) for row in doc["runs"]}, frames=frames,
                   box=_box(doc["box"]), anchors=_tupled(doc["anchors"]),
                   sources=doc["sources"], taken=doc["taken"], path=path,
                   card=doc.get("card"), drain=doc.get("drain"))


def current(path=PATH):
    """The scene at `path` when no source has moved since it was taken, else None. Its document
    says so before a body is read."""
    path = Path(path)
    if not path.is_file():
        return None
    from meshcad import scene
    doc = scene.document(path)
    if doc is None or doc.get("schema") != SCHEMA or doc["sources"] != stamps():
        return None
    return load(path)


def machine():
    """This tree's machine: the scene when it is current, or else the machine built on the mesh
    kernel, its checks run and its scene written for the next reader, then read.

    THE BUILD IS A PROCESS OF ITS OWN, `enclosure_assembly.py` run on the kernel as any mesh
    build runs (`meshcad/run.py`). It stands the whole machine, and its memory goes back when it
    exits, before the caller reads the scene. It queues on the CAD lock as a build does, or runs
    under the caller's when the caller holds it. What it prints goes to stderr, so a caller's
    own output stays its own."""
    m = current()
    if m is not None:
        return m
    print("_machine: the scene is not this tree's; building the machine on the mesh kernel",
          file=sys.stderr)
    import subprocess
    lock = sys.modules.get("_run_lock")
    env = dict(os.environ)
    if lock is not None and lock._me is not None:
        env["HSM_NO_BUILD_LOCK"] = "1"
    else:
        env.pop("HSM_NO_BUILD_LOCK", None)      # a reader's opt-out is not the build's
    subprocess.run([sys.executable, str(_HERE.parent / "meshcad" / "run.py"),
                    str(_ML / "enclosure_assembly.py")],
                   cwd=_ROOT, env=env, stdout=2, check=True)
    return load()
