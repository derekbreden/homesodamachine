"""Score the unseen lever histories against the graduation-calibrated dose forecasts."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from score_pours import (
    assemble_attempts, attempt, cell, chosen_trial, compare, condition, describe,
    json_lines, number, same_reading, write_csv,
)


def mapped_volume(reading, points):
    if not reading or number(reading.get("row")) is None or reading.get("contrast", 0) < 6:
        return None
    row = reading["row"]
    points = sorted(points)
    for (left, lower_ml), (right, higher_ml) in zip(points, points[1:]):
        if left <= row <= right:
            return lower_ml + (row - left) * (higher_ml - lower_ml) / (right - left)
    return None


def reduction_check(record, calibration, site, field):
    before = mapped_volume(record.get("pre_cup", {}).get(site), calibration["anchors"].get(site, []))
    after = mapped_volume(record.get("post_cup", {}).get(site), calibration["anchors"].get(site, []))
    sign = 1 if record["head"] == "B" else -1
    calibrated = sign * (after - before) if before is not None and after is not None else None
    return same_reading(calibrated, number(record.get(field)))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_fresh(programs, calibration_file, model_file, archive_file, journal, output):
    plan = json.loads(programs.read_text())
    model = json.loads(model_file.read_text())
    mapping = json.loads(calibration_file.read_text())
    priors = json.loads(archive_file.read_text())
    if model["source_sha256"]["programs"] != digest(programs) or priors["preregistration_sha256"] != digest(programs):
        raise ValueError("The frozen forecasts or earlier comparators use different lever programs")
    if model["source_sha256"]["map"] != digest(calibration_file):
        raise ValueError("The geometry model and scoring supplied different graduation maps")
    cells = defaultdict(list)
    attempts = []
    for record in assemble_attempts(json_lines(journal), plan):
        t = attempt(record, plan, priors)
        target = model["forecasts"][t["scenario"]][t["head"]]
        t["geometry_forecast_matches"] = same_reading(t["forecast_ml"], target)
        t["primary_readback_matches_geometry"] = reduction_check(record, mapping, "x990", "primary_ml")
        t["heldout_readback_matches_geometry"] = reduction_check(record, mapping, "x1986", "heldout_ml")
        for site in ("primary", "heldout"):
            if not t["geometry_forecast_matches"] or not t[f"{site}_readback_matches_geometry"]:
                t[f"{site}_pass"] = False
                t[f"{site}_pass_five_percent"] = False
        group = cells[cell(t)]
        t["attempt_in_cell"] = len(group) + 1
        group.append(t)
        attempts.append(t)
    for group in cells.values():
        selected = chosen_trial(group)
        for t in group:
            t["selected_for_cell"] = t is selected
    planned_cells = {cell(r) for r in plan["orders"]["validation"]}
    if set(cells) - planned_cells:
        raise ValueError("The journal includes an unregistered trial")
    grouped = defaultdict(list)
    for row in plan["orders"]["validation"]:
        grouped[row["scenario"], row["head"]].append(cells[cell(row)])
    results = []
    for (name, head), groups in grouped.items():
        s = condition(name, head, groups, len(groups), {}, plan)
        s["forecast_ml"] = model["forecasts"][name][head]
        s.pop("reconstructed_training_forecast_ml", None)
        s.pop("max_forecast_reconstruction_difference_ml", None)
        results.append(s)
    selected = [r for r in attempts if r["selected_for_cell"]]
    photographed = [r for r in selected if r["photographed_expected_waveform"]]
    summary = {
        "programs_sha256": digest(programs), "graduation_map_sha256": digest(calibration_file),
        "frozen_model_sha256": digest(model_file), "journal_sha256": digest(journal) if journal.exists() else None,
        "interpretation": "Both clear-glass sightlines are calibrated against photographed graduation crossings on the same kitchen cup. Six new pours per head and history were prescribed. Primary acceptance also requires the registered bias limit. Corroboration additionally requires five secondary doses in band.",
        "planned_validation": len(planned_cells), "attempted_cells": len(selected),
        "all_attempts": len(attempts), "classification": results,
        "available_expected_waveforms": {
            "photographed": len(photographed),
            "primary": sum(r["primary_ml"] is not None for r in photographed),
            "heldout": sum(r["heldout_ml"] is not None for r in photographed),
            "both_sightlines": sum(r["primary_ml"] is not None and r["heldout_ml"] is not None for r in photographed),
        },
        "receipts": {
            "forecast_before_command": sum(r["prospective_forecast_verified"] for r in selected),
            "forecast_matches_geometry_freeze": sum(r["geometry_forecast_matches"] for r in selected),
            "first_waveform_matches": sum(r["first_waveform_match"] for r in selected),
            "dispense_path_matches": sum(r["dispense_path_matches"] for r in selected),
            "flow_sequence_matches": sum(r["flow_sequence_match"] for r in selected),
            "completed_burst_counts_match": sum(r["burst_match"] for r in selected),
            "signed_board_minus_policy_close_ms": describe(r["close_clock_error_ms"] for r in selected),
            "input_stage_write_minus_planned_ms": describe(x for r in selected for x in r["stage_clock_errors_ms"]),
            "logged_right_displacement_reproduced": sum(r["primary_readback_matches_geometry"] for r in photographed),
            "logged_secondary_displacement_reproduced": sum(r["heldout_readback_matches_geometry"] for r in photographed),
        },
        "expected_waveform_errors": compare(photographed),
        "sightline_disagreement_ml": describe(r["heldout_ml"] - r["primary_ml"] for r in photographed if r["primary_ml"] is not None and r["heldout_ml"] is not None),
        "exceptions": [
            {"record": r["record"], "label": r["label"], "fault": r["fault"], "optical_flags": r["optical_flags"],
             "primary_ml": r["primary_ml"], "heldout_ml": r["heldout_ml"], "burst_match": r["burst_match"]}
            for r in attempts if not r["matches_plan"] or r["heldout_ml"] is None or r["attempt_in_cell"] > 1
        ],
    }
    compact = []
    for r in results:
        s = plan["scenarios"][r["scenario"]]
        compact.append({
            "scenario": r["scenario"], "head": r["head"], "ratio_setting": s["ratio"],
            "burst_count": s["ideal_bursts"], "total_on_s": s["ideal_on_s"], "nominal_water_ml": s["nominal_water_ml"],
            "forecast_ml": r["forecast_ml"], "median_observed_ml": r["primary_observations_ml"].get("median"),
            "min_observed_ml": r["primary_observations_ml"].get("minimum"), "max_observed_ml": r["primary_observations_ml"].get("maximum"),
            "primary_bias_ml": r["comparisons"]["candidate_primary"].get("bias_ml"),
            "primary_median_absolute_error_ml": r["comparisons"]["candidate_primary"].get("median_abs_error_ml"),
            "secondary_bias_ml": r["comparisons"]["candidate_heldout"].get("bias_ml"),
            "planned": r["planned"], "primary_within_band": r["primary_within_band"], "secondary_within_band": r["heldout_within_band"],
            "primary_within_five_percent": r["primary_within_five_percent"], "secondary_within_five_percent": r["heldout_within_five_percent"],
            "primary_result": r["primary_result"], "corroborated_result": r["corroborated_result"],
        })
    output.mkdir(parents=True, exist_ok=True)
    (output / "scores.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    write_csv(output / "attempts.csv", attempts)
    write_csv(output / "by-scenario.csv", compact)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("programs", "map", "model", "archive", "journal"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = score_fresh(args.programs, args.map, args.model, args.archive, args.journal, args.output)
    print(f'{result["available_expected_waveforms"]["photographed"]} new pours photographed out of {result["planned_validation"]} planned.')
