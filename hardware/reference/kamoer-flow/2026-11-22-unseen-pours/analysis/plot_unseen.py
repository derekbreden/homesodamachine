"""Plot each reserved serving's two optical dose errors against its frozen practical band."""
import argparse
import csv
import json
import math
import textwrap
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator


STUDY = Path(__file__).resolve().parents[1]
INK = "#182e39"
MUTED = "#52656f"
NEAR = "#14638a"
FAR = "#a14b13"
BAND = "#dceee5"
BAND_EDGE = "#89ad9b"


def rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def number(value):
    if value is None or value == "":
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def flag(value):
    if value is None or str(value).strip() == "":
        return None
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def error(row, lane, forecast):
    residual = number(row.get(f"{lane}_error_ml"))
    if residual is not None:
        return residual
    dose = number(row.get(f"{lane}_dose_ml"))
    if dose is not None and forecast is not None:
        return dose - forecast
    return None


def disposition(summary):
    status = flag(summary.get("both_pass"))
    if status is None:
        return "Unscored", MUTED
    if status:
        return "Pass", "#235f48"
    misses = [lane for lane in ("near", "far") if flag(summary.get(f"{lane}_pass")) is False]
    label = {"near": "Near misses", "far": "Far misses", "near far": "Both miss"}.get(" ".join(misses), "Miss")
    return label, "#963b2e"


def plot(attempts, summaries, design, output):
    summaries = {(r["head"], r["scenario"]): r for r in summaries}
    pours = defaultdict(dict)
    for r in attempts:
        pours[r["head"], r["scenario"]][int(r["block"])] = r
    scenarios = dict(design["scenarios"])
    blocks = sorted({int(entry["block"]) for entry in design["order"]})
    extent = [1.0]
    for r in summaries.values():
        tolerance = number(r.get("tolerance_ml"))
        if tolerance is not None:
            extent.append(tolerance)
    for r in attempts:
        for lane in ("near", "far"):
            value = error(r, lane, number(r.get("forecast_ml")))
            if value is not None:
                extent.append(abs(value))

    fig, axes = plt.subplots(1, 2, sharex=True, sharey=True,
                             figsize=(13, 2.45 + 1.15 * len(scenarios)), facecolor="white")
    fig.subplots_adjust(left=.208, right=.901, top=.79, bottom=.105, wspace=.41)
    fig.suptitle("Concentrate dose errors on unseen lever programs", x=.026, y=.973,
                 ha="left", fontsize=21, fontweight="bold", color=INK)
    fig.text(.027, .918, "Each linked pair shows two camera readings of the same serving.",
             color=MUTED, fontsize=11)
    step = len(blocks) + 1.45
    centers = [i * step + (len(blocks) - 1) / 2 for i in range(len(scenarios))]
    any_unscored = False

    for ax, head in zip(axes, "AB"):
        ax.set_axisbelow(True)
        ax.grid(axis="x", linewidth=.65, color="#e0e5e7")
        ax.axvline(0, color="#46555b", linewidth=1, zorder=2)
        ax.set_title(f"Head {head}", loc="left", fontsize=15, fontweight="bold", pad=13, color=INK)
        axis_row = ax.get_yaxis_transform()
        ax.text(1.035, 1.022, "Forecast / test", transform=ax.transAxes, ha="left", va="bottom",
                color=MUTED, fontsize=8)
        for group_index, name in enumerate(scenarios):
            summary = summaries.get((head, name), {})
            forecast = number(summary.get("forecast_ml"))
            tolerance = number(summary.get("tolerance_ml"))
            group_start = group_index * step
            if tolerance is not None:
                ax.fill_betweenx([group_start - .49, group_start + len(blocks) - .51],
                                 -tolerance, tolerance, color=BAND, zorder=.6)
                for boundary in (-tolerance, tolerance):
                    ax.vlines(boundary, group_start - .49, group_start + len(blocks) - .51,
                              colors=BAND_EDGE, linewidth=.7, zorder=.8)
            ax.text(1.035, centers[group_index] - .53,
                    "—" if forecast is None else f"{forecast:.1f} mL",
                    transform=axis_row, va="center", ha="left", fontsize=9.5, color=INK)
            result, color = disposition(summary)
            ax.text(1.035, centers[group_index] + .76, result, transform=axis_row,
                    va="center", ha="left", fontsize=9, fontweight="bold", color=color)
            for block_index, block in enumerate(blocks):
                row = pours[head, name].get(block, {})
                y = group_start + block_index
                near, far = (error(row, lane, forecast) for lane in ("near", "far"))
                eligible = flag(row.get("eligible")) is True and near is not None and far is not None
                any_unscored |= not eligible
                ax.text(-.017, y, f"{block}" if eligible else f"{block}×", transform=axis_row,
                        ha="right", va="center", color=MUTED if eligible else "#853e34", fontsize=7)
                if near is not None and far is not None:
                    ax.plot([near, far], [y - .17, y + .17], color="#717c82", linewidth=.85, zorder=3)
                if near is not None:
                    ax.plot(near, y - .17, marker="o", markersize=3.8, linestyle="none",
                            markerfacecolor=NEAR if eligible else "white", markeredgecolor=NEAR, zorder=4)
                if far is not None:
                    ax.plot(far, y + .17, marker="^", markersize=4.3, linestyle="none",
                            markerfacecolor="white", markeredgecolor=FAR, markeredgewidth=1.1, zorder=5)

        ax.set_xlim(-max(extent) * 1.07, max(extent) * 1.07)
        ax.set_ylim(centers[-1] + len(blocks) / 2 + .16, -.68)
        ax.set_yticks(centers)
        ax.tick_params(axis="y", length=0, pad=23, colors=INK, labelsize=10)
        ax.tick_params(axis="x", colors=MUTED, labelsize=9, length=3)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=6, symmetric=True))
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#96a2a6")
        ax.set_xlabel("Measured dose minus forecast (mL)", color=INK, fontsize=10, labelpad=7)

    labels = [textwrap.fill(details.get("name", key.replace("_", " ")), width=23)
              for key, details in scenarios.items()]
    axes[0].set_yticklabels(labels, ha="right")
    handles = [
        Line2D([], [], color=NEAR, marker="o", linestyle="none", markersize=5, label="Near sightline"),
        Line2D([], [], markeredgecolor=FAR, markerfacecolor="white", marker="^", linestyle="none",
               markersize=6, label="Far sightline"),
        Patch(facecolor=BAND, edgecolor=BAND_EDGE, label="Practical dose tolerance"),
        Line2D([], [], color="#46555b", linewidth=1.2, label="Forecast"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.022, .893), ncols=len(handles),
               frameon=False, borderaxespad=0, handlelength=1.6, columnspacing=1.9,
               fontsize=9.5, labelcolor=INK)
    foot = "Blocks run from top to bottom in each program. Pass requires both sightlines to meet the coverage and mean-bias limits."
    if any_unscored:
        foot += "  × marks an unscored block."
    fig.text(.027, .036, foot, color=MUTED, fontsize=9)
    fig.savefig(output, dpi=160, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempts", type=Path, default=STUDY / "results/attempts.csv")
    parser.add_argument("--by-program", type=Path, default=STUDY / "results/by-program.csv")
    parser.add_argument("--design", type=Path, default=STUDY / "design.json")
    parser.add_argument("--output", type=Path, default=STUDY / "results/unseen-pours.png")
    args = parser.parse_args()
    plot(rows(args.attempts), rows(args.by_program), json.loads(args.design.read_text()), args.output)


if __name__ == "__main__":
    main()
