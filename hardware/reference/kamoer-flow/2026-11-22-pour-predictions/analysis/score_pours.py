"""Score prospective syrup-dose forecasts against complete, separately photographed pours."""
import argparse
from collections import defaultdict
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
from statistics import correlation, mean, median


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def json_lines(path):
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        records.append(dict(row, source_file=path.name, source_line=line_number))
    return records


def cell(row):
    return int(row["block"]), row["scenario"], row["head"]


def describe(values):
    values = [x for x in values if x is not None]
    if not values:
        return {"n": 0}
    return {
        "n": len(values), "mean": mean(values), "median": median(values),
        "minimum": min(values), "maximum": max(values),
    }


def errors(observed_forecast):
    pairs = [(y, p) for y, p in observed_forecast if y is not None and p is not None]
    if not pairs:
        return {"n": 0}
    signed = [y - p for y, p in pairs]
    return {
        "n": len(pairs), "bias_ml": mean(signed), "median_signed_error_ml": median(signed),
        "median_abs_error_ml": median(abs(v) for v in signed),
        "mean_abs_error_ml": mean(abs(v) for v in signed), "max_abs_error_ml": max(abs(v) for v in signed),
        "within_practical_band": sum(abs(y - p) <= max(1, 0.10 * p) for y, p in pairs),
        "within_five_percent": sum(abs(y - p) <= 0.05 * p for y, p in pairs),
    }


def fault_reason(row):
    for key in ("fault", "error", "reason"):
        if row.get(key):
            return str(row[key])
    if str(row.get("status", "")).lower() in {"error", "failed", "stopped", "interrupted", "fault", "halted"}:
        return str(row["status"])
    return ""


def assemble_attempts(records, plan):
    observations = []
    active = None

    def finish(row=None, failure=""):
        nonlocal active
        if active is None:
            if row is not None:
                raise ValueError(f'Trial without an earlier prediction at {row["source_file"]}:{row["source_line"]}')
            return
        prep = active["prediction"]
        start, stop = active.get("board_pour_start", {}), active.get("board_pour_end", {})
        flow = active["flow_writes"]
        if row is None and not (start or flow):
            active = None
            return
        if row is None:
            row = dict(prep, burst_count=stop.get("bursts"), elapsed_ms=stop.get("elapsed_ms"), fault=failure)
        elif row["label"] != prep["label"] or cell(row) != cell(prep):
            raise ValueError(f'Trial did not match its preregistered forecast at {row["source_file"]}:{row["source_line"]}')
        scenario = plan["scenarios"][row["scenario"]]
        gates = scenario["ideal_gates_start_ms_width_ms"]
        ideal_on = gates[0][1]
        ideal_off = gates[1][0] - gates[0][0] - ideal_on if len(gates) > 1 else None
        first_receipt = start.get("first_receipt_clock")
        last_receipt = stop.get("receipt_clock")
        flow_sequence = [int(cmd["command"].split()[1]) for cmd in flow]
        expected_sequence = [s[0] for s in scenario["meter"]] + [0]
        sequence_match = flow_sequence == expected_sequence
        expected_valves = {"A": {"E", "G"}, "B": {"H", "J"}}[row["head"]]
        stage_clock_errors = []
        if first_receipt is not None and sequence_match:
            target_ms = 0
            for cmd, (_, duration) in zip(flow[1:], scenario["meter"]):
                target_ms += duration
                stage_clock_errors.append((cmd["mono_ns"] / 1e9 - first_receipt) * 1000 - target_ms)
        point = row.get("forecast_ml")
        posted = bool(flow and prep["mono_ns"] < flow[0]["mono_ns"]
                      and (row["phase"] == "training" or (point is not None and point == prep.get("forecast_ml"))))
        observations.append(dict(row,
            source_forecast_line=prep["source_line"], forecast_posted_before_command=posted,
            forecast_utc=prep.get("utc"), first_wet_command_utc=flow[0].get("utc") if flow else None,
            first_waveform_match=(bool(start) and start["head"] == row["head"] and start["ratio"] == scenario["ratio"]
                                  and start["first_on"] == ideal_on and (ideal_off is None or start["first_off"] == ideal_off)),
            dispense_path_matches=(set(start.get("valves", "").split()) == expected_valves),
            first_on_ms=start.get("first_on"), first_off_ms=start.get("first_off"),
            board_close_receipt_matches=(bool(stop) and stop["head"] == row["head"]
                                         and stop["bursts"] == row.get("burst_count") and stop["elapsed_ms"] == row.get("elapsed_ms")),
            flow_sequence_match=sequence_match, stage_clock_errors_ms=stage_clock_errors,
            host_pour_elapsed_ms=((last_receipt - first_receipt) * 1000 if first_receipt is not None and last_receipt is not None else None),
            pre_signal_to_first_host_command_ms=((flow[0]["mono_ns"] - prep["mono_ns"]) / 1e6 if flow else None),
            actual_first_receipt_after_command_ms=((first_receipt - flow[0]["mono_ns"] / 1e9) * 1000 if flow and first_receipt is not None else None),
        ))
        active = None

    for record in records:
        kind = record.get("event")
        if kind == "prediction":
            finish(failure="A later prediction appeared without a completed optical endpoint")
            active = {"prediction": record, "flow_writes": []}
        elif active is not None:
            if kind in ("board_pour_start", "board_pour_end"):
                active[kind] = record
            elif kind == "tx" and record.get("command", "").startswith("flow "):
                active["flow_writes"].append(record)
            elif kind == "trial":
                finish(row=record)
            elif kind == "halt":
                finish(failure=str(record.get("error", "interrupted")))
            elif kind in ("closed", "session"):
                finish(failure="The session closed without a completed optical endpoint")
    finish(failure="Journal ends before a completed optical endpoint")
    return observations


