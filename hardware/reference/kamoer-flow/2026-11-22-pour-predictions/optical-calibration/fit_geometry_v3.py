#!/usr/bin/env python3
"""Fit the range-limited clear rows on lowering and score only the prospectively reserved rising traversals."""

import argparse
import json
from pathlib import Path

import fit_geometry as original
import mark_crossings_v3 as reader

HERE = Path(__file__).resolve().parent
HELD_OUT = {
    "quarter_three_quarters": "ladder4-back-to-work-",
    "quarter_one": "ladder5-held-out-up-",
    "quarter_one_and_quarter": "ladder5-held-out-up-",
}


def samples_from_original(previous, dest, recompute=False):
    out = []
    for v in previous:
        d = dest / v["label"]
        saved = d / "cap-reading-v3.json"
        if saved.is_file() and not recompute:
            q = json.loads(saved.read_text())
        else:
            q = reader.read(d)
            original.atomic_text(
                saved, json.dumps(q, separators=(",", ":"), allow_nan=False) + "\n"
            )
        out.append(
            {
                **v,
                **q,
                "original_wide_x990": v["clear_row"],
                "lower_range_branch": v["clear_row"] >= reader.LOWER_RANGE_START,
                "neighbor_reacquisition": abs(q["clear_row"] - v["clear_row"]) > 3.5,
            }
        )
    return out


def expected_branch(row, mark):
    return row["label"].startswith(HELD_OUT.get(mark, "__diagnostic__"))


def model(samples):
    # Preserve the lowering calibration as soon as every requested graduation has a qualifying sign change.
    diagnostic = original.geometry(samples)
    times = {s["label"]: s["pts_ns"] for s in samples}
    lower = diagnostic["lowering"]
    cutoff = None
    if all(k in lower for k in original.ANCHORS):
        first_completion = [
            min(
                max(times[label] for label in bracket["labels"])
                for bracket in lower[k]["brackets"]
            )
            for k in original.ANCHORS
        ]
        cutoff = max(first_completion)
    admitted = []
    for row in samples:
        copy = dict(row)
        if row["direction"] == "rising":
            copy["marks"] = {
                name: {**data, "ok": data["ok"] and expected_branch(row, name)}
                for name, data in row["marks"].items()
            }
        if (
            cutoff is not None
            and row["direction"] == "lowering"
            and row["pts_ns"] > cutoff
        ):
            copy["controller_accepted"] = False
        admitted.append(copy)
    out = original.geometry(admitted)
    out["clear_lane_reader"] = "mark_crossings_v3"
    out["rising_eligibility_prefix"] = HELD_OUT
    out["lowering_cutoff_after_first_complete_anchor_set_pts_ns"] = cutoff
    out["diagnostic_only_all_rising_brackets"] = diagnostic["rising"]
    out["diagnostic_only_left_right_one_cup_rising"] = diagnostic[
        "left_right_one_cup"
    ].get("rising")
    out["range_branch_at_original_x990_y"] = reader.LOWER_RANGE_START
    out["primary"] = "x990"
    out["independent_lane"] = "x1986"
    out["reacquired_windows"] = [
        row["label"] for row in samples if row["neighbor_reacquisition"]
    ]
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", type=Path)
    p.add_argument("--journal", type=Path, required=True)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence/graduations")
    p.add_argument("--out", type=Path, default=HERE / "geometry-map-v3.json")
    p.add_argument(
        "--samples", type=Path, default=HERE / "graduation-observations-v3.json"
    )
    p.add_argument("--from-pixels", action="store_true")
    args = p.parse_args()
    previous = original.read_samples(
        args.windows, original.read_log(args.journal), args.evidence
    )
    rows = samples_from_original(previous, args.evidence, args.from_pixels)
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
                "reserved_rising_repeatability": m.get("direction_repeatability"),
            }
        )
    )


if __name__ == "__main__":
    main()
