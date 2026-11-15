"""Lets the Sculpted base and tip lay their shallow overhangs at their own wall speed.

The filament's overhang speeds stop overriding the process's, which already holds the same
speeds, so every other object keeps what it had. The base and the tip take the wall speed at the
slicer's two shallowest overhang points from their own object settings; the steeper points,
bridges and fan stay as the filament had them.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

MODEL = "Metadata/model_settings.config"
SETTINGS = "Metadata/project_settings.config"
FILAMENT = "Metadata/filament_settings_1.config"
SHELLS = {"faucet-shell-base", "faucet-shell-tip"}
WALL_SPEED_POINTS = ("overhang_1_4_speed", "overhang_2_4_speed")
SPEEDS = ("enable_overhang_speed", "overhang_1_4_speed", "overhang_2_4_speed", "overhang_3_4_speed",
          "overhang_4_4_speed", "overhang_totally_speed", "bridge_speed")


def filament_override_off(text):
    """The settings text with every filament's overhang override off, and nothing else changed."""
    pattern = re.compile(r'("override_process_overhang_speed": \[)([^\]]*)(\])')
    found = pattern.search(text)
    if not found:
        raise ValueError("the project has no filament overhang override")
    flags = re.sub(r'"[01]"', '"0"', found.group(2))
    return text[:found.start(2)] + flags + text[found.end(2):]


def check_process_matches_filament(config):
    pairs = {"enable_overhang_speed": "filament_enable_overhang_speed",
             "overhang_1_4_speed": "filament_overhang_1_4_speed",
             "overhang_2_4_speed": "filament_overhang_2_4_speed",
             "overhang_3_4_speed": "filament_overhang_3_4_speed",
             "overhang_4_4_speed": "filament_overhang_4_4_speed",
             "overhang_totally_speed": "filament_overhang_totally_speed",
             "bridge_speed": "filament_bridge_speed"}
    used = int(config.get("filament_self_index", ["1"])[0]) - 1
    for process, filament in pairs.items():
        wanted = config[filament][used]
        if any(v != wanted for v in config[process]):
            raise ValueError(f"{process} {config[process]} differs from the filament's {filament} {wanted}")


def write_project(source, output):
    with ZipFile(source) as archive:
        config = json.loads(archive.read(SETTINGS))
        check_process_matches_filament(config)
        variants = len(config["overhang_1_4_speed"])
        model = ET.fromstring(archive.read(MODEL))
        seen = set()
        for obj in model.findall("object"):
            entries = {item.get("key"): item for item in obj.findall("metadata") if item.get("key")}
            name = entries["name"].get("value")
            if name not in SHELLS:
                continue
            seen.add(name)
            for key in SPEEDS:
                if key in entries:
                    raise ValueError(f"{name} already sets {key}")
            for key in WALL_SPEED_POINTS:
                obj.append(ET.Element("metadata", {"key": key, "value": ",".join(["0"] * variants)}))
        if seen != SHELLS:
            raise ValueError(f"missing shells: {SHELLS - seen}")
        with ZipFile(output, "x") as out:
            for entry in archive.infolist():
                payload = archive.read(entry)
                if entry.filename == MODEL:
                    payload = ET.tostring(model, encoding="utf-8")
                elif entry.filename == SETTINGS:
                    payload = filament_override_off(payload.decode()).encode()
                elif entry.filename == FILAMENT and b"override_process_overhang_speed" in payload:
                    raise ValueError("the filament preset carries its own overhang override")
                out.writestr(entry, payload)


if __name__ == "__main__":
    write_project(sys.argv[1], sys.argv[2])
