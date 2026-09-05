"""Every picture the assembly cards show, and what each one is OF.

TWO KINDS OF SUBJECT, ONE MECHANISM. A SCENE is a set of bodies the machine places — a finished
sub-assembly, or a group a card names together. A PART SHOT is one STEP the tree already keeps.
Both are drawn by `render_scenes.py` through `tools/render/render-step-posed.js`, and both leave
a `.scene.json` beside the PNG holding the digest of the exact geometry drawn — the file the page
built its triangles from, which is the scene's mesh payload and the part shot's STEP. So a part
moving under its own picture is a fact the tree holds rather than something a reader has to
notice.

A SCENE IS A SUBSET OF THE MACHINE, NOT A FILE. `enclosure-back-top` with everything bolted,
pressed and zip-tied to it is a real thing a person holds on the bench, and no STEP in this repo
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

    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py           # every one
    tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py back-top  # one

A scene leaves three things in the tree: the PNG, its fingerprint, and the `.glb` /3d opens. The
scene STEPs land in `out/`, which `.gitignore` holds. `//:render-scenes` runs the render when the
assembly's STEP moves. `web/contracts/parts-tree.js` claims this whole directory as tooling — a
scene is a picture of a group of bodies rather than a body — so /3d draws no card for one and a
scene added here is a scene added here alone.
"""

import hashlib
import json
import sys
from collections import namedtuple
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
for _p in (_HW / "scripts", _HW / "manifold-layout", _HW / "cold-core-layout",
           _HW / "printed-parts" / "cold-core"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))



# --- what a scene is -------------------------------------------------------
#
# `roots` are the parts the unit is built on; everything they hold comes with them. `cam` is the
# direction from the target to the camera, so a scene looking INTO a piece through its own open
# faces points from the side those faces face. `zoom` is the distance in bounding-box radii and
# `up` the camera's own up — both handed to `tools/render/render-step-posed.js` unchanged.
Scene = namedtuple("Scene", "id title roots inner flip also later cam up zoom look note without",
                   defaults=(None,))

# HOW MUCH OF THE CORE A PICTURE WANTS. `manifold-layout/enclosure_assembly` stands the core's
# own bodies — the shell and its caps AND the carbonator, the coil, both reservoirs, every
# fitting, the sensing and the eight lines among them — so a scene can draw as much or as little
# of the stack as its bench step has reached. `cold-core-layout/cold_core_assembly` is the same
# stack in the shell's own frame, and its `one-core` gate holds the two agreeing about it.
#
# `inner` NAMES WHICH OF THOSE BODIES A SCENE DRAWS, in place of `INNER_ROOT`. `INNER_ALL` takes
# every one — the core on a bench with its lid off is a picture of what is inside it, and no list
# of 63 names belongs in this file — and `INNER_FOAM` takes the closed unit.
INNER_ALL = "*"

# THE NAME THE CORE IS ONE BODY UNDER. Nothing is exported by it: the machine's card measures the
# pack against the envelope, its port table hangs off it, and `inner` bodies are drawn in its
# place. A scene naming it is a scene that has not said which of the core it wants.
INNER_ROOT = "foam-assembly"

#: WHERE THE MACHINE HANGS A BODY OF THE CORE. `enclosure_assembly` stands them in a `cold-core`
#: sub-assembly, so a leaf of it is named for the branch it hangs on. THE TABLES BELOW NAME THE
#: CORE'S BODIES AS THE CORE DOES — they are rows about the core — and `inner_of` is the one
#: place that turns a row into the name the machine holds it under. One direction, one place:
#: nothing anywhere takes a machine name apart again.
INNER_ROOT_HELD = "cold-core/"

# THE FOAM ITSELF, as the core names its five pieces. `foam-assembly.step` is a compound of
# exactly these, so a scene drawing them draws the closed unit — with each piece under its own
# name. A unit that carries the core without being a picture of its insides takes these: on a
# bench the core arrives foamed and shut.
INNER_FOAM = ("foam-shell", "foam-cap-top", "foam-cap-lid-top",
              "foam-cap-bottom", "foam-cap-lid-bottom")

