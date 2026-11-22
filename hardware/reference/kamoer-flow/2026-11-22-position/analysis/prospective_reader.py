#!/usr/bin/env python3
"""Read registered cup-surface position and printed-cup volume from an upright side image."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d, uniform_filter1d


def load_luma(path, rotate):
    image = Image.open(path)
    if rotate:
        image = image.transpose(Image.Transpose.ROTATE_180)
    if image.size != (2320, 1744):
        raise ValueError(f"expected an upright 2320×1744 sensor image, received {image.size}")
    return np.array(image.convert("L"))


def column_contact(profile, bounds):
    smooth = gaussian_filter1d(profile, 1.65)
    rows = np.arange(int(bounds[0]), int(bounds[1]) + 1)
    nearby = uniform_filter1d(smooth, 12)
    farther = uniform_filter1d(smooth, 22)
    above, below = nearby[rows - 11], nearby[rows + 11]
    deep = farther[rows + 33]
    contrast = np.minimum(above - below, above - deep)
    floor = np.percentile(smooth[rows[-1] + 22:rows[-1] + 74], 35)
    score = contrast - 0.7 * np.maximum(0, below - floor - 12)
    seed = rows[np.argmax(score)]
    # A local crossing trades sensitivity to a single gradient pixel for two intensity plateaus.
    light = np.median(smooth[seed - 16:seed - 6])
    dark = np.median(smooth[seed + 7:seed + 17])
    halfway = (light + dark) / 2
    window = np.arange(seed - 10, seed + 11)
    candidates = window[(smooth[window] >= halfway) & (smooth[window + 1] < halfway)]
    if not len(candidates):
        return None
    i = candidates[np.argmin(abs(candidates - seed))]
    crossing = i + (smooth[i] - halfway) / (smooth[i] - smooth[i + 1])
    gradient = np.maximum(0, -np.gradient(smooth)[window])
    centroid = float(np.average(window, weights=gradient)) if gradient.sum() else crossing
    if light - dark < 6:
        return None
    return float(crossing), centroid, float(light - dark)


def sightline(frame, spec):
    def measure(x):
        p = frame[:, x-5:x+6].mean(axis=1)
        return column_contact(p, spec["row_search"])
    samples = [(x, a) for x in spec["columns"] if (a := measure(x)) is not None]
    if len(samples) < 3:
        return {"ok": False, "reason": "contact contrast"}
    x = np.array([v[0] - spec["x"] for v in samples], dtype=float)
    crossing, centroid, contrast = np.array([v[1] for v in samples]).T
    # For this narrow field the local contact is sloped; evaluate at the same fixed x every time.
    slopes = [(crossing[j] - crossing[i]) / (x[j] - x[i]) for j in range(len(x)) for i in range(j)]
    slope = float(np.median(slopes))
    intercept = float(np.median(crossing - slope*x))
    keep = abs(crossing - (intercept + x*slope)) < 4.0
    if keep.sum() < 3:
        return {"ok": False, "reason": "spatial disagreement"}
    slope, intercept = np.polyfit(x[keep], crossing[keep], 1)
    alternate = float(np.median(centroid[keep] - slope*x[keep]))
    tr, tv = np.array(spec["marks"]).T
    return dict(ok=bool(abs(slope) < 0.48 and spec["row_search"][0]+2 < intercept < spec["row_search"][1]-2),
                row=round(float(intercept),4), alternative_row=round(alternate,4),
                nominal_ml=round(float(np.interp(intercept,tr,tv))*236.5882365,4),
                columns_used=int(keep.sum()), contrast=round(float(np.median(contrast[keep])),2))


def read(frame, cfg):
    lines = {name:sightline(frame, spec) for name,spec in cfg["sightlines"].items()}
    good = all(l["ok"] for l in lines.values())
    result = {"ok":bool(good), "right_y":lines["right"].get("row"), "left_y":lines["left"].get("row"),"sightlines":lines}
    if good:
        values = [l["nominal_ml"] for l in lines.values()]
        result["nominal_ml"] = round(float(np.mean(values)),3)
        result["side_difference_ml"] = round(max(values)-min(values),3)
        difference = lines["right"]["nominal_ml"] - lines["left"]["nominal_ml"]
        result["ok"] = abs(difference - cfg["reference_right_minus_left_ml"]) < 8
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("frame",type=Path)
    p.add_argument("--config",type=Path,default=Path(__file__).with_name("cup.json"))
    p.add_argument("--rotate",action="store_true")
    a=p.parse_args()
    path=a.frame / "average.png" if a.frame.is_dir() else a.frame
    print(json.dumps(read(load_luma(path,a.rotate),json.loads(a.config.read_text()))))


if __name__=="__main__":
    main()
