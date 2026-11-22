"""Plot individual photographed doses and the tolerance around each prospective prediction."""
import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator


SCENARIOS = {
    "top_off": "Top-off",
    "full_glass": "Full-flow glass",
    "partial_glass": "Half-flow glass",
    "ease_open": "Lever opened in stages",
    "same_open_time": "Steady short pour",
    "release_reopen": "Release and reopen",
    "stronger_setting": "Stronger recipe",
    "trickle": "Trickle",
}
FRESH_SCENARIOS = {
    "near_full_glass": "Near-full-flow glass",
    "partial_top_off": "Half-flow top-off",
    "finish_at_full_flow": "Finish at full flow",
    "short_richer_pour": "Short, stronger pour",
}
INK = "#202f3e"
MUTED = "#4f6071"
PRIMARY = "#175a85"
SECONDARY = "#a34322"
BAND = "#dce9ef"


def figure(scores, attempts_path, output, fresh=False):
    labels = FRESH_SCENARIOS if fresh else SCENARIOS
    results = {(r["scenario"], r["head"]): r for r in scores["classification"]}
    with attempts_path.open(newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["phase"] == ("fresh" if fresh else "validation")
                and r["selected_for_cell"] == "True" and r["photographed_expected_waveform"] == "True"]
    values = [float(r[c]) for r in rows for c in ("primary_ml", "heldout_ml") if r[c]]
    values += [p * 1.1 + 1 for r in results.values() if (p := r["forecast_ml"]) is not None]
    if not values:
        raise ValueError("The plot needs a trained forecast or an independently read dose")
    upper = max(values) * (1.02 if fresh else 1)
    x_max = math.ceil(upper / 5) * 5
    x_min = min(0, math.floor(min(values) / 5) * 5)
    fig, axes = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(12.2, 4.9 if fresh else 6.65), dpi=170)
    fig.set_facecolor("white")
    fig.subplots_adjust(left=0.20, right=0.97, bottom=0.23 if fresh else 0.20, top=0.71 if fresh else 0.75, wspace=0.17)
    title = "Syrup dose on four new lever sequences" if fresh else "Predicted and measured syrup dose"
    if fresh:
        status = scores.get("calibration_status", "")
        subtitle = ("Provisional cup volumes at two clear-glass sightlines" if "provisional" in status.lower()
                    else "Graduation-calibrated cup volumes at two clear-glass sightlines")
    else:
        subtitle = "Appliance pour timing on the open-hose Diet Cola bench"
    fig.text(0.035, 0.95, title, fontsize=22, weight="bold", color=INK, va="top")
    fig.text(0.035, 0.85 if fresh else 0.876, subtitle,
             fontsize=12.3, color=MUTED, va="top")
    names = list(labels)
    for ax, head in zip(axes, ("A", "B")):
        ax.set_title(f"Pump {head}", loc="left", fontsize=15, color=INK, weight="bold", pad=9)
        for idx, name in enumerate(names):
            y = len(names) - idx - 1
            r = results[name, head]
            if idx % 2 == 0:
                ax.axhspan(y - 0.5, y + 0.5, color="#f6f8fa", zorder=0)
            predicted = r["forecast_ml"]
            if predicted is not None:
                tol = max(1, 0.10 * predicted)
                ax.fill_betweenx([y - 0.21, y + 0.21], predicted - tol, predicted + tol,
                                 color=BAND, zorder=2, linewidth=0)
                ax.vlines(predicted, y - 0.25, y + 0.25, color=INK, linewidth=1.7, zorder=3)
            obs = sorted((v for v in rows if v["scenario"] == name and v["head"] == head), key=lambda v: int(v["block"]))
            for row in obs:
                yy = y + 0.064 * (int(row["block"]) - 3.5)
                pri = float(row["primary_ml"]) if row["primary_ml"] else None
                if row["heldout_ml"]:
                    sec = float(row["heldout_ml"])
                    if pri is not None:
                        ax.plot([pri, sec], [yy, yy], color="#aaa5a2", linewidth=0.7, zorder=3)
                    ax.scatter([sec], [yy], s=16, color="white", marker="o", edgecolors=SECONDARY,
                               linewidths=0.9, zorder=4)
                if pri is not None:
                    ax.scatter([pri], [yy], s=11, facecolors=PRIMARY, edgecolors="none", zorder=5)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-0.55, len(names) - 0.45)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=7, integer=True, min_n_ticks=4))
        ax.set_xlabel("Nominal concentrate volume (mL)", fontsize=10, color=MUTED, labelpad=7)
        ax.grid(axis="x", linewidth=0.6, color="#dde3e7", zorder=1)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", colors=MUTED, labelsize=10, length=0, pad=5)
        ax.spines[["left", "top", "right"]].set_visible(False)
        ax.spines["bottom"].set_color("#bcc9d0")
    axes[0].set_yticks(range(len(names)), [labels[n] for n in reversed(names)], ha="right", color=INK)
    fig.legend(
        handles=[
            Line2D([], [], linestyle="none", marker="|", markersize=14, color=INK, markeredgewidth=2, label="Frozen forecast"),
            Patch(facecolor=BAND, edgecolor="none", label="Forecast tolerance"),
            Line2D([], [], linestyle="none", marker="o", markersize=5, markeredgecolor=PRIMARY, markerfacecolor=PRIMARY, label="Primary cup reading"),
            Line2D([], [], linestyle="none", marker="o", markersize=5, markeredgecolor=SECONDARY, markerfacecolor="white", label="Second cup reading"),
        ],
        loc="lower center", bbox_to_anchor=(0.54, 0.075), ncol=4, frameon=False, fontsize=10,
        handletextpad=0.55, columnspacing=1.5, labelcolor=INK,
    )
    fig.text(0.035, 0.045, "Each pair of points is one pour. The band is the larger of 1 mL or 10% of the forecast.",
             fontsize=9.8, color=MUTED)
    fig.savefig(output, facecolor="white")
    plt.close(fig)


