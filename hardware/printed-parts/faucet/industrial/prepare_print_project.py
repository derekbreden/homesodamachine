"""Prepare the Industrial faucet in the saved Sculpted PET-GF profile.

The project contains the Industrial base, relaxed cover and mounting plate,
plus the shared faucet tip. The TPU gasket is a separate print. Optional
slicing runs Bambu Studio locally and never connects to a printer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

TITLE = "Industrial faucet PET-GF"
PROJECT = HERE / "faucet-industrial-petgf.3mf"
PROFILE = FAUCET / "faucet-petgf.3mf"
GASKET = HERE / "industrial-above-counter-gasket.stl"
# Separate spaces for each part's brim and automatically generated supports.
PART_OFFSETS = ((-80.0, 0.0), (20.0, 47.0), (89.0, 110.0), (43.0, -52.0))
PROTECTED_SCULPTED = tuple(PROFILE.with_suffix(suffix) for suffix in (
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
    )
    missing = [relative(path) for _, path, _ in parts if not path.is_file()]
    if missing:
        raise FileNotFoundError("Generate the Industrial STLs before preparing the project: "
                                + ", ".join(missing))
    return parts


def write_readiness(project: Path, report: dict, reading: dict | None = None,
                    slice_directory: Path | None = None) -> dict:
    """Record what this offline preparation actually checked."""
    result = {
        "project_title": TITLE,
        "status": ("offline slice and support audit passed; not submitted"
                   if reading is not None else "project prepared; offline slice pending"),
        "project": relative(project),
        "project_sha256": report["project_sha256"],
        "settings_sha256": report["settings_sha256"],
        "print_report_sha256": writer.digest(project.with_suffix(".print.json").read_bytes()),
        "profile_source": report["profile_source"],
        "all_profile_members_preserved_byte_for_byte": True,
        "source_stls": {part["source"]: part["stl_sha256"] for part in report["parts"]},
        "mesh_and_placement": {
            "closed_oriented_single_body_meshes": True,
            "embedded_meshes_match_source_stls": True,
            "parts": len(report["parts"]),
            "plates": report["plate_count"],
            "minimum_required_model_bed_margin_mm": 15.0,
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


def refresh(settings_from: Path = PROFILE, output: Path = PROJECT) -> dict:
    settings_from, output = settings_from.resolve(), output.resolve()
    if output == settings_from or output in {path.resolve() for path in PROTECTED_SCULPTED}:
        raise ValueError("The Industrial output must not replace its settings source or the Sculpted project")
    if output.suffix.lower() != ".3mf":
        raise ValueError("The Industrial project needs a .3mf filename")
    before = protected_hashes()
    preserved = profile_members(settings_from)
    parts = industrial_parts()
    report = writer.refresh(settings_from, output, parts=parts,
                            offsets=PART_OFFSETS, title=TITLE)
    if report["plate_count"] != 1 or len(report["parts"]) != 4:
        raise ValueError("The Industrial project needs four parts on one plate")
    if profile_members(output) != preserved:
        raise ValueError("The complete PET-GF profile was not preserved")
    if protected_hashes() != before:
        raise ValueError("A Sculpted project artifact changed during Industrial preparation")
    for row in report["parts"]:
        if writer.digest((writer.ROOT / row["source"]).read_bytes()) != row["stl_sha256"]:
            raise ValueError(f"{row['name']} changed while preparing the project")
    report.update({
        "project_title": TITLE,
        "profile_source": relative(settings_from),
        "project_sha256": writer.digest(output.read_bytes()),
        "all_profile_members_preserved_byte_for_byte": True,
        "profile_member_sha256": {name: writer.digest(data) for name, data in preserved.items()},
        "sculpted_artifacts_unchanged": before,
        "shared_tip_source": relative(parts[1][1]),
        "gasket_included": False,
        "color_independent_geometry": True,
    })
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    write_readiness(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--settings-from", type=Path, default=PROFILE)
    parser.add_argument("--slice-output", type=Path,
                        help="Optional empty directory for an offline Bambu Studio slice; no printer connection.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    directory = args.slice_output.resolve() if args.slice_output else None
    if directory and directory.exists() and any(directory.iterdir()):
        parser.error("--slice-output must be empty so the audit cannot consume an earlier slice")
    project = args.project.resolve()
    report = refresh(args.settings_from, project)
    print(f"{project}: four parts on one plate; exact PET-GF settings {report['settings_sha256']}", flush=True)
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
