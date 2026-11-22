#!/usr/bin/env python3
"""Recompute absolute levels, positive doses, stationary repeatability and prospectively forecast errors from photographed cup scales."""

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import replay

HERE = Path(__file__).resolve().parent
FACES = {
    "primary": "right",
    "held_out": "left",
    "left_quarters_excluding_control": "independent",
}


def stats(values):
    v = np.asarray([x for x in values if x is not None], float)
    if not len(v):
        return {"n": 0}
    return {
        "n": len(v),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "median_abs": float(np.median(abs(v))),
        "q95_abs": float(np.quantile(abs(v), 0.95)),
        "min": float(v.min()),
        "max": float(v.max()),
        "max_abs": float(np.max(abs(v))),
    }


def output_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def read_journal(path):
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            break
    return out


def difference(values, before, after, sign=1):
    a, b = values.get(before, {}), values.get(after, {})
    return {
        face + "_ml": sign * (b[face + "_ml"] - a[face + "_ml"])
        if a.get(face + "_ok") and b.get(face + "_ok")
        else None
        for face in FACES.values()
    }


def extract(archive, fast):
    meta = json.loads((archive / "layout.json").read_text())
    rows = []
    idx = {}
    for path in sorted((archive / "windows").glob("*/capture.json")):
        dt = path.parent
        if dt.name != "station-idle" and not re.match(
            r"^(?:q|learn|validation)\d+-", dt.name
        ):
            continue
        capture = json.loads(path.read_text())
        data = (
            json.loads((dt / "reading.json").read_text())
            if fast
            else replay.reduced_read(replay.unpack_arrays(dt, meta), detail=False)
        )
        row = {
            "label": dt.name,
            "pts_ns": capture["mean_luma"]["mid"]["pts_ns"],
            "color_offset_s": capture["color_offset_from_luma_mid_s"],
        }
        for name, face in FACES.items():
            d = data[name]
            row[face + "_ok"] = d["ok"]
            row[face + "_ml"] = d.get("nominal_ml")
            row[face + "_y"] = d.get("y")
            row[face + "_patches"] = d.get("patches")
            row[face + "_flags"] = " | ".join(d["flags"])
            row[face + "_mad_px"] = d.get("residual_mad_px")
            row[face + "_one_cup_y"] = next(
                (m["y"] for m in d["marks"] if m["cups"] == 1.0), None
            )
            row[face + "_near_one_px"] = (
                abs(d["y"] - row[face + "_one_cup_y"])
                if d.get("y") is not None and row[face + "_one_cup_y"] is not None
                else None
            )
        row["right_minus_independent_ml"] = (
            row["right_ml"] - row["independent_ml"]
            if row["right_ok"] and row["independent_ok"]
            else None
        )
        rows.append(row)
        idx[dt.name] = row
    return rows, idx


def stable_pairs(journal, index, source):
    last = None
    out = []
    for r in journal:
        event = r["event"]
        if event in (
            "board_pour_start",
            "position_gate",
            "qualification_gate",
            "halt",
            "session",
            "closed",
        ):
            last = None
        if event not in ("before", "after", "image"):
            continue
        label = r.get("window") or r["label"]
        if last is not None and label in index and last in index:
            out.append(
                {
                    "source": source,
                    "first": last,
                    "second": label,
                    "elapsed_s": (index[label]["pts_ns"] - index[last]["pts_ns"]) / 1e9,
                    **difference(index, last, label),
                }
            )
        last = label
    return out


def trials(journal, index, source):
    attempts = {}
    results = []
    for ev in journal:
        if ev["event"] == "prediction":
            attempts[ev["label"]] = ev
        if ev["event"] != "trial":
            continue
        attempts.pop(ev["label"], None)
        sign = 1 if ev["head"] == "B" else -1
        name = ev["label"]
        r = {
            k: ev.get(k)
            for k in (
                "phase",
                "index",
                "block",
                "label",
                "scenario",
                "head",
                "pre",
                "post",
                "forecast_ml",
                "burst_count",
                "expected_bursts",
            )
        }
        r["status"] = "completed"
        r.update(difference(index, ev["pre"], ev["post"], sign))
        r["correct_bursts"] = r["burst_count"] == r["expected_bursts"]
        forecast = r["forecast_ml"]
        r["right_start_ml"] = index.get(ev["pre"], {}).get("right_ml")
        r["right_finish_ml"] = index.get(ev["post"], {}).get("right_ml")
        for face in FACES.values():
            v = r[face + "_ml"]
            r[face + "_error_ml"] = (
                None if v is None or forecast is None else v - forecast
            )
            r[face + "_within"] = (
                None
                if forecast is None
                else bool(
                    v is not None
                    and r["correct_bursts"]
                    and abs(v - forecast) <= max(1, abs(forecast) * 0.10)
                )
            )
            r[face + "_within_five_percent"] = (
                None
                if forecast is None
                else bool(
                    v is not None
                    and r["correct_bursts"]
                    and abs(v - forecast) <= abs(forecast) * 0.05
                )
            )
        r["right_minus_independent_ml"] = (
            None
            if r["right_ml"] is None or r["independent_ml"] is None
            else r["right_ml"] - r["independent_ml"]
        )
        r["logged_right_minus_replay_ml"] = (
            None
            if ev.get("primary_ml") is None or r["right_ml"] is None
            else ev["primary_ml"] - r["right_ml"]
        )
        r["logged_left_minus_replay_ml"] = (
            None
            if ev.get("heldout_ml") is None or r["left_ml"] is None
            else ev["heldout_ml"] - r["left_ml"]
        )
        results.append(r)
    for ev in attempts.values():
        # The last prediction can be in flight when running this scorer during acquisition.
        results.append(
            {
                k: ev.get(k)
                for k in (
                    "phase",
                    "index",
                    "block",
                    "label",
                    "scenario",
                    "head",
                    "pre",
                    "forecast_ml",
                )
            }
            | {"status": "prediction without complete trial"}
        )
    return results