def attempt(row, plan, priors):
    scenario = plan["scenarios"][row["scenario"]]
    head = row["head"]
    profile = priors["schedules"][row["scenario"]]["heads"][head]
    nominal_count = scenario["ideal_bursts"]
    count = number(row.get("burst_count"))
    reported_expected = number(row.get("expected_bursts"))
    primary = number(row.get("primary_ml"))
    heldout = number(row.get("heldout_ml"))
    forecast = number(row.get("forecast_ml"))
    has_images = bool(row.get("pre")) and bool(row.get("post"))
    fault = fault_reason(row)
    count_match = count == nominal_count and reported_expected in (None, nominal_count)
    shape = (count_match and row["first_waveform_match"] and row["dispense_path_matches"]
             and row["board_close_receipt_matches"] and row["flow_sequence_match"])
    recorded = not fault and has_images and primary is not None
    board_stop = number(row.get("elapsed_ms"))
    ideal_stop = scenario["ideal_stop_ms"][-1]
    out = {
        "phase": row["phase"], "index": row.get("index"), "block": row["block"], "scenario": row["scenario"],
        "head": head, "record": f'{row["source_file"]}:{row["source_line"]}', "pre": row.get("pre"), "post": row.get("post"),
        "start_ml": number(row.get("start_ml")), "finish_ml": number(row.get("finish_ml")),
        "planned_bursts": nominal_count, "acknowledged_bursts": count, "burst_match": count_match,
        "label": row["label"], "prospective_forecast_verified": row["forecast_posted_before_command"],
        "forecast_utc": row["forecast_utc"], "first_wet_command_utc": row["first_wet_command_utc"],
        "forecast_record": f'{row["source_file"]}:{row["source_forecast_line"]}',
        "first_on_ms": row["first_on_ms"], "first_off_ms": row["first_off_ms"],
        "first_waveform_match": row["first_waveform_match"], "board_close_receipt_matches": row["board_close_receipt_matches"],
        "dispense_path_matches": row["dispense_path_matches"],
        "flow_sequence_match": row["flow_sequence_match"],
        "stage_clock_errors_ms": row["stage_clock_errors_ms"],
        "first_receipt_after_command_ms": row["actual_first_receipt_after_command_ms"],
        "planned_pour_close_ms": ideal_stop, "board_pour_close_ms": board_stop,
        "host_pour_elapsed_ms": row["host_pour_elapsed_ms"],
        "host_elapsed_minus_board_ms": row["host_pour_elapsed_ms"] - board_stop if board_stop is not None and row["host_pour_elapsed_ms"] is not None else None,
        "close_clock_error_ms": board_stop - ideal_stop if board_stop is not None else None,
        "fault": fault, "journal_still_open": fault == "Journal ends before a completed optical endpoint",
        "optically_complete": recorded, "matches_waveform": shape, "matches_plan": shape and recorded,
        "photographed_expected_waveform": shape and has_images and not fault,
        "optical_flags": row.get("optical_flags"), "operating_change_ml": number(row.get("operating_change_ml")),
        "primary_ml": primary, "heldout_ml": heldout, "forecast_ml": forecast,
        "restored_mean_ml": profile["restored_ruler_mean_ml"],
        "restored_right_ml": profile["restored_constant_rate"]["right"]["dose_ml"],
        "restored_left_ml": profile["restored_constant_rate"]["projected_left"]["dose_ml"],
        "engineering_p50_ml": profile["engineering_dead_time"]["p50_ml"],
        "engineering_p10_ml": profile["engineering_dead_time"]["p10_ml"],
        "engineering_p90_ml": profile["engineering_dead_time"]["p90_ml"],
    }
    for name, observed in (("primary", primary), ("heldout", heldout)):
        residual = observed - forecast if forecast is not None and observed is not None else None
        out[f"{name}_error_ml"] = residual
        eligible = out["photographed_expected_waveform"] and out["prospective_forecast_verified"] and residual is not None
        out[f"{name}_pass"] = bool(eligible and abs(residual) <= max(1, 0.10 * forecast))
        out[f"{name}_pass_five_percent"] = bool(eligible and abs(residual) <= 0.05 * forecast)
    gap = abs(primary - heldout) if primary is not None and heldout is not None else None
    out["half_sightline_disagreement_ml"] = gap / 2 if gap is not None else None
    out["sightline_gap_exceeds_both_tolerances"] = (
        gap > 2 * max(1, 0.10 * forecast) if gap is not None and forecast is not None else None
    )
    return out


