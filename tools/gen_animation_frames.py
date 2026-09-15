#!/usr/bin/env python3
"""Generate the enclosure display's 16-frame faucet-logo pulse.

    tools/cad-venv/bin/python tools/gen_animation_frames.py

Artwork and palette come from brand/mark.svg and brand/palette.json.
The first frame is the static mark. The orange drop gently grows and settles
through a 1.6 second loop; the faucet remains still.
"""

import argparse
import math
from pathlib import Path

from build_brand_assets import PALETTE, ROOT, render, svg

NUM_FRAMES = 16
OUT_DIR = ROOT / "tools/anim_frames"
HEADER_DIR = ROOT / "firmware/src_front/images"
SVG_SIZE = 1024
RENDER_SIZE = 360


def generate_frame_svg(frame, num_frames):
    pulse = (1 - math.cos(2 * math.pi * frame / num_frames)) / 2
    return svg(background=PALETTE["cobalt"], drop_offset=16 * pulse, drop_growth=6 * pulse)


def render_frames():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(NUM_FRAMES):
        artwork = generate_frame_svg(i, NUM_FRAMES)
        (OUT_DIR / f"frame_{i:02d}.svg").write_text(artwork)
        frames.append(render(artwork, RENDER_SIZE, opaque=True))
    frames[0].save(OUT_DIR / "preview.gif", save_all=True, append_images=frames[1:],
                   duration=100, loop=0)
    return frames


def write_headers(frames):
    HEADER_DIR.mkdir(parents=True, exist_ok=True)
    size = RENDER_SIZE
    for i, frame in enumerate(frames):
        data = frame.tobytes()
        vals = [f"0x{(((data[j] & 0xF8) << 8) | ((data[j + 1] & 0xFC) << 3) | (data[j + 2] >> 3)):04X}"
                for j in range(0, len(data), 3)]
        with (HEADER_DIR / f"anim_{i:02d}.h").open("w") as f:
            f.write(f"// Faucet pulse frame {i} — {size}x{size} RGB565 bitmap\n")
            f.write("// Generated from brand/mark.svg by tools/gen_animation_frames.py.\n")
            f.write("#pragma once\n\n#include <Arduino.h>\n\n")
            f.write(f"const uint16_t anim_{i:02d}[{size} * {size}] PROGMEM = {{\n")
            for k in range(0, len(vals), 16):
                f.write("    " + ", ".join(vals[k:k + 16]) + ",\n")
            f.write("};\n")
    print(f"Enclosure logo pulse: {len(frames)} frames, {size} × {size}, RGB565.")


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    write_headers(render_frames())


if __name__ == "__main__":
    main()
