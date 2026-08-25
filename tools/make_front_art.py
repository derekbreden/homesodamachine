#!/usr/bin/env python3
"""Build the enclosure display's art partition image.

The loading animation is 16 frames of 360x360 RGB565 — 3.96 MB, which is most
of that board's firmware. Compiled in, it costs nothing at runtime (const data
in flash is memory-mapped, so LVGL renders straight out of it) but it rides
along in every update of code that never touches it.

In its own partition it is still memory-mapped and still costs nothing at
runtime — `esp_partition_mmap` hands back a real pointer through the same MMU
path — and an update of the code is 1.4 MB instead of 5.7.

The frame headers under `firmware/src_front/images/` stay the source. This
reads them and lays the pixels out back to back behind a small header, so what
lands on flash is provably what is in the tree.

    ~/.platformio/penv/bin/python tools/make_front_art.py
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(REPO, "firmware", "src_front", "images")

# Kept in step with front_art.h, which is what the firmware reads this with.
MAGIC = 0x4D534148          # "HASM" little-endian: Home-soda Art, Sixteen Mb board
FORMAT_VERSION = 1
HEADER_SIZE = 32
NUM_FRAMES = 16
SIZE_PX = 360

VALUE = re.compile(rb"0x([0-9A-Fa-f]{1,4})")


def read_frame(path: str) -> bytes:
    raw = open(path, "rb").read()
    body = raw[raw.index(b"{") + 1: raw.rindex(b"}")]
    vals = VALUE.findall(body)
    want = SIZE_PX * SIZE_PX
    if len(vals) != want:
        sys.exit(f"{os.path.basename(path)}: {len(vals)} values, expected {want}")
    out = bytearray(want * 2)
    struct.pack_into(f"<{want}H", out, 0, *(int(v, 16) for v in vals))
    return bytes(out)


def build() -> bytes:
    frames = []
    for i in range(NUM_FRAMES):
        p = os.path.join(IMAGES, f"anim_{i:02d}.h")
        if not os.path.exists(p):
            sys.exit(f"missing {p}")
        frames.append(read_frame(p))
        print(f"  anim_{i:02d}  {len(frames[-1]):,} bytes")

    pixels = b"".join(frames)
    crc = zlib.crc32(pixels) & 0xFFFFFFFF
    header = struct.pack(
        "<IIIHHI12s",
        MAGIC, FORMAT_VERSION, NUM_FRAMES, SIZE_PX, SIZE_PX, crc, b"\0" * 12
    )
    assert len(header) == HEADER_SIZE, len(header)
    return header + pixels


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out",
                    default=os.path.join(REPO, ".pio", "build", "esp32s3_front", "art.bin"))
    a = ap.parse_args()

    blob = build()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(blob)
    print(f"\n{a.out}")
    print(f"  {len(blob):,} bytes  ({NUM_FRAMES} x {SIZE_PX}x{SIZE_PX} RGB565 + {HEADER_SIZE} B header)")
    print(f"  crc32 {zlib.crc32(blob[HEADER_SIZE:]) & 0xFFFFFFFF:#010x} over the pixels")
