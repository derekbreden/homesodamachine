#!/usr/bin/env python3
"""Show the measured contacts in representative settled pour and return photographs."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

import cup_volume
import geometry_volume
from figures import BLUE, DARK, GREEN, WHITE, font
from fit_geometry import read_log
from replay import sha

HERE = Path(__file__).resolve().parent


def preserve(label, windows, dest, evidence):
    out = dest / "clear-examples" / label
    out.mkdir(parents=True, exist_ok=True)
    if windows is not None and not (out / "source.json").exists():
        native = windows / label
        proof = json.loads((evidence / "windows" / label / "capture.json").read_text())
        info = {
            "native_hashes": proof["full_sha256"],
            "crop_ltrb": cup_volume.CROP,
            "crop_sha256": {},
        }
        for name in ("average.png", "color.png"):
            cup_volume.crop(native / name).save(out / name, compress_level=7)
            info["crop_sha256"][name] = sha(out / name)
        (out / "source.json").write_text(json.dumps(info, indent=2) + "\n")
    return out


def panels(title, pairs, windows, dest, model, evidence, output):
    pw, ph = 315, 126
    margin, header, metadata = 12, 78, 104
    width = 2 * pw + 3 * margin
    image = Image.new(
        "RGB", (width, header + len(pairs) * (2 * ph + metadata) + margin), DARK
    )
    draw = ImageDraw.Draw(image)
    draw.text((margin, 9), title, fill=WHITE, font=font(24))
    draw.text(
        (margin, 41),
        "Settled mean luma, brightened. Ticks mark each measured liquid contact.",
        fill=WHITE,
        font=font(14),
    )
    for i, (tag, pre, post) in enumerate(pairs):
        paths = [preserve(label, windows, dest, evidence) for label in (pre, post)]
        readings = [geometry_volume.read(p, model) for p in paths]
        top = header + i * (2 * ph + metadata)
        draw.text((margin, top), tag, fill=WHITE, font=font(18))
        for j, (x, c, x0) in enumerate([(990, BLUE, 950), (1986, GREEN, 1730)]):
            site = "x" + str(x)
            left = margin + j * (pw + margin)
            ys = [r[site]["row"] for r in readings]
            y0 = round(sum(ys) / len(ys) - ph / 2)
            xcrop = x0 - cup_volume.CROP[0]
            ycrop = y0 - cup_volume.CROP[1]
            draw.text(
                (left, top + 24),
                f"{'Primary' if j == 0 else 'Opposite glass'}   x = {x}",
                fill=c,
                font=font(15),
            )
            for k, (img, r, label) in enumerate(zip(paths, readings, (pre, post))):
                q = r[site]
                with Image.open(img / "average.png") as source:
                    patch = (
                        ImageEnhance.Brightness(
                            source.crop((xcrop, ycrop, xcrop + pw, ycrop + ph))
                        )
                        .enhance(2.6)
                        .convert("RGB")
                    )
                ink = ImageDraw.Draw(patch)
                px = x - x0
                py = q["row"] - y0
                ink.line((px - 12, py, px - 2, py), fill=c, width=2)
                ink.line((px + 2, py, px + 12, py), fill=c, width=2)
                y = top + 47 + k * (ph + 22)
                image.paste(patch, (left, y))
                ml = q["nominal_ml"]
                v = f"{ml:.2f} mL" if ml is not None else "outside volume range"
                draw.text(
                    (left, y + ph + 1),
                    f"{'Before' if k == 0 else 'After'}   row {q['row']:.2f}    {v}",
                    fill=c,
                    font=font(13),
                )
        draw.text(
            (margin, top + 2 * ph + 91),
            pre + "   /   " + post,
            fill=WHITE,
            font=font(11),
        )
    image.save(dest / output, quality=91, optimize=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--logs", type=Path, required=True)
    p.add_argument(
        "--windows",
        type=Path,
        help="Preserve representative crops from native named windows",
    )
    p.add_argument("--photos", type=Path, default=HERE / "photos")
    p.add_argument("--map", type=Path, default=HERE / "geometry-used.json")
    p.add_argument("--evidence", type=Path, default=HERE / "evidence")
    args = p.parse_args()
    m = json.loads(args.map.read_text())
    samples = []
    rows = read_log(args.logs / "fresh.jsonl")
    for head in ("A", "B"):
        first = next(
            (r for r in rows if r["event"] == "trial" and r["head"] == head), None
        )
        if first:
            samples.append(
                (
                    f"Head {head} · " + first["scenario"].replace("_", " "),
                    first["pre"],
                    first["post"],
                )
            )
    if len(samples) == 2:
        panels(
            "First new-program pour on each head",
            samples,
            args.windows,
            args.photos,
            m,
            args.evidence,
            "clear-pour-examples.jpg",
        )
    home = []
    for journal, kind in (
        ("return.jsonl", "After fill tests"),
        ("return-final.jsonl", "After final repeat"),
    ):
        returned = next(
            (
                r
                for r in read_log(args.logs / journal)
                if r["event"] == "station_position"
            ),
            None,
        )
        if returned:
            home.append((kind, returned["first_window"], returned["last_window"]))
    if home:
        panels(
            "Returning to the photographed cup level",
            home,
            args.windows,
            args.photos,
            m,
            args.evidence,
            "clear-return.jpg",
        )


if __name__ == "__main__":
    main()
