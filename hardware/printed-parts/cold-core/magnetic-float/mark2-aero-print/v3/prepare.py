"""Make a +0.04 mm trim revision of the reviewed combined native plate."""

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "v2"
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
FLOAT = HERE.parent.parent
JOB = ROOT / ".cache/prints/magnetic-float-pair-mark2-aero-v4"
SETTING_MEMBER = "Metadata/project_settings.config"
GCODE_MEMBER = "Metadata/plate_1.gcode"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive_members(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n: z.read(n) for n in z.namelist()}


def write_archive(path, members):
    with zipfile.ZipFile(path, "x", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)


def main():
    prior = json.loads((PRIOR / "pair-preflight.json").read_text())
    prior_archive = ROOT / prior["archive"]
    assert digest(prior_archive.read_bytes()) == prior["archive_sha256"]
    members = archive_members(prior_archive)
    old_gcode = members[GCODE_MEMBER]
    assert digest(old_gcode) == prior["gcode_sha256"]
    assert hashlib.md5(old_gcode).hexdigest() == members[GCODE_MEMBER + ".md5"].decode().strip().lower()
    for part, expected in prior["source_stl_sha256"].items():
        assert digest((FLOAT / f"{part}.stl").read_bytes()) == expected
    for path, expected in prior["source_snapshot"].items():
        saved = subprocess.run(["git", "show", f"{prior['source_commit']}:{path}"],
                               cwd=ROOT, capture_output=True, check=True).stdout
        assert digest(saved) == expected, path

    helper = ROOT / "tools/funnel-mold-print/profiles.py"
    spec = importlib.util.spec_from_file_location("float_trim_profile", helper)
    profiles = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profiles)
    with zipfile.ZipFile(ROOT / ".cache/magnetic-float-print/aero-input.3mf") as z:
        stock = json.loads(z.read(SETTING_MEMBER))["machine_start_gcode"]
    old_start = profiles.trimmed_start_gcode(stock, 0.0)
    new_start = profiles.trimmed_start_gcode(stock, 0.04)
    settings = json.loads(members[SETTING_MEMBER])
    assert settings["machine_start_gcode"] == old_start
    selected = copy.deepcopy(settings)
    selected["machine_start_gcode"] = new_start
    assert [k for k in selected if selected[k] != settings[k]] == ["machine_start_gcode"]

    lines = old_gcode.decode().splitlines(keepends=True)
    changed_lines = []
    for i, line in enumerate(lines):
        if line.startswith("; machine_start_gcode = "):
            assert "user-calibrated +0.00" in line
            lines[i] = line.replace("user-calibrated +0.00", "user-calibrated +0.04").replace("Z{0.00", "Z{0.04")
        elif line.strip() == ";===== plate compensation plus user-calibrated +0.00 mm Z trim =====":
            lines[i] = line.replace("+0.00", "+0.04")
        elif re.match(r"^\s*G29\.1 Z-0\.02\s*$", line):
            lines[i] = line.replace("Z-0.02", "Z0.02")
        if lines[i] != line:
            changed_lines.append({"line": i + 1, "kind": "configuration comment" if line.startswith("; machine_start_gcode") else "trim comment" if line.lstrip().startswith(";") else "Z trim command"})
    assert len(changed_lines) == 3
    gcode = "".join(lines).encode()
    old_commands = [line for line in old_gcode.splitlines() if line.strip() and not line.lstrip().startswith(b";")]
    new_commands = [line for line in gcode.splitlines() if line.strip() and not line.lstrip().startswith(b";")]
    assert len(old_commands) == len(new_commands)
    differences = [(a.strip(), b.strip()) for a, b in zip(old_commands, new_commands) if a != b]
    assert differences == [(b"G29.1 Z-0.02", b"G29.1 Z0.02")]
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, 0.02]

    assert not JOB.exists(), "Use a new immutable archive revision."
    (JOB / "ready").mkdir(parents=True)
    revised = dict(members)
    revised[SETTING_MEMBER] = json.dumps(selected).encode()
    revised[GCODE_MEMBER] = gcode
    revised[GCODE_MEMBER + ".md5"] = hashlib.md5(gcode).hexdigest().encode()
    changed_members = [n for n in members if members[n] != revised[n]]
    assert sorted(changed_members) == sorted([SETTING_MEMBER, GCODE_MEMBER, GCODE_MEMBER + ".md5"])
    archive = JOB / "ready/magnetic-float-pair-mark2-aero-v4.gcode.3mf"
    write_archive(archive, revised)
    assert archive_members(archive) == revised

    prior_input = ROOT / prior["project"]
    assert digest(prior_input.read_bytes()) == prior["project_sha256"]
    input_members = archive_members(prior_input)
    input_settings = json.loads(input_members[SETTING_MEMBER])
    assert input_settings["machine_start_gcode"] == old_start
    input_settings["machine_start_gcode"] = new_start
    input_members[SETTING_MEMBER] = json.dumps(input_settings).encode()
    project = JOB / "magnetic-float-pair-mark2-aero-v4-input.3mf"
    write_archive(project, input_members)
    (JOB / "ready/plate_1.gcode").write_bytes(gcode)
    (HERE / "pair-preview.png").write_bytes(revised["Metadata/plate_1.png"])

    result = copy.deepcopy(prior)
    result.pop("accepted_task_id", None)
    result.update(physical_trial_revision=3, native_archive_revision=4,
                  prepared_utc=datetime.now(timezone.utc).isoformat(),
                  source_project=str(prior_input.relative_to(ROOT)), source_project_sha256=digest(prior_input.read_bytes()),
                  project=str(project.relative_to(ROOT)), project_sha256=digest(project.read_bytes()),
                  archive=str(archive.relative_to(ROOT)), archive_sha256=digest(archive.read_bytes()),
                  gcode_sha256=digest(gcode), requested_z_trim_mm=0.04, emitted_z_trim_commands_mm=trims,
                  submitted=False, preview_inspected=False, physical_fit_verified=False,
                  parent_review={"preflight": str((PRIOR / "pair-preflight.json").relative_to(ROOT)),
                                 "archive_sha256": prior["archive_sha256"], "gcode_sha256": prior["gcode_sha256"]},
                  archive_changed_members=changed_members, gcode_changed_lines=changed_lines,
                  non_trim_commands_identical=True, native_geometry_and_preview_identical=True,
                  non_trim_settings_identical=True,
                  preparation_dependency_sha256={str(helper.relative_to(ROOT)): digest(helper.read_bytes())})
    result["profile_changes"]["machine_start_gcode"]["selected_sha256"] = digest(new_start.encode())
    result["profile_changes"]["machine_start_gcode"]["change"] = "Requested +0.04 mm user trim with stock Textured PEI correction."
    (HERE / "pair-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("archive", "archive_sha256", "gcode_sha256", "requested_z_trim_mm", "emitted_z_trim_commands_mm", "non_trim_commands_identical", "native_slice_summary")}), flush=True)


if __name__ == "__main__":
    main()
