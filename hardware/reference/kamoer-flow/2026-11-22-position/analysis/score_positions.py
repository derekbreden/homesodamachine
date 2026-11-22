#!/usr/bin/env python3
"""Score each predeclared destination against its photographed liquid contact after rewiring."""

import argparse
import csv
import json
import math
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from statistics import mean, median, stdev


def describe(values):
    return {"n": len(values), "mean": mean(values) if values else None, "median": median(values) if values else None,
            "min": min(values, default=None), "max": max(values, default=None), "sample_sd": stdev(values) if len(values) > 1 else None}


def group(rows, keys):
    sets = defaultdict(list)
    for row in rows:
        sets[tuple(row[k] for k in keys)].append(row)
    return sets


def certified(actual, expected, label):
    if not math.isclose(actual, expected, abs_tol=1e-6):
        raise ValueError(f"{label}: expected {expected}, recorded {actual}")


def read_log(path):
    events = []
    data = path.read_bytes()
    for line in data.splitlines():
        events.append(json.loads(line))
    points, trials, halts = {}, {}, []
    for e in events:
        typ, label = e["event"], e.get("label", "")
        if typ == "endpoint":
            points[label] = e
            label, _ = label.rsplit("-", 1)
            trials.setdefault(label, {"file": path.name, "label": label, "predictions": {}, "gates": {}, "events": {}})
        elif typ == "prediction":
            trials[label]["predictions"][e["phase"]] = e
        elif typ == "gate":
            trials[label]["gates"][e["phase"]] = e
        elif typ in ("first_score", "final_score", "correction_score", "blank_start", "blank"):
            trials[label]["events"][typ] = e
        elif typ == "halt":
            halts.append({"file": path.name, "utc": e["utc"], "reason": e["reason"]})
    info = {"file": path.name, "sha256": sha256(data).hexdigest(), "journal_ended": bool(events and events[-1]["event"] == "session_end")}
    return list(trials.values()), points, halts, info


def contact(point):
    return point["readings"]["left_clear"]["delta_from_reference_px"]


def optical_check(pre, post, design):
    a, b = pre["readings"], post["readings"]
    primary_move = contact(post) - contact(pre)
    result = {}
    for site, scale in design["relative_stretch"].items():
        if a[site].get("ok") and b[site].get("ok"):
            equiv = (b[site]["delta_from_reference_px"] - a[site]["delta_from_reference_px"]) / scale
            result[site + "_minus_primary_motion_px"] = equiv - primary_move
    for side in ("left", "right"):
        if a.get("dry_ink") and b.get("dry_ink"):
            result[side + "_dry_mark_motion_px"] = b["dry_ink"][side]["dy"] - a["dry_ink"][side]["dy"]
    result["left_contact_patch_mad_at_post_px"] = b["left_clear"]["patch_mad_px"]
    result["left_contact_patches_at_post"] = b["left_clear"]["patches"]
    return result


