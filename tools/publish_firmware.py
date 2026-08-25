#!/usr/bin/env python3
"""The images a phone pushes, as one release asset a deploy fetches.

    ~/.platformio/penv/bin/python tools/publish_firmware.py           # what the manifest would hold
    ~/.platformio/penv/bin/python tools/publish_firmware.py --write   # build it, upload it, pin it
    ~/.platformio/penv/bin/python tools/publish_firmware.py --check   # 0 = the lock names these builds

`firmware/firmware.lock.json` names the source commit, the asset by its own sha256, and every
image inside it by target, version, size, crc32 and sha256; it is committed. The asset is
content-addressed (`fw-<sha16>.tar.gz`) and never rewritten, so a checkout resolves to the bundle
its own commit was packed against. `web/scripts/fetch-firmware.mjs` reads the lock at deploy and
holds the download to both hashes before anything is served.

THE CRC32 IN THE LOCK IS THE ONE THE WIRE CARRIES. `MSG_OTA_BEGIN` promises it and the receiver
holds the whole image to it before the boot partition moves; the phone reads it from here and
hands it through. The sha256 is what `fetch-firmware.mjs` holds the download to.

THE VERSION STRING IS THE BOARD'S OWN. `pre_build.py` writes `FW_VERSION` into each tree from
HEAD's date and short SHA, the board reports that string, and the manifest carries the same one.
"Is this machine current" is a comparison of that string against itself.

The two trees a phone never reaches: `pcba_bench` goes no further than the bench, always on USB.
`rp2040_display` runs on an RP2040, whose ROM offers USB and nothing else — it takes an image
through BOOTSEL and a cable.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import zlib
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parent.parent

LOCK = _ROOT / "firmware" / "firmware.lock.json"
TAG = "firmware"
PIO = Path.home() / ".platformio" / "penv" / "bin" / "pio"

#: What the phone can push, keyed by the name `tools/ota.py` and the app both use. `machine` is
#: which machine carries the board.
TARGETS = {
    "appliance": {
        "env": "appliance",
        "src": "src_appliance",
        "machine": "appliance",
        "what": "the main board's own firmware",
    },
    "enclosure": {
        "env": "esp32s3_front",
        "src": "src_front",
        "machine": "appliance",
        "what": "the 4.3\" enclosure display",
    },
    "faucet": {
        "env": "esp32s3_faucet",
        "src": "src_faucet",
        "machine": "appliance",
        "what": "the 1.47\" faucet display",
    },
    "art": {
        "env": "esp32s3_front",
        "src": "src_front",
        "machine": "appliance",
        "what": "the enclosure display's loading animation",
        # Not a firmware image and not built by pio — laid out from the same headers the
        # firmware used to compile in, so it carries no version of its own.
        "kind": "art",
        "art_board": "enclosure",
    },
    "rotary_art": {
        "env": "esp32s3_config",
        "src": "src_config",
        "machine": "prototype",
        "what": "the rotary display's animation and flavor faces",
        "kind": "art",
        "art_board": "rotary",
    },
    "prototype": {
        "env": "prototype",
        "src": "src_prototype",
        "machine": "prototype",
        "what": "the prototype's main ESP32",
    },
    "rotary": {
        "env": "esp32s3_config",
        "src": "src_config",
        "machine": "prototype",
        "what": "the prototype's 1.28\" rotary display",
    },
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _head() -> str:
    return subprocess.run(["git", "-C", str(_ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def _origin_slug() -> str:
    """`owner/repo` for the origin remote, which is what the download URL is built from."""
    url = subprocess.run(["git", "-C", str(_ROOT), "remote", "get-url", "origin"],
                         capture_output=True, text=True, check=True).stdout.strip()
    slug = url.split("github.com", 1)[-1].lstrip(":/")
    return slug[:-4] if slug.endswith(".git") else slug


def _dirty() -> list:
    """Tracked paths under `firmware/` or `tools/` standing outside HEAD.

    Only these two trees can move an image. A lock packed beside an edit to either carries them
    under `unproven`, the way `hardware/cad-artifacts.lock.json` carries the paths its solids
    were cut beside.
    """
    status = subprocess.run(["git", "-C", str(_ROOT), "status", "--porcelain", "--", "firmware", "tools"],
                            capture_output=True, text=True, check=True).stdout
    out = []
    for line in status.splitlines():
        rel = line[3:].split(" -> ")[-1].strip()
        # fw_version.h is generated into each tree and gitignored; it never shows here.
        if rel and not rel.endswith("/"):
            out.append(rel)
    return sorted(out)


def image_path(target: str) -> Path:
    spec = TARGETS[target]
    if spec.get("kind") == "art":
        return _ROOT / ".pio" / "build" / spec["env"] / "art.bin"
    return _ROOT / ".pio" / "build" / spec["env"] / "firmware.bin"


def fw_version(target: str) -> str | None:
    """The `FW_VERSION` the build stamped into its tree, which is what the board reports.

    The art blob carries none. Its own header holds a crc32, and so does this lock.
    """
    spec = TARGETS[target]
    if spec.get("kind") == "art":
        return None
    header = _ROOT / "firmware" / spec["src"] / "fw_version.h"
    try:
        text = header.read_text()
    except OSError:
        return None
    m = re.search(r'#define\s+FW_VERSION\s+"([^"]*)"', text)
    return m.group(1) if m else None


def build(target: str) -> None:
    """Produce this target's image. A build that fails prints its tail and leaves no image, so
    the target is absent from the survey below and the rest of the manifest goes out."""
    spec = TARGETS[target]
    if spec.get("kind") == "art":
        run = subprocess.run([sys.executable, str(_ROOT / "tools" / "make_art.py"),
                              spec["art_board"], "-q"], cwd=str(_ROOT))
        if run.returncode != 0:
            print(f"  {target}: make_art.py failed")
        return
    run = subprocess.run([str(PIO), "run", "-e", spec["env"]], cwd=str(_ROOT),
                         capture_output=True, text=True)
    if run.returncode != 0:
        tail = "\n".join(run.stdout.splitlines()[-12:])
        print(f"  {target}: `pio run -e {spec['env']}` failed\n{tail}")


def survey(targets: list) -> dict:
    """Each target that has an image on this disk, with everything the lock records about it."""
    out = {}
    for target in targets:
        path = image_path(target)
        if not path.is_file():
            continue
        data = path.read_bytes()
        spec = TARGETS[target]
        out[target] = {
            "env": spec["env"],
            "machine": spec["machine"],
            "what": spec["what"],
            "kind": spec.get("kind", "app"),
            "version": fw_version(target),
            "bytes": len(data),
            # The one the wire promises; MSG_OTA_BEGIN carries this value.
            "crc32": zlib.crc32(data) & 0xFFFFFFFF,
            "sha256": hashlib.sha256(data).hexdigest(),
            "file": f"{target}.bin",
        }
        if spec.get("kind") == "art":
            # The crc32 above is over the file, which is what MSG_OTA_BEGIN
            # promises for the transfer. The one the board reports is over the
            # pixels — it is in the blob's own header, at offset 16 — and that
            # is what says whether the pictures on a board are these pictures.
            out[target]["art_crc32"] = int.from_bytes(data[16:20], "little")
    return out


def pack(images: dict, dest: Path) -> str:
    """Write the bundle at `dest` and return its sha256.

    A member carries its name and its bytes and nothing else — no mtime, no uid, no mode beyond
    0644, and the gzip header carries no filename. So a pack over images that did not move lands
    on the same asset name and the same bytes, and a republish of an unchanged tree is a no-op
    all the way to the release.
    """
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for target in sorted(images):
            src = image_path(target)
            info = tarfile.TarInfo(images[target]["file"])
            info.size = src.stat().st_size
            info.mtime = 0
            info.mode = 0o644
            info.type = tarfile.REGTYPE
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            with open(src, "rb") as fh:
                tar.addfile(info, fh)
    with open(dest, "wb") as fh:
        # `filename=""`: handed a fileobj and no name, GzipFile reads `fileobj.name` into the
        # header, which puts the path this was built at inside the bytes and moves the hash.
        with gzip.GzipFile(filename="", fileobj=fh, mode="wb", compresslevel=6, mtime=0) as gz:
            gz.write(raw.getvalue())
    return _sha256(dest)


def lock_for(images: dict, digest: str, size: int) -> dict:
    asset = f"fw-{digest[:16]}.tar.gz"
    slug = _origin_slug()
    lock = {
        "_": "Written by tools/publish_firmware.py. The images are fetched, not committed —"
             " web/scripts/fetch-firmware.mjs reads this at deploy and /api/firmware serves it.",
        "release": {
            "tag": TAG,
            "asset": asset,
            "url": f"https://github.com/{slug}/releases/download/{TAG}/{asset}",
        },
        "source": {"commit": _head()},
        "bundle": {"sha256": digest, "bytes": size, "images": len(images)},
        "images": images,
    }
    dirty = _dirty()
    if dirty:
        lock["unproven"] = {
            "_": "source.commit does not describe these images: an uncommitted path below"
                 " reaches what built them.",
            "paths": dirty,
        }
    return lock


def read_lock() -> dict:
    try:
        return json.loads(LOCK.read_text())
    except (OSError, ValueError):
        return {}


def _gh(*args, **kw):
    return subprocess.run(["gh", *args], cwd=str(_ROOT), capture_output=True, text=True, **kw)


def upload(bundle: Path, asset: str, digest: str, size: int) -> None:
    """Put `bundle` on the release as `asset`, making the release if it is not there yet.

    The name carries the bundle's own hash, so a name already on the release holds these bytes
    and the upload is skipped. An upload that died partway also leaves the name taken, holding a
    truncated asset — `--clobber` is what lands on that one."""
    listing = _gh("release", "view", TAG, "--json", "assets")
    if listing.returncode != 0:
        made = _gh("release", "create", TAG,
                   "--title", "Firmware images",
                   "--notes", "The images a phone pushes over BLE, fetched at deploy by "
                              "web/scripts/fetch-firmware.mjs and served from /api/firmware. "
                              "Each asset is named by its own sha256 and pinned in "
                              "firmware/firmware.lock.json.")
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
        up = _gh("release", "upload", TAG, str(staged), "--clobber")
    if up.returncode != 0:
        raise SystemExit(f"gh release upload failed:\n{up.stderr}")
    print(f"  uploaded {asset}")


def show(images: dict) -> None:
    if not images:
        print("no images on this disk — build them, or run with --write")
        return
    width = max(len(t) for t in images)
    for target in sorted(images):
        e = images[target]
        version = e["version"] or "—"
        print(f"  {target:<{width}}  {e['bytes']:>9,} B  crc32 {e['crc32']:#010x}  {version}")


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="build, upload and pin")
    ap.add_argument("--check", action="store_true",
                    help="0 = the lock names the images on this disk")
    ap.add_argument("--no-build", action="store_true",
                    help="use whatever .pio/build already holds")
    ap.add_argument("targets", nargs="*", choices=sorted(TARGETS) + [[]],
                    help="targets to publish (default: all)")
    args = ap.parse_args(argv)

    targets = args.targets or sorted(TARGETS)

    if args.check:
        lock = read_lock()
        locked = lock.get("images", {})
        here = survey(targets)
        gaps = []
        for target in sorted(set(locked) | set(here)):
            a, b = locked.get(target), here.get(target)
            if not b:
                continue  # not built on this disk; the lock is not wrong for that
            if not a:
                gaps.append(f"{target} — built here, absent from the lock")
            elif a.get("sha256") != b["sha256"]:
                gaps.append(f"{target} — {b['version'] or 'art'} is not what the lock names")
        if gaps:
            print(f"firmware.lock.json does not name {len(gaps)} image(s) on this disk:")
            for line in gaps:
                print(f"    {line}")
            print("    ~/.platformio/penv/bin/python tools/publish_firmware.py --write")
            return 1
        print(f"{len(here)} image(s) at the locked hash")
        return 0

    if not args.no_build:
        for target in targets:
            print(f"building {target} ({TARGETS[target]['env']})")
            build(target)

    images = survey(targets)
    show(images)
    if not args.write:
        return 0
    if not images:
        return 1

    with tempfile.TemporaryDirectory() as d:
        bundle = Path(d) / "fw.tar.gz"
        digest = pack(images, bundle)
        size = bundle.stat().st_size
        lock = lock_for(images, digest, size)
        upload(bundle, lock["release"]["asset"], digest, size)

    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=False) + "\n")
    print(f"pinned {LOCK.relative_to(_ROOT)} — {lock['release']['asset']} ({size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
