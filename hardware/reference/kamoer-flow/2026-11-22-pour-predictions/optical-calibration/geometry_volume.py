#!/usr/bin/env python3
"""Measure two clear-glass liquid contacts against the selected photographed graduation map."""

import argparse
import json
from pathlib import Path

import numpy as np

import cup_volume
from fit_geometry import map_ml
from mark_crossings import clear_lane
from mark_crossings_v2 import clear_lane as revised_clear_lane
from mark_crossings_v3 import clear_lane as range_limited_clear_lane

HERE = Path(__file__).resolve().parent


def from_gray(gray, model):
    reader = {
        "mark_crossings_v2": revised_clear_lane,
        "mark_crossings_v3": range_limited_clear_lane,
    }.get(model.get("clear_lane_reader"), clear_lane)
    out = {}
    for key, site in [("x990", 990), ("x1986", 1986)]:
        y, contrast = reader(gray, site)
        pairs = model["anchors"].get(key, [])
        value = map_ml(pairs, y)
        flags = []
        if len(pairs) != 3:
            flags.append("selected graduation map incomplete")
        if value is None:
            flags.append("outside photographed graduation interval")
        if contrast < 6:
            flags.append("weak clear-glass contact")
        out[key] = {
            "ok": not flags,
            "flags": flags,
            "row": y,
            "contrast": contrast,
            "nominal_ml": value if not flags else None,
        }
    return out


def read(window, model=None):
    window = Path(window)
    if model is None:
        model = json.loads((HERE / "geometry-used.json").read_text())
    if (window / "capture.json").is_file() and (window / "clear.png").is_file():
        from replay import unpack_arrays

        layout = json.loads((window.parent.parent / "layout.json").read_text())
        gray = unpack_arrays(window, layout)["average"]
    else:
        gray = np.asarray(cup_volume.crop(window / "average.png").convert("L"))
    return from_gray(gray, model)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("window", type=Path)
    p.add_argument("--map", type=Path, default=HERE / "geometry-used.json")
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
