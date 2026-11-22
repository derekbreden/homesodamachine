#!/usr/bin/env python3
"""Calibrate the clear operating strip from observed foreground contact crossings at the ends of front graduations."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import (
    gaussian_filter1d,
    maximum_filter1d,
    minimum_filter1d,
    uniform_filter1d,
)

import cup_volume as frozen

# The endpoint of each fixed red bar and its nearby clear lanes are photograph features.
# Positive direction walks from the cap into the continuous printed segment.
MARKS = {
    "quarter_three_quarters": {
        "cups": 0.75,
        "cap": 1188,
        "site": 1220,
        "site_y": 1131,
        "slope": 0.074,
        "into": 1,
        "clear": [(-109, -89), (-47, -32), (-13, -5)],
    },
    "quarter_one": {
        "cups": 1.0,
        "cap": 1054,
        "site": 1220,
        "site_y": 991,
        "slope": 0.030,
        "into": 1,
        "clear": [(-31, -11)],
    },
    "quarter_one_and_quarter": {
        "cups": 1.25,
        "cap": 1131,
        "site": 1220,
        "site_y": 836,
        "slope": -0.039,
        "into": 1,
        "clear": [(-104, -85), (-43, -34), (-16, -5)],
    },
    "thirds_one": {
        "cups": 1.0,
        "cap": 1960,
        "site": 1730,
        "site_y": 977,
        "slope": -0.109,
        "into": -1,
        "clear": [(11, 42)],
    },
}


def weighted_center(col, y):
    yy = np.arange(round(y) - 19, round(y) + 20)
    v = col[yy - frozen.CROP[1]]
    w = np.maximum(0, v - np.percentile(v, 15))
    w[w < 0.48 * w.max()] = 0
    if w.max() < 7:
        return None
    return float(np.average(yy, weights=w))


def printed_tip(rgb, m):
    cx = m["cap"]
    direction = m["into"]
    x0 = frozen.CROP[0]
    r, g, b = np.moveaxis(rgb.astype(np.float32), 2, 0)
    pig = r - np.maximum(1.27 * g, 1.13 * b)
    xs = np.arange(cx + direction * 12, cx + direction * 73, direction * 3)
    cy = [
        weighted_center(pig[:, x - x0], m["site_y"] + m["slope"] * (x - m["site"]))
        for x in xs
    ]
    ok = np.array([v is not None for v in cy])
    if ok.sum() < 8:
        raise ValueError("red graduation too weak")
    values = np.array([v if v is not None else 0 for v in cy])
    slope, inter = np.polyfit(xs[ok] - cx, values[ok], 1)
    err = np.median(abs(values[ok] - (slope * (xs[ok] - cx) + inter)))
    scan = np.arange(cx - direction * 11, cx + direction * 16, direction)
    inten = []
    for x in scan:
        y = round(inter + slope * (x - cx)) - frozen.CROP[1]
        inten.append(float(np.median(pig[y - 3 : y + 4, x - x0 - 1 : x - x0 + 2])))
    val = gaussian_filter1d(inten, 1)
    base = np.median(val[:4])
    peak = np.median(val[-5:])
    target = base + 0.5 * (peak - base)
    idx = np.flatnonzero((val[:-1] <= target) & (val[1:] > target))
    if not len(idx) or peak - base < 6:
        raise ValueError("unresolved printed cap")
    i = idx[np.argmin(abs(scan[idx] - cx))]
    real = scan[i] + direction * (target - val[i]) / (val[i + 1] - val[i])
    return (
        float(real),
        float(inter + slope * (real - cx)),
        float(slope),
        float(err),
        float(peak),
    )


def clear_lane(gray, site=990):
    # This matches the operating estimator's local edge definition and extends its search at the outer graduations.
    x = site - frozen.CROP[0]
    signal = gaussian_filter1d(gray[:, x - 4 : x + 5].mean(1), 2.3)
    rows = (
        np.arange(800, 1200) if site == 990 else np.arange(720, 1165)
    ) - frozen.CROP[1]
    g = signal[rows - 5] - signal[rows + 6]
    floor = np.percentile(signal[170:570], 7)
    spread = (maximum_filter1d(signal, 43) - minimum_filter1d(signal, 43))[rows + 38]
    low = uniform_filter1d(signal, 35)[rows + 35]
    score = np.maximum(0, g) / (
        (1 + (spread / 4.0) ** 1.2)
        * (1 + (np.maximum(0, low - floor - 1) / 7.0) ** 1.2)
    )
    i = rows[np.argmax(score)]
    near = np.arange(i - 6, i + 7)
    k = near[np.argmax(signal[near - 5] - signal[near + 6])]
    z = np.arange(k - 3, k + 4)
    y = (
        np.average(z, weights=np.maximum(-np.gradient(signal)[z], 1e-5))
        + frozen.CROP[1]
    )
    return float(y), float(signal[k - 5] - signal[k + 6])


def contact(gray, rgb, x, x_lane, side, pigment_cutoff):
    j = x - frozen.CROP[0]
    r, g, b = rgb[:, j - 1 : j + 2].mean(1).T
    raw = gray[:, j - 1 : j + 2].mean(1)
    v = gaussian_filter1d(raw, 1.45)
    # The center seeds only the foreground neighborhood. The independent sign of the crossing comes from the liquid and red stroke.
    if side == "right":
        pred = x_lane + np.interp(x, [1910, 1990, 2030], [-50, -57, -64])
        margin = 26
    else:
        pred = x_lane + np.interp(x, [980, 1040, 1110, 1190], [-1, 0, -1, -7])
        margin = 23
    ii = np.arange(round(pred - margin), round(pred + margin) + 1) - frozen.CROP[1]
    drop = v[ii - 5] - v[ii + 5]
    plateau = (maximum_filter1d(v, 22) - minimum_filter1d(v, 22))[ii + 22]
    pigment = r - np.maximum(g * 1.32, b * 1.13)
    ink = maximum_filter1d((pigment > pigment_cutoff).astype(int), 5).astype(bool)
    score = np.maximum(drop, 0) / (1 + np.maximum(0, plateau - 2) / 7)
    score[ink[ii]] = 0
    if score.max() < 3:
        return None
    k = ii[np.argmax(score)]
    grid = np.arange(k - 6, k + 7)
    gg = np.maximum(-np.gradient(v)[grid], 0)
    cy = float(np.average(grid, weights=gg)) + frozen.CROP[1]
    if np.any(ink[round(cy) - frozen.CROP[1] - 3 : round(cy) - frozen.CROP[1] + 4]):
        return None
    return cy, float(v[k - 6] - v[k + 6])


def read(window):
    gray = np.asarray(frozen.crop(window / "average.png").convert("L"))
    rgb = np.asarray(frozen.crop(window / "color.png").convert("RGB"))
    lane, contrast = clear_lane(gray)
    right, right_contrast = clear_lane(gray, 1986)
    out = {}
    for name, m in MARKS.items():
        try:
            cx, cy, slope, ink_err, pigment_peak = printed_tip(rgb, m)
        except ValueError as e:
            out[name] = {"ok": False, "flags": [str(e)]}
            continue
        strips = []
        for i, (lo, hi) in enumerate(m["clear"]):
            for x in range(round(cx) + lo, round(cx) + hi + 1, 2):
                v = contact(
                    gray,
                    rgb,
                    x,
                    lane,
                    "right" if m["into"] < 0 else "left",
                    max(14.0, 0.34 * pigment_peak),
                )
                if v is not None:
                    strips.append((x, v[0], v[1], i))
        flags = []
        base = {
            "cup_ml": m["cups"] * frozen.CUP_ML,
            "cap_x": cx,
            "cap_y": cy,
            "mark_slope": slope,
            "ink_fit_mad_px": ink_err,
        }
        if len(strips) < 3:
            out[name] = dict(**base, ok=False, flags=["few clear local strips"])
            continue
        a = np.array(strips)
        dx = a[:, 0] - cx
        delta = a[:, 1] - (cy + slope * dx)
        # The nearest clear glass constrains the cap. The farther windows expose curvature and numeral occlusion.
        near = abs(dx) < 43
        close = abs(dx) < 20
        if not near.any():
            out[name] = dict(
                **base, ok=False, flags=["no immediately adjacent clear glass"]
            )
            continue
        near_dx = dx[near]
        near_delta = delta[near]
        adjacent = float(np.median(near_delta))
        # A local line carries the measured clear liquid to the physical end of the ink.
        # Pairwise slopes separated in x suppress pixel quantization and isolated reflections.
        slopes = [
            (near_delta[j] - near_delta[i]) / (near_dx[j] - near_dx[i])
            for i in range(len(near_dx))
            for j in range(i + 1, len(near_dx))
            if abs(near_dx[j] - near_dx[i]) >= 7
        ]
        local_slope = float(np.median(slopes)) if slopes else 0.0
        if abs(local_slope) > 0.38:
            flags.append("unstable foreground tangent at cap")
        step = float(np.median(near_delta - local_slope * near_dx))
        spread = float(np.median(abs(near_delta - local_slope * near_dx - step)))
        close_step = (
            float(np.median(delta[close] - local_slope * dx[close]))
            if close.any()
            else None
        )
        if close_step is None:
            flags.append("no clear strip within the local cap neighborhood")
        elif abs(close_step - step) > 3:
            flags.append("local flanks disagree")
        if near.sum() < 3:
            flags.append("few adjacent strips")
        if spread > 3.0:
            flags.append("broad or split contact")
        if abs(step) > 30:
            flags.append("outside local crossing bracket")
        out[name] = dict(
            **base,
            ok=not flags,
            flags=flags,
            contact_minus_ink_px=step,
            tangent_minus_adjacent_median_px=step - adjacent,
            local_contact_minus_ink_slope=local_slope,
            adjacent_mad_px=spread,
            nearest_clear_dx_px=float(min(abs(dx))),
            near_patches=int(near.sum()),
            all_patches=len(strips),
            close_minus_adjacent_px=None if close_step is None else close_step - step,
            patches=[
                [int(x), round(yy, 3), round(st, 2), int(group)]
                for x, yy, st, group in strips
            ],
        )
    return {
        "label": window.name,
        "clear_row": lane,
        "clear_contrast": contrast,
        "right_clear_row": right,
        "right_clear_contrast": right_contrast,
        "marks": out,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("windows", type=Path, nargs="+")
    p.add_argument("--out", type=Path)
    p.add_argument("--brief", action="store_true")
    a = p.parse_args()
    r = [read(w) for w in a.windows]
    if a.brief:
        r = [
            {
                "label": v["label"],
                "clear_row": v["clear_row"],
                "marks": {
                    k: {
                        name: z
                        for name, z in b.items()
                        if name
                        in (
                            "ok",
                            "flags",
                            "cap_x",
                            "cap_y",
                            "contact_minus_ink_px",
                            "adjacent_mad_px",
                        )
                    }
                    for k, b in v["marks"].items()
                },
            }
            for v in r
        ]
    data = json.dumps(r, indent=2, allow_nan=False) + "\n"
    if a.out:
        a.out.write_text(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
