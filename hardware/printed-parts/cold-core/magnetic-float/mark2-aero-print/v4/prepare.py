"""Add a bed priming strip to the frozen combined ASA Aero plate startup."""

import copy
import importlib.util
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "v3"
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
FLOAT = HERE.parent.parent
JOB = ROOT / ".cache/prints/magnetic-float-pair-mark2-aero-v5"
SETTING_MEMBER = "Metadata/project_settings.config"
GCODE_MEMBER = "Metadata/plate_1.gcode"
spec = importlib.util.spec_from_file_location("frozen_pair_archive", PRIOR / "prepare.py")
archive_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive_tools)
digest = archive_tools.digest


def priming_strip(settings, layout):
    width = float(settings["initial_layer_line_width"])
    height = float(settings["initial_layer_print_height"])
    flow = float(settings["filament_flow_ratio"][0])
    diameter = float(settings["filament_diameter"][0])
    assert (width, height, flow, diameter) == (0.48, 0.2, 0.52, 1.75)
    # Match the slicer's rounded rectangular bead section, including Aero flow.
    bead_area = height * (width - height) + math.pi * height**2 / 4
    feed_per_mm = bead_area * flow / (math.pi * diameter**2 / 4)
    xmin, xmax, ymin, pitch, rows = 230.0, 290.0, 15.0, 0.45, 12
    ymax = ymin + (rows - 1) * pitch
    bounds = [xmin - width / 2, ymin - width / 2,
              xmax + width / 2, ymax + width / 2]
    bed = [tuple(map(float, p.split("x"))) for p in settings["printable_area"]]
    assert bed == [(0, 0), (330, 0), (330, 320), (0, 320)]
    assert not settings["bed_exclude_area"]
    assert 0 < bounds[0] < bounds[2] < 330 and 0 < bounds[1] < bounds[3] < 320
    for obj in layout["bbox_objects"]:
        b = obj["bbox"]
        assert bounds[2] < b[0] or bounds[0] > b[2] or bounds[3] < b[1] or bounds[1] > b[3]
    x = xmin
    y = ymin
    length = 0.0
    lines = [";===== ASA Aero bed priming strip =====", "G90", "G21", "M83",
             "M109 S270", "G29.2 S1", "G1 Z1.2 F1200",
             f"G1 X{x:.3f} Y{y:.3f} F12000", "G1 Z0.2 F1200", "M204 S500"]
    for row in range(rows):
        if row:
            y = ymin + row * pitch
            lines.append(f"G1 X{x:.3f} Y{y:.3f} E{pitch * feed_per_mm:.6f} F1200")
            length += pitch
        x = xmax if row % 2 == 0 else xmin
        lines.append(f"G1 X{x:.3f} Y{y:.3f} E{(xmax-xmin) * feed_per_mm:.6f} F1200")
        length += xmax - xmin
    # Wipe along the last adhered row, lift, then retain the model's own
    # 1.5 mm retract/unretract pair. No extra retraction is introduced.
    assert x == xmin
    lines += [f"G1 X{xmin + 5:.3f} Y{y:.3f} F1200", "G1 Z1.2 F1200",
              "M204 S10000", ";===== ASA Aero bed priming strip end ====="]
    patch = "\n".join(lines) + "\n"
    assert not re.search(r"\bE-", patch)
    used_bounds = layout["bbox_all"]
    probe = [math.floor(min(bounds[0], used_bounds[0])),
             math.floor(min(bounds[1], used_bounds[1])),
             math.ceil(max(bounds[2], used_bounds[2])),
             math.ceil(max(bounds[3], used_bounds[3]))]
    return patch, {"centerline_bounds_xy_mm": [xmin, ymin, xmax, ymax],
                   "bead_bounds_xy_mm": bounds, "rows": rows,
                   "row_length_mm": xmax - xmin, "pitch_mm": pitch,
                   "layer_height_mm": height, "line_width_mm": width,
                   "speed_mm_s": 20, "flow_ratio": flow,
                   "filament_feed_mm": length * feed_per_mm,
                   "approximate_added_mass_g": length * bead_area * flow * 0.99 / 1000,
                   "extrusion_path_mm": length,
                   "nominal_extrusion_time_s": length / 20,
                   "wipe_mm": 5, "extra_retraction_mm": 0,
                   "adaptive_bed_leveling_bounds_xy_mm": probe,
                   "clear_of_parts_and_bed_exclusions": True}


