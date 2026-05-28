"""Measurement harness for the Freestyle line-art camera/visibility sieve.

Renders the enclosure iso views under many camera-distance and Freestyle
settings, rasterizes each to a pixel mask, and scores them against a
gold reference. Because the camera is orthographic, every render of a
view lands its lines at identical pixels, so masks compare directly.

Two gold sources:
  - union: OR of all VISIBLE-mode renders across camera distances. Every
    true edge appears at some distance; VISIBLE never bleeds back-face
    detail, so the union is complete and artifact-free.
  - file: an external known-good SVG (e.g. the committed iso-front).

Score per candidate: (missing, extra) pixel counts vs the gold, with a
1px dilation tolerance for anti-aliasing.

    tools/cad-venv/bin/python tools/render/freestyle-sieve/sieve.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2]
_LINEART = _REPO / "hardware" / "printed-parts" / "enclosure" / "drawings" / "line-art"
sys.path.insert(0, str(_LINEART))

import cadquery as cq
import _appliance_model as model

_SCENE = _HERE / "sieve_scene.py"


def _blender():
    for c in ("blender", "/opt/homebrew/bin/blender"):
        if shutil.which(c) or Path(c).exists():
            return c
    return "/Applications/Blender.app/Contents/MacOS/Blender"


def export_appliance(dest: Path):
    cq.exporters.export(model.build_appliance(), str(dest), exportType="STL", tolerance=0.05)


def render(appliance_stl: Path, view: str, settings: dict, out_svg: Path, tmp: Path):
    args = {"appliance_stl": str(appliance_stl), "out_svg": str(out_svg), "view": view}
    args.update(settings)
    aj = tmp / "args.json"
    aj.write_text(json.dumps(args))
    r = subprocess.run(
        [_blender(), "--background", "--python", str(_SCENE), "--", str(aj)],
        capture_output=True, text=True,
    )
    if not out_svg.exists():
        raise RuntimeError(f"render failed: {r.stdout[-800:]}\n{r.stderr[-400:]}")
    return out_svg


def svg_to_mask(svg: Path) -> np.ndarray:
    png = svg.with_suffix(".png")
    subprocess.run(["rsvg-convert", "-b", "white", str(svg), "-o", str(png)], check=True)
    a = np.array(Image.open(png).convert("L"))
    return a < 128  # True where a line is drawn


def dilate(mask: np.ndarray, r: int = 1) -> np.ndarray:
    out = mask.copy()
    for _ in range(r):
        d = out.copy()
        d[1:, :] |= out[:-1, :]
        d[:-1, :] |= out[1:, :]
        d[:, 1:] |= out[:, :-1]
        d[:, :-1] |= out[:, 1:]
        out = d
    return out


def score(cand: np.ndarray, gold: np.ndarray):
    # Crop both to the common shape — image_width can round off by 1px.
    h = min(cand.shape[0], gold.shape[0])
    w = min(cand.shape[1], gold.shape[1])
    cand = cand[:h, :w]
    gold = gold[:h, :w]
    cand_d = dilate(cand, 1)
    gold_d = dilate(gold, 1)
    missing = int(np.count_nonzero(gold & ~cand_d))
    extra = int(np.count_nonzero(cand & ~gold_d))
    return missing, extra


def main():
    cam_mults = [0.51, 0.55, 0.6, 0.7, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0,
                 5.0, 8.0, 12.0, 20.0, 50.0, 100.0]
    with tempfile.TemporaryDirectory(prefix="sieve-") as td:
        tmp = Path(td)
        for view in ("front", "back"):
            stl = tmp / f"app_{view}.stl"
            export_appliance(stl)
            masks = {}
            for m in cam_mults:
                svg = tmp / f"{view}_{m}.svg"
                render(stl, view, {"cam_mult": m, "visibility": "VISIBLE"}, svg, tmp)
                masks[m] = svg_to_mask(svg)
            shape = next(iter(masks.values())).shape
            gold = np.zeros(shape, dtype=bool)
            for mk in masks.values():
                gold |= mk
            gold_total = int(np.count_nonzero(gold))
            print(f"\n=== {view}  (union-gold line pixels: {gold_total}) ===")
            print(f"{'cam_mult':>9} {'missing':>8} {'extra':>7} {'note':>6}")
            for m in cam_mults:
                miss, extra = score(masks[m], gold)
                note = "  OK" if miss == 0 else ""
                print(f"{m:>9} {miss:>8} {extra:>7} {note}")


if __name__ == "__main__":
    main()