_COLD_CARD = _HW / "cold-core-layout" / "cold-core-assembly.scorecard.json"


def core_names() -> tuple:
    """Every body the cold core's own assembly places, off the card written beside its STEP.

    A doc driver has the card and no machine; `render_scenes` builds the assembly for the solids.
    Same bargain `_facts.json` takes for the appliance."""
    card = json.loads(_COLD_CARD.read_text())
    return tuple(sorted(card["bodies"]
                        + [f"line-{bend['id']}" for bend in card["bends"]]))


def inner_of(scene) -> tuple:
    """The cold-core bodies this scene draws, named the way the machine holds them.

    The rows above name them as the core's own card does, because that is what they are rows
    about. The machine hangs them under `INNER_ROOT_HELD`, and this is the one place a row's
    name becomes the machine's — after it, nothing takes one apart again."""
    if not scene.inner:
        return ()
    named = core_names() if scene.inner == INNER_ALL else tuple(scene.inner)
    return tuple(f"{INNER_ROOT_HELD}{n}" for n in named)


def crossings(runs) -> dict:
    """`cold-core/line-<conduit>` -> the `tube-<run>` that is the rest of the same length of tube.

    A CAP CONDUIT IS WHERE ONE MODEL HANDS A LINE TO THE OTHER. `_internal_routes` draws to the
    face the bore opens on, and the machine's own run starts on that same face — at the port both
    of them call `foam-assembly.<conduit>`. The two halves are joined by a name already, so this
    reads the pair off the runs rather than keeping a table of them.

    THE CORE'S HALF IS NAMED THE WAY THE MACHINE HOLDS IT — under `INNER_ROOT_HELD`, the path a
    body inside a sub-assembly carries. Every caller holds this key against `named` or `members`,
    which speak that path, so the pair is stated in it here and nowhere else."""
    import _cold_core_interface as _cci
    out = {}
    for r in runs:
        for end in (r.frm, r.to):
            part, _dot, mouth = end.partition(".")
            if part == "foam-assembly" and mouth in _cci.cap_conduits:
                out[f"{INNER_ROOT_HELD}line-{mouth}"] = f"tube-{r.id}"
    return out

# WHAT THE CAMERA LOOKS AT IS THE ROOTS AND NOT THE SCENE. A run reaching out of a unit — the
# carb riser leaves this box entirely — drags the whole scene's bounding box after it and puts
# the piece off in a corner of its own picture. The pieces the unit is built ON are what the
# picture is of, so their box is what is aimed at, taken at render time off the placed solids.
#
# `look` says WHERE in that box. "centre" for a piece a unit is built INSIDE; "crown" for one
# a unit is built ON TOP OF, which aims at its own upper face — the cold core is 268 mm of
# closed foam under a lid that carries everything, and a camera pointed at its middle is
# pointed at the part of it with nothing to see.

