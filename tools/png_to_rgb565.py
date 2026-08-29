#!/usr/bin/env python3
"""Convert the flavor PNGs to RGB565 C headers compiled into the display firmware.

Each source PNG produces headers for the S3 round rotary display (240×240,
firmware/src_config/images/), the RP2040 round display (128×115,
firmware/src_display/), the S3 faucet display (172×320 full-bleed center crop,
firmware/src_faucet/images/), and the three 43:80 renditions the enclosure
display draws (firmware/src_front/images/). These are the first-boot seed
bitmaps; runtime images live on the ESP32 LittleFS store.
"""

from pathlib import Path

from PIL import Image, ImageOps

PROJECT = Path(__file__).resolve().parent.parent
IMAGES = PROJECT / "images"
S3_DIR = PROJECT / "firmware" / "src_config" / "images"
RP_DIR = PROJECT / "firmware" / "src_display"
FAUCET_DIR = PROJECT / "firmware" / "src_faucet" / "images"
FRONT_DIR = PROJECT / "firmware" / "src_front" / "images"

# A channel can be given any logo here, and all three glasses render whichever
# it wears — so every logo needs the 128x115 the round display shows, the 240
# the rotary display shows, and the three 43:80 renditions the faucet and the
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

# (source png, label, S3 var [240×240], RP2040 var [128×115], faucet var [172×320],
#  front anchor var [172×320], front card var [129×240], front tile var [86×160])
FLAVORS = [
    ("flavor_1.png", "flavor_1", "flavor0_240", "flavor1_bitmap", "flavor0_faucet", "flavor0_anchor", "flavor0_card", "flavor0_tile"),
    ("flavor_2.png", "flavor_2", "flavor1_240", "flavor2_bitmap", "flavor1_faucet", "flavor1_anchor", "flavor1_card", "flavor1_tile"),
    ("flavor_3.png", "flavor_3", "flavor2_240", "flavor3_bitmap", "flavor2_faucet", "flavor2_anchor", "flavor2_card", "flavor2_tile"),
    ("flavor_4.png", "flavor_4", "flavor3_240", "flavor4_bitmap", "flavor3_faucet", "flavor3_anchor", "flavor3_card", "flavor3_tile"),
]


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def write_header(src, var, label, out_path, w, h, cover=False):
    img = Image.open(src).convert("RGB")
    if cover:
        # Scale to fill w×h and center-crop the overflow (no distortion)
        img = ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.5))
    else:
        img = img.resize((w, h), Image.LANCZOS)
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
    S3_DIR.mkdir(parents=True, exist_ok=True)
    RP_DIR.mkdir(parents=True, exist_ok=True)
    FAUCET_DIR.mkdir(parents=True, exist_ok=True)
    FRONT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Converting {len(FLAVORS)} flavors to RGB565 headers...")
    for png, label, s3_var, rp_var, faucet_var, anchor_var, card_var, tile_var in FLAVORS:
        src = IMAGES / png
        if not src.exists():
            print(f"  SKIP {png} (missing)")
            continue
        write_header(src, s3_var, label, S3_DIR / f"{s3_var}.h", 240, 240)
        write_header(src, rp_var, label, RP_DIR / f"{rp_var}.h", 128, 115)
        write_header(src, anchor_var, label, FRONT_DIR / f"{anchor_var}.h",
                     ANCHOR_W, ANCHOR_H, cover=True)
        write_header(src, card_var, label, FRONT_DIR / f"{card_var}.h",
                     CARD_W, CARD_H, cover=True)
        write_header(src, tile_var, label, FRONT_DIR / f"{tile_var}.h",
                     TILE_W, TILE_H, cover=True)
        write_header(src, faucet_var, label, FAUCET_DIR / f"{faucet_var}.h",
                     ANCHOR_W, ANCHOR_H, cover=True)
    print("Done.")


if __name__ == "__main__":
    main()
