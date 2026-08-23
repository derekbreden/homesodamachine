#!/usr/bin/env python3
"""The generated solids, as one release asset a deploy fetches.

    tools/cad-venv/bin/python tools/cad-artifacts/pack.py            # what the bundle holds
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write    # build it, upload it, pin it
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --check    # 0 = the lock names this tree
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --prune    # remove retired locked outputs
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py selftest   # the bundle, on fixtures

`hardware/cad-artifacts.lock.json` names the source commit, the asset by its own sha256, every
solid inside it, and each tracked scorecard the viewer reads by sha256; it is committed. The
scorecards stay outside the geometry tar and move atomically with its lock. The asset is content-addressed
(`cad-<sha16>.tar.gz`) and never
rewritten, so a checkout resolves to the bundle its own commit was packed against.
`web/scripts/fetch-cad-artifacts.mjs` reads the lock at deploy and holds the download to both
hashes before anything is extracted.

THE BUNDLE CARRIES NO FACT ABOUT THE MACHINE THAT PACKED IT. Members go in sorted, and the mtime,
uid, gid, uname, gname and mode a tar can hold are dropped; the gzip header carries no mtime. A
pack over a tree whose geometry has not moved lands on the same asset name and the same bytes —
the property `_cadq_export` gives each STEP it canonicalizes, kept at the bundle.

The walk reaches every `.step` under `hardware/` on disk, every `.stl` under `BUNDLED_MESH_DIRS`
— the one place where the solid is not the whole of the part — every `<file>.step.mesh` under
`BUNDLED_PAYLOAD_DIRS`, which is that same surface at the deflection a browser draws it at, and
every `.glb` under `BUNDLED_GLB_DIRS`, which the parts viewer opens directly rather than through
a STEP. What sits
out is `NOT_BUNDLED_DIRS` and `HARVESTED` below. `--check` holds what the walk found against the outputs
`tools/bazel/graph.json` declares, and names anything the graph does not carry.
"""

import argparse
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir())

LOCK = _ROOT / "hardware" / "cad-artifacts.lock.json"
TAG = "cad-artifacts"

#: Trees of local intermediates, each already ignored by the rule named beside it.
NOT_BUNDLED_DIRS = (
    "hardware/pcb/pcba/.cad-cache",          # manufacturer downloads, keyed by LCSC
    "hardware/pcb/pcba/out",                 # the on-demand full B-rep; out/<board>.glb is the artifact
    "hardware/assembly/scenes/out",          # a rendering intermediate for the unit cards' pictures
    "hardware/quickstart/out",               # where a mount study lands; no rule declares one
)

#: Solids with no builder in this tree — `y_divider.py:3` says it of its own. A generator reads
#: them: `manifold_layout.py` places the elbow and the tee. They are in git and out of the bundle.
HARVESTED = (
    "hardware/reference/elbow-connector/elbow-connector.step",
    "hardware/reference/tee-connector/tee-connector.step",
    "hardware/reference/y-divider/y-divider.step",
)


def _sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _facets(path) -> int:
    """The triangle count a binary STL declares, or -1 where nothing declares one.

    A binary STL is an 80-byte header and then a uint32 count, so this is four bytes at a known
    offset. An ASCII one opens `solid` and states no count; a STEP states none either."""
    if Path(path).suffix != ".stl":
        return -1
    with open(path, "rb") as fh:
        head = fh.read(84)
    if len(head) < 84 or head[:5] == b"solid":
        return -1
    return int.from_bytes(head[80:84], "little")


def barren(root: Path, solid_hashes: dict) -> list:
    """Members carrying no geometry, and members whose bytes are already another member's.

    A SHA256 OF AN EMPTY FILE IS A PERFECTLY GOOD SHA256. `fetch-cad-artifacts.mjs` holds every
    member to its hash on the way in, so a mesh that lost its faces between the build and the pack
    arrives verified, and the site, the card decks and every clean clone then trust it. Verified
    and non-empty are different questions and the fetch only ever asks the first.

    Both readings are free beside the hash this file already takes of every member. A binary STL
    declares its own triangle count and no part of this machine is nought facets — an empty one is
    84 bytes and its count reads zero. And two distinct parts sharing a sha256 are two files with
    the same bytes, which for geometry means neither holds any; empties collide with each other
    precisely because there is nothing in them to differ."""
    out = []
    for rel in sorted(solid_hashes):
        if _facets(root / rel) == 0:
            out.append(f"{rel} declares 0 facets — {(root / rel).stat().st_size} bytes, an empty solid")
    seen = {}
    for rel, sha in sorted(solid_hashes.items()):
        if sha in seen:
            out.append(f"{rel} carries the bytes {seen[sha]} carries — sha256 {sha[:16]}")
        else:
            seen[sha] = rel
    return out


