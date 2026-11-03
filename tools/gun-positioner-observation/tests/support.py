"""Shared test fixtures: the package on the path, and a rendered scene for the extractors."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))


def render_scene(width: int, height: int, dot=None, dot_sigma: float = 2.2, dot_peak: float = 180.0,
                 wire_tip=None, wire_angle_deg: float = 180.0, wire_width: float = 5.0,
                 wire_contrast: float = -70.0, seam=None, seam_contrast: float = 40.0,
                 background: float = 60.0, noise: float = 2.0, rng=None, bit_depth: int = 8,
                 extra_dots=()) -> np.ndarray:
    """Gray image with an aiming dot (Gaussian), a wire ending at a tip, and a seam edge.

    `wire_angle_deg` is the direction from the tip back along the wire, in image
    coordinates (0 = +x, 90 = +y). `seam` is (angle_deg, offset): the seam is the
    line x·cosθ + y·sinθ = offset, rendered as a blurred intensity step.
    """
    rng = rng or np.random.default_rng(0)
    yy, xx = np.mgrid[0:height, 0:width].astype(float)
    img = np.full((height, width), background, dtype=float)
    if seam is not None:
        theta = np.radians(seam[0])
        d = xx * np.cos(theta) + yy * np.sin(theta) - seam[1]
        img += seam_contrast * 0.5 * (1 + np.tanh(d / 1.2))
    if wire_tip is not None:
        a = np.radians(wire_angle_deg)
        ux, uy = np.cos(a), np.sin(a)
        rx, ry = xx - wire_tip[0], yy - wire_tip[1]
        along = rx * ux + ry * uy
        across = -rx * uy + ry * ux
        body = 0.5 * (1 + np.tanh(along / 0.7))          # 0 beyond the tip, 1 along the wire
        profile = np.exp(-0.5 * (across / (wire_width / 2.355)) ** 2)
        img += wire_contrast * body * profile
    for (dx, dy, peak) in ([(dot[0], dot[1], dot_peak)] if dot is not None else []) + list(extra_dots):
        img += peak * np.exp(-0.5 * ((xx - dx) ** 2 + (yy - dy) ** 2) / dot_sigma ** 2)
    img += noise * rng.normal(size=img.shape)
    top = 255 if bit_depth == 8 else 65535
    img = np.clip(np.round(img), 0, top)
    return img.astype(np.uint8 if bit_depth == 8 else np.uint16)
