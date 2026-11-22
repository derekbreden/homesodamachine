#!/usr/bin/env python3
"""Retain the original crossing analysis and fit the separately frozen wide-range glass-lane correction from lowering only."""

import argparse
import json
from pathlib import Path

import fit_geometry as original
import mark_crossings_v2 as reader

HERE = Path(__file__).resolve().parent
REVISION = "mark_crossings_v2"


def samples(windows, journal, dest, recompute=False):
    previous = original.read_samples(windows, journal, dest)
    return samples_from_original(previous, dest, recompute)


def samples_from_original(previous, dest, recompute=False):
    out = []
    for initial in previous:
        d = dest / initial["label"]
        saved = d / "cap-reading-v2.json"
        if saved.is_file() and not recompute:
            q = json.loads(saved.read_text())
        else:
            q = reader.read(d)
            original.atomic_text(
                saved, json.dumps(q, separators=(",", ":"), allow_nan=False) + "\n"
            )
        out.append(
            {
                **initial,
                **q,
                "original_wide_x990": initial["clear_row"],
                "neighbor_reacquisition": abs(q["clear_row"] - initial["clear_row"])
                > 3.5,
            }
        )
    return out


def model(rows):
    m = original.geometry(rows)
    m["clear_lane_reader"] = REVISION
    m["independent_lane"] = "x1986"
    m["original_glass_ray_failures"] = [
        {
            "label": s["label"],
            "original_row": s["original_wide_x990"],
            "revised_row": s["clear_row"],
            "continuity_row": s["logged_x990_row"],
            "leg": s["leg"],
        }
        for s in rows
        if s["neighbor_reacquisition"]
    ]
    m["method_revision"] = (
        "The left clear-lane seed uses consensus on neighboring camera columns to reject a stationary wall reflection. The physical graduation reader, disjoint right lane and lowering-only bracket rules retain the original definitions."
    )
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", type=Path)
    p.add_argument("--journal", type=Path, required=True)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence/graduations")
    p.add_argument("--out", type=Path, default=HERE / "geometry-map-v2.json")
    p.add_argument(
        "--samples", type=Path, default=HERE / "graduation-observations-v2.json"
    )
    p.add_argument("--from-pixels", action="store_true")
    args = p.parse_args()
    rows = samples(
        args.windows, original.read_log(args.journal), args.evidence, args.from_pixels
    )
    m = model(rows)
    original.atomic_text(args.out, json.dumps(m, indent=2, allow_nan=False) + "\n")
    original.atomic_text(
        args.samples, json.dumps(rows, separators=(",", ":"), allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "status": m["status"],
                "lowering": m["anchors"],
                "rising_repeatability": m.get("direction_repeatability"),
                "corrected_windows": len(m["original_glass_ray_failures"]),
            }
        )
    )


if __name__ == "__main__":
    main()
