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

`--store` lays the same four faces out as the store itself holds them — in the
slots `flavorArtFactorySlot` names, each under the header `imageStoreWriteFinish`
puts down — for esptool to write straight into a display's flash over its own
USB, with no link to carry the blob. The slots a person fills sit below them and
are not in the file, so writing it leaves their pictures where they are. It
prints the command, at the offset the partition table puts those slots.

    tools/make_logos.py --store -o .pio/build/esp32s3_faucet/logos-store.bin
"""
import argparse
import pathlib
import re
import struct
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "firmware" / "src_front" / "images"
STORE_H = ROOT / "firmware" / "lib" / "image_store" / "image_store.h"
PROTO_H = ROOT / "firmware" / "lib" / "proto_link" / "proto_msg.h"

# Both displays open their store over this partition, and erase a slot in
# sectors of this size (image_store.cpp).
STORE_PARTITION = "spiffs"
ERASE = 4096

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


def constant(path: pathlib.Path, name: str) -> int:
    """One `constexpr` out of a firmware header, so the layout follows the board's."""
    m = re.search(rf"constexpr\s+\w+\s+{name}\s*=\s*(0[xX][0-9a-fA-F]+|\d+)",
                  path.read_text())
    if not m:
        sys.exit(f"no {name} in {path.relative_to(ROOT)}")
    return int(m[1], 0)


def partition(table: pathlib.Path, label: str) -> tuple[int, int]:
    """Offset and size of one partition, as the table names them."""
    for line in table.read_text().splitlines():
        cols = [c.strip() for c in line.split("#")[0].split(",")]
        if len(cols) >= 5 and cols[0] == label:
            return int(cols[3], 0), int(cols[4], 0)
    sys.exit(f"no '{label}' partition in {table}")


def build_store(blob: bytes) -> tuple[bytes, int, int]:
    """The factory slots as the store holds them: the bytes, the first slot, slot size.

    A slot is its header, erased flash out to IMAGE_SLOT_PIXELS_AT, the bundle,
    and erased flash out to the next erase boundary. The store recognises a slot
    by its header alone, so the header is what has to be the board's own.
    """
    magic = constant(STORE_H, "IMAGE_SLOT_MAGIC")
    fmt = constant(STORE_H, "IMAGE_SLOT_FORMAT")
    pixels_at = constant(STORE_H, "IMAGE_SLOT_PIXELS_AT")
    max_sizes = constant(STORE_H, "IMAGE_MAX_SIZES")
    first = constant(PROTO_H, "FLAVOR_ART_CUSTOM")   # flavorArtFactorySlot(0)

    per = (len(blob) - HEADER_BYTES) // FACES
    slot_bytes = (pixels_at + per + ERASE - 1) // ERASE * ERASE

    sizes, at = b"", 0
    for _, w, h in RENDITIONS:
        sizes += struct.pack("<HHI", w, h, at)
        at += w * h * 2
    sizes += b"\0" * (8 * (max_sizes - len(RENDITIONS)))

    slots = []
    for face in range(FACES):
        bundle = blob[HEADER_BYTES + face * per:HEADER_BYTES + (face + 1) * per]
        crc = zlib.crc32(bundle) & 0xFFFFFFFF
        # ImageSlotHeader: magic, format, bytes, crc32, seq, count, reserved[7],
        # then the rendition table. The seq is what four writes in a row into an
        # empty store would give them; nothing reads it but the next write.
        header = struct.pack("<IIIIIB7x", magic, fmt, per, crc, face,
                             len(RENDITIONS)) + sizes
        if len(header) > pixels_at:
            sys.exit(f"slot header is {len(header)} B, past the pixels at {pixels_at}")
        slot = header.ljust(pixels_at, b"\xff") + bundle
        slots.append(slot.ljust(slot_bytes, b"\xff"))
    return b"".join(slots), first, slot_bytes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--out", required=True, help="where to write the blob")
    ap.add_argument("--store", action="store_true",
                    help="write the factory slots as the image store holds them")
    ap.add_argument("--partitions", default="firmware/partitions_s3_faucet.csv",
                    help="the display's partition table, for --store's offset")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args()

    blob = build()
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if a.store:
        image, first, slot_bytes = build_store(blob)
        base, size = partition(ROOT / a.partitions, STORE_PARTITION)
        if (first + FACES) * slot_bytes > size:
            sys.exit(f"'{STORE_PARTITION}' is {size:,} B, too small for slot "
                     f"{first + FACES - 1} at {slot_bytes:,} B a slot")
        offset = base + first * slot_bytes
        out.write_bytes(image)
        if not a.quiet:
            print(f"{out}")
            print(f"  {len(image):,} bytes  (slots {first}-{first + FACES - 1}, "
                  f"{slot_bytes:,} B each)")
            print(f"  write it at {offset:#x}, over the display's own USB:")
            print(f"    ~/.platformio/penv/bin/python -m esptool --chip esp32s3 "
                  f"--port <port> write-flash {offset:#x} {out}")
        return 0

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
