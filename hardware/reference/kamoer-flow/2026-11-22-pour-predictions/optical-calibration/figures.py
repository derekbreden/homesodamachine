#!/usr/bin/env python3
"""Annotate original cup photographs with the accepted contacts, printed tips and independent clear-glass rows."""

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

import cup_volume
import left_ruler
import mark_crossings

HERE = Path(__file__).resolve().parent
BLUE = (26, 224, 251)
GREEN = (133, 249, 151)
MARK = (255, 204, 93)
WHITE = (241, 242, 240)
DARK = (26, 30, 32)


def font(size):
    for name in ("/System/Library/Fonts/Supplemental/Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def oriented_crop(path, rect):
    im = Image.open(path / "color.png").convert("RGB")
    if im.size != cup_volume.NATIVE:
        rect = tuple(v - cup_volume.CROP[i % 2] for i, v in enumerate(rect))
    return ImageEnhance.Brightness(im.crop(rect)).enhance(2.25)


def contact_panel(window, rect):
    color = oriented_crop(window, rect)
    left, top, _, _ = rect
    d = ImageDraw.Draw(color)
    s = cup_volume.read(window, True)
    rgb = np.asarray(cup_volume.crop(window / "color.png").convert("RGB"))
    ind = left_ruler.read(rgb, True)
    for a, c in [(s["primary"], BLUE), (ind, GREEN)]:
        if a.get("y") is None:
            continue
        for point in a.get("contacts", []):
            if point["used"]:
                x = point["x"] - left
                y = point["y"] - top
                d.line((x, y - 7, x, y - 2), fill=c, width=2)
        x = a["x"] - left
        y = a["y"] - top
        d.line((x - 9, y, x + 9, y), fill=c, width=2)
    q = mark_crossings.read(window)
    for k in ("quarter_one", "thirds_one"):
        a = q["marks"][k]
        if "cap_x" in a:
            x = a["cap_x"] - left
            y = a["cap_y"] - top
            d.ellipse((x - 4, y - 4, x + 4, y + 4), outline=MARK, width=2)
    return color, s["primary"], ind, q


def primary_figures(source, dest):
    dest.mkdir(parents=True, exist_ok=True)
    canonical = [
        "station-idle",
        "q1-post",
        "q2-post",
        "q5-post",
        "learn1-010-a-t-rich-post",
        "learn1-011-b-t-rich-entry",
    ]
    for label in canonical:
        if not (source / label / "color.png").exists():
            continue
        d = dest / "originals" / label
        d.mkdir(parents=True, exist_ok=True)
        for f in ("average.png", "color.png", "window.json", "color.json"):
            if not (d / f).is_file():
                shutil.copyfile(source / label / f, d / f)
    raw = dest / "originals"
    groups = [
        (
            "qualification.jpg",
            ["q5-post", "station-idle", "q1-post", "q2-post"],
            (955, 831, 2045, 1081),
            "Settled contact on the two printed scales",
        ),
        (
            "stationary-cup.jpg",
            canonical[-2:],
            (955, 900, 2045, 1030),
            "The left reading jumps between parked exposures",
        ),
    ]
    for name, labels, rect, title in groups:
        if not all((raw / l / "color.png").is_file() for l in labels):
            continue
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        hh = 67
        row_h = h + 37
        sheet = Image.new("RGB", (w, hh + row_h * len(labels) + 12), DARK)
        draw = ImageDraw.Draw(sheet)
        draw.text((14, 8), title, font=font(25), fill=WHITE)
        draw.text((15, 42), "Right thirds", font=font(16), fill=BLUE)
        draw.text((160, 42), "Independent left quarters", font=font(16), fill=GREEN)
        draw.text((434, 42), "One-cup graduation tips", font=font(16), fill=MARK)
        for i, label in enumerate(labels):
            img, right, left, q = contact_panel(raw / label, rect)
            y = hh + i * row_h
            draw.text(
                (14, y + 5),
                f"{label}    right {right.get('nominal_ml', 0):.2f} mL    left {left.get('nominal_ml', 0):.2f} mL    clear glass {q['clear_row']:.2f} px",
                font=font(17),
                fill=WHITE,
            )
            sheet.paste(img, (0, y + 33))
        sheet.save(dest / name, quality=90, optimize=True)


def ladder_figure(map_file, samples, dest):
    cfg = json.loads(map_file.read_text())
    provisional = "sources" in cfg or "source_crossings" in cfg
    g = cfg.get("source_crossings", cfg.get("sources", cfg.get("lowering", {})))
    keys = [
        k
        for k in (
            "quarter_three_quarters",
            "quarter_one",
            "quarter_one_and_quarter",
            "thirds_one",
        )
        if k in g
    ]
    if not keys:
        return
    boxw, boxh = 310, 106
    sheet = Image.new("RGB", (2 * boxw + 22, len(keys) * (boxh + 50) + 65), DARK)
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (10, 9),
        "Printed crossings for the provisional scale"
        if provisional
        else "Front graduation crossings during lowering",
        font=font(24),
        fill=WHITE,
    )
    draw.text(
        (11, 39),
        "Gold circle shows the printed tip. Cyan dots follow the nearby liquid.",
        font=font(14),
        fill=WHITE,
    )
    for i, k in enumerate(keys):
        sample = g[k]["brackets"][0]
        labels = sample["labels"]
        direction = (
            "Rising"
            if provisional and "rising" in g[k].get("direction", g[k].get("method", ""))
            else "Lowering"
        )
        y = 64 + i * (boxh + 50)
        for j, label in enumerate(labels):
            d = samples / label
            source_name = {
                "mark_crossings_v2": "cap-reading-v2.json",
                "mark_crossings_v3": "cap-reading-v3.json",
            }.get(cfg.get("clear_lane_reader"), "cap-reading.json")
            v = json.loads((d / source_name).read_text())
            m = v["marks"][k]
            cx, cy = round(m["cap_x"]), round(m["cap_y"])
            xlo = int(
                np.clip(cx - boxw // 2, cup_volume.CROP[0], cup_volume.CROP[2] - boxw)
            )
            ylo = int(
                np.clip(cy - boxh // 2, cup_volume.CROP[1], cup_volume.CROP[3] - boxh)
            )
            rect = (xlo, ylo, xlo + boxw, ylo + boxh)
            im = oriented_crop(d, rect)
            ink = ImageDraw.Draw(im)
            ox, oy = rect[:2]
            ink.ellipse(
                (cx - ox - 4, cy - oy - 4, cx - ox + 4, cy - oy + 4),
                outline=MARK,
                width=2,
            )
            for x, p, contrast, group in m["patches"]:
                if abs(x - cx) <= 43:
                    ink.ellipse((x - ox - 1, p - oy - 2, x - ox + 1, p - oy), fill=BLUE)
            l = 8 + j * (boxw + 6)
            draw.text(
                (l, y),
                f"{direction} {m['cup_ml']:.1f} mL    Δ row {m['contact_minus_ink_px']:+.1f}",
                font=font(16),
                fill=WHITE,
            )
            sheet.paste(im, (l, y + 22))
            draw.text((l, y + boxh + 24), label, font=font(12), fill=WHITE)
    sheet.save(
        dest
        / (
            "forecast-graduations.jpg"
            if "source_crossings" in cfg
            else (
                "provisional-graduations.jpg"
                if provisional
                else "graduation-crossings.jpg"
            )
        ),
        quality=92,
        optimize=True,
    )


def upper_failure_figure(source, dest):
    high = source / "ladder4-up-high-09"
    cap = source / "ladder5-return-station-07"
    if (
        not (high / "cap-reading-v2.json").is_file()
        or not (cap / "cap-reading-v3.json").is_file()
    ):
        return
    early = json.loads((high / "cap-reading-v2.json").read_text())
    fixed = json.loads((high / "cap-reading-v3.json").read_text())
    mark = json.loads((cap / "cap-reading-v3.json").read_text())["marks"][
        "quarter_one_and_quarter"
    ]
    first = (950, 801, 1150, 906)
    second = (1002, 790, 1202, 895)
    sheet = Image.new("RGB", (823, 334), DARK)
    d = ImageDraw.Draw(sheet)
    d.text(
        (11, 9), "Two optical limits at the upper graduation", font=font(24), fill=WHITE
    )
    for x, path, rect in [(8, high, first), (415, cap, second)]:
        photo = oriented_crop(path, rect).resize((400, 210))
        ink = ImageDraw.Draw(photo)
        if path == high:
            xx = (990 - rect[0]) * 2
            for y, col in [(fixed["clear_row"], BLUE), (early["clear_row"], MARK)]:
                yy = (y - rect[1]) * 2
                ink.line((xx - 9, yy, xx + 9, yy), fill=col, width=3)
        else:
            cx = (mark["cap_x"] - rect[0]) * 2
            cy = (mark["cap_y"] - rect[1]) * 2
            ink.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=MARK, width=2)
            for xx, yy, _, _ in mark["patches"]:
                if abs(xx - mark["cap_x"]) < 45:
                    xx = (xx - rect[0]) * 2
                    yy = (yy - rect[1]) * 2
                    ink.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=BLUE)
        sheet.paste(photo, (x, 51))
    d.text((9, 268), f"Liquid row {fixed['clear_row']:.1f}", font=font(17), fill=BLUE)
    d.text(
        (9, 291),
        f"Neighbor correction chose row {early['clear_row']:.1f}",
        font=font(16),
        fill=MARK,
    )
    d.text(
        (415, 268),
        "Lowering contact beside the upper printed cap",
        font=font(16),
        fill=WHITE,
    )
    d.text(
        (415, 291),
        f"Local tangent disagrees by {abs(mark['tangent_minus_adjacent_median_px']):.1f} px",
        font=font(16),
        fill=WHITE,
    )
    d.text((9, 315), high.name, font=font(12), fill=WHITE)
    d.text((415, 315), cap.name, font=font(12), fill=WHITE)
    sheet.save(dest / "upper-measurement-limits.jpg", quality=92, optimize=True)


