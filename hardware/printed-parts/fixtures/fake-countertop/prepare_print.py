"""Prepare the fake countertop from the shared PET-GF settings; offline only.

One project per machine: the shared settings and the Z trim are what differ. Without
`--slice-output` this writes the project and its print report; with it, Bambu Studio slices
the project into that empty directory and the submittable archive lands beside the project.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "faucet"))
import refresh_print_project as writer  # noqa: E402

SOURCE_PROFILE = HERE.parents[1] / "petgf.3mf"
STL = HERE / "fake-countertop.stl"

VARIANTS = {
    "black-h2c": {"project": "fake-countertop-petgf.3mf",
                  "archive": "fake-countertop-petgf-z018-h2c.gcode.3mf",
                  "z_trim": 0.18, "title": "Fake countertop black PET-GF H2C"},
    "black-mark2": {"project": "fake-countertop-petgf-mark2.3mf",
                    "archive": "fake-countertop-petgf-z004-mark2.gcode.3mf",
                    "z_trim": 0.04, "title": "Fake countertop black PET-GF Mark2"},
}

BAMBU_STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
# The slab is the left nozzle's reach less this border, both sides (`fake_countertop.PLATE_BORDER`).
PLATE_BORDER = 5.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(variant):
    spec = VARIANTS[variant]
    project = HERE / spec["project"]
    report = writer.refresh(
        SOURCE_PROFILE, project,
        parts=(("fake-countertop", STL, 0.0),),
        offsets=((0.0, 0.0),), title=spec["title"], z_trim=spec["z_trim"],
        plate_border=PLATE_BORDER)
    report["status"] = "offline project preparation; a submission is recorded in print-jobs.json"
    report["pose"] = "show face on the bed, legs up; no support"
    report["variant"] = variant
    project.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return report, project, HERE / spec["archive"], spec


def slice_project(project, archive, spec, directory):
    directory = directory.resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Use an empty slice directory")
    directory.mkdir(parents=True, exist_ok=True)
    command = [BAMBU_STUDIO, "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", archive.name, "--outputdir", str(directory), str(project)]
    with (directory / "bambu-cli.log").open("w") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeError(f"Offline slice failed; {directory / 'bambu-cli.log'}")
    result = json.loads((directory / "result.json").read_text())
    if result.get("return_code") != 0:
        raise RuntimeError(result.get("error_string"))
    with zipfile.ZipFile(directory / archive.name) as z:
        assert z.testzip() is None
        gcode = z.read("Metadata/plate_1.gcode")
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0, round(spec["z_trim"] - 0.02, 2)]:
        raise ValueError(f"plate trim commands {trims} are not the requested +{spec['z_trim']:.2f}")
    features = sorted(set(re.findall(rb"^; FEATURE: (.+)$", gcode, re.M)))
    if any(b"Support" in f for f in features):
        raise ValueError(f"the slice carries support: {features}")
    archive.write_bytes((directory / archive.name).read_bytes())
    plate, = result["sliced_plates"]
    return {
        "status": "offline slice complete; a submission is recorded in print-jobs.json",
        "printer_submission": False,
        "slice_result": result,
        "features": [f.decode() for f in features],
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": sum(row["total_used_g"] for row in plate["filaments"]),
        "plate_trim_commands_mm": trims,
        "archive": archive.name,
        "archive_sha256": sha(archive),
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice-output", type=Path)
    parser.add_argument("--variant", choices=sorted(VARIANTS), default="black-h2c")
    args = parser.parse_args()
    report, project, archive, spec = prepare(args.variant)
    print(project)
    if args.slice_output:
        readiness = slice_project(project, archive, spec, args.slice_output)
        readiness["project_sha256"] = report["project_sha256"]
        readiness["source_stl_sha256"] = sha(STL)
        readiness["source_profile_sha256"] = sha(SOURCE_PROFILE)
        project.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
        print(json.dumps({k: readiness[k] for k in ("archive", "layers", "estimated_seconds",
                                                     "estimated_filament_g", "features",
                                                     "plate_trim_commands_mm")}, indent=2))


if __name__ == "__main__":
    main()
