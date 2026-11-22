#!/usr/bin/env python3
"""Preserve signed crossing brackets, including those the frozen map excludes for width or optical margin."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from fit_geometry import LANES, margin
from mark_crossings import MARKS
from score_optics import output_csv

HERE = Path(__file__).resolve().parent


def diagnose(rows):
    segments = defaultdict(list)
    for s in rows:
        if s["controller_accepted"] and s["segment"]:
            segments[s["segment"]].append(s)
    answers = []
    for segment, steps in segments.items():
        for name in MARKS:
            observed = []
            for s in sorted(steps, key=lambda r: r["pts_ns"]):
                m = s["marks"][name]
                d = m.get("contact_minus_ink_px")
                if not m["ok"] or d is None or abs(d) > 30 or abs(d) <= margin(m):
                    continue
                if (
                    s.get("logged_x990_row") is not None
                    and abs(s["clear_row"] - s["logged_x990_row"]) > 3.5
                ):
                    continue
                observed.append((s, d, margin(m)))
            for (a, da, ea), (b, db, eb) in zip(observed, observed[1:]):
                if da * db >= 0:
                    continue
                span = abs(b["clear_row"] - a["clear_row"])
                flags = []
                if span > 20:
                    flags.append("raw bracket width exceeds frozen limit")
                if max(abs(da), abs(db)) > 25:
                    flags.append("contact lies outside frozen fitting neighborhood")
                if (b["clear_row"] - a["clear_row"]) * (db - da) <= 0:
                    flags.append("liquid sign and x990 ordering disagree")
                if (
                    min(a["clear_contrast"], b["clear_contrast"]) < 7
                    or min(a["right_clear_contrast"], b["right_clear_contrast"]) < 5
                ):
                    flags.append("clear lane below frozen optical contrast")
                v = {
                    "segment": segment,
                    "direction": a["direction"],
                    "mark": name,
                    "first": a["label"],
                    "second": b["label"],
                    "first_contact_minus_ink_px": da,
                    "second_contact_minus_ink_px": db,
                    "x990_span_px": span,
                    "rule_eligible": not flags,
                    "flags": " | ".join(flags),
                }
                for x, field in LANES.items():
                    ya, yb = a[field], b[field]
                    v[x + "_row"] = ya + (yb - ya) * (-da) / (db - da)
                    roots = [
                        ya + (yb - ya) * (-s1) / (s2 - s1)
                        for s1 in (da - ea, da + ea)
                        for s2 in (db - eb, db + eb)
                        if s1 * s2 < 0
                    ]
                    v[x + "_local_low"] = min(roots) - 0.5
                    v[x + "_local_high"] = max(roots) + 0.5
                answers.append(v)
    return answers


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--observations", type=Path, default=HERE / "graduation-observations-v2.json"
    )
    p.add_argument("--out", type=Path, default=HERE / "crossing-brackets-v2.csv")
    a = p.parse_args()
    rows = diagnose(json.loads(a.observations.read_text()))
    output_csv(a.out, rows)
    print(
        json.dumps(
            {
                "raw_brackets": len(rows),
                "eligible": sum(r["rule_eligible"] for r in rows),
            }
        )
    )
