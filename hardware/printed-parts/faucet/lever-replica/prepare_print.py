"""Prepare one comparison lever from the shared PET-GF settings; offline only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import refresh_print_project as writer
from physical_acceptance import for_printed_model

SOURCE_PROFILE = HERE.parents[1] / "petgf.3mf"

# One comparison lever per machine. The filament colour is physical; the shared
# settings and the Z trim are what differ here.
VARIANTS = {
    "black-h2c": {"project": "lever-replica-petgf.3mf",
                  "archive": "lever-black-petgf-z018-h2c.gcode.3mf",
                  "z_trim": 0.18, "title": "Lever comparison black PET-GF H2C"},
    "white-mark2": {"project": "lever-replica-petgf-white.3mf",
                    "archive": "lever-white-petgf-z004-mark2.gcode.3mf",
                    "z_trim": 0.04, "title": "Lever comparison white PET-GF Mark2"},
}


def prepare(variant):
    spec = VARIANTS[variant]
    project = HERE / spec["project"]
    report = writer.refresh(
        SOURCE_PROFILE, project,
        parts=(("lever-replica", HERE / "lever-replica-side-down.stl", 0.0),),
        offsets=((0.0, 0.0),), title=spec["title"], z_trim=spec["z_trim"])
    report["status"] = "offline project preparation; submissions are recorded in print-jobs.json"
    report["physical_acceptance"] = for_printed_model(report["parts"][0]["stl_sha256"])
    report["pose"] = "local CAD +X side on bed; broad show face vertical"
    report["variant"] = variant
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return report, project, HERE / spec["archive"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice-output", type=Path)
    parser.add_argument("--variant", choices=sorted(VARIANTS), default="black-h2c")
    args = parser.parse_args()
    report, PROJECT, ARCHIVE = prepare(args.variant)
    print(PROJECT)
    if args.slice_output:
        directory = args.slice_output.resolve()
        if directory.exists() and any(directory.iterdir()):
            raise ValueError("Use an empty slice directory")
        directory.mkdir(parents=True, exist_ok=True)
        command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
                   "--arrange", "0", "--orient", "0", "--export-3mf", ARCHIVE.name,
                   "--outputdir", str(directory), str(PROJECT)]
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
        ARCHIVE.write_bytes((directory / ARCHIVE.name).read_bytes())
        readiness = {"status": "offline slice complete; physical observations are recorded separately",
                     "physical_acceptance": report["physical_acceptance"],
                     "project_sha256": report["project_sha256"], "printer_submission": False,
                     "support_summary": support["summary"],
                     "support_audit_sha256": writer.digest(support_path.read_bytes()),
                     "slice_result": result,
                     "archive": ARCHIVE.name,
                     "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                     "gcode": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in directory.glob("*.gcode")}}
        PROJECT.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
        print(json.dumps({"slice": str(directory), "plates": result.get("sliced_plates")}, indent=2))


if __name__ == "__main__":
    main()
