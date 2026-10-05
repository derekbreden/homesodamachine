#!/usr/bin/env python3
"""Verify prepared UF2 integrity and its source/geometry binding; opens no ports."""
import hashlib
import json
import struct
from pathlib import Path
from make_geometry import render

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def verify():
    data = json.loads((HERE / "assets/build-manifest.json").read_text())
    required = {"main.cpp", "motion_policy.h", "safety_policy.h", "command_input.h",
                "tmc_uart.h", "tmc_protocol.h", "driver_profile.h", "pins.h", "geometry_generated.h",
                "CMakeLists.txt", "make_geometry.py", "make_uf2.py", "verify_assets.py"}
    if not required.issubset(data["source_sha256"]):
        raise ValueError("Missing firmware source binding")
    for filename, expected in data["source_sha256"].items():
        if hashlib.sha256((HERE / filename).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Stale source binding: {filename}; rebuild/rebind images")
    geo = json.loads((ROOT / data["geometry_source"]).read_text())
    if {key: geo[key] for key in data["geometry_parameters"]} != data["geometry_parameters"]:
        raise ValueError("Mechanical control geometry changed; regenerate count limits and rebuild/rebind images")
    if (HERE / "geometry_generated.h").read_text() != render():
        raise ValueError("Generated firmware geometry is stale")
    for profile in data["profiles"]:
        path = HERE / "assets" / profile["file"]
        raw = path.read_bytes()
        if len(raw) != profile["bytes"] or len(raw) % 512 or hashlib.sha256(raw).hexdigest() != profile["sha256"]:
            raise ValueError(f"Changed or malformed UF2: {path.name}")
        count = len(raw) // 512
        for index in range(count):
            block = raw[index * 512:(index + 1) * 512]
            expect = (0x0A324655, 0x9E5D5157, 0x2000, 0x10000000 + 256 * index,
                      256, index, count, 0xE48BFF56)
            if struct.unpack("<8I", block[:32]) != expect or struct.unpack("<I", block[-4:])[0] != 0x0AB16F30:
                raise ValueError(f"Invalid UF2 block {index}: {path.name}")
        payload = b"".join(raw[i * 512 + 32:i * 512 + 288] for i in range(count))
        if (profile["name"] + "\0").encode() not in payload:
            raise ValueError(f"UF2 does not identify its named profile: {path.name}")
        print(f"PASS: {path.name}, {count} valid RP2040 blocks, source and geometry bound")
    return data

if __name__ == "__main__":
    verify()
