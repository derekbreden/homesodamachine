"""Package reviewed plate 1 for Mark1 without changing native G-code."""

from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print_archive.py").is_file())
sys.path.insert(0, str(ROOT / "tools"))
from bambu_print_archive import package


def main():
    folder = ROOT / ".cache/reservoir-flow105-overlap30/walls-5"
    source = folder / "reservoir-review.3mf"
    selected = folder / "reservoir-left-cap-native.gcode.3mf"
    destination = folder / "2026-10-22-reservoir-left-cap-flow105-overlap30-right08-z000-a3-mark1.gcode.3mf"
    with zipfile.ZipFile(source) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    gcode = members["Metadata/plate_1.gcode"]
    review = json.loads((HERE / "native-review.json").read_text())
    if hashlib.sha256(gcode).hexdigest() != review["plates"][0]["gcode_sha256"]:
        raise ValueError("Plate 1 differs from the native review")

    for name in ("Metadata/model_settings.config", "Metadata/slice_info.config"):
        config = ET.fromstring(members[name])
        for plate in config.findall("plate")[1:]:
            config.remove(plate)
        members[name] = ET.tostring(config, encoding="UTF-8", xml_declaration=True)
    name = "Metadata/_rels/model_settings.config.rels"
    relationships = ET.fromstring(members[name])
    for item in list(relationships):
        if item.attrib["Target"].endswith("plate_2.gcode"):
            relationships.remove(item)
    members[name] = ET.tostring(relationships, encoding="UTF-8", xml_declaration=True)
    name = "Metadata/filament_sequence.json"
    sequence = json.loads(members[name])
    members[name] = json.dumps({"plate_1": sequence["plate_1"]}).encode()
    omitted = {n for n in members if n.startswith("Metadata/") and
               any(marker in n for marker in ("plate_2.", "plate_2_", "plate_no_light_2.", "top_2.", "pick_2."))}
    with zipfile.ZipFile(selected, "x", zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            if name not in omitted:
                archive.writestr(name, data)
    report = package(selected, destination)
    with zipfile.ZipFile(destination) as archive:
        assert archive.read("Metadata/plate_1.gcode") == gcode
        assert archive.read("Metadata/project_settings.config") == members["Metadata/project_settings.config"]
    report.update(native_two_plate_archive=str(source.relative_to(ROOT)),
                  native_two_plate_archive_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  selected_parts=["reservoir-left", "reservoir-cap-left"], source_plate=1,
                  submitted_plate=1, omitted_other_plate_entries=sorted(omitted),
                  native_gcode_byte_identical=True, project_settings_byte_identical=True)
    for key in ("source_archive", "print_only_archive"):
        report[key] = str(Path(report[key]).relative_to(ROOT))
    (HERE / "packaging.json").write_text(json.dumps(report, indent=2) + "\n")
    print(destination)


if __name__ == "__main__":
    main()
