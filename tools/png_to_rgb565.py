#!/usr/bin/env python3
"""Convert the flavor PNGs to RGB565 C headers compiled into the display firmware.

Each source PNG produces headers for the S3 config display (240×240,
firmware/src_config/images/), the RP2040 round display (128×115,
firmware/src_display/), and — for the two shipping flavors — the S3 faucet
display (172×320 full-bleed center crop, firmware/src_faucet/images/).
These are the first-boot seed bitmaps; runtime images live on the ESP32
LittleFS store.
"""

from pathlib import Path

from PIL import Image, ImageOps

PROJECT = Path(__file__).resolve().parent.parent
IMAGES = PROJECT / "images"
S3_DIR = PROJECT / "firmware" / "src_config" / "images"
RP_DIR = PROJECT / "firmware" / "src_display"
FAUCET_DIR = PROJECT / "firmware" / "src_faucet" / "images"
FRONT_DIR = PROJECT / "firmware" / "src_front" / "images"

# A channel can be given any logo here, and all three glasses render whichever it
# wears — so every logo needs the 240 a Choose card shows, the 96 the picker grid
# shows, the 128x115 the round display shows, and the 172x320 the faucet shows.
THUMB = 96

# (source png, label, S3 var [240×240], RP2040 var [128×115], faucet var [172×320],
#  front thumbnail var [96×96])
FLAVORS = [
    ("flavor_1.png", "flavor_1", "flavor0_240", "flavor1_bitmap", "flavor0_faucet", "flavor0_thumb"),
    ("flavor_2.png", "flavor_2", "flavor1_240", "flavor2_bitmap", "flavor1_faucet", "flavor1_thumb"),
    ("flavor_3.png", "flavor_3", "flavor2_240", "flavor3_bitmap", "flavor2_faucet", "flavor2_thumb"),
    ("flavor_4.png", "flavor_4", "flavor3_240", "flavor4_bitmap", "flavor3_faucet", "flavor3_thumb"),
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
    for png, label, s3_var, rp_var, faucet_var, thumb_var in FLAVORS:
        src = IMAGES / png
        if not src.exists():
            print(f"  SKIP {png} (missing)")
            continue
        write_header(src, s3_var, label, S3_DIR / f"{s3_var}.h", 240, 240)
        write_header(src, rp_var, label, RP_DIR / f"{rp_var}.h", 128, 115)
        write_header(src, thumb_var, label, FRONT_DIR / f"{thumb_var}.h", THUMB, THUMB)
        if faucet_var:
            write_header(src, faucet_var, label, FAUCET_DIR / f"{faucet_var}.h",
                         172, 320, cover=True)
    print("Done.")


if __name__ == "__main__":
    main()
