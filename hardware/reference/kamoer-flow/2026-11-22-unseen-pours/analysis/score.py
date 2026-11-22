"""Score the frozen endpoints of the reserved pour programs from the controller and camera journal."""
import argparse
import csv
import hashlib
import json
import math
import re
from datetime import datetime
from itertools import accumulate
from pathlib import Path
from statistics import mean, median, stdev

from scipy.stats import t as student_t


RECORD = Path(__file__).resolve().parents[1]
SITES = {"near": "x990", "far": "x1986"}
DESIGN_GIT = "cd4b81349d685eb61ad615c59f2408cad7ca8e2d"
FORECAST_GIT = "0bc951783366815b7d9e5d1566ea9ec3bc3965ac"


def read_json(path):
    return json.loads(path.read_text())


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def save_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def trial_segments(events):
    segments = {}
    for i, e in enumerate(events):
        if e["event"] != "prediction":
            continue
        idx = e["index"]
        if idx in segments:
            raise ValueError(f"More than one prospective attempt at index {idx}")
        segment = []
        for row in events[i + 1:]:
            if row["event"] in ("prediction", "session"):
                break
            segment.append(row)
            if row["event"] in ("trial", "halt"):
                break
        segments[idx] = (e, segment)
    return segments


def score_attempt(index, item, case, freeze, segment, photos):
    head, scenario = item["head"], item["scenario"]
    sign = 1 if head == "B" else -1
    forecasts = freeze["forecasts"][scenario][head]
    forecast = forecasts["dose_ml"]
    p, rows = segment
    start = next((e for e in rows if e["event"] == "board_pour_start"), {})
    stop = next((e for e in rows if e["event"] == "board_pour_end"), {})
    trial = next((e for e in rows if e["event"] == "trial"), {})
    flow = [e for e in rows if e["event"] == "tx" and e["command"].startswith("flow ")]
    expected_commands = [f"flow {n} {math.ceil((hold + 200) / 1000)}" for n, hold in case["meter"]]
    expected_commands.append("flow 0 0")
    gates = case["ideal_gates_start_ms_width_ms"]
    on = gates[0][1]
    # The single-burst program uses the same first cycle as the uninterrupted glass.
    off = case["rest_sequence_ms"][0] if len(gates) > 1 else case["ideal_stop_ms"] - 1000 - on
    valves = {"A": "E G", "B": "H J"}[head]
    pre_label = p.get("start")
    post_label = trial.get("finish")
    pre, post = photos.get(pre_label, {}), photos.get(post_label, {})
    prospective = bool(p and flow and pre and
                       freeze["monotonic_ns"] < p["mono_ns"] < flow[0]["mono_ns"] and
                       pre["mid"]["pts_ns"] <= pre["mono_ns"] <= p["mono_ns"] and
                       datetime.fromisoformat(freeze["utc"]) <= datetime.fromisoformat(p["utc"]))
    rx = [e["line"] for e in rows if e["event"] == "rx"]
    matched = (
        [e["command"] for e in flow] == expected_commands and
        start.get("head") == stop.get("head") == head and start.get("ratio") == case["ratio"] and
        (start.get("first_on"), start.get("first_off"), start.get("valves")) == (on, off, valves) and
        stop.get("bursts") == case["ideal_bursts"] and
        any(f"pour {head} at 1:{case['ratio']}: valves {valves} open, pump {head} bursting {on} on / {off} off" in s for s in rx) and
        any(re.search(rf"pour {head}: flow stopped after {stop.get('elapsed_ms')} ms, {len(gates)} bursts? — valves closed", s) for s in rx)
    )
    if p and (any(item[k] != p[k] for k in item) or p["dose_ml"] != forecast or p["start_cup"] != pre.get("readings")):
        raise ValueError(f"Prediction or starting image differs from the reservation at {index}")
    if trial and (any(item[k] != trial[k] for k in item) or pre["readings"] != trial["pre"] or
                  post["readings"] != trial["post"] or trial["forecast_ml"] != forecast):
        raise ValueError(f"Inconsistent journal endpoints at {index}")
    eligible = bool(trial and prospective and matched and stop["mono_ns"] < post["mid"]["pts_ns"])
    timing_error = []
    if start:
        planned = accumulate(ms for _, ms in case["meter"])
        for event, ideal_ms in zip(flow[1:], planned):
            timing_error.append((event["mono_ns"] / 1e9 - start["first_receipt_clock"]) * 1000 - ideal_ms)
    row = dict(index=index, **item, nominal_water_ml=case["nominal_water_ml"], ratio=case["ratio"],
               forecast_ml=forecast, previous_width_forecast_ml=forecasts["old_width_model_ml"],
               pre_image=pre_label, post_image=post_label, prediction_utc=p.get("utc"),
               first_flow_utc=flow[0]["utc"] if flow else None, first_receipt_utc=start.get("utc"),
               last_receipt_utc=stop.get("utc"), measured=bool(trial),
               prospective=prospective, matched_receipt=matched, eligible=eligible,
               expected_bursts=len(gates), observed_bursts=stop.get("bursts"), expected_first_on_ms=on,
               observed_first_on_ms=start.get("first_on"), expected_first_off_ms=off,
               observed_first_off_ms=start.get("first_off"), expected_valves=valves,
               observed_valves=start.get("valves"), expected_stop_ms=case["ideal_stop_ms"],
               observed_stop_ms=stop.get("elapsed_ms"),
               max_abs_stage_timing_error_ms=max(map(abs, timing_error), default=None))
    for name, site in SITES.items():
        a = pre.get("readings", {}).get(site, {}).get("ml")
        b = post.get("readings", {}).get(site, {}).get("ml")
        end = p.get("predicted_finish_ml", {}).get(site)
        if end is not None and not math.isclose(end, a + sign * forecast, abs_tol=1e-9):
            raise ValueError(f"Unfrozen endpoint at {index} {site}")
        dose = sign * (b - a) if a is not None and b is not None else None
        err = dose - forecast if dose is not None else None
        if dose is not None and not math.isclose(dose, trial["dose_ml"][site], abs_tol=1e-9):
            raise ValueError(f"Journal dose and its endpoints disagree at {index} {site}")
        row.update({name+"_start_ml":a, name+"_predicted_finish_ml":end, name+"_finish_ml":b,
                    name+"_dose_ml":dose, name+"_error_ml":err})
    return row


