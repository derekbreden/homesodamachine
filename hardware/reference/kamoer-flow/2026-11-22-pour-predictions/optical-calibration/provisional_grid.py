#!/usr/bin/env python3
"""Apply the prospectively declared fallback hierarchy while preserving the official lowering-only outcome."""

import argparse
import json
from pathlib import Path

from bracket_diagnostics import diagnose
from fit_geometry import ANCHORS, LANES, at_anchor_check, atomic_text
from fit_geometry_v3 import HELD_OUT, model as formal_map
from mark_crossings import MARKS
from cup_volume import CUP_ML

HERE = Path(__file__).resolve().parent


def grid(official, observations):
    output = {
        "clear_lane_reader": "mark_crossings_v3",
        "status": "provisional printed-graduation grid",
        "formal_lowering_status": official["status"],
        "anchors": {site: [] for site in LANES},
        "sources": {},
        "independent_reserved_checks": {site: {} for site in LANES},
        "flags": [],
    }
    broad = diagnose(observations)
    for key in ANCHORS:
        known = MARKS[key]["cups"] * CUP_ML
        prior = official["lowering"].get(key)
        if prior:
            source = {
                "method": "qualifying lowering crossing",
                "labels": [b["labels"] for b in prior["brackets"]],
                "rows": prior["rows"],
                "brackets": prior["brackets"],
            }
        else:
            earlier = next(
                (
                    b
                    for b in official["diagnostic_only_all_rising_brackets"]
                    .get(key, {})
                    .get("brackets", [])
                    if all(not l.startswith(HELD_OUT[key]) for l in b["labels"])
                ),
                None,
            )
            if earlier:
                source = {
                    "method": "first qualifying exploratory rising crossing",
                    "labels": earlier["labels"],
                    "rows": earlier["interpolated_rows"],
                    "brackets": [earlier],
                }
            else:
                cand = [
                    b
                    for b in broad
                    if b["mark"] == key
                    and b["direction"] == "lowering"
                    and b["x990_span_px"] <= 35
                ]
                if not cand:
                    output["flags"].append(
                        key + " lacks a qualified or provisional observed crossing"
                    )
                    continue
                pair = min(cand, key=lambda v: v["x990_span_px"])
                source = {
                    "method": "nearby signed lowering pair within provisional bracket width",
                    "labels": [pair["first"], pair["second"]],
                    "rows": {k: pair[k + "_row"] for k in LANES},
                    "brackets": [pair],
                }
        output["sources"][key] = {"nominal_ml": known, **source}
        for lane in LANES:
            output["anchors"][lane].append([source["rows"][lane], known])
    for lane, pairs in output["anchors"].items():
        pairs.sort()
        if len(pairs) != 3:
            continue
        for key in ANCHORS:
            reserved = official["rising"].get(key)
            if reserved is None:
                continue
            y = reserved["rows"][lane]
            v = at_anchor_check(pairs, y)
            target = reserved["nominal_ml"]
            output["independent_reserved_checks"][lane][key] = {
                "row": y,
                "nominal_ml": target,
                "predicted_ml": v,
                "error_ml": v - target,
                "within_1_5_ml": abs(v - target) <= 1.5,
                "interpretation": "across direction"
                if output["sources"][key]["method"] == "qualifying lowering crossing"
                else "repeatability against substituted anchor",
            }
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--map", type=Path, default=HERE / "geometry-map-v3.json")
    p.add_argument(
        "--observations", type=Path, default=HERE / "graduation-observations-v3.json"
    )
    p.add_argument(
        "--through",
        default="ladder5-held-out-up-31",
        help="Last stored exposure of the early diagnostic. Use 'all' for the terminal reduction.",
    )
    p.add_argument("--out", type=Path, help="Save a separate diagnostic reconstruction")
    a = p.parse_args()
    observations = json.loads(a.observations.read_text())
    if a.through == "all":
        official = json.loads(a.map.read_text())
    else:
        cut = next(row["pts_ns"] for row in observations if row["label"] == a.through)
        observations = [row for row in observations if row["pts_ns"] <= cut]
        official = formal_map(observations)
    m = grid(official, observations)
    if a.out:
        atomic_text(a.out, json.dumps(m, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "anchors": m["anchors"],
                "sources": {k: v["method"] for k, v in m["sources"].items()},
            }
        )
    )
