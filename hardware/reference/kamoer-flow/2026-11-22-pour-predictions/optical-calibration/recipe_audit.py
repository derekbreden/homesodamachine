"""Test known serving programs on both glass lanes and compare the two frozen forecasts on the same pours."""

from collections import defaultdict
from statistics import mean, median

from fit_geometry import map_ml


def width_checks(rows, training_design, schedules):
    """Reconstruct every head-specific width median and ideal-trace forecast from the original photographed training pours."""
    observed = defaultdict(list)
    for trial in rows:
        if (
            trial["phase"] != "training"
            or trial["status"] != "complete"
            or not trial["bursts_match"]
        ):
            continue
        dose = trial.get("x990_dose_ml")
        if dose is not None:
            gates = training_design["scenarios"][trial["scenario"]][
                "ideal_gates_start_ms_width_ms"
            ]
            widths = {w for _, w in gates}
            if len(widths) != 1:
                raise ValueError("Training calibration contains a mixed-width program")
            observed[(trial["head"], widths.pop())].append(
                (trial["label"], dose / trial["burst_count"])
            )
    out = {"per_burst": {}, "programs": {}}
    for head in ("A", "B"):
        points = []
        out["per_burst"][head] = {}
        for (h, width), group in sorted(observed.items()):
            if h != head or len(group) < 2:
                continue
            dose = median(v for _, v in group)
            points.append((width, dose))
            out["per_burst"][head][width] = {
                "labels": [l for l, _ in group],
                "raw_ml": [m for _, m in group],
                "median_ml": dose,
            }
        for phase, (design, model) in schedules.items():
            for name, program in design["scenarios"].items():
                if program["phase"] != "validation":
                    continue
                q = out["programs"].setdefault(phase, {}).setdefault(name, {})
                amounts = [
                    map_ml(points, width)
                    for _, width in program["ideal_gates_start_ms_width_ms"]
                ]
                calculated = (
                    sum(amounts)
                    if amounts and all(v is not None for v in amounts)
                    else None
                )
                target = model["forecasts"][name][head]
                q[head] = {
                    "pixel_derived_forecast_ml": calculated,
                    "frozen_ml": target,
                    "difference_ml": None
                    if calculated is None
                    else calculated - target,
                }
    return out


def level_checks(rows, model):
    """Score the frozen fill-specific and pooled predictions on exactly the same reserved servings."""
    all_rows = [q for q in rows if q["phase"] == "fill" and q["status"] == "complete"]
    first = set(model["training_indices"])
    training = {}
    for head, levels in model["forecasts_ml"].items():
        training[head] = {}
        for level in ("low", "high"):
            dose = [
                q["x990_dose_ml"]
                for q in all_rows
                if q["index"] in first
                and q["head"] == head
                and q["level"] == level
                and q["x990_dose_ml"] is not None
                and q["bursts_match"]
            ]
            training[head][level] = {
                "source_doses_ml": dose,
                "mean_minus_frozen_ml": mean(dose) - levels[level]
                if len(dose) == 3
                else None,
            }
    seen = []
    for q in all_rows:
        if q["block"] not in (5, 6):
            continue
        r = {
            k: q[k]
            for k in (
                "label",
                "head",
                "level",
                "index",
                "block",
                "board_start_ns",
                "bursts_match",
            )
        }
        r["after_freeze"] = (
            r["board_start_ns"] is not None
            and r["board_start_ns"] >= model["frozen_monotonic_ns"]
        )
        table = model["forecasts_ml"][r["head"]]
        for k, f in (("specific", table[r["level"]]), ("pooled", table["pooled"])):
            r[k + "_forecast_ml"] = f
            for site in ("x990", "x1986"):
                v = q[site + "_dose_ml"]
                err = None if v is None else v - f
                r[k + "_" + site + "_error_ml"] = err
                r[k + "_" + site + "_inside"] = (
                    r["after_freeze"]
                    and r["bursts_match"]
                    and err is not None
                    and abs(err) <= max(1, 0.1 * f)
                )
        seen.append(r)
    groups = {}
    for head in ("all", "A", "B"):
        subset = seen if head == "all" else [q for q in seen if q["head"] == head]
        for site in ("x990", "x1986"):
            eligible = [
                q
                for q in subset
                if q["after_freeze"]
                and q["bursts_match"]
                and q["specific_" + site + "_error_ml"] is not None
            ]
            errors = {
                k: mean(abs(q[k + "_" + site + "_error_ml"]) for q in eligible)
                if eligible
                else None
                for k in ("specific", "pooled")
            }
            gain = errors["pooled"] - errors["specific"] if eligible else None
            count = sum(q["specific_" + site + "_inside"] for q in eligible)
            groups[head + "_" + site] = {
                "eligible": len(eligible),
                "specific_mae_ml": errors["specific"],
                "pooled_mae_ml": errors["pooled"],
                "mae_reduction_ml": gain,
                "specific_inside": count,
                "aggregate_decision": bool(
                    len(eligible) == 8 and gain >= 0.25 and count >= 7
                )
                if head == "all" and gain is not None
                else None,
            }
    return seen, {"training": training, "results": groups}