# `inner` DRAWS THE CORE'S OWN BODIES IN PLACE OF THE MACHINE'S ONE SOLID. The unit a person
# holds on a bench is the top cap and that cap's lid, or the shell with everything standing in
# it — neither is a body `enclosure_assembly` has. `render_scenes.cut` stands them under the
# location that machine seats `INNER_ROOT` with; the root still decides which of the MACHINE's
# bodies come with it, so a cap that carries a pump carries it either way.
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
# the box is closed, through an opening in a wall: the ASSE drip pan slides east into its own
# sleeve through the −X wall, and the funnel drops into its opening on nothing but its own brim
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
        roots=("enclosure-back-top",), inner=(), flip=((0, 1, 0), 180.0),
        # The flavour-A riser, pushed into its union from the room while this piece is open.
        # It is the longest run in the appliance and its far end is a valve on the front top,
        # which is why it is made up here rather than reached for down a closed box.
        also=("tube-fluid-18",),
        later=("asse-drip-pan",),
        cam=(0.6, -1.0, 0.5), up=(0, 0, 1), zoom=2.7, look="centre",
        note="Turned over, which is how it is worked: its ceiling is the bench, the Z seam "
             "looks up and the Y-seam mouth faces the room — the +X wall is seen from where a "
             "hand reaches it. Every body is on it before it goes back the other way, and the "
             "tray's sleeve stands empty.",
    ),
    Scene(
        "front-top", "Enclosure front top",
        roots=("enclosure-front-top",), inner=(), flip=((1, 0, 0), 180.0), also=(),
        # The funnel drops into its throat with the enclosure upright.
        later=("funnel",),
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
             "material, including the integral collet plate and its tee bores. The two openings "
             "stand empty: one "
             "takes the funnel and the front bay takes the pump cartridge both pumps ride, and "
             "each is filled with the box standing.",
    ),
    # THE UNIT THAT FILLS THAT BAY, rooted on its two printed pieces: the full-height lower
    # cradle and the small top clamp. It is worked upright, the same way it stands in the bay,
    # because both complete pumps drop along +Z into the cradle before the clamp comes down.
    Scene(
        "pump-cartridge", "Pump cartridge",
        roots=("enclosure-pump-cartridge", "enclosure-pump-cap"), inner=(),
        flip=None, also=(), later=(),
        cam=(0.9, -0.75, 0.55), up=(0, 0, 1), zoom=2.9, look="centre",
        note="Upright on its lower cradle, the same pose in which it is assembled and installed: "
             "both complete pumps drop through straight wells until their stamped brackets bear "
             "on the cradle, then the small top clamp lowers over both octagonal bosses and takes "
             "two screws. Nothing on this unit is screwed to the box — the four tube stubs, "
             "gripped in the anchor tees, are the whole of what holds it in.",
    ),
    # THE PAIR IS WORKED FLAT ON A BENCH, so the camera is a person standing over it: nearly
    # down the lid's own normal, leaned just far enough onto the near edge that a valve and
    # the pump's can read as things standing up off the plate rather than as outlines. `up` is
    # what lays the plate across the frame instead of down it — the long axis runs to the
    # pump, and the pump goes to the top right corner, which is the whole diagonal.
    Scene(
        "cap-lid-fill", "Foam shell top cap lid, filled",
        roots=("foam-assembly",), inner=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(), later=(),
        cam=(0.35, -0.2, 1.0), up=(-1.7, 1.0, 0), zoom=2.9, look="crown",
        note="The top cap and its lid alone, poured and cleaned, the lid's outer face bare. "
             "The shell is not under it yet and nothing stands on it — this is what the next "
             "scene starts from.",
    ),
    Scene(
        "cap-lid", "Foam shell top cap lid assembly",
        roots=("foam-assembly",), inner=("foam-cap-top", "foam-cap-lid-top"),
        flip=None, also=(),
        # THE RIB IS PRINTED HERE AND CLOSED SOMEWHERE ELSE. `fluid-14` runs from V-F on the
        # front top down onto this lid's reservoir-A fill bore, and this plate is on a bench
        # with no manifold in the world yet — the run is made up when the core is plumbed, and
        # what leaves here is an empty channel. The anchor table cannot say that: it knows the
        # rib is the cap's and stops there.
        later=("tube-fluid-14",),
        cam=(0.35, -0.2, 1.0), up=(-1.7, 1.0, 0), zoom=2.9, look="crown",
        note="The same cap and lid with everything that face carries: the pump bolted through, "
             "three valves pressed into their cradles, both chains and one run zip-tied into "
             "printed ribs. It meets the rest of the core after all of it is on.",
    ),
    Scene(
        "cold-core", "Cold core, plumbed",
        roots=("foam-assembly",), inner=INNER_ALL, flip=None,
        also=(), later=(),
        cam=(0.85, -1.0, 1.0), up=(0, 0, 1), zoom=3.25, look="centre",
        note="The core as it comes off its own bench and before the box is anywhere near it: "
             "the crown populated, and one tube standing in each of the seven cap conduits "
             "with its far end loose. The evaporator's two coppers are not among them — those "
             "are brazed with the machine built, not on this bench.",
    ),
    Scene(
        "cold-core-open", "Cold core, ready to foam",
        roots=("foam-assembly",), inner=INNER_ALL, flip=None, also=(), later=(),
        # THE PLUMBED CORE LESS ITS OWN CAP ASSEMBLY. What SA-04 stands on that plate — the pump,
        # three valves, both chains and every run between them — and the plate and lid with it.
        without="cap-lid",
        # Over the open mouth, which is what there is to see: the cavities the shot has to find,
        # both reservoirs standing in their pockets, and every line standing out of the top.
        cam=(0.7, -0.9, 1.5), up=(0, 0, 1), zoom=3.2, look="centre",
        note="The shell closed underneath, the carbonator and both reservoirs standing in it, and "
             "every line standing out of the open top. This is what the body pour goes into. "
             "Each line runs from the fitting it is made up on to the cap face, so what stands "
             "proud of this rim is the cap's own thickness and the cap comes down over it.",
    ),
    Scene(
        "funnel-drain", "Funnel drain stub",
        roots=("funnel",), inner=(), flip=((1, 0, 0), 180.0), also=(),
        # The union is on the far end of the stub and is the joint that PARTS: it stays in the
        # machine when the funnel comes out, so it is not on the bench with this one.
        later=("funnel-drain-union",),
        # THE BRIM IS WHAT THE FRAME HAS TO HOLD, not the spout the card is about. Inverted, the
        # funnel is a 173 mm plate with a 20 mm joint standing on the middle of it, and `crown`
        # aims at the plate's own face — so the distance is set by the plate's diagonal and the
        # subject comes out small inside it. Fitted on the PNG's borders.
        cam=(0.55, -0.85, 0.9), up=(0, 0, 1), zoom=4.0, look="crown",
        note="The funnel inverted, which is how the joint is made: the brim is the bench and the "
             "spout stands up where two hands reach it. The stub is in as far as it goes and the "
             "band is on the land between its two shoulders — nothing of the stub shows below "
             "the spout's face, because what is below that face is the collet it pushes into.",
    ),
    Scene(
        "back-half", "Enclosure back half",
        roots=("enclosure-back-bottom", "enclosure-back-top"), inner=INNER_FOAM, flip=None,
        # The four that cross the Y seam: the flavour-A riser off the +Y wall's own union,
        # and the three reservoir lines standing in the core's cap. All four are made up on
        # this half and all four leave it hanging, for the front half's valves to take.
        also=("tube-fluid-16", "tube-fluid-18", "tube-fluid-24", "tube-fluid-26"),
        later=("asse-drip-pan",),
        # High enough over the box to see down into the mouth AND across the top wall, which is
        # how the half is looked at with the front one still off the bench: the seam faces the
        # room and everything the front half must reach is under the eye at once.
        cam=(0.95, -1.1, 1.4), up=(0, 0, 1), zoom=3.2, look="centre",
        note="The two back quadrants mated, seen through the Y-seam mouth they present to the "
             "front half — the last moment anything inside is reachable. Four runs hang out of "
             "that mouth for the front half to take. The tray is not in yet: it goes east into "
             "its sleeve through the −X wall, with the box standing.",
    ),
    # TWO UNITS THAT ARE NOT BUILT ON A PIECE. Both of these are a group of bodies a card names
    # together — the refrigeration stratum, the power column — and neither is a printed part or a
    # file. `roots` takes the bodies themselves and the fastening table brings what hangs off
    # them, which is how the compressor arrives carrying its own cutoff and clamp.
    Scene(
        "en04-stratum", "The refrigeration stratum",
        roots=("compressor", "condenser+fan"), inner=(), flip=None, also=(), later=(),
        # Off the front-left corner and above, which is the corner the pair presents to a
        # bench: the can's own flank, the block beside it, and the joint drawn between them.
        cam=(-0.9, -1.0, 0.55), up=(0, 0, 1), zoom=3.0, look="centre",
        note="Compressor west, condenser + fan east, closed on the shell's own tangent with "
             "the discharge joint made on that line — the pair as it stands on the floor slab.",
    ),
    Scene(
        "en06-column", "The power column",
        roots=("psu", "pcba", "relay-1", "relay-2", "ground-stack"),
        inner=(), flip=None, also=(), later=(),
        # Square on to the +X flank the column stands down, from inside the box.
        cam=(-1.0, -0.25, 0.35), up=(0, 0, 1), zoom=2.8, look="centre",
        note="Down the +X flank — the PSU aft, the main board forward of it, both relays "
             "and the ground stack, every mounting plane on the one seat.",
    ),
)

