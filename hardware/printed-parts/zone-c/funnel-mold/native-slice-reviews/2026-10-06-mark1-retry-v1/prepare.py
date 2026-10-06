"""Prepare Mark1's editable retry project from the identified right-nozzle job."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools").is_dir())
PUBLIC = Path(__file__).resolve().parent
SOURCE = PUBLIC.parent / "2026-10-06-h2c-right-gyroid15/funnel-mold-h2c-right.3mf"
DESTINATION = PUBLIC / "funnel-mold-mark1-retry.3mf"
SOURCE_SHA = "60cd9a0e48a51edcec2fc5f2310e64e5232d6c0a903b6fb0606312f3d2f1fb57"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(SOURCE) == SOURCE_SHA
with zipfile.ZipFile(SOURCE) as z:
    assert z.testzip() is None
    payloads = {n: z.read(n) for n in z.namelist()}
settings = json.loads(payloads["Metadata/project_settings.config"])
original = dict(settings)
settings.update({
    "initial_layer_speed": ["20"] * len(settings["initial_layer_speed"]),
    "initial_layer_infill_speed": ["30"] * len(settings["initial_layer_infill_speed"]),
    "brim_type": "outer_only",
    "brim_width": "8",
})
# Probing remains disabled at Derek's explicit direction. Camera detection is
# a separate device preference; this preparation does not alter it.
assert settings["enable_wrapping_detection"] == "0"
assert settings["timelapse_type"] == "0"
assert settings["filament_map"] == ["2"]
payloads["Metadata/project_settings.config"] = (json.dumps(settings, indent=2) + "\n").encode()

core = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", core)
ET.register_namespace("p", "http://schemas.microsoft.com/3dmanufacturing/production/2015/06")
model = ET.fromstring(payloads["3D/3dmodel.model"])
placements = []
for item in model.find("{" + core + "}build"):
    values = list(map(float, item.attrib["transform"].split()))
    before = list(values)
    values[9] += 28.0  # Right-nozzle usable X25..330 has its centre at X177.5.
    item.set("transform", " ".join(f"{v:.12g}" for v in values))
    placements.append({"object_id": item.attrib["objectid"],
                       "source_transform": before, "prepared_transform": values,
                       "local_plate_center_xy_mm": [177.5, 160.0]})
payloads["3D/3dmodel.model"] = ET.tostring(model, xml_declaration=True, encoding="UTF-8")

with zipfile.ZipFile(DESTINATION, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in payloads.items():
        z.writestr(name, data)
with zipfile.ZipFile(SOURCE) as a, zipfile.ZipFile(DESTINATION) as b:
    assert b.testzip() is None
    changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
    assert set(changed) == {"Metadata/project_settings.config", "3D/3dmodel.model"}
    mesh_hashes = {n: hashlib.sha256(b.read(n)).hexdigest()
                   for n in b.namelist() if n.startswith("3D/Objects/")}

previous = json.loads((SOURCE.parent / "preparation-review.json").read_text())
essential = set(previous["selected_recipe"]) | {
    "initial_layer_speed", "initial_layer_infill_speed", "initial_layer_acceleration",
    "brim_type", "brim_width", "brim_object_gap", "enable_wrapping_detection", "timelapse_type",
}
record = {
    "checked_date": "2026-10-06",
    "scope": "Preparation only. No print submission, device preference change or calibration is performed.",
    "selected_recipe": {k: settings[k] for k in sorted(essential)},
    "preparation": {
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "prepared_project": str(DESTINATION.relative_to(ROOT)),
        "prepared_project_sha256": sha(DESTINATION),
        "setting_changes": {k: {"source": original[k], "prepared": settings[k]}
                            for k in settings if original[k] != settings[k]},
        "placements": placements,
        "changed_container_entries": changed,
        "embedded_geometry_byte_identical": True,
        "embedded_geometry_sha256": mesh_hashes,
        "all_other_payloads_identical": True,
    },
    "send_options_required": {
        "timelapse": "On", "bed_leveling": "On",
        "flow_dynamic_calibration": "On", "nozzle_offset_calibration": "On",
        "reason_for_calibration": "Replacement induction heating assembly and new right 0.4 mm nozzle reported by Derek.",
    },
    "detection": {
        "probing_enabled": False, "camera_settings_changed": False,
        "user_direction": "No, we've had problems with that too - do not enable that.",
        "timelapse_send_checkbox_required": True,
    },
    "reference_geometry_and_bead_review": str((SOURCE.parent / "readiness-review.json").relative_to(ROOT)),
}
(PUBLIC / "preparation-review.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"project": str(DESTINATION.relative_to(ROOT)), "sha256": sha(DESTINATION),
                  "setting_changes": record["preparation"]["setting_changes"],
                  "probing_enabled": False}, indent=2))
