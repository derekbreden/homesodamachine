#!/usr/bin/env python3
"""Inventory saved camera evidence against every attempted journaled pour, photograph and return."""

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

import cup_volume

from fit_geometry import read_log
from replay import sha
from score_optics import stats

HERE = Path(__file__).resolve().parent
PHASES = (
    "qualifications",
    "train",
    "validation",
    "graduations",
    "fresh",
    "fill",
    "return",
    "repeat",
    "return-final",
)


def inspect(evidence, logs, native):
    packed_root = evidence / "windows"
    packed = {p.parent.name: p for p in packed_root.glob("*/capture.json")}
    all_labels = {"station-idle"}
    journal_stats = {}
    for phase in PHASES:
        journal = logs / (phase + ".jsonl")
        if not journal.is_file():
            continue
        rows = read_log(journal)
        seen = set()
        trials = []
        for r in rows:
            if r["event"] in ("image", "ladder_image"):
                seen.add(r["label"])
            if r["event"] in ("before", "after", "hold"):
                seen.add(r["window"])
            if r["event"] == "trial":
                trials.append((r["pre"], r["post"]))
                seen.update(trials[-1])
            if r["event"] == "station_position":
                seen.update((r["first_window"], r["last_window"]))
        all_labels.update(seen)
        journal_stats[phase] = {
            "sha256": sha(journal),
            "closed": bool(rows and rows[-1]["event"] == "closed"),
            "photographed_labels": len(seen),
            "missing_photographs": sorted(seen - packed.keys()),
            "complete_trial_pairs": sum(a in packed and b in packed for a, b in trials),
            "logged_trials": len(trials),
        }
    digest = hashlib.sha256()
    offsets = []
    archive_bytes = 0
    for label, path in sorted(packed.items()):
        d = json.loads(path.read_text())
        digest.update((label + " " + sha(path) + "\n").encode())
        offsets.append(d["color_offset_from_luma_mid_s"])
        archive_bytes += sum(
            (path.parent / k).stat().st_size
            for k in ("average.png", "color.png", "clear.png")
        )
    report = {
        "archived_windows": len(packed),
        "ordered_capture_metadata_sha256": digest.hexdigest(),
        "mean_luma_and_colour_offset_seconds": stats(offsets),
        "sparse_signal_png_bytes": archive_bytes,
        "source_complete_journal_windows": not all_labels - packed.keys(),
        "missing_journal_windows": sorted(all_labels - packed.keys()),
        "preserved_extra_windows": sorted(packed.keys() - all_labels),
        "journals": journal_stats,
    }
    if native is not None:
        required = ("average.png", "color.png", "window.json", "color.json")
        available = {p.name: p for p in native.iterdir() if p.is_dir()}
        complete = {
            label: path
            for label, path in available.items()
            if all((path / f).is_file() for f in required)
        }
        report["native"] = {
            "complete": len(complete),
            "partial": sorted(available.keys() - complete.keys()),
            "missing_from_archive": sorted(complete.keys() - packed.keys()),
            "absent_from_native": sorted(packed.keys() - complete.keys()),
        }
        mismatches = []
        size = 0
        for label in sorted(packed.keys() & complete.keys()):
            path = complete[label]
            wanted = json.loads(packed[label].read_text())["full_sha256"]
            for name in required:
                if sha(path / name) != wanted[name]:
                    mismatches.append(label + "/" + name)
            size += sum(
                (path / name).stat().st_size for name in ("average.png", "color.png")
            )
        report["native"]["hash_mismatches"] = mismatches
        report["native"]["full_signal_png_bytes"] = size
        report["native"]["sparse_over_native_signal_bytes"] = (
            archive_bytes / size if size else None
        )
        aligned = {}
        for folder in (
            evidence / "graduations",
            evidence / "qualification-graduations",
            evidence.parent / "photos/clear-examples",
        ):
            checked = 0
            wrong = []
            for source in sorted(folder.glob("*/source.json")):
                label = source.parent.name
                if label not in complete:
                    wrong.append(label)
                    continue
                for name in ("average.png", "color.png"):
                    native_crop = cup_volume.crop(complete[label] / name)
                    with Image.open(source.parent / name) as saved:
                        if (
                            saved.mode != native_crop.mode
                            or saved.size != native_crop.size
                            or saved.tobytes() != native_crop.tobytes()
                        ):
                            wrong.append(label + "/" + name)
                checked += 1
            aligned[folder.name] = {
                "checked_window_pairs": checked,
                "pixel_mismatches": wrong,
            }
        report["native"]["rectangular_crops"] = aligned
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=HERE / "evidence")
    p.add_argument(
        "--native",
        type=Path,
        help="Compare every native source hash with the recorded hash",
    )
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument("--out", type=Path, default=HERE / "evidence/coverage.json")
    a = p.parse_args()
    summary = inspect(a.evidence, a.logs, a.native)
    a.out.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "archived_windows",
                    "source_complete_journal_windows",
                    "missing_journal_windows",
                )
            }
        )
    )
    native_results = summary.get("native", {})
    if (
        summary["missing_journal_windows"]
        or any(
            native_results.get(k)
            for k in ("missing_from_archive", "absent_from_native", "hash_mismatches")
        )
        or any(
            v["pixel_mismatches"]
            for v in native_results.get("rectangular_crops", {}).values()
        )
    ):
        raise SystemExit("See the inventory for unmatched photos")
