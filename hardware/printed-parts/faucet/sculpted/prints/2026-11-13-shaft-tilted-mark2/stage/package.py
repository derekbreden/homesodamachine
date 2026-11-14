"""Bind a single-plate Mark2 archive to the sequenced motion and its estimates."""

import argparse
from hashlib import md5, sha256
import json
import math
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


GCODE = "Metadata/plate_1.gcode"
SLICE = "Metadata/slice_info.config"
LAYOUT = "Metadata/plate_1.json"
LENGTH = b"; total filament length [mm] : "
VOLUME = b"; total filament volume [cm^3] : "
WEIGHT = b"; total filament weight [g] : "


def duration(seconds):
    minutes, seconds = divmod(math.ceil(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {seconds}s".encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("sequenced", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--motion-seconds", required=True, type=float)
    parser.add_argument("--first-course-seconds", required=True, type=float)
    args = parser.parse_args()
    raw = args.sequenced.read_bytes()
    schedule = json.loads(args.sequenced.with_suffix(".json").read_text())
    if sha256(raw).hexdigest() != schedule["sequenced_gcode_sha256"]:
        raise ValueError("Sequencer report and G-code differ")
    groups = raw.count(b"\n; CHANGE_LAYER\n")
    if groups != len(schedule["groups"]):
        raise ValueError("Missing course group delimiters")
    filament_mm = sum(schedule["deposition_mm_filament"].values())
    diameter = float(re.search(rb"^; filament_diameter: ([\d.]+)$", raw, re.M)[1])
    density = float(re.search(rb"^; filament_density: ([\d.]+)$", raw, re.M)[1])
    volume_mm3 = math.pi * (diameter / 2) ** 2 * filament_mm
    grams = density * volume_mm3 / 1000
    time = duration(args.motion_seconds)
    header = {
        b"; model printing time: ": b"; model printing time: " + time + b"; total estimated time: " + time,
        b"; total layer number: ": f"; total layer number: {groups}".encode(),
        LENGTH: LENGTH + f"{filament_mm:.2f}".encode(),
        # Native Bambu header stores the value in cubic millimeters under this key.
        VOLUME: VOLUME + f"{volume_mm3:.2f}".encode(),
        WEIGHT: WEIGHT + f"{grams:.2f}".encode(),
    }
    gcode = raw
    for key, line in header.items():
        gcode, found = re.subn(rb"^" + re.escape(key) + rb".*$", line, gcode, count=1, flags=re.M)
        if found != 1:
            raise ValueError(f"The Bambu header has no {key!r}")

    # Retain stock UI progress events at startup with the sequenced motion estimate.
    warmup, body = gcode.split(b"; MACHINE_START_GCODE_END\n", 1)
    warmup = re.sub(rb"^(M73 P(?:0|1) R)\d+", lambda m: m[1] + str(math.ceil(args.motion_seconds / 60)).encode(),
                    warmup, flags=re.M)
    gcode = warmup + b"; MACHINE_START_GCODE_END\n" + body

    with TemporaryDirectory(dir=args.output.parent) as scratch, ZipFile(args.template) as template:
        sliced = Path(scratch) / "sequenced.gcode.3mf"
        info = ET.fromstring(template.read(SLICE))
        plate = info.find("./plate")
        stats = {m.attrib["key"]: m for m in plate.findall("metadata")}
        stats["prediction"].set("value", str(math.ceil(args.motion_seconds)))
        stats["weight"].set("value", f"{grams:.2f}")
        stats["first_layer_time"].set("value", f"{args.first_course_seconds:.6f}")
        filament = plate.find("filament")
        filament.set("used_m", f"{filament_mm / 1000:.2f}")
        filament.set("used_g", f"{grams:.2f}")
        layer_maps = plate.find("layer_filament_lists")
        layer_maps.clear()
        ET.SubElement(layer_maps, "layer_filament_list", filament_list="0", layer_ranges=f"0 {groups}")
        layout = json.loads(template.read(LAYOUT))
        layout["first_layer_time"] = args.first_course_seconds
        replacements = {
            GCODE: gcode,
            GCODE + ".md5": md5(gcode).hexdigest().encode(),
            SLICE: ET.tostring(info, encoding="utf-8", xml_declaration=True),
            LAYOUT: json.dumps(layout, separators=(",", ":")).encode(),
        }
        with ZipFile(sliced, "w", ZIP_DEFLATED) as output:
            for name in template.namelist():
                if not name.startswith("Metadata/hsm_"):
                    output.writestr(name, replacements[name] if name in replacements else template.read(name))
        subprocess.run(["hsm-printer", "archive", sliced, args.output], check=True)
    with ZipFile(args.output) as packaged:
        if packaged.testzip() is not None or packaged.read(GCODE) != gcode:
            raise ValueError("Packaged motion differs")
    print(json.dumps({
        "gcode_sha256": sha256(gcode).hexdigest(),
        "gcode_md5": md5(gcode).hexdigest(),
        "course_groups": groups,
        "deposition_filament_mm": filament_mm,
        "deposition_weight_g": grams,
        "estimated_motion_seconds": args.motion_seconds,
        "first_bed_course_deposition_span_seconds": args.first_course_seconds,
    }))


if __name__ == "__main__":
    main()
