"""The machine scene, scalar document and Rust fine-model export interface.

The scene holds world-placed bodies, runs, frames, Box data and check readings.
`machine()` reads a current scene or runs the Rust assembly driver before reading it.
"""

import dataclasses
import json
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
    """Sources that decide the machine scene and its mesh reader, repo-relative.

    A tree without graph.json names the five source entry points directly.
    """
    kernel = {str(p.relative_to(_ROOT)) for p in (_HERE.parent / "meshcad").glob("*.py")}
    try:
        entry = json.loads(_GRAPH.read_text())[_WORLD]
    except (OSError, ValueError, KeyError):
        return tuple(sorted(kernel | {f"hardware/{rel}" for rel in _FALLBACK_SOURCES}))
    return tuple(sorted(kernel | {p for p in entry.get("reads", ()) if p.endswith((".py", ".rs", ".toml", "Cargo.lock"))}))


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








def document(a, taken=None, card=None, drain=None, *, solids=None, core=None) -> dict:
    """A machine document from scalar metadata and completed check readings."""
    metadata = a.get('metadata', a)
    return {
        'schema': SCHEMA,
        'taken': time.time() if taken is None else taken,
        'sources': stamps(),
        'solids': list(solids or metadata.get('solids', ())),
        'core': list(core or metadata.get('core_body_names', ())),
        'runs': metadata.get('runs', []),
        'frames': metadata.get('frames', {}),
        'box': metadata.get('box'),
        'anchors': metadata.get('anchors', {}),
        'card': card,
        'drain': drain,
    }





def write_from_fine(model, path=PATH, *, aliases, envelope, document) -> Path:
    """The physical fine export and exact foam instance as the machine's scene.

    Core interiors remain file references. Numeric members pass straight from the
    completed fine model into this archive; the scene changes their public names and
    adds the separate packing envelope and the build's scalar document.
    """
    import _machine_export

    path = Path(path).resolve()
    _machine_export.scene(model, path, aliases=aliases, envelope=envelope,
                          document=document)
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
    from _assembly_model import document
    doc = document(path)
    if doc is None or doc.get("schema") != SCHEMA or doc["sources"] != stamps():
        return None
    return load(path)


def machine():
    """Read this tree's current scene, building it through the Rust driver when stale."""
    m = current()
    if m is not None:
        return m
    print("_machine: the scene is stale; running the Rust assembly driver", file=sys.stderr)
    import subprocess
    import _run_slots
    subprocess.run([sys.executable, str(_ML / "enclosure_assembly.py")],
                   cwd=_ROOT, stdout=2, check=True, **_run_slots.subprocess_kwargs())
    return load()