SCENE_BY_ID = {s.id: s for s in SCENES}


# --- a part on its own ------------------------------------------------------
#
# A SCENE IS A SUBSET OF THE MACHINE; A PART SHOT IS ONE STEP. The card that names a single part
# shows that part with nothing standing on it, so its subject is a FILE rather than a set of
# bodies — and the file is the one the tree already keeps for that part. `Scene` cannot say that:
# five of these are not bodies the machine places at all, and `members` is right to raise on a
# name no assembly has.
#
# WHAT IT SHARES WITH A SCENE IS THE WHOLE POINT. Same renderer, same sidecar, same `geometry`
# digest of the exact bytes drawn — so a part shot goes stale the way a scene does, which is to
# say it does not: `render_scenes` redraws it when its STEP moves and `//:render-scenes` declares
# the picture it wrote.
#
# `id` IS THE CARD'S OWN FILE NAME. `img/<id>.png` is what the card's `<img src>` already reads,
# so a part shot takes over the drawing of a file that is already there rather than adding one
# beside it under a name nobody references.
#
# `step` is repo-relative. `cam`, `up` and `zoom` reach `render-step-posed.js` unchanged; it
# targets the subject's own bounding-box centre and sizes the frame off its own radius, so an
# entry wanting a plain three-quarter view states no pose at all.
#
# `solid` IS WHETHER THE WALLS ARE OPAQUE, and it is the one thing here a picture can get wrong
# without failing. A part a hand holds is drawn solid, the way the hand meets it. A part whose
# card is about what is INSIDE it — the packed machine, a shroud that is a cup — is drawn
# through, and the viewer ghosts it.
Part = namedtuple("Part", "id title step cam up zoom solid",
                  defaults=((1.0, 1.0, 1.0), (0, 0, 1), 3.0, True))

