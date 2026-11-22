#!/usr/bin/env python3
"""Re-measure every graduation crop from its lossless PNGs and verify the reported lowering map and held-out crossings."""

import argparse
import hashlib
import json
from pathlib import Path

import fit_geometry
import mark_crossings
import mark_crossings_v2
import fit_geometry_v2
import mark_crossings_v3
import fit_geometry_v3

HERE = Path(__file__).resolve().parent


def verify(mapfile, observations, evidence):
    expected = json.loads(mapfile.read_text())
    rev = expected.get("clear_lane_reader")
    revised = rev in ("mark_crossings_v2", "mark_crossings_v3")
    sensor = {
        "mark_crossings_v2": mark_crossings_v2.read,
        "mark_crossings_v3": mark_crossings_v3.read,
    }.get(rev, mark_crossings.read)
    map_fn = {
        "mark_crossings_v2": fit_geometry_v2.model,
        "mark_crossings_v3": fit_geometry_v3.model,
    }.get(rev, fit_geometry.geometry)
    rows = json.loads(observations.read_text())
    new = []
    for sample in rows:
        d = evidence / sample["label"]
        measured = sensor(d)
        if (
            revised
            and mark_crossings.read(d)["clear_row"] != sample["original_wide_x990"]
        ):
            raise ValueError(sample["label"] + " original raw edge differs")
        if any(sample[k] != v for k, v in measured.items()):
            raise ValueError(
                sample["label"] + " archived cap reading differed from pixels"
            )
        new.append({**sample, **measured})
    model = map_fn(new)
    if model != expected:
        raise ValueError(
            "Archived cap pixels and sweep directions did not reconstruct the supplied map"
        )
    return {
        "verified_graduation_windows": len(rows),
        "lowering_anchors": len(model["anchors"]["x990"]),
        "map_status": model["status"],
        "formal_map_sha256": hashlib.sha256(mapfile.read_bytes()).hexdigest(),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence/graduations")
    p.add_argument(
        "--observations", type=Path, default=HERE / "graduation-observations.json"
    )
    p.add_argument("--map", type=Path, default=HERE / "geometry-map.json")
    p.add_argument(
        "--all",
        action="store_true",
        help="Verify each frozen reader and both selected grids",
    )
    args = p.parse_args()
    if not args.all:
        print(json.dumps(verify(args.map, args.observations, args.evidence)))
        return
    from select_map import build
    from provisional_grid import grid

    summary = {}
    for suffix in ("", "-v2", "-v3"):
        formal = HERE / ("geometry-map" + suffix + ".json")
        obs = HERE / ("graduation-observations" + suffix + ".json")
        summary[formal.name] = verify(formal, obs, args.evidence)
    selected = build(HERE, True)
    obs = json.loads((HERE / "graduation-observations-v3.json").read_text())
    stop = next(x["pts_ns"] for x in obs if x["label"] == "ladder5-held-out-up-31")
    early = [x for x in obs if x["pts_ns"] <= stop]
    diagnostic = grid(fit_geometry_v3.model(early), early)
    for filename, computed in (
        ("geometry-used.json", selected),
        ("provisional-geometry-map.json", diagnostic),
    ):
        actual = (HERE / filename).read_bytes()
        if (json.dumps(computed, indent=2, allow_nan=False) + "\n").encode() != actual:
            raise ValueError(
                filename + " differs from the signed physical crossing reconstruction"
            )
        summary[filename] = {
            "verified_byte_exact": True,
            "sha256": hashlib.sha256(actual).hexdigest(),
        }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