# WHERE A MESH IS CARRIED TOO. A directory named here has its `.stl` bundled beside the solids.
# The enclosure's six pieces are what a slicer is handed, and their flutes are in the MESH and not
# in the solid, so the STEP beside them does not carry the surface that gets printed
# (`printed-parts/enclosure/enclosure/flute_skin.py`). They are gitignored, so the bundle is the
# route by which they leave the machine that cut them — for a reader with a printer, not for the
# viewer, which serves `.step`.
BUNDLED_MESH_DIRS = ("hardware/printed-parts/enclosure/enclosure",)

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
BUNDLED_PAYLOAD_DIRS = (
    "hardware/printed-parts/enclosure/enclosure",
    "hardware/manifold-layout",
    "hardware/faucet-layout",
)


def solids(root: Path) -> list:
    """Every generated `.step`, `.stl`, `.glb` and `.step.mesh` under `hardware/`, repo-relative
    and sorted.

    Off the disk, tracked or not: an artifact the index does not hold is one a fresh clone still
    has to be sent, and it is the lock that carries it into the index."""
    hw = root / "hardware"
    if not hw.is_dir():
        return []
    skip = tuple(f"{d}/" for d in NOT_BUNDLED_DIRS)
    meshes = tuple(f"{d}/" for d in BUNDLED_MESH_DIRS)
    scenes = tuple(f"{d}/" for d in BUNDLED_GLB_DIRS)
    payloads = tuple(f"{d}/" for d in BUNDLED_PAYLOAD_DIRS)
    out = []
    walk = list(hw.rglob("*.step"))
    for d in BUNDLED_MESH_DIRS:
        walk += list((root / d).rglob("*.stl"))
    for d in BUNDLED_PAYLOAD_DIRS:
        walk += list((root / d).rglob("*.step.mesh"))
    for d in BUNDLED_GLB_DIRS:
        walk += list((root / d).rglob("*.glb"))
    for p in walk:
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix()
        if rel.startswith(skip) or rel in HARVESTED:
            continue
        if p.suffix == ".stl" and not rel.startswith(meshes):
            continue
        if p.suffix == ".glb" and not rel.startswith(scenes):
            continue
        if p.suffix == ".mesh" and not rel.startswith(payloads):
            continue
        # A dependency's own test fixtures are solids on this disk that no part of this machine
        # is made of. `occt-import-js` ships eight.
        if "node_modules/" in rel:
            continue
        # An atomic-export temp caught mid-write (`.NAME.step.PID.RAND.step`) is not one.
        if p.name.startswith("."):
            continue
        out.append(rel)
    return sorted(out)