#   THREE OF THESE DRAW ONE STEP. `enclosure-back-top` is the wall a card looks at from outside,
# the wall another looks along for its bosses, and the wall a third looks into for its wells —
# one piece, three things to teach, three poses. What makes them three pictures is the camera,
# which is why the camera is in the row.
PARTS = (
    Part("en01-shell", "Enclosure, six pieces",
         "hardware/printed-parts/enclosure/enclosure/enclosure.step",
         cam=(0.75, -1.0, 0.55)),
    # The bare wall from OUTSIDE — the union bores in a rectangle, the C14 window under them.
    Part("en02-y-wall", "Enclosure back top, +Y wall",
         "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step",
         cam=(0.35, 1.0, 0.3)),
    Part("en03-compressor", "Compressor",
         "hardware/reference/compressor/compressor.step"),
    Part("en05-coldcore", "Cold core",
         "hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step",
         cam=(0.8, -1.0, 0.5)),
    Part("en08-asse-drip-pan", "ASSE drip pan",
         "hardware/printed-parts/enclosure/asse-drip-pan/asse-drip-pan.step",
         cam=(0.75, -1.0, 0.55)),
    Part("en09-funnel", "Funnel",
         "hardware/printed-parts/zone-c/funnel/funnel.step"),
    # Along the +X wall's INNER face, which is the face the bosses reach in off — so the camera
    # stands across the box, and the walls between it and them are drawn through.
    Part("pc01-wall-bosses", "Enclosure back top, +X wall bosses",
         "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step",
         cam=(-1.0, -0.35, 0.3), zoom=2.6, solid=False),
    # The wells are pockets in the wall itself, seen from the box's own side of it.
    Part("wago-column", "Enclosure back top, Wago wells",
         "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step",
         cam=(-1.0, 0.45, 0.25), zoom=2.2, solid=False),
    Part("asse1022-chain", "ASSE 1022 chain, made up",
         "hardware/reference/asse1022-assembly/asse1022-assembly.step"),
    # Through the walls: a pack is what is inside it.
    Part("ip03-manifold-pack", "Flavour manifold, packed",
         "hardware/manifold-layout/manifold-layout.step", solid=False),
    Part("fu02-faucet", "Faucet, made up",
         "hardware/faucet-layout/faucet-assembly.step"),
    # Through the walls: the two pieces and the seam between them.
    Part("fu05-shell", "Faucet shell, two pieces",
         "hardware/printed-parts/faucet/faucet-shell/faucet-shell.step", solid=False),
    # The tee in the attitude the split stands in — the run fore-and-aft and the branch
    # rolled to look down. `water_split._TURNS` is that turn, so the camera is the default
    # one carried back through it rather than a second copy of the fitting on disk.
    Part("water-split", "Tap-water split",
         "hardware/reference/tee-connector/tee-connector.step",
         cam=(-1.0, -1.0, 1.0), up=(-1, 0, 0)),
    Part("coil-mandrel", "Coil mandrel",
         "hardware/printed-parts/cold-core/coil-mandrel/coil-mandrel.step"),
    # 185 mm of plug, 8.5 across. NEARLY DOWN ITS OWN AXIS is the only view of it that is not a
    # line: what there is to see is the section, and the length foreshortens behind it.
    Part("copper-plug", "Copper plug, port column",
         "hardware/printed-parts/cold-core/copper-plugs/copper-plug-port.step",
         cam=(0.22, -0.28, 1.0), zoom=2.2),
    # Through the walls: the card is about the pack, and this box is black PETG.
    Part("enclosure-assembly", "The machine, packed",
         "hardware/manifold-layout/enclosure-assembly.step",
         cam=(0.85, -1.0, 0.5), solid=False),
    # Through the walls: the stack IS the thing — top cap, shell, bottom cap, lids outermost.
    Part("foam-assembly-stack", "Cold core, the stack",
         "hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step",
         cam=(1.0, -0.55, 0.35), solid=False),
    Part("foam-cap-top", "Cold core, top cap",
         "hardware/printed-parts/cold-core/foam-cap/foam-cap-top.step"),
    # Through the walls: the cavity is what this picture is of.
    Part("foam-shell-cavity", "Cold core shell, the cavity",
         "hardware/printed-parts/cold-core/foam-shell/foam-shell.step", solid=False),
    Part("pcba-assembly", "Controller board in its tray",
         "hardware/printed-parts/electronics/pcba-tray/pcba-assembly.step"),
    # Through the walls: what the shroud is, is the bore and the lip inside it.
    Part("prv-shroud", "PRV shroud",
         "hardware/printed-parts/cold-core/prv-shroud/prv-shroud.step", solid=False),
    Part("reservoir-body", "Flavour reservoir",
         "hardware/printed-parts/cold-core/reservoir/reservoir-left.step"),
    Part("reservoir-cap", "Flavour reservoir cap",
         "hardware/printed-parts/cold-core/reservoir/reservoir-cap-left.step"),
)

