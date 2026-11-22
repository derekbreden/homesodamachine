#!/usr/bin/env python3
"""Resolve a stationary wall reflection with neighboring glass lanes before measuring the original x990 luma edge."""

import importlib.util
from pathlib import Path

import numpy as np
from scipy.ndimage import (
    gaussian_filter1d,
    maximum_filter1d,
    minimum_filter1d,
    uniform_filter1d,
)

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "unchanged_printed_cap_method", HERE / "mark_crossings.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original_clear_lane = base.clear_lane


def flank_candidate(gray, x):
    j = x - base.frozen.CROP[0]
    v = gaussian_filter1d(gray[:, j - 4 : j + 5].mean(1), 2.3)
    rows = np.arange(800, 1200) - base.frozen.CROP[1]
    g = v[rows - 5] - v[rows + 6]
    floor = np.percentile(v[170:570], 7)
    spread = (maximum_filter1d(v, 43) - minimum_filter1d(v, 43))[rows + 38]
    low = uniform_filter1d(v, 35)[rows + 35]
    score = np.maximum(0, g) / (
        (1 + (spread / 4.0) ** 1.2)
        * (1 + (np.maximum(0, low - floor - 1) / 7.0) ** 1.2)
    )
    i = rows[np.argmax(score)]
    return float(i + base.frozen.CROP[1]), float(g[np.argmax(score)])


def clear_lane(gray, site=990):
    y, contrast = original_clear_lane(gray, site)
    if site != 990:
        return y, contrast
    neighbors = []
    for x, offset in [(972, -3), (1018, 2), (1036, 3)]:
        yc, st = flank_candidate(gray, x)
        if st >= 7:
            neighbors.append(yc - offset)
    if len(neighbors) < 2:
        return y, contrast
    pairs = [
        (abs(a - b), (a + b) / 2)
        for i, a in enumerate(neighbors)
        for b in neighbors[i + 1 :]
    ]
    separation, pilot = min(pairs)
    if separation > 13 or abs(y - pilot) <= 13:
        return y, contrast
    j = site - base.frozen.CROP[0]
    v = gaussian_filter1d(gray[:, j - 4 : j + 5].mean(1), 2.3)
    rows = np.arange(round(pilot) - 13, round(pilot) + 14) - base.frozen.CROP[1]
    g = v[rows - 5] - v[rows + 6]
    k = rows[np.argmax(g)]
    idx = np.arange(k - 3, k + 4)
    center = (
        np.average(idx, weights=np.maximum(-np.gradient(v)[idx], 1e-5))
        + base.frozen.CROP[1]
    )
    return float(center), float(v[k - 5] - v[k + 6])


base.clear_lane = clear_lane
read = base.read


if __name__ == "__main__":
    base.main()
