"""The sub-assembly scenes the unit cards show — one picture per finished unit.

A SCENE IS A SUBSET OF THE MACHINE, NOT A FILE. `enclosure-back-top` with everything bolted,
pressed and strapped to it is a real thing a person holds on the bench, and no STEP in this repo
contains exactly it. So a scene names its ROOTS — the printed pieces the unit is built on — and
takes everything those roots hold, transitively, off the fastening table the machine already
keeps.

WHICH BODIES A UNIT CARRIES IS DERIVED. `_scorecard.MOUNTS` is `(body, the part that holds it,
the joint)` and is gated at every build, so a body that moves to another parent moves scenes with
it and no list here goes stale. The three anchor tables say the same thing for the bodies and
runs a printed rib holds. What is stated below is the four things that table cannot say: which
piece's FLOOR a body stands on when nothing fastens it, which of the bodies it holds a unit has
not got yet, which run it is carrying that the tables have given to another piece, and where the
camera goes.

A RUN JOINS A UNIT BY ITS ENDS. A length of tube belongs to the unit that holds both of its
mouths, or to the unit whose rib closes on it — which is how `fluid-14` is part of the cold
core's finished state with its far end still hanging, and how the pump's two hose stubs come
with the pump.

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py          # every one
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top # one

Nothing here is committed but the PNG and its fingerprint: the scene STEPs land in `out/`, which
`.gitignore` holds, and the render runs when asked rather than on every build.
`hardware/scripts/check_scenes.py` is the cheap half — it hashes what would decide the picture
and says which scenes have moved since they were drawn, reading no geometry at all.
"""

