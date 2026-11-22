#!/usr/bin/env python3
"""Fit full-drive Diet Cola transfer from archived camera and controller records."""

import argparse
import csv
import io
import json
import math
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median


REVISION = "30f0c9078f5905d1041d60111efb0b832e3c554e"
DIRECTORY = "hardware/reference/kamoer-flow/2026-11-21-diet-cola"
SINGLE_CALIBRATION = ("focus-duration-1", "focus-duration-2")
SINGLE_TEST = "focus-duration-3"
HEADS = ("A", "B")


@dataclass(frozen=True)
class Trial:
    name: str
    block: str
    head: str
    width_ms: int
    count: int
    pause_ms: int
    total_on_s: float
    optical_ml: float
    start_cup_ml: float | None = None
    same_head_rest_s: float | None = None


def known_rests(events):
    """Time the first command from the preceding same-head stop receipt in this recording."""
    last_stop = {}
    result = {}
    trial = None
    for event in events:
        kind = event["event"]
        if kind == "test_start":
            trial, head = event["trial"], event["head"].upper()
        elif trial is not None and kind == "tx" and event["command"].startswith("pump "):
            if trial not in result:
                result[trial] = (event["t_ns"] - last_stop[head]) / 1e9 if head in last_stop else None
        elif trial is not None and kind == "rx" and event["line"].startswith(f"[machine] pump {head} done after"):
            last_stop[head] = event["t_ns"]
        elif kind == "test_done":
            trial = None
    return result


def load_records(read):
    def table(file):
        return csv.DictReader(io.StringIO(read(file)))

    video = []
    blocks = defaultdict(list)
    for row in table("released/trials.csv"):
        blocks[row["recording"]].append(row)
    for block, rows in blocks.items():
        prefix = f"released/recordings/{block}/"
        optics = {r["trial"]: r for r in json.loads(read(prefix + "optical.json"))}
        rest = known_rests(json.loads(line) for line in read(prefix + "events.jsonl").splitlines())
        for row in rows:
            trial = int(row["trial"])
            start = median(sightline[-1] for sightline in optics[trial]["pre"])
            video.append(Trial(f"{block}/{trial}", block, row["channel"], int(row["gate_ms"]),
                               int(row["pulses"]), int(row["pause_ms"]), int(row["board_total_on_ms"]) / 1000,
                               float(row["directed_volume_ml"]), start, rest[trial]))

    stills = []
    for row in table("native-single-shots.csv"):
        if row["head"] in HEADS:
            stills.append(Trial("native/" + row["index"], "native", row["head"], int(row["nominal_ms"]),
                                1, 0, float(row["board_reported_ms"]) / 1000, float(row["directional_transfer_ml"])))

    guided = []
    for row in table("dose-results.csv"):
        if row["pwm_pct"] == "100" and row["optical_transfer_ml"]:
            guided.append(Trial(row["run"], "guided", row["channel"], int(row["on_ms"]),
                                int(row["pulses"]), int(row["off_ms"]), float(row["gate_s"]),
                                float(row["optical_transfer_ml"])))
    return video, stills, guided


def slope(xs, ys):
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


def fit_rate(rows):
    return slope([r.total_on_s for r in rows], [r.optical_ml for r in rows])


def score(rows, predict, detail=False):
    errors = [predict(r) - r.optical_ml for r in rows]
    report = {"n": len(rows), "mean_absolute_error_ml": mean(map(abs, errors)),
              "maximum_absolute_error_ml": max(map(abs, errors)), "mean_predicted_minus_observed_ml": mean(errors)}
    if detail:
        report["predictions"] = [
            {"trial": r.name, "head": r.head, "command_ms": r.width_ms, "pulses": r.count, "pause_ms": r.pause_ms,
             "predicted_ml": r.optical_ml + error, "observed_ml": r.optical_ml, "predicted_minus_observed_ml": error}
            for r, error in zip(rows, errors)
        ]
    return report


