#!/usr/bin/env python3
"""Generated build objects and the numbered catalog's website publication, by hash.

    tools/cad-venv/bin/python tools/cad-artifacts/pack.py            # what the bundle holds
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write    # build it, upload it, point main at it
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write --publish-held
                                                                    # upload the bytes on disk
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --check    # 0 = the pointer file names this tree
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --prune    # remove retired pointed-at outputs
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --room     # what room the release has left
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --retire   # take dead assets off it
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py selftest   # the bundle, on fixtures

`hardware/cad-artifacts.json` names the asset by its own sha256, every solid inside it, each
tracked scorecard the viewer reads by sha256, and what each member was made from; it is
committed. The scorecards stay outside the geometry tar and move atomically with its pointer
file. The asset is content-addressed (`cad-<sha16>.tar.gz`) and never rewritten, so a checkout
resolves to the bundle its own commit was packed against. `web/scripts/fetch-cad-artifacts.mjs`
reads the pointer file at deploy and holds the download to both hashes before anything is
extracted.

`solids` retains the store inventory used by builds. `website` selects numbered materials'
models and print files, with the guide art and scenes their pages draw. Website fetches read
that selection; build restores use `fetch-cad-artifacts.mjs --for-build`. New uploads are
catalog files or files the active build reads or writes. Existing store objects stay named.

THE BUNDLE CARRIES WHAT THIS DISK HOLDS, and `made` says what each member was made from. A
member a rule in `tools/bazel/graph.json` writes has a line there: `inputs`, one digest over the
ids of what its writers read when its bytes were cut (`tools/_artifact_inputs.py`); `commit`,
where that line was written; and `unproven` where the tree's inputs are not those, or where
nothing says what cut the bytes. Nothing is withheld for it — a solid mid-edit is a solid to look
at.

THE BUNDLE CARRIES NO FACT ABOUT THE MACHINE THAT PACKED IT. Members go in sorted, and the mtime,
uid, gid, uname, gname and mode a tar can hold are dropped; the gzip header carries no mtime. A
pack over a tree whose geometry has not moved lands on the same asset name and the same bytes —
the property `_cadq_export` gives each STEP it canonicalizes, kept at the bundle.

The walk reaches every `.step` under `hardware/` on disk, every `.stl` under `BUNDLED_MESH_DIRS`
— the one place where the solid is not the whole of the part — every `<file>.step.mesh` under
`BUNDLED_PAYLOAD_DIRS` or a reference's `frozen-asset.json`, which is that same surface at the
deflection a browser draws it at, and
every `.glb` under `BUNDLED_GLB_DIRS`, which the parts viewer opens directly rather than through
a STEP. What sits
out is `NOT_BUNDLED_DIRS` and `HARVESTED` below. `--check` holds what the walk found against the outputs
`tools/bazel/graph.json` declares, and names anything the graph does not carry.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_HERE.parents[1]))
from _artifact_inputs import Graph, blob_id, committed, on_disk, staged  # noqa: E402
sys.path.insert(0, str(_ROOT / "tools" / "bazel"))
from inventory import frozen_assets  # noqa: E402

POINTERS = _ROOT / "hardware" / "cad-artifacts.json"
TAG = "cad-artifacts"

#: Trees of local intermediates, each already ignored by the rule named beside it.
NOT_BUNDLED_DIRS = (
    "hardware/printed-parts/enclosure/tee-carrier",  # retained physical articles
    "hardware/pcb/pcba/.cad-cache",          # manufacturer downloads, keyed by LCSC
    "hardware/assembly/scenes/out",          # local bench-service view intermediates
    "hardware/quickstart",                 # retired owner document and local studies
    "hardware/printed-parts/enclosure/asse-drip-pan",  # retained retired geometry
    "hardware/quickstart-codex",           # retired owner document and local studies
    "hardware/quickstart-claude",          # retired owner document and local studies
    "hardware/install-guide/out",            # a leaf's own two renders; no route serves one
    # a hand-run guide's page renders and its art pass's staged STEPs; the walk above reaches
    # every `.step` under `hardware/` (hardware/weld-rotator-guide/README.md)
    "hardware/weld-rotator-guide/out",
    "hardware/gun-positioner-guide/out",
    "hardware/magnetic-float-guide/out",
    "hardware/tube-insertion-guide/out",
    # the G Ganen reference's working folder, which its own .gitignore holds out; nothing
    # declares a file in it
    "hardware/reference/g-ganen-pump/_scratch",
)

#: Solids with no builder in this tree — `y_divider.py:3` says it of its own. `manifold_layout.py`
#: places the tee; the elbow is the PP0308E stand-in the machine no longer places. They are in git
#: and out of the bundle.
HARVESTED = (
    "hardware/reference/elbow-connector/elbow-connector.step",
    "hardware/reference/tee-connector/tee-connector.step",
    "hardware/reference/y-divider/y-divider.step",
)


def _sha256(path) -> str:
    return _native("sha256", path=Path(path))


def _facets(path) -> int:
    """The triangle count a binary STL declares, or -1 where nothing declares one.

    A binary STL is an 80-byte header and then a uint32 count, so this is four bytes at a known
    offset. An ASCII one opens `solid` and states no count; a STEP states none either."""
    return _native("facets", path=Path(path))


def barren(root: Path, solid_hashes: dict) -> list:
    """Members carrying no geometry, and members whose bytes are already another member's.

    A SHA256 OF AN EMPTY FILE IS A PERFECTLY GOOD SHA256. `fetch-cad-artifacts.mjs` holds every
    member to its hash on the way in, so a mesh that lost its faces between the build and the pack
    arrives verified, and the site and every clean clone then trust it. Verified
    and non-empty are different questions and the fetch only ever asks the first.

    Both readings are free beside the hash this file already takes of every member. A binary STL
    declares its own triangle count and no part of this machine is nought facets — an empty one is
    84 bytes and its count reads zero. And two distinct parts sharing a sha256 are two files with
    the same bytes, which for geometry means neither holds any; empties collide with each other
    precisely because there is nothing in them to differ."""
    return _native("barren", root=root, hashes=solid_hashes)


# WHERE A MESH IS CARRIED TOO. A directory named here has its `.stl` bundled beside the solids.
# The enclosure's six pieces are what a slicer is handed, and their flutes are in the MESH and not
# in the solid, so the STEP beside them does not carry the surface that gets printed
# (`printed-parts/cadlib/flute_skin.py`). Printable meshes are gitignored, so the bundle is the
# route by which they leave the machine that cut them — for a reader with a printer, not for the
# viewer, which serves `.step`. The cold core's shell and its two caps carry the same skin off the
# same field (`cold-core/_show_skin.py`) and leave the same way, and so does the faucet's base
# (`faucet_shell.write_bed_file`) — the one piece of this machine that stands on a counter.
BUNDLED_MESH_DIRS = (
    "hardware/printed-parts/calibration/soda-studies",
    "hardware/printed-parts/fixtures/tube-insertion",
    "hardware/printed-parts/fixtures/pgfun-positioner",
    "hardware/printed-parts/calibration/dual-nozzle-registration",
    "hardware/printed-parts/enclosure/display-cover",
    "hardware/printed-parts/enclosure/nameplate",
    "hardware/printed-parts/faucet/industrial",
    "hardware/printed-parts/cold-core/magnetic-float",
    "hardware/printed-parts/zone-c/funnel-mold",
    "hardware/printed-parts/zone-c/funnel",
    "hardware/printed-parts/zone-c/funnel-cover",
    "hardware/printed-parts/enclosure/enclosure",
    "hardware/printed-parts/enclosure/pump-dock",
    "hardware/printed-parts/cold-core/foam-shell",
    "hardware/printed-parts/cold-core/foam-cap",
    "hardware/printed-parts/faucet/faucet-shell",
    "hardware/printed-parts/faucet/lever-replica",
    "hardware/printed-parts/faucet/faucet-display-cover",
    "hardware/printed-parts/faucet/above-counter-plate",
    "hardware/printed-parts/faucet/above-counter-gasket",
    "hardware/printed-parts/faucet/asse-vent-seals",
    "hardware/printed-parts/faucet/umbilical-organizer",
    "hardware/printed-parts/fixtures/faucet-display-snap",
    "hardware/printed-parts/fixtures/faucet-cover-retention",
    "hardware/printed-parts/fixtures/valve-socket-fit",
    "hardware/printed-parts/fixtures/gun-positioner",
    "hardware/printed-parts/fixtures/gun-positioner-observation",
    "hardware/gun-positioner/mounting",
    # Parts whose printable meshes sit beside their STEPs, and the rear chips, R14 holder and ASSE
    # cuffs.
    "hardware/printed-parts/cold-core/copper-plugs",
    "hardware/printed-parts/cold-core/prv-shroud",
    "hardware/printed-parts/cold-core/reed-bridge",
    "hardware/printed-parts/cold-core/reservoir",
    "hardware/printed-parts/enclosure/display-gasket",
    "hardware/printed-parts/enclosure/data-ring",
    "hardware/printed-parts/enclosure/rear-identification",
    "hardware/printed-parts/faucet/tube-collar",
    "hardware/printed-parts/soda-bend-holder",
    "hardware/printed-parts/asse-straight-cuffs",
    # The parts the Rust kernel cuts, whose program writes the printed mesh beside the STEP.
    "hardware/printed-parts/refrigeration/fuse-clamp",
    "hardware/printed-parts/cold-core/coil-mandrel",
    "hardware/printed-parts/fixtures/weld-rotator",
    "hardware/printed-parts/fixtures/water-inlet-jet",
    "hardware/printed-parts/asse-drain-adapter",
)

#: Scene meshes the parts viewer opens as themselves. `web/public/js/viewer/parts.js` names `glb`
#: a build directory and hands one to `openGlbDetail`, so a deploy that cannot find them serves a
#: catalog whose scenes do not open. `render_scenes.py` cuts them and `graph.json` declares all
#: eleven, which is what `--check` holds them against.
BUNDLED_GLB_DIRS = ("hardware/assembly/scenes/glb",)

# AND WHERE THE SURFACE A PIECE IS DRAWN FROM IS CARRIED. A directory named here has its
# `<file>.step.mesh` bundled beside the solid it stands for. `loadStepFile` fetches that payload
# before it will parse a STEP (`web/public/js/viewer/step.js`), so for the pieces above — whose
# flutes are in the mesh and not in the solid — it is the only route by which the surface the
# machine actually has reaches a browser. `hardware/scripts/flute_payload.py` cuts them out of
# the printed mesh at the deflection occt-import-js would have meshed the STEP at.
#
# A DEPLOY WITH NO PAYLOAD SERVES A SMOOTH BOX. Elsewhere in the tree a missing payload costs a
# wasm parse and nothing else — the STEP carries the same surface — which is why `.step.mesh` is
# gitignored and why the route that serves one says a 404 there is normal.
#
# `manifold-layout/` IS HERE BECAUSE THE APPLIANCE IS. `enclosure-assembly.step` places all six
# pieces and is what the /3d assembly card opens, so the flutes reach the machine itself by the same
# route. Both payloads there are also the cheaper artifact by a wide margin — 13.97 and 2.46 MB
# against solids of 49.64 and 8.29 — so a browser that finds them fetches a quarter of the bytes
# and skips the parse.
#
# A PART THE RUST KERNEL CUTS HAS NO SURFACE ON THE PAGE BUT ITS PAYLOAD. Its STEP is triangles,
# which occt-import-js 0.0.23 (OCCT 7.6) reads none of, so a deploy without the payload draws
# nothing where the part stands.
#
# AND THE COLD CORE'S TWO DIRECTORIES ARE HERE FOR THE SAME REASON THE BOX'S IS. Its shell and
# both caps carry the same show skin off the same field (`cold-core/_show_skin.py`), cut into the
# mesh and not into the solid, so a browser that cannot fetch their payloads draws three smooth
# prisms where the machine has flutes. The faucet shell's directory is here on that same reason
# and one more: it is the piece a customer stands in front of, and `faucet-shell.step` is what
# /3d opens when anybody asks to look at the faucet.
BUNDLED_PAYLOAD_DIRS = (
    "hardware/wiring",
    "hardware/printed-parts/calibration/soda-studies",
    "hardware/printed-parts/fixtures/tube-insertion",
    "hardware/printed-parts/fixtures/pgfun-positioner",
    "hardware/printed-parts/enclosure/grip-cover",
    "hardware/printed-parts/enclosure/display-cover",
    "hardware/printed-parts/enclosure/rear-identification",
    "hardware/printed-parts/enclosure/rear-equipment-caps",
    "hardware/printed-parts/faucet/industrial",
    "hardware/printed-parts/cold-core/magnetic-float",
    "hardware/printed-parts/zone-c/funnel-mold",
    "hardware/printed-parts/zone-c/funnel",
    "hardware/printed-parts/zone-c/funnel-cover",
    "hardware/printed-parts/enclosure/enclosure",
    "hardware/printed-parts/enclosure/pump-dock",
    "hardware/printed-parts/cold-core/foam-shell",
    "hardware/printed-parts/cold-core/foam-cap",
    "hardware/printed-parts/faucet/faucet-shell",
    "hardware/printed-parts/faucet/lever-replica",
    "hardware/printed-parts/faucet/faucet-display-cover",
    "hardware/printed-parts/faucet/above-counter-plate",
    "hardware/printed-parts/faucet/above-counter-gasket",
    "hardware/printed-parts/faucet/asse-vent-seals",
    "hardware/printed-parts/faucet/umbilical-organizer",
    "hardware/manifold-layout",
    "hardware/faucet-layout",
    "hardware/printed-parts/fixtures/faucet-cover-retention",
    "hardware/printed-parts/fixtures/valve-socket-fit",
    "hardware/printed-parts/fixtures/gun-positioner",
    "hardware/printed-parts/fixtures/gun-positioner-observation",
    "hardware/gun-positioner/mounting",
    "hardware/printed-parts/refrigeration/fuse-clamp",
    "hardware/printed-parts/cold-core/coil-mandrel",
    "hardware/printed-parts/fixtures/weld-rotator",
    "hardware/printed-parts/fixtures/water-inlet-jet",
    "hardware/printed-parts/asse-drain-adapter",
    "hardware/printed-parts/asse-straight-cuffs",
)

# Explicit model payloads kept with the generated store inventory.
BUNDLED_PAYLOAD_FILES = (
    "hardware/cold-core-layout/cold-core-assembly.step.mesh",
    "hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step.mesh",
    "hardware/cut-parts/carbonation/carbonator-tube/carbonator-tube.step.mesh",
    "hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step.mesh",
    "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step.mesh",
    "hardware/printed-parts/enclosure/data-ring/data-ring.step.mesh",
    "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-water.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-carb.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-co2.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step.mesh",
    "hardware/printed-parts/enclosure/bulkhead-ring/bulkhead-ring-drain.step.mesh",
    "hardware/printed-parts/enclosure/display-gasket/display-gasket.step.mesh",
    "hardware/reference/seaflo-discharge-chain/seaflo-discharge-chain.step.mesh",
    "hardware/printed-parts/electronics/pcba-tray/pcba-board.step.mesh",
    "hardware/printed-parts/cold-core/reed-bridge/reed-bridge.step.mesh",
    "hardware/printed-parts/cold-core/reed-bridge/reed-bridge-setting-gauge.step.mesh",
    "hardware/printed-parts/cold-core/prv-shroud/prv-shroud.step.mesh",
    "hardware/printed-parts/cold-core/reservoir/reservoir-cap-left.step.mesh",
    "hardware/printed-parts/cold-core/reservoir/reservoir-cap-right.step.mesh",
    "hardware/printed-parts/cold-core/reservoir/reservoir-tube-grip.step.mesh",
    "hardware/printed-parts/cold-core/reservoir/reservoir-air-grip.step.mesh",
    "hardware/printed-parts/calibration/dual-nozzle-registration/dual-nozzle-registration.step.mesh",
    "hardware/printed-parts/enclosure/nameplate/horizontal-wing-trial/nameplate-horizontal-wings-001.step.mesh",
    "hardware/printed-parts/enclosure/nameplate/horizontal-wing-trial/nameplate-horizontal-wings-receiver.step.mesh",
    "hardware/printed-parts/enclosure/nameplate/nameplate-001.step.mesh",
    "hardware/printed-parts/enclosure/nameplate/nameplate-receiver.step.mesh",
)

#: Shared installation scene renders travel with generated pictures. The committed
#: install-guide PDF, cover and sidecar reach the site directly in its checkout.
BUNDLED_ART_DIRS = (
    "hardware/install-guide/art",
)

#: Scene metadata rides beside the picture it describes.
BUNDLED_ART_SUFFIXES = (".png", ".pdf", ".png.scene.json")

BUNDLED_ART_FILES = (
    "hardware/install-guide/art/colors.css",
)

#: A board's rendered set — the fab pack, the copper and mask views, the 3D assembly.
#: `hardware/pcb/pcba/render-board.ts` writes them on every save of a board, the way a CadQuery
#: `.py` regenerates its `.step`, and `web/lib/walk.js` serves them off `pcb/<dir>/out/`.
#: Everything in the directory but the two below.
BUNDLED_BOARD_DIRS = ("hardware/pcb/pcba/out",)

#: The on-demand full B-rep, and the routed circuit-json the board's own `.gitignore` holds back.
#: Neither is served and neither is small.
BOARD_NOT_BUNDLED = (".step", ".circuit.json")

#: Producers `graph.json` does not watch. `trace_inputs.py` watches a Python `__main__`; a board
#: is drawn by a bun script, so the graph declares none of its outputs and `--check` has nothing
#: to hold them against.
UNWATCHED_PRODUCERS = BUNDLED_BOARD_DIRS


def _native_config():
    """Authored publication membership data for the native build inventory."""
    from inventory import ACTION_INTERMEDIATE, IMPLICIT_SOLIDS
    names = ("NOT_BUNDLED_DIRS", "HARVESTED", "BUNDLED_MESH_DIRS",
             "BUNDLED_GLB_DIRS", "BUNDLED_PAYLOAD_DIRS", "BUNDLED_PAYLOAD_FILES",
             "BUNDLED_ART_DIRS", "BUNDLED_ART_SUFFIXES", "BUNDLED_ART_FILES",
             "BUNDLED_BOARD_DIRS", "BOARD_NOT_BUNDLED", "UNWATCHED_PRODUCERS")
    return {**{name: globals()[name] for name in names},
            "IMPLICIT_SOLIDS": IMPLICIT_SOLIDS,
            "ACTION_INTERMEDIATE": list(ACTION_INTERMEDIATE)}


def _plain(value):
    if isinstance(value, Path):
        return str(value.absolute())
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_plain(item) for item in value]
    return value


def _ordered(value):
    if isinstance(value, dict):
        return {"_publication_pairs": [[key, _ordered(item)] for key, item in value.items()]}
    if isinstance(value, (tuple, list)):
        return [_ordered(item) for item in value]
    return value


def _unorder(value):
    if isinstance(value, dict) and set(value) == {"_publication_pairs"}:
        return {key: _unorder(item) for key, item in value["_publication_pairs"]}
    if isinstance(value, dict) and set(value) == {"$dict"}:
        return {key: _unorder(item) for key, item in value["$dict"]}
    if isinstance(value, list):
        return [_unorder(item) for item in value]
    return value


def _native(op, **fields):
    sys.path.insert(0, str(_ROOT / "hardware/scripts"))
    from _build_data import request
    return request("publication-" + op, config=_plain(_native_config()), **_plain(fields))


def _patch(data, updates):
    wire = [{"path": list(path), "value": _ordered(value)} for path, value in updates]
    return _unorder(_native("patch", ordered=_ordered(data), updates=wire))


def _inventory_rows(root):
    sys.path.insert(0, str(root / "tools/bazel"))
    from inventory import inventory, tracked
    return [[list(generators), record] for generators, record in inventory(tracked()).items()]


def _member_filter(frozen, root: Path = _ROOT):
    """The path policy shared by the disk walk and declared public outputs."""
    policy = _native("member-policy", root=root, frozen=list(frozen))

    def member(rel):
        return _native("member-prepared", path=rel, policy=policy)
    return member


def solids(root: Path) -> list:
    """Every generated `.step`, `.stl`, `.glb`, `.step.mesh`, `.png` and `.pdf` under
    `hardware/`, repo-relative and sorted.

    Off the disk, tracked or not: an artifact the index does not hold is one a fresh clone still
    has to be sent, and it is the pointer file that carries it into the index. One pass over
    `hardware/`, which steps into no `NOT_BUNDLED_DIRS` tree and follows no link, and lists
    again only a directory whose stat identity moved."""
    return _native("solids", root=root)


def build(root: Path, rels: list, dest) -> str:
    """Write the bundle at `dest` and return its sha256. A member carries its path and its
    bytes; every other field a tar can hold is set flat."""
    return _native("build", root=root, rels=list(rels), output=Path(dest))


def _origin_slug(root: Path) -> str:
    """`owner/repo` for the origin remote, which is what the download URL is built from."""
    url = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout
    return _native("origin-slug", url=url)


def hashes(root: Path, rels: list) -> dict:
    """Each solid's sha256, by repo-relative path.

    The bundle is a function of these and their order, so a set of them equal to the pointer file's is a
    bundle equal to the pointer file's — which is the whole of what `--check` asks, and it asks it without
    compressing 117 MB to find out."""
    sys.path.insert(0, str(_ROOT / "tools"))
    from _artifact_digest import hashes as cached_hashes
    return cached_hashes(root, rels)


def line_times(held: dict, solid_hashes: dict, stamp: float) -> dict:
    """When each line of the pointer file last moved, by member.

    A line whose hash main already names keeps its time. A moved line carries the time this
    cut collected its bytes. A local file newer than that snapshot is another completed cut,
    including one that finishes while the current snapshot uploads."""
    return _native("line-times", held=held, hashes=solid_hashes, stamp=stamp)


def held_publish_plan(held: dict, rels: list, now: dict, mtimes: dict) -> tuple:
    """What a held publish does with each member on this disk, against main's pointers:
    `(built, fresh, stale, absent)`.

    A PUBLISH MOVES THE LINES FOR WHAT THIS MACHINE CUT AND TAKES MAIN'S FOR THE REST. Twenty
    machines publish into one file, and each holds a copy of every member; a copy that differs
    from main's line is this machine's newer cut when the file is newer than the line, and
    main's older bytes when it is older. The first is `built` and goes up; the second is
    `stale` and is taken from the release instead. A member main names that this disk does
    not hold is `absent`, and its line stands: retiring is `--prune`, never absence."""
    return tuple(_native("held-plan", held=held, rels=rels, now=now, mtimes=mtimes))


def object_url(held: dict, digest: str):
    """Where one member's bytes are by hash: the store, else the release; None without either."""
    return _native("object-url", held=held, digest=digest)