def chosen_trial(rows):
    # Preserve the first readable completed trial, including any unexpected burst count or dose.
    return next((r for r in rows if r["optically_complete"]), rows[0] if rows else None)


def reconstruct_training(cells, plan):
    rates = defaultdict(lambda: defaultdict(list))
    for (_, name, head), trials in cells.items():
        scenario = plan["scenarios"][name]
        if scenario["phase"] != "training":
            continue
        widths = {w for _, w in scenario["ideal_gates_start_ms_width_ms"]}
        if len(widths) != 1:
            raise ValueError(f"The training schedule {name} contains multiple gate widths")
        trial = chosen_trial(trials)
        if trial is not None and trial["matches_plan"] and trial["acknowledged_bursts"] > 0:
            rates[head][next(iter(widths))].append(trial["primary_ml"] / trial["acknowledged_bursts"])
    return {
        head: [{"width_ms": width, "n": len(runs), "median_dose_per_gate_ml": median(runs)}
               for width, runs in sorted(anchors.items())]
        for head, anchors in rates.items()
    }


def predicted_dose(anchors, schedule):
    if not anchors:
        return None
    def interpolate(width):
        for anchor in anchors:
            if width == anchor["width_ms"]:
                return anchor["median_dose_per_gate_ml"]
        for left, right in zip(anchors, anchors[1:]):
            if left["width_ms"] < width < right["width_ms"]:
                share = (width - left["width_ms"]) / (right["width_ms"] - left["width_ms"])
                return left["median_dose_per_gate_ml"] + share * (right["median_dose_per_gate_ml"] - left["median_dose_per_gate_ml"])
        return None
    doses = [interpolate(width) for _, width in schedule]
    return sum(doses) if all(d is not None for d in doses) else None


def condition(name, head, trial_groups, expected_cells, reconstructed, plan):
    observed = [chosen_trial(group) for group in trial_groups if group]
    matched = [r for r in observed if r["matches_plan"]]
    photographed = [r for r in observed if r["photographed_expected_waveform"]]
    targets = [r["forecast_ml"] for r in observed if r["forecast_ml"] is not None]
    reconstructed_ml = predicted_dose(reconstructed.get(head), plan["scenarios"][name]["ideal_gates_start_ms_width_ms"])
    # The prespecified confidence rule treats missing or incorrect waveforms as failures for coverage.
    out = {
        "scenario": name, "head": head, "planned": expected_cells,
        "attempted_cells": len(observed), "attempts": sum(map(len, trial_groups)),
        "first_attempt_valid": sum(bool(group) and group[0]["matches_plan"] for group in trial_groups),
        "matching_bursts_and_primary": len(matched),
        "matching_waveform_with_heldout": sum(r["heldout_ml"] is not None for r in photographed),
        "matching_waveform_with_both_rulers": sum(r["primary_ml"] is not None and r["heldout_ml"] is not None for r in photographed),
        "acknowledged_count_mismatches": sum(r["acknowledged_bursts"] is not None and not r["burst_match"] for r in observed),
        "primary_within_band": sum(r["primary_pass"] for r in observed),
        "heldout_within_band": sum(r["heldout_pass"] for r in observed),
        "primary_within_five_percent": sum(r["primary_pass_five_percent"] for r in observed),
        "heldout_within_five_percent": sum(r["heldout_pass_five_percent"] for r in observed),
        "forecast_ml": mean(targets) if targets else reconstructed_ml,
        "reconstructed_training_forecast_ml": reconstructed_ml,
        "max_forecast_reconstruction_difference_ml": max((abs(v - reconstructed_ml) for v in targets), default=None) if reconstructed_ml is not None else None,
        "primary_observations_ml": describe(r["primary_ml"] for r in matched),
        "heldout_observations_ml": describe(r["heldout_ml"] for r in photographed),
        "individual_signed_heldout_minus_primary_ml": describe(r["heldout_ml"] - r["primary_ml"] for r in matched if r["heldout_ml"] is not None),
        "volume_span_nominal_ml": describe(v for r in matched for v in (r["start_ml"], r["finish_ml"])),
        "clock_error_ms": describe(r["close_clock_error_ms"] for r in observed),
        "comparisons": compare(photographed),
        "comparisons_including_unexpected_waveforms": compare([r for r in observed if r["optically_complete"]]),
    }
    primary = out["comparisons"]["candidate_primary"]
    forecast = out["forecast_ml"]
    out["bias_limit_ml"] = max(0.6, 0.05 * forecast) if forecast is not None else None
    out["planned_cells_complete"] = len(observed) == expected_cells and not any(r["journal_still_open"] for r in observed)
    pass_primary = (out["planned_cells_complete"] and out["primary_within_band"] >= 5
                    and primary["n"] >= 5 and abs(primary["bias_ml"]) <= out["bias_limit_ml"])
    out["primary_result"] = ("pass" if pass_primary else "fail") if out["planned_cells_complete"] else "incomplete"
    out["corroborated_result"] = ("pass" if pass_primary and out["heldout_within_band"] >= 5 else "fail") if out["planned_cells_complete"] else "incomplete"
    out["failed_requirements"] = []
    if out["planned_cells_complete"]:
        if out["primary_within_band"] < 5:
            out["failed_requirements"].append("primary coverage")
        if not primary["n"] or abs(primary["bias_ml"]) > out["bias_limit_ml"]:
            out["failed_requirements"].append("primary mean bias")
        if out["heldout_within_band"] < 5:
            out["failed_requirements"].append("secondary optical coverage")
    return out


