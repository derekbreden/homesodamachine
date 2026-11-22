#!/usr/bin/env python3
"""Read a dose independently on two clear-glass lanes using the lowering-only printed-graduation map."""

import argparse
import json
from pathlib import Path

import numpy as np

import cup_volume
from fit_geometry import map_ml
from mark_crossings import clear_lane

HERE = Path(__file__).resolve().parent


def from_gray(gray, model):
    out = {}
    for key, site in [("x990", 990), ("x1986", 1986)]:
        y, contrast = clear_lane(gray, site)
        pairs = model["anchors"].get(key, [])
        value = map_ml(pairs, y)
        flags = []
        if len(pairs) != 3:
            flags.append("lowering graduation map incomplete")
        if value is None:
            flags.append("outside photographed graduation interval")
        if contrast < (7 if key == "x990" else 5):
            flags.append("weak clear-glass contact")
        out[key] = {
            "ok": not flags,
            "flags": flags,
            "row": y,
            "contrast": contrast,
            "nominal_ml": value,
        }
    return out


def read(window, model):
    window = Path(window)
    gray = np.asarray(cup_volume.crop(window / "average.png").convert("L"))
    return from_gray(gray, model)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("window", type=Path)
    p.add_argument("--map", type=Path, default=HERE / "geometry-map.json")
    p.add_argument("--before", type=Path)
    a = p.parse_args()
    m = json.loads(a.map.read_text())
    after = read(a.window, m)
    if a.before:
        before = read(a.before, m)
        print(
            json.dumps(
                {
                    "before": before,
                    "after": after,
                    "nominal_change_ml": {
                        k: (after[k]["nominal_ml"] - before[k]["nominal_ml"])
                        if before[k]["ok"] and after[k]["ok"]
                        else None
                        for k in after
                    },
                },
                indent=2,
            )
        )
    else:
        print(json.dumps(after, indent=2))


if __name__ == "__main__":
    main()