def download_object(url: str) -> bytes:
    """A release object, gunzipped. Its bytes stay bytes: a list of them sent to the store worker
    takes many times a large member's size in memory, which this Mac does not have."""
    import gzip
    from urllib.request import Request, urlopen
    with urlopen(Request(url, headers={"User-Agent": "pack.py"}), timeout=120) as resp:
        return gzip.decompress(resp.read())


def adopt(root: Path, held: dict, rels: list) -> list:
    """Main's bytes for the members this disk holds older copies of, put in their place.

    The same move `fetch-cad-artifacts.mjs --adopt` makes on a server, made here for exactly
    the members `held_publish_plan` read as stale, so a generator that reads another part as
    its input reads the part main points at. Returns the members taken; one that could not be
    fetched or does not hash to its line is left as it was and said so."""
    taken = []
    for rel in rels:
        digest = held["solids"][rel]
        url = object_url(held, digest)
        if not url:
            print(f"  {rel}: main's bytes are not on the release by hash; left as it is")
            continue
        try:
            data = download_object(url)
        except Exception as exc:
            print(f"  {rel}: main's bytes did not come ({exc}); left as it is")
            continue
        if hashlib.sha256(data).hexdigest() != digest:
            print(f"  {rel}: the release's object does not hash to main's line; left as it is")
            continue
        target = root / rel
        temporary = target.with_name(target.name + ".adopt")
        temporary.write_bytes(data)
        os.replace(temporary, target)
        taken.append(rel)
    return taken


def _head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _dirty_artifact_reach(root: Path) -> tuple:
    """`(artifact rules the tree's edits reach, the edits)`.

    Ignored generated solids are intentionally absent from what `affected.changed` reports; they
    are the bytes being packed. What is left is the working tree standing outside HEAD, asked of
    HEAD by content, and the rules it reaches are the ones a reconciliation leaves uncut."""
    sys.path.insert(0, str(root / "tools/bazel"))
    import affected
    moved = list(affected.changed(root))
    moved = _native("dirty-inputs", moved=moved, sidecars=sidecars(root),
                    held_sidecars=list(read_pointers(root).get("sidecars", {})),
                    presentation=[path for path in moved if affected.artifact_presentation_only(path)])
    if not moved:
        return [], []
    found, _hit = affected.manifest_targets(moved)
    state = _native("set-plan", first=list(found), second=list(affected.artifact_targets()))
    state = _native("set-plan", first=state["intersection"], second=list(affected.sentinel_targets(moved)))
    return state["union"], moved


