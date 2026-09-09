#!/usr/bin/env python3
"""Convert the flavor PNGs to RGB565 C headers compiled into the display firmware.

Each source PNG produces the faucet display's 172×320 full-bleed center crop
(firmware/src_faucet/images/) and the three 43:80 renditions the enclosure
display draws (firmware/src_front/images/). These are the factory logos, in
every image and never removed; a user's own picture arrives from a phone into
each display's image store.
"""

from pathlib import Path

from PIL import Image, ImageOps

PROJECT = Path(__file__).resolve().parent.parent
IMAGES = PROJECT / "images"
FAUCET_DIR = PROJECT / "firmware" / "src_faucet" / "images"
FRONT_DIR = PROJECT / "firmware" / "src_front" / "images"

# A channel can be given any logo here, and both glasses render whichever it
# wears — so every logo needs the three 43:80 renditions the faucet and the
# enclosure draw between them.

# THE ENCLOSURE'S FACES ARE THE FAUCET'S SHAPE, SCALED. Every surface on that
# panel that shows a logo shows the same rectangle a photograph gave the glass:
# the anchor is the faucet's own rendition, the card is it at three quarters,
# the picker tile at half. Center-cropped like the faucet's own, so a face is a
# preview of the glass rather than a differently-framed picture of it.
# These mirror IMAGE_BUNDLE in firmware/lib/proto_link/proto_msg.h, which is
# what a phone resamples a user's own picture to.
ANCHOR_W, ANCHOR_H = 43 * 4, 80 * 4   # 172x320 — and the faucet's own
CARD_W, CARD_H     = 43 * 3, 80 * 3   # 129x240
TILE_W, TILE_H     = 43 * 2, 80 * 2   #  86x160

# (source png, label, faucet var [172×320], front anchor var [172×320],
#  front card var [129×240], front tile var [86×160])
FLAVORS = [
    ("flavor_1.png", "flavor_1", "flavor0_faucet", "flavor0_anchor", "flavor0_card", "flavor0_tile"),
    ("flavor_2.png", "flavor_2", "flavor1_faucet", "flavor1_anchor", "flavor1_card", "flavor1_tile"),
    ("flavor_3.png", "flavor_3", "flavor2_faucet", "flavor2_anchor", "flavor2_card", "flavor2_tile"),
    ("flavor_4.png", "flavor_4", "flavor3_faucet", "flavor3_anchor", "flavor3_card", "flavor3_tile"),
]


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def write_header(src, var, label, out_path, w, h):
    img = Image.open(src).convert("RGB")
    # Scale to fill w×h and center-crop the overflow (no distortion)
    img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
    data = img.tobytes()  # RGB, 3 bytes per pixel
    vals = [f"0x{rgb565(data[i], data[i + 1], data[i + 2]):04X}" for i in range(0, len(data), 3)]
    with open(out_path, "w") as f:
        f.write(f"// {label} - {w}x{h} RGB565 bitmap\n")
        f.write(f"// Auto-generated from {src.name} by tools/png_to_rgb565.py\n")
        f.write("#pragma once\n\n#include <Arduino.h>\n\n")
        f.write(f"const uint16_t {var}[{w} * {h}] PROGMEM = {{\n")
        for i in range(0, len(vals), 16):
            f.write("    " + ", ".join(vals[i:i + 16]) + ",\n")
        f.write("};\n")
    print(f"  {out_path.relative_to(PROJECT)}  ({out_path.stat().st_size:,} bytes)")


def main():
    FAUCET_DIR.mkdir(parents=True, exist_ok=True)
    FRONT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Converting {len(FLAVORS)} flavors to RGB565 headers...")
    for png, label, faucet_var, anchor_var, card_var, tile_var in FLAVORS:
        src = IMAGES / png
        if not src.exists():
            print(f"  SKIP {png} (missing)")
            continue
        write_header(src, anchor_var, label, FRONT_DIR / f"{anchor_var}.h",
                     ANCHOR_W, ANCHOR_H)
        write_header(src, card_var, label, FRONT_DIR / f"{card_var}.h",
                     CARD_W, CARD_H)
        write_header(src, tile_var, label, FRONT_DIR / f"{tile_var}.h",
                     TILE_W, TILE_H)
        write_header(src, faucet_var, label, FAUCET_DIR / f"{faucet_var}.h",
                     ANCHOR_W, ANCHOR_H)
    print("Done.")


if __name__ == "__main__":
    main()
