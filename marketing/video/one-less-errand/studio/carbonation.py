"""Fine moving carbonation over the uncropped 1920 x 1080 soda photograph.

``draw(t, width, height)`` returns only a transparent RGBA overlay. Composite
it over the photograph before applying the shot's shared crop and camera move.
The photographed beads remain attached; these sparse glints rise in the liquid.
"""

from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw


_W, _H = 1920, 1080
_TOP, _BOTTOM = 494.0, 1075.0
_AA = 2


def _particles():
    rng = random.Random(640173)
    result = []
    for lane in (0.525, 0.591, 0.657, 0.724, 0.791, 0.858, 0.934):
        offset = rng.random()
        for i in range(4):
            radius = rng.uniform(1.15, 2.85)
            speed = max(35, min(110, 35 + (radius - 1.15) * 38 + rng.uniform(-9, 9)))
            result.append((
                lane * _W + rng.uniform(-14, 14),
                (offset + (i + rng.uniform(-0.22, 0.22)) / 4) % 1,
                speed, radius, rng.uniform(4, 10), rng.uniform(0.45, 0.85),
                rng.uniform(0, math.tau), rng.uniform(0.62, 0.95),
            ))
    return tuple(result)


_PARTICLES = _particles()


def _ease(value):
    p = max(0.0, min(1.0, value))
    return p * p * (3 - 2 * p)


def draw(t: float, width: int = 1920, height: int = 1080) -> Image.Image:
    """Draw 28 deterministic rising clear glints, with invisible loop resets."""
    if not math.isfinite(t):
        raise ValueError("t must be finite")
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    frame = Image.new("RGBA", (width * _AA, height * _AA))
    d = ImageDraw.Draw(frame)
    sx, sy = width / _W * _AA, height / _H * _AA
    unit = min(sx, sy)
    travel = _BOTTOM - _TOP

    for origin, phase, speed, radius, sway, frequency, angle, strength in _PARTICLES:
        progress = ((t * speed / travel) + phase) % 1
        y = _BOTTOM - progress * travel
        x = origin + sway * math.sin(t * frequency + angle)
        x += sway * 0.28 * math.sin(t * 0.31 + angle * 1.7)
        opacity = strength * _ease((y - _TOP) / 62) * _ease((_BOTTOM - y) / 64)
        if opacity <= 0:
            continue
        r = radius * unit
        cx, cy = x * sx, y * sy
        bounds = (cx - r, cy - r, cx + r, cy + r)
        # The center stays transparent. A green refractive edge, a short pale
        # lower rim and one tiny meniscus glint borrow the photograph's light.
        line = max(1, round(0.5 * unit))
        d.ellipse(bounds, outline=(59, 89, 25, round(108 * opacity)), width=line)
        d.arc(bounds, 32, 116, fill=(214, 232, 138, round(76 * opacity)), width=line)
        d.arc(bounds, 211, 283, fill=(255, 255, 226, round(188 * opacity)), width=line)

    return frame.resize((width, height), Image.Resampling.LANCZOS)