def program_score(rows):
    first = rows[0]
    forecast = first["forecast_ml"]
    tolerance, bias_limit = max(1.0, .10 * forecast), max(.6, .05 * forecast)
    prior = first["previous_width_forecast_ml"]
    out = dict(head=first["head"], scenario=first["scenario"], planned=len(rows), forecast_ml=forecast,
               previous_width_forecast_ml=prior,
               nominal_water_ml=first["nominal_water_ml"], tolerance_ml=tolerance, bias_limit_ml=bias_limit)
    for site in SITES:
        errors = [r[site+"_error_ml"] for r in rows if r["eligible"] and r[site+"_error_ml"] is not None]
        average = mean(errors) if errors else None
        hits = sum(abs(x) <= tolerance for x in errors)
        passed = len(rows) == 6 and hits >= 5 and average is not None and abs(average) <= bias_limit
        out.update({site+"_scorable":len(errors), site+"_hits":hits,
                    site+"_five_percent_hits":sum(abs(x) <= .05 * forecast for x in errors),
                    site+"_mean_dose_ml":None if average is None else forecast+average,
                    site+"_mean_error_ml":average, site+"_median_dose_ml":None if not errors else forecast+median(errors),
                    site+"_mean_abs_error_ml":None if not errors else mean(map(abs,errors)),
                    site+"_max_abs_error_ml":max(map(abs, errors), default=None), site+"_pass":passed,
                    site+"_previous_mean_error_ml":None if average is None else forecast+average-prior,
                    site+"_previous_mean_abs_error_ml":None if not errors else mean(abs(forecast+e-prior) for e in errors)})
    out["both_pass"] = out["near_pass"] and out["far_pass"]
    return out