def compare(rows):
    outcome = {}
    for label, observed, predicted in (
        ("candidate_primary", "primary_ml", "forecast_ml"),
        ("candidate_heldout", "heldout_ml", "forecast_ml"),
        ("restored_ruler_mean_primary", "primary_ml", "restored_mean_ml"),
        ("restored_right_primary", "primary_ml", "restored_right_ml"),
        ("restored_left_heldout", "heldout_ml", "restored_left_ml"),
        ("engineering_primary", "primary_ml", "engineering_p50_ml"),
    ):
        outcome[label] = errors((row[observed], row[predicted]) for row in rows)
    outcome["engineering_prior_middle_80_coverage_n"] = sum(
        row["primary_ml"] is not None and row["engineering_p10_ml"] <= row["primary_ml"] <= row["engineering_p90_ml"] for row in rows
    )
    return outcome


def pixel_score(rows, attempted, expected):
    trials = [r for r in rows if r["photographed_expected_waveform"]
              and r["observed_clear_px"] is not None and r["forecast_clear_px"] is not None]
    residuals = [r["observed_clear_px"] - r["forecast_clear_px"] for r in trials]
    success = sum(abs(diff) <= max(2.5, 0.10 * r["forecast_clear_px"]) for diff, r in zip(residuals, trials))
    forecast = mean(r["forecast_clear_px"] for r in trials) if trials else None
    bias = mean(residuals) if residuals else None
    limit = max(1.5, 0.05 * forecast) if forecast is not None else None
    result = "incomplete" if attempted < expected else (
        "pass" if success >= 5 and bias is not None and abs(bias) <= limit else "fail"
    )
    return {
        "n": len(trials), "forecast_px": forecast, "mean_signed_error_px": bias,
        "median_abs_error_px": median(map(abs, residuals)) if residuals else None,
        "within_band": success, "bias_limit_px": limit,
        "observations_px": describe(r["observed_clear_px"] for r in trials), "result": result,
    }


def repeat_diagnostics(rows):
    good = [r for r in rows if r["matches_plan"]]
    independent = [r for r in rows if r["photographed_expected_waveform"] and r["heldout_ml"] is not None]
    clear = [r for r in rows if r["photographed_expected_waveform"] and r["observed_clear_px"] is not None]
    pairs = [r for r in good if r["heldout_ml"] is not None]
    return {
        "observed_pours": len(rows),
        "primary_error_ml": describe(r["primary_error_ml"] for r in good),
        "heldout_error_ml": describe(r["heldout_error_ml"] for r in independent),
        "clear_error_px": describe(r["observed_clear_px"] - r["forecast_clear_px"] for r in clear if r["forecast_clear_px"] is not None),
        "heldout_minus_primary_ml": describe(r["heldout_ml"] - r["primary_ml"] for r in pairs),
        "absolute_ruler_disagreement_ml": describe(abs(r["heldout_ml"] - r["primary_ml"]) for r in pairs),
        "half_sightline_disagreement_ml": describe(r["half_sightline_disagreement_ml"] for r in pairs),
        "sightline_gap_exceeds_both_tolerances": sum(r["sightline_gap_exceeds_both_tolerances"] is True for r in pairs),
        "primary_relative_error_pct": describe(r["primary_error_pct"] for r in good),
        "heldout_relative_error_pct": describe(r["heldout_error_pct"] for r in independent),
        "clear_relative_error_pct": describe(r["clear_error_pct"] for r in clear),
        "primary_within_band": sum(r["primary_pass"] for r in rows),
        "heldout_within_band": sum(r["heldout_pass"] for r in rows),
        "clear_within_band": sum(r["clear_pass"] for r in rows),
    }


def diagnostic_splits(rows):
    return {
        "first_three_blocks": repeat_diagnostics([r for r in rows if r["block"] <= 3]),
        "last_three_blocks": repeat_diagnostics([r for r in rows if r["block"] > 3]),
        "all_blocks": repeat_diagnostics(rows),
    }


def centered_correlation(rows, x, y):
    groups = defaultdict(list)
    for row in rows:
        if row[x] is not None and row[y] is not None:
            groups[row["scenario"]].append((row[x], row[y]))
    pairs = []
    for numbers in groups.values():
        base_x, base_y = mean(v[0] for v in numbers), mean(v[1] for v in numbers)
        pairs.extend((a - base_x, b - base_y) for a, b in numbers)
    if len(pairs) < 3 or len({p[0] for p in pairs}) < 2 or len({p[1] for p in pairs}) < 2:
        return {"n": len(pairs), "pearson_r": None}
    return {"n": len(pairs), "pearson_r": correlation(*zip(*pairs))}


