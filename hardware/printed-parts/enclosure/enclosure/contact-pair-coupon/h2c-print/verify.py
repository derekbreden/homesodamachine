"""Verify the unsupported contact-seat trial against its automatic-support slice."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

from shapely.geometry import LineString
from shapely.ops import unary_union

from prepare import HERE, COUPON, ROOT, sha, validate_geometry_sources, writer

sys.path[:0] = [str(ROOT / "hardware/scripts"),
               str(ROOT / "hardware/printed-parts/enclosure/nameplate")]
from enclosure_support_audit import audit
from verify_mark2_print import segments


def verify(revision, automatic_revision):
    job = ROOT / f".cache/prints/contact-pair-coupons-h2c-v{revision}"
    comparison = ROOT / f".cache/prints/contact-pair-coupons-h2c-v{automatic_revision}"
    prep = json.loads((job / "preparation.json").read_text())
    geometry = json.loads((COUPON / "geometry-check.json").read_text())
    assert sha(COUPON / "geometry-check.json") == prep["geometry_record_sha256"]
    source_review = validate_geometry_sources(geometry)
    record = json.loads((job / "native-slice.json").read_text())
    for name, digest in record["source_stl_sha256"].items():
        assert sha(COUPON / f"{name}.stl") == digest
    project = ROOT / record["project"]
    baseline_record = json.loads((comparison / "native-slice.json").read_text())
    with zipfile.ZipFile(ROOT / baseline_record["project"]) as before, zipfile.ZipFile(project) as after:
        changed = [name for name in before.namelist() if before.read(name) != after.read(name)]
        assert changed == ["3D/Objects/object_1.model", "3D/Objects/object_2.model"], changed
        for name in changed:
            initial, painted = ET.fromstring(before.read(name)), ET.fromstring(after.read(name))
            for triangle in painted.iter(writer.qn("triangle")):
                assert triangle.attrib.pop("paint_supports") == "8"
            assert ET.tostring(initial) == ET.tostring(painted), "Blockers changed geometry"
    archive = ROOT / record["archive"]
    assert sha(archive) == record["archive_sha256"]
    with zipfile.ZipFile(archive) as native:
        gcode = native.read("Metadata/plate_1.gcode")
    assert hashlib.sha256(gcode).hexdigest() == record["gcode_sha256"]
    path = job / "ready/plate_1.gcode"
    assert path.read_bytes() == gcode
    text = gcode.decode()
    reading = audit(path, "contact-pair-coupons", include_unlabelled_support=True)
    assert reading["summary"]["support_bodies"] == 0, reading["summary"]
    assert not re.search(r"^; FEATURE: Support", text, re.M)
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text, re.M)]
    assert trims == [0.0, 0.16], trims
    roads = list(segments(path))
    assert {r["object"] for r in roads} == {1901, 1902}
    assert {r["tool"] for r in roads} == {0}
    parts = []
    for key, part in zip(("male", "female"), prep["parts"]):
        paths = [r for r in roads if r["object"] == part["identify_id"]]
        layers = sorted({r["layer"] for r in paths})
        assert layers[:2] == [0.2, 0.44]
        assert all(abs((b - a) - 0.24) < 1e-6 for a, b in zip(layers, layers[1:-1]))
        first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                             for r in paths if r["layer"] == 0.2])
        overlaps = []
        for road in paths:
            if road["layer"] != 0.44:
                continue
            line = LineString((road["a"], road["b"]))
            bead = line.buffer(road["width"] / 2)
            overlaps.append((bead.intersection(first).area / bead.area, road, line.length))
        outer_min = min(n for n, road, length in overlaps if road["feature"] == "Outer wall")
        assert outer_min > 0.5, (key, outer_min)
        short = [{"area_overlap_fraction": n, "feature": road["feature"], "length_mm": length,
                  "start_plate_mm": road["a"], "end_plate_mm": road["b"], "width_mm": road["width"]}
                 for n, road, length in overlaps if n < 0.5]
        assert all(road["feature"] == "Inner wall" and length < 0.2
                   for n, road, length in overlaps if n < 0.5), short
        roof_point = next(p["bed"] for p in geometry["coupons"][key]["landmarks"]
                          if p["feature"].startswith("seat roof"))
        first_roof = next(z for z in layers if z >= roof_point[2])
        cx, cy = [part["plate_translation_mm"][i] - part["source_center_mm"][i] for i in (0, 1)]
        roof_paths = [road for road in paths
                      if first_roof <= road["layer"] <= first_roof + 0.24 + 1e-6
                      and all(abs(p[0] - cx) < 11.85 and abs(p[1] - cy - roof_point[1]) < 2.0
                              for p in (road["a"], road["b"]))]
        bridges = [road for road in roof_paths if road["feature"] == "Bridge"]
        assert bridges, (key, first_roof)
        parts.append({"name": part["name"], "source_stl_sha256": part["stl_sha256"],
                      "production_print_pose_retained": True,
                      "native_rotation_x_degrees": part["rotation_x_degrees"],
                      "plate_bounds_mm": part["plate_bounds_mm"], "model_layer_count": len(layers),
                      "first_two_layer_heights_mm": layers[:2],
                      "minimum_second_layer_bead_area_overlap_fraction": min(n for n, _, _ in overlaps),
                      "minimum_second_layer_outer_wall_bead_area_overlap_fraction": outer_min,
                      "short_inner_wall_corner_segments_below_half_overlap": short,
                      "overlap_scope": "Short corner segments connect to longer anchored inner-wall paths; all second-layer outer walls have more than half their nominal bead area on the first-layer footprint.",
                      "seat_roof_landmark_z_mm": roof_point[2], "first_roof_layer_z_mm": first_roof,
                      "roof_bridge_layers_mm": sorted({road["layer"] for road in bridges}),
                      "maximum_roof_bridge_toolpath_length_mm": max(math.dist(road["a"], road["b"]) for road in bridges)})
    automatic = audit(comparison / "ready/plate_1.gcode", "contact-pair-coupons",
                      include_unlabelled_support=True)
    record.update(status="reviewed_for_unsupported_contact_seat_trial",
                  support_mode=prep["support_mode"], blocked_source_facets=prep["blocked_source_facets"],
                  project_members_changed_from_automatic_comparison=changed,
                  emitted_z_trim_commands_mm=trims, support_paths=0, support_summary=reading["summary"],
                  parts=parts, export_generator_review=source_review,
                  automatic_comparison={"archive": baseline_record["archive"],
                                        "archive_sha256": baseline_record["archive_sha256"],
                                        "support_summary": automatic["summary"],
                                        "record": "automatic-support-audit.json"},
                  geometry_record_sha256=prep["geometry_record_sha256"], physical_fit_tested=False)
    (HERE / "preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    (HERE / "automatic-support-audit.json").write_text(json.dumps(automatic, indent=2) + "\n")
    (HERE / "unsupported-support-audit.json").write_text(json.dumps(reading, indent=2) + "\n")
    (HERE / "preparation.json").write_bytes((job / "preparation.json").read_bytes())
    print(json.dumps({"status": record["status"], "seconds": record["estimated_seconds"],
                      "support_paths": 0, "parts": [{k: p[k] for k in
                      ("name", "minimum_second_layer_outer_wall_bead_area_overlap_fraction",
                       "first_roof_layer_z_mm", "maximum_roof_bridge_toolpath_length_mm")}
                      for p in parts]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, type=int)
    parser.add_argument("--automatic-revision", required=True, type=int)
    args = parser.parse_args()
    verify(args.revision, args.automatic_revision)
