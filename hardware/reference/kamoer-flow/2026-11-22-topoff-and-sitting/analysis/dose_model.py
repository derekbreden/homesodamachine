"""Fit or apply a head-specific concentrate dose model to a controller motor schedule."""
import argparse
import csv
import io
import json
import math
import re
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path


ARCHIVE = "bc26987f18f42e863b6e2af7df3dad5da07d3eb7"
STUDY = "hardware/reference/kamoer-flow/2026-11-22-pour-predictions/"
TRIALS = "optical-calibration/geometry-results/trials.csv"
DESIGNS = ("preregistration.json", "fresh-programs.json")
POLICY = "firmware/lib/machine_policy/pour_policy.h"
FEATURES = ("on_s", "pulses", "train_starts", "on_s_above_knee")
MODELS = {
    "time_only": ("on_s",),
    "per_pulse": ("on_s", "pulses"),
    "per_pulse_and_first_start": ("on_s", "pulses", "nonempty"),
    "exponential_pause_recovery": ("on_s", "pulses", "recovered"),
    "quadratic_width_and_first_start": ("on_s", "pulses", "nonempty", "width_s_squared"),
    "piecewise_width_and_first_start": ("on_s", "pulses", "nonempty", "on_s_above_knee"),
    "piecewise_width_and_restarts": FEATURES,
}


def gate_intervals(gates):
    """Read ordered, physically distinct intervals during which the motor is on."""
    result = []
    for gate in gates:
        if len(gate) != 2:
            raise ValueError("Each gate must contain its start and width in milliseconds.")
        start, width = map(float, gate)
        if not all(map(math.isfinite, (start, width))) or start < 0 or width <= 0:
            raise ValueError("Gate starts must be finite and nonnegative, widths finite and positive.")
        if result:
            previous_start, previous_width = result[-1]
            previous_end = previous_start + previous_width
            if start < previous_end:
                raise ValueError("Motor gates are unsorted or overlapping.")
            if start == previous_end:
                result[-1] = (previous_start, previous_width + width)
                continue
        result.append((start, width))
    return result


def feature_values(gates, width_knee_ms, normal_off_limit_ms):
    gates = gate_intervals(gates)
    widths = [width for _, width in gates]
    gaps = [start - (prior_start + prior_width)
            for (prior_start, prior_width), (start, _) in zip(gates, gates[1:])]
    return {
        "on_s": sum(widths) / 1000,
        "pulses": len(widths),
        "train_starts": int(bool(gates)) + sum(gap > normal_off_limit_ms for gap in gaps),
        "on_s_above_knee": sum(max(width - width_knee_ms, 0) for width in widths) / 1000,
        "nonempty": int(bool(gates)),
        "recovered": sum(-math.expm1(-gap / 350) for gap in gaps),
        "width_s_squared": sum((width / 1000) ** 2 for width in widths),
    }


def predict(model, head, gates):
    """Predict the positive quantity of concentrate moved, in cup-calibrated mL."""
    values = feature_values(gates, model["width_knee_ms"], model["normal_off_limit_ms"])
    coefficients = model["heads"][head]
    return max(0.0, sum(coefficient * values[key] for key, coefficient in coefficients.items()))


