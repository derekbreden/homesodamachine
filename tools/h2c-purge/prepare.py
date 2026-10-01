#!/usr/bin/env python3
"""Package the reviewed, fixed-left H2C purge program for Bambu Connect.

This builds a maintenance archive; it never sends commands to a printer.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verify(gcode: bytes) -> dict:
    commands = [line.split(";", 1)[0].strip() for line in gcode.decode().splitlines()]
    commands = [line for line in commands if line]
    depth = 0
    for line in commands:
        if line.startswith("M622 "):
            depth += 1
        elif line == "M623":
            depth -= 1
        assert depth >= 0, "Unbalanced firmware conditional"
    assert depth == 0, "Unclosed firmware conditional"
    assert commands[-1] == "M73 P100 R0"
    assert "M83" in commands and "M109 S280" in commands
    extrusions = [line for line in commands if re.match(r"G[0123] .*\bE", line)]
    assert extrusions == ["G1 E45 F449.008", "G1 E-3 F1800"], extrusions
    assert commands.index("M109 S280") < commands.index("G1 E45 F449.008")
    assert commands.index("G28 Z P0 T250") < commands.index("G1 E45 F449.008")
    assert commands.index("T0 H-1") < commands.index("G1 E45 F449.008")
    assert not any(line.startswith(("M190", "G29 A", "G383", "M983.3", "M500")) for line in commands)
    assert not any(line.startswith(("T65535", "T65279")) for line in commands)
    assert all(line == "M140 S0" for line in commands if line.startswith("M140 "))
    assert all(line == "M141 S0" for line in commands if line.startswith("M141 "))
    cleanup = commands[commands.index("M73 P95 R0"):]
    for line in ("M104 S0 T0", "M104 S0 T1", "M140 S0", "M141 S0", "M211 X1 Y1 Z1", "M18"):
        assert line in cleanup, line
    assert not any("{" in line or "}" in line for line in commands)
    return {
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
        "explicit_extrusions": extrusions,
        "explicit_purge_temperature_c": 280,
        "material_prepare_flush_temperature_c": 300,
        "bed_heating": False,
        "chamber_heating": False,
        "bed_deposition": False,
        "print_end_unload": False,
        "firmware_conditionals_balanced": True,
        "heater_shutdown_present": True,
        "nozzle_wipe_present": "G150 T265" in commands,
        "physical_validation": "required",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".cache/h2c-purge-v1/h2c-left-petgf-purge-v1.gcode.3mf")
    args = parser.parse_args()
    source = json.loads((HERE / "source.json").read_text())
    gcode = (HERE / "h2c-left-petgf-purge.gcode").read_bytes()
    check = verify(gcode)
    entries = {name: content.encode() for name, content in json.loads((HERE / "package-metadata.json").read_text()).items()}
    settings = json.loads(entries["Metadata/project_settings.config"])
    assert [int(x) for x in settings["filament_map"]] == [1]
    assert settings["printer_model"] == "Bambu Lab H2C"
    settings.update({"machine_start_gcode": gcode.decode(), "machine_end_gcode": ""})
    entries["Metadata/project_settings.config"] = json.dumps(settings, indent=2).encode()
    entries["Metadata/plate_1.gcode"] = gcode
    entries["Metadata/plate_1.gcode.md5"] = hashlib.md5(gcode).hexdigest().encode()
    # An empty thumbnail matches the archive's empty model/build; nothing is printed on the bed.
    png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")
    for name in ("plate_1.png", "plate_1_small.png", "plate_no_light_1.png", "top_1.png", "pick_1.png"):
        entries["Metadata/" + name] = png
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None
        assert archive.read("Metadata/plate_1.gcode.md5").decode() == hashlib.md5(archive.read("Metadata/plate_1.gcode")).hexdigest()
        assert not ET.fromstring(archive.read("Metadata/slice_info.config")).findall("plate/object")
    check.update({"archive": str(args.output.relative_to(ROOT)), "archive_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "source_archive_sha256": source["native_archive_sha256"], "objects": 0, "active_nozzle": "fixed left hardened 0.4 mm", "expected_external_spool": 254})
    (args.output.parent / "preflight.json").write_text(json.dumps(check, indent=2) + "\n")
    print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