def build(root: Path, rels: list, dest) -> str:
    """Write the bundle at `dest` and return its sha256. A member carries its path and its
    bytes; every other field a tar can hold is set flat."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for rel in rels:
            src = root / rel
            info = tarfile.TarInfo(rel)
            info.size = src.stat().st_size
            info.mtime = 0
            info.mode = 0o644
            info.type = tarfile.REGTYPE
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            with open(src, "rb") as fh:
                tar.addfile(info, fh)
    with open(dest, "wb") as fh:
        # `filename=""` and not the default: handed a fileobj and no name, GzipFile takes
        # `fileobj.name` and writes it into the header under the FNAME flag, which puts the path
        # this was built at inside the bytes and moves the hash with it.
        with gzip.GzipFile(filename="", fileobj=fh, mode="wb", compresslevel=6, mtime=0) as gz:
            gz.write(raw.getvalue())
    return _sha256(dest)


def _origin_slug(root: Path) -> str:
    """`owner/repo` for the origin remote, which is what the download URL is built from."""
    url = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout.strip()
    slug = url.split("github.com", 1)[-1].lstrip(":/")
    return slug[:-4] if slug.endswith(".git") else slug


def hashes(root: Path, rels: list) -> dict:
    """Each solid's sha256, by repo-relative path.

    The bundle is a function of these and their order, so a set of them equal to the lock's is a
    bundle equal to the lock's — which is the whole of what `--check` asks, and it asks it without
    compressing 117 MB to find out."""
    return {rel: _sha256(root / rel) for rel in rels}


def _head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _dirty_artifact_inputs(root: Path) -> list:
    """Tracked/untracked edits that can reach a published output.

    Ignored generated solids are intentionally absent from git status; they are the bytes being
    packed. Source provenance is only honest when every input that can cut those bytes belongs
    to HEAD.
    """
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    sys.path.insert(0, str(root / "tools" / "bazel"))
    import affected

    moved = {path for line in status.stdout.splitlines()
             for path in affected.paths_in(line)}
    moved.discard("hardware/cad-artifacts.lock.json")
    # These are generated outputs this very publication carries. A hand edit still cannot slip
    # through: its changed hash maps back to the producer below and `_cut_is_fresh` refuses until
    # the current Bazel output and tree agree.
    moved -= set(sidecars(root)) | set(read_lock(root).get("sidecars", {}))
    moved = {path for path in moved if not affected.artifact_presentation_only(path)}
    if not moved:
        return []
    forced = sorted(p for p in moved if affected.artifact_unknown(p, artifacts_only=True))
    hit, miss = affected.known(sorted(moved))
    risky = [p for p in miss if affected.artifact_unknown(p, artifacts_only=True)]
    reached = sorted(set(affected.targets(hit)) & affected.artifact_targets())
    return sorted(set(forced) | set(risky) | set(reached))


def _owed_artifact_targets(root: Path) -> list:
    """Artifact rules changed since the source commit the lock proves."""
    source = read_lock(root).get("source", {}).get("commit", "")
    script = root / "tools" / "bazel" / "affected.py"
    args = ([sys.executable, str(script), "--base", source, "--head", "HEAD", "--artifacts"]
            if source else [sys.executable, str(script), "--all-artifacts"])
    run = subprocess.run(args, cwd=str(root), capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f"could not establish artifact debt:\n{run.stderr}")
    return sorted({line for line in run.stdout.splitlines() if line.startswith("//:")})


def _cut_is_fresh(root: Path, targets: list) -> bool:
    """Whether Bazel and the tree both hold the outputs the owed rules make."""
    if not targets:
        return True
    check = subprocess.run(["bazel", "build", "--check_up_to_date", *targets],
                           cwd=str(root), capture_output=True, text=True)
    owed = [line for line in check.stderr.splitlines() if "not up-to-date" in line]
    stale = [line for line in owed if "BazelWorkspaceStatusAction" not in line]
    if check.returncode != 0 and (stale or not owed):
        print("the artifact targets have not been built from this source commit:")
        for line in (stale or check.stderr.splitlines())[:10]:
            print(f"  {line.strip()}")
        return False
    sync = subprocess.run(
        [sys.executable, str(root / "tools" / "bazel" / "sync_tree.py"),
         "--runtime-only", "--targets", " ".join(targets)], cwd=str(root))
    if sync.returncode != 0:
        print("the tree does not hold the complete cut in bazel-bin")
        return False
    return True


def _targets_for_members(root: Path, members: set) -> tuple:
    """The artifact rules that own bundle members or scorecards, and any no rule owns.

    The lock source tells which rules the commit range owes. The bytes on disk can also have
    moved independently because generated solids are ignored; mapping every changed member
    back to its producer makes `--write` prove those bytes came from a current Bazel output too.
    """
    if not members:
        return [], []
    if root.resolve() != _ROOT.resolve():
        return [], sorted(members)
    sys.path.insert(0, str(root / "tools" / "bazel"))
    from gen_build import target_name
    from inventory import inventory, tracked

    inv = inventory(tracked())
    seen, shared = set(), set()
    for gens in inv:
        for gen in gens:
            stem = Path(gen).stem.strip("_").replace("_", "-")
            (shared if stem in seen else seen).add(stem)

    remaining = set(members)
    targets = set()
    for gens, made in inv.items():
        owned = remaining & set(made["solids"])
        if owned:
            targets.add(f"//:{target_name(gens[0], shared)}")
            remaining -= owned
    return sorted(targets), sorted(remaining)


def lock_for(root: Path, rels: list, digest: str, size: int, solid_hashes: dict = None,
             sidecar_hashes: dict = None) -> dict:
    asset = f"cad-{digest[:16]}.tar.gz"
    slug = _origin_slug(root)
    return {
        "_": "Written by tools/cad-artifacts/pack.py. The solids are fetched, not committed —"
             " web/scripts/fetch-cad-artifacts.mjs reads this at deploy.",
        "release": {
            "tag": TAG,
            "asset": asset,
            "url": f"https://github.com/{slug}/releases/download/{TAG}/{asset}",
        },
        "source": {"commit": _head(root)},
        "bundle": {"sha256": digest, "bytes": size, "solids": len(rels)},
        "solids": solid_hashes if solid_hashes is not None else hashes(root, rels),
        "sidecars": sidecar_hashes if sidecar_hashes is not None
                    else hashes(root, sidecars(root)),
    }


def read_lock(root: Path = _ROOT) -> dict:
    try:
        return json.loads((root / "hardware" / "cad-artifacts.lock.json").read_text())
    except (OSError, ValueError):
        return {}


def _write_lock(data: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def _declared(root: Path) -> set:
    """Every publishable output the build graph says a clean action produces."""
    try:
        graph = json.loads((root / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return set()
    declared = {
        str(f)
        for node in graph.values()
        for f in (node.get("writes") or [])
        if str(f).endswith((".step", ".stl", ".glb", ".step.mesh"))
    }
    if root.resolve() == _ROOT.resolve():
        sys.path.insert(0, str(_ROOT / "tools" / "bazel"))
        from inventory import ACTION_INTERMEDIATE, IMPLICIT_SOLIDS
        declared |= {path for paths in IMPLICIT_SOLIDS.values() for path in paths}
        declared -= ACTION_INTERMEDIATE
    return declared


def sidecars(root: Path) -> list:
    """Graph-declared scorecards served directly from the committed tree, repo-relative."""
    try:
        graph = json.loads((root / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return []
    return sorted({
        str(path)
        for node in graph.values()
        for path in (node.get("writes") or [])
        if str(path).endswith(".scorecard.json")
    })


def sidecar_debt_targets(root: Path) -> list:
    """Producer labels whose committed viewer scorecards do not match this lock."""
    held = read_lock(root).get("sidecars", {})
    owed = {
        rel for rel in sidecars(root)
        if not (root / rel).is_file() or held.get(rel) != _sha256(root / rel)
    }
    targets, unowned = _targets_for_members(root, owed)
    if unowned:
        raise SystemExit("scorecard output(s) have no current Bazel producer:\n  "
                         + "\n  ".join(unowned))
    return targets


def _graph_gaps(root: Path, rels: list) -> tuple:
    """Bundled-but-undeclared and declared-but-absent publish outputs.

    Equality is the gate. A sibling STEP is not a declaration for an STL or `.step.mesh`:
    Bazel carries bytes, and every byte the release ships must be an output of the action that
    makes it."""
    declared = _declared(root)
    present = set(rels)
    return sorted(present - declared), sorted(declared - present)


def _undeclared(root: Path, rels: list) -> list:
    """Compatibility name for callers that only ask about the first half of `_graph_gaps`."""
    return _graph_gaps(root, rels)[0]


def _retirement_evidence(root: Path, retired: list) -> list:
    """Retired paths whose producing source did not move since the published cut."""
    if not retired:
        return []
    source = read_lock(root).get("source", {}).get("commit", "")
    if not source:
        return list(retired)
    old = subprocess.run(
        ["git", "-C", str(root), "show", f"{source}:tools/bazel/graph.json"],
        capture_output=True, text=True)
    moved = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", source, "HEAD"],
        capture_output=True, text=True)
    if old.returncode != 0 or moved.returncode != 0:
        return list(retired)
    try:
        graph = json.loads(old.stdout)
    except ValueError:
        return list(retired)
    changed = set(moved.stdout.splitlines())
    unexplained = []
    for rel in retired:
        producers = {gen for gen, seen in graph.items() if rel in seen.get("writes", ())}
        if producers:
            explained = bool(producers & changed)
        else:
            explained = "tools/bazel/inventory.py" in changed
        if not explained:
            unexplained.append(rel)
    return unexplained


def retired_outputs(root: Path) -> list:
    """Locked solids or scorecards no current producer declares."""
    lock = read_lock(root)
    return sorted(
        (set(lock.get("solids", {})) - _declared(root))
        | (set(lock.get("sidecars", {})) - set(sidecars(root)))
    )


def prune(root: Path, allow_retired: bool = False) -> int:
    """Remove locked bundle members and scorecards the current graph has retired.

    Explicit because solid deletion is otherwise invisible to git, while a retired tracked
    scorecard must leave the public endpoint in the same commit that removes its lock pin. Every
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
    removed = 0
    hardware = (root / "hardware").resolve()
    for rel in retired:
        path = root / rel
        try:
            path.resolve().relative_to(hardware)
        except ValueError:
            raise SystemExit(f"refusing to prune a lock path outside hardware/: {rel}")
        if path.is_file() or path.is_symlink():
            path.unlink()
            removed += 1
            print(f"  {rel}")
    print(f"{removed} retired locked output(s) removed; recoverable from the prior commit")
    return 0


