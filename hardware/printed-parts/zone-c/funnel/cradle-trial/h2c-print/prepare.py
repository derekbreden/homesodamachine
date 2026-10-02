"""Prepare immutable native H2C slices of the receiver and elbow-cradle trial."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer

FROZEN_STLS = {
    "test-receiver": "fba0609890e494df9be162c66ba1df90cab2d613f1921ec92a1dad4b5b84973b",
    "test-cradle": "a138ed5c47fac79c396acbbc6ba11f3cbcda31f49a2cae6fa3939608156cd7e9",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(revision, hooks_only):
    stem = f"funnel-cradle-trial-h2c-v{revision}"
    job = ROOT / ".cache/prints" / stem
    if job.exists():
        raise FileExistsError("Use a fresh revision; reviewed inputs are immutable.")
    for name, expected in FROZEN_STLS.items():
        assert sha(TRIAL / f"{name}.stl") == expected, name
    sources = [TRIAL / "cradle_trial.py", TRIAL / "geometry-check.json",
               TRIAL.parent / "elbow_cradle.py", TRIAL.parent / "funnel.py",
               TRIAL.parent / "funnel_frame.py",
               ROOT / "hardware/printed-parts/cadlib/fits.py",
               ROOT / "hardware/reference/jg-pp0308e-elbow/elbow.py",
               ROOT / "hardware/reference/jg-pp0308e-elbow/scan-measurements.json"]
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    job.mkdir(parents=True)
    project = job / f"{stem}-input.3mf"
    profile = ROOT / "hardware/printed-parts/petgf.3mf"
    prep = writer.refresh(profile, project,
                          parts=tuple((name, TRIAL / f"{name}.stl", 0.0)
                                      for name in FROZEN_STLS),
                          offsets=((-45.0, 0.0), (45.0, 0.0)), z_trim=0.18,
                          title="Funnel receiver and elbow cradle; H2C")
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    overrides = {"initial_layer_print_height": "0.2", "layer_height": "0.24",
                 "elefant_foot_compensation": "0", "brim_type": "no_brim", "brim_width": "0",
                 "support_filament": "1", "support_interface_filament": "1",
                 "flush_into_support": "0"}
    prep["trial_settings_changes"] = {
        key: {"from": settings.get(key), "to": value}
        for key, value in overrides.items() if settings.get(key) != value}
    settings.update(overrides)
    assert settings["filament_nozzle_map"] == ["0"]
    assert settings["enable_arc_fitting"] == "0"
    assert settings["enable_support"] == "1" and settings["support_type"] == "tree(auto)"
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    hook_faces, blocked = [], {}
    for part in prep["parts"]:
        model = ET.fromstring(members[part["member"]])
        vertices = writer.np.array([[float(v.get(k)) for k in ("x", "y", "z")]
                                    for v in model.iter(writer.qn("vertex"))])
        vertices += part["source_center_mm"]
        count = 0
        for triangle in model.iter(writer.qn("triangle")):
            points = vertices[[int(triangle.get(k)) for k in ("v1", "v2", "v3")]]
            normal = writer.np.cross(points[1] - points[0], points[2] - points[0])
            horizontal_down = normal[2] < 0 and writer.np.linalg.norm(normal[:2]) < 1e-6
            hook = (part["name"] == "test-cradle" and horizontal_down
                    and abs(points[:, 2].mean() - 33.5529) < 1e-4)
            if hook:
                hook_faces.append({"source_bounds_mm": [points.min(axis=0).tolist(),
                                                         points.max(axis=0).tolist()]})
            elif hooks_only:
                triangle.set("paint_supports", "8")
                count += 1
        if hooks_only:
            members[part["member"]] = writer.xml(model)
            blocked[part["name"]] = count
    assert len(hook_faces) == 4, hook_faces
    writer.archive_write(project, members)
    prep.update(project_sha256=sha(project), requested_z_trim_mm=0.18,
                source_hashes=source_hashes, source_stl_sha256=FROZEN_STLS,
                support_mode="hook_undersides_only" if hooks_only else "shared_automatic_tree",
                blocked_source_facets=blocked, hook_underside_facets=hook_faces,
                preparation_script_sha256=sha(Path(__file__)),
                source_commit_at_preparation=subprocess.run(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                    text=True, check=True).stdout.strip())
    (job / "preparation.json").write_text(json.dumps(prep, indent=2) + "\n")
    ready = job / "ready"
    ready.mkdir()
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
               "--arrange", "0", "--orient", "0", "--outputdir", str(ready),
               "--export-3mf", f"{stem}.gcode.3mf", str(project)]
    (job / "slice-command.json").write_text(json.dumps(command, indent=2) + "\n")
    with (ready / "slice.log").open("w") as log:
        subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
    archive = ready / f"{stem}.gcode.3mf"
    with zipfile.ZipFile(archive) as native:
        assert native.testzip() is None
        gcode = native.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == native.read(
            "Metadata/plate_1.gcode.md5").decode().strip().lower()
        (HERE / f"preview-v{revision}.png").write_bytes(native.read("Metadata/plate_1.png"))
    (ready / "plate_1.gcode").write_bytes(gcode)
    result = json.loads((ready / "result.json").read_text())
    assert result["return_code"] == 0, result
    plate, = result["sliced_plates"]
    assert len(plate["objects"]) == 2 and not plate["warning_message"], plate
    for name, expected in FROZEN_STLS.items():
        assert sha(TRIAL / f"{name}.stl") == expected, name
    record = {"revision": revision, "status": "native_slice_awaiting_toolpath_review",
              "printer": "H2C", "quantity": {"receiver": 1, "cradle": 1},
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
              "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
              "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
              "estimated_seconds": plate["total_predication"],
              "source_stl_sha256": FROZEN_STLS, "requested_z_trim_mm": 0.18,
              "support_mode": prep["support_mode"], "submitted": False}
    (job / "native-slice.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=int, required=True)
    parser.add_argument("--hooks-only", action="store_true")
    args = parser.parse_args()
    prepare(args.revision, args.hooks_only)
