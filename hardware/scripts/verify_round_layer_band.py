#!/usr/bin/env python3
"""Check emitted wall layer heights across measured curved-edge print-Z spans.

Pass spans measured from the printable STEP in its plate orientation. The 3MF range
declaration alone is insufficient: the slicer can let a coarse layer cross its lower
boundary before switching to the requested height.

Example::

    python3 hardware/scripts/verify_round_layer_band.py \
        --gcode path/to/plate.gcode.3mf --object-id 1901 \
        --span roof-corners:187.392:195 --height 0.08
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from contextlib import contextmanager
from pathlib import Path


EXTRUSION = re.compile(r"(?:^|\s)E([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
WALL_FEATURES = {"Outer wall", "Inner wall", "Overhang wall"}


@contextmanager
def gcode_lines(path: Path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            member = next((name for name in archive.namelist()
                           if name.endswith("plate_1.gcode")), None)
            if member is None:
                raise ValueError("archive has no plate_1.gcode")
            with archive.open(member) as source:
                yield (line.decode("utf-8", "replace") for line in source)
    else:
        with path.open(errors="replace") as source:
            yield source


def wall_layers(path: Path, object_id: int) -> list[tuple[float, float]]:
    layers: set[tuple[float, float]] = set()
    z = height = None
    current_object = None
    feature = None
    with gcode_lines(path) as lines:
        for line in lines:
            if line.startswith("; Z_HEIGHT:"):
                z = float(line.split(":", 1)[1])
                height = None
                feature = None
                current_object = None
            elif line.startswith("; LAYER_HEIGHT:"):
                height = float(line.split(":", 1)[1])
            elif line.startswith("; OBJECT_ID:"):
                current_object = int(line.split(":", 1)[1])
                feature = None
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif (line.startswith(("G1 ", "G2 ", "G3 ")) and z is not None
                  and height is not None and current_object == object_id
                  and feature in WALL_FEATURES):
                extrusion = EXTRUSION.search(line)
                if extrusion and float(extrusion.group(1)) > 0:
                    layers.add((round(z, 6), round(height, 6)))
    return sorted(layers)


def check_span(layers: list[tuple[float, float]], name: str, low: float,
               high: float, target: float, tolerance: float) -> dict:
    hits = [(z, height) for z, height in layers
            if z > low and z - height < high]
    bad = [{"z_mm": z, "height_mm": height} for z, height in hits
           if abs(height - target) > tolerance]
    coverage = sorted((max(low, z - height), min(high, z))
                      for z, height in hits if abs(height - target) <= tolerance)
    cursor = low
    gaps = []
    for start, end in coverage:
        if start - cursor > 0.02:
            gaps.append([round(cursor, 6), round(start, 6)])
        cursor = max(cursor, end)
    if high - cursor > 0.02:
        gaps.append([round(cursor, 6), round(high, 6)])
    return {
        "name": name,
        "print_z_mm": [low, high],
        "wall_layer_count": len(hits),
        "first_wall_layer": list(hits[0]) if hits else None,
        "last_wall_layer": list(hits[-1]) if hits else None,
        "wrong_height_layers": bad,
        "uncovered_intervals_mm": gaps,
        "pass": bool(hits) and not bad and not gaps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcode", required=True, type=Path)
    parser.add_argument("--object-id", required=True, type=int)
    parser.add_argument("--span", action="append", required=True,
                        help="name:lower_print_z:upper_print_z")
    parser.add_argument("--height", type=float, default=0.08)
    parser.add_argument("--tolerance", type=float, default=0.001)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    spans = []
    for value in args.span:
        name, low, high = value.rsplit(":", 2)
        low, high = float(low), float(high)
        if not name or low < 0 or high <= low:
            parser.error(f"invalid span: {value}")
        spans.append((name, low, high))
    layers = wall_layers(args.gcode, args.object_id)
    result = {
        "gcode": str(args.gcode),
        "object_id": args.object_id,
        "requested_layer_height_mm": args.height,
        "spans": [check_span(layers, name, low, high, args.height, args.tolerance)
                  for name, low, high in spans],
    }
    result["pass"] = all(span["pass"] for span in result["spans"])
    payload = json.dumps(result, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload)
    sys.stdout.write(payload)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