def repeat_figure(scores, output):
    results = {(r["scenario"], r["head"]): r for r in scores["classification"]}
    methods = [
        ("primary_relative_error_pct", "Right cup scale", PRIMARY, "o", 0.22),
        ("heldout_relative_error_pct", "Left cup scale", SECONDARY, "D", 0.0),
        ("clear_relative_error_pct", "Clear glass patch", "#287a5c", "s", -0.22),
    ]
    periods = ["first_three_blocks", "last_three_blocks"]
    limits = [0]
    for r in results.values():
        for period in periods:
            for field, *_ in methods:
                v = r["repeat_diagnostics"][period][field].get("median")
                if v is not None:
                    limits.append(v)
    fig, axes = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(12.2, 6.65), dpi=170)
    fig.set_facecolor("white")
    fig.subplots_adjust(left=0.20, right=0.97, bottom=0.21, top=0.74, wspace=0.17)
    fig.text(0.035, 0.95, "How the three optical readings compare", fontsize=22, weight="bold", color=INK, va="top")
    fig.text(0.035, 0.874, "Median error over the first three and last three validation blocks",
             fontsize=12.3, color=MUTED, va="top")
    names = list(SCENARIOS)
    for ax, head in zip(axes, ("A", "B")):
        ax.set_title(f"Pump {head}", loc="left", fontsize=15, color=INK, weight="bold", pad=9)
        for i, name in enumerate(names):
            y = len(names) - i - 1
            if i % 2 == 0:
                ax.axhspan(y - 0.5, y + 0.5, color="#f6f8fa", zorder=0)
            for field, _, color, marker, dy in methods:
                halves = [results[name, head]["repeat_diagnostics"][p][field].get("median") for p in periods]
                if None not in halves:
                    ax.plot(halves, [y + dy, y + dy], linewidth=1.3, color=color, zorder=3)
                for j, v in enumerate(halves):
                    if v is not None:
                        ax.scatter([v], [y + dy], marker=marker, s=23 if j == 0 else 15,
                                   facecolors="white" if j == 0 else color, edgecolors=color, linewidths=1.0, zorder=4)
        ax.axvline(0, color=INK, linestyle="--", linewidth=0.8, zorder=1)
        ax.set_xlim(10 * math.floor((min(limits) - 3) / 10), 10 * math.ceil((max(limits) + 3) / 10))
        ax.set_ylim(-0.55, len(names) - 0.45)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True, min_n_ticks=4))
        ax.set_xlabel("Measured minus predicted (%)", fontsize=10, color=MUTED, labelpad=7)
        ax.grid(axis="x", linewidth=0.55, color="#dde3e7")
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", colors=MUTED, labelsize=10, length=0, pad=5)
        ax.spines[["left", "top", "right"]].set_visible(False)
        ax.spines["bottom"].set_color("#bcc9d0")
    axes[0].set_yticks(range(len(names)), [SCENARIOS[n] for n in reversed(names)], ha="right", color=INK)
    fig.legend(
        handles=[Line2D([], [], linestyle="none", marker=marker, markersize=5,
                        color=color, label=label) for _, label, color, marker, _ in methods],
        loc="lower center", bbox_to_anchor=(0.54, 0.095), ncol=3, frameon=False, fontsize=10,
        handletextpad=0.55, columnspacing=1.5, labelcolor=INK,
    )
    fig.text(0.035, 0.065, "Open symbols show the earlier blocks. Filled symbols show the later blocks.",
             fontsize=9.8, color=MUTED)
    fig.text(0.035, 0.033, "Both printed scales use the volume forecast. The clear patch uses its own frozen pixel forecast.",
             fontsize=9.8, color=MUTED)
    fig.savefig(output, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scores", type=Path)
    parser.add_argument("attempts", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repeat-figure", type=Path)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.scores.read_text())
    figure(data, args.attempts, args.output, args.fresh)
    if args.repeat_figure:
        repeat_figure(data, args.repeat_figure)
