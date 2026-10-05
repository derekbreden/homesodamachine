#!/usr/bin/env python3
"""Pack the Pico SDK's linked flash .bin into RP2040 UF2 blocks."""
import argparse
import struct
from pathlib import Path

def convert(source: Path, destination: Path):
    data = source.read_bytes()
    if not data or len(data) > 2 * 1024 * 1024:
        raise ValueError("Expected a nonempty <=2MiB RP2040 flash image")
    count = (len(data) + 255) // 256
    with destination.open("wb") as out:
        for index in range(count):
            payload = data[index * 256:(index + 1) * 256].ljust(256, b"\0")
            header = struct.pack("<8I", 0x0A324655, 0x9E5D5157, 0x2000,
                                 0x10000000 + 256 * index, 256, index, count, 0xE48BFF56)
            out.write(header + payload + bytes(220) + struct.pack("<I", 0x0AB16F30))
    return {"binary_bytes": len(data), "uf2_blocks": count, "uf2_bytes": count * 512}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("destination", type=Path)
    a = p.parse_args()
    print(convert(a.source, a.destination))
