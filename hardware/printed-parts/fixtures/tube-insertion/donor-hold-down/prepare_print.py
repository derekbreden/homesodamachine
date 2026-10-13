"""Manually prepare and optionally slice one face-down TPU donor hand pad.

This file submits no printer job and is not part of the build/check path.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/docgen").is_dir())
READY = HERE / "ready"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

module_spec = importlib.util.spec_from_file_location("fixture_print", FIXTURE / "prepare_print.py")
fixture_print = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(fixture_print)
writer = fixture_print.writer

SETTINGS_SOURCE = (FIXTURE / "prints/2026-10-12-tpu-liners-close-z000-mark1"
                   / "2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.3mf")
PROJECT = READY / "donor-hold-down-half-body-tpu85a-right06-z018-mark1.3mf"
SPEC = {
    "printer": "Mark1 (H2C)",
    "nozzle_mapping": "Right fixed 0.6 mm; black TPU 85A external spool 255",
    "z_trim_mm": 0.18,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice-output", type=Path)
    args = parser.parse_args()
    reviewed = json.loads(SETTINGS_SOURCE.with_suffix(".readiness.json").read_text())
    if fixture_print.sha(SETTINGS_SOURCE) != reviewed["project_sha256"]:
        raise ValueError("TPU recipe source differs from its reviewed project")
    with zipfile.ZipFile(SETTINGS_SOURCE) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings["print_compatible_printers"] = ["Bambu Lab H2C 0.6 Standard +0.18 Z trim"]
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    profile = ROOT / ".cache/donor-hold-down-settings.3mf"
    writer.archive_write(profile, members)
    report = writer.refresh(
        profile, PROJECT,
        parts=(("TPU upper-half donor cover", HERE / "donor-hold-down-print.stl", 0.0),),
        offsets=((0.0, 0.0),), title="Touch-Flo TPU half-body hold-down cover",
        z_trim=SPEC["z_trim_mm"], plate_border=20.0)
    report.update(
        status="offline project preparation; no printer submission",
        printer_submission=False, intended_printer=SPEC["printer"],
        material="Black TPU 85A", nozzle_mapping=SPEC["nozzle_mapping"],
        print_pose="Broad flat hand face down; conforming upper-half donor cavity upward",
        z_trim_basis="Mark1 standard +0.18 mm; the liner job's +0.00 mm exception is local to that job",
        original_settings_source=str(SETTINGS_SOURCE.relative_to(ROOT)),
        original_settings_source_sha256=fixture_print.sha(SETTINGS_SOURCE),
        process_compatibility_binding="Bambu Lab H2C 0.6 Standard +0.18 Z trim",
    )
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    print(PROJECT.relative_to(ROOT), flush=True)
    if args.slice_output:
        record = fixture_print.slice_project(
            PROJECT, report, SPEC, args.slice_output.resolve(), ready_directory=READY)
        with zipfile.ZipFile(READY / record["archive"]) as archive:
            native_settings = json.loads(archive.read(writer.SETTINGS_MEMBER))
        process_keys = ("filament_type", "filament_settings_id", "curr_bed_type",
                        "layer_height", "initial_layer_print_height", "wall_loops",
                        "sparse_infill_density", "enable_support", "filament_nozzle_map")
        changed = [key for key in process_keys if native_settings.get(key) != settings.get(key)]
        if changed:
            raise ValueError(f"Native slice changed the requested TPU recipe: {changed}")
        record["native_material_process"] = {key: native_settings.get(key) for key in process_keys}
        PROJECT.with_suffix(".readiness.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps({key: record[key] for key in (
            "archive", "layers", "estimated_seconds", "estimated_filament_g",
            "support_generated", "bead_margin_mm")}), flush=True)


if __name__ == "__main__":
    main()