def contrasts(attempts, forecasts):
    index = {(r["head"], r["scenario"], r["block"]):r for r in attempts if r["eligible"]}
    output = {}
    for key, first, second, divisor in [
            ("restart", "resumed_glass", "steady_glass", 1), ("added_burst", "steady_glass", "quick_taste", 13)]:
        output[key] = {}
        for head in "AB":
            prediction = (forecasts[first][head]["dose_ml"] - forecasts[second][head]["dose_ml"]) / divisor
            summary = {"forecast_ml":prediction}
            for site in SITES:
                pairs = []
                for block in range(1, 7):
                    a, b = index.get((head, first, block), {}), index.get((head, second, block), {})
                    ua, ub = a.get(site+"_dose_ml"), b.get(site+"_dose_ml")
                    if ua is not None and ub is not None:
                        pairs.append({"block": block, "measured_ml":(ua-ub)/divisor})
                residuals = [r["measured_ml"]-prediction for r in pairs]
                avg = mean(residuals) if residuals else None
                interval = None
                if len(residuals) >= 2:
                    margin = student_t.ppf(.95, len(residuals)-1) * stdev(residuals) / math.sqrt(len(residuals))
                    interval = [avg-margin, avg+margin]
                summary[site] = {"pairs":pairs, "mean_measured_ml":None if avg is None else prediction+avg,
                                 "mean_measured_minus_forecast_ml":avg, "paired_90pct_error_interval_ml":interval}
                if key == "restart":
                    summary[site]["corroborated"] = bool(len(pairs)==6 and interval and interval[0]>-1 and interval[1]<1)
            output[key][head] = summary
    return output


def aggregate(attempts, site):
    rows = [r for r in attempts if r["eligible"] and r[site+"_dose_ml"] is not None]
    if not rows:
        return {"scorable":0}
    err = [r[site+"_error_ml"] for r in rows]
    previous = [r[site+"_dose_ml"] - r["previous_width_forecast_ml"] for r in rows]
    return {"planned":len(attempts), "scorable":len(rows), "mean_error_ml":mean(err),
            "mean_absolute_error_ml":mean(map(abs, err)), "max_absolute_error_ml":max(map(abs, err)),
            "within_practical":sum(abs(e)<=max(1,.10*r["forecast_ml"]) for e,r in zip(err,rows)),
            "within_five_percent":sum(abs(e)<=.05*r["forecast_ml"] for e,r in zip(err,rows)),
            "previous_width_forecast_mean_error_ml":mean(previous),
            "previous_width_forecast_mean_absolute_error_ml":mean(map(abs,previous))}


def block_scores(attempts):
    """Summarize residuals in acquisition order with every lever program represented in each block."""
    blocks = []
    for head, block in sorted({(r["head"], r["block"]) for r in attempts}):
        group = [r for r in attempts if r["head"]==head and r["block"]==block]
        row = {"head": head, "block": block, "planned": len(group)}
        for site in SITES:
            values = [r[site+"_error_ml"] for r in group if r["eligible"] and r[site+"_error_ml"] is not None]
            row[site+"_scorable"] = len(values)
            row[site+"_mean_error_ml"] = mean(values) if values else None
            row[site+"_mean_abs_error_ml"] = mean(map(abs,values)) if values else None
        blocks.append(row)
    return blocks


def describe(values):
    if not values:
        return {"n": 0}
    return {"n": len(values), "mean_ml": mean(values), "median_absolute_ml": median(map(abs, values)),
            "max_absolute_ml": max(map(abs, values))}


def stationary_pairs(events):
    """Compare successive snapshots with no intervening command capable of moving liquid."""
    prior = None
    pairs = []
    for e in events:
        if e["event"] == "session" or (e["event"] == "tx" and
                                       e["command"].startswith(("pump ", "flow ", "stop"))):
            prior = None
        if e["event"] != "image":
            continue
        if prior:
            row = {"first": prior["label"], "second": e["label"],
                   "elapsed_s": (e["mid"]["pts_ns"]-prior["mid"]["pts_ns"]) / 1e9}
            for site, key in SITES.items():
                a, b = prior["readings"][key]["ml"], e["readings"][key]["ml"]
                row[site+"_change_ml"] = None if a is None or b is None else b-a
            pairs.append(row)
        prior = e
    return pairs


def bench_state(logs):
    def read(mode):
        return [json.loads(line) for line in (logs/(mode+".jsonl")).read_text().splitlines()]

    def returned_status(events):
        last = max(i for i,e in enumerate(events) if e["event"]=="tx" and e["command"]=="status")
        lines = [e["line"] for e in events[last:] if e["event"]=="rx"]
        restored = next(e for e in reversed(events) if e["event"]=="settings_restored")
        return {"status_utc": events[last]["utc"], "settings": restored["settings"],
                "readbacks": [s for s in lines if s.startswith(("state ", "valves ", "volume ", "expanders "))]}

    before, after = read("qualify"), read("park")
    stationary = next(e for e in before if e["event"]=="no_pump")
    returned = next(e for e in after if e["event"]=="station_return")
    return {"qualified": returned_status(before), "parked": returned_status(after),
            "stationary_pretest_change_ml": {k: s["ml"]-stationary["start"][k]["ml"]
                                           for k,s in stationary["finish"].items()},
            "initial_position_ml": {k:s["ml"] for k,s in returned["initial"].items()},
            "parked_position_ml": {k:s["ml"] for k,s in returned["final"].items()},
            "parked_minus_initial_ml": returned["change_ml"]}


