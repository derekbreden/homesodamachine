"""Prepare one white PET-GF comparison lever; optional offline slicing only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import refresh_print_project as writer

SOURCE_PROFILE = HERE.parent / "faucet-petgf.3mf"
PROJECT = HERE / "lever-replica-white-petgf.3mf"
OVERRIDES = {
    "layer_height": "0.16",
    "wall_loops": "4",
    "sparse_infill_density": "100%",
    "sparse_infill_pattern": "zig-zag",
    "print_settings_id": "0.16mm PET-GF comparison lever, four walls, solid",
    "filament_colour": ["#FFFFFF"],
    "enable_prime_tower": "0",
    "brim_type": "outer_only",
    "brim_width": "5",
}


def prepare():
    with zipfile.ZipFile(SOURCE_PROFILE) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {key: {"from": settings.get(key), "to": value} for key, value in OVERRIDES.items()}
    settings.update(OVERRIDES)
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + "\n").encode()
    with tempfile.TemporaryDirectory(prefix="lever-print-") as directory:
        profile = Path(directory) / "comparison-profile.3mf"
        writer.archive_write(profile, members)
        report = writer.refresh(profile, PROJECT,
                                parts=(("lever-replica", HERE / "lever-replica-side-down.stl", 0.0),),
                                offsets=((0.0, 0.0),), title="White PET-GF comparison lever")
    report["settings_source"] = str(SOURCE_PROFILE.relative_to(writer.ROOT))
    report["settings_source_sha256"] = writer.digest(SOURCE_PROFILE.read_bytes())
    report["settings_changes"] = changes
    report["settings_preserved_byte_for_byte"] = False
    report["status"] = "prepared comparison prototype; no printer submission"
    report["fit_and_strength_validated"] = False
    report["pose"] = "local CAD +X side on bed; broad show face vertical"
    PROJECT.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice-output", type=Path)
    args = parser.parse_args()
    report = prepare()
    print(PROJECT)
    if args.slice_output:
        directory = args.slice_output.resolve()
        if directory.exists() and any(directory.iterdir()):
            raise ValueError("Use an empty slice directory")
        directory.mkdir(parents=True, exist_ok=True)
        command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
                   "--arrange", "0", "--orient", "0", "--outputdir", str(directory), str(PROJECT)]
        with (directory / "bambu-cli.log").open("w") as log:
            completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        if completed.returncode:
            raise RuntimeError(f"Offline slice failed; {directory / 'bambu-cli.log'}")
        result = json.loads((directory / "result.json").read_text())
        if result.get("return_code") != 0:
            raise RuntimeError(result.get("error_string"))
        sys.path.insert(0, str(writer.ROOT / "hardware/scripts"))
        from enclosure_support_audit import audit
        support = audit(directory / "plate_1.gcode", "lever-replica",
                        HERE / "lever-replica-side-down.stl", PROJECT, PROJECT,
                        include_unlabelled_support=True)
        support["source_frame_note"] = "CAD coordinates in this audit are the side-down STL print frame."
        support_path = PROJECT.with_suffix(".support-audit.json")
        support_path.write_text(json.dumps(support, indent=2) + "\n")
        readiness = {"status": "offline slice complete; physical fit, strength and support removal unvalidated",
                     "project_sha256": report["project_sha256"], "printer_submission": False,
                     "support_summary": support["summary"],
                     "support_audit_sha256": writer.digest(support_path.read_bytes()),
                     "slice_result": result,
                     "gcode": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in directory.glob("*.gcode")}}
        PROJECT.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
        print(json.dumps({"slice": str(directory), "plates": result.get("sliced_plates")}, indent=2))


if __name__ == "__main__":
    main()
