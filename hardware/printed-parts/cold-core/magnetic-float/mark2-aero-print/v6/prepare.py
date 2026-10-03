"""Export the frozen combined Aero plate for glued Engineering plate."""

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "v5"
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
FLOAT = HERE.parent.parent
JOB = ROOT / ".cache/prints/magnetic-float-pair-mark2-aero-v6"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
SETTINGS = "Metadata/project_settings.config"
GCODE = "Metadata/plate_1.gcode"
HELPER = HERE.parent / "v3/prepare.py"
spec = importlib.util.spec_from_file_location("float_archive_tools", HELPER)
archive_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive_tools)
digest = archive_tools.digest


def commands(program):
    return [line.strip() for line in program.splitlines()
            if line.strip() and not line.lstrip().startswith((b";", b"M73 "))]


def main():
    prior = json.loads((PRIOR / "pair-preflight.json").read_text())
    original_archive = ROOT / prior["archive"]
    original_project = ROOT / prior["project"]
    assert digest(original_archive.read_bytes()) == prior["archive_sha256"]
    assert digest(original_project.read_bytes()) == prior["project_sha256"]
    old = archive_tools.archive_members(original_archive)
    original = archive_tools.archive_members(original_project)
    for part, want in prior["source_stl_sha256"].items():
        assert digest((FLOAT / f"{part}.stl").read_bytes()) == want
    for path, want in prior["source_snapshot"].items():
        saved = subprocess.check_output(["git", "show", prior["source_commit"] + ":" + path], cwd=ROOT)
        assert digest(saved) == want, path

    source_settings = json.loads(original[SETTINGS])
    selected = copy.deepcopy(source_settings)
    assert selected["curr_bed_type"] == "Textured PEI Plate"
    assert selected["eng_plate_temp"] == selected["eng_plate_temp_initial_layer"] == ["90"]
    selected["curr_bed_type"] = "Engineering Plate"
    assert [k for k in selected if selected[k] != source_settings[k]] == ["curr_bed_type"]
    revised = dict(original)
    revised[SETTINGS] = json.dumps(selected).encode()
    metadata = revised["Metadata/model_settings.config"]
    assert metadata.count(b'key="bed_type" value="Textured PEI Plate"') == 1
    revised["Metadata/model_settings.config"] = metadata.replace(
        b'key="bed_type" value="Textured PEI Plate"',
        b'key="bed_type" value="Engineering Plate"')
    assert all(revised[n] == original[n] for n in original
               if n not in (SETTINGS, "Metadata/model_settings.config"))

    project = JOB / "magnetic-float-pair-mark2-aero-v6-input.3mf"
    native_dir = JOB / "native"
    native = native_dir / "magnetic-float-pair-mark2-aero-v6.gcode.3mf"
    if not native.exists():
        assert not JOB.exists(), "An incomplete export requires inspection before reusing its directory."
        native_dir.mkdir(parents=True)
        archive_tools.write_archive(project, revised)
        with (JOB / "slice.log").open("w") as log:
            subprocess.run([str(STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
                            "--export-3mf", native.name, "--outputdir", str(native_dir), str(project)],
                           cwd=native_dir, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert archive_tools.archive_members(project) == revised
    output = archive_tools.archive_members(native)
    gcode = output[GCODE]
    assert hashlib.md5(gcode).hexdigest() == output[GCODE + ".md5"].decode().strip().lower()
    settings = json.loads(output[SETTINGS])
    old_settings = json.loads(old[SETTINGS])
    changed_settings = [k for k in settings if settings[k] != old_settings.get(k)]
    assert changed_settings == ["curr_bed_type"], changed_settings
    assert settings["curr_bed_type"] == "Engineering Plate"
    assert settings["filament_nozzle_map"] == ["1"]
    assert settings["filament_type"] == ["ASA-AERO"]
    assert settings["filament_flow_ratio"] == ["0.52"]
    assert settings["nozzle_temperature"] == ["270"]
    assert settings["chamber_temperatures"] == ["60"]
    assert b'key="bed_type" value="Engineering Plate"' in output["Metadata/model_settings.config"]
    layout = json.loads(output["Metadata/plate_1.json"])
    prior_layout = json.loads(old["Metadata/plate_1.json"])
    assert layout["bed_type"] == "eng_plate", layout["bed_type"]
    assert layout["bbox_all"] == prior_layout["bbox_all"]
    assert layout["bbox_objects"] == prior_layout["bbox_objects"]
    for name in old:
        if name.startswith("3D/"):
            assert output[name] == old[name], name

    old_start, old_parts = old[GCODE].split(b"; MACHINE_START_GCODE_END\n")
    new_start, new_parts = gcode.split(b"; MACHINE_START_GCODE_END\n")
    assert commands(new_parts) == commands(old_parts), "A part printing command changed."
    old_commands, new_commands = commands(old_start), commands(new_start)
    assert len(old_commands) == len(new_commands)
    changes = [(a.decode(), b.decode()) for a, b in zip(old_commands, new_commands) if a != b]
    assert changes == [("M972 S26 P0 C0", "M972 S36 P0 C0 X1"),
                       ("G29.1 Z0.02", "G29.1 Z0.04")], changes
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, 0.04]
    strip_begin = b";===== ASA Aero bed priming strip ====="
    strip_end = b";===== ASA Aero bed priming strip end ====="
    assert new_start.split(strip_begin)[1].split(strip_end)[0] == old_start.split(strip_begin)[1].split(strip_end)[0]
    assert b"X110 Y14 I181 J146 R" in new_start

    # The frozen mesh and every emitted part printing command are identical.
    # Retain their coordinate, overlap and mass review without importing CAD.
    paths = copy.deepcopy(prior["per_part_native_path_review"])
    summary = json.loads((native_dir / "result.json").read_text())["sliced_plates"][0]
    assert not summary["warning_message"] and len(summary["objects"]) == 2
    assert sorted(o["bbox"]["height"] for o in summary["objects"]) == [10.0, 44.0]

    ready = JOB / "ready"
    ready.mkdir(exist_ok=True)
    archive = ready / native.name
    if archive.exists():
        assert archive.read_bytes() == native.read_bytes()
    else:
        shutil.copyfile(native, archive)
    archive.chmod(0o444)
    (ready / "plate_1.gcode").write_bytes(gcode)
    (HERE / "pair-preview.png").write_bytes(output["Metadata/plate_1.png"])
    record = copy.deepcopy(prior)
    for key in ("accepted_task_id", "submitted_utc", "retry_of", "archive_reused_without_changes"):
        record.pop(key, None)
    record.update(physical_trial_revision=6, native_archive_revision=6,
                  prepared_utc=datetime.now(timezone.utc).isoformat(),
                  source_project=str(original_project.relative_to(ROOT)),
                  source_project_sha256=digest(original_project.read_bytes()),
                  project=str(project.relative_to(ROOT)), project_sha256=digest(project.read_bytes()),
                  archive=str(archive.relative_to(ROOT)), archive_sha256=digest(archive.read_bytes()),
                  gcode_sha256=digest(gcode), emitted_z_trim_commands_mm=trims,
                  bed="Engineering Plate", adhesive_application_reported=True,
                  per_part_native_path_review=paths, submitted=False, preview_inspected=False,
                  geometry_and_orientation_identical=True,
                  native_geometry_and_preview_identical=all(output[n] == old[n] for n in old
                                                           if n.startswith("3D/") or n.endswith(".png")),
                  part_program_byte_identical=new_parts == old_parts,
                  part_printing_commands_identical=True, priming_strip_byte_identical=True,
                  startup_command_changes=changes, changed_native_settings=changed_settings,
                  non_startup_settings_identical=False, non_plate_settings_identical=True,
                  per_part_review_basis="Frozen mesh and all part printing commands are identical; only M73 progress estimates differ.",
                  archive_changed_members=[n for n in old if output[n] != old[n]],
                  parent_review={"preflight": str((PRIOR / "pair-preflight.json").relative_to(ROOT)),
                                 "archive_sha256": prior["archive_sha256"], "gcode_sha256": prior["gcode_sha256"]},
                  native_export_result=summary,
                  native_slice_summary={"estimated_time_s": summary["total_predication"],
                                        "filament_mass_g": summary["filaments"][0]["total_used_g"],
                                        "object_count": len(summary["objects"]), "warnings": []},
                  native_slice_summary_scope="Native v6 estimate includes the priming strip; actual heating, calibration and bed probing times vary.",
                  preparation_dependency_sha256={str(HELPER.relative_to(ROOT)): digest(HELPER.read_bytes())})
    record["profile_changes"]["curr_bed_type"] = {"source": "Textured PEI Plate", "selected": "Engineering Plate"}
    record["profile_changes"]["machine_start_gcode"]["change"] = "Retain the corner priming strip and +0.04 mm user trim; native export compiles the Engineering plate branch."
    record["selected_recipe"].update(eng_plate_temp=["90"], eng_plate_temp_initial_layer=["90"])
    (HERE / "pair-preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record[k] for k in ("archive", "archive_sha256", "gcode_sha256", "bed",
                                           "emitted_z_trim_commands_mm", "part_printing_commands_identical",
                                           "priming_strip_byte_identical", "startup_command_changes")}), flush=True)


if __name__ == "__main__":
    main()
