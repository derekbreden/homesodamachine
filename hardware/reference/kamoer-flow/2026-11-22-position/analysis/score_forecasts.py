#!/usr/bin/env python3
"""Score frozen pump forecasts from the prospective width and pause journals."""

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from statistics import mean, median, stdev


def spread(values):
    return {"n": len(values), "mean": mean(values) if values else None,
            "min": min(values, default=None), "max": max(values, default=None),
            "sample_sd": stdev(values) if len(values) > 1 else None}


def block_name(stem):
    match = re.match(r"(width|gap)-(\d+)", stem)
    return match[0] if match else stem


def read_log(file, payload):
    """Keep each attempt, including acknowledged motion without a settled endpoint."""
    attempts, incomplete_lines = [], []
    current, command = None, None
    for line_no, line in enumerate(payload.splitlines(), 1):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            incomplete_lines.append(line_no)
            continue
        event = e["event"]
        if event == "pre":
            current = {"id": f"{file.name}#{line_no}", "file": file.name, "block": block_name(file.stem),
                       "label": e["label"], "utc": e["utc"], "pre": e["reading"], "commands": []}
            attempts.append(current)
            command = None
        elif current is not None and event in ("prediction", "observation"):
            current[event] = e
        elif current is not None and event == "tx" and e["command"].startswith("pump "):
            _, head, width = e["command"].split()
            command = {"tx_ns": e["mono_ns"], "head": head.upper(), "width_ms": int(width)}
            current["commands"].append(command)
        elif command is not None and event == "rx":
            start = re.search(r"pump ([AB]) at full for (\d+) ms", e["line"])
            done = re.search(r"pump ([AB]) done after (\d+) ms", e["line"])
            if start:
                command.update(start_ack_ns=e["mono_ns"], start_head=start[1], start_ms=int(start[2]))
            if done:
                command.update(done_ack_ns=e["mono_ns"], done_head=done[1], board_ms=int(done[2]))
        elif command is not None and event == "gate":
            if e["tx_ns"] != command["tx_ns"]:
                raise ValueError(f"Mismatched gate in {current['id']}")
            command.update({k: e[k] for k in ("start_ack_ns", "done_ack_ns", "board_ms")})
            command["gate_index"] = e["gate_index"]
        elif event == "session_end":
            current, command = None, None
    return attempts, incomplete_lines


def classify(block, prediction):
    if not prediction:
        return "unknown"
    if prediction["head"] is None:
        return "blank"
    if prediction["kind"] == "unseen_duration":
        return "width_after_idle" if block.startswith("qualification") else "width"
    if block.startswith("gap") and prediction["gate_ms"] == 100 and prediction["count"] == 8:
        return "gap"
    return "setup"