def evaluate(trial, points, design):
    label = trial["label"]
    index = int(label.rsplit("-", 1)[1])
    target, policy = design["trials"][index]
    row = {"file": trial["file"], "label": label, "design_index": index, "policy": policy, "target_px": target}
    pred, gates, es = (trial[k] for k in ("predictions", "gates", "events"))
    pre = points[label + "-pre"]
    row["pre_image_pts_ns"] = pre["pts_ns"]
    if pre["readings"]["left_clear"].get("ok"):
        row["start_px"] = contact(pre)
    if policy == "idle":
        if "blank" in es:
            end = points[label + "-hold"]
            value = contact(end) - contact(pre)
            certified(value, es["blank"]["drift_px"], label)
            row.update(status="blank", blank_drift_px=value, blank_image_interval_s=(end["pts_ns"] - pre["pts_ns"]) / 1e9,
                       **optical_check(pre, end, design))
        else:
            row["status"] = "blank_incomplete"
        return row

    for phase, p in pred.items():
        start = contact(points[p["pre_endpoint"]])
        certified(start, p["pre_px"], label)
        certified(target, p["target_px"], label)
        certified(start + design["pixels_per_second"][p["channel"]] * p["ms"] / 1000, p["predicted_px"], label)
        if policy != p["policy"]:
            raise ValueError(f"{label}: policy changed")
        row[phase + "_head"] = p["channel"]
        row[phase + "_requested_gate_ms"] = p["ms"]
        row[phase + "_prediction_utc"] = p["utc"]
        row[phase + "_predicted_px"] = p["predicted_px"]
        if phase in gates:
            g = gates[phase]
            if p["mono_ns"] >= g["tx_ns"] or g["channel"] != p["channel"] or abs(g["board_ms"] - p["ms"]) > 3:
                raise ValueError(f"{label}/{phase}: invalid prediction/receipt order or command")
            row[phase + "_board_ms"] = g["board_ms"]
            row[phase + "_tx_to_start_ack_ms"] = (g["start_ack_ns"] - g["tx_ns"]) / 1e6
            row[phase + "_tx_ns"], row[phase + "_done_ack_ns"] = g["tx_ns"], g["done_ack_ns"]
    for event, endpoint, prefix in (("first_score", "first", "first"), ("correction_score", "corrected", "after_correction"), ("final_score", "final", "final")):
        if event not in es:
            continue
        post = points[label + "-" + endpoint]
        actual = contact(post)
        certified(actual, es[event]["observed_px"], label)
        certified(actual - target, es[event]["error_px"], label)
        phase = "correct" if "correct" in gates and event != "first_score" else "first"
        g = gates[phase]
        row[prefix + "_px"] = actual
        row[prefix + "_error_px"] = actual - target
        row[prefix + "_absolute_error_px"] = abs(actual - target)
        row[prefix + "_image_after_stop_s"] = (post["pts_ns"] - g["done_ack_ns"]) / 1e9
        if event == "first_score":
            row.update(optical_check(pre, post, design))
            row["first_observed_minus_predicted_px"] = actual - pred["first"]["predicted_px"]
            row["first_x980_signed_motion_px"] = actual - contact(pre)
            cup_sign = -1 if row["first_head"] == "A" else 1
            for site in ("right", "projected_left"):
                pre_ml = pre["readings"].get(site, {}).get("nominal_ml")
                post_ml = post["readings"].get(site, {}).get("nominal_ml")
                if pre_ml is not None and post_ml is not None:
                    row[site + "_before_ml"] = pre_ml
                    row[site + "_after_first_ml"] = post_ml
                    row[site + "_signed_cup_change_ml"] = post_ml - pre_ml
                    row[site + "_directed_dose_ml"] = cup_sign * (post_ml - pre_ml)
    row["correction_commands"] = int("correct" in gates)
    row["status"] = ("scored_final" if "final_score" in es else "scored_first_only" if "first_score" in es
                     else "driven_without_score" if gates else "no_acknowledged_gate")
    if row["status"] == "scored_final":
        expected_correction = policy == "correct" and abs(row["first_error_px"]) >= design["correction_deadband_px"]
        if expected_correction != bool(row["correction_commands"]):
            raise ValueError(f"{label}: actual correction differs from planned policy")
        last_measured = row.get("after_correction_px", row["first_px"])
        row["passive_motion_early_to_final_px"] = row["final_px"] - last_measured
        row["first_absolute_minus_final_absolute_px"] = row["first_absolute_error_px"] - row["final_absolute_error_px"]
    return row


def summaries(rows, keys):
    outputs = []
    for key, batch in group(rows, keys).items():
        stages = {}
        for stage in ("first", "after_correction", "final"):
            field = stage + "_error_px"
            accepted = [r for r in batch if field in r]
            if accepted:
                stages[stage] = {"signed_error_px": describe([r[field] for r in accepted]),
                                 "absolute_error_px": describe([abs(r[field]) for r in accepted]),
                                 "image_seconds_after_last_stop": describe([r[stage + "_image_after_stop_s"] for r in accepted])}
        outputs.append(dict(zip(keys, key), outcomes=len(batch), applied_corrections=sum(r["correction_commands"] for r in batch),
                            distance_requested_px=describe([abs(r["target_px"] - r["start_px"]) for r in batch]), **stages))
    return outputs


def fit_delivery(rows):
    outputs = {}
    for (head,), trials in group(rows, ("first_head",)).items():
        head_fits = {"observed_board_ms": [r["first_board_ms"] for r in trials],
                     "observed_board_ms_range": [min(r["first_board_ms"] for r in trials), max(r["first_board_ms"] for r in trials)]}
        for field in ("first_x980_signed_motion_px", "right_signed_cup_change_ml", "projected_left_signed_cup_change_ml"):
            sample = [r for r in trials if field in r]
            if not sample:
                continue
            ts = [r["first_board_ms"] / 1000 for r in sample]
            ys = [r[field] for r in sample]
            q = sum(t*v for t,v in zip(ts, ys)) / sum(t*t for t in ts)
            head_fits[field] = {"n": len(sample), "trial_labels": [r["label"] for r in sample],
                                "signed_units_per_second": q, "directional_magnitude_per_second": abs(q),
                                "per_trial_signed_change": ys, "absolute_fit_residual": describe([abs(q*t - v) for t,v in zip(ts, ys)])}
        outputs[head] = head_fits
    return {"method": "Descriptive least squares through zero for first target shots, using acknowledged board-on seconds. The x980 contact is a signed camera coordinate. Signed cup mL decrease on withdrawal. The direct right ruler and the projected left ruler each use their own available paired endpoints. The projected left contact interpolates between two clear regions across printed ink. Cup graduation accuracy is unknown.",
            "heads": outputs}


