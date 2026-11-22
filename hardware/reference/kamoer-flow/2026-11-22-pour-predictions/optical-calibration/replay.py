#!/usr/bin/env python3
"""Store disjoint lossless sensor strips and reconstruct the exact settled readings from the archived pixels."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import cup_volume as frozen
import left_ruler
from mark_crossings import clear_lane

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "evidence"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def boundaries(cols):
    groups = []
    for j in sorted(cols):
        if groups and groups[-1][1] == j:
            groups[-1][1] = j + 1
        else:
            groups.append([j, j + 1])
    return groups


def layout():
    r = {xi for x in frozen.SITES["thirds"] for xi in range(x - 3, x + 4)}
    l = {xi for x in frozen.SITES["quarters"] for xi in range(x - 3, x + 4)}
    ink = {
        xi
        for site, _ in frozen.SCALES.values()
        for xi in range(site - 18, site + 19, 3)
    }
    return {
        "input_size": frozen.NATIVE,
        "crop_ltrb": frozen.CROP,
        "coordinates": "Upright native camera pixels. Every column interval is half open. Rows are contiguous from crop top to crop bottom.",
        "average": boundaries(r),
        "color": boundaries(r | l | ink),
        "clear_lanes": boundaries(
            {v for x in (972, 990, 1018, 1036, 1450, 1986) for v in range(x - 4, x + 5)}
        ),
        "frozen_reader_sha256": sha(HERE / "cup_volume.py"),
        "left_reader_sha256": sha(HERE / "left_ruler.py"),
        "left_check": {
            "printed_x": frozen.SCALES["quarters"][0],
            "surface_patches_x": left_ruler.LEFT_STATIONS,
            "patch_radius": 3,
            "excluded_control_columns_inclusive": left_ruler.CONTROL_COLUMNS,
            "right_primary_x": frozen.SCALES["thirds"][0],
        },
    }


def cols(ranges):
    return (
        np.concatenate([np.arange(start, stop, dtype=int) for start, stop in ranges])
        - frozen.CROP[0]
    )


def atomic_text(path, data):
    temp = path.with_suffix(path.suffix + ".partial")
    temp.write_text(data)
    temp.replace(path)


def reduced_read(raw, detail=False):
    gray, rgb = raw["average"], raw["color"]
    primary = frozen.face(gray, rgb, "thirds", detail)
    held = frozen.face(gray, rgb, "quarters", detail)
    independent = left_ruler.read(rgb, detail)
    return {
        "primary": primary,
        "held_out": held,
        "left_quarters_excluding_control": independent,
    }


def save_clear(path, dt, meta):
    a = np.asarray(frozen.crop(path / "average.png").convert("L"))
    arr = np.ascontiguousarray(a[:, cols(meta["clear_lanes"])])
    tmp = dt / "clear.partial.png"
    Image.fromarray(arr).save(tmp, compress_level=6)
    tmp.replace(dt / "clear.png")


def clear_proof(gray, dt, meta):
    recovered = unpack_arrays(dt, meta)["average"]
    output = {}
    for x in (990, 1986):
        original = clear_lane(gray, x)
        if clear_lane(recovered, x) != original:
            raise ValueError(f"Clear strip differs at {dt.name} x{x}")
        output["x" + str(x)] = {"row": original[0], "contrast": original[1]}
    return output


def one_pack(path, dest, meta):
    label = path.name
    dt = dest / "windows" / label
    dt.mkdir(parents=True, exist_ok=True)
    if (dt / "capture.json").exists():
        capture = json.loads((dt / "capture.json").read_text())
        if capture.get("clear_geometry") and (dt / "clear.png").exists():
            return False
        if not (dt / "clear.png").exists():
            save_clear(path, dt, meta)
        native = np.asarray(frozen.crop(path / "average.png").convert("L"))
        capture["clear_lanes_sha256"] = sha(dt / "clear.png")
        capture["clear_geometry"] = clear_proof(native, dt, meta)
        atomic_text(
            dt / "capture.json", json.dumps(capture, separators=(",", ":")) + "\n"
        )
        return True
    needed = ["average.png", "color.png", "window.json", "color.json"]
    if not all((path / f).is_file() for f in needed):
        return False
    window = json.loads((path / "window.json").read_text())
    color = json.loads((path / "color.json").read_text())
    raw = {}
    for key in ("average", "color"):
        source = path / (key + ".png")
        a = np.asarray(frozen.crop(source).convert("L" if key == "average" else "RGB"))
        selected = cols(meta[key])
        tile = np.ascontiguousarray(a[:, selected])
        target = dt / (key + ".png")
        tmp = dt / (key + ".partial.png")
        Image.fromarray(tile).save(tmp, compress_level=6)
        tmp.replace(target)
        raw[key] = a
    # Compare the actual native image arrays to the replayed arrays through all three scoring paths.
    opened = unpack_arrays(dt, meta)
    full = reduced_read(raw)
    restored = reduced_read(opened)
    if full != restored:
        raise ValueError(
            "Lossless strip replay differs from the complete still at " + label
        )
    save_clear(path, dt, meta)
    summary = {
        "clear_lanes_sha256": sha(dt / "clear.png"),
        "clear_geometry": clear_proof(raw["average"], dt, meta),
        "label": label,
        "mean_luma": {"mid": window["mid"], "frames": window["frames"]},
        "color": color,
        "color_offset_from_luma_mid_s": (color["pts_ns"] - window["mid"]["pts_ns"])
        / 1e9,
        "full_sha256": {f: sha(path / f) for f in needed},
        "packed_sha256": {
            key: sha(dt / (key + ".png")) for key in ("average", "color")
        },
        "reproduces_full_sensor_read": True,
    }
    atomic_text(dt / "capture.json", json.dumps(summary, separators=(",", ":")) + "\n")
    atomic_text(dt / "reading.json", json.dumps(restored, separators=(",", ":")) + "\n")
    return True


def unpack_arrays(dt, meta):
    raw = {}
    h = frozen.CROP[3] - frozen.CROP[1]
    w = frozen.CROP[2] - frozen.CROP[0]
    for key in ("average", "color"):
        with Image.open(dt / (key + ".png")) as im:
            tile = np.asarray(im).copy()
        out = np.zeros((h, w) if key == "average" else (h, w, 3), dtype=np.uint8)
        out[:, cols(meta[key])] = tile
        if key == "average" and (dt / "clear.png").exists():
            with Image.open(dt / "clear.png") as im:
                out[:, cols(meta["clear_lanes"])] = np.asarray(im)
        raw[key] = out
    return raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(required=True, dest="command")
    b = sub.add_parser("pack")
    b.add_argument("window_root", type=Path)
    b.add_argument("--evidence", type=Path, default=DEFAULT)
    b.add_argument("--only", nargs="*")
    for name in ("read", "unpack", "verify"):
        o = sub.add_parser(name)
        o.add_argument("label", nargs="?" if name == "verify" else None)
        o.add_argument("--evidence", type=Path, default=DEFAULT)
        if name == "unpack":
            o.add_argument("destination", type=Path)
        if name == "read":
            o.add_argument("--detail", action="store_true")
    args = p.parse_args()
    ev = args.evidence
    shape = layout()
    if args.command == "pack":
        ev.mkdir(parents=True, exist_ok=True)
        atomic_text(ev / "layout.json", json.dumps(shape, indent=2) + "\n")
        root = args.window_root
        dirs = (
            [root / v for v in args.only]
            if args.only
            else sorted(v for v in root.iterdir() if v.is_dir())
        )
        n = 0
        for source in dirs:
            try:
                n += one_pack(source, ev, shape)
            except (json.JSONDecodeError, OSError) as exc:
                print(f"{source.name}: {exc}", file=sys.stderr)
        print(
            json.dumps(
                {
                    "packed": n,
                    "total": sum(1 for _ in (ev / "windows").glob("*/capture.json")),
                }
            )
        )
        return
    saved = json.loads((ev / "layout.json").read_text())
    if json.loads(json.dumps(shape)) != saved:
        raise ValueError(
            "Frozen reader, independent reader or archived sensor layout changed"
        )
    if args.command == "verify":
        windows = (
            [ev / "windows" / args.label]
            if args.label
            else sorted(p.parent for p in (ev / "windows").glob("*/capture.json"))
        )
        for dt in windows:
            capture = json.loads((dt / "capture.json").read_text())
            expected = json.loads((dt / "reading.json").read_text())
            if any(
                sha(dt / (key + ".png")) != h
                for key, h in capture["packed_sha256"].items()
            ):
                raise ValueError(dt.name + " digest mismatch")
            if sha(dt / "clear.png") != capture["clear_lanes_sha256"]:
                raise ValueError(dt.name + " operating strip digest mismatch")
            if reduced_read(unpack_arrays(dt, saved)) != expected:
                raise ValueError(dt.name + " replay mismatch")
        print(json.dumps({"verified_from_pixels": len(windows)}))
        return
    dt = ev / "windows" / args.label
    raw = unpack_arrays(dt, saved)
    if args.command == "unpack":
        args.destination.mkdir(parents=True, exist_ok=True)
        for key, a in raw.items():
            Image.fromarray(a).save(args.destination / (key + ".png"))
    else:
        print(json.dumps(reduced_read(raw, args.detail), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