def main():
    prior = json.loads((PRIOR / "pair-preflight.json").read_text())
    source = ROOT / prior["archive"]
    assert digest(source.read_bytes()) == prior["archive_sha256"]
    members = archive_tools.archive_members(source)
    old_gcode = members[GCODE_MEMBER]
    assert digest(old_gcode) == prior["gcode_sha256"]
    import hashlib
    assert hashlib.md5(old_gcode).hexdigest() == members[GCODE_MEMBER + ".md5"].decode().strip().lower()
    for part, expected in prior["source_stl_sha256"].items():
        assert digest((FLOAT / f"{part}.stl").read_bytes()) == expected
    for path, expected in prior["source_snapshot"].items():
        data = subprocess.run(["git", "show", f"{prior['source_commit']}:{path}"],
                              cwd=ROOT, capture_output=True, check=True).stdout
        assert digest(data) == expected, path
    settings = json.loads(members[SETTING_MEMBER])
    patch, patch_review = priming_strip(settings, json.loads(members["Metadata/plate_1.json"]))
    x0, y0, x1, y1 = patch_review["adaptive_bed_leveling_bounds_xy_mm"]
    probe_args = f"X{x0} Y{y0} I{x1-x0} J{y1-y0} R"
    old_args = "X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]} R"
    old_start = settings["machine_start_gcode"]
    assert old_start.count(old_args) == 3
    new_start = old_start.replace(old_args, probe_args) + "\n" + patch
    selected = copy.deepcopy(settings)
    selected["machine_start_gcode"] = new_start
    assert [k for k in selected if selected[k] != settings[k]] == ["machine_start_gcode"]

    text = old_gcode.decode()
    header = "; machine_start_gcode = " + json.dumps(old_start)[1:-1]
    assert text.count(header + "\n") == 1
    text = text.replace(header + "\n", "; machine_start_gcode = " + json.dumps(new_start)[1:-1] + "\n")
    old_prefix, old_parts = text.split("; MACHINE_START_GCODE_END\n")
    new_prefix, count = re.subn(r"(?m)^(\s*G29 A[12] O )X[-+.\d]+ Y[-+.\d]+ I[-+.\d]+ J[-+.\d]+ R$",
                              lambda m: m[1] + probe_args, old_prefix)
    assert count == 2
    gcode = (new_prefix + "\n" + patch + "; MACHINE_START_GCODE_END\n" + old_parts).encode()
    assert gcode.split(b"; MACHINE_START_GCODE_END\n")[1] == old_gcode.split(b"; MACHINE_START_GCODE_END\n")[1]
    assert [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)] == [0.0, 0.02]
    assert patch.count("M109 S270") == 1 and "G1 Z0.2 F1200" in patch
    assert not JOB.exists(), "Use a new immutable native revision directory."
    (JOB / "ready").mkdir(parents=True)
    revised = dict(members)
    revised[SETTING_MEMBER] = json.dumps(selected).encode()
    revised[GCODE_MEMBER] = gcode
    revised[GCODE_MEMBER + ".md5"] = hashlib.md5(gcode).hexdigest().encode()
    changed = [n for n in members if members[n] != revised[n]]
    assert sorted(changed) == sorted([SETTING_MEMBER, GCODE_MEMBER, GCODE_MEMBER + ".md5"])
    archive = JOB / "ready/magnetic-float-pair-mark2-aero-v5.gcode.3mf"
    archive_tools.write_archive(archive, revised)
    assert archive_tools.archive_members(archive) == revised
    original_input = ROOT / prior["project"]
    assert digest(original_input.read_bytes()) == prior["project_sha256"]
    input_members = archive_tools.archive_members(original_input)
    input_settings = json.loads(input_members[SETTING_MEMBER])
    assert input_settings["machine_start_gcode"] == old_start
    input_settings["machine_start_gcode"] = new_start
    input_members[SETTING_MEMBER] = json.dumps(input_settings).encode()
    project = JOB / "magnetic-float-pair-mark2-aero-v5-input.3mf"
    archive_tools.write_archive(project, input_members)
    (JOB / "ready/plate_1.gcode").write_bytes(gcode)
    (HERE / "pair-preview.png").write_bytes(revised["Metadata/plate_1.png"])

    result = copy.deepcopy(prior)
    for k in ("accepted_task_id", "non_trim_commands_identical", "non_trim_settings_identical", "gcode_changed_lines"):
        result.pop(k, None)
    result.update(physical_trial_revision=4, native_archive_revision=5,
                  prepared_utc=datetime.now(timezone.utc).isoformat(),
                  source_project=str(original_input.relative_to(ROOT)), source_project_sha256=digest(original_input.read_bytes()),
                  project=str(project.relative_to(ROOT)), project_sha256=digest(project.read_bytes()),
                  archive=str(archive.relative_to(ROOT)), archive_sha256=digest(archive.read_bytes()),
                  gcode_sha256=digest(gcode), submitted=False, preview_inspected=True,
                  preview_review="Part geometry and native previews are byte-identical; the startup strip is checked separately by its coordinates.",
                  parent_review={"preflight": str((PRIOR / "pair-preflight.json").relative_to(ROOT)),
                                 "archive_sha256": prior["archive_sha256"], "gcode_sha256": prior["gcode_sha256"]},
                  archive_changed_members=changed, part_program_byte_identical=True,
                  non_startup_settings_identical=True, priming_strip_review=patch_review,
                  native_slice_summary_scope="Inherited part estimate; excludes added startup strip time and additional adaptive bed leveling.",
                  preparation_dependency_sha256={str((PRIOR / "prepare.py").relative_to(ROOT)): digest((PRIOR / "prepare.py").read_bytes())})
    result["profile_changes"]["machine_start_gcode"]["selected_sha256"] = digest(new_start.encode())
    result["profile_changes"]["machine_start_gcode"]["change"] = "Add a single-layer corner priming strip after stock startup and include it in adaptive bed leveling; retain +0.04 mm user trim."
    (HERE / "pair-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("archive", "archive_sha256", "gcode_sha256", "priming_strip_review", "part_program_byte_identical")}), flush=True)


if __name__ == "__main__":
    main()