def fit_volume_scale(rows):
    fits = {}
    for site in ("right", "projected_left"):
        field = site + "_signed_cup_change_ml"
        accepted = [r for r in rows if field in r and r["first_x980_signed_motion_px"]]
        if not accepted:
            continue
        def slope(subset):
            return -sum(r["first_x980_signed_motion_px"] * r[field] for r in subset) / sum(r["first_x980_signed_motion_px"]**2 for r in subset)
        q = slope(accepted)
        destinations = {r["target_px"] for r in accepted}
        fits[site] = {
            "n": len(accepted), "nominal_ml_per_downward_pixel_withdrawn": q,
            "by_head": {h: slope(batch) for (h,), batch in group(accepted, ("first_head",)).items()},
            "per_trial_nominal_ml_per_pixel": describe([-r[field]/r["first_x980_signed_motion_px"] for r in accepted]),
            "leave_one_destination_out_ml_per_pixel": describe([slope([r for r in accepted if r["target_px"] != t]) for t in destinations]) if len(destinations) > 1 else None,
            "absolute_calibration_residual_ml": describe([abs(r[field] + q*r["first_x980_signed_motion_px"]) for r in accepted]),
        }
    return {"method": "Direct through-zero regression of nominal mL withdrawn against downward displacement of the left clear contact, pooling both directions. The two local rulers have common cup-manufacturing and optical uncertainty. Per-trial ratios, residuals and omitted-destination sensitivity describe agreement within these observations.",
            "scales": fits}


def timing_summary(rows, folder):
    """Time visible upper-rim motion from the imaged trajectory at each independent viewing region."""
    gates = []
    for row in rows:
        for phase in ("first", "correct"):
            if phase + "_tx_ns" not in row:
                continue
            label = row["label"] + "-" + phase
            metadata = folder / (label + ".json")
            if not metadata.is_file():
                continue
            meta = json.loads(metadata.read_text())
            head = row[phase + "_head"]
            sign = 1 if head == "A" else -1
            gate = {"label": label, "head": head, "phase": phase, "board_ms": row[phase + "_board_ms"], "trajectory_file": metadata.name}
            if meta["gate"]["tx_ns"] != row[phase + "_tx_ns"]:
                raise ValueError(f"{label}: optical record belongs to a different gate")
            for view, summary in meta["sightlines"].items():
                path = folder / (label + "-" + view + ".csv")
                with path.open() as f:
                    trace = [(float(v["from_tx_s"]), float(v["offset_from_pre_px"])) for v in csv.DictReader(f)]
                quiet = [abs(y) for t,y in trace if -.65 <= t < -.03]
                if not quiet:
                    continue
                threshold = max(1.0, max(quiet) + .25)
                sustained = 3 if view == "native" else 2
                late = summary.get("done_plus_4s_px")
                obs = {"quiet_to_motion_threshold_px": threshold, "frame_spacing_ms": summary["median_sensor_dt_ms"],
                       "at_done_px": summary["at_done_px"], "done_plus_4s_px": late}
                if late is not None:
                    obs["additional_directional_motion_done_to_4s_px"] = sign * (late - summary["at_done_px"])
                if late is not None and sign * late >= 3:
                    for i in range(len(trace) - sustained + 1):
                        if 0 <= trace[i][0] <= 1.5 and all(sign*y > threshold for _,y in trace[i:i+sustained]):
                            obs["first_sustained_response_after_tx_s"] = trace[i][0]
                            break
                gate[view] = obs
            gates.append(gate)
    primary = [g for g in gates if g["phase"] == "first"]
    qualified = [g for g in primary if all("first_sustained_response_after_tx_s" in g.get(v,{}) for v in ("native","preview"))]
    by_head = {}
    for (head,), subset in group(qualified, ("head",)).items():
        by_head[head] = {
            v: {"first_sustained_response_after_tx_s": describe([g[v]["first_sustained_response_after_tx_s"] for g in subset]),
                "additional_directional_motion_done_to_4s_px": describe([g[v]["additional_directional_motion_done_to_4s_px"] for g in subset])}
            for v in ("native", "preview")
        }
    return {"source": "Gate-aligned upper-rim optical tracks at native-row spacing and a second camera region on the preview. Each uses the same sensor, with separate visible regions. Both are distinct from the x980 target contact.",
            "definition": "Record the first sustained displacement in the driven direction above the larger of one pixel or the largest absolute pre-command displacement plus a quarter pixel. The native record requires three successive frames and the preview two. Include gates in head summaries only when both regions reach a directional three-pixel movement by four seconds after the stop and each crosses its threshold. These are visible threshold-crossing times measured from the host write. Sampling and serial timing limit inference to shaft motion.",
            "first_gate_records": len(primary), "first_with_corroborated_threshold": len(qualified),
            "first_shots_by_head": by_head, "gate_results": gates}


