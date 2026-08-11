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
Scene = namedtuple("Scene", "id title roots parts flip also cam up zoom look note")

# WHAT THE CAMERA LOOKS AT IS THE ROOTS AND NOT THE SCENE. A run reaching out of a unit — the
# carb riser leaves this box entirely — drags the whole scene's bounding box after it and puts
# the piece off in a corner of its own picture. The pieces the unit is built ON are what the
# picture is of, so their box is what is aimed at, taken at render time off the placed solids.
#
# `look` says WHERE in that box. "centre" for a piece a unit is built INSIDE; "crown" for one
# a unit is built ON TOP OF, which aims at its own upper face — the cold core is 268 mm of
# closed foam under a lid that carries everything, and a camera pointed at its middle is
# pointed at the part of it with nothing to see.

# `parts` DRAWS PART OF A ROOT. The cold core is one solid in the machine — `foam-assembly` —
# and the unit a person actually holds is its top cap and that cap's lid, which take their own
# foam pour and carry everything on the crown long before the shell is under them. A scene names
# the sub-solids of the root it wants and `render_scenes.cut` carries them through the root's own
# placement; the root still decides which bodies come with it.
#
# `flip` IS THE POSE THE UNIT IS WORKED IN, not a camera trick. A piece open at its ceiling is
# turned over on the bench so the open faces look up, and the picture shows the piece the way a
# hand meets it.
#
# The machine's frame: +X east, +Y aft, +Z up. A back piece is open FORWARD (−Y) at the Y seam
# and open at the Z seam it telescopes on.
SCENES = (
    Scene(
        "back-top", "Enclosure back top",
        roots=("enclosure-back-top",), parts=(), flip=((1, 0, 0), 180.0), also=(),
        cam=(0.6, -1.0, 0.5), up=(0, 0, 1), zoom=2.3, look="centre",
        note="Turned over, which is how it is worked: its ceiling is the bench and both open "
             "faces look up. Every body is on it before it goes back the other way.",
    ),
    Scene(
        "cap-lid-fill", "Foam shell top cap lid, filled",
        roots=("foam-assembly",), parts=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(),
        cam=(0.5, -0.6, 1.3), up=(0, -1, 0), zoom=2.5, look="crown",
        note="The top cap and its lid alone, poured and cleaned, the lid's outer face bare. "
             "The shell is not under it yet and nothing stands on it — this is what the next "
             "scene starts from.",
    ),
    Scene(
        "cap-lid", "Foam shell top cap lid assembly",
        roots=("foam-assembly",), parts=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(),
        cam=(0.5, -0.6, 1.3), up=(0, -1, 0), zoom=2.5, look="crown",
        note="The same cap and lid with everything that face carries: the pump bolted through, "
             "three valves pressed into their cradles, both chains and two runs strapped into "
             "printed ribs. It meets the rest of the core after all of it is on.",
    ),
    Scene(
        "back-half", "Enclosure back half",
        roots=("enclosure-back-bottom", "enclosure-back-top"), parts=(), flip=None, also=(),
        cam=(0.95, -1.0, 0.35), up=(0, 0, 1), zoom=2.45, look="centre",
        note="The two back quadrants mated, seen through the Y-seam mouth they present to the "
             "front half — the last moment anything inside is reachable.",
    ),
)

SCENE_BY_ID = {s.id: s for s in SCENES}

# The scene that shows a unit BEFORE anything mounts to it. A pair listed here is drawn from the
# same roots and differs only in what is allowed to stand on them, which is what makes the two
# pictures worth putting side by side.
BARE = {"cap-lid-fill"}

# WHICH PIECE A BODY BEARS ON — the column `MOUNTS` does not carry. It names a piece for the
# fastened and the unfastened alike: a body that lands on a slab and is fenced by what is around
# it, one hanging off the tube it splices, and one clamped through a wall by its own nut all come
# to the bench on exactly one piece, and for a picture that is the answer whatever `by` reads.
#
# A body the fastening table leaves without a parent and this table does not name is REPORTED,
# not dropped — see `holders`. The one exception is the flavour pack, whose bodies rest on their
# own spine hairpins and arrive as one folded unit of their own.
BEARS_ON = {
    # Standing on a printed floor.
    "foam-assembly": "enclosure-back-bottom",
    "compressor": "enclosure-front-bottom",
    "condenser+fan": "enclosure-front-bottom",
    # Clamped through a hole in that wall by their own nut, which is why no screw is billed for
    # them. All six of the rear wall's crossings are above the back column's Z seam.
    "bulkhead-water": "enclosure-back-top",
    "bulkhead-carb": "enclosure-back-top",
    "bulkhead-flavor-a": "enclosure-back-top",
    "bulkhead-flavor-b": "enclosure-back-top",
    "co2-inlet": "enclosure-back-top",
    "gasher-co2": "enclosure-back-top",             # made up on the CO2 inlet's inboard stub
    "display": "enclosure-front-top",               # let into that piece's own facet
    "hopper-funnel": "enclosure-front-top",         # brim on the top wall, collar forward
    # Hanging off the line they splice, on the wall that line is cradled against.
    "water-split": "enclosure-back-top",
    "flow-regulator": "enclosure-back-top",
    # Riding another body rather than a piece.
    "bpv31": "compressor",
    "fuse-clamp": "compressor",
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

    out, orphans = {}, []
    for name, by, joint in _sc.mounts():
        out[name] = by or BEARS_ON.get(name)
        if out[name] is None and joint != "pack" and name not in BEARS_ON:
            orphans.append(f"{name} ({joint})")
    if orphans:
        raise ValueError(
            "these bodies have no parent, so no scene can know whether to show them: "
            + ", ".join(sorted(orphans))
            + ". `_scorecard.MOUNTS` fastens them to nothing; name the piece each bears on in "
              "`_scenes.BEARS_ON`, or None for one that comes with the flavour pack.")
    for rid, _leg, _root, piece in _ea.TUBE_ANCHOR_SITES:
        out[f"tube-{rid}"] = piece
    for name, _section, _root, piece in _ea.BODY_ANCHOR_SITES:
        out[name] = piece
    for name, station in _cci.cap_anchors.items():
        # A run's rib holds the tube; a chain's holds the chain itself.
        out[f"tube-{name}" if station.over_face is not None else name] = "foam-assembly"
    # A RIDER GOES WHERE ITS HOST GOES — `_scorecard.RIDES`, the coils on their valves and the
    # Kamoers' rear bosses and motor cans on their heads. One purchased thing apiece, drawn as
    # several so each takes its own colour.
    for rider, host in _sc.RIDES.items():
        if rider in out and host in out:
            out[rider] = out[host]
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
        # The roots and nothing else — not even the runs their own ribs will hold, which is the
        # whole difference between this picture and the one after it.
        names = set(scene.roots) | set(scene.also)
    else:
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