PART_BY_ID = {p.id: p for p in PARTS}


def part_digest(part) -> str:
    """A name for a part shot's own tuple — its subject and its pose."""
    h = hashlib.blake2b(digest_size=16)
    h.update(repr(tuple(part)).encode())
    return h.hexdigest()


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
    # them. All five of the +Y wall's crossings are above the back column's Z seam.
    "bulkhead-water": "enclosure-back-top",
    "bulkhead-carb": "enclosure-back-top",
    "bulkhead-flavor-a": "enclosure-back-top",
    "bulkhead-flavor-b": "enclosure-back-top",
    "co2-inlet": "enclosure-back-top",
    "display": "enclosure-front-top",               # let into that piece's own facet
    "display-gasket": "enclosure-front-top",         # in the same inset, under the plate's lap
    "funnel": "enclosure-front-top",         # brim on the top wall, collar forward
    # The funnel's disconnect, all of it on the spout the funnel carries: the stub and the clamp
    # go to the dishwasher with it, and the union is on the stub's far end.
    "funnel-drain-stub": "funnel",
    "funnel-drain-clamp": "funnel",
    "funnel-drain-union": "funnel",
    # Hanging off the line they splice, on the wall that line is cradled against.
    "water-split": "enclosure-back-top",
    "flow-regulator": "enclosure-back-top",
    # A hop inboard of the CO2 inlet and a hop short of the regulator, on that same wall.
    "gasher-co2": "enclosure-back-top",
    # Riding another body rather than a piece.
    "fuse-clamp": "compressor",
}