def _gh(root: Path, *args, **kw):
    return subprocess.run(["gh", *args], cwd=str(root), capture_output=True, text=True, **kw)


def _release_asset_matches(root: Path, asset: str, digest: str, size: int) -> bool:
    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        return False
    have = {a["name"]: a for a in json.loads(listing.stdout).get("assets", [])}
    old = have.get(asset)
    return bool(old and old.get("state") == "uploaded" and old.get("size") == size
                and old.get("digest") == f"sha256:{digest}")


def upload(root: Path, bundle: Path, asset: str, digest: str, size: int) -> None:
    """Put `bundle` on the release as `asset`, making the release if it is not there yet.

    The name carries the bundle's own hash, so a name already on the release holds these bytes
    and the upload is skipped. An upload that died partway also leaves the name taken, holding a
    truncated asset — `--clobber` is what lands on that one."""
    listing = _gh(root, "release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        made = _gh(root, "release", "create", TAG,
                   "--title", "CAD artifacts",
                   "--notes", "Generated solids for the /3d viewer, fetched at deploy by "
                              "web/scripts/fetch-cad-artifacts.mjs. Each asset is named by its "
                              "own sha256 and pinned in hardware/cad-artifacts.lock.json.")
        if made.returncode != 0:
            raise SystemExit(f"gh release create failed:\n{made.stderr}")
    else:
        have = {a["name"]: a for a in json.loads(listing.stdout).get("assets", [])}
        old = have.get(asset)
        if (old and old.get("state") == "uploaded" and old.get("size") == size
                and old.get("digest") == f"sha256:{digest}"):
            print(f"  {asset} is already on the release at the verified size and digest")
            return
        if old:
            print(f"  {asset} exists without the expected size/digest — replacing it")
    with tempfile.TemporaryDirectory() as d:
        staged = Path(d) / asset
        staged.write_bytes(bundle.read_bytes())
        up = _gh(root, "release", "upload", TAG, str(staged), "--clobber")
    if up.returncode != 0:
        raise SystemExit(f"gh release upload failed:\n{up.stderr}")
    print(f"  uploaded {asset}")


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", choices=["selftest"])
    ap.add_argument("--write", action="store_true", help="build, upload and pin")
    ap.add_argument("--check", action="store_true", help="1 if the lock does not name this tree")
    ap.add_argument("--prune", action="store_true",
                    help="remove locked members no longer declared by the build graph")
    ap.add_argument("--sidecar-debt", action="store_true",
                    help="print producers whose viewer scorecards do not match the lock")
    ap.add_argument("--allow-retired", action="store_true",
                    help="with --prune, confirm graph retirements lacking source evidence")
    args = ap.parse_args(argv)

    if args.mode == "selftest":
        return selftest()
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

    if args.write:
        dirty = _dirty_artifact_inputs(_ROOT)
        if dirty:
            print("refusing to stamp HEAD onto a bundle cut from dirty artifact inputs:")
            for item in dirty[:20]:
                print(f"  {item}")
            print("  Commit the inputs, then pack from that clean source commit.")
            return 2
        owed = _owed_artifact_targets(_ROOT)
    else:
        owed = []

    rels = solids(_ROOT)
    total = sum((_ROOT / r).stat().st_size for r in rels)
    print(f"{len(rels)} generated solid(s), {total / 1e6:.1f} MB in the tree")

    sidecar_rels = sidecars(_ROOT)
    missing_sidecars = [rel for rel in sidecar_rels if not (_ROOT / rel).is_file()]
    if missing_sidecars:
        print("the build graph declares public scorecards absent from the tree:")
        for rel in missing_sidecars:
            print(f"  {rel}")
        print("  Build and carry their producer before packing.")
        return 2

    loose, missing = _graph_gaps(_ROOT, rels)
    if loose or missing:
        print("the publish inventory and build outputs do not agree, so no bundle is packed")
    if loose:
        print(f"  {len(loose)} bundled solid(s) are not declared outputs:")
        for rel in loose[:8]:
            print(f"    {rel}")
    if missing:
        print(f"  {len(missing)} declared publish output(s) are absent from the tree:")
        for rel in missing[:8]:
            print(f"    {rel}")
    if loose or missing:
        return 2

    now = hashes(_ROOT, rels)
    sidecar_now = hashes(_ROOT, sidecar_rels)

    hollow = barren(_ROOT, now)
    if hollow:
        print(f"{len(hollow)} member(s) carry no geometry, so nothing here is packed:")
        for line in hollow:
            print(f"    {line}")
        print("  Rebuild the part.")
        return 1

    held = read_lock()
    retired_sidecars = sorted(set(held.get("sidecars", {})) - set(sidecar_rels))
    unexplained_sidecars = _retirement_evidence(_ROOT, retired_sidecars)
    if unexplained_sidecars:
        print("refusing to unpin scorecards without a changed producing source:")
        for rel in unexplained_sidecars:
            print(f"  {rel}")
        return 2
    unpruned_sidecars = [rel for rel in retired_sidecars if (_ROOT / rel).exists()]
    if unpruned_sidecars:
        print("retired scorecards are still publicly served; run --prune before packing:")
        for rel in unpruned_sidecars:
            print(f"  {rel}")
        return 2
    changed_members = {rel for rel, digest in now.items()
                       if held.get("solids", {}).get(rel) != digest}
    changed_sidecars = {rel for rel, digest in sidecar_now.items()
                        if held.get("sidecars", {}).get(rel) != digest}
    changed_targets, unowned = _targets_for_members(
        _ROOT, changed_members | changed_sidecars)
    if args.write:
        if unowned:
            print("refusing to publish changed bundle members with no current Bazel producer:")
            for rel in unowned[:20]:
                print(f"  {rel}")
            return 2
        verify_targets = sorted(set(owed) | set(changed_targets))
        if not _cut_is_fresh(_ROOT, verify_targets):
            print("  Build and carry every owed or changed artifact target before --write.")
            return 2
    same_solids = held.get("solids") == now
    same_sidecars = held.get("sidecars") == sidecar_now
    if same_solids and same_sidecars:
        if args.write:
            release = held.get("release", {})
            bundle = held.get("bundle", {})
            if not _release_asset_matches(_ROOT, release.get("asset", ""),
                                          bundle.get("sha256", ""), bundle.get("bytes", -1)):
                with tempfile.TemporaryDirectory() as d:
                    path = Path(d) / "bundle.tar.gz"
                    digest = build(_ROOT, rels, path)
                    if digest != bundle.get("sha256"):
                        raise SystemExit("equal member hashes built a different bundle digest")
                    upload(_ROOT, path, release["asset"], digest, path.stat().st_size)
            if held.get("source", {}).get("commit") != _head(_ROOT):
                held["source"] = {"commit": _head(_ROOT)}
                _write_lock(held)
                print(f"lock names this tree — {held['release']['asset']}; source advanced")
                return 0
        print(f"lock names this tree — {held['release']['asset']}")
        return 0

    was = held.get("solids", {})
    moved = sorted(k for k in now if k in was and was[k] != now[k])
    fresh = sorted(set(now) - set(was))
    gone = sorted(set(was) - set(now))
    side_was = held.get("sidecars", {})
    side_moved = sorted(k for k in sidecar_now
                        if k in side_was and side_was[k] != sidecar_now[k])
    side_fresh = sorted(set(sidecar_now) - set(side_was))
    side_gone = sorted(set(side_was) - set(sidecar_now))
    if not held:
        print("no lock yet — `--write` makes one")
    else:
        print(f"lock is behind: {len(moved)} moved, {len(fresh)} new, {len(gone)} gone")
        for rel in (moved + fresh + gone)[:8]:
            print(f"    {rel}")
        if side_moved or side_fresh or side_gone:
            print(f"  scorecards: {len(side_moved)} moved, {len(side_fresh)} new, "
                  f"{len(side_gone)} gone")
            for rel in (side_moved + side_fresh + side_gone):
                print(f"    {rel}")
    if not args.write:
        print("  publish and pin the current viewer cut:")
        print("    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write")
        return 1 if args.check else 0

    if same_solids:
        release = held.get("release", {})
        bundle = held.get("bundle", {})
        if not _release_asset_matches(_ROOT, release.get("asset", ""),
                                      bundle.get("sha256", ""), bundle.get("bytes", -1)):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / "bundle.tar.gz"
                digest = build(_ROOT, rels, path)
                if digest != bundle.get("sha256"):
                    raise SystemExit("equal member hashes built a different bundle digest")
                upload(_ROOT, path, release["asset"], digest, path.stat().st_size)
        held["source"] = {"commit": _head(_ROOT)}
        held["sidecars"] = sidecar_now
        _write_lock(held)
        print(f"pinned current scorecards without rebuilding {release['asset']}")
        return 0

    with tempfile.TemporaryDirectory() as d:
        bundle = Path(d) / "bundle.tar.gz"
        digest = build(_ROOT, rels, bundle)
        size = bundle.stat().st_size
        data = lock_for(_ROOT, rels, digest, size, now, sidecar_now)
        print(f"bundle {data['release']['asset']} — {size / 1e6:.1f} MB "
              f"({100 * size / total:.0f}% of the tree's bytes)")
        upload(_ROOT, bundle, data["release"]["asset"], digest, size)

    _write_lock(data)
    print(f"pinned in {LOCK.relative_to(_ROOT)}")
    return 0