def equal_water(cells, plan):
    scores = {}
    needed = plan["epochs"]["validation_blocks"]
    for head in ("A", "B"):
        for measure in ("primary_ml", "heldout_ml", "observed_clear_px"):
            pairs = []
            attempted = 0
            forecast_difference = None
            for block in range(1, needed + 1):
                fast = chosen_trial(cells[block, "full_glass", head])
                slow = chosen_trial(cells[block, "partial_glass", head])
                if not (fast and slow):
                    continue
                attempted += not (fast["journal_still_open"] or slow["journal_still_open"])
                field = "forecast_clear_px" if measure == "observed_clear_px" else "forecast_ml"
                if fast[field] is not None and slow[field] is not None:
                    forecast_difference = fast[field] - slow[field]
                valid = "matches_plan" if measure == "primary_ml" else "photographed_expected_waveform"
                if not (fast[valid] and slow[valid]) or fast[measure] is None or slow[measure] is None:
                    continue
                pairs.append({"block": block, "full": fast[measure], "half": slow[measure], "full_minus_half": fast[measure] - slow[measure]})
            signs = sum(p["full_minus_half"] > 0 for p in pairs)
            scores[f"{head}_{measure}"] = {
                "paired_blocks_attempted": attempted, "eligible_pair_n": len(pairs), "full_greater": signs,
                "frozen_full_minus_half": forecast_difference,
                "paired_differences": describe(p["full_minus_half"] for p in pairs),
                "result": "incomplete" if attempted < needed else ("pass" if signs >= 5 else "fail"),
                "pairs": pairs,
            }
    return scores


def face_volume(face):
    if not face.get("ok") or number(face.get("y")) is None:
        return None
    y = face["y"]
    marks = sorted(face["marks"], key=lambda mark: mark["y"])
    for high, low in zip(marks, marks[1:]):
        if high["y"] <= y <= low["y"]:
            fraction = (y - high["y"]) / (low["y"] - high["y"])
            return 236.5882365 * (high["cups"] + fraction * (low["cups"] - high["cups"]))
    return None


def same_reading(one, two):
    if one is None or two is None:
        return one is None and two is None
    return abs(one - two) <= 1e-8


def verify_image_endpoints(trial, images):
    before, after = images.get(trial["pre"]), images.get(trial["post"])
    sign = 1 if trial["head"] == "B" else -1
    measured = {}
    if before and after:
        measured["clear"] = -sign * (after["clear"][1] - before["clear"][1])
    for name, side in (("primary", "primary"), ("heldout", "held_out")):
        displacement = None
        mark_motion = []
        if before and after:
            pre, post = before["optics"][side], after["optics"][side]
            lo, hi = face_volume(pre), face_volume(post)
            if lo is not None and hi is not None:
                measured[name] = sign * (hi - lo)
                displacement = -sign * (post["y"] - pre["y"])
            a = {m["cups"]: m["y"] for m in pre["marks"]}
            b = {m["cups"]: m["y"] for m in post["marks"]}
            mark_motion = [b[k] - a[k] for k in a.keys() & b.keys()]
        trial[f"{name}_surface_displacement_px"] = displacement
        trial[f"{name}_max_abs_mark_motion_px"] = max(map(abs, mark_motion)) if mark_motion else None
    trial["paired_images_found"] = bool(before and after)
    for name, field in (("primary", "primary_ml"), ("heldout", "heldout_ml"), ("clear", "observed_clear_px")):
        trial[f"{name}_readback_matches_reduction"] = bool(before and after and same_reading(measured.get(name), trial[field]))


def cooldown(cells, plan):
    scores = {}
    for head in ("A", "B"):
        for measure in ("primary_ml", "heldout_ml"):
            pairs = []
            predicted_reduction = None
            for block in range(1, plan["epochs"]["validation_blocks"] + 1):
                steady = chosen_trial(cells[block, "same_open_time", head])
                reopen = chosen_trial(cells[block, "release_reopen", head])
                valid = "matches_plan" if measure == "primary_ml" else "photographed_expected_waveform"
                if not (steady and steady[valid] and reopen and reopen[valid]):
                    continue
                if steady["forecast_ml"] and reopen["forecast_ml"] is not None:
                    predicted_reduction = 1 - reopen["forecast_ml"] / steady["forecast_ml"]
                if steady[measure] is None or steady[measure] <= 0 or reopen[measure] is None:
                    continue
                pairs.append({"block": block, "steady_ml": steady[measure], "reopen_ml": reopen[measure],
                              "paired_reduction_fraction": 1 - reopen[measure] / steady[measure]})
            attempted = sum(
                all(chosen_trial(cells[b, name, head]) is not None and not chosen_trial(cells[b, name, head])["journal_still_open"]
                    for name in ("same_open_time", "release_reopen"))
                for b in range(1, plan["epochs"]["validation_blocks"] + 1)
            )
            reduction = 1 - median(p["reopen_ml"] for p in pairs) / median(p["steady_ml"] for p in pairs) if pairs else None
            lower = sum(p["reopen_ml"] < p["steady_ml"] for p in pairs)
            result = "incomplete" if attempted < plan["epochs"]["validation_blocks"] else (
                "pass" if lower >= 5 and reduction is not None and reduction >= 0.20 else "fail")
            scores[f"{head}_{measure}"] = {
                "paired_blocks_attempted": attempted, "eligible_pair_n": len(pairs), "reopen_lower": lower,
                "frozen_reduction_fraction": predicted_reduction,
                "reduction_of_medians_fraction": reduction, "result": result, "pairs": pairs,
            }
    return scores


