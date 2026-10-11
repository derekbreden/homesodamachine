"""Prepare the complete Industrial faucet with the accepted PET-GF recipe.

The project contains the Industrial base, relaxed cover and mounting plate,
plus the shared faucet tip and side-down lever. The TPU gasket is a separate print. Optional
slicing runs Bambu Studio locally and never connects to a printer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

TITLE = "Industrial faucet PET-GF"
PROJECT = HERE / "faucet-industrial-petgf.3mf"
ACCEPTANCE = HERE / "physical-acceptance.json"
ACCEPTED = json.loads(ACCEPTANCE.read_text())
RECIPE = writer.ROOT / ACCEPTED["prepared_project"]
PROFILE = RECIPE
FINISH = HERE / "finish-selection.json"
GASKET = HERE / "industrial-above-counter-gasket.stl"
# Separate spaces for each part's brim and automatically generated supports.
PART_OFFSETS = ((-80.0, 0.0), (20.0, 47.0), (89.0, 86.0), (43.0, -52.0), (-17.5, -60.0))
PROTECTED_SCULPTED = tuple((FAUCET / "faucet-petgf.3mf").with_suffix(suffix) for suffix in (
    ".3mf", ".print.json", ".support-audit.json", ".readiness.json"))


def relative(path: Path) -> str:
    path = path.resolve()
    return str(path.relative_to(writer.ROOT) if path.is_relative_to(writer.ROOT) else path)


def profile_members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if name == writer.SETTINGS_MEMBER
            or name.startswith("Metadata/filament_settings_") and name.endswith(".config")
        }


def protected_hashes() -> dict[str, str]:
    return {relative(path): writer.digest(path.read_bytes())
            for path in PROTECTED_SCULPTED if path.is_file()}


def industrial_parts() -> tuple:
    # Assembly-frame STLs use the shared production print rotations.
    rotations = {name: rotation for name, _, rotation in writer.PARTS}
    parts = (
        ("industrial-shell-base", HERE / "industrial-shell-base.stl",
         rotations["faucet-shell-base"]),
        ("faucet-shell-tip", FAUCET / "faucet-shell/faucet-shell-tip.stl",
         rotations["faucet-shell-tip"]),
        ("industrial-display-cover", HERE / "industrial-display-cover.stl",
         rotations["faucet-display-cover"]),
        ("industrial-above-counter-plate", HERE / "industrial-above-counter-plate.stl", 0.0),
        ("lever-replica", FAUCET / "lever-replica/lever-replica-side-down.stl", 0.0),
    )
    missing = [relative(path) for _, path, _ in parts if not path.is_file()]
    if missing:
        raise FileNotFoundError("Generate the Industrial STLs before preparing the project: "
                                + ", ".join(missing))
    return parts


def shoulder_readings(report: dict, recipe_report: dict) -> list[dict]:
    row = report["parts"][0]
    mesh = trimesh.load(writer.ROOT / row["source"], force="mesh", process=True)
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3)
    readings = []
    for reference in recipe_report["selected_faces"]:
        z = reference["cad_z_mm"]
        mask = ((np.abs(mesh.triangles[:, :, 2] - z).max(axis=1) < 1e-5)
                & (mesh.face_normals[:, 2] > .9999))
        if not mask.any():
            raise ValueError(f"The current base has no upward shoulder at CAD Z{z:g}")
        points = mesh.triangles[mask].reshape(-1, 3)
        placed = (points - row["source_center_mm"]) @ rotation + row["plate_translation_mm"]
        readings.append({"cad_z_mm": z, "pick_mm": reference["pick_mm"],
                         "measurement": "Current source STL upward planar facets at the selected CAD Z",
                         "area_mm2": float(mesh.area_faces[mask].sum()),
                         "cad_bounds_mm": [points.min(axis=0).tolist(), points.max(axis=0).tolist()],
                         "print_z_span_mm": [float(placed[:, 2].min()), float(placed[:, 2].max())],
                         "fine_band_print_z_mm": reference["fine_band_print_z_mm"]})
    return readings


def write_readiness(project: Path, report: dict, reading: dict | None = None,
                    slice_directory: Path | None = None) -> dict:
    """Record what this offline preparation actually checked."""
    result = {
        "project_title": TITLE,
        "status": ("selected finish offline slice and support audit passed"
                   if reading is not None else "complete current project prepared with selected finish; native review pending"),
        "preparation_only": True,
        "launch_authorized": False,
        "finish_choices_pending": [],
        "finish_selection": relative(FINISH),
        "project": relative(project),
        "project_sha256": report["project_sha256"],
        "settings_sha256": report["settings_sha256"],
        "print_report_sha256": writer.digest(project.with_suffix(".print.json").read_bytes()),
        "profile_source": report["profile_source"],
        "all_profile_members_preserved_byte_for_byte": report["all_profile_members_preserved_byte_for_byte"],
        "source_stls": {part["source"]: part["stl_sha256"] for part in report["parts"]},
        "mesh_and_placement": {
            "closed_oriented_single_body_meshes": True,
            "embedded_meshes_match_source_stls": True,
            "parts": len(report["parts"]),
            "plates": report["plate_count"],
            "minimum_required_model_bed_margin_mm": 40.0,
        },
        "offline_slice": {"completed": reading is not None},
        "printer_submission": {"performed_by_this_tool": False},
        "physical_print": {
            "evaluated": False,
            "remaining": "Support removal, contact finish, display fit and retention are physical print readings.",
        },
        "gasket": {"source": relative(GASKET), "material": "TPU", "included_in_petgf_project": False},
        "color": "The same meshes and project geometry serve black and white PET-GF.",
        "sculpted_artifacts_unchanged": report["sculpted_artifacts_unchanged"],
    }
    if reading is not None:
        result["offline_slice"].update({
            "directory": relative(slice_directory),
            "slicer": reading["slicer"],
            "support_audit_sha256": writer.digest(project.with_suffix(".support-audit.json").read_bytes()),
            "plates": reading["plates"],
            "fit": reading["fit"],
            "physical_support_removal_validated": False,
        })
    project.with_suffix(".readiness.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def refresh(settings_from: Path = PROFILE, output: Path = PROJECT,
            printer: str | None = None, filament_colour: str | None = None) -> dict:
    settings_from, output = settings_from.resolve(), output.resolve()
    finish = json.loads(FINISH.read_text())
    printer = printer or finish["default_printer"]
    trim = {"Mark1": .18, "Mark2": .04}[printer]
    filament_colour = filament_colour or finish["default_filament_colour"]
    if output == settings_from or output == RECIPE.resolve() or output in {path.resolve() for path in PROTECTED_SCULPTED}:
        raise ValueError("The Industrial output must not replace its settings source or the Sculpted project")
    if output.suffix.lower() != ".3mf":
        raise ValueError("The Industrial project needs a .3mf filename")
    before = protected_hashes()
    if writer.digest(RECIPE.read_bytes()) != ACCEPTED["prepared_project_sha256"]:
        raise ValueError("The accepted five-part recipe has changed")
    recipe_report = json.loads((RECIPE.parent / "preparation.json").read_text())
    preserved = profile_members(settings_from)
    parts = industrial_parts()
    report = writer.refresh(settings_from, output, parts=parts,
                            offsets=PART_OFFSETS, title=TITLE, plate_border=40.0,
                            z_trim=trim)
    # One perimeter-spanning region retains the accepted reinforcement without
    # splitting the outside wall at the three screw hosts.
    regions = tuple({"part": r["part"], "name": r["name"],
                     "source_bounds_mm": r["source_bounds_mm"], "clip_to_part_bounds": False}
                    for r in recipe_report["local_solid_regions"])
    writer.add_local_solid_regions(output, report, regions)
    with zipfile.ZipFile(output) as archive, zipfile.ZipFile(RECIPE) as recipe:
        members = {name: archive.read(name) for name in archive.namelist()}
        config = ET.fromstring(members["Metadata/model_settings.config"])
        source_config = ET.fromstring(recipe.read("Metadata/model_settings.config"))
        source_objects = {obj.find("metadata[@key='name']").get("value"): obj
                          for obj in source_config.findall("object")}
        for obj in config.findall("object"):
            name = obj.find("metadata[@key='name']").get("value")
            for setting in source_objects[name].findall("metadata"):
                key = setting.get("key")
                if key and key not in ("name", "extruder"):
                    writer.metadata(obj, key, setting.get("value"))
        members["Metadata/model_settings.config"] = writer.xml(config)
        members["Metadata/layer_config_ranges.xml"] = recipe.read("Metadata/layer_config_ranges.xml")
        settings = json.loads(members[writer.SETTINGS_MEMBER])
        original_colour = settings["filament_colour"]
        settings["filament_colour"] = [filament_colour]
        members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
        for obj in config.findall("object"):
            for key, value in finish["seam_object_overrides"].items():
                writer.metadata(obj, key, value)
        ranges = ET.fromstring(members["Metadata/layer_config_ranges.xml"])
        for entry, band in zip(ranges.find("object").findall("range"),
                               finish["base_fine_bands_print_z_mm"], strict=True):
            entry.set("min_z", f"{band[0]:.4f}")
            entry.set("max_z", f"{band[1]:.4f}")
        members["Metadata/model_settings.config"] = writer.xml(config)
        members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges)
    writer.archive_write(output, members)
    if report["plate_count"] != 1 or len(report["parts"]) != 5:
        raise ValueError("The complete Industrial project needs five rigid parts on one plate")
    actual_profile = profile_members(output)
    before_settings = json.loads(preserved[writer.SETTINGS_MEMBER])
    after_settings = json.loads(actual_profile[writer.SETTINGS_MEMBER])
    changed_settings = {k for k in set(before_settings) | set(after_settings)
                        if before_settings.get(k) != after_settings.get(k)}
    if changed_settings - {"machine_start_gcode", "printer_settings_id", "filament_colour"}:
        raise ValueError("Unexpected change to the complete PET-GF profile")
    if any(actual_profile.get(n) != data for n, data in preserved.items()
           if n != writer.SETTINGS_MEMBER):
        raise ValueError("The PET-GF filament profile was not preserved")
    if protected_hashes() != before:
        raise ValueError("A Sculpted project artifact changed during Industrial preparation")
    for row in report["parts"]:
        if writer.digest((writer.ROOT / row["source"]).read_bytes()) != row["stl_sha256"]:
            raise ValueError(f"{row['name']} changed while preparing the project")
    report.update({
        "project_title": TITLE,
        "profile_source": relative(settings_from),
        "project_sha256": writer.digest(output.read_bytes()),
        "settings_sha256": writer.digest(actual_profile[writer.SETTINGS_MEMBER]),
        "native_settings_sha256": writer.digest(actual_profile[writer.SETTINGS_MEMBER]),
        "all_profile_members_preserved_byte_for_byte": actual_profile == preserved,
        "profile_member_sha256": {name: writer.digest(data) for name, data in actual_profile.items()},
        "sculpted_artifacts_unchanged": before,
        "shared_tip_source": relative(parts[1][1]),
        "gasket_included": False,
        "color_independent_geometry": True,
        "accepted_recipe": relative(RECIPE),
        "accepted_recipe_sha256": ACCEPTED["prepared_project_sha256"],
        "accepted_geometry_tag": ACCEPTED["tag"],
        "active_nozzle": 0,
        "printer": printer,
        "requested_z_trim_mm": trim,
        "selected_faces": shoulder_readings(report, recipe_report),
        "insert_review_regions": recipe_report["insert_review_regions"],
        "review_host_regions": recipe_report["review_host_regions"],
        "preparation_only": True,
        "launch_authorized": False,
        "submitted": False,
        "send_attempted": False,
        "finish_choices_pending": [],
        "finish_selection": relative(FINISH),
        "selected_finish": finish,
        "provisional_finish": "SB scarf slope gap 10%; E eight coarse lip layers before 0.12 mm; full-print confirmation pending",
    })
    if original_colour != [filament_colour]:
        report["settings_changes"]["filament_colour"] = {"from": original_colour, "to": [filament_colour]}
    for face, band in zip(report["selected_faces"], finish["base_fine_bands_print_z_mm"], strict=True):
        face["fine_band_print_z_mm"] = band
    from prepare_vent_prints import source_hashes
    report["source_sha256"] = source_hashes(parts)
    for path in (Path(__file__), RECIPE, ACCEPTANCE, FINISH):
        report["source_sha256"][relative(path)] = writer.digest(path.read_bytes())
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    write_readiness(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--settings-from", type=Path, default=PROFILE)
    parser.add_argument("--printer", choices=("Mark1", "Mark2"),
                        help="Apply this printer's standard Z trim; default is the selected finish recipe's printer.")
    parser.add_argument("--filament-colour", help="Spool colour reported by the destination printer, as #RRGGBB.")
    parser.add_argument("--slice-output", type=Path,
                        help="Optional empty directory for an offline Bambu Studio slice; no printer connection.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    directory = args.slice_output.resolve() if args.slice_output else None
    if directory and directory.exists() and any(directory.iterdir()):
        parser.error("--slice-output must be empty so the audit cannot consume an earlier slice")
    project = args.project.resolve()
    report = refresh(args.settings_from, project, args.printer, args.filament_colour)
    print(f"{project}: five rigid parts on one plate; exact PET-GF settings {report['settings_sha256']}", flush=True)
    for row in report["parts"]:
        print(f"  {row['name']}: Rx {row['rotation_x_degrees']:g} degrees; {row['triangles']} triangles", flush=True)
    if directory is None:
        return
    before = protected_hashes()
    directory.mkdir(parents=True, exist_ok=True)
    command = [str(args.slicer.resolve()), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(directory), str(project)]
    log = directory / "bambu-cli.log"
    with log.open("w") as stream:
        result = subprocess.run(command, cwd=directory, stdout=stream, stderr=subprocess.STDOUT)
    print(f"Offline slice exited {result.returncode}; {log}", flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
    reading = writer.slice_review(project, report, directory)
    if protected_hashes() != before:
        raise ValueError("A Sculpted project artifact changed during the Industrial slice")
    write_readiness(project, report, reading, directory)
    print(json.dumps(reading["fit"], indent=2), flush=True)


if __name__ == "__main__":
    main()
