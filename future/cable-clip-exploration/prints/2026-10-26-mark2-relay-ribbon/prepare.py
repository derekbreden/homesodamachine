"""Offline Mark2 slice of the bare J5 relay-ribbon coupon. Never sends a print.

Run manually with tools/cad-venv/bin/python. The current shared PET-GF process
is retained; the local declaration changes only geometry, orientation and border.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
SHARED = ROOT / "hardware/printed-parts/enclosure/trial-preparation"
STUDY = HERE.parents[1]
PIECE = "relay-ribbon-4p-upright"
PART = "relay-ribbon-4p-print"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def source_binding():
    report_path = STUDY / "geometry-report.json"
    report = json.loads(report_path.read_text())
    expected = {report["source"]: report["source_sha256"], **report["files"]}
    actual = {name: sha(ROOT / name) for name in expected}
    if actual != expected:
        raise ValueError("The geometry report does not bind the current source/STEP/STL")
    return {**actual, relative(report_path): sha(report_path)}


def declaration():
    shared_path = SHARED / "pieces.json"
    shared = json.loads(shared_path.read_text())
    spec = {key: copy.deepcopy(value) for key, value in shared.items() if key != "pieces"}
    piece = copy.deepcopy(shared["pieces"]["factory-tools"])
    piece.update(parts=[{"stl": relative(STUDY / "parts" / f"{PART}.stl")}],
                 yaw_degrees=0, plate_border_mm=80,
                 settings={"brim_type": {"value":"no_brim",
                     "reason":"Derek requests the installed orientation and a larger wall footprint below the hook instead of a brim. The coupon has a 24 by 3 mm wall footprint and 6 mm of wall below the hook."},
                     "brim_width":{"value":"0","reason":"No brim on this enlarged-wall fit coupon."}})
    spec["pieces"] = {PIECE: piece}
    spec["source_declaration"] = relative(shared_path)
    spec["source_declaration_sha256"] = sha(shared_path)
    save(HERE / "job.json", spec)


def summarize(directory, binding, review):
    preparation = json.loads((directory / "preparation.json").read_text())
    archive = ROOT / preparation["archive"]
    native = json.loads((directory / "slice-result.json").read_text())
    plate = native["sliced_plates"][0]
    previews = []
    with zipfile.ZipFile(archive) as sliced:
        settings = json.loads(sliced.read("Metadata/project_settings.config"))
        for name in sliced.namelist():
            if name.startswith("Metadata/") and name.endswith(".png"):
                destination = directory / Path(name).name
                destination.write_bytes(sliced.read(name))
                previews.append(relative(destination))
    if binding != source_binding():
        raise ValueError("Geometry inputs changed during this offline slice")
    result = {
        "status": "Offline preparation and native path review; no printer submission.",
        "submitted": False,
        "source_sha256": binding,
        "preparer_sha256": sha(Path(__file__)),
        "directory": relative(directory),
        "project": preparation["project"],
        "project_sha256": preparation["project_sha256"],
        "archive": preparation["archive"],
        "archive_sha256": preparation["archive_sha256"],
        "profile": preparation["profile"],
        "profile_sha256": preparation["profile_sha256"],
        "printer": preparation["printer"],
        "nozzle": preparation["nozzle"],
        "material": preparation["material"],
        "requested_z_trim_mm": preparation["requested_z_trim_mm"],
        "emitted_z_trim_mm": review["emitted_z_trim_mm"],
        "process": {key: settings.get(key) for key in (
            "wall_loops", "sparse_infill_density", "sparse_infill_pattern", "layer_height",
            "initial_layer_print_height", "enable_support", "support_type", "support_style",
            "brim_type", "brim_width", "filament_colour", "filament_map", "curr_bed_type",
            "overhang_fan_threshold", "overhang_fan_speed")},
        "model_pose": "Entry-up STL, with no rotation. The 24 by 3 mm wall edge starts on the bed; the 45 degree hook corbel starts 6 mm above it.",
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": sum(float(f["total_used_g"]) for f in plate["filaments"]),
        "filaments": plate["filaments"],
        "slicer_warnings": plate.get("warning_message"),
        "native_preview_images": previews,
        "native_review": relative(directory / "review.json"),
        "native_review_pass": review["pass"],
        "minimum_bead_margin_mm": review["minimum_bed_margin_mm"],
        "first_second_layer_stack": review["first_second_layer_stack"],
        "support_topology": review["support_topology"],
        "physical_evaluation": "Use the actual bare 22 AWG 4P relay ribbon to evaluate insertion, retention, slide, release and layer/root survival. Modeled stock dimensions are not caliper acceptance.",
    }
    save(HERE / "offline-review.json", result)
    print(json.dumps(result, indent=2), flush=True)


def main():
    binding = source_binding()
    declaration()
    preparer = module("relay_ribbon_shared_prepare", SHARED / "prepare.py")
    reader = module("relay_ribbon_shared_review", SHARED / "review.py")
    preparer.SPEC_PATH = HERE / "job.json"
    if len(sys.argv) == 2:
        directory = Path(sys.argv[1]).resolve()
    else:
        directory = preparer.prepare(PIECE, output=HERE)
        preparer.slice_project(directory)
    reviewed = reader.review(directory)
    summarize(directory, binding, reviewed)


if __name__ == "__main__":
    main()