#: How much newer than a member one of its generated inputs may stand and still be what its cut
#: read. `sync_tree --write` copies one build's outputs in path order, so a part copied after
#: the assembly that reads it stands newer by the copies between them.
GENERATED_SKEW_NS = 60 * 10**9


def cut_after_inputs(root: Path, rel: str, graph: Graph) -> bool:
    """Whether `rel` was written after each input it reads last changed: an authored input no
    later than the member, a generated one no more than `GENERATED_SKEW_NS` later."""
    return _native("cut-after-inputs", root=root, path=rel, inputs=list(graph.inputs(rel)),
                   writers=list(graph.writers), skew_ns=GENERATED_SKEW_NS)


def _line(inputs: str = None, commit: str = None, unproven: bool = False) -> dict:
    """One `made` line, its keys in the order the pointer file holds them."""
    return _unorder(_native("line-ordered", inputs=inputs, commit=commit, unproven=unproven))


def made_lines(held: dict, members, head: str, tree: dict, cut: dict = None,
               derived=(), moved=(), refuted=()) -> dict:
    """The `made` line for each of `members`.

    `tree` is each member's input digest as the tree commits it, and `cut` as this disk holds
    it. A member in `derived` was cut from this disk and is recorded off `cut`. A member whose
    bytes `moved` otherwise, or that has no line yet, is unproven with nothing to say what cut
    it. The rest keep their lines, unproven where `tree` is not their inputs or `refuted`
    names them."""
    return _unorder(_native("made-lines-ordered", held=held, held_order=_ordered(held),
        members=list(members), head=head, tree=tree, cut=cut, derived=list(derived),
        moved=list(moved), refuted=list(refuted)))


def made_moves(held: dict, tree: dict) -> list:
    """The members whose `made` line moves though no bytes do: one with no line, a proven line
    whose inputs the tree has moved off, and an unproven one the tree has come back to."""
    return _native("made-moves", held=held, tree=tree)


def tree_digests(root: Path, graph: Graph, lines: dict, index: dict = None) -> dict:
    """The input digest, as the tree commits it, of each declared member `lines` names."""
    return _unorder(_native("tree-digests", root=root, graph=graph._wire(), lines=lines,
                           line_order=list(lines), index=staged(root) if index is None else index))


def made_for(held: dict, lines: dict, head: str, tree: dict, cut: dict = None,
             derived=(), moved=(), refuted=(), frozen=()) -> dict:
    """The pointer file's `made`: a line for each declared member `lines` names, and the line
    each undeclared one already has."""
    return _unorder(_native("made-for", held=held, held_order=_ordered(held), lines=lines,
        head=head, tree=tree, cut=cut, derived=list(derived), moved=list(moved),
        refuted=list(refuted), frozen=list(frozen)))


def _members_of_targets(root: Path, labels: set) -> set:
    """Every bundle member and scorecard the named artifact rules produce.

    The inverse of `_targets_for_members`, off the same inventory."""
    if not _native("target-query", root=root, workspace=_ROOT, members=list(labels)):
        return set()
    return set(_native("target-members", targets=list(labels), inventory=_inventory_rows(root)))


def _owed_artifact_targets(root: Path, made: dict, tree: dict) -> list:
    """The rules owning a member whose `made` line does not prove it against the tree."""
    members = _native("owed-members", made=made, tree=tree)
    return _targets_for_members(root, set(members))[0]


def _behind(root: Path, targets: list) -> bool:
    """Whether bazel says any of `targets` is not up to date with this tree.

    `BazelWorkspaceStatusAction` reruns on every invocation and says nothing about an output."""
    if not targets:
        return False
    check = subprocess.run(["bazel", "build", "--check_up_to_date", *targets],
                           cwd=str(root), capture_output=True, text=True)
    return _native("behind", returncode=check.returncode, stderr=check.stderr)


def carry_the_cut(root: Path, targets: list) -> list:
    """`(rules that would not cut, members this tree does not hold the cut of)`.

    THE PART AS IT IS, WHICH IS WHAT THE SITE IS FOR. A rule whose source has moved and whose
    output has not describes the part as it was, and publishing that shows a change that has not
    happened. Bazel already knows which rules those are and how to cut them, so it cuts them —
    a refusal here would only be this asking someone to run the build it could run.

    A CUT REACHES BAZEL-BIN AND STOPS THERE. Carrying it into the tree is `sync_tree --write`,
    which copies over files other sessions are editing, and this is not the caller that gets to
    decide that. So the tree keeps its own bytes, the bundle carries them, and a member whose
    bytes are not the ones HEAD's source just cut comes back on the right to be recorded —
    which is the same answer as a rule that would not cut at all, arrived at one step later.
    """
    if not targets:
        return [], set()
    if _behind(root, targets):
        print(f"cutting {len(targets)} artifact target(s) this tree is behind on")
        subprocess.run(["bazel", "build", "--keep_going", *targets], cwd=str(root))
    # ONE RULE THAT WOULD NOT CUT IS NOT THE OTHERS' PROBLEM, so the failed ones leave the set
    # rather than the reading, and every rule that did cut is still compared.
    failed = [t for t in targets if _behind(root, [t])] if _behind(root, targets) else []
    if failed:
        print(f"  {len(failed)} target(s) would not cut:")
        for label in failed[:8]:
            print(f"    {label}")
    carried = _native("set-plan", first=targets, second=failed)["difference"]
    if not carried:
        return failed, set()
    sys.path.insert(0, str(root / "tools" / "bazel"))
    from sync_tree import _runtime_output, _targets as cut_pairs

    pairs = [[str(built), rel, _runtime_output(rel)] for built, rel in cut_pairs(tuple(carried)).items()]
    unheld = set(_native("unheld", root=root, pairs=pairs))
    if unheld:
        print(f"  {len(unheld)} member(s) are not the bytes that cut just made, and are recorded:")
        for rel in sorted(unheld)[:8]:
            print(f"    {rel}")
    return failed, unheld


def _targets_for_members(root: Path, members: set) -> tuple:
    """The artifact rules that own bundle members or scorecards, and any no rule owns.

    The pointer file source tells which rules the commit range owes. The bytes on disk can also have
    moved independently because generated solids are ignored; mapping every changed member
    back to its producer makes `--write` prove those bytes came from a current Bazel output too.
    """
    if not _native("target-query", root=root, workspace=_ROOT, members=list(members)):
        return [], sorted(members)
    return tuple(_native("member-targets", members=list(members), inventory=_inventory_rows(root)))


#: The pointer file's keys, in the order it holds them.
KEYS = ("_", "release", "store", "bundle", "solids", "sidecars", "website", "mesh_assets", "moved", "made")


def _retired(root: Path, rel: str) -> bool:
    """A retired directory and its descendants are outside website publication."""
    return _native("retired", root=root, path=rel)


def _website_paths(root: Path, available=()) -> set:
    """Catalog membership, companions and named print files, without a filename allowlist."""
    return set(_native("website-paths", root=root, available=list(available)))


def website_for(root: Path, data: dict) -> dict:
    """Catalog models and their files; the complete store inventory stays in `solids`."""
    return _unorder(_native("website-ordered", root=root, data=data))


def pointers_for(root: Path, rels: list, digest: str, size: int, solid_hashes: dict = None,
             sidecar_hashes: dict = None, made: dict = None, held: dict = None,
             stamp: float = None) -> dict:
    solid_hashes = solid_hashes if solid_hashes is not None else hashes(root, rels)
    sidecar_hashes = sidecar_hashes if sidecar_hashes is not None else hashes(root, sidecars(root))
    return _unorder(_native("pointers", root=root, rels=rels, digest=digest, size=size,
        slug=_origin_slug(root), tag=TAG, store_url=STORE_URL, prefix=OBJECT_PREFIX,
        hashes=solid_hashes, hashes_order=_ordered(solid_hashes),
        sidecar_order=_ordered(sidecar_hashes), made=made, made_order=_ordered(made),
        held=held or {}, stamp=stamp if stamp is not None else time.time()))


def _pointer_file(data: dict) -> dict:
    """`data` as the pointer file holds it: the keys `KEYS` names, in that order, and each
    member map in path order."""
    return _unorder(_native("pointer-file", ordered=_ordered(data)))


def read_pointers(root: Path = _ROOT) -> dict:
    return _unorder(_native("read-pointers-ordered", root=root))


def _write_pointers(data: dict) -> None:
    _native("write-pointers", root=_ROOT, path=POINTERS, data=data, ordered=_ordered(data))


def _declared(root: Path) -> set:
    """Every publishable graph output and frozen static reference member."""
    return set(_native("declared", root=root, same_root=root.resolve() == _ROOT.resolve()))


def sidecars(root: Path, graph: Graph = None) -> list:
    """Graph-declared scorecards served directly from the committed tree, repo-relative."""
    return _native("sidecars", root=root, graph=graph._wire() if graph is not None else None)


def sidecar_lines(root: Path, held: dict, graph: Graph = None) -> dict:
    """Each scorecard's line: the hash of the one the tree holds, and the line the pointer file
    already has for one the tree does not hold."""
    return _native("sidecar-lines", root=root, held=held,
                   graph=graph._wire() if graph is not None else None)


def sidecar_debt_targets(root: Path) -> list:
    """Producer labels whose committed viewer scorecards do not match this pointer file."""
    targets, unowned = _targets_for_members(root, set(_native("sidecar-debt", root=root)))
    if unowned:
        raise SystemExit("scorecard output(s) have no current Bazel producer:\n  " + "\n  ".join(unowned))
    return targets


def _graph_gaps(root: Path, rels: list) -> tuple:
    """Bundled-but-undeclared and declared-but-absent publish outputs.

    A sibling STEP is not a declaration for an STL or `.step.mesh`: every published member is
    named by its producing action or its frozen reference manifest."""
    return tuple(_native("graph-gaps", root=root, rels=rels, declared=list(_declared(root))))


def _undeclared(root: Path, rels: list) -> list:
    """Compatibility name for callers that only ask about the first half of `_graph_gaps`."""
    return _graph_gaps(root, rels)[0]


def _retirement_evidence(root: Path, retired: list) -> list:
    """Retired paths with nothing to show for their retirement.

    Each is asked of the commit its `made` line was written at: whether a producer the graph
    named there has moved since, or is gone from the tree. A path with no line has no commit to
    ask.

    A SOURCE THAT IS GONE FROM THE TREE HAS ALREADY ANSWERED. A rename older than that commit is
    behind it, so no diff over `commit..HEAD` holds it; whether the file is there now does not
    depend on a range at all."""
    groups = _native("retirement-groups", held=read_pointers(root), retired=retired)
    records = []
    for commit, rels in groups.items():
        if not commit:
            continue
        old = subprocess.run(["git", "-C", str(root), "show", f"{commit}:tools/bazel/graph.json"],
                             capture_output=True, text=True)
        moved = subprocess.run(["git", "-C", str(root), "diff", "--name-only", commit, "HEAD"],
                               capture_output=True, text=True)
        records.append(dict(rels=rels, graph=old.stdout, graph_ok=old.returncode == 0,
                            diff_ok=moved.returncode == 0, changed=moved.stdout.splitlines()))
    return _native("retirement-evidence", root=root, records=records, unrecorded=groups.get("", []))


def retired_outputs(root: Path) -> list:
    """Pointed-at solids or scorecards no current producer or static manifest declares."""
    return _native("retired-outputs", root=root, declared=list(_declared(root)))


def prune(root: Path, allow_retired: bool = False) -> int:
    """Remove pointed-at bundle members and scorecards the current graph has retired.

    Explicit because solid deletion is otherwise invisible to git, while a retired tracked
    scorecard must leave the public endpoint in the same commit that removes its pointer. Every
    target remains recoverable from the preceding published commit.
    """
    retired = retired_outputs(root)
    unexplained = [] if allow_retired else _retirement_evidence(root, retired)
    if unexplained:
        print("refusing to retire public outputs without a changed producing source:")
        for rel in unexplained[:20]:
            print(f"  {rel}")
        print("  Correct the graph/source history, or review and pass --allow-retired.")
        return 2
    try:
        removed = _native("prune", root=root, retired=retired)
    except ValueError as error:
        raise SystemExit(str(error).removeprefix("build-data: ")) from None
    for rel in removed:
        print(f"  {rel}")
    print(f"{len(removed)} retired pointed-at output(s) removed; recoverable from the prior commit")
    return 0