def isolated_shots(video, native):
    calibration = [r for r in video if r.block in SINGLE_CALIBRATION]
    test = [r for r in video if r.block == SINGLE_TEST]
    pooled = fit_rate(calibration)
    rates, heads = {}, {}
    for head in HEADS:
        train = [r for r in calibration if r.head == head]
        held = [r for r in test if r.head == head]
        held_native = [r for r in native if r.head == head]
        rate = rates[head] = fit_rate(train)
        on = [r.total_on_s for r in train]
        dose = [r.optical_ml for r in train]
        offset_rate = slope([t - mean(on) for t in on], [v - mean(dose) for v in dose])
        offset = mean(dose) - offset_rate * mean(on)
        # Centering by squared on-time makes the fill term orthogonal to the fitted rate.
        center = sum(r.total_on_s**2 * r.start_cup_ml for r in train) / sum(t*t for t in on)
        fill_slope = slope([r.total_on_s * (r.start_cup_ml - center) for r in train], dose)
        with_age = [r for r in train if r.same_head_rest_s is not None]
        known_test = [r for r in held if r.same_head_rest_s is not None]
        log_center = mean(math.log2(r.same_head_rest_s) for r in with_age)
        age_slope = slope([math.log2(r.same_head_rest_s) - log_center for r in with_age],
                          [r.optical_ml - rate * r.total_on_s for r in with_age])
        base = lambda r: rate * r.total_on_s
        heads[head] = {
            "rate_ml_per_s": rate, "training_trials": [r.name for r in train],
            "released_video_holdout": {
                "head_rate": score(held, base, detail=True),
                "one_rate_for_both_heads": score(held, lambda r: pooled * r.total_on_s),
                "rate_plus_start_offset": score(held, lambda r: offset_rate * r.total_on_s + offset),
                "rate_linear_in_starting_cup_level": score(held, lambda r: base(r) + fill_slope * r.total_on_s * (r.start_cup_ml - center)),
            },
            "earlier_same_head_stop_known": {
                "calibration_rest_s_range": [min(r.same_head_rest_s for r in with_age), max(r.same_head_rest_s for r in with_age)],
                "test_rest_s_range": [min(r.same_head_rest_s for r in known_test), max(r.same_head_rest_s for r in known_test)],
                "ml_per_doubling_of_idle": age_slope,
                "head_rate": score(known_test, base),
                "head_rate_plus_centered_log_idle": score(known_test, lambda r: base(r) + age_slope * (math.log2(r.same_head_rest_s) - log_center)),
            },
            "native_camera_holdout": score(held_native, base, detail=True),
            "native_width_absent_from_training": score([r for r in held_native if r.width_ms == 50], base),
        }
    return rates, heads


def restarts(rows, rates):
    """Fit a common empirical volume for each restart in a finite pulse train."""
    return slope([r.count - 1 for r in rows], [r.optical_ml - rates[r.head] * r.total_on_s for r in rows])


def train_holdout(video, rates):
    first = [r for r in video if r.block == "segments-1"]
    second = [r for r in video if r.block == "segments-2"]
    base = lambda r: rates[r.head] * r.total_on_s
    bonus = restarts(first, rates)
    result = {
        "calibration_trials": [r.name for r in first],
        "common_ml_per_restart": bonus,
        "summing_motor_on_time": score(second, base),
        "adding_per_restart": score(second, lambda r: base(r) + (r.count - 1) * bonus, detail=True),
        "repeating_identical_command_from_first_recording": score(second, lambda r: next(
            a.optical_ml for a in first if a.head == r.head and a.width_ms == r.width_ms)),
    }
    by_width = {}
    for width in sorted({r.width_ms for r in second}):
        other_widths = [r for r in first if r.width_ms != width]
        bonus = restarts(other_widths, rates)
        other_block = [r for r in second if r.width_ms == width]
        by_width[width] = {
            "summing_motor_on_time": score(other_block, base),
            "adding_per_restart": score(other_block, lambda r: base(r) + (r.count - 1) * bonus),
        }
    result["also_holding_out_each_width_pause_pair_from_training"] = by_width
    return result


def fill_band_test(guided):
    result = {}
    for head in HEADS:
        high = [r for r in guided if r.head == head and r.name.startswith("repeat-")]
        lower = [r for r in guided if r.head == head and r.name.startswith("level-low-")]
        rate = fit_rate(high)
        result[head] = {"calibration_trials": [r.name for r in high], "higher_band_rate_ml_per_s": rate,
                        "lower_band_rate_ml_per_s": fit_rate(lower),
                        "prediction_in_lower_band": score(lower, lambda r: rate * r.total_on_s, detail=True)}
    return result


