#!/usr/bin/env python3
"""The speed a slice commands at one place on a part's outer wall, layer by layer.

RUN BY HAND. NOT A STEP OF THE BUILD.

    python3 tools/gcode/speeds.py SLICE.gcode.3mf --layers 26-33 --at leftmost
    python3 tools/gcode/speeds.py SLICE.gcode.3mf --layers 20-40 --at 168.9,160.0 --object 1901

The place is found by geometry on each layer's exterior loop: its extreme point toward
leftmost (-X), rightmost (+X), front (-Y) or back (+Y) on the plate, or the loop point nearest a
plate X,Y. The speed printed is the modal feed of the move that ends at that point and of the
move that leaves it. A feed-only line between them changes the speed without ending the loop.
The loop's whole range is printed beside it. An outer-wall setting does not fix the speed of
every outer-wall move: overhang speeds and the cooling slowdown replace it on the moves they
cover, and those moves can still be labelled "Outer wall". Layers are numbered from 1, as Bambu
Studio's layer slider numbers them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toolpaths as tp  # noqa: E402

DIRECTIONS = {'leftmost': (0, -1), 'rightmost': (0, 1), 'front': (1, -1), 'back': (1, 1)}


def probe(slice_path: Path, at: str, layers: range | None = None, object_id: int | None = None) -> list[dict]:
    """One row per layer: the commanded speed at `at` on the exterior loop."""
    loops = tp.exterior_loops(tp.read_runs(tp.slice_text(slice_path), object_id))
    rows = []
    for lp in loops:
        r = lp['run']
        n = r['layer'] + 1
        if layers is not None and n not in layers:
            continue
        pts = r['pts']
        if at in DIRECTIONS:
            axis, sign = DIRECTIONS[at]
            i = int(np.argmax(sign * pts[1:, axis])) + 1
        else:
            xy = np.array([float(v) for v in at.split(',')])
            i = int(np.argmin(np.linalg.norm(pts[1:, :2] - xy, axis=1))) + 1
        leaving = min(i, len(r['feed']) - 1)
        rows.append({'layer': n, 'print_z': r['z'], 'point_plate': pts[i].round(3).tolist(),
                     'arriving_mm_s': round(float(r['feed'][i - 1]), 2),
                     'leaving_mm_s': round(float(r['feed'][leaving]), 2),
                     'arriving_line': int(r['lines'][i - 1]),
                     'labelled_overhang': bool(r['overhang'][i - 1]),
                     'loop_min_mm_s': round(float(r['feed'].min()), 2),
                     'loop_max_mm_s': round(float(r['feed'].max()), 2)})
    return rows


def layer_range(text: str | None) -> range | None:
    if not text:
        return None
    lo, _, hi = text.partition('-')
    return range(int(lo), int(hi or lo) + 1)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('slice', type=Path)
    ap.add_argument('--at', required=True, help='leftmost, rightmost, front, back, or a plate X,Y')
    ap.add_argument('--layers', help='first-last, numbered from 1 (default: every layer)')
    ap.add_argument('--object', type=int, help='identify ID of the object (default: every object)')
    ap.add_argument('--json', type=Path)
    a = ap.parse_args(argv)
    rows = probe(a.slice, a.at, layer_range(a.layers), a.object)
    print(f"{'layer':>5} {'print Z':>8} {'point (plate mm)':>24} {'arrive':>7} {'leave':>7} {'line':>8} "
          f"{'overhang':>8} {'loop range':>12}")
    for r in rows:
        x, y, z = r['point_plate']
        print(f"{r['layer']:5d} {r['print_z']:8.2f} {f'{x:.2f}, {y:.2f}, {z:.2f}':>24} {r['arriving_mm_s']:7.2f} "
              f"{r['leaving_mm_s']:7.2f} {r['arriving_line']:8d} {str(r['labelled_overhang']):>8} "
              f"{r['loop_min_mm_s']:5.1f}-{r['loop_max_mm_s']:<5.1f}")
    if a.json:
        a.json.write_text(json.dumps(rows, indent=1) + '\n')


if __name__ == '__main__':
    main()
