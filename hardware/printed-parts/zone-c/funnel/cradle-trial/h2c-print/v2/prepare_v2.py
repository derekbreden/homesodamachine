"""Prepare and review the frozen v2 trial pair with one part per ready printer."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile

from shapely.geometry import LineString
from shapely.ops import unary_union

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent
sys.path.insert(0, str(BASELINE))
from prepare import ROOT, TRIAL, sha, writer
from verify import audit, segments

FROZEN_STLS = {
    "test-receiver": "cd25b650c948d38fbe8880bfb51b223620adec2f44bfc56b13316797c308bd4e",
    "test-cradle": "a12fccaa8557b81198caacc6b7913a0361806beb46d79df29ea62f7aa0fc622f",
}

ALLOCATIONS = (("test-receiver", "Mark2", 0.04), ("test-cradle", "H2C", 0.18))


def review(job, key, record, prep):
    archive = ROOT / record["archive"]
    assert sha(archive) == record["archive_sha256"]
    assert sha(ROOT / record["project"]) == record["project_sha256"]
    with zipfile.ZipFile(archive) as native:
        assert native.testzip() is None
        gcode = native.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == native.read(
            "Metadata/plate_1.gcode.md5").decode().strip().lower()
        settings = json.loads(native.read(writer.SETTINGS_MEMBER))
        (HERE / f"{key}-preview.png").write_bytes(native.read("Metadata/plate_1.png"))
    assert hashlib.sha256(gcode).hexdigest() == record["gcode_sha256"]
    for setting, expected in {"filament_nozzle_map": ["0"], "filament_type": ["PET-CF"],
                              "filament_colour": ["#000000"], "layer_height": "0.24",
                              "initial_layer_print_height": "0.2", "enable_arc_fitting": "0",
                              "elefant_foot_compensation": "0", "brim_type": "no_brim",
                              "support_filament": "1", "support_interface_filament": "1"}.items():
        assert settings[setting] == expected, (setting, settings[setting])
    assert float(settings["nozzle_diameter"][0]) == 0.4
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, round(record["requested_z_trim_mm"] - 0.02, 2)], trims
    path = job / "ready/plate_1.gcode"
    path.write_bytes(gcode)
    roads = list(segments(path))
    assert {r["object"] for r in roads} == {1901}
    assert {r["tool"] for r in roads} == {0}
    support = [r for r in roads if r["feature"].startswith("Support")]
    model = [r for r in roads if not r["feature"].startswith("Support")]
    part, = prep["parts"]
    assert part["rotation_x_degrees"] == 0.0
    assert abs(part["plate_bounds_mm"][0][2]) < 1e-6
    layers = sorted({r["layer"] for r in model})
    assert layers[:2] == [0.2, 0.44]
    assert all(abs(b - a - 0.24) < 1e-6 for a, b in zip(layers, layers[1:-1]))
    first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                         for r in model if r["layer"] == 0.2])
    overlaps = []
    for r in model:
        if r["layer"] == 0.44:
            bead = LineString((r["a"], r["b"])).buffer(r["width"] / 2)
            overlaps.append((bead.intersection(first).area / bead.area, r["feature"]))
    assert min(n for n, _ in overlaps) > 0.5
    reading = audit(path, key, include_unlabelled_support=True)
    summary = reading["summary"]
    shift = [part["plate_translation_mm"][i] - part["source_center_mm"][i] for i in range(3)]
    if part["name"] == "test-receiver":
        assert not support and summary["support_bodies"] == 0
        contacts = "none"
    else:
        assert support
        assert summary["support_bodies"] == summary["bed_rooted_bodies"] == 2
        assert summary["interface_islands"] == 2 and summary["model_rooted_bodies"] == 0
        assert summary["bodies_without_interface_labels"] == 0
        reading["coordinate_frame"] = {"plate_to_printed_cradle_translation_mm": [-v for v in shift]}
        for row in reading["trees"] + reading["interfaces"]:
            row["bbox_printed_cradle_xy_mm"] = [round(v - shift[i % 2], 4)
                                                for i, v in enumerate(row["bbox_xy_mm"])]
        for interface in reading["interfaces"]:
            x0, y0, x1, y1 = interface["bbox_printed_cradle_xy_mm"]
            assert 15.0498 < min(abs(x0), abs(x1)) and max(abs(x0), abs(x1)) < 18.5
            assert -11.84 < y0 < y1 < 21.17
            assert (interface["first_z_mm"], interface["last_z_mm"]) == (32.84, 33.08)
        assert min(abs(p[0] - shift[0]) for r in support for p in (r["a"], r["b"])) > 15.0498
        hooks = [r for r in model if min(abs(p[0] - shift[0]) for p in (r["a"], r["b"])) > 15.15]
        assert min(r["layer"] for r in hooks) == 33.8
        contacts = "two_external_hook_undersides_only"
        record.update(hook_underside_geometry_z_mm=33.552898407,
                      support_interface_last_z_mm=33.08, first_hook_model_layer_z_mm=33.8,
                      nominal_first_hook_layer_bottom_z_mm=33.56, printed_support_gap_mm=0.48,
                      pocket_support_paths=0)
    record.update(status="reviewed_for_elbow_cradle_snap_trial", emitted_z_trim_commands_mm=trims,
                  parts=prep["parts"], model_layer_count=len(layers),
                  first_two_layer_heights_mm=layers[:2],
                  minimum_second_layer_bead_area_overlap_fraction=min(n for n, _ in overlaps),
                  minimum_second_layer_outer_wall_bead_area_overlap_fraction=
                      min(n for n, feature in overlaps if feature == "Outer wall"),
                  support_summary=summary, support_contacts=contacts,
                  physical_fit_and_retention_tested=False, production_print_pose_retained=True,
                  filament_mapping={"physical_material": "black PET-GF", "profile_label": "PET-CF",
                                    "external_spool": 254, "nozzle": "fixed left hardened 0.4 mm"})
    (HERE / f"{key}-support-audit.json").write_text(json.dumps(reading, indent=2) + "\n")
    (HERE / f"{key}-preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record[k] for k in ("printer", "part", "archive", "archive_sha256",
                     "gcode_sha256", "estimated_seconds", "emitted_z_trim_commands_mm", "support_summary")}, indent=2), flush=True)


def prepare_all(revision):
    baseline = json.loads((BASELINE / "preflight.json").read_text())
    profile = ROOT / baseline["project"]
    assert sha(profile) == baseline["project_sha256"]
    for name, expected in FROZEN_STLS.items():
        assert sha(TRIAL / f"{name}.stl") == expected, name
    sources = [TRIAL / "cradle_trial.py", TRIAL / "geometry-check.json",
               TRIAL.parent / "elbow_cradle.py", TRIAL.parent / "funnel.py",
               TRIAL.parent / "funnel_frame.py",
               ROOT / "hardware/printed-parts/cadlib/fits.py",
               ROOT / "hardware/reference/jg-pp0308e-elbow/elbow.py",
               ROOT / "hardware/reference/jg-pp0308e-elbow/scan-measurements.json"]
    source_snapshot = {str(path.relative_to(ROOT)): sha(path) for path in sources}
    for name, printer, trim in ALLOCATIONS:
        key = f"{name.removeprefix('test-')}-{printer.lower()}"
        stem = f"funnel-test-{key}-v{revision}"
        job = ROOT / ".cache/prints" / stem
        if job.exists():
            raise FileExistsError("Use a fresh revision; reviewed inputs are immutable.")
        job.mkdir(parents=True)
        project = job / f"{stem}-input.3mf"
        prep = writer.refresh(profile, project, parts=((name, TRIAL / f"{name}.stl", 0.0),),
                              offsets=((0.0, 0.0),), z_trim=trim,
                              title=f"Funnel {name}; {printer}")
        prep.update(printer=printer, requested_z_trim_mm=trim,
                    geometry_export_revision=None,
                    geometry_export_status="awaiting_source_commit_from_Funnel_2",
                    source_snapshot=source_snapshot,
                    preparation_script_sha256=sha(HERE / "prepare_v2.py"))
        (job / "preparation.json").write_text(json.dumps(prep, indent=2) + "\n")
        (HERE / f"{key}-preparation.json").write_bytes((job / "preparation.json").read_bytes())
        ready = job / "ready"
        ready.mkdir()
        command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
                   "--arrange", "0", "--orient", "0", "--outputdir", str(ready),
                   "--export-3mf", f"{stem}.gcode.3mf", str(project)]
        (job / "slice-command.json").write_text(json.dumps(command, indent=2) + "\n")
        with (ready / "slice.log").open("w") as log:
            subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = json.loads((ready / "result.json").read_text())
        assert result["return_code"] == 0
        plate, = result["sliced_plates"]
        assert len(plate["objects"]) == 1 and not plate["warning_message"], plate
        archive = ready / f"{stem}.gcode.3mf"
        with zipfile.ZipFile(archive) as native:
            gcode = native.read("Metadata/plate_1.gcode")
        record = {"revision": revision, "printer": printer, "part": name, "quantity": 1,
                  "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
                  "project": str(project.relative_to(ROOT)), "project_sha256": sha(project),
                  "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
                  "estimated_seconds": plate["total_predication"],
                  "source_stl_sha256": {name: FROZEN_STLS[name]}, "requested_z_trim_mm": trim,
                  "support_mode": "shared_automatic_tree", "submitted": False,
                  "geometry_export_revision": None,
                  "geometry_export_status": "awaiting_source_commit_from_Funnel_2",
                  "source_snapshot": source_snapshot,
                  "source_snapshot_matches_export_revision": False}
        review(job, key, record, prep)
    for name, expected in FROZEN_STLS.items():
        assert sha(TRIAL / f"{name}.stl") == expected, name
    for source, expected in source_snapshot.items():
        assert sha(ROOT / source) == expected, source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=int, required=True)
    prepare_all(parser.parse_args().revision)
