"""Review the new ordinary-layer cartridge/cap archive without printer control."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(HERE), str(ENC / "magnet-retention"), str(ROOT / "hardware/scripts")]
from prepare import JOBS, sha, relative, archive_members, write_json
import audit_prints as pocket
from audit_cartridge_pair import native_components, cap_roads
from verify_round_layer_band import wall_layers, check_span


def main():
    part = "pump-cartridge-cap"
    directory = ROOT / ".cache/prints" / JOBS[part]["stem"]
    prep = json.loads((directory / "preparation.json").read_text())
    project = directory / prep["project"]
    archive = directory / "ready" / (prep["stem"] + ".gcode.3mf")
    assert sha(project) == prep["project_sha256"]
    for name, digest in prep["source_sha256"].items():
        assert sha(ROOT / name) == digest, name
    payload = archive_members(archive)
    data = payload["Metadata/plate_1.gcode"]
    gcode_digest = hashlib.sha256(data).hexdigest()
    assert hashlib.md5(data).hexdigest() == payload["Metadata/plate_1.gcode.md5"].decode().strip().lower()
    job = {**prep, "project": relative(project), "native_archive": relative(archive),
           "native_archive_sha256": sha(archive), "gcode_sha256": gcode_digest}
    bindings, native_parts = native_components(payload, job)
    cartridge = next(s for s in prep["components"] if s["part"] == "pump-cartridge")
    geometry = json.loads((ENC / "magnet-retention/geometry-check.json").read_text())["pieces"]["pump-cartridge"]

    # The production pocket audit is otherwise unchanged. Its upper-rim span
    # reads the new ordinary-layer policy; the real lower-rim span stays fine.
    def policy_span(layers, name, low, high, target, tolerance):
        if name == "grip-ceiling-rounds":
            name, target = "additive-upper-grip-transition", .24
        return check_span(layers, name, low, high, target, tolerance)

    pocket.check_span = policy_span
    cartridge_check = pocket.read_job({**job, **cartridge}, geometry)
    for check in cartridge_check["checks"]:
        if check["check"] == "emitted fine show-round layer bands":
            check["check"] = "emitted lower fine rim and upper ordinary transition"
    cap = next(s for s in prep["components"] if s["part"] == "pump-cap")
    cap_id = next(p["identify_id"] for p in native_parts if p["name"] == "enclosure-pump-cap")
    cap_check = cap_roads(data, cap, cap_id)
    source = archive_members(project)
    baseline = archive_members(ROOT / prep["baseline_project"])
    changed = [name for name in source if source[name] != baseline[name]]
    assert changed == ["Metadata/layer_config_ranges.xml"], changed
    result = json.loads((directory / "ready/result.json").read_text())
    plate, = result["sliced_plates"]
    slice_info = ET.fromstring(payload["Metadata/slice_info.config"]).find("plate")
    metadata = {m.get("key"): m.get("value") for m in slice_info.findall("metadata")}
    pauses = slice_info.findall("pause_list/pause")
    assert len(pauses) == 1
    layers = wall_layers(archive, 1901)
    bands = [check_span(layers, "lower-inward-top-rim", 6.23, 18.23, .08, .001),
             check_span(layers, "upper-additive-transition", 100.999, 112.999, .24, .001)]
    assert layers[:2] == [(.2, .2), (.44, .24)], layers[:2]
    # Count paths across a straight station through the upper hand-pocket wall;
    # source X >= 91.7 selects the cartridge's visible outer side.
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/bottom-grip-print"))
    import verify as bottom
    path = directory / "ready/plate_1.gcode"
    path.write_bytes(data)
    shift = cartridge["machine_to_bed_translation_mm"]
    station_y = 43. + shift[1]
    crossings = {}
    for road in bottom.roads(path):
        if road["object"] != 1901 or road["feature"] not in ("Outer wall", "Inner wall", "Overhang wall"):
            continue
        if not 102 < road["layer"] < 111:
            continue
        x1, y1 = road["a"]
        x2, y2 = road["b"]
        if min(y1, y2) <= station_y < max(y1, y2):
            x = x1+(station_y-y1)*(x2-x1)/(y2-y1)-shift[0]
            if x >= 91.7:
                crossings.setdefault(road["layer"], []).append(x)
    wall_counts = [{"print_z_mm": z, "outer_side_crossing_count": len(xs)}
                   for z, xs in sorted(crossings.items())]
    assert wall_counts and all(r["outer_side_crossing_count"] >= 6 for r in wall_counts), wall_counts
    checks = {
        "current_mesh_and_complete_solid_host_bindings": all(r["pass_check"] for r in bindings),
        "cartridge_pause_bridge_support_and_dense_hosts": cartridge_check["native_checks_pass"],
        "cap_first_layers_orientation_and_dense_hosts": cap_check["native_checks_pass"],
        "native_success_without_warning": result["return_code"] == 0 and not plate["warning_message"],
        "both_objects_inside_plate": len(plate["objects"]) == 2 and metadata["outside"] == "false",
        "one_retained_rc62_pause": len(re.findall(rb"(?m)^M400 U1(?:\s*;.*)?$", data)) == 1,
        "settings_support_paint_solid_hosts_pose_and_pause_members_unchanged": len(changed) == 1,
        "fine_lower_rim_and_ordinary_upper_transition": all(b["pass"] for b in bands),
        "six_walls_through_upper_transition_station": all(r["outer_side_crossing_count"] >= 6 for r in wall_counts),
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail", "native_checks_pass": all(checks.values()),
        "submitted": False, "archive": relative(archive), "archive_sha256": sha(archive),
        "gcode_sha256": gcode_digest, "project_sha256": sha(project),
        "checks": checks, "source_bindings": bindings, "parts": [cartridge_check, cap_check],
        "first_two_wall_layers_mm": layers[:2], "layer_spans": bands,
        "six_wall_station_source_y_mm": 43., "upper_wall_counts": wall_counts,
        "estimate_seconds": plate["total_predication"],
        "pause": {"layer": int(pauses[0].get("layer")), "print_z_mm": prep["requested_pause_height_mm"]},
        "preview": "preview.png", "review_script_sha256": sha(__file__),
        "inherited_pocket_review_sha256": sha(ENC / "magnet-retention/audit_prints.py"),
        "inherited_cap_review_sha256": sha(ENC / "magnet-retention/audit_cartridge_pair.py"),
        "launch_state": "queued_awaiting_printer_availability_and_fresh_preflight",
        "physical_surface_retention_or_strength_qualification": False,
    }
    output = HERE / part
    (output / "preview.png").write_bytes(payload["Metadata/plate_1.png"])
    write_json(output / "native-check.json", report)
    print(json.dumps({"part": part, "status": report["status"], "checks": checks,
                      "estimate_seconds": report["estimate_seconds"]}), flush=True)
    if not report["native_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
