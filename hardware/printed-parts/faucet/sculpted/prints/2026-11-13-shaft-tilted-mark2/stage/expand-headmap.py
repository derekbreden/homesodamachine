"""Extend the cited lower-envelope map with the rest of the modeled left-active toolhead."""
import argparse
import json
from pathlib import Path

import numpy as np


def nearest_cell(points, x0, y0, step, shape):
    x = np.rint((points[:, 0] - x0) / step).astype(int)
    y = np.rint((points[:, 1] - y0) / step).astype(int)
    valid = (x >= 0) & (y >= 0) & (x < shape[1]) & (y < shape[0])
    return y[valid], x[valid], points[valid, 2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lower_envelope", type=Path)
    parser.add_argument("left_active_npz", type=Path)
    parser.add_argument("output_text", type=Path)
    args = parser.parse_args()
    with np.load(args.lower_envelope) as retained, np.load(args.left_active_npz) as head:
        lowest = retained["H"].copy()
        flank = retained["N"]
        x0, y0, step = (float(retained[key]) for key in ("x0", "y0", "step"))
        names = json.loads(bytes(head["names"]).decode())
        for index, name in enumerate(names):
            if name.startswith("Left nozzle"):
                continue
            vertices, folds = head[f"V{index}"], head[f"T{index}"]
            triangles = vertices[folds]
            for a, b, c in triangles[triangles[:, :, 2].min(axis=1) >= 30.0]:
                span = max(np.linalg.norm(b - a), np.linalg.norm(c - a), np.linalg.norm(c - b))
                size = max(2, int(np.ceil(span / (step / 2))))
                u, v = np.meshgrid(np.arange(size + 1) / size, np.arange(size + 1) / size)
                included = u + v <= 1.0 + 1e-9
                points = a + u[included, None] * (b - a) + v[included, None] * (c - a)
                y, x, z = nearest_cell(points, x0, y0, step, lowest.shape)
                np.minimum.at(lowest, (y, x), z)
        with args.output_text.open("w") as output:
            for label, envelope in (("H", lowest), ("N", flank)):
                for y, x in zip(*np.nonzero(np.isfinite(envelope))):
                    print(label, round(x0 / step) + x, round(y0 / step) + y,
                          float(envelope[y, x]), file=output)


if __name__ == "__main__":
    main()
