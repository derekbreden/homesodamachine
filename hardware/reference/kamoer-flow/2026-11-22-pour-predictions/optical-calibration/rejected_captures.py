#!/usr/bin/env python3
"""Archive optically inspectable sweep photographs rejected by acquisition before an accepted step was recorded."""

import argparse
import json
from pathlib import Path

import fit_geometry
import mark_crossings
import mark_crossings_v2
import mark_crossings_v3

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", type=Path)
    p.add_argument("--journal", type=Path, required=True)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence/graduations")
    p.add_argument("--out", type=Path, default=HERE / "rejected-crossing-captures.json")
    a = p.parse_args()
    rows = fit_geometry.read_log(a.journal)
    gates = {r["label"]: r for r in rows if r["event"] == "ladder_gate"}
    accepted = {r["label"] for r in rows if r["event"] == "ladder_step"}
    halts = [r["error"] for r in rows if r["event"] == "halt"]
    rejected = []
    for label, g in gates.items():
        if label in accepted:
            continue
        dest = a.evidence / label
        if not (dest / "source.json").exists():
            if a.windows is None or not (a.windows / label / "color.json").exists():
                continue
            dest = fit_geometry.preserve(a.windows / label, a.evidence)
        one = mark_crossings.read(dest)
        two = mark_crossings_v2.read(dest)
        rejected.append(
            {
                "label": label,
                "head": g["head"],
                "leg": g["leg"],
                "acquisition_halt": [h for h in halts if label in h],
                "admitted_to_either_map": False,
                "v1": one,
                "v2": two,
                "v3": mark_crossings_v3.read(dest),
            }
        )
    (a.out).write_text(
        json.dumps(rejected, separators=(",", ":"), allow_nan=False) + "\n"
    )
    print(json.dumps({"retained_rejected_captures": len(rejected)}))


if __name__ == "__main__":
    main()
