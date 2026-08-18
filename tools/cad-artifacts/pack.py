#!/usr/bin/env python3
"""The generated solids, as one release asset a deploy fetches.

    tools/cad-venv/bin/python tools/cad-artifacts/pack.py            # what the bundle holds
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write    # build it, upload it, pin it
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --check    # 0 = the lock names this tree
    tools/cad-venv/bin/python tools/cad-artifacts/pack.py selftest   # the bundle, on fixtures

`hardware/cad-artifacts.lock.json` names the asset by its own sha256 and every solid inside it by
sha256, and it is committed. The asset is content-addressed (`cad-<sha16>.tar.gz`) and never
rewritten, so a checkout resolves to the bundle its own commit was packed against.
`web/scripts/fetch-cad-artifacts.mjs` reads the lock at deploy and holds the download to both
hashes before anything is extracted.

THE BUNDLE CARRIES NO FACT ABOUT THE MACHINE THAT PACKED IT. Members go in sorted, and the mtime,
uid, gid, uname, gname and mode a tar can hold are dropped; the gzip header carries no mtime. A
pack over a tree whose geometry has not moved lands on the same asset name and the same bytes —
the property `_cadq_export` gives each STEP it canonicalizes, kept at the bundle.

The walk reaches every `.step` under `hardware/` on disk. What sits out is `NOT_BUNDLED_DIRS` and
`HARVESTED` below. `--check` holds what the walk found against the outputs `tools/bazel/graph.json`
declares, and names any solid the graph does not carry.
"""

import argparse
import gzip
import hashlib
import io
import json
import os
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


def solids(root: Path) -> list:
    """Every generated `.step` under `hardware/`, repo-relative and sorted.

    Off the disk, tracked or not: a solid the index does not hold is one a fresh clone still has
    to be sent, and it is the lock that carries it into the index."""
    hw = root / "hardware"
    if not hw.is_dir():
        return []
    skip = tuple(f"{d}/" for d in NOT_BUNDLED_DIRS)
    out = []
    for p in hw.rglob("*.step"):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix()
        if rel.startswith(skip) or rel in HARVESTED:
            continue
        # A dependency's own test fixtures are solids on this disk that no part of this machine
        # is made of. `occt-import-js` ships eight.
        if "node_modules/" in rel:
            continue
        # An atomic-export temp caught mid-write (`.NAME.step.PID.RAND.step`) is not a solid.
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


def lock_for(root: Path, rels: list, digest: str, size: int, solid_hashes: dict = None) -> dict:
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
        "bundle": {"sha256": digest, "bytes": size, "solids": len(rels)},
        "solids": solid_hashes if solid_hashes is not None else hashes(root, rels),
    }


def read_lock() -> dict:
    try:
        return json.loads(LOCK.read_text())
    except (OSError, ValueError):
        return {}


def _write_lock(data: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def _undeclared(root: Path, rels: list) -> list:
    """Generated solids the walk reached that `graph.json` does not declare an output.

    Named, not excluded: the bundle carries a part whose generator has not been re-traced.
    `HARVESTED` is already out of `rels`, so what is left is a fresh part or a stale graph."""
    try:
        graph = json.loads((root / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return []
    declared = set()
    for node in graph.values():
        for key in ("writes", "outs", "outputs"):
            for f in (node.get(key) or []):
                if str(f).endswith(".step"):
                    declared.add(str(f))
    return [r for r in rels if r not in declared]


def _gh(root: Path, *args, **kw):
    return subprocess.run(["gh", *args], cwd=str(root), capture_output=True, text=True, **kw)


def upload(root: Path, bundle: Path, asset: str) -> None:
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
        have = {a["name"] for a in json.loads(listing.stdout).get("assets", [])}
        if asset in have:
            print(f"  {asset} is already on the release")
            return
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
    args = ap.parse_args(argv)

    if args.mode == "selftest":
        return selftest()

    rels = solids(_ROOT)
    total = sum((_ROOT / r).stat().st_size for r in rels)
    print(f"{len(rels)} generated solid(s), {total / 1e6:.1f} MB in the tree")

    loose = _undeclared(_ROOT, rels)
    if loose:
        print(f"  {len(loose)} not declared an output in graph.json (a fresh part, or a stale "
              f"graph — the bundle carries them either way):")
        for rel in loose[:8]:
            print(f"    {rel}")

    now = hashes(_ROOT, rels)
    held = read_lock()
    if held.get("solids") == now:
        print(f"lock names this tree — {held['release']['asset']}")
        return 0

    was = held.get("solids", {})
    moved = sorted(k for k in now if k in was and was[k] != now[k])
    fresh = sorted(set(now) - set(was))
    gone = sorted(set(was) - set(now))
    if not held:
        print("no lock yet — `--write` makes one")
    else:
        print(f"lock is behind: {len(moved)} moved, {len(fresh)} new, {len(gone)} gone")
        for rel in (moved + fresh + gone)[:8]:
            print(f"    {rel}")
    if not args.write:
        print("  the bundle these belong in, on the release and pinned:")
        print("    tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write")
        return 1 if args.check else 0

    with tempfile.TemporaryDirectory() as d:
        bundle = Path(d) / "bundle.tar.gz"
        digest = build(_ROOT, rels, bundle)
        size = bundle.stat().st_size
        data = lock_for(_ROOT, rels, digest, size, now)
        print(f"bundle {data['release']['asset']} — {size / 1e6:.1f} MB "
              f"({100 * size / total:.0f}% of the tree's bytes)")
        upload(_ROOT, bundle, data["release"]["asset"])

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

        a, b = root / "a.tar.gz", root / "b.tar.gz"
        rels = solids(root)
        da = build(root, rels, a)
        os.utime(hw / "printed-parts" / "cap" / "cap.step", (1, 1))
        db = build(root, rels, b)
        hold("an mtime does not move the bundle", da, db)
        hold("nor does it move the bytes", a.read_bytes(), b.read_bytes())

        (hw / "printed-parts" / "cap" / "cap.step").write_text("ISO-10303-21;\nmoved\n")
        dc = build(root, rels, root / "c.tar.gz")
        hold("moved geometry moves the bundle", dc != da, True)

        with tarfile.open(a, "r:gz") as tar:
            names = tar.getnames()
        hold("members are repo-relative", names, ["hardware/printed-parts/cap/cap.step"])
        info = tarfile.open(a, "r:gz").getmember(names[0])
        hold("no machine is named in a member",
             (info.mtime, info.uid, info.gid, info.uname, info.gname), (0, 0, 0, "", ""))

    print(f"pack selftest {holds}/7")
    return 0 if holds == 7 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
