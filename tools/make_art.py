#!/usr/bin/env python3
"""A display's art partition image, laid out from the headers in its tree.

    ~/.platformio/penv/bin/python tools/make_art.py enclosure
    ~/.platformio/penv/bin/python tools/make_art.py rotary

Two boards carry pixels that dwarf their code. The enclosure display's loading
animation is 16 frames of 360x360 RGB565 — 3.96 MB. The rotary display's
animation and flavor faces are 19 of 240x240 — 2.09 MB, of a 3.19 MB app.

In its own partition the art is still memory-mapped and still costs nothing at
runtime — `esp_partition_mmap` hands back a real pointer through the same MMU
path — and an update of the code carries the code.

The headers under each tree's `images/` stay the source. This reads them and
lays the pixels out back to back behind a small header, so what lands on flash
is provably what is in the tree. `firmware/lib/board_art` is what reads it back.
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Kept in step with board_art.h.
MAGIC = 0x4D534148          # "HASM" little-endian
FORMAT_VERSION = 1
HEADER_SIZE = 32

#: The order is the layout, and the firmware indexes into it by position.
BOARDS = {
    "enclosure": {
        "env": "esp32s3_front",
        "images": os.path.join(REPO, "firmware", "src_front", "images"),
        "size_px": 360,
        "names": [f"anim_{i:02d}" for i in range(16)],
    },
    "rotary": {
        "env": "esp32s3_config",
        "images": os.path.join(REPO, "firmware", "src_config", "images"),
        "size_px": 240,
        "names": [f"anim_{i:02d}" for i in range(16)] +
                 ["flavor0_240", "flavor1_240", "flavor2_240"],
    },
}

VALUE = re.compile(rb"0x([0-9A-Fa-f]{1,4})")


def read_image(path: str, size_px: int) -> bytes:
    raw = open(path, "rb").read()
    body = raw[raw.index(b"{") + 1: raw.rindex(b"}")]
    vals = VALUE.findall(body)
    want = size_px * size_px
    if len(vals) != want:
        sys.exit(f"{os.path.basename(path)}: {len(vals)} values, expected {want}")
    out = bytearray(want * 2)
    struct.pack_into(f"<{want}H", out, 0, *(int(v, 16) for v in vals))
    return bytes(out)


def build(board: str, quiet: bool = False) -> bytes:
    spec = BOARDS[board]
    images = []
    for name in spec["names"]:
        p = os.path.join(spec["images"], f"{name}.h")
        if not os.path.exists(p):
            sys.exit(f"missing {p}")
        images.append(read_image(p, spec["size_px"]))
        if not quiet:
            print(f"  {name}  {len(images[-1]):,} bytes")

    pixels = b"".join(images)
    crc = zlib.crc32(pixels) & 0xFFFFFFFF
    header = struct.pack(
        "<IIIHHI12s",
        MAGIC, FORMAT_VERSION, len(images), spec["size_px"], spec["size_px"],
        crc, b"\0" * 12
    )
    assert len(header) == HEADER_SIZE, len(header)
    return header + pixels


def default_out(board: str) -> str:
    return os.path.join(REPO, ".pio", "build", BOARDS[board]["env"], "art.bin")


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("board", choices=sorted(BOARDS))
    ap.add_argument("-o", "--out")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)

    out = a.out or default_out(a.board)
    blob = build(a.board, a.quiet)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(blob)

    spec = BOARDS[a.board]
    px = spec["size_px"]
    print(f"\n{out}")
    print(f"  {len(blob):,} bytes  ({len(spec['names'])} x {px}x{px} RGB565 "
          f"+ {HEADER_SIZE} B header)")
    print(f"  crc32 {zlib.crc32(blob[HEADER_SIZE:]) & 0xFFFFFFFF:#010x} over the pixels")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
