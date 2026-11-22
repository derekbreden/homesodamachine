#!/usr/bin/env python3
"""Distinguish the returned liquid contact from the strongest brightness transition on the same glass strip."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from scipy.ndimage import gaussian_filter1d

import cup_volume
import geometry_volume
from clear_photos import preserve
from figures import BLUE, DARK, WHITE, MARK, font
from fit_geometry import read_log

HERE = Path(__file__).resolve().parent


def measure(frame, model):
    gray = np.asarray(cup_volume.crop(frame / "average.png").convert("L"))
    readings = geometry_volume.from_gray(gray, model)
    result = {}
    for x, center in ((990, 989), (1986, 932)):
        offset = cup_volume.CROP[1]
        j = x - cup_volume.CROP[0]
        profile = gaussian_filter1d(gray[:, j - 4 : j + 5].mean(1), 2.3)
        tested = np.arange(center - 110, center + 122) - offset
        g = profile[tested - 5] - profile[tested + 6]
        peak = tested[int(np.argmax(g))]
        nearby = np.arange(peak - 3, peak + 4)
        raw = float(
            np.average(nearby, weights=np.maximum(-np.gradient(profile)[nearby], 1e-5))
            + offset
        )
        site = "x" + str(x)
        at = readings[site]
        record = {
            "wide_row": raw,
            "wide_gradient": float(np.max(g)),
            "qualified_row": at["row"],
            "qualified_gradient": at["contrast"],
            "qualified_ml": at["nominal_ml"],
            "wide_minus_qualified_px": raw - at["row"],
        }
        for name, y in (("wide", raw), ("qualified", at["row"])):
            i = round(y) - offset
            underneath = profile[i + 17 : i + 60]
            record[name + "_below_mean_luma"] = float(np.mean(underneath))
            record[name + "_below_luma_span"] = float(np.ptp(underneath))
        result[site] = record
    return result


def draw(rows, dest):
    w, h = 330, 196
    sheet = Image.new("RGB", (len(rows) * (w + 8) + 8, 345), DARK)
    canvas = ImageDraw.Draw(sheet)
    canvas.text(
        (10, 8), "The far-glass contact on return", font=font(23), fill=WHITE
    )
    canvas.text(
        (10, 39),
        "Mean luma at the opposite glass sightline. All panels use the same crop.",
        font=font(15),
        fill=WHITE,
    )
    ox, oy, x1, y1 = 1800, 817, 2045, 963
    sx = w / (x1 - ox)
    sy = h / (y1 - oy)
    for index, (label, name, path, reading) in enumerate(rows):
        xoff = 8 + (w + 8) * index
        source = cup_volume.crop(path / "average.png").convert("L")
        photo = source.crop(
            (
                ox - cup_volume.CROP[0],
                oy - cup_volume.CROP[1],
                x1 - cup_volume.CROP[0],
                y1 - cup_volume.CROP[1],
            )
        )
        photo = (
            ImageEnhance.Brightness(photo.resize((w, h))).enhance(2.5).convert("RGB")
        )
        draw = ImageDraw.Draw(photo)
        info = reading["x1986"]
        x = (1986 - ox) * sx
        for key, color in (("wide_row", MARK), ("qualified_row", BLUE)):
            y = (info[key] - oy) * sy
            if key == "wide_row":
                draw.line((x - 19, y, x - 8, y), fill=color, width=3)
            else:
                draw.line((x + 2, y, x + 16, y), fill=color, width=3)
        canvas.text((xoff, 66), name, font=font(18), fill=WHITE)
        sheet.paste(photo, (xoff, 91))
        canvas.text(
            (xoff, 290),
            f"Strongest gradient   {info['wide_row']:.2f} px",
            font=font(14),
            fill=MARK,
        )
        canvas.text(
            (xoff, 310),
            f"Liquid contact            {info['qualified_row']:.2f} px",
            font=font(14),
            fill=BLUE,
        )
        canvas.text((xoff, 330), label, font=font(11), fill=WHITE)
    sheet.save(dest, quality=93, optimize=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument("--windows", type=Path)
    p.add_argument("--photos", type=Path, default=HERE / "photos")
    p.add_argument("--map", type=Path, default=HERE / "geometry-used.json")
    p.add_argument("--evidence", type=Path, default=HERE / "evidence")
    p.add_argument(
        "--out", type=Path, default=HERE / "geometry-results/return-edges.json"
    )
    a = p.parse_args()
    model = json.loads(a.map.read_text())
    labels = {"station-idle": ("Original station", {})}
    for fname, descr in (
        ("return.jsonl", "After fill trials"),
        ("return-final.jsonl", "After repeat trials"),
    ):
        receipt = next(
            (r for r in read_log(a.logs / fname) if r["event"] == "station_position"),
            None,
        )
        if receipt:
            labels[receipt["first_window"]] = (
                "Original station",
                {v[0]: v[1] for v in receipt["initial"]},
            )
            labels[receipt["last_window"]] = (
                descr,
                {v[0]: v[1] for v in receipt["final"]},
            )
    data = {}
    visual = []
    for label, (descr, logged) in labels.items():
        path = preserve(label, a.windows, a.photos, a.evidence)
        found = measure(path, model)
        for x in (990, 1986):
            q = found["x" + str(x)]
            q["logged_wide_row"] = logged.get(x)
            if x in logged and round(q["wide_row"], 3) != logged[x]:
                raise ValueError(
                    label + " original wide-scan replay differs at " + str(x)
                )
        data[label] = found
        visual.append((label, descr, path, found))
    a.out.write_text(json.dumps(data, indent=2) + "\n")
    if len(visual) > 1:
        draw(visual, a.photos / "return-edge-selection.jpg")


if __name__ == "__main__":
    main()