def summarize(rows, design, files, halts):
    first = [r for r in rows if "first_error_px" in r]
    final = [r for r in first if "final_error_px" in r]
    blanks = [r for r in rows if "blank_drift_px" in r]
    pairs = []
    for (target,), at in group(final, ("target_px",)).items():
        correct = [r for r in at if r["policy"] == "correct"]
        hold = [r for r in at if r["policy"] == "hold"]
        if correct and hold:
            def change(field):
                return mean(r[field] for r in hold) - mean(r[field] for r in correct)
            pairs.append({"target_px": target, "hold_labels": [r["label"] for r in hold], "correct_labels": [r["label"] for r in correct],
                          "hold_minus_correct_start_px": change("start_px"), "hold_minus_correct_first_absolute_error_px": change("first_absolute_error_px"),
                          "hold_minus_correct_final_absolute_error_px": change("final_absolute_error_px")})
    cross = {}
    for key in ("left_contact_patch_mad_at_post_px", "left_dry_mark_motion_px", "right_dry_mark_motion_px", "center_minus_primary_motion_px", "right_minus_primary_motion_px", "outer_right_minus_primary_motion_px"):
        values = [r[key] for r in first if key in r]
        cross[key] = describe(values)
    return {
        "scope": "Restored tube layout and revised electrical connections. Each target is a downward image displacement in pixels from the reset reference at the clear contact on x=980. A increases this coordinate and B decreases it on the verified setup.",
        "method": "Errors are observed position minus requested position. The first-shot, post-correction and later endpoint columns are computed separately from the saved camera readings. The hold policy receives one initial gate. The correction policy permits one additional gate. The last image is timed from the most recent completion receipt.",
        "uncertainty": "Each photographed endpoint combines nearby patches on the same optical contact. Patch scatter and other normalized sightline motions check optical sensitivity. The spread among held-out trials describes this run. Pixel position has no independent absolute liquid-volume tolerance.",
        "frozen_model_px_per_s": design["pixels_per_second"], "local_reference": design["coordinate"],
        "journals": files, "halts": halts, "target_trials_planned": sum(a[1] != "idle" for a in design["trials"]),
        "target_trials_with_first_score": len(first), "target_trials_with_final_score": len(final),
        "incomplete": [{k: r.get(k) for k in ("file", "label", "design_index", "policy", "status", "first_board_ms", "first_error_px")} for r in rows if r["status"] not in ("scored_final", "blank")],
        "all": summaries(first, ()), "by_initial_channel": summaries(first, ("first_head",)),
        "by_policy": summaries(first, ("policy",)), "by_initial_channel_and_policy": summaries(first, ("first_head", "policy")),
        "matched_destinations": pairs,
        "paired_hold_minus_correct_final_absolute_error_px": describe([p["hold_minus_correct_final_absolute_error_px"] for p in pairs]),
        "passive_shift_after_most_recent_gate_px": describe([r["passive_motion_early_to_final_px"] for r in final]),
        "blank_signed_motion_px": describe([r["blank_drift_px"] for r in blanks]),
        "blank_image_interval_s": describe([r["blank_image_interval_s"] for r in blanks]),
        "first_shot_optical_crosschecks": cross,
        "first_shot_descriptive_delivery_fit": fit_delivery(first),
        "nominal_volume_scale_on_target_coordinate": fit_volume_scale(first),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("journals", type=Path)
    p.add_argument("--design", type=Path)
    p.add_argument("--responses", type=Path, help="Directory of gate-aligned optical response CSVs and their JSON metadata.")
    p.add_argument("--out", type=Path, default=Path(__file__).parent)
    args = p.parse_args()
    design = json.loads((args.design or args.journals / "rewired-design.json").read_text())
    rows, files, halts = [], [], []
    for f in sorted(args.journals.glob("position-r*.jsonl")):
        trials, points, errors, info = read_log(f)
        files.append(info)
        halts.extend(errors)
        rows.extend(evaluate(t, points, design) for t in trials)
    rows.sort(key=lambda r: r["pre_image_pts_ns"])
    args.out.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows, design, files, halts)
    if args.responses:
        summary["continuous_surface_response"] = timing_summary(rows, args.responses)
    (args.out / "position_scores.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    fields = dict.fromkeys(k for r in rows for k in r)
    with (args.out / "position_trials.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
