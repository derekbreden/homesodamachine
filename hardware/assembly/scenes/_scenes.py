"""The sub-assembly scenes the unit cards show — one picture per finished unit.

A SCENE IS A SUBSET OF THE MACHINE, NOT A FILE. `enclosure-back-top` with everything bolted,
pressed and strapped to it is a real thing a person holds on the bench, and no STEP in this repo
contains exactly it. So a scene names its ROOTS — the printed pieces the unit is built on — and
takes everything those roots hold, transitively, off the fastening table the machine already
keeps.

WHICH BODIES A UNIT CARRIES IS DERIVED. `_scorecard.MOUNTS` is `(body, the part that holds it,
the joint)` and is gated at every build, so a body that moves to another parent moves scenes with
it and no list here goes stale. The three anchor tables say the same thing for the bodies and
runs a printed rib holds. What is stated below is the two things that table cannot say: which
piece's FLOOR a body stands on when nothing fastens it, and where the camera goes.

A RUN JOINS A UNIT BY ITS ENDS. A length of tube belongs to the unit that holds both of its
mouths, or to the unit whose rib closes on it — which is how `fluid-14` is part of the cold
core's finished state with its far end still hanging, and how the pump's two hose stubs come
with the pump.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py          # all four
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top # one

Nothing here is committed but the PNG and its fingerprint: the scene STEPs land in `out/`, which
`.gitignore` holds, and the render runs when asked rather than on every build.
`hardware/scripts/check_scenes.py` is the cheap half — it hashes what would decide the picture
and says which scenes have moved since they were drawn, reading no geometry at all.
"""