def archive_text(repo, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{ARCHIVE}:{path}"], text=True)


def write_json(path, record):
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n")


def archive_rows(repo):
    designs = {}
    for filename in DESIGNS:
        designs.update(json.loads(archive_text(repo, STUDY + filename))["scenarios"])
    rows = list(csv.DictReader(io.StringIO(archive_text(repo, STUDY + TRIALS))))
    groups = {}
    for row in rows:
        scenario = row["scenario"]
        gates = tuple(tuple(gate) for gate in designs[scenario]["ideal_gates_start_ms_width_ms"])
        if row["status"] != "complete" or row["bursts_match"] != "True" or int(row["burst_count"]) != len(gates):
            raise ValueError(f"Unconfirmed training waveform in {row['label']}")
        group = groups.setdefault(gates, {"scenarios": [], "observations": defaultdict(list)})
        if scenario not in group["scenarios"]:
            group["scenarios"].append(scenario)
        group["observations"][row["head"]].append(row)
    return rows, groups


def parameters(groups, rule_text):
    widths = sorted({width for gates in groups for _, width in gates})
    off_limit = re.search(r"\bkPourOffMaxMs\s*=\s*(\d+)\s*;", rule_text)
    return {
        "width_knee_ms": statistics.median(widths),
        "normal_off_limit_ms": int(off_limit.group(1)),
    }


def estimate(keys, head, indices, groups, features):
    import numpy as np

    matrix = [[features[i][key] for key in keys] for i in indices]
    dose = [statistics.mean(float(r["x990_dose_ml"]) for r in groups[i]["observations"][head])
            for i in indices]
    scale = np.maximum(1.0, 0.05 * np.array(dose))
    coefficients, _, rank, _ = np.linalg.lstsq(np.array(matrix) / scale[:, None],
                                                np.array(dose) / scale, rcond=None)
    if rank < len(keys):
        raise ValueError(f"Unidentified coefficients for {keys}, {head}")
    return {key: float(value) for key, value in zip(keys, coefficients)}


def group_score(prediction, rows):
    record = {"prediction_ml": prediction, "pours": len(rows)}
    for sightline in ("x990", "x1986"):
        doses = [float(r[sightline + "_dose_ml"]) for r in rows]
        errors = [dose - prediction for dose in doses]
        record[sightline] = {
            "mean_observed_ml": statistics.mean(doses),
            "mean_observed_minus_predicted_ml": statistics.mean(errors),
            "single_pours_inside_practical": sum(abs(e) <= max(1.0, 0.10 * prediction) for e in errors),
            "single_pours_inside_five_percent": sum(abs(e) <= 0.05 * prediction for e in errors),
        }
    return record


def summarise(scored):
    result = {}
    for head in "AB":
        records = [record[head] for record in scored]
        by_lane = {}
        for sightline in ("x990", "x1986"):
            errors = [r[sightline]["mean_observed_minus_predicted_ml"] for r in records]
            by_lane[sightline] = {
                "mean_absolute_program_error_ml": statistics.mean(map(abs, errors)),
                "maximum_absolute_program_error_ml": max(map(abs, errors)),
                "mean_signed_program_error_ml": statistics.mean(errors),
                "single_pours_inside_practical": sum(r[sightline]["single_pours_inside_practical"] for r in records),
                "single_pours_inside_five_percent": sum(r[sightline]["single_pours_inside_five_percent"] for r in records),
            }
        result[head] = {"gate_trains": len(records), "pours": sum(r["pours"] for r in records), **by_lane}
    return result


def holdout(keys, group_ids, groups, features):
    scores = [None] * len(groups)
    for held in dict.fromkeys(group_ids):
        train = [i for i, family in enumerate(group_ids) if family != held]
        excluded = [i for i, family in enumerate(group_ids) if family == held]
        fits = {head: estimate(keys, head, train, groups, features) for head in "AB"}
        for i in excluded:
            scores[i] = {"scenarios": groups[i]["scenarios"]}
            for head in "AB":
                forecast = max(0.0, sum(fits[head][k] * features[i][k] for k in keys))
                scores[i][head] = group_score(forecast, groups[i]["observations"][head])
    return scores


def legacy_comparison(repo, gates, groups, leave_train_out):
    import numpy as np

    schedule = json.loads(archive_text(repo, STUDY + DESIGNS[0]))["scenarios"]
    training_gates = {tuple(map(tuple, s["ideal_gates_start_ms_width_ms"])) for s in schedule.values()
                      if s["phase"] == "training"}
    anchors = json.loads(archive_text(repo, STUDY + "optical-calibration/geometry-model.json"))["anchors_ml_per_burst"]
    baseline, candidate = [], []
    for i, train in enumerate(gates):
        if train in training_gates:
            continue
        legacy = {"scenarios": groups[i]["scenarios"]}
        for head in "AB":
            points = sorted((int(width), value) for width, value in anchors[head].items())
            widths, doses = zip(*points)
            prediction = sum(float(np.interp(w, widths, doses)) for _, w in train)
            legacy[head] = group_score(prediction, groups[i]["observations"][head])
        baseline.append(legacy)
        candidate.append(leave_train_out[i])
    return {
        "comparison": "Programs excluded from the archived anchor calibration. Candidate excludes the entire scored train.",
        "archived_anchor_model": summarise(baseline),
        "candidate": summarise(candidate),
        "archived_anchor_group_results": baseline,
    }


def fit(repo, output):
    rows, grouped = archive_rows(repo)
    gates, groups = list(grouped), list(grouped.values())
    settings = parameters(grouped, archive_text(repo, POLICY))
    features = [feature_values(train, **settings) for train in gates]
    indices = list(range(len(groups)))
    heads = {head: estimate(FEATURES, head, indices, groups, features) for head in "AB"}
    model = {
        "purpose": "Predict the concentrate transferred by one bench head from its controller motor-on intervals.",
        "training_revision": ARCHIVE,
        "training_files": [STUDY + name for name in (TRIALS, *DESIGNS)],
        "controller_source": POLICY,
        "response": "Positive cup-calibrated mL from the x990 settled clear-glass sightline.",
        "gate_units": "[start_ms, width_ms], relative to the first motor command",
        "equation": "max(0, sum of each feature times its head coefficient)",
        "features": {
            "on_s": "Sum of motor-on durations in seconds.",
            "pulses": "Number of separate motor-on intervals.",
            "train_starts": "One for a nonempty schedule plus each motor-off gap exceeding the controller normal off-time limit.",
            "on_s_above_knee": "Sum of each motor-on interval's positive duration above the width knee in seconds.",
        },
        "width_knee_source": "Median of the distinct gate widths present in the archived motor schedules.",
        "normal_off_limit_source": "kPourOffMaxMs in the archived controller source; only one prior program had a gap above this limit.",
        "weighting": "One mean per unique gate train per head. Minimize squared dose residuals divided by max(1 mL, 5% of the training mean dose) squared.",
        "conditions": "Bench transfer of undiluted Diet Cola. A withdraws from the OXO cup and B fills it. Starting fill and conditioning varied in the archive.",
        **settings,
        "heads": heads,
        "historical_ranges": {
            "gate_width_ms": [min(w for g in gates for _, w in g), max(w for g in gates for _, w in g)],
            "motor_intervals_per_pour": [min(map(len, gates)), max(map(len, gates))],
            "off_gap_ms": sorted({cur[0] - sum(prev) for g in gates for prev, cur in zip(g, g[1:])}),
            "unique_gate_trains_per_head": len(groups),
            "observations_per_head": {head: sum(len(g["observations"][head]) for g in groups) for head in "AB"},
            "starting_x990_ml": {head: [min(float(r["x990_start_ml"]) for r in rows if r["head"] == head),
                                       max(float(r["x990_start_ml"]) for r in rows if r["head"] == head)] for head in "AB"},
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "model.json", model)

    by_family = [tuple(sorted({w for _, w in train})) for train in gates]
    candidate_scores = None
    diagnostics = {
        "interpretation": "Historical model-development checks. Folds hold both heads and every repeat of a gate train out together. A width-family fold holds every train with the same set of widths out together. The second sightline views the same pour and does not set fit coefficients.",
        "residual": "Observed minus predicted, in cup-calibrated mL.",
        "candidates": {},
    }
    for name, keys in MODELS.items():
        train_scores = holdout(keys, indices, groups, features)
        family_scores = holdout(keys, by_family, groups, features)
        diagnostics["candidates"][name] = {
            "features": list(keys),
            "leave_gate_train_out": summarise(train_scores),
            "leave_width_family_out": summarise(family_scores),
        }
        if keys == FEATURES:
            candidate_scores = train_scores
            diagnostics["candidate_gate_train_results"] = train_scores
            diagnostics["candidate_width_family_results"] = family_scores
    diagnostics["archived_interpolator"] = legacy_comparison(repo, gates, groups, candidate_scores)
    write_json(output / "fit-diagnostics.json", diagnostics)

    fields = ["label", "head", "scenario", "phase", "level", "burst_count",
              "x990_dose_ml", "x1986_dose_ml", "x990_start_ml", "x1986_start_ml"]
    with (output / "historical-doses.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_json(output / "historical-gates.json",
               [{"scenarios": group["scenarios"], "gates": train} for train, group in grouped.items()])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    fitter = actions.add_parser("fit")
    fitter.add_argument("--repo", type=Path, default=Path.cwd())
    fitter.add_argument("--out", type=Path, default=Path(__file__).parent)
    estimator = actions.add_parser("predict")
    estimator.add_argument("--model", type=Path, default=Path(__file__).with_name("model.json"))
    estimator.add_argument("--head", choices=("A", "B"), required=True)
    estimator.add_argument("--gates", type=json.loads, required=True)
    args = parser.parse_args()
    if args.action == "fit":
        fit(args.repo, args.out)
    else:
        print(predict(json.loads(args.model.read_text()), args.head, args.gates))


if __name__ == "__main__":
    main()
