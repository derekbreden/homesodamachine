"""A flat, accumulating case-load graphic for the short film.

``draw(time, duration, width, height)`` returns an RGB Pillow image. Three
unbranded case symbols land in a stack; each contains twelve plain can marks.
The normalized contact times also drive sound placement. There is no exit
animation: cut from the completed load directly to the faucet.
"""

from __future__ import annotations

from functools import lru_cache
import math

from PIL import Image, ImageDraw


COBALT = (23, 73, 209)
ICE = (220, 230, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 145, 82)

# Each time is the visible instant at which the case bottom meets its support.
CONTACTS = (
    (0.16, "case_contact_1"),
    (0.43, "case_contact_2"),
    (0.70, "case_contact_3"),
)

_W, _H, _SCALE = 1920, 1080, 2
_CASE_W, _CASE_H = 900, 224
_FLOOR = 924
_X_OFFSETS = (-18, 15, -4)


def normalized_events() -> list[tuple[float, str]]:
    """Return case contacts as fractions of this shot's duration."""
    return list(CONTACTS)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _settle(u: float) -> float:
    # The support yields under each additional load. No springy rebound.
    result = 0.0
    for at, _ in CONTACTS:
        p = _clamp((u - at) / 0.045)
        result += 12 * p * p * (3 - 2 * p)
    return result


@lru_cache(maxsize=1)
def _case() -> Image.Image:
    """A case is a diagram, with no drink label or metallic rendering."""
    s = _SCALE
    tile = Image.new("RGBA", (_CASE_W * s, _CASE_H * s))
    d = ImageDraw.Draw(tile)
    d.rectangle((0, 0, _CASE_W * s - 1, _CASE_H * s - 1), fill=ICE)
    # Twelve blank can silhouettes, six across and two deep. Their repetition
    # communicates inventory rather than a beverage brand or a packshot.
    cw, ch, step_x, step_y = 54, 76, 142, 96
    left = (_CASE_W - (5 * step_x + cw)) / 2
    top = (_CASE_H - (step_y + ch)) / 2
    for row in range(2):
        for column in range(6):
            x, y = left + column * step_x, top + row * step_y
            d.rounded_rectangle((x * s, (y + 5) * s,
                                 (x + cw) * s, (y + ch) * s),
                                radius=5 * s, fill=COBALT)
            d.ellipse((x * s, y * s, (x + cw) * s, (y + 12) * s), fill=COBALT)
            # A visible oval lid and small pull tab distinguish cans from
            # bottles even when the entire composition is viewed on a phone.
            d.ellipse(((x + 5) * s, (y + 3) * s,
                       (x + cw - 5) * s, (y + 10) * s), outline=ICE, width=2 * s)
            d.line(((x + cw / 2 - 4) * s, (y + 6) * s,
                    (x + cw / 2 + 4) * s, (y + 6) * s), fill=ICE, width=2 * s)
    # The outer rule and a narrow lower seam identify one containing case.
    d.rectangle((s, s, (_CASE_W - 1) * s, (_CASE_H - 1) * s), outline=WHITE, width=3 * s)
    d.line((0, (_CASE_H - 9) * s, _CASE_W * s, (_CASE_H - 9) * s), fill=COBALT, width=3 * s)
    return tile


def draw(time: float, duration: float, width: int = 1920, height: int = 1080) -> Image.Image:
    """Render one deterministic frame; time and duration are in seconds."""
    if duration <= 0 or not math.isfinite(duration) or not math.isfinite(time):
        raise ValueError("time must be finite and duration must be positive")
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    u = _clamp(time / duration)
    s = _SCALE
    frame = Image.new("RGB", (_W * s, _H * s), COBALT)
    d = ImageDraw.Draw(frame)
    sag = _settle(u)

    # A graphic support line bends as the stack accumulates. It remains a
    # line, with no invented room, shelf, trunk, shadow or horizon.
    support = []
    for x in range(190, 1731, 10):
        distance = abs(x - _W / 2)
        p = _clamp((770 - distance) / 290)
        weight = p * p * (3 - 2 * p)
        support.append((x * s, (_FLOOR + sag * weight) * s))
    d.line(support, fill=ICE, width=4 * s)

    tile = _case()
    for index, (contact, _) in enumerate(CONTACTS):
        start = 0.0 if index == 0 else contact - 0.18
        if u < start:
            continue
        p = _clamp((u - start) / (contact - start))
        bottom = _FLOOR + sag - index * _CASE_H
        if p < 1:
            # Accelerating descent, then a rigid stop at the declared contact.
            entry = 350 if index == 0 else -40
            bottom = entry + (bottom - entry) * p * p
        x = (_W - _CASE_W) / 2 + _X_OFFSETS[index]
        y = bottom - _CASE_H
        frame.paste(tile, (round(x * s), round(y * s)), tile)

    # Short orange contact marks coincide with the sound cues, then disappear.
    # They occur at actual visible support contacts, not arbitrary cut points.
    for index, (contact, _) in enumerate(CONTACTS):
        dt = u - contact
        if not 0 <= dt < 0.052:
            continue
        strength = 1 - dt / 0.052
        color = tuple(round(c * strength + b * (1 - strength)) for c, b in zip(ORANGE, COBALT))
        left = (_W - _CASE_W) / 2 + _X_OFFSETS[index]
        right = left + _CASE_W
        y = _FLOOR + sag - index * _CASE_H
        for edge, direction in ((left, -1), (right, 1)):
            d.line(((edge + direction * 12) * s, (y - 4) * s,
                    (edge + direction * 43) * s, (y - 4) * s), fill=color, width=5 * s)
            d.line(((edge + direction * 9) * s, (y - 16) * s,
                    (edge + direction * 26) * s, (y - 34) * s), fill=color, width=4 * s)

    return frame.resize((width, height), Image.Resampling.LANCZOS)