import hashlib
import sys
from collections import namedtuple
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
for _p in (_HW / "scripts", _HW / "manifold-layout", _HW / "printed-parts" / "cold-core"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _realized                                        # noqa: E402


# --- what a scene is -------------------------------------------------------
#
# `roots` are the parts the unit is built on; everything they hold comes with them. `cam` is the
# direction from the target to the camera, so a scene looking INTO a piece through its own open
# faces points from the side those faces face. `zoom` is the distance in bounding-box radii and
# `up` the camera's own up — both handed to `tools/render/render-step-posed.js` unchanged.
Scene = namedtuple("Scene", "id title roots also cam up zoom note")

# The machine's frame: +X east, +Y aft, +Z up. A back piece is open FORWARD (−Y) at the Y seam
# and open at the Z seam it telescopes on, so a camera forward of it and off its own axis looks
# in through both.
SCENES = (
    Scene(
        "back-top", "Enclosure back top",
        roots=("enclosure-back-top",), also=(),
        cam=(0.85, -1.0, 0.45), up=(0, 0, 1), zoom=2.15,
        note="Open at the Y seam and at its own Z seam, both toward the camera — the piece as "
             "it lies on the bench with every body already on it.",
    ),
    Scene(
        "cap-lid-fill", "Foam shell top cap lid, filled",
        roots=("foam-assembly",), also=(),
        cam=(0.9, -0.75, 0.7), up=(0, 0, 1), zoom=2.0,
        note="The cold core closed and poured, its lid's outer face bare. Nothing stands on it "
             "yet — this is what the next scene starts from.",
    ),
    Scene(
        "cap-lid", "Foam shell top cap lid assembly",
        roots=("foam-assembly",), also=(),
        cam=(0.9, -0.75, 0.7), up=(0, 0, 1), zoom=2.0,
        note="The same core with everything its lid carries: the pump bolted through, the three "
             "valves pressed into their cradles, both chains and two runs strapped into printed "
             "ribs.",
    ),
    Scene(
        "back-half", "Enclosure back half",
        roots=("enclosure-back-bottom", "enclosure-back-top"), also=(),
        cam=(0.85, -1.0, 0.4), up=(0, 0, 1), zoom=2.25,
        note="The two back quadrants mated, seen through the Y-seam mouth they present to the "
             "front half — the last moment anything inside is reachable.",
    ),
)

SCENE_BY_ID = {s.id: s for s in SCENES}

# The scene that shows a unit BEFORE anything mounts to it. A pair listed here is drawn from the
# same roots and differs only in what is allowed to stand on them, which is what makes the two
# pictures worth putting side by side.
BARE = {"cap-lid-fill"}

# WHICH PIECE'S FLOOR A BODY STANDS ON — the column `MOUNTS` does not carry. Its `held` says
# "floor" and its `by` is None, because nothing FASTENS these: they bear on a printed slab and
# are fenced by what is around them. For a picture, the slab they bear on is the answer.
STANDS_ON = {
    "foam-assembly": "enclosure-back-bottom",
    "compressor": "enclosure-front-bottom",
    "condenser+fan": "enclosure-front-bottom",
}


def holders():
    """`name -> the part that holds it`, off the machine's own tables.

    Four sources, in the order a later one may correct an earlier: the fastening table, the two
    box anchor tables, and the cap's. A body named twice is named with the same parent by each —
    the regulator lies in a rib off the wall that also carries its row — so the merge is a
    reading and not a choice."""
    import _scorecard as _sc
    import enclosure_assembly as _ea
    import _cold_core_interface as _cci

    out = {}
    for name, by, _held in _sc.mounts():
        out[name] = by or STANDS_ON.get(name)
    for rid, _leg, _root, piece in _ea.TUBE_ANCHOR_SITES:
        out[f"tube-{rid}"] = piece
    for name, _section, _root, piece in _ea.BODY_ANCHOR_SITES:
        out[name] = piece
    for name, station in _cci.cap_anchors.items():
        # A run's rib holds the tube; a chain's holds the chain itself.
        out[f"tube-{name}" if station.over_face is not None else name] = "foam-assembly"
    # A COIL RIDES ITS VALVE. `pack_mounts` gives every pack body to "the pack" because no
    # printed feature fastens one, but a coil is on the valve it drives and goes wherever that
    # valve goes — which for the three on the cap is the cold core.
    for name in list(out):
        if name.startswith("valve-v-"):
            coil = name.replace("valve-", "coil-")
            if coil in out:
                out[coil] = out[name]
    return out


def held_by(root, holder_map):
    """Every body `root` carries, transitively, `root` itself included."""
    out, queue = set(), [root]
    while queue:
        node = queue.pop()
        if node in out:
            continue
        out.add(node)
        queue += [n for n, by in holder_map.items() if by == node and n not in out]
    return out


def runs_for(bodies, runs, holder_map):
    """The tube ids a unit carries: a run whose BOTH mouths stand on bodies it holds, and a run
    whose rib is one of them with its far end still hanging."""
    out = set()
    for r in runs:
        anchored = holder_map.get(f"tube-{r.id}")
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        if (anchored in bodies) or ends <= bodies:
            out.add(f"tube-{r.id}")
    return out


def members(scene, assembly):
    """Every child name of the built assembly this scene shows, bodies and tube both."""
    holder_map = holders()
    bodies = set()
    for root in scene.roots:
        bodies |= held_by(root, holder_map)
    bodies |= set(scene.also)
    if scene.id in BARE:
        bodies = set(scene.roots) | set(scene.also)
    names = bodies | runs_for(bodies, assembly.runs, holder_map)
    present = {c.name for c in assembly.children}
    missing = sorted(n for n in names if n not in present)
    if missing:
        raise ValueError(
            f"scene {scene.id!r} names {', '.join(missing)}, which the built assembly does not "
            f"place. The fastening table and the anchor tables are what this reads; a body in "
            f"one of them and not in the machine is the table to correct.")
    return sorted(names)


# --- the fingerprint -------------------------------------------------------
#
# What decides a picture is the code that builds the machine, the tables that say who holds whom,
# and this file's own camera. THE LIST OF THOSE FILES IS RECORDED WHEN THE PICTURE IS DRAWN, and
# the check re-hashes exactly that list — `docgen`'s `.sources.json` bargain, for the same reason
# it takes it.
#
# The walk itself is not the check's to take. `_realized.source_files` resolves a module name
# with `find_spec`, which imports the package a dotted name hangs off — so asking for the graph
# from a cold process loads OCP, costs seconds, and still comes back short because the paths the
# build runs under are not set up. Taken from inside the render, where every module is already
# imported, it is free and complete. So the render walks and records; the check reads and hashes.


def scene_digest(scene) -> str:
    """A name for the scene's own tuple — its roots, its camera, its framing."""
    h = hashlib.blake2b(digest_size=16)
    h.update(repr(tuple(scene)).encode())
    return h.hexdigest()


def source_map() -> dict:
    """`{repo-relative path: hash}` for every file whose text can decide any picture.

    CALLED FROM INSIDE A RENDER and nowhere else. Two roots: the module that builds the machine,
    and this one, which holds the cameras and the rule for which bodies a unit carries."""
    import enclosure_assembly

    files = set()
    for start in (enclosure_assembly.__file__, __file__):
        files |= set(_realized.source_files(start))
    out = {}
    for path in sorted(files):
        h = hashlib.blake2b(digest_size=16)
        h.update(Path(path).read_bytes())
        out[Path(path).resolve().relative_to(_HW.parent).as_posix()] = h.hexdigest()
    return out


def hash_of(rel: str) -> str | None:
    """The hash of one recorded file as it stands now, or None when it is gone."""
    try:
        h = hashlib.blake2b(digest_size=16)
        h.update((_HW.parent / rel).read_bytes())
        return h.hexdigest()
    except OSError:
        return None


def sidecar_path(png: Path) -> Path:
    return png.with_suffix(png.suffix + ".scene.json")