def score(rows, recipe, widths):
    observations = []
    training = defaultdict(list)
    tests = defaultdict(list)
    frozen_ns = recipe["frozen_monotonic_ns"]
    training_indices = set(recipe["training_indices"])
    for trial in rows:
        if (
            trial.get("phase") not in ("fresh", "repeat")
            or trial["status"] != "complete"
        ):
            continue
        scenario, head = trial["scenario"], trial["head"]
        if trial["phase"] == "fresh" and trial["index"] in training_indices:
            training[(scenario, head)].append(trial)
            continue
        if trial["phase"] == "fresh" and trial["block"] < 3:
            continue
        board_start = trial["board_start_ns"]
        eligible = board_start is not None and board_start >= frozen_ns
        q = {
            key: trial[key]
            for key in (
                "phase",
                "head",
                "scenario",
                "block",
                "index",
                "label",
                "pre",
                "post",
                "bursts_match",
                "prediction_monotonic_ns",
                "board_start_ns",
            )
        }
        q["command_ms_after_recipe_freeze"] = (
            None if board_start is None else (board_start - frozen_ns) / 1e6
        )
        q["eligible_by_freeze_time"] = eligible
        for model, table in (("recipe", recipe), ("width", widths)):
            pred = table["forecasts"][scenario][head]
            q[model + "_forecast_ml"] = pred
            for site in ("x990", "x1986"):
                v = trial[site + "_dose_ml"]
                q[site + "_dose_ml"] = v
                err = None if v is None else v - pred
                prefix = model + "_" + site
                q[prefix + "_error_ml"] = err
                q[prefix + "_inside"] = (
                    eligible
                    and trial["bursts_match"]
                    and err is not None
                    and abs(err) <= max(1.0, 0.10 * pred)
                )
        observations.append(q)
        if eligible:
            tests[(head, scenario)].append(q)
    checked = []
    for name, by_head in recipe["forecasts"].items():
        for head, fixed in by_head.items():
            group = training[(name, head)]
            primary = [
                r["x990_dose_ml"]
                for r in group
                if r["x990_dose_ml"] is not None and r["bursts_match"]
            ]
            observed = mean(primary) if len(primary) == 2 else None
            checked.append(
                {
                    "scenario": name,
                    "head": head,
                    "labels": [r["label"] for r in group],
                    "x990_photographed_doses_ml": primary,
                    "frozen_forecast_ml": fixed,
                    "pixel_replay_minus_frozen_ml": None
                    if observed is None
                    else observed - fixed,
                }
            )
    results = []
    for (head, name), group in sorted(tests.items()):
        by_block = {}
        for q in group:
            by_block.setdefault((q["phase"], q["block"]), q)
        done = list(by_block.values())
        for model in ("recipe", "width"):
            f = group[0][model + "_forecast_ml"]
            r = {
                "head": head,
                "scenario": name,
                "model": model,
                "scheduled": 6,
                "eligible_unique_repeats": len(done),
                "forecast_ml": f,
            }
            for site in ("x990", "x1986"):
                prefix = model + "_" + site
                errors = [
                    q[prefix + "_error_ml"]
                    for q in done
                    if q[prefix + "_error_ml"] is not None and q["bursts_match"]
                ]
                passed = sum(q[prefix + "_inside"] for q in done)
                bias = mean(errors) if errors else None
                r[site + "_scored"] = len(errors)
                r[site + "_inside"] = passed
                r[site + "_mean_error_ml"] = bias
                r[site + "_median_abs_error_ml"] = (
                    median(abs(v) for v in errors) if errors else None
                )
                r[site + "_meets_count_and_bias"] = (
                    len(done) == 6
                    and passed >= 5
                    and bias is not None
                    and abs(bias) <= max(0.6, 0.05 * f)
                )
            r["both_lanes_meet_count_and_bias"] = (
                r["x990_meets_count_and_bias"] and r["x1986_meets_count_and_bias"]
            )
            results.append(r)
    return (
        observations,
        results,
        {
            "frozen_monotonic_ns": frozen_ns,
            "training": checked,
            "eligible": sum(q["eligible_by_freeze_time"] for q in observations),
            "started_before_freeze_or_unknown": [
                q["label"] for q in observations if not q["eligible_by_freeze_time"]
            ],
        },
    )