def _gh(root: Path, *args, **kw):
    """`gh`, with a machine that cannot run it reported the way a call that failed is.

    NO `gh`, NO DIRECTORY, NO ANSWER — and every caller here already reads a non-zero return as
    "the release did not answer". Letting the OSError out instead would take a check on the
    board down with a traceback on a machine that simply has no CLI installed, which says
    nothing about the tree the board is reading.
    """
    try:
        return subprocess.run(["gh", *args], cwd=str(root),
                              capture_output=True, text=True, **kw)
    except OSError as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def _release_asset_matches(root: Path, asset: str, digest: str, size: int) -> bool:
    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        return False
    return _native("release-match", assets=json.loads(listing.stdout).get("assets", []),
                   asset=asset, digest=digest, size=size)


OBJECT_PREFIX = "s-"
#: THE STORE IS THE SITE. Each member goes up by hash to homesodamachine.com, which holds it on
#: its own disk and serves it (web/lib/objects.js); the GitHub release stays an archive the
#: fetcher falls back to. Any machine that cut a member can put it here, a cloud session
#: included, which the release refuses.
STORE_URL = "https://homesodamachine.com/objects/"

#: WHAT ONE RELEASE HOLDS. GitHub takes 1000 assets on a release and refuses the 1001st, and
#: this store is append-only: every cut adds a bundle and every member that moved adds an
#: object. The ceiling does not announce itself. It arrives as one member's upload failing,
#: which `upload_objects` reads as "this pointer file is read from the bundle" and survives — so the
#: first thing a full release does is quietly turn the fast path off and send every deploy
#: back to the whole tarball. The bundle is what fails next, and it has no fallback: a pointer file
#: naming an asset the release does not hold is a deploy that cannot fetch the geometry.
RELEASE_ASSET_CAP = 1000

#: HOW MANY CUTS THE RELEASE HOLDS WHOLE. A cut is a bundle and one object per member that
#: moved, and this is the window both are kept for: the last `CUTS_KEPT` pointer files, entire. A
#: publish that repaints or re-tessellates the tree moves every member at once — the material
#: change on 2026-08-26 rewrote all five cold-core STEPs — so the room a cut wants is bounded
#: by the member count and not by any average, and the store refills in a few of them.
CUTS_KEPT = 12

#: HOW LONG AN ASSET IS OFF LIMITS AFTER IT LANDS. `--write` puts the bundle and one object per
#: moved member on the release BEFORE it writes the pointer file that names them, so for the length of
#: an upload those bytes are on the release and no pointer file anywhere names them. A sweep reading
#: only committed pointer files calls exactly that unreachable, and deleting it leaves a pointer file about to
#: be written naming an asset the release does not hold — which is a deploy that cannot fetch
#: the geometry, and nothing puts it back. Across the twelve cuts of 2026-08-27 the pointer file commit
#: followed the newest asset it names by 1-2 s; this covers the upload in front of that gap,
#: with room for the 143 MB bundle, and costs the sweep nothing — an asset this new is inside
#: the `CUTS_KEPT` window in any case.
RETIRE_FLOOR_S = 30 * 60


def object_asset(sha: str) -> str:
    """The release asset holding one member's bytes, named by those bytes."""
    return _native("object-asset", prefix=OBJECT_PREFIX, digest=sha)


def release_assets(root: Path) -> list:
    """Every asset on the release, as `gh` reports it."""
    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        return []
    return json.loads(listing.stdout).get("assets", [])


def pointer_assets(held: dict) -> set:
    """The release assets one pointer file names — its bundle, and one per member and scorecard sha.

    A SCORECARD IS SERVED FROM THE COMMITTED TREE and `upload_objects` sends solids, so a
    scorecard's name here is one the release never holds. This is reach, and a superset of the
    names on the release is the safe direction for it."""
    return set(_native("pointer-assets", held=held, prefix=OBJECT_PREFIX))


def _shallow(root: Path) -> bool:
    """Whether this clone holds less than the whole history.

    `git rev-list` ANSWERS A TRUNCATED CLONE WITHOUT SAYING SO. It reports the revisions the
    clone can reach and nothing about the ones it does not hold, so `locks_in_history` on a
    shallow tree returns FEWER pointer files and every asset only the missing ones name reads as
    unreachable — which is the one verdict that takes bytes off the release. Nothing downstream
    can catch it: the answer is confident, well-formed and short.

    A RUNNER IS WHERE THIS BITES, because a checkout there is shallow by default and the sweep
    is the one caller whose whole job is deletion. `actions/checkout` needs `fetch-depth: 0`.
    """
    got = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                         cwd=str(root), capture_output=True, text=True)
    return got.stdout.strip() == "true"


def pointer_files_in_history(root: Path) -> list:
    """Every committed pointer file, newest first, as the asset names each one names.

    THE POINTER FILE IS COMMITTED, so what a checkout can ask the release for is what its own pointer file
    names — and the union over all of history is the set of names anyone can ask for at all.
    A name outside it is not old, it is unreachable: the cut that made it was superseded before
    its pointer file landed, or the commit that named it is no longer in the graph.
    """
    rel = str(POINTERS.relative_to(_ROOT))            # the same path inside any root
    revs = subprocess.run(["git", "rev-list", "HEAD", "--", rel],
                          cwd=str(root), capture_output=True, text=True).stdout.split()
    out = []
    for rev in revs:                                                    # newest first
        blob = subprocess.run(["git", "show", f"{rev}:{rel}"],
                              cwd=str(root), capture_output=True, text=True)
        if blob.returncode != 0:
            continue
        try:
            held = json.loads(blob.stdout)
        except json.JSONDecodeError:
            continue
        out.append(pointer_assets(held))
    return out


def too_new(assets: list, now: float = None) -> set:
    """The assets inside `RETIRE_FLOOR_S`, which no sweep may take.

    AN ASSET THIS FUNCTION CANNOT DATE IS NEW. A sweep with no ground to say when something
    landed has no ground to delete it, and the cost of keeping one is one slot."""
    return set(_native("too-new", assets=assets, now=time.time() if now is None else now,
                       floor=RETIRE_FLOOR_S))


def retirable(root: Path, keep_cuts: int = CUTS_KEPT, now: float = None) -> tuple:
    """The assets that may leave the release, as `(unreachable, superseded)`.

    UNREACHABLE IS NOT A JUDGEMENT — no commit's pointer file names it, so no checkout can fetch it.

    SUPERSEDED IS EVERYTHING OUTSIDE THE LAST `keep_cuts` POINTER FILES, bundle and object alike, and
    what retiring one costs is a re-pack rather than the bytes. This file's own contract is
    that the pack carries no fact about the machine that made it: members go in sorted, the
    tar's mtime/uid/gid/mode and the gzip header's mtime are dropped, so a tree whose geometry
    has not moved packs to the same name and the same bytes. Checking that commit out and
    running `--write` puts the identical assets back under the identical names.

    THE WINDOW IS A UNION AND NOT A SLICE. A member that has not moved in fifty cuts is named
    by the newest pointer file as well as the oldest, so it stands inside the window on the strength of
    the newest — which is what makes this a retention rule about cuts rather than about bytes.

    AND TWO SETS STAND OUTSIDE ALL OF IT, both of them a cut that has not finished landing. The
    pointer file on disk names a cut whose bytes are up and whose commit is not made; this tree is the
    one shared record of it, so it is read here beside the committed ones — and it is the
    NEWEST cut there is, so it stands inside the window as well as inside reach.
    `RETIRE_FLOOR_S` covers the upload in front of that, where the bytes are on the release and
    no pointer file names them at all.

    WHAT THE COMMITTED POINTER FILES ALONE LEAVE OPEN IS THE WHOLE CUT. Asked of this tree on
    2026-08-28 with the newest pointer file commit held back — the history a sweep reads while that
    cut is still landing — reach off the committed pointer files alone missed 7 of that cut's 271
    assets, one of them the bundle tarball. `make_room` is the only caller and it runs inside
    a publish, so the sweep and the upload it would delete are the same minute.
    """
    if _shallow(root):
        raise SystemExit(
            "this clone is shallow, so reach read off its history is short and a sweep would "
            "take assets a full checkout still resolves to — measured on 2026-08-27, 74 of 354 "
            "against 0 from the whole history. Fetch it all (actions/checkout `fetch-depth: 0`) "
            "before asking what may be retired.")
    assets = release_assets(root)
    history = [list(cut) for cut in pointer_files_in_history(root)]
    return tuple(_native("retirable", assets=assets, history=history,
        disk=list(pointer_assets(read_pointers(root))), keep_cuts=keep_cuts,
        now=time.time() if now is None else now, floor=RETIRE_FLOOR_S))


def held_and_free(root: Path) -> tuple:
    """How full the release is — a question about the release, not about this clone's history.

    SEPARATE FROM `room` BECAUSE THE GUARD IS. Whether there is space costs one `gh` call and
    is true anywhere; WHICH assets may leave is read off every committed pointer file, and a clone that
    does not hold them must not be asked. `make_room` wants the first on every publish and the
    second only at the cliff, so asking them together is what put a shallow tree in front of a
    sweep."""
    return tuple(_native("release-space", assets=release_assets(root), capacity=RELEASE_ASSET_CAP))


def room(root: Path, keep_cuts: int = CUTS_KEPT) -> dict:
    """How many assets the release holds, how many it can still take, and what could leave."""
    held, _free = held_and_free(root)
    unreachable, superseded = retirable(root, keep_cuts)
    return _native("release-room", held=held, capacity=RELEASE_ASSET_CAP,
                   unreachable=unreachable, superseded=superseded)


def retire(root: Path, keep_cuts: int = CUTS_KEPT, unreachable_only: bool = False) -> int:
    """Take the retirable assets off the release, unreachable first, and report the room won."""
    import concurrent.futures as cf

    state = room(root, keep_cuts)
    going = _native("retire-plan", state=state, unreachable_only=unreachable_only)
    if not going:
        print(f"release holds {state['held']} of {RELEASE_ASSET_CAP}; nothing to retire")
        return 0
    print(f"release holds {state['held']} of {RELEASE_ASSET_CAP} — "
          f"{len(state['unreachable'])} asset(s) no commit names"
          + ("" if unreachable_only
             else f", {len(state['superseded'])} outside the last {keep_cuts} cut(s)"))

    def drop(name: str):
        """Take one asset off. Returns the name on failure, None on success."""
        return None if _gh(root, "release", "delete-asset", TAG, name,
                           "--yes").returncode == 0 else name

    # FOUR AT A TIME, BECAUSE `gh` SPENDS THE DELETE WAITING. `delete-asset` resolves the name
    # against the release's whole listing before it removes anything, and eight round trips
    # measured on 2026-08-28 against a release holding 981 assets ran 1.90 s each serially,
    # 0.62 s each four-wide and 0.60 s each eight-wide — the client saturates at four. This
    # sweep runs from `make_room` inside a publish, on the post-commit path, and the 648 assets
    # retirable that night are 20.5 minutes of it serially.
    with cf.ThreadPoolExecutor(max_workers=min(4, len(going))) as pool:
        failed = [name for name in pool.map(drop, going) if name]
    for name in failed:
        print(f"  {name} did not come off")
    left = len(release_assets(root))
    print(f"{len(going) - len(failed)} asset(s) retired; release holds {left} of "
          f"{RELEASE_ASSET_CAP}, {RELEASE_ASSET_CAP - left} free")
    return 1 if failed else 0


def make_room(root: Path, need: int) -> bool:
    """Free enough of the release for a cut of `need` assets, and say whether anything left it.

    CALLED BEFORE THE UPLOAD AND NOT AFTER THE FAILURE, because the failure is silent. `gh`
    reports a refused upload the same way it reports a network flake, and the only reader of
    that is `upload_objects`, which turns off `objects` and carries on.

    THE ANSWER MATTERS TO THE CALLER because a reading of the release taken before this one is
    stale after it: a sweep takes assets an older pointer file's window held, and a caller still
    holding the earlier `objects_on_release` would skip sending an object the release no longer
    has — and then claim `objects` over a set it is short of.
    """
    held, free = held_and_free(root)
    if free >= need:
        return False
    print(f"  release holds {held} of {RELEASE_ASSET_CAP} and this cut wants {need}")
    # A SHALLOW CLONE DOES NOT SWEEP, IT SAYS SO. At `fetch-depth: 1` reach is read off a single
    # pointer file and all but the newest cut looks unreachable — so the cliff is exactly where
    # this would have deleted the bytes older commits resolve to.
    # Declining costs a publish its `objects` lane, which `upload_objects` already degrades
    # gracefully; sweeping wrongly costs the release. `.github/workflows/retire.yml` holds the
    # store down from a full history so this floor is not reached.
    if _shallow(root):
        print("  this clone is shallow, so what is reachable cannot be read here and nothing "
              "is swept; the `retire` workflow keeps the release below this")
        return False
    retire(root)
    return True