def reflection_figure(source, dest):
    q = source / "ladder1-down-low-14"
    old = q / "cap-reading.json"
    new = q / "cap-reading-v2.json"
    if not old.is_file() or not new.is_file():
        return
    v1 = json.loads(old.read_text())
    v2 = json.loads(new.read_text())
    rect = (954, 1050, 1100, 1195)
    im = oriented_crop(q, rect).resize((438, 435))
    drawing = ImageDraw.Draw(im)
    x = (990 - rect[0]) * 3
    for row, color in [(v1["clear_row"], MARK), (v2["clear_row"], BLUE)]:
        y = round((row - rect[1]) * 3)
        drawing.line((x - 17, y, x + 17, y), fill=color, width=3)
    sheet = Image.new("RGB", (680, 485), DARK)
    sheet.paste(im, (0, 50))
    d = ImageDraw.Draw(sheet)
    d.text(
        (12, 10), "A stationary wall edge in the wide scan", font=font(24), fill=WHITE
    )
    for off, data, color, name in [
        (88, v2, BLUE, "Near-wall liquid"),
        (270, v1, MARK, "Stationary reflection"),
    ]:
        d.text((454, off), name, font=font(17), fill=color)
        d.text(
            (454, off + 31),
            f"x990 row {data['clear_row']:.2f}",
            font=font(16),
            fill=WHITE,
        )
    sheet.save(dest / "wide-search-reflection.jpg", quality=91, optimize=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", type=Path)
    p.add_argument("--out", type=Path, default=HERE / "photos")
    p.add_argument("--map", type=Path, default=HERE / "geometry-map.json")
    p.add_argument("--graduations", type=Path, default=HERE / "evidence/graduations")
    a = p.parse_args()
    if a.windows:
        primary_figures(a.windows, a.out)
    if a.map.is_file():
        ladder_figure(a.map, a.graduations, a.out)
    reflection_figure(a.graduations, a.out)
    upper_failure_figure(a.graduations, a.out)