def measure(attempt, prior):
    p = attempt.get("prediction", {})
    o = attempt.get("observation", {})
    pre, post = attempt["pre"], o.get("post", {})
    commands = attempt["commands"]
    phase = classify(attempt["block"], p)
    r = {k: attempt[k] for k in ("id", "file", "block", "label", "utc")}
    r["physical_context"] = "uncertain_during_tube_and_wiring_change" if r["file"] == "gap-1b.jsonl" else "before_rewiring"
    r.update(phase=phase, kind=p.get("kind"), head=p.get("head"), pair=p.get("pair"),
             width_ms=p.get("gate_ms"), count=p.get("count"), off_ms=p.get("off_ms"),
             commands_sent=len(commands), acknowledged=sum("board_ms" in c for c in commands),
             gate_records=sum("gate_index" in c for c in commands), pre_ml=pre["nominal_ml"], pre_y=pre["right_y"],
             pre_reader=pre.get("reader", "broad"),
             predicted_ml=p.get("predicted_transfer_ml"), null_ml=p.get("null_predicted_transfer_ml"))
    if not p:
        status = "no_prediction"
    elif commands and min(c["tx_ns"] for c in commands) <= p["mono_ns"]:
        status = "prediction_after_command"
    elif any(c.get("head") != p["head"] or c.get("done_head") != p["head"] or c.get("start_head") != p["head"]
             or c.get("start_ms") != p["gate_ms"] or c.get("width_ms") != p["gate_ms"]
             or abs(c.get("board_ms", -100) - p["gate_ms"]) > 3 for c in commands):
        status = "incomplete_or_mismatched_receipt"
    elif p["head"] and not commands:
        status = "predicted_without_command"
    elif p["head"] and len(commands) != p["count"]:
        status = "incomplete_train"
    elif not o:
        status = "no_settled_observation"
    elif not all(v["ok"] for v in (pre, post)):
        status = "unresolved_camera_position"
    else:
        status = "complete"
    r["status"] = status
    intervals = {"done_ack_to_next_start_ack_ms": [], "tx_period_minus_previous_board_ms": []}
    for prev, nxt in zip(commands, commands[1:]):
        if "done_ack_ns" in prev and "start_ack_ns" in nxt:
            intervals["done_ack_to_next_start_ack_ms"].append((nxt["start_ack_ns"] - prev["done_ack_ns"]) / 1e6)
        if "board_ms" in prev:
            intervals["tx_period_minus_previous_board_ms"].append((nxt["tx_ns"] - prev["tx_ns"]) / 1e6 - prev["board_ms"])
    r.update(intervals, board_on_ms=sum(c.get("board_ms", 0) for c in commands))
    if commands:
        r["pre_image_to_first_write_s"] = (commands[0]["tx_ns"] - pre["pts_ns"]) / 1e9
    if o and commands and "done_ack_ns" in commands[-1]:
        r["last_done_to_post_image_s"] = (post["pts_ns"] - commands[-1]["done_ack_ns"]) / 1e9
    if phase in ("width", "width_after_idle", "gap"):
        fixed_null = prior["new_single_command_forecast"]["rates_ml_per_s"][p["head"]] * p["gate_ms"] * p["count"] / 1000
        if phase == "gap":
            preds = prior["new_pause_forecast"][p["head"]]["forecasts"]
            frozen = next(v["eight_100_ms_total_ml"] for v in preds if v["pause_ms"] == p["off_ms"])
        else:
            frozen = fixed_null
        if abs(r["predicted_ml"] - frozen) > 0.005001 or abs(r["null_ml"] - fixed_null) > 1e-8:
            raise ValueError(f"Journal prediction differs from frozen prior in {r['id']}")
    if o:
        cup_change = post["nominal_ml"] - pre["nominal_ml"]
        sign = -1 if p.get("head") == "A" else 1
        r.update(post_ml=post["nominal_ml"], post_y=post["right_y"], post_reader=post.get("reader", "broad"), signed_cup_change_ml=cup_change,
                 right_delta_px=post["right_y"] - pre["right_y"], left_delta_px=post["left_y"] - pre["left_y"])
        if p.get("head") and r["physical_context"] == "before_rewiring":
            observed = sign * cup_change
            if not math.isclose(observed, o["nominal_transfer_ml"], abs_tol=0.00051):
                raise ValueError(f"Optical observation does not match endpoints in {r['id']}")
            sides = {s: sign * (post["sightlines"][s]["nominal_ml"] - pre["sightlines"][s]["nominal_ml"])
                     for s in ("left", "right")}
            error, null_error = r["predicted_ml"] - observed, r["null_ml"] - observed
            r.update(observed_ml=observed, left_observed_ml=sides["left"], right_observed_ml=sides["right"],
                     error_ml=error, absolute_error_ml=abs(error), null_error_ml=null_error, null_absolute_error_ml=abs(null_error),
                     null_minus_prior_absolute_error_ml=abs(null_error) - abs(error), endpoint_error_px=post["right_y"] - p["predicted_right_y"])
    return r