def objects_on_release(root: Path) -> set:
    """Every member sha the release already holds as its own asset.

    ASKED, NOT INFERRED. The previous pointer file's shas say where those bytes were, not that an asset
    holds them — a pointer file written before these existed names members that only ever went up inside
    the bundle. Reading the release answers for a hand backfill, an upload that failed last time
    and a member reverting to bytes some older pointer file named, all the same way and without any of
    them being special cases.
    """
    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        return set()
    return set(_native("objects-on-release", assets=json.loads(listing.stdout).get("assets", []),
                       prefix=OBJECT_PREFIX))


def objects_to_send(rels: list, solid_hashes: dict, known: set) -> list:
    """Which members `upload_objects` actually puts up: one per hash the release lacks.

    ONE ASSET PER HASH, NOT PER MEMBER. The name is the hash, so two members carrying the same
    bytes are one asset — and sending both puts two concurrent `--clobber` uploads on one name,
    where one wins and the other reports a failure for a member that is demonstrably up. That
    failure costs the pointer file its `objects`, and every deploy then reads the whole bundle for
    members it already holds. The second member of a pair is not a second send; it is already
    there when the first lands."""
    return _native("objects-to-send", rels=rels, hashes=solid_hashes, known=list(known))


def put_object(url: str, staged: Path) -> bool:
    """One gzipped member up to the store by hash; True when the store holds it afterwards."""
    from urllib.request import Request, urlopen

    try:
        req = Request(url, data=staged.read_bytes(), method="PUT",
                      headers={"Content-Type": "application/gzip", "User-Agent": "pack.py"})
        with urlopen(req, timeout=300) as resp:
            return resp.status in (200, 201)
    except Exception as exc:  # noqa: BLE001 — the caller falls back and names the failure
        print(f"  {url.rsplit('/', 1)[-1]}: the store did not take it ({exc})")
        return False


def objects_in_store(hashes) -> set:
    """Which of these hashes the store already holds, asked one by one; a store that does not
    answer holds nothing, and every member is sent."""
    from urllib.request import Request, urlopen
    import concurrent.futures as cf

    def present(digest):
        try:
            with urlopen(Request(STORE_URL + object_asset(digest), method="HEAD",
                                 headers={"User-Agent": "pack.py"}), timeout=30) as resp:
                if resp.status == 200:
                    return digest
        except Exception:  # noqa: BLE001 — absent or unreachable reads the same: send it
            pass
        return None
    values = _native("unique", values=list(hashes))
    with cf.ThreadPoolExecutor(max_workers=max(1,min(4,len(values)))) as pool:
        return {digest for digest in pool.map(present,values) if digest}


def upload_objects(root: Path, rels: list, solid_hashes: dict, known: set, sources=None) -> bool:
    """Upload changed members by digest, using the release when the store cannot accept them."""
    import concurrent.futures as cf
    import tempfile

    todo = objects_to_send(rels, solid_hashes, known)
    if not todo:
        print("  every member is already on the release under its own hash")
        return True

    # Compressed objects are reusable by the digest of their uncompressed geometry.
    cache = root / ".cache" / "meshes" / "publication"
    cache.mkdir(parents=True, exist_ok=True)
    compressed = {rel: cache / object_asset(solid_hashes[rel]) for rel in todo}
    _native("gzip-many", files=[{"source": str((sources or {}).get(rel, root / rel)), "output": str(compressed[rel])}
                               for rel in todo], level=1)
    import threading
    fallback_lock = threading.Lock()
    fallback_ready = False

    def send(rel):
        nonlocal fallback_ready
        sha = solid_hashes[rel]
        staged = compressed[rel]
        if put_object(STORE_URL + object_asset(sha), staged):
            return None
        with fallback_lock:
            if not fallback_ready:
                make_room(root, len(todo))
                fallback_ready = True
        return None if _gh(root, "release", "upload", TAG, str(staged),
                           "--clobber").returncode == 0 else rel

    with cf.ThreadPoolExecutor(max_workers=min(4, len(todo))) as pool:
        failures = [r for r in pool.map(send, todo) if r]
    for rel in failures:
        print(f"  {rel} did not upload as {object_asset(solid_hashes[rel])}")
    print(f"  {len(todo) - len(failures)} of {len(todo)} changed object(s) uploaded on their own hash"
          + (f"; {len(failures)} did not, so this pointer file is read from the bundle" if failures else ""))
    return not failures


def upload_mesh_assets(root: Path, rels: list, held: dict, sources=None, lines=None, keep_previous=False) -> list:
    """Shared scene objects go up before any manifest that refers to them."""
    import concurrent.futures as cf
    sys.path.insert(0, str(root / "hardware/scripts"))
    from _build_data import request
    manifests = {str((sources or {}).get(rel, root / rel)): (lines or {}).get(rel)
                 for rel in rels if rel.endswith((".step.mesh", ".glb.mesh"))}
    assets = request("scene-assets", paths=list(manifests), expected=manifests)
    known = set(held.get("mesh_assets") or [])
    todo = [row for row in assets if row["sha256"] not in known]
    present = objects_in_store([row["sha256"] for row in todo])
    todo = [row for row in todo if row["sha256"] not in present]
    cache = root / ".cache/meshes/publication"
    cache.mkdir(parents=True, exist_ok=True)
    _native("gzip-many", files=[{"source": row["path"], "output": str(cache / object_asset(row["sha256"]))}
                               for row in todo], level=1)
    def send(row):
        sha = row["sha256"]
        if not put_object(STORE_URL + object_asset(sha), cache / object_asset(sha)):
            raise RuntimeError(f"mesh object {sha} did not upload")
    with cf.ThreadPoolExecutor(max_workers=max(1,min(4,len(todo)))) as pool:
        list(pool.map(send,todo))
    if todo:
        print(f"  {len(todo)} shared mesh object(s) uploaded")
    current = {row["sha256"] for row in assets}
    return sorted(current | known if keep_previous else current)


def upload(root: Path, bundle: Path, asset: str, digest: str, size: int) -> None:
    """Put `bundle` on the release as `asset`, making the release if it is not there yet.

    The name carries the bundle's own hash, so a name already on the release holds these bytes
    and the upload is skipped. An upload that died partway also leaves the name taken, holding a
    truncated asset — `--clobber` is what lands on that one."""
    import tempfile

    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        made = _gh(root, "release", "create", TAG,
                   "--title", "CAD artifacts",
                   "--notes", "Generated solids for the /3d viewer, fetched at deploy by "
                              "web/scripts/fetch-cad-artifacts.mjs. Each asset is named by its "
                              "own sha256 and pointed at from hardware/cad-artifacts.json.")
        if made.returncode != 0:
            raise SystemExit(f"gh release create failed:\n{made.stderr}")
    else:
        state = _native("release-state", assets=json.loads(listing.stdout).get("assets", []),
                        asset=asset, digest=digest, size=size)
        if state["matches"]:
            print(f"  {asset} is already on the release at the verified size and digest")
            return
        if state["exists"]:
            print(f"  {asset} exists without the expected size/digest — replacing it")
    with tempfile.TemporaryDirectory() as d:
        staged = Path(d) / asset
        _native("copy-file", source=bundle, output=staged)
        up = _gh(root, "release", "upload", TAG, str(staged), "--clobber")
    if up.returncode != 0:
        raise SystemExit(f"gh release upload failed:\n{up.stderr}")
    print(f"  uploaded {asset}")


def made_here(root: Path, held: dict, graph: Graph, index: dict, head: str, lines: dict,
              walked: dict, moved: set, grafted: set = frozenset()) -> dict:
    """The `made` a held publish writes for `lines`.

    A member of `moved` cut after every input it reads is recorded off the ids of those inputs
    on this disk, with `walked` holding each member's hash as this disk held it before anything
    was adopted. The rest of `moved`, and whatever the enclosure graft wrote, has nothing to say
    what cut it."""
    return _unorder(_native("made-here", root=root, held=held, held_order=_ordered(held),
        graph=graph._wire(), index=index, head=head, lines=lines, walked=walked,
        moved=list(moved), grafted=list(grafted), frozen=list(frozen_assets(root)),
        skew_ns=GENERATED_SKEW_NS))


def _unproven(made: dict) -> str:
    return _native("unproven", made=made)


def _bundle_on_release(held: dict, rels: list) -> None:
    """The bundle the pointer file names, put back on the release where the release does not
    hold it at its size and digest."""
    import tempfile

    release, bundle = held.get("release", {}), held.get("bundle", {})
    if _release_asset_matches(_ROOT, release.get("asset", ""), bundle.get("sha256", ""),
                              bundle.get("bytes", -1)):
        return
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "bundle.tar.gz"
        digest = build(_ROOT, rels, path)
        if digest != bundle.get("sha256"):
            raise SystemExit("equal member hashes built a different bundle digest")
        upload(_ROOT, path, release["asset"], digest, path.stat().st_size)


def cut_whole_bundle(held: dict, rels: list, now: dict, sidecar_now: dict, made: dict) -> int:
    """The bundle a held publish left behind, cut whole and pointed at.

    The members it lacked are on the release by their own hashes, which is what a reader
    fetches by; this is the one asset that answers a pointer file without `objects`, made current
    by the reconciler's plain `--write`. The members and their hashes are the pointer file's own;
    only the bundle and the `made` lines move."""
    import tempfile

    release = held.get("release", {})
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "bundle.tar.gz"
        digest = build(_ROOT, rels, path)
        size = path.stat().st_size
        data = pointers_for(_ROOT, rels, digest, size, now, sidecar_now, made, held=held)
        if release.get("objects"):
            data = _patch(data, [(('release', 'objects'), release["objects"])])
        make_room(_ROOT, 1)
        upload(_ROOT, path, data["release"]["asset"], digest, size)
    _write_pointers(data)
    print(f"bundle {data['release']['asset']} — {size / 1e6:.1f} MB, cut whole behind the "
          f"held publish that left {release.get('asset')} behind")
    return 0


def cut_bundle(held: dict, rels: list, now: dict, sidecar_now: dict, made: dict,
               known: set, stamp: float = None) -> int:
    """A whole bundle of `rels` up on the release with every member it lacks, and pointed at."""
    import tempfile

    total = _native("total-bytes", root=_ROOT, rels=rels)
    with tempfile.TemporaryDirectory() as d:
        bundle = Path(d) / "bundle.tar.gz"
        digest = build(_ROOT, rels, bundle)
        size = bundle.stat().st_size
        data = pointers_for(_ROOT, rels, digest, size, now, sidecar_now, made, held=held, stamp=stamp)
        print(f"bundle {data['release']['asset']} — {size / 1e6:.1f} MB "
              f"({100 * size / total:.0f}% of the tree's bytes)")
        # THIS CUT'S OWN BUNDLE PLUS EVERY MEMBER THAT MOVED, asked for before a byte goes up.
        # AND ASKED AGAIN AFTERWARDS, because retiring is what winning the room means. A member
        # this pointer file does not name can stand on the release under an older pointer file's window and go
        # in the same sweep — `known` was read before that and would have this run skip an
        # object it no longer holds, leaving `objects` claiming a set the release is short of.
        if make_room(_ROOT, _native("object-count", rels=rels, hashes=now, known=list(known), extra=1)):
            known = objects_on_release(_ROOT)
        upload(_ROOT, bundle, data["release"]["asset"], digest, size)
        complete = upload_objects(_ROOT, rels, now, known)

    # `objects` says EVERY member of this pointer file is on the release under its own hash, so a reader
    # may fetch what it is missing rather than the whole bundle. One upload that did not land
    # leaves it off, and the pointer file is read from the bundle the way a pointer file without it is — the
    # claim is about the whole set, so a partial one is not a smaller claim but a false one.
    if complete:
        data = _patch(data, [(('release', 'objects'), OBJECT_PREFIX)])

    _write_pointers(data)
    print(f"pointed at from {POINTERS.relative_to(_ROOT)}{_unproven(made)}")
    return 0


def publish_held(grafted: set, viewer_only=False, members=None) -> int:
    """Each publication holds only its changed objects while their producers continue."""
    import tempfile
    directory = _ROOT / ".cache/runs"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="publication-", dir=directory) as staging:
        return _publish_held(grafted, Path(staging), viewer_only, members)


