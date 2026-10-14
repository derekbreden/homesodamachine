"""Offline preparation of one compact V elbow in Bambu TPU 85A on Mark1.

Run with tools/cad-venv/bin/python from the repository root. --colour RRGGBB
records an observed spool colour; omitting it uses an unverified black placeholder.
This script does not connect to a printer or establish loading/feed-path readiness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
STUDY = ROOT / "future/pump-elbow-exploration"
HELPER = STUDY / "prints/2026-10-13-full-base-single-tpu85a-mark1/prepare_mark1.py"
GEOMETRY = STUDY / "tpu_elbow.py"
PROFILE_NAME = "Bambu TPU 85A @BBL H2C"
STEM = "2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1"
PROJECT, ARCHIVE = HERE / (STEM + ".3mf"), HERE / (STEM + ".gcode.3mf")
MODEL = HERE / "compact-single-elbow-print.stl"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colour", help="Actual spool colour, exactly six hexadecimal digits")
    args = parser.parse_args()
    colour = (args.colour or "000000").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", colour):
        parser.error("--colour must be RRGGBB")
    helper = load(HELPER, "compact_single_native_helpers")
    helper.HERE, helper.PROJECT, helper.ARCHIVE, helper.MODEL = HERE, PROJECT, ARCHIVE, MODEL
    machine_recipe = helper.recipe_helpers
    recipe, original, _, low, high = machine_recipe.settings()
    profiles = {}
    selected = machine_recipe.filament(PROFILE_NAME, profiles)
    recipe.update(selected)
    recipe.update({"filament_settings_id": [PROFILE_NAME], "filament_ids": ["GFU04"],
                   "filament_colour": ["#" + colour],
                   "filament_type": ["TPU"], "filament_map": ["2"], "filament_nozzle_map": ["1"],
                   "filament_extruder_compatibility": ["0"],
                   "curr_bed_type": "Engineering Plate",
                   "print_settings_id": "One compact TPU 85A elbow 0.12 mm right 0.6 Mark1"})
    # This job uses the manufacturer's unmodified machine-start template.
    # On Engineering Plate with a 0.6 mm nozzle it emits only the Z0 reset.
    stock_start = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/machine/Bambu Lab H2C 0.4 nozzle template machine_start_gcode.json")
    stock_payload = stock_start.read_bytes()
    recipe["machine_start_gcode"] = json.loads(stock_payload)["machine_start_gcode"]
    recipe["printer_settings_id"] = "Bambu Lab H2C 0.6 nozzle"
    recipe["print_compatible_printers"] = ["Bambu Lab H2C 0.6 nozzle"]
    recipe["print_settings_id"] = "One compact TPU85A elbow Engineering Plate zero Z trim Mark1"
    dependencies = {str(p.relative_to(ROOT)): helper.sha(p.read_bytes()) for p in
                    (GEOMETRY, HELPER, Path(machine_recipe.__file__))}
    module = load(GEOMETRY, "compact_single_elbow_geometry")
    specimen = helper.make_project(recipe, low, high, module.Elbow().print_shape())
    # Set the visible labels for this compact geometry; keep the proven native
    # object/volume/instance structure of the single-specimen serializer.
    with zipfile.ZipFile(PROJECT) as z:
        members = {n: z.read(n) for n in z.namelist()}
    for member in ("3D/3dmodel.model", "Metadata/model_settings.config"):
        members[member] = members[member].replace(b"full-base", b"compact")
    machine_recipe.archive_write(PROJECT, members)
    cache = ROOT / ".cache/printer-control/compact-single-elbow-tpu85a-engineering-z000-mark1-20261013"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    preflight = {"scope": "Offline compact-elbow material trial; loading and feed mapping unverified",
                 "ready_to_send": False, "spool_loading_verified": False,
                 "colour_is_placeholder": args.colour is None, "sliced_colour": colour,
                 "material_recipe": "Bambu TPU 85A / GFU04 / TPU",
                 "source_geometry": str(GEOMETRY.relative_to(ROOT)), "source_dependencies_sha256": dependencies,
                 "native_filament_profile_sources_sha256": profiles,
                 "machine_profile_donor": str(machine_recipe.DONOR.relative_to(ROOT)),
                 "machine_profile_donor_sha256": helper.sha(machine_recipe.DONOR.read_bytes()),
                 "machine_start_gcode_sha256": helper.sha(recipe["machine_start_gcode"].encode()),
                 "stock_machine_start_source": str(stock_start), "stock_machine_start_source_sha256": helper.sha(stock_payload),
                 "user_z_trim_mm": 0.0, "bed_type": "Engineering Plate",
                 "project": PROJECT.name, "project_sha256": helper.sha(PROJECT.read_bytes()),
                 "specimen": specimen,
                 "settings_changes": {k: {"from": original.get(k), "to": v}
                                      for k, v in recipe.items() if original.get(k) != v}}
    PROJECT.with_suffix(".print.json").write_text(json.dumps(preflight, indent=2) + "\n")
    command = [str(helper.SLICER), "--slice", "0", "--arrange", "0", "--orient", "0", "--export-3mf",
               ARCHIVE.name, "--outputdir", str(run), str(PROJECT)]
    with (run / "slice.log").open("w") as log:
        subprocess.run(command, cwd=run, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((run / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    native = run / ARCHIVE.name
    with zipfile.ZipFile(native) as z:
        if z.testzip() is not None:
            raise ValueError("Native ZIP checksum error")
        gcode = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
        emitted = json.loads(z.read(helper.SETTINGS))
        slices = ET.fromstring(z.read("Metadata/slice_info.config"))
        model = ET.fromstring(z.read("3D/3dmodel.model"))
        config = ET.fromstring(z.read("Metadata/model_settings.config"))
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0]:
        raise ValueError(f"Unexpected Mark1 trim: {trims}")
    for key in ("wall_loops", "sparse_infill_density", "spiral_mode", "enable_support",
                "filament_map", "filament_colour", "filament_type", "curr_bed_type", "machine_start_gcode"):
        if emitted.get(key) != recipe[key]:
            raise ValueError(f"Native setting differs for {key}: {emitted.get(key)}")
    plate, = slices.findall("plate")
    used, = plate.findall("filament")
    if used.get("type") != "TPU" or used.get("tray_info_idx") != "GFU04":
        raise ValueError("The slice does not use Bambu TPU 85A")
    counts = {"build_instances": len(model.findall(f"{helper.qn('build')}/{helper.qn('item')}")),
              "model_objects": len(config.findall("object")),
              "normal_volumes": len(config.findall("object/part[@subtype='normal_part']")),
              "slice_objects": len([v for v in plate.findall("object") if v.get("skipped") != "true"])}
    if set(counts.values()) != {1}:
        raise ValueError(f"The plate must contain exactly one specimen: {counts}")
    deposition = helper.beads(gcode)
    bead_low, bead_high = map(np.array, deposition["native_full_bead_bounds_xy_mm"])
    margins = [*(bead_low - low), *(high - bead_high)]
    if min(margins) < 20:
        raise ValueError("Native beads enter the 20 mm bed inset")
    if any(helper.sha((ROOT / p).read_bytes()) != digest for p, digest in dependencies.items()):
        raise ValueError("A source changed during preparation")
    (run / "plate_1.gcode").write_bytes(gcode)
    ARCHIVE.write_bytes(native.read_bytes())
    row, = result["sliced_plates"]
    keys = ("printer_settings_id", "filament_settings_id", "filament_map", "filament_nozzle_map", "filament_colour",
            "filament_type", "nozzle_diameter", "curr_bed_type", "nozzle_temperature", "nozzle_temperature_initial_layer",
            "eng_plate_temp", "eng_plate_temp_initial_layer", "filament_flow_ratio", "filament_max_volumetric_speed", "filament_retraction_length",
            "fan_min_speed", "fan_max_speed", "layer_height", "initial_layer_print_height", "wall_loops",
            "wall_generator", "sparse_infill_density", "spiral_mode", "seam_gap", "enable_support", "brim_width", "brim_type")
    readiness = {"status": "Offline native slice reviewed; loading/feed mapping unverified; not ready to send",
                 "ready_to_send": False, "colour_is_placeholder": args.colour is None,
                 "observed_at": datetime.now(timezone.utc).isoformat(), "cache_run": str(run.relative_to(ROOT)),
                 "project": PROJECT.name, "project_sha256": preflight["project_sha256"], "archive": ARCHIVE.name,
                 "archive_sha256": helper.sha(ARCHIVE.read_bytes()), "gcode_sha256": helper.sha(gcode),
                 "source_dependencies_sha256": dependencies, "native_filament_profile_sources_sha256": profiles,
                 "specimen": specimen, "native_single_specimen_counts": counts, "plate_trim_commands_mm": trims,
                 "user_z_trim_mm": 0.0, "stock_machine_start_source": str(stock_start),
                 "stock_machine_start_source_sha256": helper.sha(stock_payload),
                 "machine_start_gcode_matches_stock": emitted["machine_start_gcode"] == json.loads(stock_payload)["machine_start_gcode"],
                 "emitted_settings": {k: emitted.get(k) for k in keys}, "native_active_filament": used.attrib,
                 "minimum_full_bead_edge_margin_mm": min(margins),
                 "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
                 "estimated_seconds": row["total_predication"],
                 "estimated_filament_g": sum(f["total_used_g"] for f in row["filaments"]),
                 "estimate_density_g_cm3": emitted["filament_density"], "slicer_warning": row["warning_message"], **deposition}
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
    print(json.dumps(readiness, indent=2))


if __name__ == "__main__":
    main()
