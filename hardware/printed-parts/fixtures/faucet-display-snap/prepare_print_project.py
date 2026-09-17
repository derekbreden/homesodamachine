"""Place the complete display fit trial in the production PET-GF profile.

The trial generator supplies each STL in its stated print pose. This wrapper
uses the production 3MF writer and support reader; it changes only the parts,
their plate positions, and the trial's project and plate names.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


HERE = Path(__file__).resolve().parent
FAUCET = HERE.parents[1] / "faucet"
sys.path.insert(0, str(FAUCET))
import refresh_print_project as writer

TITLE = "Faucet display fit trial"
PROJECT = HERE / "faucet-display-fit-trial.3mf"
PROFILE = FAUCET / "faucet-petgf.3mf"
PART_OFFSETS = ((-65.0, 0.0), (65.0, 0.0))


def trial_parts() -> tuple:
    report = json.loads((HERE / "trial-geometry.json").read_text())
    for relative_path, expected in report.get("sources", {}).items():
        if writer.digest((writer.ROOT / relative_path).read_bytes()) != expected:
            raise ValueError(f"{relative_path} changed after the trial geometry was exported")
    parts = report["parts"]
    if len(parts) != 2:
        raise ValueError("the complete display trial needs exactly one housing and one cover")
    result = []
    for part in parts:
        source = HERE / part["stl"]
        if writer.digest(source.read_bytes()) != part["sha256"]:
            raise ValueError(f"{source.name} differs from the geometry report")
        result.append((source.stem, source, 0.0))
    return tuple(result)


def profile_members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            name: archive.read(name)
            for name in archive.namelist()
            if name == writer.SETTINGS_MEMBER
            or name.startswith("Metadata/filament_settings_") and name.endswith(".config")
        }


def refresh(settings_from: Path = PROFILE, output: Path = PROJECT) -> dict:
    preserved = profile_members(settings_from)
    previous_parts, previous_offsets = writer.PARTS, writer.PART_OFFSETS
    try:
        writer.PARTS, writer.PART_OFFSETS = trial_parts(), PART_OFFSETS
        report = writer.refresh(settings_from, output)
    finally:
        writer.PARTS, writer.PART_OFFSETS = previous_parts, previous_offsets

    with zipfile.ZipFile(output) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(members["3D/3dmodel.model"])
    for entry in model.findall(writer.qn("metadata")):
        if entry.get("name") == "Title":
            entry.text = TITLE
    config = ET.fromstring(members["Metadata/model_settings.config"])
    plates = config.findall("plate")
    assert len(plates) == 1
    for entry in plates[0].findall("metadata"):
        if entry.get("key") == "plater_name":
            entry.set("value", TITLE)
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    writer.archive_write(output, members)
    assert len(report["parts"]) == 2
    assert len(plates[0].findall("model_instance")) == 2
    assert profile_members(output) == preserved
    report["project_title"] = TITLE
    report["geometry_report_sha256"] = writer.digest((HERE / "trial-geometry.json").read_bytes())
    report["profile_source"] = str(settings_from.resolve().relative_to(writer.ROOT))
    report["project_sha256"] = writer.digest(output.read_bytes())
    report["all_profile_members_preserved_byte_for_byte"] = True
    report["placement"] = {
        "left_to_right": [part["name"] for part in report["parts"]],
        "source_stls_already_in_print_pose": True,
    }
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--settings-from", type=Path, default=PROFILE)
    parser.add_argument("--slice-output", type=Path,
                        help="Optional local Bambu CLI slice directory; no printer connection.")
    parser.add_argument("--slicer", type=Path,
                        default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    project = args.project.resolve()
    report = refresh(args.settings_from.resolve(), project)
    print(f"{project}: complete housing and cover, one plate; exact production settings {report['settings_sha256']}", flush=True)
    if args.slice_output is None:
        return
    directory = args.slice_output.resolve()
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
    print(json.dumps(reading["fit"], indent=2), flush=True)


if __name__ == "__main__":
    main()
