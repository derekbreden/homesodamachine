"""Turn the reviewed 0.08 mm TAP/FLAVOR plate face down without changing its settings."""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools").is_dir())
SOURCE = ROOT / ".cache/prints/2026-09-23-bulkhead-rings-tap-flavor-mark2-v2/bulkhead-rings-tap-flavor-black-white-z004-mark2-v2-input.3mf"
DEST = ROOT / ".cache/prints/2026-09-23-bulkhead-rings-tap-flavor-mark2-v3/bulkhead-rings-tap-flavor-black-white-z004-mark2-v3-input.3mf"
SOURCE_SHA256 = "ea9ffbbae864f0e047ce6d88e6b00690381e71ac379736b1dde8ec0e1112b4d4"
MODEL = "3D/3dmodel.model"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", CORE)
Q = lambda name: f"{{{CORE}}}{name}"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clean(value):
    return "0" if abs(value) < 0.00000005 else f"{value:.8f}"


def main():
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA256, "The reviewed v2 input changed"
    with ZipFile(SOURCE) as source:
        members = {entry.filename: source.read(entry) for entry in source.infolist()}
        infos = {entry.filename: entry for entry in source.infolist()}

    settings = json.loads(members["Metadata/project_settings.config"])
    assert settings["layer_height"] == settings["initial_layer_print_height"] == "0.08"
    assert settings["top_shell_layers"] == settings["bottom_shell_layers"] == "13"
    assert settings["filament_nozzle_map"] == ["0", "1"]
    assert settings["filament_colour"] == ["#000000", "#FFFFFF"]
    assert "G29.1 Z{0.02} ; for Textured PEI Plate" in settings["machine_start_gcode"]

    model = ET.fromstring(members[MODEL])
    converted = {}
    for obj in model.findall(f"./{Q('resources')}/{Q('object')}"):
        vertices = obj.findall(f"./{Q('mesh')}/{Q('vertices')}/{Q('vertex')}")
        if not vertices:
            continue
        z_top = max(float(v.get("z")) for v in vertices)
        z_low = min(float(v.get("z")) for v in vertices)
        assert abs(z_top - 2.0) < 0.000001
        assert abs(z_low - (1.0 if obj.get("id") in {"2", "5", "8"} else 0.0)) < 0.000001
        for vertex in vertices:
            # A proper half turn about X puts the letter face on the bed. Reversing
            # both Y and Z preserves handedness and the readable assembled word.
            vertex.set("y", clean(-float(vertex.get("y"))))
            vertex.set("z", clean(z_top - float(vertex.get("z"))))
        converted[obj.get("id")] = len(vertices)
    assert set(converted) == {"1", "2", "4", "5", "7", "8"}
    members[MODEL] = ET.tostring(model, encoding="UTF-8", xml_declaration=True)

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(DEST, "w") as output:
        for name, data in members.items():
            output.writestr(infos[name], data)
    with ZipFile(DEST) as staged:
        assert staged.testzip() is None
        for name, data in members.items():
            assert staged.read(name) == data
    print(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": SOURCE_SHA256,
        "staged_input": str(DEST.relative_to(ROOT)),
        "staged_input_sha256": sha(DEST.read_bytes()),
        "changed_members": [name for name in members if name == MODEL],
        "face_down_rotation": "180 degrees about the plate X axis",
        "converted_mesh_vertices": converted,
        "layer_height_mm": 0.08,
        "requested_mark2_z_trim_mm": 0.04,
    }, indent=2))


if __name__ == "__main__":
    main()