def selftest() -> int:
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
        hold("a declared scorecard is pinned outside the bundle",
             sidecars(root), ["hardware/printed-parts/cap/cap.scorecard.json"])
        hold("a payload needs its own declared output",
             _undeclared(root, solids(root)),
             ["hardware/printed-parts/enclosure/enclosure/piece.step.mesh"])
        graph["piece.py"]["writes"].append(
            "hardware/printed-parts/enclosure/enclosure/piece.step.mesh")
        (graph_dir / "graph.json").write_text(json.dumps(graph))
        hold("an exactly declared publish inventory passes",
             _graph_gaps(root, solids(root)), ([], []))
        (hw / "cad-artifacts.lock.json").write_text(json.dumps({
            "solids": {
                "hardware/printed-parts/cap/cap.step": "kept",
                "hardware/retired/old.step": "gone",
            },
            "sidecars": {
                "hardware/printed-parts/cap/cap.scorecard.json": "kept",
                "hardware/retired/old.scorecard.json": "gone",
            },
        }))
        hold("retired solids and scorecards leave the lock together",
             retired_outputs(root), ["hardware/retired/old.scorecard.json",
                                     "hardware/retired/old.step"])
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
        hold("a scorecard moves its lock hash without moving the geometry bundle",
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

    print(f"pack selftest {holds}/13")
    return 0 if holds == 13 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
