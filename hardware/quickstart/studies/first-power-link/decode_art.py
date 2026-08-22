"""Decode the exact RGB565 art compiled into the two shipping displays."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = next(path for path in HERE.parents if (path / "firmware").is_dir())
OUT = HERE / "art"


def decode(source: Path, target: Path, width: int, height: int) -> None:
    body = source.read_text()
    body = body[body.index("{") + 1 : body.rindex("}")]
    words = [int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{4})", body)]
    expected = width * height
    if len(words) != expected:
        raise ValueError(f"{source}: expected {expected} pixels, found {len(words)}")
    pixels = [
        (
            ((value >> 11) & 0x1F) * 255 // 31,
            ((value >> 5) & 0x3F) * 255 // 63,
            (value & 0x1F) * 255 // 31,
        )
        for value in words
    ]
    image = Image.new("RGB", (width, height))
    image.putdata(pixels)
    image.save(target, format="PNG", optimize=True)


OUT.mkdir(parents=True, exist_ok=True)
decode(
    ROOT / "firmware/src_config/images/flavor0_240.h",
    OUT / "front-flavor-1.png",
    240,
    240,
)
decode(
    ROOT / "firmware/src_config/images/flavor1_240.h",
    OUT / "front-flavor-2.png",
    240,
    240,
)
decode(
    ROOT / "firmware/src_front/images/anim_07.h",
    OUT / "boot-frame.png",
    360,
    360,
)