def holders():
    """`name -> the part that holds it`, off the machine's own tables.

    Five sources, in the order a later one may correct an earlier: the fastening table, the two
    box anchor tables, the cap's, and the pack's own barb runs. A body named twice is named with
    the same parent by each — the regulator lies in a rib off the wall that also carries its row
    — so the merge is a reading and not a choice."""
    import _scorecard as _sc
    import enclosure_assembly as _ea
    import _cold_core_interface as _cci
    import manifold_layout as _ml

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
    # A TUBE PUSHED OVER A BARB GOES ON WITH THE PUMP AND COMES OFF WITH IT, and no table above
    # holds one: `manifold_layout` draws these four inside the pack, one per anchor tee, from the
    # barb's own collet plane to the tee's branch. `BARB_OF` names the pump each stands on. A
    # stub is made up on the pump cartridge's own bench, threads the collet plate's hole as the
    # pump cartridge goes home, and is drawn back out of the tee when the pump cartridge is pulled — so it
    # stands on the head whose barb grips it and goes wherever that head goes.
    pump_at = {x: name for name, x in _ml.PUMPS.items()}
    for cid, _frm, _to, how in _ml.SEGMENTS:
        if how in _ml.BARB_OF:
            out[f"tube-fluid-{cid}"] = f"{pump_at[_ml.BARB_OF[how][0]]}-head"
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
    round there. That is one reading and not two: the moisture plate lies in the ASSE drip pan, so
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
        carried |= set(inner_of(scene))
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
    # THE CORE'S OWN BODIES STAND WHERE THE MACHINE'S ONE SOLID WOULD. `roots` still decided
    # which of the machine's bodies this unit carries; what it names is drawn from the frame
    # that has the pieces. What they stand in place of is `INNER_ROOT` — the one name the
    # machine carried the whole core under — and not whatever this scene happens to be rooted
    # on: a scene rooted on two box halves carries the core because a half holds it, and
    # replacing its roots would take the box out of its own picture.
    inner = set(inner_of(scene))
    if inner:
        derived.discard(INNER_ROOT)
        derived |= inner - set(scene.later)
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
    names = derived | set(scene.also)
    # ONE LENGTH OF TUBE IS ONE LENGTH OF TUBE. A unit drawing the half inside the core draws the
    # half outside it too, wherever the fastening tables put that half: the cut, the bends and the
    # length are the bench's, and the conduit is a hole the one tube passes through.
    names |= {half for line, half in crossings(runs).items() if line in names}
    return sorted(names)


def members(scene, assembly):
    """`named`, held against the machine that has to place every one of them."""
    names = named(scene, assembly.runs)
    # ONE MODEL PLACES EVERY ONE OF THEM. The machine stands the core's own bodies, so a name
    # this cannot find is a name nothing draws — including a body the core's card claims and
    # the machine does not stand, which is the divergence worth hearing about.
    # THE MACHINE HOLDS AN ASSEMBLY, so what it places is its leaves and not its children —
    # a pass one level deep would find the `cold-core` node and nothing inside it.
    import manifold_layout as _ml
    present = {name for name, _shape, _colour in _ml.placed_leaves(assembly)}
    missing = sorted(n for n in names if n not in present)
    if missing:
        raise ValueError(
            f"scene {scene.id!r} names {', '.join(missing)}, which the machine does not place. "
            f"The fastening tables and the two assemblies' own body lists are what this reads; "
            f"a name in one of them and not in the model is the table to correct.")
    return names


# --- the fingerprint -------------------------------------------------------
#
def scene_digest(scene) -> str:
    """A name for the scene's own tuple — its roots, its camera, its framing."""
    h = hashlib.blake2b(digest_size=16)
    h.update(repr(tuple(scene)).encode())
    return h.hexdigest()


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