import hashlib
import json
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
Scene = namedtuple("Scene", "id title roots parts flip also later cam up zoom look note without",
                   defaults=(None,))

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
# `also` IS THE MIRROR OF `later` — what the unit carries and the tables give to somebody else.
# A LENGTH OF TUBE IS MADE UP ONCE, on the unit whose mouth it can reach, and it leaves that
# bench with its far end hanging: `fluid-18` is pushed into the nozzle-A union while the back top
# is open and travels the length of the machine to a valve the front half has not brought yet,
# and the three reservoir lines are pushed into the core's own cap conduits with the core still
# on its own. `runs_for` reads a run off its two mouths and its rib; the ones made up early are
# named, per scene, here. A name here the scene already derives is REPORTED.
#
# `later` IS WHAT THE PIECE HOLDS AND THE UNIT DOES NOT CARRY YET. A body named here goes with
# its piece in the finished machine — the fastening table is right about it — and arrives after
# the box is closed, through an opening in a wall: the drip tray slides east into its own
# channels through the −X wall, and the funnel drops into the hopper on nothing but its own brim
# at final staging. Neither is on the bench unit, so neither is in its picture, and whatever
# stands on one goes with it. A name here the roots do not hold is reported.
#   A RUN CAN BE LATE. The cap's lid prints a rib for `fluid-14`, so the anchor table hands that
# run to the cold core and every unit built on the core takes it — the cap and lid alone on a
# bench among them, where the run's far end is a valve on a piece nobody has brought. The rib
# leaves that bench empty and the run is made up when the core is plumbed.
#
# `without` IS ONE UNIT STATED AS ANOTHER, LESS A THIRD: the core standing open for its body pour
# is the plumbed core without everything its top cap carries. It names another scene id and takes
# that scene's members out of this one, less the roots they share. A body that moves onto the
# crown leaves this picture with it.
#
# `flip` IS THE POSE THE UNIT IS WORKED IN, not a camera trick. A piece open at its ceiling is
# turned over on the bench so the open faces look up, and the picture shows the piece the way a
# hand meets it. WHICH AXIS IT TURNS ABOUT IS WHICH WAY IT THEN FACES: the two top pieces are
# open at opposite Y faces, and each turns about the axis that leaves its own mouth toward the
# camera — the back top about Y, the front top about X. Both end up on their ceilings.
#
# The machine's frame: +X east, +Y aft, +Z up. A back piece is open FORWARD (−Y) at the Y seam
# and open at the Z seam it telescopes on; a front piece is open AFT (+Y) at that same seam, and
# at the Z seam of its own column.
SCENES = (
    Scene(
        "back-top", "Enclosure back top",
        roots=("enclosure-back-top",), parts=(), flip=((0, 1, 0), 180.0),
        # The flavour-A riser, pushed into its union from the room while this piece is open.
        # It is the longest run in the appliance and its far end is a valve on the front top,
        # which is why it is made up here rather than reached for down a closed box.
        also=("tube-fluid-18",),
        later=("drip-pan",),
        cam=(0.6, -1.0, 0.5), up=(0, 0, 1), zoom=2.7, look="centre",
        note="Turned over, which is how it is worked: its ceiling is the bench, the Z seam "
             "looks up and the Y-seam mouth faces the room — the shelf is seen from where a "
             "hand reaches it. Every body is on it before it goes back the other way, and the "
             "tray's channels stand empty.",
    ),
    Scene(
        "front-top", "Enclosure front top",
        roots=("enclosure-front-top",), parts=(), flip=((1, 0, 0), 180.0), also=(),
        later=("hopper-funnel",),
        # `zoom` is a multiple of the SCENE's own bounding radius, and nothing here leaves the
        # piece: the radius is the piece's. The elevation is what opens the two valve rows —
        # they stand one behind the other on two Y planes, and a camera down the valves' own
        # axis draws them as one row.
        #
        # THE RADIUS IS NOT THE SILHOUETTE. This piece's box is a cube and the camera looks into
        # its open corner, so the diagonal it presents runs past what a radius-fitted frame
        # holds: the fit is taken on the rendered PNG's own borders, and the frame carries the
        # facet's bottom arris with air under it.
        cam=(0.8, -1.0, 0.9), up=(0, 0, 1), zoom=4.4, look="centre",
        note="The same pose as the back top and the other half of the same box: on its ceiling, "
             "the mouth to the room. Every seat under this manifold is the piece's own "
             "material, and the hopper opening is an opening — nothing is in it yet.",
    ),
    # THE PAIR IS WORKED FLAT ON A BENCH, so the camera is a person standing over it: nearly
    # down the lid's own normal, leaned just far enough onto the near edge that a valve body and
    # the pump's can read as things standing up off the plate rather than as outlines. `up` is
    # what lays the plate across the frame instead of down it — the long axis runs to the
    # pump, and the pump goes to the top right corner, which is the whole diagonal.
    Scene(
        "cap-lid-fill", "Foam shell top cap lid, filled",
        roots=("foam-assembly",), parts=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(), later=(),
        cam=(0.35, -0.2, 1.0), up=(-1.7, 1.0, 0), zoom=2.9, look="crown",
        note="The top cap and its lid alone, poured and cleaned, the lid's outer face bare. "
             "The shell is not under it yet and nothing stands on it — this is what the next "
             "scene starts from.",
    ),
    Scene(
        "cap-lid", "Foam shell top cap lid assembly",
        roots=("foam-assembly",), parts=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(),
        # THE RIB IS PRINTED HERE AND CLOSED SOMEWHERE ELSE. `fluid-14` runs from V-F on the
        # front top down onto this lid's reservoir-A fill bore, and this plate is on a bench
        # with no manifold in the world yet — the run is made up when the core is plumbed, and
        # what leaves here is an empty channel. The anchor table cannot say that: it knows the
        # rib is the cap's and stops there.
        later=("tube-fluid-14",),
        cam=(0.35, -0.2, 1.0), up=(-1.7, 1.0, 0), zoom=2.9, look="crown",
        note="The same cap and lid with everything that face carries: the pump bolted through, "
             "three valves pressed into their cradles, both chains and one run strapped into "
             "printed ribs. It meets the rest of the core after all of it is on.",
    ),
    Scene(
        "cold-core", "Cold core, plumbed",
        roots=("foam-assembly",), parts=(), flip=None,
        # EVERY CAP CONDUIT CARRIES ITS TUBE OUT OF THIS UNIT. Two of the seven the tables
        # already give the core — `water-5` has both mouths on it and `fluid-14` lies in a rib
        # its own cap prints — and the other five are made up here with their far end hanging:
        # the gas line and the carbonated riser wait on the rear wall's bodies, the three
        # reservoir lines on valves the flavour manifold has not brought yet.
        also=("tube-carb-1", "tube-co2-2", "tube-fluid-16", "tube-fluid-24", "tube-fluid-26"),
        later=(),
        cam=(0.85, -1.0, 1.0), up=(0, 0, 1), zoom=3.25, look="centre",
        note="The core as it comes off its own bench and before the box is anywhere near it: "
             "the crown populated, and one tube standing in each of the seven cap conduits "
             "with its far end loose. The evaporator's two coppers are not among them — those "
             "are brazed with the machine built, not on this bench.",
    ),
    Scene(
        "cold-core-open", "Cold core, ready to foam",
        roots=("foam-assembly",),
        # THE THREE PIECES THAT ARE ON. The shell closed underneath by the bottom cap and its
        # lid; the top cap and its lid are a unit of their own and go down over the lines after
        # the pour, so they are not drawn at all rather than drawn empty.
        parts=("foam-shell", "foam-cap-bottom", "foam-cap-lid-bottom"),
        flip=None,
        # The same five the plumbed core is made up with, less the two whose far end is on the
        # crown — nothing on that face exists yet, so nothing routed to it does either.
        also=("tube-carb-1", "tube-co2-2", "tube-fluid-16", "tube-fluid-24", "tube-fluid-26"),
        later=(),
        # THIS IS THE PLUMBED CORE LESS ITS OWN CAP ASSEMBLY. The pump, the three valves, both
        # chains and every run between them stand on a plate that is not down yet, and stating
        # it that way is what keeps the two pictures one reading apart.
        without="cap-lid",
        cam=(0.85, -1.0, 1.0), up=(0, 0, 1), zoom=3.25, look="centre",
        note="The shell closed underneath, everything that goes inside inside it, and every "
             "line standing up out of the open mouth. This is what the body pour goes into — "
             "the top cap comes down over these lines afterwards, and the crown is populated "
             "on a bench of its own before it does.",
    ),
    Scene(
        "hopper-drain", "Hopper basin drain stub",
        roots=("hopper-funnel",), parts=(), flip=((1, 0, 0), 180.0), also=(),
        # The union is on the far end of the stub and is the joint that PARTS: it stays in the
        # machine when the basin comes out, so it is not on the bench with this one.
        later=("hopper-drain-union",),
        # THE BRIM IS WHAT THE FRAME HAS TO HOLD, not the spout the card is about. Inverted, the
        # basin is a 173 mm plate with a 20 mm joint standing on the middle of it, and `crown`
        # aims at the plate's own face — so the distance is set by the plate's diagonal and the
        # subject comes out small inside it. Fitted on the PNG's borders.
        cam=(0.55, -0.85, 0.9), up=(0, 0, 1), zoom=4.0, look="crown",
        note="The basin inverted, which is how the joint is made: the brim is the bench and the "
             "spout stands up where two hands reach it. The stub is in as far as it goes and the "
             "band is on the land between its two shoulders — nothing of the stub shows below "
             "the spout's face, because what is below that face is the collet it pushes into.",
    ),
    Scene(
        "back-half", "Enclosure back half",
        roots=("enclosure-back-bottom", "enclosure-back-top"), parts=(), flip=None,
        # The four that cross the Y seam: the flavour-A riser off the rear wall's own union,
        # and the three reservoir lines standing in the core's cap. All four are made up on
        # this half and all four leave it hanging, for the front half's valves to take.
        also=("tube-fluid-16", "tube-fluid-18", "tube-fluid-24", "tube-fluid-26"),
        later=("drip-pan",),
        # High enough over the box to see down into the mouth AND across the top wall, which is
        # how the half is looked at with the front one still off the bench: the seam faces the
        # room and everything the front half must reach is under the eye at once.
        cam=(0.95, -1.1, 1.4), up=(0, 0, 1), zoom=3.2, look="centre",
        note="The two back quadrants mated, seen through the Y-seam mouth they present to the "
             "front half — the last moment anything inside is reachable. Four runs hang out of "
             "that mouth for the front half to take. The tray is not in yet: it goes east into "
             "its channels through the −X wall, with the box standing.",
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
    # The basin's disconnect, all of it on the spout the basin carries: the stub and the clamp
    # go to the dishwasher with it, and the union is on the stub's far end.
    "hopper-drain-stub": "hopper-funnel",
    "hopper-drain-clamp": "hopper-funnel",
    "hopper-drain-union": "hopper-funnel",
    # Hanging off the line they splice, on the wall that line is cradled against.
    "water-split": "enclosure-back-top",
    "flow-regulator": "enclosure-back-top",
    # Riding another body rather than a piece.
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
        # TWO PIECES CLOSING ON ONE BODY PUT IT IN NEITHER'S UNIT. `_scorecard.MOUNTS` gives such
        # a body a tuple, and where it stands is `BEARS_ON` — the cold core is fastened by the
        # front-bottom's blocks and the back-top's brackets and sits on the back-bottom's slab.
        out[name] = (by if isinstance(by, str) else None) or BEARS_ON.get(name)
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


def held_by(root, holder_map, stop=()):
    """Every body `root` carries, transitively, `root` itself included.

    A body in `stop` is not carried and neither is anything standing on it — the walk turns
    round there. That is one reading and not two: the moisture plate lies in the drip tray, so
    a unit the tray has not reached has no plate in it either."""
    out, queue, stop = set(), [root], set(stop)
    while queue:
        node = queue.pop()
        if node in out or node in stop:
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


def named(scene, runs):
    """Every name this scene shows, bodies and tube both, off the tables and the drawn runs.

    A doc driver has the runs and the tables and no machine; a render has all three. This is the
    half both can ask for — see `members`."""
    holder_map = holders()
    bodies = set()
    for root in scene.roots:
        bodies |= held_by(root, holder_map, scene.later)
    # WHAT IS HELD BACK IS SOMETHING THE PIECE HOLDS. `later` is written against the fastening
    # table, and a body that leaves that piece — or is renamed — leaves the row naming nothing.
    if scene.later:
        carried = set()
        for root in scene.roots:
            carried |= held_by(root, holder_map)
        adrift = sorted(n for n in scene.later if n not in carried)
        if adrift:
            raise ValueError(
                f"scene {scene.id!r} holds back {', '.join(adrift)}, which nothing in "
                f"{', '.join(scene.roots)} carries. `later` names a body the piece DOES hold "
                f"and the unit has not got yet; a body that has moved to another piece leaves "
                f"this row with the piece it moved to.")
    if scene.id in BARE:
        # The roots and nothing else — not even the runs their own ribs will hold, which is the
        # whole difference between this picture and the one after it.
        derived = set(scene.roots)
    else:
        derived = bodies | runs_for(bodies, runs, holder_map)
    # `later` reaches the run pass too — a rib alone gives a run to the unit its rib is on.
    derived -= set(scene.later)
    if scene.without:
        other = SCENE_BY_ID[scene.without]
        if other.without:
            raise ValueError(
                f"scene {scene.id!r} is {scene.without!r} less its own {other.without!r}. "
                f"State this scene against a unit that is drawn whole.")
        gone = set(named(other, runs)) - set(scene.roots)
        surplus = sorted(gone - derived)
        if surplus:
            raise ValueError(
                f"scene {scene.id!r} takes {scene.without!r} out of itself and does not carry "
                f"{', '.join(surplus)} to take. The two are no longer built on the same thing.")
        derived -= gone
    # WHAT IS ADDED IS SOMETHING THE TABLES GIVE AWAY. A row that names what the scene already
    # takes is a row saying nothing, and the day the tables change their mind about it nothing
    # here would notice.
    idle = sorted(n for n in scene.also if n in derived)
    if idle:
        raise ValueError(
            f"scene {scene.id!r} names {', '.join(idle)} in `also`, which it already draws. "
            f"`also` is for what the unit carries and the tables hand to another piece — a "
            f"name the scene derives on its own belongs to the tables, not to this row.")
    return sorted(derived | set(scene.also))


def members(scene, assembly):
    """`named`, held against the machine that has to place every one of them."""
    names = named(scene, assembly.runs)
    present = {c.name for c in assembly.children}
    missing = sorted(n for n in names if n not in present)
    if missing:
        raise ValueError(
            f"scene {scene.id!r} names {', '.join(missing)}, which the built assembly does not "
            f"place. The fastening table and the anchor tables are what this reads; a body in "
            f"one of them and not in the machine is the table to correct.")
    return names


# --- the fingerprint -------------------------------------------------------
#
# What decides a picture is the code that builds the machine, the tables that say who holds whom,
# and this file's own camera. THE LIST OF THOSE FILES IS RECORDED WHEN THE PICTURE IS DRAWN, and
# the check re-hashes exactly that list — `docgen`'s own bargain, for the same reason
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
        out[Path(path).resolve().relative_to(_HW.parent).as_posix()] = _realized.code_digest(path)
    return out


def hash_of(rel: str) -> str | None:
    """The name of what one recorded file computes now, or None when it is gone."""
    return _realized.code_digest(_HW.parent / rel)


def sidecar_path(png: Path) -> Path:
    return png.with_suffix(png.suffix + ".scene.json")


def digest_of(path: Path) -> str | None:
    """The hash of a file's bytes, or None when it is not there."""
    try:
        h = hashlib.blake2b(digest_size=16)
        h.update(Path(path).read_bytes())
        return h.hexdigest()
    except OSError:
        return None


def held_record(png: Path) -> dict:
    """What the last render wrote beside `png`, or an empty record."""
    try:
        return json.loads(sidecar_path(png).read_text())
    except (OSError, ValueError):
        return {}


# --- the picture itself ----------------------------------------------------
#
# THE SOURCES SAY WHAT WOULD DRAW A PICTURE; THIS SAYS WHICH PICTURE WAS DRAWN.


def image_fingerprint(png: Path) -> dict:
    """`{w, h, bytes, sha}` for a drawn picture."""
    raw = png.read_bytes()
    h = hashlib.blake2b(digest_size=16)
    h.update(raw)
    # A PNG's IHDR is fixed: eight bytes of signature, a four-byte length, `IHDR`, then the two
    # dimensions as big-endian u32.
    w = int.from_bytes(raw[16:20], "big")
    ht = int.from_bytes(raw[20:24], "big")
    return {"w": w, "h": ht, "bytes": len(raw), "sha": h.hexdigest()}
