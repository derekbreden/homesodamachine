#!/usr/bin/env python3
"""Locate photographed graduation sign changes on each sweep and test the rising crossings against a lowering-only calibration."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import cup_volume as frozen
import mark_crossings as marks
from replay import atomic_text

HERE = Path(__file__).resolve().parent
ANCHORS = ("quarter_three_quarters", "quarter_one", "quarter_one_and_quarter")
LANES = {"x990": "clear_row", "x1986": "right_clear_row"}


def read_log(path):
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            break
    return out


def preserve(window, dest):
    d = dest / window.name
    d.mkdir(parents=True, exist_ok=True)
    if not (d / "source.json").exists():
        for key in ("average", "color"):
            frozen.crop(window / (key + ".png")).save(
                d / (key + ".png"), compress_level=5
            )
        cap = json.loads((window / "window.json").read_text())
        co = json.loads((window / "color.json").read_text())
        st = {
            "label": window.name,
            "mid": cap["mid"],
            "frames": cap["frames"],
            "color": co,
            "full_sha256": {
                k: hashlib.sha256((window / k).read_bytes()).hexdigest()
                for k in ("average.png", "color.png")
            },
        }
        atomic_text(d / "source.json", json.dumps(st, separators=(",", ":")) + "\n")
    return d


def read_samples(windows, journal, destination):
    steps = {ev["label"]: ev for ev in journal if ev["event"] == "ladder_step"}
    gates = {ev["label"]: ev for ev in journal if ev["event"] == "ladder_gate"}
    items = [ev for ev in journal if ev["event"] == "ladder_image"]
    out = []
    for ev in items:
        name = ev["label"]
        d = destination / name
        if not (d / "source.json").exists():
            if windows is None or not (windows / name / "color.json").is_file():
                continue
            d = preserve(windows / name, destination)
        measured = d / "cap-reading.json"
        if measured.exists():
            data = json.loads(measured.read_text())
        else:
            data = marks.read(d)
            atomic_text(
                measured,
                json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n",
            )
        s = steps.get(name, {})
        gt = gates.get(name, {})
        leg = s.get("leg") or gt.get("leg")
        direction = {"A": "lowering", "B": "rising"}.get(
            s.get("head") or gt.get("head")
        )
        src = json.loads((d / "source.json").read_text())
        out.append(
            {
                **data,
                "direction": direction,
                "leg": leg,
                "segment": name.rsplit("-" + leg + "-", 1)[0] + "/" + leg
                if leg and "-" + leg + "-" in name
                else None,
                "controller_accepted": bool(s),
                "logged_x990_row": ev.get("lanes", {}).get("990", {}).get("row"),
                "pts_ns": src["mid"]["pts_ns"],
            }
        )
    return out


def margin(mark):
    return max(
        0.75,
        mark["ink_fit_mad_px"]
        + mark["adjacent_mad_px"] * 0.55
        + abs(mark["close_minus_adjacent_px"] or 0) * 0.45
        + abs(mark.get("tangent_minus_adjacent_median_px", 0)) * 0.25,
    )


def roots(segment, key):
    observed = []
    for row in sorted(segment, key=lambda v: v["pts_ns"]):
        logged = row.get("logged_x990_row")
        if logged is not None and abs(row["clear_row"] - logged) > 3.5:
            continue
        m = row["marks"][key]
        d = m.get("contact_minus_ink_px")
        if (
            not m["ok"]
            or d is None
            or abs(d) > 25
            or row["clear_contrast"] < 7
            or row["right_clear_contrast"] < 5
        ):
            continue
        # A signed frame only brackets a crossing when it clears local pigment and flank variation.
        error = margin(m)
        if abs(d) <= error:
            continue
        observed.append((row, d, error))
    out = []
    for (a, da, ea), (b, db, eb) in zip(observed, observed[1:]):
        if da * db >= 0:
            continue
        signed = (b["clear_row"] - a["clear_row"]) * (db - da)
        if signed <= 0:
            continue
        span = abs(b["clear_row"] - a["clear_row"])
        if span > 20:
            continue
        values = {}
        bounds = {}
        for site, field in LANES.items():
            ya, yb = a[field], b[field]
            values[site] = float(ya + (yb - ya) * (-da) / (db - da))
            ends = []
            for d1 in (da - ea, da + ea):
                for d2 in (db - eb, db + eb):
                    if d1 * d2 < 0:
                        ends.append(ya + (yb - ya) * (-d1) / (d2 - d1))
            bounds[site] = [float(min(ends) - 0.5), float(max(ends) + 0.5)]
        out.append(
            {
                "labels": [a["label"], b["label"]],
                "segment": a["segment"],
                "row_span_px": span,
                "contact_minus_ink_px": [da, db],
                "flank_allowances_px": [ea, eb],
                "observed_rows": {
                    site: [a[field], b[field]] for site, field in LANES.items()
                },
                "interpolated_rows": values,
                "local_sensitivity_range_px": bounds,
            }
        )
    return out


def map_ml(pairs, row):
    if len(pairs) < 2 or row < pairs[0][0] or row > pairs[-1][0]:
        return None
    return float(np.interp(row, [v[0] for v in pairs], [v[1] for v in pairs]))


def at_anchor_check(pairs, row):
    # Evaluate a held-out crossing against the edge segment even just outside the fitted endpoint.
    # Only the direction check uses this labeled signed distance. Dose conversion stays bracketed.
    nearest = min(range(len(pairs)), key=lambda k: abs(pairs[k][0] - row))
    j = min(max(nearest - 1 if row < pairs[nearest][0] else nearest, 0), len(pairs) - 2)
    (x1, v1), (x2, v2) = pairs[j : j + 2]
    return float(v1 + (v2 - v1) * (row - x1) / (x2 - x1))


def geometry(samples):
    out = {
        "status": "waiting for lowering crossings",
        "unit": "US customary printed cup converted to nominal mL",
        "anchors": {k: [] for k in LANES},
        "lowering": {},
        "rising": {},
        "rising_checks": {},
        "left_right_one_cup": {},
        "middle_omitted_checks": {},
        "flags": [],
        "counts": {
            "captured": len(samples),
            "accepted_steps": sum(bool(a["controller_accepted"]) for a in samples),
        },
    }
    for direction in ("lowering", "rising"):
        subset = [
            s
            for s in samples
            if s["direction"] == direction and s["controller_accepted"]
        ]
        segments = sorted({s["segment"] for s in subset if s["segment"]})
        for name in marks.MARKS:
            found = [
                cross
                for segment in segments
                for cross in roots([s for s in subset if s["segment"] == segment], name)
            ]
            if not found:
                continue
            vol = marks.MARKS[name]["cups"] * frozen.CUP_ML
            aggregate = {
                site: float(np.median([c["interpolated_rows"][site] for c in found]))
                for site in LANES
            }
            out[direction][name] = {
                "nominal_ml": vol,
                "rows": aggregate,
                "brackets": found,
            }
            if direction == "lowering" and name in ANCHORS:
                for site, y in aggregate.items():
                    out["anchors"][site].append([y, vol])
        l = out[direction].get("quarter_one")
        r = out[direction].get("thirds_one")
        if l and r:
            out["left_right_one_cup"][direction] = {
                k: r["rows"][k] - l["rows"][k] for k in LANES
            }
    for pairs in out["anchors"].values():
        pairs.sort()
    if len(out["anchors"]["x990"]) != 3:
        out["flags"].append(
            "one or more lowering graduation tips lack confident sign-changing frames"
        )
        return out
    for site, pairs in out["anchors"].items():
        if not all(pairs[i][1] > pairs[i + 1][1] for i in range(2)):
            out["flags"].append(site + " lowering crossings are non-monotone")
            return out
        mid = out["lowering"]["quarter_one"]
        out["middle_omitted_checks"][site] = (
            map_ml([pairs[0], pairs[-1]], mid["rows"][site]) - mid["nominal_ml"]
        )
        out["rising_checks"][site] = {}
        for name in ANCHORS:
            rising = out["rising"].get(name)
            if rising is None:
                continue
            y = rising["rows"][site]
            v = at_anchor_check(pairs, y)
            err = v - rising["nominal_ml"]
            out["rising_checks"][site][name] = {
                "row": y,
                "nominal_ml": rising["nominal_ml"],
                "predicted_ml": v,
                "error_ml": err,
                "within_1_5_ml": bool(abs(err) <= 1.5),
                "beyond_lowering_span": bool(y < pairs[0][0] or y > pairs[-1][0]),
            }
    out["status"] = "lowering map available"
    out["direction_repeatability"] = {
        k: (all(v["within_1_5_ml"] for v in site.values()) if len(site) == 3 else None)
        for k, site in out["rising_checks"].items()
    }
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--windows",
        type=Path,
        help="Native named camera windows; omit to replay archived graduation crops",
    )
    p.add_argument("--journal", type=Path, required=True)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence/graduations")
    p.add_argument("--out", type=Path, default=HERE / "geometry-map.json")
    p.add_argument(
        "--samples", type=Path, default=HERE / "graduation-observations.json"
    )
    args = p.parse_args()
    samples = read_samples(args.windows, read_log(args.journal), args.evidence)
    o = geometry(samples)
    atomic_text(args.out, json.dumps(o, indent=2, allow_nan=False) + "\n")
    atomic_text(
        args.samples, json.dumps(samples, separators=(",", ":"), allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "status": o["status"],
                "anchors": o["anchors"],
                "held_out": o.get("direction_repeatability"),
                **o["counts"],
            }
        )
    )


if __name__ == "__main__":
    main()
