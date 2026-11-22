"""Predict syrup delivery from a planned gate sequence using two archived baselines."""
import argparse
import csv
import functools
import io
import json
import math
from pathlib import Path
import random
import subprocess


POSITION_COMMIT = "a21b1685370d62bad7cb620c013c4c01c3b7a19d"
POSITION_DIRECTORY = "hardware/reference/kamoer-flow/2026-11-22-position/analysis"
ENGINEERING_SOURCE = "tools/hsm/repo-tools/src/model.rs"
ENGINEERING_COMMIT = "7c59ea2198bfe600d591236d43cd6bdb5f04b81d"
BOOTSTRAP_SEED = 2026112201


def git_file(commit, path):
    root = subprocess.check_output(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
    return subprocess.check_output(["git", "-C", root, "show", f"{commit}:{path}"], text=True)


@functools.lru_cache
def archive_rates():
    rows = csv.DictReader(io.StringIO(git_file(POSITION_COMMIT, f"{POSITION_DIRECTORY}/position_trials.csv")))
    profiles = {"A": [], "B": []}
    for row in rows:
        if row["first_head"] in profiles:
            profiles[row["first_head"]].append((
                float(row["first_board_ms"]) / 1000,
                float(row["right_directed_dose_ml"]),
                float(row["projected_left_directed_dose_ml"]),
            ))
    source = json.loads(git_file(POSITION_COMMIT, f"{POSITION_DIRECTORY}/position_scores.json"))
    score_fields = ["right_signed_cup_change_ml", "projected_left_signed_cup_change_ml"]
    result = {}
    for head, observations in profiles.items():
        def slope(shots, side):
            return sum(s[0] * s[side] for s in shots) / sum(s[0] ** 2 for s in shots)

        point = [slope(observations, side) for side in (1, 2)]
        for idx, field in enumerate(score_fields):
            published = source["first_shot_descriptive_delivery_fit"]["heads"][head][field]
            if not math.isclose(point[idx], published["directional_magnitude_per_second"]):
                raise ValueError(f"Recomputed slope did not match the published {head} {field} slope")
        rng = random.Random(f"{BOOTSTRAP_SEED}-{head}")
        repeats = []
        for _ in range(10000):
            sample = rng.choices(observations, k=len(observations))
            repeats.append([slope(sample, side) for side in (1, 2)])
        result[head] = {
            "calibration_shots": len(observations),
            "gate_seconds_fit_range": [min(s[0] for s in observations), max(s[0] for s in observations)],
            "rulers": {
                name: {
                    "rate_ml_s": point[side],
                    "rate_fit_middle_80_ml_s": [
                        quantile_by_rank([r[side] for r in repeats], q) for q in (0.10, 0.90)
                    ],
                }
                for side, name in enumerate(["right", "projected_left"])
            },
        }
    return result


def quantile_by_rank(values, fraction):
    return sorted(values)[min(len(values) - 1, int(len(values) * fraction))]


@functools.lru_cache
def engineering_draws():
    rng = random.Random(20261009)
    trials = []
    for _ in range(2000):
        values = [rng.random() for _ in range(35)]
        spread = 0.9 + 0.2 * values[27]
        supply_v = 11.8 + 0.4 * values[28]
        drop_v = 0.5 + 0.5 * values[29]
        motor_ir_v = 2.5 + 2.5 * values[30]
        loss_ms = 10 + 30 * values[31]
        slip = 0.03 * values[32]
        rate_ml_min = 600 * spread * (supply_v - drop_v - motor_ir_v) / (12 - motor_ir_v) * (1 - slip)
        trials.append((rate_ml_min, loss_ms))
    return trials


def validated_widths(gate_widths_ms):
    widths = tuple(float(w) for w in gate_widths_ms)
    if any(not math.isfinite(w) or w <= 0 for w in widths):
        raise ValueError("Every gate width must be a positive finite millisecond duration")
    return widths


@functools.lru_cache(maxsize=128)
def engineering_forecast(widths):
    counts = {width: widths.count(width) for width in set(widths)}
    doses = [
        rate * sum(count * max(0.0, width - loss) for width, count in counts.items()) / 60000
        for rate, loss in engineering_draws()
    ]
    return {
        "p10_ml": quantile_by_rank(doses, 0.10),
        "p50_ml": quantile_by_rank(doses, 0.50),
        "p90_ml": quantile_by_rank(doses, 0.90),
    }


def forecast(head, gate_widths_ms):
    widths = validated_widths(gate_widths_ms)
    if head not in ("A", "B"):
        raise ValueError("Head must identify PCB output A or B")
    on_seconds = sum(widths) / 1000
    restored = {
        side: {
            "dose_ml": info["rate_ml_s"] * on_seconds,
            "rate_fit_middle_80_dose_ml": [rate * on_seconds for rate in info["rate_fit_middle_80_ml_s"]],
        }
        for side, info in archive_rates()[head]["rulers"].items()
    }
    return {
        "head": head,
        "gates": len(widths),
        "total_nominal_on_ms": sum(widths),
        "restored_constant_rate": restored,
        "engineering_dead_time": engineering_forecast(widths),
    }


def specification():
    return {
        "restored_constant_rate": {
            "source_git": POSITION_COMMIT,
            "files": [f"{POSITION_DIRECTORY}/{name}" for name in ("position_trials.csv", "position_scores.json")],
            "formula": "The slope fitted through zero to nominal cup volume against acknowledged board-on seconds, multiplied by total planned on-seconds. It has no allowance for a restart, pause or valve opening.",
            "rulers": "Direct right glass marks and independently projected left marks share the same cup. The two predictions show volume-scale sensitivity. Each middle-80 band resamples whole archived shots in paired ruler measurements and propagates slope uncertainty. Neither band covers future individual-pour variation, common cup accuracy, geometry changes or transfer between rigs.",
            "models": archive_rates(),
        },
        "engineering_dead_time": {
            "source_git": ENGINEERING_COMMIT,
            "file": ENGINEERING_SOURCE,
            "formula": "For each engineering prior draw, sum rate_ml_min * max(0, width_ms - loss_ms) / 60000 across all planned gates. All gates of the pour share the same rate and loss. Use the exact seeded model quantiles.",
            "distribution": "Independent uniform engineering inputs. Rate = 600 * spread * (supply_V - drop_V - armature_V) / (12 - armature_V) * (1 - slip). Ranges: spread 0.9–1.1, supply 11.8–12.2 V, drop 0.5–1.0 V, armature 2.5–5 V, slip 0–0.03, loss per gate 10–40 ms.",
            "interpretation": "These are engineering-parameter prior quantiles, shared by the heads. They are not calibrated bounds on future measurements. The model subtracts spin-up even when firmware briefly parks at the transition of a nominal continuous ratio cycle.",
            "rate_prior_ml_min_p10_p50_p90": [
                quantile_by_rank([rate for rate, _ in engineering_draws()], q)
                for q in (0.10, 0.50, 0.90)
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("head", choices=["A", "B"], nargs="?")
    parser.add_argument("widths", nargs="*", help="Width in milliseconds, optionally followed by x and its count")
    options = parser.parse_args()
    if options.head is None:
        result = specification()
    else:
        widths = []
        for pattern in options.widths:
            width, sep, repeats = pattern.partition("x")
            count = int(repeats) if sep else 1
            if count < 1:
                parser.error("A gate count must be positive")
            widths.extend([float(width)] * count)
        result = forecast(options.head, widths)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