def partition(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    return groups


def accuracy(rows):
    return {
        "n": len(rows),
        "starting_nominal_ml_range": [min(r["pre_ml"] for r in rows), max(r["pre_ml"] for r in rows)],
        "observed_ml": spread([r["observed_ml"] for r in rows]),
        "predicted_minus_observed_ml": spread([r["error_ml"] for r in rows]),
        "mean_absolute_error_ml": mean(r["absolute_error_ml"] for r in rows),
        "max_absolute_error_ml": max(r["absolute_error_ml"] for r in rows),
        "null_mean_absolute_error_ml": mean(r["null_absolute_error_ml"] for r in rows),
        "null_minus_prior_absolute_error_ml": spread([r["null_minus_prior_absolute_error_ml"] for r in rows]),
        "left_minus_right_measured_transfer_ml": spread([r["left_observed_ml"] - r["right_observed_ml"] for r in rows]),
        "seconds_from_last_stop_receipt_to_settled_image": spread([r["last_done_to_post_image_s"] for r in rows]),
    }


def grouped_accuracy(rows, *keys):
    return [dict(zip(keys, key), **accuracy(group)) for key, group in partition(rows, keys).items()]


def fit_local_rate(rows):
    return sum(r["board_on_ms"] * r["observed_ml"] for r in rows) * 1000 / sum(r["board_on_ms"]**2 for r in rows)


def transfer_widths(samples):
    result = {}
    for head in ("A", "B"):
        first = [r for r in samples if r["phase"] == "width" and r["block"] == "width-1" and r["head"] == head]
        later = [r for r in samples if r["phase"] == "width" and r["block"] != "width-1" and r["head"] == head]
        if not first:
            continue
        rate = fit_local_rate(first)
        errors = [rate * r["board_on_ms"] / 1000 - r["observed_ml"] for r in later]
        result[head] = {
            "first_block_rate_ml_per_s": rate,
            "fit_ids": [r["id"] for r in first], "held_out_ids": [r["id"] for r in later],
            "later_block_errors_ml": spread(errors), "later_block_absolute_error_ml": spread(list(map(abs, errors))),
            "later_per_block": [dict(block=block, starting_cup_ml=spread([r["pre_ml"] for r in group]),
                                     absolute_error_ml=spread([abs(rate * r["board_on_ms"] / 1000 - r["observed_ml"]) for r in group]))
                                for (block,), group in partition(later, ("block",)).items()],
        }
    return result


def freeze_local(rows, prior, destination, inventory):
    heads = {}
    for head in ("A", "B"):
        selected = [r for r in rows if r["head"] == head and r["phase"] in ("width", "width_after_idle") and r["status"] == "complete"]
        rate = fit_local_rate(selected)
        old_rate = prior["new_single_command_forecast"]["rates_ml_per_s"][head]
        ratio = rate / old_rate
        values = {}
        for old in prior["new_pause_forecast"][head]["forecasts"]:
            # Match the predeclared doses that the journal stores for the primary comparison.
            announced = round(old["eight_100_ms_total_ml"], 2)
            values[old["pause_ms"]] = {"null_ml": 0.8 * rate, "prior_shape_ml": ratio * announced}
        heads[head] = {
            "fit_inputs": [{"id": r["id"], "label": r["label"], "board_ms": r["board_on_ms"], "observed_ml": r["observed_ml"]} for r in selected],
            "local_rate_ml_per_s": rate, "archive_announced_rate_ml_per_s": old_rate, "rate_ratio": ratio,
            "eight_100_ms_by_pause_ms": values,
            "short_minus_long_ml": values[50]["prior_shape_ml"] - values[1100]["prior_shape_ml"],
            "null_short_minus_long_ml": values[50]["null_ml"] - values[1100]["null_ml"],
        }
    record = {
        "frozen_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "purpose": "Predict the new pause experiment from previously completed isolated qualification and width shots.",
        "method": "Least squares through zero per head, using directed optical dose and board-reported seconds for every completed isolated test shot, including the first shot after idle. Both announced archive forecasts scale by the ratio of this rate to the announced archive rate.",
        "width_journal_hashes_at_freeze": inventory, "heads": heads,
    }
    with destination.open("x") as stream:
        stream.write(json.dumps(record, indent=2, allow_nan=False) + "\n")


def attach_local(rows, local):
    for r in rows:
        if r["phase"] != "gap" or r["status"] != "complete" or r["physical_context"] != "before_rewiring":
            continue
        if datetime.fromisoformat(r["utc"]) <= datetime.fromisoformat(local["frozen_utc"]):
            raise ValueError(f"Local model was not frozen before {r['label']}")
        forecast = local["heads"][r["head"]]["eight_100_ms_by_pause_ms"][str(r["off_ms"])]
        r["local_predicted_ml"] = forecast["prior_shape_ml"]
        r["local_null_ml"] = forecast["null_ml"]
        r["local_error_ml"] = r["local_predicted_ml"] - r["observed_ml"]
        r["local_null_error_ml"] = r["local_null_ml"] - r["observed_ml"]
        r["local_null_minus_prior_absolute_error_ml"] = abs(r["local_null_error_ml"]) - abs(r["local_error_ml"])


def match_gaps(gaps, reference_ms):
    """Contrast each shorter pause with a reference on the same head in the same block."""
    block_rows = []
    for (block, head), rows in partition(gaps, ("block", "head")).items():
        by_gap = partition(rows, ("off_ms",))
        reference = by_gap.get((reference_ms,))
        if not reference:
            continue
        for (off_ms,), test in by_gap.items():
            if off_ms >= reference_ms:
                continue
            def diff(field):
                return mean(r[field] for r in test) - mean(r[field] for r in reference)
            observed, expected = diff("observed_ml"), diff("predicted_ml")
            comparison = dict(block=block, head=head, off_ms=off_ms, reference_ms=reference_ms,
                                   test_ids=[r["id"] for r in test], reference_ids=[r["id"] for r in reference],
                                   starting_cup_ml_difference=diff("pre_ml"), observed_difference_ml=observed,
                                   left_sightline_difference_ml=diff("left_observed_ml"), right_sightline_difference_ml=diff("right_observed_ml"),
                                   predicted_difference_ml=expected, null_difference_ml=diff("null_ml"),
                                   prior_contrast_error_ml=expected - observed)
            if "local_predicted_ml" in test[0]:
                comparison["local_predicted_difference_ml"] = diff("local_predicted_ml")
            block_rows.append(comparison)
    across = []
    for (head, pause), matched in partition(block_rows, ("head", "off_ms")).items():
        observed = [r["observed_difference_ml"] for r in matched]
        result = dict(head=head, off_ms=pause, reference_ms=reference_ms, blocks_with_more_at_shorter_pause=sum(v > 0 for v in observed),
                      observed_difference_across_blocks_ml=spread(observed),
                      predicted_difference_ml=mean(r["predicted_difference_ml"] for r in matched),
                      null_mean_abs_contrast_error_ml=mean(map(abs, observed)),
                      prior_mean_abs_contrast_error_ml=mean(abs(r["prior_contrast_error_ml"]) for r in matched))
        if "local_predicted_difference_ml" in matched[0]:
            result["local_predicted_difference_ml"] = mean(r["local_predicted_difference_ml"] for r in matched)
            result["local_mean_abs_contrast_error_ml"] = mean(abs(r["local_predicted_difference_ml"] - r["observed_difference_ml"]) for r in matched)
        across.append(result)
    return {"block_pairs": block_rows, "across_blocks": across}


def match_heads(rows):
    pairs = []
    for (block, pair, width, off), group in partition(rows, ("block", "pair", "width_ms", "off_ms")).items():
        heads = partition(group, ("head",))
        if not all((h,) in heads for h in ("A", "B")):
            continue
        def difference(key):
            return mean(r[key] for r in heads[("B",)]) - mean(r[key] for r in heads[("A",)])
        pairs.append(dict(block=block, pair=pair, width_ms=width, off_ms=off, observed_B_minus_A_ml=difference("observed_ml"),
                          predicted_B_minus_A_ml=difference("predicted_ml"), starting_cup_B_minus_A_ml=difference("pre_ml")))
    return pairs


def summarize(rows, inventory):
    earlier = [r for r in rows if r["physical_context"] == "before_rewiring"]
    samples = [r for r in earlier if r["phase"] in ("width", "width_after_idle", "gap") and r["status"] == "complete"]
    blanks = [r for r in earlier if r["phase"] == "blank" and r["status"] == "complete"]
    gaps = [r for r in samples if r["phase"] == "gap"]
    acknowledged = [r for r in earlier if r["phase"] == "gap" and r["acknowledged"] == r["count"]]
    timing = []
    for (off,), group in partition(acknowledged, ("off_ms",)).items():
        summary = {"off_ms": off, "acknowledged_trains": len(group), "optically_scored_trains": sum(r["status"] == "complete" for r in group)}
        for field in ("done_ack_to_next_start_ack_ms", "tx_period_minus_previous_board_ms"):
            times = [v for r in group for v in r[field]]
            summary[field] = dict(spread(times), median=median(times))
        timing.append(summary)
    scaled = {}
    for title, keys in (("by_head", ("head",)), ("by_setting", ("head", "off_ms")), ("by_block", ("head", "block"))):
        groups = []
        for key, group in partition([r for r in gaps if "local_error_ml" in r], keys).items():
            groups.append(dict(zip(keys, key), n=len(group),
                               mean_error_ml=mean(r["local_error_ml"] for r in group),
                               mean_abs_error_ml=mean(abs(r["local_error_ml"]) for r in group),
                               null_mean_abs_error_ml=mean(abs(r["local_null_error_ml"]) for r in group),
                               null_minus_prior_absolute_error_ml=spread([r["local_null_minus_prior_absolute_error_ml"] for r in group])))
        scaled[title] = groups
    return {
        "physical_context": "On the scored observations, A emptied the cup and B refilled it. Derek reported that a pump had fallen at an unknown point. The rate change has no isolated physical cause in these observations. The gap-1b-002-post camera window already shows the rearranged tubes. The full gap-1b journal is retained as a transition record and contributes no dose, error or timing estimate in this cohort. Rewired confirmation and validation use separate records.",
        "camera_transition": {"camera_source": "scene-transitions.csv", "earlier_check_anchor_utc": "08:02:53.666",
                              "sustained_post_reset_anchor_first_utc": "08:05:56.666",
                              "interpretation": "Dry-region appearance in the one-second bins changed after the last scored pause result. The pump fall and wiring change lack independent timestamps."},
        "method": {
            "eligible": "Only the qualification, randomized width and pause journals are read. Frozen optical-volume predictions must precede command transmission and match the earlier archive model to journal rounding. Relocations, blanks and interrupted attempts are reported separately.",
            "sign": "Positive transfer is withdrawal on A or refill on B. Positive error means the model predicted more than the observed delivery. Positive null-minus-prior absolute error favors the pause-sensitive forecast.",
            "precision": "The primary volume is the mean of the two printed-cup sightlines. Individual sightline changes are in the trial CSV. Camera blanks use the observed signed change in cup level. Vessel graduation tolerance is unknown.",
            "groups": "Width qualification indexes the first shot on each head after an approximately hour-long idle. Each completed trial contributes one settled dose. Block-level contrasts keep repeats and head direction together and report differences in starting fill. Numbers following a block designate the planned filling/order block; filename suffixes retain retries.",
            "timing": "Actual timing is measured from host command and receipt times. The first gap estimate uses completion receipt to next start receipt. A second subtracts board-reported on-time from consecutive host writes. The board reports on-time in integer milliseconds.",
            "uncertainty": "Ranges and sample SD describe the observed trial or matched-block variation. Different initial fills, the same two heads and shared cup calibration limit inference to this apparatus. The pulses and the sightlines within a train are not experimental replicates.",
        },
        "logs": inventory,
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "unscored_incomplete": [{k: r.get(k) for k in ("id", "label", "phase", "kind", "head", "width_ms", "off_ms", "commands_sent", "acknowledged", "gate_records", "status")} for r in rows if r["status"] != "complete"],
        "excluded_transition_records": [{k: r.get(k) for k in ("id", "label", "kind", "head", "commands_sent", "acknowledged", "status", "physical_context", "pre_ml", "post_ml", "signed_cup_change_ml")} for r in rows if r["physical_context"] != "before_rewiring"],
        "blank_cup_change_ml": spread([r["signed_cup_change_ml"] for r in blanks]),
        "by_phase_and_head": grouped_accuracy(samples, "phase", "head"),
        "by_setting": grouped_accuracy(samples, "phase", "head", "width_ms", "off_ms"),
        "by_block_and_head": grouped_accuracy(samples, "phase", "block", "head"),
        "warm_width_first_block_predicts_later": transfer_widths(samples),
        "matched_B_minus_A": match_heads(samples),
        "pause_coverage": [{"block": f"gap-{n}", "head": head,
                            "observed_ms": [g for g in (50, 150, 450, 1100) if any(r["block"] == f"gap-{n}" and r["head"] == head and r["off_ms"] == g for r in gaps)],
                            "unobserved_ms": [g for g in (50, 150, 450, 1100) if not any(r["block"] == f"gap-{n}" and r["head"] == head and r["off_ms"] == g for r in gaps)]}
                           for n in (1, 2, 3, 4) for head in ("A", "B")],
        "primary_short_vs_longest_pause": match_gaps(gaps, 1100),
        "available_same_head_pause_contrast": match_gaps(gaps, 450),
        "locally_rescaled_frozen_forecasts": scaled,
        "pause_timing": timing,
    }


def draw_figure(rows, summary, prior, local, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    rows = [r for r in rows if r["physical_context"] == "before_rewiring"]
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.3), sharey="row")
    fig.subplots_adjust(left=.09, right=.975, top=.86, bottom=.16, hspace=.43, wspace=.09)
    fig.suptitle("Timed Diet Cola delivery before rewiring", x=.09, y=.97, ha="left", fontsize=18, weight="bold")
    fig.text(.09, .925, "Each marker is a settled camera reading. A pump fell at an unknown point. Three pulse trains have scored doses.", fontsize=10.5)
    fig.text(.09, .896, "The current-session line uses the first width block above and all isolated shots below.", fontsize=9.5)
    archive, refit, data = "#566171", "#a14c21", "#006d77"
    markers = ["o", "s", "^", "D"]
    for i, head in enumerate(("A", "B")):
        top, bottom = axes[:, i]
        top.set_title(f"Head {head}  ·  {'withdrawal' if head == 'A' else 'refill'}", loc="left", fontsize=13, weight="bold")
        width_rows = [r for r in rows if r["head"] == head and r["status"] == "complete" and r["phase"] == "width"]
        for (block,), group in partition(width_rows, ("block",)).items():
            n = int(block.split("-")[1])
            top.scatter([r["width_ms"] / 1000 for r in group], [r["observed_ml"] for r in group], marker=markers[n-1],
                        s=45, facecolors="none", edgecolors=data, linewidths=1.35, zorder=5)
        idle = [r for r in rows if r["head"] == head and r["phase"] == "width_after_idle" and r["status"] == "complete"]
        top.scatter([r["width_ms"]/1000 for r in idle], [r["observed_ml"] for r in idle], marker="x", c="#1f2429", s=35, zorder=6)
        old = prior["new_single_command_forecast"]["rates_ml_per_s"][head]
        first = summary["warm_width_first_block_predicts_later"][head]["first_block_rate_ml_per_s"]
        top.plot([0, 2.3], [0, 2.3*old], color=archive, lw=1.6)
        top.plot([0, 2.3], [0, 2.3*first], color=refit, lw=1.6)
        top.set(xticks=[0, .375, .75, 1.5, 2.25], xlabel="Isolated gate duration (s)", ylim=(0, 36))
        top.set_xticklabels(["0", "0.375", "0.75", "1.5", "2.25"])

        pauses = [50, 150, 450, 1100]
        old_gap = {r["pause_ms"]: r["eight_100_ms_total_ml"] for r in prior["new_pause_forecast"][head]["forecasts"]}
        current = local["heads"][head]["eight_100_ms_by_pause_ms"]
        bottom.plot(pauses, [old_gap[p] for p in pauses], color=archive, lw=1.6)
        bottom.plot(pauses, [old * .8] * len(pauses), color=archive, ls=":", lw=1.7)
        bottom.plot(pauses, [current[str(p)]["prior_shape_ml"] for p in pauses], color=refit, lw=1.6)
        bottom.plot(pauses, [current[str(p)]["null_ml"] for p in pauses], color=refit, ls=":", lw=1.7)
        gap_rows = [r for r in rows if r["head"] == head and r["status"] == "complete" and r["phase"] == "gap"]
        for (block,), group in partition(gap_rows, ("block",)).items():
            n = int(block.split("-")[1])
            ordered = sorted(group, key=lambda r: r["off_ms"])
            bottom.scatter([r["off_ms"] for r in ordered], [r["observed_ml"] for r in ordered], marker=markers[(n-1)%4],
                           s=45, facecolors="none", edgecolors=data, linewidths=1.35, zorder=5)
        bottom.set(xscale="log", xlabel="Pause between 100 ms gates (ms)", xlim=(40, 1400), xticks=pauses)
        bottom.set_xticklabels([str(g) for g in pauses])
        bottom.minorticks_off()
        for ax in (top, bottom):
            ax.grid(axis="y", color="#dce1e4", lw=.8)
            ax.set_axisbelow(True)
            ax.spines[["right", "top"]].set_visible(False)
    axes[0, 0].set_ylabel("One gate · syrup (nominal mL)")
    axes[1, 0].set_ylabel("Eight gates · syrup (nominal mL)")
    handles = [Line2D([], [], color=archive, label="Previous calibration"),
               Line2D([], [], color=refit, label="Current-session calibration"),
               Line2D([], [], color="#566171", ls=":", label="On-time-only pause forecast"),
               Line2D([], [], color="#1f2429", ls="none", marker="x", label="First shot after idle")]
    shown_blocks = {int(r["block"].split("-")[1]) for r in rows if r["phase"] in ("width", "gap") and r["status"] == "complete"}
    handles.extend(Line2D([], [], color=data, ls="none", marker=m, markerfacecolor="none", label=f"Block {i+1}") for i,m in enumerate(markers) if i+1 in shown_blocks)
    fig.legend(handles=handles, ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(.51, .012), fontsize=9.2)
    fig.savefig(out, dpi=160, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journals", type=Path)
    parser.add_argument("--prior", type=Path, default=Path(__file__).with_name("archive_model.json"))
    parser.add_argument("--local", type=Path, default=Path(__file__).with_name("local-gap-forecast.json"))
    parser.add_argument("--freeze-local", action="store_true", help="Write the secondary prediction once using only qualification and width journals.")
    parser.add_argument("--figure", action="store_true", help="Render the width and pause comparisons with Matplotlib.")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    prior = json.loads(args.prior.read_text())
    attempts, inventory = [], []
    for file in sorted(args.journals.glob("*.jsonl")):
        if not re.fullmatch(r"(?:qualification-a|width-[123][a-z0-9-]*|gap-[a-zA-Z0-9-]+)", file.stem):
            continue
        if args.freeze_local and file.stem.startswith("gap-"):
            continue
        payload = file.read_bytes()
        records, partial = read_log(file, payload)
        attempts.extend(records)
        inventory.append({"file": file.name, "bytes_read": len(payload), "sha256": sha256(payload).hexdigest(),
                          "attempts": len(records), "unreadable_lines": partial})
    rows = sorted((measure(a, prior) for a in attempts), key=lambda r: r["utc"])
    if args.freeze_local:
        freeze_local(rows, prior, args.local, inventory)
        return
    local = json.loads(args.local.read_text()) if args.local.is_file() else None
    if local:
        attach_local(rows, local)
    summary = summarize(rows, inventory)
    if local:
        summary["local_forecast_frozen_utc"] = local["frozen_utc"]
        summary["first_pause_trial_pre_utc"] = next((r["utc"] for r in rows if r["phase"] == "gap" and r["commands_sent"]), None)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "forecast_scores.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    with (args.out / "forecast_trials.csv").open("w", newline="") as stream:
        columns = dict.fromkeys(k for r in rows for k in r)
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, separators=(",", ":")) if isinstance(v, list) else v for k, v in row.items()})
    if args.figure:
        draw_figure(rows, summary, prior, local, args.out / "forecast_validation.png")


if __name__ == "__main__":
    main()