def write_csv(path, rows):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def score(preregistration, archive, training, validation, output):
    design_raw = preregistration.read_bytes()
    plan = json.loads(design_raw)
    priors = json.loads(archive.read_text())
    design_hash = hashlib.sha256(design_raw).hexdigest()
    if priors["preregistration_sha256"] != design_hash:
        raise ValueError("The priors were frozen against different registration bytes")
    model_path = preregistration.with_name("frozen-model.json")
    pixel_path = preregistration.with_name("frozen-pixels.json")
    model = json.loads(model_path.read_text()) if model_path.exists() else {}
    pixels = json.loads(pixel_path.read_text()) if pixel_path.exists() else {}
    cells = defaultdict(list)
    attempts = []
    all_records = json_lines(training) + json_lines(validation)
    images = {r["label"]: r for r in all_records if r.get("event") == "image"}
    for record in assemble_attempts(all_records, plan):
        trial = attempt(record, plan, priors)
        scenario, head = trial["scenario"], trial["head"]
        ref_volume = model.get("forecasts", {}).get(scenario, {}).get(head)
        ref_pixels = pixels.get("forecasts", {}).get(scenario, {}).get(head)
        clear = trial["operating_change_ml"] / 0.42 if trial["operating_change_ml"] is not None else None
        trial["forecast_clear_px"] = ref_pixels
        trial["observed_clear_px"] = clear
        trial["registered_volume_forecast_matches"] = (
            abs(ref_volume - trial["forecast_ml"]) < 1e-9 if ref_volume is not None and trial["forecast_ml"] is not None else None)
        trial["heldout_minus_primary_ml"] = (
            trial["heldout_ml"] - trial["primary_ml"] if trial["primary_ml"] is not None and trial["heldout_ml"] is not None else None)
        for name in ("primary", "heldout"):
            err = trial[f"{name}_error_ml"]
            trial[f"{name}_error_pct"] = 100 * err / ref_volume if ref_volume and err is not None else None
            if trial["registered_volume_forecast_matches"] is False:
                trial[f"{name}_pass"] = False
                trial[f"{name}_pass_five_percent"] = False
        trial["clear_error_pct"] = 100 * (clear - ref_pixels) / ref_pixels if clear is not None and ref_pixels else None
        trial["clear_pass"] = (trial["photographed_expected_waveform"] and clear is not None and ref_pixels is not None
                               and abs(clear - ref_pixels) <= max(2.5, 0.10 * ref_pixels))
        verify_image_endpoints(trial, images)
        key = cell(record)
        trial["attempt_in_cell"] = len(cells[key]) + 1
        cells[key].append(trial)
        attempts.append(trial)
    order = plan["orders"]["validation"]
    for rows in cells.values():
        selected = chosen_trial(rows)
        for trial in rows:
            trial["selected_for_cell"] = trial is selected
    planned_keys = {cell(row) for row in order}
    extra = [t for t in attempts if t["phase"] == "validation" and cell(t) not in planned_keys]
    if extra:
        raise ValueError(f"Unexpected validation trial appeared: {extra[0]['record']}")
    trained = reconstruct_training(cells, plan)
    grouped = defaultdict(list)
    for row in order:
        grouped[row["scenario"], row["head"]].append(cells[cell(row)])
    conditions = [condition(name, head, trials, len(trials), trained, plan) for (name, head), trials in grouped.items()]
    validation_selected = [chosen_trial(cells[cell(r)]) for r in order]
    validation_selected = [r for r in validation_selected if r is not None]
    matched = [r for r in validation_selected if r["matches_plan"]]
    photographed = [r for r in validation_selected if r["photographed_expected_waveform"]]
    last_train = max((r["utc"] for r in all_records if r.get("event") == "trial" and r.get("phase") == "training"), default=None)
    first_validation = min((r["first_wet_command_utc"] for r in validation_selected if r["first_wet_command_utc"]), default=None)
    freeze_time = model.get("utc")
    for result in conditions:
        rows = [r for r in validation_selected if r["scenario"] == result["scenario"] and r["head"] == result["head"]]
        result["clear_pixel_model"] = pixel_score(rows, sum(not r["journal_still_open"] for r in rows), result["planned"])
        result["repeat_diagnostics"] = diagnostic_splits(rows)
    summary = {
        "preregistration_sha256": design_hash,
        "frozen_volume_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest() if model else None,
        "frozen_pixels_sha256": hashlib.sha256(pixel_path.read_bytes()).hexdigest() if pixels else None,
        "frozen_training_log_matches": hashlib.sha256(training.read_bytes()).hexdigest() == model.get("training_sha256") if training.is_file() and model else None,
        "training_and_forecast_times": {
            "last_calibration_trial_utc": last_train, "volume_model_frozen_utc": freeze_time,
            "first_validation_meter_command_utc": first_validation,
            "ordered_training_then_freeze_then_validation": (
                datetime.fromisoformat(last_train) < datetime.fromisoformat(freeze_time) < datetime.fromisoformat(first_validation)
                if last_train and freeze_time and first_validation else None
            ),
        },
        "definitions": {
            "errors": "Signed error is measured volume minus the prospective forecast, in nominal mL. Each planned head, scenario and block contributes at most one pour. Scores use the first optically complete attempt, including a wrong burst count. Wrong waveforms cannot pass and their numeric errors appear separately.",
            "ruler": "Both readings come from the same experimental pour. The independently read optical measure tests sensitivity to how the camera observes the graduated cup. It does not supply a second experimental replicate.",
            "coverage": "Counts use all planned blocks as the denominator. A posted primary forecast is required. Primary pass also requires the preregistered mean signed-error bound. Corroborated pass additionally requires the preregistered independent optical coverage.",
            "clock": "The stock controller reports the first cycle timing and the number of bursts at pour closure. The optional final elapsed time is compared with ideal policy closure, which includes the cooldown. Individual gate edges are not instrumented.",
            "clear_pixels": "A separate pre-validation model predicts the settled motion of a clear foreground patch in native pixels. The journal's working-coordinate change is divided by its acquisition scale to recover the sensor displacement. Relative errors use this model's own frozen pixel prediction. The two printed scales use the frozen primary volume prediction.",
            "repeat_diagnostics": "First and last groups use consecutive registered blocks. Within-scenario correlations center each measure on its own head/scenario mean before pooling the replicates. All measures come from the same camera and couple optical readout, cup registration, liquid shape, and pump delivery.",
            "sightline_gap": "Half the separation between the two volume readings is a lower bound on the absolute measurement error of at least one reading of this pour. A full gap larger than twice the registered tolerance makes the two acceptance intervals disjoint.",
        },
        "training_anchors_reconstructed": trained,
        "planned_validation": len(order), "selected_validation_attempts": len(validation_selected),
        "all_validation_attempts": sum(r["phase"] == "validation" for r in attempts),
        "validation_numeric_expected_waveform": len(matched), "classification": conditions,
        "measurement_availability_expected_waveform": {
            "photographed": len(photographed),
            "primary_ruler": sum(r["primary_ml"] is not None for r in photographed),
            "heldout_ruler": sum(r["heldout_ml"] is not None for r in photographed),
            "both_rulers": sum(r["primary_ml"] is not None and r["heldout_ml"] is not None for r in photographed),
            "clear_pixels": sum(r["observed_clear_px"] is not None for r in photographed),
        },
        "paired_image_reductions": {
            "archived_windows_found": sum(r["paired_images_found"] for r in photographed),
            "primary_values_reproduced": sum(r["primary_readback_matches_reduction"] for r in photographed),
            "heldout_values_reproduced": sum(r["heldout_readback_matches_reduction"] for r in photographed),
            "clear_displacements_reproduced": sum(r["clear_readback_matches_reduction"] for r in photographed),
            "right_mark_max_absolute_motion_per_pour_px": describe(r["primary_max_abs_mark_motion_px"] for r in photographed),
            "left_mark_max_absolute_motion_per_pour_px": describe(r["heldout_max_abs_mark_motion_px"] for r in photographed),
        },
        "clocks": {
            "first_receipt_after_input_ms": describe(r["first_receipt_after_command_ms"] for r in validation_selected),
            "stage_write_minus_planned_ms": describe(v for r in validation_selected for v in r["stage_clock_errors_ms"]),
            "board_closure_minus_ideal_ms": describe(r["close_clock_error_ms"] for r in validation_selected),
            "host_receipt_duration_minus_board_ms": describe(r["host_elapsed_minus_board_ms"] for r in validation_selected),
            "burst_count_matches": sum(r["burst_match"] for r in validation_selected),
            "first_waveform_matches": sum(r["first_waveform_match"] for r in validation_selected),
            "dispense_path_matches": sum(r["dispense_path_matches"] for r in validation_selected),
            "board_close_receipts_match": sum(r["board_close_receipt_matches"] for r in validation_selected),
            "flow_sequence_matches": sum(r["flow_sequence_match"] for r in validation_selected),
            "forecast_posted_before_wet_command": sum(r["prospective_forecast_verified"] for r in validation_selected),
            "prospective_forecast_matches_frozen_file": sum(r["registered_volume_forecast_matches"] is True for r in validation_selected),
        },
        "overall_expected_waveform": compare(photographed),
        "expected_waveform_by_head": {
            head: compare([r for r in photographed if r["head"] == head]) for head in ("A", "B")
        },
        "overall_including_unexpected_waveforms": compare([r for r in validation_selected if r["optically_complete"]]),
        "cooldown": cooldown(cells, plan),
        "equal_water_full_minus_half": equal_water(cells, plan),
        "repeat_diagnostics_by_head": {
            head: diagnostic_splits([r for r in validation_selected if r["head"] == head]) for head in ("A", "B")
        },
        "within_scenario_repeat_correlations": {
            head: {
                f"{a}__{b}": centered_correlation([r for r in matched if r["head"] == head], a, b)
                for a, b in (("primary_error_pct", "heldout_error_pct"), ("primary_error_pct", "clear_error_pct"),
                             ("heldout_error_pct", "clear_error_pct"), ("start_ml", "primary_error_pct"),
                             ("start_ml", "heldout_error_pct"), ("start_ml", "clear_error_pct"))
            } for head in ("A", "B")
        },
        "faults_and_retries": [
            {"record": t["record"], "scenario": t["scenario"], "head": t["head"], "block": t["block"],
             "attempt": t["attempt_in_cell"], "fault": t["fault"], "burst_match": t["burst_match"],
             "primary_readable": t["primary_ml"] is not None, "heldout_readable": t["heldout_ml"] is not None,
             "optical_flags": t["optical_flags"]}
            for t in attempts if not t["matches_plan"] or t["heldout_ml"] is None or t["attempt_in_cell"] > 1
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "scores.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    write_csv(output / "attempts.csv", attempts)
    compact = []
    for result in conditions:
        compact.append({k: result[k] for k in (
            "scenario", "head", "forecast_ml", "attempted_cells", "planned", "attempts", "matching_bursts_and_primary",
            "primary_within_band", "heldout_within_band", "primary_within_five_percent", "heldout_within_five_percent",
            "bias_limit_ml", "primary_result", "corroborated_result")} | {
                "observed_median_ml": result["primary_observations_ml"].get("median"),
                "observed_min_ml": result["primary_observations_ml"].get("minimum"),
                "observed_max_ml": result["primary_observations_ml"].get("maximum"),
                "primary_bias_ml": result["comparisons"]["candidate_primary"].get("bias_ml"),
                "primary_median_abs_error_ml": result["comparisons"]["candidate_primary"].get("median_abs_error_ml"),
                "heldout_bias_ml": result["comparisons"]["candidate_heldout"].get("bias_ml"),
                "candidate_training_check_ml": result["max_forecast_reconstruction_difference_ml"],
                "frozen_clear_px": result["clear_pixel_model"]["forecast_px"],
                "measured_clear_within_band": result["clear_pixel_model"]["within_band"],
                "mean_clear_error_px": result["clear_pixel_model"]["mean_signed_error_px"],
                "clear_pixel_result": result["clear_pixel_model"]["result"],
            })
    write_csv(output / "by-scenario.csv", compact)
    block_rows = []
    split_sources = [(r["scenario"], r["head"], r["repeat_diagnostics"]) for r in conditions]
    split_sources += [("all scenarios", head, splits) for head, splits in summary["repeat_diagnostics_by_head"].items()]
    for name, head, splits in split_sources:
        for period in ("first_three_blocks", "last_three_blocks"):
            d = splits[period]
            block_rows.append({
                "scenario": name, "head": head, "validation_blocks": "1–3" if period == "first_three_blocks" else "4–6",
                "observed_pours": d["observed_pours"], "readable_primary": d["primary_error_ml"]["n"],
                "primary_within_band": d["primary_within_band"], "primary_bias_ml": d["primary_error_ml"].get("mean"),
                "readable_heldout": d["heldout_error_ml"]["n"],
                "heldout_within_band": d["heldout_within_band"], "heldout_bias_ml": d["heldout_error_ml"].get("mean"),
                "readable_clear_pixels": d["clear_error_px"]["n"],
                "clear_within_band": d["clear_within_band"], "clear_bias_px": d["clear_error_px"].get("mean"),
                "primary_median_relative_error_pct": d["primary_relative_error_pct"].get("median"),
                "heldout_median_relative_error_pct": d["heldout_relative_error_pct"].get("median"),
                "clear_median_relative_error_pct": d["clear_relative_error_pct"].get("median"),
                "paired_sightline_readings": d["half_sightline_disagreement_ml"]["n"],
                "median_half_sightline_gap_ml": d["half_sightline_disagreement_ml"].get("median"),
                "disjoint_sightline_tolerance_intervals": d["sightline_gap_exceeds_both_tolerances"],
            })
    write_csv(output / "block-comparison.csv", block_rows)
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("design", type=Path)
    ap.add_argument("priors", type=Path)
    ap.add_argument("train", type=Path)
    ap.add_argument("validation", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = score(args.design, args.priors, args.train, args.validation, args.output)
    seen = result["measurement_availability_expected_waveform"]
    print(f'{seen["photographed"]} of {result["planned_validation"]} scheduled pour waveforms photographed. '
          f'The cup yielded {seen["primary_ruler"]} primary and {seen["heldout_ruler"]} secondary volumes.')
