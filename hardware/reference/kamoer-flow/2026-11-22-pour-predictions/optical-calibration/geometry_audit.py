#!/usr/bin/env python3
"""Recheck clear-lane dose predictions, stopped-cup drift and calibration coverage from the preserved camera pixels."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import t as student

import replay
import recipe_audit
from fit_geometry import at_anchor_check, map_ml, read_log
from mark_crossings import clear_lane
from mark_crossings_v2 import clear_lane as revised_clear_lane
from mark_crossings_v3 import clear_lane as range_limited_clear_lane, LOWER_RANGE_START
from score_optics import output_csv, stats

HERE = Path(__file__).resolve().parent
LANES = {"x990": 990, "x1986": 1986}


def endpoints(evidence, model, fast=False):
    layout = json.loads((evidence / "layout.json").read_text())
    v2 = model.get("clear_lane_reader") == "mark_crossings_v2"
    v3 = model.get("clear_lane_reader") == "mark_crossings_v3"
    reader = (
        range_limited_clear_lane if v3 else (revised_clear_lane if v2 else clear_lane)
    )
    out = {}
    for q in sorted((evidence / "windows").glob("*/capture.json")):
        p = q.parent
        capt = json.loads(q.read_text())
        cached = capt.get("clear_geometry_v2" if v2 else "clear_geometry", {})
        if v3 and capt.get("clear_geometry") and capt.get("clear_geometry_v2"):
            native = capt["clear_geometry"]
            corrected = capt["clear_geometry_v2"]
            cached = {
                "x990": corrected["x990"]
                if native["x990"]["row"] >= LOWER_RANGE_START
                else native["x990"],
                "x1986": native["x1986"],
            }
        gray = None
        row = {"label": p.name, "pts_ns": capt["mean_luma"]["mid"]["pts_ns"]}
        for site, x in LANES.items():
            if fast and site in cached:
                y, contrast = cached[site]["row"], cached[site]["contrast"]
            else:
                if gray is None:
                    gray = replay.unpack_arrays(p, layout)["average"]
                y, contrast = reader(gray, x)
                if site in cached and (
                    y != cached[site]["row"] or contrast != cached[site]["contrast"]
                ):
                    raise ValueError(p.name + " clear-row replay failed")
            pairs = model["anchors"].get(site, [])
            bracketed = map_ml(pairs, y)
            row[site + "_bracketed_ml"] = bracketed if contrast >= 6 else None
            v = bracketed if len(pairs) == 3 else None
            row[site + "_row"] = y
            row[site + "_contrast"] = contrast
            row[site + "_ml"] = v if contrast >= 6 else None
            row[site + "_inside_map"] = v is not None
        out[p.name] = row
    return out


def dry_mark_drift(evidence):
    """Measure the apparent position of the upper front ink at both faces, without correcting the frozen forecasts."""
    dry = {"quarters": ("held_out", 1.5), "thirds": ("primary", 4 / 3)}
    paths = sorted((evidence / "windows").glob("*/reading.json"))
    rows = []
    for p in paths:
        data = json.loads(p.read_text())
        row = {"label": p.parent.name}
        for side, (face, cups) in dry.items():
            row[side + "_row"] = next(
                (v["y"] for v in data[face]["marks"] if v["cups"] == cups), None
            )
        rows.append(row)
    reference = next((r for r in rows if r["label"] == "station-idle"), {})
    for r in rows:
        for side in dry:
            v, initial = r[side + "_row"], reference.get(side + "_row")
            r[side + "_minus_first_px"] = (
                v - initial if v is not None and initial is not None else None
            )
    stats_by_phase = {}
    for phase in (
        "all",
        "learn",
        "validation",
        "ladder",
        "fresh",
        "fill",
        "repeat",
        "home",
    ):
        selected = (
            rows
            if phase == "all"
            else [r for r in rows if r["label"].startswith(phase)]
        )
        if selected:
            stats_by_phase[phase] = {
                side: stats([r[side + "_minus_first_px"] for r in selected])
                for side in dry
            }
    return rows, {
        "first": reference,
        "cups": {k: v[1] for k, v in dry.items()},
        "readable_offsets_px": stats_by_phase,
    }


def subtract(index, a, b, field, sign=1):
    first = index.get(a, {}).get(field)
    last = index.get(b, {}).get(field)
    return sign * (last - first) if first is not None and last is not None else None


def dose_rows(log, index, phase):
    out = []
    attempt = {}
    pending = None
    for ev in log:
        event = ev["event"]
        label = ev.get("label")
        if event == "prediction":
            pending = {**ev}
            attempt[label] = pending
        if event == "board_pour_start" and pending is not None:
            pending["board_start_ns"] = ev["mono_ns"]
        if event != "trial":
            continue
        forecast_record = attempt.pop(label, {})
        pending = None
        r = {
            k: ev.get(k)
            for k in (
                "index",
                "block",
                "head",
                "scenario",
                "level",
                "label",
                "pre",
                "post",
                "forecast_ml",
                "burst_count",
                "expected_bursts",
            )
        }
        r["phase"] = phase
        r["prediction_monotonic_ns"] = forecast_record.get("mono_ns")
        r["board_start_ns"] = forecast_record.get("board_start_ns")
        r["status"] = "complete"
        r["bursts_match"] = r["burst_count"] == r["expected_bursts"]
        sign = 1 if r["head"] == "B" else -1
        for k in LANES:
            d = subtract(index, r["pre"], r["post"], k + "_ml", sign)
            r[k + "_dose_ml"] = d
            r[k + "_delta_px"] = subtract(index, r["pre"], r["post"], k + "_row", -sign)
            r[k + "_start_ml"] = index.get(r["pre"], {}).get(k + "_ml")
            r[k + "_finish_ml"] = index.get(r["post"], {}).get(k + "_ml")
            f = r["forecast_ml"]
            r[k + "_error_ml"] = (
                d - f
                if d is not None
                and f is not None
                and phase in ("fresh", "fill", "repeat")
                else None
            )
            r[k + "_inside_practical"] = (
                bool(
                    d is not None
                    and r["bursts_match"]
                    and abs(d - f) <= max(1, 0.10 * f)
                )
                if f is not None and phase in ("fresh", "fill", "repeat")
                else None
            )
            r[k + "_inside_five_percent"] = (
                bool(d is not None and r["bursts_match"] and abs(d - f) <= 0.05 * f)
                if f is not None and phase in ("fresh", "fill", "repeat")
                else None
            )
            if phase in ("fresh", "fill", "repeat"):
                logged = ev.get("primary_ml" if k == "x990" else "heldout_ml")
                if logged is None:
                    pml = ev.get("pre_cup", {}).get(k, {}).get("ml")
                    qml = ev.get("post_cup", {}).get(k, {}).get("ml")
                    if pml is not None and qml is not None:
                        logged = sign * (qml - pml)
                r[k + "_replay_minus_logged_ml"] = (
                    d - logged if d is not None and logged is not None else None
                )
        if r["x990_dose_ml"] is not None and r["x1986_dose_ml"] is not None:
            r["primary_minus_far_ml"] = r["x990_dose_ml"] - r["x1986_dose_ml"]
        out.append(r)
    for ev in attempt.values():
        out.append(
            {
                k: ev.get(k)
                for k in (
                    "index",
                    "block",
                    "head",
                    "scenario",
                    "level",
                    "label",
                    "pre",
                    "forecast_ml",
                )
            }
            | {"phase": phase, "status": "prediction without complete trial"}
        )
    return out


def fresh_scenarios(rows, phase="fresh", condition="scenario"):
    groups = defaultdict(list)
    for d in rows:
        if d["phase"] == phase:
            groups[(d["head"], d[condition])].append(d)
    out = []
    for (head, name), group in sorted(groups.items()):
        seen = {}
        for d in group:
            if d["status"] == "complete" and d["index"] not in seen:
                seen[d["index"]] = d
        done = list(seen.values())
        f = group[0]["forecast_ml"]
        r = {
            "head": head,
            condition: name,
            "forecast_ml": f,
            "scheduled": 6,
            "complete_indices": len(done),
            "missing_or_extra_attempts": len(group) - len(done),
        }
        for key in LANES:
            inside = sum(bool(d.get(key + "_inside_practical")) for d in done)
            v = [
                d[key + "_error_ml"]
                for d in done
                if d.get(key + "_error_ml") is not None and d["bursts_match"]
            ]
            bias = None if not v else float(np.mean(v))
            r[key + "_scored"] = len(v)
            r[key + "_inside"] = inside
            r[key + "_bias_ml"] = bias
            r[key + "_median_abs_error_ml"] = float(np.median(np.abs(v))) if v else None
            r[key + "_within_five_percent"] = sum(
                bool(d.get(key + "_inside_five_percent")) for d in done
            )
            r[key + "_meets_count_and_bias"] = bool(
                len(done) == 6
                and inside >= 5
                and bias is not None
                and abs(bias) <= max(0.6, 0.05 * f)
            )
        r["both_lanes_meet_count_and_bias"] = (
            r["x990_meets_count_and_bias"] and r["x1986_meets_count_and_bias"]
        )
        out.append(r)
    return out


def native_forecasts(rows, design):
    """Score predicted x990 displacement directly in the original camera coordinates."""
    answers = []
    groups = defaultdict(dict)
    for d in rows:
        if d["phase"] != "fresh" or d["status"] != "complete":
            continue
        f = design["forecasts_px"][d["scenario"]][d["head"]]
        motion = d["x990_delta_px"]
        error = None if motion is None else motion - f
        item = {
            "head": d["head"],
            "scenario": d["scenario"],
            "label": d["label"],
            "index": d["index"],
            "forecast_px": f,
            "motion_px": motion,
            "error_px": error,
            "bursts_match": d["bursts_match"],
            "inside": error is not None
            and d["bursts_match"]
            and abs(error) <= max(2.5, 0.10 * f),
        }
        answers.append(item)
        groups[(d["head"], d["scenario"])].setdefault(d["index"], item)
    scores = []
    for (head, name), trials in sorted(groups.items()):
        group = list(trials.values())
        inside = sum(r["inside"] for r in group)
        errors = [
            r["error_px"]
            for r in group
            if r["bursts_match"] and r["error_px"] is not None
        ]
        bias = float(np.mean(errors)) if errors else None
        f = group[0]["forecast_px"]
        scores.append(
            {
                "head": head,
                "scenario": name,
                "forecast_px": f,
                "scheduled": 6,
                "completed_indices": len(group),
                "readable_and_correct_bursts": len(errors),
                "inside": inside,
                "mean_signed_error_px": bias,
                "meets_count_and_bias": len(group) == 6
                and inside >= 5
                and bias is not None
                and abs(bias) <= max(1.5, 0.05 * f),
            }
        )
    return answers, scores


def paired_fill(rows):
    def aggregate(group, field, statistic):
        values = [v[field] for v in group if v[field] is not None]
        return float(statistic(values)) if values else None

    groups = defaultdict(dict)
    for d in rows:
        if d["phase"] == "fill" and d["status"] == "complete" and d["bursts_match"]:
            groups[(d["head"], d["block"])].setdefault(d["level"], d)
    pairs = []
    decisions = {}
    for (head, block), values in sorted(groups.items()):
        if not {"low", "high"} <= values.keys():
            continue
        low, high = values["low"], values["high"]
        for site in LANES:
            a, b = low.get(site + "_dose_ml"), high.get(site + "_dose_ml")
            if a is None or b is None:
                continue
            mid_high = (high[site + "_start_ml"] + high[site + "_finish_ml"]) / 2
            mid_low = (low[site + "_start_ml"] + low[site + "_finish_ml"]) / 2
            xp_low = low[site + "_delta_px"]
            xp_high = high[site + "_delta_px"]
            slope_low = a / xp_low if xp_low else None
            slope_high = b / xp_high if xp_high else None
            native_part = slope_part = None
            if slope_low is not None and slope_high is not None:
                native_part = (xp_high - xp_low) * (slope_high + slope_low) / 2
                slope_part = (slope_high - slope_low) * (xp_high + xp_low) / 2
            pairs.append(
                {
                    "head": head,
                    "block": block,
                    "site": site,
                    "low": low["label"],
                    "high": high["label"],
                    "high_minus_low_dose_ml": b - a,
                    "low_dose_ml": a,
                    "high_dose_ml": b,
                    "low_motion_px": xp_low,
                    "high_motion_px": xp_high,
                    "high_minus_low_motion_px": xp_high - xp_low,
                    "low_ml_per_px": slope_low,
                    "high_ml_per_px": slope_high,
                    "part_from_native_motion_ml": native_part,
                    "part_from_map_slope_ml": slope_part,
                    "midpoint_separation_ml": mid_high - mid_low,
                }
            )
    for head in ("A", "B"):
        for site in LANES:
            selected = [v for v in pairs if v["head"] == head and v["site"] == site]
            n = len(selected)
            if n < 2:
                continue
            d = np.array([v["high_minus_low_dose_ml"] for v in selected])
            mean = float(d.mean())
            half = float(student.ppf(0.95, n - 1) * d.std(ddof=1) / n**0.5)
            px = np.asarray([v["high_minus_low_motion_px"] for v in selected])
            px_mean = float(px.mean())
            px_half = float(student.ppf(0.95, n - 1) * px.std(ddof=1) / n**0.5)
            sep = float(np.mean([v["midpoint_separation_ml"] for v in selected]))
            decisions[head + "_" + site] = {
                "n": n,
                "mean_high_minus_low_ml": mean,
                "interval_90_ml": [mean - half, mean + half],
                "median_high_minus_low_ml": float(np.median(d)),
                "mean_high_minus_low_px": px_mean,
                "interval_90_px": [px_mean - px_half, px_mean + px_half],
                "median_high_minus_low_px": float(np.median(px)),
                "low_median_motion_px": aggregate(selected, "low_motion_px", np.median),
                "high_median_motion_px": aggregate(
                    selected, "high_motion_px", np.median
                ),
                "low_median_dose_ml": aggregate(selected, "low_dose_ml", np.median),
                "high_median_dose_ml": aggregate(selected, "high_dose_ml", np.median),
                "low_median_ml_per_px": aggregate(selected, "low_ml_per_px", np.median),
                "high_median_ml_per_px": aggregate(
                    selected, "high_ml_per_px", np.median
                ),
                "mean_part_from_native_motion_ml": aggregate(
                    selected, "part_from_native_motion_ml", np.mean
                ),
                "mean_part_from_map_slope_ml": aggregate(
                    selected, "part_from_map_slope_ml", np.mean
                ),
                "mean_midpoint_separation_ml": sep,
                "meets_preregistered_equivalence": n == 6
                and sep >= 30
                and mean - half > -1
                and mean + half < 1,
            }
    return pairs, decisions


def holds(log, index):
    groups = defaultdict(list)
    for ev in log:
        if ev["event"] == "hold":
            groups[ev["label"]].append(ev)
    rows = []
    summary = []
    for label, stops in groups.items():
        stops.sort(key=lambda t: t["elapsed_s"])
        start = stops[0]["window"]
        end = stops[-1]["window"]
        r = {
            "label": label,
            "start": start,
            "end": end,
            "from_s": stops[0]["elapsed_s"],
            "to_s": stops[-1]["elapsed_s"],
            "n": len(stops),
        }
        complete = r["from_s"] < 10 and r["to_s"] > 60
        for ev in stops:
            q = index.get(ev["window"], {})
            rows.append({"hold": label, "elapsed_s": ev["elapsed_s"], **q})
        for site in LANES:
            d = subtract(index, start, end, site + "_ml")
            r[site + "_net_px"] = subtract(index, start, end, site + "_row")
            r[site + "_net_ml"] = d
            values = [index.get(v["window"], {}).get(site + "_ml") for v in stops]
            r[site + "_span_ml"] = (
                max(values) - min(values)
                if all(v is not None for v in values)
                else None
            )
            r[site + "_net_within_observed_bracket_ml"] = subtract(
                index, start, end, site + "_bracketed_ml"
            )
            r[site + "_observed_within_0_75_ml"] = (
                bool(abs(d) <= 0.75) if complete and d is not None else None
            )
        r["both_within_0_75_ml"] = (
            all(r[s + "_observed_within_0_75_ml"] is True for s in LANES)
            if all(r[s + "_observed_within_0_75_ml"] is not None for s in LANES)
            else None
        )
        summary.append(r)
    return rows, summary


def no_command_pairs(log, index, phase):
    """Measure apparent movement between consecutive photographed windows without a commanded transfer."""
    stopped = None
    out = []
    for ev in log:
        event = ev["event"]
        if event in {
            "board_pour_start",
            "position_gate",
            "qualification_gate",
            "condition",
            "home_trim",
            "ladder_gate",
            "halt",
            "session",
            "closed",
        }:
            stopped = None
        if event not in ("image", "before", "after"):
            continue
        label = ev.get("window") or ev["label"]
        if stopped is not None and label in index and stopped in index:
            q = {
                "phase": phase,
                "first": stopped,
                "second": label,
                "interval_s": (index[label]["pts_ns"] - index[stopped]["pts_ns"]) / 1e9,
            }
            for site in LANES:
                q[site + "_change_ml"] = subtract(index, stopped, label, site + "_ml")
                q[site + "_change_px"] = subtract(index, stopped, label, site + "_row")
            out.append(q)
        stopped = label
    return out


def graduation_checks(model, formal):
    """Evaluate the reserved crossings against the exact map used to forecast the experiments."""
    out = {}
    sources = model.get(
        "source_crossings", model.get("sources", model.get("lowering", {}))
    )
    for site in LANES:
        pairs = model["anchors"].get(site, [])
        if len(pairs) != 3:
            continue
        tests = {}
        for name, observed in formal.get("rising", {}).items():
            if not name.startswith("quarter") or name not in sources:
                continue
            y = observed["rows"][site]
            target = observed["nominal_ml"]
            found = at_anchor_check(pairs, y)
            how = sources[name].get(
                "direction", sources[name].get("method", "lowering")
            )
            tests[name] = {
                "row": y,
                "nominal_ml": target,
                "predicted_ml": found,
                "error_ml": found - target,
                "fit_direction": how,
                "within_1_5_ml": abs(found - target) <= 1.5,
                "independent_cross_direction": "rising" not in how,
                "reserved_sources": [b["labels"] for b in observed["brackets"]],
            }
        y_mid, v_mid = pairs[1]
        sensitivities = {}
        for name, anchor in sources.items():
            if name not in tests:
                continue
            spans = [
                b["local_sensitivity_range_px"][site]
                for b in anchor["brackets"]
                if "local_sensitivity_range_px" in b
            ]
            if spans:
                ends = min(x[0] for x in spans), max(x[1] for x in spans)
                sensitivities[name] = {
                    "row_extrema_across_bracket_sensitivities": ends,
                    "nominal_ml_extrema_at_those_rows": sorted(
                        at_anchor_check(pairs, y) for y in ends
                    ),
                }
        out[site] = {
            "row_interval": [pairs[0][0], pairs[-1][0]],
            "nominal_ml_interval": [pairs[-1][1], pairs[0][1]],
            "reserved_rising": tests,
            "local_flank_sensitivity": sensitivities,
            "middle_error_using_outer_only_ml": map_ml([pairs[0], pairs[-1]], y_mid)
            - v_mid,
        }
        opposite = formal.get("lowering", {}).get("thirds_one")
        if opposite is not None:
            opposite_row = opposite["rows"][site]
            opposite_ml = map_ml(pairs, opposite_row)
            out[site]["opposite_printed_one_cup"] = {
                "row": opposite_row,
                "opposite_minus_calibration_mark_px": opposite_row - y_mid,
                "volume_on_selected_scale_ml": opposite_ml,
                "difference_from_printed_nominal_ml": None
                if opposite_ml is None
                else opposite_ml - v_mid,
            }
    return out


def resting_position(log, index):
    """Compare every saved return photograph with the original settled cup on each clear lane."""
    stops = [r for r in log if r["event"] == "station_position"]
    stopped = stops[-1] if stops else {}
    stop_labels = [r["last_window"] for r in stops]
    reference = stopped.get("first_window", "station-idle")
    observed = [
        r
        for r in index.values()
        if r["label"] == reference
        or r["label"].startswith("home-")
        or r["label"].startswith("return-to-reference-")
    ]
    rows = []
    for r in sorted(observed, key=lambda x: x["pts_ns"]):
        q = {
            "label": r["label"],
            "reference": reference,
            "controller_final": r["label"] == stopped.get("last_window"),
            "confirmed_stop": r["label"] in stop_labels,
            "pts_ns": r["pts_ns"],
        }
        for site in LANES:
            for unit in ("row", "ml"):
                q[site + "_" + unit] = r[site + "_" + unit]
                q[site + "_change_" + unit] = subtract(
                    index, reference, r["label"], site + "_" + unit
                )
        rows.append(q)
    return rows


def compare_original(trials, index, face_results):
    """Compare both pairs of sightlines on the same validation pours and the same stopped exposures."""
    if not (face_results / "trials.csv").is_file():
        return [], {}
    measured = {
        r["label"]: r
        for r in trials
        if r["phase"] == "original program" and r["status"] == "complete"
    }
    doses = []
    with (face_results / "trials.csv").open() as f:
        for d in csv.DictReader(f):
            if d["phase"] != "validation" or not d.get("right_minus_independent_ml"):
                continue
            clear = measured.get(d["label"], {})
            if clear.get("primary_minus_far_ml") is None:
                continue
            doses.append(
                {
                    "label": d["label"],
                    "head": d["head"],
                    "scenario": d["scenario"],
                    "printed_right_minus_independent_left_ml": float(
                        d["right_minus_independent_ml"]
                    ),
                    "clear_primary_minus_opposite_ml": clear["primary_minus_far_ml"],
                }
            )
    parked = []
    with (face_results / "stationary-pairs.csv").open() as f:
        for d in csv.DictReader(f):
            if not d["right_ml"] or not d["independent_ml"]:
                continue
            a, b = d["first"], d["second"]
            v = [subtract(index, a, b, s + "_ml") for s in LANES]
            if all(x is not None for x in v):
                parked.append(
                    {
                        "printed_right": float(d["right_ml"]),
                        "printed_left": float(d["independent_ml"]),
                        "clear_x990": v[0],
                        "clear_x1986": v[1],
                    }
                )
    return doses, {
        "same_validation_pour_lane_difference_ml": {
            k: stats([d[k] for d in doses])
            for k in (
                "printed_right_minus_independent_left_ml",
                "clear_primary_minus_opposite_ml",
            )
        },
        "same_no_command_pair_change_ml": {
            k: stats([d[k] for d in parked])
            for k in ("printed_right", "printed_left", "clear_x990", "clear_x1986")
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence")
    p.add_argument("--map", type=Path, default=HERE / "geometry-used.json")
    p.add_argument("--formal", type=Path, default=HERE / "geometry-map-v3.json")
    p.add_argument(
        "--native-forecasts",
        type=Path,
        default=HERE / "reserved-native-and-fallback.json",
    )
    p.add_argument("--recipe-model", type=Path, default=HERE / "repeat-model.json")
    p.add_argument("--width-model", type=Path, default=HERE / "geometry-model.json")
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument("--original-face-results", type=Path, default=HERE / "results")
    p.add_argument("--designs", type=Path, default=HERE / "designs")
    p.add_argument("--out", type=Path, default=HERE / "geometry-results")
    p.add_argument("--fast", action="store_true")
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    m = json.loads(a.map.read_text())
    formal = json.loads(a.formal.read_text())
    e = endpoints(a.evidence, m, a.fast)
    dry_rows, dry_summary = dry_mark_drift(a.evidence)
    tr = []
    quiet = []
    for log, phase in [
        ("train", "training"),
        ("validation", "original program"),
        ("fresh", "fresh"),
        ("fill", "fill"),
        ("repeat", "repeat"),
    ]:
        journal = read_log(a.logs / (log + ".jsonl"))
        tr += dose_rows(journal, e, phase)
        quiet += no_command_pairs(journal, e, phase)
    quiet += no_command_pairs(
        read_log(a.logs / "qualifications.jsonl"), e, "qualification"
    )
    hr, hs = holds(read_log(a.logs / "graduations.jsonl"), e)
    sc = fresh_scenarios(tr)
    matched, comparison = compare_original(tr, e, a.original_face_results)
    fill = fresh_scenarios(tr, "fill", "level")
    fill_pairs, fill_decisions = paired_fill(tr)
    native_rows, native_scores = native_forecasts(
        tr, json.loads(a.native_forecasts.read_text())
    )
    known_rows, known_scores, known_checks = recipe_audit.score(
        tr,
        json.loads(a.recipe_model.read_text()),
        json.loads(a.width_model.read_text()),
    )
    width_checks = recipe_audit.width_checks(
        tr,
        json.loads((a.designs / "preregistration.json").read_text()),
        {
            "fresh": (
                json.loads((a.designs / "fresh-programs.json").read_text()),
                json.loads(a.width_model.read_text()),
            ),
            "fill": (
                json.loads((a.designs / "fill-design.json").read_text()),
                json.loads((a.designs / "fill-model.json").read_text()),
            ),
        },
    )
    level_rows, level_summary = recipe_audit.level_checks(
        tr, json.loads((a.designs / "level-forecast.json").read_text())
    )
    home = resting_position(
        read_log(a.logs / "return.jsonl") + read_log(a.logs / "return-final.jsonl"), e
    )
    for name, rows in [
        ("endpoints", list(e.values())),
        ("dry-mark-drift", dry_rows),
        ("trials", tr),
        ("fresh-scenarios", sc),
        ("same-pour-method-comparison", matched),
        ("fill-levels", fill),
        ("fill-pairs", fill_pairs),
        ("fill-specific-forecast-trials", level_rows),
        ("hold-frames", hr),
        ("hold-results", hs),
        ("no-command-pairs", quiet),
        ("native-trials", native_rows),
        ("native-scenarios", native_scores),
        ("return-to-reference", home),
        ("known-recipe-trials", known_rows),
        ("known-recipe-scenarios", known_scores),
    ]:
        output_csv(a.out / (name + ".csv"), rows)
    z = {
        "map_file": a.map.name,
        "upper_printed_mark_motion": dry_summary,
        "map_sha256": hashlib.sha256(a.map.read_bytes()).hexdigest(),
        "map_status": m.get("calibration_status", m.get("status")),
        "lowering_only_status": formal["status"],
        "unresolved_lowering_marks": [
            k
            for k in (
                "quarter_three_quarters",
                "quarter_one",
                "quarter_one_and_quarter",
            )
            if k not in formal["lowering"]
        ],
        "graduation_checks": graduation_checks(m, formal),
        "lowering_parallax_right_one_cup_minus_left_one_cup_px": formal.get(
            "left_right_one_cup", {}
        ).get("lowering"),
        "source": "source-proved per-window readings"
        if a.fast
        else "lossless PNGs read on each clear sightline",
        "n_archived_windows": len(e),
        "phase": {},
        "holds": hs,
        "no_command_change_ml": {
            s: stats([q[s + "_change_ml"] for q in quiet]) for s in LANES
        },
        "fresh_tests": sc,
        "original_training_forecast_replay": width_checks,
        "matched_method_comparison": comparison,
        "native_scenarios": native_scores,
        "known_recipe_training_and_timing": known_checks,
        "known_recipe_scenarios": known_scores,
        "return_to_reference": next((r for r in home if r["controller_final"]), None),
        "intermediate_and_final_returns": [r for r in home if r["confirmed_stop"]],
        "fill_levels": fill,
        "fill_equivalence": fill_decisions,
        "fill_specific_forecast": level_summary,
    }
    for phase in ("training", "original program", "fresh", "fill", "repeat"):
        done = [r for r in tr if r["phase"] == phase and r["status"] == "complete"]
        z["phase"][phase] = {
            "completed": len(done),
            "observed_endpoint_ml": {
                site: stats(
                    [
                        r.get(site + "_" + stage + "_ml")
                        for r in done
                        for stage in ("start", "finish")
                    ]
                )
                for site in LANES
            },
            "primary_minus_independent_dose_ml": stats(
                [v.get("primary_minus_far_ml") for v in done]
            ),
            "x990_log_replay_error_ml": stats(
                [v.get("x990_replay_minus_logged_ml") for v in done]
            ),
            "x1986_log_replay_error_ml": stats(
                [v.get("x1986_replay_minus_logged_ml") for v in done]
            ),
        }
    (a.out / "summary.json").write_text(json.dumps(z, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "windows": len(e),
                "holds": len(hs),
                "fresh": z["phase"]["fresh"]["completed"],
            }
        )
    )


if __name__ == "__main__":
    main()