def groups(rows):
    table = []
    gr = defaultdict(list)
    for r in rows:
        if r.get("phase") == "validation":
            gr[(r["head"], r["scenario"])].append(r)
    for (head, name), data in sorted(gr.items()):
        # A faulty/aborted attempt remains visible. A repeated scheduled index can contribute only once.
        completed = {}
        for r in data:
            if r["status"] == "completed" and r["index"] not in completed:
                completed[r["index"]] = r
        done = list(completed.values())
        f = data[0]["forecast_ml"]
        r = {
            "head": head,
            "scenario": name,
            "forecast_ml": f,
            "scheduled": 6,
            "completed_indices": len(done),
            "extra_or_incomplete_attempts": len(data) - len(done),
        }
        for face in FACES.values():
            scored = [
                v
                for d in done
                if (v := d.get(face + "_error_ml")) is not None and d["correct_bursts"]
            ]
            inside = sum(bool(d.get(face + "_within")) for d in done)
            bias = float(np.mean(scored)) if scored else None
            r[face + "_scored"] = len(scored)
            r[face + "_inside"] = inside
            r[face + "_bias_ml"] = bias
            r[face + "_inside_five_percent"] = sum(
                bool(d.get(face + "_within_five_percent")) for d in done
            )
            r[face + "_dose_mae_ml"] = (
                float(np.mean(abs(np.asarray(scored)))) if scored else None
            )
            r[face + "_meets_count_and_bias"] = bool(
                inside >= 5
                and bias is not None
                and abs(bias) <= max(0.6, abs(f) * 0.05)
            )
        r["primary_corroborated_by_spatially_disjoint_count"] = (
            r["right_meets_count_and_bias"] and r["independent_inside"] >= 5
        )
        table.append(r)
    return table


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence")
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument("--out", type=Path, default=HERE / "results")
    p.add_argument(
        "--fast",
        action="store_true",
        help="Use readings already verified at pack time for a progress snapshot",
    )
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    endpoints, index = extract(a.evidence, a.fast)
    out = []
    stationary = []
    qualification = []
    for log in ("qualifications", "train", "validation"):
        journal = read_journal(a.logs / (log + ".jsonl"))
        stationary += stable_pairs(journal, index, log)
        if log == "qualifications":
            heads = {
                v["label"]: v for v in journal if v["event"] == "qualification_gate"
            }
            for item in journal:
                if item["event"] != "after":
                    continue
                label = item["label"]
                gate = heads.get(label, {})
                qualification.append(
                    {
                        "label": label,
                        "head": gate.get("head"),
                        "board_ms": gate.get("board_ms"),
                        **difference(index, label + "-pre", item["window"]),
                    }
                )
        else:
            out += trials(journal, index, log)
    scenarios = groups(out)
    summary = {
        "source": "verified per-window readings"
        if a.fast
        else "lossless strips re-read from PNG",
        "n_windows": len(index),
        "mean_luma_vs_color_timestamp_s": stats(
            [v["color_offset_s"] for v in endpoints]
        ),
        "face_counts": {
            f: sum(v[f + "_ok"] for v in endpoints) for f in FACES.values()
        },
        "full_images_equivalent": all(
            json.loads((a.evidence / "windows" / label / "capture.json").read_text())[
                "reproduces_full_sensor_read"
            ]
            for label in index
        ),
        "nominal_endpoint_range_ml": {
            f: stats([v[f + "_ml"] for v in endpoints if v[f + "_ok"]])
            for f in FACES.values()
        },
        "no_command_between_captures_ml": {
            f: stats([v[f + "_ml"] for v in stationary]) for f in FACES.values()
        },
        "right_minus_independent_absolute_ml": stats(
            [v["right_minus_independent_ml"] for v in endpoints]
        ),
        "phase": {},
    }
    for phase in ("training", "validation"):
        done = [e for e in out if e["phase"] == phase and e["status"] == "completed"]
        summary["phase"][phase] = {
            "complete": len(done),
            "right_minus_independent_dose_ml": stats(
                [d["right_minus_independent_ml"] for d in done]
            ),
            "frozen_right_log_minus_replay_ml": stats(
                [d["logged_right_minus_replay_ml"] for d in done]
            ),
            "frozen_left_log_minus_replay_ml": stats(
                [d["logged_left_minus_replay_ml"] for d in done]
            ),
            "right_missing": sum(d["right_ml"] is None for d in done),
        }
    for filename, items in [
        ("endpoints", endpoints),
        ("stationary-pairs", stationary),
        ("qualification", qualification),
        ("trials", out),
        ("scenarios", scenarios),
    ]:
        output_csv(a.out / (filename + ".csv"), items)
    (a.out / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "windows": len(index),
                "replayed_trials": len([r for r in out if r["status"] == "completed"]),
                "stationary_pairs": len(stationary),
            }
        )
    )


if __name__ == "__main__":
    main()
