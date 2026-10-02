"""Review the native receiver/cradle slice and its accessible hook supports."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from shapely.geometry import LineString
from shapely.ops import unary_union

from prepare import HERE, ROOT, TRIAL, FROZEN_STLS, sha

sys.path[:0] = [str(ROOT / "hardware/scripts"),
               str(ROOT / "hardware/printed-parts/enclosure/nameplate")]
from enclosure_support_audit import audit
from verify_mark2_print import segments


def verify(revision):
    job = ROOT / f".cache/prints/funnel-cradle-trial-h2c-v{revision}"
    prep = json.loads((job / "preparation.json").read_text())
    record = json.loads((job / "native-slice.json").read_text())
    export_revision = "f8f59be7e"
    for source, expected in prep["source_hashes"].items():
        versioned = subprocess.run(["git", "show", f"{export_revision}:{source}"],
                                   cwd=ROOT, capture_output=True, check=True).stdout
        assert hashlib.sha256(versioned).hexdigest() == expected, source
    for name, expected in FROZEN_STLS.items():
        assert sha(TRIAL / f"{name}.stl") == expected
    assert sha(ROOT / record["project"]) == record["project_sha256"]
    archive = ROOT / record["archive"]
    assert sha(archive) == record["archive_sha256"]
    with zipfile.ZipFile(archive) as native:
        assert native.testzip() is None
        gcode = native.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == native.read(
            "Metadata/plate_1.gcode.md5").decode().strip().lower()
    assert hashlib.sha256(gcode).hexdigest() == record["gcode_sha256"]
    path = job / "ready/plate_1.gcode"
    assert path.read_bytes() == gcode
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", gcode.decode(), re.M)]
    assert trims == [0.0, 0.16], trims
    roads = list(segments(path))
    assert {road["object"] for road in roads} == {1901, 1902}
    assert {road["tool"] for road in roads} == {0}
    supports = [road for road in roads if road["feature"].startswith("Support")]
    assert supports and {road["object"] for road in supports} == {1902}
    reading = audit(path, "funnel-cradle-trial", include_unlabelled_support=True)
    summary = reading["summary"]
    assert summary["support_bodies"] == summary["bed_rooted_bodies"] == 2
    assert summary["interface_islands"] == 2 and summary["model_rooted_bodies"] == 0
    assert summary["bodies_without_interface_labels"] == 0
    cradle = prep["parts"][1]
    shift = [cradle["plate_translation_mm"][i] - cradle["source_center_mm"][i]
             for i in range(3)]
    reading["coordinate_frame"] = {"plate_to_printed_cradle_translation_mm": [-v for v in shift]}
    for row in reading["trees"] + reading["interfaces"]:
        row["bbox_printed_cradle_xy_mm"] = [round(v - shift[i % 2], 4)
                                            for i, v in enumerate(row["bbox_xy_mm"])]
    for interface in reading["interfaces"]:
        x0, y0, x1, y1 = interface["bbox_printed_cradle_xy_mm"]
        assert 11.3128 < min(abs(x0), abs(x1)) and max(abs(x0), abs(x1)) < 15.0
        assert -11.84 < y0 < y1 < 21.17
        assert (interface["first_z_mm"], interface["last_z_mm"]) == (32.84, 33.08)
    # The complete support paths stand outside the cradle's straight sides.
    assert min(abs(p[0] - shift[0]) for road in supports
               for p in (road["a"], road["b"])) > 11.3128
    parts = []
    for part in prep["parts"]:
        paths = [road for road in roads if road["object"] == part["identify_id"]
                 and not road["feature"].startswith("Support")]
        layers = sorted({road["layer"] for road in paths})
        assert layers[:2] == [0.2, 0.44]
        assert all(abs(b - a - 0.24) < 1e-6 for a, b in zip(layers, layers[1:-1]))
        first = unary_union([LineString((road["a"], road["b"])).buffer(road["width"] / 2)
                             for road in paths if road["layer"] == 0.2])
        overlaps = []
        for road in paths:
            if road["layer"] == 0.44:
                bead = LineString((road["a"], road["b"])).buffer(road["width"] / 2)
                overlaps.append((bead.intersection(first).area / bead.area, road["feature"]))
        assert min(n for n, _ in overlaps) > 0.5
        parts.append({"name": part["name"], "stl_sha256": part["stl_sha256"],
                      "rotation_x_degrees": part["rotation_x_degrees"],
                      "plate_bounds_mm": part["plate_bounds_mm"],
                      "embedded_vertex_error_mm": part["embedded_vertex_error_mm"],
                      "model_layer_count": len(layers), "first_two_layer_heights_mm": layers[:2],
                      "minimum_second_layer_bead_area_overlap_fraction": min(n for n, _ in overlaps),
                      "minimum_second_layer_outer_wall_bead_area_overlap_fraction":
                          min(n for n, feature in overlaps if feature == "Outer wall")})
    hook_paths = [road for road in roads if road["object"] == 1902
                  and not road["feature"].startswith("Support")
                  and min(abs(p[0] - shift[0]) for p in (road["a"], road["b"])) > 11.4]
    assert min(road["layer"] for road in hook_paths) == 33.8
    record.update(status="reviewed_for_elbow_cradle_snap_trial", submitted=False,
                  emitted_z_trim_commands_mm=trims, parts=parts, support_summary=summary,
                  support_contacts="two_external_hook_undersides_only",
                  receiver_support_paths=0, pocket_support_paths=0,
                  hook_underside_geometry_z_mm=33.552898407,
                  support_interface_last_z_mm=33.08,
                  first_hook_model_layer_z_mm=33.8,
                  nominal_first_hook_layer_bottom_z_mm=33.56,
                  printed_support_gap_mm=0.48,
                  production_print_poses_retained=True,
                  physical_fit_and_retention_tested=False,
                  geometry_export_revision=export_revision,
                  source_snapshot_matches_export_revision=True,
                  source_snapshot=prep["source_hashes"])
    (HERE / "preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    (HERE / "support-audit.json").write_text(json.dumps(reading, indent=2) + "\n")
    (HERE / "preparation.json").write_bytes((job / "preparation.json").read_bytes())
    print(json.dumps({"status": record["status"], "estimated_seconds": record["estimated_seconds"],
                      "support_summary": summary, "parts": parts}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=int, required=True)
    args = parser.parse_args()
    verify(args.revision)