def main(journal, output):
    design, freeze = read_json(RECORD/"design.json"), read_json(RECORD/"forecasts.json")
    for filename, expected in freeze["input_sha256"].items():
        if hashlib.sha256((RECORD/filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Changed frozen input: {filename}")
    events = [json.loads(line) for line in journal.read_text().splitlines()]
    segments = trial_segments(events)
    photos = {e["label"]:e for e in events if e["event"] == "image"}
    attempts = [score_attempt(i, item, design["scenarios"][item["scenario"]], freeze,
                              segments.get(i, ({}, [])), photos) for i,item in enumerate(design["order"])]
    conditions = [program_score([r for r in attempts if r["head"]==h and r["scenario"]==case])
                  for h in "AB" for case in design["scenarios"]]
    first_wet = next((e for e in events if e["event"]=="tx" and e["command"].startswith(("pump ","flow "))), {})
    measured = [r for r in attempts if r["measured"]]
    blanks = stationary_pairs(events)
    paired = [r["near_dose_ml"] - r["far_dose_ml"] for r in measured
              if r["eligible"] and r["near_dose_ml"] is not None and r["far_dose_ml"] is not None]
    summary = {
        "unit":"Concentrate volume indicated by the printed cup, nominal mL; error is measured dose minus forecast.",
        "design_revision":DESIGN_GIT, "forecasts_revision":FORECAST_GIT, "freeze_utc":freeze["utc"],
        "validation_journal_sha256":hashlib.sha256(journal.read_bytes()).hexdigest(),
        "first_wet_position_utc":first_wet.get("utc"),
        "first_reserved_flow_utc":next((r["first_flow_utc"] for r in attempts if r["first_flow_utc"]),None),
        "planned":len(attempts), "forecast_logged":len(segments), "measured":len(measured),
        "eligible":sum(r["eligible"] for r in attempts),
        "passed_conditions":sum(r["both_pass"] for r in conditions),
        "all_conditions_pass":all(r["both_pass"] for r in conditions),
        "failed_conditions":[[r["head"],r["scenario"]] for r in conditions if not r["both_pass"]],
        "maximum_abs_stage_timing_error_ms":max((r["max_abs_stage_timing_error_ms"] for r in measured),default=None),
        "closure_error_ms":[r["observed_stop_ms"]-r["expected_stop_ms"] for r in measured],
        "aggregate":{scope:{site:aggregate([r for r in attempts if scope=="both" or r["head"]==scope],site)
                            for site in SITES} for scope in ["both","A","B"]},
        "near_minus_far_dose_ml": describe(paired),
        "adjacent_stationary_changes": {site: describe([r[site+"_change_ml"] for r in blanks
                                                        if r[site+"_change_ml"] is not None]) for site in SITES},
    }
    output.mkdir(parents=True, exist_ok=True)
    save_csv(output/"attempts.csv",attempts)
    save_csv(output/"by-program.csv",conditions)
    save_csv(output/"by-block.csv", block_scores(attempts))
    if blanks:
        save_csv(output/"stationary.csv", blanks)
    save_json(output/"scores.json",summary)
    save_json(output/"contrasts.json",contrasts(attempts,freeze["forecasts"]))
    park_log = journal.parent/"park.jsonl"
    if park_log.is_file() and (journal.parent/"qualify.jsonl").is_file() and '"station_return"' in park_log.read_text():
        save_json(output/"bench-state.json", bench_state(journal.parent))
    print(f"{len(measured)} photographed pours, {summary['eligible']} matched and prospective; "
          f"{summary['passed_conditions']} of {len(conditions)} conditions pass.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--journal", type=Path, default=RECORD/"logs/validation.jsonl")
    p.add_argument("--out", type=Path, default=RECORD/"results")
    args = p.parse_args()
    main(args.journal, args.out)