def gap_forecast(guided, video, rates):
    result = {}
    for head in HEADS:
        short = [r for r in guided if r.head == head and r.width_ms == 110 and r.pause_ms == 60]
        long = [r for r in guided if r.head == head and r.width_ms == 110 and r.pause_ms == 480]
        anchor = [r for r in video if r.head == head and r.count == 20 and r.width_ms == 100 and r.pause_ms == 150]
        rate = rates[head]
        delta = (mean(r.optical_ml for r in short) - mean(r.optical_ml for r in long)) / (short[0].count - 1)
        anchors = [(r.optical_ml - rate * r.total_on_s) / (r.count - 1) for r in anchor]

        def gap_fraction(pause):
            return math.log(min(480, max(60, pause)) / 150) / math.log(60 / 480)

        def estimate(on_s, n, gap, restart, contrast):
            return rate * on_s + (n - 1) * (restart + contrast * gap_fraction(gap))

        second = [r for r in video if r.head == head and r.block == "segments-2"]
        first_anchor = next(value for row, value in zip(anchor, anchors) if row.block == "segments-1")
        forecasts = []
        for gap in (50, 150, 450, 1100):
            variants = [estimate(0.8, 8, gap, start, (fast.optical_ml - slow.optical_ml) / (fast.count - 1))
                        for start in anchors for fast in short for slow in long]
            forecasts.append({"pause_ms": gap, "eight_100_ms_total_ml": estimate(0.8, 8, gap, mean(anchors), delta),
                              "on_time_only_ml": rate * 0.8, "range_using_individual_archived_repeats_ml": [min(variants), max(variants)]})
        result[head] = {
            "anchor_trials": [r.name for r in anchor], "same_width_pause_calibration_trials": [r.name for r in short + long],
            "extra_ml_per_restart_at_150_ms": mean(anchors), "extra_ml_per_restart_60_minus_480_ms": delta,
            "forecasts": forecasts,
            "earlier_block_only_anchor_predicts_second_block": score(second, lambda r: estimate(r.total_on_s, r.count, r.pause_ms, first_anchor, delta), detail=True),
        }
    return result


def run(read):
    video, native, guided = load_records(read)
    rates, isolated = isolated_shots(video, native)
    return {
        "source_commit": REVISION, "source_directory": DIRECTORY,
        "scope": "Full-drive forward Diet Cola transfer on the open-hose bench. A withdraws and B refills the cup. Each direction includes its tubing, head and optical path.",
        "method": {
            "observable": "Settled directed optical volume from the marked cup. Signed sub-resolution readings are retained. Every test unit is a complete camera-bracketed command or train.",
            "single_gate": "Per head, least squares through zero against actual board-reported on-time in seconds. Each entire camera observation has equal weight. Fit records are the first two released duration blocks. The complete third block and the separate native-resolution series are withheld.",
            "idle": "Time from the last same-head stop receipt to the first write in the same recording. Initial unknown ages are excluded only from the idle comparison. The additive aging term adjusts the fixed head rate by centered log2 of measured idle.",
            "fixed_duty_trains": "The finite-train estimate adds one common fitted increment for each restart after the first. The first segmentation recording calibrates this increment. The entire reversed-order second recording tests it. Pulse width, gap and number covary at fixed duty.",
            "cup_level": "The released-video candidate makes rate linear in the cup level measured before the gate. The separate guided comparison transfers rates from the earlier higher starting band to lower starting levels at fixed gate length.",
            "gap_forecast": "Base dose is rate times total on-time. Add a correction for each restart. Anchor the correction with the released trains at the reference pause. Change it linearly in log pause with the earlier fixed-width short-versus-long contrast, holding it flat beyond the measured pause endpoints. The anchor uses both archived segmentation blocks only for forecasting the next experiment. Its separate earlier-block test uses the first anchor alone.",
            "uncertainty": "Archive-only residuals pool pump variation and camera error. The clock measures commands and receipts. Cup graduation accuracy and true shaft position are unknown. One train per head sets the fast end of the prior pause contrast, A had bend guides in that contrast, and priors at the shortest and longest new gaps are clamped extrapolations. Repeat sensitivity ranges vary the measured calibration repeats and are not statistical intervals.",
        },
        "isolated_gate": isolated,
        "held_out_train_recording": train_holdout(video, rates),
        "guided_to_lower_fill_band": fill_band_test(guided),
        "new_single_command_forecast": {
            "rounding": "Announced rates rounded to two decimals before multiplication. The gap forecasts use full fit precision.",
            "rates_ml_per_s": {h: round(rates[h], 2) for h in HEADS},
            "directed_ml_by_gate_ms": {ms: {h: round(rates[h], 2) * ms / 1000 for h in HEADS} for ms in (375, 750, 1500, 2250)},
            "inverse": "For a desired settled endpoint, choose A if the starting cup level is higher and B if lower. Gate seconds equals the absolute volume difference divided by the chosen rate.",
        },
        "new_pause_forecast": gap_forecast(guided, video, rates),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, help="Read from an extracted copy of the archived bench directory.")
    parser.add_argument("--repo", default=".", help="Git checkout containing the archived bench record.")
    args = parser.parse_args()

    def read(file):
        if args.data:
            return (args.data / file).read_text()
        return subprocess.check_output(["git", "-C", args.repo, "show", f"{REVISION}:{DIRECTORY}/{file}"], text=True)

    print(json.dumps(run(read), indent=2, allow_nan=False))
