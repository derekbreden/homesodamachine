#!/usr/bin/env python3
"""Render drawing overviews and contextual review crops; never modify the PDF."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess


def region(value):
    try:
        page, name, *coordinates = value.split(",")
        page = int(page)
        box = tuple(float(v) for v in coordinates)
        if page < 1 or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise ValueError
        if len(box) != 4 or not all(math.isfinite(v) for v in box):
            raise ValueError
        x0, y0, x1, y1 = box
        if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
            raise ValueError
        return page, name, box
    except ValueError:
        raise argparse.ArgumentTypeError(
            "use PAGE,NAME,X0,Y0,X1,Y1 with a lowercase name and a positive-area box"
        ) from None


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def page_sizes(pdf, page_count):
    info = run(["pdfinfo", "-f", "1", "-l", str(page_count), "-box", str(pdf)])
    sizes = {}
    number = r"(-?\d+(?:\.\d+)?)"
    for match in re.finditer(
        rf"^Page\s+(\d+)\s+CropBox:\s+{number}\s+{number}\s+{number}\s+{number}",
        info, re.MULTILINE,
    ):
        page = int(match[1])
        x0, y0, x1, y1 = map(float, match.groups()[1:])
        sizes[page] = (x1 - x0, y1 - y0)
    for match in re.finditer(r"^Page\s+(\d+)\s+rot:\s+(-?\d+)", info, re.MULTILINE):
        page, rotation = map(int, match.groups())
        if rotation % 180 == 90 and page in sizes:
            width, height = sizes[page]
            sizes[page] = height, width
    return sizes


def render(pdf, page, dpi, prefix, crop=None):
    command = ["pdftoppm", "-f", str(page), "-l", str(page), "-cropbox",
               "-r", str(dpi), "-png", "-singlefile"]
    if crop:
        for flag, value in zip(("-x", "-y", "-W", "-H"), crop):
            command.extend([flag, str(value)])
    command.extend([str(pdf), str(prefix)])
    run(command)
    return str(prefix.with_suffix(".png"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--page", action="append", type=int,
                        help="page to render; repeat to select several (default: all)")
    parser.add_argument("--region", action="append", type=region, default=[],
                        metavar="PAGE,NAME,X0,Y0,X1,Y1")
    parser.add_argument("--overview-dpi", type=int, default=150)
    parser.add_argument("--detail-dpi", type=int, default=240)
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    if not pdf.is_file():
        parser.error(f"PDF does not exist: {pdf}")
    if min(args.overview_dpi, args.detail_dpi) <= 0:
        parser.error("rendering DPI must be positive")
    for command in ("pdfinfo", "pdftoppm"):
        if not shutil.which(command):
            parser.error(f"Poppler command is unavailable: {command}")

    try:
        info = run(["pdfinfo", str(pdf)])
        count_match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
        if not count_match:
            parser.error("pdfinfo did not return the page count")
        page_count = int(count_match[1])
        pages = sorted(set(args.page or range(1, page_count + 1)))
        if any(page < 1 or page > page_count for page in pages):
            parser.error(f"pages must be between 1 and {page_count}")
        sizes = page_sizes(pdf, page_count)
        if any(page not in sizes for page in pages):
            parser.error("pdfinfo did not return the selected pages' crop boxes")
        names = set()
        for page, name, box in args.region:
            if page not in pages:
                parser.error(f"region {name} belongs to an unselected page: {page}")
            if (page, name) in names:
                parser.error(f"duplicate region name on page {page}: {name}")
            names.add((page, name))
            width, height = sizes[page]
            if box[2] > width or box[3] > height:
                parser.error(f"region {name} exceeds page {page} ({width} x {height} pt)")

        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        review = {"source_pdf": str(pdf),
                  "source_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                  "overview": [], "details": []}
        for page in pages:
            image = render(pdf, page, args.overview_dpi,
                           output / f"page-{page:02d}-overview")
            review["overview"].append({"page": page, "dpi": args.overview_dpi,
                                       "size_pt": sizes[page], "image": image})
        scale = args.detail_dpi / 72
        for page, name, box in args.region:
            _, height = sizes[page]
            x0, y0, x1, y1 = box
            left = math.floor(x0 * scale)
            top = math.floor((height - y1) * scale)
            crop = (left, top, math.ceil(x1 * scale) - left,
                    math.ceil((height - y0) * scale) - top)
            image = render(pdf, page, args.detail_dpi,
                           output / f"page-{page:02d}-{name}", crop)
            review["details"].append({"page": page, "name": name,
                                      "box_pt": box, "dpi": args.detail_dpi,
                                      "image": image})
        manifest = output / "review-images.json"
        manifest.write_text(json.dumps(review, indent=2) + "\n")
        print(json.dumps(review, indent=2))
    except subprocess.CalledProcessError as error:
        parser.exit(1, error.stderr or str(error))


if __name__ == "__main__":
    main()
