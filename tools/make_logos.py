#!/usr/bin/env python3
"""Lay the four factory logos out for the image store.

Reads `firmware/src_front/images/flavor{0..3}_{anchor,card,tile}.h` and writes
one blob: a 64-byte header, then four bundles of three renditions each, in the
order `IMAGE_BUNDLE` names in proto_msg.h. A bundle laid out in another order
reads as another board's and the store hands back nothing for that slot.

The header carries each bundle's crc32, which `imageStoreWriteBegin` is given
before that slot's bytes.

Every rendition is 43:80, and the faucet's 172x320 headers are byte-for-byte the
enclosure's anchors, so one blob fills either store.

    tools/make_logos.py -o logos.bin
"""
import argparse
import pathlib
import re
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "firmware" / "src_front" / "images"

MAGIC = 0x53474F4C  # 'LOGS'
FORMAT = 1
HEADER_BYTES = 64

# The rendition order IMAGE_BUNDLE names in proto_msg.h, which is the order a
# slot's pixels are concatenated in.
RENDITIONS = [("anchor", 172, 320), ("card", 129, 240), ("tile", 86, 160)]
FACES = 4


def read_pixels(path: pathlib.Path) -> bytes:
    """The RGB565 words out of one generated header, little-endian.

    The count is checked against the rendition's geometry by the caller.
    """
    text = path.read_text()
    body = text[text.index("{") + 1 : text.rindex("}")]
    words = [int(w, 0) for w in re.findall(r"0[xX][0-9a-fA-F]+", body)]
    return b"".join(struct.pack("<H", w & 0xFFFF) for w in words)


def build() -> bytes:
    bundles = []
    for face in range(FACES):
        parts = []
        for name, w, h in RENDITIONS:
            path = IMAGES / f"flavor{face}_{name}.h"
            px = read_pixels(path)
            want = w * h * 2
            if len(px) != want:
                sys.exit(f"{path.name}: {len(px)} bytes, expected {want} for {w}x{h}")
            parts.append(px)
        bundles.append(b"".join(parts))

    per = len(bundles[0])
    if any(len(b) != per for b in bundles):
        sys.exit("bundles differ in size — a rendition is missing from one face")

    header = struct.pack(
        "<IIIII", MAGIC, FORMAT, FACES, per, len(RENDITIONS)
    ) + b"".join(struct.pack("<I", zlib.crc32(b) & 0xFFFFFFFF) for b in bundles)
    header += b"\0" * (HEADER_BYTES - len(header))
    return header + b"".join(bundles)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--out", required=True, help="where to write the blob")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args()

    blob = build()
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)

    if not a.quiet:
        per = (len(blob) - HEADER_BYTES) // FACES
        print(f"{out}")
        print(f"  {len(blob):,} bytes  ({FACES} faces x {per:,} B, "
              f"{len(RENDITIONS)} renditions each)")
        print(f"  crc32 {zlib.crc32(blob) & 0xFFFFFFFF:#010x} over the file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
