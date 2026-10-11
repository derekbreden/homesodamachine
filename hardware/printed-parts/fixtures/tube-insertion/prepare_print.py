"""Prepare the complete tube-insertion tool's native projects, offline.

Run by hand after generating the tool. ``--slice-output`` also slices each
plate into its own empty directory and writes its ready G-code archive.
This tool neither submits a print nor joins the repository build/check path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(HERE.parents[1] / "faucet"))
import refresh_print_project as writer

BAMBU_STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
READY = HERE / "ready"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(spec: dict) -> tuple[Path, dict]:
    source = ROOT / spec["settings_source"]
    with zipfile.ZipFile(source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {}
    if spec["material"] == "PET-GF":
        requested = {
            "wall_loops": "6",
            "sparse_infill_density": "100%",
            "sparse_infill_pattern": "zig-zag",
            "initial_layer_print_height": "0.2",
            "layer_height": "0.24",
            "enable_support": "1",
            "support_type": "tree(auto)",
            "support_style": "default",
            "enable_prime_tower": "0",
            "print_settings_id": "0.24mm PET-GF tube insertion solid",
        }
        for key, value in requested.items():
            if settings.get(key) != value:
                changes[key] = {"from": settings.get(key), "to": value}
                settings[key] = value
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    profile = ROOT / ".cache/tube-insertion-print" / (spec["id"] + "-settings.3mf")
    writer.archive_write(profile, members)
    project = READY / spec["project"]
    parts = tuple((row["name"], HERE / row["source"], row.get("rotation_x_degrees", 0.0))
                  for row in spec["parts"])
    report = writer.refresh(
        profile, project, parts=parts,
        offsets=tuple(tuple(row["offset_mm"]) for row in spec["parts"]),
        title=spec["title"], z_trim=spec["z_trim_mm"], plate_border=20.0)
    report.update(
        status="offline project preparation; no printer submission",
        printer_submission=False,
        intended_printer=spec["printer"],
        material=spec["material"],
        nozzle_mapping=spec["nozzle_mapping"],
        original_settings_source=spec["settings_source"],
        original_settings_source_sha256=sha(source),
        task_process_changes=changes,
        print_pose=("tube axis vertical; preformed half-channel liners"
                    if spec["material"] == "TPU 85A"
                    else "flat manufacturing STL; open jaw pockets upward"),
    )
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return project, report


def slice_project(project: Path, report: dict, spec: dict, directory: Path) -> dict:
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(f"Use an empty slice directory: {directory}")
    directory.mkdir(parents=True, exist_ok=True)
    archive_name = project.stem + ".gcode.3mf"
    command = [BAMBU_STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", archive_name, "--outputdir", str(directory), str(project)]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    with (directory / "bambu-cli.log").open("w") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env)
    if completed.returncode:
        raise RuntimeError(f"Offline slice failed; {directory / 'bambu-cli.log'}")
    result = json.loads((directory / "result.json").read_text())
    if result.get("return_code") != 0:
        raise RuntimeError(result.get("error_string"))
    sliced = directory / archive_name
    with zipfile.ZipFile(sliced) as archive:
        if archive.testzip() is not None:
            raise ValueError("Sliced archive has a damaged member")
        gcode = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read("Metadata/plate_1.gcode.md5").strip().decode().lower()
        if hashlib.md5(gcode).hexdigest() != expected_md5:
            raise ValueError("Embedded G-code digest differs")
    trims = [float(value) for value in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    expected_trim = [0.0, round(spec["z_trim_mm"] - 0.02, 2)]
    if trims != expected_trim:
        raise ValueError(f"Plate trims {trims} differ from {expected_trim}")
    features = sorted({value.decode() for value in re.findall(rb"^; FEATURE: (.+)$", gcode, re.M)})
    gcode_path = directory / "plate_1.gcode"
    gcode_path.write_bytes(gcode)
    envelope = writer.object_toolpaths(gcode_path, directory / "review.gcode", None)
    low, high = envelope["extrusion_bounds_xy_mm"]
    usable_low, usable_high = report["shared_printable_area_mm"]
    margins = [low[0] - usable_low[0], low[1] - usable_low[1],
               usable_high[0] - high[0], usable_high[1] - high[1]]
    if min(margins) < 20.0:
        raise ValueError(f"Emitted bead margin {min(margins):.2f} mm is below 20 mm")
    target = READY / archive_name
    target.write_bytes(sliced.read_bytes())
    plate, = result["sliced_plates"]
    record = {
        "status": "offline slice reviewed; no physical print or force qualification",
        "printer_submission": False,
        "project": project.name,
        "project_sha256": sha(project),
        "archive": target.name,
        "archive_sha256": sha(target),
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
        "source_stls": {row["source"]: row["stl_sha256"] for row in report["parts"]},
        "printer": spec["printer"],
        "nozzle_mapping": spec["nozzle_mapping"],
        "plate_trim_commands_mm": trims,
        "features": features,
        "support_generated": any("Support" in value for value in features),
        "bead_envelope": envelope,
        "bead_margin_mm": margins,
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": sum(row["total_used_g"] for row in plate["filaments"]),
        "slicer_warning": plate["warning_message"],
        "native_process": {key: result.get(key) for key in
                           ("layer_height", "wall_loops", "sparse_infill_density")},
    }
    project.with_suffix(".readiness.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plate", help="Prepare just this print-layout plate ID")
    parser.add_argument("--slice-output", type=Path)
    args = parser.parse_args()
    layout = json.loads((HERE / "print-layout.json").read_text())
    selected = [spec for spec in layout["plates"] if args.plate is None or spec["id"] == args.plate]
    if not selected:
        parser.error("Unknown plate ID")
    for spec in selected:
        project, report = prepare(spec)
        print(project.relative_to(ROOT), flush=True)
        if args.slice_output:
            record = slice_project(project, report, spec,
                                   args.slice_output.resolve() / spec["id"])
            print(json.dumps({key: record[key] for key in
                              ("archive", "layers", "estimated_seconds", "estimated_filament_g",
                               "support_generated", "bead_margin_mm")}), flush=True)


if __name__ == "__main__":
    main()
