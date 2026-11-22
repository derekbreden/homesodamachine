#!/usr/bin/env python3
"""Plot paired optical dose disagreement on the same photographed pours."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

HERE = Path(__file__).resolve().parent
SERIES = (
    (
        "Printed-scale readers",
        "printed_right_minus_independent_left_ml",
        "#9a452e",
        "--",
    ),
    ("Clear-glass readers", "clear_primary_minus_opposite_ml", "#006a70", "-"),
)


def draw(table, output):
    with table.open() as f:
        rows = list(csv.DictReader(f))
    fig, (ax, details) = plt.subplots(
        1, 2, figsize=(8.6, 4.4), gridspec_kw={"width_ratios": [3.3, 1.18]}
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.78, bottom=0.19, wspace=0.21)
    fig.text(
        0.085,
        0.93,
        "How closely two optical sightlines agree",
        size=18,
        weight="semibold",
        color="#232b30",
    )
    fig.text(
        0.086,
        0.86,
        f"Both reader pairs measured the same {len(rows)} held-out pours.",
        size=10,
        color="#414b50",
    )
    details.axis("off")
    for i, (label, field, color, style) in enumerate(SERIES):
        d = np.sort(np.abs([float(r[field]) for r in rows]))
        y = np.arange(1, len(d) + 1) / len(d)
        ax.step(
            np.r_[0, d],
            np.r_[0, y],
            where="post",
            color=color,
            linestyle=style,
            linewidth=2.3,
            label=label,
        )
        title_y = 0.87 - 0.48 * i
        details.text(0, title_y, label, fontsize=11, weight="semibold", color=color)
        median, p95 = np.quantile(d, (0.5, 0.95))
        for j, (quantity, v) in enumerate(
            (("Median", median), ("95th percentile", p95), ("Maximum", d[-1]))
        ):
            loc = title_y - 0.105 * (j + 1)
            details.text(0, loc, quantity, fontsize=9.5, color="#394246")
            details.text(
                1, loc, f"{v:.2f} mL", fontsize=9.5, ha="right", color="#202528"
            )
    ax.set(
        xlim=(0, None),
        ylim=(0, 1.04),
        xlabel="Absolute difference in measured dose (nominal mL)",
        ylabel="Share of pours",
    )
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.spines[["right", "top"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linewidth=0.7)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.text(
        0.086,
        0.045,
        "The readings share one camera and cup. The vertical axis counts pours at or below each difference.",
        size=8.5,
        color="#505b61",
    )
    fig.savefig(output, dpi=185, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--table",
        type=Path,
        default=HERE / "geometry-results/same-pour-method-comparison.csv",
    )
    parser.add_argument(
        "--out", type=Path, default=HERE / "photos/same-pour-optical-agreement.png"
    )
    args = parser.parse_args()
    draw(args.table, args.out)