def _measured(phase, started):
    """Requested measurements separate publication work from network delivery."""
    target = os.environ.get("HSM_PUBLISH_TIMING")
    if target:
        with open(target, "a") as log:
            log.write(json.dumps({"phase": "pack."+phase, "pid": os.getpid(),
                                  "wall_time_ns": time.time_ns(),
                                  "seconds": time.monotonic()-started})+"\n")
    return time.monotonic()


def _publish_held(grafted: set, staging: Path, viewer_only=False, members=None) -> int:
    """`--write --publish-held`: what this machine cut since main's pointers moved goes up on its
    own hash, and each member's `made` line moves with what moved. Nothing here asks Bazel.

    WHAT A HELD PUBLISH MOVES IS WHAT THIS MACHINE CUT, and the rest of the file is main's. A
    copy older than its line is taken from the release before anything else is decided, so the
    lines describe a disk that holds main's bytes for every member this machine did not cut."""
    # Pointer times identify when this cut's member bytes are collected.
    captured = time.time()
    phase_started = time.monotonic()
    held = read_pointers()
    graph = Graph.load(_ROOT)
    index = staged(_ROOT)
    head = _head(_ROOT)
    rels = solids(_ROOT)
    if members is not None:
        selected = set(members)
        rels = [rel for rel in rels if rel in selected]
    if viewer_only:
        rels = [rel for rel in rels if rel.endswith((".step.mesh", ".glb.mesh"))]
    sys.path.insert(0,str(_ROOT / "hardware/scripts"))
    from _build_data import request
    obsolete = set(request("scene-obsolete",root=str(_ROOT),paths=list(held.get("solids",{}))))
    if obsolete:
        held = {**held,"solids":{path:sha for path,sha in held.get("solids",{}).items() if path not in obsolete},
                "made":{path:line for path,line in held.get("made",{}).items() if path not in obsolete}}
        rels = [path for path in rels if path not in obsolete]
        print(f"  {len(obsolete)} standalone export(s) retired by their shared-scene producers")
    now = hashes(_ROOT, rels)
    sidecar_now = held.get("sidecars", {}) if viewer_only else sidecar_lines(_ROOT, held, graph)
    walked = _native("merge-lines", maps=[now, sidecar_now])
    mtimes = _native("mtimes", root=_ROOT, rels=rels) if held.get("solids") else {}
    state = _native("held-state", held=held, rels=rels, now=now, sidecar_now=sidecar_now, mtimes=mtimes)
    if held.get("solids"):
        if state["stale"]:
            print(f"{len(state['stale'])} member(s) on this disk are older than main's pointers; taking main's bytes")
            taken = adopt(_ROOT, held, state["stale"])
            now = _native("updated-lines", held=now, new=held["solids"], paths=taken)
        if state["absent"]:
            print(f"{len(state['absent'])} member(s) main points at are not on this disk; their lines stand")
        if state["pinned"]:
            print(f"{len(state['built'])} member(s) cut here since main's pointers moved and {len(state['fresh'])} new; those lines move")
    state = _native("held-state", held=held, rels=rels, now=now, sidecar_now=sidecar_now, mtimes=mtimes)
    pinned, side_moved, lines = state["pinned"], state["side_moved"], state["lines"]
    moved = set(state["moved"])
    stable = _native("freeze", directory=staging,
                     files=[{"relative":rel,"source":_ROOT / rel} for rel in pinned])
    sources = {row["relative"]: Path(row["source"]) for row in stable}
    for row in stable:
        now[row["relative"]] = row["sha256"]
        lines[row["relative"]] = row["sha256"]
        walked[row["relative"]] = row["sha256"]
    whole_lines = _native("merge-lines", maps=[lines, sidecar_now])
    if viewer_only:
        # Surface references carry their exact source bindings; input-proof bookkeeping follows them.
        made = dict(held.get("made", {}))
        for rel in moved:
            made[rel] = {**made.get(rel, {}), "commit": head, "unproven": True}
    else:
        made = made_here(_ROOT, held, graph, index, head, whole_lines, walked, moved, grafted)

    if not pinned:
        records = _native("held-record-state", held=held, made=made, side_moved=side_moved,
                          website=website_for(_ROOT, held))
        if records["unchanged"]:
            print("no unpublished bytes or `made` lines are held")
            return 0
        held = _patch(held, [(('sidecars',), sidecar_now), (('made',), made)])
        _write_pointers(held)
        print(f"{len(side_moved)} scorecard(s) and {records['shifted']} `made` line(s) moved, and no member's bytes{_unproven(made)}")
        return 0

    phase_started = _measured("plan", phase_started)
    asset_members = pinned if viewer_only else [rel for rel in lines if (_ROOT / rel).is_file()]
    mesh_assets = upload_mesh_assets(_ROOT, asset_members, held, sources, lines, keep_previous=viewer_only)
    phase_started = _measured("mesh-objects", phase_started)
    known = set()
    prior_bundle = held.get("bundle", {})
    if prior_bundle.get("sha256"):
        pin_hashes = _native("map-values", data=now, paths=pinned)
        known = set(_native("set-plan", first=list(known), second=list(objects_in_store(pin_hashes)))["union"])
        phase_started = _measured("member-heads", phase_started)
        if upload_objects(_ROOT, pinned, now, known, sources):
            phase_started = _measured("members", phase_started)
            data = pointers_for(_ROOT, sorted(lines), prior_bundle["sha256"],
                                prior_bundle.get("bytes", 0), lines, sidecar_now, made, held=held,
                                stamp=captured)
            data = _patch(data, [(('mesh_assets',), mesh_assets), (('bundle',), prior_bundle), (('bundle', 'behind'), True),
                                 (('release', 'objects'), OBJECT_PREFIX)])
            _write_pointers(data)
            print(f"{len(pinned)} member(s) up on their own hash; {data['release']['asset']} stays behind for the reconciler")
            print(f"pointed at from {POINTERS.relative_to(_ROOT)}{_unproven(made)}")
            return 0
        if viewer_only or members is not None:
            print("  completed members remain unpublished; the current pointer stays")
            return 1
        print("  not every object landed; cutting the bundle so this pointer file reads whole")
        known = objects_on_release(_ROOT)
    return cut_bundle(held, rels, now, sidecar_now,
                      made_here(_ROOT, held, graph, index, head, state["whole"], walked, moved, grafted),
                      known, stamp=captured)


def main(argv) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", choices=["selftest"])
    ap.add_argument("--write", action="store_true", help="build, upload and move the pointer file")
    ap.add_argument("--publish-held", action="store_true",
                    help="with --write, publish bytes already on disk without cutting their "
                         "producer rules")
    ap.add_argument("--viewer-only", action="store_true",
                    help="with --publish-held, advance viewer members while manufacturing files retain their current lines")
    ap.add_argument("--members-json", help="with --publish-held, publish only these completed members")
    ap.add_argument("--grafted", action="append", default=[], metavar="PATH",
                    help="with --publish-held, a member the enclosure graft wrote")
    ap.add_argument("--check", action="store_true", help="1 if the pointer file does not name this tree")
    ap.add_argument("--prune", action="store_true",
                    help="remove pointed-at members no longer declared by the build graph")
    ap.add_argument("--retire", action="store_true",
                    help="take unreachable and superseded assets off the release")
    ap.add_argument("--room", action="store_true",
                    help="print how much of the release is left and what could leave it")
    ap.add_argument("--keep-cuts", type=int, default=CUTS_KEPT, metavar="N",
                    help=f"with --retire/--room, cuts to keep whole (default {CUTS_KEPT})")
    ap.add_argument("--sidecar-debt", action="store_true",
                    help="print producers whose viewer scorecards do not match the pointer file")
    ap.add_argument("--allow-retired", action="store_true",
                    help="with --prune, confirm graph retirements lacking source evidence")
    args = ap.parse_args(argv)

    if args.publish_held and not args.write:
        ap.error("--publish-held is only valid with --write")
    if args.grafted and not args.publish_held:
        ap.error("--grafted is only valid with --publish-held")
    if args.mode == "selftest":
        return selftest()
    if args.room:
        if args.write or args.check or args.prune or args.retire:
            ap.error("--room is a separate read-only query")
        state = room(_ROOT, args.keep_cuts)
        print(f"release holds {state['held']} of {RELEASE_ASSET_CAP}; {state['free']} free")
        print(f"  {len(state['unreachable'])} asset(s) no commit's pointer file names")
        print(f"  {len(state['superseded'])} asset(s) outside the last {args.keep_cuts} cut(s)")
        return 0
    if args.retire:
        if args.write or args.check or args.prune:
            ap.error("--retire is a separate explicit step")
        return retire(_ROOT, args.keep_cuts)
    if args.sidecar_debt:
        if args.write or args.check or args.prune or args.allow_retired:
            ap.error("--sidecar-debt is a separate read-only query")
        for target in sidecar_debt_targets(_ROOT):
            print(target)
        return 0
    if args.prune:
        if args.write or args.check:
            ap.error("--prune is a separate explicit step")
        return prune(_ROOT, args.allow_retired)
    if args.allow_retired:
        ap.error("--allow-retired is only valid with --prune")
    if args.publish_held:
        return publish_held(set(args.grafted), args.viewer_only,
                            json.loads(args.members_json) if args.members_json is not None else None)

    graph = Graph.load(_ROOT)
    rels = solids(_ROOT)
    total = _native("total-bytes", root=_ROOT, rels=rels)
    print(f"{len(rels)} generated solid(s), {total / 1e6:.1f} MB in the tree")

    # A SCORECARD THE GRAPH DECLARES AND THE TREE DOES NOT HOLD IS NOT PINNABLE, and that is the
    # whole of what follows from it. It keeps the line it has and the rest are pointed at around it.
    declared_sidecars = sidecars(_ROOT, graph)
    sidecar_rels = _native("existing", root=_ROOT, paths=declared_sidecars)
    for rel in _native("set-plan", first=declared_sidecars, second=sidecar_rels)["difference"]:
        print(f"  no scorecard in the tree for a rule that declares one: {rel}")

    loose, missing = _graph_gaps(_ROOT, rels)
    if loose:
        print(f"  {len(loose)} bundled solid(s) no rule declares, recorded and shipped:")
        for rel in loose[:8]:
            print(f"    {rel}")
    if missing:
        print(f"  {len(missing)} declared publish output(s) are absent from the tree:")
        for rel in missing[:8]:
            print(f"    {rel}")

    held = read_pointers()
    now = hashes(_ROOT, rels)

    # AN EMPTY SOLID IS WHAT THIS TREE HOLDS FOR THAT PART, so it ships and the record names it.
    # A part that renders as nothing is the state of the work, told on the site rather than here.
    for line in barren(_ROOT, now):
        print(f"  {line}")

    # Retirement takes a public thing away, which `--prune` does deliberately and this does not.
    # A scorecard whose producer is gone keeps the pointer it has until that runs.
    kept = _native("set-plan", first=list(held.get("sidecars", {})), second=sidecar_rels)["difference"]
    if kept:
        print(f"  {len(kept)} scorecard(s) hold their point at; --prune retires one")
    sidecar_now = sidecar_lines(_ROOT, held, graph)
    made = held.get("made") or {}
    if args.write:
        index, head = staged(_ROOT), _head(_ROOT)
        reached, dirty = _dirty_artifact_reach(_ROOT)
        was = _native("merge-lines", maps=[held.get("solids", {}), held.get("sidecars", {})])
        lines = _native("merge-lines", maps=[now, sidecar_now])
        bytes_moved = set(_native("changed-lines", old=was, new=lines))
        tree = tree_digests(_ROOT, graph, lines, index)
        debt = _native("set-plan", first=_owed_artifact_targets(_ROOT, made, tree),
                       second=_targets_for_members(_ROOT, bytes_moved)[0])["union"]
        # A rule an uncommitted edit reaches has nothing at HEAD to be cut against, and the
        # record is what says so; the rest are cut and carried here.
        would_not_cut, unheld = carry_the_cut(_ROOT, _native("set-plan", first=debt, second=reached)["difference"])
        carried = set(_native("set-plan", first=debt, second=reached, third=would_not_cut)["remaining"])
        # The carry writes bazel-bin into the tree, so the bytes this points at are read after it.
        rels = solids(_ROOT)
        now = hashes(_ROOT, rels)
        sidecar_now = sidecar_lines(_ROOT, held, graph)
        lines = _native("merge-lines", maps=[now, sidecar_now])
        tree = tree_digests(_ROOT, graph, lines, index)
        # A MEMBER THIS TREE HOLDS THE CUT OF IS WHAT ITS INPUTS ON THIS DISK MAKE. One whose
        # bytes are not that cut's, or that reads one, is refuted, whatever its line said.
        derived = set(_native("derived-members", members=list(_members_of_targets(_ROOT, carried)),
                              tree=tree, unheld=list(unheld), graph=graph._wire()))
        cut = _native("cut-digests", root=_ROOT, graph=graph._wire(), index=index,
                      lines=lines, members=lines, paths=list(derived))
        bytes_moved = _native("changed-lines", old=was, new=lines)
        uncut = _native("set-plan", first=bytes_moved, second=list(derived))["difference"]
        made = made_for(made, lines, head, tree, cut, derived, uncut, unheld, frozen=frozen_assets(_ROOT))
        if _unproven(made):
            print(f"{head[:12]}:{_unproven(made)}")
            for path in dirty[:8]:
                print(f"  uncommitted: {path}")
    state = _native("reconcile-state", held=held, now=now, sidecars=sidecar_now)
    same_solids, same_sidecars = state["same_solids"], state["same_sidecars"]
    if same_solids and same_sidecars:
        if args.write:
            release = held.get("release", {})
            if held.get("bundle", {}).get("behind"):
                return cut_whole_bundle(held, rels, now, sidecar_now, made)
            _bundle_on_release(held, rels)
            # AND THE OBJECT PATH, WHICH NOTHING ELSE PUTS BACK. `objects` is written only where
            # a cut moves geometry, so a pointer file that lost it cannot regain it while the tree
            # stands still — and losing it takes one refused upload, which a full release gives
            # every one of them. The fast path then stays off and every deploy reads the whole
            # tarball for members it already has. The members are named by their own bytes and
            # this tree holds those bytes, so what the release is missing goes up without
            # cutting anything and without the pointer file naming a different asset.
            known = objects_on_release(_ROOT)
            if make_room(_ROOT, _native("object-count", rels=rels, hashes=now, known=list(known))):
                known = objects_on_release(_ROOT)
            whole = upload_objects(_ROOT, rels, now, known)
            records = _native("reconcile-records", held=held, held_order=_ordered(held),
                              made=made, made_order=_ordered(made), complete=whole,
                              prefix=OBJECT_PREFIX, website=website_for(_ROOT, held))
            if records["changed"]:
                held = _unorder(records["ordered"])
                _write_pointers(held)
                print(f"pointer file names this tree — {held['release']['asset']}; its records "
                      f"moved{_unproven(made)}")
                return 0
        print(f"pointer file names this tree — {held['release']['asset']}")
        return 0

    moved, fresh, gone = state["solids"]
    side_moved, side_fresh, side_gone = state["sidecars"]
    if not held:
        print("no pointer file yet — `--write` makes one")
    else:
        print(f"pointer file is behind: {len(moved)} moved, {len(fresh)} new, {len(gone)} gone")
        for rel in (moved + fresh + gone)[:8]:
            print(f"    {rel}")
        if side_moved or side_fresh or side_gone:
            print(f"  scorecards: {len(side_moved)} moved, {len(side_fresh)} new, "
                  f"{len(side_gone)} gone")
            for rel in (side_moved + side_fresh + side_gone):
                print(f"    {rel}")
    if not args.write:
        # NOBODY HAS TO DO THIS. `.githooks/post-commit` runs `tools/publish_now.py` detached
        # after every commit, and that cuts and points at exactly what is named above — so a pointer file
        # standing behind the tree is a pointer file whose commit has not been made yet, or one whose
        # publish is still running. Saying "run --write" here without saying that is what sends
        # a reader off to run it by hand, against a publish already in flight; the two race, and
        # the second one lands on a tree the first has already moved.
        print("  the pointer file is written by the post-commit hook, from the commit that moves it:")
        print("    git commit      # tools/publish_now.py cuts and points at this, detached")
        print("    tail .cache/publish-now.log      # what it did, or why it could not")
        print("  --write forces it from here, which is only wanted when there is no commit to")
        print("  make and no publish already running.")
        return 1 if args.check else 0

    if same_solids:
        release = held.get("release", {})
        if held.get("bundle", {}).get("behind"):
            return cut_whole_bundle(held, rels, now, sidecar_now, made)
        _bundle_on_release(held, rels)
        held = _patch(held, [(('sidecars',), sidecar_now), (('made',), made)])
        _write_pointers(held)
        print(f"pointed at current scorecards without rebuilding {release['asset']}")
        return 0

    return cut_bundle(held, rels, now, sidecar_now, made, objects_on_release(_ROOT))


