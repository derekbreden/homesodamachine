"""Bind a fresh single-object RC62 native slice to its approximate pause time.

Optional --retention also runs the production pocket/roof/host path review.
Neither mode sends, starts, resumes or modifies a printer or native archive.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

from prepare import ENC, GEOMETRY, HERE, JOBS, ROOT, relative, save, sha


def elapsed_text(minutes):
    hours, remainder = divmod(minutes, 60)
    return f"about {hours} hours {remainder} minutes" if hours else f"about {remainder} minutes"


def review(part, retention_review=False):
    scope = HERE / JOBS[part]["scope"]
    prep = json.loads((scope / "preparation.json").read_text())
    native = json.loads((scope / "native-slice.json").read_text())
    directory = ROOT / ".cache/prints" / JOBS[part]["stem"]
    archive, project = ROOT / native["archive"], ROOT / native["project"]
    assert sha(archive) == native["archive_sha256"]
    assert sha(project) == native["project_sha256"] == prep["project_sha256"]
    for source, digest in prep["source_sha256"].items():
        assert sha(ROOT / source) == digest, source
    result_path = directory / "ready/result.json"
    result = json.loads(result_path.read_text())
    plate_result, = result["sliced_plates"]
    assert result["return_code"] == 0 and not plate_result["warning_message"]
    assert len(plate_result["objects"]) == 1
    with zipfile.ZipFile(archive) as source:
        assert source.testzip() is None
        metadata = ET.fromstring(source.read("Metadata/slice_info.config")).find("plate")
        values = {m.get("key"): m.get("value") for m in metadata.findall("metadata")}
        pauses = metadata.findall("pause_list/pause")
        assert len(pauses) == 1 and values["pause_count"] == "1"
        object_row, = metadata.findall("object")
        assert object_row.get("name") == prep["native_object_name"]
        assert object_row.get("skipped") == "false"
        assert int(object_row.get("identify_id")) == prep["identify_id"]
        assert [n.get("id") for n in metadata.findall("nozzle")] == ["0"]
        assert metadata.find("nozzle").get("extruder_id") == "1"
        assert values["outside"] == "false"
        assert abs(float(values["prediction"])-float(plate_result["total_predication"])) <= 1.
        assert all(f.get("color") == prep["filament_colour"] for f in metadata.findall("filament"))
        config = ET.fromstring(source.read("Metadata/model_settings.config"))
        owner, = config.findall("object")
        normal, = owner.findall("part[@subtype='normal_part']")
        assert normal.find("metadata[@key='name']").get("value") == f"enclosure-{part}"
        assert "pump-cap" not in ET.tostring(owner, encoding="unicode")
        expected_hosts = {r["name"] for r in prep["solid_host_regions"]}
        actual_hosts = {p.find("metadata[@key='name']").get("value")
            for p in owner.findall("part[@subtype='modifier_part']")}
        assert actual_hosts == expected_hosts
        settings = json.loads(source.read("Metadata/project_settings.config"))
        assert settings["filament_nozzle_map"] == ["0"]
        assert settings["filament_colour"] == [prep["filament_colour"]]
        assert settings["layer_height"] == "0.24" and settings["initial_layer_print_height"] == "0.2"
        assert float(settings["support_bottom_z_distance"]) == .3
        assert float(settings["support_object_xy_distance"]) == .5
        custom = ET.fromstring(source.read("Metadata/custom_gcode_per_layer.xml"))
        custom_layer, = custom.findall("plate/layer")
        assert custom_layer.get("gcode") == "M400 U1"
        assert abs(float(custom_layer.get("top_z"))-prep["requested_pause_height_mm"]) < 1e-6
        digest, md5 = hashlib.sha256(), hashlib.md5()
        line_num = 0
        layer = total_layers = None
        layer_z = previous_layer_z = None
        first_countdown = None
        last_countdown = last_progress = None
        trims = []
        emitted_pauses = []
        with source.open("Metadata/plate_1.gcode") as gcode:
            for raw in gcode:
                line_num += 1
                digest.update(raw)
                md5.update(raw)
                line = raw.decode().strip()
                if line.startswith("; Z_HEIGHT:"):
                    previous_layer_z, layer_z = layer_z, float(line.split(":", 1)[1])
                elif match := re.fullmatch(r"; layer num/total_layer_count:\s*(\d+)/(\d+)", line):
                    layer, total_layers = map(int, match.groups())
                elif match := re.fullmatch(r"M73 C(\d+)", line):
                    if first_countdown is None:
                        first_countdown = int(match.group(1))
                    last_countdown = line
                elif re.fullmatch(r"M73 P\d+ R\d+", line):
                    last_progress = line
                elif match := re.fullmatch(r"G29\.1 Z([-+\d.]+)(?:\s*;.*)?", line):
                    trims.append(float(match.group(1)))
                elif re.fullmatch(r"M400 U1(?:\s*;.*)?", line):
                    emitted_pauses.append(dict(gcode_line_1_based=line_num,
                        before_layer=layer, total_native_layers=total_layers,
                        before_print_z_mm=layer_z, preceding_layer_boundary_z_mm=previous_layer_z,
                        last_progress=last_progress, last_countdown=last_countdown))
        assert digest.hexdigest() == native["gcode_sha256"]
        assert md5.hexdigest() == source.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        assert len(emitted_pauses) == 1 and first_countdown is not None
        pause = emitted_pauses[0]
        assert pause["before_layer"] == int(pauses[0].get("layer"))
        assert abs(pause["before_print_z_mm"]-prep["requested_pause_height_mm"]) < .001
        assert trims == [0., prep["expected_textured_trim_mm"]], trims
    total = float(plate_result["total_predication"])
    remaining = int(pauses[0].get("remaining_time"))
    elapsed_minutes = round(total/60.-remaining)
    assert elapsed_minutes > 0
    method_bounds = [min(first_countdown, elapsed_minutes), max(first_countdown, elapsed_minutes)]
    timing = dict(schema_version=1, status="current_native_pause_forecast_verified",
        checked_utc=datetime.now(timezone.utc).isoformat(), part=part,
        printer=prep["printer"], quantity=1, cap_included=False,
        archive=native["archive"], archive_sha256=native["archive_sha256"],
        gcode_sha256=native["gcode_sha256"], project=native["project"],
        project_sha256=native["project_sha256"], source_stl_sha256=prep["source_stl_sha256"],
        source_step_sha256=prep["source_step_sha256"], preparation=relative(scope / "preparation.json"),
        native_result=relative(result_path), native_result_sha256=sha(result_path),
        preparation_sha256=sha(scope / "preparation.json"), review_script_sha256=sha(__file__),
        programmed_pause=dict(command="M400 U1", count=1, **pause,
            custom_top_z_mm=float(custom_layer.get("top_z")),
            pause_list_remaining_minutes=remaining, pause_list_percent=int(pauses[0].get("percent"))),
        native_forecast=dict(approximate_elapsed_from_native_start_minutes=elapsed_minutes,
            approximate_elapsed_text=elapsed_text(elapsed_minutes), native_total_prediction_seconds=total,
            initial_native_pause_countdown_minutes=first_countdown,
            approximate_two_method_elapsed_minutes=method_bounds,
            method="Round native total prediction minus the minute-rounded pause-list remainder to the nearest elapsed minute; compare with the initial emitted M73 C countdown.",
            resolution="Native remainder and countdown are rounded to minutes. Startup heating/calibration and physical printing can shift the actual pause; this is not an exact clock deadline."),
        binding_checks=dict(native_crc_and_gcode_md5=True, exact_current_mesh_and_project=True,
            single_expected_model_no_cap=True, current_host_modifiers_only=True,
            one_left_standard_nozzle=True, exact_printer_colour_and_trim=True,
            one_custom_and_emitted_pause_at_current_roof=True),
        preferred_magnet_label="C3", preferred_valve_label="V69",
        submitted=False, launch_authorized=False, printer_task_id=None,
        retention_path_review=None, physical_fit_roof_or_strength_qualified=False,
        scope="Current single-object native timing and identity only. Actual insertion requires a separately observed matching programmed printer pause. No printer command or archive edit was performed.")
    if retention_review:
        sys.path.insert(0, str(ENC / "magnet-retention"))
        from audit_prints import read_job
        geometry = json.loads(GEOMETRY.read_text())["pieces"][part]
        job = dict(part=part, native_archive=native["archive"],
            native_archive_sha256=native["archive_sha256"], gcode_sha256=native["gcode_sha256"],
            project=native["project"], project_sha256=native["project_sha256"],
            native_object_name=prep["native_object_name"],
            source_stl_sha256=prep["source_stl_sha256"],
            machine_to_bed_translation_mm=prep["machine_to_bed_translation_mm"],
            solid_host_regions=prep["solid_host_regions"])
        retention = read_job(job, geometry)
        save(scope / "retention-native-check.json", retention)
        timing["retention_path_review"] = dict(record="retention-native-check.json",
            sha256=sha(scope / "retention-native-check.json"),
            native_checks_pass=retention["native_checks_pass"],
            reviewer_source_sha256=sha(ENC / "magnet-retention/audit_prints.py"))
        assert retention["native_checks_pass"], retention["checks"]
    elif (retention_path := scope / "retention-native-check.json").exists():
        retention = json.loads(retention_path.read_text())
        for key in ("native_archive_sha256", "gcode_sha256", "project_sha256", "source_stl_sha256"):
            expected = native["archive_sha256"] if key == "native_archive_sha256" else (
                prep[key] if key == "source_stl_sha256" else native[key])
            assert retention[key] == expected, key
        assert retention["native_checks_pass"]
        existing = json.loads((scope / "pause-forecast.json").read_text())["retention_path_review"]
        assert existing["sha256"] == sha(retention_path)
        assert existing["reviewer_source_sha256"] == sha(ENC / "magnet-retention/audit_prints.py")
        timing["retention_path_review"] = existing
    save(scope / "pause-forecast.json", timing)
    print(json.dumps(dict(part=part, printer=prep["printer"],
        approximate_elapsed=elapsed_text(elapsed_minutes),
        initial_countdown_minutes=first_countdown,
        programmed_pause_before_z_mm=pause["before_print_z_mm"],
        retention_path_review=timing["retention_path_review"]), indent=2), flush=True)
    return timing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=JOBS)
    parser.add_argument("--retention", action="store_true", help="Also review current pocket, dense hosts, bands and closing paths.")
    args = parser.parse_args()
    review(args.part, args.retention)
