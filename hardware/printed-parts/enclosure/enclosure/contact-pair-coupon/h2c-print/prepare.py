"""Prepare a native H2C slice of the two production-derived contact coupons."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
COUPON = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_geometry_sources(geometry):
    """Bind frozen meshes to production inputs and the versioned export generator."""
    review = {}
    generator = COUPON / "contact_pair_coupon.py"
    for path, expected in geometry["source_sha256"].items():
        source = ROOT / path
        if sha(source) == expected:
            continue
        if source != generator:
            raise ValueError(f"Geometry source changed: {path}")
        # The peer's README-only amendments preserve the frozen meshes. Check the
        # versioned generator and every geometry-producing function before using them.
        revision = "9d3b242f9"
        prior = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=ROOT,
                               capture_output=True, check=True).stdout
        assert hashlib.sha256(prior).hexdigest() == expected
        old, new = ast.parse(prior), ast.parse(source.read_bytes())
        functions = lambda tree: {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        before, after = functions(old), functions(new)
        for name in before.keys() - {"main"}:
            assert ast.dump(before[name]) == ast.dump(after[name]), name
        stop = next(i for i, n in enumerate(before["main"].body)
                    if "geometry-check.json" in ast.dump(n))
        assert [ast.dump(n) for n in before["main"].body[:stop + 1]] == [
            ast.dump(n) for n in after["main"].body[:stop + 1]]
        for node in old.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign)):
                assert ast.dump(node) in {ast.dump(n) for n in new.body}
        review = {"export_generator_revision": revision,
                  "export_source_sha256": expected, "current_source_sha256": sha(source),
                  "geometry_functions_and_export_unchanged": True}
    return review


def prepare(revision, unsupported):
    stem = f"contact-pair-coupons-h2c-v{revision}"
    job = ROOT / ".cache/prints" / stem
    if job.exists():
        raise FileExistsError("Use a new revision; reviewed slices are immutable.")
    geometry = json.loads((COUPON / "geometry-check.json").read_text())
    source_review = validate_geometry_sources(geometry)
    names = ("contact-pair-male-coupon", "contact-pair-female-coupon")
    for name, key in zip(names, ("male", "female")):
        assert sha(COUPON / f"{name}.stl") == geometry["coupons"][key]["outputs"][f"{name}.stl"]
    job.mkdir(parents=True)
    project = job / f"{stem}-input.3mf"
    profile = ROOT / "hardware/printed-parts/petgf.3mf"
    report = writer.refresh(
        profile, project,
        parts=tuple((name, COUPON / f"{name}.stl", 0.0) for name in names),
        offsets=((-30.0, 0.0), (30.0, 0.0)), z_trim=0.18,
        title="Pump cartridge contact seats; production orientation; H2C")
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    changes = {
        "initial_layer_print_height": "0.2", "layer_height": "0.24",
        "elefant_foot_compensation": "0", "brim_type": "no_brim", "brim_width": "0",
        "support_filament": "1", "support_interface_filament": "1", "flush_into_support": "0"
    }
    report["coupon_settings_changes"] = {
        key: {"from": settings.get(key), "to": value}
        for key, value in changes.items() if settings.get(key) != value}
    settings.update(changes)
    assert settings["filament_nozzle_map"] == ["0"]
    assert settings["enable_arc_fitting"] == "0"
    assert settings["enable_support"] == "1"
    assert settings["support_type"] == "tree(auto)"
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    painted = {}
    if unsupported:
        # This coupon trial tests unsupported seats and wire passages. The automatic
        # comparison records every support body before coupon-only blockers are applied.
        # Geometry and the shared production support recipe remain byte-identical.
        for part in report["parts"]:
            model = ET.fromstring(members[part["member"]])
            triangles = list(model.iter(writer.qn("triangle")))
            for triangle in triangles:
                triangle.set("paint_supports", "8")
            painted[part["name"]] = len(triangles)
            members[part["member"]] = writer.xml(model)
    writer.archive_write(project, members)
    report.update(
        project_sha256=sha(project), requested_z_trim_mm=0.18,
        support_mode="coupon_only_support_blockers" if unsupported else "shared_automatic_tree",
        blocked_source_facets=painted,
        geometry_record_sha256=sha(COUPON / "geometry-check.json"),
        geometry_sources=geometry["source_sha256"],
        export_generator_review=source_review,
        preparation_script_sha256=sha(Path(__file__)),
        source_profile=str(profile.relative_to(ROOT)), source_profile_sha256=sha(profile))
    (job / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
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
    record = {
        "revision": revision, "status": "native_slice_awaiting_toolpath_review",
        "printer": "H2C", "quantity": {"male": 1, "female": 1},
        "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
        "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
        "estimated_seconds": plate["total_predication"],
        "source_stl_sha256": {name: sha(COUPON / f"{name}.stl") for name in names},
        "requested_z_trim_mm": 0.18, "submitted": False,
    }
    (job / "native-slice.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, type=int)
    parser.add_argument("--unsupported", action="store_true",
                        help="Apply coupon-only blockers for the unsupported seat/lead trial")
    args = parser.parse_args()
    prepare(args.revision, args.unsupported)
