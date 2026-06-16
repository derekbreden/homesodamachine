#!/usr/bin/env python3
"""Render the app-icon logo to an RGB565 C header for the front-face display.

The brand mark lives at ios/AppIcon.svg (the same source behind the iOS app
icon and src_config/images/logo_240.h). This tool rasterizes it to a square
RGB565 bitmap compiled into the 4.3" front-face firmware (firmware/src_front/
images/) as the boot/loading logo.

It prefers the SVG master via cairosvg; if cairosvg (and its native cairo
dependency) is unavailable, it falls back to the committed 1024x1024 render at
ios/.../AppIcon.appiconset/AppIcon.png. Both paths composite onto the theme
background (0x1a1a2e) so the centered logo blends seamlessly into the screen.

Run with the project venv (Pillow lives there):
    tools/cad-venv/bin/python tools/gen_logo.py [SIZE]

SIZE is the square edge in pixels (default 480 — the panel's full height).
"""

import io
import sys
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parent.parent
SVG_SRC = PROJECT / "ios" / "AppIcon.svg"
PNG_SRC = (
    PROJECT
    / "ios"
    / "SodaMachine"
    / "SodaMachine"
    / "Assets.xcassets"
    / "AppIcon.appiconset"
    / "AppIcon.png"
)
OUT_DIR = PROJECT / "firmware" / "src_front" / "images"

# Theme background (0x1a1a2e) — matches THEME_BG across every display + the iOS
# app. The logo composites onto this so its edges vanish into the screen fill.
THEME_BG = (26, 26, 46)


def render(size):
    """Return a `size`x`size` RGB image of the logo on the theme background."""
    try:
        import cairosvg  # noqa: WPS433 — optional; native cairo dep

        png = cairosvg.svg2png(
            url=str(SVG_SRC), output_width=size, output_height=size
        )
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        src = f"{SVG_SRC.name} (vector master via cairosvg)"
    except ImportError:
        img = Image.open(PNG_SRC).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        src = f"{PNG_SRC.name} (1024x1024 render; cairosvg unavailable)"

    bg = Image.new("RGBA", img.size, (*THEME_BG, 255))
    return Image.alpha_composite(bg, img).convert("RGB"), src


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def write_header(img, size, src):
    var = f"logo_{size}"
    out = OUT_DIR / f"{var}.h"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = img.tobytes()  # RGB, 3 bytes per pixel
    vals = [f"0x{rgb565(data[i], data[i + 1], data[i + 2]):04X}"
            for i in range(0, len(data), 3)]
    with open(out, "w") as f:
        f.write(f"// {var} - {size}x{size} RGB565 bitmap\n")
        f.write(f"// Auto-generated from {src} by tools/gen_logo.py\n")
        f.write("#pragma once\n\n#include <Arduino.h>\n\n")
        f.write(f"const uint16_t {var}[{size} * {size}] PROGMEM = {{\n")
        for i in range(0, len(vals), 16):
            f.write("    " + ", ".join(vals[i:i + 16]) + ",\n")
        f.write("};\n")
    print(f"  Wrote {out} ({size}x{size}, {len(vals) * 2} bytes) from {src}")


def main():
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    img, src = render(size)
    write_header(img, size, src)


if __name__ == "__main__":
    main()