def selftest() -> int:
    import datetime as dt
    import gzip
    import shutil
    import tarfile
    import tempfile

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        hw = root / "hardware"
        (hw / "printed-parts" / "cap").mkdir(parents=True)
        (hw / "printed-parts" / "cap" / "cap.step").write_text("ISO-10303-21;\n")
        (hw / "assembly" / "scenes" / "out").mkdir(parents=True)
        (hw / "assembly" / "scenes" / "out" / "scene.step").write_text("intermediate\n")
        (hw / "reference" / "y-divider").mkdir(parents=True)
        (hw / "reference" / "y-divider" / "y-divider.step").write_text("harvested\n")
        (hw / "printed-parts" / "cap" / ".cap.step.999.ab.step").write_text("orphan temp\n")

        hold("a generated solid is carried",
             solids(root), ["hardware/printed-parts/cap/cap.step"])

        (hw / "printed-parts" / "cap" / "cap.step.png").write_text("picture")
        (hw / "printed-parts" / "cap" / "cap.step.mesh").write_text("mesh")
        hold("what sits beside a solid is not a solid",
             solids(root), ["hardware/printed-parts/cap/cap.step"])

        # EXCEPT WHERE THE SOLID IS NOT THE WHOLE OF THE PART. A payload under a named directory
        # is the only copy of a fluted surface a browser can reach, so it travels; the one beside
        # `cap.step` above is a tessellation of a solid the bundle already carries, and does not.
        payload_dir = hw / "printed-parts" / "enclosure" / "enclosure"
        payload_dir.mkdir(parents=True)
        (payload_dir / "piece.step").write_text("ISO-10303-21;\n")
        (payload_dir / "piece.step.mesh").write_text("payload")
        (payload_dir / "piece.step.png").write_text("picture")
        hold("a payload under a named directory travels with its solid",
             solids(root), ["hardware/printed-parts/cap/cap.step",
                            "hardware/printed-parts/enclosure/enclosure/piece.step",
                            "hardware/printed-parts/enclosure/enclosure/piece.step.mesh"])

        graph_dir = root / "tools" / "bazel"
        graph_dir.mkdir(parents=True)
        graph = {"piece.py": {"writes": [
            "hardware/printed-parts/cap/cap.step",
            "hardware/printed-parts/enclosure/enclosure/piece.step",
            "hardware/printed-parts/cap/cap.scorecard.json",
        ]}}
        scorecard = hw / "printed-parts" / "cap" / "cap.scorecard.json"
        scorecard.write_text('{"gatesPass": true}\n')
        (graph_dir / "graph.json").write_text(json.dumps(graph))
        hold("a declared scorecard is pointed at outside the bundle",
             sidecars(root), ["hardware/printed-parts/cap/cap.scorecard.json"])
        hold("a payload needs its own declared output",
             _undeclared(root, solids(root)),
             ["hardware/printed-parts/enclosure/enclosure/piece.step.mesh"])
        graph["piece.py"]["writes"].append(
            "hardware/printed-parts/enclosure/enclosure/piece.step.mesh")
        (graph_dir / "graph.json").write_text(json.dumps(graph))
        hold("an exactly declared publish inventory passes",
             _graph_gaps(root, solids(root)), ([], []))
        (hw / "cad-artifacts.json").write_text(json.dumps({
            "solids": {
                "hardware/printed-parts/cap/cap.step": "kept",
                "hardware/retired/old.step": "gone",
            },
            "sidecars": {
                "hardware/printed-parts/cap/cap.scorecard.json": "kept",
                "hardware/retired/old.scorecard.json": "gone",
            },
        }))
        hold("retired solids and scorecards leave the pointer file together",
             retired_outputs(root), ["hardware/retired/old.scorecard.json",
                                     "hardware/retired/old.step"])
        hold("a scorecard the tree does not hold keeps the line it has",
             sidecar_lines(root, read_pointers(root)),
             {"hardware/retired/old.scorecard.json": "gone",
              "hardware/printed-parts/cap/cap.scorecard.json": _sha256(scorecard)})

        hold("a pointer file names its bundle and one asset per member and scorecard sha",
             sorted(pointer_assets({"solids": {"a.step": "aa"},
                                 "sidecars": {"a.scorecard.json": "bb"},
                                 "release": {"asset": "cad-cc.tar.gz"}})),
             ["cad-cc.tar.gz", object_asset("aa"), object_asset("bb")])

        # WHAT A SWEEP MAY NOT TAKE IS A CUT STILL LANDING. `--write` uploads before it writes
        # its pointer file and commits after, so an asset can be on the release while no committed pointer file
        # names it — and deleting one leaves a pointer file naming bytes the release does not hold.
        clock = 1_700_000_000.0

        def born(ago):
            return dt.datetime.fromtimestamp(clock - ago, dt.timezone.utc
                                             ).strftime("%Y-%m-%dT%H:%M:%SZ")

        hold("an asset inside the floor stays, and so does one carrying no date",
             sorted(too_new([{"name": "settled.gz", "createdAt": born(RETIRE_FLOOR_S + 60)},
                             {"name": "landing.gz", "createdAt": born(60)},
                             {"name": "undated.gz"}], clock)),
             ["landing.gz", "undated.gz"])

        (hw / "cad-artifacts.json").write_text(json.dumps({
            "release": {"asset": "cad-inflight.tar.gz"},
            "solids": {"hardware/printed-parts/cap/cap.step": "inflight"},
        }))
        listing = [{"name": name, "createdAt": born(RETIRE_FLOOR_S + 60)}
                   for name in ("cad-inflight.tar.gz", object_asset("inflight"), "obj-dead.gz")]
        was = (release_assets, pointer_files_in_history)
        globals()["release_assets"] = lambda _root: listing
        globals()["pointer_files_in_history"] = lambda _root: []
        try:
            swept = retirable(root, now=clock)
        finally:
            globals()["release_assets"], globals()["pointer_files_in_history"] = was
        hold("a cut whose pointer file is on disk and in no commit is neither unreachable nor stale",
             swept, (["obj-dead.gz"], []))

        shutil.rmtree(hw / "printed-parts" / "enclosure")

        a, b = root / "a.tar.gz", root / "b.tar.gz"
        rels = solids(root)
        da = build(root, rels, a)
        os.utime(hw / "printed-parts" / "cap" / "cap.step", (1, 1))
        db = build(root, rels, b)
        hold("an mtime does not move the bundle", da, db)
        hold("nor does it move the bytes", a.read_bytes(), b.read_bytes())

        score_before = hashes(root, sidecars(root))
        scorecard.write_text('{"gatesPass": false}\n')
        score_after = hashes(root, sidecars(root))
        score_bundle = build(root, rels, root / "scorecard-only.tar.gz")
        hold("a scorecard moves its pointer file hash without moving the geometry bundle",
             (score_before != score_after, score_bundle), (True, da))

        (hw / "printed-parts" / "cap" / "cap.step").write_text("ISO-10303-21;\nmoved\n")
        dc = build(root, rels, root / "c.tar.gz")
        hold("moved geometry moves the bundle", dc != da, True)

        with tarfile.open(a, "r:gz") as tar:
            names = tar.getnames()
        hold("members are repo-relative", names, ["hardware/printed-parts/cap/cap.step"])
        info = tarfile.open(a, "r:gz").getmember(names[0])
        hold("no machine is named in a member",
             (info.mtime, info.uid, info.gid, info.uname, info.gname), (0, 0, 0, "", ""))

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        model = root / "hardware" / "reference" / "vendor" / "fitting"
        model.mkdir(parents=True)
        prefix = model.relative_to(root).as_posix()
        contents = {"fitting.step": b"frozen STEP", "fitting.step.mesh": b"viewer payload"}
        members = {}
        for name, data in contents.items():
            (model / name).write_bytes(data)
            members[f"{prefix}/{name}"] = hashlib.sha256(data).hexdigest()
        (model / "fitting.step.npz").write_bytes(b"finer kernel import")
        (model / "other.step.mesh").write_bytes(b"unlisted viewer payload")
        (model / "frozen-asset.json").write_text(json.dumps({
            "source": {"commit": "snapshot", "path": "fitting.py", "sha256": "source"},
            "members": {Path(rel).name: digest for rel, digest in members.items()},
        }))
        hold("a nested frozen manifest names static inputs without a generator",
             frozen_assets(root), members)
        hold("only the frozen viewer payload travels; kernel import meshes stay separate",
             solids(root), sorted(members))
        hold("frozen members need no active producer and are not graph gaps",
             _graph_gaps(root, solids(root)), ([], []))
        hold("publication hashes agree with the frozen identities",
             hashes(root, sorted(members)), members)
        payload = f"{prefix}/fitting.step.mesh"
        step = f"{prefix}/fitting.step"
        changed_payload = b"different payload"
        (root / payload).write_bytes(changed_payload)
        hold("publication hashes held bytes without a veto from the frozen snapshot",
             hashes(root, [payload])[payload], hashlib.sha256(changed_payload).hexdigest())
        (root / payload).write_bytes(contents[Path(payload).name])
        previous = {"commit": "earlier", "unproven": True}
        hold("a frozen STEP keeps its line and a new payload claims no fresh derivation",
             made_for({step: previous}, members, "publish", {}, moved={payload}, frozen=members),
             {step: previous, payload: {"commit": "publish", "unproven": True}})
        (root / payload).unlink()
        hold("a checkout knows its static inputs before fetching them",
             frozen_assets(root), members)
        held_frozen = {"store": {"url": "https://site/objects/", "objects": "s-"},
                       "solids": members}
        was = download_object
        globals()["download_object"] = lambda url: contents[Path(payload).name]
        try:
            restored = adopt(root, held_frozen, [payload])
        finally:
            globals()["download_object"] = was
        hold("the existing pointer/store route restores a missing frozen payload",
             (restored, _sha256(root / payload)), ([payload], members[payload]))
        (root / "hardware" / "cad-artifacts.json").write_text(json.dumps(held_frozen))
        hold("retiring the generator does not retire its frozen assets",
             retired_outputs(root), [])

    # AN ASSET IS NAMED BY ITS BYTES, so what `upload_objects` sends is one send per hash. Two
    # members carrying the same bytes sent as two uploads race one asset name, and the loser
    # reports a failure that costs the pointer file its `objects` for a member that is demonstrably up.
    twins = {"a.png": "h1", "b.png": "h1", "c.step": "h2"}
    hold("two members of one hash are one send",
         objects_to_send(list(twins), twins, set()), ["a.png", "c.step"])
    hold("a member already on the release is not re-sent",
         objects_to_send(list(twins), twins, {"h1"}), ["c.step"])
    hold("nothing to send when the release holds every hash",
         objects_to_send(list(twins), twins, {"h1", "h2"}), [])

    # A HELD PUBLISH MOVES THE LINES FOR WHAT THIS MACHINE CUT AND TAKES MAIN'S FOR THE REST.
    held = {"release": {"tag": TAG, "asset": "cad-x.tar.gz", "objects": OBJECT_PREFIX,
                        "url": "https://example/releases/download/cad-artifacts/cad-x.tar.gz"},
            "solids": {"a": "ha", "b": "hb", "c": "hc", "d": "hd"},
            "moved": {"a": 100, "b": 100, "c": 100, "d": 100}}
    now = {"a": "ha", "b": "hb2", "c": "hc2", "e": "he"}          # d is not on this disk
    mtimes = {"a": 50, "b": 150, "c": 50, "e": 10}
    built, fresh, stale, absent = held_publish_plan(held, sorted(now), now, mtimes)
    hold("a copy newer than its line was cut here", built, ["b"])
    hold("a member main does not name is new here", fresh, ["e"])
    hold("a copy older than its line is main's earlier bytes", stale, ["c"])
    hold("a member absent from this disk keeps its line", absent, ["d"])
    hold("a line without a time reads as older than any file",
         held_publish_plan({"solids": {"c": "hc"}}, ["c"], {"c": "x"}, {"c": 1})[0], ["c"])
    times = line_times(held, {"a": "ha", "b": "hb2", "e": "he"}, 200)
    hold("an unmoved line keeps its time, a moved or new one is stamped", times, {"a": 100, "b": 200, "e": 200})
    hold("the object url is the release directory, the prefix and the hash",
         object_url(held, "hc"), "https://example/releases/download/cad-artifacts/s-hc.gz")
    hold("the store comes first when the pointer file names one",
         object_url({**held, "store": {"url": "https://site/objects/", "objects": "s-"}}, "hc"),
         "https://site/objects/s-hc.gz")
    hold("no object lane, no url", object_url({"release": {"url": "https://x/y/z"}}, "h"), None)
    hold("a pointer file names the store",
         pointers_for(_ROOT, [], "d", 1, {}, {}, None)["store"],
         {"url": STORE_URL, "objects": OBJECT_PREFIX})
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "m.step").write_text("member")
        sent = []
        was_put = put_object
        globals()["put_object"] = lambda url, staged: sent.append((url, gzip.decompress(staged.read_bytes()))) or True
        try:
            hold("a member goes to the store by hash, gzipped",
                 upload_objects(root, ["m.step"], {"m.step": "hm"}, set()), True)
        finally:
            globals()["put_object"] = was_put
        hold("…at the store's address", sent, [(STORE_URL + "s-hm.gz", b"member")])
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "hardware").mkdir()
        (root / "hardware" / "c.step").write_text("older bytes")
        good = b"main's bytes"
        want = hashlib.sha256(good).hexdigest()
        held2 = {"release": held["release"], "solids": {"hardware/c.step": want, "hardware/x.step": "nope"}}
        was = download_object
        globals()["download_object"] = lambda url: good if url.endswith(f"{want}.gz") else b"wrong"
        try:
            (root / "hardware" / "x.step").write_text("older")
            taken = adopt(root, held2, ["hardware/c.step", "hardware/x.step"])
        finally:
            globals()["download_object"] = was
        hold("main's bytes are taken where they hash to the line", taken, ["hardware/c.step"])
        hold("and stand in the member's place", (root / "hardware" / "c.step").read_bytes(), good)
        hold("an object that does not hash to its line is left as it was",
             (root / "hardware" / "x.step").read_text(), "older")

    # WHAT EACH MEMBER WAS MADE FROM. The cap reads its source; the assembly reads the cap and a
    # handoff nothing names, which reads the assembly's source.
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        sources = ("src/cap.py", "src/asm.py", "gen/cap.py", "gen/handoff.py", "gen/asm.py")
        for rel in sources + ("hw/cap.step", "hw/asm.step"):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(rel)
        g = Graph({
            "gen/cap.py": {"reads": ["src/cap.py"], "writes": ["hw/cap.step"]},
            "gen/handoff.py": {"reads": ["src/asm.py"], "writes": ["hw/handoff.mesh"]},
            "gen/asm.py": {"reads": ["hw/cap.step", "hw/handoff.mesh"], "writes": ["hw/asm.step"]},
        })
        index = {rel: blob_id(root / rel) for rel in sources}
        lines = {"hw/cap.step": "c1", "hw/asm.step": "a1"}
        tree = tree_digests(root, g, lines, index)
        hold("a member's inputs move with a member it reads",
             tree_digests(root, g, {**lines, "hw/cap.step": "c2"}, index)["hw/asm.step"]
             != tree["hw/asm.step"], True)
        hold("…and not with one it does not",
             tree_digests(root, g, {**lines, "hw/asm.step": "a2"}, index)["hw/cap.step"],
             tree["hw/cap.step"])
        hold("a handoff nothing names counts as its writer's inputs",
             tree_digests(root, g, lines, {**index, "src/asm.py": "edited"})["hw/asm.step"]
             != tree["hw/asm.step"], True)

        def at(rel, s):
            os.utime(root / rel, (1_700_000_000 + s, 1_700_000_000 + s))

        for rel in sources:
            at(rel, 0)
        at("hw/cap.step", 10)
        at("hw/asm.step", 20)
        hold("a member written after every input it reads was cut from them",
             cut_after_inputs(root, "hw/cap.step", g), True)
        at("src/cap.py", 11)
        hold("an input edited after the member was not what its cut read",
             cut_after_inputs(root, "hw/cap.step", g), False)
        at("src/cap.py", 0)
        at("hw/cap.step", 50)
        hold("a part copied within a minute after the assembly reading it is what the cut read",
             cut_after_inputs(root, "hw/asm.step", g), True)
        at("hw/cap.step", 140)
        hold("…and one copied later than that is not",
             cut_after_inputs(root, "hw/asm.step", g), False)
        at("hw/cap.step", 10)

        head = "h2"
        proven = {"inputs": "t1", "commit": "h1"}
        hold("a proven line stands while the tree holds its inputs",
             made_lines({"m": proven}, ["m"], head, {"m": "t1"}), {"m": proven})
        hold("an input the tree moves off leaves it unproven at the commit it was made",
             made_lines({"m": proven}, ["m"], head, {"m": "t2"}),
             {"m": {"inputs": "t1", "commit": "h1", "unproven": True}})
        hold("…and the tree coming back to those inputs proves it here",
             made_lines({"m": {**proven, "unproven": True}}, ["m"], head, {"m": "t1"}),
             {"m": {"inputs": "t1", "commit": head}})
        hold("a member cut on this disk is recorded off what its cut read",
             made_lines({}, ["m"], head, {"m": "t1"}, {"m": "w1"}, derived={"m"}),
             {"m": {"inputs": "w1", "commit": head, "unproven": True}})
        hold("…and is proven where the tree holds that",
             made_lines({}, ["m"], head, {"m": "t1"}, {"m": "t1"}, derived={"m"}),
             {"m": {"inputs": "t1", "commit": head}})
        hold("bytes that moved uncut, and a member with no line, have nothing to say what cut them",
             made_lines({"m": proven}, ["m", "n"], head, {"m": "t1", "n": "t9"}, moved={"m"}),
             {"m": {"commit": head, "unproven": True}, "n": {"commit": head, "unproven": True}})
        hold("that line stands until its bytes move",
             made_lines({"m": {"commit": "h1", "unproven": True}}, ["m"], head, {"m": "t1"}),
             {"m": {"commit": "h1", "unproven": True}})
        hold("a cut that does not reproduce the bytes leaves a proven line unproven",
             made_lines({"m": proven}, ["m"], head, {"m": "t1"}, refuted={"m"}),
             {"m": {"inputs": "t1", "commit": "h1", "unproven": True}})
        hold("a line moves with no bytes for no line, inputs moved off, and inputs come back",
             made_moves({"a": proven, "b": proven, "c": {**proven, "unproven": True},
                         "d": {**proven, "unproven": True}, "e": {"commit": "h1", "unproven": True}},
                        {"a": "t1", "b": "t2", "c": "t1", "d": "t2", "e": "t3", "f": "t1"}),
             ["b", "c", "f"])
        hold("an undeclared member keeps its line, and one the pointer file drops leaves `made`",
             made_for({"u": proven, "gone": proven}, {"u": "x", "m": "y"}, head, {"m": "t1"}),
             {"m": {"commit": head, "unproven": True}, "u": proven})

        walked = {"hw/cap.step": "c1", "hw/asm.step": "a1"}
        here = made_here(root, {}, g, index, head, lines, walked, {"hw/cap.step"})
        hold("a held publish proves a member cut after the inputs the tree commits",
             here["hw/cap.step"], {"inputs": tree["hw/cap.step"], "commit": head})
        hold("a member the graft wrote has nothing to say what cut it",
             made_here(root, {}, g, index, head, lines, walked, {"hw/cap.step"},
                       {"hw/cap.step"})["hw/cap.step"], {"commit": head, "unproven": True})
        (root / "src/cap.py").write_text("uncommitted")
        at("src/cap.py", 0)
        edited = made_here(root, {}, g, index, head, lines, walked, {"hw/cap.step"})["hw/cap.step"]
        hold("a cut from an uncommitted edit is recorded off the edit, unproven",
             (edited.get("unproven"), edited.get("inputs") not in (None, tree["hw/cap.step"])),
             (True, True))

    hold("the pointer file holds its keys in order, and only those",
         list(_pointer_file({"made": {}, "source": {"commit": "c"}, "solids": {},
                             "unproven": {"members": []}, "_": "note"})),
         ["_", "solids", "made"])
    hold("…and its members in path order",
         list(_pointer_file({"solids": {"b": "1", "a": "2"}})["solids"]), ["a", "b"])

    print(f"pack selftest {holds}/66")
    return 0 if holds == 66 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
